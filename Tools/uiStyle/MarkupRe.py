# -*- coding: utf-8 -*-
'''
Created on 19/09/2015

@author: Alex Montes Barrios
'''
from builtins import StopIteration
from collections import namedtuple
import re
import itertools
import operator
from html.parser import HTMLParser
from enum import Enum

import tokenizer
from Tools.uiStyle.CustomRegEx import ExtCompile


# Tipo de pattterns compuestos
class CPatterns(Enum):
    ZIN = '<<>>'
    CHILDREN = '<<>*>'
    NXTTAG = '<><>'
    PARENT = '<*<>>'
    SIBLINGS = '<>*<>'

    def __eq__(self, other):
        if isinstance(other, str):
            return self.value == other
        return super().__eq__(other)


class MarkupReError(Exception):
    pass


class ExtRegexParser(HTMLParser):
    def __init__(self, varList=None, reqTags=None, optTags=None, factory=None):
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
        self.factory = factory
        pass

    def checkStartTag(self, data):
        # tag = re.match(r'<([a-zA-Z\d]+)[\W >]', data).group(1)
        if 'tagpholder' not in self.reqTags:
            return True
        reqTags = dict(self.reqTags['tagpholder'])
        if '*' in reqTags:
            reqTags.pop('*')
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

    def haveTagAllAttrReq(self, element_path, element_attrs, req_attrs=-1):
        '''
        Verifica que elemento tenga en sus atributos todos los elementos requeridos y
        que cumplan con el pattern solicitado.
        :param element_path: str. Full path del elemento a revisar.
        :param element_attrs: dict. Atributs asociados al elemento.
        :param req_attrs: dict or -1. Dict de attributos requeridos, si es -1 se utilizan los
                          required tags.
        :return: bool. (cumple/no cumple) con lo solicitado.
        '''
        if req_attrs == -1:
            req_attrs = self.reqTags.get(element_path, {})
        diff_set = req_attrs.keys() - element_attrs.keys()
        if diff_set:
            return False
        bflag = all(
            [
                req_attrs[key].match(element_attrs[key])
                for key in req_attrs if req_attrs[key]
            ]
        )
        return bflag

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
        # en este punto se tiene enlazados hijos y padres.
        n_elem = len(tagList)
        elem_params = [{'__DADSPAN__': tagList[dad_id][0]} for dad_id in dadList]
        childList = {}
        [
            childList.setdefault(dad_id, []).append(child_id)
            for child_id, dad_id in enumerate(dadList)
        ]
        [
            # Número de hijos. Si no tiene no aparece entre las key del dict.
            (elem_params[dad_id].setdefault('__NCHILDREN__', len(children)),
             # Enumeración de hijos desde 1
             elem_params[child_id].setdefault('__NCHILD__', k + 1)
             )
            for dad_id, children in sorted(childList.items())
            for k, child_id in enumerate(children)
        ]
        # La información de DADSPAN y NCHILD no tiene sentido para el raiz
        # porque desde allí comienza a parsear el archivo.
        elem_params[0].pop('__DADSPAN__')
        elem_params[0].pop('__NCHILD__')

        # for dad_id, children in sorted(childList.items()):
        #     elem_params[dad_id]['__NCHILDREN__'] = len(children)
        #     for k, child_id in enumerate(children):
        #         elem_params[child_id]['__NCHILD__'] = k

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
        if not self.checkStartTag(data):
            return None
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
            if not self.tagStack:
                break
            beg = end
        self.reset()
        if not self.tagList:
            return None
        tagList = sorted(self.tagList)
        reqSet = set(self.reqTags.keys())
        optSet = set(self.optTags.keys()).difference(reqSet)
        reqSet = reqSet.union(optSet)
        toProcess = self.setPathTag(tagList, reqSet=reqSet)  # aqui 5
        reqSet.difference_update(optSet)
        if reqSet:
            return None
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

    def handle_starttag(self, tag, attrs):  # startswith('<')
        posini, posfin = self.getSpan(self.get_starttag_text())
        self.stackPath += '.' + tag
        self.tagStack.append([tag, (posini, posfin)])
        self.factory.start_tag(tag, (posini, posfin), attrs)

    def handle_endtag(self, tag):  # startswith("</")
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
        self.factory.end_tag(tag, (posini, posfin))

    def handle_startendtag(self, tag, attrs):
        posini, posfin = self.getSpan(self.get_starttag_text())
        # self.stackPath += '.' + tag
        self.tagList.append([(posini, posfin), tag, -1])
        self.factory.start_end_tag(tag, (posini, posfin), attrs)

    def storeDataStr(self, dataIn):
        dSpanIn = self.getSpan(dataIn)
        if self.tagList and self.tagList[-1][1] == '*':
            dataSpan = self.tagList[-1][0]
            if dataSpan[1] == dSpanIn[0]:
                self.tagList[-1][0] = (dataSpan[0], dSpanIn[1])
                return
        if not dataIn.strip(' \t\n\r\f\v'): return
        self.tagList.append([dSpanIn, '*', None])
        self.factory.process_data(dSpanIn, dataIn)

    def handle_data(self, data):
        self.storeDataStr(data)

    def handle_entityref(self, name):  # startswith('&')
        data = '&%s;' % name
        self.storeDataStr(data)

    def handle_charref(self, name):  # startswith("&#")
        data = '&#%s;' % name
        self.storeDataStr(data)

    def handle_comment(self, data):  # startswith("<!--")
        posini, posfin = self.getSpan('<!--%s-->' % data)

    def handle_decl(self, data):  # startswith("<!")
        posini, posfin = self.getSpan('<!%s>' % data)

    def handle_pi(self, data):  # startswith("<?")
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
    def __init__(self, regex_pattern_str, regex_flags, tag_pattern, srch_attrs, var_list, e_zones):
        self.regex_pattern_str = self.pattern = regex_pattern_str
        self.regex_flags = self.flags = regex_flags
        self.tag_pattern = tag_pattern
        varNames = []
        self.groupindex = {}
        for element_path, attr_name in var_list:
            itemName = attr_name.strip('_') if attr_name != '__TAG__' else attr_name
            if itemName in varNames: continue
            varNames.append(itemName)
            self.groupindex[itemName] = len(varNames)
        self.var_list = var_list
        self.groups = len(self.groupindex)
        self._e_zones = e_zones
        self.searchFlag = None
        self.isSearchFlagSet = lambda: True if not self.searchFlag else self.searchFlag.is_set()

        # Separación de attributos buscados (srch_attrs) entre requeridos (req_attrs) y
        # opcionales (opt_attrs)
        self.req_attrs = req_tags = srch_attrs
        self.opt_attrs = opt_attrs = {}

        optional_paths = [
            attr_path.rsplit('.', 1)
            for attr_path, var in self.var_list
            if var != '__TAG__' and var != var.strip('_')
        ]
        optional_elems = set()
        for element_path, attr_name in optional_paths:
            attr_pattern = req_tags[element_path].pop(attr_name)
            optional_elems.add(element_path)
            opt_attr = opt_attrs.setdefault(element_path, {})
            opt_attr[attr_name] = attr_pattern

        # Se eliminan de los elementos requeridos aquellos que no tienen  atributos buscados
        while optional_elems:
            element_path = optional_elems.pop()
            if not req_tags[element_path]:
                req_tags.pop(element_path)

        match_factory = MatchObjectFactory(tag_pattern, srch_attrs, var_list)
        self.regex_parser = ExtRegexParser(self.var_list, self.req_attrs, self.opt_attrs, match_factory)
        self._seeker = None
        pass

    def __eq__(self, other):
        fields = ['tag_pattern', 'req_attrs', 'opt_attrs', 'var_list', '_e_zones']
        return all(
            [
                getattr(self, field) == getattr(other, field)
                for field in fields
            ]
        )

    def get_seeker(self):
        if self._seeker is None:
            root_tag = 'tagpholder'
            # Atributos no utilizables para encontrar candidato a solución
            exc_attr = ['*', '__TAG__']
            # Adicionalmente debemos retirar los atributos opcionales
            opt_attrs = [
                attr.rsplit(ATTRSEP, 1)[-1]
                for attr, var in self.var_list
                if attr.startswith(root_tag) and var != '__TAG__' and var != var.strip('_')
            ]
            exc_attr.extend(opt_attrs)
            diff_set = self.req_attrs.get(root_tag, {}).keys() - exc_attr
            if diff_set:
                myfunc = lambda x: rf'<{self.tag_pattern}\s[^>]*{"=[^>]+".join(x)}=[^>]+[/]*>'
                srch_pattern = '|'.join(map(myfunc, itertools.permutations(diff_set, len(diff_set))))
            else:
                srch_pattern = rf'<(?:{self.tag_pattern}).*?/*>'
            self._seeker = re.compile(srch_pattern, re.DOTALL | re.IGNORECASE)
        return self._seeker

    def match(self, html_string, pos=-1, endpos=-1, parameters=None):
        pos = max(pos, 0)
        endpos = endpos if endpos != -1 else len(html_string)

        varPos = self.regex_parser.initParse(html_string[pos: endpos], pos)
        if varPos:
            if self.var_list and 'tagpholder..*' in self.var_list[0][0]:
                self.groups = len(varPos) - 1
                self.groupindex = dict(('grp%s' % k, k) for k in range(1, len(varPos)))
            return ExtMatchObject(self, html_string, pos, endpos, varPos, parameters)

    def finditer(self, html_string, pos=-1, endpos=-1, seek_to_end=False, parameters=None):
        pos = max(pos, 0)
        endpos = endpos if endpos != -1 else len(html_string)
        master_pat = self.get_seeker()
        e_zones = self._e_zones

        pointer_pos = HTMLPointer(
            html_string, it_span=[(pos, endpos)], seek_to_end=seek_to_end, next_pattern=master_pat,
            special_zones=e_zones
        )

        def match_gen(html_string, pointer_pos):
            span_gen = pointer_pos()
            while self.isSearchFlagSet():
                try:
                    beg_pos, end_pos = next(span_gen)
                except StopIteration:
                    break
                m = self.match(html_string, beg_pos, endpos, parameters=parameters)
                if m:
                    span_gen.send(m.end())
                    yield m
            # raise StopIteration

        return match_gen(html_string, pointer_pos)

    def search(self, html_string, spos=-1, sendpos=-1, parameters=None):
        it = finditer(self, html_string, spos, sendpos, parameters)
        return next(it)

    def split(self, html_string, maxsplit=0):
        answer = []
        lstPos = 0
        for k, match in enumerate(self.finditer(html_string)):
            if maxsplit and k + 1 > maxsplit:
                break
            posIni, posFin = match.span()
            answer.append(html_string[lstPos:posIni])
            lstPos = posFin
            if match.groups():
                answer.extend(match.groups())
        if lstPos != len(html_string):
            answer.append(html_string[lstPos:])
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

    def sub(self, repl, string, count=0):
        pass

    def subn(self, repl, string, count=0):
        pass


class zinwrapper(ExtRegexObject):
    def __init__(self, pattern, flags, spanRegexObj, srchRegexObj, zone=CPatterns.ZIN):
        '''
        ExtRegexObject para patterns compuestos. Ver enum CPatterns.
        :param pattern: str. Pattern compuesto compilado.
        :param flags: int. Para compatibilidad con re original. Siempre es cero.
        :param spanRegexObj: ExtRegexObject. Compile pattern que entrega las zonas válidas
                            para la búsqueda.
        :param srchRegexObj: ExtRegexObject. Compile pattern que entrega los datos buscados.
        :param zone: CPatterns. Compole patterns type.
        '''

        self.__dict__['spanRegexObj'] = spanRegexObj
        self.__dict__['srchRegexObj'] = srchRegexObj
        self.zone = zone
        self.parameters = namedtuple('zinparams', sorted(spanRegexObj.groupindex.keys()))
        self.spanDelim = self.params = None
        self.pattern = pattern
        self.flags = flags
        pass

    def __eq__(self, other):
        return all(
            [
                self.spanRegexObj == other.spanRegexObj,
                self.srchRegexObj == other.srchRegexObj,
            ]
        )

    def __getattr__(self, attr):
        return getattr(self.__dict__['srchRegexObj'], attr)

    def __setattr__(self, attr, value):
        return setattr(self.__dict__['srchRegexObj'], attr, value)

    @property
    def searchFlag(self):
        return self.srchRegexObj.searchFlag

    @searchFlag.setter
    def searchFlag(self, value):
        self.srchRegexObj.searchFlag = value
        self.spanRegexObj.searchFlag = value

    def finditer(self, html_string, pos=-1, endpos=-1, parameters=None):
        bflag = not self.zone == CPatterns.ZIN  # Con esto se asegura que el puntero se va al final

        # del span que es lo que se quiere en caso de
        # '<<>*>'(children) y de '<><>' (nexttag)
        def match_gen(html_string):
            for match_srchobj in self.spanRegexObj.finditer(
                    html_string, pos, endpos, seek_to_end=False, parameters=parameters
            ):
                params = self.parameters(**match_srchobj.groupdict())
                span_beg_pos, span_end_pos = match_srchobj.span()
                match self.zone:
                    case CPatterns.ZIN | CPatterns.CHILDREN:
                        it = self.srchRegexObj.finditer(
                            html_string, span_beg_pos + 1, span_end_pos,
                            seek_to_end=bflag, parameters=params
                        )
                    case CPatterns.NXTTAG:
                        beg_pos = html_string[span_end_pos + 1: endpos].find('<')
                        if beg_pos > 0:
                            beg_pos += span_end_pos + 1
                            m = self.srchRegexObj.match(html_string, beg_pos, parameters=params)
                        else:
                            m = None
                        it = [m] if m else []
                    case CPatterns.PARENT | CPatterns.SIBLINGS:
                        # No se ha implementado y se coloca la lista vacía
                        it = []
                yield from it

        return match_gen(html_string)


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


class HTMLPointer:
    next_pattern = '<[a-zA-Z].*?/*>'

    def __init__(self, html_str, is_file=False, it_span=None,
                 next_pattern=None, seek_to_end=True,
                 special_zones='[!--|style|script]'):
        '''
        Recorre un html string con cierto saltando entre ocurrencias de un determinado pattern.
        :param html_str: str or filename. Objeto a recorrer.
        :param is_file: bool. True si html_str es el nombre de un archivo
        :param it_span: list(tuple(int, int)) or iterator. Límites entre los cuales se hará la búsqueda.
        :param next_pattern: str or re.compile instance. Pattern para situar el puntero.
        :param special_zones: str. String de la forma "[exc_zones]^[inc_zones]".
                "exc_zones" tiene la forma "!--|tag1|.." y los tag# son los tags que demarcan
                zonas excluídas, caso especial son los comentarios que se denotan por !--.
                "inc_zones" con igual forma que exc_zones pero denota las zonas donde deberá
                hacerse la búsqueda respetando las zonas de exclusión (exc_zones).
        '''
        if is_file:
            with open(html_str, 'r') as f:
                html_str = f.read()
        self.html_str = html_str
        it_span = it_span or [(0, len(html_str))]
        if isinstance(it_span, list):
            it_span = iter(it_span)
        self.it_span = it_span
        self.exc_zones = self.get_special_zones(special_zones)
        pattern = next_pattern or self.next_pattern
        if isinstance(pattern, str):
            pattern = re.compile(pattern, re.IGNORECASE)
        self.next_tag = pattern
        self.span = next(self.it_span)
        self.pos = self.span[0]
        self.seek_to_end = seek_to_end

    def __call__(self):
        while True:
            html_str = self.html_str
            beg_pos = self.find(self.next_tag)
            if beg_pos is None:
                break
            end_inner = self.pos
            assert (html_str[beg_pos], html_str[end_inner - 1]) == ('<', '>'), 'No se tiene tag completo'
            bflag = html_str[beg_pos:end_inner].endswith('/>') or html_str[beg_pos:end_inner].endswith('-->')
            if not bflag:  # No start-end tag o comentario
                tag = re.match('<(.+?)(?:\s|>)', html_str[beg_pos:end_inner]).group(1)
                cp_pattern = re.compile(rf'</\s*{tag}\s*>', re.IGNORECASE | re.DOTALL)
                beg_inner = self.find(cp_pattern, use_sectors=False)
                if not beg_inner:
                    continue
            end_pos = self.pos
            new_end_pos = yield beg_pos, end_pos
            if new_end_pos is None:
                if not self.seek_to_end:
                    self.pos = end_inner
            else:  # new_end_pos is not None
                self.pos = new_end_pos
                yield end_pos if self.seek_to_end else end_inner

    def find(self, cp_pattern, use_sectors=True):
        '''
        Mueve el apuntador del archivo al comienzo de la etiqueta que cumple
        con el cmp_pattern.
        :param cmp_pattern: re.compile object. Patron a buscar, o próximo
                            comienzo de etiqueta
        :return: int.
        '''
        linf, lsup = self.span
        beg_pos = self.pos - linf
        html_str = self.html_str[linf: lsup]
        while True:
            m = cp_pattern.search(html_str, beg_pos)
            if not m:
                if not use_sectors:
                    break
                # si no se encuentra el pattern, se busca el próximo pattern se pide
                # el próximo sector, el cual si no existe eleva el Stop iteration
                try:
                    self.span = next(self.it_span)
                except StopIteration:
                    break
                linf, lsup = self.span
                html_str = self.html_str[linf: lsup]
                self.pos = linf
                beg_pos = 0
                continue
            beg_pos = self.confirm_position(m.start())
            if m.start() == beg_pos:
                # Se tiene un match del pattern buscado. Se procede entonces a buscar
                # el tag de cierre.
                self.pos = m.end() + linf
                return beg_pos + linf
        return None

    def get_special_zones(self, special_zones):
        '''

        :param special_zones:
        :return:
        '''
        zones = special_zones.split('^')[:2]  # Solo se tiene en cuenta las dos primeras zonas.
        try:
            special_zones, inc_tags = zones
            comment_pat = tag_pat = ''
            if '!--' in inc_tags:
                inc_tags = f'{inc_tags[1:-1]}|'.replace('!--|', '')
                inc_tags = f'[{inc_tags}]'
                comment_pat = r'(?:<!--.+?-->)'
            if inc_tags[1:-1]:
                tag_pat = rf'(?:<(?:{inc_tags[1:-1]})(?:>|\s.+?(?<!/)>))'
            full_pat = '|'.join([comment_pat, tag_pat]).strip('|')
            cp_pattern = re.compile(full_pat, re.DOTALL | re.IGNORECASE)
            sectors = self.__class__(
                self.html_str,
                it_span=self.it_span,
                next_pattern=cp_pattern,
                special_zones=special_zones
            )()
            self.it_span = sectors
        except Exception as e:
            pass
        exc_zones = []
        for exc_tag in special_zones[1:-1].split('|'):
            pattern = f'(?:<!--|-->)' if exc_tag == '!--' else f'<\\s*?/*{exc_tag}(?:\\s|>)'
            exc_zones.append((re.compile(pattern, re.IGNORECASE), 0))
        return exc_zones

    def confirm_position(self, pos):
        '''
        Verifica que 'pos' no se encuentre en una zona de exclusión.
        :param pos: int. Posición que se quiere verificar.
        :return:
        '''
        linf, lsup = self.span
        pos = pos + linf
        linf_zexc = []  # almacena la posición del tag de cierre de las
        # zonas de exclusión cuando pos se encuentra en una de ellas
        for k, (cp_pattern, lim_inf) in enumerate(self.exc_zones):
            # Se excluyen los exc_zones cuya primera ocurrencia sabemos está despues de pos
            if pos >= lim_inf:
                m = cp_pattern.search(self.html_str[pos:lsup], re.IGNORECASE)
                if m is None:
                    lim_inf = lsup
                else:
                    found_pattern = re.sub('\\s', '', m.group())
                    if found_pattern[:2] == '</' or found_pattern == '-->':
                        linf_zexc.append(pos + m.end())
                    lim_inf = pos + m.start()
                self.exc_zones[k] = (cp_pattern, lim_inf)
        if linf_zexc:
            return max(linf_zexc) - linf
        return pos - linf

    def seek(self, new_pos):
        '''
        Mueve el puntero hacia adelante
        :param new_pos: int. Posición a la que mover el puntero. Siempre mayor a
                             la posición en que se encuentra
        :return: int. Posición válida en la que se posiciono el puntero.
        '''
        # Solo se puede mover hacia adelante.
        if new_pos < self.pos:
            raise MarkupReError(f'''{self.__class__.__name__}: Can't position behind position {self.pos}''')
        # Se ubica el sector donde debe ser posicionado el puntero.
        while True:
            linf, lsup = self.span
            bflag = linf <= new_pos < lsup
            if bflag:
                break
            try:
                self.span = next(self.it_span)
            except StopIteration:
                raise MarkupReError(f"""{self.__class__.__name__}: position {new_pos} beyond iterator limits""")
        # Se verifica que la posici+on solicitada se encuentra en una zona permtida.
        self.pos = new_pos = self.confirm_position(new_pos)
        return new_pos


class MatchObjectFactory:
    def __init__(self, tag_pattern, req_tags, req_vars):
        self.tag_pattern = tag_pattern
        self.req_tags = req_tags
        self.req_vars = req_vars
        self.stack = []
        self.path = ''
        self.n_children = {}
        self.path_dict = {}
        self.bd_tags = []

    def get_path(self, tag):
        path = self.path
        self.n_children[path] = self.n_children.get(path, 0) + 1
        path += f'.{tag}'
        self.path_dict[path] = n = self.path_dict.setdefault(path, 0) + 1
        answ = path + ('' if n == 1 else f'[{n}]')
        return answ

    def start_tag(self, tag, span, attribs):
        root = self.path
        self.path = path = self.get_path(tag)
        attribs.append(('__N_CHILD__', self.n_children[root]))
        self.stack.append([tag, path, span, attribs])
        pass

    def end_tag(self, tag, span):
        posini, posfin = span
        while self.stack:
            stck_tag, stck_path, stck_span, stck_attribs = self.stack.pop()
            bflag = tag == stck_tag
            tag_span = (stck_span[0], posfin) if bflag else stck_span
            stck_attribs.append(('__N_CHILDREN__', self.n_children.get(self.path, 0)))
            self.path = self.path.rsplit('.', 1)[0]
            self.bd_tags.append([tag_span, stck_path, stck_attribs, None])
            if bflag:
                break
        if self.path and not self.stack:
            raise MarkupReError('ParseError: Bad file format')

    def start_end_tag(self, tag, span, attribs):
        root = self.path
        path = self.get_path(tag)
        attribs.append(['__N_CHILD__', self.n_children[root]])
        self.bd_tags.append([span, path, attribs, -1])
        pass

    def process_data(self, span, data):
        if self.bd_tags and self.bd_tags[-1][1] == '*':
            data_span = self.bd_tags[-1][0]
            if data_span[1] == span[0]:
                self.bd_tags[-1][0] = (data_span[0], span[1])
                return
        if not data.strip(' \t\n\r\f\v'):
            return
        self.bd_tags.append([span, '*', None, None])


REGEX_SCANNER = re.compile(r'''
    (?P<SEPARATOR>(?:
       (?:<\*<) |                       # Inicio Pattern
         (?:><) |                       # Inicio Pattern
       (?:>\*<) |                       # Inicio Pattern
       (?:>\*>) |                       # Inicio Pattern
         (?:>>) |                       # Inicio Pattern
          (?:<) |                       # Inicio Pattern
          (?:>)                         # Inicio Pattern
    )) |
    (?P<WHITESPACE>\s+) |           # string
    (?P<SPECIAL_ATTR>(?:                            # Atributo del sistema
        __                                          # Prefix = __
        [A-Z]+?                                     # Nombre de atributo, en mayúscula
        __                                          # Suffix = __
        (?==)                                    # Siempre seguida por =
     )) |           
    (?P<TAG_PATTERN>(?:
        (?<=<)\s*?                   # Precedida por < y posiblemente espacios
        \(*(?:__TAG__|[A-Za-z].*?)\)*   # Pattern tag
        (?!=)
        (?=\s|>)                 # La sigue uno o mas espacios o >
     )) |           
    (?P<VAR>(?:
        (?<=\=)                 # Precedida por el signo igual
        (?:_{,2}|&)*           # Indica variable opcional(_) o clean var (&)
        [a-zA-Z][a-zA-Z\d_]*?        # Nombre de la variable
        (?:_{,2}|&)*           # Indica variable opcional(_) o clean var (&)
        (?=\s|>|\})             # Siempre seguida por ' ', > o }
     )) |           
    (?P<ATTRIBUTE>(?:
        [a-zA-Z\*\.\d][a-zA-Z\d\.\[\]\*]*?        # Nombre de atributo
        (?=\=|>|\s)
     )) |           
    (?P<PREFIX>(?:
        [a-zA-Z\.\d][a-zA-Z\d\.\[\]]*?        # Nombre de la variable
        (?=\{)
     )) |           
    (?P<IMPLICIT>(?:        # Encerrado entre parentesis
        \(                  # Prefix
        [a-zA-Z\*\.\d][a-zA-Z\d\.\[\]\*]*?          # Pattern
        \)                  # Suffix
    )) |    
    (?P<ATTR_PATTERN>(?:
        (?<=\=)          # Debe estar precedido por el = 
        (?P<quote>["'])     # Prefix
        (.*?)               # Pattern, puede ser nula
        (?P=quote)          # Suffix
        (?=\s|>|=)          # Nota: Esto no acepta espacios en el pattern luego de un scape quote
    )) |
    (?P<ASIGNATION>(?:
        =                   # Igual
    )) | 
    (?P<OPEN_TAG>(?:
        \{      # parenthesis
    )) | 
    (?P<CLOSE_TAG>(?:
        \}      # parenthesis
    )) | 
    (?P<ERROR>.)                    # an error
    ''', re.DOTALL | re.VERBOSE)


def compile(regex_str_in, flags=0, etags_str='[!--|style|script]'):
    '''
    Compila el regex_str.
        Entrega un objeto cuando se tiene un patron básico: zin, children,
        father, sibling, nextag (<p1<p2>*>, <p1<p2>>, ...).
        Etrega una lista de objetos cuando se tiene un patron de la siguiente dorma:
            <p1><p2>...., (<p1<p2>*>)<p3>> (
    :param regex_str_in: str. Regex pattern.
    :param flags: int. Combinación de flags definidas en el re.
    :param etags_str: str. Elementos que no son considerados válidos para
                    posicionar el puntero.
    :return: re.compile or ExtRegExObject or a list of both objects.
    '''

    if not regex_str_in:
        return None
    pattern = r'\(\?#<.+?>\)'
    # En rgxflags se filtran _todo lo que se considera comentario por el re. De esta
    # manera los flags del re no tienen incidencia sobre el rgxflags.
    rgxflags = ''.join(re.findall(pattern, regex_str_in))
    # Para compatibilidad con versiones anteriores, se eliminan flags que ya no se requieren.
    rgx_pattern = re.sub(r'\(\?#(<(?:PASS|SPAN|PARAM|SEARCH|NXTPOSINI).*?>)\)', '', rgxflags)
    rgxflags = re.findall(pattern, rgx_pattern)
    if rgxflags:
        # Solo se acepta el primer patron.
        rgx_pattern = rgxflags[0]

    # En re_pattern se filtra _todo aquello que es considerado como pattern (no comentario)
    # por el re. Este será procesado si y solo si no se tiene un rgxflags válido.
    re_pattern = ''.join(re.split(pattern, regex_str_in))

    # Condición necesaria pero no suficiente
    # bflag = rgx_pattern.startswith('(?#<') and rgx_pattern.endswith('>)')
    if not rgx_pattern:
        return re.compile(re_pattern, flags)

    regex_str = rgx_pattern.strip(')(?#')

    # Chequeo de balance de {} y ()
    if regex_str.count('(') != regex_str.count(')'):
        raise MarkupReError(f'Compile: Unbalanced parenthesis')

    if regex_str.count('{') != regex_str.count('}'):
        raise MarkupReError(f'Compile: Unbalanced curly braces')

    compile_type = ''
    regexobj_stack = []

    tokens = tokenizer.Tokenizer(REGEX_SCANNER)
    for token in tokens.tokenize(regex_str):
        match token.tag:
            case 'SEPARATOR':
                compile_type += token.value
                match compile_type:
                    case '<' | '<*<':  # Primer separator
                        pini = tokens.pos
                    case '<>' | '<*<>' | '<><' | '<>*<' | '<<':  # Segundo separator
                        end = len(token.value)
                        pfin = tokens.pos
                        spattern = f'(?#<{regex_str[pini: pfin - end]}>)'
                        if compile_type == '<>':
                            compile_type = ''
                        regex_obj1 = ExtRegexObject(spattern, flags, tag_pattern, tags, list(varList), maskParam)
                        regexobj_stack.append(regex_obj1)
                        pini = pfin
                    case CPatterns.ZIN | CPatterns.CHILDREN | CPatterns.NXTTAG:  # Tercer separator
                        regex_obj1 = regexobj_stack.pop()
                        end = len(token.value)
                        pfin = tokens.pos
                        spattern = regex_str[pini: pfin - end]
                        if compile_type != CPatterns.ZIN:
                            # Se alteran los datos básicos del RegexObj para adecuarla
                            # a la condición de CHILDREN
                            bflag = 'tagpholder' not in tags or '__TAG__' not in tags['tagpholder']
                            if bflag:
                                req_tagpholder = tags.setdefault('tagpholder')
                                spattern = spattern.split(' ', 1)[-1]
                                if tag_pattern != tag_pattern_default:
                                    spattern = f'__TAG__ __TAG__="{tag_pattern}" {spattern}'
                                    req_tagpholder['__TAG__'] = re.compile(tag_pattern + '\\Z', re.DOTALL)
                                    tag_pattern = tag_pattern_default
                                else:
                                    spattern = f'__TAG__ {spattern}'
                                    req_tagpholder['__TAG__'] = ''
                        spattern = f'(?#<{spattern}>)'
                        regex_obj2 = ExtRegexObject(spattern, flags, tag_pattern, tags, list(varList), maskParam)
                        regexobj = zinwrapper(
                            f'(?#{regex_str})', flags, regex_obj1, regex_obj2, CPatterns(compile_type)
                        )
                        regexobj_stack.append(regexobj)
                        compile_type = ''
                    case CPatterns.PARENT | CPatterns.SIBLINGS:
                        raise MarkupReError(f'{compile_type} not yet implemented')
                    case _:
                        raise MarkupReError(f'{compile_type}: Unrecognizable compile type')

                # Reset variables del regexobj
                prefix_stack = ['tagpholder']
                prefix = 'tagpholder'
                attribute = ''
                n_implicit = 0

                tag_pattern = tag_pattern_default = '[a-zA-Z][^\s>]*'
                tags = {}
                varList = []
                maskParam = etags_str

            case 'TAG_PATTERN':
                if token.value == '__TAG__':
                    pass
                elif token.value != token.value.strip(')('):
                    tag_pattern = token.value[1:-1]
                    attribute = '.'.join([prefix, '__TAG__'])
                    element, attr = attribute.rsplit('.', 1)
                    attr_dict = tags.setdefault(element, {})
                    attr_dict.setdefault(attr, '')
                    varList.append([attribute, '__TAG__'])
                else:
                    tag_pattern = token.value
                tags.setdefault('tagpholder', {})
            case 'VAR':
                var_name = token.value
                var_name = var_name.strip('&')
                if varList:
                    attr_set, var_set = list(zip(*varList))
                    if var_name in var_set:
                        raise MarkupReError(
                            f'redefinition of group name {var_name} as group {len(var_set) + 1}'
                        )
                    if attribute in attr_set:
                        raise MarkupReError(
                            f'{regex_str}: Reassigment of attribute {attribute} to group name {var_name}'
                        )
                p1, sep, p2 = attribute.partition('..')
                if sep and p2.count('.') == 0:
                    raise MarkupReError(
                        f'{regex_str}: Required tags ({attribute}) not allowed as variables'
                    )
                if var_name != token.value:
                    attr_dict[attr] = re.compile('(?:(?:&nbsp;)*\\s*)*(.+?)(?:(?:&nbsp;)*\\s*)*\\Z')
                try:
                    varList.append([attribute, var_name])
                except AttributeError:
                    raise MarkupReError('With required Tag ".*", no vars are allowed')
            case 'SPECIAL_ATTR':
                attribute = '.'.join([prefix, token.value])
                element, attr = attribute.rsplit('.', 1)
                if token.value == '__TAG__':
                    attr_dict = tags.setdefault(element, {})
                    attr_dict.setdefault(attr, '')
            case 'ATTRIBUTE':
                value = token.value
                attribute = '.'.join([prefix, value])

                # Se normaliza la forma del atributo
                attribute = re.sub(r'\.(\d+)\.', r'.[\1].', attribute)
                attribute = attribute.replace('.[', '[').replace('[1]', '')

                if attribute == 'tagpholder..*':
                    if varList:
                        raise MarkupReError('With required Tag ".*", no vars are allowed')
                    # Se hace varList un tuple para evitar que puedan agregarse variables.
                    varList = (['tagpholder..*', 'text_tags'],)
                else:
                    element, attr = attribute.rsplit('.', 1)
                    attr_dict = tags.setdefault(element, {})
                    attr_dict.setdefault(attr, '')
            case 'PREFIX':
                value = token.value
                prefix_stack.append(value)
            case 'IMPLICIT':
                n_implicit += 1
                attribute = '.'.join([prefix, token.value[1:-1]])
                element, attr = attribute.rsplit('.', 1)
                attr_dict = tags.setdefault(element, {})
                attr_dict.setdefault(attr, '')
                varList.append([attribute, f'group{n_implicit}'])
            case 'ATTR_PATTERN':
                attr_pattern = token.value
                match attr:
                    case '__EZONE__':
                        maskParam = attr_pattern[1:-1]
                    case _:
                        # attr_dict = tags.setdefault(element, {})
                        attr_dict[attr] = re.compile(token.value[1:-1] + '\\Z', re.DOTALL)
            case 'ASIGNATION':
                pass
            case 'OPEN_TAG':
                prefix = '.'.join(prefix_stack)
            case 'CLOSE_TAG':
                prefix_stack.pop()
                prefix = '.'.join(prefix_stack)
            case 'ERROR':
                raise MarkupReError(
                    f'{regex_str}: {token.value} in {tokens.pos} position not a valid element'
                )
    # Se limita al caso de 1 solo objeto. Para implementar varios objetos en cascada se debe
    # primero implementar la opción de los separadores y definirlos al menos como en el css:
    # 'div p', 'div > p', 'div + p', 'p ~ ul'
    assert len(regexobj_stack) == 1, 'Acá debe encontrarse al menos un elemento'
    return regexobj_stack.pop() if len(regexobj_stack) == 1 else regexobj_stack


if __name__ == '__main__':
    from rich.console import Console
    from rich.table import Table

    console = Console(color_system='truecolor')

    test = 'tokenizer'
    if test == 'zin':
        htmlStr = """
        <span class="independiente">span0</span>
        <script>
            <span class="bloque1">span1</span>
            <a href="http://www.eltiempo.com.co">El Tiempo</a>
            <span class="bloque1">span2</span>
        </script>
        <bloque>
            <span class="independiente">bloque1</span>
            <parent id="root">
                <hijo id="hijo1">primer hijo</hijo>
                <hijo id="hijo2" exp="hijo con varios comentarios">
                     <h1>El primer comentario</h1>
                     <h1>El segundo comentario</h1>
                     <h1>El tercer comentario</h1>
                </hijo>
                <span class="colado">blk1</span>
                <hijo id="hijo3">tercer hijo</hijo>
            </parent>
            <span class="independiente">bloque2</span>
        </bloque>
        <!--
            <span class="bloque2">span1</span>
            <a href="http://www.elheraldo.com.co">El Heraldo</a>
            <span class="bloque2">span2</span>
        -->
        <span class="independiente">span3</span>
            """
        attrs = ('regex_pattern_str', 'req_attrs', 'opt_attrs', 'var_list', '_e_zones')
        zw_obj = compile('(?#<bloque <span id=_w_ class=__w__>>)')
        console.rule(f'spanRegexObj')
        console.print({attr: getattr(zw_obj.spanRegexObj, attr) for attr in attrs})
        console.rule(f'srchRegexObj')
        console.print({attr: getattr(zw_obj.srchRegexObj, attr) for attr in attrs})
        for m in zw_obj.finditer(htmlStr):
            console.print(m.span())
            console.print(m.groupdict())
        pass
    elif test == 'tokenizer':
        cases = {
            'test_implicitvars': '<a (href) *=label>',
            'minimo': '<table>',
            'test_namedvars': '<a href=url *=label>',
            'test_namedvarswithpattern': '<a href="http://uno/.+?/tres.html" href=url *=label>',
            'test_cleanvars': '<a (href) *=&label&>',
            'test_equivNotation': '<a href span{src=icon *=label} div.id>',
            'test_equivNotationII': '<table id td{1.*=grp1 2{b.*=grp2 a{href=grp2a src=grp2b}} 3.*=grp3 4.*=grp4}>',
            'test_tripleAsignation': '<ese a.*="http//.+?/prueba"=icon href=url>',
            'test_zin': '<bloque <span *=label>>',
            'test_nxttag1': '<hijo id="hijo1"><__TAG__=name exp=label h1[3].*=head>',
            'test_nxttag2': '<hijo id="hijo1"><hijo exp=label>',
            'test_nxttag3': '<h1 *="El segundo comentario">< *=label>',
            'test_children1': '<bloque <__TAG__=name>*>',
            'test_children2': '<bloque <__TAG__=name *="bloque2" class=clase>*>',
            'test_children3': '<bloque <__TAG__=name>*>',
            'test_parent': '<*<bloque >__TAG__=name>',
            'test_sibling': '<bloque >*<__TAG__=name>',
            'TestOptionalVars1': '<son id=id href=_url_>',
            'TestOptionalVars2': '<son id=_id_ href=_url_>',
            'TestOptionalVars3': '<son id=id href1="son2[^"]+"=_url_>',
            'TestOptionalVars5': '<son id=id href=url href1=_url_>',
            'TestOptionalVars6': '<son id=id href=url href1=_url_ grandson{href=__url__ *=label}>',
            'TestOptionalVars7': '<son id="3" href1=_url_ href2=__url__>',
            'test_errors': '<son id="3" href1=_url_ href2=_url_>',
            'test_tag1': '<span|a *=label>',
            'test_tag2': '<(span|a) *=label>',
            'test_tag3': '<span|a __TAG__=mi_nametag_var *=label>',
            'test_tag4': '<__TAG__ *="[sb].+?"=label>',
            'test_tag5': '<__TAG__ __TAG__=mi_nametag_var *=".+?"=label>',
            'test_tag6': '<__TAG__ __TAG__="span|a"=mi_nametag_var *=label>',
            'test_nzone1': '<span class=test *=label __EZONE__="[!--|script]">',
            'test_nzone2': '<span class=test *=label __EZONE__="">',
            'test_nzone3': '<span class=test *=label __EZONE__="[bloque]">',
            'test_nzone4': '<span class=test *=label __EZONE__="^[!--|script]">',
            'test_nzone5': '<a href=url *=label __EZONE__="^[!--]">',
        }
        token_gen = tokenizer.Tokenizer(REGEX_SCANNER)
        for case, regex_str in list(cases.items())[:1]:
            # regex_str = r'(?#' + regex_str + r')'
            console.rule(f'{case} = {regex_str}')
            tokens = [token for token in token_gen.tokenize(regex_str)]
            bflag = all([x.tag != 'ERROR' for x in tokens]) and False
            if not bflag:
                for token in token_gen.tokenize(regex_str):
                    console.print(token)
    elif test == 'htmlpointer':
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
        cp_pattern = re.compile('<blk1.*?/*>')
        # pointer = HTMLPointer(html_str, next_pattern=cp_pattern, exc_tags='[out]', seek_to_end=False)
        # console.print([html_str[b:e] for b, e in pointer()])

        pointer = HTMLPointer(html_str, next_pattern=cp_pattern, special_zones='[!--]^[out]', seek_to_end=False)
        console.print([html_str[b:e] for b, e in pointer()])
    elif test == 'extcompile':
        cases = {
            'No tag attribute': '<*=label>',
            '__TAG__ implicit': '<__TAG__=name>',
            'TestOptionalVars2': '<son id=_id_ href=_url_>',
            'minimo': '<table>',
            'all_text': '<hijo exp .*>',
            'test_namedvars': '<a href=url *=label>',
            'test_namedvarswithpattern1': '<a href="http://uno/.+?/tres.html">',
            'test_namedvarswithpattern2': '<a href="http://uno/.+?/tres.html" href=url *=label>',
            'test_implicitvars1': '<a (href)>',
            'test_implicitvars2': '<a (href) *=label>',
            'test_cleanvars': '<a (href) *=&label&>',
            'test_equivNotation': '<a href span{src=icon *=label} div.id>',
            'test_equivNotationII': '<table id td{1.*=grp1 2{b.*=grp2 a{href=grp2a src=grp2b}} 3.*=grp3 4.*=grp4}>',
            'test_tripleAsignation': '<ese a.*="http//.+?/prueba"=icon href=url>',
            'TestOptionalVars10': '<son href=_url_>',
            'TestOptionalVars11': '<son id=id href=_url_>',
            'TestOptionalVars3': '<son id=id href1="son2[^"]+"=_url_>',
            'TestOptionalVars5': '<son id=id href=url href1=_url_>',
            'TestOptionalVars6': '<son id=id href=url href1=_url_ grandson{href=__url__ *=label}>',
            'TestOptionalVars7': '<son id="3" href1=_url_ href2=__url__>',
            'test_tag1': '<span|a *=label>',
            'test_tag2': '<(span|a) *=label>',
            'test_tag3': '<span|a __TAG__=mi_nametag_var *=label>',
            'test_tag4': '<__TAG__ *="[sb].+?"=label>',
            'test_tag5': '<__TAG__ __TAG__=mi_nametag_var *=".+?"=label>',
            'test_tag6': '<__TAG__ __TAG__="span|a"=mi_nametag_var *=label>',
            'test_nzone1': '<span class=test *=label __EZONE__="[!--|script]">',
            'test_nzone2': '<span class=test *=label __EZONE__="">',
            'test_nzone3': '<span class=test *=label __EZONE__="[bloque]">',
            'test_nzone4': '<span class=test *=label __EZONE__="^[!--|script]">',
            'test_nzone5': '<a href=url *=label __EZONE__="^[!--]">',
            'test_relative_path': '<table id td{1.*=grp1 2{.b.*=grp2 .a{href=grp2a src=grp2b}} 3.*=grp3 4.*=grp4}>',
        }
        attrs = ('regex_pattern_str', 'tag_pattern', 'req_attrs', 'opt_attrs', 'var_list', '_e_zones')
        # attrs = ('tagPattern', 'tags', 'optTags', 'varList', '_maskTags')
        console.print('Inicio')
        for case, regex_str in list(cases.items()):
            regex_str = r'(?#' + regex_str + r')'
            comp_obj1 = compile(regex_str)
            comp_obj2 = ExtCompile(regex_str)
            try:
                bflag = comp_obj1 == comp_obj2
            except:
                bflag = False
            if not bflag:
                console.rule(f'{case} = {regex_str}')
                if isinstance(comp_obj1, ExtRegexObject):
                    table = Table()
                    table.add_column("Attribute", justify="right", style="cyan", no_wrap=True)
                    table.add_column("ExtCompile", style="magenta")
                    table.add_column("new_compile", justify="right", style="green")

                    for key in attrs:
                        table.add_row(key, str(getattr(comp_obj2, key, None)), str(getattr(comp_obj1, key, None)))
                    console.print(table)
        console.print('Final')
    elif test == 'tagpholder..*':
        htmlstr = '''
        <uno>
            primero
            <div>
                segundo
            </div>
            <div>
                tercero
            </div>
            cuarto
        </uno>
        '''
        m = search('(?#<uno .*>)', htmlstr)
        console.print(m)
    elif test == 'htmlpointer':
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
        (<table title="esto es un error"></table>
        (?#<table .[2].__TAG__=label>) label = span
        (?#<table .[2].__TAG__=lbl1 .[2].attr=lbl2>) lbl1=span, lbl2=hijo3
        (?#<table .[2]{__TAG__=lbl attr=lbl2}>) lbl1=span, lbl2=hijo3
        -->
        <table attr="padre">
            <span attr="hijo2">
                <row attr="hijo1">
                    <span attr="nieto">
                </row>
            </span>
            <medio>
                Esta etiqueta esta en el medio
            </medio>
            <row attr="hijo1">
                <col attr="nieto">
                    <span attr="bisnieto"/>
                </col>
            </row>
            <span attr="hijo3"/>
        </table>
    </head>
    <body>
    
    </body>
    </html>
        '''
        span = [(600, 758), (901, 966)]  # [(600, 932)]
        for pos in HTMLPointer(htmlstr, it_span=span):  # , next_pattern='<(table|row) ', it_span=):
            print(pos, htmlstr[pos: pos + 6])

    # (?P<PATTERN>(?:(?<=\=)(?P<quote>["'])(.*?)(?P=quote)(?=\s|>|=)))
    # equis="esto\" es uno"\nequis="esto es otro"
    # pattern = '(?#<table ..attr=label>)'
    # pattern = '(?#<table .[1].attr=label>)'
    # pattern = '(?#<table .2.attr=label>)'
    # pattern = '(?#<table .[2].__TAG__=lbl1 .[2].attr=lbl2>)'
    # pattern = '(?#<table .[2].attr=label>)'
    # pattern = '(?#<table ..attr=lbl1>)'
    # m = search(pattern, htmlstr)

    print('Hola miundo')
