
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
        enabled = widget.getvar(name1)
        state = 'normal' if enabled else 'disabled'
        widget.configure(state=state)
    return enableCallback

wdg_enable = enabledClosure

STATES = dict([('visible', geoManagerClosure), ('enable', enabledClosure)])
