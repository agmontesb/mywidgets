import tkinter as tk

import userinterface
from equations import equations_manager


class View(tk.Frame):

    def __init__(self, master, layout, name=None):
        super().__init__(name=name)
        self.fragments = {}
        self.setGUI(layout)

    def setGUI(self, layout):
        xmlObj = userinterface.getLayout(layout)
        userinterface.newPanelFactory(
            master=self,
            selpane=xmlObj,
            genPanelModule=None,
            setParentTo='master',
            registerWidget=self.register_widget,
        )
        equations_manager.set_initial_widget_states()

    def register_widget(self, master, xmlwidget, widget):
        if isinstance(widget, Fragment):
            self.fragments[widget.winfo_name()] = widget

    def onReceive(self, fragment_id, data):
        '''
        Recibe datos procesados por el fragment
        :param fragment_id: str. Fragment source dientifier.
        :param data: obj. Data send by the fragment
        :return: None
        '''
        pass

    def onSend(self, data, fragment_id=None):
        '''
        Envía información al fragment identificado con fragment_id o a todos los fragments.
        :param data: obj. Data send to the fragment.
        :param fragment_id: str or None. Fragment identifier. None indicates that the data
        must be send to all fragments.
        :return: None.
        '''
        receivers = (fragment_id,) if fragment_id is not None else self.fragments.keys()
        for fragment  in receivers:
            fragment.receive(data)
        pass


class Fragment(View):

    def receive(self, data):
        pass

    def send(self, data):
        self.master.onReceive(self.winfo_name(), data)
        pass