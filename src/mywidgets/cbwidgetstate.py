import tkinter as tk


def geoManagerClosure(widget, **kwargs):
    geomanager = kwargs.pop('geomanager', 'pack')

    def geoCallback(name1, name2, op):
        visible = widget.getvar(name1)
        if visible:
            getattr(widget, geomanager)(**kwargs)
        else:
            getattr(widget, f'{geomanager}_forget')()
    return geoCallback

wdg_visible = geoManagerClosure


def enabledClosure(widget, **kwargs):

    def enableCallback(name1, name2, op):
        # enabled = widget.getvar(name1)
        tkApp = tk._default_root.tk
        enabled = tkApp.call('set', name1)
        state = 'normal' if enabled else 'disabled'
        widget.configure(state=state)
    return enableCallback

wdg_enable = enabledClosure


def mnuStateClosure(menu_wdg, ndx, **kwargs):

    def enableCallback(name1, name2, op):
        tkApp = tk._default_root.tk
        value = tkApp.call('set', name1)
        state = 'active' if value else 'disabled'
        menu_wdg.entryconfigure(ndx, state=state)
    return enableCallback

mnu_state = mnuStateClosure


def mnuVisibleClosure(menu_wdg, ndx, mtype, **kwargs):

    def enableCallback(name1, name2, op):
        tkApp = tk._default_root.tk
        value = tkApp.call('set', name1)
        if value:
            method_name = f'insert_{kwargs.pop("mtype")}'
            fnc = getattr(menu_wdg, method_name)
            fnc(ndx, **kwargs)
        else:
            menu_wdg.delete(ndx)
    return enableCallback

mnu_visible = mnuVisibleClosure


def mnuLabelClosure(menu_wdg, ndx, mtype, **kwargs):

    def enableCallback(name1, name2, op):
        tkApp = tk._default_root.tk
        value = tkApp.call('set', name1)
        if value:
            menu_wdg.entryconfigure(ndx, label=value)
    return enableCallback

mnu_label = mnuLabelClosure


STATES = dict(
    [
        ('visible', geoManagerClosure), 
        ('enable', enabledClosure),
        ('mnu_state', mnuStateClosure),
        ('mnu_visible', mnuVisibleClosure),
        ('mnu_label', mnuLabelClosure)
    ]
)

mnu_closure = [ x for x in STATES if x.startswith('mnu_')]
var_types = {'mnu_label': tk.StringVar}
