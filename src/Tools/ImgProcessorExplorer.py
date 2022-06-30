import collections
import os
import tkinter as tk
import tkinter.messagebox as tkMessageBox
from PIL import Image, ImageTk, ImageFont

import userinterface
from equations import equations_manager
from Widgets.Custom import ImageProcessor
from Widgets.kodiwidgets import FormFrame

class ImgProcessorE(tk.Tk):
    def __init__(self):
        super().__init__()
        self.event_add('<<MENUCLICK>>', 'None')
        self.event_add('<<VAR_CHANGE>>', 'None')
        self.bind_all('<<MENUCLICK>>', self.onMenuClick)
        self.bind_all('<<VAR_CHANGE>>', self.onVarChange)

        self.forms = {}
        self.canvas = None
        self.imgId = None
        self.canvas_widgets = []
        self.setGui()

        self.attributes('-zoomed', True)
        pass

    def setGui(self):
        file_path = 'Data/tkinter/tkImgProcessorExplorer.xml'
        xmlObj = userinterface.getLayout(file_path)
        fframe = tk.Frame(self, name='fframe')
        userinterface.newPanelFactory(
            master=fframe,
            selpane=xmlObj,
            genPanelModule=None,
            setParentTo='master',
            registerWidget=self.register_widget,
        )
        equations_manager.set_initial_widget_states()
        fframe.pack(side=tk.TOP, fill=tk.BOTH, expand=tk.YES, anchor=tk.NE)

        self.chartree.bind('<<ActiveSelection>>', self.onActiveSelection, add='+')
        self.chartree.tag_configure('selected', background='light green')

    def onActiveSelection(self, event=None):
        chartree = event.widget
        selected = chartree.tag_has('selected')
        [chartree.item(nodeid, tags='') for nodeid in selected]

        nodeid = chartree.focus()
        chartree.item(nodeid, tags='selected')

        children = chartree.get_children(nodeid)
        if not children:
            value = nodeid
        else:
            value = ', '.join(children)
        form = self.forms['getfontawesomeicon']
        widget = form.getElements(('charname',))[0]
        value = f'{widget.getValue()}, {value}'.strip(', ')
        widget.setValue(value)

    def register_widget(self, master, xmlwidget, widget):
        attribs = xmlwidget.attrib
        name = attribs.get('name')
        if isinstance(widget, FormFrame):
            self.forms[name] = widget
        elif name in ('canvas', 'chartree'):
            setattr(self, name, widget)
            if name == 'chartree':
                rootdir = os.path.dirname(ImageProcessor.__file__)
                ttf_url = os.path.join(rootdir, 'FontAwesome', 'fa-solid-900.ttf')
                ttf_url = ImageProcessor.staticFile(ttf_url)
                css_url = os.path.join(rootdir, 'FontAwesome', 'fontawesome-all.css')
                css_url = ImageProcessor.staticFile(css_url)
                faMap = ImageProcessor.ccsCharCodeMap(css_url)
                char_map = collections.defaultdict(list)
                keys = ((key[3], key) for key in faMap)
                [char_map[key].append(value) for key, value in keys]
                tree = self.chartree
                for key in char_map:
                    tree.insert(
                        '',
                        'end',
                        iid=key,
                        text=key.upper(),
                    )
                for key, value in char_map.items():
                    for x in value:
                        tree.insert(
                            key,
                            'end',
                            iid=x,
                            text=x,
                        )
        pass

    def onVarChange(self, event):
        var_name, value = event.attr_data
        pass

    def onMenuClick(self, event):
        menu_master, indx = event.widget, event.data
        menu_label = menu_master.entrycget(indx, "label").lower()
        pass

    def onClickEvent(self, btn_id):
        if btn_id == 'getlabel':
            form = self.forms['getlabelargs']
            args = form.getSettings()
            wdg_font = form.getElements(('font',))[0]
            font_path = wdg_font.getAbsolutePath()
            args['font'] = ImageFont.truetype(font_path, 50)
            font = args.pop('font')
            label = args.pop('label')
            textcolor = args.pop('textcolor')
            positional = (label, font, textcolor)
            bg = args.pop('background')
            bg = Image.new('RGBA', (500, 100), (128, 128, 128, 128))
            bg = bg.rotate(args['angle'], expand=1)
            args['background'] = bg
            keywords = {key: args.pop(key) for key in ('background', 'xpos', 'ypos')}
            args.pop('getlabel')
            options = args
            labelImg = ImageProcessor.getLabel(*positional, **keywords, **options)
            self.labelImg = labelImg = ImageTk.PhotoImage(labelImg)
            canvas = self.canvas
            if self.imgId:
                [canvas.delete(x) for x in self.imgId]
            self.imgId = [canvas.create_image(canvas.winfo_width() // 2, canvas.winfo_height() // 2, image=labelImg)]
        elif btn_id == 'getfontawesome':
            form = self.forms['getfontawesomeicon']
            args = form.getSettings()
            args.pop('getfontawesome')
            charcodes = args.pop('charname')
            charcodes = charcodes.split(', ')
            args['isPhotoImage'] = args.pop('isphotoimage')
            try:
                args['size'] = eval(args['size'])
            except:
                msg = f'Invalid Size:{args["size"]}, it must be an integer or a 2-integer tuple (width, height)'
                tkMessageBox.showinfo(title='onClickEvent', message=msg)
                return
            canvas = self.canvas
            if self.imgId:
                [canvas.delete(x) for x in self.imgId]
                if self.canvas_widgets:
                    [x.destroy() for x in self.canvas_widgets]
            self.char_fawesome = []
            self.imgId = []
            self.canvas_widgets = []
            try:
                cell_width, cell_height = args['size']
            except:
                cell_width = cell_height = args['size']
            cell_width += 20
            cell_height += 20
            for k, charcode in enumerate(charcodes):
                char_fawesome = ImageProcessor.getFontAwesomeIcon(charcode, **args)
                self.char_fawesome.append(char_fawesome)
                widget = tk.Label(self, image=char_fawesome, text=charcode, compound=tk.TOP)
                self.canvas_widgets.append(widget)
                # widget.pack()
                x, y = cell_width*(k % 5 + 1), cell_height*(k // 5 + 1)
                # self.imgId.append(canvas.create_image(x, y, image=char_fawesome, anchor=tk.NW))
                self.imgId.append(canvas.create_window(x, y, window=widget, anchor=tk.NW))
            # x, y = canvas.winfo_width() // 2, canvas.winfo_height() // 2
            # self.imgId = canvas.create_window(x, y, window=widget)
        elif btn_id == 'gettexture':
            form = self.forms['gettextureargs']
            args = form.getSettings()
            args.pop('gettexture')
            keys = ('imagefile', 'bordertexture')
            option = {key: wdg.getAbsolutePath() for key, wdg in zip(keys, form.getElements(keys))}
            args.update(option)

            for key in ('border', 'bordersize', 'diffuse'):
                try:
                    args[key] = eval(args[key])
                except:
                    msg = f'Invalid {key}:{args[key]}, it must be an integer or a integer tuple'
                    tkMessageBox.showinfo(title='onClickEvent', message=msg)
                    return

            positional = (args.pop('imagefile'), args.pop('width'), args.pop('height'))
            kwargs = {key: args.pop(key) for key in ('aspectratio',)}
            options = args
            texture = ImageProcessor.getTexture(*positional, **kwargs, **options)
            self.labelImg = texture = ImageTk.PhotoImage(texture)
            canvas = self.canvas
            if self.imgId:
                [canvas.delete(x) for x in self.imgId]
            x, y = canvas.winfo_width() // 2, canvas.winfo_height() // 2
            self.imgId = [canvas.create_image(x, y, image=texture)]
        else:
            msg = f'ButtonClick fire. Button id: {btn_id}'
            tkMessageBox.showinfo(title='onClickEvent', message=msg)


def main():
    top = ImgProcessorE()
    top.mainloop()

if __name__ == '__main__':
    main()
