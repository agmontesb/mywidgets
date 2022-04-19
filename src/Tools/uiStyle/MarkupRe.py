# -*- coding: utf-8 -*-
'''
Created on 19/09/2015

@author: Alex Montes Barrios
'''
import functools
from builtins import StopIteration, ValueError
from collections import namedtuple, defaultdict, deque
import re
import itertools
from typing import Tuple, Callable, Any
from html.parser import HTMLParser
from enum import Enum

from src import tokenizer

TAG_PATTERN_DEFAULT = r'[a-zA-Z][^\s>]*'

ATTRSEP = r'.'
COMMSEP = r'*'
TAGPHOLDER = r'tagpholder'

# Tipo de pseudo attributos
TEXTO = r'*'
PARAM_POS = r'*ParamPos*'
TAG = r'__TAG__'
N_CHILDREN = r'__N_CHILDREN__'
N_CHILD = r'__N_CHILD__'
N_TAG = r'__N_TAG__'

PSEUDO_ATTRS = set([TEXTO, PARAM_POS, TAG, N_CHILDREN, N_CHILD, N_TAG])

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
        (?=\s|>|<)                 # La sigue uno o mas espacios o >
     )) |           
    (?P<VAR>(?:
        (?<=\=)                 # Precedida por el signo igual
        (?:_{,2}|&)*           # Indica variable opcional(_) o clean var (&)
        [a-zA-Z][a-zA-Z\.\d_]*?        # Nombre de la variable
        (?:_{,2}|&)*           # Indica variable opcional(_) o clean var (&)
        (?=\s|>|<|\})             # Siempre seguida por ' ', > o }
     )) |           
    (?P<ATTRIBUTE>(?:
        [a-zA-Z\*\.\d][a-zA-Z\d\.\[\]\*]*?        # Nombre de atributo
        (?=\=|>|<|\s)
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
        (?=\s|>|<|=)          # Nota: Esto no acepta espacios en el pattern luego de un scape quote
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

ATTR_SCANNER = re.compile(r'''
    (?P<SEPARATOR>(?:
          (?:<) |                       # Inicio Pattern
          (?:>)                         # Inicio Pattern
    )) |
    (?P<WHITESPACE>\s+) |           # string
    (?P<TAG_PATTERN>(?:
        (?<=<)\s*?                   # Precedida por < y posiblemente espacios
        \(*(?:__TAG__|[A-Za-z].*?)\)*   # Pattern tag
        (?!=)
        (?=\s|>|<)                 # La sigue uno o mas espacios o >
     )) |           
    (?P<ATTRIBUTE>(?:
        (?<=\ )          # Debe estar precedido por el espacio 
        [a-zA-Z\*\.\d][a-zA-Z\d\.\[\]\*-_]*?        # Nombre de atributo
        (?=\=|>|<|\s)
     )) |           
    (?P<ATTR_PATTERN>(?:
        (?<=\=)          # Debe estar precedido por el = 
        (?:
            (?P<quote>["'])(.*?)(?P=quote) |      # standar attr pattern
            ([^=]+?)                                 # No quote attr pattern
        )
        (?=\s|>|<|=)          # Nota: Esto no acepta espacios en el pattern luego de un scape quote
    )) |
    (?P<ASIGNATION>(?:
        =                   # Igual
    )) | 
    (?P<ERROR>.)                    # an error
    ''', re.DOTALL | re.VERBOSE)

Token = namedtuple('Token', ['type', 'value'])


# Tipo de pattterns compuestos
class CPatterns(Enum):
    ZIN = '<<>>'
    CHILDREN = '<<>*>'
    NXTTAG = '<><>'
    PRECEDES = '<>*<>'
    PARENT = '<*<>>'
    SIBLINGS = '<>=<>'

    def __eq__(self, other):
        if isinstance(other, str):
            return self.value == other
        return super().__eq__(other)


class MarkupReError(Exception):
    pass


class TreeElement:
    def __init__(self, span, tag, attrs):
        self.span = span
        self.tag = tag
        self.attrs = attrs
        self.children = []
        self._root = ''

    def __repr__(self):
        return f'TreeElement({self.span}, {self.tag})'

    def __lt__(self, other):
        return self.span[0] < other.span[0]

    def __eq__(self, other):
        return self.span == other.span

    def add(self, *children):
        self.children.extend(children)

    @property
    def root_path(self):
        return self._root

    @root_path.setter
    def root_path(self, path):
        self._root = path
        pass

    @property
    def full_path(self):
        n = self.attrs.get(N_TAG, 1)
        full_path = f'{self._root}.{self.tag}[{n}]'.strip('.').replace('[1]', '')
        return full_path

    def attr_span(self, key=None):
        attr_spans = self.attrs.get(PARAM_POS, {})
        if key is None:
            return attr_spans
        return attr_spans.get(key, None)


class ExtRegexObject:
    def __init__(self, regex_pattern_str, regex_flags, tag_pattern, srch_attrs, var_list, e_zones):
        self.regex_pattern_str = self.pattern = regex_pattern_str
        self.regex_flags = self.flags = regex_flags
        self.tag_pattern = tag_pattern
        varNames = []
        self.groupindex = {}
        for element_path, attr_name in var_list:
            itemName = attr_name.strip('_') if attr_name != TAG else attr_name
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
            if var != TAG and var != var.strip('_')
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

        # match_factory = MatchObjectFactory(tag_pattern, srch_attrs, var_list)
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
            root_tag = TAGPHOLDER
            # Atributos no utilizables para encontrar candidato a solución
            exc_attr = PSEUDO_ATTRS.copy()
            # Adicionalmente debemos retirar los atributos opcionales
            opt_attrs = [
                attr.rsplit(ATTRSEP, 1)[-1]
                for attr, var in self.var_list
                if attr.startswith(root_tag) and var != var.strip('_')
            ]
            exc_attr.update(opt_attrs)
            diff_set = self.req_attrs.get(root_tag, {}).keys() - exc_attr
            if diff_set:
                myfunc = lambda x: rf'<{self.tag_pattern}\s[^>]*{"=[^>]+".join(x)}=[^>]+[/]*>'
                srch_pattern = '|'.join(map(myfunc, itertools.permutations(diff_set, len(diff_set))))
            else:
                srch_pattern = rf'<(?:{self.tag_pattern}).*?/*>'
            self._seeker = re.compile(srch_pattern, re.DOTALL | re.IGNORECASE)
        return self._seeker

    def match(self, html_string, pos=-1, endpos=-1, parameters=None):
        pos, max_pos = max(pos, 0), len(html_string)
        end_pos = endpos if endpos != -1 else max_pos

        parser = MarkupParser(self.var_list, self.req_attrs, self.opt_attrs)
        varPos = parser.check_match(html_string, pos, end_pos)
        if varPos:
            if self.var_list and f'{TAGPHOLDER}..*' in self.var_list[0][0]:
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
                m = self.match(html_string, beg_pos, end_pos, parameters=parameters)
                if m:
                    span_gen.send(m.end())
                    yield m

        return match_gen(html_string, pointer_pos)

    def search(self, html_string, spos=-1, sendpos=-1, parameters=None):
        try:
            it = self.finditer(html_string, spos, sendpos, parameters)
            answ = next(it)
        except StopIteration:
            answ = None
        return answ

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


class CompoundRegexObject(ExtRegexObject):
    def __init__(self, spanRegexObj, srchRegexObj, cpattern=CPatterns.ZIN, parameters=None):
        '''
        Ext RegexObject de dos etapas. Con spanRegexObj se determinan las zonas donde buscar
        en el documento. Con srchRegexObj se determina que buscar en una zona determinada.
        :param spanRegexObj: ExtRegexObject or CompoundRegexObject. Zonas donde buscar.
        :param srchRegexObj: ExtRegexObject or CompoundRegexObject. Que buscar.
        :param cpattern: CPatterns member. Relación entre spanRegexObj y srchRegexObj
        :param parameters: list(namedtuple) or None. Parámetros del CompoundRegexObject.
        '''
        pattern = self.get_compound_pattern(spanRegexObj, srchRegexObj, cpattern)
        self.spanRegexObj = spanRegexObj
        self.srchRegexObj = self.validateSrchRegexObj(srchRegexObj, cpattern)
        self.cpattern = cpattern
        self.spanDelim = None
        self.params = parameters or tuple()
        self._params_class = -1
        self.pattern = pattern
        self.flags = 0
        pass

    def __eq__(self, other):
        return all(
            [
                self.spanRegexObj == other.spanRegexObj,
                self.srchRegexObj == other.srchRegexObj,
            ]
        )

    def __getattr__(self, item):
        return getattr(self.srchRegexObj, item)

    @property
    def groupindex(self):
        return self.srchRegexObj.groupindex

    @property
    def params_class(self):
        if self._params_class == -1:
            fields = tuple()
            co = self.spanRegexObj
            while True:
                fields = tuple(sorted(co.groupindex.keys())) + fields
                if not isinstance(co, self.__class__):
                    break
                co = co.spanRegexObj
            param_class = namedtuple('zinparams', fields)
            self._params_class = param_class
        return self._params_class

    @property
    def searchFlag(self):
        return self.srchRegexObj.searchFlag

    @searchFlag.setter
    def searchFlag(self, value):
        self.srchRegexObj.searchFlag = value
        self.spanRegexObj.searchFlag = value

    @classmethod
    def validateSrchRegexObj(cls, srchRegexObj_in, cpattern):
        srchRegexObj = srchRegexObj_in
        if cpattern != CPatterns.ZIN:
            # Se alteran los datos básicos del RegexObj para adecuarla
            # a la condición de CHILDREN
            while isinstance(srchRegexObj, cls):
                srchRegexObj = srchRegexObj.spanRegexObj
            if not isinstance(srchRegexObj, ExtRegexObject):
                raise MarkupReError('SrchRegexObj not a valid RegExObject')
            tag_pattern = srchRegexObj.tag_pattern
            req_attrs = srchRegexObj.req_attrs
            spattern = srchRegexObj.pattern[4:-2]
            bflag = TAGPHOLDER not in req_attrs or TAG not in req_attrs[TAGPHOLDER]
            if bflag:
                req_tagpholder = req_attrs.setdefault(TAGPHOLDER)
                spattern = spattern.split(' ', 1)[-1]
                if tag_pattern != TAG_PATTERN_DEFAULT:
                    spattern = f'__TAG__ __TAG__="{tag_pattern}" {spattern}'
                    req_tagpholder[TAG] = re.compile(tag_pattern + '\\Z', re.DOTALL)
                    tag_pattern = TAG_PATTERN_DEFAULT
                else:
                    spattern = f'__TAG__ {spattern}'
                    req_tagpholder[TAG] = ''
            srchRegexObj.tag_pattern = tag_pattern
            # req_attrs = srchRegexObj.req_attrs
            srchRegexObj.pattern = f'(?#<{spattern}>)'
        return srchRegexObj

    @classmethod
    def get_compound_pattern(cls, spanRegexObj, srchRegexObj, cpattern):
        '''
        Entrega el pattern compuesto correspondiente a spanRegexObj y srchRegexObj cuando
        se combinan en un zone wrapper zone.
        :param spanRegexObj: ExtRegexObject or CompoundRegexObject. RegexObject para determinar
                            las zonas de búsqueda.
        :param srchRegexObj: ExtRegexObject or CompoundRegexObject. RegexObject para determinar
                            que buscar en una zona de búsqueda determinada.
        :param cpattern: CPatterns member.
        :return: str.
        '''
        pattern1 = spanRegexObj.pattern[4:-2] if not isinstance(spanRegexObj, cls) else spanRegexObj.pattern[3:-1]
        pattern2 = srchRegexObj.pattern[4:-2] if not isinstance(srchRegexObj, cls) else srchRegexObj.pattern[3:-1]
        match cpattern:
            case CPatterns.ZIN:
                pattern = f'(?#<{pattern1}<{pattern2}>>)'
            case CPatterns.CHILDREN:
                pattern = f'(?#<{pattern1}<{pattern2}>*>)'
            case CPatterns.NXTTAG:
                pattern = f'(?#<{pattern1}><{pattern2}>)'
            case _:
                pattern = ''
        return pattern

    def match(self, html_string, pos=-1, endpos=-1, parameters=None):
        return self.srchRegexObj.match(html_string, pos, endpos, parameters)

    def finditer(self, html_string, pos=-1, endpos=-1, seek_to_end=False, parameters=None):
        bflag = not self.cpattern == CPatterns.ZIN  # Con esto se asegura que el puntero se va al final

        # del span que es lo que se quiere en caso de
        # '<<>*>'(children) y de '<><>' (nexttag)
        def match_gen(html_string):
            for match_srchobj in self.spanRegexObj.finditer(
                    html_string, pos, endpos, seek_to_end=False, parameters=parameters
            ):
                params = match_srchobj.parameters
                if match_srchobj.groupdict():
                    params = tuple(
                        [
                            *params,
                            *tuple(
                                value for _, value in sorted(match_srchobj.groupdict().items())
                            )
                        ]
                    )
                    params = self.params_class(*params)
                span_beg_pos, span_end_pos = match_srchobj.span()
                match self.cpattern:
                    case CPatterns.ZIN | CPatterns.CHILDREN:
                        it = self.srchRegexObj.finditer(
                            html_string, span_beg_pos + 1, span_end_pos,
                            seek_to_end=bflag, parameters=params
                        )
                    case CPatterns.NXTTAG | CPatterns.PRECEDES:
                        beg_pos = html_string[span_end_pos + 1: endpos].find('<')
                        if beg_pos > 0:
                            method_name = 'match' if self.cpattern == CPatterns.NXTTAG else 'search'
                            method = getattr(self.srchRegexObj, method_name)
                            beg_pos += span_end_pos + 1
                            # if self.cpattern == CPatterns.NXTTAG:
                            #     tag = re.split('[\s>]', html_string[beg_pos:], 1)[0].strip('<')
                            #     end_tag = f'</{tag}>'
                            #     end_pos = html_string[beg_pos:].find(end_tag) + beg_pos + len(end_tag)
                            # else:
                            #     end_pos = len(html_string)
                            # m = method(html_string, beg_pos, end_pos, parameters=params)
                            m = method(html_string, beg_pos, parameters=params)
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
        self.parameters = parameters or tuple()
        pass

    def _varIndex(self, x):
        nPos = self.groupindex[x] if isinstance(x, str) else int(x)
        if nPos > len(self.varpos): raise Exception
        return nPos

    def expand(self, template):
        pass

    def group(self, *grouplist):
        grouplist = grouplist or [0]
        answer = []
        for group in grouplist:
            span = self.span(group)
            if span == (-1, -1):
                answer.append(None)
            elif isinstance(span, tuple):
                posIni, posFin = span
                answer.append(self.string[posIni:posFin])
            else:
                texto = '' if span == [] else ' '.join(
                    map(lambda posIni, posFin: self.string[posIni:posFin], *zip(*span))
                )
                answer.append(texto)
        return answer if len(answer) > 1 else answer[0]

    def groups(self, default=None):
        answ = tuple()
        if len(self.varpos) > 1:
            grp_ids = [k for k in range(len(self.varpos))]
            answ = tuple(grp_str if grp_str is not None else default for grp_str in self.group(*grp_ids)[1:])
        return answ

    def groupdict(self, default=None):
        keys = sorted(list(self.groupindex.keys()), key=lambda x: self.groupindex[x])
        values = self.groups(default=default)
        return {key: value for key, value in zip(keys, values)}

    def start(self, group=0):
        return self.span(group)[0]

    def end(self, group=0):
        return self.span(group)[1]

    def span(self, group=0):
        nPos = self._varIndex(group)
        return self.varpos[nPos]


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
                tag = re.match(r'<(.+?)(?:\s|>)', html_str[beg_pos:end_inner]).group(1)
                pattern = fr'(?:<{tag}(\s[^>]+?)*(?<!/)>)|(?:</{tag}>)'
                cp_pattern = re.compile(pattern, re.IGNORECASE | re.DOTALL)
                ene = 1
                while ene:
                    beg_inner = self.find(cp_pattern, use_sectors=False)
                    if not beg_inner:
                        break
                    ene += 1 if html_str[beg_inner:self.pos][:2] != '</' else -1
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

    def start_tag(self, span, tag, attribs):
        root = self.path
        self.path = path = self.get_path(tag)
        attribs.append((N_CHILD, self.n_children[root]))
        self.stack.append([tag, path, span, attribs])
        pass

    def end_tag(self, span, tag):
        posini, posfin = span
        while self.stack:
            stck_tag, stck_path, stck_span, stck_attribs = self.stack.pop()
            bflag = tag == stck_tag
            tag_span = (stck_span[0], posfin) if bflag else stck_span
            stck_attribs.append((N_CHILDREN, self.n_children.get(self.path, 0)))
            self.path = self.path.rsplit('.', 1)[0]
            self.bd_tags.append([tag_span, stck_path, stck_attribs, None])
            if bflag:
                break
        if self.path and not self.stack:
            raise MarkupReError('ParseError: Bad file format')

    def start_end_tag(self, span, tag, attribs):
        root = self.path
        path = self.get_path(tag)
        attribs.append([N_CHILD, self.n_children[root]])
        attribs.append([N_CHILDREN, 0])
        self.bd_tags.append([span, path, attribs, -1])
        pass

    def process_data(self, span, data):
        if self.bd_tags and self.bd_tags[-1][1] == TEXTO:
            data_span = self.bd_tags[-1][0]
            if data_span[1] == span[0]:
                self.bd_tags[-1][0] = (data_span[0], span[1])
                return
        if not data.strip(' \t\n\r\f\v'):
            return
        self.bd_tags.append([span, TEXTO, None, None])


class MarkupParser(HTMLParser):
    CDATA_CONTENT_ELEMENTS: tuple[str, ...] = tuple()

    def __init__(self, var_list=None, req_attrs=None, opt_attrs=None):
        super().__init__()
        self.var_list = var_list = var_list or []
        self.req_attrs = req_attrs = req_attrs or {}
        self.opt_attrs = opt_attrs = opt_attrs or {}

        self.pathIndex = []
        self.var_map = {}
        var_names = []
        for item_path, item_key in var_list:
            self.pathIndex.append(item_path)
            item_name = item_key.strip('_') if item_key != TAG else item_key
            if item_name in var_names:
                k = var_names.index(item_name) + 1
            else:
                var_names.append(item_name)
                k = len(var_names)
            self.var_map[item_path] = k
        self.var_pos = [(-1, -1) for x in range(len(var_names) + 1)]

        self.pos = 0
        self.data_offset = 0
        self.totLen = 0
        self.stackPath = ''
        self.tagStack = []
        self.tagList = []
        self.n_children = {}
        self.path_dict = {}

    @staticmethod
    def abs_coord(span_in, offset):
        if not span_in:
            return span_in
        x, y = span_in
        offset = offset if span_in != (-1, -1) else 0
        answ = (x + offset, y + offset)
        return answ

    @staticmethod
    def get_attrs_pos(str_in, out_offset=0):
        def store_tuple(pini, pfin):
            dini = 1 if str_in[pini] in '\'"' else 0
            dfin = -1 if str_in[pfin - 1] in '\'"' else 0
            answ.append((pini + dini + out_offset, pfin + dfin + out_offset))
            return dini, dfin

        regex_str = f'<{str_in.strip(" </>")}>'
        offset = str_in.find(regex_str[:-1])
        tokens = tokenizer.Tokenizer(ATTR_SCANNER, skipTokens=tuple())
        tokens_it = tokens.tokenize(regex_str)
        answ = []
        dini = dfin = 0
        for token in tokens_it:
            # print(token)
            match token.tag:
                case 'TAG_PATTERN':
                    pini = offset
                    pfin = tokens.pos + offset
                    answ.append(TAG)
                    dini, dfin = store_tuple(pini + 1, pfin)
                case 'ATTR_PATTERN':
                    pfin = tokens.pos + offset
                    dini, dfin = store_tuple(pini, pfin)
                case 'ATTRIBUTE':
                    attr = token.value
                    bflag = dini == -dfin
                    if bflag:
                        answ.append(attr)
                        if tokens.peek().tag in ['WHITESPACE', 'SEPARATOR']:
                            answ.append(tuple())
                case 'ASIGNATION':
                    pini = tokens.pos + offset
                case 'WHITESPACE' | 'SEPARATOR':
                    if tokens.getPrevToken().tag == 'ERROR' and tokens.peek().tag != 'ERROR':
                        if isinstance(answ[-1], tuple):
                            answ.pop()
                        dini, dfin = store_tuple(pini, pfin)
                case 'ERROR':
                    pfin = tokens.pos + offset
                    pass
        answ = dict(zip(answ[::2], answ[1::2]))
        return answ

    @staticmethod
    def adjust_end_points(data: str, beg_pos: int, end_pos: int) -> Tuple[int, int]:
        '''

        :param data: str. String a verificar.
        :param beg_pos: int. Posición inicial a verificar.
        :param end_pos: int. Posición final a verificar.
        :return: Tuple[int, int]. Posiciones ajustadas.
        '''
        message = f'adjust_end_points: Not a markup type string'
        try:
            x_dmy = data[beg_pos:end_pos].index('<') + beg_pos
            y_dmy = data[beg_pos:end_pos].rindex('>') + beg_pos + 1
        except ValueError:
            raise MarkupReError(message)
        return x_dmy, y_dmy

    def parse(self, data: str, beg_pos: int, max_pos: int, efilter: Callable[[Any], bool] = None):
        beg_pos, max_pos = self.adjust_end_points(data, beg_pos, max_pos)
        efilter = efilter or (lambda x: False)
        pos = beg_pos
        end_pos = data[pos:].find('>') + pos + 1  # Con esto se asegura que se inicializa el tagStack
        offset = pos
        while pos < max_pos:
            self.feed(data[pos:end_pos], offset)
            if not self.tagStack:
                break
            pos = end_pos
            end_tag = f'</{self.tagStack[0].tag}>'
            end_pos = data[pos:].find(end_tag)
            if end_pos == -1:
                break
            end_pos += pos + len(end_tag) + 1
            offset += self.pos
        if self.tagStack:
            raise MarkupReError(f'{self.__class__.__name__}: Incomplete parsing')
        root = self.tagList[-1]
        root.tag = TAGPHOLDER
        root.root_path = ''

        stack = deque([('', root)])
        to_process = []
        while stack:
            root_path, elem = stack.pop()
            elem.root_path = root_path
            elem.attrs[N_CHILDREN] = len(elem.children)
            if efilter(elem):
                to_process.append(elem)
            n_child: dict[str, int] = defaultdict(int)
            for k, child in enumerate(elem.children):
                n_child[child.tag] += 1
                child.attrs[N_TAG] = n_child[child.tag]
                child.attrs[N_CHILD] = k + 1
                stack.insert(0, (elem.full_path, child))
        return to_process or root

    def feed(self, data, offset=0):
        self.data_offset = offset
        self.pos = 0
        super().feed(data)

    def check_tagpholder(self, data, beg_pos, end_pos):
        beg = data[beg_pos:].find('<') + beg_pos  # Con esto se asegura que se inicializa el tagStack
        end = data[beg:].find('>') + beg + 1  # Con esto se asegura que se inicializa el tagStack
        bflag = end <= end_pos
        if bflag:
            param_pos = self.get_attrs_pos(data[beg:end], beg)
            attrs = {key: data[x:y] for key, (x, y) in param_pos.items()}
            attrs[PARAM_POS] = param_pos
            req_attrs = self.req_attrs.get(TAGPHOLDER, {}).copy()
            # Se eliminan los atributos que no se encuentran en la declaración del tag,
            # por ejemplo TEXTO que se encuentra luego de procesar el tag.
            non_req_attrs = tuple(
                req_attrs.pop(key) for key in (TEXTO,) if req_attrs.get(key, None) is not None
            )
            bflag = self.haveTagAllAttrReq(TAGPHOLDER, attrs, req_attrs)
            cflag = not (self.req_attrs.keys() - (TAGPHOLDER, )) and len(non_req_attrs) == 0
            cflag = cflag and f'{TAGPHOLDER}..*' not in self.var_map
            if bflag and cflag:
                return TreeElement((beg_pos, end_pos), TAGPHOLDER, attrs)
        return bflag

    def check_match(self, data: str, beg_pos: int, end_pos: int):
        # Se verifica que el tag inicial (tagpholder) tenga los atributos requeridos
        pholder = self.check_tagpholder(data, beg_pos, end_pos)
        match pholder:
            case False:
                return
            case TreeElement(full_path=fpath):
                to_process = [pholder]
            case _:
                req_set = set(self.req_attrs.keys())
                opt_set = set(self.opt_attrs.keys()).difference(req_set)
                req_set = req_set.union(opt_set)
                rel_path = sorted(
                    [x for x in req_set if x.find('..') != -1], key=lambda x: x.count('.')
                )
                efilter = functools.partial(self.is_req_path, req_set=req_set, rel_path=rel_path)
                to_process = self.parse(data, beg_pos, end_pos, efilter)
                if req_set or rel_path:
                    return
        if f'{TAGPHOLDER}..*' in self.var_map:
            var_pos = [to_process[0].span]
            while to_process:
                elem = to_process.pop()
                var_pos.extend(elem.attr_span(TEXTO))
                to_process.extend(elem.children)
            self.var_pos = sorted(var_pos)
            self.var_map = dict(('grp%s' % k, k) for k in range(1, len(self.var_pos)))
        else:
            self.var_pos = [(-1, -1) for x in range(len(self.var_pos))]
            optValues: dict[str, tuple[int, int]] = {}
            self.var_pos[0] = to_process[0].span
            for element_info in to_process:
                element_attrs = element_info.attrs
                element_path = element_info.full_path
                if not self.haveTagAllAttrReq(element_path, element_attrs):
                    return None
                self.storeReqVars(element_path, element_attrs, optValues)
            for key in self.pathIndex:
                value = optValues.get(key, None)
                if value is None:
                    continue
                k = self.var_map[key]
                self.var_pos[k] = value
        return self.var_pos

    def storeReqVars(self, element_path, element_attrs, optValues):
        paramPos = element_attrs.pop(PARAM_POS)
        req_attrs = self.req_attrs.get(element_path, {})
        for attr in req_attrs:
            fullAttr = element_path + ATTRSEP + attr
            if fullAttr not in self.var_map:
                continue
            if req_attrs[attr] and req_attrs[attr].groups:
                m = req_attrs[attr].match(element_attrs[attr])
                optValues[fullAttr] = self.abs_coord(m.span(1), paramPos[attr][0])
            else:
                optValues[fullAttr] = paramPos[attr]

        opt_attrs = self.opt_attrs.get(element_path, {})
        for attr in opt_attrs:
            fullAttr = element_path + ATTRSEP + attr
            if attr not in paramPos:
                continue
            if opt_attrs[attr]:
                m = opt_attrs[attr].match(element_attrs[attr])
                if not m:
                    continue
                if not opt_attrs[attr].groups:
                    optValues[fullAttr] = paramPos[attr]
                else:
                    offset = paramPos[attr][0]
                    optValues[fullAttr] = self.abs_coord(m.span(1), offset)
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
            req_attrs = self.req_attrs.get(element_path, {})
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
            tagAttr[TEXTO] = ''
            tagName = tagAttr[TAG]
            posBeg = posEnd = posEnd - len('</' + tagName + '>')
            tagAttr[PARAM_POS][TEXTO] = (posBeg, posEnd)
        elif n > 0:
            posBeg, posEnd = tagList[n][0]
            tagAttr[TEXTO] = data[posBeg:posEnd]
            tagAttr[PARAM_POS][TEXTO] = tagList[n][0]
        return tagAttr

    def get_path(self, tag):
        path = self.stackPath
        self.n_children[path] = self.n_children.get(path, 0) + 1
        path += f'.{tag}'
        self.path_dict[path] = n = self.path_dict.setdefault(path, 0) + 1
        answ = path + ('' if n == 1 else f'[{n}]')
        return answ

    def is_req_path(self, element: TreeElement, req_set: set, rel_path: list):
        pathTag = element.full_path
        efe = lambda x, path_tag: not (
                path_tag.startswith(x.split('..')[0]) and path_tag.endswith(x.split('..')[1]))
        if pathTag in req_set:
            req_set.difference_update([pathTag])
            return True
        if rel_path:
            rpos = list(itertools.takewhile(lambda x: efe(x, pathTag), rel_path))
            npos = len(rpos) + 1
            if npos <= len(rel_path):
                pathTag = rel_path.pop(npos - 1)
                req_set.difference_update([pathTag])
                return True
        return False

    def getSpan(self, entityStr):
        posini = self.pos
        self.pos = posfin = posini + len(entityStr)
        self.totLen += len(entityStr)
        return posini + self.data_offset, posfin + self.data_offset

    def handle_starttag(self, tag, attrs):  # startswith('<')
        attrs = dict(attrs)
        starttag_text = self.get_starttag_text()
        posini, posfin = self.getSpan(starttag_text)
        root = self.stackPath
        self.stackPath = path = self.get_path(tag)
        # attrs[N_CHILD] = self.n_children[root]
        attrs[TAG] = tag
        attrs.setdefault(TEXTO, '')
        param_pos = self.get_attrs_pos(starttag_text, posini)
        param_pos.setdefault(TEXTO, [])
        attrs[PARAM_POS] = param_pos
        self.tagStack.append(TreeElement((posini, posfin), tag, attrs))

    def handle_endtag(self, tag):  # startswith("</")
        posini, posfin = self.getSpan('</%s>' % tag)
        while self.tagStack:
            try:
                stck_tag = self.tagStack.pop()
                self.tagList.append(stck_tag)
                bflag = stck_tag.tag == tag
                if bflag:
                    stck_tag.span = (stck_tag.span[0], posfin)
                    self.tagStack[-1].add(stck_tag)
                    break
                # Transferimos los hijos al nivel superior
                self.tagStack[-1].add(stck_tag, *stck_tag.children)
                stck_tag.children = []
            except:
                break
        if not bflag:
            raise MarkupReError(f'{self.__class__.__name__}: Unexpected end tag')

    def handle_startendtag(self, tag, attrs):
        attrs = dict(attrs)
        starttag_text = self.get_starttag_text()
        posini, posfin = self.getSpan(starttag_text)
        root = self.stackPath
        # attrs[N_CHILD] = self.n_children[root]
        # attrs[N_CHILDREN] = 0
        attrs[TAG] = tag
        attrs.setdefault(TEXTO, '')
        param_pos = self.get_attrs_pos(starttag_text, posini)
        param_pos.setdefault(TEXTO, [])
        attrs[PARAM_POS] = param_pos
        tag_path = self.get_path(tag)
        # tag_path = self.get_req_path(tag_path, None)
        self.tagList.append(te := TreeElement((posini, posfin), tag, attrs))
        self.tagStack[-1].add(te)

    def storeDataStr(self, dataIn):
        dSpanIn = self.getSpan(dataIn)
        dataIn = dataIn.strip(' \t\n\r\f\v')
        if dataIn:
            attrs = self.tagStack[-1].attrs
            attrs_pos_map = attrs[PARAM_POS]
            texto_span = attrs_pos_map.setdefault(TEXTO, [])
            texto_span.append(dSpanIn)
            texto = attrs.setdefault(TEXTO, '')
            attrs[TEXTO] = ' '.join([texto, dataIn]).strip()

    def handle_data(self, data):
        b_pos = self.pos
        e_pos = self.rawdata[b_pos:].find('<') + b_pos
        new_data = self.rawdata[b_pos: e_pos]
        self.storeDataStr(new_data)

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

    regexobj_stack = []
    separator_stack = []
    pini = 0
    tokens = tokenizer.Tokenizer(REGEX_SCANNER)
    tokens_it = tokens.tokenize(regex_str)
    while True:
        try:
            token = next(tokens_it)
        except StopIteration:
            break
        if tokens.getPrevToken().tag == 'SEPARATOR' and token.tag != 'SEPARATOR':
            # Reset variables del regexobj
            prefix_stack = [TAGPHOLDER]
            prefix = TAGPHOLDER
            attribute = ''
            n_implicit = 0

            tag_pattern = TAG_PATTERN_DEFAULT
            tags = {}
            varList = []
            maskParam = etags_str

        match token.tag:
            case 'SEPARATOR':
                pfin = tokens.pos
                end = len(token.value)
                compile_type = regex_str[pini: pfin - end]
                if compile_type:
                    compile_type, zini = separator_stack.pop() if separator_stack else ('', 0)
                    compile_type += token.value
                match compile_type:
                    case '':
                        separator_stack.append((token.value, pini))
                    case '<>' | '<*<>' | '<><' | '<>*<' | '<<':
                        if compile_type != '<>':
                            separator_stack.append((compile_type, zini))
                        end = len(token.value)
                        pfin = tokens.pos
                        spattern = f'(?#<{regex_str[pini: pfin - end]}>)'
                        regex_obj1 = ExtRegexObject(spattern, flags, tag_pattern, tags, list(varList), maskParam)
                        regexobj_stack.append(regex_obj1)
                    case CPatterns.ZIN | CPatterns.CHILDREN | CPatterns.NXTTAG | CPatterns.PRECEDES:
                        cpattern = CPatterns(compile_type)
                        regex_obj1 = regexobj_stack.pop()
                        spattern = f'(?#<{regex_str[pini: pfin - end]}>)'
                        regex_obj2 = ExtRegexObject(spattern, flags, tag_pattern, tags, list(varList), maskParam)
                        regexobj = CompoundRegexObject(
                            regex_obj1, regex_obj2, cpattern
                        )
                        regexobj_stack.append(regexobj)
                        if separator_stack:
                            try:
                                token = next(tokens_it)
                                assert token.tag == 'SEPARATOR'  # Se verifica que el próximo tag es un SEPARATOR
                            except StopIteration:
                                raise MarkupReError(f'Incomplete pattern')
                            except AssertionError:
                                raise MarkupReError(f'{compile_type}: expected SEPARATOR at position {pfin}')
                            compile_type, zini = separator_stack.pop()
                            compile_type += token.value
                            separator_stack.append((compile_type, zini))
                            pfin = tokens.pos
                        pass
                    case CPatterns.PARENT | CPatterns.SIBLINGS:
                        raise MarkupReError(f'{compile_type} not yet implemented')
                    case _:
                        raise MarkupReError(f'{compile_type}: Unrecognizable compile type')
                pini = pfin
            case 'TAG_PATTERN':
                if token.value == TAG:
                    pass
                elif token.value != token.value.strip(')('):
                    tag_pattern = token.value[1:-1]
                    attribute = '.'.join([prefix, TAG])
                    element, attr = attribute.rsplit('.', 1)
                    attr_dict = tags.setdefault(element, {})
                    attr_dict.setdefault(attr, '')
                    varList.append([attribute, TAG])
                else:
                    tag_pattern = token.value
                tags.setdefault(TAGPHOLDER, {})
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
                if token.value == TAG:
                    attr_dict = tags.setdefault(element, {})
                    attr_dict.setdefault(attr, '')
            case 'ATTRIBUTE':
                value = token.value
                attribute = '.'.join([prefix, value])

                # Se normaliza la forma del atributo
                attribute = re.sub(r'\.(\d+)\.', r'.[\1].', attribute)
                attribute = attribute.replace('.[', '[').replace('[1]', '')

                if attribute == f'{TAGPHOLDER}..*':
                    if varList:
                        raise MarkupReError('With required Tag ".*", no vars are allowed')
                    # Se hace varList un tuple para evitar que puedan agregarse variables.
                    varList = ([f'{TAGPHOLDER}..*', 'text_tags'],)
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
    return regexobj_stack.pop()


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
    from rich.console import Console
    from rich.table import Table

    console = Console(color_system='truecolor')

    htmlStr1 = """
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
    htmlStr2 = """
    <span id="1" class="independiente">span0</span>
    <scripts id="2">
        <span class="bloque1">span1</span>
        <a href="http://www.eltiempo.com.co">El Tiempo</a>
        <span class="bloque1">span2</span>
    </scripts>
    <bloque id="3">
        <span class="independiente">bloque1</span>
        <parent id="root">
        <hijo id="hijo1">primer hijo</hijo>
        <hijo id="hijo2" exp="hijo con varios comentarios">
             <h1>El primer comentario</h1>
             <h1>El segundo comentario</h1>
             <h1>El tercer comentario</h1>
        </hijo>
        <hijo id="hijo3">tercer hijo</hijo>
        </parent>
        <span class="independiente">bloque2</span>
    </bloque>
    <!--
        <span class="bloque2">span1</span>
        <a href="http://www.elheraldo.com.co">El Heraldo</a>
        <span class="bloque2">span2</span>
    -->
    <span id="4" class="independiente">span3</span>
            """

    console.print('Inicio')
    test = 'ext_match'
    if test == 'ext_match':
        cmpobj = compile('(?#<__TAG__ __TAG__=mi_nametag_var id=id>)', etags_str='[<!--]')
        answer = cmpobj.findall(htmlStr2)
        required = [('span', '1'), ('scripts', '2'), ('bloque', '3'), ('span', '4')]
        assert answer == required, 'Utilizando __TAG__ como tagpattern'
    elif test == 'parse_attrs':

        cases = {
            'caso3': """<a href0="el 'tiempo com" href1="el 'tiempo" com' href2='el 'tiempo' com' href3=''el tiempo' com' href4='el 'tiempo com''>""",
            'caso1': """<a href2=eltiempo.com href1 href0="eltiempo.com">""",
            'caso4': """<hijo id="hijo2" exp="hijo con varios comentarios">""",
            'caso2': """<a href1="eltiempo.com' href0="eltiempo.com" href2='eltiempo.com' href3=eltiempo.com>""",
            'caso0': """<a href1="eltiempo.com" href2="eltiempo.com" href0="eltiempo.com">""",
        }
        items = [
            'href0',
            'href1="el tiempo com"',
            "href2='el tiempo com'",
            """href3="el 'tiempo' com\"""",
            """href4='el "tiempo" com'""",
            """href5='el tiempo com\"""",
            """href6="el tiempo com'""",
            """href7=''el tiempo' com'""",
            """href8='el tiempo 'com''""",
        ]
        caso = f'<a {" ".join(items)}>'

        ATTR_SCANNER = re.compile(r'''
            (?P<SEPARATOR>(?:
                  (?:<) |                       # Inicio Pattern
                  (?:>)                         # Inicio Pattern
            )) |
            (?P<WHITESPACE>\s+) |           # string
            (?P<TAG_PATTERN>(?:
                (?<=<)\s*?                   # Precedida por < y posiblemente espacios
                \(*(?:__TAG__|[A-Za-z].*?)\)*   # Pattern tag
                (?!=)
                (?=\s|>|<)                 # La sigue uno o mas espacios o >
             )) |           
            (?P<ATTRIBUTE>(?:
                (?<=\ )          # Debe estar precedido por el espacio 
                [a-zA-Z\*\.\d][a-zA-Z\d\.\[\]\*-_]*?        # Nombre de atributo
                (?=\=|>|<|\s)
             )) |           
            (?P<ATTR_PATTERN>(?:
                (?<=\=)          # Debe estar precedido por el = 
                (?:
                    (?P<quote>["'])(.*?)(?P=quote) |      # standar attr pattern
                    ([^=]+?)                                 # No quote attr pattern
                )
                (?=\s|>|<|=)          # Nota: Esto no acepta espacios en el pattern luego de un scape quote
            )) |
            (?P<ASIGNATION>(?:
                =                   # Igual
            )) | 
            (?P<ERROR>.)                    # an error
            ''', re.DOTALL | re.VERBOSE)


        def get_attrs_pos(str_in):
            def store_tuple(pini, pfin):
                dini = 1 if str_in[pini] in '\'"' else 0
                dfin = -1 if str_in[pfin - 1] in '\'"' else 0
                answ.append((pini + dini, pfin + dfin))
                return dini, dfin

            regex_str = f'<{str_in.strip(" </>")}>'
            offset = str_in.find(regex_str[:-1])
            tokens = tokenizer.Tokenizer(ATTR_SCANNER, skipTokens=tuple())
            tokens_it = tokens.tokenize(regex_str)
            answ = []
            dini = dfin = 0
            for token in tokens_it:
                print(token)
                match token.tag:
                    case 'TAG_PATTERN':
                        pini = offset
                        pfin = tokens.pos + offset
                        answ.append(TAG)
                        dini, dfin = store_tuple(pini + 1, pfin)
                    case 'ATTR_PATTERN':
                        pfin = tokens.pos + offset
                        dini, dfin = store_tuple(pini, pfin)
                    case 'ATTRIBUTE':
                        attr = token.value
                        bflag = dini == -dfin
                        if bflag:
                            answ.append(attr)
                            if tokens.peek().tag in ['WHITESPACE', 'SEPARATOR']:
                                answ.append(tuple())
                    case 'ASIGNATION':
                        pini = tokens.pos + offset
                    case 'WHITESPACE' | 'SEPARATOR':
                        if tokens.getPrevToken().tag == 'ERROR' and tokens.peek().tag != 'ERROR':
                            if isinstance(answ[-1], tuple):
                                answ.pop()
                            dini, dfin = store_tuple(pini, pfin)
                    case 'ERROR':
                        pfin = tokens.pos + offset
                        pass
            answ = dict(zip(answ[::2], answ[1::2]))
            return answ.items()


        # for case, elem in list(cases.items()):
        # for k in range(500):
        for k in range(1):
            # case, elem = f'caso{k}', f'<a {" ".join(random.sample(items, len(items)))}>'
            case, elem = f'caso{k}', '<meta content="width=device-width, initial-scale=1.0" name="viewport"/>'
            case, elem = f'caso{k}', """<a href7=''el tiempo' com' href0 href5='el tiempo com" href2='el tiempo com' href4='el "tiempo" com' href8='el tiempo 'com'' href1="el tiempo com" href3="el 'tiempo' com" href6="el tiempo com'>"""
            answ = dict(get_attrs_pos(elem))
            answ.pop(TAG)
            error = 'href0' not in answ
            for key, value in answ.items():
                if value:
                    beg, end = value
                    attr_val_raw = elem[beg:end]
                    attr_val = attr_val_raw.replace('"', '').replace('\'', '')
                    error = error or attr_val != 'el tiempo com'
                    # console.print(key, elem[beg:end])
                else:
                    # console.print(key, value)
                    error = error or key != 'href0'
            if error:
                console.rule(f'{case}, valid={not error}')
                console.print(elem)
                for key, (beg, end) in answ.items():
                    console.print(f'{key}={elem[beg:end]}')
        pass
    elif test == 'new_match_factory':
        new_fact = MarkupParser()
        new_fact.feed(htmlStr1)
        new_fact.close()
        sl = sorted(new_fact.tagList)
        console.print(
            [
                (n, m[N_CHILD], m[N_CHILDREN]) for n, m in
                [(x[3], dict(x[4])) for x in sl if x[1] != TEXTO]
            ]
        )
    elif test == 'zin':
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
    elif test == 'params':
        htmlStr = htmlStr1
        cases = {
            'Nested CPatterns3': '<<parent id=idp<hijo id="hijo2"=idh>*><h1 *="El segundo comentario">*>',
            'Nested CPatterns4': '<<bloque<hijo id="hijo2">><h1 *="El segundo comentario">*>',
            'Nested CPatterns2': '<<bloque<parent id="root">><h1 *="El segundo comentario">>',
        }
        for case, regex_str in list(cases.items())[:1]:
            regex_str = r'(?#' + regex_str + r')'
            comp_obj1 = compile(regex_str)
            answer = comp_obj1.search(htmlStr)

            # answer = [
            #     [m.params for m in comp_obj1.finditer(htmlStr)]
            # ]
            console.print(answer.parameters)
            pass
    elif test == 'nested_cpatterns':
        htmlStr = htmlStr1
        cases = {
            'Nested CPatterns4': '<<bloque<hijo id="hijo2">><h1 *="El segundo comentario">*>',
            'Nested CPatterns3': '<<parent<hijo id="hijo2">*><h1 *="El segundo comentario">*>',
            'Nested CPatterns2': '<<bloque<parent id="root">><h1 *="El segundo comentario">>',
        }
        for case, regex_str in list(cases.items())[:1]:
            regex_str = r'(?#' + regex_str + r')'
            comp_obj1 = compile(regex_str)

            answer = [
                htmlStr[a:b] for a, b in
                [m.span() for m in comp_obj1.finditer(htmlStr)]
            ]
            console.print(answer)
            pass
    elif test == 'extcompile':
        cases = {
            'Nested CPatterns1': '<bloque<row class="base">>',
            'test_namedvars': '<a href=url *=label>',
            'No tag attribute': '<*=label>',
            '__TAG__ implicit': '<__TAG__=name>',
            'TestOptionalVars2': '<son id=_id_ href=_url_>',
            'minimo': '<table>',
            'all_text': '<hijo exp .*>',
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
        for case, regex_str in list(cases.items()):
            regex_str = r'(?#' + regex_str + r')'
            comp_obj1 = compile(regex_str)
            # comp_obj2 = ExtCompile(regex_str)
            comp_obj2 = None
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
        console.print(m.groups())
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

    console.print('Final')
