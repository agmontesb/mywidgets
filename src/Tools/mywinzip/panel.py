import os.path
import tkinter as tk
import tkinter.messagebox as tkMessageBox
import zipfile

import userinterface
from Widgets.Custom import navigationbar


class Panel(tk.Frame):

    def __init__(self, master, *, name=None, column_ids='', path_obj=None, text='text'):
        tk.Frame.__init__(self, master, name=name)
        self.setGUI(column_ids)
        self.text = text
        if path_obj:
            self.path_obj = path_obj
        self.icons_col = None
        self.records = None
        self.root_dir = None
        self._group_by = False
        pass

    def setGUI(self, column_ids):
        file_path = 'Tools/mywinzip/res/layout/panel.xml'
        xmlObj = userinterface.getLayout(file_path, withCss=True)
        userinterface.newPanelFactory(
            master=self,
            selpane=xmlObj,
            genPanelModule=None,
            setParentTo='master',
            registerWidget=self.register_widget,
        )

        tree = self.tree
        tree['columns'] = column_ids
        for column in column_ids.split(' '):
            tree.heading(column, text=column, anchor=tk.W)
            tree.column(column, stretch=1, width=100)
        tree.tag_configure('selected', background='light green')
        tree.bind('<<TreeviewOpen>>', self.onTreeViewOpen)
        tree.bind('<<ActiveSelection>>', self.onTreeSelection, '+')

        canvas = self.tree_path
        canvas.tag_bind('arrow', '<Button-1>', self.onCanvasClickEvent)

    def register_widget(self, master, xmlwidget, widget):
        attribs = xmlwidget.attrib
        name = attribs.get('name')
        if name in ('name', 'tree_path', 'tree',):
            setattr(self, name, widget)
        if name == 'groupby':
            widget.config(command=self.onGroupBy)
        if name == 'selectall':
            self.selectall = widget
            widget.config(command=self.onSelectAll)

    def onCanvasClickEvent(self, event):
        canvas = event.widget
        x, y = event.x, event.y
        pfocus = canvas.identify_index(x, y)
        if pfocus is not None:
            canvas.set_active_index(pfocus)
            path = self.tree_path.getActivePath().path
            self.onTreeViewOpen(path=path)

    def onTreeViewOpen(self, event=None, *, path=None):
        tree = self.tree
        if event is not None:
            iid = tree.focus()
            lpath = tree.item(iid, 'text')
            root = self.tree_path.getActivePath().path
            path = os.path.join(root, lpath)
        assert path is not None

        tree.delete(*tree.get_children(''))
        root, d_names, f_names = next(self.path_obj.walk(path))
        root = root.rstrip('/')
        path_id = ''
        for k, names in enumerate((d_names, f_names)):
            suffix = (os.sep, '')[k]
            for name in names:
                filename = os.path.join(root, name) + suffix
                indx = self.icons_col.index(filename)
                row = self.records[indx]
                child_id = tree.insert(
                    path_id,
                    'end',
                    text=name,
                    values=row,
                )
                if filename.endswith(os.sep):
                    tree.insert(child_id, 'end', text='dummy')
        self.selectall.deselect()
        self.tree_path.setActivePath(root)

    def onGroupBy(self):
        self.selectall.deselect()
        self.groupby = not self.groupby

    def onSelectAll(self):
        tree = self.tree
        selection = tree.get_children('')
        selected = tree.tag_has('selected')
        bflag = len(selection) != len(selected)
        if bflag:
            tag = 'selected'
        else:
            tag = ''
            self.selectall.deselect()
        [tree.item(iid, tags=tag) for iid in selection]

    def selected_data(self, col_id='values'):
        tree = self.tree
        selected = tree.tag_has('selected')
        data = []
        method = tree.item
        if col_id != 'values':
            method = tree.set
        for iid in selected:
            data.append(method(iid, col_id))
        return data

    def onToggleSel(self):
        tree = self.tree
        selection = tree.get_children('')
        selected = tree.tag_has('selected')
        selection = set(selection).difference(selected)
        [tree.item(iid, tags='selected') for iid in selection]
        [tree.item(iid, tags='') for iid in selected]
        if not selected:
            self.selectall.select()
        if not selection:
            self.selectall.deselect()

    def onTreeSelection(self, event):
        tree = event.widget
        selection = tree.get_children('')
        selected = tree.tag_has('selected')
        bflag = len(selection) != len(selected)
        if bflag:
            self.selectall.deselect()
        else:
            self.selectall.select()

    def tree_data(self, root_dir, icons_col, records, groupby=False, mode='replace'):
        match mode:
            case 'replace':
                self.text = root_dir.strip('/')
                self.icons_col = icons_col
                self.records = records
                self.path_obj = navigationbar.StrListObj(icons_col, root_dir)
            case 'add':
                path = self.tree_path.getActivePath().path
                self.icons_col.extend(icons_col)
                self.records.extend(records)
                root_dir = self.path_obj.root
                icons_col = self.icons_col
                self.path_obj = navigationbar.StrListObj(icons_col, root_dir)
                # self.onTreeViewOpen(path=path)
                groupby = self.groupby
        self.groupby = groupby

    @property
    def text(self):
        return self.name['text']

    @text.setter
    def text(self, text):
        self.name['text'] = text

    @property
    def path_obj(self):
        return self.tree_path.path_obj

    @path_obj.setter
    def path_obj(self, obj):
        self.tree_path.path_obj = obj

    @property
    def groupby(self):
        return self._group_by

    @groupby.setter
    def groupby(self, bflag):
        tree = self.tree
        tree.delete(*tree.get_children(''))
        self._group_by = bflag
        if not bflag:
            tree['displaycolumns'] = '#all'
            tree['show'] = 'headings'
            for icon, row in zip(self.icons_col, self.records):
                if icon.endswith(os.sep):
                    continue
                tree.insert('', 'end', values=row)
            root = self.path_obj.root
            self.tree_path.setActivePath(root)
        else:
            tree['displaycolumns'] = '#all'
            tree['show'] = 'tree headings'
            root_dir = self.path_obj.root
            self.onTreeViewOpen(path=root_dir)
            pass



def listzip(infolist):
    lst_str = []
    totsize = totcsize = ndir =0
    for zinfo in infolist:
        if zinfo.is_dir():
            ndir += 1
            date_time = '{0}-{1:0>2d}-{2:0>2d} {3:0>2d}:{4:0>2d}'.format(*zinfo.date_time[:-1])
            data = ('', '', '', '', '', date_time, '', zinfo.filename)
        else:
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
                    ratio, offset, date_time, CRC, zinfo.filename)
        lst_str.append(data)
    return lst_str


def main():
    top = tk.Tk()
    top.attributes('-zoomed', True)
    # chk = tk.Checkbutton(top, text='groupby', command=lambda: setattr(panel, 'groupby', not panel.groupby))
    # chk.pack(side=tk.TOP, fill=tk.X)
    panel = Panel(
        top,
        path_obj='/mnt/c/',
        text='PRUEBA',
        column_ids="Length Method Size Ratio Offset DateTime CRC32 Name",
    )
    panel.pack(side=tk.TOP, fill=tk.BOTH, expand=tk.YES)

    filename = '/mnt/c/users/Alex Montes/Downloads/app.zip'
    zf = zipfile.ZipFile(filename)
    root = f'/{os.path.basename(filename)}'
    namelist = [os.path.join(root, x) for x in zf.namelist()]
    records = listzip(zf.infolist())
    panel.tree_data(root, namelist, records)

    top.mainloop()


if __name__ == '__main__':
    main()
