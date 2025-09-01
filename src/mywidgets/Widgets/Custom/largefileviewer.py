import tkinter as tk
import tkinter.font

import mywidgets.Tools.uiStyle.MarkupRe as MarkupRe


CHUNK_SIZE = 10 * 1024  # Number of lines per chunk


class Chunks:
    def __init__(self, content, chars_perline, *, chunk_kb=CHUNK_SIZE):
        self.file = content
        self.chunk_size = chunk_kb
        self._pointer = None
        self.span = (0, 0)
        self.chars_perline = None
        self.display_lines = None

    def __len__(self):
        return len(self.file)
    
    @property
    def display_info(self):
        return self.chars_perline, self.display_lines
    
    @display_info.setter
    def display_info(self, value: tuple[int, int]):
        chars_perline, display_lines = value
        if chars_perline != self.chars_perline:
            # Adjust the pointer to the new chars_perline
            beg_blk, end_blk = self.span
            beg_blk -= self.file[:beg_blk].count('\r')
            end_blk -= self.file[:end_blk].count('\r')

            self.file = self.file.replace('\r', '')
            linf = 0
            while lsup := self.file.find('\n', linf):
                while lsup - linf > chars_perline:
                    self.file = self.file[:linf + chars_perline] + '\r' + self.file[linf + chars_perline:]
                    lsup += 1
                    linf += chars_perline + 1
                linf = lsup + 1

            beg_blk += self.file[:beg_blk].count('\r')

            end_blk += self.file[:end_blk].count('\r')
            self.adjust_span()
            
        self.chars_perline, self.display_lines = chars_perline, display_lines

    def adjust_span(self):
        beg_blk, end_blk = self.span

        if beg_blk > 0 and self.file[beg_blk - 1] not in ('\n', '\r'):
            beg_blk = max(self.file.rfind('\n', 0, beg_blk), self.file.rfind('\r', 0, beg_blk)) + 1

        if end_blk < len(self.file) and self.file[end_blk + 1] not in ('\n', '\r'):
            v1 = self.file.find('\n', end_blk)
            v2 = self.file.find('\r', end_blk)
            end_blk = min(v1 if v1 != -1 else len(self.file), v2 if v2 != -1 else len(self.file))

        self.span = (beg_blk, end_blk)

    @property
    def pointer(self):
        return self.span[0]
    
    def load_chunk(self, chunk_num=None):
        if chunk_num is not None:
            self.pointer = chunk_num
        linf, lsup = self.span
        return self.file[linf: lsup]
    
    def next(self):
        self.pointer += self.chunk_size
        return self.load_chunk()
    
    def prior(self):
        self.pointer -= self.chunk_size
        return self.load_chunk()
    
    def lineoffset(self):
        nlines = self.file[:self.pointer].count('\n') or 1
        return nlines


class TclMonitor:
    cmdlookup = (
        ('tag', 'add'), ('tag', 'delete'), ('tag', 'names'), ('tag', 'nextrange'), ('tag', 'prevrange'),
        ('mark', 'next'), ('mark', 'previous'), ('mark', 'set'), ('mark', 'unset'),
        ('see',),
    )

    def __init__(self, lfinst: 'LargeFileViewer'):
        self.lfinst = lfinst
        self.tkinst = lfinst.master.tk
        self.call = self.call_decorator(self.tkinst.call)
        pass

    def call_decorator(self, fnc):
        def wrapper(*args, **kwargs):
            wdgname, cmd, *params = args[0]
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
        wdg = self.lfinst
        if scmd == 'names':
            tagname, *ndxes = '', params
        else:
            tagname, *ndxes = params
        abs_indexes = [ndx if isinstance(ndx, int) else wdg.wdg2content(ndx) for ndx in ndxes]
        ndxes = wdg.tag(scmd, *abs_indexes)
        params = [ndx if isinstance(ndx, int) else wdg.content2wdg(ndx) for ndx in ndxes]
        params = [tagname, *params] if tagname else None
        return params
    
    def mark(self, wdgname, scmd, *params):
        print(f'Mark command: {scmd} with params {params}')
        return ((wdgname, 'mark', scmd, *params),)
    
    def see(self, wdgname, index, *params):
        print(f'See command: {index}')
        return ((wdgname, 'see', index),)
    
    def __getattr__(self, name):
        return getattr(self.tkinst, name)


class LargeFileViewer(tk.Text):
    chunkt = '*#'

    def __init__(self, master, show_lineno=False, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        # Activar la siguiente línea si se quiere monitorear los comando tcl pedidos a través
        # de self.tk.call
        self.fnt = fnt = tkinter.font.Font(family='Consolas', size=14)
        self.configure(font=fnt)
        self._tk = TclMonitor(self)
        self.prefix = lambda k, s='*': f'{(k):04d}{s} ' if show_lineno else ''
        self.n_chunkt = 0
        self.content = None
        self.tags = {}
        self.event_add(
            '<<ScrollMonitor>>', '<Next>', '<Prior>', '<Home>', '<End>', '<Up>', '<Down>', 
            '<MouseWheel>', '<Button-4>', '<Button-5>'
        )
        self.bind('<<ScrollMonitor>>', self.scroll_monitor)
        self.bind('<Configure>', self.on_redraw)
        tkwargs = dict(lmargin1=30, lmargin2=60) if show_lineno else {}
        self.tag_configure("indented", lmargincolor="grey", **tkwargs)
        self.tag_configure("lineno", background='grey', foreground='white')
        self.dev_setup()
        pass

    def __getattribute__(self, name):
        if name == 'tk':
            return self.__dict__.get('_tk', self.__dict__['tk'])
        return super().__getattribute__(name)
    
    def on_redraw(self, event):
        wdg = event.widget
        fnt = tkinter.font.Font(font=wdg['font'])
        height = fnt.metrics('linespace')
        chars_perline = event.width // fnt.measure('0', displayof=wdg)
        display_lines = event.height // fnt.metrics('linespace', displayof=wdg)
        self.content.display_info = (chars_perline, display_lines)
        self.content.load_chunk()
        print('Redraw event')
    
    def dev_setup(viewer):
            viewer.customFont = tkinter.font.Font(family='Consolas', size=14)
            viewer.configure(font=viewer.customFont)

            fname = r'C:\Users\agmontesb\Documents\GitHub\mywidgets\src\mywidgets\Widgets\Custom\regexframe.py'
            fname = r"C:\Users\agmontesb\Downloads\sheet18.xml"
            with open(fname, 'r') as f:
                content = 5 * '0123456789' + '\n' + f.read()
            viewer.load_content(content)
            # Test para verificar el etiquetado

            textw = viewer
            textw.tag_configure('evenMatch', background='yellow')
            textw.tag_configure('oddMatch', background='red')
            tagColor = ['evenMatch', 'oddMatch']


            regex_pat = '(?#<c r=adr <v *="\d{4,}"=val>*>)'
            cpat = MarkupRe.compile(regex_pat)

            for k, m in enumerate(cpat.finditer(content)):
                tstart, tend = m.span()
                if tstart != tend:
                    textw.tag_add(tagColor[k % 2], m.start(), m.end())


    def wdg2content(self, index):
        line, col = self.splt_ndx(index, 0), self.splt_ndx(index, 1)
        lprefix = len(self.prefix(1))
        col -= lprefix # Adjust for prefix
        chunk_lines = self.get('1.0', 'end').splitlines()
        abs_index = self.content.pointer
        for i in range(line - 1):
            abs_index += len(chunk_lines[i]) - (lprefix - 1) # 6 for prefix, -1 for newline
        abs_index += col
        return abs_index

    def content2wdg(self, index):
        pinf, psup = self.content.span
        if not (pinf <= index < psup):
            return tk.END if index >= psup else '1.0'

        chunk_content = self.content.load_chunk()
        rel_index = index - pinf
        
        lines = chunk_content.split('\n')
        char_count = 0
        line_num = 0
        for i, line in enumerate(lines):
            if char_count + len(line) + 1 > rel_index:
                line_num = i
                break
            char_count += len(line) + 1

        col_num = rel_index - char_count
        
        widget_line = line_num + 1
        widget_col = col_num + len(self.prefix(1))
        return f'{widget_line}.{widget_col}'
    
    # def see(self, index):
    #     wdg_index = self.wdg2content(index)
    #     if wdg_index:
    #         super().see(wdg_index)

    def abs_index(self, *indexes):
        answ = [index if isinstance(index, int) else self.wdg2content(index) for index in indexes]
        return answ


    # def tag_add(self, tagName, index1, index2, *args):
    #     # Guarda la etiqueta en el diccionario interno
    #     if tagName not in self.tags:
    #         self.tags[tagName] = []
    #     match index1:
    #         case int():
    #             abs_index1, abs_index2 = index1, index2
    #             index1 = self.content2wdg(index1)
    #             index2 = self.content2wdg(index2)
    #         case _:
    #             abs_index1 = self.wdg2content(index1)
    #             abs_index2 = self.wdg2content(index2)
    #     self.tags[tagName].append((abs_index1, abs_index2))
    #     # Aplica la etiqueta al texto visible
    #     lprefix = len(self.prefix(1))
    #     if index1 != index2:
    #         super().tag_add(tagName, f'{index1} + {lprefix} chars', f'{index2} + {lprefix} chars', *args)

    # def tag_remove(self, tagName, index1, index2):
    #     # Elimina la etiqueta del diccionario interno
    #     if tagName in self.tags:
    #         abs_index1 = self.wdg2content(index1)
    #         abs_index2 = self.wdg2content(index2)
    #         self.tags[tagName] = [(start, end) for start, end in self.tags[tagName] if start != abs_index1 or end != abs_index2]
    #     # Elimina la etiqueta del texto visible
    #     super().tag_remove(tagName, index1, index2)

    def load_content(self, content, chunk_kb=CHUNK_SIZE):
        font = tkinter.font.Font(font=self['font'])
        chars_perline = self.winfo_width() // font.measure('0')
        self.content = Chunks(content, chars_perline, chunk_kb=chunk_kb)
        self.load_chunk(0)

    def load_chunk(self, chunk_num):
        span = self.content.span
        chars = self.content.load_chunk(chunk_num)
        if self.content.span != span:
            self.delete('1.0', tk.END)
            offset = self.content.lineoffset()
            s = self.chunkt[self.n_chunkt]
            for k, x in enumerate(chars.splitlines(keepends=True)):
                pfix = self.prefix(k + offset, s)
                if pfix:
                    self.insert(tk.END, pfix, 'lineno')
                self.insert(tk.END, x, 'indented')
            self.n_chunkt = (self.n_chunkt + 1) % len(self.chunkt)

            # Recalcula y aplica las etiquetas para el nuevo chunk
            lprefix = len(self.prefix(1))
            for tagName, ranges in self.tags.items():
                for start, end in ranges:
                    wdg_start = self.content2wdg(start)
                    wdg_end = self.content2wdg(end)
                    if wdg_start and wdg_end:
                        super().tag_add(tagName, f'{wdg_start} + {lprefix} chars', f'{wdg_end} + {lprefix} chars')
        return self.content.span

    def nchars(self, index1, index2=None):
        index2 = index2 or tk.END
        ltop, lbottom = map(lambda x: self.splt_ndx(x, 0), (index1, index2))
        ctop, cbottom = map(lambda x: self.splt_ndx(x, 1), (index1, index2))
        nlines = abs(lbottom - ltop)
        lprefix = len(self.prefix(1))
        full_lines = sum(self.splt_ndx(f'{x}.end', 1) for x in range(ltop, lbottom - 1)) - lprefix * nlines # 5 is the length of the prefix
        return full_lines - ctop + cbottom
        
    def splt_ndx(self, index, pos):
        ndx = self.index(index)
        return int(ndx.split('.')[pos])

    def scroll_monitor(self, event):
        wdg = event.widget
        keysym = event.keysym


        # Se determina la altura de una línea de texto
        _, _, _, lheight, hbase = self.dlineinfo(f'@0,{wdg.winfo_height()}')
        lheight += hbase
        # El marco de líneas visibles
        ntop, nbottom = map(self.index, ('@0,0', f'@0,{wdg.winfo_height() - 2*lheight}'))
        ltop, lbottom = map(lambda x: self.splt_ndx(x, 0), (ntop, nbottom))
        ctop, cbottom = map(lambda x: self.nchars('1.0', x), (ntop, nbottom))
        wnd_chars = cbottom - ctop
        # Posición del cursor
        inslin, inscol = map(lambda x: self.splt_ndx(tk.INSERT, x), (0, 1))
        dinslin = inslin - ltop
        # Que caractacteres se estan desplegandoen el widget.
        pinf, psup = self.content.span

        match keysym:
            case '??':
                assert event.type.name == 'MouseWheel'
                tcase = - abs(event.delta) // event.delta
                nlines = abs(event.delta)
                ndx = self.index(f'@0,{self.winfo_height() - nlines}')
                wnd_chars = self.nchars('1.0', ndx) - ctop
            case 'Down' | 'Up':
                tcase = (1, -1)[keysym == 'Up']
                wnd_chars = (20 * wnd_chars) // 100
            case 'Next' | 'Prior':
                tcase = (1, -1)[keysym == 'Prior']
            case 'Home' | 'End':
                tcase = 0
                if (event.state & 0x00004): # Control key pressed
                    bflag = keysym == 'End'
                    chnk_pos = [0, len(self.content)][bflag]
                    self.load_chunk(chnk_pos)
            case _:
                tcase = 0
                print(f'Unknown event: {event.keysym}: {event}')
                pass

        chunk_size = self.content.chunk_size
        if tcase > 0 and cbottom + wnd_chars > chunk_size:
            # nchars = self.nchars(f'{ltop}.0', tk.END)
            # self.load_chunk(psup - nchars)
            self.load_chunk(pinf + ctop) 
        elif tcase < 0 and ctop - wnd_chars < 0:
            # nchars = self.nchars(f'{ltop}.0', f'{lbottom}.0')
            # self.load_chunk(pinf + nchars - (psup - pinf))
            self.load_chunk(pinf + cbottom - chunk_size)

        if self.content.span != (pinf, psup):
            inscol = max(inscol, len(self.prefix(1)))
            if tcase < 0:
                self.see(tk.END)
                inspos = f'@0,0 + {dinslin} lines + {inscol} chars'
            else:
                inspos = f'{dinslin + 1}.{inscol}'
            self.mark_set(tk.INSERT, inspos)

def main():
    top = tk.Tk()
    top.state('zoomed')
    viewer = LargeFileViewer(top)

    index1 = '1.5'
    index2 = '1.15'
    args = ('2.0', '2.10', '3.0', '3.10')
    tag_name = 'lineo'
    print(25*'#')

    '''
    #########################
tag_add(lineo, 1.5)
{.!largefileviewer tag add lineo 1.5}
tag_add(lineo, 1.5, 1.15)
{.!largefileviewer tag add lineo 1.5 1.15}     
tag_add(lineo, 1.5, 2.0, 2.10, 3.0, 3.10)      
{.!largefileviewer tag add lineo 2.0 2.10 3.0 3.10}

tag_delete(dmytag1)
{.!largefileviewer tag delete dmytag1}
tag_delete(dmytag1, dmytag2, dmytag3, dmytag4) 
{.!largefileviewer tag delete dmytag1 dmytag2 dmytag3 dmytag4}

tag_names()
.!largefileviewer tag names None
tag_names(1.5)
.!largefileviewer tag names 1.5

tag_nextrange(lineo, 1.5)
.!largefileviewer tag nextrange lineo 1.5 None 
tag_nextrange(lineo, 1.5, 1.15)
.!largefileviewer tag nextrange lineo 1.5 1.15 

tag_prevrange(lineo, 1.5)
.!largefileviewer tag prevrange lineo 1.5 None 
tag_prevrange(lineo, 1.5, 1.15)
.!largefileviewer tag prevrange lineo 1.5 1.15 

mark_names()
.!largefileviewer mark names

mark_next(lineo)
.!largefileviewer mark next lineo

mark_next(1.5)
.!largefileviewer mark next 1.5

mark_previous(lineo)
.!largefileviewer mark previous lineo

mark_previous(1.5)
.!largefileviewer mark previous 1.5

mark_set(lineo, 1.5)
.!largefileviewer mark set lineo 1.5

mark_unset(lineo)
{.!largefileviewer mark unset lineo}

see(1.5)
.!largefileviewer see 1.5
#########################

    '''

    print(f'tag_add({tag_name}, {index1})')
    viewer.tag_add(tag_name, index1)
    print(f'tag_add({tag_name}, {index1}, {index2})')
    viewer.tag_add(tag_name, index1, index2)
    print(f'tag_add({tag_name}, {index1}, {", ".join(args)})')
    viewer.tag_add(tag_name, *args)
    viewer.pack(fill=tk.BOTH, expand=True)

    print(f'tag_delete({"dmytag1"})')
    viewer.tag_delete('dmytag1')
    print(f'tag_delete({"dmytag1"}, {"dmytag2"}, {"dmytag3"}, {"dmytag4"})')
    viewer.tag_delete('dmytag1', 'dmytag2', 'dmytag3', 'dmytag4')

    print(f'tag_names()')
    viewer.tag_names()
    print(f'tag_names({index1})')
    viewer.tag_names(index1)
    
    print(f'tag_nextrange({tag_name}, {index1})')
    viewer.tag_nextrange(tag_name, index1)
    print(f'tag_nextrange({tag_name}, {index1}, {index2})')
    viewer.tag_nextrange(tag_name, index1, index2)

    print(f'tag_prevrange({tag_name}, {index1})')
    viewer.tag_prevrange(tag_name, index1)
    print(f'tag_prevrange({tag_name}, {index1}, {index2})')
    viewer.tag_prevrange(tag_name, index1, index2)

    print(f'mark_names()')
    viewer.mark_names()

    print(f'mark_next({tag_name})')
    viewer.mark_next(tag_name)
    print(f'mark_next({index1})')
    viewer.mark_next(index1)

    print(f'mark_previous({tag_name})')
    viewer.mark_previous(tag_name)
    print(f'mark_previous({index1})')
    viewer.mark_previous(index1)

    print(f'mark_set({tag_name}, {index1})')
    viewer.mark_set(tag_name, index1)

    print(f'mark_unset({tag_name})')
    viewer.mark_unset(tag_name)

    print(f'see({index1})')
    viewer.see(index1)
    print(25*'#')

    top.mainloop()



if __name__ == '__main__':
    main()