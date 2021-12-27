import collections
import importlib
import os
import re
import tkinter as tk
import tkinter.messagebox as tkMessageBox
import tkinter.filedialog as tkFileDialog
import xml.etree.ElementTree as ET

from Widgets.Custom import CollapsingFrame, SintaxEditor
from userinterface import getWidgetInstance, widgetFactory
from Widgets.kodiwidgets import formFrameGen, CustomDialog
from TreeExplorer import TreeForm

# Este es una especie de manejador de recursos que quiero implementar
R = type('Erre', (object, ), {})


class UIeditor(tk.Toplevel):
    def __init__(self):
        tk.Toplevel.__init__(self)
        self.activeViewIndx = tk.IntVar(value=-1)
        self.activeViewIndx.trace("w", self.setActiveView)
        self.rightPaneIndx = tk.IntVar(value=-1)
        self.fileHistory = []
        self.treeFocusAct = None
        self.treeSelectAct = None

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
        if self.codeFrame.textw.edit_modified():
            self.setSaveFlag(True)

    def setUpPaneCtrls(self):
        m1 = self.vPaneWindow
        self.ui_view = tk.Frame(m1, name='ui_view', bg='grey')
        self.codeFrame = SintaxEditor.SintaxEditor(m1, hrzslider=True)
        self.codeFrame.textw.bind(
            '<<Modified>>',
            self.onXmlTextModified
        )

        widgetParams = formFrameGen(
            self.ui_view,
            filename=os.path.join('../data/kodi/', 'WidgetParams.xml')
        )
        widgetParams.pack(side=tk.RIGHT, fill=tk.Y, expand=tk.YES, anchor=tk.E)
        widgetParams.widget_attrs.bind('<<OptionList_Edit>>', self.doOptionListEdit)

        self.testFrame = CollapsingFrame.collapsingFrame(
            self.ui_view,
            tk.VERTICAL,
            inisplit=0.2,
            buttconf='RM',
            bg='yellow'
        )
        self.testFrame.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.YES)
        ui_pane = self.testFrame.frstWidget
        tform = TreeForm(ui_pane)
        tform.setChangeListener(self.treeChangeListener)
        # Esto me parece una salvajada pero va como inicio de concepto
        tform.treeview.bind('<<TreeviewSelect>>', self.doTreeviewSelect)
        # tform.refreshPaneInfo()
        tform.pack(side=tk.TOP, fill=tk.Y, expand=tk.YES)

        ui_pane = self.testFrame.scndWidget
        tk.Frame(ui_pane).pack()

        # Para saber en que punto hizo click el mouse:
        self.bind_all('<1>', self.monitorMouseClick)

        self.avRightPanes = [self.codeFrame, self.ui_view]
        self.viewPanes = [('XML', 0), ('UI', 1)]

    def doOptionListEdit(self, event):
        widget = event.widget
        event_data = widget.virtualEventData
        # Se actualiza el widget Seleccionado segú la modificación dada
        name = self.treeSelectAct[0]
        obj = self.nametowidget(name)
        if event_data[0] == 'config':
            kwargs = {event_data[1]: event_data[2][0]}
            obj.config(**kwargs)
        # Se actualiza la información en el file tree que describe el formato.
        nodeid = obj.winfo_name()
        tform = self.testFrame.frstWidget.winfo_children()[0]
        values = eval(tform.treeview.item(nodeid, 'values')[1])
        values[event_data[1]] = event_data[2][0]
        tform.treeview.item(nodeid, values=(name, str(values)))
        self.setSaveFlag(True)

    def xmlTreeRep(self):
        xml_str = '<?xml version="1.0" encoding="utf-8" standalone="yes"?>\n<setting>\n'
        tform = self.testFrame.frstWidget.winfo_children()[0]
        treeview = tform.treeview
        to_process = collections.deque()
        indent_stack = [('', 'setting')]
        to_process.extend(treeview.get_children())
        while to_process:
            nodeid = to_process.popleft()
            attribs = eval(treeview.item(nodeid, 'values')[1])
            tag = attribs.pop('tag')
            attribs = ' '.join(f'{key}="{value}"' for key, value in attribs.items())
            parentid = treeview.parent(nodeid)
            children = treeview.get_children(nodeid)
            if children:
                to_process.extendleft(reversed(children))
                end_str = '>'
            else:
                end_str = '/>'
            while parentid != indent_stack[-1][0]:
                _, end_tag = indent_stack.pop()
                xml_str += f'{len(indent_stack) * "    "}</{end_tag}>\n'
            xml_str += f'{len(indent_stack) * "    "}<{tag} {attribs}{end_str}\n'
            if end_str == '>':
                indent_stack.append((nodeid, tag))
        while indent_stack:
            _, end_tag = indent_stack.pop()
            xml_str += f'{len(indent_stack) * "    "}</{end_tag}>\n'
        return xml_str

    def monitorMouseClick(self, event):
        widget = event.widget
        if 'collapsingframe.scndwidget' in str(widget):
            tform = self.testFrame.frstWidget.winfo_children()[0]
            while True:
                name = widget.winfo_name()
                if tform.treeview.exists(name):
                    break
                widget = widget.master
            # Nos aseguramos que el widget seleccionado obtenga el foco
            tform.treeview.focus(name)
            tform.treeview.selection_set(name)
            pass
        pass

    def setActiveView(self, *args, **kwargs):
        self.actViewPane = activeView = self.activeViewIndx.get()
        viewName, vwRightPane = self.viewPanes[activeView]

        rightPaneIndx = self.rightPaneIndx.get()
        if rightPaneIndx == vwRightPane:
            return
        self.setRightPane(vwRightPane)
        if vwRightPane == 1 and self.codeFrame.textw.edit_modified():
            xmlstr, _, _ = self.codeFrame.getContent()
            self.init_UI_View(xmlstr)

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
                        label='{} {:30s}'.format(k+1, flabel),
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
                menuType, mLabel, mAccelKey, mUnderline, mCommand =  menuDesc
                master.add(menuType,
                           label='{:30s}'.format(mLabel),
                            accelerator=mAccelKey,
                            underline=mUnderline,
                            command=mCommand)
            elif menuType == 'cascade':
                menuType, mLabel, mUnderline =  menuDesc
                menuLabel = masterID + '.' + mLabel.replace(' ', '_')
                self.menuBar[menuLabel] = tk.Menu(master, tearoff = False)
                master.add('cascade',
                           label = '{:30s}'.format(mLabel),
                           underline = mUnderline,
                           menu = self.menuBar[menuLabel])
            elif menuType == 'radiobutton':
                menuType, radioVar, radioOps = menuDesc
                for k, elem in enumerate(radioOps):
                    master.add_radiobutton(label = elem, variable = radioVar, value = k)
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
        with open(file_name, 'rb') as f:
            file_content = f.read()
        settingObj = CustomDialog(self, title='Application Settings', xmlFile=file_content, isFile=True, settings={})
        all_settings = settingObj.allSettings
        for key, value in all_settings:
            setattr(R, key, value)
        R.__dict__.update(all_settings)

        print(R.initial_path)
        # settingObj = AppSettingDialog(self, 'IDE_Settings.xml', settings = nonDefParam, title = 'IDE General Settings')
        # self.ideSettings.setNonDefaultParams(settingObj.result)
        # if settingObj.applySelected:
        #     self.ideSettings.save()
        #     self.processModIdeSettings(settingObj.applySelected)

    def doTreeviewSelect(self, event=None):
        top_widget = self.testFrame.scndWidget
        try:
            prevNodeId, prevNodeColor = self.treeFocusAct
            widget = top_widget.nametowidget(prevNodeId)
        except:
            frame_old = None
        else:
            frame_old = prevNodeId.split('scndwidget.', 1)[1].split('.', 1)[0]
            widget.config(bg=prevNodeColor)

        tform = self.testFrame.frstWidget.winfo_children()[0]
        treeview = tform.treeview
        nodeid = treeview.focus()
        values = treeview.item(nodeid, 'values')
        try:
            nodeid = values[0]
            widget = top_widget.nametowidget(nodeid)
        except:
            self.treeFocusAct = None
        else:
            frame_new = nodeid.split('scndwidget.', 1)[1].split('.', 1)[0]
            if frame_old and frame_old != frame_new:
                top_widget.nametowidget(frame_old).pack_forget()
            top_widget.nametowidget(frame_new).pack(side='top', fill='y', expand='yes')
            bflag = self.treeFocusAct is None or self.treeSelectAct is None
            bflag = bflag or self.treeSelectAct[0] != nodeid
            node_colour = widget.cget('bg') if bflag else 'light green'
            widget.config(bg='black')
            self.treeFocusAct = (nodeid, node_colour)
        pass

    def treeChangeListener(self, prevNode, actualNode):
        top_widget = self.testFrame.scndWidget
        tform = self.testFrame.frstWidget.winfo_children()[0]
        colour = self.treeSelectAct[1] if self.treeSelectAct else '#d9d9d9'
        pairs = [(prevNode, colour), (actualNode, 'light green')]
        # if self.treeSelectAct and self.treeSelectAct[0] == self.treeFocusAct[0]:
        #     pairs = pairs[:1]
        for nodeid, bgcolor in pairs:
            try:
                path, values = tform.treeview.item(nodeid, 'values')
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

        parameters = self.getWidgetParams(widget)
        wattr = self.ui_view.winfo_children()[0]
        getattr(wattr, 'widget_attrs').setValue(parameters, sep=('|', '*'))
        # wattr = self.ui_view.winfo_children()[0]
        # getattr(wattr, 'widget_tag').setValue(values.pop('tag'))
        # value = '#'. join(['*'.join((x, str(y))) for x, y in sorted(values.items())])
        # getattr(wattr, 'widget_attrs').setValue(value, sep=('#', '*'))

    def getWidgetParams(self, widget):
        '''
        Obtiene los parámetros de configuración y geomanager del widget "name"
        :param widget: tkinter obj. Widget a procesar
        :return: dict. Diccionario con dos keys, una configure y la otra geomanager.
        '''
        master = widget.master
        tform = self.testFrame.frstWidget.winfo_children()[0]
        path, values = tform.treeview.item(master.winfo_name(), 'values')
        m = re.search("'geomanager': '([a-z]+?)'", values)
        if m:
            geo_info = f'{m.group(1)}_info'
        else:
            geo_info = 'pack_info'
        geomanager = getattr(widget,geo_info)()
        config = {}
        for param, values in widget.configure().items():
            try:
                _, _, _, _, value = values
            except:
                continue
            config[param] = value
        parameters = {}
        parameters['config'] = config
        parameters[geo_info] = geomanager

        seq = -1
        bdParams = []
        for key, params in parameters.items():
            seq += 1
            node_id = f'ND{seq}'
            bdParams.append(('', node_id, key))
            for param, value in params.items():
                seq += 1
                bdParams.append((node_id, f'ND{seq}', param, value))
        value = '|'. join(['*'.join(str(y) for y in x) for x in bdParams])
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

        self.init_XMl_View(xmlstr)
        self.init_UI_View(xmlstr)

    def init_XMl_View(self, xmlstr):
        self.codeFrame.setContent(
            (xmlstr, 'xml', self.currentFile),
            inspos='1.0',
            sintaxArray=SintaxEditor.XMLSINTAX
        )
        # self.codeFrame.setCursorAt('1.0')
        self.codeFrame.textw.edit_modified(0)

    def init_UI_View(self, xmlstr):
        ui_pane = self.testFrame.frstWidget
        tform = ui_pane.winfo_children()[0]
        treeview = tform.treeview
        treeview.delete(*treeview.get_children())
        self.treeFocusAct = self.treeSelectAct = None

        ui_pane = self.testFrame.scndWidget
        fframes = ui_pane.winfo_children()[1:]
        [fframe.destroy() for fframe in fframes]
        try:
            panel = ET.XML(xmlstr)
            self.newSetupForms(panel, tform, ui_pane)
            self.xmlTreeRep()
        except Exception as e:
            tk.Label(ui_pane, text=str(e)).pack()
        else:
            self.codeFrame.textw.edit_modified(0)

    def newSetupForms(self, panel, treeForm, formRoot):
        def mapWidgetToTree(xmlwidget, widget):
            widget_attribs = xmlwidget.attrib
            widget_attribs['tag'] = xmlwidget.tag
            widget_attribs.pop('name', None)
            if xmlwidget.tag == 'category':
                parent_id = ''
                caption = '%s: %s' % (xmlwidget.tag, widget_attribs['label'])
            else:
                parent_id = widget.master.winfo_name()
                caption = xmlwidget.tag
            child_id = widget.winfo_name()
            child_id = treeForm.treeview.insert(
                parent_id,
                'end',
                iid=child_id,
                text=caption,
                values=(str(widget), str(widget_attribs))
            )
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
            #siguiente expresión:
            # widget.pack(side='top', fill='both', expand='yes')
            # Pero como todos los paneles de las categorías deben estaar ocultos, no lo hacemos.
            # Cuando se defina el foco inicial se activará (Se hara pack) sobre el nodo escogido.

            mapWidgetToTree(category_panel, widget)
            seq = widgetFactory(widget, category_panel, registerWidget=mapWidgetToTree, k=seq)[0]

        # Nos aseguramos que el treeview tenga el foco.
        treeForm.treeview.focus_set()
        # Nos aseguramos que la primera categoría obtenga el foco
        treeForm.treeview.focus('0')
        treeForm.treeview.selection_set('0')
        # # Se genera el evento <<TreeviewSelect>> para que se llame al método pack_forget
        # treeForm.treeview.event_generate(
        #     '<<TreeviewSelect>>',
        #     when='tail'
        # )

    def setupForms(self, panel, treeForm, formRoot):
        def isContainer(node):
            return len(list(node)) > 0

        seq = -1
        parents = collections.deque()
        for category_panel in panel.findall('category'):
            root, master = category_panel, formRoot
            panel_module = root.get('lib') if root.get('lib') else None
            if panel_module:
                panel_module = importlib.import_module(panel_module, __package__)

            widget_name, widget_attribs = root.tag, root.attrib
            widget_attribs['tag'] = widget_name
            seq += 1
            widget_attribs['name'] = 'wdg%s' % seq
            attributes = {
                'text': widget_attribs['label'],
                'name': widget_attribs['name'],
                'side': 'top',
                'fill': 'both',
                'expand': 'yes'
            }
            widget = getWidgetInstance(
                master,
                'labelframe',
                attributes,
                panelModule=panel_module
            )
            widget_attribs['tag'] = widget_name
            widget_attribs.pop('name')
            child_id = widget.winfo_name()
            treeForm.insertTreeElem(
                '',
                child_id,
                '%s: %s' % (widget_name, widget_attribs['label']),
                values=(str(widget), str(widget_attribs)))

            parents.append((child_id, root, widget))
            widget.pack_forget()
        parents[0][2].pack(fill=tk.BOTH, expand=tk.YES)
        while parents:
            parent_id, parent_node, master_widget = parents.popleft()
            for child in list(parent_node):
                widget_name, widget_attribs = child.tag, child.attrib
                seq += 1
                widget_attribs['name'] = 'wdg%s' % seq
                visible = True
                if 'visible' in widget_attribs:
                    visible = widget_attribs.pop('visible') == 'true'
                widget = getWidgetInstance(
                    master_widget,
                    widget_name,
                    widget_attribs,
                    panelModule=panel_module
                )
                if not visible:
                    widget.pack_forget()
                    widget_attribs['visible'] = 'false'
                widget_attribs['tag'] = widget_name
                widget_attribs.pop('name')
                child_id = widget.winfo_name()
                treeForm.insertTreeElem(
                    parent_id,
                    child_id,
                    widget_name,
                    values=(str(widget), str(widget_attribs)))
                if isContainer(child):
                    parents.append((parent_id + '/' + child_id, child, widget))

        # Nos aseguramos que el treeview tenga el foco.
        treeForm.treeview.focus_set()
        # Nos aseguramos que la primera categoría obtenga el foco
        treeForm.treeview.focus('wdg0')
        treeForm.treeview.selection_set('wdg0')
        # # Se genera el evento <<TreeviewSelect>> para que se llame al método pack_forget
        # treeForm.treeview.event_generate(
        #     '<<TreeviewSelect>>',
        #     when='tail'
        # )

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

    def setSaveFlag(self, state, lstChanged = None):
        suffix = '  **' if state else ''
        fileName = (self.currentFile if self.currentFile else 'default.pck') + suffix
        self.title(fileName)
        # if lstChanged:
        #     self.parseTree.refreshTreeInfo(lstChanged = lstChanged)
        #     self.addonId.set(self.addonSettings.getParam('addon_id'))

    def Close(self):
        self.checkSaveFlag()
        self.destroy()
        pass

if __name__ == "__main__":
    Root = tk.Tk()
    Root.withdraw()
    mainWin = UIeditor()
    Root.wait_window(mainWin)
