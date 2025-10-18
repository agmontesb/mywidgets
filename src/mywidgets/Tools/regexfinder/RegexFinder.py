import tkinter as tk
import tkinter.messagebox as tkMessageBox
import urllib.parse
import queue
import platform

import mywidgets.userinterface as userinterface
from mywidgets.equations import equations_manager
import mywidgets.Tools.uiStyle.MarkupRe as MarkupRe


class RegexFinder(tk.Tk):

    def __init__(self):
        super().__init__()
        # self.event_add('<<MENUCLICK>>', 'None')
        # self.event_add('<<VAR_CHANGE>>', 'None')
        # self.bind_all('<<MENUCLICK>>', self.onMenuClick)
        # self.bind_all('<<VAR_CHANGE>>', self.onVarChange)

        # self.project_path = '/mnt/c/Users/Alex Montes/PycharmProjects/mywidgets'
        self.dropDownFiler = None
        self.popUpMenu = None
        self.queue = queue.Queue(maxsize=0)
        self.activeCallBack = []
        self.threadFlag = 'stop'
        self.messageVar = tk.StringVar()

        self.setGui()
        if platform.system() == 'Windows':
            self.attributes('-zoomed', True)
        else:
            self.state('zoomed')
        pass

    def onMenuClick(self, event):
        pass

    def onVarChange(self, event):
        var_name, value = event.attr_data
        # print(f'var_change: var_name: {var_name}, value: {value}')
        if var_name == 'view_sel':
            if value == 0:
                self.hframe.hide_band('bottom')
            else:
                self.hframe.show_band()
        elif var_name in ('tree_top_sel', 'tree_btm_sel'):
            visible = sum(equations_manager.var_values[x] for x in ('tree_top_sel', 'tree_btm_sel'))
            if visible:
                self.vframe.show_band()
            else:
                self.vframe.hide_band('left')
        pass

    def setGui(self):
        file_path = '@layout/regexfinder'
        xmlObj = userinterface.getLayout(file_path, withCss=False)
        userinterface.newPanelFactory(
            master=self,
            selpane=xmlObj,
            genPanelModule=None,
            setParentTo='master',
            registerWidget=self.register_widget,
        )
        equations_manager.set_initial_widget_states()

        self.urlFrame.setUrlContentProcessor(self.setContent)
        self.regexBar.messageVar = self.messageVar
        self.regexBar.setZoomManager(self.zoom)

        self.txtEditor.setKeyHandler(self)
        self.txtEditor.setHyperlinkManager(self.hyperLnkMngr)
        self.regexBar.setTextWidget(self.txtEditor.textw)
        self.regexBar.setTreeWidget(self.tree)
        self.txtEditor.textw.bind('<Button-3>', self.do_popup)
        self.statusBar.Message.config(textvariable=self.messageVar)

    def register_widget(self, master, xmlwidget, widget):
        attribs = xmlwidget.attrib
        name = attribs.get('name')
        if name in ('urlFrame', 'regexBar', 'txtEditor', 'tree', 'statusBar',):
            setattr(self, name, widget)
        pass

    def isZoomed(self):
        return self.regexBar.butKeyMaker.cget('text') != 'ZoomIn'

    def zoom(self, btnText):
        if btnText == 'ZoomIn':
            selRange = self.txtEditor.getSelRange() or self.txtEditor.getSelRange('actMatch')
            if not selRange:
                return False
            zinBuff = [self.txtEditor.scrbar.get(), selRange]
            textw = self.txtEditor.textw
            height = textw.winfo_height()
            zinBuff.append((textw.index(tk.INSERT), textw.index('@0,%s' % (height // 2))))
            regExPat = self.getRegexpPattern()
            prefix = self.regexBar.cbIndex.get()
            zinBuff.append((prefix, regExPat))
            self.regexBar.anchorPos.append(zinBuff)
            self.regexBar.butAnchor['state'] = tk.DISABLED
            if regExPat.startswith('(?#<SPAN>)'):
                self.setActiveUrl()
            texto = self.txtEditor.getContent(*selRange)
            try:
                htmlParse = MarkupRe.ExtRegexParser({}, []).htmlStruct(texto)
            except:
                tkMessageBox.showinfo('Actual match HTMLstruct', 'Not HTML conform')
            else:
                for (pins, _), path, _ in reversed(htmlParse):
                    texto = texto[:pins] + f'<!-- {path} -->' + texto[pins:]
            self.setContent(texto, False)
            self.setRegexpPattern('<!-- .+? -->')
            return True
        else:
            self.urlFrame.returnKey()
            return False

    def setDropDownFiler(self, callbckFunc):
        self.regexBar.setDropDownFiler(callbckFunc)

    def do_popup(self, event):
        if not self.popUpMenu: return
        popup = self.popUpMenu()
        try:
            popup.post(event.x_root, event.y_root)
        finally:
            popup.grab_release()

    def setPopUpMenu(self, popUpMenu):
        self.popUpMenu = popUpMenu

    def keyHandler(self, event):
        textw = event.widget
        if textw == self.txtEditor.textw and event.keysym not in ['Left', 'Right', 'Up', 'Down', 'Next', 'Prior',
                                                                  'Button-1']:
            return "break"

    def getSelRange(self, tagName='sel'):
        return self.txtEditor.getSelRange(tagName)

    def setContent(self, data, newUrl=True):
        self.txtEditor.setContent(data)
        self.regexBar.getPatternMatch()
        if self.regexBar.getZoomType() == 'ZoomOut' and (
                len(self.regexBar.anchorPos) - self.regexBar.anchor.get()) == 1:
            zinBuff = self.regexBar.anchorPos.pop()
            textw = self.txtEditor.textw
            posIni, posFin = zinBuff[1]
            textw.mark_set('tk::anchor1', posIni)
            textw.tag_add('sel', posIni, posFin)
            insPos, wndFIN = zinBuff[2]
            textw.mark_set(tk.INSERT, insPos)
            textw.see(wndFIN)
            prefix, regExPat = zinBuff[3]
            self.regexBar.cbIndex.set(prefix)
            self.setRegexpPattern(regExPat)
            self.regexBar.butAnchor['state'] = tk.NORMAL
        if newUrl: self.regexBar.setZoomType('ZoomIn')

    def pasteFromClipboard(self, event=None):
        textw = self.txtEditor.textw
        try:
            data = textw.selection_get(selection='CLIPBOARD')
            self.setContent(data)
        except tk.TclError:
            pass
        else:
            self.urlFrame.setActiveUrl('')

    def getContent(self, posIni='1.0', posFin='end'):
        return self.txtEditor.getContent(posIni, posFin)

    def getRegexpPattern(self, *args, **kwargs):
        return self.regexBar.getRegexpPattern(*args, **kwargs)

    def getCompFlags(self):
        return self.regexBar.getCompFlags()

    def setRegexpPattern(self, regexp):
        self.regexBar.setRegexpPattern(regexp)

    def setCompFlags(self, compflags):
        self.regexBar.setCompFlags(compflags)

    def hyperLnkMngr(self, url):
        baseurl = self.urlFrame.getActiveUrl()
        url = urllib.parse.urljoin(baseurl, url)
        self.urlFrame.setActiveUrl(url)
        # self.setContent(content)

    def setActiveUrl(self, url=None):
        if url:
            if self.regexBar.anchorPos:
                self.regexBar.anchorPos = []
                self.regexBar.anchor.set(0)
            self.urlFrame.setActiveUrl(url)

    def getActiveUrl(self):
        return self.urlFrame.getActiveUrl()


def mainOLD():
    import tkinter as tk
    from mywidgets.Widgets.Custom.regexframe import StatusBar, RegexpFrame

    top = tk.Tk()
    # top.attributes('-zoomed', True)
    top.state('zoomed')
    message = tk.StringVar()
    status_list = [('Message:', message)]
    sb = StatusBar(top, status_list)
    sb.pack(side=tk.BOTTOM, fill=tk.X, expand=0)
    rgf = RegexpFrame(top, message)
    rgf.pack(side=tk.TOP, fill=tk.BOTH, expand=tk.YES)
    top.mainloop()

def main():
    html_str = '''
        <beg num="1">
            <blk1 num="2" />
            <span num="3">
                <blk1 num="4">
                    <span num="5"/>
                    <blk1 num="5.5" />
                    <span num="5.6"/>
                </blk1>
            </span>
            <blk1></blk1>
            <blk12></blk12>
            <out num="6">
                <blk1 num="7">
                    <row num="8">
                        <p num="9"/>
                        <p num="10"/>
                        <p num="11"/>
                    </row>
                </blk1>
            </out>
            <blk1 num="12" />
        </beg>
    '''
    top = RegexFinder()
    top.setContent(html_str)
    top.mainloop()


if __name__ == '__main__':
    main()
