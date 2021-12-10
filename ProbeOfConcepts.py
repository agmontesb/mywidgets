# -*- coding: utf-8 -*-
import collections
import os
import tkinter as tk
import xml.etree.ElementTree as ET
from basicViews import formFrame


def getLayout(layoutfile):
    # restype = directory_indx('layout')
    # layoutfile = self._unpack_pointer(id, restype)
    with open(layoutfile, 'rb') as f:
        xmlstr = f.read()
    return ET.XML(xmlstr).find('category')


def traverseTree(layoutfile):
    def isContainer(node):
        return node.tag in ['container', 'fragment']
    seq = 1
    pairs = [('', ('category1', 'category'))]
    parents = collections.deque()
    parents.append(('category1', getLayout(layoutfile)))
    while parents:
        parentid, parent = parents.popleft()
        for child in list(parent):
            id = child.attrib.get('id', '')
            if not id:
                seq += 1
                id = '%s%s' % (child.tag, seq)
            else:
                id = id.split('/')[-1]
            pairs.append((parentid, (id, child.tag)))
            if isContainer(child):
                parents.append((id, child))
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
    file_path = 'Data/ApplicationLayout.xml'
    xmlObj = getLayout(file_path)
    top = tk.Tk()
    settings = {}
    fframe = formFrame(master=top, settings=settings, selPane=xmlObj)
    dummy = fframe
    fframe.pack(side=tk.TOP, fill=tk.BOTH, expand=tk.YES, anchor=tk.NE)
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