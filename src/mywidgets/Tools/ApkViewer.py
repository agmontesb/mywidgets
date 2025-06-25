import io
import os
import sys
import tkinter as tk
import tkinter.messagebox as tkMessageBox
import tkinter.filedialog as tkFileDialog
import ctypes
import zipfile

import userinterface
import Tools.aapt as aapt
from equations import equations_manager


class ApkViewer(tk.Tk):
    def __init__(self):
        super().__init__()
        self.event_add('<<MENUCLICK>>', 'None')
        self.event_add('<<VAR_CHANGE>>', 'None')
        self.bind_all('<<MENUCLICK>>', self.onMenuClick)
        self.bind_all('<<VAR_CHANGE>>', self.onVarChange)
        self.fileHistory = []

        self.setGui()

        self.attributes('-zoomed', True)

        # Contenido habilitado solo para desarrolllo
        #
        # initial_path = '/mnt/c/Users/Alex Montes/PycharmProjects/TestFiles'
        # filename = 'TeaTV-v9.9.6r_build_111-Mod_v2.apk'
        # filename = os.path.join(initial_path, filename)
        # self.init_UI_View(filename)
        # self.cframe.show_band()
        pass

    def setGui(self):
        file_path = 'Data/tkinter/tkApkViewer.xml'
        xmlObj = userinterface.getLayout(file_path)
        fframe = tk.Frame(self, name='fframe')
        userinterface.newPanelFactory(
            master=fframe,
            selpane=xmlObj,
            genPanelModule=None,
            setParentTo='master',
            registerWidget=self.register_widget,
        )
        equations_manager.set_initial_widget_states()
        fframe.pack(side=tk.TOP, fill=tk.BOTH, expand=tk.YES, anchor=tk.NE)

        # self.cframe.hide_band('left')

        self.apktree.bind('<<ActiveSelection>>', self.onActiveSelection, add='+')
        self.apktree.tag_configure('selected', background='light green')

        self.rawtree.bind('<<ActiveSelection>>', self.onRawActiveSelection, add='+')
        self.rawtree.tag_configure('selected', background='red')

        self.fields.bind('<<ActiveSelection>>', self.onFieldActiveSelection)
        self.fields.tag_configure('selected', background='red')

        self.textw = self.output.textw
        self.textw.tag_config('selected', background='light green')
        self.textw.tag_config('chunk', foreground='red')

        def fileHist():
            menu_name = self.recents_file_menu
            lstIndx = menu_name.index(tk.END)
            menu_name.delete(0, lstIndx)
            for k, filename in enumerate(self.fileHistory, start=1):
                flabel = os.path.basename(filename)
                menu_name.insert_command(
                    k,
                    label='{} {:30s}'.format(k, flabel),
                    command=lambda x=filename: self.init_UI_View(x)
                )
        self.recents_file_menu.config(postcommand=fileHist)

    def register_widget(self, master, xmlwidget, widget):
        attribs = xmlwidget.attrib
        name = attribs.get('name')
        if name:
            if name in ('apktree', 'apk_path', 'rawtree', 'output', 'fields', 'cframe'):
                setattr(self, name, widget)
            elif name == 'main_menu':
                menu_name = widget.children['master'].entrycget(1, 'menu')
                recents_file_menu = widget.nametowidget(menu_name)
                setattr(self, 'recents_file_menu', recents_file_menu)
                pass

    def onRawActiveSelection(self, event):
        rawtree = event.widget
        selected = rawtree.tag_has('selected')
        [rawtree.item(nodeid, tags='') for nodeid in selected]

        nodeid = rawtree.focus()
        rawtree.item(nodeid, tags='selected')

        type_name, offset, t_size = rawtree.item(nodeid, 'values')
        offset = int(offset)
        t_size = int(t_size)
        t_loff = offset % 16

        self.data.seek(0)
        p1 = offset
        p2 = p1 + t_size  # ctypes.sizeof(ctype_struct)
        t_offset = 16 * (p1 // 16)
        size = min(16 * (p2 // 16 + 1), sys.getsizeof(self.data)) - t_offset
        out_string = []
        aapt.dumpHexData(self.data, offset=t_offset, size=size, to_string=out_string)
        self.output.setContent(
            (''.join(out_string), 'txt', ''),
            inspos='1.0',
        )
        self.setOutputTag(0, t_loff, t_size, tag='chunk')

        if not len(rawtree.get_children(nodeid)):
            # Solo se presenta la info para nodos terminales (sin hijos)
            self.setFieldsTree(type_name, offset)

    def setFieldsTree(self, type_name, offset):

        self.data.seek(0)
        ctype_struct = self.header_for_type(type_name)

        ctypeStruct_inst = aapt.ru.readResHeader(self.data, ctype_struct, offset=offset)
        table = aapt.ctypeInstanceTable(ctypeStruct_inst)
        if ctype_struct == aapt.ResourcesTypes.ResXMLTree_node:
            d_offset = ctypeStruct_inst.header.headerSize
            data_header_ctype_struct = self.header_for_data(type_name)
            lprefix = data_header_ctype_struct.__name__
            ctypeStruct_inst = aapt.ru.readResHeader(self.data, data_header_ctype_struct, offset=offset + d_offset)
            table.append((lprefix, None, d_offset // 16, d_offset % 16, ctypes.sizeof(ctypeStruct_inst)))
            data_header = aapt.ctypeInstanceTable(ctypeStruct_inst, shift=d_offset, lprefix=lprefix)
            table += data_header

            if data_header_ctype_struct == aapt.ResourcesTypes.ResXMLTree_attrExt:
                data_header_ctype_struct = aapt.ru.ResXMLTree_attribute
                d_offset += ctypeStruct_inst.attributeStart
                items = ctypeStruct_inst.attributeCount
                for item in range(items):
                    lprefix = data_header_ctype_struct.__name__
                    ctypeStruct_inst = aapt.ru.readResHeader(self.data, data_header_ctype_struct, offset=offset + d_offset)
                    table.append((lprefix, None, d_offset // 16, d_offset % 16, ctypes.sizeof(ctypeStruct_inst)))
                    data_header = aapt.ctypeInstanceTable(ctypeStruct_inst, shift=d_offset, lprefix=lprefix)
                    table += data_header
                    d_offset += ctypes.sizeof(ctypeStruct_inst)

        self.setCtypeStructFields(table, offset)

    def setOutputTag(self, saddr, loff, size, tag='selected'):
        selected = self.textw.tag_ranges(tag)
        [
            self.textw.tag_remove(tag, beg_ndx, end_ndx)
            for beg_ndx, end_ndx in zip(selected[::2], selected[1::2])
        ]

        saddr += 5          # 5 es el número de líneas del encabezado mas 1
        lines = (loff + size) // 16
        nchar = (loff + size) % 16
        selected = []
        beg_ndx = f'{saddr}.{3 * loff + 9}'
        self.textw.see(beg_ndx)
        if lines == 0:
            end_ndx = f'{saddr}.{3 * nchar + 9 - 1}'
            selected.append((beg_ndx, end_ndx))
        else:
            end_ndx = f'{saddr}.{3 * 16 + 9 - 1}'
            selected.append((beg_ndx, end_ndx))
            for line in range(1, lines):
                beg_ndx = f'{saddr + line}.{9}'
                end_ndx = f'{saddr + line}.{3*16 + 9 - 1}'
                selected.append((beg_ndx, end_ndx))
            beg_ndx = f'{saddr + lines}.{9}'
            end_ndx = f'{saddr + lines}.{3 * nchar + 9 - 1}'
            selected.append((beg_ndx, end_ndx))

        for beg_ndx, end_ndx in selected:
            self.textw.tag_add(tag, beg_ndx, end_ndx)

    def onFieldActiveSelection(self, event=None):
        fields_table = event.widget
        selected = fields_table.tag_has('selected')
        for nodeid in selected:
            fields_table.item(nodeid, tags='')
        nodeid = fields_table.focus()
        fields_table.item(nodeid, tags='selected')
        _, _, saddr, loff, size = fields_table.item(nodeid, 'values')


        saddr, loff, size = int(saddr, 16) // 16, int(loff, 16), int(size)
        self.setOutputTag(saddr, loff, size)

    def onActiveSelection(self, event=None):
        apktree = event.widget
        selected = apktree.tag_has('selected')
        [apktree.item(nodeid, tags='') for nodeid in selected]

        nodeid = apktree.focus()
        apktree.item(nodeid, tags='selected')

        label = apktree.item(nodeid, 'text')
        try:
            ext = '.' + label.rsplit('.', 1)[1]
        except:
            ext = ''
        self.setvar('show_var', 'true' if ext in ('.arsc', '.xml') else 'false')
        view = self.getvar('vis_var')
        self.fillOutputWidget(view)

    def fillOutputWidget(self, view):
        apk_path_obj = self.apk_path
        path = apk_path_obj.getActivePath().path
        path = path.lstrip('/')
        try:
            self.data = data = io.BytesIO(self.zf.read(path))
        except:
            return
        out_string = []
        if view == 'text':
            _, ext = os.path.splitext(path)
            if ext == '.xml':
                aapt.dumpXmlTree(data, to_string=out_string)
            elif ext == '.arsc':
                assert path == 'resources.arsc'
                aapt.dumpResources(data, what='resources', to_string=out_string)
            else:
                try:
                    out_string = [x.decode('utf-8') for x in data.readlines()]
                except:
                    out_string = ['CONTENIDO NO DISPONIBLE\n']
        elif view == 'raw':
            out_string = []
            aapt.dumpHexData(data, to_string=out_string)
            self.setUpRawTree(path, data)
        self.output.setContent(
            (''.join(out_string), 'txt', ''),
            inspos='1.0',
        )

    def onVarChange(self, event):
        var_name, value = event.attr_data
        # print(f'var_change: var_name: {var_name}, value: {value}')
        if var_name == 'vis_var':
            self.fillOutputWidget(value)
        if var_name in ('vis_var', 'show_var'):
            bflag = self.getvar('vis_var') == 'text' or self.getvar('show_var') == 'true'
            if bflag:
                self.cframe.show_band()
            else:
                self.cframe.hide_band('left')

    def onMenuClick(self, event):
        menu_master, indx = event.widget, event.data
        menu_label = menu_master.entrycget(indx, "label").lower()
        if menu_label == 'open':
            initial_path = '/mnt/c/Users/Alex Montes/PycharmProjects/TestFiles'
            filename = tkFileDialog.askopenfilename(
                initialdir=initial_path,
                filetypes=[('apk Files', '*.apk'), ('All Files', '*.*')]
            )
            if not filename:
                return
            filename = os.path.join(initial_path, filename)
            try:
                self.init_UI_View(filename)
                self.recFile(filename)
                self.title(filename)
            except:
                pass
            self.apk_path.setActivePath('/AndroidManifest.xml')
        else:
            msg = f'MENUCLICK fire. Menu: {menu_master.cget("title")}, Menu_item:{menu_label}'
            print(msg)
            tkMessageBox.showinfo(title='on_menuclick', message=msg)

    def recFile(self, filename):
        try:
            ndx = self.fileHistory.index(filename)
            self.fileHistory.pop(ndx)
        except:
            pass
        self.fileHistory.insert(0, filename)
        nmax = 5
        self.fileHistory = self.fileHistory[:nmax]

    def setCtypeStructFields(self, table, offset):
        tree = self.fields
        tree.delete(*tree.get_children())
        for label, value, saddr, loff, size in table:
            value = None if value in (0xff, 0xffff, 0xffffffff, 0xffffffffffffffff) else value
            abs_offset = offset + 16 * saddr + loff
            saddr = abs_offset // 16 - offset // 16
            left_offset = abs_offset % 16
            row = (label, value, f'{16 * saddr:0>8x}', f'{left_offset:0>2x}', size)
            tree.insert('', 'end', values=row)

    def init_UI_View(self, apkname):
        tree = self.apktree
        tree.delete(*tree.get_children())

        parent_id_map = {'': ''}
        self.zf = zf = zipfile.ZipFile(apkname)
        path = ''
        for root, d_names, f_names in self.walk_apk(path, zf):
            root = root.rstrip('/')
            path_id = parent_id_map[root]
            for f_name in f_names:
                tree.insert(
                    path_id,
                    'end',
                    text=f_name,
                )
            for d_name in d_names:
                child_id = tree.insert(
                    path_id,
                    'end',
                    text=d_name,
                )
                path = f'{root}/{d_name}'.lstrip('/')
                parent_id_map[path] = child_id

        iid, = [iid for iid in tree.get_children('') if tree.item(iid, 'text') == 'AndroidManifest.xml']
        tree.focus(iid)
        pass

    # Metodos que operan sobre el archivo.

    @staticmethod
    def walk_apk(start_path, zf):
        stack = [start_path]
        namelist = set(zf.namelist())
        path = ''
        while stack:
            dummy = stack.pop(0)
            while isinstance(dummy, int):
                npos = dummy
                path = path[:npos]
                dummy = stack.pop(0)
                if stack and not isinstance(stack[0], int):
                    stack.insert(0, npos)
            path = f'{path.rstrip("/")}/{dummy}/'.lstrip('/')
            files = []
            dirs = set()
            n = len(path)
            for info in namelist:
                if info.startswith(path):
                    suffix = info[n:]
                    try:
                        prefix, suffix = suffix.split('/', 1)
                        dirs.add(prefix)
                    except:
                        files.append(suffix)
            dirs = sorted(dirs)
            files.sort()
            yield path, dirs, files
            to_purge = [f'{path}{dummy}'.lstrip('/') for dummy in files]
            namelist.difference_update(to_purge)
            if len(dirs) > 1:
                dirs.insert(1, len(path))
            stack = dirs + stack

    @staticmethod
    def header_for_type(chunk_type):
        if chunk_type == 'RES_TABLE_TYPE':
            class_name = 'ResTable_header'
        elif chunk_type == 'RES_TABLE_LIBRARY_TYPE':
            class_name = 'ResTable_lib_header'
        elif chunk_type.startswith('RES_TABLE_'):
            prefix, *suffix = chunk_type.split('_')[2:-1]
            class_name = ''.join([prefix.lower(), *map(lambda x: x.title(), suffix)])
            class_name = f'ResTable_{class_name}'
        elif chunk_type == 'RES_STRING_POOL_TYPE':
            class_name = 'ResStringPool_header'
        elif chunk_type.startswith('RES_XML_'):
            class_name = 'ResXMLTree_node' if chunk_type != 'RES_XML_RESOURCE_MAP_TYPE' else 'ResChunk_header'
        else:
            class_name = 'ResXMLTree_header'
        return getattr(aapt.ResourcesTypes, class_name)

    @staticmethod
    def header_for_data(chunk_type):
        if chunk_type.startswith('RES_XML_'):
            if chunk_type == 'RES_XML_START_ELEMENT_TYPE':
                class_name = 'ResXMLTree_attrExt'
            elif chunk_type != 'RES_XML_RESOURCE_MAP_TYPE':
                pini = 2 if not 'NAMESPACE' in chunk_type else 3
                # RES_XML_END_ELEMENT_TYPE -> ResXMLTree_endElementExt
                # RES_XML_CDATA_TYPE -> ResXMLTree_cdataExt
                # RES_XML_START_NAMESPACE_TYPE -> ResXMLTree_namespaceExt
                # RES_XML_END_NAMESPACE_TYPE -> ResXMLTree_namespaceExt
                prefix, *suffix = chunk_type.split('_')[pini: -1]
                class_name = ''.join([prefix.lower(), *map(lambda x: x.title(), suffix)])
                class_name = f'ResXMLTree_{class_name}Ext'
            else:
                class_name = 'ResXMLTree_header'
        return getattr(aapt.ResourcesTypes, class_name)

    def setUpRawTree(self, path, data):
        _, case = os.path.splitext(path)
        if case in ('.arsc', '.xml'):
            self.crawl_resources_arsc(data, self.rawtree)
            self.setvar('show_var', 'true')
            # self.cframe.show_band()
        else:
            self.setvar('show_var', 'false')
            # self.cframe.hide_band('left')
        pass

    @staticmethod
    def crawl_resources_arsc(data, tree):
        tree.delete(*tree.get_children())

        gcrawl = aapt.GenCrawler()
        k = 0
        parent_stack = ['']
        for nstack, file_pos, rch in gcrawl.crawl(data, offset=k):
            caption = f'{rch.typeName}'
            if rch.typeName == 'RES_TABLE_TYPE_TYPE':
                rtt = aapt.ResourcesTypes.readResHeader(data, aapt.ResourcesTypes.ResTable_type, offset=file_pos)
                caption = f'({rtt.config.toString()}) {caption}'

            parent_id = parent_stack[nstack]
            child_id = tree.insert(
                parent_id,
                'end',
                text=caption,
                values=(rch.typeName, file_pos, rch.size)
            )
            parent_stack = parent_stack[:nstack + 1]
            parent_stack.append(child_id)



def main():
    top = ApkViewer()
    top.mainloop()

if __name__ == '__main__':
    main()
