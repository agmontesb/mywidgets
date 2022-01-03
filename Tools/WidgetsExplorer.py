# -*- coding: utf-8 -*-
import collections
import tkinter as tk
import tkinter.ttk as ttk


class WidgetExplorer(ttk.Treeview):

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.tag_configure('activenode', background='light green')
        self.event_add('<<ActiveSelection>>', '<Double-1>', '<Return>')

        self.bind("<ButtonPress-1>", self.bDown)
        self.bind("<ButtonRelease-1>", self.bUp, add='+')
        self.bind("<B1-Motion>", self.bMove, add='+')

        # Análogo al widget Text el _edit_flag se enciende cuando se
        # realiza una operación de insert, delete o cambio de datos en las
        # columnas
        self._edit_flag = False
        # Esta variable es puesta en verdadera si el widget ha pasado por Press-Move-Release
        self._drag_and_drop = False

        pass

    def edit_modified(self, flag=None):
        '''
        Función que permite alterar el estado de edición o entregar
        el estado del tree.
        :param flag: bool o None. Cuando es True o False enciende o apaga
                     la bandera edit_flag. Cuando es None entrega el estado
                     del edit_flag.
        :return: bool, None. Estado del _edit_flag.
        '''
        if flag is None:
            return self._edit_flag
        if not self._edit_flag and flag:
            self.event_generate('<<Modified>>', when='tail')
        self._edit_flag = bool(flag)

    # Las funciones delete, insert e item se modifican para reportar
    # la edición del edit_flag pues estas funciones alteran la estructura
    #o la información en el tree.
    def delete(self, *items):
        super(WidgetExplorer, self).delete(*items)
        self.edit_modified(True)

    def insert(self, parent, index, iid=None, **kw):
        answ = super(WidgetExplorer, self).insert(parent, index, iid, **kw)
        self.edit_modified(True)
        return answ

    def item(self, iid, option=None, **kw):
        if kw:
            self.edit_modified(True)
        if option == 'path':
            path = ''
            while True:
                path = f'.{iid}' + path
                if not self.parent(iid):
                    break
                iid = self.parent(iid)
            return path
        return super(WidgetExplorer, self).item(iid, option, **kw)

    # A través de bDown, bUp y bMove se implementa el Drag and Drop en este widget.
    def bDown(self, event):
        tv = event.widget
        tv.configure(cursor='hand2')
        if tv.identify_row(event.y) not in tv.selection():
            tv.selection_set(tv.identify_row(event.y))

    def bUp(self, event):
        tv = event.widget
        tv.configure(cursor='')
        if not self._drag_and_drop:
            return 'break'
        if tv.identify_row(event.y) in tv.selection():
            tv.selection_set(tv.identify_row(event.y))
        self._drag_and_drop = False
        self.edit_modified(True)

    def bMove(self, event):
        tv = event.widget
        on_iid = tv.identify_row(event.y)
        if on_iid != tv.focus():
            on_parent_iid = tv.parent(on_iid)
            moveto = tv.index(on_iid)
            for s in tv.selection():
                tv.move(s, on_parent_iid, moveto)
            self._drag_and_drop = True

    def dump(self):
        xml_str = '<?xml version="1.0" encoding="utf-8" standalone="yes"?>\n<setting>\n'
        to_process = collections.deque()
        indent_stack = [('', 'setting')]
        to_process.extend(self.get_children())
        while to_process:
            nodeid = to_process.popleft()
            attribs = eval(self.item(nodeid, 'values')[1])
            tag = attribs.pop('tag')
            attribs = ' '.join(f'{key}="{value}"' for key, value in attribs.items())
            parentid = self.parent(nodeid)
            children = self.get_children(nodeid)
            if children:
                to_process.extendleft(reversed(children))
                end_str = '>'
            else:
                end_str = '/>'
            while parentid != indent_stack[-1][0]:
                _, end_tag = indent_stack.pop()
                xml_str += f'{len(indent_stack) * "    "}</{end_tag}>\n'
            xml_str += f'{len(indent_stack) * "    "}<{tag} {attribs}{end_str}\n'
            if end_str == '>':
                indent_stack.append((nodeid, tag))
        while indent_stack:
            _, end_tag = indent_stack.pop()
            xml_str += f'{len(indent_stack) * "    "}</{end_tag}>\n'
        return xml_str


if __name__ == '__main__':
    top = tk.Tk()
    tree = WidgetExplorer(top)
    nodes = ['', 'uno', 'dos', 'tres', 'cuatro', 'cinco']
    for ndx in range(len(nodes) - 1):
        tree.insert(nodes[ndx], 'end', nodes[ndx + 1])
    print(tree.item('cinco', 'path'))
    tree.pack()
    top.mainloop()