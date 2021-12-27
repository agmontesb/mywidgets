# -*- coding: utf-8 -*-
'''
Created on 20/02/2015

@author: Alex Montes Barrios
'''
import collections
import os
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox as tkMessageBox
import tkinter.messagebox as tkFileDialog
import tkinter.simpledialog as tkSimpleDialog
import re
import urllib
import zipfile
import operator
import xml.etree.ElementTree as ET
from PIL import Image, ImageTk

SEP = '/'
IMAGEFILES = ['.bmp', '.dcx', '.eps', '.gif', '.im', '.jpg', '.jpeg', '.pcd', '.pcx', '.pdf', '.png', '.ppm', '.psd',
              '.tiff', '.xbm', '.xpm']


class FilteredTree(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, padx=2, pady=2)
        self.onTreeSelProc = None
        self.popUpMenu = None
        self.resetVariables()
        self.setGUI()

    def resetVariables(self):
        self.activeSel = None
        self.editedContent = {}
        self.removedNodes = []
        self._activeNodes = []

    def setGUI(self):
        self.srchVar = tk.StringVar()
        self.srchVar.trace('w', self.filterTree)
        entry = tk.Entry(self, textvariable=self.srchVar)
        entry.pack(side=tk.TOP, fill=tk.X, padx=2, pady=2)
        bottompane = tk.Frame(self, padx=2, pady=2)
        bottompane.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=1)

        vscrollbar = tk.Scrollbar(bottompane)
        vscrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        hscrollbar = tk.Scrollbar(bottompane, orient=tk.HORIZONTAL)
        hscrollbar.pack(side=tk.BOTTOM, fill=tk.X)

        # imPath = os.path.abspath('./images/lockIcon.png')
        # lockImg = Image.open(imPath)
        # lockImg.thumbnail((15, 15), Image.ANTIALIAS)
        # self.lockImg = ImageTk.PhotoImage(lockImg)
        treeview = ttk.Treeview(bottompane, show='tree')
        treeview.pack(fill=tk.BOTH, expand=tk.YES)
        treeview.tag_configure('activeNode', background='light green')
        treeview.tag_configure('filterNode', foreground='red')
        # treeview.tag_configure('locked', image=self.lockImg)
        treeview.event_add('<<myEvent>>', '<Double-1>', '<Return>')
        treeview.bind('<<myEvent>>', self.onTreeSelEvent)
        treeview.bind('<Button-3>', self.do_popup)
        treeview.column('#0', width=400, stretch=False)

        treeview.config(xscrollcommand=hscrollbar.set, yscrollcommand=vscrollbar.set)
        vscrollbar.config(command=treeview.yview)
        hscrollbar.config(command=treeview.xview)
        self.treeview = treeview

    def setOnTreeSelProc(self, onTreeSelProc):
        self.onTreeSelProc = onTreeSelProc

    def setPopUpMenu(self, popUpMenu):
        self.popUpMenu = popUpMenu

    def filterTree(self, *args, **kwargs):
        for node, parent, index in self.removedNodes:
            self.treeview.move(node, parent, index)
        srchTxt = self.srchVar.get()
        allNodes = self.getAllNodes()
        for nodeId, nodeText in allNodes:
            self.treeview.item(nodeId, open=False)
        for nodeId, nodeText in allNodes:
            fltrTest = self.treeview.item(nodeId, 'open') or nodeText.find(srchTxt) != -1
            self.treeview.item(nodeId, open=fltrTest)
            if fltrTest: self.treeview.see(nodeId)

        self.removedNodes = self.getCloseNodes()
        for node, parent, index in self.removedNodes:
            self.treeview.detach(node)

    def getAllNodes(self, nodeId='', lista=None):
        lista = lista or []
        for node in self.treeview.get_children(nodeId):
            lista.append((node, self.treeview.item(node, 'text')))
            lista = self.getAllNodes(node, lista)
        return lista

    def getCloseNodes(self, nodeId='', lista=None):
        lista = lista or []
        for node in self.treeview.get_children(nodeId):
            if not self.treeview.item(node, 'open'):
                parent = self.treeview.parent(node)
                index = self.treeview.get_children(parent).index(node)
                lista.append((node, parent, index))
            else:
                lista = self.getCloseNodes(node, lista)
        return lista

    def onTreeSelEvent(self, event):
        if self.onTreeSelProc: self.onTreeSelProc(node=None)

    def do_popup(self, event):
        if self.popUpMenu: self.popUpMenu()

    def setActiveSel(self, newSel):
        if self.activeSel and self.treeview.exists(self.activeSel):
            iid = self.activeSel
            tags = self.treeview.item(iid, 'tags')
            tags = [tag for tag in tags if tag != 'activeNode']
            self.treeview.item(iid, tags=tags)

        iid = newSel
        if self.treeview.exists(iid):
            tags = list(self.treeview.item(iid, 'tags'))
            tags.append('activeNode')
            self.treeview.item(iid, tags=tags)
            self.activeSel = iid
            self.treeview.selection_set(iid)

class TreeForm(FilteredTree):
    def __init__(self, master, etreeRoot=None):
        FilteredTree.__init__(self, master)
        self.setExplorerParam(etreeRoot)
        # self.treeview.config(columns=('type', 'editable', 'source', 'inspos'), displaycolumns=())
        self.setOnTreeSelProc(self.onTreeSelection)
        self.setPopUpMenu(self.treeExpPopUpMenu)
        self.reportChange = True
        self.refreshFlag = False
        self.menuBar = {}
        self.changeListener = None

    def setChangeListener(self, callbackfunction):
        self.changeListener = callbackfunction

    def setExplorerParam(self, etreeRoot):
        self.resetVariables()
        self.etreeRoot = etreeRoot
        self.refreshFlag = True

    def getTreeFileStruct(self):
        root = list(self.treeview)
        root = root[0]
        toExclude = ['%s/Dependencies' % root]
        toAppend = ['%s/Dependencies/xbmc.python' % root]
        stack = [root]
        files = toAppend
        while stack:
            nodo = stack.pop()
            if nodo in toExclude:
                continue
            children = list(self.treeview)
            if children and not nodo.endswith('.py'):
                stack.extend(children)
            else:
                files.append(nodo)
        while toExclude:
            nodo = toExclude.pop()
            children = self.treeview.get_children(nodo)
            files.extend(children)
        return sorted(files)

    def insertTreeElem(self, parentid, elemid, elemName, values, refreshFlag=False):
        childId = SEP.join((parentid, elemid)) if parentid else elemid
        self.treeview.insert(
            parentid,
            'end',
            iid=childId,
            text=elemName,
            values=values
        )
        if refreshFlag:
            self.onTreeSelection(parentid)
        return childId

    def traverseTree(self):
        def isContainer(node):
            return node.tag in ['container', 'fragment']

        seq = 1
        root = self.etreeRoot
        pairs = [('', (root.tag + str(seq), root.tag, root.attrib))]
        parents = collections.deque()
        parents.append(('category1', self.etreeRoot))
        while parents:
            parentid, parent = parents.popleft()
            for child in list(parent):
                id = child.attrib.get('id', '')
                if not id:
                    seq += 1
                    id = '%s%s' % (child.tag, seq)
                else:
                    id = id.split('/')[-1]
                    child.attrib.pop('name')
                pairs.append((parentid, (id, child.tag, child.attrib)))
                if isContainer(child):
                    parents.append((id, child))
        return pairs

    def populateTree(self):
        tree = self.traverseTree()
        nodeIds = {}
        for parent, (child, child_name, child_attrib) in tree:
            parentid = nodeIds.get(parent, '')
            childid = self.insertTreeElem(parentid, child, child_name, child_attrib.items())
            nodeIds[child] = childid
        self.onTreeSelection('category1')
        pass

    def refreshPaneInfo(self):
        self.populateTree()

    def processRawContent(self, nodeId, rawcontent):
        filesource = self.treeview.set(nodeId, 'source').split('::')
        filetype = os.path.splitext(filesource[-1])[1]
        if filetype in IMAGEFILES:
            try:
                from PIL import ImageTk  # @UnresolvedImport
            except:
                return tkMessageBox.showerror('Dependencies not meet',
                                              'For image viewing PIL is needed. Not found in your system ')
            else:
                self.image = ImageTk.PhotoImage(data=rawcontent)
                content = self.image
        elif filetype == '.zip':
            # fp = StringIO.StringIO(rawcontent)
            # rawcontent = zipfile.ZipFile(fp, 'r')
            content = '\n'.join(rawcontent.namelist())
        elif filetype == '.pck':
            # fp = StringIO.StringIO(rawcontent)
            # rawcontent = FileGenerator.vrtDisk(file=fp)
            addonfiles = [x[0] for x in rawcontent.listAddonFiles()]
            content = '\n'.join(sorted(addonfiles))
        else:
            content = rawcontent
        return content, rawcontent

    def onTreeSelection(self, node=None):
        nodeId = node or self.treeview.focus()
        prevActiveNode = self.setActiveNode(nodeId)
        try:
            self.changeListener(prevActiveNode, nodeId)
        except:
            pass

    def treeExpPopUpMenu(self):
        selNode = self.treeview.focus()
        if not selNode: selNode = ''
        itype = self.treeview.set(selNode, 'type')
        if itype in ['depfile', 'repfile', 'repdir']: return False
        self.menuBar['popup'] = tk.Menu(self, tearoff=False)
        menuOpt = []
        if itype == 'repdatadir':
            menuOpt.append(('command', 'AddonArchFile', 'Ctrl+A', 0, lambda x='addonfile': self.onInsertAddon(x)))
            menuOpt.append(('command', 'AddonDir', 'Ctrl+A', 0, lambda x='addondir': self.onInsertAddon(x)))
        else:
            menuOpt.append(('command', 'Rename', 'Ctrl+R', 0, self.onRename))
            if itype != 'root': menuOpt.append(('command', 'Delete', 'Ctrl+D', 0, self.onDelete))
            menuOpt.append(('separator',))
            menuOpt.append(('command', 'Properties', 'Ctrl+P', 0, self.dummyCommand))
            if itype == 'depdir':
                menuOpt = menuOpt[2:]
                menuOpt.insert(0, ('command', 'Delete', 'Ctrl+D', 0, self.onDelDependency))
            if itype == 'requires':
                menuOpt.pop(1)
                menuOpt.insert(0, ('command', 'New dependency', 'Ctrl+D', 0, self.onNewDependency))
                menuOpt.insert(1, ('separator',))
            if itype not in ['genfile', 'file', 'requires', 'depdir']:
                menuOpt.insert(0, ('cascade', 'Insert New', 0))
                menuOpt.insert(1, ('separator',))
        self.makeMenu('popup', menuOpt)

        if self.menuBar.get('popup' + SEP + 'Insert_New', None):
            menuOpt = []
            menuOpt.append(('command', 'Genfile', 'Ctrl+B', 0, self.dummyCommand))
            menuOpt.append(('command', 'File', 'Ctrl+A', 0, self.onInsertFile))
            menuOpt.append(('command', 'Dir', 'Ctrl+A', 0, self.onInsertDir))
            menuOpt.append(('command', 'Web Resource', 'Ctrl+A', 0, self.onInsertWeb))
            self.makeMenu('popup' + SEP + 'Insert_New', menuOpt)
        return True

    def do_popup(self, event):
        nodeId = self.treeview.identify_row(event.y)
        self.onTreeSelection(node=nodeId)
        self.popUpMenu()
        try:
            menu = self.menuBar['popup']
        except:
            pass
        else:
            menu.post(event.x_root, event.y_root)
            menu.grab_release()

    def dummyCommand(self):
        tkMessageBox.showerror('Not implemented', 'Not yet available')

    def setActiveNode(self, nodeId):
        self.treeview.see(nodeId)
        self.treeview.selection_set(nodeId)
        self.treeview.focus(nodeId)
        # itype = self.treeview.set(nodeId, 'type')
        activeNode = self.activeSel
        self.setActiveSel(nodeId)
        return activeNode or ''

    def setEditorWidget(self, editorWidget):
        self.editorWidget = editorWidget

    def registerNode(self, iid, childName=None):
        treeview = self.treeview
        if treeview.exists(iid): return
        iidPart = iid.rpartition(SEP)
        if len(iidPart[1]) and not treeview.exists(iidPart[0]):
            self.registerNode(iidPart[0], childName)
        nodeValues = self.treeview.item(iidPart[0], 'values')
        treeview.insert(iidPart[0], 'end', iid, values=nodeValues)
        if childName:
            treeview.item(iid, text=iidPart[2])

    def onDelDependency(self):
        iid = self.treeview.focus()
        self.vrtDisc.modDependencies('delete', iid, None)
        self.treeview.delete(iid)
        iid = iid.rpartition('/')[0]
        self.onTreeSelection(iid)

    def onNewDependency(self, iid=None, newDependency=None):
        iid = iid or self.treeview.focus()

        # if not newDependency or not os.path.dirname(newDependency):
        #     from xbmc import translatePath
        #     addonsPath = translatePath('special://home/addons')
        #     if not newDependency:
        #         newDependency = tkFileDialog.askdirectory(title='New dependency', initialdir=addonsPath, mustexist=True)
        #     else:
        #         newDependency = os.path.join(addonsPath, newDependency)

        bFlag = os.path.exists(newDependency)
        # if not os.path.exists(newDependency):
        #     newDependency = tkFileDialog.askdirectory(title = newDependency + 'not found, please set new dependency', initialdir = addonsPath, mustexist=True)

        if not bFlag: return
        xmlfile = ET.parse(os.path.join(newDependency, 'addon.xml')).getroot()
        addonVer = xmlfile.get('version')
        source = os.path.basename(newDependency)
        self.vrtDisc.modDependencies('insert', source, addonVer)
        self.insertDirectory(iid, newDependency, values=('depdir', 0, source, addonVer), excludeext=('.pyc', '.pyo'))
        self.vrtDisc.hasChange = True

    def insertDirectory(self, dirParent=None, dirName=None, values=None, excludeext=None):
        if not dirName:
            dirName = tkFileDialog.askdirectory()
        dirName = os.path.normpath(dirName + os.sep)
        head, destino = os.path.split(dirName)
        idBaseDir = self.insertFolder(dirParent, destino)
        values = values or ()
        excludeext = excludeext or ()
        self.treeview.item(idBaseDir, values=values)
        itype, edit, source, inspos = values
        itype = 'depfile' if itype == 'depdir' else 'file'
        inspos = '1.0'
        source = dirName
        for dirname, subshere, fileshere in os.walk(source):
            for fname in fileshere:
                if os.path.splitext(fname)[1] in excludeext: continue
                fsource = os.path.join(dirname, fname)
                relpath = os.path.relpath(fsource, source).strip('.').replace(os.sep, SEP)
                nodeId = idBaseDir + SEP + relpath
                self.registerNode(nodeId, childName=True)
                self.treeview.item(nodeId, values=(itype, edit, fsource, inspos))

    def insertFolder(self, folderParent=None, folderName=None):
        parentId = folderParent or self.treeview.focus()
        if not folderName:
            folderName = tkSimpleDialog.askstring('Insert nuevo elemento', 'Nombre del nuevo elemento a incluir:')
        childId = parentId + SEP + folderName
        self.registerNode(childId, childName=True)
        colValues = self.treeview.item(parentId, 'values')
        self.treeview.item(childId, values=colValues)
        self.treeview.item(parentId, open=True)
        self.treeview.selection_set(childId)
        self.treeview.focus(childId)
        return childId

    def getContentOutline(self, rawcontent, moduleID):
        sourcetype = self.treeview.set(moduleID, 'source').rsplit('::', 1)[-1]
        sourcetype = os.path.splitext(sourcetype)[1]
        if sourcetype == '.py':
            xbmcThread = self.vrtDisc._menuthreads
            fileTree = self.getTextTree(rawcontent, prefix=moduleID)
            for child in sorted(fileTree):
                self.registerNode(child[0], child[1])
                self.treeview.set(child[0], column='type', value='markpos')
                self.treeview.set(child[0], column='source', value=(child[2], child[3]))
                self.treeview.set(child[0], column='inspos', value='1.0 + %d chars' % child[2])
                if xbmcThread.existsThread(child[1]) and xbmcThread.isthreadLocked(child[1]):
                    self.treeview.item(child[0], tags=('locked',))
        elif sourcetype in ['.zip', '.pck']:
            if sourcetype == '.zip':
                nodelist = rawcontent.namelist()
            elif sourcetype == '.pck':
                nodelist = map(operator.itemgetter(0), rawcontent.listAddonFiles())
            self.treeview.set(moduleID, column='type', value='depdir')
            zsource = self.treeview.set(moduleID, column='source')
            for child in sorted(nodelist):
                childId = moduleID + '/' + child
                self.registerNode(childId, True)
                # values = (itype, isEditable, source, inspos)
                values = ('file', 'False', zsource + '::' + child, '1.0')
                self.treeview.item(childId, values=values)
            self.treeview.set(moduleID, column='type', value='file')

    def getTextTree(self, text, prefix=''):
        prefixID = ''
        fileTree = []
        tIter = re.finditer('^([ \t]*)(def|class)[ \t]+([^\(:)]*).*:', text, re.MULTILINE)
        for match in tIter:
            indent = (match.end(1) - match.start(1)) / 4 if match.group(1) else 0
            while prefixID.count(SEP) and indent <= prefixID.count(SEP) - 1:
                prefixID = prefixID.rpartition(SEP)[0]
            prefixID = prefixID + SEP + match.group(2) + '(' + match.group(3) + ')'
            prefixMOD = prefix + prefixID if prefix else prefixID[1:]
            fileTree.append((prefixMOD, match.group(3), match.start(3), match.end(3)))
        return fileTree

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
                menuLabel = masterID + SEP + mLabel.replace(' ', '_')
                self.menuBar[menuLabel] = tk.Menu(master, tearoff=False)
                master.add('cascade',
                           label='{:30s}'.format(mLabel),
                           underline=mUnderline,
                           menu=self.menuBar[menuLabel])
            else:
                master.add('separator')

    def onRename(self):
        iid = self.treeview.focus()
        oldName = self.treeview.item(iid, 'text')
        newName = tkSimpleDialog.askstring('Rename', 'Input new name for ' + oldName, initialvalue=oldName)
        if newName:
            self.vrtDisc.modResources('rename', iid, None, None, newName)
            self.treeview.item(iid, text=newName)
            self.vrtDisc.hasChange = True

    def onDelete(self):
        iid = self.treeview.focus()
        self.vrtDisc.modResources('delete', iid, None, None, None)
        self.treeview.delete(iid)
        self.vrtDisc.hasChange = True
        iid = iid.rpartition('/')[0]
        self.onTreeSelection(iid)

    def onInsertWeb(self):
        webaddres = tkSimpleDialog.askstring('Web Resource', 'Enter url for the web resource')
        if not webaddres: return
        location = self.treeview.focus()
        urllib.URLopener.version = 'Mozilla/5.0 (Windows NT 6.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.112 Safari/537.36'
        opener = urllib.FancyURLopener()
        (fileSource, HttpMessage) = opener.retrieve(webaddres)
        fileName = os.path.basename(fileSource)
        srcName, srcExt = os.path.splitext(fileSource)
        if not srcExt:
            ContentType = HttpMessage.get('Content-Type')
            m = re.match(r'(\w+)/(\w+)(?:; charset=([-\w]+))*', ContentType)
            srcExt = m.group(2)
            fileName += srcExt
        isEditable = False
        self.insertTreeElem(location, fileName, 'file', isEditable, webaddres)

    def onInsertFile(self):
        pathName = tkFileDialog.askopenfilenames(
            filetypes=[('python Files', '*.py'), ('xml Files', '*.xml'), ('Image Files', '*.jpg, *.png'),
                       ('All Files', '*.*')])
        if not pathName: return
        location = self.treeview.focus()
        for fileSource in pathName:
            fileExt = os.path.splitext(fileSource)[1]
            fileName = os.path.basename(fileSource)
            isEditable = int(fileExt not in IMAGEFILES)
            self.insertTreeElem(location, fileName, 'file', isEditable, fileSource, refreshFlag=False)
        self.onTreeSelection(location)

    def onInsertDir(self):
        parent = self.treeview.focus()
        newDir = tkSimpleDialog.askstring('Insert directory', 'Input name for new directory')
        if not newDir: return
        self.insertTreeElem(parent, newDir, 'dir', True, '')

    def onInsertAddon(self, addonresource):
        if addonresource == 'addonfile':
            pathName = tkFileDialog.askopenfilenames(
                filetypes=[('AddonIDE Files', '*.pck'), ('Archive Files', '*.zip'), ('All Files', '*.*')])
            if not pathName: return
            location = self.treeview.focus()
            for fileSource in pathName:
                fileExt = os.path.splitext(fileSource)[1]
                fileName = os.path.basename(fileSource)
                if fileExt not in ['.zip', '.pck']: continue
                if fileExt == '.zip':
                    zfile = zipfile.ZipFile(fileSource)
                    filelist = zfile.namelist()
                # if fileExt == '.pck':
                #     zfile = FileGenerator.vrtDisk(file=fileSource)
                #     try:
                #         zfile.zipFileStr()
                #     except Exception as e:
                #         strMsg = "During insertion of %s, the following files weren't found:\n%s"
                #         tkMessageBox.showerror('Addon Insert', strMsg % (os.path.basename(fileSource),
                #                                                          str(e)))
                #         continue
                #     filelist = [x[0] for x in zfile.listAddonFiles()]
                addonId = filelist[0].split('/', 1)[0]
                addonxmlfile = '%s/addon.xml' % addonId
                if addonxmlfile not in filelist: continue
                if fileExt == '.zip':
                    addonxmlstr = zfile.read(addonxmlfile)
                elif fileExt == '.pck':
                    addonxmlstr = zfile.getPathContent(addonxmlfile)
                try:
                    version = re.search(r'<addon.+?version="([^"]+)".*?>', addonxmlstr).group(1)
                except:
                    continue
                dirname = '/'.join([location, addonId])
                self.insertTreeElem(location, addonId, 'dir', False, '', refreshFlag=False)
                addonzipfile = '%s-%s.zip' % (addonId, version)
                filelist = filter(lambda x: x.count('/') == 1 and not (x.endswith('.py') or x.endswith('.txt')),
                                  filelist)
                for fileName in filelist:
                    filesrc = '%s::%s' % (fileSource, fileName)
                    fileName = '%s/%s' % (location, fileName)
                    fileloc, fileName = os.path.split(fileName)
                    self.insertTreeElem(fileloc, fileName, 'file', False, filesrc, refreshFlag=False)
                self.insertTreeElem(dirname, addonzipfile, 'file', False, fileSource, refreshFlag=True)
            pass
        elif addonresource == 'addondir':
            addondir = tkFileDialog.askdirectory(title='Addon Directory', initialdir=os.path.abspath('.'),
                                                 mustexist=True)
            if not addondir: return
            addonxmlfile = os.path.join(addondir, 'addon.xml')
            if not os.path.exists(addonxmlfile):
                return tkMessageBox.showerror('Addon Directory',
                                              'The addon.xml file for this addon directory was not found')
            with open(addonxmlfile, 'rb') as fp:
                addonxmlstr = fp.read()
            try:
                addonId = re.search(r'<addon.+?id="([^"]+)".*?>', addonxmlstr, re.DOTALL).group(1)
                version = re.search(r'<addon.+?version="([^"]+)".*?>', addonxmlstr, re.DOTALL).group(1)
            except:
                tkMessageBox.showerror('Addon Directory', 'The addon.xml file does not have the required structure')
            location = self.treeview.focus()
            dirname = '/'.join([location, addonId])
            addonzipfile = '%s-%s.zip' % (addonId, version)
            self.insertTreeElem(location, addonId, 'dir', False, '', refreshFlag=False)
            filelist = os.walk(addondir).next()[2]
            filelist = filter(lambda x: os.path.splitext(x)[1] not in ('.md', '.py', '.txt', '.pyc', '.pyo'),
                              filelist)
            for fileName in filelist:
                filesrc = os.path.join(addondir, fileName)
                self.insertTreeElem(dirname, fileName, 'file', False, filesrc, refreshFlag=False)
            self.insertTreeElem(dirname, addonzipfile, 'depdir', False, addondir, refreshFlag=True)
        pass




