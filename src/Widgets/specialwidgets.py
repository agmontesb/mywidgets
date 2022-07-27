import tkinter as tk

from equations import equations_manager
from Widgets.kodiwidgets import formFrame


def getWidgetClass(wdg_name):
    wdg_names = dict(var=var, form=form)
    return wdg_names.get(wdg_name, None)


def var(master, **kwargs):
    '''
    Declara una variable de estado.
    :param master: tk.
    :param kwargs: dict. Paámetros puede incluir claves como 'type', 'name', 'value'
    :return:
    '''
    _type = kwargs.pop('type', 'string')
    var_type = f"{_type.title()}Var"
    tk_var = getattr(tk, var_type)(master, **kwargs)
    equations_manager.state_equations[(var_name := str(tk_var))] = tk_var
    equations_manager.var_values[var_name] = tk_var.get()
    equations_manager.register_variable(var_name)
    return tk_var


def form(master, **kwargs):
    import userinterface as ui

    options = {key: value for key, value in kwargs.items() if key in ('src', 'name')}
    layout_name = options.get('src')
    selpane = ui.getLayout(layout_name, withCss=True)
    fframe = formFrame(master, settings={}, selPane=selpane, name=options.get('name', None))
    return fframe