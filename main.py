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






if __name__ == '__main__':
    file_path = 'Data/ApplicationLayout.xml'
    xmlObj = getLayout(file_path)
    top = tk.Tk()
    settings = {}
    fframe = formFrame(master=top, settings=settings, selPane=xmlObj)
    dummy = fframe
    fframe.pack(side=tk.TOP, fill=tk.BOTH, expand=tk.YES, anchor=tk.NE)

    top.mainloop()