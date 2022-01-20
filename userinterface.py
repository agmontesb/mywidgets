# -*- coding: utf-8 -*-

# tkinter reference: https://anzeljg.github.io/rin2/book2/2405/docs/tkinter/index.html
# Tcl8.5.19/Tk8.5.19 Documentation: http://tcl.tk/man/tcl8.5/contents.htm


import importlib
import tkinter as tk
import xml.etree.ElementTree as ET

from equations import equations_manager
import cbwidgetstate

pack_params = ["after", "anchor", "before", "expand", "fill", "in", "ipadx", "ipady", "padx", "pady", "side"]
grid_params = ["column", "columnspan", "in", "ipadx", "ipady", "padx", "pady", "row", "rowspan", "sticky"]
place_params = ["anchor", "bordermode", "height", "in", "relheight", "relwidth", "relx", "rely", "width", "x", "y"]


def getLayout(layoutfile):
    # restype = directory_indx('layout')
    # layoutfile = self._unpack_pointer(id, restype)
    with open(layoutfile, 'rb') as f:
        xmlstr = f.read()
    return ET.XML(xmlstr)


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

    # Tratamiento de las variables
    if widgetname == 'var':
        _type = f"{attributes.pop('type', 'string').title()}Var"
        parent = equations_manager.default_root()
        tk_var = getattr(tk, _type)(master=parent, **attributes)
        equations_manager.var_values[str(tk_var)] = tk_var.get()
        return tk_var
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


def widgetFactory(master, selPane, panelModule=None, setParentTo='master', registerWidget=None, k=-1):
    '''
    Crea la jerarquia de widgets que conforman una tkinter form.
    :param master: tkinter Form. Padre de la Form a generar.
    :param selPane:     element tree nade. Nodo raiz definido por el archivo de layout.
    :param panelModule: modulo. Define los widgets definidos por el usuario.
    :param setParentTo: str. Los widgets que se desprendan de selPane, serán creados como hijos de:
                             'master': Hace del master también el parent del widget.
                             'category': Frame 'category' parent de todos los widgets que contiene.
                             'root': Hace parent general al Frame que contiene toda la Form
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
    geometric_manager = selPane.get('geomanager', 'pack')
    for xmlwidget in selPane:
        k += 1
        has_children = bool(len(xmlwidget.getchildren()))
        is_widget = xmlwidget.tag != 'var'
        options = dict.copy(xmlwidget.attrib)
        options.setdefault('name', str(k))    # Se asigna el consecutivo como nombre del widget.

        parent = master
        bparent = is_widget and ((setParentTo == 'category' and selPane.tag != 'category') or setParentTo == 'root')
        if bparent:
            # Cuando se elige la opción sameParent=True significa que todos los widgets que están
            # bajo una misma categoría serán creados como hijos del frame correspondiente a
            # la categoría pero puestos bajo el widget master
            options.setdefault('in', master.winfo_name())
            parent = master.nametowidget(master.winfo_parent())

        # Se asigna como id del widget el último segmento del id definido.
        id = options.get('id', '').rsplit('/')[-1]

        options.pop('geomanager', None)

        states_eq = dict([
            (key, options.pop(key)) for key in cbwidgetstate.STATES
            if key in options
        ])

        wType = xmlwidget.tag

        geomngr_params = findGeometricManager(geometric_manager)
        geomngr_keys = options.keys() & geomngr_params
        geomngr_opt = {key: options.pop(key) for key in geomngr_keys}

        bflag = 'lib' in options
        if bflag:
            module_path = options.pop('lib')
            module = importlib.import_module(module_path, __package__)
            panelModule.append((kini, module))

        dummy = getWidgetInstance(parent, wType, options, panelModule=panelModule)

        if bflag:
            panelModule.pop()

        if 'in' in geomngr_opt and isinstance(geomngr_opt['in'], (bytes, str)):
            parent_name = geomngr_opt.pop('in').lstrip('.')
            if setParentTo:
                parent_path = dummy.winfo_parent()
            else:
                # Se hace necesario hacer esto porque es posible que se despliegue el widget en
                # un conatenedor con el que comparte el padre en algún punto.
                parent_path = None
                items = dummy.parent.winfo_children()
                while items:
                    item = items.pop(0)
                    if item.winfo_name() == parent_name:
                        parent_path = str(item)
                        break
                    items.extend(item.winfo_children())
                if parent_path is None:
                    raise Exception(f"Can't pack {dummy.winfo_name()} inside {parent_name}")
            geomngr_opt['in_'] = '.'.join((parent_path, parent_name))

        if is_widget and 'visible' not in states_eq:
            getattr(dummy, geometric_manager)(**geomngr_opt)

        if registerWidget:
            registerWidget(master, xmlwidget, dummy)

        for state, eq in states_eq.items():
            callback_closure = cbwidgetstate.STATES[state]
            if state == 'visible':
                kwargs = geomngr_opt
            elif state == 'enable':
                kwargs = {}
            cb = callback_closure(dummy, **kwargs)
            equations_manager.add_equation(eq, cb)

        if has_children:
            k = widgetFactory(
                dummy,
                xmlwidget,
                panelModule=panelModule,
                setParentTo=setParentTo,
                registerWidget=registerWidget,
                k=k
            )
    if kini == panelModule[-1][0]:
        panelModule.pop()
    return k


def newPanelFactory(master, selpane, genPanelModule=None, registerWidget=None):
    '''
    Crea la jerarquia de widgets que conforman una tkinter form.
    :param registerWidget:
    :param master:      tkinter Form. Padre de la Form a generar.
    :param selPane:     element tree nade. Nodo raiz definido por el archivo de layout.
    :param genPanelModule: modulo. Define los widgets definidos por el usuario.
    :param registerWidget: callable. Callback function para registrar los widgets creados.
    :return:            2 members tuple. Posición 0: Valor consecutivo del últimmo widget agregado.
                        Posición 1: Lista de tuples que muestra el id del widget y
                        la ecuación que activa (enable) el widget.
    '''

    categories = selpane.findall('category')
    n = -1
    if len(categories) <= 1:
        if selpane.tag != 'category':
            selpane = selpane.find('category')
        n = widgetFactory(
            master,
            selpane,
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
            child.config(command=lambda x=child['value'], y=tuple(paneArray): selectPane(x, y))

        frstboton.invoke()
        for root, selPane in zip(paneArray, categories):
            n = widgetFactory(
                root,
                selPane,
                panelModule=genPanelModule,
                registerWidget=registerWidget,
                k=n)
    return n


