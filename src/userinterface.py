# -*- coding: utf-8 -*-

# tkinter reference: https://anzeljg.github.io/rin2/book2/2405/docs/tkinter/index.html
# Tcl8.5.19/Tk8.5.19 Documentation: http://tcl.tk/man/tcl8.5/contents.htm


import importlib
import inspect
import os.path
import tkinter as tk
import xml.etree.ElementTree as ET
import urllib.request
import urllib.parse
import functools
from contextlib import contextmanager
from typing import Callable, Sequence, Any, MutableMapping, Iterable, Tuple, Literal, TypeAlias, Optional
from typing_extensions import Protocol, runtime_checkable
from types import ModuleType


from Widgets import specialwidgets
from Widgets.Custom import ImageProcessor as imgp
from Widgets.Custom.network import network
from equations import equations_manager
import cbwidgetstate

MODULE_STACK = [(-1, tk), (-1, specialwidgets)]


@runtime_checkable
class TreeLike(Iterable['TreeLike'], Protocol):
    tag: str
    attrib: dict[str, Optional[str]]

    def get(self, item: str, default: Optional[str] = None) -> Optional[str]:
        return self.attrib.get(item, default)

    def findall(self, name: str) -> Iterable['TreeLike']:
        ...


RegWidgetCb: TypeAlias = Optional[Callable[[tk.Tk | tk.Widget, TreeLike, tk.Widget], Any]]
GeoManager_Type = Literal['grid', 'place', 'pack']

pack_params = ["after", "anchor", "before", "expand", "fill", "in", "ipadx", "ipady", "padx", "pady", "side"]
grid_params = ["column", "columnspan", "in", "ipadx", "ipady", "padx", "pady", "row", "rowspan", "sticky"]
place_params = ["anchor", "bordermode", "height", "in", "relheight", "relwidth", "relx", "rely", "width", "x", "y"]

# Este context manager se puede utilizar cuando se quiere adjuntar datos en la emision de un evento:
#   with event_data as event:
#       event.data = 'este es el mensaje'
#       widget.event_generate('<<el_evento_name>>')
#
@contextmanager
def event_data(**params):
    def decor(f):
        try:
            vars = inspect.getclosurevars(f)
            f = vars.nonlocals['f']
        except:
            pass

        def wrapper(*args, **kwargs):
            answ = f(*args, **kwargs)
            answ.__dict__.update(params)
            return answ

        return wrapper
        return decor

    wrapped = tk.Event
    tk.Event = decor(tk.Event)
    try:
        yield tk.Event
    finally:
        tk.Event = wrapped


def getContent(fileurl):
    if not urllib.parse.urlparse(fileurl).scheme:
        basepath = os.path.dirname(__file__)
        layoutpath = os.path.join(basepath, fileurl)
        layoutfile = os.path.abspath(layoutpath)
        layoutfile = f'file://{urllib.request.pathname2url(layoutfile)}'
    initConf = 'curl --user-agent "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.80 Safari/537.36" --cookie-jar "cookies.lwp" --location'
    net = network(initConf)
    content, _ = net.openUrl(layoutfile)
    return content


def getLayout(layoutfile: str) -> ET.Element:
    content = getContent(layoutfile)
    return ET.XML(content)


def findGeometricManager(tag: GeoManager_Type) -> list[str]:
    if tag == 'grid':
        return grid_params
    if tag == 'place':
        return place_params
    return pack_params


def getWidgetInstance(master: tk.Tk | tk.Widget,
                      widgetname: str,
                      attributes: MutableMapping[str, str],
                      panelModule: list[Tuple[int, ModuleType]] | None = None) -> tk.Widget:
    '''

    :param master: widget. De ser derivado de basicWidget.
    :param widgetname: str. Nombre del widget que se quiere instanciar.
    :param attributes: dict. Atributos del widget a instanciar.
    :param panelModule: módulo. Contiene definiciones de widgets definidos por el usuario.
    :return: widget.
    '''

    # Si no se tiene panelModule se asume que es tkinter
    # panelModule = panelModule or tk
    panelModule = panelModule or MODULE_STACK
    for indx in range(len(panelModule) - 1, -1, -1):
        _, module = panelModule[indx]
        getWdgClass = getattr(module, 'getWidgetClass', lambda x: getattr(module, x, None))
        widgetname = widgetname if module.__name__ != 'tkinter' else (
            widgetname.title() if widgetname != 'labelframe' else 'LabelFrame')
        widgetClass = getWdgClass(widgetname)
        if widgetClass:
            break

    if widgetClass is None:
        # ERROR: No se encontró definición del widget
        raise AttributeError(f'{widgetname} is not a tkinter widget or a user defined class. ')

    widget = widgetClass(master, **attributes)

    return widget


def widgetFactory(master: tk.Tk | tk.Widget,
                  selPane: TreeLike,
                  panelModule: list[Tuple[int, ModuleType]] | None = None,
                  registerWidget: RegWidgetCb = None,
                  setParentTo: Literal['master', 'category', 'root'] = 'master',
                  k: int = -1) -> int:
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
    kini = k
    panelModule = panelModule or [(kini, m) for _, m in MODULE_STACK]
    if selPane.get('lib'):
        # El contenedor declara que sus widgets están definidos en "lib" por lo cual se agrega
        # al camino de definiciones de los widgets.
        module_path = selPane.get('lib', '')
        assert module_path is not None
        module = importlib.import_module(module_path, __package__)
        panelModule.append((kini, module))
    geometric_manager: GeoManager_Type = selPane.get('geomanager', 'pack')
    assert geometric_manager in ['grid', 'place', 'pack']
    for xmlwidget in selPane:
        k += 1
        has_children = bool(len(list(xmlwidget)))
        is_widget = xmlwidget.tag != 'var'
        options: dict[str, Optional[str]] = dict.copy(xmlwidget.attrib)
        # Se asigna como id del widget el último segmento del id definido.
        name_default = options.get('id', '').rsplit('/')[-1] or str(k)
        options.setdefault('name', name_default)  # Se asigna el consecutivo como nombre del widget.

        parent = master
        bparent = is_widget and ((setParentTo == 'category' and selPane.tag != 'category') or setParentTo == 'root')
        if bparent:
            # Cuando se elige la opción sameParent=True significa que todos los widgets que están
            # bajo una misma categoría serán creados como hijos del frame correspondiente a
            # la categoría pero puestos bajo el widget master
            in_default = master.winfo_name()
            if options.setdefault('in', in_default).startswith('.') and setParentTo != 'master':
                options['in'] = in_default + options['in']
            parent = master.nametowidget(master.winfo_parent())

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

        # El atributo 'read' se utiliza para especificar un widget que despliega un texto y
        # puede tomar los valores left-to-right ('LtoR'), top-to-bottom ('TtoB'),
        # bottom-to-top ('BtoT').
        # Con este atributo se pueden generar botones (normales, checkbutton, radiobutton) verticales
        # cuyo texto se reemplaza por una imagen de un texto vertical si se agrega un atibuto read con
        # valor 'TtoB' o 'BtoT'.
        read = options.pop('read', 'LtoR')

        widget = getWidgetInstance(parent, wType, options, panelModule=panelModule)

        if read in ('TtoB', 'BtoT'):
            text = widget.cget('text')
            angle = 90 if read == 'BtoT' else -90
            font = imgp._eqTkFont('/usr/share/fonts/truetype/ubuntu/UbuntuMono-B.ttf', size=12)
            image = imgp.getLabel(text, font, 'black', angle=angle, isPhotoImage=True)
            widget.image = image
            widget.config(image=image)
            if wType in ('checkbutton', 'radiobutton'):
                widget.config(selectimage=image)

        if bflag:
            panelModule.pop()

        # if 'in' in geomngr_opt and isinstance(geomngr_opt['in'], (bytes, str)):
        ref_labels = geomngr_opt.keys() & ('in', 'before', 'after')
        if ref_labels:
            for ref_label in ref_labels:
                if not isinstance(geomngr_opt[ref_label], (bytes, str)):
                    continue
                parent_name = geomngr_opt.pop(ref_label).lstrip('.')
                parent_path = widget.winfo_parent()
                geomngr_opt[ref_label] = '.'.join((parent_path if parent_path != '.' else '', parent_name))
            if 'in' in ref_labels:
                geomngr_opt['in_'] = geomngr_opt.pop('in')

        if is_widget and 'visible' not in states_eq:
            getattr(widget, geometric_manager)(**geomngr_opt)

        if registerWidget:
            registerWidget(master, xmlwidget, widget)

        for state, eq in states_eq.items():
            callback_closure = cbwidgetstate.STATES[state]
            if state == 'visible':
                kwargs = geomngr_opt
            elif state == 'enable':
                kwargs = {}
            cb = callback_closure(widget, **kwargs)
            equations_manager.add_equation(eq, cb)

        if has_children:
            k = widgetFactory(
                widget,
                xmlwidget,
                panelModule=panelModule,
                setParentTo=setParentTo,
                registerWidget=registerWidget,
                k=k
            )
    if kini == panelModule[-1][0]:
        panelModule.pop()
    return k


def newPanelFactory(master: tk.Tk | tk.Widget,
                    selpane: TreeLike,
                    genPanelModule: list[Tuple[int, ModuleType]] | None = None,
                    setParentTo: Literal['master', 'category', 'root'] = 'master',
                    registerWidget: RegWidgetCb = None) -> int:
    '''
    Crea la jerarquia de widgets que conforman una tkinter form.
    :param master:      tkinter Form. Padre de la Form a generar.
    :param selpane:     element tree nade. Nodo raiz definido por el archivo de layout.
    :param genPanelModule: modulo. Define los widgets definidos por el usuario.
    :param setParentTo:       str. One of ['master', 'category', 'root'].
    :param registerWidget: callable. Callback function para registrar los widgets creados.
    :return:            2 members tuple. Posición 0: Valor consecutivo del últimmo widget agregado.
                        Posición 1: Lista de tuples que muestra el id del widget y
                        la ecuación que activa (enable) el widget.
    '''

    categories = selpane.findall('category')
    n = -1
    if len(categories) <= 1:
        try:
            selpane = categories[0]  # Case categories = [category]
        except IndexError:
            pass
        n = widgetFactory(
            master,
            selpane,
            panelModule=genPanelModule,
            registerWidget=registerWidget,
            setParentTo=setParentTo,
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
                text=elem.get('label', ''),
                value=k,
                indicatoron=False
            )
            boton.pack(side=tk.TOP, fill=tk.X)
            frstboton = frstboton or boton
            pane = tk.Frame(master, name=f'categoria{k + 1}', relief=tk.RIDGE, bd=5, bg='white', padx=3, pady=3)
            pane.form = master  # type: ignore
            paneArray.append(pane)
        for child in leftPane.winfo_children():
            child.config(command=lambda x=child['value'], y=tuple(paneArray): selectPane(x, y))  # type: ignore
        assert isinstance(frstboton, tk.Radiobutton)
        frstboton.invoke()
        for root, selPane in zip(paneArray, categories):
            n = widgetFactory(
                root,
                selPane,
                panelModule=genPanelModule,
                registerWidget=registerWidget,
                setParentTo=setParentTo,
                k=n)
    return n


def menuFactory(
        parent: tk.Tk | tk.Widget,
        selPane: TreeLike,
        menu_map: dict[str, tk.Menu] = None,
        registerMenu: RegWidgetCb = None) -> tk.Menu:
    def menu_closure(widget, data=None):
        def menu_cb():
            with event_data(data=data) as event:
                widget.event_generate('<<MENUCLICK>>')
        return menu_cb

    master = parent.winfo_toplevel()
    menu_map = menu_map or {}
    options = selPane.attrib.copy()
    label = options.pop('label')
    options['title'] = label
    menu_map[label] = menu_master = tk.Menu(parent, name=label.lower(), **options)
    for k, item in enumerate(selPane):
        menu_type = item.tag
        options = item.attrib.copy()
        if menu_type not in ['separator', 'cascade']:
            try:
                command = options['command']
                cb = getattr(master, command)
            except (AttributeError, KeyError):
                cb = menu_closure(widget=menu_master, data=k)
            options['command'] = cb
            if 'accelerator' in options:
                accelerator = options['accelerator'].lower()
                accelerator = accelerator.replace('+', '-')
                try:
                    modifiers, key = accelerator.rsplit('-', 1)
                    modifiers_map = [('ctrl', 'Control'), ('alt', 'Alt'), ('shift', 'Shift')]
                    modifiers = functools.reduce(lambda t, x: t.replace(x[0], x[1]), modifiers_map, modifiers)
                    accelerator = f'{modifiers}-KeyPress-{key}'
                except ValueError:
                    accelerator = f'KeyPress-{accelerator}'
                master.bind(f'<{accelerator}>', lambda x, y=cb: y())
        elif menu_type == 'cascade':
            menu_wdg = menuFactory(master, item, menu_map, registerMenu)
            options['menu'] = menu_wdg
            options.pop('tearoff', None)
        menu_master.add(menu_type, **options)
    try:
        registerMenu(parent, selPane, menu_master)
    except:
        pass
    return menu_master
