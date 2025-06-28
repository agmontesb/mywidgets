import tkinter as tk

from mywidgets.Widgets.Custom import ImageProcessor as imgp


BAND_WIDTH = 18
BAND_COLOR = 'light sea green'

# Button Configuration
# R = Restore
# M = Maximize
# m = Minimize


class collapsingFrame(tk.Frame):
    def __init__(self, master, orientation=tk.HORIZONTAL, inisplit=0.8, buttconf='RMm', name=None, hide=None):
        tk.Frame.__init__(self, master, name=name)
        self.buttIcon = {}
        self.frstWidget = tk.Frame(self, name='frstwidget')
        self.scndWidget = tk.Frame(self, name='scndwidget')
        self.bandRelDim = 0
        self._state = None

        assert orientation in [tk.VERTICAL, tk.HORIZONTAL], f'{orientation} is not a valid orientation'
        self.orientation = orientation
        buttconf = buttconf if hide is None else ('hR' if hide.lower() in ('left', 'top') else 'HR')
        self.buttConf = buttconf
        self.setIcons(orientation, buttconf)
        self.cursor = 'sb_v_double_arrow' if orientation == tk.HORIZONTAL else 'sb_h_double_arrow'
        self.dim = 'height' if orientation == tk.HORIZONTAL else 'width'
        self.bind('<Configure>', self.configure, add=True)
        self.split = float(inisplit)
        self.setGUI()

    def setIcons(self, orientation, buttconf):
        if 'h' in buttconf.lower():
            return
        iconImage = imgp.getFontAwesomeIcon
        commOptions = dict(size=BAND_WIDTH, isPhotoImage=True, color='black')
        case = len(buttconf)
        if case == 2:
            if orientation == tk.VERTICAL:
                self.buttIcon['M'] = iconImage('fa-caret-left', **commOptions)
                self.buttIcon['m'] = iconImage('fa-caret-right', **commOptions)
                if 'R' in buttconf:
                    faIcon = 'fa-caret-right' if 'M' in buttconf else 'fa-caret-left'
                    self.buttIcon['R'] = iconImage(faIcon, **commOptions)
            else:
                self.buttIcon['M'] = iconImage('fa-caret-up', **commOptions)
                self.buttIcon['m'] = iconImage('fa-caret-down', **commOptions)
                if 'R' in buttconf:
                    faIcon = 'fa-caret-down' if 'M' in buttconf else 'fa-caret-up'
                    self.buttIcon['R'] = iconImage(faIcon, **commOptions)

                self.buttIcon['R'] = iconImage('fa-caret-down', **commOptions)
        elif case == 3:
            self.buttIcon['M'] = iconImage(imgp.FA_WINDOW_MAX, **commOptions)
            self.buttIcon['R'] = iconImage(imgp.FA_WINDOW_RES, **commOptions)
            self.buttIcon['m'] = iconImage(imgp.FA_WINDOW_MIN, **commOptions)

    def clickButton(self, nButt=1):
        nButt = max(1, min(len(self.buttConf) - 1, nButt))
        boton = getattr(self, 'b' + str(nButt))
        btTxt = boton.cget('text')
        self.comButton(btTxt)

    def hide_band(self, side):
        match side:
            case 'h' | 'left' | 'top':                         # hide in ('left', 'top')
                self.frstWidget.place_forget()
                self.band.place_forget()
                self.scndWidget.place(**self.trn(rely=0, y=0, relheight=1.0, relwidth=1.0))
            case 'H' | 'right' | 'bottom':                         # hide in ('left', 'top')
                self.scndWidget.place_forget()
                self.band.place_forget()
                self.frstWidget.place(**self.trn(rely=0, relheight=1, relwidth=1.0))

    def show_band(self):
        self.wdef()

    def setWidgetLayout(self, btnTxt=None):
        if btnTxt:
            self._state = btnTxt
        else:
            btnTxt = self._state
        match btnTxt:
            case 'M':                   # Maximize case
                return self.wmax()
            case 'm':                   # Minimize case
                return self.wmin()
            case 'h' | 'H':             # Hide case
                return self.hide_band(btnTxt)
            case _: # Restore case
                self.wdef()

    def configure(self, event):
        totDim = event.height if self.orientation == tk.HORIZONTAL else event.width
        self.bandRelDim = float((1.0 * BAND_WIDTH) / totDim)
        if self.is_hide():
            return
        btnTxt = self.nxtButton()
        self.setWidgetLayout(btnTxt)

    def nxtButton(self):
        if self.is_hide():
            return 'R'
        buttons = [getattr(self, 'b' + str(k + 1)) for k in range(len(self.buttConf) - 1)]
        return set(self.buttConf).difference(map(lambda x: x['text'][1], buttons)).pop()

    def is_hide(self):
        return self._state.lower() == 'h'

    def setGUI(self):
        master = self
        self.band = tk.Frame(master, bg=BAND_COLOR, cursor=self.cursor)
        self.band[self.dim] = BAND_WIDTH
        self.band.bind('<ButtonPress-1>', self.b1pressh)
        self.band.bind('<Button1-Motion>', self.b1motion)
        self.band.bind('<ButtonRelease-1>', self.b1releaseh)
        btn_labels = self.buttConf[1:]
        btn_labels = btn_labels.replace('h', '').replace('H', '').replace('R', '')
        for k, btnTxt in enumerate(btn_labels):
            buttLabel = str(k + 1) + btnTxt
            setattr(self, 'b' + str(k + 1),
                    tk.Button(master, bg=BAND_COLOR, text=buttLabel, image=self.buttIcon[btnTxt],
                              command=lambda x=buttLabel: self.comButton(x)))
        self.setWidgetLayout(self.buttConf[0])

    def comButton(self, btTxt):
        nBtn, btId = btTxt
        self.setWidgetLayout(btId)
        btnTxt = self.nxtButton()
        boton = getattr(self, 'b' + nBtn)
        boton['text'] = nBtn + btnTxt
        boton['image'] = self.buttIcon[btnTxt]
        boton['command'] = lambda: self.comButton(boton['text'])

    def trn(self, **kwargs):
        if self.orientation == tk.HORIZONTAL: return kwargs
        answer = {}
        for k in kwargs:
            if k.endswith('x'):
                newK = k[:-1] + 'y'
            elif k.endswith('y'):
                newK = k[:-1] + 'x'
            elif k.endswith('width'):
                newK = k.replace('width', 'height')
            elif k.endswith('height'):
                newK = k.replace('height', 'width')
            else:
                newK = k
            answer[newK] = kwargs[k]
        return answer

    def wdef(self):
        splitComp = 1 - self.split - self.bandRelDim
        trn = self.trn
        self.frstWidget.place(**trn(relheight=self.split, relwidth=1.0))
        self.placeSepBand()
        self.scndWidget.place(**trn(rely=self.split, y=BAND_WIDTH, relheight=splitComp, relwidth=1.0))
        self.band['cursor'] = self.cursor

    def placeSepBand(self, kwargs=None):
        kwargs = kwargs or {}
        trn = self.trn
        placeInfo = trn(rely=self.split, y=0, relwidth=1.0)
        placeInfo.update(kwargs)
        self.band.place(**placeInfo)
        if not self.is_hide():
            for k in range(len(self.buttConf) - 1):
                widget = getattr(self, 'b' + str(k + 1))
                placeInfo = trn(rely=self.split, relx=1.0, y=0, x=-(k + 1) * BAND_WIDTH, height=BAND_WIDTH,
                                width=BAND_WIDTH)
                if self.orientation == tk.VERTICAL:
                    placeInfo['rely'] = 0
                    placeInfo['y'] = -(placeInfo['y'] + BAND_WIDTH)
                if kwargs: placeInfo.update(kwargs)
                widget.place(**placeInfo)

    def wmax(self):
        self.frstWidget.place_forget()
        self.scndWidget.place(**self.trn(rely=0, y=BAND_WIDTH, relheight=1.0 - self.bandRelDim, relwidth=1.0))
        kwargs = self.trn(rely=0, y=0)
        self.placeSepBand(kwargs)
        self.band['cursor'] = 'arrow'

    def wmin(self):
        self.scndWidget.place_forget()
        self.frstWidget.place(**self.trn(rely=0, relheight=1 - self.bandRelDim, relwidth=1.0))
        kwargs = self.trn(rely=1.0, y=-BAND_WIDTH)
        self.placeSepBand(kwargs)
        self.band['cursor'] = 'arrow'

    def b1pressh(self, event):
        if 'R' != self.nxtButton(): return
        self.mband = tk.Frame(self, bg='grey', cursor=self.cursor)
        self.mband[self.dim] = BAND_WIDTH
        kwargs = self.trn(rely=self.split, relwidth=1.0)
        self.mband.place(**kwargs)

    def b1motion(self, event):
        if 'R' != self.nxtButton():
            return
        mwidth = self.master.winfo_height() if self.orientation == tk.HORIZONTAL else self.master.winfo_width()
        mmin = 0
        mmax = 1 - self.bandRelDim
        pos = event.y if self.orientation == tk.HORIZONTAL else event.x
        puPos = float((self.split * mwidth + pos) / mwidth)
        pixels = min(mmax, max(mmin, puPos))
        self.mband.place(**self.trn(rely=pixels))

    def b1releaseh(self, event):
        if 'R' != self.nxtButton():
            return
        if self.orientation == tk.HORIZONTAL:
            mwidth = self.master.winfo_height()
            pos = event.y
        else:
            mwidth = self.master.winfo_width()
            pos = event.x
        split = (float(self.split * mwidth) + pos) / float(mwidth)
        self.split = max(0.0, min(1.0 - float(BAND_WIDTH) / float(mwidth), split))
        self.mband.place_forget()
        self.wdef()
        pass


if __name__ == '__main__':
    leftPane = 3
    def leftPaneChg(pane):
        global leftPane
        labels[leftPane - 1].pack_forget()
        labels[pane - 1].pack(side=tk.TOP, fill=tk.BOTH, expand=tk.YES)
        leftPane = pane
    root = tk.Tk()

    def hide_show(*args, **kwargs):
        if bVar.get():
            motherFrame.show_band()
        else:
            motherFrame.hide_band('left')
    bVar = tk.BooleanVar()
    bVar.set(True)
    bVar.trace_add('write', hide_show)
    btn1 = tk.Checkbutton(
        root, text='H\ni\nd\ne', indicatoron=0, bg='red', variable=bVar
    )
    btn1.pack(side=tk.LEFT)
    motherFrame = collapsingFrame(root, tk.VERTICAL, inisplit=0.3, buttconf='RM')
    motherFrame.config(height=200, width=200)
    motherFrame.pack(side=tk.TOP, fill=tk.BOTH, expand=tk.YES)
    btn = tk.Button(motherFrame.frstWidget, text='Show', bg='blue', command=lambda: btn1.deselect())
    btn.pack(side=tk.TOP, anchor='ne')

    labels = []
    for k in range(5):
        label = tk.Label(motherFrame.frstWidget, text='Panel IZQUIERDO No. %s\nEl boton solo presenta o oculta el panel' % (k+1))
        labels.append(label)
    labels[leftPane - 1].pack(side=tk.TOP, fill=tk.BOTH, expand=tk.YES)
    test = collapsingFrame(motherFrame.scndWidget, tk.HORIZONTAL)
    test.pack(side=tk.TOP, fill=tk.BOTH, expand=tk.YES)
    tk.Button(test.frstWidget, text='Panel de ARRIBA').pack(side=tk.TOP, fill=tk.BOTH, expand=tk.YES)
    for k in range(5):
        button = tk.Button(test.scndWidget, command=lambda x=k+1:leftPaneChg(x), text='Frame No. ' + str(k + 1))
        button.pack(side=tk.TOP, fill=tk.BOTH, expand=tk.YES)
    pass
    root.mainloop()