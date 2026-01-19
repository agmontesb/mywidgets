import os.path
import queue
import threading
import tkinter as tk
import zipfile
from datetime import datetime

import mywidgets.userinterface as userinterface
from mywidgets.Widgets.Custom import navigationbar


class Panel(tk.Frame):

    def __init__(self, master, *, name=None, column_ids='', path_obj=None, text='text'):
        tk.Frame.__init__(self, master, name=name)
        self.mutex = threading.Event()
        self.queue = None        # queue.Queue(maxsize=0)
        self.thread_id = None
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
        tree.bind('<Escape>', self.onEscape)

        canvas = self.tree_path
        canvas.tag_bind('arrow', '<Button-1>', self.onCanvasClickEvent)

        self.loading_widget = tk.Label(
            self.tree,
            text="Loading data.\nPress escape to cancel",
            background='white',
            font=('Helvetica', 20),
            justify=tk.LEFT
        )


    def onEscape(self, event):
        self.cancel()

    def cancel(self):
        self.loading_widget.place_forget()
        self.mutex.clear()
        with self.queue.mutex:
            self.queue.queue.clear()

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

    def tree_elements(self, path, only_files=False):
        if only_files:
            for root, _, f_names in self.path_obj.walk(path):
                if not self.mutex.is_set():
                    break
                for name in f_names:
                    filename = self.path_obj.join(root, name)
                    self.queue.put((filename, name))
        else:
            root, d_names, f_names = next(self.path_obj.walk(path))
            for k, names in enumerate((d_names, f_names)):
                if not self.mutex.is_set():
                    break
                suffix = self.path_obj.SEP if k == 0 else ''
                for name in names:
                    filename = self.path_obj.join(root, name) + suffix
                    self.queue.put((filename, name))
        self.mutex.clear()

    def update_tree(self):
        BATCH_SIZE = 100
        if self.queue.empty():
            if not self.mutex.is_set():
                self.loading_widget.place_forget()
            return
        tree = self.tree
        path_id = ''
        nitems = 0
        while not self.queue.empty() and nitems < BATCH_SIZE:
            nitems += 1
            filename, name = self.queue.get()
            row = self.records(filename)
            child_id = tree.insert(
                path_id,
                'end',
                text=name,
                values=row,
            )
            if filename.endswith(self.path_obj.SEP):
                tree.insert(child_id, 'end', text='dummy')
        prefix, suffix = self.loading_widget['text'].split('\n')
        ndots = prefix.count('.')
        ndots = (ndots + 1) % 11
        prefix = 'Loading data' + ndots * '.'
        txt = f'{prefix}\n{suffix}'
        self.loading_widget['text'] = txt
        if self.mutex.is_set():
            self.after(100, self.update_tree)
        else:
            self.loading_widget.place_forget()

    def onTreeViewOpen(self, event=None, *, path=None):
        tree = self.tree
        if event is not None:
            iid = tree.focus()
            lpath = tree.item(iid, 'text')
            root = self.tree_path.getActivePath().path
            path = self.path_obj.join(root, lpath)
        assert path is not None
        tree.delete(*tree.get_children(''))
        path = self.path_obj.validate_path(path)
        bflag = not self.groupby
        self.queue = queue.Queue(maxsize=0)

        self.mutex.set()
        self.thread_id = threading.Thread(
            target=self.tree_elements,
            args=(path,),
            kwargs=dict(only_files=bflag),
        )
        self.thread_id.start()
        self.loading_widget.place(relx=.5, rely=.5, anchor=tk.CENTER)
        tree.focus_set()
        print(self.focus_get())
        self.after(100, self.update_tree)

        self.selectall.deselect()
        self.selectall.configure(text='Select All')
        self.tree_path.setActivePath(path)

    def onGroupBy(self):
        self.selectall.deselect()
        self.selectall.configure(text='Select All')
        self.groupby = not self.groupby

    def onSelectAll(self):
        tree = self.tree
        selection = tree.get_children('')
        selected = tree.tag_has('selected')
        if len(selected) == 0:
            tag = 'selected'
            nitems = len(selection)
            self.selectall.configure(text=f'{nitems} Item(s) selected')
        else:
            tag = ''
            self.selectall.deselect()
            self.selectall.configure(text='Select All')
        [tree.item(iid, tags=tag) for iid in selection]

    def selected_data(self, col_id='values'):
        tree = self.tree
        selected = tree.tag_has('selected')
        data = []
        method = tree.item if col_id == 'values' else tree.set
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
            nitems = len(selection)
            self.selectall.select()
            self.selectall.configure(text=f'{nitems} Item(s) selected')
        if not selection:
            self.selectall.deselect()
            self.selectall.configure(text='Select All')

    def onTreeSelection(self, event):
        tree = event.widget
        selection = tree.get_children('')
        selected = tree.tag_has('selected')
        nitems = len(selected)
        self.selectall.select()
        self.selectall.configure(text=f'{nitems} Item(s) selected')

    def tree_data(self, path_obj, records, groupby=None):
        if groupby is None:
            groupby = self.groupby
        self.text = path_obj.root.strip('/')
        self.records = records
        self.path_obj = path_obj
        wdg_name = f'{str(self)}.chk_btns_frm.groupby'
        wdg = self.nametowidget(wdg_name)
        fnc = wdg.select if groupby else wdg.deselect
        fnc()
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

        tree['displaycolumns'] = '#all'
        tree['show'], path = ('tree headings', self.tree_path.getActivePath().path) if bflag else ('headings', self.path_obj.root)
        self.onTreeViewOpen(path=path)


def zipinfo_record(zinfo):
    if zinfo.is_dir():
        ndir += 1
        date_time = '{0}-{1:0>2d}-{2:0>2d} {3:0>2d}:{4:0>2d}'.format(*zinfo.date_time[:-1])
        data = ('', '', '', '', '', date_time, '', zinfo.filename)
    else:
        # totsize += zinfo.file_size
        # totcsize += zinfo.compress_size
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
    return data


def listzip(infolist):
    lst_str = []
    totsize = totcsize = ndir =0
    for zinfo in infolist:
        data = zipinfo_record(zinfo)
        lst_str.append(data)
    return lst_str


def main():
    top = tk.Tk()
    top.state('zoomed')
    # chk = tk.Checkbutton(top, text='groupby', command=lambda: setattr(panel, 'groupby', not panel.groupby))
    # chk.pack(side=tk.TOP, fill=tk.X)
    case = 'zip_files'
    if case == 'zip_panel':
        panel = Panel(
            top,
            path_obj='C:/',
            text='PRUEBA',
            column_ids="Length Method Size Ratio Offset DateTime CRC32 Name",
        )
        panel.pack(side=tk.TOP, fill=tk.BOTH, expand=tk.YES)
        # filename = "C:/Users/agmontesb/Downloads/Attachment-FE31.zip"
        filename = r"C:\Users\agmontesb\Documents\GitHub\excel\tests\files\teatv_v11.1.4.apk"
        zf = zipfile.ZipFile(filename)
        root = f'/{os.path.basename(filename)}'
        namelist = [f'{root}/{x}' for x in zf.namelist()]
        path_obj = navigationbar.StrListObj(namelist, root)
        # print(path_obj.listdir(f'{root}/META-INF'))
        def f_data(zf, path_obj):
            def f_record(x):
                x = x.rstrip(path_obj.SEP)
                data = ('', '', '', '', '', '', '', x)
                if path_obj.validate_path(x).startswith(x):
                    bflag = path_obj.isdir(x)
                    filename = x[len(path_obj.root)+1:]
                    try:
                        zinfo = zf.getinfo(filename)
                        data = zipinfo_record(zinfo)
                    except KeyError:
                        if bflag:
                            data = ('', '', '', '', '', '', '', filename)
                else:
                    pass
                return data
            return f_record
        records = listzip(zf.infolist())
        panel.tree_data(path_obj, f_data(zf, path_obj))
    if case == 'zip_files':
        panel = Panel(
            top,
            # path_obj='/mnt/c/',
            path_obj='C:/',
            text='PRUEBA',
            column_ids="Modified Size Name",
        )
        panel.pack(side=tk.TOP, fill=tk.BOTH, expand=tk.YES)
        path_obj = navigationbar.DirectoryObj(r'C:\Users\agmontesb', r'C:\Users\agmontesb')
        def f_record(x):
            stat = os.stat(x)
            size = '' if x.endswith(path_obj.SEP) else f'{stat.st_size // 1024:>10d} KB'
            fname = x[len(path_obj.root)+1:]
            return datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M'), size, fname
        panel.tree_data(path_obj, f_record, groupby=True)
    top.mainloop()


if __name__ == '__main__':
    main()
