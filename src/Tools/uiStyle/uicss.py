# TODO Crear clase Selector:
# Esta clase deberá al menos tener los siguientes métodos: parse, especificidad,
# comparadores como __lt__, __gt__, ... hechoss con base en especificidad.
# TODO: Crear Test para clase selector con ccs.py y un archivo que contenga los casos de
# ejemplo en w3school
import collections
import os
import re
import itertools
import urllib
from html.parser import HTMLParser
import xml.etree.ElementTree as ET

import src.Tools.uiStyle.MarkupRe as MarkupRe
from Widgets.Custom.network import network

THOUSANDS = 0
HUNDRES = 1
TENS = 2
ONES = 3

PATTERN = re.compile(r'(?:\:*[:\.#]*?[A-Za-z\d\-\+\_\(\)]+)|(?:\[.+?\])')
SPLIT_PATTERN = re.compile(r'((?:(?:\:*[:\.#]*?[A-Za-z\d\-\+\_\(\)]+)|(?:\[.+?\]))+)')
COMBINATORS = re.compile(r'([\+\>\ \~\,]+)')
ATTRIBUTES = re.compile(r'([\&\|\^\$\*]*=)')
CP_PATTERN = re.compile('\s*?((?:[^\{\s\*]+?\*?[^\{\*]+?)|(?:\*))\ *?(\{.+?\})', re.DOTALL)
STYLE_PATTERN = re.compile('^\s*?([^\s]+?)\s*:\s*([^;]+?);$', re.MULTILINE)


class MElement(ET.Element):

    def __init__(self, tag, attrib={}, *, tpos=None, sels=None, **extra):
        super().__init__(tag, attrib, **extra)
        self.sels = sels
        self.tpos = tpos
        self.src = None

    @property
    def raw_attrib(self):
        return super().attrib

    @property
    def attrib(self):
        sels = self.sels or []
        sels.sort()
        raw_attrib = self.raw_attrib
        attrib = dict(itertools.chain(*(sel.style_str.items() for sel in sels), raw_attrib.items()))
        if self.src and (pckg := self.src.pckg):
            cp = re.compile(r'@(.+?:)*(.+?)/(.+)')
            for key, value in attrib.items():
                if (m := cp.match(value)) and not m.group(1):
                    attrib[key] = f'@{pckg}:{m.group(2)}/{m.group(3)}'
        return attrib

    def set(self, key, value):
        super().set(key, value)

    def get(self, key, default=None):
        return self.attrib.get(key, default)

    def pop(self, key, default=None):
        return super().attrib.pop(key, default)

    def items(self):
        return self.attrib.items()


class XmlSerializer:  # The target object of the parser

    def __init__(self):
        self.style_strs = []
        self._style_ids = []
        self.wrapper = None
        self.stack = []
        self._data = []
        self._tail = None
        self._last_open = [('root', dict(_tag_='root', __NCHILDREN__=[]))]
        self._ntags = 0
        self._nclose = 0
        self._parser = None
        self.selectors = None
        self.src = None

    def __call__(self, htmlstr):
        self.src = getattr(htmlstr, 'src', '')
        self._parser = parser = ET.XMLParser(target=self)
        parser.feed(htmlstr)
        parser.close()
        return self.stack

    def getpos(self):
        return self._ntags, len(self._last_open) - 1

    def start(self, tag, attrib):  # Called for each opening tag.
        self._flush(self._nclose)
        attrib['_tag_'] = tag
        attrib[MarkupRe.N_CHILDREN] = []
        self._nclose = len(self.stack)
        self._last_open[-1][1][MarkupRe.N_CHILDREN].append(attrib)
        self._last_open.append((tag, attrib, len(self.stack)))
        self._ntags += 1
        self.stack.append(('starttag', tag, attrib, self.getpos()))
        self._tail = 0

    def end(self, tag):  # Called for each closing tag.
        self._flush(self._nclose)
        last_tag, last_attrib, self._nclose = self._last_open.pop()
        assert last_tag == tag, "end tag mismatch (expected %s, got %s)" % (
            last_tag, tag
        )
        self.stack.append(('endtag', tag, self.getpos()))

        children = last_attrib.pop(MarkupRe.N_CHILDREN)
        nchildren = len(children)
        last_attrib[MarkupRe.N_CHILDREN] = nchildren
        if nchildren:
            child_map = collections.Counter(
                child['_tag_'] for child in children
            )
            tag_count = collections.defaultdict(int)
            for k, child in enumerate(children):
                key = child.pop('_tag_')
                tag_count[key] += 1
                child.update([
                    (MarkupRe.NCHILD, k + 1),
                    (MarkupRe.LCHILD, nchildren - k),
                    (MarkupRe.NTAG, tag_count[key]),
                    (MarkupRe.LTAG, child_map[key] - tag_count[key] + 1),
                ])

        self._tail = 1
        if self.stack[-2][:2] == ('starttag', tag):
            # No se admiten otros elementos en un elemento que se instrumentaliza como style
            attribs = self.stack[-2][2]
            id = attribs.get('id', '')
            if id in self._style_ids:
                self._style_ids.remove(id)
                style_str = attribs.get('_text', '')
                self.style_strs.append(style_str)

    def start_ns(self, prefix, uri):
        self.stack.append(('start-ns', prefix, uri, self.getpos()))

    def end_ns(self, prefix):
        self.stack.append(('end-ns', prefix, self.getpos()))

    def comment(self, text):
        self.stack.append(('comment', text, self.getpos()))

    def pi(self, target, text=None):
        data = f'<{target} {text}>'
        attrs_pos = MarkupRe.MarkupParser.get_attrs_pos(data)
        attribs = {key: data[x:y] for key, (x, y) in attrs_pos.items()}
        if attribs['__TAG__'] == 'xml-stylesheet':
            match attribs.pop('type', "text/css"):
                case "text/css":
                    url = attribs.get('href', '')
                    if url.startswith('#'):
                        self._style_ids.append(url[1:])
                    else:
                        try:
                            data = self.getContent(url)
                            if isinstance(data, (bytes, str)):
                                self.style_strs.append(data)
                        except:
                            pass
                case _:
                    pass

    def data(self, data):
        data = data.strip(' \n')
        if data:
            self._data.append(data)

    def close(self):  # Called when all data has been parsed.
        # Se normaliza los style strs
        style_strs = '\n'.join(self.style_strs)
        self.selectors = self.process_css_string(style_strs)

    @staticmethod
    def process_css_string(css_string):
        # Se establece salto de línea en cada definición de selector.
        css_string = css_string.replace('{', '{\n').replace(';', ';\n').replace('\n\n', '\n')
        # Se eliminan los comentarios
        css_string = '\n'.join(re.split('/\*.+?\*/', css_string, flags=re.DOTALL))
        # Se hace equivalente la expresión tipo '(4n + 5)' a (4n+5)
        css_string = re.sub(
            r'\(\d+[a-z](\s*)[-+](\s*)\d+\)',
            lambda m: m.group(0).replace(' ', ''),
            css_string
        )

        css_tuples = CP_PATTERN.findall(css_string)
        selectors = []
        for select_str, style_str in css_tuples:
            selectors.extend([Selector(x.strip(), style_str) for x in select_str.split(',')])
        return selectors

    def _flush(self, npos=-1):
        if self._data:
            text = "".join(self._data)
            if self.stack:
                attribs = self.stack[npos][2]
                key = '_tail' if self._tail else '_text'
                msg = "internal error (tail)" if self._tail else "internal error (text)"
                assert key not in attribs, msg
                attribs[key] = text
            self._data = []

    @staticmethod
    def getContent(fileurl):
        if not urllib.parse.urlparse(fileurl).scheme:
            basepath = os.path.dirname(__file__)
            layoutpath = os.path.join(basepath, fileurl)
            layoutfile = os.path.abspath(layoutpath)
            layoutfile = f'file://{urllib.request.pathname2url(layoutfile)}'
        initConf = 'curl --user-agent "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.80 Safari/537.36" --cookie-jar "cookies.lwp" --location'
        net = network(initConf)
        content, _ = net.openUrl(layoutfile)
        return content


class HtmlSerializer(XmlSerializer, HTMLParser):

    def __init__(self):
        super().__init__()

    def __call__(self, htmlstr):
        self.feed(htmlstr)
        self.close()
        return self.stack

    def getpos(self):
        return HTMLParser.getpos(self)

    def handle_starttag(self, tag, attrs):  # startswith('<')
        dattrs = dict(attrs)
        self.start(tag, dattrs)
        if tag == 'link':
            self.pi(f'xml-{dattrs["rel"]}', ' '.join(f'{key}="{value}"' for key, value in dattrs.items()))

    def handle_endtag(self, tag):  # startswith("</")
        no_end = []
        while self._last_open[-1][0] != tag:
            no_end.append(self._last_open.pop())
        if no_end:
            children = []
            for npos, attrs, pos in no_end[::-1]:
                children.extend(attrs.pop(MarkupRe.N_CHILDREN))
            self._last_open[-1][1][MarkupRe.N_CHILDREN].extend(children)
            for etag, _, npos in no_end:
                self.stack.insert(npos + 1, ('endtag', etag, self.stack[npos][3]))
        self.end(tag)

    def handle_startendtag(self, tag, attrs):
        self.start(tag, dict(attrs))
        self.end(tag)

    def handle_data(self, data):
        # ... <tag ...>data</tag>
        # ... </tag>data<tag ...>
        if self._last_open[-1][0] == 'style':
            self.style_strs.append(data)
        self.data(data)
        pass

    def handle_entityref(self, name):  # startswith('&')
        print('handle_entityref', name)
        pass

    def handle_charref(self, name):  # startswith("&#")
        print('handle_charref', name)
        pass

    def handle_comment(self, data):  # startswith("<!--")
        # <!-- Esto es lo que entrega en data -->
        self.comment(data)
        pass

    def handle_decl(self, data):  # startswith("<!")
        # '<!doctype' -> doctype
        print('handle_decl', data)
        pass

    def handle_pi(self, data):  # startswith("<?")
        # <? esto es lo que entrega en data>
        self.pi(data)
        pass

    def unknown_decl(self, data):
        # '<![[mark content]]>' -> mark: "temp", "cdata", "ignore", "include", "rcdata",
        # '<![[mark content]]>' -> mark: "if", "else", "endif"
        self.pi(data)
        pass


class UiCssError(Exception):
    pass


class Selector:
    seq_gen = itertools.count()

    def __init__(self, selector_str, style_str='', cascade_priority=None):
        '''
        Objeto que representa la unidad mínima de especificidad del css
        :param selector_str: str. String que especifica el selector.
        :param style_str: str. Style asociado a este selector
        :param cascade_priority: object. Define que elemento tiene precedencia sobre otro
               cuando tienen igual specificity.
        '''
        if cascade_priority is None:
            cascade_priority = next(self.__class__.seq_gen)
        self._specificity = [0, 0, 0, 0, cascade_priority]
        # Se estandariza el style_str.
        self._style_str = style_str.replace('{', '{\n').replace(';', ';\n').replace('\n\n', '\n')
        self._selector_str = selector_str
        self._compiled_selector = None
        try:
            assert not selector_str.count(','), f'SelectorStrError: Aggregated patterns (,) not posible'
            cp = self._get_compiled_selector_pattern()
            pattern = cp.pattern
            assert isinstance(cp,
                              MarkupRe.ExtRegexObject) or cp.regex_pattern_str == '<', f'SelectorStrError: Not a valid MarkupRe object: {cp.regex_pattern_str}'
            self._compiled_selector = cp
        except (UiCssError, AssertionError) as e:
            self._pattern = str(e)
        else:
            self._pattern = pattern

    def __str__(self):
        return f"Selector('{self.selector_str}', '{self._style_str}')" if self._style_str else f"Selector('{self.selector_str}')"

    @property
    def style_str(self):
        '''
        :return: str. Style asociated with the selector.
        '''
        style_pairs = STYLE_PATTERN.findall(self._style_str)
        return dict(style_pairs)

    @property
    def selector_str(self):
        '''
        :return: str. CSS selector
        '''
        return self._selector_str

    @property
    def pattern(self):
        '''
        :return: str. MarkupRe pattern equivalente al CSS selector.
        '''
        return self._pattern

    @property
    def is_valid(self):
        '''
        :return: bool. True si self.pattern es una expresión válida.
        '''
        # DeprecationWarning('Property will be deprecated in next version.')
        return self.compiled_selector is not None

    @property
    def specificity(self):
        return self._specificity[:4]

    @property
    def compiled_selector(self):
        return self._compiled_selector

    def _get_basic_pattern(self, basic_selector):
        '''
        Entrega el pattern correspondiente a un selector básico para el MarkupRe
        Se entiende como básicos: *, p, .clase, #id, [attr]
        :param basic_selector: str. Descripción de un selector básico
        :return: str. MarkupRe pattern.
        '''
        items = PATTERN.findall(basic_selector)
        try:
            assert basic_selector == ''.join(items)
        except AssertionError:
            raise UiCssError(f"SelectorStrError: {basic_selector} is not a basic selector")
        bflag = items[0][0] in '.#[:'
        if not bflag:
            self._specificity[ONES] += 1
        basic_pattern = [f'{items.pop(0) if not bflag else "__TAG__"}']
        while items:
            selector = items.pop(0)
            case, selector = selector[0], selector[1:]
            if case == '.':  # case == '.': #clase
                self._specificity[TENS] += 1
                selector = '\\b \\b'.join(selector.split('.'))
                basic_pattern.append(f'class=".*?\\b{selector}\\b.*?"')
            elif case == '#':  # case == '#': #id
                self._specificity[HUNDRES] += 1
                basic_pattern.append(f'id="{selector}"')
            elif case == ':':
                # Hasta ahora
                if selector[0] != ':':  # case == ':' pseudo clases
                    self._specificity[TENS] += 1 if selector != 'where' else 0
                    # Tree-structural pseudo-classes
                    if selector in (
                            'empty', 'first-child', 'last-child', 'only-child',
                            'first-of-type', 'last-of-type', 'only-of-type',
                    ):
                        match selector:
                            case 'empty':
                                basic_pattern.append(f'{MarkupRe.N_CHILDREN}="0"')
                            case 'first-child':
                                basic_pattern.append(f'{MarkupRe.NCHILD}="1"')
                            case 'last-child':
                                basic_pattern.append(f'{MarkupRe.LCHILD}="1"')
                            case 'only-child':
                                basic_pattern.append(f'{MarkupRe.NCHILD}="1" {MarkupRe.LCHILD}="1"')
                            case 'first-of-type':
                                basic_pattern.append(f'{MarkupRe.NTAG}="1"')
                            case 'last-of-type':
                                basic_pattern.append(f'{MarkupRe.LTAG}="1"')
                            case 'only-of-type':
                                basic_pattern.append(f'{MarkupRe.NTAG}="1" {MarkupRe.LTAG}="1"')
                    elif selector.startswith('nth-'):
                        npos = selector.find('(')
                        assert npos > -1
                        ec, selector = selector[npos + 1:-1], selector[:npos]
                        ec = ec.replace('even', '2n').replace('odd', '2n+1')
                        match selector:
                            case 'nth-child':
                                basic_pattern.append(f'{MarkupRe.NCHILD}="{ec}"')
                            case 'nth-last-child':
                                basic_pattern.append(f'{MarkupRe.LCHILD}="{ec}"')
                            case 'nth-of-type':
                                basic_pattern.append(f'{MarkupRe.NTAG}="{ec}"')
                            case 'nth-last-of-type':
                                basic_pattern.append(f'{MarkupRe.LTAG}="{ec}"')
                else:  # case == '::'
                    self._specificity[ONES] += 1
            else:  # case == '[': [exp]   pseudo attributes
                self._specificity[TENS] += 1
                selector = selector[:-1]
                selectors = selector.split(' ')
                for selector in selectors:
                    splt_sel = ATTRIBUTES.split(selector)
                    case = len(splt_sel)
                    if case == 1:  # Case [target]:
                        attr = splt_sel[0]
                        basic_pattern.append(f'{attr}')
                    else:  # case >= 3
                        bflag = not case % 2 or case > 5  # case 2, 4 y case > 5: [a=], [a=b=] y [a=b=c=...]
                        if not bflag:  # case in (3, 5)    [a=b], [a=b=c]
                            (attr, case, value), suffix = splt_sel[:3], ''.join(splt_sel[3:])
                            bflag = suffix and suffix[0] != '='
                        if bflag:
                            raise UiCssError(f"SelectorStrError: {selector} is not allowed as attribute selector")
                        if case == '=':
                            delta = f'{attr}="{value}"'
                        else:
                            value = value.strip('\'"')
                            if case == '&=':  # Antiguo '~='
                                delta = f'{attr}=".*?\\b{value}\\b.*?"'
                            elif case == '|=':
                                delta = f'{attr}="{value}-*.*?"'
                            elif case == '^=':
                                delta = f'{attr}="{value}.*?"'
                            elif case == '$=':
                                delta = f'{attr}=".*?{value}"'
                            elif case == '*=':
                                delta = f'{attr}=".*?{value}.*?"'
                            delta += suffix
                        basic_pattern.append(delta)
        basic_pattern = ' '.join(basic_pattern)
        return basic_pattern

    def _get_compiled_selector_pattern(self):
        '''
        Entrega el regex pattern necesario para encontrar los widgets a los cuales aplicar el estilo.
        Formas de selectores válidos (<tag class="clase" id="id">):
        'tag',                          # widget class = tag
        'tag1,tag2,..tagn               # widget class = tag
        'tag.clase',                    # widget class = tag y css class = clase
        '.clase',                       # widget con css class = clase
        '.clase1,.clase2,...clasen',    # widget con css class = clase
        '#id',                          # widget con id = id
        '#id1,#id2,..#idn',             # widget con id = id
        'tag1 tag2',                    # widget class = tag2 en algún nivel por debajo de widget class = tag1
        'tag1 tag2 tag3 tag4',          # igual al anterior pero con varios tipos de widget class
        'tag .clase',                   # widget con css class = clase en algún nivel por debajo de widget class = tag
        '.clase tag',                   # widget class = tag en algún nivel por debajo de widget css class = clase
        '#id tag',                      # widget class = tag en algún nivel por debajo de widget con id = id
        '#id tag.clase'                 # widget class = tag y css class = clase por debajo de widget con id = id
        :param selector_str: str. CSS selector.
        :return: str. Pattern correspondiene al selector
        '''

        selector_str = self._selector_str
        selector_str = selector_str.replace('~=', '&=')  # Se hace para evitar conflicto entre combinator y
        # y attributes.
        if selector_str == '*':
            cp = MarkupRe.compile('(?#<__TAG__>)')
            self._freeze_specificity()
            return cp
        selector_str = selector_str.strip('\n\t ')
        splt_sel = SPLIT_PATTERN.split(selector_str)[1:-1]
        try:
            assert selector_str == ''.join(splt_sel), 'Bad split selector string'
        except AssertionError:
            raise UiCssError(f"SelectorStrError: Can't split selector str: {selector_str} != {''.join(splt_sel)}")
        split_selectors = [
            x.strip('\n\t ') for x in splt_sel
        ]
        try:
            assert len(split_selectors) % 2 == 1, 'Siempre número impar cuando se tienen combinators '
        except AssertionError:
            raise UiCssError(f"SelectorStrError: {selector_str}")
        linf, lsup = 0, len(split_selectors)
        selectors, combinators = split_selectors[linf:lsup:2], split_selectors[linf + 1:lsup:2]

        basic_patterns = [f'(?#<{self._get_basic_pattern(x)}>)' for x in selectors]
        cp_selectors = [MarkupRe.compile(basic_pattern) for basic_pattern in basic_patterns]

        CPatterns = MarkupRe.CPatterns
        combinators_map = {
            '': CPatterns.ZIN, '+': CPatterns.NXTTAG, '>': CPatterns.CHILDREN, '~': CPatterns.PRECEDES
        }
        cpatterns = [combinators_map[x] for x in combinators]
        self._freeze_specificity()

        # while cpatterns:
        #     cpattern = cpatterns.pop(0)
        #     span_regex = cp_selectors.pop(0)
        #     srch_regex = cp_selectors.pop(0)
        #     sel_pattern = MarkupRe.CompoundRegexObject(span_regex, srch_regex, cpattern)
        #     cp_selectors.insert(0, sel_pattern)
        while cpatterns:
            cpattern = cpatterns.pop(-1)
            srch_regex = cp_selectors.pop(-1)
            span_regex = cp_selectors.pop(-1)
            sel_pattern = MarkupRe.CompoundRegexObject(span_regex, srch_regex, cpattern)
            cp_selectors.append(sel_pattern)
        cp_pattern = cp_selectors.pop()
        return cp_pattern

    def _freeze_specificity(self):
        '''
        Congela la specificity de un pattern dado una vez se han procesado
        sus componentes básicos.
        :return: None.
        '''
        self._specificity = tuple(self._specificity)

    def __eq__(self, other):
        '''
        Dos selectores son iguales si tienen igual pattern.
        :param other: Selector instance.
        :return: bool.
        '''
        return self._specificity == other.specificity

    def __lt__(self, other):
        '''
        :param other: Selector instance.
        :return: bool.
        '''
        return self._specificity < other.specificity

    def __gt__(self, other):
        return not (self.__eq__(other) or self.__lt__(other))

    def __ge__(self, other):
        return not self.__lt__(other)

    def __le__(self, other):
        return not self.__gt__()

    def __getattr__(self, item):
        if self.compiled_selector and hasattr(self.compiled_selector, item):
            return getattr(self.compiled_selector, item)


class ElementFactory:

    def __init__(self):
        self.style_strings = None
        self.patterns = []
        self.srch_mapping = collections.defaultdict(list)
        self.end_tag_patterns = collections.defaultdict(list)
        self.css_selectors = None
        self.attrs_equiv = {}

    def add_to_patterns(self, cp_patterns, level):
        for sel_ndx, cp, sel_str in cp_patterns:
            if isinstance(cp, MarkupRe.CompoundRegexObject):
                srch_regex, pattern = cp.spanRegexObj, cp.srchRegexObj
                key, sel_str = sel_str.split(',', 1)
            else:
                srch_regex, pattern = cp, None
                key, sel_str = sel_str, ''
            key = key.split('[', 1)[0]
            comb, key = key[0], key[1:]
            if any(map(lambda x: x in key, ('.', '#', ':'))):
                key = srch_regex.tag_pattern
                if key == MarkupRe.TAG_PATTERN_DEFAULT:
                    req_attrs = srch_regex.req_attrs['tagpholder']
                    key = '*' if not req_attrs.get('__TAG__', '') else req_attrs['__TAG__'].pattern.rstrip(r'\Z')
            if comb in (' ', '>'):
                npos = len(self.patterns)
                srch_bin = self.srch_mapping[key]
                srch_bin.append((npos, srch_regex, comb))
                self.patterns.append((level, (sel_ndx, pattern, sel_str, key, len(srch_bin) - 1)))
            else:
                self.end_tag_patterns[level - 1].append((sel_ndx, pattern, sel_str, key, srch_regex, comb))

    def check_elem(self, in_level, tag, attrs_in:dict):
        attrs = attrs_in.copy()
        [attrs.__setitem__(ckey, attrs.pop(key)) for key, ckey in self.attrs_equiv.items() if key in attrs]

        to_check = ['*', tag]
        if 'id' in attrs:
            to_check.append(f'#{attrs["id"]}')
        if 'class' in attrs:
            # attrs['class'] = 'clase1 clase2 clase3'
            # to_check = [
            #       '.clase1',
            #       '.clase2',
            #       '.clase3',
            #       '.clase1.clase2',
            #       '.clase1.clase3',
            #       '.clase2.clase3',
            #       '.clase1.clase2.clase3'
            # ]
            clases = attrs['class'].split(' ')
            clases = itertools.chain(
                *(
                    [f'.{".".join(x)}' for x in itertools.combinations(clases, y + 1)]
                    for y in range(len(clases))
                )
            )
            to_check.extend(clases)
        # Se filtra to_check a solo los elementos presentes en srch_mapping.keys()
        to_check &= self.srch_mapping.keys()
        checked = []
        haveAllReqAttr = MarkupRe.MarkupParser._haveTagAllAttrReq
        for key in to_check:
            srch_bin = self.srch_mapping[key]
            for npos, srch_regex, comb in srch_bin:
                req_attrs = srch_regex.req_attrs.get('tagpholder', {}).copy()
                match comb:
                    case '>':  # div > p, Selects all <p> elements where the parent is a <div> element.
                        level = self.patterns[npos][0]
                        bflag = in_level == level + 1
                        # assert req_attrs.pop('__TAG__').match(key)
                    case '+':  # div + p, Selects the first <p> element that is placed immediately after <div> elements
                        level = self.patterns[npos][0]
                        bflag = in_level == level
                        assert req_attrs.pop('__TAG__').match(key)
                    case '~':  # p ~ ul, Selects every <ul> element that is preceded by a <p> element
                        level = self.patterns[npos][0]
                        bflag = in_level == level + 1
                        assert req_attrs.pop('__TAG__').match(key)
                    case _:  # div p, Selects all <p> elements inside <div> elements
                        bflag = True
                bflag = bflag and haveAllReqAttr(attrs, req_attrs)
                if bflag:
                    checked.append(npos)
        match_sel = []
        to_add = []
        for npos in checked:
            _, (sel_ndx, pattern, sel_str, _, _) = self.patterns[npos]
            if pattern is None:
                match_sel.append(sel_ndx)
            else:
                to_add.append((sel_ndx, pattern, sel_str))
        if in_level and to_add:
            self.add_to_patterns(to_add, in_level)
        return [self.selectors[sel_ndx] for sel_ndx in match_sel]

    def clear_levels(self, levels):
        while levels:
            level = levels.pop()
            while self.patterns[-1][0] == level:
                _, (_, _, _, key, npos) = self.patterns.pop()
                self.srch_mapping[key].pop(npos)
                if not self.srch_mapping[key]:
                    self.srch_mapping.pop(key)
        lst_level = level - 1
        # Se debe asegurar que los elementos en self.patterns sean únicos. Esto se asegura
        # vigilando que (level, sel_str, key)
        lst_filter = [(x, y[2], y[3]) for x, y in self.patterns if x > -1]
        for level in (lst_level, lst_level + 1):
            bin_pattern = self.end_tag_patterns.pop(level, [])
            for sel_ndx, pattern, sel_str, key, srch_regex, comb in bin_pattern:
                if level == lst_level and comb == '+':
                    self.end_tag_patterns[level + 1].append((sel_ndx, pattern, sel_str, key, srch_regex, comb))
                    continue
                if (level, sel_str, key) in lst_filter:
                    continue
                npos = len(self.patterns)
                srch_bin = self.srch_mapping[key]
                srch_bin.append((npos, srch_regex, comb))
                self.patterns.append((level, (sel_ndx, pattern, sel_str, key, len(srch_bin) - 1)))

    def getElements(self, htmlstr, tcase='.xml'):
        if tcase == '.xml':
            serializer = XmlSerializer()
            self.attrs_equiv = dict(name='id')
        elif tcase == '.html':
            serializer = HtmlSerializer()
        else:
            raise UiCssError('tcase not valid')
        it = serializer(htmlstr)
        self.selectors = serializer.selectors
        if self.selectors:
            cp_patterns = []
            for k, sel in enumerate(self.selectors):
                split = [x.strip('\n\t ') for x in SPLIT_PATTERN.split(sel.selector_str)[1:-1]]
                tags, comb = split[::2], [' '] + split[1::2]
                selector_str = ','.join([f'{x.strip() if x.strip() else " "}{y}' for x, y in zip(comb, tags)])
                cp_patterns.append((k, sel.compiled_selector, selector_str))

            self.add_to_patterns(cp_patterns, -1)

        tag_stack = []
        element_stack = [ET.Element('root')]
        # MElement = type('MElement', (ET.Element,), dict(tpos=None, sels=None))
        for item, *params, tpos in it:
            match item:
                case 'starttag':
                    tag, attrs = params
                    tag_stack.append(tag)
                    level = len(tag_stack)
                    match_sels = self.check_elem(level, tag, attrs) if self.selectors else None
                    text, tail, *_ = [
                        attrs.pop(x, None) for x in (
                            '_text', '_tail', MarkupRe.N_CHILDREN, MarkupRe.NCHILD, MarkupRe.LCHILD, MarkupRe.NTAG,  MarkupRe.LTAG,
                        )
                    ]

                    elem = MElement(tag, attrs)
                    elem.text = text
                    elem.tail = tail
                    elem.sels = match_sels
                    elem.tpos = tpos
                    elem.src = htmlstr.src
                    element_stack[-1].append(elem)
                    element_stack.append(elem)
                case 'endtag':
                    tag = params[0]
                    levels = []
                    while tag_stack[-1] != tag:
                        level = len(tag_stack)
                        tag_stack.pop()
                        levels.append(level)
                    if self.selectors:
                        level = len(tag_stack)
                        levels.append(level)
                        self.clear_levels(levels)
                    tag_stack.pop()
                    element_stack.pop()
                case _:
                    pass
        root = element_stack[-1][0]
        return root


def main():
    test = 'in_study'
    if test == 'in_study':
        import userinterface
        file_path = '/mnt/c/Users/Alex Montes/PycharmProjects/mywidgets/src/Tools/mypycharm/res/layout/pycharm_css.xml'
        xmlObj = userinterface.getLayout(file_path, withCss=True)
        eroot = ET.ElementTree(xmlObj)
        ET.indent(eroot, space="\t", level=0)
        ET.dump(eroot)

    if test == 'htmlserializer':
        html_filename = '/mnt/c/Users/Alex Montes/PycharmProjects/mywidgets/tests/css_files/generic.html'
        with open(html_filename, 'r') as f:
            html_string = f.read()
        serializer = HtmlSerializer()
        answ = serializer(html_string)
        for item in answ:
            print(item)
    elif test == 'Selector_class':
        # Selectores válidos
        selectors = {}
        selectors['validos'] = [
            # 'tag1 tag2 tag3 tag4',
            # 'tag1,tag2',           # Esto solo es válido para
            'tag.clase',
            'tag',
            '.clase',
            '#id',
            'tag1 tag2',
            'tag .clase',
            '.clase tag',
            '#id tag',
            '#id tag.clase'
        ]
        selectors['redundantes'] = ['tag#id', '.clase#id', '#id.clase']
        for key, selectores in selectors.items():
            print(f'***** Selectores {key} *********')
            for sel_str in selectores:
                selector = Selector(sel_str)
                print(f'{sel_str}, {selector.pattern}')
    elif test == 'ElementFactory':
        case = 3
        cssfilename = [
            '/mnt/c/Users/Alex Montes/PycharmProjects/mywidgets/tests/css_files/simple_selectors.css',
            '/mnt/c/Users/Alex Montes/PycharmProjects/mywidgets/tests/css_files/compound_selectors.css',
        ]

        htmlfilename = [
            '/mnt/c/Users/Alex Montes/PycharmProjects/mywidgets/tests/css_files/simple_selectors.html',
            '/mnt/c/Users/Alex Montes/PycharmProjects/mywidgets/tests/css_files/compound_selectors.html',
            '/mnt/c/Users/Alex Montes/PycharmProjects/mywidgets/tests/css_files/generic.html',
            '/mnt/c/Users/Alex Montes/PycharmProjects/mywidgets/src/Tools/mypycharm/res/layout/pycharm_css.xml',
        ]
        with open(htmlfilename[case], 'r') as f:
            html_string = f.read()

        wfactory = ElementFactory()

        root = wfactory.getElements(html_string, tcase='.xml')
        answ = collections.defaultdict(list)
        elem_stack = [root]
        while elem_stack:
            elem = elem_stack.pop()
            elem_stack.extend(list(elem))
            if elem.sels:
                for match_sel in elem.sels:
                    key = match_sel.selector_str
                    answ[key].append((elem.tpos, elem.tag, elem.attrib, elem.text))

        for key in sorted(answ):
            print(f'**** Selector: {key} ****')
            for tpos, tag, attrs, text in answ[key]:
                msg = " ".join('%s="%s"' % (key, val) for key, val in attrs.items())
                if text:
                    msg += f' {text=}'
                msg = f'{"lin: %s, col: %s" % tpos} => <{tag} {msg.strip()}>'
                print('    ' + msg)


if __name__ == '__main__':
    main()
