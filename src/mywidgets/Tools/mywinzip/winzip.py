import os.path
import shutil
import tkinter as tk
import tkinter.messagebox as tkMessageBox
import tkinter.filedialog as tkFileDialog
import tkinter.simpledialog as tkSimpleDialog
import zipfile
from datetime import datetime
import tempfile
import fnmatch

import mywidgets.userinterface as userinterface
import mywidgets.Tools.mywinzip.file_menu as fm
from mywidgets.Widgets import kodiwidgets
from mywidgets.Widgets.Custom import navigationbar
from mywidgets.equations import equations_manager

RECYCLEBIN = '_recyclebin/'
LOCK_CHR = '🔒'


class Winzip(tk.Tk):

    def __init__(self):
        super().__init__()
        self.event_add('<<MENUCLICK>>', 'None')
        self.event_add('<<VAR_CHANGE>>', 'None')
        self.bind_all('<<MENUCLICK>>', self.onMenuClick)
        self.bind_all('<<VAR_CHANGE>>', self.onVarChange)
        self.bind_all('<Button-3>', self.onRightClick)

        self.project_path = '/mnt/c/Users/Alex Montes/PycharmProjects/mywidgets'
        self.menu_file = menu_file = fm.FileMenu(self)
        menu_file.default_file_name = 'newZip.zip'
        menu_file.default_path = '/mnt/c/Users/Alex Montes/Downloads/'
        menu_file.default_extension = '.zip'
        menu_file.default_file_type = ('zip Files', '*.zip')

        self.zf = None

        self._recyclebin = set()

        self.filters = ['*.*;', '*.js,*.py;*.pyc', ';*.pyc', '*.pdf;']
        self.active_filter = 0

        self.winzip_ops = {
            'blower': False,
            'bupper': False,
            'bnumeric': False,
            'bother': False,
            'cipher_method': 'zip20',
            'add_folder': 'last_folder',
            'tmp_folder': tempfile.gettempdir(),
            'wrk_folder': menu_file.default_path,
            'user_folder': menu_file.default_path,
        }

        self.unzip_ops = {
            'unzip': 'all',
            "Ask before file replacement": True,
            "Do not replace new files with early versions": False,
            "Use folder names": True,
            "Show unzip files": False,
            "Last folder": None,
        }

        self.zip_ops = {
            'zip_type': 'zip',
            'zip_method': 'noc',
            'Cipher': False,
        }

        self.rclick_name = None

        self.setGui()

        self.last_n_directories = [menu_file.default_path.rstrip(os.sep)]
        src = '@mywinzip:menu/zip_panel_popup'
        selpane = userinterface.getLayout(src)
        self.popUpZip = userinterface.menuFactory(self, selpane, registerMenu=self.registerMenu)

        self.file_menu('New')
        self.attributes('-zoomed', True)
        pass

    def file_menu(self, menu_item):
        match menu_item.split():
            case 'New', :
                with self.menu_file.newFile():
                    filename = os.path.join(self.menu_file.default_path, self.menu_file.default_file_name)
                    if os.path.exists(filename):
                        os.remove(filename)
                    self.loadzip(filename, mode='x')
            case 'Open', :
                with self.menu_file.openFile() as filename:
                    assert filename
                    self.loadzip(filename, mode='a')
            case 'Print', :
                tree = self.zip_panel.tree
                selected = tree.get_children()
                values = [tree.set(iid, 'Name') for iid in selected]
                infolist = [self.zf.getinfo(path) for path in values]
                print(f'Filename: {self.title()}')
                print('\n'.join(self.dumpzip(infolist)))
                pass
            case 'Save', *suffix:       # case 'Save' | 'Save As':
                method = getattr(self.menu_file, 'saveFile' if not suffix else 'saveAsFile')
                with method() as filename:
                    if not self._recyclebin:
                        # El archivo no tiene elementos eliminados
                        srcfile, dstfile = self.zf.filename, filename
                        print(f'Save: {srcfile} -> {dstfile}')
                        self.zf.close()
                        dstfile = shutil.copy(srcfile, dstfile)
                        if suffix[0] == 'As':
                            dstfile = os.path.join(os.path.dirname(srcfile), os.path.basename(filename))
                            os.rename(srcfile, dstfile)
                            self.menu_file.title(filename)
                        try:
                            self._loadzip(dstfile, mode='a')
                        except Exception as e:
                            tkMessageBox.showerror(title='Saving Error', message=str(e))
                    else:
                        srcfile, dstfile = self.zf.filename, filename
                        selected = [
                            x for x in self.zf.namelist()
                            if x.count(os.sep) == 0 or (x.count(os.sep) == 1 and x.endswith(os.sep))
                        ]
                        self._save_partial(dstfile, selected)
                        self.zf.close()
                        os.remove(srcfile)
                        self.loadzip(dstfile, mode='a')
                        self._recyclebin = set()

            case 'Settings', :
                title = 'Winzip Settings'
                xmlfile = userinterface.getFileUrl('@mywinzip:layout/dlg_settings')
                dlg = kodiwidgets.CustomDialog(
                    self,
                    title=title, xmlFile=xmlfile, isFile=True, settings=self.winzip_ops, dlg_type='okcancel'
                )
                self.winzip_ops.update(dlg.settings)

            case indx, filename if indx.isdigit():
                zipfilename = self.menu_file.fileHistory[int(indx) - 1]
                assert zipfilename.endswith(filename)
                self.loadzip(zipfilename, mode='a')

            case 'Close', :
                self.file_menu('New')
            case _:
                title = f'File Menu - Option: {menu_item}'
                tkMessageBox.showinfo(title=title, message='Not implemented yet')

    def unzip_menu(self, menu_item):
        zippath, zipname = os.path.split(self.menu_file.title())
        dest_path = self.unzip_ops['Last folder']
        match menu_item:
            case 'Same folder':
                dest_path = zippath or self.menu_file.default_path.rstrip(os.sep)
            case 'Last folder':
                dest_path = self.unzip_ops['Last folder'] or zippath
            case 'My PC':
                msg = f'Unzip - {zipname}'
                initialdir = self.last_n_directories[0]
                dest_path = tkFileDialog.askdirectory(initialdir=initialdir, title=msg)
                menu_item = not dest_path or menu_item
            case "Ask before file replacement" | "Do not replace new files with early versions" | "Use folder names" | "Show unzip files":
                self.unzip_ops[menu_item] = not self.unzip_ops[menu_item]
            case _:
                if menu_item[0].isdigit():
                    indx, dirname = menu_item.split(' ')
                    dest_path = self.last_n_directories[int(indx)]
                    menu_item = 'Documents'
                else:
                    title = f'Unzip Menu - Option: {menu_item}'
                    tkMessageBox.showinfo(title=title, message='Not implemented yet')

        if menu_item in ('extract', 'Same folder', 'Documents', 'Last folder', 'My PC'):
            use_folder = self.unzip_ops["Use folder names"]
            ask_before = self.unzip_ops["Ask before file replacement"]
            unzip_selected = self.unzip_ops['unzip'] == 'selected'
            pwd = None
            if self.zip_ops['Cipher']:
                if self.zf.pwd is None:
                    pwd = tkSimpleDialog.askstring(title='Password', prompt='Please enter the zip file password', show='*')
                    if pwd:
                        pwd = pwd.encode('utf-8')
                        self.zf.setpassword(pwd)
                pwd = self.zf.pwd
            if unzip_selected:
                selected = [x.rstrip(' ' + LOCK_CHR) for x in self.selected_data()]
                members = list(map(self.zf.getinfo, selected))
            else:
                members = self.zf.infolist()
            if not use_folder:
                members = [zinfo for zinfo in members if not zinfo.is_dir()]
            title = 'Confirm file overwriting'
            xmlfile = '/mnt/c/Users/Alex Montes/PycharmProjects/mywidgets/src/Tools/mywinzip/res/layout/unzip_dlg.xml'
            settings = {'msg': 'msg to display', 'noask': False, 'what_to_do': 'replace'}
            for zinfo in members:
                filename = zinfo.filename
                filepath, name = os.path.dirname(filename), os.path.basename(zinfo.filename)
                filepath = os.path.join(dest_path, filepath) if use_folder else dest_path
                dest_filename = os.path.join(filepath, name)
                if ask_before and os.path.exists(dest_filename) and not settings["noask"]:
                    stat = os.stat(dest_filename)
                    src = (zinfo.file_size, datetime(*zinfo.date_time).strftime('%Y-%m-%d %H:%M'))
                    dst = (stat.st_size, datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M'))
                    msg = f'This file exists in the destination folder.\n'
                    msg += f'Replace the existing file:\n{dest_filename}\n{dst[0]} bytes {dst[1]}\n'
                    msg += f'With this:\n{name}\n{src[0]} bytes {src[1]}'
                    settings['msg'] = msg
                    dlg = kodiwidgets.CustomDialog(self, title=title, xmlFile=xmlfile, isFile=True, settings=settings, dlg_type='ok')
                    settings.update(dlg.settings)
                what_to_do = settings.get('what_to_do')
                if what_to_do == "replace":
                    pass
                elif what_to_do == "omit":
                    continue
                elif what_to_do == "keep":
                    n = 1
                    while True:
                        name, ext = os.path.splitext(name)
                        dmy = os.path.join(filepath, f'{name} ({n}){ext}')
                        if not os.path.exists(dmy):
                            break
                        n += 1
                    dest_filename = dmy
                if zinfo.is_dir():
                    os.makedirs(dest_filename)
                else:
                    os.makedirs(os.path.dirname(dest_filename), exist_ok=True)
                    with self.zf.open(zinfo, pwd=pwd) as fsrc, open(dest_filename, 'wb') as fdst:
                        try:
                            shutil.copyfileobj(fsrc, fdst)
                        except Exception as e:
                            msg = str(e)
                            tkMessageBox.showerror(title='Unzip - Not valid', message=msg)
            self.unzip_ops['Last folder'] = dest_path
            self.last_n_directories = self.menu_file.recFile(dest_path, self.last_n_directories)

    def zip_menu(self, menu_item):
        match menu_item:
            # case 'Cipher':
            #     self.zip_ops['Cipher'] = not self.zip_ops['Cipher']

            case 'Add Files':
                files = tkFileDialog.askopenfilenames(
                    defaultextension=None,
                    filetypes=[('All Files', '*.*'), self.menu_file.default_file_type],
                    initialdir=self.menu_file.default_path,
                    initialfile=None,
                    parent=None,
                    title='Add To File',
                    typevariable=None,
                )
                if files:
                    self._addFiles(files)
                pass
            case 'Add Folder':
                folder_name = tkFileDialog.askdirectory(
                    initialdir=self.menu_file.default_path,
                    title='Add To File',
                    mustexist=True
                )
                if folder_name:
                    files = []
                    for root, d_names, f_names in os.walk(folder_name):
                        files.append(os.path.join(root, ''))
                        files.extend(
                            [os.path.join(root, x) for x in f_names]
                        )
                    self._addFiles(files, directory=True)
            case prefix, suffix:
                if prefix.isdigit():
                    self.active_filter = int(prefix) - 1
                else:
                    menu_item = f'{prefix} {suffix}'
                    assert menu_item == "Create/edit/delete Filter"
                    xmlfile = userinterface.getFileUrl('@mywinzip:layout/dlg_crud_filters')
                    settings = {
                        'filters': '|'.join(self.filters[1:]),
                    }
                    dlg = kodiwidgets.CustomDialog(
                        self,
                        title=menu_item, xmlFile=xmlfile, isFile=True, settings=settings, dlg_type='ok'
                    )
                    if dlg.result:
                        self.filters[1:] = dlg.result['filters'].split('|')
                pass
            case _:
                title = f'Zip Menu - Option: {menu_item}'
                tkMessageBox.showinfo(title=title, message='Not implemented yet')

    def manage_menu(self, menu_item):
        match menu_item:
            case 'Copy To' | 'Move To':
                msg = f'{menu_item} - Selected Item(s)'
                dest_path = tkFileDialog.askdirectory(initialdir=self.menu_file.default_path, title=msg)
                self.unzip_ops['Last folder'] = dest_path
                unzip = self.unzip_ops['unzip']
                self.unzip_ops['unzip'] = 'selected'
                self.unzip_menu('extract')
                self.unzip_ops['unzip'] = unzip
                if menu_item == 'Move To':
                    selected = self.selected_data()
                    n = self.delete_items(selected)
                    msg = f'{n} items has been moved to Recycle Bin'
                    tkMessageBox.showinfo(title='Delete', message=msg)
            case 'Delete':
                if selected := self.selected_data():
                    msg = '\n'.join(['Do you want to delete the following items:', *selected])
                    bflag = tkMessageBox.askokcancel(title='Delete Zip File Item', message=msg)
                    if bflag:
                        n = self.delete_items(selected)
                        msg = f'{n} items has been moved to Recycle Bin'
                        tkMessageBox.showinfo(title='Delete', message=msg)
            case 'Rename':
                new_name = tkSimpleDialog.askstring(title='Rename Item To', prompt="Item's New Name:")
                name = self.rclick_name
                if name is None:
                    msg = 'Option valid with only one item selected'
                    tkMessageBox.showinfo(title='Rename', message=msg)
                    return
                new_name = os.path.join(os.path.dirname(name.rstrip(os.sep)), new_name).lstrip(os.sep)
                is_dir = name.endswith(os.sep)
                if is_dir:
                    new_name = os.path.join(new_name, '')
                    to_rename = [x for x in self.zf.NameToInfo if x.startswith(name)]
                    for item in to_rename:
                        zinfo = self.zf.NameToInfo.pop(item)
                        item = item.replace(name, new_name)
                        zinfo.filename = item
                        self.zf.NameToInfo[item] = zinfo
                else:
                    zinfo = self.zf.NameToInfo.pop(name)
                    zinfo.filename = new_name
                    self.zf.NameToInfo[new_name] = zinfo
                self.onVarChange(attr_data=('view_recycle', 0))
                self.menu_file.setSaveFlag(True)
                pass
            case 'Restore':
                if self.zip_panel.text != RECYCLEBIN[1:-1]:
                    msg = 'Option valid only with Recycle Bin'
                    tkMessageBox.showinfo(title='Restore', message=msg)
                    return
                if selected := self.selected_data():
                    msg = '\n'.join(['Do you want to restore the following items:', *selected])
                    bflag = tkMessageBox.askokcancel(title='Restore Zip File Item', message=msg)
                    if bflag:
                        n = self.restore_items(selected)
                        msg = f'{n} items has been restore'
                        tkMessageBox.showinfo(title='Restore', message=msg)
            case 'Select All':
                self.zip_panel.onSelectAll()
            case 'Toggle Selection':
                self.zip_panel.onToggleSel()
            case _:
                title = f'Manage Menu - Option: {menu_item}'
                tkMessageBox.showinfo(title=title, message='Not implemented yet')

    def apply_filter(self, raw_files: list, filter_indx: int) -> list:
        if filter_indx:
            active_filter = self.filters[filter_indx]
            filter_items = active_filter.split(';')
            fltr_files = []
            if filter_item := filter_items[0]:      # == '+': Include
                for fltr in filter_item.split(','):
                    fltr_files.extend(fnmatch.filter(raw_files, fltr))
            if filter_item := filter_items[1]:      # == '-': Exclude
                fltr_files = fltr_files or raw_files[::]
                exc_files = []
                for fltr in filter_item.split(','):
                    exc_files.extend(fnmatch.filter(fltr_files, fltr))
                fltr_files = list(set(fltr_files).difference(exc_files))
        else:
            fltr_files = raw_files[::]
        return fltr_files

    def _addFiles(self, files, zip_files=None, directory=False):
        tree_path = self.zip_panel.tree_path
        root_dir = tree_path.path_obj.root
        files = self.apply_filter(files, self.active_filter)
        if zip_files is None:
            sys_root = os.path.commonpath(files) if len(files) > 1 else os.path.dirname(files[0])
            if directory:
                sys_root = os.path.dirname(sys_root)
            zip_files = [os.path.relpath(x, sys_root) + ('/' if x.endswith('/') else '') for x in files]
            zip_path = tree_path.getActivePath().path
            # Cuando se agregan archivos en un directorio diferente al raiz del zip file
            if zip_path != root_dir:
                zip_path = os.path.relpath(zip_path, root_dir)
                zip_files = [
                    os.path.join(zip_path, x)
                    for x in zip_files
                ]
        compression = self.active_compression_method()
        try:
            for fname, arcname in zip(files, zip_files):
                self.zf.write(fname, arcname, compress_type=compression)
        except Exception as e:
            tkMessageBox.showerror(title='Add Files Error', message=str(e))
            return

        self.onVarChange(attr_data=('view_recycle', 0))
        self.menu_file.setSaveFlag(True)

    def pop_up_zip(self, menu_item):
        match menu_item:
            case "New Folder":
                dir_name = tkSimpleDialog.askstring(title='Add New Folder', prompt='Folder Name:')
                if dir_name:
                    files = [os.path.dirname(self.zf.filename)]
                    tree_path = self.zip_panel.tree_path
                    zip_path = tree_path.getActivePath().path
                    root_dir = tree_path.path_obj.root
                    zip_path = os.path.relpath(zip_path, root_dir)
                    zip_files = [os.path.join(zip_path, dir_name, '')]
                    self._addFiles(files, zip_files)
            case "Unzip":
                msg = f'Unzip'
                dest_path = tkFileDialog.askdirectory(initialdir=self.menu_file.default_path, title=msg)
                self.unzip_ops['Last folder'] = dest_path
                unzip = self.unzip_ops['unzip']
                self.unzip_ops['unzip'] = 'selected'
                self.unzip_menu('extract')
                self.unzip_ops['unzip'] = unzip
            case "A Level Up":
                path = self.zip_panel.tree_path.getActivePath().path
                path = os.path.dirname(path)
                self.zip_panel.onTreeViewOpen(path=path)
            case "Delete":
                name = self.rclick_name
                msg = f'Do you want to delete {name} item'
                bflag = tkMessageBox.askokcancel(title='Delete Zip File Item', message=msg)
                if bflag:
                    n = self.delete_items([name])
                    msg = f'{n} items has been moved to Recycle Bin'
                    tkMessageBox.showinfo(title='Delete', message=msg)
            case 'Restore':
                self.manage_menu(menu_item)
            case "Select All":
                self.manage_menu(menu_item)
            case "Toggle Selection":
                self.manage_menu(menu_item)
            case "Select By Name":
                self.manage_menu('Search')
            case "Rename":
                self.manage_menu(menu_item)
            case "Zip File With Selected Files":
                title = 'Zip File With Selected Files'
                xmlfile = userinterface.getFileUrl('@mywinzip:layout/dlg_add_files')
                settings = {
                    'fname': 'NuevoZip.zip', 'fpath': self.menu_file.default_path,
                    'zip_type': 'fzip', 'cipher': False, 'fltr_type': 'fltr1',
                }
                fltr_strs = ['Predeterminado (+*.*)']
                for k, filter in enumerate(self.filters[1:], start=1):
                    items = filter.split(';')
                    filter = ';'.join([('+-'[k] + item) if item else item for k, item in enumerate(items)])
                    fltr_strs.append(filter.strip(';'))

                template = '<kbool id="fltr{0}" label="{1}" group="fltr_type" cside="left"/>'
                block = '\n'.join(template.format(*pair) for pair in enumerate(fltr_strs, start=1))
                content = userinterface.getContent(xmlfile)
                content = content.replace('<<block>>', block)
                dlg = kodiwidgets.CustomDialog(
                    self,
                    title=title, xmlFile=content, isFile=False, settings=settings, dlg_type='okcancel'
                )
                if dlg.result:
                    settings.update(dlg.settings)
                    filename = os.path.join(settings['fpath'], settings['fname'])
                    method = zipfile.ZipFile if settings['zip_type'] == 'fzip' else zipfile.PyZipFile
                    cipher = settings['cipher']
                    active_filter = int(settings['fltr_type'].strip('fltr')) - 1
                    selected = self.zip_panel.selected_data('Name')
                    self._save_partial(filename, selected, method, active_filter=active_filter)
                pass
            case "Copy To" | "Move To":
                self.manage_menu(menu_item)
            case _:
                title = f'Popup Menu - Option: {menu_item}'
                tkMessageBox.showinfo(title=title, message='Not implemented yet')
        self.rclick_name = None

    def delete_items(self, selected):
        to_delete = set()
        for name in selected:
            is_dir = name.endswith(os.sep)
            if is_dir:
                delta = [x for x in self.zf.NameToInfo if x.startswith(name)]
            else:
                delta = [name]
            to_delete.update(delta)
        self._recyclebin.update(to_delete)
        self.onVarChange(attr_data=('view_recycle', 0))
        self.menu_file.setSaveFlag(True)
        return len(to_delete)

    def restore_items(self, selected):
        to_delete = set()
        for name in selected:
            d_names = os.path.dirname(name).split(os.sep)
            delta = [os.path.join(*d_names[:k]) + os.sep for k in range(1, len(d_names) + 1)]
            is_dir = name.endswith(os.sep)
            if is_dir:
                delta.extend([x for x in self.zf.NameToInfo if x.startswith(name)])
            else:
                delta.append(name)
            to_delete.update(delta)
        to_delete.intersection_update(self._recyclebin)
        self._recyclebin.difference_update(to_delete)

        # Esta parte se puede utilizar para purgar el recycle bin de directorios vacíos
        # Se restauran los directorios que no contengan al menos un archivo
        # infolist = set(
        #     x for x in self._recyclebin
        #     if not x.endswith('/')
        # )
        # paths = set(os.path.dirname(filename) for filename in infolist)
        # paths.intersection_update(self._recyclebin)
        # self._recyclebin = infolist.union(paths)

        self.onVarChange(attr_data=('view_recycle', 1))
        return len(to_delete)

    def _save_partial(self, filename, selected, method=None, *, active_filter=0):
        infolist = []
        path_obj = self.zip_panel.path_obj
        root_dir = path_obj.root
        # En este punto se agregan solo los archivos, no los directorios
        for name in selected:
            if name in self._recyclebin:
                continue
            zinfo = self.zf.getinfo(name)
            if zinfo.is_dir():
                full_name = os.path.join(root_dir, name.strip(os.sep))
                pgen = self.zip_panel.path_obj.walk(full_name)
                for root, dirs, files in pgen:
                    if root in self._recyclebin:
                        continue
                    root = os.path.relpath(root, root_dir)
                    files = [os.path.join(root, x).lstrip('./') for x in files]
                    files = [x for x in files if x not in self._recyclebin]
                    infolist.extend(files)
            else:
                infolist.append(name)
        # Se filtran los archivos de acuerdo al filtro escogido
        infolist = self.apply_filter(infolist, filter_indx=active_filter)
        # Se agregan los directorios que se encuentran en la ruta de los archivos a agregar,
        # de esta forma no se agregan directorios que se encuentren vacíos luego de aplicar el filtro.
        dirs = set(infolist)
        for f_name in infolist:
            d_names = os.path.dirname(f_name).split('/')
            d_names = ['/'.join(d_names[:k + 1]) + '/' for k in range(len(d_names))]
            dirs.update(d_names)
        infolist = sorted(dirs)
        infolist = map(self.zf.getinfo, infolist)
        if os.path.exists(filename):
            os.remove(filename)
        method = method or zipfile.ZipFile
        try:
            with method(filename, mode='x') as new_zf:
                for zinfo in infolist:
                    if zinfo.is_dir():
                        new_zf.write(os.path.abspath('.'), zinfo.filename)
                    else:
                        data = self.zf.read(zinfo.filename)
                        new_zf.writestr(zinfo, data)
        except Exception as e:
            tkMessageBox.showerror(title='Saving Error', message=str(e))

    def onRightClick(self, event):
        wdg = event.widget
        if str(wdg) == str(self.zip_panel.tree):
            popup_menu = self.popUpZip
            x, y = event.x, event.y
            to_hide = []
            if not self.zip_panel.groupby:
                to_hide.extend(['A Level Up', 'New Folder'])
            else:
                index = self.zip_panel.tree_path.getActivePath().index
                if index == 0:
                    to_hide.append('A Level Up')
            if self.zip_panel.text != RECYCLEBIN[1:-1]:
                to_hide.append('Restore')
            iid = wdg.identify_row(y)
            if iid:
                self.rclick_name = name = wdg.set(iid, 'Name')
                is_dir = name.endswith(os.sep)
                if not is_dir:
                    to_hide.append('Open Folder')
            n_entry = popup_menu.index(tk.END)
            fn = lambda x: popup_menu.entrycget(x, 'label')
            [
                popup_menu.entryconfigure(k, state=tk.DISABLED if fn(k) in to_hide else tk.ACTIVE)
                for k in range(n_entry)
                if popup_menu.type(k) in (tk.CHECKBUTTON, tk.COMMAND, tk.RADIOBUTTON)
            ]
            try:
                popup_menu.tk_popup(x, y)
            finally:
                popup_menu.grab_release()
                pass

    def onMenuClick(self, event):
        menu_master, indx = event.widget, event.data
        menu, menu_item = menu_master.cget("title"), menu_master.entrycget(indx, "label")
        if menu in ('file', 'open recent'):
            self.file_menu(menu_item)
        elif menu in ('unzip', 'unzip settings'):
            self.unzip_menu(menu_item)
        elif menu in ('zip', 'zip method'):
            self.zip_menu(menu_item)
        elif menu in ('manage', ):
            self.manage_menu(menu_item)
        elif menu == 'popupzippanel':
            self.pop_up_zip(menu_item)
        elif menu == 'filters':
            menu_item = menu_item.split(' ', 1)
            self.zip_menu(menu_item)
        pass

    def onVarChange(self, event=None, attr_data=None):
        if event:
            attr_data = event.attr_data
        var_name, value = attr_data
        match var_name:
            case 'view_files':
                if value == 0:
                    self.lframe.hide_band('left')
                else:
                    self.lframe.show_band()
            case 'view_actions':
                if value == 0:
                    self.rframe.hide_band('right')
                else:
                    self.rframe.show_band()
            case 'cipher':
                self.zip_ops['Cipher'] = value
            case 'view_recycle':
                self.basename = os.path.basename(self.zf.filename)
                filename = self.basename
                path_obj_root = f'/{filename}'
                if value == 1:
                    infolist = [
                        self.zf.getinfo(x) for x in self._recyclebin
                    ]
                    infolist.sort(key=lambda x: x.filename)
                else:
                    infolist = [x for x in self.zf.infolist() if x.filename not in self._recyclebin]
                file_members = [os.path.join(path_obj_root, x.filename) for x in infolist]
                rows = self.listzip(infolist)
                groupby = self.zip_panel.groupby

                def f_data(records, namelist):
                    def f_record(x):
                        try:
                            indx = namelist.index(x)
                            zinfo = records[indx]
                        except ValueError:
                            is_file = not x.endswith('/')
                            if is_file:
                                raise
                            # Se expresa como relative path
                            _, _, x = x.split('/', 2)
                            date_time = datetime.now()
                            date_time = date_time.strftime('%Y-%m-%d %H:%M')
                            zinfo = ('', '', '', '', '', date_time, '', x)
                        return zinfo

                    return f_record
                path_obj = navigationbar.StrListObj(file_members, path_obj_root)
                path_obj.validate_path = lambda path: os.path.abspath(path)
                path = self.zip_panel.tree_path.getActivePath().path
                if not path.startswith(path_obj.root):
                    path = path_obj.root
                path_obj.actual_dir = path
                self.zip_panel.tree_data(path_obj, f_data(rows, file_members), groupby=groupby)
                if value:
                    self.zip_panel.text = RECYCLEBIN[1:-1]
            case 'mn_unzip':
                msg = f'{var_name}={value}'
                tkMessageBox.showinfo(title='on_varchange', message=msg)
            case 'zip_type' | 'zip_method':
                self.zip_ops[var_name] = value
            case 'zip_filters':
                self.active_filter = int(value) - 1
            case 'unzip_scope':
                self.unzip_ops['unzip'] = value
        pass

    def setGui(self):
        file_path = '@mywinzip:layout/winzip'
        xmlObj = userinterface.getLayout(file_path, withCss=True)
        userinterface.newPanelFactory(
            master=self,
            selpane=xmlObj,
            genPanelModule=None,
            setParentTo='master',
            registerWidget=self.register_widget,
        )
        equations_manager.set_initial_widget_states()

        files_panel = self.files_panel
        tree_path = files_panel.children['tree_path']
        tree_path.path_obj = '/mnt/c/Users/Alex Montes'

    def register_widget(self, master, xmlwidget, widget):
        attribs = xmlwidget.attrib
        name = attribs.get('name')
        if name in ('lframe', 'rframe', 'zip_panel', 'files_panel',):
            setattr(self, name, widget)
        # elif name in ('zip_panel',):
        #     setattr(self, name, widget.winfo_children()[0])
        pass

    def registerMenu(self, parent, selPane, menu_master, labels):
        title = menu_master.cget('title')
        match title:
            case 'zip' | 'zip method':
                radio_keys = ('zip_file',) if title == 'zip' else ('zip_method', )
                to_invoke = [self.zip_ops[key] for key in radio_keys]

                check_keys = ('Cipher', ) if title == 'zip' else []
                to_invoke.extend([key for key in check_keys if self.zip_ops.get(key, False)])

                for key in to_invoke:
                    index = labels.index(key)
                    menu_master.invoke(index)

            case 'unzip':
                unzip = self.unzip_ops['unzip']
                unzip = 'All files' if unzip == 'all' else 'Selected files'
                index = labels.index(unzip)
                menu_master.invoke(index)
                pass
            case 'unzip settings':
                for key, value in self.unzip_ops.items():
                    if key == 'unzip' or not value:
                        continue
                    index = labels.index(key)
                    menu_master.invoke(index)
            case 'open recent':
                menu_master.config(postcommand=lambda: self.menu_file.fileHist(menu_master))
            case 'recent folders':
                menu_master.config(postcommand=lambda: self.menu_file.fileHist(menu_master, self.last_n_directories))
            case 'filters':
                menu_master.config(postcommand=lambda: self.filters_menu(menu_master))

    def filters_menu(self, menu_inst:tk.Menu):
        lstIndx = menu_inst.index(tk.END) - 1
        menu_inst.delete(1, lstIndx)
        for k, filter in enumerate(self.filters[1:], start=1):
            items = filter.split(';')
            filter = ';'.join([('+-'[k] + item) if item else item for k, item in enumerate(items)])
            menu_inst.insert_radiobutton(
                k,
                label='{} {:30s}'.format(k + 1, filter.strip(';')),
                value=f'{k + 1}',
                variable='zip_filters',
                command=userinterface.menuclick_closure(widget=menu_inst, data=k)
            )
        menu_inst.insert_separator(k + 1)
        menu_inst.entryconfig(k + 2, command=userinterface.menuclick_closure(widget=menu_inst, data=k + 2))

    def destroy(self):
        self.menu_file.checkSaveFlag()
        super().destroy()

    def active_compression_method(self):
        match self.zip_ops['zip_method']:
            case 'max':                             # 'Maxima'
                compression = zipfile.ZIP_BZIP2
            case 'enh':                             # 'Enhance Deflate'
                compression = zipfile.ZIP_DEFLATED
            case 'sup':                             # 'Super Fast'
                compression = zipfile.ZIP_LZMA
            case _:                                 # No Compression
                compression = zipfile.ZIP_STORED
        return compression

    def _loadzip(self, file, mode='r', compression=None, allowZip64=True, compresslevel=None, *, strict_timestamps=True):
        compression = compression or self.active_compression_method()

        method, kw = zipfile.ZipFile, {'compresslevel': compresslevel, 'strict_timestamps': strict_timestamps}
        if self.zip_ops['zip_type'] == 'pyzip':
            method, kw = zipfile.PyZipFile, {'optimize': -1}

        tmpdir = tempfile.gettempdir()
        if mode == 'a':
            try:
                dstfile = shutil.copy(file, tmpdir)
                shutil.copystat(file, dstfile)
            except shutil.SameFileError:
                dstfile = file
        elif mode == 'x':
            filename = os.path.basename(file)
            dstfile = os.path.join(tmpdir, filename)
            if os.path.exists(dstfile):
                os.remove(dstfile)
        self.zf = method(dstfile, mode, compression, allowZip64, **kw)

    def loadzip(self, file, mode='r', compression=None, allowZip64=True, compresslevel=None, *, strict_timestamps=True):
        try:
            self._loadzip(file, mode, compression, allowZip64, compresslevel, strict_timestamps=strict_timestamps)
        except Exception as e:
            tkMessageBox.showerror(title='Loading Error', message=str(e))
        self.menu_file.fileHistory = self.menu_file.recFile(file)
        self.menu_file.title(file)
        self.onVarChange(attr_data=('view_recycle', 0))

    def listzip(self, infolist):
        lst_str = []
        totsize = totcsize = ndir = 0
        for zinfo in infolist:
            if zinfo.is_dir():
                ndir += 1
                date_time = '{0}-{1:0>2d}-{2:0>2d} {3:0>2d}:{4:0>2d}'.format(*zinfo.date_time[:-1])
                data = ('', '', '', '', '', date_time, '', zinfo.filename)
            else:
                filename = zinfo.filename
                if zinfo.flag_bits & 0x1:
                    filename += ' ' + LOCK_CHR
                totsize += zinfo.file_size
                totcsize += zinfo.compress_size
                size = f'{zinfo.file_size:>10d}'
                match zinfo.compress_type:
                    case zipfile.ZIP_DEFLATED:
                        method = 'Deflated'
                    case zipfile.ZIP_STORED:
                        method = 'Stored'
                    case zipfile.ZIP_BZIP2:
                        method = 'BZIP2'
                    case zipfile.ZIP_LZMA:
                        method = 'LZMA'
                compress_size = f'{zinfo.compress_size:>10d}'
                ratio = int(100.0 - 100.0 * zinfo.compress_size // zinfo.file_size) if zinfo.file_size else 0
                ratio = f'{ratio:>2d}'
                date_time = '{0}-{1:0>2d}-{2:0>2d} {3:0>2d}:{4:0>2d}'.format(*zinfo.date_time[:-1])
                CRC = f'{int(zinfo.CRC) if hasattr(zinfo, "CRC") else 0:0>8x}'
                offset = f'{zinfo.header_offset if hasattr(zinfo, "header_offset") else 0: >10d}'
                data = (size, method, compress_size,
                        ratio, offset, date_time, CRC, filename)
            lst_str.append(data)
        return lst_str

    def dumpzip(self, infolist):
        lst_str = []
        lst_str.append(5 * (8 * '-' + ' ') + 16 * '-' + 2 * (' ' + 8 * '-'))
        prtStr1 = '{:^8} {:^8} {:^8} {:^8} {:^8} {:^16} {:^8} {:^8}'
        lst_str.append(prtStr1.format('Length', 'Method', 'Size', 'Ratio', 'Offset', 'Date Time',
                             'CRC-32', 'Name'))
        lst_str.append(5 * (8 * '-' + ' ') + 16 * '-' + 2 * (' ' + 8 * '-'))
        prtStr = '{:8d} {:8} {:8d} {:7d}% {:8d} {:16} {:8} {:8}'
        totsize = totcsize = ndir =0
        for zinfo in infolist:
            if zinfo.is_dir():
                ndir += 1
                continue
            totsize += zinfo.file_size
            totcsize += zinfo.compress_size
            method = 'Deflate' if zinfo.compress_type == zipfile.ZIP_DEFLATED else 'Stored'
            ratio = int(100.0 - 100.0 * zinfo.compress_size // zinfo.file_size) if zinfo.file_size else 0
            date_time = '{0}-{1}-{2} {3}:{4}'.format(*zinfo.date_time[:-1])
            CRC = '{:0>8x}'.format(int(zinfo.CRC))
            data = (zinfo.file_size, method, zinfo.compress_size,
                    ratio, zinfo.header_offset, date_time, CRC, zinfo.filename)
            lst_str.append(prtStr.format(*data))
        ratio = int(100.0 - 100.0 * totcsize // totsize)
        lst_str.append(8 * '-' + 10 * ' ' + 8 * '-' + ' ' + 8 * '-' + 27 * ' ' + 8 * '-')
        prtStr = '{:8}' + 10 * ' ' + '{:8}' + ' ' + '{:7}%' + 27 * ' ' + '{} files'
        lst_str.append(prtStr.format(totsize, totcsize, ratio, len(infolist) - ndir))
        return lst_str

    def selected_data(self):
        if self.rclick_name:
            selected = [self.rclick_name]
        else:
            selected = self.zip_panel.selected_data(col_id='Name')
        selected = [x.rstrip(' ' + LOCK_CHR) for x in selected]
        return selected


def main():
    top = Winzip()
    top.mainloop()


if __name__ == '__main__':
    main()

