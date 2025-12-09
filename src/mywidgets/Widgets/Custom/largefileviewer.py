import bisect
import itertools
import tkinter as tk
import tkinter.font

import mywidgets.Tools.uiStyle.MarkupRe as MarkupRe


CHUNK_SIZE = 10 * 1024  # Number of lines per chunk


class TagManager:
    def __init__(self):
        self.tags = {}
    
    def add(self, tagName, index1, *args):
        ltags = self.tags.setdefault(tagName, [])
        if not args:
            args = (index1 + 1,)
        args = (index1, *args)
        for index1, index2 in zip(args[::2], args[1::2]):
            if not ltags:
                ltags.extend((index1, index2))
                continue
            ndx1 = bisect.bisect_left(ltags, index1)
            ndx2 = bisect.bisect_left(ltags, index2)
            if ndx1 < len(ltags) and ndx1 % 2 == 1:
                ndx1 -= 1
                index1 = ltags[ndx1]
            if ndx2 < len(ltags):
                if ndx2 % 2 == 1:
                    index2 = ltags[ndx2]
                    ndx2 += 1
                elif ltags[ndx2] == index2:
                    index2 = ltags[ndx2 + 1]
                    ndx2 += 2
            ltags[ndx1:ndx2] = [index1, index2]
    
    def remove(self, tagName, index1, index2=None):
        ltags = self.tags.get(tagName, [])
        if not ltags:
            return
        index2 = index2 or index1 + 1

        ndx1 = bisect.bisect_left(ltags, index1)
        ndx2 = bisect.bisect_left(ltags, index2)
        head = ltags[:ndx1]
        if len(head) % 2 == 1:
            head = head + [index1]
        tail = ltags[ndx2:]
        if len(tail) % 2 == 1:
            if tail[0] != index2:
                tail = [index2] + tail
            else:
                tail = tail[1:]
        self.tags[tagName] = head + tail
    
    def names(self, index=None):
        if index is None:
            return list(self.tags.keys())

        answ = [
            tag
            for tag, ltags in self.tags.items()
            if (
                    (ndx := bisect.bisect_left(ltags, index)) < len(ltags)
                and
                    (ndx % 2 == 1 and ltags[ndx] > index
                        or
                    ndx % 2 == 0 and ltags[ndx] == index)
            )
        ]
        return answ

    def ranges_between(self, tagName, index1, index2):
        ltags = self.tags.get(tagName, [])
        if not ltags:
            return []
        ndx1 = bisect.bisect_left(ltags, index1)
        ndx2 = bisect.bisect_left(ltags, index2)

        answ = ltags[ndx1:ndx2]
        prefix = []
        if len(ltags[:ndx1]) % 2 == 1:
            prefix = [index1]

        suffix = []
        if len(ltags[ndx2:]) % 2 == 1:
            if ltags[ndx2] >= index2:
                suffix = [index2]
        answ = prefix + answ + suffix
        return answ
    
    def ranges(self, tagName):
        return self.tags.get(tagName, [])
    
    def nextrange(self, tagName, index1, index2=None):
        index2 = index2 or self.tags[tagName][-1]
        ltags = self.ranges_between(tagName, index1, index2)
        if ltags:
            ndx = 0 if ltags[0] != index1 else 2
            try:
                return [ltags[ndx], ltags[ndx + 1]]
            except IndexError:
                pass
        return ''

    def prevrange(self, tagName, index1, index2=None):
        index2 = index2 or self.tags[tagName][0]
        if index1 > index2:
            index1, index2 = index2, index1
        ltags = self.ranges_between(tagName, index1, index2)
        # if set(ltags) != set(ltags).difference(self.tags[tagName]):
        if ltags and ltags != [index1, index2]:
            if ltags[-1] == index2:
                ltags = ltags[:-1]
                ndx = bisect.bisect_left(self.tags[tagName], index2)
                ltags.append(self.tags[tagName][ndx])
            try:
                return [ltags[-2], ltags[-1]]
            except IndexError:
                pass
        return ''
    
    def clear(self):
        self.tags.clear()


class Blocks:
    def __init__(self, content: str, display_info: tuple[int, int], *, chunk_kb: int=CHUNK_SIZE):
        self.file = content
        self.chunk_size = chunk_kb
        self._pointer = None
        self.span = (0, 0)
        self._blk_offset = (0, 0)
        self.chars_perline = None
        self.display_lines = None
        self.display_info = display_info

    def __len__(self):
        return len(self.file)
    
    def nblocks(self):
        # Number of blocks
        return (len(self) + self.chunk_size - 1) // self.chunk_size
    
    def block_content(self):
        return self.file[self.span[0]: self.span[1]]
    
    @property
    def display_info(self):
        return self.chars_perline, self.display_lines
    
    @display_info.setter
    def display_info(self, value: tuple[int, int]):
        chars_perline, display_lines = value
        bflag = chars_perline != self.chars_perline
        self.chars_perline, self.display_lines = chars_perline, display_lines
        if bflag:
            # Adjust the pointer to the new chars_perline
            beg_blk, end_blk = self.span
            self.adjust_span(beg_blk, end_blk)
            

    def adjust_span(self, beg_blk, end_blk):
        beg_blk = self.line_coords(beg_blk)[0]
        end_blk = self.line_coords(end_blk)[1]
        self.span = (beg_blk, end_blk)

    @property
    def pointer(self):
        return self.span[0]
    
    def load_block(self, chunk_num=None):
        if chunk_num is None:
            chunk_num = self.pointer
        chunk_num = max(min(chunk_num, len(self) - self.chunk_size), 0)
        self.adjust_span(chunk_num, chunk_num + self.chunk_size)
        linf, lsup = self.span
        self._blk_offset = (
            self.file[:self.pointer].count('\n') + 1, 
            self.pointer - (self.file.find('\n', 0, self.pointer) + 1)
        )
        chars = self.file[linf: lsup]
        return chars
    
    def lineoffset(self):
        return self._blk_offset
    
    def prior_nlines(self, pos, npfx=1):
        """
        Entrega en el vector "lstlns" los "npfx" anteriores comienzos de línea que preceden a "pos".
        Donde "lstlns[-1]" corresponde al inicio de la línea que contiene a "pos".
        """
        if not self.chars_perline:
            return [pos]
        nempty = npfx
        lstlns = []
        while nempty:
            ndx = itertools.cycle(range(nempty))
            pfx_lines = npfx * [-1]
            lstln = self.file.rfind('\n', 0, pos) + 1
            pfx_lines[next(ndx)] = lstln
            while lstln + self.chars_perline < pos:
                lstln += self.chars_perline
                lstln += self.file[lstln] == ' '
                pfx_lines[next(ndx)] = lstln
            nempty = pfx_lines.count(-1)
            lstlns = [*pfx_lines[:len(pfx_lines) - nempty], *lstlns]
            pos = max(pfx_lines[0] - 1, 0)
            if not nempty or pos == 0:
                break
        lstlns = sorted(lstlns)
        return lstlns
    
    def next_nlines(self, pos, nsfx=1):
        """
        Entrega en el vector "nxtlns" los "nsfx" siguientes fin línea luego de "pos", donde nxtlns[0] 
        corresponde al fin de la línea que inicia en pos.
        """
        if not self.chars_perline:
            return [pos]
        nempty = nsfx
        nxtlns = []
        while nempty:
            nxtln1 = pos + self.chars_perline
            nxtln1 += ((nxtln1 < len(self)) and (self.file[nxtln1] == ' '))
            nxtln1 = min(nxtln1, len(self))
            nxtln = self.file.find('\n', pos, nxtln1)
            nxtln = nxtln1 * (nxtln == -1) or (nxtln + 1)
            nxtlns.append(nxtln)
            if nxtln == len(self):
                break
            # nxtln += 1
            # pos = nxtln + (self.file[nxtln] == '\n')
            pos = nxtln
            nempty -= 1
        return nxtlns
    
    def line_coords(self, pos):
        lstlns = self.prior_nlines(pos, 1)
        nxtlns = self.next_nlines(lstlns[-1], 1)
        return lstlns[0], nxtlns[0]
    
    def next_page(self, pos, npage_lines=None):
        npage_lines = npage_lines or self.display_lines
        lstlns = self.prior_nlines(pos, npfx=1)
        return self.next_nlines(lstlns[-1], nsfx=npage_lines)
    
    def prior_page(self, pos, npage_lines=None):
        npage_lines = npage_lines or self.display_lines
        return self.prior_nlines(pos, npfx=npage_lines)


class TclMonitor:
    cmdlookup = (
        ('tag', 'names'), ('tag', 'add'), 
        ('tag', 'ranges'), ('tag', 'nextrange'), ('tag', 'prevrange'),
        ('tag', 'delete'), ('tag', 'remove'),
        # ('mark', 'next'), ('mark', 'previous'), ('mark', 'set'), ('mark', 'unset'),
        # ('see',),
        ('index',),
    )

    def __init__(self, lfinst: 'LargeFileViewer'):
        self.lfinst = lfinst
        self.tkinst = lfinst.master.tk
        self.call = self.call_decorator(self.tkinst.call)
        pass

    def call_decorator(self, fnc):
        def wrapper(*args, **kwargs):
            if isinstance(args[0], (tuple, list)):
                args = args[0]
            wdgname, cmd, *params = args
            if (cmd, params[0]) in self.cmdlookup or (cmd,) in self.cmdlookup:
                method = getattr(self, cmd)
                assert method is not None
                args = method(wdgname, *params)
            if args is not None:
                try:
                    answ = fnc(*args, **kwargs)
                except Exception as e:
                    print(str(e))
                else:
                    return answ
        return wrapper
    
    def tag(self, wdgname, scmd, *params):
        print(f'Tag command: {scmd} with params {params}')
        wdg = self.lfinst.nametowidget(wdgname)
        if scmd == 'names':
            tagname, ndxes = '', params
        else:      # 'add' | 'delete' | 'nextrange' | 'prevrange'
            tagname, *ndxes = params
        if wdg.content.nblocks() > 1:
            abs_indexes = [ndx if isinstance(ndx, int) else wdg.wdg2abs(ndx) for ndx in ndxes]
            ndxes = wdg.tag(scmd, tagname, *abs_indexes)
        params = [wdg.abs2wdg(ndx) if isinstance(ndx, int) else ndx for ndx in ndxes if ndx]
        params = [tagname, *params] if tagname else params
        answ = [wdgname, 'tag', scmd, *params]
        return answ
    
    def mark(self, wdgname, scmd, *params):
        print(f'Mark command: {scmd} with params {params}')
        return ((wdgname, 'mark', scmd, *params),)
    
    def see(self, wdgname, index, *params):
        print(f'See command: {index}')
        return ((wdgname, 'see', index),)
    
    def __getattr__(self, name):
        return getattr(self.tkinst, name)


class LargeFileViewer(tk.Text):
    chunkt = itertools.cycle('*#')

    def __init__(self, master, show_lineno=False, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        # Activar la siguiente línea si se quiere monitorear los comando tcl pedidos a través
        # de self.tk.call
        self.fnt = fnt = tkinter.font.Font(family='Consolas', size=14)
        self.configure(font=fnt)
        # self._tk = TclMonitor(self)
        self.prefix = lambda k, s='*': f'{(k):04d}{s} ' if show_lineno else ''
        self.n_chunkt = 0
        # self.content = None
        # self.tags = {}
        # self.event_add(
        #     '<<ScrollMonitor>>', '<Next>', '<Prior>', '<Home>', '<End>', '<Up>', '<Down>', 
        #     '<MouseWheel>', '<Button-4>', '<Button-5>'
        # )
        # self.bind('<<ScrollMonitor>>', self.scroll_monitor)
        # self.bind('<Configure>', self.on_redraw)
        tkwargs = dict(lmargin1=30, lmargin2=60) if show_lineno else {}
        self.tag_configure("indented", lmargincolor="grey", **tkwargs)
        self.tag_configure("lineno", background='grey', foreground='white')
        pass

    def __getattribute__(self, name):
        if name == 'tk':
            return self.__dict__.get('_tk', self.__dict__['tk'])
        return super().__getattribute__(name)
    
    def on_redraw(self, event):
        if self.content:
            wdg = event.widget
            fnt = tkinter.font.Font(font=wdg['font'])
            chars_perline = max(event.width // fnt.measure('0', displayof=wdg) - len(self.prefix(1)), 0)
            display_lines = event.height // fnt.metrics('linespace', displayof=wdg)
            self.content.display_info = (chars_perline, display_lines)
            print('Redraw event')

    def abs2ndx(self, index: int) -> str:
        chars = self.content.file
        ndx_line = chars[:index].count('\n') + 1
        lstln = chars[:index].rfind('\n') + 1
        ndx_col = index - lstln
        return f'{ndx_line}.{ndx_col}'
    
    def ndx2abs(self, index: str) -> int:
        line, col = map(int, index.split('.'))
        chars = self.content.file
        abs_index = 0
        dmy = line - 1
        ndx = 0
        while dmy:
            ndx = chars.find('\n', ndx) + 1
            dmy -= 1
        abs_index += ndx + col
        return max(0, min(abs_index, len(self.content)))
    
    def ndx2wdg(self, index: str) -> str:
        abs_index = self.ndx2abs(index)
        linf_abs, lsup_abs = self.content.span
        abs_index = max(linf_abs, min(lsup_abs, abs_index))
        ndx = self.abs2ndx(abs_index) 
        ndx_line, ndx_col = map(int, ndx.split('.'))
        loffset, coffset = self.content.lineoffset()
        wdg_line = ndx_line - loffset + 1
        wdg_col = ndx_col + len(self.prefix(1))
        if wdg_line == 1:
            wdg_col -= coffset
        return f'{wdg_line}.{wdg_col}'
    
    def wdg2ndx(self, index: str) -> str:
        wdg_line, wdg_col = map(int, index.split('.'))
        loffset, coffset = self.content.lineoffset()
        ndx_line = wdg_line + loffset - 1
        ndx_col = max(0, wdg_col - len(self.prefix(1)))
        if wdg_line == 1:
            ndx_col += coffset
        return f'{ndx_line}.{ndx_col}'
    
    def wdg2abs(self, index: str) -> int:
        ndx_index = self.wdg2ndx(index)
        abs_index = self.ndx2abs(ndx_index)
        return abs_index
    
    def abs2wdg(self, index: int) -> str:
        ndx_index = self.abs2ndx(index)
        wdg_index = self.ndx2wdg(ndx_index)
        return wdg_index
    
    def wdg2abs_old(self, index, fromcall=True):
        line, col = self.splt_ndx(index, 0), self.splt_ndx(index, 1)
        loffset, coffset = self.content.lineoffset()
        if not fromcall:
            line = line - loffset + 1
            col -= coffset
        lprefix = len(self.prefix(1)) if fromcall else 0
        col = max(0, col - lprefix) # Adjust for prefix
        chars = self.content.block_content()
        abs_index = self.content.pointer
        dmy = line - 1
        ndx = 0
        while dmy:
            ndx = chars.find('\n', ndx) + 1
            dmy -= 1
        abs_index += ndx + col
        return abs_index

    def abs2wdg_old(self, index, tocall=False):
        pinf, psup = self.content.span
        if not (pinf <= index < psup):
            return tk.END if index >= psup else '1.0'

        rel_index = index - pinf
        chars = self.content.block_content()
        widget_line = chars[:rel_index].count('\n') + 1
        lstln = chars[:rel_index].rfind('\n') + 1
        widget_col = rel_index - lstln + len(self.prefix(1))
        if not tocall:
            loffset, coffset = self.content.lineoffset()
            widget_line = widget_line + loffset - 1
            widget_col = coffset + widget_col - len(self.prefix(1))
        return f'{widget_line}.{widget_col}'
    
    # def see(self, index):
    #     wdg_index = self.wdg2content(index)
    #     if wdg_index:
    #         super().see(wdg_index)

    def abs_index(self, *indexes):
        answ = [index if isinstance(index, int) else self.wdg2abs(index) for index in indexes]
        return answ

    def tag(self, scmd, *params):
        match scmd:
            case 'add':
                tagName, index1, *args = params
                if not args:
                    args = (index1 + 1,)
                args = (index1, *args)
                # Guarda la etiqueta en el diccionario interno
                if tagName not in self.tags:
                    self.tags[tagName] = []

                linf, lsup = self.content.span
                visibles = []
                for index1, index2 in zip(args[::2], args[1::2]):
                    self.tags[tagName].append((index1, index2))
                    tpl1, tpl2 = tuple(max(linf, min(lsup, ndx)) for ndx in (index1, index2))
                    if tpl1 != tpl2:
                        visibles.extend((tpl1, tpl2))
                return visibles or None


    # def tag_remove(self, tagName, index1, index2):
    #     # Elimina la etiqueta del diccionario interno
    #     if tagName in self.tags:
    #         abs_index1 = self.wdg2content(index1)
    #         abs_index2 = self.wdg2content(index2)
    #         self.tags[tagName] = [(start, end) for start, end in self.tags[tagName] if start != abs_index1 or end != abs_index2]
    #     # Elimina la etiqueta del texto visible
    #     super().tag_remove(tagName, index1, index2)

    def load_content(self, content, chunk_kb=CHUNK_SIZE):
        winfo_width = self.winfo_width()
        winfo_height = self.winfo_height()
        font = tkinter.font.Font(font=self['font'])
        chars_perline = max(winfo_width // font.measure('0', displayof=self) - len(self.prefix(1)), 0)
        display_lines = winfo_height // font.metrics('linespace', displayof=self)
        self.content = Blocks(content, (chars_perline, display_lines), chunk_kb=chunk_kb)
        self._tk = TclMonitor(self)
        if len(content) > chunk_kb:
            self.event_add(
                '<<ScrollMonitor>>', '<Next>', '<Prior>', '<Home>', '<End>', '<Up>', '<Down>', 
                '<MouseWheel>', '<Button-4>', '<Button-5>'
            )
            self.bind('<<ScrollMonitor>>', self.scroll_monitor)
            # self.content = None
            self.tags = {}
            self.bind('<Configure>', self.on_redraw)

        self.load_chunk(0)

    def load_chunk(self, chunk_num=None):
        span = self.content.span
        chunk_num = chunk_num if chunk_num is not None else span[0]
        chars = self.content.load_block(chunk_num)
        if self.content.span != span:
            loffset, _ = self.content.lineoffset()
            s = next(self.chunkt)
            self.delete('1.0', tk.END)
            tags = ('lineno', 'indented')
            for k, line in enumerate(chars.splitlines(keepends=True)):
                str_k = (self.prefix(k + loffset, s), line)
                list(map(lambda x, y:self.insert(tk.END, x, y), str_k, tags))

            # for k, x in enumerate(chars.splitlines(keepends=True)):
            #     pfix = self.prefix(k + loffset, s)
            #     if pfix:
            #         self.insert(tk.END, pfix, 'lineno')
            #     self.insert(tk.END, x, 'indented')

            # Recalcula y aplica las etiquetas para el nuevo chunk
            try:
                for tagName, ranges in self.tags.items():
                    allndx = [
                        tpl 
                        for pair in ranges 
                        if (tpl := list(map(lambda x: self.abs2wdg(x), pair))) and tpl[0] != tpl[1]
                    ]
                    if allndx:
                        ndxes = sum(allndx, [])
                        self._tk.tkinst.call(self, 'tag', 'add', tagName, *ndxes)
            except Exception as e:
                print(str(e))
        return self.content.span

    def nchars(self, index1, index2=None):
        index2 = index2 or tk.END
        ltop, lbottom = map(lambda x: self.splt_ndx(x, 0), (index1, index2))
        ctop, cbottom = map(lambda x: self.splt_ndx(x, 1), (index1, index2))
        # nlines = abs(lbottom - ltop)
        # lprefix = len(self.prefix(1))
        full_lines = sum(self.splt_ndx(f'{x}.end', 1) for x in range(ltop, lbottom - 1)) #- - lprefix * nlines
        return full_lines - ctop + cbottom
        
    def splt_ndx(self, index, pos):
        ndx = str(self._tk.tkinst.call(self, 'index', index))
        return int(ndx.split('.')[pos])  # - pos * len(self.prefix(1))

    def scroll_monitor(self, event):
        wdg = event.widget
        keysym = event.keysym


        # Se determina la altura de una línea de texto
        cwidth = self.fnt.measure('0', displayof=wdg)
        lheight = self.fnt.metrics('linespace', displayof=wdg)

        # _, _, _, lheight, _ = self.dlineinfo(f'@0,{wdg.winfo_height()}')
        # lheight += hbase

        # El marco de líneas visibles
        ntop, nbottom = map(self.index, (f'@{(len(self.prefix(1)) + 1) * cwidth},{lheight//2}', f'@{wdg.winfo_width()},{wdg.winfo_height() - lheight}'))
        ltop, lbottom = map(lambda x: self.splt_ndx(x, 0), (ntop, nbottom))
        ctop, cbottom = map(lambda x: self.wdg2abs(x), (ntop, nbottom))
        # ctop, cbottom = map(lambda x: self.nchars('1.0', x), (ntop, nbottom))
        wnd_char1, wnd_char2 = map(self.content.line_coords, (ctop, cbottom))
        wnd_chars = wnd_char2[1] - wnd_char1[0]

        # Posición del cursor
        inslin, inscol = map(lambda x: self.splt_ndx(tk.INSERT, x), (0, 1))
        dinslin = inslin - ltop
        if not dinslin:
            inscol = inscol - self.splt_ndx(ntop, 1)

        # Que caractacteres se estan desplegando en el widget.
        cinf, csup = self.content.span

        nlns = 20
        if event.type.name == 'MouseWheel':
            tcase = - abs(event.delta) // event.delta
            nlns = abs(event.delta)
            keysym = 'Down' if tcase > 0 else 'Up'
        elif keysym in ('Next', 'Prior'):
            nlns = None

        match keysym:
            case 'Next' | 'Down':
                clns = self.content.next_page(cbottom, npage_lines=nlns)
                if clns[-1] <= csup:
                    return
                if keysym == 'Down':
                    _, beg_blk = self.content.line_coords(ctop)
                else:
                    beg_blk, _ = self.content.line_coords(cbottom)
                self.load_chunk(beg_blk)
                offset = self.content.lineoffset()
                inspos = f'{dinslin + 1}.{inscol}'
                self.mark_set(tk.INSERT, inspos)
                return 'break'
            case 'Prior' | 'Up':
                clns = self.content.prior_page(ctop, npage_lines=nlns)
                if clns[0] >= cinf:
                    return
                if keysym == 'Up':
                    end_blk, _ = self.content.line_coords(cbottom)
                else:
                    _, end_blk = self.content.line_coords(ctop)
                self.load_chunk(end_blk - self.content.chunk_size)
                inspos = f'@0,0 + {dinslin} lines + {inscol} chars'
                self.mark_set(tk.INSERT, inspos)
                return 'break'
            case 'Home' | 'End':
                tcase = 0
                if (event.state & 0x00004): # Control key pressed
                    bflag = keysym == 'End'
                    chnk_pos = [0, len(self.content)][bflag]
                    self.load_chunk(chnk_pos)
                    ndx = [f'1.0 + {len(self.prefix(1))} chars', tk.END][bflag]
                    self.see(ndx)
                    return 'break'
            case _:
                tcase = 0
                print(f'Unknown event: {event.keysym}: {event}')
                pass


def main():
    top = tk.Tk()
    top.state('zoomed')
    viewer = LargeFileViewer(top, show_lineno=True)
    dev_setup(viewer)
    viewer.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    top.mainloop()


def dev_setup(viewer: LargeFileViewer):
    viewer.customFont = tkinter.font.Font(family='Consolas', size=14)
    viewer.configure(font=viewer.customFont)

    fname = r'C:\Users\agmontesb\Documents\GitHub\mywidgets\src\mywidgets\Widgets\Custom\regexframe.py'
    fname = r"C:\Users\agmontesb\Downloads\sheet18.xml"
    with open(fname, 'r') as f:
        content = f.read()
    content = 13 * '0123456789' + '  0123456789' + '\n' + content
    viewer.load_content(content, chunk_kb=len(content))
    # Test para verificar el etiquetado

    bflag = True
    if bflag:
        textw: LargeFileViewer = viewer
        textw.tag_configure('evenMatch', background='yellow')
        textw.tag_configure('oddMatch', background='red')
        tagColor = ['evenMatch', 'oddMatch']

        p1 = (10, 15)
        p2 = (51 + 20, 51 + 28)
        pwdg = lambda x, y: (textw.abs2wdg(x), textw.abs2wdg(y))
        p1wdg = pwdg(*p1)
        p2wdg = pwdg(*p2)

        textw.tag_add(tagColor[0], *p1)
        textw.tag_add(tagColor[1], *p2)
        print(textw.tag_names())
        print(textw.tag_names(p1[0]))
        print(textw.tag_names(p2[0]))

        print(textw.tag_ranges('oddMatch'))
        print(textw.tag_nextrange('oddMatch', 1))
        print(textw.tag_prevrange('oddMatch', tk.END))
        # regex_pat = '(?#<c r=adr <v *="\d{4,}"=val>*>)'
        # cpat = MarkupRe.compile(regex_pat)

        # for k, m in enumerate(cpat.finditer(content)):
        #     tstart, tend = m.span()
        #     if tstart != tend:
        #         textw.tag_add(tagColor[k % 2], m.start(), m.end())
        #         print(f'tag = {tagColor[k % 2]}, start = {m.start()}, end = {m.end()}, {m.group()}')


def devTagManager():
    tm = TagManager()
    tag = 'mitag'
    assert tm.ranges(tag) == []

    tm.add(tag, 3, 12)
    assert tm.ranges(tag) == [3, 12]

    tm.add(tag, 25, 55)
    assert tm.ranges(tag) == [3, 12, 25, 55]

    tm.add(tag, 18, 20)
    assert tm.ranges(tag) == [3, 12, 18, 20, 25, 55]

    tm.add(tag, 15, 19)
    assert tm.ranges(tag) == [3, 12, 15, 20, 25, 55]

    tm.add(tag, 18, 30)
    assert tm.ranges(tag) == [3, 12, 15, 55]

    tm.add(tag, 1, 2)
    assert tm.ranges(tag) == [1, 2, 3, 12, 15, 55]

    tm.add(tag, 2, 3)
    assert tm.ranges(tag) == [1, 12, 15, 55]

    tm.add(tag, 1, 12)
    assert tm.ranges(tag) == [1, 12, 15, 55]

    tm.add(tag, 1, 55)
    assert tm.ranges(tag) == [1, 55]

    tm.tags[tag] = [3, 12, 18, 20, 25, 55]
    tm.remove(tag, 15, 17)
    assert tm.ranges(tag) == [3, 12, 18, 20, 25, 55]

    tm.tags[tag] = [3, 12, 18, 20, 25, 55]
    tm.remove(tag, 5, 10)
    assert tm.ranges(tag) == [3, 5, 10, 12, 18, 20, 25, 55]

    tm.tags[tag] = [3, 12, 18, 20, 25, 55]
    tm.remove(tag, 12, 19)
    assert tm.ranges(tag) == [3, 12, 19, 20, 25, 55]

    tm.tags[tag] = [3, 12, 18, 20, 25, 55]
    tm.remove(tag, 22, 30)
    assert tm.ranges(tag) == [3, 12, 18, 20, 30, 55]

    tm.tags[tag] = ltags = [3, 12, 18, 20, 25, 55]
    assert all(tm.names(k) == [tag] for ndx1, ndx2 in zip(ltags[::2], ltags[1::2]) for k in range(ndx1, ndx2))

    ltags = ltags[1:] + [100]
    assert all(tm.names(k) == [] for ndx1, ndx2 in zip(ltags[::2], ltags[1::2]) for k in range(ndx1, ndx2))

    tm.tags[tag] = ltags = [3, 12, 18, 20, 25, 55]
    assert tm.ranges_between(tag, 15, 19) == [18, 19]
    assert tm.ranges_between(tag,  3, 12) == [ 3, 12]
    assert tm.ranges_between(tag, 10, 16) == [10, 12]
    assert tm.ranges_between(tag, 10, 18) == [10, 12]
    assert tm.ranges_between(tag, 30, 40) == [30, 40]
    assert tm.ranges_between(tag, 10, 40) == [10, 12, 18, 20, 25, 40]
    assert tm.ranges_between(tag, 15, 19) == [18, 19]
    assert tm.ranges_between(tag, 15, 30) == [18, 20, 25, 30]

    tm.tags[tag] = ltags = [3, 12, 18, 20, 25, 55]
    assert tm.nextrange(tag, 1) == [3, 12]
    assert tm.nextrange(tag, 10) == [18, 20]
    assert tm.nextrange(tag, 30, 40) == ''
    assert tm.nextrange(tag, 5) == [18, 20]
    assert tm.nextrange(tag, 22) == [25, 55]

    tm.tags[tag] = ltags = [3, 12, 18, 20, 25, 55]
    assert tm.prevrange(tag, 5) == [3, 12]
    assert tm.prevrange(tag, 5, 10) == ''
    assert tm.prevrange(tag, 5, 1) == [3, 12]
    assert tm.prevrange(tag, 19) == [18, 20]
    assert tm.prevrange(tag, 30) == [25, 55]
    assert tm.prevrange(tag, 21) == [18, 20]
    assert tm.prevrange(tag, 15) == [3, 12]


    pass




if __name__ == '__main__':
    # main()
    devTagManager()