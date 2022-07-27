
import tkinter as tk

import userinterface


class OldMenuBar(tk.Frame):
    def __init__(self, master, src, name=None):
        tk.Frame.__init__(self, master, name=name)
        selpane = userinterface.getLayout(src)
        for item in selpane:
            elem_name = item.attrib['label']
            menubutton = tk.Menubutton(self, text=elem_name, name=elem_name.lower())
            menubutton.pack(side=tk.LEFT)
            menu_master = userinterface.menuFactory(menubutton, item)
            menubutton.config(menu=menu_master)


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



