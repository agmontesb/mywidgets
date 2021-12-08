import os
import tkinter as tk
import tkinter.messagebox as tkMessageBox
import tkinter.filedialog as tkFileDialog
import xml.etree.ElementTree as ET

import CollapsingFrame
import SintaxEditor
from basicViews import formFrame
from TreeExplorer import TreeForm

class UIeditor(tk.Toplevel):
    def __init__(self):
        tk.Toplevel.__init__(self)
        self.activeViewIndx = tk.IntVar(value=-1)
        self.activeViewIndx.trace("w", self.setActiveView)
        self.rightPaneIndx = tk.IntVar(value=-1)
        self.fileHistory = []

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

    def setUpPaneCtrls(self):
        m1 = self.vPaneWindow
        self.testFrame = CollapsingFrame.collapsingFrame(m1, tk.VERTICAL, inisplit=0.2, buttConf='RM')
        self.codeFrame = SintaxEditor.SintaxEditor(m1, hrzSlider=True)
        self.avRightPanes = [self.codeFrame, self.testFrame]
        self.viewPanes = [('XML', 0), ('UI', 1)]

    def setActiveView(self, *args, **kwargs):
        activeView = self.activeViewIndx.get()
        self.actViewPane = activeView
        viewName, vwRightPane = self.viewPanes[activeView]

        # leftPaneIndx = self.leftPaneIndx.get()
        # if leftPaneIndx != vwLeftPane:
        #     self.setLeftPane(vwLeftPane)
        #
        # refreshFlag = kwargs.get('refreshFlag', False)
        # if refreshFlag or leftPaneIndx != vwLeftPane:
        #     self.avLeftPanes[vwLeftPane].refreshPaneInfo()

        rightPaneIndx = self.rightPaneIndx.get()
        if rightPaneIndx != vwRightPane:
            self.setRightPane(vwRightPane)
        # if refreshFlag or rightPaneIndx != vwRightPane:
        #     self.avRightPanes[vwRightPane].initFrameExec()

    def setRightPane(self, rightPaneIndx):
        actRightPane = int(self.rightPaneIndx.get())
        if actRightPane != -1:
            pane = self.avRightPanes[actRightPane]
            pane.pack_forget()
        self.rightPaneIndx.set(rightPaneIndx)
        pane = self.avRightPanes[rightPaneIndx]
        pane.pack(fill=tk.BOTH, expand=1)

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
            if self.fileHistory:
                self.menuBar['File'].delete(frstIndx, tk.END)
                for k, filename in enumerate(self.fileHistory):
                    flabel = os.path.basename(filename)
                    self.menuBar['File'].add(
                        'command',
                        label='{} {:30s}'.format(k+1, flabel),
                        command=lambda x=filename: self.__openFile(x)
                    )
                self.menuBar['File'].add('separator')
            self.menuBar['File'].add('command', label='Settings', accelerator='Ctrl+S',
                                             underline=0, command=self.dummyCommand)
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
        initial_path = os.path.abspath('../data/')
        default_name = os.path.join(initial_path, 'LayoutDefault.xml')
        self.__openFile(name=default_name)

    def treeChangeListener(self, prevNode, actualNode):
        ui_pane = self.testFrame.scndWidget
        fframe = ui_pane.winfo_children()[0]
        for nodeid, bgcolor in zip((prevNode, actualNode), ('#d9d9d9', 'yellow')):
            try:
                nodeid = nodeid.rsplit('/', 1)
                widget = getattr(fframe, nodeid[1])
            except:
                pass
            else:
                widget.config(bg=bgcolor)

    def saveFile(self):
        nameFile = self.currentFile
        self.saveAsFile(nameFile)

    def saveAsFile(self, nameFile=None):
        # if not nameFile:
        #     D = os.path.abspath(self.ideSettings.getParam(srchSett='appdir_data'))
        #     name = tkFileDialog.asksaveasfilename(initialdir=D, title='File Name to save', defaultextension='.pck',
        #                                           filetypes=[('pck Files', '*.pck'), ('All Files', '*.*')])
        #     if not name: return
        # else:
        #     name = nameFile
        # try:
        #     with open(name, 'wb') as f:
        #         objetos = [self.xbmcThreads.getThreadData(), self.addonSettings.getNonDefaultParams(),
        #                    self.coder.modSourceCode]
        #         for objeto in objetos:
        #             # objStr = json.dumps(objeto)
        #             # f.write(objStr + '\n')
        # except:
        #     tkMessageBox.showerror('Error', 'An error was found saving the file')
        # else:
        #     self.currentFile = name if name.endswith('.pck') else name + '.pck'
        #     self.setSaveFlag(False)
        pass

    def __openFile(self, name=None):
        self.checkSaveFlag()
        initial_path = os.path.abspath('../data/')
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

        self.codeFrame.setContent((xmlstr, 'xml', self.currentFile), inspos=tk.END)
        ui_pane = self.testFrame.scndWidget
        for child in ui_pane.winfo_children():
            child.destroy()
        formFrame(ui_pane, {}, panel).pack(side=tk.TOP, fill=tk.Y, expand=tk.YES)
        ui_pane = self.testFrame.frstWidget
        for child in ui_pane.winfo_children():
            child.destroy()
        tform = TreeForm(ui_pane, panel)
        tform.setChangeListener(self.treeChangeListener)
        tform.refreshPaneInfo()
        tform.pack(side=tk.TOP, fill=tk.Y, expand=tk.YES)

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
