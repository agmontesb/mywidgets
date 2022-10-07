# -*- coding: utf-8 -*-
import collections
import contextlib
import fnmatch
import functools
import inspect
import os
import tkinter as tk
import traceback
import tkinter.messagebox as tkMessageBox
import tkinter.filedialog as tkFileDialog
from datetime import datetime

import userinterface
from Widgets import kodiwidgets
from equations import equations_manager

R = type('Erre', (object,), {})
REFRESH_TIME = '10'


class UiMonitor(tk.Tk):
    def __init__(self, layout_file=None, *filters):
        super().__init__()
        self.event_add('<<MENUCLICK>>', 'None')
        self.bind_all('<<MENUCLICK>>', self.on_menuclick)
        self.uimonitor_ops = {
            'refresh_time': REFRESH_TIME,
            'geometry': '500x500',
            'filters': ', '.join(filters) or '*.xml, *.css',
            'initial_path': os.path.dirname(
                userinterface.getFileUrl('@data:tkinter/LayoutDefault')
            )
        }
        self.R = collections.namedtuple('Settings', self.uimonitor_ops.keys())(**self.uimonitor_ops)
        self.geometry(self.R.geometry)
        self.pack_propagate(0)

        self.watched = {}
        self.fileHistory = []

        self.layout = ''
        self.update_changed = False
        self.pid = None

        self.setGui()
        if layout_file:
            self.open_file(layout_file)
        pass

    def setGui(self):
        file_path = '@data:tkinter/tkUiMonitor'
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

        # variables:
        self.activeViewIndx = equations_manager.state_equations['srv_view_sel']
        self.activeViewIndx.trace_add('write', self.setActiveView)

        tree = self.tree
        tree['columns'] = column_ids = 'Name Date Path'
        for column in column_ids.split(' '):
            tree.heading(column, text=column, anchor=tk.W)
            tree.column(column, stretch=1, width=100)

    def register_widget(self, master, xmlwidget, widget):
        attribs = xmlwidget.attrib
        name = attribs.get('name')
        if name:
            if name in ('parent_frame', 'tree', 'lst_update', ):
                setattr(self, name, widget)
            elif name == 'open_file':
                widget.config(command=self.open_file)
            elif name == 'open_recent':
                widget.config(command=self.do_popup)
            elif name == 'app_settings':
                widget.config(command=self.get_settings)

    def get_settings(self):
        title = 'UiMonitor Settings'
        xmlfile = userinterface.getFileUrl('@data:tkinter/dlg_uimonitor_settings')
        dlg = kodiwidgets.CustomDialog(
            self,
            title=title, xmlFile=xmlfile, isFile=True, settings=self.R._asdict(), dlg_type='okcancel'
        )
        if dlg.allSettings:
            settings = dict(dlg.allSettings)
            self.R = self.R._replace(**settings)

    def do_popup(self):
        popup_menu = tk.Menu(self, tearoff=0)
        for k, filename in enumerate(self.fileHistory, start=1):
            flabel = os.path.basename(filename)
            popup_menu.insert_command(
                k,
                label='{} {:30s}'.format(k, flabel),
                command=lambda x=filename: self.open_file(x)
            )
        x, y = self.winfo_pointerxy()
        try:
            popup_menu.tk_popup(x, y)
        finally:
            popup_menu.grab_release()
            pass

    def setActiveView(self, *args, **kwargs):
        activeView = self.activeViewIndx.get()
        if activeView == 'wtch':
            self.init_WTCH_View()
        elif activeView == 'ui':
            self.init_UI_View()

    def init_WTCH_View(self):
        if self.update_changed:
            tree = self.tree
            tree.delete(*tree.get_children(''))

            for filename, idate in sorted(self.watched.items()):
                fpath, fname = os.path.split(filename)
                row = (fname, datetime.fromtimestamp(idate).strftime('%Y-%m-%d %H:%M'), fpath)
                child_id = tree.insert(
                    '',
                    'end',
                    text=filename,
                    values=row,
                )
            self.update_changed = False
        pass

    def init_UI_View(self):
        if not self.layout:
            return
        with self.context_open():
            xmlstr = userinterface.getContent(self.layout)

            ui_pane = self.parent_frame
            fframes = ui_pane.winfo_children()
            [fframe.destroy() for fframe in fframes]
            try:
                panel = userinterface.getLayout(xmlstr, withCss=True, is_content=True)                 # ET.XML(xmlstr)
                self.setupForms(panel, ui_pane)
            except IOError:
                tkMessageBox.showerror('Not a valid File', 'File not xml compliant ')
                return
            except ValueError:
                tkMessageBox.showerror('Not a valid File', 'An error has occurred while rendering the file ')
                return
            except Exception as e:
                tkMessageBox.showerror('Not a valid File', 'An error has occurred while rendering the layout file ')
                msg = traceback.format_exc()
                tk.Message(ui_pane, text=f'{str(e)}\n{msg}').pack()
                raise e

    def setupForms(self, panel, formRoot):
        seq = -1
        for category_panel in panel.findall('category'):
            root, master = category_panel, formRoot
            widget_name, widget_attribs = root.tag, root.attrib
            seq += 1
            widget_attribs['name'] = str(seq)
            attributes = {
                'text': widget_attribs['label'],
                'name': '%s' % seq,
            }
            widget = userinterface.getWidgetInstance(
                master,
                'labelframe',
                attributes,
            )
            widget.pack(side='top', fill='both', expand='yes')
            # En este punto se debería hacer pack sobre cada nodo de categoría con la
            # siguiente expresión:
            # widget.pack(side='top', fill='both', expand='yes')
            # Pero como todos los paneles de las categorías deben estaar ocultos, no lo hacemos.
            # Cuando se defina el foco inicial se activará (Se hara pack) sobre el nodo escogido.

            seq = userinterface.widgetFactory(
                widget,
                category_panel,
                setParentTo='root',
                k=seq
            )
        # equations_manager.set_initial_widget_states()
        self.seq = seq

    def check_watched_files(self):
        changed = [
            (key, new_value)
            for key, value in self.watched.items()
            if (new_value := os.path.getmtime(key)) != value
        ]
        if changed:
            self.lst_update: tk.Label
            now = datetime.now()
            self.lst_update.configure(text=now.strftime('%H:%M:%S'))
            self.update_changed = True
            self.init_UI_View()

        self.pid = self.after(int(self.R.refresh_time) * 1000, self.check_watched_files)

    @contextlib.contextmanager
    def context_open(self):
        def open_wrapper(open_f):
            @functools.wraps(open_f)
            def wrapper(file, *args, **kwargs):
                filters = [x.strip() for x in self.R.filters.split(',')]
                if any(fnmatch.fnmatch(file, x) for x in filters):
                    self.watched[file] = os.path.getmtime(file)
                return open_f(file, *args, **kwargs)

            return wrapper

        bltin_mod = globals()['__builtins__']
        open_f = bltin_mod.open
        try:
            bltin_mod.open = open_wrapper(open_f)
            yield
        finally:
            bltin_mod.open = inspect.unwrap(bltin_mod.open)

    def list_to_watch(self):
        msg = '\n'.join(x for x in sorted(self.watched.keys()))
        tkMessageBox.showinfo(title='Files To Watch', message=msg)

    # Menu methods

    def open_file(self, name=None):
        if self.fileHistory:
            fname = self.fileHistory[0]
            initial_path = os.path.dirname(fname)
        else:
            initial_path = self.R.initial_path
        name = name or tkFileDialog.askopenfilename(
            initialdir=initial_path,
            filetypes=[('xml Files', '*.xml'), ('All Files', '*.*')]
        )
        if not name:
            return

        self.layout = name
        self.watched = {}
        self.update_changed = True
        self.activeViewIndx.set('ui')
        if self.pid is None:
            self.pid = self.after(int(self.R.refresh_time) * 1000, self.check_watched_files)
        self.recFile(name)

    def recFile(self, filename):
        try:
            ndx = self.fileHistory.index(filename)
        except:
            pass
        else:
            self.fileHistory.pop(ndx)
        self.fileHistory.insert(0, filename)
        nmax = 5
        self.fileHistory = self.fileHistory[:nmax]

    def on_menuclick(self, event):
        menu_master, indx = event.widget, event.data
        msg = f'MENUCLICK fire. Menu: {menu_master.cget("title")}, Menu_item:{menu_master.entrycget(indx, "label")}'
        # print(msg)
        tkMessageBox.showinfo(title='on_menuclick', message=msg)


def main():
    top = UiMonitor()
    top.mainloop()

if __name__ == '__main__':
    main()