# -*- coding: utf-8 -*-
import importlib
import re
import tkinter as tk
import xml.etree.ElementTree as ET

# tkinter reference: https://anzeljg.github.io/rin2/book2/2405/docs/tkinter/index.html
# Tcl8.5.19/Tk8.5.19 Documentation: http://tcl.tk/man/tcl8.5/contents.htm


pack_params = ["after", "anchor", "before", "expand", "fill", "in", "ipadx", "ipady", "padx", "pady", "side"]
grid_paprams = ["column", "columnspan", "in_", "ipadx", "ipady", "padx", "pady", "row", "rowspan", "sticky"]
place_params = ["anchor", "bordermode", "height", "in", "relheight", "relx", "rely", "width", "x", "y"]


def getWidgetInstance(master, widgetname, attributes, panelModule=None):
    '''

    :param master: widget. De ser derivado de basicWidget.
    :param widgetname: str. Nombre del widget que se quiere instanciar.
    :param attributes: dict. Atributos del widget a instanciar.
    :param panelModule: módulo. Contiene definiciones de widgets definidos por el usuario.
    :return: widget.
    '''

    # Si no se tiene panelModule se asume que es tkinter
    # panelModule = panelModule or tk
    getTkinterClass = lambda x: getattr(tk, x.title() if x != 'labelframe' else 'LabelFrame')
    getUdfClass = getattr(panelModule, 'getWidgetClass', lambda x: getattr(panelModule, x))
    try:
        widgetClass = getTkinterClass(widgetname)
    except AttributeError:
        widgetClass = getUdfClass(widgetname)
        if widgetClass is None:
            # ERROR: No se encontró definición del widget
            raise AttributeError(f'{widgetname} is not a tkinter widget or a user defined class. ')

    pack_keys = attributes.keys() & pack_params
    pack_opt = {key: attributes.pop(key) for key in pack_keys}

    # config_opt = {key: attributes.pop(key) for key in ('name', ) if key in attributes}
    # widget = widgetClass(master, **config_opt)
    # widget_attr = widget.configure()
    # config_keys = attributes.keys() & widget_attr.keys()
    # config_opt = {key: attributes.pop(key) for key in config_keys}
    # widget.configure(**config_opt)
    widget = widgetClass(master, **attributes)

    if 'in' in pack_opt and isinstance(pack_opt['in'], (bytes, str)):
        pack_opt['in_'] = widget.winfo_parent() + pack_opt.pop('in')
    widget.pack(**pack_opt)

    return widget


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

    if not panelModule and selPane.get('lib'):
        panelModule = selPane.get('lib')
        panelModule = importlib.import_module(panelModule, __package__)
    enableEc = []
    visibleEc = []
    for xmlwidget in selPane:
        k += 1
        isContainer = bool(len(xmlwidget.getchildren()))
        options = xmlwidget.attrib
        options.setdefault('name', str(k))    # Se asigna el consecutivo como nombre del widget.

        try:
            # Se asigna como id del widget el último segmento del id definido.
            id = options.pop('id').split('/')[-1]
        except KeyError:
            id = None

        # Se almacena en enableEc la ecuación que habilita el widget.
        try:
            enable = options.pop('enable')
            enableEc.append((k, enable))
        except KeyError:
            enable = None

        # Se almacena en visibleEc la ecuación que hace visible el widget.
        try:
            visible = options.pop('visible')
            visibleEc.append((k, visible))
        except KeyError:
            visible = None

        wType = xmlwidget.tag
        dummy = getWidgetInstance(master, wType, options, panelModule=panelModule)
        if visible and visible != 'true':
            dummy.pack_forget()
        if isContainer:
            k, deltEnableEc, deltVisibleEc = widgetFactory(dummy, settings, xmlwidget, panelModule=panelModule, k=k)
            enableEc += deltEnableEc
            visibleEc += deltVisibleEc
        if id:
            # Si se tiene un widget con id:
            key = id
            if settings and key in settings:
                # Se asigna como valor del widget el valor definido en settings.
                dummy.setValue(settings[key])
            # Se establece la equivalencia del id asignado y el árbol que lleva a él.
            # Se registra en el formFrame padre, el id y el widget.
            # if hasattr(dummy.form, 'form'):
            try:
                dummy.form.registerWidget(id, str(dummy))
            except Exception as e:
                print(str(e))
    return k, enableEc, visibleEc


def newPanelFactory(master, settings, selPane, genPanelModule=None, k=-1):
    '''
    Crea la jerarquia de widgets que conforman una tkinter form.
    :param master:      tkinter Form. Padre de la Form a generar.
    :param settings:    dict. Valores de las variables diferentes a los default definidos
                        en el archivo de layout.
    :param selPane:     element tree nade. Nodo raiz definido por el archivo de layout.
    :param genPanelModule: modulo. Define los widgets definidos por el usuario.
    :param k:           integer. Consecutivo utilizado por la función para crear el nombre
                        interno de los widgets a crear.
    :return:            2 members tuple. Posición 0: Valor consecutivo del últimmo widget agregado.
                        Posición 1: Lista de tuples que muestra el id del widget y
                        la ecuación que activa (enable) el widget.
    '''

    categories = selPane.findall('category')
    n = -1
    if len(categories) <= 1:
        if selPane.tag != 'category':
            selPane = selPane.find('category')
        n, enableEc, visibleEc = widgetFactory(master, settings, selPane, panelModule=genPanelModule, k=n)
    else:
        def selectPane(id, panels):
            for pane in panels:
                pane.pack_forget()
            panels[id].pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.YES)
            pass
        paneArray = []
        leftPane = tk.Frame(master, relief=tk.RIDGE, bd=5, bg='white', padx=3, pady=3)
        leftPane.pack(side=tk.LEFT, fill=tk.Y)
        frstboton = None
        for k, elem in enumerate(categories):
            boton = tk.Radiobutton(
                leftPane,
                text=elem.get('label'),
                value=k,
                command= lambda x=k, y=tuple(paneArray): selectPane(x, y),
                indicatoron=0
            )
            boton.pack(side=tk.TOP, fill=tk.X)
            frstboton = frstboton or boton
            pane = tk.Frame(master, relief=tk.RIDGE, bd=5, bg='white', padx=3, pady=3)
            pane.form = master
            paneArray.append(pane)
        frstboton.invoke()
        enableEc = []
        visibleEc = []
        for root, selPane in zip(paneArray, categories):
            n, deltEnableEc, deltVisibleEc = widgetFactory(root, settings, selPane, panelModule=genPanelModule, k=n)
            enableEc += deltEnableEc
            visibleEc += deltVisibleEc
    return n, enableEc, visibleEc


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
    if isinstance(selPane, (bytes, str)):
        selPane = ET.XML(selPane).find('category')

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
        :param formModule: module. Contiene las definiciones de todos los widgets deffinidos
                            por el usuario.
        :return: None.
        '''
        # En este punto se debe incluir la lógica para la visibleEc
        enableEq = newPanelFactory(self, settings, selPane, genPanelModule=formModule)[1]
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
                elif key and key in settings:
                    changedSettings['reset'].append(key)
        filterFlag = lambda key: (key not in settings or settings[key] != changedSettings[key])
        toProcess = dict([(key, value) for key, value in changedSettings.items() if filterFlag(key)])
        return toProcess


