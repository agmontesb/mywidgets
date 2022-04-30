
import tkinter as tk

import userinterface


class MenuBar(tk.Frame):
    def __init__(self, master, src, name=None):
        tk.Frame.__init__(self, master, name=name)
        selpane = userinterface.getLayout(src)
        for item in selpane:
            elem_name = item.attrib['label']
            menubutton = tk.Menubutton(self, text=elem_name, name=elem_name.lower())
            menubutton.pack(side=tk.LEFT)
            menu_master = userinterface.menuFactory(menubutton, item)
            menubutton.config(menu=menu_master)



