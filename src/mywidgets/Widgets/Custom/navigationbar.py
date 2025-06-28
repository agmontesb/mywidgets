# -*- coding: utf-8 -*-
import collections
import os
import tkinter as tk
import tkinter.ttk as tkk
import tkinter.font as tkFont
from abc import ABC, abstractmethod

import mywidgets.userinterface as userinterface

MENU_WINDOW = 20
DOWN_ARROW = 'ᐁ'  #     '▼'    # 'ᐯ'
UP_ARROW = 'ᐃ'    #     '▲'    # 'ᐱ'

ActivePath = collections.namedtuple('ActivePath', ('index', 'path', 'isDir'))


class RollingMenu:

    def __init__(self, master=None, cnf={}, **kw):
        self.menu_offset = 0
        self.menu_list = []
        self.fidle = None
        self.active_index = 0

        kw = cnf or kw
        self.req_nitems = kw.pop('req_nitems', MENU_WINDOW)
        self.postcommand = kw.pop('postcommand', None)
        kw['postcommand'] = self.inner_postcommand
        kw.setdefault('tearoff', 0)
        kw.setdefault('font', tkFont.Font(family='Consolas', size=10))
        self.menu = tk.Menu(master=master, **kw)
        self.menu.bind('<<MenuSelect>>', self.onMenuSelect)

    def __str__(self):
        # De esta forma es posible utilizar RollingMenu con cualquier widget que en su
        # configuración tenga un menu, ya que le entrega el camino del menu delegado.
        return str(self.menu)

    def cget(self, key):
        if key in ('req_nitems', 'postcommand'):
            return getattr(self, key)
        return self.menu.cget(key)

    __getitem__ = cget

    def config(self, cnf={}, **kw):
        [setattr(self, key, kw.pop(key)) for key in ('req_nitems', 'postcommand') if kw.get(key, None)]
        self.menu.config(cnf=cnf, **kw)

    __setitem__ = configure = config

    def inner_postcommand(self):
        # En este callback debe ejecutarse al menos self.popup_menu.activate(x) para que el
        # menú muestre la opción activa.
        try:
            self.postcommand()
        except:
            pass
        active_index = self.active_index
        linf = max(0, active_index - self.req_nitems // 2)
        lsup = min(len(self.menu_list), active_index + self.req_nitems // 2 + self.req_nitems % 2) - 1
        self.loadMenuOptions(linf, lsup)

    def activate(self, index):
        self.active_index = index

    def add(self, itemType, cnf={}, **kw):
        self.menu_list.append((itemType, cnf or kw))

    def insert(self, index, itemType, cnf={}, **kw):
        self.menu_list.insert(self.index(index), (itemType, cnf or kw))

    def delete(self, index1, index2=None):
        index2 = index2 or index1
        num_index1, num_index2 = self.index(index1), self.index(index2)
        if num_index2 == num_index1:
            num_index2 +=1
        del self.menu_list[num_index1:num_index2]

    def entrycget(self, index, option):
        return self.menu_list[index][1].get(option, None)

    def entryconfigure(self, index, cnf=None, **kw):
        kw = cnf or kw
        self.menu_list[index][1].update(kw)

    entryconfig = entryconfigure

    def index(self, index):
        if isinstance(index, int):
            return index
        if isinstance(index, str):
            if index == tk.END:
                return len(self.menu_list)
            if index == tk.ACTIVE:
                npos = (self.menu.index(tk.ACTIVE) or 0) + self.menu_offset
                if len(self.menu_list) > self.req_nitems:
                    npos -= 1
                return npos

    def invoke(self, index):
        cb = self.menu_list[index][1].get('command', None)
        try:
            cb()
        except:
            pass

    def type(self, index):
        return  self.menu_list[index][0]

    def isMouseOver(self, index):
        num_index = index
        menu = self.menu
        m1, m2 = menu.winfo_pointerxy()
        x1, x2 = menu.winfo_rootx(), menu.winfo_rooty() + menu.yposition(num_index)
        bflag = num_index == menu.index(tk.END)
        width = (menu.winfo_height() if bflag else menu.yposition(num_index + 1)) - menu.yposition(num_index)
        y1, y2 = x1 + menu.winfo_width(), x2 + width
        return (x1 <= m1 <= y1) and (x2 <= m2 <= y2)

    def onMenuSelect(self, event):
        # <<MenuSelect>> virtual event generado por el widget
        menu = event.widget
        ndx = menu.index(tk.ACTIVE)
        if len(self.menu_list) > self.req_nitems and ndx in (0, self.req_nitems + 1):
            self.after_idle(self.rollMenu)
        elif self.fidle is not None:
            self.after_cancel(self.fidle)
            self.fidle = None

    def loadMenuOptions(self, linf, lsup):
        if lsup - linf < self.req_nitems - 1:
            # Se rompe un límite
            if linf:
                linf = lsup - self.req_nitems + 1
            else:
                lsup = linf + self.req_nitems - 1
        self.menu_offset = linf
        self.menu.delete(0, tk.END)
        [
            self.menu.add(
                x[0],
                **x[1],
            ) for x in self.menu_list[linf:lsup + 1]
        ]
        active_index = max(0, min(self.active_index - self.menu_offset, self.req_nitems - 1))
        if len(self.menu_list) > self.req_nitems:
            nlen = max(*[len(self.entrycget(x, 'label')) for x in range(len(self.menu_list))])
            active_index += 1
            self.menu.insert_command(0, label=f"{DOWN_ARROW.center(nlen, ' ')}")
            self.menu.insert_command(tk.END, label=f"{UP_ARROW.center(nlen, ' ')}")
        self.menu.activate(active_index)

    def rollMenu(self):
        ndx = self.menu.index(tk.ACTIVE)
        bflag = ndx in (0, self.req_nitems + 1) and self.isMouseOver(ndx)
        if ndx == self.req_nitems + 1:
            ndx += self.menu_offset - 1
            if ndx < len(self.menu_list):
                next_item = self.menu_offset + self.req_nitems
                itemType, kw = self.menu_list[next_item]
                self.menu.insert(self.req_nitems + 1, itemType, **kw)
                self.menu.delete(1)
                self.menu_offset += 1
                self.menu.activate(self.req_nitems + 1)
                if not bflag:
                    self.menu.event_generate('<Up>')
            else:           # ndx == len(self.menu_list):
                linf, lsup = 0, self.req_nitems - 1
                self.loadMenuOptions(linf, lsup)
                ndx = (self.req_nitems + 1) if bflag else 1
                self.menu.activate(ndx)
            pass
        elif ndx == 0:
            if self.menu_offset > 0:
                self.menu.delete(self.req_nitems)
                next_item = self.menu_offset - 1
                itemType, kw = self.menu_list[next_item]
                self.menu.insert(1, itemType, **kw)
                self.menu_offset -= 1
                self.menu.activate(0)
                if not bflag:
                    self.menu.event_generate('<Down>')
            else:           # self.menu_offset == 0:
                linf, lsup = len(self.menu_list) - self.req_nitems, len(self.menu_list)
                self.loadMenuOptions(linf, lsup)
                if not bflag:
                    self.menu.activate(self.req_nitems)
                else:
                    self.menu.activate(0)
        self.update_idletasks()
        if bflag:
            self.fidle = self.after(800, self.rollMenu)

    def __getattr__(self, item):
        return getattr(self.menu, item)


class BreadCumb(tk.Canvas):

    def __init__(self, master, path_obj, name=None, **kwargs):
        height = kwargs.setdefault('height', 25)
        super().__init__(master, name=name, **kwargs)

        self.height = height
        self.draw_path = ''
        self.labels = []
        self.actual_dir = ''
        self.pfocus = None
        self.polygon_ids = []
        self.text_ids = []

        self.setGui()

        self.base_dir = None
        top = master.winfo_toplevel()
        if isinstance(path_obj, str):
            try:
                path_obj = getattr(top, path_obj)
            except AttributeError:
                dmy = os.path.abspath('.')
                path_obj = DirectoryObj(dmy, dmy)
        self.path_obj = path_obj
        pass

    @property
    def path_obj(self):
        return self._path_obj

    @path_obj.setter
    def path_obj(self, obj):
        try:
            path_obj = pathObjWrapper(obj)
        except AttributeError:
            path_obj = DirectoryObj('/', '/')
        path_obj.set_master(self)
        self.base_dir = path_obj.root
        self._path_obj = path_obj
        self.draw_path = ''
        # Porque no existe el canvas draw_focus es False
        self.setActivePath(path_obj.actual_dir)

    def setGui(self):
        canvas = self
        canvas.tag_bind('arrow', '<Button-1>', self.onCanvasClickEvent)
        canvas.event_add('<<HRZ_ARROWS>>', '<Left>', '<Right>')
        canvas.bind('<<HRZ_ARROWS>>', self.onCanvasHrzArrowsEvent)
        canvas.bind("<Down>", self.onCanvasDownArrowEvent)
        canvas.focus_set()

        self.popup_menu = RollingMenu(self, name="breadcumb", tearoff=0, postcommand=self.build_popup, relief=tk.FLAT)
        self.popup_menu.bind('<<HRZ_ARROWS>>', self.onMenuKeyboardEvent)
        self.popup_menu.bind('<Return>', self.onMenuKeyboardEvent)
        pass

    def setupCanvas(self, *labels):
        deltax = 4
        height = self.height
        font = tkFont.Font(self)
        labels = labels or self.labels
        to_draw = os.path.join(*labels)

        common_path = os.path.commonpath([to_draw, self.draw_path])
        npos = (len(common_path.split(os.sep)) + 1) if common_path else 0

        for pid, ptext in zip(self.polygon_ids[npos:], self.text_ids[npos:]):
            self.delete(pid, ptext)
        del (self.polygon_ids[npos:])
        del (self.text_ids[npos:])

        if len(self.polygon_ids) > 0:
            last_polygon_id = self.polygon_ids[-1]
            x = self.coords(last_polygon_id)[2] + deltax
            pass
        else:
            x = 0

        labels = labels[npos:]
        if labels and labels[0] == '.':
            labels[0] = os.path.basename(self.base_dir)
        for k, lbl in enumerate(labels):
            width = self.draw_polygon(font, height, x, lbl)
            x += width + deltax
            pass
        self.draw_path = to_draw

    def draw_polygon(self, font, height, x, lbl):
        '''
        Este método dibuja cada elemento del breadcumb. Heredando de esta clase y overriding
        este método, se puede cambiar el aspecto del breadcumb.
        '''
        width = font.measure(lbl) + height // 4
        v1 = [x, 0]
        v2 = [v1[0] + width, 0]
        v3 = [v2[0] + height // 2, height // 2]
        v4 = [v2[0], height]
        v5 = [v1[0], height]
        v6 = [(v1[0] + height // 2) if v1[0] != 0 else 0, height // 2]
        vertices = v1 + v2 + v3 + v4 + v5 + v6
        pid = self.create_polygon(
            *vertices,
            fill='white',
            outline='black',
            tag='arrow'
        )
        self.polygon_ids.append(pid)
        tid = self.create_text(
            (v6[0] + v2[0]) // 2, height // 2,
            text=lbl,
            anchor=tk.CENTER,
            tag='arrow'
        )
        self.text_ids.append(tid)
        return width

    def draw_focus(self, pfocus, next_pfocus):
        if pfocus is not None:
            polygon = self.polygon_ids[pfocus]
            self.itemconfig(polygon, fill='white')
        to_draw = os.path.join(*self.labels)
        if to_draw != self.draw_path:
            self.setupCanvas()
        if next_pfocus is not None:
            polygon = self.polygon_ids[next_pfocus]
            self.focus(polygon)
            self.itemconfig(polygon, fill='green')

    def set_active_index(self, next_pfocus, draw_focus=True):
        next_pfocus = next_pfocus % len(self.labels)
        pfocus, self.pfocus = self.pfocus, next_pfocus
        if draw_focus:
            self.draw_focus(pfocus, next_pfocus)
        return pfocus

    def getActivePath(self):
        path = os.path.join(self.base_dir, *self.labels[1:self.pfocus + 1])
        isdir = (self.pfocus < len(self.labels) - 1) or self.path_obj.isdir(path)
        return ActivePath(self.pfocus, path, isdir)

    def setActivePath(self, apath, draw_focus=True):
        path = self.path_obj.validate_path(apath)
        rel_path = os.path.relpath(path, self.path_obj.root)
        # Se asegura que el camino relativo siempre empiece con ./ porque
        # os.path.abspath('/la/raiz/./uno/dos') = '/la/raiz/uno/dos'
        if rel_path != '.':
            rel_path = './' + rel_path.rstrip('./')
        self.actual_dir = rel_path
        self.labels = rel_path.split(self.path_obj.SEP)
        self.set_active_index(len(self.labels) - 1, draw_focus=draw_focus)
        if not self.path_obj.isdir(path):
            self.path_obj.actual_dir = path

    # Utility methods

    def join(self, *args):
        sep = self.path_obj.SEP
        return sep.join(args)

    def build_popup(self):
        aPath = self.getActivePath()
        if aPath.isDir:
            wdir = self.path_obj.walk(aPath.path)
            adir, dirs, files = next(wdir)
            # dirs = list(f'{item}/' for item in dirs if not item.startswith('__'))
            dirs = list(item for item in dirs if not item.startswith('__'))
            next_index = aPath.index + 1
            menu_list = dirs + files
            # self.menu_list = menu_list = dirs + files
            try:
                next_label = self.labels[next_index]
                next_index = menu_list.index(next_label)
            except:
                next_index = 0
            self.popup_menu.delete(0, tk.END)
            [
                self.popup_menu.add(
                    'cascade' if x in dirs else 'command',
                    label=x.rstrip('/'),
                    menu=None
                ) for x in menu_list
            ]
            self.popup_menu.activate(next_index)

    # Callbacks methods

    def onCanvasHrzArrowsEvent(self, event):
        inc = 1 if event.keysym == 'Right' else -1
        self.set_active_index(self.pfocus + inc)

    def onCanvasDownArrowEvent(self, event=None):
        aPath = self.getActivePath()
        if not aPath.isDir or len(self.path_obj.listdir(aPath.path)) == 0:
            self.set_active_index(aPath.index - 1)
            aPath = self.getActivePath()
        pfocus = self.polygon_ids[aPath.index]
        bbox = self.bbox(pfocus)
        x, y = bbox[0] + self.winfo_rootx() + 1, bbox[3] + self.winfo_rooty() + 1
        self.popup_menu.focus_set()
        try:
            self.popup_menu.tk_popup(x, y)
        except Exception as e:
            print(e)
        finally:
            self.popup_menu.grab_release()
            pass

    def onCanvasClickEvent(self, event):
        self.focus_set()
        x, y = event.x, event.y
        pfocus = self.identify_index(x, y)
        if pfocus:
            self.set_active_index(pfocus)
            self.onCanvasDownArrowEvent(event)

    def identify_index(self, x, y):
        polygons = self.find_overlapping(x, y, x, y)
        polygons = [polygon for polygon in polygons if self.type(polygon) == 'polygon']
        pfocus = None
        if polygons:
            next_pfocus = polygons[0]
            try:
                pfocus = self.polygon_ids.index(next_pfocus)
            except:
                pass
        return pfocus

    def onMenuKeyboardEvent(self, event):
        self.event_generate('<Escape>')     # Este evento retira el menu de la ventana
        keysym = event.keysym
        if keysym in ('Left', 'Right'):
            inc = 1 if event.keysym == 'Right' else -1
            self.set_active_index(self.pfocus + inc)
        elif keysym == 'Return':
            indx = self.popup_menu.index(tk.ACTIVE)
            label = self.popup_menu.entrycget(indx, 'label')
            prev_pfocus, path, _ = self.getActivePath()
            path = os.path.join(path, label)
            self.setActivePath(path)
        aPath = self.getActivePath()
        if aPath.isDir:
            self.onCanvasDownArrowEvent()
        else:
            self.focus_get()


class PathObj(ABC):
    SEP = os.sep

    @abstractmethod
    def isdir(self, path):
        pass

    @abstractmethod
    def listdir(self, path):
        pass

    @abstractmethod
    def walk(self, path):
        pass

    @abstractmethod
    def relpath(self, path, base_path):
        pass

    def set_master(self, master):
        pass

    def validate_path(self, apath):
        path = os.path.abspath(apath)
        # Solo se permiten los path que se derivan del directorio raiz. Cuando se tiene un path
        # que se deriva de otro directorio, se entrega el directorio raiz.
        if not path.startswith(self.root):
            return self.root
        # Si el candidato a activepath (apath) resulta ser un directorio, se adicionan a él
        # todos los directorios que contienen un solo directorio hasta encontrar: 1 - un archivo o
        # 2 - Un directorio con más de un hijo.
        while self.isdir(path):
            try:
                label, *listLabelsDir = self.listdir(path)
            except:
                break   # Directorio vacío
            if len(listLabelsDir):
                break
            path = os.path.join(path, label)
        return path


class DirectoryObj(PathObj):

    def __init__(self, root_dir, actual_dir):
        assert actual_dir.startswith(root_dir)
        self.root = root_dir.rstrip(self.SEP)
        self.actual_dir = actual_dir

    def isdir(self, path):
        return os.path.isdir(path)

    def listdir(self, path):
        return os.listdir(path)

    def walk(self, path):
        return os.walk(path)

    def relpath(self, path, base_path):
        return os.path.relpath(path, base_path)


class TkkTreeObj(PathObj):

    def __init__(self, tkktree):
        self.tkkTree = tkktree
        tkktree.bind('<<ActiveSelection>>', self.selectionMonitor, add='+')
        self.master = None
        self._iid_map = {'': '', '/.': '', '/': ''}

    def selectionMonitor(self, event):
        if not hasattr(event, "data"):
            treeview = event.widget
            master = self.master
            # Al ser un evento generado por el treeview mismo, se va a la fija con el focus
            # para identificar el proximo selected. No se puede estar seguro en que posición
            # se llame este callback.
            iid = treeview.focus()
            path = self._path_for_iid(iid)
            try:
                master.setActivePath(path)
            except:
                pass
        pass

    @property
    def root(self):
        return '/'

    @property
    def actual_dir(self):
        selected = self.tkkTree.tag_has('selected')
        iid = selected[0] if selected else ''
        return self._path_for_iid(iid)

    @actual_dir.setter
    def actual_dir(self, path):
        if self.actual_dir == path:
            return
        iid = self._iid_for_path(path)
        self.tkkTree.see(iid)
        self.tkkTree.selection_set(iid)
        self.tkkTree.focus(iid)
        with userinterface.event_data(data=path) as event:
            self.tkkTree.event_generate('<<ActiveSelection>>')
        pass

    def set_master(self, master):
        self.master = self.master or master

    def _path_for_iid(self, iid):
        path = [iid]
        child_id = iid
        while True:
            parent_id = self.tkkTree.parent(child_id)
            if not parent_id:
                break
            path.append(parent_id)
            child_id = parent_id
        path = os.path.join(*map(lambda x: self.tkkTree.item(x, 'text'), path[::-1]))
        return os.path.join(self.root, path)

    def _iid_for_path(self, path):
        if path not in self._iid_map:
            key = path
            assert path.startswith(self.root)
            tree = self.tkkTree
            path = path.split(self.SEP)
            iid = path.pop(0)       # se supone que path inicia con ./ es decir la raiz iid=''
            while path:
                children = [(x, tree.item(x, 'text')) for x in tree.get_children(iid)]
                ch_iids, ch_labels = zip(*children)
                label = path.pop(0)
                try:
                    npos = ch_labels.index(label)
                    iid = ch_iids[npos]
                except:
                    break
            self._iid_map[key] = iid
        else:
            iid = self._iid_map[path]
        return iid

    def listdir(self, path):
        iid = self._iid_for_path(path)
        children = self.tkkTree.get_children(iid)
        return [self.tkkTree.item(x, 'text') for x in children]

    def walk(self, path):
        tree = self.tkkTree
        iid = self._iid_for_path(path)
        stack = collections.deque([iid])
        while stack:
            iid = stack.popleft()
            children = tree.get_children(iid)
            f_iids = [x for x in children if not len(tree.get_children(x))]
            d = sorted([(tree.item(x, 'text'), x) for x in set(children).difference(f_iids)])
            path = self._path_for_iid(iid)
            d_names, d_iids = zip(*d) if d else ([], [])

            f_names = sorted([tree.item(x, 'text') for x in f_iids])
            yield path, list(d_names), f_names
            stack.extendleft(d_iids[::-1])
        pass

    def relpath(self, path, base_path):
        return os.path.dirname(path, base_path)

    def isdir(self, path):
        iid = self._iid_for_path(path)
        children = self.tkkTree.get_children(iid)
        return bool(len(children))


class TkMenuObj(PathObj):

    def __init__(self, tkMenu):
        self.tkMenu = tkMenu

    @property
    def root(self):
        return self.tkMenu.cget('title')

    @property
    def actual_dir(self):
        return self.root + self.SEP

    def _path_for_iid(self, iid):
        path = []
        parent_id, npos = iid
        while isinstance(parent_id, tk.Menu):
            if npos:
                path.append(parent_id.entrycget(npos, 'label'))
                npos = None
            path.append(parent_id.cget('title'))
            menu_name = parent_id.winfo_parent()
            parent_id = parent_id.nametowidget(menu_name)
        path = self.SEP.join(path[::-1])
        return self.root + self.SEP + path

    def _iid_for_path(self, path):
        assert path.startswith(self.root + self.SEP)
        root_pattern = '.' + self.SEP
        path = path[len(self.root):].replace(root_pattern, '').split(self.SEP)
        path.pop(0)
        iid, npos = self.tkMenu, None   # se supone que path inicia con el menu raiz
        while path:
            label = path.pop(0)
            children = [
                (x, iid.entrycget(x, 'label')) for x in range(iid.index(tk.END) or 0)
                if iid.type(x) not in (tk.SEPARATOR, 'tearoff')
            ]
            try:
                ch_index, ch_labels = zip(*children)
                npos = ch_labels.index(label)
                menu = iid.entrycget(ch_index[npos], 'menu')
                iid = iid.nametowidget(menu)
            except ValueError:
                break
            except:
                return iid, npos
        return iid, None

    def listdir(self, path):
        iid = self._iid_for_path(path)
        iid, npos = iid
        assert npos is None
        children = [
            iid.entrycget(x, 'label') for x in range(iid.index(tk.END) or 0)
            if iid.type(x) not in (tk.SEPARATOR, 'tearoff')
        ]
        return children

    def walk(self, path):
        assert self.isdir(path), f'the path "{path}" is not a directory'
        # tree = self.tkMenu
        iid, _ = self._iid_for_path(path)   # Por ser un directory npos es None
        stack = collections.deque([iid])
        while stack:
            iid = stack.popleft()
            children = [(x, iid.type(x)) for x in range(iid.index(tk.END) or 0)]
            f_names = [iid.entrycget(x, 'label') for x, y in children if y not in (tk.CASCADE, tk.SEPARATOR, 'tearoff')]
            d = [(iid.entrycget(x, 'label'), iid.entrycget(x, 'menu')) for x, y in children if y == tk.CASCADE]
            path = self._path_for_iid((iid, None))
            d_names, d_iids = zip(*d) if d else ([], [])

            yield path, d_names, f_names
            stack.extendleft(iid.nametowidget(x) for x in d_iids[::-1])
        pass

    def relpath(self, path, base_path):
        b_path = base_path.rstrip('/') + '/'
        if path.startswith(b_path):
            npos = len(b_path)
            return path[npos:] if path != b_path else '.'
        if path.startswith('./'):
            return base_path.count('/') * '/..' + path
        return self.root + self.SEP + path if path else self.root

    def isdir(self, path):
        path = path.replace('.' + self.SEP, '')
        iid = self._iid_for_path(path)
        iid, npos = iid
        return npos is None


class StrListObj(PathObj):

    def __init__(self, strlist, root_dir):
        assert root_dir.startswith(self.SEP)
        assert all(x.startswith(root_dir) for x in strlist)
        self.strlist = strlist
        self.root = root_dir.rstrip(self.SEP)
        self.actual_dir = self.root

    def isdir(self, path):
        dmy = self.listdir(path)
        return bool(dmy)

    def listdir(self, path):
        dmy = [x for x in self.strlist if x.startswith(f'{path}/')]
        return [os.path.split(x)[1] for x in dmy]

    def walk(self, path):
        stack = [path]
        namelist = set(self.strlist)
        path = ''
        while stack:
            dummy = stack.pop(0)
            while isinstance(dummy, int):
                npos = dummy
                path = path[:npos]
                dummy = stack.pop(0)
                if stack and not isinstance(stack[0], int):
                    stack.insert(0, npos)
            path = '/' + f'{path.rstrip("/")}/{dummy}/'.lstrip('/')
            files = []
            dirs = set()
            n = len(path)
            for info in namelist:
                if info.startswith(path):
                    suffix = info[n:]
                    try:
                        prefix, suffix = suffix.split('/', 1)
                        dirs.add(prefix)
                    except:
                        if suffix:
                            files.append(suffix)
            dirs = sorted(dirs)
            files.sort()
            yield path, dirs, files
            to_purge = [f'{path}{dummy}'.lstrip('/') for dummy in files]
            namelist.difference_update(to_purge)
            if len(dirs) > 1:
                dirs.insert(1, len(path))
            stack = dirs + stack

    def relpath(self, path, base_path):
        return os.path.relpath(path, base_path)


def navigationFactory(master, path_obj, **kwargs):
    '''
    Factory for NavigationBar by identifying the proper path_obj.
    :param master: tk.Widget | tk.Tk. Parent of the navigation bar to create.
    :param path_obj: str. Name of the attribute in tk.Tk object that owns master.
    :param kwargs: dict. Configurations options for tk.Canvas.
    :return: NavigationBar instance.
    '''
    try:
        top = master.winfo_toplevel()
        obj = getattr(top, path_obj)
        if isinstance(obj, tkk.Treeview):
            path_obj = TkkTreeObj(obj)
        elif isinstance(obj, tk.Menu):
            path_obj = TkMenuObj(obj)
        elif isinstance(obj, (bytes, str)):
            path_obj = DirectoryObj(obj, obj)
    except AttributeError:
        dmy = os.path.abspath('.')
        path_obj = DirectoryObj(dmy, dmy)
    return BreadCumb(master, path_obj=path_obj, **kwargs)


def pathObjWrapper(obj):
    if isinstance(obj, PathObj):
        path_obj = obj
    elif isinstance(obj, tkk.Treeview):
        path_obj = TkkTreeObj(obj)
    elif isinstance(obj, tk.Menu):
        path_obj = TkMenuObj(obj)
    elif isinstance(obj, (list, tuple)) and all(isinstance(x, str) for x in obj):
        obj = ['/' + x.lstrip('/') for x in obj]
        root_dir = os.path.commonpath(obj)
        path_obj = StrListObj(obj, root_dir)
    elif isinstance(obj, (bytes, str)):
        path_obj = DirectoryObj(obj, obj)
    else:
        raise AttributeError(f'{str(obj)} is not a valid path_obj')
    return path_obj

def main():
    top = tk.Tk()
    top.attributes('-zoomed', True)
    base_dir = '/mnt/c/Users/Alex Montes/PycharmProjects/mywidgets/'
    initial_dir = '/mnt/c/Users/Alex Montes/PycharmProjects/mywidgets/src/Widgets/Custom/navigationbar.py'
    path_obj = DirectoryObj(base_dir, initial_dir)
    nbar = BreadCumb(top, path_obj)
    top.mainloop()

if __name__ == '__main__':
    # main()
    import zipfile
    import tkinter.ttk as ttk

    def walk_apk(start_path, zf):
        stack = [start_path]
        namelist = set(zf.namelist())
        path = ''
        while stack:
            dummy = stack.pop(0)
            while isinstance(dummy, int):
                npos = dummy
                path = path[:npos]
                dummy = stack.pop(0)
                if stack and not isinstance(stack[0], int):
                    stack.insert(0, npos)
            path = f'{path.rstrip("/")}/{dummy}/'.lstrip('/')
            files = []
            dirs = set()
            n = len(path)
            for info in namelist:
                if info.startswith(path):
                    suffix = info[n:]
                    try:
                        prefix, suffix = suffix.split('/', 1)
                        dirs.add(prefix)
                    except:
                        files.append(suffix)
            dirs = sorted(dirs)
            files.sort()
            yield path, dirs, files
            to_purge = [f'{path}{dummy}'.lstrip('/') for dummy in files]
            namelist.difference_update(to_purge)
            if len(dirs) > 1:
                dirs.insert(1, len(path))
            stack = dirs + stack


    top = tk.Tk()
    top.attributes('-zoomed', True)

    case = 'strlistobj'
    if case == 'strlistobj':
        apkname = '/mnt/c/Users/Alex Montes/PycharmProjects/TestFiles/TeaTV-v9.9.6r_build_111-Mod_v2.apk'
        zf = zipfile.ZipFile(apkname)
        root_dir = '/zf'
        strlist = [f'{root_dir}/{x}' for x in zf.namelist()]
        path_obj = obj_name = StrListObj(strlist, root_dir)
        next(path_obj.walk(root_dir))
        pass
    elif case == 'tkktree':
        def onActiveSelection(event=None):
            treeview = event.widget
            selected = treeview.tag_has('selected')
            for nodeid in selected:
                treeview.item(nodeid, tags='')
            nodeid = treeview.focus()
            treeview.item(nodeid, tags='selected')

        apkname = '/mnt/c/Users/Alex Montes/PycharmProjects/TestFiles/TeaTV-v9.9.6r_build_111-Mod_v2.apk'
        zf = zipfile.ZipFile(apkname)
        tree = ttk.Treeview(top)
        parent_id_map = {'': ''}
        zf = zipfile.ZipFile(apkname)
        path = ''
        for root, d_names, f_names in walk_apk(path, zf):
            root = root.rstrip('/')
            path_id = parent_id_map[root]
            for f_name in f_names:
                tree.insert(
                    path_id,
                    'end',
                    text=f_name,
                )
            for d_name in d_names:
                child_id = tree.insert(
                    path_id,
                    'end',
                    text=d_name,
                )
                path = f'{root}/{d_name}'.lstrip('/')
                parent_id_map[path] = child_id

        tree.pack(side=tk.LEFT, fill=tk.Y)
        tree.tag_configure('selected', background='light green')
        tree.event_add('<<ActiveSelection>>', '<Double-1>', '<Return>')
        tree.bind('<<ActiveSelection>>', onActiveSelection)
        top.treeview = tree

        obj_name = 'treeview'
    elif case == 'tkmenu':
        menufile = '/mnt/c/Users/Alex Montes/PycharmProjects/mywidgets/src/Data/menu/file_menu.xml'
        menuPanel = userinterface.getLayout(menufile)
        menu = userinterface.menuFactory(top, selPane=menuPanel)
        path_obj = obj_name = TkMenuObj(menu)
        # for path, d_names, f_names in path_obj.walk('master/'):
        #     print(path, d_names, f_names)
    elif case == 'tkktree_methods':
        apkname = '/mnt/c/Users/Alex Montes/PycharmProjects/TestFiles/TeaTV-v9.9.6r_build_111-Mod_v2.apk'
        zf = zipfile.ZipFile(apkname)
        tree = ttk.Treeview(top)
        tree.pack(side=tk.LEFT, fill=tk.Y, anchor=tk.NW)
        parent_id_map = {'': ''}
        zf = zipfile.ZipFile(apkname)
        path = ''
        for root, d_names, f_names in walk_apk(path, zf):
            root = root.rstrip('/')
            path_id = parent_id_map[root]
            for f_name in f_names:
                tree.insert(
                    path_id,
                    'end',
                    text=f_name,
                )
            for d_name in d_names:
                child_id = tree.insert(
                    path_id,
                    'end',
                    text=d_name,
                )
                path = f'{root}/{d_name}'.lstrip('/')
                parent_id_map[path] = child_id

        path_obj = obj_name = TkkTreeObj(tree)
        path = '/org'
        path_obj.isdir(path)
        path = '/org/apache/xmlrpc/client'
        iid = path_obj._iid_for_path(path)
        assert path == path_obj._path_for_iid(iid)
        bflag = path_obj.isdir('/assets/Bridge.js')

        for path, d_names, f_names in path_obj.walk('/org'):
            print(path, d_names, f_names)
    elif case == 'directory':
        base_dir = '/mnt/c/Users/Alex Montes/PycharmProjects/mywidgets/env/'
        initial_dir = '/mnt/c/Users/Alex Montes/PycharmProjects/mywidgets/src/Widgets/Custom/navigationbar.py'
        top.base_dir = base_dir
        obj_name = 'base_dir'
    elif case == 'rolling_menu':

        def post_cb():
            menu.delete(0, tk.END)
            for k in range(30):
                menu.add('command', label=f'comm{k}')
            menu.activate(5)

        btn = tk.Menubutton(top, text='MenuButton')
        menu = RollingMenu(btn, postcommand=post_cb)
        btn.config(menu=menu)
        btn.pack(side=tk.LEFT, anchor='n')

        def dir_menu(menu, path):
            menu.delete(0, tk.END)
            apath, dirs, files = next(os.walk(path))
            for dir in dirs:
                smenu = RollingMenu(top, title=dir, tearoff=0)
                smenu['postcommand'] = lambda x=smenu, y=os.path.join(apath, dir): dir_menu(x, y)
                menu.insert(tk.END, 'cascade', label=dir, menu=smenu)

            for file in files:
                menu.insert(tk.END, 'command', label=file)

        def cb():
            fmenu.focus_set()
            fmenu.tk_popup(10, 10)


        base_dir = '/mnt/c/Users/Alex Montes/PycharmProjects/mywidgets/env/'
        fmenu = RollingMenu(top, title='main', tearoff=0, req_nitems=4)
        fmenu['postcommand'] = lambda x=fmenu, y=base_dir: dir_menu(x, y)

        # btn1 = tk.Button(top, text='dir_menu', command=cb)
        # btn1.pack(side=tk.LEFT, anchor='n')
        top['menu'] = fmenu

    try:
        # nbar = navigationFactory(top, obj_name)
        nbar = BreadCumb(top, path_obj=obj_name)
        nbar.pack(side=tk.LEFT, fill=tk.X, expand=tk.YES, anchor=tk.NW)
    except Exception as e:
        print(str(e))
    finally:
        top.mainloop()
