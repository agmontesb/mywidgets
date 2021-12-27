# -*- coding: utf-8 -*-
import importlib
import tkinter as tk

# tkinter reference: https://anzeljg.github.io/rin2/book2/2405/docs/tkinter/index.html
# Tcl8.5.19/Tk8.5.19 Documentation: http://tcl.tk/man/tcl8.5/contents.htm


pack_params = ["after", "anchor", "before", "expand", "fill", "in", "ipadx", "ipady", "padx", "pady", "side"]
grid_params = ["column", "columnspan", "in_", "ipadx", "ipady", "padx", "pady", "row", "rowspan", "sticky"]
place_params = ["anchor", "bordermode", "height", "in", "relheight", "relwidth", "relx", "rely", "width", "x", "y"]

def findGeometricManager(tag):
    if tag == 'grid':
        return grid_params
    if tag == 'place':
        return place_params
    return pack_params



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
    panelModule = panelModule or [(-1, tk)]
    for indx in range(len(panelModule) - 1, -1, -1):
        _, module = panelModule[indx]
        getWdgClass = getattr(module, 'getWidgetClass', lambda x: getattr(module, x, None))
        widgetname = widgetname if module.__name__ != 'tkinter' else (widgetname.title() if widgetname != 'labelframe' else 'LabelFrame')
        widgetClass = getWdgClass(widgetname)
        if widgetClass:
            break

    if widgetClass is None:
        # ERROR: No se encontró definición del widget
        raise AttributeError(f'{widgetname} is not a tkinter widget or a user defined class. ')

    # En este punto se tiene un parche para no romper con los Kodiwidgets que utilizan
    # el attributo 'id' y que desactivan algunas características dependiendo si tienen id o no.
    if module.__name__ == 'Widgets.kodiwidgets':
        attributes.pop(id, None)
    widget = widgetClass(master, **attributes)

    return widget


def widgetFactory(master, selPane, panelModule=None, registerWidget=None, k=-1):
    '''
    Crea la jerarquia de widgets que conforman una tkinter form.
    :param master:      tkinter Form. Padre de la Form a generar.
    :param settings:    dict. Valores de las variables diferentes a los default definidos
                        en el archivo de layout.
    :param selPane:     element tree nade. Nodo raiz definido por el archivo de layout.
    :param panelModule: modulo. Define los widgets definidos por el usuario.
    :param registerWidget: callable. Callable que debe aceptar dos parámetros: element tree node y
                        el widget recién procesado.
    :param k:           integer. Consecutivo utilizado por la función para crear el nombre
                        interno de los widgets a crear.
    :return:            2 members tuple. Posición 0: Valor consecutivo del últimmo widget agregado.
                        Posición 1: Lista de tuples que muestra el id del widget y
                        la ecuación que activa (enable) el widget.
    '''

    panelModule = panelModule or []
    kini = k
    if selPane.get('lib'):
        # El contenedor declara que sus widgets están definidos en "lib" por lo cual se agrega
        # al camino de definiciones de los widgets.
        module_path = selPane.get('lib')
        module = importlib.import_module(module_path, __package__)
        panelModule.append((kini, module))
    elif not panelModule:
        # Nos aseguramos que tkinter es la librería por defecto por lo cual lo agregamos
        # en la raiz del camino de búsqueda de los widgets.
        panelModule.append((kini, tk))
    enableEc = []
    visibleEc = []
    geometric_manager = selPane.get('geomanager', 'pack')
    for xmlwidget in selPane:
        k += 1
        isContainer = bool(len(xmlwidget.getchildren()))
        options = dict.copy(xmlwidget.attrib)
        options.setdefault('name', str(k))    # Se asigna el consecutivo como nombre del widget.

        # Se asigna como id del widget el último segmento del id definido.
        id = options.get('id', '').rsplit('/')[-1]

        options.pop('geomanager', None)

        # Se almacena en enableEc la ecuación que habilita el widget.
        enable = options.pop('enable', None)
        if enable:
            enableEc.append((k, enable))

        # Se almacena en visibleEc la ecuación que hace visible el widget.
        visible = options.pop('visible', None)
        if visible:
            visibleEc.append((k, visible))

        wType = xmlwidget.tag
        bflag = 'lib' in options

        if bflag:
            module_path = options.pop('lib')
            module = importlib.import_module(module_path, __package__)
            panelModule.append((kini, module))

        geomngr_params = findGeometricManager(geometric_manager)
        geomngr_keys = options.keys() & geomngr_params
        geomngr_opt = {key: options.pop(key) for key in geomngr_keys}

        dummy = getWidgetInstance(master, wType, options, panelModule=panelModule)

        if 'in' in geomngr_opt and isinstance(geomngr_opt['in'], (bytes, str)):
            geomngr_opt['in_'] = dummy.winfo_parent() + geomngr_opt.pop('in')
        getattr(dummy, geometric_manager)(**geomngr_opt)

        if bflag:
            panelModule.pop()

        if visible and visible != 'true':
            dummy.pack_forget()

        if registerWidget:
            registerWidget(xmlwidget, dummy)

        if isContainer:
            k, deltEnableEc, deltVisibleEc = widgetFactory(
                dummy,
                xmlwidget,
                panelModule=panelModule,
                registerWidget=registerWidget,
                k=k
            )
            enableEc += deltEnableEc
            visibleEc += deltVisibleEc
    if kini == panelModule[-1][0]:
        panelModule.pop()
    return k, enableEc, visibleEc


def newPanelFactory(master, selPane, genPanelModule=None, registerWidget=None):
    '''
    Crea la jerarquia de widgets que conforman una tkinter form.
    :param registerWidget:
    :param master:      tkinter Form. Padre de la Form a generar.
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
        n, enableEc, visibleEc = widgetFactory(
            master,
            selPane,
            panelModule=genPanelModule,
            registerWidget=registerWidget,
            k=n
        )
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
                indicatoron=0
            )
            boton.pack(side=tk.TOP, fill=tk.X)
            frstboton = frstboton or boton
            pane = tk.Frame(master, relief=tk.RIDGE, bd=5, bg='white', padx=3, pady=3)
            pane.form = master
            paneArray.append(pane)
        for child in leftPane.winfo_children():
            child.config(command= lambda x=child['value'], y=tuple(paneArray): selectPane(x, y))

        frstboton.invoke()
        enableEc = []
        visibleEc = []
        for root, selPane in zip(paneArray, categories):
            n, deltEnableEc, deltVisibleEc = widgetFactory(
                root,
                selPane,
                panelModule=genPanelModule,
                registerWidget=registerWidget,
                k=n)
            enableEc += deltEnableEc
            visibleEc += deltVisibleEc
    return n, enableEc, visibleEc



