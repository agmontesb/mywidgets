import tkinter as tk

import mywidgets.userinterface as ui


class UiStyle(tk.Toplevel):

    def __init__(self):
        tk.Toplevel.__init__(self, name='uistyle')
        self.title('UiStyle')
        self.setGUI()
        pass

    def setGUI(self):
        filename = '@data:tkinter/tkWidgetStyle'
        panel = ui.getLayout(filename)
        ui.newPanelFactory(self, panel)
        self.nametowidget('op_param').bind('<<OptionList_Edit>>', self.doOptionListEdit)
        pass

    def doOptionListEdit(self, event):
        widget = self.nametowidget('op_param')
        # ('', '', ['*uno.btn', 'dos'])
        # print(widget.virtualEventData)
        _, _, (pattern, value) = widget.virtualEventData
        self.option_add(pattern, value, 20)
        for widget in self.winfo_children()[:-1]:
            widget.pack()

def main():
    root = tk.Tk()
    root.withdraw()
    uistyle = UiStyle()
    root.wait_window(uistyle)


if __name__ == '__main__':
    main()