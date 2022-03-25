import collections
import importlib
import os
import tkinter as tk
import tkinter.messagebox as tkMessageBox
import tkinter.filedialog as tkFileDialog
import xml.etree.ElementTree as ET

from Widgets.Custom import CollapsingFrame, SintaxEditor
from userinterface import getWidgetInstance, widgetFactory, findGeometricManager
from Widgets.kodiwidgets import formFrameGen, CustomDialog
from Tools.WidgetsExplorer import WidgetExplorer
from equations import equations_manager

# Este es una especie de administrador de recursos que quiero implementar
R = type('Erre', (object,), {})


class UIeditor(tk.Toplevel):
    def __init__(self):
        tk.Toplevel.__init__(self)
        self.activeViewIndx = tk.IntVar(value=-1)
        self.activeViewIndx.trace("w", self.setActiveView)
        self.rightPaneIndx = tk.IntVar(value=-1)
        self.fileHistory = []
        self.treeFocusAct = None
        self.treeSelectAct = None
        self.seg = -1

        self.setGUI()
        self.newFile()
        self.state = tk.NORMAL

    def setGUI(self):
        frame = tk.Frame(self)
        frame.pack(fill=tk.BOTH, expand=1)

        ''' Se construye la barra de menus'''
        menuFrame = tk.Frame(frame)
        menuFrame.pack(side=tk.TOP, fill=tk.X)
        self.menuBar = {}
        menuOp = ['File', 'Get', 'Set', 'View', 'Knoth', 'Coding', 'Tools']
        for elem in menuOp:
            menubutton = tk.Menubutton(menuFrame, text=elem, name=elem.lower())
            menubutton.pack(side=tk.LEFT)
            self.menuBar[elem] = tk.Menu(menubutton, tearoff=False)

        viewsPane = tk.Frame(menuFrame)
        viewsPane.pack(side=tk.RIGHT)

        '''Views pane'''
        tk.Label(viewsPane, text='Views:  ').pack(side=tk.LEFT)
        common_options = dict(width=5, indicatoron=0, variable=self.activeViewIndx)
        nviews = 2
        for k in range(nviews):
            tk.Radiobutton(viewsPane, name='btn%s' % k, value=k, **common_options).pack(side=tk.LEFT)

        # label = tk.Label(topPane, text='View: ', width=13)
        # label.pack(side=tk.LEFT)
        # fileChsr = ttk.Combobox(topPane, textvariable=self.activeViewIndx, name='combo2')
        # fileChsr.pack(side=tk.LEFT)
        # cClass = fileChsr.__class__
        # cClass.config(fileChsr, state='readonly', takefocus=0)

        # '''Status bar'''
        # self.activeKnot = tk.StringVar()
        # self.addonId = tk.StringVar()
        # self.message = tk.StringVar()
        # self.statusBar = StatusBar(frame, [('AddonId: ', self.addonId),
        #                                    ('ActiveNode ', self.activeKnot),
        #                                    ('Selection: ', self.message)])
        # self.statusBar.pack(side=tk.BOTTOM, fill=tk.X, expand=0)

        '''Middle Zone'''
        # m1 = CollapsingFrame.collapsingFrame(frame, tk.VERTICAL, inisplit=0.3, buttConf='MR')
        self.vPaneWindow = m1 = tk.Frame(frame)
        m1.pack(side=tk.TOP, fill=tk.BOTH, expand=tk.YES)

        self.setUpPaneCtrls()

        ''' Setting the views'''
        views = [view[0] for view in self.viewPanes]
        for k, (view, _) in enumerate(self.viewPanes):
            tag = 'btn%s' % k
            viewsPane.children[tag].config(text=view)
        self.activeViewIndx.set(0)

        self.menuBuilder()
        for elem in menuOp:
            menubutton = menuFrame.children[elem.lower()]
            menubutton.config(menu=self.menuBar[elem])

    def onXmlTextModified(self, event):
        if event.widget.edit_modified():
            self.setSaveFlag(True)

    def setUpPaneCtrls(self):
        m1 = self.vPaneWindow
        self.ui_view = tk.Frame(m1, name='ui_view')
        self.codeFrame = SintaxEditor.SintaxEditor(m1, hrzslider=True)
        self.codeFrame.textw.bind(
            '<<Modified>>',
            self.onXmlTextModified
        )

        widgetParams = formFrameGen(
            self.ui_view,
            filename=os.path.join('../data/kodi/', 'WidgetParams.xml')
        )
        widgetParams.pack(side=tk.RIGHT, fill=tk.Y, anchor=tk.E)
        widgetParams.widget_attrs.bind('<<OptionList_Edit>>', self.doOptionListEdit)

        self.testFrame = CollapsingFrame.collapsingFrame(
            self.ui_view,
            tk.VERTICAL,
            inisplit=0.2,
            buttconf='RM',
        )
        self.testFrame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=tk.YES)
        self.testFrame.pack_propagate(0)
        ui_pane = self.testFrame.frstWidget
        self.treeview = treeview = WidgetExplorer(ui_pane)
        treeview.bind('<<ActiveSelection>>', self.onTreeActiveSelection)
        treeview.bind('<<TreeviewSelect>>', self.doTreeviewSelect)
        treeview.bind(
            '<<Modified>>',
            self.onXmlTextModified
        )
        treeview.bind('<Button-3>', self.do_popup)
        treeview.bind("<ButtonRelease-1>", lambda event: self.modifyTree(event, 'Move'), add='+')
        treeview.pack(side=tk.TOP, fill=tk.BOTH, expand=tk.YES)

        self.parent_frame = ui_pane = self.testFrame.scndWidget
        tk.Frame(ui_pane).pack()

        # Para saber en que punto hizo click el mouse:
        self.bind_all('<Button-1>', self.monitorMouseClick)

        self.avRightPanes = [self.codeFrame, self.ui_view]
        self.viewPanes = [('XML', 0), ('UI', 1)]

    def doOptionListEdit(self, event):
        widget = event.widget
        str_command, attr_key, (attr_value,) = widget.virtualEventData
        # Se actualiza el widget Seleccionado segú la modificación dada
        if self.treeSelectAct is None:
            return
        name = self.treeSelectAct[0]
        active_widget = self.nametowidget(name)
        treeview = self.treeview
        if str_command == 'config':
            kwargs = {attr_key: attr_value}
            active_widget.config(**kwargs)
        elif str_command == widget.winfo_manager():
            geo_info = getattr(active_widget, f'{str_command}_info')()
            geo_info[attr_key] = attr_value
            if str_command == 'pack':
                # Averiguamos la posición del widget en la configuración original
                next_widget = treeview.next(active_widget.winfo_name())
                if next_widget:  # El widget a tratar no es el último de los hijos a re geolocalizar
                    next_widget = treeview.item(next_widget, 'values')[0]
                    geo_info['before'] = next_widget
                    pass
            getattr(active_widget, str_command)(**geo_info)
            pass

        # Se actualiza la información en el file tree que describe el formato.
        nodeid = active_widget.winfo_name()
        values = eval(treeview.item(nodeid, 'values')[1])
        values[attr_key] = attr_value
        treeview.item(nodeid, values=(name, str(values)))
        self.setSaveFlag(True)

    # def xmlTreeRep(self):
    #     xml_str = '<?xml version="1.0" encoding="utf-8" standalone="yes"?>\n<setting>\n'
    #     treeview = self.treeview
    #     to_process = collections.deque()
    #     indent_stack = [('', 'setting')]
    #     to_process.extend(treeview.get_children())
    #     while to_process:
    #         nodeid = to_process.popleft()
    #         attribs = eval(treeview.item(nodeid, 'values')[1])
    #         tag = attribs.pop('tag')
    #         attribs = ' '.join(f'{key}="{value}"' for key, value in attribs.items())
    #         parentid = treeview.parent(nodeid)
    #         children = treeview.get_children(nodeid)
    #         if children:
    #             to_process.extendleft(reversed(children))
    #             end_str = '>'
    #         else:
    #             end_str = '/>'
    #         while parentid != indent_stack[-1][0]:
    #             _, end_tag = indent_stack.pop()
    #             xml_str += f'{len(indent_stack) * "    "}</{end_tag}>\n'
    #         xml_str += f'{len(indent_stack) * "    "}<{tag} {attribs}{end_str}\n'
    #         if end_str == '>':
    #             indent_stack.append((nodeid, tag))
    #     while indent_stack:
    #         _, end_tag = indent_stack.pop()
    #         xml_str += f'{len(indent_stack) * "    "}</{end_tag}>\n'
    #     return xml_str

    def monitorMouseClick(self, event):
        widget = event.widget
        if 'collapsingframe.scndwidget' in str(widget):
            treeview = self.treeview
            while True:
                name = widget.winfo_name()
                if treeview.exists(name):
                    break
                widget = widget.master
            # Nos aseguramos que el widget seleccionado obtenga el foco
            # treeview.focus_set()
            treeview.focus(name)
            treeview.selection_set(name)
            treeview.see(name)
            pass
        pass

    def setActiveView(self, *args, **kwargs):
        self.actViewPane = activeView = self.activeViewIndx.get()
        viewName, vwRightPane = self.viewPanes[activeView]

        rightPaneIndx = self.rightPaneIndx.get()
        if rightPaneIndx == vwRightPane:
            return
        self.setRightPane(vwRightPane)
        if vwRightPane == 0 and self.treeview.edit_modified():
            xmlstr = self.treeview.dump()
            self.init_XMl_View(xmlstr)
            self.treeview.edit_modified(0)
        elif vwRightPane == 1 and self.codeFrame.textw.edit_modified():
            xmlstr, _, _ = self.codeFrame.getContent()
            self.init_UI_View(xmlstr)
            self.codeFrame.textw.edit_modified(0)

    def setRightPane(self, rightPaneIndx):
        actRightPane = int(self.rightPaneIndx.get())
        if actRightPane != -1:
            pane = self.avRightPanes[actRightPane]
            pane.pack_forget()
        self.rightPaneIndx.set(rightPaneIndx)
        pane = self.avRightPanes[rightPaneIndx]
        pane.pack(fill=tk.BOTH, expand=1)
        pass

    def menuBuilder(self):
        self.menuBar['popup'] = tk.Menu(self, tearoff=False)

        self.menuBar['webpopup'] = tk.Menu(self, tearoff=False)

        menuOpt = []
        menuOpt.append(('command', 'Cut', '', 2, self.dummyCommand))
        menuOpt.append(('command', 'Copy', '', 0, self.dummyCommand))
        menuOpt.append(('command', 'Paste', '', 0, self.dummyCommand))
        menuOpt.append(('separator',))
        menuOpt.append(('command', 'Send UserForm', '', 0, self.dummyCommand))
        menuOpt.append(('separator',))
        menuOpt.append(('command', 'Encrypt Rijndael', '', 0, self.dummyCommand))
        menuOpt.append(('command', 'Decrypt Rijndael', '', 0, self.dummyCommand))
        menuOpt.append(('separator',))
        menuOpt.append(('command', 'Unwise process', '', 0, self.dummyCommand))
        menuOpt.append(('command', 'Unwise variable', '', 0, self.dummyCommand))
        menuOpt.append(('separator',))
        menuOpt.append(('command', 'Detect packer', '', 0, self.dummyCommand))
        menuOpt.append(('command', 'Unpack', '', 0, self.dummyCommand))
        self.makeMenu('webpopup', menuOpt)

        menuOpt = []
        menuOpt.append(('command', 'New', 'Ctrl+O', 0, self.newFile))
        menuOpt.append(('command', 'Open', 'Ctrl+O', 0, self.__openFile))
        menuOpt.append(('command', 'Save', 'Ctrl+S', 0, self.saveFile))
        menuOpt.append(('command', 'Save as', 'Ctrl+S', 0, self.saveAsFile))
        menuOpt.append(('separator',))
        # menuOpt.append(('command', 'Export to XBMC', 'Ctrl+x', 0, self.dummyCommand))
        # menuOpt.append(('command', 'MakeZip File', 'Ctrl+M', 0, self.dummyCommand))
        # menuOpt.append(('separator',))
        # menuOpt.append(('command', 'Settings', 'Ctrl+S', 0, self.dummyCommand))
        # menuOpt.append(('command', 'Close', 'Alt+Q', 0, self.Close))
        self.makeMenu('File', menuOpt)

        def fileHist(frstIndx):
            self.menuBar['File'].delete(frstIndx, tk.END)
            if self.fileHistory:
                for k, filename in enumerate(self.fileHistory):
                    flabel = os.path.basename(filename)
                    self.menuBar['File'].add(
                        'command',
                        label='{} {:30s}'.format(k + 1, flabel),
                        command=lambda x=filename: self.__openFile(x)
                    )
                self.menuBar['File'].add('separator')
            self.menuBar['File'].add('command', label='Settings', accelerator='Ctrl+S',
                                     underline=0, command=self.programSettingDialog)
            self.menuBar['File'].add('command', label='Close', accelerator='Alt+Q',
                                     underline=0, command=self.Close)

        self.menuBar['File'].config(postcommand=lambda x=len(menuOpt): fileHist(x))

    def makeMenu(self, masterID, menuArrDesc):
        master = self.menuBar[masterID]
        for menuDesc in menuArrDesc:
            menuType = menuDesc[0]
            if menuType == 'command':
                menuType, mLabel, mAccelKey, mUnderline, mCommand = menuDesc
                master.add(menuType,
                           label='{:30s}'.format(mLabel),
                           accelerator=mAccelKey,
                           underline=mUnderline,
                           command=mCommand)
            elif menuType == 'cascade':
                menuType, mLabel, mUnderline = menuDesc
                menuLabel = masterID + '.' + mLabel.replace(' ', '_')
                self.menuBar[menuLabel] = tk.Menu(master, tearoff=False)
                master.add('cascade',
                           label='{:30s}'.format(mLabel),
                           underline=mUnderline,
                           menu=self.menuBar[menuLabel])
            elif menuType == 'radiobutton':
                menuType, radioVar, radioOps = menuDesc
                for k, elem in enumerate(radioOps):
                    master.add_radiobutton(label=elem, variable=radioVar, value=k)
            elif menuType == 'checkbutton':
                menuType, checkLabel, checkVar, checkVals = menuDesc
                master.add_checkbutton(label=checkLabel, variable=checkVar, onvalue=checkVals[1], offvalue=checkVals[0])
            else:
                master.add('separator')

    def dummyCommand(self):
        tkMessageBox.showerror('Not implemented', 'Not yet available')

    def newFile(self, fileName='', xmlstr=None, panel=None):
        initial_path = os.path.abspath('../data/tkinter')
        default_name = os.path.join(initial_path, 'LayoutDefault.xml')
        # default_name = os.path.join(initial_path, 'tkUiEditor.xml')
        self.__openFile(name=default_name)

    def programSettingDialog(self):
        file_name = '/mnt/c/Users/Alex Montes/PycharmProjects/mywidgets/Data/kodi/uiEditorSettings.xml'
        settingObj = CustomDialog(self, title='Application Settings', xmlFile=file_name, isFile=True, settings={})
        all_settings = settingObj.allSettings
        if all_settings:
            for key, value in all_settings:
                setattr(R, key, value)
            print(R.initial_path)
        # settingObj = AppSettingDialog(self, 'IDE_Settings.xml', settings = nonDefParam, title = 'IDE General Settings')
        # self.ideSettings.setNonDefaultParams(settingObj.result)
        # if settingObj.applySelected:
        #     self.ideSettings.save()
        #     self.processModIdeSettings(settingObj.applySelected)

    def checkCategoryChange(self, wbefore, wafter):
        '''
        Chequea si dos categorías de widget son diferentes, hace que la categoría asociada
        con wafter se muestre en pantalla.
        :param wbefore: str or tkinter widget. Widget or widget name que esta sociado a la
                        primera categoría.
        :param wafter: str or tkinter widget. Widget or widget name que esta sociado a la
                        segunda categoría.
        :return: None.
        '''
        # Es posible que wbefore sea None, lo convertimos en el string nulo
        wbefore = wbefore or ''
        # Con str(x) hacemos que si wbefore o wafter es un tkinter widget, lo convertimos en
        # el equivalente a su camino y se identifica el widgete id en el treeview como el
        # último componente de esta cadena.
        wbefore, wafter = tuple(map(lambda x: str(x).rsplit('.', 1)[-1], (wbefore, wafter)))
        # Se convierte el widget id en widget path.
        frame1, frame2 = tuple(map(lambda x: self.treeview.item(x, 'path'), (wbefore, wafter)))
        # Se entiende que la categoría es el primer segmento del path.
        frame1, frame2 = tuple(map(lambda x: x.lstrip('.').split('.', 1)[0], (frame1, frame2)))
        if frame1 != frame2:
            top_widget = self.parent_frame
            if frame1:
                top_widget.nametowidget(frame1).pack_forget()
            top_widget.nametowidget(frame2).pack(side='top', fill='y', expand='yes')

    def doTreeviewSelect(self, event=None):
        top_widget = self.parent_frame
        try:
            prevNodeId, prevNodeColor = self.treeFocusAct
            widget = top_widget.nametowidget(prevNodeId)
        except:
            frame_old = None
        else:
            widget.config(bg=prevNodeColor)
            frame_old = prevNodeId

        treeview = self.treeview
        nodeid = frame_new = treeview.focus()
        values = treeview.item(nodeid, 'values')
        try:
            nodeid = values[0]
            widget = top_widget.nametowidget(nodeid)
        except:
            self.treeFocusAct = None
        else:
            self.checkCategoryChange(frame_old, frame_new)
            bflag = self.treeFocusAct is None or self.treeSelectAct is None
            bflag = bflag or self.treeSelectAct[0] != nodeid
            node_colour = widget.cget('bg') if bflag else 'light green'
            widget.config(bg='black')
            self.treeFocusAct = (nodeid, node_colour)
        pass

    def onTreeActiveSelection(self, event):
        treeview = event.widget
        actualNode = treeview.focus()
        prevNode = treeview.tag_has('activenode')
        if prevNode:
            prevNode = prevNode[0]
            treeview.item(prevNode, tags=[])
        treeview.item(actualNode, tags=('activenode',))
        treeview.selection_set(actualNode)

        top_widget = self.parent_frame
        colour = self.treeSelectAct[1] if self.treeSelectAct else '#d9d9d9'
        pairs = [(prevNode, colour), (actualNode, 'light green')]
        # if self.treeSelectAct and self.treeSelectAct[0] == self.treeFocusAct[0]:
        #     pairs = pairs[:1]
        for nodeid, bgcolor in pairs:
            try:
                path, values = treeview.item(nodeid, 'values')
                nodeid = path
                widget = top_widget.nametowidget(nodeid)
            except:
                self.treeSelectAct = None
            else:
                values = eval(values)
                bflag = self.treeFocusAct is None or nodeid != self.treeFocusAct[0]
                node_colour = widget.cget('bg') if bflag else self.treeFocusAct[1]
                self.treeSelectAct = (nodeid, node_colour)
                widget.config(bg=bgcolor)

        wattr = self.ui_view.winfo_children()[0]
        getattr(wattr, 'widget_tag').setValue(values.pop('tag'))
        parameters = self.getWidgetParams(widget, values)
        getattr(wattr, 'widget_attrs').setValue(parameters, sep=('|', '*'))

    def getWidgetParams(self, widget, xml_config):
        '''
        Obtiene los parámetros de configuración y geomanager del widget "name"
        :param widget: tkinter obj. Widget a procesar
        :return: dict. Diccionario con dos keys, una configure y la otra geomanager.
        '''
        treeview = self.treeview
        geo_info = widget.winfo_manager()
        bflag = bool(geo_info)
        if not bflag:
            # Si el widget no es visible en pantalla, averiguamos por el geomanager
            # en el padre.
            master_id = treeview.parent(widget.winfo_name())
            values = eval(treeview.item(master_id, 'values')[1])
            geo_info = values.get('geomanager', 'pack')
        # Se filtran los valores de configuración en el xml (xml_config) correspondientes
        # al geomanager.
        geomngr_params = findGeometricManager(geo_info)
        geomngr_keys = xml_config.keys() & geomngr_params
        dummy = {key: xml_config.pop(key) for key in geomngr_keys}
        # Los valores filtrados se utilizan cuando el widget no es visible en pantalla.
        geomanager = getattr(widget, geo_info + '_info')() if bflag else dummy

        config = {}
        for param, values in widget.configure().items():
            try:
                _, _, _, _, value = values
            except:
                continue
            config[param] = value
        config.update(xml_config)
        parameters = {'config': config, geo_info: geomanager}

        seq = -1
        bdParams = []
        for key, params in parameters.items():
            seq += 1
            node_id = f'ND{seq}'
            bdParams.append(('', node_id, key))
            for param, value in sorted(params.items()):
                seq += 1
                bdParams.append((node_id, f'ND{seq}', param, value))
        value = '|'.join(['*'.join(str(y) for y in x) for x in bdParams])
        return value

    def saveFile(self):
        nameFile = self.currentFile
        self.saveAsFile(nameFile)

    def saveAsFile(self, nameFile=None):
        if not nameFile:
            D = os.path.abspath('../Data/')
            name = tkFileDialog.asksaveasfilename(
                initialdir=D,
                title='File Name to save',
                defaultextension='.xml',
                filetypes=[('xml Files', '*.xml'), ('All Files', '*.*')]
            )
            if not name:
                return
        else:
            name = nameFile
        try:
            xmlstr, _, _ = self.codeFrame.getContent()
            with open(name, 'wb') as f:
                f.write(xmlstr.encode('utf-8'))
        except Exception as e:
            tkMessageBox.showerror('Error', str(e))
        else:
            self.currentFile = name if name.endswith('.xml') else name + '.xml'
            self.setSaveFlag(False)
        pass

    def __openFile(self, name=None):
        self.checkSaveFlag()
        initial_path = os.path.abspath('../data/tkinter/')
        name = name or tkFileDialog.askopenfilename(
            initialdir=initial_path,
            filetypes=[('xml Files', '*.xml'), ('All Files', '*.*')]
        )
        if name is None:
            return
        with open(name, 'rb') as f:
            xmlstr = f.read()
        try:
            panel = ET.XML(xmlstr).find('category')
        except IOError:
            tkMessageBox.showerror('Not a valid File', 'File not xml compliant ')
            return
        except ValueError:
            tkMessageBox.showerror('Not a valid File', 'An error has ocurred while reding the file ')
            return
        default_name = os.path.join(initial_path, 'LayoutDefault.xml')
        if name != default_name:
            self.recFile(name)

        self.currentFile = name
        self.title(self.currentFile)

        if self.activeViewIndx.get() == 0:
            self.init_XMl_View(xmlstr)
        else:
            self.init_UI_View(xmlstr)

    def init_XMl_View(self, xmlstr):
        self.codeFrame.setContent(
            (xmlstr, 'xml', self.currentFile),
            inspos='1.0',
            sintaxArray=SintaxEditor.XMLSINTAX
        )
        self.codeFrame.textw.edit_modified(1)

    def init_UI_View(self, xmlstr):
        treeview = self.treeview
        treeview.delete(*treeview.get_children())
        self.treeFocusAct = self.treeSelectAct = None

        ui_pane = self.parent_frame
        fframes = ui_pane.winfo_children()[1:]
        [fframe.destroy() for fframe in fframes]
        try:
            panel = ET.XML(xmlstr)
            self.setupForms(panel, treeview, ui_pane)
        except Exception as e:
            tk.Label(ui_pane, text=str(e)).pack()
        self.treeview.edit_modified(1)

    def mapWidgetToTree(self, master, xmlwidget, widget, tree, indx='end'):
        # En este momento no se hace nada con las variables
        if xmlwidget.tag == 'var':
            return
        widget_attribs = xmlwidget.attrib
        widget_attribs['tag'] = xmlwidget.tag
        widget_attribs.pop('name', None)
        if xmlwidget.tag == 'category':
            parent_id = ''
            caption = '%s: %s' % (xmlwidget.tag, widget_attribs['label'])
        else:
            # geomanager = widget.winfo_manager()
            # parent = getattr(widget, geomanager + '_info')()['in']
            parent_id = master.winfo_name()
            caption = xmlwidget.tag
        child_id = widget.winfo_name()
        child_id = tree.insert(
            parent_id,
            indx,
            iid=child_id,
            text=caption,
            values=(str(widget), str(widget_attribs))
        )

    def setupForms(self, panel, treeview, formRoot):
        seq = -1
        for category_panel in panel.findall('category'):
            root, master = category_panel, formRoot
            widget_name, widget_attribs = root.tag, root.attrib
            seq += 1
            widget_attribs['name'] = str(seq)
            attributes = {
                'text': widget_attribs['label'],
                'name': '%s' % seq,
            }
            widget = getWidgetInstance(
                master,
                'labelframe',
                attributes,
            )
            # En este punto se debería hacer pack sobre cada nodo de categoría con la
            # siguiente expresión:
            # widget.pack(side='top', fill='both', expand='yes')
            # Pero como todos los paneles de las categorías deben estaar ocultos, no lo hacemos.
            # Cuando se defina el foco inicial se activará (Se hara pack) sobre el nodo escogido.

            self.mapWidgetToTree(master, category_panel, widget, tree=treeview)
            seq = widgetFactory(
                widget,
                category_panel,
                setParentTo='root',
                registerWidget=lambda master, category, widget: self.mapWidgetToTree(master, category, widget, tree=treeview),
                k=seq
            )
        equations_manager.set_initial_widget_states()
        self.seq = seq
        # Nos aseguramos que el treeview tenga el foco.
        treeview.focus_set()
        # Nos aseguramos que la primera categoría obtenga el foco
        treeview.focus('0')
        treeview.selection_set('0')

    def recFile(self, filename):
        try:
            ndx = self.fileHistory.index(filename)
        except:
            pass
        else:
            self.fileHistory.pop(ndx)
        self.fileHistory.insert(0, filename)
        # D = os.path.dirname(filename)
        # self.ideSettings.setParam('appdir_data', D)
        # nmax = self.ideSettings.getParam("file_opendoc").split('|', 1)[0]
        # nmax = int(nmax)
        nmax = 5
        self.fileHistory = self.fileHistory[:nmax]
        # self.ideSettings.setParam('var_fileHistory', json.dumps(self.fileHistory))
        # self.ideSettings.save()

    def checkSaveFlag(self):
        fileName = self.title()
        if fileName.endswith('**'):
            fileName = os.path.basename(self.currentFile) if not self.currentFile else 'default.pck'
            ans = tkMessageBox.askyesno('Warning', 'Do you want to save the changes you made to ' + fileName)
            if ans:
                self.saveFile()
            else:
                self.setSaveFlag(False)

    def setSaveFlag(self, state, lstChanged=None):
        suffix = '  **' if state else ''
        fileName = (self.currentFile if self.currentFile else 'default.pck') + suffix
        self.title(fileName)
        # if lstChanged:
        #     self.parseTree.refreshTreeInfo(lstChanged = lstChanged)
        #     self.addonId.set(self.addonSettings.getParam('addon_id'))

    def do_popup(self, event=None):
        iid = event.widget.identify_row(event.y)
        if iid:
            popup_menu = tk.Menu(self, tearoff=0)
            [
                popup_menu.add_command(
                    label=item,
                    command=lambda x=item: self.modifyTree(event, x)
                ) for item in ['Insert', 'Delete', 'Move']
            ]

            x, y = event.x_root, event.y_root
            try:
                popup_menu.tk_popup(x, y)
            finally:
                popup_menu.grab_release()
                pass

    def modifyTree(self, event, event_type):
        treeview = event.widget
        iid = treeview.identify_row(event.y)
        if event_type == 'Insert':
            xmlDlg = '/mnt/c/Users/Alex Montes/PycharmProjects/mywidgets/Data/kodi/InsertWidgetDialog.xml'
            dlg = CustomDialog(self, title='Insert Widget', xmlFile=xmlDlg, isFile=True)
            if dlg.allSettings:
                # treeview = self.treeview
                parent = treeview.focus()
                values = eval(treeview.item(parent, 'values')[1])
                tag = values.pop('tag')
                selPane = ET.Element(tag, values)

                allSettings = dict(dlg.allSettings)
                tag = allSettings['widget']
                attribs = allSettings['parameters']
                if allSettings['lib']:
                    attribs += f' lib="{allSettings["lib"]}"'
                nodo = ET.XML(f'<{tag} {attribs} />')

                selPane.append(nodo)

                master = self.parent_frame
                master = master.children[parent]
                self.seq = widgetFactory(
                    master,
                    selPane,
                    setParentTo='root',
                    registerWidget=lambda category, widget: self.mapWidgetToTree(category, widget, tree=treeview),
                    k=self.seq
                )
        elif event_type == 'Delete':
            answ = tkMessageBox.askquestion(
                'Delete widget',
                'Do you relly wants to delete the %s widget' % iid,
                icon=tkMessageBox.QUESTION
            )
            if answ == 'yes':
                widget = self.parent_frame[iid]
                widget.destroy()
                treeview.delete(iid)
        elif event_type == 'Move':
            widget_name = treeview.focus()
            # A través del treeview.parent se tiene la ubicación donde va a quedar el widget.
            parent_name = treeview.parent(widget_name)
            widget = self.parent_frame.children[widget_name]
            geo_manager = widget.winfo_manager()
            geo_info = getattr(widget, geo_manager + '_info')()
            # A través de la geo_info['in'] se tiene de donde se movió el widget.
            geo_master = geo_info['in'].winfo_name()
            if geo_master != parent_name:
                parent_widget = self.parent_frame.children[parent_name]
                parent_attrs = eval(treeview.item(parent_name, 'values')[1])
                new_geo_manager = parent_attrs.get('geomanager', 'pack')
                if geo_manager != new_geo_manager:
                    # Se tienen diferentes geo_manager
                    # Priemro eliminamos de values la información relativa al
                    # viejo geo_manager
                    wpath, values = treeview.item(widget_name, 'values')
                    values = eval(values)
                    geo_params = findGeometricManager(geo_manager)
                    [values.pop(x) for x in values.keys() & geo_params]
                    treeview.item(widget_name, values=(wpath, str(values)))
                    # Actualizamos al nuevo geo_manager
                    geo_manager = new_geo_manager
                    # Como no se conoce los parámetros que el usuario quiera en el
                    # nuevo geo_manager, comenzamos con lo mínimo.
                    geo_info = {}
                geo_info['in'] = parent_widget
            if geo_manager == 'pack' and treeview.next(widget_name):
                next_name = treeview.next(widget_name)
                geo_info['before'] = self.parent_frame.children[next_name]
            self.checkCategoryChange(geo_master, parent_name)
            getattr(widget, geo_manager)(**geo_info)
            pass

    def Close(self):
        self.checkSaveFlag()
        self.destroy()
        pass


def main():
    root = tk.Tk()
    root.withdraw()
    mainWin = UIeditor()
    root.wait_window(mainWin)


if __name__ == "__main__":
    main()
