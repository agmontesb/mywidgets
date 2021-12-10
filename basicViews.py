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
import importlib
import xml.etree.ElementTree as ET



def widgetFactory(master, settings, selPane, panelModule=None, k=-1):
    '''
    Crea la jerarquia de widgets que conforman una tkinter form.
    :param master:      tkinter Form. Padre de la Form a generar.
    :param settings:    dict. Valores de las variables diferentes a los default definidos
                        en el archivo de layout.
    :param selPane:     element tree nade. Nodo raiz definido por el archivo de layout.
    :param panelModule: modulo. Define los widgets definidos por el usuario.
    :param k:           integer. Consecutivo utilizado por la función para crear el nombre
                        interno de los widgets a crear.
    :return:            2 members tuple. Posición 0: Valor consecutivo del últimmo widget agregado.
                        Posición 1: Lista de tuples que muestra el id del widget y
                        la ecuación que activa (enable) el widget.
    '''
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

    if not panelModule and selPane.get('lib'):
        panelModule = selPane.get('lib')
        panelModule = importlib.import_module(panelModule, __package__)
    enableEc = []
    for xmlwidget in selPane:
        k += 1
        options = xmlwidget.attrib
        options['name'] = str(k)    # Se asigna el consecutivo como nombre del widget.
        if options.get('enable', None):
            # Se almacena en enableEc la ecuación que habilita el widget.
            enableEc.append((k, xmlwidget.attrib['enable']))
        wType = xmlwidget.tag
        if wType in widgetTypes:
            widgetClass = widgetTypes.get(wType, None)
        elif panelModule and hasattr(panelModule, wType):
            # Widget definido por el usuario en panelModule.
            widgetClass = getattr(panelModule, wType)
            assert issubclass(widgetClass, baseWidget), 'All user defined widget must be inherited from baseWidget'
        else:
            # ERROR: No se encontró definición del widget
            widgetClass = None
            err_str = 'The setting type "%s" is not a define type. \n' \
                      'It must me one of: %s ' % (wType, ', '.join(sorted(widgetTypes.keys())))
            raise KeyError(err_str)

        if options.get('id'):
            # Se asigna como id del widget el último segmento del id definido.
            options['id'] = options['id'].split('/')[-1]

        wId = options.get('id')
        if wId and panelModule and hasattr(panelModule, wId):
            # El usuarrio puede definir un widget derivándolo de una clase base, para lo cual
            # debe tener en panelModule una clase con nombre del id
            idClass = getattr(panelModule, wId)
            assert issubclass(idClass, widgetClass), \
                'In module %s the class "%s" must be ' \
                'inherited from %s' % (panelModule.__name__, wId, widgetClass.__name__)
            setattr(idClass, 'me', master)
            widgetClass = idClass

        dummy = widgetClass(master, **options)
        if isinstance(dummy, settContainer):
            wcontainer = dummy
            if hasattr(wcontainer, 'innerframe'):
                wcontainer = wcontainer.innerframe
            k, deltEnableEc = widgetFactory(wcontainer, settings, xmlwidget, panelModule=panelModule, k=k)
            enableEc += deltEnableEc
        if hasattr(dummy, 'id'):
            # Si se tiene un widget con id:
            key = dummy.id
            if settings and key in settings:
                # Se asigna como valor del widget el valor definido en settings.
                dummy.setValue(settings[key])
            # Se establece la equivalencia del id asignado y el árbol que lleva a él.
            # Se registra en el formFrame padre, el id y el widget.
            dummy.form.registerWidget(options['id'], dummy.path)
    return k, enableEc


def formFrameGen(master, filename=None, selPane=None, settings=None):
    '''
    Identifica la librería que se utiliza para generar los widgets que conforman la form.
    :param master: tkinter Frame que actuara como padre de la forma.
    :param settings: dict. Valores diferentes a default para las variables de la forma.
    :param selPane: ElementTreee. Nodo raiz del element tree que traduce el layout.
    :return: formFrame or object define in user library.
    '''
    if not any((filename, selPane)):
        raise AttributeError('You must specify filename or selPane')
    if filename:
        with open(filename, 'rb') as f:
            xmlstr = f.read()
        selPane = ET.XML(xmlstr).find('category')

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

    return formclass(master, settings, selPane, formModule)


class formFrame(tk.Frame):
    '''
    Clase que entrega un Frame lleno con los widgets definicos en un archivo layout definido.
    '''
    def __init__(self, master, settings, selPane, formModule=None):
        '''
        :param master:      tkinter Form. Padre de la forma a generar.
        :param settings:    dict. Valores de las variables cuyo valor es difernte
                            al defaul definido en el layout.
        :param selPane:     elementtree. Nodo raiz del element tree que define el layout.
        :param formModule:  module. Modulo que contiene la definición de los widgets.
                            definidos por el usuario.
        '''
        tk.Frame.__init__(self, master)
        self.settings = {}
        self.enEquations = {}
        self.dependents = {}
        self.widgetMapping = {}
        self.nameToId = {}
        self.radioGroups = {}
        # self.frame = frame = settContainer(self, name="frame")
        # frame.pack(side=tk.TOP, fill=tk.BOTH, expand=tk.YES, anchor=tk.NE)

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
            widget = self
            while wpath:
                wdName, wpath = wpath.partition('.')[0:3:2]
                widget = widget.nametowidget(wdName)
            return widget
        raise AttributeError("The '%s' form doesn't have an attribute call '%s'" % (self, attr))


    def populateWithSettings(self, settings, selPane, formModule):
        '''
        Construye todos los widgets que dependen de este formFrame.
        :param settings: dict. Valores de los widgets diferentes a los defaults.
        :param selPane: element tree node. Nodo raiz del cual se desprenden la estructura
                        del formFrame.
        :param formModule: module. Contiene las definiciones de todos los widgets deffinidos
                            por el usuario.
        :return: None.
        '''
        enableEq = widgetFactory(self, settings, selPane, panelModule=formModule)[1]
        self.nameToId = {value.rsplit('.', 1)[-1]: key for key, value in self.widgetMapping.items()}
        self.category = selPane.get('label')
        self.registerEc(enableEq)
        self.setDependantWdgState()
        self.registerChangeListeners()

    def setChangeSettings(self, settings):
        '''
        Establece el valor asociado a los widgets cuyo valor difiere del default y
        establece a default el valor de los widgets que no aparecen en settings.
        :param settings:
        :return: None.
        '''
        form = self
        mapping = [key for key in self.widgetMapping.keys()
                   if hasattr(getattr(form, key), 'setValue')]
        toModify = set(settings.keys()).intersection(mapping)
        list(map(lambda w: w.setValue(settings[w.id]), self.getWidgets(toModify)))
        toReset = set(mapping).difference(toModify)
        list(map(lambda w: w.setValue(w.default), self.getWidgets(toReset)))

    def registerEc(self, enableEquations):
        '''
        Preprocesa las enable equations: obtiene forma absoluta, las variables asociadas,
        y mapea al widget con su correspondiente ecuación absoluta la cual es posible evaluar
        como una expresión de python.
        :param enableEquations: str. Equación que establece cuando se habilita un widget
                                con base al valor o estado de otros en la  forma.
        :return: None.
        '''
        for posWidget, enableEc in enableEquations:
            enableEc = self.getAbsEcuation(posWidget, enableEc)
            wVars = list(map(str, self.findVars(enableEc)))
            assert set(wVars).issubset(self.nameToId), 'The enable equation for "%s" widget' \
                                                       ' reference a non id widget' \
                                                       % (self.nameToId[str(posWidget)])
            for elem in wVars:
                self.dependents[elem] = self.dependents.get(elem, []) + [str(posWidget)]
            self.enEquations[str(posWidget)] = enableEc.replace('+', ' and ')

    def getAbsEcuation(self, pos, enableEc):
        '''

        :param pos: int. Id absoluto del widget al que se quiere asociar la enableEc.
        :param enableEc: str. Equación que establece cuando se habilita un widget
                         con base al valor o estado de otros en la  forma.
        :return: str. Ecuación absoluta porque en la enableEc se integra la "pos" en los
                 tos en que queda implicita esta.
        '''
        for tag in ['eq(', 'lt(', 'gt(']:
            enableEc = enableEc.replace(tag, tag + '+')
        enableEc = enableEc.replace('+-', '-').replace('!', 'not ')
        enableEc = enableEc.replace('true', 'True').replace('false', 'False').replace(',)', ',None)')
        for tag in ['eq(', 'lt(', 'gt(']:
            enableEc = enableEc.replace(tag, tag + str(pos))
        return enableEc

    def findVars(self, enableEc):
        '''

        :param enableEc: str. Equación que establece cuando se habilita un widget
                         con base al valor o estado de otros en la  forma.
        :return: list. Lista widgets ids (enteros) de los cuales depende el estado que a los
                 que la enableEc se refiere.
        '''
        enableEc = enableEc.replace('not ', '').replace('*', '+')
        eq = lt = gt = lambda x, a: [x]
        vars = eval(enableEc)
        try:
            retval = set(vars)
        except:
            retval = []
        else:
            retval = list(retval)
        return retval
        # return [elem for k, elem in enumerate(vars) if elem not in vars[0:k]]

    def findWidgetState(self, enableEq):
        '''
        Evalúa la enableEq para encontrar el widget state.
        :param enableEq: str. Expresión válida en python.
        :return: tk.NORMAL o tk.DISABLE.
        '''
        eq = lambda x, a: getattr(self, self.nameToId[str(x)]).getValue() == a
        lt = lambda x, a: getattr(self, self.nameToId[str(x)]).getValue() < a
        gt = lambda x, a: getattr(self, self.nameToId[str(x)]).getValue() > a
        state = eval(enableEq) >= 1
        return tk.NORMAL if state else tk.DISABLED

    def setDependantWdgState(self):
        '''
        Establece el estado de los widgets que componen la forma.
        :return: None.
        '''
        for key in sorted(self.enEquations.keys(), key=int):
            enableEq = self.enEquations[key]
            calcState = self.findWidgetState(enableEq)
            widget = getattr(self, self.nameToId[key])
            try:
                idKey = widget.id
                widget.children[idKey].configure(state=calcState)
            except:
                pass

    def registerChangeListeners(self):
        '''
        Establece como callbak function a self.varChange en todos aquellos widgets que puedan
        afectar el estado de otros en la forma.
        :return: None
        '''
        for key in self.dependents.keys():
            widget = getattr(self, self.nameToId[key])
            widget.setListener(self.varChange)

    def varChange(self, widgetName):
        '''
        Callback function que actualiza el estado de los widgets que dependen de widgetName
        cuando este cambia de valor/estado.
        :param widgetName: str. Nombre del widget cuyo valor/estado ha cambiado.
        :return: None.
        '''
        for depname in self.dependents[widgetName]:
            enableEq = self.enEquations[depname]
            calcState = self.findWidgetState(enableEq)
            widget = getattr(self, self.nameToId[depname])
            try:
                idKey = widget.id
                widget.children[idKey].configure(state=calcState)
            except:
                pass

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
        widgetsIds = widgetsIds or self.widgetMapping.keys()
        return [self.__getattr__(key) for key in widgetsIds]

    def getGroupVar(self, groupName):
        '''
        Obtiene la tk.StringVar asociada a un radio grupo determinado.
        :param groupName: str. Nombre del radio grupo cuya variable se quiere referenciar.
        :return: tk.StringVar. Variable que tiene el valor asociado cen el groupName.
        '''
        return self.radioGroups.setdefault(groupName, tk.StringVar())

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
                 su valro de default.
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
                elif key and settings.has_key(key):
                    changedSettings['reset'].append(key)
        filterFlag = lambda key: (not settings.has_key(key) or settings[key] != changedSettings[key])
        toProcess = dict([(key, value) for key, value in changedSettings.items() if filterFlag(key)])
        return toProcess


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
            self.form = master
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
        basepath = os.path.abspath('.')
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


class TreeDialog(tkSimpleDialog.Dialog):
    def __init__(self, master, title=None, xmlFile=None, isFile=False, settings=None):
        import xmlFileWrapper
        self.allSettings = None
        self.settings = settings = settings or {}
        self.ads = xmlFileWrapper.xmlFileWrapper(xmlFile, isFile=isFile, nonDefaultValues=settings)
        tkSimpleDialog.Dialog.__init__(self, master, title)

    def body(self, master):
        '''create dialog body.

        return widget that should have initial focus.
        This method should be overridden, and is called
        by the __init__ method.
        '''
        selPanel = self.ads.getActivePane()
        self.form = form = formFrameGen(master, {}, selPanel)
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
            deltaStr = '<setting id="{0}" type="text" label="Parent Element" default="{1}" enable="false"/>\n'
            outStr += 8 * ' ' + deltaStr.format(*tupleSett[0])
            deltaStr = '<setting id="{0}" type="text" label="Element Name" default="{1}" />\n'
            outStr += 8 * ' ' + deltaStr.format(*tupleSett[1])
            tupleSett = tupleSett[2:]

        templateStr = '<setting id="{0}" type="text" label="{0}" default=""/>\n'
        if isEdit:
            templateStr = '<setting id="{0}" type="text" label="{0}" default="{1}"/>\n'
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
        dlg = TreeDialog(self, title='Add', xmlFile=xmlDlg, isFile=False)
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
        if iid:
            value = self.tree.set
            columnsId = self.columnsId
            pair = [(col, value(iid, col)) for col in columnsId]
            xmlDlg = self.xmlDlgWindow(pair, isEdit=True)
            dlg = TreeDialog(self, title='Edit', xmlFile=xmlDlg, isFile=False)
            if dlg.allSettings:
                result = dict(dlg.allSettings)
                record = [result[col].strip() for col in columnsId]
                for k, col in enumerate(columnsId):
                    self.tree.set(iid, col, record[k])

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
