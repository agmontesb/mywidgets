# -*- coding: utf-8 -*-
import collections
import itertools
import tkinter
import tkinter as tk
import tkinter.font as tkFont
import tkinter.messagebox as tkMessage
import xml.etree.ElementTree as ET
import re

from Tools.uiStyle.cssflexbox import CssFlexBox
from userinterface import getWidgetInstance
from Tools.uiStyle.cssgrid import CssGrid


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

def nameElements(htmlstr, k=-1):
    import src.Tools.uiStyle.CustomRegEx as CustomRegEx
    htmlstr = '''<!DOCTYPE html>
    <html>
    <head>
    <style>
    p {
      text-align: center;
      color: red;
    }
    </style>
    </head>
    <body>

    <p>Every paragraph will be affected by the style.</p>
    <p id="para1">Me too!</p>
    <p>And me!</p>

    </body>
    </html>'''

    htmlstr = '''<head>
    <uno id="alex" />
    <dos />
    <tres>esto es el freeze</tres>
    </head>'''

    cmpobj = CustomRegEx.compile('(?#<__TAG__ __TAG__=tag id=_id_ >)')

    from_pos = 0
    to_pos = len(htmlstr)
    answ = []
    it = cmpobj.finditer(htmlstr, from_pos, to_pos)
    stack = [(m.span(), m.groups()) for m in it]

    while stack:
        (pini, pfin), (tag, id) = stack.pop(0)
        if id is None:
            k += 1
            id = str(k)
        answ.append(((pini, pfin), (tag, id)))

        from_pos = htmlstr[pini:pfin].find('>') + pini + 1
        to_pos = htmlstr[pini:pfin].rfind('<') + pini

        bflag = from_pos != -1 and to_pos != -1 and from_pos < to_pos
        if bflag:
            it = cmpobj.finditer(htmlstr, from_pos, to_pos)
            stack = [(m.span(), m.groups()) for m in it] + stack
    return answ


if __name__ == '__main__':
    caso = 'cssflex_place'
    if caso == 'cssflex_place':

        def set_align_self(align, wsize, msize):
            match align:
                case 'stretch':
                    return 0, msize
                case 'flex-start' | 'start' | 'self-start':
                    return 0, wsize
                case 'center':
                    return (msize - wsize) // 2, wsize
                case 'flex-end' | 'end' | 'self-end':
                    return msize - wsize, wsize


        def set_justify_content(self, event, widgets, axis=None, static_len=0, flex_gap=0, justify_content='center', isreverse=False):
            flex_axis, cross_axis = axis, ('width', 'height')[axis == 'width']
            mflex_size, mcross_size = getattr(event, flex_axis), getattr(event, cross_axis)
            axis, cross = ('x', 'y')[:: 1 - 2 * (flex_axis == 'height')]

            master = event.widget

            match justify_content:
                case 'flex-start' | 'start' | 'left':
                    beg_gap, end_gap = (0, (static_len - (len(widgets) - 1) * flex_gap))[:: 1 - 2 * isreverse]
                    gap_size = flex_gap
                case 'flex-end' | 'end' | 'right':
                    beg_gap, end_gap = ((static_len - (len(widgets) - 1) * flex_gap), 0)[:: 1 - 2 * isreverse]
                    gap_size = flex_gap
                case 'center':
                    beg_gap = end_gap = (static_len - (len(widgets) - 1) * flex_gap) // 2
                    gap_size = flex_gap
                case 'space-between' | 'space-around' | 'space-evenly':
                    n = len(widgets) - 1
                    delta_n = ('space-between', 'space-around', 'space-evenly').index(justify_content)
                    n += delta_n
                    gap_size = static_len // n
                    beg_gap = end_gap = (delta_n * gap_size) // 2

            gaps = [
                (tkinter.Frame(master, bg='blue', name=f'gap{axis}_{k:0>2d}'), 'stretch', gap_size, mcross_size)
                for k, gap_size in enumerate([beg_gap, *((len(widgets) - 1) * [gap_size]), end_gap])
            ]
            offset = 0
            if isreverse:
                widgets = widgets[::-1]
            it = itertools.chain(*zip(gaps, [*widgets, (None, None, None, None)]))
            while True:
                wdg, align_self, waxis_size, wcross_size = next(it)
                if wdg is None:
                    break
                wcross, wcross_size = set_align_self(align_self, wcross_size, mcross_size)
                params = {axis: offset, flex_axis: waxis_size, cross: wcross, cross_axis: wcross_size, 'in_': master}
                wdg.place(params)
                offset += waxis_size

        def _config_master(self, event):
            processed_slaves = self.get_process_item_attribs(event)
            names, _ = zip(*processed_slaves)

            nline = 0
            flines = []
            wslaves = []
            static_size = 0
            align_self = 'stretch'
            while nline < len(processed_slaves):
                _, gp = processed_slaves[nline]
                flex_line = gp.pop('flex-line')
                nline += flex_line['n-widgets']
                cross_size = flex_line[cross_axis]
                static_size += cross_size

                flex_line_name = f'flex_line{len(wslaves) + 1:0>2d}'
                gp['flex-line'] = flex_line_name
                flex_line['name'] = flex_line_name
                wslave = tkinter.Frame(master, name=flex_line_name, bg='red')
                wslaves.append([wslave, align_self, cross_size])
                flines.append((wslave, flex_line))

            cross_size = getattr(event, cross_axis)
            static_size = cross_size - static_size
            [x.append(cross_size) for x in wslaves]
            line_attr = {
                'axis': cross_axis, 'static_len': static_size, 'flex_gap': cross_gap,
                'justify_content': self.align_content, 'isreverse': 'reverse' in self.flex_wrap,
            }
            master.configure(width=event.width, height=event.height)
            set_justify_content(self, event, wslaves, **line_attr)

            # ===========================================================================

            wslaves = []
            npos = 0
            nslaves = len(processed_slaves)
            for wmaster, fattribs in flines:
                master_name = wmaster.winfo_name()
                while npos < nslaves:
                    name, item_attrs = processed_slaves[npos]
                    if item_attrs.get('flex-line', master_name) != master_name:
                        break
                    wdg = master.nametowidget(name)
                    align_self = item_attrs.pop('align-self')
                    wflex_size, wcross_size = item_attrs.pop(flex_axis), item_attrs.pop(cross_axis)
                    wslaves.append((wdg, align_self, wflex_size, wcross_size))
                    npos += 1
                frst_wdg = wslaves[0][0]
                wmaster.lower(belowThis=frst_wdg)
                wplace_info = wmaster.place_info()
                event = Event(widget=wmaster, width=int(wplace_info['width']), height=int(wplace_info['height']))
                static_size = fattribs['free-space']
                line_attr = {
                    'axis': flex_axis, 'static_len': static_size, 'flex_gap': flex_gap,
                    'justify_content': self.justify_content, 'isreverse': 'reverse' in self.flex_direction
                }
                set_justify_content(self, event, wslaves, **line_attr)
                wslaves = []
            pass


        justify_content = 'flex-start'
        flex_axis, cross_axis = 'width', 'height'
        flex_gap, cross_gap = 25, 25

        req_width, max_width, min_width = 300, 150, 75
        basis = 100
        grid = {
                  'flex-flow': 'row wrap',
                  'align-items': 'stretch',
                  'justify-content': 'flex-start',
                  'align-content': 'space-evenly',
                  'gap': f'{flex_gap} {cross_gap}',
        }
        cssflex = self = CssFlexBox(**grid)
        items = [
            (
                'flexible',
                {'flex': f'1 1 {basis}px', 'width': '100px', 'height': '50px'}
            ),
            (
                'inflexible',
                {'flex': f'0 0 {basis}px', 'width': '100px', 'height': '75px'}
            ),
            (
                'flex-grow',
                {'flex': f'1 0 {basis}px', 'width': '100px', 'height': '25px', 'max-width': f'{max_width}px'}
            ),
            (
                'flex-shrink',
                {'flex': f'0 1 {basis}px', 'width': '100px', 'height': '50px', 'min-width': f'{min_width}px'}
            ),
        ]

        master = tk.Tk()

        for k, (name, attrib) in enumerate(items):
            wdg = tkinter.Label(master, name=name.replace('-', '_'), text=str(k + 1), bg='green')
            cssflex.register_item(wdg, attrib)

        Event = collections.namedtuple('Event', 'widget width height')
        event = Event(widget=master, width=req_width, height=req_width)

        _config_master(self, event)

        master.mainloop()
    elif caso == 'css_units':
        class CssUnit:
            '''
            Unifica la salida de las dimensiones css a pixel
            '''
            absolute_units = 'cm|mm|in|px|pt|pc'
            relative_units = 'em|ex|ch|rem|vw|vh|vmin|vmax|%'
            units = f'{absolute_units}|{relative_units}'

            def __new__(cls, size_str: str):
                m = re.match(fr'(\d+)({cls.units})', size_str)
                try:
                    m.groups()
                    return super().__new__(cls)
                except:
                    return size_str


                return super().__new__(cls)

            def __init__(self, size_str: str):
                self._memory = (0, 0)
                try:
                    m = re.match(fr'(\d+)({self.units})', size_str)
                    size, self.unit = m.groups()
                    self.size = int(size)
                except AttributeError:
                    raise AttributeError('Not a valid css string unit')

            def config_params(self, widget, attrib):
                def on_config(event):
                    if event.widget == widget.master and self._memory != (event.width, event.height):
                        value = self._value(event, attrib)
                        params = {attrib: value}
                        widget.config(**params)
                        self._memory = (event.width, event.height)
                        print(params)
                return on_config

            def __repr__(self):
                return f'{self.size}{self.unit}'

            def value(self, widget: tk.Widget, attrib: str):
                if self.unit in self.absolute_units:
                    size, unit = self.size, self.unit
                    if unit == 'px':
                        unit = ''
                    else:       # 'cm' | 'mm' | 'in' | 'pt' | 'pc'
                        if unit == 'pc':
                            size *= 10
                            unit = 'pt'
                        match unit:
                            case 'cm':
                                size = (size * 254 * 96) // 100
                            case 'mm':
                                size = (size * 254 * 96) // 1000
                            case 'in':
                                size = size * 96
                            case 'pt':
                                size = (size * 96) // 72
                    return size
                top = widget.winfo_toplevel()
                match self.unit:
                    case '%':
                        master = widget.master
                        master.bind("<Configure>", self.config_params(widget, attrib), add=True)
                        return 1
                    case 'vw' | 'vh' | 'vmin' | 'vmax':
                        top.bind("<Configure>", self.config_params(widget, attrib), add=True)
                        return 1
                    case 'em' | 'rem' | 'ch':
                        # https://stackoverflow.com/questions/25548060/converting-pt-and-px
                        wdg = widget if self.unit != 'rem' else top
                        return self._value(wdg, attrib)

            def _value(self, obj: tk.Event, attrib: str):
                match self.unit:
                    case '%':
                        base_value = getattr(obj, attrib)
                    case 'vw' | 'vh' | 'vmin' | 'vmax':
                        vw, vh = map(lambda x: getattr(obj, x), ('width', 'height'))
                        match self.unit:
                            case 'vw':
                                base_value = vw
                            case 'vh':
                                base_value = vh
                            case 'vmin':
                                base_value = min(vw, vh)
                            case 'vmax':
                                base_value = max(vw, vh)
                    case 'em' | 'rem' | 'ch':
                        fnt_name = obj.cget('font')
                        fnt = tkFont.nametofont(fnt_name)
                        size_pt = fnt.cget('size') if self.unit != 'ch' else fnt.measure('0')
                        base_value = 100 * (size_pt * 96) // 72
                return (base_value * self.size) // 100

        print(CssUnit('25fr'))
        width1 = CssUnit('5in')
        width2 = CssUnit('75%')
        top = tk.Tk()
        top.geometry('500x500')
        lbl1 = tk.Frame(top, bg='green', height=50)
        size = width1.value(lbl1, 'width')
        lbl1.configure(width=size)
        lbl1.pack()
        lbl2 = tk.Frame(top, bg='red')
        # size = width2.value(lbl2, 'width')
        lbl2.configure(width=size, height=50)
        lbl2.pack()
        top.mainloop()
        pass
    elif caso == 'cycle_it':
        class Cycle:
            def __init__(self, it):
                self.it = it
                self.n = 0

            def __iter__(self):
                return self

            def __next__(self):
                x = self.it[self.n]
                self.n = (self.n + 1) % len(self.it)
                return x

            def reset(self):
                self.n = 0

        it = Cycle([1, 2, 3])
        print([next(it) for x in range(5)])
        it.reset()
        print([next(it) for x in range(5)])

    elif caso == 'track_template':
        import re
        import bisect

        track_template = ['50px', 'minmax(50px, 300px)', 'minmax(50px, 1fr)']

        def minmax_fnc(track_template, size_offset=0):
            size_lim = []
            params = []
            base = []
            lsup_size = []
            for k, x in enumerate(track_template):
                if x.endswith('px'):
                    x = int(x.strip('px'))
                    base.append(x)
                elif m := re.match(r'minmax\(([0-9]+)px,\s*([0-9]+)(fr|px)\)', x):
                    min_size, max_size = map(int, m.groups()[:-1])
                    base.append(min_size)
                    mtype = 1 if m.group(3) == 'fr' else -1
                    if m.group(3) == 'fr':
                        lsup_size.append([1, max_size, k])
                    else:
                        lsup_size.append([-1, max_size - min_size, k])
            lsup_size.sort()
            size_lim.append(sum(base) + size_offset)
            free_tracks = {k: '1fr' if mtype < 0 else f'{fr_mult}fr' for mtype, fr_mult, k in lsup_size}
            params.append([f'{base[k]}px' if k not in free_tracks else free_tracks[k] for k in range(len(base))])

            npos = 0
            while lsup_size[npos][0] < 0:
                n = npos
                delta = lsup_size[npos][1]
                while n < len(lsup_size):
                    k = lsup_size[n][2]
                    base[k] += delta * (1 if lsup_size[n][0] < 0 else lsup_size[n][1])
                    if lsup_size[n][0] < 0:
                        lsup_size[n][1] -= delta
                    n += 1
                size_lim.append(sum(base) + size_offset)
                free_tracks = {k: '1fr' if mtype < 0 else f'{fr_mult}fr' for mtype, fr_mult, k in lsup_size[npos + 1:]}
                params.append([f'{base[k]}px' if k not in free_tracks else free_tracks[k] for k in range(len(base))])
                npos += 1
            fnc = lambda x, keys=size_lim, confs=params: confs[max(0, bisect.bisect_left(keys, x) - 1)]
            return fnc

        fnc = minmax_fnc(track_template, 20)
        print(fnc.__defaults__)

    elif caso == 'responsive_server':
        import fnmatch

        class TopClass(tk.Tk):
            def __init__(self, layout_file, *filters):
                super().__init__()
                self.event_add('<<MENUCLICK>>', 'None')
                self.bind_all('<<MENUCLICK>>', self.on_menuclick)
                self.watched = {}
                self.to_watch = {}

                self.filters = filters or ['*.xml', '*.css']
                self.layout = layout_file

                self.setGui()
                self.pid = None
                # self.attributes('-zoomed', True)
                if self.watched:
                    self.pid = self.after(10000, self.check_watched_files)
                pass

            def setGui(self, ):
                frm_top = tk.Frame(self)
                frm_top.pack(side=tk.LEFT, fill=tk.Y)

                btn = tk.Button(
                    frm_top,
                    text='to_watch',
                    command=self.list_to_watch
                )
                btn.pack()
                frm_bottom = tk.Frame(self, name='lmaster')
                frm_bottom.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.YES)
                self.render_layout(frm_bottom)

            def on_menuclick(self, event):
                menu_master, indx = event.widget, event.data
                msg = f'MENUCLICK fire. Menu: {menu_master.cget("title")}, Menu_item:{menu_master.entrycget(indx, "label")}'
                print(msg)
                tkMessage.showinfo(title='on_menuclick', message=msg)


        top = TopClass('@data:tkinter/tkWidgetsShowcase')
        top.mainloop()
        pass

    # elif caso == 'minmax':
    #     import bisect
    #     # params.append((track_ids, dict(minsize=int(key[:-2]), weight=0)))
    #     answ = []
    #     min_size = 120
    #     nfr = 3
    #     params_base = []
    #     minmax = {
    #         (1, 5, 6): (20, 100),
    #         (3, 7): (30, 150),
    #         (4, 8): (40, 80),
    #     }
    #     delta_size = 0
    #     params = []
    #     max_items = []
    #     for track_ids, (tmin, tmax) in minmax.items():
    #         params.append((track_ids, dict(minsize=tmin, weight=1)))
    #         delta_size += tmin * len(track_ids)
    #         max_items.append((tmax, track_ids, tmin))
    #     answ.append((min_size + delta_size, params_base + params))
    #     max_items.sort()
    #
    #     total_frs = nfr + sum([len(x[1]) for x in max_items])
    #     for k, (tmax, track_ids, tmin) in enumerate(max_items):
    #         params = []
    #         delta_size = nfr * tmax
    #         for tmax, track_ids, _ in max_items[:k + 1]:
    #             delta_size += tmax * len(track_ids)
    #             params.append((track_ids, dict(minsize=tmax, weight=0)))
    #         for _, track_ids, tmin in max_items[k + 1:]:
    #             delta_size += tmax * len(track_ids)
    #             params.append((track_ids, dict(minsize=tmin, weight=1)))
    #         answ.append((min_size + delta_size, params_base + params))
    #         total_frs -= len(track_ids)
    #
    #     size_lim, params = zip(*answ)
    #     assert size_lim == (320, 920, 1080, 1330)
    #     print((x := bisect.bisect_left(size_lim, 700)), params[x - 1])
    #     exit(0)
    #
    #
    #     pass
    # if caso == 'kodiwidgets_custom_dialog':
    #     from Widgets import kodiwidgets
    #
    #     top = tk.Tk()
    #     top.attributes('-zoomed', True)
    #
    #     title = 'Zip File With Selected Files'
    #     xmlfile = '/mnt/c/Users/Alex Montes/PycharmProjects/mywidgets/src/Tools/mywinzip/res/layout/dlg_add_files_test.xml'
    #     settings = {
    #         'fname': 'NuevoZip.zip', 'fpath': '/mnt/c/Users/Alex Montes/PycharmProjects',
    #         'zip_type': 'fzip', 'cipher': False, 'fltr_type': 'fltr1',
    #     }
    #     dlg = kodiwidgets.CustomDialog(
    #         top,
    #         title=title, xmlFile=xmlfile, isFile=True, settings=settings, dlg_type='okcancel'
    #     )
    #     if dlg.result:
    #         settings.update(dlg.settings)
    #     top.mainloop()
    #
    # elif caso == 'treebuilder':
    #     import xml.etree.ElementTree as ET
    #     from xml.etree.ElementTree import XMLParser, TreeBuilder, ProcessingInstruction
    #
    #     from src.Tools.uiStyle.uicss import CssWrapper
    #
    #     pi = ProcessingInstruction('xml-stylesheet', text='type="text/css" href="style.css"')
    #
    #     exampleXml = """
    #     <!DOCTYPE html>
    #     <html>
    #     <head>
    #     <style>
    #     body {
    #       background-color: lightblue;
    #     }
    #
    #     h1 {
    #       color: white;
    #       text-align: center;
    #     }
    #
    #     p {
    #       color: red;
    #       font-family: verdana;
    #       font-size: 20px;
    #     }
    #     </style>
    #     </head>
    #     <body>
    #
    #     <h1>My First CSS Example</h1>
    #     <p>This is a paragraph.</p>
    #     <div>
    #         <style>
    #             p {
    #                 color: green;
    #             }
    #         </style>
    #       <p>This is a second paragraph.</p>
    #     </div>
    #         <style>
    #             p {
    #                 color: yellow;
    #             }
    #         </style>
    #     <p>This is a third paragraph.</p>
    #
    #     </body>
    #     </html>"""
    #
    #     class XmlSerializer:  # The target object of the parser
    #         style_strs = []
    #         wrapper = None
    #         stack = []
    #         _data = []
    #         _tail = 1
    #         _last_open = []
    #
    #         def __call__(self, htmlstr):
    #             parser = ET.XMLParser(target=self)
    #             parser.feed(htmlstr)
    #             parser.close()
    #             return self.stack
    #
    #         @property
    #         def selectors(self):
    #             return getattr(self.wrapper, 'selectors', None)
    #
    #         def start(self, tag, attrib):  # Called for each opening tag.
    #             self._flush()
    #             self.stack.append(('starttag', tag, attrib, (0, 0)))
    #             self._last_open.append(tag)
    #             self._tail = 0
    #
    #         def end(self, tag):  # Called for each closing tag.
    #             self._flush()
    #             assert self._last_open.pop() == tag, "end tag mismatch (expected %s, got %s)" % (
    #                 self._last_open[-1], tag
    #             )
    #             self.stack.append(('endttag', tag, (0, 0)))
    #             self._tail = 1
    #             if tag == 'style':
    #                 self.stack.pop()
    #                 _, _, attribs, _ = self.stack.pop()
    #                 style_str = attribs.get('_tail', '')
    #                 self.style_strs.append(style_str)
    #
    #         def pi(self, target, text=None):
    #             if target == 'xml-stylesheet':
    #                 self.style_strs.append((target, text))
    #
    #         def data(self, data):
    #             data = data.strip(' \n')
    #             if data:
    #                 self._data.append(data)
    #
    #         def close(self):  # Called when all data has been parsed.
    #             style_strs = '\n'.join(self.style_strs)
    #             self.wrapper = CssWrapper(style_strs)
    #
    #         def _flush(self):
    #             if self._data:
    #                 text = "".join(self._data)
    #                 if self.stack:
    #                     attribs = self.stack[-1][2]
    #                     # msg = "internal error (tail)" if self._tail else "internal error (text)"
    #                     # assert '_tail' in attribs, msg
    #                     attribs['_tail'] = text
    #                 self._data = []
    #
    #
    #     xmlserializer = XmlSerializer()
    #     it = xmlserializer(exampleXml)
    #     for x in it:
    #         print(x)
    #     for sel in xmlserializer.selectors:
    #         print(sel)
    # elif caso == 'css_selectors':
    #     from Tools.uiStyle import uicss
    #     selector_str = 'body #touchnav-wrapper div strong'
    #     sel = uicss.Selector(selector_str)
    #     cs = sel.compiled_selector
    #
    #     simple_selectors = [
    #         # '.intro',
    #         # '.name1.name2',
    #         # '#firstname',
    #         # '*',
    #         # 'p',
    #         # 'p.intro',
    #         # 'a[target]',
    #         'a[target=_blank]',
    #         'img[title~=flower]',
    #         # 'p[lang|=en]',
    #         # 'a[href^="https"]',
    #         # 'a[href$=".pdf"]',
    #         'a[href*="w3schools"]',
    #     ]
    #
    #     compound_selectors = [
    #         '.name1 .name2',
    #         'div, p',
    #         'div p',
    #         'div > p',
    #         'div + p',
    #         'p ~ ul',
    #     ]
    #
    #     pseudoelem_selectors = [
    #         'a:active',
    #         'p::after',
    #         'p::before',
    #         'input:checked',
    #         'input:default',
    #         'input:disabled',
    #         'p:empty',
    #         'input:enabled',
    #         'p:first-child',
    #         'p::first-letter',
    #         'p::first-line',
    #         'p:first-of-type',
    #         'input:focus',
    #         ':fullscreen',
    #         'a:hover',
    #         'input:in-range',
    #         'input:indeterminate',
    #         'input:invalid',
    #         'p:lang(it)',
    #         'p:last-child',
    #         'p:last-of-type',
    #         'a:link',
    #         '::marker',
    #         ':not(p)',
    #         'p:nth-child(2)',
    #         'p:nth-last-child(2)',
    #         'p:nth-last-of-type(2)',
    #         'p:nth-of-type(2)',
    #         'p:only-of-type',
    #         'p:only-child',
    #         'input:optional',
    #         'input:out-of-range',
    #         'input::placeholder',
    #         'input:read-only',
    #         'input:read-write',
    #         'input:required',
    #         ':root',
    #         '::selection',
    #         '#news:target',
    #         'input:valid',
    #         'a:visited',
    #     ]
    #
    #     selectors = simple_selectors
    #     for selector_str in selectors:
    #         sel = uicss.Selector(selector_str)
    #         msg = f'{sel.selector_str=} {sel.is_valid} '
    #         if sel.is_valid:
    #             cp = sel.compiled_selector
    #             msg += f'pattern={cp.pattern} tag_pattern={cp.tag_pattern} req_attrs={cp.req_attrs}'
    #         print(msg)
    #     pass
    # elif caso == 'imageprocessor_label':
    #     top = tk.Tk()
    #
    #     font = ImageFont.truetype('/usr/share/fonts/truetype/ubuntu/UbuntuMono-B.ttf', 50)
    #     label = 'Texto de Prueba'
    #     bg = Image.new('RGBA', (500, 100), (128, 128, 128, 128))
    #     bg = bg.rotate(90, expand=1)
    #     options = dict(
    #         angle=90,
    #         width=200,
    #         shadowcolor='black',
    #         alignment='center',
    #         yalignment='center',
    #         background=bg,
    #     )
    #     labelImg = getLabel(label, font, 'blue', **options)
    #     labelImg = ImageTk.PhotoImage(labelImg)
    #     canvas = tk.Canvas(top)
    #     canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=tk.YES)
    #     canvas.create_image(top.winfo_screenwidth()//2, top.winfo_screenheight()//2, image=labelImg)
    #
    #     top.attributes('-zoomed', True)
    #     top.mainloop()
    # elif caso == 'menu_factory':
    #     class TopClass(tk.Tk):
    #         def __init__(self):
    #             super().__init__()
    #             self.event_add('<<MENUCLICK>>', 'None')
    #             self.bind_all('<<MENUCLICK>>', self.on_menuclick)
    #             # file_path = 'src/Data/menu/file_menu.xml'
    #             # selpane = userinterface.getLayout(file_path)
    #             # menuBar = menuFactory(self, selpane)
    #             # menuBar.config(title=os.path.basename(os.path.splitext(file_path)[0]))
    #             # self['menu'] = menuBar
    #             self.setGui()
    #             self.attributes('-zoomed', True)
    #             pass
    #
    #         def setGui(self):
    #             file_path = 'Data/tkinter/tkUiEditor.xml'
    #             xmlObj = userinterface.getLayout(file_path)
    #             settings = {}
    #             fframe = formFrame(master=self, settings=settings, selPane=xmlObj)
    #             equations_manager.set_initial_widget_states()
    #             fframe.pack(side=tk.TOP, fill=tk.BOTH, expand=tk.YES, anchor=tk.NE)
    #
    #         def callback1(self):
    #             msg = 'Hello from callback1'
    #             print(msg)
    #             tkMessage.showinfo(title='callback1', message=msg)
    #
    #         def on_menuclick(self, event):
    #             menu_master, indx = event.widget, event.data
    #             msg = f'MENUCLICK fire. Menu: {menu_master.cget("title")}, Menu_item:{menu_master.entrycget(indx, "label")}'
    #             print(msg)
    #             tkMessage.showinfo(title='on_menuclick', message=msg)
    #
    #     top = TopClass()
    #     top.mainloop()
    # elif caso == 'test_css':
    #     top = tk.Tk()
    #     file_path = 'Data/tkinter/tkUiEditor.xml'
    #     file_path = 'Data/tkinter/tkGeometricManagers.xml'
    #     xmlObj = getLayout(file_path)
    #     settings = {}
    #     # fframe = formFrame(master=top, settings=settings, selPane=xmlObj)
    #     fframe = tk.Frame(top, name='fframe')
    #     regWidget = lambda x, y, z: None
    #     newPanelFactory(
    #         master=fframe,
    #         selpane=xmlObj,
    #         genPanelModule=None,
    #         setParentTo='root',
    #         registerWidget=regWidget,
    #     )
    #     equations_manager.set_initial_widget_states()
    #     fframe.pack(side=tk.TOP, fill=tk.BOTH, expand=tk.YES, anchor=tk.NE)
    #     top.mainloop()
    # elif caso == 'type_hinting':
    #     from typing import Protocol, runtime_checkable
    #     from typing import Iterable, Iterator, MutableMapping
    #
    #     @runtime_checkable
    #     class TreeLike(Iterable['TreeLike'], Protocol):
    #         tag: str
    #         attrib: MutableMapping[str, str]
    #
    #     class MyTree(TreeLike):
    #         def __init__(self, tag: str, **kwargs: str) -> None:
    #             self.tag = tag
    #             self.attrib = kwargs
    #
    #         def __iter__(self) -> Iterator['MyTree']:
    #             item = 0
    #             while item < 10:
    #                 yield self.__class__(str(item))
    #                 item += 1
    #
    #     dmy = MyTree('alex', uno='1', dos='3')
    #     assert isinstance(dmy, Iterable)
    #     assert isinstance(dmy, TreeLike)
    # else:
    #     nameElements('')
    #     top = tk.Tk()
    #     if caso == 'tkinter':
    #         layoutfile = os.path.join('./data/tkinter/', 'tkUiEditor.xml')
    #         selPane = getLayout(layoutfile)
    #         fframe = newPanelFactory(top, selPane)
    #         # fframe.pack(side=tk.TOP, fill=tk.BOTH, expand=tk.YES)
    #     elif caso == 'configure_widget':
    #         def configWidget(event):
    #             widget = event.widget
    #             ifocus = widget.tree.focus()
    #             kwargs = dict([widget.tree.item(ifocus, 'values')])
    #             boton.config(**kwargs)
    #             pass
    #         fframe = userinterface.formFrameGen(
    #             top,
    #             filename=os.path.join('./data/', 'WidgetParams.xml')
    #         )
    #         fframe.pack(side=tk.RIGHT, fill=tk.Y, expand=tk.YES)
    #         fframe.widget_attrs.bind('<<OL_Edit>>', configWidget)
    #         boton = ttk.Button(top, text='Boton de Prueba')
    #         boton.pack(side=tk.RIGHT, fill=tk.BOTH, expand=tk.YES)
    #
    #         params = boton.config()
    #         # Se eliminan los alias que pudieran existir de algunas claves
    #         keys = sorted(key for key in params if len(params[key]) == 5)
    #         # Se establece el tipo de widget
    #         getattr(fframe, 'widget_tag').setValue(str(type(boton)))
    #         # Se calculan los pares (attribute, value)
    #         values = '$'.join(['&'.join((x, str(boton.cget(x)))) for x in keys])
    #         # Se transfieren los atributos al fframe.
    #         getattr(fframe, 'widget_attrs').setValue(values, sep=('$', '&'))
    #         pass
    #
    #     elif caso == 'traverse':
    #         file_path = 'Data/kodi/BasicViewsShowCase.xml'
    #         pairs = traverseTree(top, file_path)
    #     elif caso == 'test_newPaneFactory':
    #         file_path = 'Data/kodi/MultiCategoryExample.xml'
    #         file_path = 'Data/mixing/mxShowcase.xml'
    #         file_path = 'Data/tkinter/tkUiEditor.xml'
    #         xmlObj = userinterface.getLayout(file_path)
    #         settings = {}
    #         fframe = formFrame(master=top, settings=settings, selPane=xmlObj)
    #         equations_manager.set_initial_widget_states()
    #         fframe.pack(side=tk.TOP, fill=tk.BOTH, expand=tk.YES, anchor=tk.NE)
    #         pass
    #     elif caso == 'widgetFactory':
    #         file_path = 'Data/kodi/ApplicationLayout.xml'
    #         xmlObj = getLayout(file_path)
    #         settings = {}
    #         fframe = formFrame(master=top, settings=settings, selPane=xmlObj)
    #         dummy = fframe
    #         fframe.pack(side=tk.TOP, fill=tk.BOTH, expand=tk.YES, anchor=tk.NE)
    #     else:
    #         file_path = 'Data/kodi/ApplicationLayout.xml'
    #         xmlObj = getLayout(file_path)
    #         settings = {}
    #         fframe = formFrame(master=top, settings=settings, selPane=xmlObj)
    #
    #         def motion(event):
    #             widget, x, y = event.widget, event.x, event.y
    #             try:
    #                 if widget.name.isdigit():
    #                     print('{}, {}, {}'.format(widget.name, x, y))
    #                     dummy = 2
    #             except:
    #                 pass
    #         fframe.bind_all("<Enter>", motion)
    #         Example(fframe).pack(fill="both", expand=True)
    #     top.attributes('-zoomed', True)
    #     top.mainloop()

        """
li > a[href*="en-US"] > .inline-warning
:nth-of-type
:nth-of-type(3n)
        
        """