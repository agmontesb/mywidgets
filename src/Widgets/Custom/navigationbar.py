# -*- coding: utf-8 -*-
import collections
import os
import tkinter as tk
import tkinter.font as tkFont


class NavigationBar(tk.Canvas):
    def __init__(self, master, base_dir, initial_dir, **kwargs):
        super().__init__(master, **kwargs)
        self.base_dir = base_dir
        self.actual_dir = os.path.relpath(initial_dir, base_dir)
        self.labels = self.actual_dir.split(os.path.sep)
        self.height = 25

        self.pfocus = len(self.labels) - 1
        self.polygon_ids = []
        self.text_ids = []
        self.setGui()
        self.pack(side=tk.TOP, fill=tk.BOTH, expand=tk.YES)
        pass

    def _hrz_arrows(self, event):
        inc = 1 if event.keysym == 'Right' else -1
        self.set_active_index(self.pfocus + inc)

    def set_active_index(self, next_pfocus):
        next_pfocus = next_pfocus % len(self.labels)
        if self.pfocus is not None:
            pfocus = self.polygon_ids[self.pfocus]
            self.itemconfig(pfocus, fill='white')
        if next_pfocus is not None:
            polygon = self.polygon_ids[next_pfocus]
            self.focus(polygon)
            self.itemconfig(polygon, fill='green')
        self.pfocus = next_pfocus
        return self.getActivePath()

    def _clickEvent(self, event):
        x, y = event.x, event.y
        polygons = self.find_overlapping(x, y, x, y)
        polygons = [polygon for polygon in polygons if self.type(polygon) == 'polygon']
        if polygons:
            next_pfocus = polygons[0]
            try:
                pfocus = self.polygon_ids.index(next_pfocus)
            except:
                pfocus = None
            self.set_active_index(pfocus)
            self.do_popup(event)

    def setGui(self):
        # self = canvas = tk.Canvas(self)
        canvas = self
        canvas.pack(side=tk.TOP, fill=tk.X, expand=tk.YES)
        canvas.tag_bind('arrow', '<Button-1>', self._clickEvent)
        canvas.event_add('<<HRZ_ARROWS>>', '<Left>', '<Right>')
        canvas.bind('<<HRZ_ARROWS>>', self._hrz_arrows)
        # self.bind_all("<Button-3>", self.do_popup)
        canvas.bind("<Down>", self.do_popup)
        canvas.focus_set()

        self.popup_menu = tk.Menu(self, tearoff=0, postcommand=self.build_popup, relief=tk.FLAT)
        self.popup_menu.bind('<<HRZ_ARROWS>>', self.build_cascade)
        self.popup_menu.bind('<Return>', self.build_cascade)

        self.setupCanvas(*self.labels)
        pass

    def setupCanvas(self, *labels):
        deltax = 4
        height = self.height
        font = tkFont.Font(self)
        if len(self.polygon_ids) > 0:
            last_polygon_id = self.polygon_ids[-1]
            x = self.coords(last_polygon_id)[2] + deltax
            pass
        else:
            x = 0
        for k, lbl in enumerate(labels):
            width = font.measure(lbl) + height/4
            v1 = [x, 0]
            v2 = [v1[0] + width, 0]
            v3 = [v2[0] + height/2, height/2]
            v4 = [v2[0], height]
            v5 = [v1[0], height]
            v6 = [(v1[0] + height/2) if v1[0] != 0 else 0, height/2]
            vertices = v1 + v2 + v3 +v4 + v5 + v6
            pid = self.create_polygon(
                *vertices,
                fill='white',
                outline='black',
                tag='arrow'
            )
            self.polygon_ids.append(pid)
            tid = self.create_text(
                (v6[0] + v2[0])/2, height/2,
                text=lbl,
                anchor=tk.CENTER,
                tag='arrow'
            )
            self.text_ids.append(tid)
            x += width + deltax
            pass

    def getActivePath(self):
        ActivePath = collections.namedtuple('ActivePath', ('index', 'path', 'isDir'))
        path = os.path.join(self.base_dir, *self.labels[:self.pfocus + 1])
        isfile = os.path.isdir(path)
        return ActivePath(self.pfocus, path, isfile)

    # create menu
    def build_cascade(self, event):
        keysym = event.keysym
        if keysym == 'Return':
            next_pfocus = self.pfocus + 1
            indx = self.popup_menu.index(tk.ACTIVE)
            label = self.popup_menu.entrycget(indx, 'label')
            bflag = next_pfocus < len(self.labels) and self.labels[next_pfocus] == label
            if not bflag:
                if next_pfocus < len(self.labels):
                    for pid, ptext in zip(self.polygon_ids[next_pfocus:], self.text_ids[next_pfocus:]):
                        self.delete(pid, ptext)
                    del(self.polygon_ids[next_pfocus:])
                    del(self.text_ids[next_pfocus:])
                    del(self.labels[next_pfocus:])
                activePath = self.getActivePath()
                labels = []
                while True:
                    labels.append(label)
                    path = os.path.join(activePath.path, *labels)
                    if not os.path.isdir(path):
                        break
                    listLabelsDir = os.listdir(path)
                    if len(listLabelsDir) != 1:
                        break
                    label = listLabelsDir[0]
                    newpath = os.path.join(path, label)
                    if not os.path.isdir(newpath):
                        break
                self.labels.extend(labels)
                self.setupCanvas(*labels)
                self.set_active_index(activePath.index + len(labels) - 1)
            keysym = 'Right'
        self.event_generate('<Escape>')
        self.event_generate(f'<{keysym}>')
        aPath = self.getActivePath()
        if aPath.isDir:
            self.do_popup()

    def build_popup(self):
        aPath = self.getActivePath()
        if aPath.isDir:
            self.popup_menu.delete(0, tk.END)
            wdir = os.walk(aPath.path)
            adir, dirs, files = next(wdir)
            dirs = list(item for item in dirs if not item.startswith('__'))
            next_index = aPath.index + 1
            try:
                next_label = self.labels[next_index]
                if next_label == 'navigationbar.py':
                    next_label = 'navigationbar.py'
                next_index = (dirs + files).index(next_label)
            except:
                next_index = 0
            [
                self.popup_menu.add_cascade(
                    label=item,
                    menu=None
                ) for item in dirs
            ]
            # self.popup_menu.add_separator()
            [
                self.popup_menu.add_command(
                    label=item,
                    command=None
                ) for item in files
            ]
            self.popup_menu.activate(next_index)

    # display menu on right click
    def do_popup(self, event=None):
        aPath = self.getActivePath()
        if not aPath.isDir:
            aPath = self.set_active_index(aPath.index - 1)
        pfocus = self.polygon_ids[aPath.index]
        bbox = self.bbox(pfocus)
        x, y = bbox[0] + self.winfo_rootx() + 1, bbox[3] + self.winfo_rooty() + 1
        self.popup_menu.focus_set()
        try:
            self.popup_menu.tk_popup(int(x), int(y))
            print(f'tk_popup con menu con {self.popup_menu.entrycget(0, "label")}')
        except Exception as e:
            self.popup_menu.grab_release()
            print('except grab_release')
            pass
        finally:
            self.popup_menu.grab_release()
            print('finally grab_release')
            pass


if __name__ == '__main__':
    top = tk.Tk()
    base_dir = '/mnt/c/Users/Alex Montes/PycharmProjects/'
    initial_dir = '/src/Widgets/Custom/navigationbar.py'
    nbar = NavigationBar(top, base_dir, initial_dir)
    top.mainloop()