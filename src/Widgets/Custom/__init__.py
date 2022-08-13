# -*- coding: utf-8 -*-

from . import SintaxEditor
from . import CollapsingFrame
from . import WidgetsExplorer
from . import MenuBar
from . import navigationbar


def getWidgetClass(widgetName):
    widgetTypes = dict(
        sintaxeditor=SintaxEditor.SintaxEditor,
        collapsingframe=CollapsingFrame.collapsingFrame,
        widgetexplorer=WidgetsExplorer.WidgetExplorer,
        menubar=MenuBar.MenuBar,
        ribbon=MenuBar.Ribbon,
        navigationbar=navigationbar.navigationFactory,
    )
    return widgetTypes.get(widgetName, None)
