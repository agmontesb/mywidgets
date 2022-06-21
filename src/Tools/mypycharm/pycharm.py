import tkinter as tk

import userinterface
from equations import equations_manager


class Pycharm(tk.Tk):

    def __init__(self):
        super().__init__()
        self.event_add('<<MENUCLICK>>', 'None')
        self.event_add('<<VAR_CHANGE>>', 'None')
        self.bind_all('<<MENUCLICK>>', self.onMenuClick)
        self.bind_all('<<VAR_CHANGE>>', self.onVarChange)

        self.project_path = '/mnt/c/Users/Alex Montes/PycharmProjects/mywidgets'

        self.setGui()

        self.attributes('-zoomed', True)
        pass

    def onMenuClick(self, event):
        pass

    def onVarChange(self, event):
        var_name, value = event.attr_data
        # print(f'var_change: var_name: {var_name}, value: {value}')
        if var_name == 'view_sel':
            if value == 0:
                self.hframe.hide_band('bottom')
            else:
                self.hframe.show_band()
        elif var_name in ('tree_top_sel', 'tree_btm_sel'):
            visible = sum(equations_manager.var_values[x] for x in ('tree_top_sel', 'tree_btm_sel'))
            if visible:
                self.vframe.show_band()
            else:
                self.vframe.hide_band('left')
        pass

    def setGui(self):
        file_path = 'Tools/mypycharm/res/layout/pycharm.xml'
        xmlObj = userinterface.getLayout(file_path)
        userinterface.newPanelFactory(
            master=self,
            selpane=xmlObj,
            genPanelModule=None,
            setParentTo='master',
            registerWidget=self.register_widget,
        )
        equations_manager.set_initial_widget_states()

    def register_widget(self, master, xmlwidget, widget):
        attribs = xmlwidget.attrib
        name = attribs.get('name')
        if name in ('hframe', 'vframe', 'file_path',):
            setattr(self, name, widget)
        pass


def main():
    top = Pycharm()
    top.mainloop()

if __name__ == '__main__':
    main()

