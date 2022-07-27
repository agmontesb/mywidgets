from . import panel


def getWidgetClass(widgetName):
    widgetTypes = dict(
        panel=panel.Panel,
    )
    return widgetTypes.get(widgetName, None)