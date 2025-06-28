
import tkinter as tk

import mywidgets.userinterface as userinterface
from mywidgets.equations import equations_manager


class MenuBar(tk.Frame):

    def __init__(self, master, src, name=None, topmenu='false'):
        tk.Frame.__init__(self, master, name=name)

        def pop_menu(menu, wdg):
            try:
                menu.tk_popup(wdg.winfo_rootx(), wdg.winfo_rooty() + wdg.winfo_height())
            finally:
                menu.grab_release()

        top = master.winfo_toplevel()
        regMenu = getattr(top, 'registerMenu', None)
        selpane = userinterface.getLayout(src)
        master_menu = userinterface.menuFactory(self, selpane, registerMenu=regMenu)
        if topmenu == 'true':
            top = master.winfo_toplevel()
            top.config(menu=master_menu)
            return

        nitems = master_menu.index(tk.END) + 1
        for ndx in range(nitems):
            case = master_menu.type(ndx)
            if case in (tk.SEPARATOR, 'tearoff'):
                continue
            elem_name = master_menu.entrycget(ndx, 'label')
            menubutton = tk.Button(self, text=elem_name, name=elem_name.lower(), relief=tk.FLAT)
            menubutton.pack(side=tk.LEFT)
            if case == tk.CASCADE:
                menu = self.nametowidget(master_menu.entrycget(ndx, 'menu'))
                command = lambda x=menu, w=menubutton: pop_menu(x, w)
            else:
                command = lambda x=ndx: master_menu.invoke(x)
            menubutton.config(command=command)


class Ribbon(tk.Frame):

    def __init__(self, master, src, name=None, topmenu='false', is_content=False):
        super().__init__(master, name=name)

        def pop_menu(menu, wdg):
            bflag = not show_ribbon.get()
            if bflag:
                try:
                    menu.tk_popup(wdg.winfo_rootx(), wdg.winfo_rooty() + wdg.winfo_height())
                finally:
                    menu.grab_release()
                    self.setvar(varname, '')
            pass

        def ribbon(var_name, index, mode):
            if mode == 'w':
                bflag = self.getboolean(self.getvar(var_name))
                if bflag:
                    frst_button = master_menu.entrycget(0, 'label').lower()
                    self.setvar(varname, frst_button)
                    panels.pack(side='top', fill='x')
                else:
                    panels.pack_forget()
                    self.setvar(varname, '')

        self._tclCommands = {}
        top = master.winfo_toplevel()
        regMenu = getattr(top, 'registerMenu', None)
        ribbon_root = userinterface.getLayout(src, withCss=True, is_content=is_content)

        menu_element = ribbon_root.find('rmenu')
        src = menu_element.attrib['src']
        menupane = userinterface.getLayout(src)
        master_menu = userinterface.menuFactory(self, menupane, registerMenu=regMenu)

        varname = f'ribbon_{id(master_menu)}'
        menu_element.clear()
        menu_element.tag = 'var'
        [menu_element.set(key, value) for key, value in {'type': 'string', 'name': varname, 'value': ''}.items()]

        # Se le da forma a los paneles del ribbon (rpanel)
        panels = tk.Frame(self, name='panels', height=5)
        geo_ops = dict(side="top", fill="both", expand="yes")
        menuids = []
        for panel in ribbon_root.findall('rpanel'):
            menuid = panel.pop('menuid')
            attrib = {'name': f'ribbon_{menuid}', 'visible': f"eq({varname},'{menuid}')"}
            # attrib['name'] = f'ribbon_{menuid}'
            # attrib['visible'] = f"eq({varname},'{menuid}')"
            attrib.update(geo_ops)
            menuids.append(menuid)
            panel.tag = 'frame'
            # panel.clear()
            [panel.set(key, value) for key, value in attrib.items()]
            pass
        [ribbon_root.remove(selem) for selem in list(ribbon_root) if selem.tag not in ('var', 'frame')]
        userinterface.widgetFactory(panels, ribbon_root)
        buttons = tk.Frame(self, name='buttons')
        buttons.pack(side='top', fill='x')

        show_ribbon = tk.BooleanVar(name='show_ribbon', value=False)
        show_ribbon.trace_variable('w', ribbon)
        menubutton = tk.Checkbutton(
            buttons,
            text='V',
            offrelief=tk.FLAT,
            indicatoron=0,
            variable=show_ribbon,
        )
        menubutton.pack(side=tk.RIGHT)

        show_ribbon.set(0)

        nitems = master_menu.index(tk.END) + 1
        for ndx in range(nitems):
            case = master_menu.type(ndx)
            if case in (tk.SEPARATOR, 'tearoff'):
                continue
            elem_name = master_menu.entrycget(ndx, 'label')
            menubutton = tk.Checkbutton(
                buttons,
                text=elem_name,
                name=elem_name.lower(),
                offrelief=tk.FLAT,
                indicatoron=0,
                variable=varname,
                onvalue=elem_name.lower()
            )
            menubutton.pack(side=tk.LEFT)
            if case == tk.CASCADE:
                menu = self.nametowidget(master_menu.entrycget(ndx, 'menu'))
                command = lambda x=menu, w=menubutton: pop_menu(x, w)
            else:
                command = lambda x=ndx: master_menu.invoke(x)
            menubutton.config(command=command)

        nitems = master_menu.index(tk.END) + 1
        for ndx in range(nitems):
            case = master_menu.type(ndx)
            if case in (tk.SEPARATOR, 'tearoff'):
                continue
            root = master_menu.entrycget(ndx, 'label')
            if case == tk.CASCADE:
                menu_name = master_menu.entrycget(ndx, 'menu')
                menu = self.nametowidget(menu_name)
                nentries = menu.index(tk.END)
                if not nentries:
                    continue
                for n in range(nentries + 1):
                    case = menu.type(n)
                    if case in (tk.SEPARATOR, 'tearoff'):
                        continue
                    path = f'{root}/{menu.entrycget(n, "label").replace(" ", "_")}'
                    if case == tk.CASCADE:
                        self._tclCommands[path] = (menu.entrycget(n, 'menu'), n)
                        self.tk.createcommand(path, lambda x=path: self.post_cascade(x))
                    else:
                        self._tclCommands[path] = (menu_name, n)
                        self.tk.createcommand(path, lambda x=path: self.run_command(x))
            else:
                path = root
                self._tclCommands[path] = (str(master_menu), ndx)
                self.tk.createcommand(path, lambda x=path: self.run_command(x))

    def run_command(self, cmd_name):
        print(cmd_name)
        if self._tclCommands.get(cmd_name):
            menu_name, ndx = self._tclCommands[cmd_name]
            self.tk.call(menu_name, 'invoke', ndx)

    def post_cascade(self, cmd_name):
        print(cmd_name)
        top = self.winfo_toplevel()
        top.update_idletasks()
        x, y = top.winfo_pointerxy()
        wdg = top.winfo_containing(x, y)
        menu_name, ndx = self._tclCommands[cmd_name]
        menu = self.nametowidget(menu_name)
        try:
            menu.tk_popup(wdg.winfo_rootx(), wdg.winfo_rooty() + wdg.winfo_height())
        finally:
            menu.grab_release()


class OldRibbon(tk.Frame):

    def __init__(self, master, src, name=None, topmenu='false', is_content=False):
        super().__init__(master, name=name)

        def pop_menu(menu, wdg):
            if not show_ribbon.get():
                try:
                    menu.tk_popup(wdg.winfo_rootx(), wdg.winfo_rooty() + wdg.winfo_height())
                finally:
                    menu.grab_release()
                    self.setvar('panel', '')
            pass

        def ribbon(var_name, index, mode):
            if mode == 'w':
                bflag = self.getboolean(self.getvar(var_name))
                if bflag:
                    frst_button = master_menu.entrycget(0, 'label').lower()
                    self.setvar('panel', frst_button)
                    panels.pack(side='top', fill='x')
                else:
                    panels.pack_forget()
                    self.setvar('panel', '')

        self._tclCommands = {}
        top = master.winfo_toplevel()
        regMenu = getattr(top, 'registerMenu', None)
        selpane = userinterface.getLayout(src, is_content=is_content)
        master_menu = userinterface.menuFactory(self, selpane, registerMenu=regMenu)
        if topmenu == 'true':
            top = master.winfo_toplevel()
            top.config(menu=master_menu)
            return

        buttons = tk.Frame(self, name='buttons')
        buttons.pack(side='top', fill='x')

        show_ribbon = tk.BooleanVar(name='show_ribbon', value=False)
        show_ribbon.trace_variable('w', ribbon)
        menubutton = tk.Checkbutton(
            buttons,
            text='V',
            offrelief=tk.FLAT,
            indicatoron=0,
            variable=show_ribbon,
        )
        menubutton.pack(side=tk.RIGHT)

        panels = tk.Frame(self, name='panels', height=5)
        show_ribbon.set(0)

        nitems = master_menu.index(tk.END) + 1
        for ndx in range(nitems):
            case = master_menu.type(ndx)
            if case in (tk.SEPARATOR, 'tearoff'):
                continue
            elem_name = master_menu.entrycget(ndx, 'label')
            menubutton = tk.Checkbutton(
                buttons,
                text=elem_name,
                name=elem_name.lower(),
                offrelief=tk.FLAT,
                indicatoron=0,
                variable='panel',
                onvalue=elem_name.lower()
            )
            menubutton.pack(side=tk.LEFT)
            if case == tk.CASCADE:
                menu = self.nametowidget(master_menu.entrycget(ndx, 'menu'))
                command = lambda x=menu, w=menubutton: pop_menu(x, w)
            else:
                command = lambda x=ndx: master_menu.invoke(x)
            menubutton.config(command=command)

        nitems = master_menu.index(tk.END) + 1
        for ndx in range(nitems):
            case = master_menu.type(ndx)
            if case in (tk.SEPARATOR, 'tearoff'):
                continue
            root = master_menu.entrycget(ndx, 'label')
            if case == tk.CASCADE:
                menu_name = master_menu.entrycget(ndx, 'menu')
                menu = self.nametowidget(menu_name)
                nentries = menu.index(tk.END)
                if not nentries:
                    continue
                for n in range(nentries + 1):
                    case = menu.type(n)
                    if case in (tk.SEPARATOR, 'tearoff'):
                        continue
                    path = f'{root}/{menu.entrycget(n, "label").replace(" ", "_")}'
                    if case == tk.CASCADE:
                        self._tclCommands[path] = (menu.entrycget(n, 'menu'), n)
                        self.tk.createcommand(path, lambda x=path: self.post_cascade(x))
                    else:
                        self._tclCommands[path] = (menu_name, n)
                        self.tk.createcommand(path, lambda x=path: self.run_command(x))
            else:
                path = root
                self._tclCommands[path] = (str(master_menu), ndx)
                self.tk.createcommand(path, lambda x=path: self.run_command(x))

    def run_command(self, cmd_name):
        print(cmd_name)
        if self._tclCommands.get(cmd_name):
            menu_name, ndx = self._tclCommands[cmd_name]
            self.tk.call(menu_name, 'invoke', ndx)

    def post_cascade(self, cmd_name):
        print(cmd_name)
        top = self.winfo_toplevel()
        top.update_idletasks()
        x, y = top.winfo_pointerxy()
        wdg = top.winfo_containing(x, y)
        menu_name, ndx = self._tclCommands[cmd_name]
        menu = self.nametowidget(menu_name)
        try:
            menu.tk_popup(wdg.winfo_rootx(), wdg.winfo_rooty() + wdg.winfo_height())
        finally:
            menu.grab_release()


def main():
    import tkinter.messagebox as tkMessageBox

    class Top(tk.Tk):

        def __init__(self):
            super().__init__()
            self.event_add('<<MENUCLICK>>', 'None')
            self.event_add('<<VAR_CHANGE>>', 'None')
            self.bind_all('<<MENUCLICK>>', self.onMenuClick)
            self.bind_all('<<VAR_CHANGE>>', self.onVarChange)

            self.attributes('-zoomed', True)
            self.setGui()

        def setGui(self):
            file_path = 'Tools/mywinzip/res/layout/ribbon.xml'
            xmlObj = userinterface.getLayout(file_path, withCss=True)
            userinterface.newPanelFactory(
                master=self,
                selpane=xmlObj,
                genPanelModule=None,
                setParentTo='master',
                # registerWidget=self.register_widget,
            )
            equations_manager.set_initial_widget_states()
            pass

        def onMenuClick(self, event):
            menu_master, indx = event.widget, event.data
            menu, menu_item = menu_master.cget("title"), menu_master.entrycget(indx, "label")
            tkMessageBox.showinfo(title=menu, message=menu_item)

        def onVarChange(self, event):
            pass

    top = Top()
    top.mainloop()


if __name__ == '__main__':
    main()


