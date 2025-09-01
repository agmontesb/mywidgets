# -*- coding: utf-8 -*-

from . import SintaxEditor
from . import CollapsingFrame
from . import WidgetsExplorer
from . import MenuBar
from . import navigationbar
from . import regexframe


def getWidgetClass(widgetName):
    widgetTypes = dict(
        sintaxeditor=SintaxEditor.SintaxEditor,
        collapsingframe=CollapsingFrame.collapsingFrame,
        widgetexplorer=WidgetsExplorer.WidgetExplorer,
        menubar=MenuBar.MenuBar,
        ribbon=MenuBar.Ribbon,
        navigationbar=navigationbar.navigationFactory,
        rgxtreelist=regexframe.TreeList,
        rgxpatbar=regexframe.RegexpBar,
        rgxnavbar=regexframe.NavigationBar,
        rgxeditor=regexframe.PythonEditor,
        rgxstatusbar=regexframe.StatusBar,
    )
    return widgetTypes.get(widgetName, None)
