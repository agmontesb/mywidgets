# -*- coding: utf-8 -*-
'''
Created on 19/09/2015

@author: Alex Montes Barrios
'''
from collections import namedtuple
from operator import pos
import re
from timeit import template
import itertools
import operator
from html.parser import HTMLParser
import copy
import threading

RGXFLAGS = ['IGNORECASE', 'LOCALE', 'MULTILINE', 'DOTALL', 'UNICODE', 'VERBOSE']
RGXFLAGSPAT = ['i', 'L', 'm', 's', 'u', 'x']

CRGFLAGS = ['SPAN', 'PARAM']
CRGFLAGSPAT = ['(?#<SPAN>)', '(?#<PARAM>)']

FLAGS = RGXFLAGS + CRGFLAGS


def getCompFlagsPatt(compFlags):
    if compFlags == '0': return ''
    compFlags = compFlags.replace('re.', '')
    trnMap = dict(list(zip(RGXFLAGS + CRGFLAGS, RGXFLAGSPAT + CRGFLAGSPAT)))
    compFlags = ''.join([trnMap[x] for x in compFlags.split('|')])
    rgxflags = ''.join(re.findall(r'[iLmsux]', compFlags))
    crgflags = re.findall(r'\(\?#<[A-Z]+>\)', compFlags)
    crgflags = [x for x in crgflags if x in CRGFLAGSPAT]
    crgflags = ''.join(crgflags)
    if rgxflags: rgxflags = '(?%s)' % rgxflags
    return rgxflags + crgflags


def getCompFlags(flags):
    crgpat = r'\(\?\#\<[A-Z]+\>\)'
    pattern = r'^(\(\?[iLmsux]+\))*((?:%s)+)*' % crgpat
    rgxflags, crgflags = re.findall(pattern, flags)[0]
    trnMap = dict(list(zip(RGXFLAGSPAT, RGXFLAGS)))
    rgxflags = [trnMap[x] for x in rgxflags.strip('(?)')]
    trnMap = dict(list(zip(CRGFLAGSPAT, CRGFLAGS)))
    crgflags = [trnMap.get(x, None) for x in re.findall(crgpat, crgflags)]
    crgflags = [_f for _f in crgflags if _f]
    return rgxflags + crgflags


def getFlagsRegexPair(regexpat):
    crgpat = r'\(\?\#\<[A-Z]+\>\)'
    pattern = r'^(\(\?[iLmsux]+\))*((?:%s)+)*(.+)' % crgpat
    rgxflags, crgflags, regexp = re.findall(pattern, regexpat)[0]
    crgflags = re.findall(crgpat, crgflags)
    regexp = ''.join([x for x in crgflags if x not in CRGFLAGSPAT]) + regexp
    crgflags = ''.join([x for x in crgflags if x in CRGFLAGSPAT])
    return rgxflags, crgflags, regexp


class ExtRegexParser(HTMLParser):
    def __init__(self, varList=None, reqTags=None, optTags=None):
        HTMLParser.__init__(self)
        self.TAGPATT = r'<(?P<TAG>[a-zA-Z\d]+)(?P<ATTR>[^>]*)(?:>|/>)'
        self.ATTR_PARAM = r'(?P<ATTR>(?<=\W)[^\s]+(?==))=([\"\'])(?P<PARAM>(?<==[\"\']).*?)\2(?=[\W>])'
        self.master_pat = re.compile('|'.join([GENSELFTAG, GENTAG, ENDTAG, BLANKTEXT, DOCSTR, GENTEXT, SUFFIX]))

        varList = varList or []  # aqui 4
        self.reqTags = reqTags or {}
        self.optTags = optTags or {}
        self.pathIndex = []
        self.varDict = {}
        varNames = []
        for itemPath, itemKey in varList:
            self.pathIndex.append(itemPath)
            itemName = itemKey.strip('_') if itemKey != '__TAG__' else itemKey
            if itemName in varNames:
                k = varNames.index(itemName) + 1
            else:
                varNames.append(itemName)
                k = len(varNames)
            self.varDict[itemPath] = k
        self.varPos = [(-1, -1) for x in range(len(varNames) + 1)]
        self.totLen = 0
        pass

    def checkStartTag(self, data):
        tag = re.match(r'<([a-zA-Z\d]+)[\W >]', data).group(1)
        if 'tagpholder' not in self.reqTags: return True
        reqTags = dict(self.reqTags['tagpholder'])
        if '*' in reqTags: reqTags.pop('*')
        tagAttr = self.getAttrDict(data, 0)
        return self.haveTagAllAttrReq('tagpholder', tagAttr, reqTags)

    def htmlStruct(self, data, posIni):
        self.initParserVar()
        tagName = re.match(r'<([a-zA-Z\d]+)[\W >]', data).group(1)
        self.feed(data)
        if not self.tagList: return None
        tagList = sorted(self.tagList)
        self.setPathTag(tagList, rootName=tagName)
        return tagList

    def storeReqVars(self, tag, tagAttr, optValues):
        paramPos = tagAttr.pop('*ParamPos*')
        reqAttr = self.reqTags.get(tag, {})
        for attr in reqAttr:
            fullAttr = tag + ATTRSEP + attr
            if fullAttr not in self.varDict: continue
            k = self.varDict[fullAttr]
            if reqAttr[attr] and reqAttr[attr].groups:
                m = reqAttr[attr].match(tagAttr[attr])
                optValues[fullAttr] = self.trnCoord(m.span(1), paramPos[attr][0])
            else:
                optValues[fullAttr] = paramPos[attr]

        optAttr = self.optTags.get(tag, {})
        for attr in optAttr:
            fullAttr = tag + ATTRSEP + attr
            if attr not in paramPos: continue
            if optAttr[attr]:
                m = optAttr[attr].match(tagAttr[attr])
                if not m: continue
                if not optAttr[attr].groups:
                    optValues[fullAttr] = paramPos[attr]
                else:
                    offset = paramPos[attr][0]
                    optValues[fullAttr] = self.trnCoord(m.span(1), offset)
            else:
                optValues[fullAttr] = paramPos[attr]

    def haveTagAllAttrReq(self, tag, tagAttr, reqTags=-1):
        if reqTags == -1: reqTags = self.reqTags.get(tag, {})
        diffSet = set(reqTags.keys()).difference(list(tagAttr.keys()))
        interSet = set(reqTags.keys()).intersection(list(tagAttr.keys()))
        bFlag = diffSet or not all([reqTags[key].match(tagAttr[key]) for key in interSet if reqTags[key]])
        return not bFlag

    def getAllTagData(self, tagPos, data, tagList):
        posBeg, posEnd = tagList[tagPos][0]
        tagAttr = self.getAttrDict(data[:posEnd], posBeg)
        n = tagList[tagPos][2]
        if n is None:
            tagAttr['*'] = ''
            tagName = tagAttr['__TAG__']
            posBeg = posEnd = posEnd - len('</' + tagName + '>')
            tagAttr['*ParamPos*']['*'] = (posBeg, posEnd)
        elif n > 0:
            posBeg, posEnd = tagList[n][0]
            tagAttr['*'] = data[posBeg:posEnd]
            tagAttr['*ParamPos*']['*'] = tagList[n][0]
        return tagAttr

    def setPathTag(self, tagList, rootName='tagpholder', reqSet=-1):
        dadList = [-1]  # dadList[k] señala la posición del padre de tagList[k]
        no_reqSetFlag = reqSet == -1
        for k in range(len(tagList) - 1):
            indx = k + 1
            while 1:
                if tagList[indx][0][1] < tagList[k][0][1]:
                    dadList.append(k)
                    if tagList[indx][1] == '*': tagList[k][2] = indx
                    break
                k = dadList[k]

        pathDict = {}
        toProcess = []  # aqui 5
        tagList[0][1] = rootName
        if not no_reqSetFlag:
            if tagList[0][1] in reqSet: toProcess.append(0)
            reqSet.difference_update([tagList[0][1]])
            relPath = sorted([x for x in reqSet if x.find('..') != -1], key=lambda x: x.count('.'))
            efe = lambda x: not (pathTag.startswith(x.split('..')[0]) and pathTag.endswith(x.split('..')[1]))

        for k in range(1, len(tagList)):
            indx = dadList[k]
            pathTag = tagList[indx][1] + '.' + tagList[k][1]
            pathDict[pathTag] = pathDict.get(pathTag, 0) + 1
            if pathDict[pathTag] > 1: pathTag += '[' + str(pathDict[pathTag]) + ']'
            tagList[k][1] = pathTag
            if no_reqSetFlag: continue
            #             packedPath = pathTag if pathTag.count('.') < 3 else packPath(pathTag, pathTag.count('.'))
            if pathTag in reqSet:
                reqSet.difference_update([pathTag])
                toProcess.append(k)
            elif relPath:
                rpos = list(itertools.takewhile(efe, relPath))
                rpos = len(rpos) + 1
                if rpos <= len(relPath):
                    toProcess.append((k, relPath[rpos - 1]))
                    reqSet.difference_update([relPath.pop(rpos - 1)])
            if not reqSet: break
        if no_reqSetFlag: return None
        for k in range(len(toProcess)):
            m = toProcess[k]
            if isinstance(m, int): continue
            toProcess[k] = m[0]
            tagList[m[0]][1] = m[1]
        return toProcess

    @staticmethod
    def getAttrDict(data, offset=0, noTag=True):

        def skipCharsInSet(strvar, aSet, npos=0, peek=False):
            m = re.match('[' + aSet + ']+', strvar[npos:])
            res = m.group() if m else ''
            return (res, npos + len(res)) if not peek else res

        def getCharsNotInSet(strvar, aSet, npos=0, peek=False):
            res = re.split('[' + aSet + ']', strvar[npos:], 1)[0]
            return (res, npos + len(res)) if not peek else res

        WHITESPACE = ' \t\n\r\f\v'
        pini = offset
        pfin = data.find('>', pini) + 1
        tag = data[pini:pfin].strip('/>') + '>'

        npos = 1
        pmax = len(tag) - 1
        key = '__TAG__'
        attrD = {}
        attrPos = {}
        attrvalue, posfin = getCharsNotInSet(tag, '>' + WHITESPACE, npos)
        while 1:
            attrD[key] = attrvalue
            attrPos[key] = (npos + offset, posfin + offset)
            sep, npos = skipCharsInSet(tag, '\'"' + WHITESPACE, posfin)
            if npos >= pmax: break
            key, npos = getCharsNotInSet(tag, '=>' + WHITESPACE, npos)
            sep, npos = skipCharsInSet(tag, '=' + WHITESPACE, npos)
            if sep == "=":
                sep, npos = skipCharsInSet(tag, '\'"', npos)
                if sep:
                    posfin = npos
                    attr = sep
                    while 1:
                        attrInc, posfin = getCharsNotInSet(tag, '\'"', posfin)
                        # if len(attr) > 1 and attrInc[-1] in '=>' and attr[0] == attr[-1]: break
                        if len(attr) > 1 and attrInc[-1] in '=>' and attr[-1] in '\'"': break
                        attr += attrInc
                        sep, posfin = skipCharsInSet(tag, '\'"', posfin)
                        attr += sep
                    attrvalue = attr[1:-1]
                    posfin = npos + len(attrvalue)
                else:
                    attrvalue, posfin = getCharsNotInSet(tag, '>' + WHITESPACE, npos)
            else:
                attrvalue = ''
                posfin = npos

        attrD['*ParamPos*'] = attrPos
        return attrD if noTag else (attrD.pop('__TAG__'), attrD)

    def trnCoord(self, tupleIn, offset):
        offset = offset if tupleIn != (-1, -1) else 0
        return (tupleIn[0] + offset, tupleIn[1] + offset)

    def getTag(self, data):
        match = re.match(self.TAGPATT, data)
        return match.group('TAG')
        pass

    def initParse(self, data, posIni):
        if not self.checkStartTag(data): return None
        mtag = re.match(r'<([a-zA-Z\d]+)[^>]*>', data)
        pattEndTag = '</' + mtag.group(1) + '>' if mtag.group()[-2:] != '/>' else '/>'
        self.initParserVar()
        beg = 0
        while True:
            m = re.search(pattEndTag, data[beg:])
            if not m:
                self.tagList.append([mtag.span(), mtag.group(1), -1])
                break
            end = m.end() + beg
            self.feed(data[beg:end])
            if not self.tagStack: break
            beg = end
        self.reset()
        if not self.tagList: return None
        tagList = sorted(self.tagList)
        reqSet = set(self.reqTags.keys())
        optSet = set(self.optTags.keys()).difference(reqSet)
        reqSet = reqSet.union(optSet)
        toProcess = self.setPathTag(tagList, reqSet=reqSet)  # aqui 5
        reqSet.difference_update(optSet)
        if reqSet: return None
        if 'tagpholder..*' in self.varDict:
            self.varPos = [tagList[0][0]]
            self.varPos.extend([texto[0] for texto in tagList if texto[1][-1] == '*'])
            self.varDict = dict(('grp%s' % k, k) for k in range(1, len(self.varPos)))
        else:
            self.varPos = [(-1, -1) for x in range(len(self.varPos))]
            optValues = {}
            self.varPos[0] = tagList[0][0]
            for k in toProcess:
                tag = tagList[k][1]
                tagAttr = self.getAllTagData(k, data, tagList)
                if not self.haveTagAllAttrReq(tag, tagAttr): return None
                self.storeReqVars(tag, tagAttr, optValues)
            for key in self.pathIndex:
                value = optValues.get(key, None)
                if value is None: continue
                k = self.varDict[key]
                self.varPos[k] = value
        return [self.trnCoord(elem, posIni) for elem in self.varPos]

    def initParserVar(self):
        self.pos = 0
        self.totLen = 0
        self.tagStack = []
        self.tagList = []
        self.stackPath = ''

    def getSpan(self, entityStr):
        posini = self.pos
        self.pos = posfin = posini + len(entityStr)
        self.totLen += len(entityStr)
        return (posini, posfin)

    def handle_starttag(self, tag, attrs):
        posini, posfin = self.getSpan(self.get_starttag_text())
        self.stackPath += '.' + tag
        self.tagStack.append([tag, (posini, posfin)])

    def handle_endtag(self, tag):
        posini, posfin = self.getSpan('</%s>' % tag)
        dmy = self.stackPath + '.'
        rootTag, sep = dmy.rpartition('.%s.' % tag)[:2]
        if sep:
            self.stackPath = rootTag
            while 1:
                stckTag, stckTagSpan = self.tagStack.pop()
                bFlag = tag == stckTag
                if bFlag:
                    tagSpan = (stckTagSpan[0], posfin)
                else:
                    tagSpan = stckTagSpan
                self.tagList.append([tagSpan, stckTag, None])
                if bFlag: break

    def handle_startendtag(self, tag, attrs):
        posini, posfin = self.getSpan(self.get_starttag_text())
        # self.stackPath += '.' + tag
        self.tagList.append([(posini, posfin), tag, -1])

    def storeDataStr(self, dataIn):
        dSpanIn = self.getSpan(dataIn)
        if self.tagList and self.tagList[-1][1] == '*':
            dataSpan = self.tagList[-1][0]
            if dataSpan[1] == dSpanIn[0]:
                self.tagList[-1][0] = (dataSpan[0], dSpanIn[1])
                return
        if not dataIn.strip(' \t\n\r\f\v'): return
        self.tagList.append([dSpanIn, '*', None])

    def handle_data(self, data):
        self.storeDataStr(data)

    def handle_entityref(self, name):
        data = '&%s;' % name
        self.storeDataStr(data)

    def handle_charref(self, name):
        data = '&#%s;' % name
        self.storeDataStr(data)

    def handle_comment(self, data):
        posini, posfin = self.getSpan('<!--%s-->' % data)

    def handle_decl(self, data):
        posini, posfin = self.getSpan('<!%s>' % data)

    def handle_pi(self, data):
        posini, posfin = self.getSpan('<?%s>' % data)

    def unknown_decl(self, data):
        posini, posfin = self.getSpan('<![%s]>' % data)


# equis = """<img itemprop="contentURL" src="http://www.eltiempo.com/contenido/colombia/medellin/IMAGEN/IMAGEN-16428112-1.jpg" data-real-type='image' data-real-src2=""  alt=''Nada vale tanto como la paz': José Mujica en Medellín'>"""
# equis = """<img itemprop="contentURL'>"""
# equis = '<table>'
# newx = maskAttrib(equis)

# tag, attrD = NewGetAttrDict(equis, noTag = False)
# attrP = attrD.pop('*ParamPos*')
# print tag
# for key in sorted(attrD):
#     print key, attrD[key], attrP[key]


Token = namedtuple('Token', ['type', 'value'])

PREFIX = r'(?P<PREFIX>(?s).+(?=<!DOCTYPE))'
GENSELFTAG = r'(?P<GENSELFTAG><[a-zA-Z\d]+[^>]+/>)'
GENTAG = r'(?P<GENTAG><[a-zA-Z\d]+[^>]*>)'
DOCSTR = r'(?P<DOCSTR><!--.*?-->|<!D[^>]*>)'
BLANKTEXT = r'(?P<BLANKTEXT>(?<=>)\s+(?=<[a-z/]))'
GENTEXT = r'(?P<GENTEXT>(?<=>).+?(?=<[!a-z/]))'
ENDTAG = r'(?P<ENDTAG></[^>]+>)'
SUFFIX = r'(?P<SUFFIX>(?s)(?<=</html>).+)'


class ExtRegexObject:
    def __init__(self, pattern, flags, tagPattern, tags, varList, maskParam):
        self.pattern = pattern
        self.flags = flags
        self.tagPattern = tagPattern
        varNames = []
        self.groupindex = {}
        for itemPath, itemKey in varList:
            itemName = itemKey.strip('_') if itemKey != '__TAG__' else itemKey
            if itemName in varNames: continue
            varNames.append(itemName)
            self.groupindex[itemName] = len(varNames)
        self.varList = varList
        self.groups = len(self.groupindex)
        self._maskTags = maskParam
        self.searchFlag = None
        self.isSearchFlagSet = lambda: True if not self.searchFlag else self.searchFlag.is_set()

        self.tags = reqTags = tags
        self.optTags = opTags = {}

        optionalTags = [x[0] for x in varList if x[1] != '__TAG__' and x[1] != x[1].strip('_')]
        optionalPath = set()
        for item in optionalTags:
            itemPath, itemKey = item.rpartition(ATTRSEP)[0:3:2]
            value = reqTags[itemPath].pop(itemKey)
            optionalPath.add(itemPath)
            optAttrs = opTags.setdefault(itemPath, {})
            optAttrs[itemKey] = value
        while optionalPath:
            itemPath = optionalPath.pop()
            if not reqTags[itemPath]:
                reqTags.pop(itemPath)

        self.findTag = ExtRegexParser(self.varList, self.tags, self.optTags)
        rootTag = 'tagpholder'
        # if self.tags:
        #     rootTag = self.tags.keys()[0].partition('.')[0]
        excAttr = ['*', '__TAG__']
        for fullPath, itemName in self.varList:
            if itemName == itemName.strip('_'): continue
            itemPath, itemAttr = fullPath.rsplit(ATTRSEP, 1)
            if itemPath != rootTag: continue
            excAttr.append(itemAttr)
        diffSet = set(self.tags.get(rootTag, {}).keys()).difference(excAttr)
        if diffSet:
            myfunc = lambda x: '<' + self.tagPattern + '\s[^>]*' + '=[^>]+'.join(x) + '=[^>]+[/]*>'
            SRCHTAG = '|'.join(map(myfunc, itertools.permutations(diffSet, len(diffSet))))
        else:
            SRCHTAG = '<' + self.tagPattern + '(?:\s|>)'
        self.SRCHTAG = SRCHTAG
        pass

    def testMatch(self, origString, posIni):
        answ = self._maskTags[1]
        for maskTag in self._maskTags[0]:
            nPos = [-1, -1]
            for k in range(2):
                tagPos = 0 if posIni <= maskTag[k + 2] else maskTag[k + 2]
                nPos[k] = origString[tagPos:posIni].rfind(maskTag[k])
                if nPos[k] != -1: maskTag[k + 2] = nPos[k] + tagPos
            if maskTag[2] > maskTag[3]: answ = not self._maskTags[1]
        return answ

    def search(self, origString, spos=-1, sendpos=-1, parameters=None):
        pos = spos if spos != -1 else 0
        endpos = sendpos if sendpos != -1 else len(origString)
        findTag = self.findTag
        SRCHTAG = self.SRCHTAG

        # findTag = ExtRegexParser(self.varList, self.tags)
        # rootTag = self.tags.keys()[0].partition('.')[0]
        # excAttr = ['*', '__TAG__']
        # for fullPath, itemName in self.varList:
        #     if itemName == itemName.strip('_'): continue
        #     itemPath, itemAttr = fullPath.rsplit(ATTRSEP, 1)
        #     if itemPath != rootTag: continue
        #     excAttr.append(itemAttr)
        # diffSet = set(self.tags.get(rootTag,{}).keys()).difference(excAttr)
        # if diffSet:
        #     myfunc = lambda x: '<' + self.tagPattern + '\s[^>]*' + '=[^>]+'.join(x) + '=[^>]+[/]*>'
        #     SRCHTAG =  '|'.join(map(myfunc, itertools.permutations(diffSet,len(diffSet))))
        # else:
        #     SRCHTAG = '<' + self.tagPattern + '(?:\s|>)'
        master_pat = re.compile(SRCHTAG, re.DOTALL | re.IGNORECASE)
        posIni = pos
        self.testMatch(origString, posIni)

        varPos = None
        while self.isSearchFlagSet():
            match = master_pat.search(origString[posIni:endpos])
            if not match: return
            tagPos = match.start() + posIni
            if self.testMatch(origString, tagPos):
                varPos = findTag.initParse(origString[tagPos:], tagPos)
                if varPos: break
            posIni = match.end() + posIni
        if varPos is None: return
        if self.varList and 'tagpholder..*' in self.varList[0][0]:
            self.groups = len(varPos) - 1
            self.groupindex = dict(('grp%s' % k, k) for k in range(1, len(varPos)))
        return ExtMatchObject(self, origString, spos, sendpos, varPos, parameters)

    def match(self, string, pos=-1, endpos=-1):
        m = self.search(string, pos, endpos)
        return m if m.start() == 0 else None

    def split(self, string, maxsplit=0):
        answer = []
        lstPos = 0
        for k, match in enumerate(self.finditer(string)):
            if maxsplit and k + 1 > maxsplit: break
            posIni, posFin = match.span()
            answer.append(string[lstPos:posIni])
            lstPos = posFin
            if match.groups(): answer.extend(match.groups())
        if lstPos != len(string): answer.append(string[lstPos:])
        return answer

    def findall(self, string, pos=-1, endpos=-1):
        answ = []
        for m in self.finditer(string, pos, endpos):
            ngroups = len(m.groups())
            if ngroups > 1:
                answ.append(m.groups())
            else:
                answ.append(m.group(ngroups))
        return answ

    def finditer(self, string, pos=-1, endpos=-1):
        def iterTag():
            match = self.search(iterTag.ese, iterTag.posIni, iterTag.posFin)
            if not match: return None
            iterTag.posIni = match.end()
            return match

        iterTag.__dict__ = dict(ese=string, posIni=pos, posFin=endpos)
        return iter(iterTag, None)

    def sub(self, repl, string, count=0):
        pass

    def subn(self, repl, string, count=0):
        pass


class zinwrapper(ExtRegexObject):
    def __init__(self, pattern, flags, spanRegexObj, srchRegexObj, zone='zin'):
        """
        zone indica la zona de [posINI:posFIN] en que se limitara la búsqueda de
        srchRegexObj, con relación a la zona [pos:endpos] de spanRegexObj. Sera:
             zin      --> para zona [pos:endpos]
             zoutr    --> para zona [endpos:posFIN]
             zoutl    --> para zona [posINI:pos]
        """
        # try:
        #     tagPattern, tags, varList, maskParam = srchRegexObj.tagPattern, srchRegexObj.tags, srchRegexObj.varList, srchRegexObj._maskTags
        # except:
        #     tagPattern, tags, varList, maskParam = "", {}, [], []
        #
        # ExtRegexObject.__init__(self, pattern, flags,tagPattern, tags, varList, maskParam)

        self.__dict__['spanRegexObj'] = spanRegexObj
        self.__dict__['srchRegexObj'] = srchRegexObj
        self.zone = zone
        self.parameters = namedtuple('zinparams', sorted(spanRegexObj.groupindex.keys()))
        self.spanDelim = self.params = None
        pass

    @property
    def searchFlag(self):
        return self.srchRegexObj.searchFlag

    @searchFlag.setter
    def searchFlag(self, value):
        self.srchRegexObj.searchFlag = value
        self.spanRegexObj.searchFlag = value

    def findSpan(self, string, posIni, posFin):
        offset = posIni
        if isinstance(self.spanRegexObj, ExtRegexObject):
            string = string[posIni:posFin]
            posIni = offset + re.match(GENTAG, string).end()
            posFin = offset + re.search(ENDTAG + '\Z', string).start()
        return posIni, posFin

    def delimiter(self, string, pos, endpos):
        if endpos == -1: endpos = len(string)
        if self.spanDelim == None:
            srchFunc = getattr(self.spanRegexObj, 'search')
            match = srchFunc(string, pos, endpos)
            if not match: return None
            self.params = params = self.parameters(**match.groupdict())
            if self.zone == 'zin':
                self.spanDelim = self.findSpan(string, *match.span())
                answ = self.spanDelim
            elif self.zone == 'zoutr':
                self.spanDelim = match.span()
                answ = ExtCompile('(?#<__TAG__>)', 0)
                answ = answ.search(string, match.end(), endpos)
                answ = answ.span()
            elif self.zone == 'zoutl':
                self.spanDelim = match.span()
                answ = pos, match.start()
            return answ + (params,)
        limInf, limSup = self.spanDelim
        if limInf <= pos < limSup:
            return pos, min(limSup, endpos), self.params
        self.spanDelim = self.params = None
        return self.delimiter(string, limSup, endpos)

    def search(self, string, pos=0, endpos=-1):
        spanDelim = self.delimiter(string, pos, endpos)
        if not spanDelim: return None
        posIni, posFin, parameters = spanDelim
        srchFunc = getattr(self.srchRegexObj, 'search')
        match = srchFunc(string, posIni, posFin, parameters)
        if match:
            return match
        posFin = self.spanDelim[1]
        return self.search(string, posFin, endpos)

    def __getattr__(self, attr):
        return getattr(self.__dict__['srchRegexObj'], attr)

    def __setattr__(self, attr, value):
        return setattr(self.__dict__['srchRegexObj'], attr, value)


class ExtMatchObject:
    def __init__(self, regexObject, htmlstring, pos, endpos, varPos, parameters=None):
        self.pos = pos
        self.enpos = endpos
        self.lastindex = 0
        self.lastgroup = 0
        self.groupindex = dict.copy(regexObject.groupindex)
        self.re = regexObject
        self.string = htmlstring
        self.varpos = varPos
        self.parameters = parameters
        pass

    def _varIndex(self, x):
        nPos = self.groupindex[x] if isinstance(x, str) else int(x)
        if nPos > len(self.varpos): raise Exception
        return nPos

    def expand(self, template):
        pass

    def group(self, *grouplist):
        if not grouplist: grouplist = [0]
        answer = []
        for group in grouplist:
            posIni, posFin = self.span(group)
            answer.append(self.string[posIni:posFin])
        return answer if len(answer) > 1 else answer[0]

    def groups(self, default=None):
        trn = lambda x: (self.string[x[0]:x[1]], None)[1 * (x == (-1, -1))]
        return tuple(map(trn, self.varpos[1:]))
        # return tuple(self.string[tpl[0]:tpl[1]] or None for tpl in self.varpos[1:])

    def groupdict(self, default=None):
        keys = sorted(list(self.groupindex.keys()), key=lambda x: self.groupindex[x])
        values = self.groups()
        return dict(list(zip(keys, values)))

    def start(self, group=0):
        return self.span(group)[0]

    def end(self, group=0):
        return self.span(group)[1]

    def span(self, group=0):
        nPos = self._varIndex(group)
        return self.varpos[nPos]


ATTRSEP = '.'
COMMSEP = '*'

"""
EJEMPLO DEL RESUULTADO DE COMPILAR LOS PATTERNS

++++++++++++++++++++
>>> req = compile(r'(?#<TAG a>)', 0)
>>> req.tags
{'a': {}}
>>> req.varList
[]

+++++++++++++++++++
(?#<TAG a href>)
****
(?#<TAG a href>)
{'a': {'href': ''}}
[]

+++++++++++++++++++
(?#<TAG a *>)
****
(?#<TAG a *>)
{'a': {'*': ''}}
[]


+++++++++++++++++++
(?#<TAG a href=url>)
****
(?#<TAG a href=url>)
{'a': {'href': ''}}
[['a.href', 'url']]

+++++++++++++++++++
(?#<TAG a href="/">)
****
(?#<TAG a href="/">)
{'a': {'href': <_sre.SRE_Pattern object at 0x03631CB8>}}
[]
a {'href': '/\\Z'}

"""


def ExtCompile(regexPattern, flags=0):
    '''
    Analiza el regexPattern para encontrar: tag pattern, required attrs y sus patterns asociados,
     las variables a entregar.
     tag pattern: (?#<tagpattern .........>) o (?#<tagpattern>). El tagpattern puede ser el nombre
     del elemento (a, div, table, input, etc) o una expresión válida de re (cas[a-zA-Z3], *.+?, etc)
     required attrs: Son los atributos asociados a un elemento. Estos pueden referirse al elemento
     requerido o el de uno cualquiera de sus descendientes. Para designar un descendiente de primer nivel
     precedemos el nombre con el camino que llega a el separando los elementos que lo contienen con
     un punto table.a.div.span.* se refiere a el comentario del elemento span que desciende de table
     pasando por a y div (es decir span es bisnieto de a.
    :param regexPattern:
    :param flags:
    :return:
    '''
    def skipCharsInSet(strvar, aSet, npos=0, peek=False):
        m = cmp_patt__in[aSet].match(strvar, npos)
        res = m.group() if m else ''
        return (res, npos + len(res)) if not peek else res

    def getCharsNotInSet(strvar, aSet, npos=0, peek=False):
        m = cmp_patt_not[aSet].match(strvar, npos)
        res = m.group() if m else ''
        return (res, npos + len(res)) if not peek else res

        # r'''
        # \(\?\#\w<                               # Prefix Tag for CustomRegEx
        # \(*                                     # Inicio de grupo
        # (?P<tagpattern>[a-zA-Z]\S*|__TAG__)     # Toda palabra que comience con una letra o __TAG__
        # \)*                                     # Fin de grupo
        # (?P<vars>[^>]*>)                        # Lo que no es >
        # \)                                      # Sufix Tag for CustomRegEx
        # '''

    match = re.search(
        '\(\?#<\(*(?P<tagpattern>[a-zA-Z]\S*|__TAG__)\)*(?P<vars>[^>]*>)\)',
        regexPattern
    )
    if not match:
        answ = re.compile(regexPattern, flags)
    else:
        WHITESPACE = ' \t\n\r\f\v'
        ATTRSEP = '.'
        PATH_MOD = '{'
        PATH_RES = '}'
        END_PAT = '>'
        PARAM_DEL = '\'"'
        EQ = '='
        ATTR_RDEL = PATH_MOD + EQ + END_PAT + WHITESPACE
        ATTR_LDEL = PARAM_DEL + WHITESPACE

        TAG_PATT = END_PAT + WHITESPACE
        ATTR_PATT = PATH_RES + ATTR_RDEL
        PARAM_PATT = PARAM_DEL
        VAR_PATT = EQ + PATH_RES + END_PAT + ATTR_LDEL

        cmp = re.compile
        cmp_patt_not = dict([
            ('TAG_PATT', cmp('[^' + TAG_PATT + ']+')),          # [^> \t\n\r\f\v]+
            ('ATTR_PATT', cmp('[^' + ATTR_PATT + ']+')),        # [^}{=> \t\n\r\f\v]+
            ('PARAM_PATT', cmp('[^' + PARAM_PATT + ']+')),      # [^\'"]+
            ('VAR_PATT', cmp('[^' + VAR_PATT + ']+'))           # [^=}>\'" \t\n\r\f\v]+
        ])

        rootTag = "tagpholder"
        cmp_patt__in = dict([
            ('PATH_RES', cmp('[' + PATH_RES + ']+')),   # [}]+
            ('ATTR_LDEL', cmp('[' + ATTR_LDEL + ']+')), # [\'" \t\n\r\f\v]+
            ('ATTR_RDEL', cmp('[' + ATTR_RDEL + ']+')), # [{=> \t\n\r\f\v]+
            ('PARAM_DEL', cmp('[' + PARAM_DEL + ']+'))  # [\'"]+
        ])
        rootTagStck = [rootTag]
        pattern = regexPattern.strip('(?#)')

        npos = 1
        pmax = len(pattern) - 1
        tags = {rootTag: {}}
        varList = []
        TAG, npos = getCharsNotInSet(pattern, 'TAG_PATT', npos)
        if TAG[0] == '(' and TAG[-1] == ')':
            tagPattern = TAG[1:-1]
            tags[rootTag]['__TAG__'] = ''
            varList.append([rootTag + ATTRSEP + '__TAG__', '__TAG__'])
        else:
            tagPattern = TAG
        if tagPattern == '__TAG__': tagPattern = '[a-zA-Z][^\s>]*'
        ATTR = PARAM = VAR = ''
        while 1:
            sep, npos = skipCharsInSet(pattern, 'PATH_RES', npos)
            while sep:
                if len(rootTagStck) == 1:
                    v = 'Closing curly brace without corresponding opening curly brace'
                    raise re.error(v)
                rootTagStck.pop()
                rootTag = '.'.join(rootTagStck)
                sep = sep[:-1]
            sep, npos = skipCharsInSet(pattern, 'ATTR_LDEL', npos)

            if npos >= pmax: break
            ATTR, npos = getCharsNotInSet(pattern, 'ATTR_PATT', npos)

            PARAM = VAR = ''
            sep, npos = skipCharsInSet(pattern, 'ATTR_RDEL', npos)

            if sep == PATH_MOD:
                rootTagStck.append(ATTR)
                rootTag = ATTRSEP.join(rootTagStck)
                continue

            if sep[0] in PATH_MOD + EQ and len(sep) > 1:
                v = 'the pattern "%s" is not allowed ' % sep
                raise re.error(v)

            attrName = ATTR.rstrip(')').lstrip('(')
            if attrName != ATTR:
                if len(attrName) - len(ATTR) == 1:
                    v = 'unbalanced parenthesis'
                    raise re.error(v)
                if attrName[0] == ATTRSEP and ATTRSEP not in attrName[1:]:
                    v = 'Required tags not allowed as variables'
                    raise re.error(v)
                VAR = "group" + str(1 + len(varList))
            pathKey, psep, attrKey = attrName.rpartition(ATTRSEP)
            if not pathKey and psep:
                pathKey = rootTag + 2 * ATTRSEP + attrKey
                attrKey = ''
            else:
                pathKey = rootTag + psep + pathKey
            pathKey = re.sub(r'[.](\d+)(?=[.]*)', r'[\1]', pathKey).replace('[1]', '')
            tags.setdefault(pathKey, {})
            if attrKey:
                tagDict = tags[pathKey]
                tagDict.setdefault(attrKey, '')
                if VAR:
                    varName = VAR
                    attrName = pathKey + ATTRSEP + attrKey
                    varList.append([attrName, varName])

            if sep == "=":
                nt = n1 = n2 = 0
                while 1:
                    nt += 1
                    if nt == 3:
                        v = 'Triple asignation not allowed'
                        raise re.error(v)
                    sep, npos = skipCharsInSet(pattern, 'PARAM_DEL', npos)

                    if sep:
                        n1 += 1
                        if n1 == 2:
                            v = 'Double attr value not allowed'
                            raise re.error(v)
                        posfin = npos
                        attr = sep
                        while 1:
                            attrInc, posfin = getCharsNotInSet(pattern, 'PARAM_PATT', posfin)
                            if attrInc[-1] in '=>': break
                            attr += attrInc
                            sep, posfin = skipCharsInSet(pattern, 'PARAM_DEL', posfin)
                            attr += sep
                        PARAM = attr[1:-1]

                        if attrKey != '__EZONE__':
                            tagDict[attrKey] = re.compile(PARAM + r'\Z', re.DOTALL)
                        else:
                            tagDict[attrKey] = PARAM

                        if len(PARAM): npos += len(PARAM) + 1
                        if pattern[npos] != '=': break
                        npos += 1
                        continue
                    if not sep:
                        n2 += 1
                        if n2 == 2:
                            v = 'Double variable asignation to the same attribute value not allowed'
                            raise re.error(v)
                        VAR, npos = getCharsNotInSet(pattern, 'VAR_PATT', npos)

                        if not attrKey:
                            v = 'Store tags as variables is not allowed'
                            raise re.error(v)
                        attrName = pathKey + ATTRSEP + attrKey
                        varName = VAR.strip('&')
                        if attrName in list(map(operator.itemgetter(0), varList)):
                            v = 'reassigment of attribute ' + attrName + ' to var ' + varName
                            raise re.error(v)
                        if varName in list(map(operator.itemgetter(1), varList)):
                            v = 'redefinition of group name ' + varName + ' as group ' + str(len(varList) + 1)
                            raise re.error(v)
                        varList.append([attrName, varName])
                        if VAR != varName:
                            tagDict[attrKey] = re.compile("(?:(?:&nbsp;)*\s*)*(.+?)(?:(?:&nbsp;)*\s*)*" + r'\Z')
                            # tagDict[attrKey] = re.compile("\s*([ \S]*?)\s*" + r'\Z')

                        if pattern[npos] != '=': break
                        npos += 1

        if len(rootTagStck) > 1:
            v = 'Unbalanced curly braces'
            raise re.error(v)

        if 'tagpholder..*' in tags:
            if not varList:
                tags.pop('tagpholder..*')
                varList.append(['tagpholder..*', 'text_tags'])
            else:
                v = 'With required Tag ".*", var are not allowed'
                raise re.error(v)

        stags = tags[rootTag].get('__EZONE__', '[!--|script]')
        if '__EZONE__' in tags[rootTag]: tags[rootTag].pop('__EZONE__')
        incFlag = not stags.startswith('^[')
        stags = stags.strip("[^]").split('|') if stags else []
        ezones = []
        for stag in stags:
            if stag == '!--':
                stag = '<' + stag
                etag = '-->'
            else:
                etag = '</' + stag + '>'
                stag = '<' + stag
            ezones.append([stag, etag, 0, 0])  # aqui 1
        answ = ExtRegexObject(regexPattern, flags, tagPattern, tags, varList, (ezones, incFlag))
    return answ


# equis = '(?#<span class="cerrar" onclick="d.+?\'([^\']+)\'.+?;">)'
# ese = ExtCompile(equis)

def compile(regexPatternIn, flags=0, debug=0):
    BEG = r'(?#'
    END = r')'
    ZIN = r'<<>>'
    NXTTAG = r'<><>'
    CHILDREN = r'<<>*>'
    PARENT = r'<*<>>'
    SIBLING = r'<>*<>'
    TAG = r'<>'
    PATDIRECT = r'\(\?#(<(?:PASS|SPAN|PARAM|SEARCH|NXTPOSINI).*?>)\)'

    if not regexPatternIn: return None
    pattern = r'\(\?#<.+?>\)'
    rgxflags = ''.join(re.findall(pattern, regexPatternIn))
    rePattern = ''.join(re.split(pattern, regexPatternIn))

    regexPattern = re.sub(PATDIRECT, '', rgxflags)
    patterns = re.split(r'(?:<\*<|>\*<|>\*>|>|<)', regexPattern)
    if not (patterns[0].startswith(BEG) and patterns[-1].endswith(END)):
        regexPattern = rePattern
        return ExtCompile(regexPattern, flags)
    patterns = patterns[1:-1]

    tags = re.findall(r'[<>][<>*]*', regexPattern)
    if len(tags) <= 1 or tags[0] not in ['<', '<*<']: return None
    token = ''.join(tags)
    if token == TAG: return ExtCompile(regexPattern, flags)
    patt1 = BEG + '<' + patterns[0] + '>' + END
    zone = 'zin'
    if token == ZIN:
        #
        # (?#<h1 class="price" <p *=label>>)
        # (?#<h1 class="price" <__TAG__ __TAG__="p|span" *=label>>)
        #
        patt2 = patterns[-2] if tags[-1] == '>>' else ''
        patt2 = BEG + '<' + patt2 + '>' + END
        # zone = 0 if tags[1] == '<' else patterns[1]
    elif token == CHILDREN:
        #
        # Dos formas:
        # Primera:
        #       (?#<h1 class="price" .p<*=label>*>)
        # Segunda:
        #       (?#<h1 class="price" <__TAG__ __TAG__="p|span" *=label>*>)
        #
        chldpat = '|'.join(re.findall(r'(?<= )[.]([a-z\d_-]+)(?=[ >])', patt1))
        chldpat = chldpat or '__TAG__'
        patt2 = patterns[-1] if tags[-1] == '>*>' else ''
        patt2 = BEG + '<' + chldpat + ' ' + patt2 + '>' + END
    elif token == NXTTAG:
        #
        # (?#<h1 class="price"><__TAG__ __TAG__="p|span" *=label>)
        #
        patt2 = patterns[-1] if tags[-1] == '>' else ''
        patt2 = BEG + '<__TAG__ ' + patt2 + '>' + END
        zone = 'zoutr'
    elif token in [PARENT, SIBLING]:
        raise re.error(token + ' not yet implemented')
        pass
    else:
        return None

    if debug: return regexPattern, flags, patt1, patt2, zone
    srchRegexObj = ExtCompile(patt2, flags)
    if not patt1: return srchRegexObj
    spanRegexObj = ExtCompile(patt1, flags)
    return zinwrapper(regexPattern, flags, spanRegexObj, srchRegexObj, zone)


def ExtDecorator(func):
    def wrapper(*args, **kwords):
        pattern, flagsvalue = args[0], 1 * ('flags' in kwords) and kwords.pop('flags')
        compPat = compile(pattern, flags=flagsvalue)
        callfunc = getattr(compPat, func.__name__)
        return callfunc(*args[1:], **kwords)

    return wrapper


@ExtDecorator
def search(pattern, string, flags=0):
    pass


@ExtDecorator
def match(pattern, string, flags=0):
    pass


@ExtDecorator
def split(pattern, string, maxsplit=0, flags=0):
    pass


@ExtDecorator
def findall(pattern, string, flags=0):
    pass


@ExtDecorator
def finditer(pattern, string, flags=0):
    pass


@ExtDecorator
def sub(pattern, repl, string, count=0, flags=0):
    pass


@ExtDecorator
def subn(pattern, repl, string, count=0, flags=0):
    pass

if __name__ == '__main__':
    htmlstr = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Elementos para estudio de CustomRegEx</title>
    <!--
    (?#<table span.attr=label>) label = hijo2
    (?#<table ..attr=label>)    label = hijo1
    (?#<table .[1].attr=label>) label = hijo1
    (?#<table .[2].attr=label>) label = hijo3 ???? Se salto span con attr="hijo2"
    (?#<table .[2].__TAG__=label>) label = span
    (?#<table .[2].__TAG__=lbl1 .[2].attr=lbl2>) lbl1=span, lbl2=hijo3
    (?#<table .[2]{__TAG__=lbl attr=lbl2}>) lbl1=span, lbl2=hijo3   
    -->
    <table attr="padre">
        <row attr="hijo1">
            <col attr="nieto">
                <span attr="bisnieto"/>
            </col>
        </row>
        <span attr="hijo2">
            <row attr="hijo1">
                <span attr="nieto">
            </row>
        </span>
        <span attr="hijo3"/>
    </table>
</head>
<body>

</body>
</html>
    '''

    pattern = '(?#<table ..attr=label>)'
    pattern = '(?#<table .[1].attr=label>)'
    pattern = '(?#<table .2.attr=label>)'
    pattern = '(?#<table .[2].__TAG__=lbl1 .[2].attr=lbl2>)'
    pattern = '(?#<table .[2].attr=label>)'
    m = search(pattern, htmlstr)
    print('Hola miundo')