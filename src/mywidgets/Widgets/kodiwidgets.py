# -*- coding: utf-8 -*-
'''
Created on 18/09/2014

@author: Alex Montes Barrios
'''

import os
import re
import tkinter as tk
import tkinter.simpledialog as tkSimpleDialog
import tkinter.filedialog as tkFileDialog
from tkinter.colorchooser import askcolor as tkColorDialog
from tkinter import ttk
import xml.etree.ElementTree as ET
import importlib
import fnmatch
import operator
import platform

import mywidgets.userinterface as userinterface
from mywidgets.equations import equations_manager


def getWidgetClass(widgetName):
    widgetTypes = dict(
        kaction=settAction,
        kaudio=settFile,
        kbool=settBool,
        kcolor=settColor,
        kcontainer=settContainer,
        kdrpdwnlst=settDDList,
        kenum=settEnum,
        kexecutable=settFile,
        kfile=settFile,
        kfileenum=settFileenum,
        kfolder=settFolder,
        kfragment=settFragment,
        kimage=settFile,
        kipaddress=settNumber,
        klabel=settLabel,
        klabelenum=settEnum,
        klsep=settSep,
        knumber=settNumber,
        koptionlst=settOptionList,
        ksep=settSep,
        kslider=settSlider,
        ktext=settText,
        kvideo=settFile,
    )
    return widgetTypes.get(widgetName, None)


class baseWidget(tk.Frame, object):
    '''
    Clase que define el widget básico como un tk.Frame
    '''

    params = ('frametype', 'name', 'id', 'nopack', 'varType', 'text', 'bg', )

    def __new__(cls, *args, **options):
        instance = super(baseWidget, cls).__new__(cls)
        return instance

    def __init__(self, master, **in_options):
        '''
        Inicialización del instance.
        :param master: tkinter Frame. Padre del widget.
        :param options: dict. kwargs válidos para la definición de un tkinter Frame, además
                        de los cuales acepta "id", "name", "varType"
        '''
        options = {key: in_options[key] for key in in_options.keys() & self.params}
        frametype = options.get('frametype', 'Frame')
        assert frametype in ('Frame', 'LabelFrame')
        wdgName = options.get('name', '').lower()
        self.id = options.get('id').lower() if options.get('id') else None # Atributo id definido por el usuario
        self._id = options.pop('id', wdgName)       # Atributo _id = 'id' propio.

        nopack = options.pop('nopack', 'false')
        varType = options.pop('varType', None)
        self.value = None
        self._default = None                         # Atributo: default.
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
            if frametype == 'LabelFrame':
                baseConf['text'] = options['text']

        if varType:                    # Atributo: value.
            self.setVarType(varType, name=baseConf.get('name', None))

        super_class = getattr(tk, frametype)
        super_class.__init__(self, master, **baseConf)
        # Se definen dos atributos:
        # path = Camino que resulta de concatenar los nombres de los Frame que contienen
        #        este baseWidget
        # form = Tkinter Form que es el padre de este baseWidget
        if issubclass(master.__class__, settContainer):
            self.path = master.path + '.' + baseConf.get('name', '')
            self.form = master.form
            if nopack != 'true':
                master.applyGeoManager(self)
        else:
            self.path = baseConf.get('name', '')
            self.form = master.form if hasattr(master, 'form') else master
            if nopack != 'true':
                self.pack(side=tk.TOP, fill=tk.X, ipadx=2, ipady=2, padx=1, pady=1)

    @property
    def default(self):
        return self._default

    @default.setter
    def default(self, value):
        self._default = value
        equations_manager.state_equations[self._id]._default = value
        equations_manager.var_values[self._id] = value
        pass

    def setVarType(self, vartype='string', name=None):
        '''
        Tipo de valor asociado con el widget.
        :param vartype: str. Tipo de variable, puede ser uno de estas:
                        ['str', 'int', 'double', 'boolean'], cualquier
                        otro valor se asimila a 'str'.
        :param name: str or None. Nombre de la variable, que cuando existe, se hace igual
                     al nombre del widget. Si no tiene nombre name es None.
        :return: None.
        '''
        if vartype == 'int':
            self.value = tk.IntVar(name=name)
        elif vartype == 'double':
            self.value = tk.DoubleVar(name=name)
        elif vartype == 'boolean':
            self.value = tk.BooleanVar(name=name)
        else:
            self.value = tk.StringVar(name=name)
        equations_manager.state_equations[name] = self.value

    def getSettingPair(self, tId=False):
        '''
        :param tId: boolean. Utilizar id propio (_id) o el id asignado por tkinter.
        :return: tuple. "id" y valor asociado al widget.
        '''
        id = self._id if tId else self.id
        return (str(self.value), self.getValue())

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
        if not str(self.value).startswith('PY_VAR'):
            equations_manager.var_values[str(self.value)] = value
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

    def configure(self, option=None, **options):
        if option:
            return self.getConfig(option)
        return self.setConfig(**options)

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
        baseWidget.__init__(self, master, varType='string', **options)
        self.setGUI(options)
        self.name = options.get('name').lower()

    def setGUI(self, options):
        if options.get('id'):
            texto = self.getValue()
            method = tk.Message if texto.count('\n') else ttk.Label
            method(self, name=options.get('id', None), textvariable=self.value, width=20, anchor=tk.NW).pack(side=tk.LEFT, fill=tk.X, expand=1)
        else:
            method = tk.Message if options.get('label').count('\n') else ttk.Label
            method(self, text=options.get('label'), width=20, anchor=tk.NW).pack(side=tk.LEFT, fill=tk.X, expand=1)


class settFileenum(baseWidget):
    def __init__(self, master, **options):
        baseWidget.__init__(self, master, varType='string', **options)
        self.setGUI(options)
        self.name = options.get('name').lower()

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
        basepath = os.path.abspath('../..')
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
        baseWidget.__init__(self, master, varType='string', **options)
        self.setGUI(options)
        self.name = options.get('name').lower()

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
        baseWidget.__init__(self, master, varType='string', **options)
        self.setGUI(options)
        self.name = options.get('name').lower()

    def setGUI(self, options):
        if options.get('label'):
            ttk.Label(self, text=options.get('label'), width=20, anchor=tk.NW).pack(side=tk.LEFT)
        if options.get('id'): self.id = options.get('id').lower()
        self.initialdir = options.get('initialdir', '')
        self.default = options.get('default', '')
        if self.initialdir and self.default:
            self.default = os.path.relpath(self.default, self.initialdir)
        tk.Button(
            self,
            name=self.id,
            textvariable=self.value,
            command=lambda x=options.get("initialdir", ""): self.getFile(x)
        ).pack(side=tk.RIGHT, fill=tk.X, expand=1)
        self.setValue(self.default)

    def getFile(self, initialdir):
        initialdir = self.value.get() or initialdir
        fileName = tkFileDialog.askopenfilename(initialdir=initialdir)
        if fileName:
            fileName = os.path.relpath(fileName, initialdir)
            self.value.set(fileName)

    def getAbsolutePath(self):
        return os.path.join(self.initialdir, self.value.get()) if self.value.get() else ''


class settColor(settFile):

    def setValue(self, value):
        super().setValue(value)
        if value:
            btn = self.nametowidget(self.id)
            btn.config(bg=value)

    def getFile(self, x=None):
        colors = tkColorDialog(title='Tkinter Color Chooser')
        if colors[1] is not None:
            self.setValue(colors[1])
            # self.value.set(colors[1])
            # btn = self.nametowidget(self.id)
            # btn.config(bg=colors[1])


class settDDList(baseWidget):
    def __init__(self, master, **options):
        baseWidget.__init__(self, master, varType='string', **options)
        self.setGUI(options)
        self.name = options.get('name').lower()

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
        # self.value.set(self.lvalues[ndx])
        super().setValue(self.lvalues[ndx])

    def getValue(self):
        try:
            value = super().getValue()
            ndx = self.lvalues.index(value)
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
        baseWidget.__init__(self, master, varType='string', **options)
        self.setGUI(options)
        self.name = options.get('name').lower()

    def setGUI(self, options):
        ttk.Label(self, text=options.get('label'), width=25, anchor=tk.NW).pack(side=tk.LEFT)
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
        # self.value.set(value)
        super().setValue(value)

    def getValue(self, onlyValue=False):
        onlyValue = onlyValue or not self.withValues
        value = super().getValue()
        if onlyValue: return value
        return '|'.join([value] + self.children[self.id].cget('values').split(' '))

    def getSettingPair(self, tId=False):
        id = self._id if tId else self.id
        return (id, self.getValue(tId))


class CustomDialog(tkSimpleDialog.Dialog):
    def __init__(self, master, title=None, xmlFile=None, isFile=False, settings=None, dlg_type='okcancel'):
        self.allSettings = None
        self.settings = settings or {}
        if isFile:
            xmlFile = userinterface.getContent(xmlFile)
        self.ads = xmlFile
        self.dlg_type = dlg_type
        tkSimpleDialog.Dialog.__init__(self, master, title)

    def body(self, master):
        '''create dialog body.

        return widget that should have initial focus.
        This method should be overridden, and is called
        by the __init__ method.
        '''
        self.form = form = formFrameGen(master, settings=self.settings, selPane=self.ads)
        form.pack(side=tk.TOP, fill=tk.BOTH, expand=tk.YES)
        wdgId = list(form.nameToId.keys())[0]
        # wdgId = sorted(form.nameToId.keys(), key=int)[0]
        wdgId = form.nameToId[wdgId]
        widget = getattr(self.form, wdgId)
        return widget

    def buttonbox(self):
        '''add standard button box.

        override if you do not want the standard buttons
        '''

        box = tk.Frame(self)

        if self.dlg_type in ('okcancel', 'ok'):
            w = ttk.Button(box, text="OK", width=10, command=self.ok, default=tk.ACTIVE)
            w.pack(side=tk.LEFT, padx=5, pady=5)
            self.bind("<Return>", self.ok)
        if self.dlg_type == 'okcancel':
            w = ttk.Button(box, text="Cancel", width=10, command=self.cancel)
            w.pack(side=tk.LEFT, padx=5, pady=5)
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

    # def geometry(self, posStr):
    #     width, height = 290, 220
    #     posx = (self.winfo_screenwidth() - width) / 2
    #     posy = (self.winfo_screenheight() - height) / 2
    #     posStr = "+%d+%d" % (posx, posy)
    #     tkSimpleDialog.Dialog.geometry(self, posStr)


class settOptionList(baseWidget):
    def __init__(self, master, **options):
        self.isTree = options.get('tree', 'false') == 'true'
        baseWidget.__init__(self, master, varType='string', **options)
        self.setGUI(options)
        self.name = options.get('name').lower()
        self.virtualEventData = None

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
        column_names = list(map(lambda x: x.strip(), colHeadings.split(',')))
        columnsId = dcolumns = [x.lower() for x in column_names]
        if self.isTree:
            dshow = 'tree ' + dshow
            dcolumns = '#all'
        tree = ttk.Treeview(uFrame, show=dshow, columns=columnsId, displaycolumns=dcolumns)
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        sbar.config(command=tree.yview)  # xlink sbar and tree
        tree.config(yscrollcommand=sbar.set)  # move one moves other
        for column in column_names:
            tree.heading(column.lower(), text=column, anchor=tk.W)
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

        self.separator = separator = tuple(options.get('separator', '|,'))
        self.setValue(self.default, sep=separator)

    def xmlDlgWindow(self, tupleSett, isEdit=False, isTree=False):
        header = """<?xml version="1.0" encoding="utf-8" standalone="yes"?>
<settings>
    <category label="TCombobox" lib="mywidgets.%s">
"""
        footer = """    </category>
</settings>
"""
        header = header % __name__
        outStr = header
        if not isEdit and isTree:
            deltaStr = '<ktext id="{0}" label="Parent Element" default="{1}" enable="false"/>\n'
            outStr += 8 * ' ' + deltaStr.format(*tupleSett[0])
            deltaStr = '<ktext id="{0}" label="Element Name" default="{1}" />\n'
            outStr += 8 * ' ' + deltaStr.format(*tupleSett[1])
            tupleSett = tupleSett[2:]

        templateStr = '<ktext id="{0}" label="{0}" default=""/>\n'
        if isEdit:
            templateStr = '<ktext id="{0}" label="{0}" default="{1}"/>\n'
        for x, y in tupleSett:
            deltaStr = templateStr.format(x, y)
            outStr += 8 * ' ' + deltaStr
        outStr += footer
        outStr = userinterface.SignedContent(outStr)
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
            piid = self.tree.parent(iid)
            self.virtualEventData = (self.tree.item(piid, 'text'), self.tree.item(iid, 'text'), record)
            self.event_generate('<<OptionList_Edit>>', when='tail')

    def onDel(self):
        iid = self.tree.focus()
        if iid: self.tree.delete(iid)

    def setValue(self, value, sep=None):
        sep = sep or self.separator
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

    def getValue(self, sep=None):
        sep = sep or self.separator
        seprow, sepcol = sep
        stack = list(self.tree.get_children('')[::-1])
        bDatos = []
        while stack:
            iid = stack.pop()
            iidValues = []
            if self.isTree:
                iidValues = [self.tree.parent(iid), iid, self.tree.item(iid, 'text')]
            iidValues = iidValues + list(self.tree.item(iid, 'values'))
            iidValStr = sepcol.join(iidValues)
            bDatos.append(iidValStr)
            children = self.tree.get_children(iid)
            if children:
                stack.extend(list(children)[::-1])
        return seprow.join(bDatos)


class settSlider(baseWidget):
    def __init__(self, master, **options):
        baseWidget.__init__(self, master, varType='double', **options)
        self.setGUI(options)
        self.name = options.get('name').lower()

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
        baseWidget.__init__(self, master, varType='int', **options)
        self.setGUI(options)
        self.name = options.get('name').lower()

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
        self.name = options.get('name').lower()
        baseWidget.__init__(self, master, varType='string', **options)
        self.setGUI(options)

    def setGUI(self, options):
        ttk.Label(self, name='textlbl', text=options.get('label'),
                 width=20, anchor=tk.NW).pack(side=tk.LEFT)
        self.value = tk.StringVar(name=self.name)
        self.default = options.get('default', '')
        self.setValue(self.default)
        if options.get('id'):
            self.id = options.get('id').lower().replace('.', '__')
            ttk.Entry(self, name=self.id, textvariable=self.value).pack(side=tk.RIGHT, fill=tk.X, expand=1)
        else:
            ttk.Label(self, textvariable=self.value).pack(side=tk.RIGHT, fill=tk.X, expand=1)


class settBool(baseWidget):
    def __init__(self, master, **options):
        baseWidget.__init__(self, master, **options)
        self.name = options.get('name', '').lower()
        if 'group' in options:
            groupName = options['group']
            self.value = self.form.getGroupVar(groupName)
        else:
            self.setVarType('boolean', name=self.name)
        self.setGUI(options)

    def setGUI(self, options):
        self.id = id = options.get('id', '').lower()
        self.default = options.get('default') == 'true'
        if 'group' in options:
            method = ttk.Radiobutton
            value_opt = dict(value=id)
            if self.default: self.setValue(id)
        else:
            method = ttk.Checkbutton
            value_opt = dict(onvalue=True)
            self.setValue(self.default)
        chkbtn = method(self, name=self.id, variable=self.value,
                                command=self.onClick,
                                **value_opt
                        )
        cside = options.get('cside', tk.RIGHT)
        chkbtn.pack(side=cside)
        ttk.Label(self, name="boollbl", text=options.get('label'), width=20, anchor=tk.NW)\
            .pack(side=tk.LEFT, fill=tk.X, expand=tk.YES)

    @property
    def default(self):
        return self._default

    @default.setter
    def default(self, value):
        self._default = value
        try:
            equations_manager.state_equations[self._id]._default = value
            equations_manager.var_values[self._id] = value
        except:
            pass

    def isValueSetToDefault(self):
        return self.getValue() == self.default

    def setValue(self, value):
        self.value.set(value)

    def getValue(self):
        value = self.value.get()
        # if isinstance(value, str):
        #     value = (value == self.id)
        return value

    def onClick(self):
        try:
            self.form.onClickEvent(self._id)
        except:
            pass


class settAction(baseWidget):
    def __init__(self, master, **options):
        baseWidget.__init__(self, master, **options)
        self.setGUI(options)
        self.name = options.get('name', '').lower()

    def setGUI(self, options):
        if options.get('id'):
            self.id = options.get('id').lower()
        self.value = options.get('default')
        ttk.Button(self, name=self.id, text=options.get('label'), command=self.onClick).pack(side=tk.RIGHT, fill=tk.X,
                                                                                            expand=1)

    def onClick(self):
        wdg = self.form if hasattr(self.form, 'onClickEvent') else self.winfo_toplevel()
        try:
            wdg.onClickEvent(self._id)
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
        baseWidget.__init__(self, master, **options)
        self.setGUI(options)
        self.name = options.get('name').lower().lower()

    def setGUI(self, options):
        if options.get('type', None) == 'lsep':
            ttk.Label(self, text=options.get('label')).pack(side=tk.LEFT)
        if 'noline' not in options:
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
        keys = {'side', 'label', 'scrolled', 'type'}.intersection(options)
        contoptions = {key: options.pop(key) for key in keys}
        bflag = 'label' in contoptions
        if bflag:
            options['frametype'] = 'LabelFrame'
            options['text'] = contoptions.pop('label')
        packSide = contoptions.get('side', 'top')
        self.side = dict(top=tk.TOP, bottom=tk.BOTTOM, left=tk.LEFT, right=tk.RIGHT).get(packSide, tk.TOP)
        wdgName = options.get('name', '').lower().replace('.', '_')
        id = options.get('id', wdgName).lower()
        if id != wdgName:
            self.id = id
        baseWidget.__init__(self, master, **options)
        self.name = wdgName

        self.innerframe = self
        if contoptions.get('scrolled', 'false') == 'true':
            self.outerframe = outerframe = tk.Frame(self, name='outerframe')
            outerframe.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=tk.YES)

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

    def _OnCanvasConfigure(self, event):
        if self.innerframe.winfo_reqheight() <= self.canvas.winfo_height():
            self.vsb.grid_remove()
            # self.vsb.pack_forget()
        else:
            self.vsb.grid()
            # self.vsb.pack()

        if self.innerframe.winfo_reqwidth() != self.canvas.winfo_width():
            self.canvas.itemconfigure(self.innerframeId, width=self.canvas.winfo_width()-4)
        # canvas_width = event.width
        # self.canvas.itemconfig(self.innerframeId, width=canvas_width)

    def _OnInnerFrameConfigure(self, event):
        # x, y = 0, 0
        reqwidth, reqheight = self.innerframe.winfo_reqwidth(), self.innerframe.winfo_reqheight()
        # scrl_rgn = (x, y, reqwidth, reqheight)
        self.canvas.config(scrollregion=self.canvas.bbox('all'))
        options = {}
        if reqwidth != self.canvas.winfo_width():
            options['width'] = reqwidth
        if reqheight <= self.canvas.winfo_height():
            options['height'] = reqheight
        if options:
            self.canvas.config(**options)
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def onMouseWheel(self, event):  # cross platform scroll wheel event
        if platform.system() == 'Windows':
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        elif platform.system() == 'Darwin':
            self.canvas.yview_scroll(int(-1 * event.delta), "units")
        else:
            if event.num == 4:
                self.canvas.yview_scroll(-1, "units")
            elif event.num == 5:
                self.canvas.yview_scroll(1, "units")

    def onEnter(self, event):  # bind wheel events when the cursor enters the control
        if platform.system() == 'Linux':
            self.canvas.bind_all("<Button-4>", self.onMouseWheel)
            self.canvas.bind_all("<Button-5>", self.onMouseWheel)
        else:
            self.canvas.bind_all("<MouseWheel>", self.onMouseWheel)

    def onLeave(self, event):  # unbind wheel events when the cursorl leaves the control
        if platform.system() == 'Linux':
            self.canvas.unbind_all("<Button-4>")
            self.canvas.unbind_all("<Button-5>")
        else:
            self.canvas.unbind_all("<MouseWheel>")

    def isValueSetToDefault(self):
        return True

    def setValue(self, value):
        pass

    def getValue(self):
        return self.innerframe

    def applyGeoManager(self, widget):
        innerframe = self.innerframe
        fill = tk.X if self.side in (tk.TOP, tk.BOTTOM) else tk.Y
        widget.pack(in_=innerframe, side=self.side, fill=fill,
                    ipadx=2, ipady=2, padx=2, pady=2)


class settFragment(baseWidget):
    def __init__(self, master, **options):
        baseWidget.__init__(self, master, **options)
        self.setGUI(options)
        self.name = options.get('name', '').lower()

    def setGUI(self, options):
        if options.get('id'):
            self.id = options.get('id').lower()
        tk.Frame(self, name=self.id).pack(side=tk.TOP, fill=tk.BOTH, expand=tk.YES)


class FormFrame(tk.Frame):
    '''
    Clase que entrega un Frame lleno con los widgets definicos en un archivo layout definido.
    '''

    def __init__(self, master, settings, selPane, formModule=None, name=None):
        '''
        :param master:      tkinter Form. Padre de la forma a generar.
        :param settings:    dict. Valores de las variables cuyo valor es difernte
                            al defaul definido en el layout.
        :param selPane:     elementtree. Nodo raiz del element tree que define el layout.
        :param formModule:  module. Modulo que contiene la definición de los widgets.
                            definidos por el usuario.
        '''
        tk.Frame.__init__(self, master, name=name)
        settings = settings or {}
        self.settings = settings
        self.widgetMapping = {}
        self.nameToId = {}
        self.radioGroups = {}

        self.populateWithSettings(settings, selPane, formModule)
        pass

    def __getattr__(self, attr):
        '''
        Todos los widgets en este container pueden ser referenciados como atributos
        de la forma "self.widgetname"
        :param attr: st. Nombre del widget
        :return: basicWidget instance o None. Widget referenciado o None si no existe.
        '''
        if attr in self.__dict__['widgetMapping']:
            widgetMapping = self.__dict__['widgetMapping']
            wpath = widgetMapping.get(attr)
            widget = self.nametowidget(wpath)
            return widget
        raise AttributeError("The '%s' form doesn't have an attribute call '%s'" % (self, attr))

    def populateWithSettings(self, settings, selPane, formModule):
        '''
        Construye todos los widgets que dependen de este formFrame.
        :param settings: dict. Valores de los widgets diferentes a los defaults.
        :param selPane: element tree node. Nodo raiz del cual se desprenden la estructura
                        del formFrame.
        :param formModule: module. Contiene las definiciones de todos los widgets definidos
                            por el usuario.
        :return: None.
        '''
        from mywidgets.userinterface import newPanelFactory

        # En este punto se debe incluir la lógica para la visibleEc
        newPanelFactory(self, selPane, genPanelModule=formModule, registerWidget=self.regWidget)
        self.nameToId = {value.rsplit('.', 1)[-1]: key for key, value in self.widgetMapping.items()}
        self.category = selPane.get('label')
        self.setChangeSettings(settings)
        equations_manager.set_initial_widget_states()

    def regWidget(self, master, xmlwidget, widget):
        '''
        Crea un acceso directo al widget procesado por newPanelFactory.
        :param xmlwidget: element tree node. Representación base para la generación de widget.
        :param widget: tkinter object. Último widget generado a través de newPanelFactory.
        :return: None
        '''
        if not isinstance(widget, baseWidget):
            return
        #Solo se procesan los kodiwidgets.
        try:
            key = xmlwidget.attrib.pop('id')
        except:
            return
        try:
            # Se establece la equivalencia del id asignado y el árbol que lleva a él.
            # Se registra en el formFrame padre, el id y el widget.
            # if hasattr(dummy.form, 'form'):
            widget.form.registerWidget(key, str(widget))
        except Exception as e:
            print(str(e))
        if key in self.settings:
            # Se actualiza el valor asociado con el widget para los que tengan id.
            # Se asigna como valor del widget el valor definido en settings.
            widget.setValue(self.settings[key])

    def setChangeSettings(self, settings):
        '''
        Establece el valor asociado a los widgets cuyo valor difiere del default y
        establece a default el valor de los widgets que no aparecen en settings.
        :param settings:
        :return: None.
        '''
        form = self
        groupvars = set(settings.keys()).intersection(self.radioGroups)
        for grpvar in groupvars:
            self.radioGroups[grpvar].set(self.settings.pop(grpvar))
        mapping = [key for key in self.widgetMapping.keys()
                   if hasattr(getattr(form, key), 'setValue')]
        toModify = set(settings.keys()).intersection(mapping)
        list(map(lambda w: w.setValue(settings[w.id]), self.getWidgets(toModify)))
        toReset = set(mapping).difference(toModify)
        list(map(lambda w: w.setValue(w.default), self.getWidgets(toReset)))

    def resetForm(self):
        '''
        Vuelve los valores del form a sus valores de default
        :return: None
        '''
        self.setChangeSettings({})

    def registerWidget(self, wdId, wdPath):
        '''
        Mapea el wdId y el camino absoluto del widget.
        :param wdId: str. Nombre del widget.
        :param wdPath: str. Camino del widget desde la raiz.
        :return: None
        '''
        self.widgetMapping[wdId.lower()] = wdPath

    def getWidgets(self, widgetsIds=None):
        '''
        Lista los todos o algunos de los widgets que componen la forma.
        :param widgetsIds: list o None. Id de los widgets que se quieren listar o
                           None si se quieren todos los widgets.
        :return: list. basicWidgets
        '''
        if widgetsIds is None:
            widgetsIds = self.widgetMapping.keys()
        return [self.__getattr__(key) for key in widgetsIds]

    def getGroupVar(self, groupName):
        '''
        Obtiene la tk.StringVar asociada a un radio grupo determinado.
        :param groupName: str. Nombre del radio grupo cuya variable se quiere referenciar.
        :return: tk.StringVar. Variable que tiene el valor asociado cen el groupName.
        '''
        return self.radioGroups.setdefault(groupName, tk.StringVar(name=groupName))

    def getGroupValue(self, groupName):
        '''
        Obtiene el valor asociado con un radio grupo determinado.
        :param groupName: str. Nombre del radio grupo cuyo valor se requiere.
        :return:
        '''
        return self.radioGroups[groupName].get()

    def getChangeSettings(self, settings):
        '''
        Actualiza los valores que han cambiado en la forma.
        :param settings: dict. Valores que se quieren actualizar con los valores cambiados.
        :return: dict. Valores que estando en settings han cambiado en la forma.
                 Bajo la clave 'reset' entrega los valores que estando en settings han vuelto a
                 su valor de default.
        '''
        changedSettings = dict(reset=[])
        for child in self.getWidgets():
            try:
                flag = child.isValueSetToDefault()
            except:
                pass
            else:
                key, value = child.getSettingPair()
                if not flag:
                    changedSettings[key] = value
                elif key and key in settings:
                    changedSettings['reset'].append(key)
        filterFlag = lambda key: (key not in settings or settings[key] != changedSettings[key])
        toProcess = dict([(key, value) for key, value in changedSettings.items() if filterFlag(key)])
        return toProcess

    def getSettings(self):
        args = {
            key: value
            for key, value in [
                child.getSettingPair() for child in self.getWidgets()
            ]
        }
        return args

# Se hace para compatibilidad con versiones anteriores.
formFrame = FormFrame


def formFrameGen(master, filename=None, selPane=None, settings=None, withCss=True):
    '''
    Identifica la librería que se utiliza para generar los widgets que conforman la form.
    :param master: tkinter Frame que actuara como padre de la forma.
    :param filename: str. Path al archivo xml que contiene el layout a configurar.
    :param selPane: ElementTreee. Nodo raiz del element tree que traduce el layout.
    :param settings: dict. Valores diferentes a default para las variables de la forma.
    :return: formFrame or object define in user library.
    '''
    if not any((filename, selPane)):
        raise AttributeError('You must specify filename or selPane')
    is_content = selPane is not None
    layout = selPane or filename
    selPane = userinterface.getLayout(layout, withCss, is_content)

    formclass = formFrame
    formModule = None
    if selPane.get('lib'):
        libname = selPane.get('lib')
        try:
            parentname = re.match(r'(\.0x[0-9a-f]+)\.?', str(master))
            baseframe = master.nametowidget(parentname.group(1))
        except:
            pckname = master.__module__.rsplit('.', 1)[0]
        else:
            pckname = baseframe.droidInstance.__module__.rsplit('.', 1)[0]
        formModule = importlib.import_module(libname, pckname)
        classname = selPane.get('label').title().replace(' ', '')
        try:
            formClass = getattr(formModule, classname)
        except:
            pass
        else:
            if issubclass(formClass, formFrame):
                formclass = formClass

    return formclass(master, settings, selPane, None)
