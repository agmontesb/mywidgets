# -*- coding: utf-8 -*-
import collections
import os
import tkinter as tk
import tkinter.ttk as ttk
import xml.etree.ElementTree as ET
from userinterface import formFrame, formFrameGen
from userinterface import newPanelFactory, getWidgetInstance


def getLayout(layoutfile):
    # restype = directory_indx('layout')
    # layoutfile = self._unpack_pointer(id, restype)
    with open(layoutfile, 'rb') as f:
        xmlstr = f.read()
    return ET.XML(xmlstr)


def traverseTree(master, layoutfile):
    def isContainer(node):
        return node.tag in ['container', 'fragment']

    root = getLayout(layoutfile)
    panel_module = root.get('lib') if root.get('lib') else None

    seq = 1
    widget_name, widget_attribs = root.tag, root.attrib
    widget_attribs['tag'] = widget_name
    pairs = [('', ('wdg0', '.', str(widget_attribs)))]
    parents = collections.deque()
    parents.append(('wdg0', root, master))
    while parents:
        parentid, parent_node, master_widget = parents.popleft()
        for child in list(parent_node):
            widget_name, widget_attribs = child.tag, child.attrib
            seq += 1
            widget_attribs['name'] = 'wdg%s' % seq
            widget = getWidgetInstance(
                master_widget,
                widget_name,
                widget_attribs,
                panelModule=panel_module
            )
            widget_attribs['tag'] = widget_name
            child_id = widget.winfo_name()
            pairs.append((parentid, (child_id, widget.path, str(widget_attribs))))
            if isContainer(child):
                parents.append((widget.winfo_name(), child, widget))
    return pairs


class Example(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)

        self.main = tk.Canvas(self, width=400, height=400,
                              borderwidth=0, highlightthickness=0,
                              background="bisque")
        self.main.pack(side="top", fill="both", expand=True)

        # add a callback for button events on the main canvas
        evento = "<Enter>"
        self.main.bind(evento, self.on_main_click)

        for x in range(10):
            for y in range(10):
                canvas = tk.Canvas(self.main, width=48, height=48,
                                   borderwidth=1, highlightthickness=0,
                                   relief="raised")
                if ((x+y)%2 == 0):
                    canvas.configure(bg="pink")

                self.main.create_window(x*50, y*50, anchor="nw", window=canvas)

                # adjust the bindtags of the sub-canvas to include
                # the parent canvas
                bindtags = list(canvas.bindtags())
                bindtags.insert(1, self.main)
                canvas.bindtags(tuple(bindtags))

                # add a callback for button events on the inner canvas
                canvas.bind(evento, self.on_sub_click)

    def on_sub_click(self, event):
        canvas_colour = event.widget.cget("background")
        print("sub-canvas %s binding" % canvas_colour)
        if canvas_colour == "pink":
            return "break"

    def on_main_click(self, event):
        print("main widget binding")

if __name__ == '__main__':
    top = tk.Tk()
    caso = 'test_newPaneFactory'
    if caso == 'tkinter':
        layoutfile = os.path.join('./data/tkinter/', 'tkUiEditor.xml')
        selPane = getLayout(layoutfile)
        fframe = newPanelFactory(
            top,
            {},
            selPane
        )
        # fframe.pack(side=tk.TOP, fill=tk.BOTH, expand=tk.YES)
    elif caso == 'configure_widget':
        def configWidget(event):
            widget = event.widget
            ifocus = widget.tree.focus()
            kwargs = dict([widget.tree.item(ifocus, 'values')])
            boton.config(**kwargs)
            pass
        fframe = formFrameGen(
            top,
            filename=os.path.join('./data/', 'WidgetParams.xml')
        )
        fframe.pack(side=tk.RIGHT, fill=tk.Y, expand=tk.YES)
        fframe.widget_attrs.bind('<<OL_Edit>>', configWidget)
        boton = ttk.Button(top, text='Boton de Prueba')
        boton.pack(side=tk.RIGHT, fill=tk.BOTH, expand=tk.YES)

        params = boton.config()
        # Se eliminan los alias que pudieran existir de algunas claves
        keys = sorted(key for key in params if len(params[key]) == 5)
        # Se establece el tipo de widget
        getattr(fframe, 'widget_tag').setValue(str(type(boton)))
        # Se calculan los pares (attribute, value)
        values = '$'.join(['&'.join((x, str(boton.cget(x)))) for x in keys])
        # Se transfieren los atributos al fframe.
        getattr(fframe, 'widget_attrs').setValue(values, sep=('$', '&'))
        pass

    elif caso == 'traverse':
        file_path = 'Data/kodi/BasicViewsShowCase.xml'
        pairs = traverseTree(top, file_path)
    elif caso == 'test_newPaneFactory':
        file_path = 'Data/kodi/MultiCategoryExample.xml'
        file_path = 'Data/mixing/mxShowcase.xml'
        xmlObj = getLayout(file_path)
        settings = {}
        fframe = formFrame(master=top, settings=settings, selPane=xmlObj)
        dummy = fframe
        fframe.pack(side=tk.TOP, fill=tk.BOTH, expand=tk.YES, anchor=tk.NE)
        pass
    elif caso == 'widgetFactory':
        file_path = 'Data/kodi/ApplicationLayout.xml'
        xmlObj = getLayout(file_path)
        settings = {}
        fframe = formFrame(master=top, settings=settings, selPane=xmlObj)
        dummy = fframe
        fframe.pack(side=tk.TOP, fill=tk.BOTH, expand=tk.YES, anchor=tk.NE)
    else:
        def motion(event):
            widget, x, y = event.widget, event.x, event.y
            try:
                if widget.name.isdigit():
                    print('{}, {}, {}'.format(widget.name, x, y))
                    dummy = 2
            except:
                pass
        fframe.bind_all("<Enter>", motion)


        Example(fframe).pack(fill="both", expand=True)
    top.mainloop()