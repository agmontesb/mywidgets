# -*- coding: utf-8 -*-
import os
import tkinter as tk
import traceback
import tkinter.messagebox as tkMessageBox
import tkinter.filedialog as tkFileDialog
import xml.etree.ElementTree as ET

import mywidgets.userinterface as userinterface
from mywidgets.Widgets.kodiwidgets import CustomDialog
from mywidgets.Widgets.Custom import SintaxEditor
from mywidgets.equations import equations_manager

R = type('Erre', (object,), {})


class UiEditor(tk.Tk):
    def __init__(self):
        super().__init__()
        self.event_add('<<MENUCLICK>>', 'None')
        self.bind_all('<<MENUCLICK>>', self.on_menuclick)

        self.currentFile = ''
        self.fileHistory = []
        self.treeFocusAct = None
        self.treeSelectAct = None
        self.seg = -1
        self.just_loaded = False

        self.setGui()
        self.newFile()
        # self.state = tk.NORMAL

        self.state('zoomed')
        pass

    def setGui(self):
        file_path = 'Data/tkinter/tkUiEditor.xml'
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

        self.widgetParams.widget_attrs.bind('<<OptionList_Edit>>', self.doOptionListEdit)
        self.codeFrame.textw.bind('<<Modified>>', self.onXmlTextModified)
        self.treeview.bind('<<Modified>>', self.onXmlTextModified)
        self.treeview.bind('<<ActiveSelection>>', self.onTreeActiveSelection)
        self.treeview.bind('<<TreeviewSelect>>', self.doTreeviewSelect)
        self.treeview.bind('<Button-3>', self.do_popup)
        self.treeview.bind("<ButtonRelease-1>", lambda event: self.modifyTree(event, 'Move'), add='+')

        # variables:
        self.activeViewIndx = equations_manager.state_equations['view_sel']
        self.activeViewIndx.trace_add('write', self.setActiveView)

        # Menu
        def fileHist(frstIndx):
            if self.fileHistory:
                lstIndx = self.file_menu.index(tk.END) - 3
                if lstIndx - frstIndx > 0:
                    self.file_menu.delete(frstIndx, lstIndx)
                self.file_menu.insert_separator(frstIndx)
                for k, filename in enumerate(self.fileHistory, start=1):
                    flabel = os.path.basename(filename)
                    self.file_menu.insert_command(
                        frstIndx + k,
                        label='{} {:30s}'.format(k, flabel),
                        command=lambda x=filename: self.openFile(x)
                    )

        insert_indx = self.file_menu.index(tk.END) - 2
        self.file_menu.config(postcommand=lambda x=insert_indx: fileHist(x))

    def register_widget(self, master, xmlwidget, widget):
        attribs = xmlwidget.attrib
        name = attribs.get('name')
        if name:
            if name in ('codeFrame', 'widgetParams', 'treeview', 'parent_frame'):
                setattr(self, name, widget)
            elif name == 'main_menu':
                menu_name = widget.children['master'].entrycget(0, 'menu')
                file_menu = widget.nametowidget(menu_name)
                setattr(self, 'file_menu', file_menu)

    def setActiveView(self, *args, **kwargs):
        activeView = self.activeViewIndx.get()
        if activeView == 'xml':
            if self.treeview.edit_modified():
                xmlstr = self.treeview.dump()
                self.init_XMl_View(xmlstr)
            self.treeview.edit_modified(0)
        elif activeView == 'ui':
            if self.codeFrame.textw.edit_modified():
                xmlstr, _, filename = self.codeFrame.getContent()
                xmlstr = userinterface.SignedContent(xmlstr, src=filename)
                try:
                    self.init_UI_View(xmlstr)
                    self.codeFrame.textw.edit_modified(0)
                except:
                    pass
        self.update_frame = False

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
            fileName = os.path.basename(self.currentFile) if not self.currentFile else 'LayoutDefault.xml'
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

    def init_XMl_View(self, xmlstr):
        self.codeFrame.setContent(
            (xmlstr, 'xml', self.currentFile),
            inspos='1.0',
            sintaxArray=SintaxEditor.XMLSINTAX
        )

    def init_UI_View(self, xmlstr):
        treeview = self.treeview
        treeview.delete(*treeview.get_children())
        self.treeFocusAct = self.treeSelectAct = None

        ui_pane = self.parent_frame
        fframes = ui_pane.winfo_children()[1:]
        [fframe.destroy() for fframe in fframes]
        try:
            panel = userinterface.getLayout(xmlstr, withCss=True, is_content=True)                 # ET.XML(xmlstr)
            self.setupForms(panel, treeview, ui_pane)
        except IOError:
            tkMessageBox.showerror('Not a valid File', 'File not xml compliant ')
            return
        except ValueError:
            tkMessageBox.showerror('Not a valid File', 'An error has occurred while rendering the file ')
            return
        except Exception as e:
            tkMessageBox.showerror('Not a valid File', 'An error has occurred while rendering the layout file ')
            msg = traceback.format_exc()
            tk.Message(ui_pane, text=f'{str(e)}\n{msg}').pack()
            raise e
        finally:
            self.treeview.edit_modified(0)

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
            widget = userinterface.getWidgetInstance(
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
            seq = userinterface.widgetFactory(
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

    def mapWidgetToTree(self, master, xmlwidget, widget, tree, indx='end'):
        # En este momento no se hace nada con las variables
        if xmlwidget.tag == 'var':
            child_id = str(widget)
        else:
            child_id = widget.winfo_name()
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
        tree.insert(
            parent_id,
            indx,
            iid=child_id,
            text=caption,
            values=(str(widget), str(widget_attribs))
        )

    # Bind callbacks

    def onXmlTextModified(self, event):
        if self.just_loaded:
            self.treeview.edit_modified(0)
            self.codeFrame.textw.edit_modified(0)
            self.just_loaded = False
        if event.widget.edit_modified():
            self.setSaveFlag(True)

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

        wattr = self.widgetParams
        wattr.widget_tag.setValue(values.pop('tag'))
        parameters = self.getWidgetParams(widget, values)
        wattr.widget_attrs.setValue(parameters, sep=('|', '*'))

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
        geomngr_params = userinterface.findGeometricManager(geo_info)
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
            top_widget.nametowidget(frame2).pack(side='top', fill='both', expand='yes')

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
            xmlDlg = userinterface.getLayout('Data/kodi/InsertWidgetDialog.xml')
            dlg = CustomDialog(self, title='Insert Widget', xmlFile=xmlDlg)
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
                    attribs += f' lib="mywidgets.{allSettings["lib"]}"'
                nodo = ET.XML(f'<{tag} {attribs} />')

                selPane.append(nodo)

                master = self.parent_frame
                master = master.children[parent]
                self.seq = userinterface.widgetFactory(
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
                    geo_params = userinterface.findGeometricManager(geo_manager)
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

    def destroy(self):
        self.checkSaveFlag()
        super().destroy()

    # Menu methods

    def saveFile(self):
        nameFile = self.currentFile.strip(' **')
        nameFile = nameFile if nameFile != 'LayoutDefault.xml' else None
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

    def openFile(self, name=None):
        self.checkSaveFlag()
        initial_path = os.path.abspath('../data/tkinter/')
        name = name or tkFileDialog.askopenfilename(
            initialdir=initial_path,
            filetypes=[('xml Files', '*.xml'), ('All Files', '*.*')]
        )
        if not name:
            return
        xmlstr = userinterface.getContent(name)
        try:
            # Se inicializa el UI_View para verificar que efectivamente el archivo es válido
            self.init_UI_View(xmlstr)
        except Exception:
            pass
        else:
            default_name = os.path.join(initial_path, 'LayoutDefault.xml')
            if name != default_name:
                self.recFile(name)
            # else:
            #     name = default_name # 'LayoutDefault.xml'
            self.currentFile = name
            self.title(self.currentFile)
            self.init_XMl_View(xmlstr)
            self.just_loaded = True

    def newFile(self, fileName='', xmlstr=None, panel=None):
        initial_path = os.path.join(os.path.dirname(__file__), '../Data/tkinter')
        initial_path = os.path.abspath(initial_path)
        default_name = os.path.join(initial_path, 'LayoutDefault.xml')
        self.openFile(name=default_name)

    def programSettingDialog(self):
        file_name = os.path.abspath('../Data/kodi/uiEditorSettings.xml')
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

    def callback1(self):
        msg = 'Hello from callback1'
        print(msg)
        tkMessageBox.showinfo(title='callback1', message=msg)

    def on_menuclick(self, event):
        menu_master, indx = event.widget, event.data
        msg = f'MENUCLICK fire. Menu: {menu_master.cget("title")}, Menu_item:{menu_master.entrycget(indx, "label")}'
        print(msg)
        tkMessageBox.showinfo(title='on_menuclick', message=msg)


def main():
    top = UiEditor()
    top.mainloop()

if __name__ == '__main__':
    main()