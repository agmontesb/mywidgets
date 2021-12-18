# -*- coding: utf-8 -*-

from . import SintaxEditor
from . import CollapsingFrame


def getWidgetClass(widgetName):
    widgetTypes = dict(
        sintaxeditor=SintaxEditor.SintaxEditor,
        collapsingframe=CollapsingFrame.collapsingFrame
    )
    return widgetTypes.get(widgetName, None)
