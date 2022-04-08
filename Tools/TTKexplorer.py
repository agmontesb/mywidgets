import tkinter.ttk as ttk
from collections import deque


class TtkStyleError(Exception):
    pass


class Ttk_Style:

    def __init__(self, theme, name):
        self._theme = theme
        self.name = name
        self.attributes = []
        self.children = self.get_children(self.get_layout())

    def _get_style_instance(self):
        s = ttk.Style()
        s.theme_use(self._theme)
        return s

    def configure(self, *args, **kwargs):
        s = self._get_style_instance()
        return s.configure(self.name, *args, **kwargs)

    def map(self, *args, **kwargs):
        s = self._get_style_instance()
        return s.map(self.name, *args, **kwargs)

    def get_layout(self):
        s = self._get_style_instance()
        try:
            layout = s.layout(self.name)
        except Exception as e:
            layout = []
        return layout

    def get_children(self, layout):
        answ = []
        for eltName, d in layout:
            answ.append(WidgetLayout(self._theme, eltName, **d))
        return answ

    def get_elements(self):
        stack = deque([(0, self)])
        indent = 4*' '
        answ = ''
        while stack:
            level, wdg_layout = stack.popleft()
            answ += f'{level*indent}{wdg_layout.name}\n'
            stack.extendleft([(level + 1, child) for child in wdg_layout.children][::-1])
        return answ

    def walk(self):
        stack = deque([('', self)])
        while stack:
            path, wdg_layout = stack.popleft()
            path = f'{path}/{wdg_layout.name}'
            attribs = wdg_layout.attributes
            children = wdg_layout.children
            stack.extend([(path, child) for child in children])
            yield path, wdg_layout, children


class WidgetLayout(Ttk_Style):
    def __init__(self, theme, name, **kwargs):
        children = kwargs.pop('children', [])
        self.get_layout = lambda: children
        super().__init__(theme, name)
        self.attributes = kwargs

    def element_options(self):
        s = self._get_style_instance()
        return s.element_options(self.name)

    def map(self):
        s = self._get_style_instance()
        keys = self.element_options()
        answ = {key: s.lookup(self.name, key) for key in keys}
        return answ

if __name__ == '__main__':
    from rich.tree import Tree
    from rich.console import Console
    from rich.console import Group
    console = Console(color_system='truecolor')

    test = 'app'
    if test == 'app':
        import tkinter as tk
        from tkinter import ttk


        class App(tk.Tk):
            def __init__(self):
                super().__init__()

                self.geometry('300x150')
                self.resizable(0, 0)
                self.title('Login')

                # configure style
                self.style = ttk.Style(self)
                self.style.configure('TLabel', font=('Helvetica', 11))
                self.style.configure('TButton', font=('Helvetica', 11))

                # heading style
                self.style.configure('Heading.TLabel', font=('Helvetica', 24), background='red')

                # UI options
                paddings = {'padx': 5, 'pady': 5}
                entry_font = {}     # {'font': ('Helvetica', 11)}

                # configure the grid
                self.columnconfigure(0, weight=1)
                self.columnconfigure(1, weight=3)

                username = tk.StringVar()
                password = tk.StringVar()

                # heading
                heading = ttk.Label(self, text='Member Login', style='Heading.TLabel')
                heading.grid(column=0, row=0, columnspan=2, pady=5, sticky=tk.N)

                # username
                username_label = ttk.Label(self, text="Username:")
                username_label.grid(column=0, row=1, sticky=tk.W, **paddings)

                username_entry = ttk.Entry(self, textvariable=username, **entry_font)
                username_entry.grid(column=1, row=1, sticky=tk.E, **paddings)

                # password
                password_label = ttk.Label(self, text="Password:")
                password_label.grid(column=0, row=2, sticky=tk.W, **paddings)

                password_entry = ttk.Entry(
                    self, textvariable=password, show="*", **entry_font)
                password_entry.grid(column=1, row=2, sticky=tk.E, **paddings)

                # login button
                login_button = ttk.Button(self, text="Login")
                login_button.grid(column=1, row=3, sticky=tk.E, **paddings)

        app = App()
        app.mainloop()

    elif test == 'ttk_style':
        ttk_style = Ttk_Style('classic', '.')

        attributes = str(ttk_style.configure())
        options = str(ttk_style.map())

        tree = Tree(Group('.', attributes, options))
        map_path = {'': tree}

        widget_names = [
            'Button',
            'Checkbutton',
            'Entry',
            'Frame',
            'Label',
            'LabelFrame',
            'Menubutton',
            'PanedWindow',
            'Radiobutton',
            'Scale',
            'Scrollbar',
        ]
        s = ttk.Style()
        theme_names = s.theme_names()
        console.print(theme_names)
        # theme_names = ['clam', 'alt', 'default', 'classic']
        theme_name = theme_names[0]
        for widget_name in widget_names:
            method = getattr(ttk, widget_name)
            try:
                b = method(None, text='Yo')
            except Exception as e:
                b = method(None)
                # console.print(widget_name, str(e))
                # continue
            ttk_style = Ttk_Style(theme_name, b.winfo_class())
            for path, parent, children in ttk_style.walk():
                parent_path, name = path.rsplit('/', 1)
                attributes = str(parent.attributes or ttk_style.configure())
                options = str(parent.map())
                dmy = map_path[parent_path].add(Group(name, attributes, options))
                map_path[path] = dmy
        console.print(tree)
