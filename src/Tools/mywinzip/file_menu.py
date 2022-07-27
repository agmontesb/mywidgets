import os
import tkinter as tk
import tkinter.messagebox as tkMessageBox
import tkinter.filedialog as tkFileDialog
from contextlib import contextmanager

import userinterface


class FileMenu:

    def __init__(self, master):
        self.master = master
        self.currentFile = ''
        self.default_file_name = 'LayoutDefault.xml'
        self.default_path = '../Data/'
        self.default_extension = '.xml'
        self.default_file_type = ('xml Files', '*.xml')
        self.fileHistory = []
        self.max_file_history = 5

    def title(self, name=None):
        if name is None:
            return self.master.title()
        self.master.title(name)

    @contextmanager
    def saveFile(self):
        nameFile = self.title().strip(' **')
        nameFile = nameFile if nameFile != self.default_file_name else None
        with self.saveAsFile(nameFile) as name:
            yield name

    @contextmanager
    def saveAsFile(self, nameFile=None):
        name = nameFile
        if not name:
            D = os.path.abspath(self.default_path)
            name = tkFileDialog.asksaveasfilename(
                initialdir=D,
                title='File Name to save',
                defaultextension=self.default_extension,
                filetypes=[self.default_file_type, ('All Files', '*.*')]
            )
        if not name.endswith(self.default_extension):
            name += self.default_extension
        try:
            yield name
        finally:
            self.title(name)
            self.setSaveFlag(False)
        pass

    @contextmanager
    def openFile(self, name=None):
        self.checkSaveFlag()
        initial_path = os.path.abspath(self.default_path)
        name = name or tkFileDialog.askopenfilename(
            initialdir=initial_path,
            filetypes=[self.default_file_type, ('All Files', '*.*')]
        )
        try:
            yield name
        except:
            pass
        else:
            default_name = os.path.join(initial_path, self.default_file_name)
            if name != default_name:
                self.fileHistory = self.recFile(name)
            else:
                name = self.default_file_name
            self.title(name)

    @contextmanager
    def newFile(self, fileName='', xmlstr=None, panel=None):
        initial_path = os.path.abspath(self.default_path)
        default_name = os.path.join(initial_path, self.default_file_name)
        try:
            with self.openFile(name=default_name) as name:
                yield name
        finally:
            pass

    def checkSaveFlag(self):
        fileName = self.title()
        if fileName.endswith('**'):
            fileName = fileName.rstrip(' *')
            fileName = os.path.basename(fileName)
            ans = tkMessageBox.askyesno('Warning', 'Do you want to save the changes you made to ' + fileName)
            if ans:
                self.saveFile()
            else:
                self.setSaveFlag(False)

    def setSaveFlag(self, state):
        suffix = '  **' if state else ''
        fileName = self.title() if self.title() else self.default_file_name
        fileName = fileName.rstrip(' *') + suffix
        self.title(fileName)

    def recFile(self, filename, filenames=None):
        filenames = filenames or self.fileHistory
        if os.path.basename(filename) != self.default_file_name:
            try:
                ndx = filenames.index(filename)
            except:
                pass
            else:
                filenames.pop(ndx)
            filenames.insert(0, filename)
            nmax = self.max_file_history
            filenames = filenames[:nmax]
        return filenames

    def fileHist(self, menu_name, filenames=None):
        filenames = filenames or self.fileHistory
        lstIndx = menu_name.index(tk.END)
        menu_name.delete(0, lstIndx)
        for k, filename in enumerate(filenames, start=1):
            flabel = os.path.basename(filename)
            menu_name.insert_command(
                k,
                label='{} {:30s}'.format(k, flabel),
                command=userinterface.menuclick_closure(widget=menu_name, data=k)
            )


