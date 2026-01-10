import tkinter as tk
from tkinter import ttk

TOPLEVEL_OPTIONS = [
    'background', 'bd', 'bg', 'borderwidth', 'class',
    'colormap', 'container', 'cursor', 'height', 'highlightbackground',
    'highlightcolor', 'highlightthickness', 'menu', 'relief', 'screen', 'takefocus',
    'use', 'visual', 'width'
]


class BCPopupMenu(tk.Toplevel):
    
    def __init__(self, master, **kwargs):
        # Pop 'tearoff' to prevent it from being passed to Toplevel, where it's not a valid option.
        # This provides API compatibility with tk.Menu.
        kwargs.pop('tearoff', None)
        self._post_command = kwargs.pop('postcommand', None)
        super_kwargs = {key: kwargs.pop(key) for key in kwargs.keys() & TOPLEVEL_OPTIONS}
        super().__init__(master, **super_kwargs)
        self.overrideredirect(True)
        self._items = []
        self.current_selection_index = -1
        self.active_item = None

        self.main_frame = ttk.Frame(self, style="BCPopupMenu.TFrame")
        self.main_frame.pack(expand=True, fill="both")
        font = kwargs.pop('font', ('Consolas', 10))
        self._setup_styles(font)
        self.unpost()

    def _setup_styles(self, font):
        style = ttk.Style(self)
        style.configure("BCPopupMenu.TFrame", background="white", borderwidth=1, relief="solid")

        conf_kwargs = dict(font=font, padding=(5, 3), background='white', foreground='black')
        map_kwargs = dict(
            background=[('active', '#005A9E')],
            foreground=[('active', 'black')]
        )
        
        # --- Command button style ---
        # Increase left padding to align with checkbuttons (simulating indicator space)
        btn_kwargs = conf_kwargs.copy()
        btn_kwargs['padding'] = (22, 3, 5, 3)
        style.configure("BCPopupMenu.TButton", borderwidth=0, relief="flat", anchor="w", **btn_kwargs)
        style.map("BCPopupMenu.TButton", **map_kwargs)

        # --- Checkbutton and Radiobutton styles ---
        # Inherit from default TCheckbutton layout to keep the indicator
        style.layout('BCPopupMenu.TCheckbutton', style.layout('TCheckbutton'))
        style.configure('BCPopupMenu.TCheckbutton', **conf_kwargs, borderwidth=0)
        style.map("BCPopupMenu.TCheckbutton", **map_kwargs)

        style.layout('BCPopupMenu.TRadiobutton', style.layout('TRadiobutton'))
        style.configure('BCPopupMenu.TRadiobutton', **conf_kwargs, borderwidth=0)
        style.map("BCPopupMenu.TRadiobutton", **map_kwargs)

        style.configure("BCPopupMenu.TSeparator", background="gray")

    def _redraw_menu(self):
        """Clears and redraws all menu widgets."""
        for child in self.main_frame.winfo_children():
            child.destroy()

        wdg_params = []
        lbl_len = 0
        for item in self._items:
            widget = None
            item_type = item['type']
            
            # Make a mutable copy of the options for widget creation
            creation_opts = item['options'].copy()
            
            # Map the public 'label' option to the internal 'text' option for ttk widgets
            if 'label' in creation_opts:
                creation_opts['text'] = creation_opts.pop('label')

            # Wrapper for command to close menu
            original_command = creation_opts.get('command', lambda: None)
            def wrapped_command(cmd=original_command):
                if cmd:
                    cmd()
                self._close_menu()

            creation_opts['command'] = wrapped_command
            lbl_len = max(lbl_len, len(creation_opts.get('text', '')))
            wdg_params.append(creation_opts)

        fmt_str = f"{{: <{lbl_len}}}".format
        for i, creation_opts in enumerate(wdg_params):
            item = self._items[i]
            item_type = item['type']
            widget = None

            if 'text' in creation_opts:
                creation_opts['text'] = fmt_str(creation_opts['text'])
            if item_type == 'command':
                widget = ttk.Button(self.main_frame, style="BCPopupMenu.TButton", **creation_opts)
            elif item_type == 'checkbutton':
                widget = ttk.Checkbutton(self.main_frame, style="BCPopupMenu.TCheckbutton", **creation_opts)
            elif item_type == 'radiobutton':
                widget = ttk.Radiobutton(self.main_frame, style="BCPopupMenu.TRadiobutton", **creation_opts)
            elif item_type == 'separator':
                widget = ttk.Separator(self.main_frame, orient='horizontal', style="BCPopupMenu.TSeparator")
                widget.pack(expand=True, fill='x', padx=5, pady=2)
            elif item_type == 'cascade':
                # Add cascade indicator
                creation_opts['text'] = creation_opts.get('text', '') + '  ▶'
                widget = ttk.Button(self.main_frame, style="BCPopupMenu.TButton", **creation_opts)

            if widget and item_type != 'separator':
                widget.pack(expand=True, fill='x')

                def on_enter(event, index=i):
                    self.current_selection_index = index
                    self._update_selection_visuals()

                widget.bind("<Enter>", on_enter)
            item['widget'] = widget

    def _get_selectable_indices(self):
        """Returns a list of indices for items that can be selected (not separators)."""
        return [i for i, item in enumerate(self._items) if item['type'] != 'separator']
    
    def _add_item(self, item_type, options):
        self._items.append({'type': item_type, 'options': options, 'widget': None})
        self._redraw_menu()

    def add(self, item_type, **options):
        """Generic method to add an item of a specific type."""
        self._add_item(item_type, options)

    def add_command(self, **options):
        self._add_item('command', options)

    def add_checkbutton(self, **options):
        self._add_item('checkbutton', options)

    def add_radiobutton(self, **options):
        self._add_item('radiobutton', options)

    def add_separator(self, **options):
        self._add_item('separator', options)

    def add_cascade(self, **options):
        self._add_item('cascade', options)

    def insert(self, index, item_type, **options):
        final_index = self.index(index) + (index == tk.END)
        self._items.insert(final_index, {'type': item_type, 'options': options, 'widget': None})
        self._redraw_menu()

    def insert_command(self, index, **options):
        self.insert(index, 'command', **options)

    def insert_checkbutton(self, index, **options):
        self.insert(index, 'checkbutton', **options)

    def insert_radiobutton(self, index, **options):
        self.insert(index, 'radiobutton', **options)

    def insert_separator(self, index, **options):
        self.insert(index, 'separator', **options)

    def insert_cascade(self, index, **options):
        self.insert(index, 'cascade', **options)

    def delete(self, index1, index2=None):
        start = self.index(index1)
        end = self.index(index2) if index2 is not None else start
        del self._items[start:end+1]
        self._redraw_menu()

    def entrycget(self, index, option):
        final_index = self.index(index)
        return self._items[final_index]['options'].get(option)

    def entryconfigure(self, index, **options):
        final_index = self.index(index)
        self._items[final_index]['options'].update(options)
        self._redraw_menu()

    def index(self, index):
        if isinstance(index, int):
            return index
        if index in ('end', 'last'):
            return len(self._items) - 1 if self._items else 0
        if index == 'active':
            return self.current_selection_index
        if index == 'none':
            return -1
        # Does not support @y syntax
        return 0

    def invoke(self, index):
        final_index = self.index(index)
        item = self._items[final_index]
        if item and item.get('widget'):
            item['widget'].invoke()
    
    def post(self, x, y):
        if self._post_command:
            self._post_command()
            
        self.geometry(f"+{int(x)}+{int(y)}")
        self.deiconify()
        self.focus_set()
        self.lift()
        self.grab_set()

        selectable = self._get_selectable_indices()
        self.current_selection_index = selectable[0] if selectable else -1
        self._update_selection_visuals()

        self.bind("<FocusOut>", self._close_menu)
        self.bind("<Up>", self.onKeyPress)
        self.bind("<Down>", self.onKeyPress)
        self.bind("<Return>", self.onKeyPress)
        self.bind("<Escape>", self.onKeyPress)

    tk_popup = post # Alias for tk.Menu compatibility

    def unpost(self):
        self.withdraw()

    def type(self, index):
        final_index = self.index(index)
        return self._items[final_index]['type']

    def yposition(self, index):
        final_index = self.index(index)
        widget = self._items[final_index].get('widget')
        return widget.winfo_y() if widget else 0

    def configure(self, **kwargs):
        if 'postcommand' in kwargs:
            self._post_command = kwargs.pop('postcommand')
    
    config = configure

    def cget(self, option_name):
        if option_name == 'postcommand':
            return self._post_command
        # For other options, you might need to handle them appropriately.
        # This is a simplified cget.
        return None
    
    def activate(self, index):
        final_index = self.index(index)
        self.current_selection_index = final_index
        self._update_selection_visuals()
    
    def _update_selection_visuals(self):
        for i, item in enumerate(self._items):
            widget = item.get('widget')
            if not widget or item['type'] == 'separator':
                continue
            if i == self.current_selection_index:
                widget.state(['active'])
                self.active_item = widget
            else:
                widget.state(['!active'])
        self.event_generate('<<MenuSelect>>')

    def onKeyPress(self, event):
        keysym = event.keysym
        if keysym == 'Return':
            if self.active_item:
                self.active_item.invoke()
            return "break"

        if keysym == 'Escape':
            self._close_menu()
            return "break"

        selectable = self._get_selectable_indices()
        if not selectable: return "break"

        if keysym == 'Up':
            delta = -1
        elif keysym == 'Down':
            delta = 1
        try:
            current_pos = selectable.index(self.current_selection_index)
            new_pos = (current_pos + delta) % len(selectable)
        except ValueError:
            new_pos = (len(selectable) - 1) if delta == -1 else 0

        self.current_selection_index = selectable[new_pos]
        self._update_selection_visuals()
        return "break"

    def _close_menu(self, event=None):
        self.grab_release()
        self.withdraw()


def main():
    root = tk.Tk()
    root.title("Advanced BCPopupMenu Test")
    root.geometry("500x400")

    # Variables for checkbuttons and radiobuttons
    show_status_var = tk.BooleanVar(value=True)
    file_format_var = tk.StringVar(value="JSON")

    def on_menu_select(event):
        print("<<MenuSelect>> event generated!")
        widget = event.widget
        if isinstance(widget, BCPopupMenu) and widget.current_selection_index != -1:
            try:
                item_type = widget.type(widget.current_selection_index)
                label = widget.entrycget(widget.current_selection_index, 'label')
                print(f"  Selected item: index={widget.current_selection_index}, type='{item_type}', label='{label}'")
            except tk.TclError:
                # This can happen if the index is somehow invalid temporarily
                pass
            except Exception as e:
                print(f"Error retrieving menu item details: {e}")

    def post_command_1():
        print("Post command 1: Building initial menu.")
        build_menu(1)

    def post_command_2():
        print("Post command 2: Building alternative menu.")
        build_menu(2)

    # Create a single popup menu instance to be modified dynamically
    popup = BCPopupMenu(root, tearoff=0, postcommand=post_command_1)
    # popup = tk.Menu(root, tearoff=0)
    popup.bind('<<MenuSelect>>', on_menu_select)

    def build_menu(menu_type=1):
        # Clear existing menu items before building
        popup.delete(0, 'end')
        
        if menu_type == 1:
            popup.add_command(label="Copy", command=lambda: print("Action: Copy"))
            popup.add_command(label="Cut", command=lambda: print("Action: Cut"))
            popup.add_separator()
            popup.add_checkbutton(label="Show Status Bar", variable=show_status_var, 
                                  command=lambda: print(f"Show Status: {show_status_var.get()}"))
            popup.add_separator()
            popup.add_radiobutton(label="JSON", variable=file_format_var, value="JSON", 
                                  command=lambda: print(f"File Format: {file_format_var.get()}"))
            popup.add_radiobutton(label="XML", variable=file_format_var, value="XML", 
                                  command=lambda: print(f"File Format: {file_format_var.get()}"))
            popup.add_radiobutton(label="YAML", variable=file_format_var, value="YAML", 
                                  command=lambda: print(f"File Format: {file_format_var.get()}"))

        else:
            popup.add_command(label="Option A", command=lambda: print("Action: A"))
            popup.add_command(label="Option B", command=lambda: print("Action: B"))
        
        popup.add_separator()
        popup.add_command(label="Exit", command=root.destroy)


    def show_popup(event):
        try:
            popup.post(event.x_root, event.y_root)
        finally:
            popup.grab_release()

    def switch_post_command():
        # Example of dynamically changing the postcommand
        current_command = popup.cget('postcommand')
        if current_command == post_command_1:
            popup.configure(postcommand=post_command_2)
            print("Switched to post command 2.")
        else:
            popup.configure(postcommand=post_command_1)
            print("Switched to post command 1.")


    # UI Elements
    info_label = ttk.Label(root, text="Right-click to show the popup menu.", font=('Consolas', 12))
    info_label.pack(pady=20)
    
    switch_button = ttk.Button(root, text="Switch Post Command", command=switch_post_command)
    switch_button.pack(pady=10)

    root.bind("<Button-3>", show_popup)

    build_menu()
    root.configure(menu=popup)  # For testing purposes, set as main menu

    root.mainloop()

    

if __name__ == '__main__':
    main()
    pass