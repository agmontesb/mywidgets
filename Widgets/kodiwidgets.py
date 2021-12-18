# -*- coding: utf-8 -*-
'''
Created on 18/09/2014

@author: Alex Montes Barrios
'''

import tkinter as tk
import re
import tkinter.simpledialog as tkSimpleDialog
import tkinter.filedialog as tkFileDialog
from tkinter import ttk
import os
import fnmatch
import operator

from userinterface import formFrameGen


def getWidgetClass(widgetName):
    widgetTypes = dict(sep=settSep, lsep=settSep,
                       text=settText,
                       label=settLabel,
                       optionlst=settOptionList,
                       number=settNumber, ipaddress=settNumber,
                       slider=settSlider,
                       bool=settBool,
                       enum=settEnum, labelenum=settEnum,
                       drpdwnlst=settDDList,
                       file=settFile, audio=settFile, video=settFile, image=settFile, executable=settFile,
                       folder=settFolder,
                       fileenum=settFileenum,
                       action=settAction,
                       container=settContainer,
                       fragment=settFragment, )
    return widgetTypes.get(widgetName, None)


class baseWidget(tk.Frame, object):
    '''
    Clase que define el widget básico como un tk.Frame
    '''
    def __new__(cls, *args, **options):
        # instance = super(baseWidget, cls).__new__(cls, *args, **options)
        instance = super(baseWidget, cls).__new__(cls)
        return instance

    def __init__(self, master, **options):
        '''
        Inicialización del instance.
        :param master: tkinter Frame. Padre del widget.
        :param options: dict. kwargs válidos para la definición de un tkinter Frame, además
                        de los cuales acepta "id", "name", "varType"
        '''
        wdgName = options.get('name', '').lower()
        self._id = options.pop('id', wdgName)       # Atributo _id = 'id' propio.
        # self.id = options.get('id').lower() if options.get('id') else None # Atributo id definido por el usuario

        if 'varType' in options:                    # Atributo: value.
            self.setVarType(options.pop('varType'))
        self.default = None                         # Atributo: default.
        self.listener = None                        # Atributo: Callback function asociado
                                                    # al cambio del valor asociado al widget.
        if not issubclass(self.__class__, settContainer):
            baseConf = dict(bd=1, highlightbackground='dark grey', highlightthickness=2,
                            highlightcolor='green', takefocus=1)
            baseConf.update(options)
            if wdgName:
                baseConf['name'] = wdgName
        else:
            baseConf = dict(name=self._id)
            if options.get('bg'):
                baseConf['bg'] = options['bg']
        tk.Frame.__init__(self, master, **baseConf)
        # Se definen dos atributos:
        # path = Camino que resulta de concatenar los nombres de los Frame que contienen
        #        este baseWidget
        # form = Tkinter Form que es el padre de este baseWidget
        if issubclass(master.__class__, settContainer):
            self.path = master.path + '.' + baseConf.get('name', '')
            self.form = master.form
            master.applyGeoManager(self)
        else:
            self.path = baseConf.get('name', '')
            self.form = master.form if hasattr(master, 'form') else master
            self.pack(side=tk.TOP, fill=tk.BOTH, expand=tk.YES, ipadx=2, ipady=2, padx=1, pady=1)

    def setVarType(self, varType='string'):
        '''
        Tipo de valor asociado con el widget.
        :param varType: str. Tipo de variable, puede ser uno de estas:
                        ['str', 'int', 'double', 'boolean'], cualquier
                        otro valor se asimila a 'str'.
        :return: None.
        '''
        if varType == 'int':
            self.value = tk.IntVar()
        elif varType == 'double':
            self.value = tk.DoubleVar()
        elif varType == 'boolean':
            self.value = tk.BooleanVar()
        else:
            self.value = tk.StringVar()

    def getSettingPair(self, tId=False):
        '''
        :param tId: boolean. Utilizar id propio (_id) o el id asignado por tkinter.
        :return: tuple. "id" y valor asociado al widget.
        '''
        id = self._id if tId else self.id
        return (id, self.getValue())

    def isValueSetToDefault(self):
        '''
        Verifica si el valor actual asociado al qidget corrresponde al default definido en el
        archivo de layout.
        :return: boolean. True, si value = default. False, si value != default.
        '''
        return self.getValue() == self.default

    def setValue(self, value):
        '''
        Cambia el valor del widget.
        :param value: obj. Puede ser str, int, double, boolean
        :return: None.
        '''
        self.value.set(value)

    def getValue(self):
        '''
        Entrega el valor actual del widget.
        :return: obj. Puede ser str, int, double, boolean.
        '''
        return self.value.get()

    def getConfig(self, option):
        '''

        :param option: str.
        :return: obj.
        '''
        return self.children[self.id].cget(option)

    def setConfig(self, **options):
        '''

        :param options: dict.
        :return: None
        '''
        self.children[self.id].configure(**options)

    def setListener(self, function):
        '''
        Establece la callback function a ejecutar cuando cambia el valor asociado al widget.
        :param function: callable. Esta función debe aceptar como variable de entrada el nombre
                         del widget.
        :return: None
        '''
        self.listener = function
        self.value.trace_add("w", self.callListener)

    def callListener(self, *args):
        '''
        Callback function que e llama caundo cambia el valor asociado al widget.
        :param args: list. No se utiliza.
        :return: None
        '''
        self.listener(self.name)

    def getDroidInstance(self):
        '''
        Entrega ??????
        :return: None or droidInstance.
        '''
        try:
            parentname = re.match(r'(\.0x[0-9a-f]+)\.?', str(self.master))
            basic_frame = self.master.nametowidget(parentname.group(1))
        except:
            return
        return basic_frame.droidInstance


class settLabel(baseWidget):
    def __init__(self, master, **options):
        wdgName = options.get('name').lower()
        baseWidget.__init__(self, master, varType='string', name=wdgName, id=options.get('id', ''))
        self.setGUI(options)
        self.name = wdgName

    def setGUI(self, options):
        ttk.Label(self, text=options.get('label'), width=20, anchor=tk.NW).pack(side=tk.LEFT, fill=tk.X, expand=1)


class settFileenum(baseWidget):
    def __init__(self, master, **options):
        wdgName = options.get('name').lower()
        baseWidget.__init__(self, master, varType='string', name=wdgName, id=options.get('id', ''))
        self.setGUI(options)
        self.name = wdgName

    def setGUI(self, options):
        ttk.Label(self, text=options.get('label'), width=20, anchor=tk.NW).pack(side=tk.LEFT)
        if options.get('id'):
            self.id = options.get('id').lower()
        self.default = options.get('default', '')
        self.setValue(self.default)
        spBoxValues = self.getFileList(options)
        tk.Spinbox(self, name=self.id, textvariable=self.value, values=spBoxValues).pack(side=tk.RIGHT, fill=tk.X,
                                                                                         expand=1)

    def getFileList(self, options):
        basepath = os.path.abspath('..')
        values = options.get('values', '')
        mypath = os.path.join(basepath, values)
        if not os.path.exists(mypath):
            return
        dirpath, dirnames, filenames = next(os.walk(mypath))
        if options.get('mask', None) == '/':
            return dirnames
        else:
            mask = options.get('mask', None)
            filenames = [elem for elem in filenames if fnmatch.fnmatch(elem, mask)]
            if options.get('hideext', 'true') == 'true':
                filenames = [elem.split('.')[0] for elem in filenames]
            return filenames


class settFolder(baseWidget):
    def __init__(self, master, **options):
        wdgName = options.get('name').lower()
        baseWidget.__init__(self, master, varType='string', name=wdgName, id=options.get('id', ''))
        self.setGUI(options)
        self.name = wdgName

    def setGUI(self, options):
        ttk.Label(self, text=options.get('label'), width=20, anchor=tk.NW).pack(side=tk.LEFT)
        if options.get('id'): self.id = options.get('id').lower()
        self.default = options.get('default', '')
        self.setValue(self.default)
        ttk.Button(self, name=self.id, textvariable=self.value, command=self.getFolder).pack(side=tk.RIGHT, fill=tk.X,
                                                                                            expand=1)

    def getFolder(self):
        folder = tkFileDialog.askdirectory()
        if folder:
            self.value.set(folder)


class settFile(baseWidget):
    def __init__(self, master, **options):
        wdgName = options.get('name').lower()
        baseWidget.__init__(self, master, varType='string', name=wdgName, id=options.get('id', ''))
        self.setGUI(options)
        self.name = wdgName

    def setGUI(self, options):
        ttk.Label(self, text=options.get('label'), width=20, anchor=tk.NW).pack(side=tk.LEFT)
        if options.get('id'): self.id = options.get('id').lower()
        self.default = options.get('default', '')
        self.setValue(self.default)
        ttk.Button(self, name=self.id, #anchor='e',
                   textvariable=self.value, command=self.getFile).pack(side=tk.RIGHT,
                                                                                                      fill=tk.X,
                                                                                                      expand=1)

    def getFile(self):
        fileName = tkFileDialog.askopenfilename()
        if fileName:
            self.value.set(fileName)


class settDDList(baseWidget):
    def __init__(self, master, **options):
        wdgName = options.get('name').lower()
        baseWidget.__init__(self, master, varType='string', name=wdgName, id=options.get('id', ''))
        self.setGUI(options)
        self.name = wdgName

    def setGUI(self, options):
        ttk.Label(self, text=options.get('label'), width=20, anchor=tk.NW).pack(side=tk.LEFT)
        if options.get('id'): self.id = options.get('id').lower()
        self.default = options.get('default', '')
        self.spBoxValues = options.get('values').split('|')
        self.lvalues = spBoxValues = options.get('lvalues').split('|')
        tk.Spinbox(self, name=self.id, command=self.onChangeSel, textvariable=self.value, values=spBoxValues).pack(
            side=tk.RIGHT, fill=tk.X, expand=1)
        self.setValue(self.default)

    def setValue(self, value):
        try:
            ndx = self.spBoxValues.index(value)
        except:
            return
        self.value.set(self.lvalues[ndx])

    def getValue(self):
        try:
            ndx = self.lvalues.index(self.value.get())
        except:
            return
        return self.spBoxValues[ndx]

    def onChangeSel(self):
        try:
            self.form.onChangeSelEvent(self._id)
        except:
            pass


class settEnum(baseWidget):
    def __init__(self, master, **options):
        wdgName = options.get('name').lower()
        baseWidget.__init__(self, master, varType='string', name=wdgName, id=options.get('id', ''))
        self.setGUI(options)
        self.name = wdgName

    def setGUI(self, options):
        ttk.Label(self, text=options.get('label'), width=20, anchor=tk.NW).pack(side=tk.LEFT)
        if options.get('id'): self.id = options.get('id').lower()
        self.default = options.get('default', '')
        if 'values' in options:
            spBoxValues = options.get('values').split('|')
        else:
            spBoxValues = options.get('lvalues').split('|')
        tk.Spinbox(self, name=self.id, textvariable=self.value, values=spBoxValues).pack(side=tk.RIGHT, fill=tk.X,
                                                                                         expand=1)
        self.setValue(self.default)

    def setValue(self, value):
        nPos = value.find('|')
        self.withValues = withValues = nPos != -1
        if withValues:
            spBoxValue = value[nPos + 1:].split('|')
            self.children[self.id].configure(values=spBoxValue)
            value = value[:nPos]
        self.value.set(value)

    def getValue(self, onlyValue=False):
        onlyValue = onlyValue or not self.withValues
        if onlyValue: return self.value.get()
        return '|'.join([self.value.get()] + self.children[self.id].cget('values').split(' '))

    def getSettingPair(self, tId=False):
        id = self._id if tId else self.id
        return (id, self.getValue(tId))


class CustomDialog(tkSimpleDialog.Dialog):
    def __init__(self, master, title=None, xmlFile=None, isFile=False, settings=None):
        # import xmlFileWrapper
        self.allSettings = None
        self.settings = settings = settings or {}
        # self.ads = xmlFileWrapper.xmlFileWrapper(xmlFile, isFile=isFile, nonDefaultValues=settings)
        self.ads = xmlFile
        tkSimpleDialog.Dialog.__init__(self, master, title)

    def body(self, master):
        '''create dialog body.

        return widget that should have initial focus.
        This method should be overridden, and is called
        by the __init__ method.
        '''
        # selPanel = self.ads.getActivePane()
        self.form = form = formFrameGen(master, settings={}, selPane=self.ads)
        form.pack(side=tk.TOP, fill=tk.BOTH, expand=tk.YES)
        wdgId = sorted(form.nameToId.keys(), key=int)[0]
        wdgId = form.nameToId[wdgId]
        widget = getattr(self.form, wdgId)
        return widget

    def buttonbox(self):
        '''add standard button box.

        override if you do not want the standard buttons
        '''

        box = tk.Frame(self)

        w = ttk.Button(box, text="OK", width=10, command=self.ok, default=tk.ACTIVE)
        w.pack(side=tk.LEFT, padx=5, pady=5)
        w = ttk.Button(box, text="Cancel", width=10, command=self.cancel)
        w.pack(side=tk.LEFT, padx=5, pady=5)

        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.cancel)

        box.pack()

    def ok(self, event=None):
        settings = self.settings
        changedSettings = self.form.getChangeSettings(settings)
        reset = changedSettings.pop('reset')
        for key in reset: settings.pop(key)
        settings.update(changedSettings)
        self.result = dict(settings)
        allwidgets = self.form.getWidgets()
        allwidgets.sort(key=operator.attrgetter('id'))
        allSettings = [widget.getSettingPair(tId=True) for widget in allwidgets]

        self.allSettings = allSettings
        self.cancel()
        pass

    def geometry(self, posStr):
        width, height = 290, 220
        posx = (self.winfo_screenwidth() - width) / 2
        posy = (self.winfo_screenheight() - height) / 2
        posStr = "+%d+%d" % (posx, posy)
        tkSimpleDialog.Dialog.geometry(self, posStr)


class settOptionList(baseWidget):
    def __init__(self, master, **options):
        wdgName = options.get('name').lower()
        self.isTree = options.get('tree', 'false') == 'true'
        baseWidget.__init__(self, master, varType='string', name=wdgName, id=options.get('id', ''))
        self.setGUI(options)
        self.name = wdgName

    def setGUI(self, options):
        settSep(self, name='label', type='lsep', label=options.get('label'))

        if options.get('id'): self.id = options.get('id').lower().replace('.', '__')
        self.default = options.get('default', '')

        uFrame = tk.Frame(self)
        uFrame.pack(side=tk.TOP, fill=tk.BOTH)

        sbar = ttk.Scrollbar(uFrame)
        sbar.pack(side=tk.RIGHT, fill=tk.Y)

        colHeadings = options.get('columnsheadings')
        dshow = 'headings'
        columnsId = dcolumns = list(map(lambda x: x.strip(), colHeadings.split(',')))
        if self.isTree:
            dshow = 'tree ' + dshow
            dcolumns = '#all'
        tree = ttk.Treeview(uFrame, show=dshow, columns=columnsId, displaycolumns=dcolumns)
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        sbar.config(command=tree.yview)  # xlink sbar and tree
        tree.config(yscrollcommand=sbar.set)  # move one moves other
        for column in columnsId:
            tree.heading(column, text=column, anchor=tk.W)
        self.tree = tree
        self.columnsId = columnsId

        bFrame = tk.Frame(self)
        bFrame.pack(side=tk.BOTTOM, fill=tk.X)
        boton = ttk.Button(bFrame, text='Add', width=15, command=self.onAdd)
        boton.pack(side=tk.LEFT)
        boton = ttk.Button(bFrame, text='Edit', width=15, command=self.onEdit)
        boton.pack(side=tk.LEFT)
        boton = ttk.Button(bFrame, text='Del', width=15, command=self.onDel)
        boton.pack(side=tk.RIGHT)

        self.setValue(self.default)

    def xmlDlgWindow(self, tupleSett, isEdit=False, isTree=False):
        header = """<?xml version="1.0" encoding="utf-8" standalone="yes"?>
<settings>
    <category label="TCombobox">
"""
        footer = """    </category>
</settings>
"""
        outStr = header
        if not isEdit and isTree:
            deltaStr = '<text id="{0}" label="Parent Element" default="{1}" enable="false"/>\n'
            outStr += 8 * ' ' + deltaStr.format(*tupleSett[0])
            deltaStr = '<text id="{0}" label="Element Name" default="{1}" />\n'
            outStr += 8 * ' ' + deltaStr.format(*tupleSett[1])
            tupleSett = tupleSett[2:]

        templateStr = '<text id="{0}" label="{0}" default=""/>\n'
        if isEdit:
            templateStr = '<text id="{0}" label="{0}" default="{1}"/>\n'
        for x, y in tupleSett:
            deltaStr = templateStr.format(x, y)
            outStr += 8 * ' ' + deltaStr
        outStr += footer
        return outStr

    def onAdd(self):
        parent = self.tree.focus()
        pair = [(col, col) for col in self.columnsId]
        if self.isTree:
            pair = [('parent', self.tree.item(parent, 'text')), ('text', '')] + pair
        xmlDlg = self.xmlDlgWindow(pair, isEdit=False, isTree=self.isTree)
        dlg = CustomDialog(self, title='Add', xmlFile=xmlDlg, isFile=False)
        if dlg.allSettings:
            result = dict(dlg.allSettings)
            columnsId = self.columnsId
            if self.isTree:
                columnsId = ['text'] + columnsId
            record = [result[col].strip() for col in columnsId]
            parent, iid, text = parent, None, ''
            if self.isTree:
                text = record[0]
                record = record[1:]
            self.tree.insert(parent, 'end', iid=iid, text=text, values=record, open=True)

    def onEdit(self):
        iid = self.tree.focus()
        if not iid:
            return
        value = self.tree.set
        columnsId = self.columnsId
        pair = [(col, value(iid, col)) for col in columnsId]
        xmlDlg = self.xmlDlgWindow(pair, isEdit=True)
        dlg = CustomDialog(self, title='Edit', xmlFile=xmlDlg, isFile=False)
        if dlg.allSettings:
            result = dict(dlg.allSettings)
            record = [result[col].strip() for col in columnsId]
            for k, col in enumerate(columnsId):
                self.tree.set(iid, col, record[k])
                self.event_generate('<<OL_Edit>>', when='tail', data=f"{iid} {col} {record[k]}")

    def onDel(self):
        iid = self.tree.focus()
        if iid: self.tree.delete(iid)

    def setValue(self, value, sep=('|', ',')):
        seprow, sepcol = sep
        lista = self.tree.get_children('')
        self.tree.delete(*lista)
        if value == '': return
        maxCol = len(self.columnsId) - 1
        if self.isTree:
            maxCol += 3
        bDatos = [
            list(map(lambda x: x.strip(), record.split(sepcol, maxCol)))
            for record in value.split(seprow)
        ]
        parent, iid, text = '', None, ''
        for record in bDatos:
            if self.isTree:
                parent, iid, text = record[:3]
                record = record[3:]
            self.tree.insert(parent, 'end', iid=iid, text=text, values=record, open=True)

    def getValue(self):
        stack = list(self.tree.get_children('')[::-1])
        bDatos = []
        while stack:
            iid = stack.pop()
            iidValues = []
            if self.isTree:
                iidValues = [self.tree.parent(iid), iid, self.tree.item(iid, 'text')]
            iidValues = iidValues + list(self.tree.item(iid, 'values'))
            iidValStr = ','.join(iidValues)
            bDatos.append(iidValStr)
            children = self.tree.get_children(iid)
            if children:
                stack.extend(list(children)[::-1])
        return '|'.join(bDatos)


class settSlider(baseWidget):
    def __init__(self, master, **options):
        wdgName = options.get('name').lower()
        baseWidget.__init__(self, master, varType='string', name=wdgName, id=options.get('id', ''))
        self.setGUI(options)
        self.name = wdgName

    def setGUI(self, options):
        ttk.Label(self, text=options.get('label'), width=20, anchor=tk.NW).pack(side=tk.LEFT)
        if options.get('id'): self.id = options.get('id').lower()
        self.default = options.get('default', '')
        self.setValue(self.default)
        valRange = list(map(int, options.get('range').split(',')))
        scale = ttk.Scale(self, variable=self.value, #showvalue=0,
                           from_=valRange[0], to=valRange[-1])
                         #orient=tk.HORIZONTAL
        scale.pack(side=tk.RIGHT, fill=tk.X, expand=1)
        if len(valRange) == 3: scale.configure(resolution=valRange[1])
        ttk.Entry(self, textvariable=self.value).pack(side=tk.RIGHT, fill=tk.X)


class settNumber(baseWidget):
    def __init__(self, master, **options):
        wdgName = options.get('name').lower()
        baseWidget.__init__(self, master, varType='string', name=wdgName, id=options.get('id', ''))
        self.setGUI(options)
        self.name = wdgName

    def setGUI(self, options):
        ttk.Label(self, text=options.get('label'), width=20, anchor=tk.NW).pack(side=tk.LEFT)
        if options.get('id'): self.id = options.get('id').lower()
        self.default = options.get('default', '')
        # valid percent substitutions (from the Tk entry man page)
        # %d = Type of action (1=insert, 0=delete, -1 for others)
        # %i = index of char string to be inserted/deleted, or -1
        # %P = value of the entry if the edit is allowed
        # %s = value of entry prior to editing
        # %S = the text string being inserted or deleted, if any
        # %v = the type of validation that is currently set
        # %V = the type of validation that triggered the callback
        #      (key, focusin, focusout, forced)
        # %W = the tk name of the widget
        func = self.validateNumber
        vcmd = (self.register(func),
                '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        self.entry = entry = tk.Entry(self, name=self.id, textvariable=self.value, validate='key', validatecommand=vcmd)
        entry.pack(side=tk.RIGHT, fill=tk.X, expand=1)
        self.setValue(self.default)

    def validateNumber(self, d, i, P, s, S, v, V, W):
        return S.isdigit()

    def setValue(self, value):
        self.entry.delete(0, tk.END)
        self.entry.insert(0, value)
        pass


class settText(baseWidget):
    def __init__(self, master, **options):
        wdgName = options.get('name').lower()
        self.name = wdgName
        baseWidget.__init__(self, master, name=wdgName, id=options.get('id', ''))
        self.setGUI(options)

    def setGUI(self, options):
        ttk.Label(self, name='textlbl', text=options.get('label'),
                 width=20, anchor=tk.NW).pack(side=tk.LEFT)
        self.value = tk.StringVar()
        self.default = options.get('default', '')
        self.setValue(self.default)
        if options.get('id'):
            self.id = options.get('id').lower().replace('.', '__')
            ttk.Entry(self, name=self.id, textvariable=self.value).pack(side=tk.RIGHT, fill=tk.X, expand=1)
        else:
            ttk.Label(self, textvariable=self.value).pack(side=tk.RIGHT, fill=tk.X, expand=1)

    def setValue(self, value):
        if value == None:
            self.value.set('')
        else:
            self.value.set(value)

    def getValue(self):
        return self.value.get() if self.value.get() != '' else ''


class settBool(baseWidget):
    def __init__(self, master, **options):
        wdgName = options.get('name', '').lower()
        baseWidget.__init__(self, master, name=wdgName, id=options.get('id', ''))
        if 'group' in options:
            groupName = options['group']
            self.value = self.form.getGroupVar(groupName)
        else:
            self.setVarType('boolean')
        self.setGUI(options)
        self.name = wdgName

    def setGUI(self, options):
        self.id = id = options.get('id', '').lower()
        self.default = options.get('default') == 'true'
        if 'group' in options:
            value_on = id
            if self.default: self.setValue(id)
        else:
            value_on = True
            self.setValue(self.default)
        chkbtn = ttk.Checkbutton(self, name=self.id, variable=self.value,
                                onvalue=value_on,
                                command=self.onClick)
        chkbtn.pack(side = tk.RIGHT)
        ttk.Label(self, name="boollbl", text=options.get('label'), width=20, anchor=tk.NW)\
            .pack(side = tk.LEFT, fill=tk.X, expand=tk.YES)

    def isValueSetToDefault(self):
        return self.getValue() == self.default

    def setValue(self, value):
        self.value.set(value)

    def getValue(self):
        value = self.value.get()
        if isinstance(value, str):
            value = (value == self.id)
        return value

    def onClick(self):
        try:
            self.form.onClickEvent(self._id)
        except:
            pass


class settAction(baseWidget):
    def __init__(self, master, **options):
        wdgName = options.get('name', '').lower()
        baseWidget.__init__(self, master, name=wdgName, id=options.get('id', ''))
        self.setGUI(options)
        self.name = wdgName

    def setGUI(self, options):
        if options.get('id'):
            self.id = options.get('id').lower()
        self.value = options.get('default')
        ttk.Button(self, name=self.id, text=options.get('label'), command=self.onClick).pack(side=tk.RIGHT, fill=tk.X,
                                                                                            expand=1)

    def onClick(self):
        try:
            self.form.onClickEvent(self._id)
        except:
            pass

    def isValueSetToDefault(self):
        return True

    def setValue(self, value):
        pass

    def getValue(self):
        return None

    def setListener(self, function):
        pass

    def callListener(self, *args):
        pass


class settSep(baseWidget):
    def __init__(self, master, **options):
        wdgName = options.get('name').lower().lower()
        baseWidget.__init__(self, master, name=wdgName)
        self.setGUI(options)
        self.name = wdgName

    def setGUI(self, options):
        if options.get('type', None) == 'lsep': ttk.Label(self, text=options.get('label')).pack(side=tk.LEFT)
        if not 'noline' in options:
            color = options.get('color', 'red')
            tk.Frame(self, relief=tk.RIDGE, height=2, bg=color).pack(side=tk.RIGHT, fill=tk.X, expand=1)

    def getSettingPair(self):
        return (None, None)

    def isValueSetToDefault(self):
        return True

    def setValue(self, value):
        pass

    def getValue(self):
        return None

    def setListener(self, function):
        pass


class settContainer(baseWidget):
    def __init__(self, master, **options):
        keys = set(('side', 'label', 'scrolled', 'type')).intersection(options)
        contoptions = {key: options.pop(key) for key in keys}
        packSide = contoptions.get('side', 'top')
        self.side = dict(top=tk.TOP, bottom=tk.BOTTOM, left=tk.LEFT, right=tk.RIGHT).get(packSide, tk.TOP)
        wdgName = options.get('name', '').lower().replace('.', '_')
        id = options.get('id', wdgName).lower()
        if id != wdgName:
            self.id = id
        baseWidget.__init__(self, master, **options)
        self.name = wdgName

        self.innerframe = self
        if 'label' in contoptions:
            outerframe = tk.LabelFrame(self, text=contoptions.get('label'))
            outerframe.pack(side=tk.TOP, fill=tk.BOTH, expand=tk.YES)
            if contoptions.get('scrolled', 'false') == 'false':
                self.innerframe = innerframe = settContainer(self, name="innerframe",
                                                                side=self.side)
                innerframe.pack(in_=outerframe, side=tk.TOP, fill=tk.BOTH, expand=tk.YES)
        else:
            outerframe = tk.Frame(self)
            outerframe.pack(side=tk.TOP, fill=tk.BOTH, expand=tk.YES)

        if contoptions.get('scrolled', 'false') == 'true':
            outerframe.grid_columnconfigure(0, weight=1)
            outerframe.grid_columnconfigure(1, weight=0)
            outerframe.grid_rowconfigure(0, weight=1)

            self.vsb = tk.Scrollbar(outerframe, orient="vertical", )
            self.vsb.grid(row=0, column=1, sticky=tk.NS)

            self.canvas = tk.Canvas(outerframe, name="canvas", borderwidth=0)
            self.canvas.grid(row=0, column=0, sticky=tk.NSEW)

            self.canvas.configure(yscrollcommand=self.vsb.set)
            self.vsb.configure(command=self.canvas.yview)

            self.canvas.xview_moveto(0)
            self.canvas.yview_moveto(0)

            self.innerframe = innerframe = settContainer(self, name="innerframe",
                                                            side=self.side)
            innerframe.pack_forget()
            self.innerframeId = self.canvas.create_window((0, 0),
                                                          window=innerframe,
                                                          anchor="nw",
                                                          tags="innerframe")


            self.canvas.bind("<Configure>", self._OnCanvasConfigure)
            self.innerframe.bind("<Configure>", self._OnInnerFrameConfigure)

    # def _OnCanvasConfigure(self, event):
    #     canvas = event.widget
    #     canvas.itemconfig(self.innerframeId, width=event.width)
    #
    # def _OnInnerFrameConfigure(self, event):
    #     height = event.height
    #     width = event.width
    #     if height <= self.canvas.winfo_reqheight():
    #         self.vsb.grid_forget()
    #     else:
    #         self.vsb.grid(row=0, column=1, sticky=tk.NS)
    #     self.canvas.config(scrollregion=(0, 0, width, height))

    def _OnCanvasConfigure(self, event):
        if self.innerframe.winfo_reqheight() <= self.canvas.winfo_height():
            self.vsb.grid_remove()
        else:
            self.vsb.grid()

        if self.innerframe.winfo_reqwidth() != self.canvas.winfo_width():
            self.canvas.itemconfigure(self.innerframeId, width=self.canvas.winfo_width()-4)

    def _OnInnerFrameConfigure(self, event):
        size = (self.innerframe.winfo_reqwidth(), self.innerframe.winfo_reqheight())
        self.canvas.config(scrollregion="0 0 %s %s" % size)
        options = {}
        if self.innerframe.winfo_reqwidth() != self.canvas.winfo_width():
            width = self.innerframe.winfo_reqwidth()
            options['width'] = width
        if self.innerframe.winfo_reqheight() <= self.canvas.winfo_height():
            height = self.innerframe.winfo_reqheight()
            options['height'] = height
        if options:
            self.canvas.config(**options)

    def isValueSetToDefault(self):
        return True

    def setValue(self, value):
        pass

    def getValue(self):
        return self.innerframe

    def applyGeoManager(self, widget):
        innerframe = self.innerframe
        fill = tk.X if self.side in (tk.TOP, tk.BOTTOM) else tk.Y
        widget.pack(in_=innerframe, side=self.side, expand=tk.YES, fill=fill,
                    ipadx=2, ipady=2, padx=2, pady=2)
                    # ipadx=2, ipady=2, padx=2, pady=2, anchor=tk.NW)


class settFragment(baseWidget):
    def __init__(self, master, **options):
        wdgName = options.get('name', '').lower()
        baseWidget.__init__(self, master, name=wdgName, id=options.get('id', ''))
        self.setGUI(options)
        self.name = wdgName

    def setGUI(self, options):
        if options.get('id'):
            self.id = options.get('id').lower()
        tk.Frame(self, name=self.id).pack(side=tk.TOP, fill=tk.BOTH, expand=tk.YES)
