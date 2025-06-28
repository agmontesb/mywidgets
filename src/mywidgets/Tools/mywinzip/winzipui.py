import os.path
import shutil
import tkinter as tk
import tkinter.messagebox as tkMessageBox
import tkinter.filedialog as tkFileDialog
import tkinter.simpledialog as tkSimpleDialog
import zipfile
from datetime import datetime
import tempfile

import mywidgets.userinterface as userinterface
import mywidgets.Tools.mywinzip.file_menu as fm
from mywidgets.Widgets import kodiwidgets
from mywidgets.Widgets.Custom import navigationbar
from mywidgets.equations import equations_manager
from mywidgets.Tools.mywinzip.winzipactions import WinzipActions

RECYCLEBIN = '_recyclebin/'
LOCK_CHR = chr(0x0001F512)


class WinzipUI(WinzipActions, tk.Tk):
    def __init__(self):
        super().__init__()
        self.event_add('<<MENUCLICK>>', 'None')
        self.event_add('<<VAR_CHANGE>>', 'None')
        self.bind_all('<<MENUCLICK>>', self.onMenuClick)
        self.bind_all('<<VAR_CHANGE>>', self.onVarChange)
        self.bind_all('<Button-3>', self.onRightClick)
        # self.attributes('-zoomed', True)
        self.state('zoomed')

        self.project_path = '/mnt/c/Users/Alex Montes/PycharmProjects/mywidgets'
        self.menu_file = menu_file = fm.FileMenu(self)
        menu_file.default_file_name = 'newZip.zip'
        menu_file.default_path = '/mnt/c/Users/Alex Montes/Downloads/'
        menu_file.default_extension = '.zip'
        menu_file.default_file_type = ('zip Files', '*.zip')

        self.winzip_ops = {
            'blower': False,
            'bupper': False,
            'bnumeric': False,
            'bother': False,
            'cipher_method': 'zip20',
            'add_folder': 'last_folder',
            'tmp_folder': tempfile.gettempdir(),
            'wrk_folder': '',
            'user_folder': '',
        }

        self.zip_ops = {
            'zip_type': 'zip',
            'zip_method': 'noc',
            'cipher': False,
        }

        self.unzip_ops = {
            'scope': 'all',
            "Ask before file replacement": True,
            "Do not replace new files with early versions": False,
            "Use folder names": True,
            "Show unzip files": False,
            "Last folder": None,
        }
        self.winzip_ops['wrk_folder'] = menu_file.default_path
        self.winzip_ops['user_folder'] = menu_file.default_path

        self.rclick_name = None

        self.last_n_directories = [menu_file.default_path.rstrip(os.sep)]
        src = '@mywinzip:menu/zip_panel_popup'
        selpane = userinterface.getLayout(src)
        self.popUpZip = userinterface.menuFactory(self, selpane, registerMenu=self.registerMenu)

        self.setGui()

        self.file_menu('New')

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

    def registerMenu(self, parent, selPane, menu_master, labels):
        title = menu_master.cget('title')
        match title:
            case 'zip' | 'zip method':
                radio_keys = ('zip_file',) if title == 'zip' else ('zip_method', )
                to_invoke = [self.zip_ops[key] for key in radio_keys]

                check_keys = ('cipher', ) if title == 'zip' else []
                to_invoke.extend([key for key in check_keys if self.zip_ops.get(key, False)])

                for key in to_invoke:
                    index = labels.index(key)
                    menu_master.invoke(index)

            case 'unzip':
                unzip = self.unzip_ops['scope']
                unzip = 'All files' if unzip == 'all' else 'Selected files'
                index = labels.index(unzip)
                menu_master.invoke(index)
                pass
            case 'unzip settings':
                onkeys = (key for key, value in self.unzip_ops.items() if value)
                for key in onkeys:
                    index = labels.index(key)
                    menu_master.invoke(index)
            case 'open recent':
                menu_master.config(postcommand=lambda: self.menu_file.fileHist(menu_master))
            case 'recent folders':
                menu_master.config(postcommand=lambda: self.menu_file.fileHist(menu_master, self.last_n_directories))
            case 'filters':
                menu_master.config(postcommand=lambda: self.filters_menu(menu_master))

    def register_widget(self, master, xmlwidget, widget):
        attribs = xmlwidget.attrib
        name = attribs.get('name')
        if name in ('lframe', 'rframe', 'zip_panel', 'files_panel',):
            setattr(self, name, widget)
        pass

    def filters_menu(self, menu_inst: tk.Menu):
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

    def onVarChange(self, event=None, attr_data=None):
        if event:
            attr_data = event.attr_data
        var_name, value = attr_data
        match var_name:
            case 'zip_type':
                self.zip_ops[var_name] = value
                self.zip_type = value
            case 'zip_method':
                self.zip_ops[var_name] = value
                self.set_compression_method(value)
            case 'cipher':
                self.zip_ops[var_name] = value
            case 'unzip_scope':
                self.unzip_ops['scope'] = value
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

    def onMenuClick(self, event):
        menu_master, indx = event.widget, event.data
        menu, menu_item = menu_master.cget("title"), menu_master.entrycget(indx, "label")
        if menu in ('file', 'open recent'):
            self.file_menu(menu_item)
        elif menu in ('unzip', 'unzip settings'):
            self.unzip_menu(menu_item)
        elif menu in ('zip', 'zip method'):
            self.zip_menu(menu_item)
        elif menu in ('manage',):
            self.manage_menu(menu_item)
        elif menu == 'popupzippanel':
            self.pop_up_zip(menu_item)
        elif menu == 'filters':
            menu_item = menu_item.split(' ', 1)
            self.zip_menu(menu_item)
        elif menu == 'recent folders':
            menu_item = menu_item.split(' ', 1)
            self.unzip_menu(menu_item)
        pass

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

    def file_menu(self, menu_item):
        match menu_item.split():
            case 'New', :
                with self.menu_file.newFile():
                    filename = os.path.join(self.menu_file.default_path, self.menu_file.default_file_name)
                    if os.path.exists(filename):
                        os.remove(filename)
                    self.loadzip(filename, mode='x')
            case 'Open',:
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
            case 'Save', *suffix:  # case 'Save' | 'Save As':
                method = getattr(self.menu_file, 'saveFile' if not suffix else 'saveAsFile')
                with method() as filename:
                    try:
                        self.save(filename)
                        self.menu_file.title(filename)
                    except Exception as e:
                        tkMessageBox.showerror(title='Saving Error', message=str(e))
            case 'Settings', :
                title = 'Winzip Settings'
                xmlfile = userinterface.getContent('@mywinzip:layout/dlg_settings')
                dlg = kodiwidgets.CustomDialog(
                    self,
                    title=title, xmlFile=xmlfile, isFile=False, settings=self.winzip_ops, dlg_type='okcancel'
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
            case prefix, _ if prefix.isdigit():
                dest_path = self.last_n_directories[int(prefix) - 1]
                menu_item = 'Same folder'
            case _:
                title = f'Unzip Menu - Option: {menu_item}'
                tkMessageBox.showinfo(title=title, message='Not implemented yet')

        if menu_item in ('Same folder', 'Last folder', 'My PC'):
            self.interactive_extract(dest_path)

    def interactive_extract(self, dest_path):
        use_folder = self.unzip_ops["Use folder names"]
        ask_before = self.unzip_ops["Ask before file replacement"]
        unzip_selected = self.unzip_ops['scope'] == 'selected'
        pwd = None
        if self.zip_ops['cipher']:
            if self.zf.pwd is None:
                pwd = tkSimpleDialog.askstring(title='Password',
                                               prompt='Please enter the zip file password', show='*')
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
        xmlfile = '@mywinzip:layout/unzip_dlg'
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
                dlg = kodiwidgets.CustomDialog(self, title=title, xmlFile=xmlfile, isFile=True,
                                               settings=settings, dlg_type='ok')
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
            try:
                self.extract(zinfo, dest_filename, pwd)
            except Exception as e:
                msg = str(e)
                tkMessageBox.showerror(title='Unzip - Not valid', message=msg)
        self.unzip_ops['Last folder'] = dest_path
        self.last_n_directories = self.menu_file.recFile(dest_path, self.last_n_directories)

    def zip_menu(self, menu_item):
        match menu_item:
            # case 'cipher':
            #     self.zip_ops['cipher'] = not self.zip_ops['cipher']

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
                unzip = self.unzip_ops['scope']
                self.unzip_ops['scope'] = 'selected'
                self.interactive_extract(dest_path)
                self.unzip_ops['scope'] = unzip
                if menu_item == 'Move To':
                    selected = self.selected_data()
                    items = self.delete_items(selected)
                    self.onVarChange(attr_data=('view_recycle', 0))
                    self.menu_file.setSaveFlag(True)
                    msg = f'{len(items)} items has been moved to Recycle Bin'
                    tkMessageBox.showinfo(title='Delete', message=msg)
            case 'Delete':
                if selected := self.selected_data():
                    msg = '\n'.join(['Do you want to delete the following items:', *selected])
                    bflag = tkMessageBox.askokcancel(title='Delete Zip File Item', message=msg)
                    if bflag:
                        items = self.delete_items(selected)
                        self.onVarChange(attr_data=('view_recycle', 0))
                        self.menu_file.setSaveFlag(True)
                        msg = f'{len(items)} items has been moved to Recycle Bin'
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
                        items = self.restore_items(selected)
                        self.onVarChange(attr_data=('view_recycle', 1))
                        msg = f'{len(items)} items has been restore'
                        tkMessageBox.showinfo(title='Restore', message=msg)
            case 'New Folder':
                title = 'New Folder'
                prompt = 'Name of the new folder to create:'
                name = tkSimpleDialog.askstring(title, prompt)
                if name:
                    zip_path = self.zip_panel.tree_path.getActivePath().path
                    filename = os.path.join(zip_path, name, '')
                    date_time = datetime.now().timetuple()[:6]
                    self.create_folder(filename, date_time)
                    self.onVarChange(attr_data=('view_recycle', 0))
                    self.menu_file.setSaveFlag(True)
                pass
            case 'Select All':
                self.zip_panel.onSelectAll()
            case 'Toggle Selection':
                self.zip_panel.onToggleSel()
            case _:
                title = f'Manage Menu - Option: {menu_item}'
                tkMessageBox.showinfo(title=title, message='Not implemented yet')

    def selected_data(self):
        if self.rclick_name:
            selected = [self.rclick_name]
        else:
            selected = self.zip_panel.selected_data(col_id='Name')
        selected = [x.rstrip(' ' + LOCK_CHR) for x in selected]
        return selected

    def _addFiles(self, files, zip_files=None, directory=False):
        tree_path = self.zip_panel.tree_path
        root_dir = tree_path.path_obj.root
        zip_path = tree_path.getActivePath().path
        zip_path = os.path.relpath(zip_path, root_dir).lstrip('.')
        try:
            self.addFiles(files, zip_files, directory, dest_folder=zip_path)
        except Exception as e:
            tkMessageBox.showerror(title='Add Files Error', message=str(e))
            return
        self.onVarChange(attr_data=('view_recycle', 0))
        self.menu_file.setSaveFlag(True)

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

    def destroy(self):
        self.menu_file.checkSaveFlag()
        super().destroy()


def main():
    wz = WinzipUI()
    wz.mainloop()


if __name__ == '__main__':
    main()



