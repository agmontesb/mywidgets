# -*- coding: utf-8 -*-

from . import SintaxEditor
from . import CollapsingFrame
from . import WidgetsExplorer
from . import MenuBar


def getWidgetClass(widgetName):
    widgetTypes = dict(
        sintaxeditor=SintaxEditor.SintaxEditor,
        collapsingframe=CollapsingFrame.collapsingFrame,
        widgetexplorer=WidgetsExplorer.WidgetExplorer,
        menubar=MenuBar.MenuBar,
    )
    return widgetTypes.get(widgetName, None)
