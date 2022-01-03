import tkinter as tk

if __name__ == '__main__':
    import ImageProcessor
else:
    from . import ImageProcessor

BAND_WIDTH = 16

class collapsingFrame(tk.Frame):
    def __init__(self, master, orientation=tk.HORIZONTAL, inisplit=0.8, buttconf='RMm', **kwargs):
        tk.Frame.__init__(self, master, **kwargs)
        self.buttIcon = {}
        self.buttIcon['M'] = ImageProcessor.getIconImageTk(ImageProcessor.WINDOW_MAX)
        self.buttIcon['m'] = ImageProcessor.getIconImageTk(ImageProcessor.WINDOW_MIN)
        self.buttIcon['R'] = ImageProcessor.getIconImageTk(ImageProcessor.WINDOW_RESTORE)

        self.bind('<Configure>', self.cframe_configure, add='+')
        self.bandRelDim = 0
        self.frstWidget = tk.Frame(self, name='frstwidget', bg='blue')
        self.scndWidget = tk.Frame(self, name='scndwidget', bg='green')
        self.band = None

        self.configure(orientation=orientation, inisplit=inisplit, buttconf=buttconf)
        pass

    def configure(self, **genkwargs):
        if not genkwargs:
            cnfParams = super().configure()
            cnfParams["orientation"] = ("orientation", "orientation", None, "horizontal", self.orientation)
            cnfParams["inisplit"] = ("inisplit", "inisplit", None, "0.8", str(self.split))
            cnfParams["buttconf"] = ("buttconf", "buttconf", None, "RMm", self.buttConf)
            return cnfParams
        #Se filtran los parametros
        kwargs = {
            key: genkwargs.pop(key)
            for key in ('orientation', 'inisplit', 'buttconf')
            if key in genkwargs
        }
        super().configure(**genkwargs)
        orientation = kwargs.get("orientation", 'horizontal')
        if orientation in [tk.VERTICAL, tk.HORIZONTAL]:
            self.orientation = orientation
        else:
            raise AttributeError('%s is not a valid orientation' % orientation)
        self.cursor = 'sb_v_double_arrow' if orientation == tk.HORIZONTAL else 'sb_h_double_arrow'
        self.dim = 'height' if orientation == tk.HORIZONTAL else 'width'
        self.buttConf = kwargs.get('buttconf', 'RMm')
        self.split = float(kwargs.get('inisplit', '0.8'))
        self.setGUI()
        self.setWidgetLayout(self.buttConf[0])
        pass

    config = configure

    def clickButton(self, nButt=1):
        nButt = max(1, min(len(self.buttConf) - 1, nButt))
        boton = getattr(self, 'b' + str(nButt))
        btTxt = boton.cget('text')
        self.comButton(btTxt)

    def setWidgetLayout(self, btnTxt):
        if btnTxt == 'M': return self.wmax()
        if btnTxt == 'm': return self.wmin()
        self.wdef()
        
    def cframe_configure(self, event):
        totDim = event.height if self.orientation == tk.HORIZONTAL else event.width
        self.bandRelDim = float((1.0*BAND_WIDTH)/totDim)
        btnTxt = self.nxtButton()
        self.setWidgetLayout(btnTxt)

    def nxtButton(self):
        buttons = [getattr(self, 'b' + str(k+1)) for k in range(len(self.buttConf)-1)]
        return set(self.buttConf).difference(map(lambda x: x['text'][1], buttons)).pop()
        
    def setGUI(self):
        master = self
        if self.band:
            self.band.destroy()
            for k in range(3):
                try:
                    btn = getattr(self, 'b' + str(k + 1))
                    btn.destroy()
                    del btn
                except AttributeError:
                    pass
        self.band = tk.Frame(master, bg='red', cursor=self.cursor)
        self.band[self.dim] = BAND_WIDTH
        self.band.bind('<ButtonPress-1>', self.b1pressh)
        self.band.bind('<Button1-Motion>', self.b1motion)
        self.band.bind('<ButtonRelease-1>', self.b1releaseh)
        for k, btnTxt in enumerate(self.buttConf[1:]):
            buttLabel = str(k+1) + btnTxt
            setattr(self, 'b' + str(k+1), tk.Button(master, bg ='red', text=buttLabel, image=self.buttIcon[btnTxt], command = lambda x = buttLabel:self.comButton(x)))
        
    def comButton(self, btTxt):
        nBtn, btId = btTxt
        self.setWidgetLayout(btId)
        btnTxt = self.nxtButton()        
        boton = getattr(self, 'b' + nBtn)
        boton['text'] = nBtn + btnTxt
        boton['image'] = self.buttIcon[btnTxt]
        boton['command'] = lambda:self.comButton(boton['text'])

    def trn(self, **kwargs):
        if self.orientation == tk.HORIZONTAL:
            return kwargs
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
            else: newK = k
            answer[newK] = kwargs[k]
        return answer
        
    def wdef(self):
        splitComp = 1 - self.split - self.bandRelDim
        trn = self.trn
        self.frstWidget.place(
            **trn(relheight=self.split, relwidth=1.0)
        )
        self.placeSepBand()
        self.scndWidget.place(
            **trn(rely=self.split, y=BAND_WIDTH, relheight= splitComp, relwidth=1.0)
        )
        self.band['cursor'] = self.cursor
        
    def placeSepBand(self, kwargs = None):
        kwargs = kwargs or {}
        trn = self.trn
        placeInfo = trn(rely = self.split, y = 0, relwidth = 1.0)
        placeInfo.update(kwargs)
        self.band.place(**placeInfo)
        for k in range(len(self.buttConf)-1):
            widget = getattr(self,'b' + str(k+1))
            placeInfo = trn(rely = self.split, relx = 1.0, y = 0, x = -(k+1)*BAND_WIDTH, height = BAND_WIDTH, width = BAND_WIDTH)
            if self.orientation == tk.VERTICAL: 
                placeInfo['rely'] = 0
                placeInfo['y'] = -(placeInfo['y'] + BAND_WIDTH)
            if kwargs: placeInfo.update(kwargs)
            widget.place(**placeInfo)
            
    def wmax(self):
        self.frstWidget.place_forget()
        self.scndWidget.place(**self.trn(rely = 0, y = BAND_WIDTH, relheight = 1.0 - self.bandRelDim, relwidth = 1.0))
        kwargs = self.trn(rely = 0, y = 0)
        self.placeSepBand(kwargs)
        self.band['cursor'] = 'arrow'
        
    def wmin(self):
        self.scndWidget.place_forget()
        self.frstWidget.place(**self.trn(rely = 0, relheight = 1 - self.bandRelDim, relwidth = 1.0))
        kwargs = self.trn(rely = 1.0, y = -BAND_WIDTH)
        self.placeSepBand(kwargs)
        self.band['cursor'] = 'arrow'

    def b1pressh(self, event):
        if 'R' != self.nxtButton(): return
        self.mband = tk.Frame(self, bg = 'grey', cursor = self.cursor)
        self.mband[self.dim] = BAND_WIDTH
        kwargs = self.trn(rely = self.split, relwidth = 1.0)  
        self.mband.place(**kwargs)

    def b1motion(self, event):
        if 'R' != self.nxtButton(): return
        mwidth = self.master.winfo_height() if self.orientation == tk.HORIZONTAL else self.master.winfo_width()
        mmin = 0
        mmax = 1 - self.bandRelDim
        pos = event.y if self.orientation == tk.HORIZONTAL else event.x
        puPos = float((self.split*mwidth + pos)/mwidth)
        pixels = min(mmax,max(mmin,puPos))
        self.mband.place(**self.trn(rely = pixels))

    def b1releaseh(self, event):
        if 'R' != self.nxtButton(): return
        if self.orientation == tk.HORIZONTAL:
            mwidth = self.master.winfo_height()
            pos = event.y
        else:
            mwidth = self.master.winfo_width()
            pos = event.x
        split = (float(self.split * mwidth) + pos)/float(mwidth)
        self.split = max(0.0, min(1.0 - float(BAND_WIDTH)/float(mwidth), split))
        self.mband.place_forget()
        self.wdef()
        pass

if __name__ == '__main__':
    leftPane = 3
    def leftPaneChg(pane):
        global leftPane
        labels[leftPane - 1].pack_forget()
        labels[pane - 1].pack(side = tk.TOP, fill = tk.BOTH, expand = tk.YES)
        leftPane = pane
    root = tk.Tk()
    motherFrame = collapsingFrame(root, tk.VERTICAL, inisplit = 0.3,buttconf = 'RM')
    motherFrame.config(height=200, width=200)
    motherFrame.pack(side = tk.TOP, fill = tk.BOTH, expand = tk.YES)
    labels = []
    for k in range(5):
        label = tk.Label(motherFrame.frstWidget, text = 'Panel IZQUIERDO No. %s\nEl boton solo presenta o oculta el panel' % (k+1))
        labels.append(label)
    labels[leftPane - 1].pack(side = tk.TOP, fill = tk.BOTH, expand = tk.YES)
    test = collapsingFrame(motherFrame.scndWidget, tk.HORIZONTAL)
    test.pack(side = tk.TOP, fill = tk.BOTH, expand = tk.YES)
    tk.Button(test.frstWidget, text = 'Panel de ARRIBA').pack(side = tk.TOP, fill = tk.BOTH, expand = tk.YES)
    for k in range(5):
        button = tk.Button(test.scndWidget, command=lambda x=k+1:leftPaneChg(x), text = 'Frame No. ' + str(k + 1))
        button.pack(side = tk.TOP, fill = tk.BOTH, expand = tk.YES)
    pass
    root.mainloop()