import os.path
import re
import shutil
from io import StringIO

import sh
import tkinter as tk
import tkinter.messagebox as tkMessageBox
import tkinter.filedialog as tkFileDialog
import tkinter.simpledialog as tkSimpleDialog
import zipfile
from datetime import datetime
import tempfile

import userinterface
from Widgets.Custom import navigationbar
from equations import equations_manager


class GitClientUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.event_add('<<MENUCLICK>>', 'None')
        self.event_add('<<VAR_CHANGE>>', 'None')
        self.bind_all('<<MENUCLICK>>', self.onMenuClick)
        self.bind_all('<<VAR_CHANGE>>', self.onVarChange)
        self.bind_all('<Button-3>', self.onRightClick)
        self.attributes('-zoomed', True)

        self.git = sh.git

        self.setGui()

    def setGui(self):
        file_path = '@mygitclient:layout/gitclient'
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
            case _:
                pass

    def register_widget(self, master, xmlwidget, widget):
        attribs = xmlwidget.attrib
        name = attribs.get('name')
        if name in ('zip_panel',):
            setattr(self, name, widget)
        pass

    def onVarChange(self, event=None, attr_data=None):
        if event:
            attr_data = event.attr_data
        var_name, value = attr_data
        match var_name:
            case _:
                pass

    @staticmethod
    def runGitCommand(*args):
        buf = StringIO()
        sh.git(*args, _out=buf)
        buf.seek(0)
        msg = buf.read()
        return msg

    def onMenuClick(self, event):
        menu_master, indx = event.widget, event.data
        menu, menu_item = menu_master.cget("title"), menu_master.entrycget(indx, "label")
        match menu:
            case 'git':
                match menu_item:
                    case 'Version' | 'Html Path' | 'Man Path' | 'Info Path' | 'Exec Path':
                        arg = '--' + menu_item.lower().replace(' ', '-')
                        msg = self.runGitCommand(arg)
                        tkMessageBox.showinfo(title=f'Git Info', message=f'{arg}: {msg}')
                    case 'Git Dir' | 'Work Tree' | 'Namespace' | 'Exec Path':
                        arg = '--' + menu_item.lower().replace(' ', '-')
                        msg = f'Path to assign to {arg}'
                        ask_path = tkFileDialog.askdirectory(initialdir=os.getcwd(), title=msg)
                        if ask_path:
                            msg = self.runGitCommand(f'{arg}={ask_path}')
                    case 'Open':
                        msg = f'Path to repository'
                        ask_path = tkFileDialog.askdirectory(initialdir=os.getcwd(), title=msg)
                        if ask_path:
                            git_dir = os.path.join(ask_path, '.git')
                            if os.path.exists(git_dir):
                                self.git = sh.git.bake('-C', ask_path)
                            else:
                                msg = f'{ask_path}: Not a repository'
                                tkMessageBox.showerror(title='Path Error', message=msg)
                    case 'Configuration':
                        buff = self.runGitCommand('config', '--list', '--null', '--show-origin')
                        recs = re.split(r'\x1b\[7m\^\@\x1b\[27m|\x1b\[m\n', buff.split('\r')[1])[:-2]
                        recs = [recs[3 * k: 3 * k + 3] for k, _ in enumerate(recs[::3])]
                        path_obj_root = '/conf'
                        namelist = [os.path.join(path_obj_root, x[1].replace('.', '/')) for x in recs]
                        path_obj = navigationbar.StrListObj(namelist, path_obj_root)
                        def rec_data(records, namelist):
                            def f_record(x):
                                try:
                                    indx = namelist.index(x)
                                    rec_info = records[indx]
                                except ValueError:
                                    is_file = not x.endswith('/')
                                    if is_file:
                                        raise
                                    rec_info = ('', '', '')
                                return rec_info
                            return f_record
                        groupby = False
                        self.zip_panel.tree_data(path_obj, rec_data(recs, namelist), groupby=groupby)

                    case _:
                        tkMessageBox.showinfo(title='MenuClick', message=f'{menu_item}: Not implemented yet')
        pass

    def onRightClick(self, event):
        wdg = event.widget
        pass

    def destroy(self):
        super().destroy()


def main():
    gc = GitClientUI()
    gc.mainloop()


if __name__ == '__main__':
    main()



