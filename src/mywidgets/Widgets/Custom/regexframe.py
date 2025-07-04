import time
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.simpledialog
import tkinter.messagebox as tkMessageBox
import tkinter.filedialog as tkFileDialog

import _thread
import tkinter.ttk
import tkinter.font
import urllib.request, urllib.parse, urllib.error

import urllib.parse
import re
import mywidgets.Tools.uiStyle.MarkupRe as MarkupRe
from mywidgets.Tools.uiStyle.uicss import Selector
from mywidgets.Widgets.Custom import network, CollapsingFrame
import queue
from mywidgets.Widgets.kodiwidgets import CustomDialog
import threading
from mywidgets.Widgets.Custom import ImageProcessor as imgp
from functools import reduce


class TreeList(ttk.Treeview):
    def __init__(self, *args, **kwargs):
        self._sortby = None
        ttk.Treeview.__init__(self, *args, **kwargs)

        self.event_add('<<CopyEvent>>', '<Control-C>', '<Control-c>')
        self.event_add('<<MoveTo>>', '<Home>', '<End>')
        self.event_add('<<ExpandSelUpOrDown>>', '<Shift-Down>', '<Shift-Up>',
                            '<Shift-Home>', '<Shift-End>')
        self.event_add('<<SelectAll>>', '<Control-A>', '<Control-a>')
        self.event_add('<<LeftClick>>', '<Button-1>', '<Control-Button-1>', '<Shift-Button-1>')

        self.bind('<<CopyEvent>>',          self.selCopy)
        self.bind('<<ExpandSelUpOrDown>>',  self.expandSelUpOrDown)
        self.bind('<<MoveTo>>',             self.MoveTo)
        self.bind('<<LeftClick>>',          self.onLeftClick)
        self.bind('<<SelectAll>>',          lambda event: self.selection_set(self.get_children()))

    @property
    def sortby(self):
        treew = self
        sortby = self._sortby
        if sortby:
            try:
                colName = treew.heading(sortby, option='text')
            except:
                self._sortby = sortby = None
            else:
                if not any(map(colName.endswith, ('(a-z)', '(z-a)'))):
                    self._sortby = sortby = None
        return sortby

        pass

    @sortby.setter
    def sortby(self, value):
        self._sortby = value

    def selCopy(self, event=None):
        treew = self
        answ = []
        for columnId in treew.cget('columns'):
            text = treew.heading(columnId, 'text')
            if not text: break
            answ.append(text)
        nCols = len(answ)
        answ = [','.join(answ)]

        itemsSEL = treew.selection()
        for itemid in itemsSEL:
            values = treew.item(itemid, 'values')
            answ.append(','.join(values[:nCols]))
        text = '\n'.join(answ)
        treew.clipboard_clear()
        treew.clipboard_append(text)

    def expandSelUpOrDown(self,event):
        treew = self
        cursel = treew.focus()
        if event.keysym in ['Up', 'Down']:
            itemsSel = treew.selection()
            if event.keysym == 'Down':
                nxtitem = treew.next(cursel)
            else:
                nxtitem = treew.prev(cursel)
            if not nxtitem: return
            # treew.selection_toggle(nxtitem)
            if nxtitem in itemsSel:
                treew.selection_remove(cursel)
            else:
                treew.selection_add(nxtitem)
            treew.focus(nxtitem)
        elif event.keysym in ['Home', 'End']:
            toInclude = treew.get_children()
            ndx = toInclude.index(cursel)
            if event.keysym == 'End':
                pIni, pFin = ndx, len(toInclude)
            else:
                pIni, pFin = 0, ndx + 1
            treew.selection_add(toInclude[pIni:pFin])
        return 'break'

    def MoveTo(self, event=None):
        treew = self
        toInclude = treew.get_children()
        if event.keysym == 'Home':
            nxtitem = toInclude[0]
        else:
            nxtitem = toInclude[-1]
        treew.see(nxtitem)
        treew.focus(nxtitem)
        treew.selection_set(nxtitem)
        return 'break'

    def onLeftClick(self, event=None):
        treew = event.widget
        x, y = event.x, event.y
        region = self.identify_region(x, y)
        control_key = (event.state & 0x0004)
        shift_key = (event.state & 0x0001)
        if region == 'cell':
            if not (control_key or shift_key): return
            itemsSel = treew.selection()
            cursel = treew.focus()
            row = treew.identify_row(y)
            if shift_key:
                nxtitem, posFIN = sorted((cursel, row))
                while 1:
                    treew.selection_add(nxtitem)
                    if nxtitem == posFIN: break
                    nxtitem = treew.next(nxtitem)
            if control_key:
                treew.selection_toggle(row)
            treew.focus(row)
            return 'break'
        elif region == 'heading':
            iid = self.focus()
            nCol = treew.identify_column(x)
            nCol = int(nCol[1:]) - 1
            displaycolumns = treew['displaycolumns']
            if displaycolumns == ('#all',):
                displaycolumns = treew['columns']
            treeCol = displaycolumns[nCol]

            if self.sortby is not None and self.sortby == treeCol:
                colName = treew.heading(self.sortby, option='text')
                revFlag = colName.endswith('(a-z)')
                colName = colName[:-5] + ('(z-a)' if revFlag else '(a-z)')
            else:
                if self.sortby:
                    colName = treew.heading(self.sortby, option='text')[:-6]
                    treew.heading(self.sortby, text=colName)
                revFlag = False
                colName =  treew.heading(treeCol, option='text') + ' (a-z)'
            treew.heading(treeCol, text=colName)
            self.sortby = treeCol
            rows = self.get_children()
            self.detach(*rows)
            rows = sorted(rows, key=lambda x: treew.set(x, treeCol), reverse=revFlag)
            for k, iid in enumerate(rows):
                treew.move(iid, '', k)
            # self.update()
            # iid = self.focus()
            self.see(iid)
            # print '**', iid, '**'


class RegexpBar(tk.Frame):
    RGXFLAGS = ['IGNORECASE', 'LOCALE', 'MULTILINE', 'DOTALL', 'UNICODE', 'VERBOSE']
    RGXFLAGSPAT = ['i', 'L', 'm', 's', 'u', 'x']
    CRGFLAGS = ['SPAN', 'PARAM']
    CRGFLAGSPAT = ['(?#<SPAN>)', '(?#<PARAM>)']
    FLAGS = RGXFLAGS + CRGFLAGS

    def __init__(self, master, messageVar):
        tk.Frame.__init__(self, master)
        self.dropDownFiler = None
        self.textWidget = None
        self.actMatchIndx = 0

        self.mutex = threading.Event()
        self.queue = queue.Queue(maxsize=0)
        self.activeCallBack = []
        self.threadFlag = 'stop'
        self.keyboard_delay = None

        self.messageVar = messageVar
        self.setGUI()

    def setTextWidget(self, tWidget):
        self.textWidget = tWidget

    def setTreeWidget(self, treeWdgt):
        self.tree = treeWdgt
        self.tree.bind('<<TreeviewSelect>>', self.onTreeSel)

    def onTreeSel(self, event):
        treew = event.widget
        if treew.selection():
            selId = treew.selection()[0]
            posINI = treew.set(selId, column='posINI')
            posFIN = treew.set(selId, column='posFIN')
            self.setActualMatch((posINI, posFIN))

    def setDropDownFiler(self, callbckFunc):
        self.dropDownFiler = callbckFunc

    def setGUI(self):
        self.customFont = tkinter.font.Font(family='Consolas', size=14)

        frame1 = tk.Frame(self)
        frame1.pack(fill=tk.X)

        iconImage = imgp.getFontAwesomeIcon
        commOptions = dict(size=24, isPhotoImage=True, color='green', aspectratio='stretch')

        self.frstIcon = frstIcon = iconImage('fa-angle-double-left', **commOptions)
        self.prvIcon = prvIcon = iconImage('fa-angle-left', **commOptions)
        self.anchorIcon = anchorIcon = iconImage('fa-anchor', **commOptions)
        self.lstIcon = lstIcon = iconImage('fa-angle-double-right', **commOptions)
        self.nxtIcon = nxtIcon = iconImage('fa-angle-right', **commOptions)

        self.anchor = tk.IntVar()
        self.anchorPos = []

        navFrame = tk.Frame(frame1)
        navFrame.pack(side=tk.RIGHT)
        self.leftWing = leftWing = tk.Frame(navFrame)
        leftWing.pack(side=tk.LEFT)
        self.rightWing = rightWing = tk.Frame(navFrame)
        rightWing.pack(side=tk.RIGHT)

        self.butLast = tk.Button(rightWing, image=lstIcon, font=self.customFont, text="L",
                                 command=lambda: self.extreme('>>'))
        self.butLast.pack(side=tk.RIGHT)
        self.butNext = tk.Button(rightWing, image=nxtIcon, font=self.customFont, text=">", command=self.nextMatch)
        self.butNext.pack(side=tk.RIGHT)
        self.matchLabel = tk.Label(navFrame, font=self.customFont, text="")
        self.matchLabel.pack(side=tk.LEFT)
        self.butPrev = tk.Button(leftWing, image=prvIcon, font=self.customFont, text="<", command=self.prevMatch)
        self.butPrev.pack(side=tk.RIGHT)
        self.butFirst = tk.Button(leftWing, image=frstIcon, font=self.customFont, text="F",
                                  command=lambda: self.extreme('<<'))
        self.butFirst.pack(side=tk.RIGHT)

        self.butAnchor = tk.Checkbutton(frame1, image=anchorIcon, variable=self.anchor, indicatoron=0,
                                        font=self.customFont, text="A", command=self.onAnchor)
        self.butAnchor.pack(side=tk.LEFT, fill=tk.Y)
        self.butKeyMaker = tk.Button(frame1, text="ZoomIn", command=self.zoomInOut)
        self.butKeyMaker.pack(side=tk.LEFT, padx=4, fill=tk.Y)
        self.cbIndex = tk.StringVar()
        lbl = tk.Label(frame1, textvariable=self.cbIndex)
        lbl.pack(side=tk.LEFT)

        self.regex_type = tk.StringVar()
        for elem in ['selector', 'markupre']:
            chkbutt = tk.Checkbutton(
                frame1, text=elem[0].upper(), variable=self.regex_type,
                indicatoron=False, font=self.customFont, onvalue=elem
            )
            chkbutt.pack(side=tk.RIGHT)
        self.regex_type.set('markupre')
        self.regex_type.trace('w', self.getPatternMatch)
        self.regexPattern = tk.StringVar()
        cbStyle = tkinter.ttk.Style()
        cbStyle = cbStyle.configure('red.TCombobox', foreground='red')
        self.entry = tkinter.ttk.Combobox(
            frame1,
            font=self.customFont,
            textvariable=self.regexPattern
        )
        self.entry.configure(postcommand=self.fillDropDownLst)
        self.entry.pack(after=lbl,side=tk.LEFT, fill=tk.X, expand=1)

        self.entry.event_add('<<re_escape>>', '<Control-E>', '<Control-e>')
        self.entry.bind('<<re_escape>>', self.selPasteWithReEscape)
        self.entry.bind('<Return>', lambda event: self.extreme('<<'))
        self.entry.bind('<FocusIn>', self.onFocusEvent)
        self.entry.bind('<FocusOut>', self.onFocusEvent)
        self.entry.bind('<<ComboboxSelected>>', self.getPatternMatch)

        frame15 = tk.Frame(self)
        frame15.pack(fill=tk.X)
        label = tk.Label(frame15, text=" Flags: ", font=self.customFont)
        label.pack(side=tk.LEFT)

        self.chkVar = {}
        chkTxt = self.FLAGS
        for elem in chkTxt:
            self.chkVar[elem] = tk.IntVar()
            chkbutt = tk.Checkbutton(frame15, text=elem, variable=self.chkVar[elem], font=self.customFont)
            chkbutt.bind('<Button-1>', self.flagToggle)
            chkbutt.pack(side=tk.LEFT)

        frame3 = tk.Frame(self)
        cmbbxValues = ['[^X]+', '.+?', r'\w+', r'\W+?', r'(?P=<keyName>)']
        self.cmbbxPattern = tkinter.ttk.Combobox(frame3, font=self.customFont, values=cmbbxValues)
        self.cmbbxPattern.pack(side=tk.LEFT, fill=tk.X)
        cmbbxIntVar = tk.IntVar()
        self.cmbbxIntVar = cmbbxIntVar
        for k, elem in enumerate(['Pattern', 'Key']):
            boton = tk.Radiobutton(frame3, text=elem, width=15, value=k, variable=cmbbxIntVar)
            boton.pack(side=tk.LEFT)

        cmbbxValues = ['url', 'label', 'iconImage', 'thumbnailImage', 'SPAN', 'SEARCH', 'NXTPOSINI']
        self.cmbbxKey = tkinter.ttk.Combobox(frame3, font=self.customFont, values=cmbbxValues)
        self.cmbbxKey.pack(side=tk.LEFT, fill=tk.X)

        boton = tk.Button(frame3, font=self.customFont, text="Apply", command=self.keyMaker)
        boton.pack(side=tk.LEFT)

    def onFocusEvent(self, event):
        if event.type == '9':
            self.wtracer = self.regexPattern.trace("w", self.getPatternMatch)
        elif event.type == '10':
            self.regexPattern.trace_vdelete("w", self.wtracer)

    def onAnchor(self):
        textw = self.textWidget
        if self.anchor.get() == 1:
            height = textw.winfo_height()
            wndINI = textw.index('@0,0')
            wndFIN = textw.index('@0,%s' % height)
            seeIndx = textw.index('@0,%s' % (height // 2))
            self.anchorPos = [(wndINI, wndFIN, seeIndx)]
        else:
            wndINI, wndFIN, seeIndx = self.anchorPos.pop()
            textw.see(seeIndx)

    def setZoomManager(self, callBackFunc):
        self.zoomManager = callBackFunc

    def setZoomType(self, zoomType):
        self.butKeyMaker.config(text=zoomType)

    def getZoomType(self):
        return self.butKeyMaker.cget('text')

    def zoomInOut(self):
        if self.zoomManager:
            btnText = self.butKeyMaker.cget('text')
            retValue = self.zoomManager(btnText)
            if retValue:
                indx = 1 - ['ZoomIn', 'ZoomOut'].index(btnText)
                self.setZoomType(['ZoomIn', 'ZoomOut'][indx])

    def selPasteWithReEscape(self, event=None):
        textw = self.entry
        text = textw.selection_get(selection='CLIPBOARD')
        try:
            if text:
                if textw.select_present():
                    textw.delete('sel.first', 'sel.last')
                text = ''.join([(re.escape(elem) if elem in '()?.*{}[]+\\' else elem) for elem in text])
                textw.insert('insert', text)
        except tk.TclError:
            pass
        return 'break'

    def fillDropDownLst(self):
        if not self.dropDownFiler: return
        self.theValues = self.dropDownFiler()
        cbValues = [val[0] + val[1] for val in self.theValues if val[1]]
        self.entry.configure(values=cbValues)

    def extreme(self, widgetText):
        if widgetText == '<<':
            npos = 0
        elif widgetText == '>>':
            npos = -1
        children = self.tree.get_children()
        iid = children[npos]
        self.tree.selection_set(iid)

    def keyMaker(self):
        tagName = self.cmbbxKey.get()
        tagPattern = self.cmbbxPattern.get()
        entryTxt = self.regexPattern.get()
        if tagName in ['SPAN', 'NXTPOSINI']:
            entryTxt = '(?#<' + tagName + '>)' + entryTxt
        elif self.entry.select_present():
            selText = self.entry.selection_get()
            posIni = entryTxt.find(selText)
            posFin = posIni + len(selText)
            if tagPattern == '[^X]+': tagPattern = tagPattern.replace('^X', '^' + entryTxt[posFin])
            if tagPattern == r'(?P=<keyName>)':
                tagReplace = tagPattern.replace('<keyName>', tagName)
            elif tagName == 'SEARCH':
                entryTxt = '(?#<SEARCH>)' + entryTxt
                tagReplace = '<search>'
                posIni += len('(?#<SEARCH>)')
                posFin += len('(?#<SEARCH>)')
            elif self.cmbbxIntVar.get() == 1:
                tagReplace = '(?P<' + tagName + '>' + tagPattern + ')'
            elif self.cmbbxIntVar.get() == 0:
                tagReplace = tagPattern
            entryTxt = entryTxt[:posIni] + tagReplace + entryTxt[posFin:]
            posFin = posIni + len(tagReplace)
            self.entry.select_range(posIni, posFin)
            self.entry.icursor(posFin)
        self.regexPattern.set(entryTxt)

    def actMatch(self, nPos):
        selTag = 'I{:03x}'.format(nPos)
        # selTag = selTag.upper()
        self.tree.see(selTag)

    def getRegexpPattern(self, withFlags=False):
        regExPat = self.regexPattern.get()
        if withFlags:
            compFlags = self.getCompFlags()
            regExPat = self.getCompFlagsPatt(compFlags) + regExPat
        return regExPat

    def setCompFlagsPatt(self, comFlagsPatt):
        comFlagsPatt = self.getCompFlags(comFlagsPatt)
        comFlags = '|'.join(['re.%s' % x for x in comFlagsPatt])
        self.setCompFlags(comFlags)

    def setCompFlags(self, compflags):
        if compflags == -1: compflags = ''
        keyFlags = compflags.replace('re.', '').split('|') if compflags else []
        for key in list(self.chkVar.keys()):
            flag = True if key in keyFlags else False
            self.chkVar[key].set(flag)

    def setRegexpPattern(self, regexp):
        if regexp:
            rgxflags, crgflags, regexp = self.getFlagsRegexPair(regexp)
            compFlags = rgxflags + crgflags
            if compFlags:
                self.setCompFlagsPatt(compFlags)
        self.regexPattern.set(regexp)

    def setActualMatch(self, selTag):
        textw = self.textWidget
        selTag = [textw.index('1.0  + %s chars' % x) for x in selTag]
        index = selTag[0]
        while True:
            index = textw.mark_next(index)
            if index.startswith('I'): break

        assert textw.index(index) == selTag[0]
        nPos = int(index[1:], 16)  # Para corregir verificar que la marca es Ixxx

        matchStr = self.matchLabel.cget('text')
        n = matchStr.find(' de ')
        matchStr = ' ' + str(nPos) + matchStr[n:]
        self.actMatchIndx = nPos

        self.textWidget.tag_remove('actMatch', '1.0', 'end')
        self.textWidget.tag_add('actMatch', *selTag)
        self.textWidget.mark_set('insert', selTag[0])

        dif = len(self.textWidget.get(*selTag))
        line, col = str(selTag[0]).split('.')
        self.messageVar.set('Ln: %s Col: %s Sel:%s' % (line, col, dif))

        self.textWidget.see(selTag[1])
        self.textWidget.see(selTag[0])
        self.matchLabel.config(text=matchStr)

        self.actMatch(nPos)

    def getBorderTags(self, indexPos, withActMatch=True):
        textw = self.textWidget

        def getNextItem(indexPos):
            index = indexPos = textw.index(indexPos)
            while True:
                index = textw.mark_next(index)
                if index:
                    if index.startswith('I') and textw.index(index) != indexPos:
                        break
                else:
                    index = '1.0'
            return index

        def getPreviousItem(indexPos):
            index = indexPos = textw.index(indexPos)
            while True:
                index = textw.mark_previous(index)
                if index:
                    if index.startswith('I') and textw.index(index) != indexPos:
                        break
                else:
                    index = tk.END
            return index

        nxtMark = getNextItem(indexPos)
        prevMark = getPreviousItem(indexPos)

        if withActMatch and 'actMatch' in textw.tag_names(indexPos) and 'actMatch' in textw.tag_names(prevMark):
            prevMark = getPreviousItem(prevMark)

        return (prevMark, nxtMark)

    def nextMatch(self):
        insPoint = self.textWidget.index(tk.INSERT)
        iid = self.getBorderTags(insPoint)[1]
        # iid = 'I{:03x}'.format(iid).upper()
        self.tree.selection_set(iid)

    def prevMatch(self):
        insPoint = self.textWidget.index(tk.INSERT)
        iid = self.getBorderTags(insPoint)[0]
        # iid = 'I{:03x}'.format(iid).upper()
        self.tree.selection_set(iid)

    def flagToggle(self, event):
        widget = event.widget
        widget.toggle()
        self.getPatternMatch()
        return 'break'

    def getPatternMatch(self, *dummy):
        pattern = self.regexPattern.get()
        if self.entry.current() != -1 and self.entry.get() == pattern:
            ndx, pattern = re.match(r'(?P<ndx>\(\?#<r.+?>\))?(?P<rgx>.+?)\Z', pattern).groups()
            self.cbIndex.set(ndx)
        else:
            if self.cbIndex.get():
                cbValues = self.entry.cget('values')
                if self.cbIndex.get() + pattern not in cbValues:
                    self.cbIndex.set('')
        self.setRegexpPattern(pattern)
        self.formatContent()
        if self.cbIndex.get():
            self.textWidget.focus_force()
        # A continuación la implementación del keyboard delay
        # if self.keyboard_delay is None:
        #     # print('inicio delay buffer')
        #     self.after(500, self.delay_buffer)
        # self.keyboard_delay = time.time_ns() // 1_000_000

    def delay_buffer(self):
        now = time.time_ns() // 1_000_000
        delta = now - self.keyboard_delay
        if delta >= 500:
            self.formatContent()
            if self.cbIndex.get():
                self.textWidget.focus_force()
            self.keyboard_delay = None
        else:
            self.after(500 - delta, self.delay_buffer)


    def formatContent(self, index1='1.0', index2='end'):
        mutex = self.mutex
        if self.activeCallBack:
            idAfter = self.activeCallBack.pop()
            self.after_cancel(idAfter)
        if mutex.is_set():
            mutex.clear()
            if self.t.is_alive():
                self.t.join(10)
                mutex.clear()

        self.queue.queue.clear()
        self.removeTags('1.0', 'end')

        no_flags_pattern = self.getRegexpPattern()
        if not no_flags_pattern:
            return None
        regexPattern = self.getRegexpPattern(withFlags=True)
        rgxflags, crgflags, no_flags_pattern = self.getFlagsRegexPair(regexPattern)
        regexPattern = crgflags + no_flags_pattern
        compileOp = self.getCompFlags(rgxflags)
        matchLabel = self.matchLabel

        opFlag = {'UNICODE': re.UNICODE, 'DOTALL': re.DOTALL, 'IGNORECASE': re.IGNORECASE,
                  'LOCALE': re.LOCALE, 'MULTILINE': re.MULTILINE, 'VERBOSE': re.VERBOSE}
        compFlags = reduce(lambda x, y: x | y, [opFlag[key] for key in compileOp], 0)

        content = self.textWidget.get(index1, index2)
        if not content.strip(' \n\r\t\f'):
            return None
        baseIndex = self.textWidget.index(index1)

        yesCompFlag = len(regexPattern) > 0
        if not yesCompFlag:
            matchLabel.config(text='')
            return None
        self.entry.configure(style='red.TCombobox')
        try:
            match self.regex_type.get():
                case 'selector':
                    sel = Selector(no_flags_pattern)
                    if sel.is_valid:
                        reg = sel.compiled_selector
                        # Para que se presente el span de los aciertos.
                        regexPattern = '(?#<SPAN>)' + no_flags_pattern
                    else:
                        reg = None
                case _:
                    reg = MarkupRe.compile(no_flags_pattern, compFlags)
        except Exception as inst:
            self.queue.put([None, (str(inst),)])
            return self.updateGUI()
        else:
            self.matchLabel.config(text='')
            self.messageVar.set('')
            if not reg:
                return None
        if hasattr(reg, 'searchFlag'):
            reg.searchFlag = mutex
        self.entry.configure(style='TCombobox')
        tags = ['_grp%s' % x for x in range(1, reg.groups + 1)]
        for key, val in list(reg.groupindex.items()):
            tags[val - 1] = key

        prefix = ['PosINI', 'PosFIN']
        if regexPattern.startswith('(?#<SPAN>)'):
            pini = 0
            if hasattr(reg, 'params_class'):
                prefix += reg.params_class._fields
        else:
            pini = 2

        tags = prefix + tags
        self.tree['displaycolumns'] = list(range(pini, len(tags)))
        for k, colName in enumerate(tags):
            self.tree.heading(k, text=colName)
        colBeg = len(tags)
        colEnd = len(self.tree.cget('columns'))
        for k in range(colBeg, colEnd):
            self.tree.heading(k, text='')

        if not mutex.is_set():
            mutex.set()
            self.t = threading.Thread(
                name="searchThread",
                target=self.lengthProcess,
                args=(reg, content, baseIndex, mutex)
            )
            self.t.start()
            self.activeCallBack.append(self.after(100, self.updateGUI))

    def lengthProcess(self, reg, content, baseIndex, mutex):
        sentinel = 0
        it = enumerate(reg.finditer(content, 0))
        while mutex.is_set() and sentinel >= 0:
            try:
                k, match = next(it)
                sentinel = k = k + 1
            except StopIteration:
                k, match = -sentinel, None
                sentinel = -1
            except Exception as e:
                k, match = None, (str(e),)
                sentinel = -1
            self.queue.put([k, (match, baseIndex)])

    def removeTags(self, tagIni, tagFin):
        tagColor = ['evenMatch', 'oddMatch', 'actMatch', 'group', 'hyper']
        for match in tagColor:
            self.textWidget.tag_remove(match, tagIni, tagFin)
        for button in [self.leftWing, self.rightWing]:
            button.pack_forget()
        self.matchLabel.config(text='')
        items = self.tree.get_children()
        self.tree.delete(*items)
        list(map(self.textWidget.mark_unset, items))

    def setTag(self, tag, baseIndex, match, grpIndx):
        # start, end = match.span(grpIndx)
        # tagIni = f'{baseIndex} + {start} chars'
        # tagFin = f'{baseIndex} + {end} chars'

        f = lambda x: f'{baseIndex} + {x} chars'
        tagIni, tagFin = tuple(map(f, match.span(grpIndx)))
        try:
            self.textWidget.tag_add(tag, tagIni, tagFin)
        except:
            print(
                'exception: ' + tag + ' tagIni: ' + tagIni + ' tagFin: ' + tagFin
            )

        ngroups = len(match.groups())
        for key in range(1, ngroups + 1):
            tagIni, tagFin = tuple(map(f, match.span(key)))
            self.textWidget.tag_add('group', tagIni, tagFin)

        urlkeys = [key for key in list(match.groupdict().keys()) if key.lower().endswith('url')]
        if not urlkeys and 'label' in match.groupdict():
            urlkeys = ['label']
        for key in urlkeys:
            tagIni, tagFin = tuple(map(f, match.span(key)))
            self.textWidget.tag_add('hyper', tagIni, tagFin)

    def updateGUI(self):
        nProcess = 100
        k = 10000
        while k > 0 and not self.queue.empty() and nProcess:
            k, args = self.queue.get()
            if k is None:
                # k is None, an error has ocurred
                self.messageVar.set(args[0])
                self.matchLabel.config(text='Error', bg='red')
                btState = tk.DISABLED
                k = -1      # De esta forma sale del loop
            elif k > 0:
                match, baseIndex = args
                nProcess -= 1
                tagColor = ['evenMatch', 'oddMatch']
                matchColor = tagColor[k % 2]
                self.setTag(matchColor, baseIndex, match, 0)
                tagValues = match.span()        # (match.start(0), match.end(0))
                tagIni = self.textWidget.index(baseIndex + ' + %d chars' % tagValues[0])
                iid = 'I{:03x}'.format(k)
                self.textWidget.mark_set(iid, tagIni)

                max_cols = len(self.tree['columns'])
                if hasattr(match, 'parameters') and match.parameters:
                    tagValues += match.parameters
                tagValues += match.groups() + max_cols * ('',)
                tagValues = tagValues[:max_cols]
                self.tree.insert('', 'end', iid, values=tagValues)

                if k > 1:
                    matchStr = ' ' + str(k) + ' '
                    self.matchLabel.config(text=matchStr)
                    self.matchLabel.update()
                    continue
                self.actMatchIndx = 1
                self.matchLabel.config(text=' 1 ')
                self.setTag('actMatch', baseIndex, match, 0)
                self.textWidget.tag_delete('sel')
                btState = tk.NORMAL
            elif k == 0:
                self.actMatchIndx = 0
                self.matchLabel.config(text=' 0 de 0 ', bg='red')
                btState = tk.DISABLED
            elif k < 0:  # k is an negative integer, success
                btState = tk.NORMAL
                matchStr = ' ' + str(self.actMatchIndx) + ' de ' + str(-k) + ' '
                self.matchLabel.config(text=matchStr)
                self.matchLabel.update()

            if btState == tk.DISABLED and self.leftWing.winfo_ismapped():
                for button in [self.leftWing, self.rightWing]:
                    button.pack_forget()
            elif btState == tk.NORMAL and not self.leftWing.winfo_ismapped():
                self.matchLabel.pack_forget()
                for button in [self.leftWing, self.matchLabel, self.rightWing]:
                    button.pack(side=tk.LEFT)
        if k is not None and k > 0 or not self.queue.empty():
            if self.activeCallBack:
                idAfter = self.activeCallBack.pop()
                self.after_cancel(idAfter)
            self.activeCallBack.append(self.after(100, self.updateGUI))

    def getCompFlagsPatt(self, compFlags):
        if compFlags == '0':
            return ''
        compFlags = compFlags.replace('re.', '')
        trnMap = dict(list(zip(self.RGXFLAGS + self.CRGFLAGS, self.RGXFLAGSPAT + self.CRGFLAGSPAT)))
        compFlags = ''.join([trnMap[x] for x in compFlags.split('|')])
        rgxflags = ''.join(re.findall(r'[iLmsux]', compFlags))
        crgflags = re.findall(r'\(\?#<[A-Z]+>\)', compFlags)
        crgflags = [x for x in crgflags if x in self.CRGFLAGSPAT]
        crgflags = ''.join(crgflags)
        if rgxflags: rgxflags = '(?%s)' % rgxflags
        return rgxflags + crgflags

    def getCompFlags(self, flags=None):
        if flags is None:
            compflags = ['re.' + key for key in self.FLAGS if self.chkVar[key].get()]
            return '|'.join(compflags) if compflags else '0'
        crgpat = r'\(\?\#\<[A-Z]+\>\)'
        pattern = r'^(\(\?[iLmsux]+\))*((?:%s)+)*' % crgpat
        rgxflags, crgflags = re.findall(pattern, flags)[0]
        trnMap = dict(list(zip(self.RGXFLAGSPAT, self.RGXFLAGS)))
        rgxflags = [trnMap[x] for x in rgxflags.strip('(?)')]
        trnMap = dict(list(zip(self.CRGFLAGSPAT, self.CRGFLAGS)))
        crgflags = [trnMap.get(x, None) for x in re.findall(crgpat, crgflags)]
        crgflags = [_f for _f in crgflags if _f]
        return rgxflags + crgflags

    def getFlagsRegexPair(self, regexpat):
        crgpat = r'\(\?\#\<[A-Z]+\>\)'
        pattern = r'^(\(\?[iLmsux]+\))*((?:%s)+)*(.+)' % crgpat
        rgxflags, crgflags, regexp = re.findall(pattern, regexpat)[0]
        crgflags = re.findall(crgpat, crgflags)
        regexp = ''.join([x for x in crgflags if x not in self.CRGFLAGSPAT]) + regexp
        crgflags = ''.join([x for x in crgflags if x in self.CRGFLAGSPAT])
        return rgxflags, crgflags, regexp


class NavigationBar(tk.Frame):
    DEF_REQUEST_HEADERS = [
        ["User-Agent",
         "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.111 Safari/537.36"],
        ["Accept", "text/html, application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"],
        ["Accept-Encoding", "gzip,deflate,sdch"],
        ["Accept-Language", "es-ES,es;q=0.8,en;q=0.6"],
        ["Cache-Control", "max-age=0"],
        ["Connection", "keep-alive"]
    ]

    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.urlContent = None
        self.mutex = _thread.allocate_lock()
        self.activeUrl = tk.StringVar(master)
        self.upHistory = []
        self.downHistory = []
        self.cookies = {}
        self.request_headers = []
        self.browserParam = {'user-agent': network.DESKTOP_BROWSER, 'switch_location': True,
                             'working-dir': 'c:/testFiles'}
        self.initNetwork()
        self.makeWidgets()

    def makeWidgets(self):
        self.customFont = tkinter.font.Font(family='Consolas', size=18)
        urlFrame = self

        iconImage = imgp.getFontAwesomeIcon
        commOptions = dict(size=24, isPhotoImage=True, color='black', aspectratio='stretch')

        self.leftIcon = leftIcon = iconImage('fa-long-arrow-alt-left', **commOptions)
        self.rightIcon = rightIcon = iconImage('fa-long-arrow-alt-right', **commOptions)
        self.gearIcon = gearIcon = iconImage('fa-cog', **commOptions)

        self.prevUrl = tk.Button(urlFrame, image=leftIcon, state=tk.DISABLED, font=self.customFont, text="<",
                                 command=self.prevButton)
        self.prevUrl.pack(side=tk.LEFT)
        self.nextUrl = tk.Button(urlFrame, image=rightIcon, state=tk.DISABLED, font=self.customFont, text=">",
                                 command=self.nxtButton)
        self.nextUrl.pack(side=tk.LEFT)
        labelUrl = tk.Label(urlFrame, text="Actual URL:", width=11, justify=tk.LEFT)
        labelUrl.pack(side=tk.LEFT)
        self.labelUrl = labelUrl
        self.settings = tk.Button(urlFrame, image=gearIcon, font=self.customFont, text="S", command=self.settingComm)
        self.settings.pack(side=tk.RIGHT)
        entryUrl = tk.Entry(urlFrame, textvariable=self.activeUrl, font=self.customFont)
        entryUrl.pack(side=tk.LEFT, fill=tk.X, expand=1)
        entryUrl.bind('<Return>', self.returnKey)
        entryUrl.bind('<Control-o>', self.controlleftKey)

    def settingComm(self):
        file_name = '/Data/kodi/browserSettings.xml'
        settingObj = CustomDialog(
            self, title='Application Settings', xmlFile=file_name, isFile=True, settings=self.browserParam.copy()
        )
        changed_settings = settingObj.settings
        if self.browserParam != changed_settings:
            self.browserParam = changed_settings
            self.initNetwork()

    def initNetwork(self):
        bp = self.browserParam
        initConf = 'curl '
        initConf += ' --user-agent "%s"' % bp['user-agent']
        initConf += ' --cookie-jar "%s"' % bp.get('cookie-jar', 'cookies.lwp')
        if 'flag-output' in bp:
            initConf += ' -o "%s"' % bp['output']
            if 'remote-name' in bp: initConf += ' --remote-name'
            if 'remote-header-name' in bp: initConf += ' --remote-header-name'
        for key in bp:
            if not key.startswith('switch_'): continue
            switch = key[len('switch_'):]
            initConf += ' --' + switch
        if 'flag-proxy' in bp:
            initConf += ' --proxy "%s"' % bp['proxy']
            proxy_auth = bp['proxy_auth'].split('|', 1)[0]
            if proxy_auth != 'No authentication':
                initConf += ' --proxy-%s' % proxy_auth
                initConf += ' --proxy-user "%s:%s"' % (bp['proxy-user'], bp['proxy-password'])

        self.net = network.network(initConf, defDirectory=bp['working-dir'])

    def setActiveUrl(self, url):
        if url and not url.startswith('curl'):
            activeUrl = self.normUrl(self.activeUrl.get())
            url = urllib.parse.urljoin(activeUrl, url)
            url = self.unNormUrl(url)
        self.activeUrl.set(url)
        self.returnKey()

    def getActiveUrl(self):
        # rawUrl = self.activeUrl.get()
        # return self.net.getValuesFromUrl(rawUrl) if rawUrl else ''
        return self.net.values.url if self.net.values else ''

    def nxtButton(self, *args, **kwargs):
        if not len(self.upHistory): return
        self.prevUrl.config(state=tk.NORMAL)
        self.downHistory.append(self.upHistory.pop())
        if len(self.upHistory) == 1:
            self.nextUrl.config(state=tk.DISABLED)
        self.activeUrl.set(self.upHistory[-1])
        self.returnKey()

    def prevButton(self, *args, **kwargs):
        self.nextUrl.config(state=tk.NORMAL)
        self.upHistory.append(self.downHistory.pop())
        if not len(self.downHistory):
            self.prevUrl.config(state=tk.DISABLED)
        self.activeUrl.set(self.upHistory[-1])
        self.returnKey()

    def returnKey(self, *args, **kwargs):
        rawUrl = self.activeUrl.get()
        if not rawUrl: return
        if not self.upHistory:
            self.upHistory.append(rawUrl)
        elif rawUrl != self.upHistory[-1]:
            if len(self.upHistory) == 1:
                self.downHistory.append(self.upHistory.pop())
                self.prevUrl.config(state=tk.NORMAL)
            else:
                self.upHistory = []
                self.nextUrl.config(state=tk.DISABLED)
            self.upHistory.append(rawUrl)

        thId = _thread.start_new_thread(self.importUrl, (rawUrl, self.mutex))
        self.colorAnimation()

    def controlleftKey(self, event):
        name = tkFileDialog.askopenfilename(filetypes=[('text Files', '*.txt'), ('All Files', '*.*')])
        if name:
            name = 'file://' + urllib.request.pathname2url(name)
            self.activeUrl.set(name)
            self.returnKey()

    def colorAnimation(self, *args, **kwargs):
        with self.mutex:
            bFlag = not self.urlContent
        if bFlag:
            self.settings['state'] = tk.DISABLED
            colorPalette = ['-  -  -  -', '\\  /  \\  /', '/  \\  /  \\']
            actColor = self.labelUrl.cget('text')
            try:
                indx = (colorPalette.index(actColor) + 1) % (len(colorPalette))
            except:
                indx = 0
            self.labelUrl.config(text=colorPalette[indx])
            self.labelUrl.after(100, self.colorAnimation)
        else:
            resp_url, self.urlContent = self.urlContent
            self.activeUrl.set(resp_url)
            self.settings['state'] = tk.NORMAL
            if isinstance(self.urlContent, Exception):
                tkinter.messagebox.showerror('Error', self.urlContent)
                self.urlContent = ''
            self.urlContentProcessor(self.urlContent)
            self.urlContent = None
            self.labelUrl.config(text='Actual URL:')

    def setUrlContentProcessor(self, processor):
        self._urlContentProcessor = processor

    def urlContentProcessor(self, data):
        if self._urlContentProcessor: return self._urlContentProcessor(data)
        pass

    def normUrl(self, url):
        match = re.match(r'[a-zA-Z0-9]+?://', url)
        if match is None: url = 'http://' + url
        return url

    def unNormUrl(self, url):
        if url.startswith('http://'):
            url = url[7:]
        return url

    def importUrl(self, urlToOpen, mutex):
        try:
            data, resp_url = self.net.openUrl(urlToOpen)
        except Exception as e:
            self.urlContent = e
            return
        if isinstance(data, str):
            for match in re.finditer("\$\.cookie\('([^']+)',\s*'([^']+)", data):
                key, value = match.groups()
                self.cookies[key] = value
        with mutex:
            resp_url = self.unNormUrl(resp_url)
            self.urlContent = (resp_url, data)

    def openUrl(self, urlToOpen):
        """
        http://www.bvc.com.co/pps/tibco/portalbvc/Home/Mercados/enlinea/acciones?com.tibco.ps.pagesvc.action=portletAction&com.tibco.ps.pagesvc.targetSubscription=5d9e2b27_11de9ed172b_-74187f000001&action=buscar&tipoMercado=1&diaFecha=09&mesFecha=10&anioFecha=2015&nemo=&filtroAcciones=2
        <option\W+selected="selected"\W+value='(?P<grp1>[^']+)'>.+?</option>
        (?#<button class="yt-uix-button yt-uix-button-size-default yt-uix-button-default yt-uix-button-has-icon" .span<.*>*>)
        """

        # 31-08-04
        # v1.0.0

        # cookie_example.py
        # An example showing the usage of cookielib (New to Python 2.4) and ClientCookie

        # Copyright Michael Foord
        # You are free to modify, use and relicense this code.
        # No warranty express or implied for the accuracy, fitness to purpose or otherwise for this code....
        # Use at your own risk !!!

        # If you have any bug reports, questions or suggestions please contact me.
        # If you would like to be notified of bugfixes/updates then please contact me and I'll add you to my mailing list.
        # E-mail michael AT foord DOT me DOT uk
        # Maintained at www.voidspace.org.uk/atlantibots/pythonutils.html

        COOKIEFILE = 'cookies.lwp'  # the path and filename that you want to use to save your cookies in
        import os.path

        cj = None
        cookielib = None

        import http.cookiejar
        import urllib.request, urllib.parse
        cj = http.cookiejar.LWPCookieJar()  # This is a subclass of FileCookieJar that has useful load and save methods
        opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

        ####################################################
        # We've now imported the relevant library - whichever library is being used urlopen is bound to the right function for retrieving URLs
        # Request is bound to the right function for creating Request objects
        # Let's load the cookies, if they exist.

        if cj != None and os.path.isfile(
                COOKIEFILE):  # now we have to install our CookieJar so that it is used as the default CookieProcessor in the default opener handler
            cj.load(COOKIEFILE)

        request_headers = self.request_headers or self.DEF_REQUEST_HEADERS

        referer = 'http://www.peliculaspepito.com/'
        if self.downHistory:
            referer = self.downHistory[-1]
        request_headers.append(["Referer", referer])

        headers = dict(request_headers)

        urlToOpen, custHdr = urlToOpen.partition('<headers>')[0:3:2]
        if custHdr:
            custHdr = urllib.parse.parse_qs(custHdr)
            for key in custHdr:
                headers[key] = custHdr[key][0]

        urlToOpen, postData = urlToOpen.partition('<post>')[0:3:2]
        postData = postData or None

        try:
            req = urllib.request.Request(urlToOpen, postData or None, headers)
            url = opener.open(req)
        except Exception as e:
            data = e
        else:
            self.genHdr = []
            #             self.genHdr.append(('Remote Address', socket.gethostbyname(req.get_host()) + ':' + str(socket.getservbyname(req.get_type()))))
            #             self.genHdr.append(('Request Url', req.get_full_url()))
            #             self.genHdr.append(('Request Method', req.get_method()))
            #             self.genHdr.append(('Status Code', str(url.getcode())))
            self.reqHdr = req.header_items()
            self.rspHdr = list(url.headers.items())
            self.activeUrl.set(self.unNormUrl(url.geturl()))
            data = url.read()
            if url.info().get('Content-Encoding') == 'gzip':
                import io
                compressedstream = io.StringIO(data)
                import gzip
                gzipper = gzip.GzipFile(fileobj=compressedstream)
                data = gzipper.read()
                gzipper.close()
            url.close()
        if cj != None: cj.save(COOKIEFILE)  # save the cookies again
        return data


class PythonEditor(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.customFont = tkinter.font.Font(family='Consolas', size=18)
        self.prompt = ''
        self.cellInput = ''
        self.hyperlinkManager = None

        self.scrbar = scrollbar = tk.Scrollbar(self)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        textw = tk.Text(self, font=self.customFont, tabs=('1.5c'))
        textw.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=textw.yview)

        self.textw = textw
        textw.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        textw.see('end')
        textw.event_add('<<CursorlineOff>>', '<Up>', '<Down>', '<Next>', '<Prior>', '<Button-1>')
        textw.event_add('<<CursorlineOn>>', '<KeyRelease-Up>', '<KeyRelease-Down>', '<KeyRelease-Next>',
                        '<KeyRelease-Prior>', '<ButtonRelease-1>')
        textw.event_add('<<CopyEvent>>', '<Control-C>', '<Control-c>')
        textw.event_add('<<PasteEvent>>', '<Control-V>', '<Control-v>')
        textw.event_add('<<CutEvent>>', '<Control-X>', '<Control-x>')
        textw.event_add('<<SelAllEvent>>', '<Control-A>', '<Control-a>')
        textw.event_add('<<NavigationEvent>>',
                        '<Home>', '<Control-Home>', '<Shift-Home>',
                        '<End>', '<Control-End>', '<Shift-End>',
                        '<Control-Left>', '<Shift-Control-Left>',
                        '<Control-Right>', '<Shift-Control-Right>')

        textw.tag_configure('cursorLine', background='alice blue')
        textw.tag_configure('evenMatch', background='yellow')
        textw.tag_configure('oddMatch', background='red')
        textw.tag_configure('actMatch', background='light green')
        textw.tag_configure('group', foreground='blue')
        textw.tag_configure("hyper", foreground="blue", underline=1)
        textw.tag_configure(tk.SEL, foreground='white', background='blue')
        textw.tag_raise(tk.SEL)

        textw.tag_bind("hyper", "<Enter>", self._enter)
        textw.tag_bind("hyper", "<Leave>", self._leave)
        textw.tag_bind("hyper", "<Button-1>", self._click)

        self.dispPrompt()
        textw.bind('<<CopyEvent>>', self.selCopy)
        textw.bind('<<PasteEvent>>', self.selPaste)
        textw.bind('<<CutEvent>>', self.selCut)
        textw.bind('<<SelAllEvent>>', self.selAll)
        textw.bind('<<CursorlineOff>>', self.onUpPress)
        textw.bind('<<CursorlineOn>>', self.onUpRelease)
        textw.bind('<<NavigationEvent>>', self.moveCursor)

    def moveCursor(self, event):
        control_key = (event.state & 0x0004)
        shift_key = (event.state & 0x0001)
        posIni = self.textw.index(tk.INSERT)
        if event.keysym == 'Home' and control_key:  # <Control-Home>
            posFin = '1.0'
        elif event.keysym == 'End' and control_key:  # <Control-End>
            posFin = tk.END
        elif event.keysym == 'Home' and not control_key:  # <Home>
            posFin = '%s linestart' % posIni
        elif event.keysym == 'End' and not control_key:  # <End>
            posFin = '%s lineend' % posIni
        elif event.keysym == 'Left' and control_key:  # <Control-Left>
            posFin = '%s wordstart' % posIni
        elif event.keysym == 'Right' and control_key:  # <Control-Right>
            posFin = '%s wordend' % posIni

        if shift_key:
            if not self.textw.tag_ranges('sel'): self.textw.mark_set('tk::anchor1', posIni)
            self.textw.tag_add('sel', posIni, posFin)
        self.textw.see(posFin)
        self.textw.mark_set('insert', posFin)

    def _enter(self, event):
        self.textw.config(cursor="hand2")

    def _leave(self, event):
        self.textw.config(cursor="")

    def _click(self, event):
        if 'hyper' in self.textw.tag_names(tk.CURRENT):
            tagRange = self.textw.tag_prevrange('hyper', tk.CURRENT) or (tk.CURRENT,)
            texto = self.textw.get(*tagRange)
            self.processHyperlink(texto)
            return

    def setHyperlinkManager(self, callbackFunction):
        self.hyperlinkManager = callbackFunction

    def processHyperlink(self, texto):
        if self.hyperlinkManager:
            self.hyperlinkManager(texto)

    def onUpPress(self, event=None):
        textw = self.textw
        textw.tag_remove('cursorLine', '1.0', 'end')

    def onUpRelease(self, event=None):
        textw = self.textw
        if textw.tag_ranges('sel'): return
        textw.tag_add('cursorLine', 'insert linestart', 'insert lineend + 1 chars')

    def getSelRange(self, tagName='sel'):
        textw = self.textw
        try:
            return textw.tag_ranges(tagName)
        except tk.TclError:
            return None

    def colorMatch(self, baseIndex, match, matchColor, frstMatch=False):
        tagIni, tagFin = tuple(map(lambda x: f'{baseIndex} + {x} chars', match.span()))

        try:
            self.textw.tag_add(matchColor, tagIni, tagFin)
        except:
            print()
            'exception: ' + matchColor + ' tagIni: ' + tagIni + ' tagFin: ' + tagFin
        # self.textw.tag_add('matchTag', tagIni, tagFin)
        if frstMatch:
            self.textw.tag_add('actMatch', tagIni, tagFin)
        return

    def getContent(self, posIni='1.0', posFin='end'):
        textw = self.textw
        return textw.get(posIni, posFin)

    def setContent(self, text):
        self.textw.delete('1.0', 'end')
        if text:
            self.textw.insert('1.0', text.replace('\r', ''))

    def selDel(self, event=None):
        textw = self.textw
        selRange = self.getSelRange()
        if selRange: textw.delete(*selRange)

    def selPaste(self, event=None):
        textw = self.textw
        try:
            text = textw.selection_get(selection='CLIPBOARD')
            textw.insert('insert', text)
        except tk.TclError:
            pass
        return 'break'

    def selCopy(self, event=None):
        textw = self.textw
        selRange = self.getSelRange()
        if selRange:
            text = textw.get(*selRange)
            textw.clipboard_clear()
            textw.clipboard_append(text)
        return selRange

    def selCut(self, event=None):
        textw = self.textw
        selRange = self.selCopy()
        if selRange: textw.delete(*selRange)

    def selAll(self, event=None):
        textw = self.textw
        textw.tag_add('sel', '1.0', 'end')

    def setCustomFont(self, tFamily="Consolas", tSize=18):
        self.customFont.configure(family=tFamily, size=tSize)

    def dispPrompt(self):
        self.textw.insert('insert', self.prompt)
        self.textw.insert('insert', self.cellInput)

    def isIndentModeOn(self):
        return len(self.cellInput) > 0

    def setNextIndentation(self, expr):
        if len(expr):
            nTabs = len(expr) - len(expr.lstrip('\t'))
            if expr[-1] == ':': nTabs += 1
            self.cellInput = nTabs * '\t'
        else:
            self.cellInput = ''

    def setKeyHandler(self, objInst):
        self.textw.bind('<Key>', objInst.keyHandler)


class StatusBar(tk.Frame):
    def __init__(self, master, statusList):
        tk.Frame.__init__(self, master)
        self.setGUI(statusList)

    def setGUI(self, statusList):
        kwargs = dict(bd=3, relief=tk.SUNKEN, height=1, width=40, anchor=tk.NW, padx=5)
        frame = tk.Frame(self, bd=5)
        frame.pack(side=tk.TOP, fill=tk.X)
        for ltext, str_var in statusList[:-1]:
            label = tk.Label(frame, text=ltext, bd=3)
            label.pack(side=tk.LEFT)
            kwargs['textvariable'] = str_var
            label = tk.Label(frame, **kwargs)
            label.pack(side=tk.LEFT)

        kwargs['textvariable'] = statusList[-1][1]
        label = tk.Label(frame, **kwargs)
        label.pack(side=tk.RIGHT, fill=tk.X, expand=1)
        label = tk.Label(frame, text=statusList[-1][0], bd=3)
        label.pack(side=tk.RIGHT)


class RegexpFrame(tk.Frame):
    def __init__(self, master, messageVar):
        tk.Frame.__init__(self, master)
        self.dropDownFiler = None
        self.popUpMenu = None
        self.state = None
        self.queue = queue.Queue(maxsize=0)
        self.activeCallBack = []
        self.threadFlag = 'stop'

        self.messageVar = messageVar
        self.setGUI()

    def setGUI(self):
        self.customFont = tkinter.font.Font(family='Consolas', size=18)

        self.urlFrame = NavigationBar(self)
        self.urlFrame.pack(fill=tk.X)
        self.urlFrame.setUrlContentProcessor(self.setContent)

        self.regexBar = RegexpBar(self, self.messageVar)
        self.regexBar.pack(fill=tk.X)
        self.regexBar.setZoomManager(self.zoom)

        frame2 = CollapsingFrame.collapsingFrame(self, buttconf='mRM')
        frame2.pack(fill=tk.BOTH, expand=1)
        self.txtEditor = PythonEditor(frame2.frstWidget)
        self.tree = TreeList(
            frame2.scndWidget,
            displaycolumns='#all',
            show='headings', columns=(
                'posINI', 'posFIN', 'var0', 'var1', 'var2', 'var3', 'var4', 'var5', 'var6', 'var7', 'var8', 'var9'
            )
        )
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

        self.txtEditor.setKeyHandler(self)
        self.txtEditor.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        self.txtEditor.setHyperlinkManager(self.hyperLnkMngr)
        self.regexBar.setTextWidget(self.txtEditor.textw)
        self.regexBar.setTreeWidget(self.tree)
        self.txtEditor.textw.bind('<Button-3>', self.do_popup)

    def isZoomed(self):
        return self.regexBar.butKeyMaker.cget('text') != 'ZoomIn'

    def zoom(self, btnText):
        if btnText == 'ZoomIn':
            selRange = self.txtEditor.getSelRange() or self.txtEditor.getSelRange('actMatch')
            if not selRange:
                return False
            zinBuff = [self.txtEditor.scrbar.get(), selRange]
            textw = self.txtEditor.textw
            height = textw.winfo_height()
            zinBuff.append((textw.index(tk.INSERT), textw.index('@0,%s' % (height // 2))))
            regExPat = self.getRegexpPattern()
            prefix = self.regexBar.cbIndex.get()
            zinBuff.append((prefix, regExPat))
            self.regexBar.anchorPos.append(zinBuff)
            self.regexBar.butAnchor['state'] = tk.DISABLED
            if regExPat.startswith('(?#<SPAN>)'):
                self.setActiveUrl()
            texto = self.txtEditor.getContent(*selRange)
            try:
                htmlParse = MarkupRe.ExtRegexParser({}, []).htmlStruct(texto)
            except:
                tkMessageBox.showinfo('Actual match HTMLstruct', 'Not HTML conform')
            else:
                for (pins, _), path, _ in reversed(htmlParse):
                    texto = texto[:pins] + f'<!-- {path} -->' + texto[pins:]
            self.setContent(texto, False)
            self.setRegexpPattern('<!-- .+? -->')
            return True
        else:
            self.urlFrame.returnKey()
            return False

    def setDropDownFiler(self, callbckFunc):
        self.regexBar.setDropDownFiler(callbckFunc)

    def do_popup(self, event):
        if not self.popUpMenu: return
        popup = self.popUpMenu()
        try:
            popup.post(event.x_root, event.y_root)
        finally:
            popup.grab_release()

    def setPopUpMenu(self, popUpMenu):
        self.popUpMenu = popUpMenu

    def keyHandler(self, event):
        textw = event.widget
        if textw == self.txtEditor.textw and event.keysym not in ['Left', 'Right', 'Up', 'Down', 'Next', 'Prior',
                                                                  'Button-1']:
            return "break"

    def getSelRange(self, tagName='sel'):
        return self.txtEditor.getSelRange(tagName)

    def setContent(self, data, newUrl=True):
        self.txtEditor.setContent(data)
        self.regexBar.getPatternMatch()
        if self.regexBar.getZoomType() == 'ZoomOut' and (
                len(self.regexBar.anchorPos) - self.regexBar.anchor.get()) == 1:
            zinBuff = self.regexBar.anchorPos.pop()
            textw = self.txtEditor.textw
            posIni, posFin = zinBuff[1]
            textw.mark_set('tk::anchor1', posIni)
            textw.tag_add('sel', posIni, posFin)
            insPos, wndFIN = zinBuff[2]
            textw.mark_set(tk.INSERT, insPos)
            textw.see(wndFIN)
            prefix, regExPat = zinBuff[3]
            self.regexBar.cbIndex.set(prefix)
            self.setRegexpPattern(regExPat)
            self.regexBar.butAnchor['state'] = tk.NORMAL
        if newUrl: self.regexBar.setZoomType('ZoomIn')

    def pasteFromClipboard(self, event=None):
        textw = self.txtEditor.textw
        try:
            data = textw.selection_get(selection='CLIPBOARD')
            self.setContent(data)
        except tk.TclError:
            pass
        else:
            self.urlFrame.setActiveUrl('')

    def getContent(self, posIni='1.0', posFin='end'):
        return self.txtEditor.getContent(posIni, posFin)

    def getRegexpPattern(self, *args, **kwargs):
        return self.regexBar.getRegexpPattern(*args, **kwargs)

    def getCompFlags(self):
        return self.regexBar.getCompFlags()

    def setRegexpPattern(self, regexp):
        self.regexBar.setRegexpPattern(regexp)

    def setCompFlags(self, compflags):
        self.regexBar.setCompFlags(compflags)

    def hyperLnkMngr(self, url):
        baseurl = self.urlFrame.getActiveUrl()
        url = urllib.parse.urljoin(baseurl, url)
        self.urlFrame.setActiveUrl(url)
        # self.setContent(content)

    def setActiveUrl(self, url=None):
        if url:
            if self.regexBar.anchorPos:
                self.regexBar.anchorPos = []
                self.regexBar.anchor.set(0)
            self.urlFrame.setActiveUrl(url)

    def getActiveUrl(self):
        return self.urlFrame.getActiveUrl()


if __name__ == '__main__':
    top = tk.Tk()
    message = tk.StringVar()
    status_list = [('Message:', message)]
    sb = StatusBar(top, status_list)
    sb.pack(side=tk.BOTTOM, fill=tk.X, expand=0)
    rgf = RegexpFrame(top, message)
    rgf.pack(side=tk.TOP, fill=tk.BOTH, expand=tk.YES)
    top.mainloop()
