
#TODO Crear clase Selector:
# Esta clase deberá al menos tener los siguientes métodos: parse, especificidad,
# comparadores como __lt__, __gt__, ... hechoss con base en especificidad.
#TODO: Crear Test para clase selector con ccs.py y un archivo que contenga los casos de
# ejemplo en w3school



import re
import itertools

import Tools.uiStyle.CustomRegEx as CustomRegEx

THOUSANDS = 0
HUNDRES = 1
TENS = 2
ONES = 3

PATTERN = re.compile('(?:\:*[:\.#]*?[A-Za-z\d\-\_]+)|(?:\[.+?\])')
COMBINATORS = re.compile('(?:\W*?([\+\>\ \~\,]+)\W*?)')
ATTRIBUTES = re.compile('([\&\|\^\$\*]*=)')


def getWidgetMap(htmlstr, k=-1):
    cmpobj = CustomRegEx.compile('(?#<__TAG__ __TAG__=tag name=_name_ id=_id_ >)')

    from_pos = 0
    to_pos = len(htmlstr)
    answ = []
    it = cmpobj.finditer(htmlstr, from_pos, to_pos)
    stack = [(m.span(), m.groups()) for m in it]

    while stack:
        (pini, pfin), (tag, name, id) = stack.pop(0)

        k += 1
        if id:
            id = id.rsplit('/')[-1]
        name = name or id or str(k)
        answ.append(((pini, pfin), (tag, name)))

        #
        # En este punto se puede mandar a calcular el style a aplicar
        #

        from_pos = htmlstr[pini:pfin].find('>') + pini + 1
        to_pos = htmlstr[pini:pfin].rfind('<') + pini

        bflag = from_pos != -1 and to_pos != -1 and from_pos < to_pos
        if bflag:
            it = cmpobj.finditer(htmlstr, from_pos, to_pos)
            stack = [(m.span(), m.groups()) for m in it] + stack
    wdg_map = {key: value[1] for key, value in answ}
    return wdg_map


class Selector:
    seq_gen = itertools.count()

    def __init__(self, selector_str, style_str=None, cascade_priority=None):
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
        self._style_str = style_str
        self._selector_str = selector_str
        self._compiled_selector = None
        try:
            assert  not selector_str.count(','), f'SelectorStrError: Aggregated patterns (,) not posible'
            pattern = self._set_selector_pattern()
            cp = CustomRegEx.compile(pattern)
            assert isinstance(cp, CustomRegEx.ExtRegexObject) or cp.regex_pattern_str == '<', f'SelectorStrError: Not a valid CustomRegEx object: {cp.regex_pattern_str}'
            self._compiled_selector = cp
        except AssertionError as e:
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
        return self._style_str

    @property
    def selector_str(self):
        '''
        :return: str. CSS selector
        '''
        return self._selector_str

    @property
    def pattern(self):
        '''
        :return: str. CustomRegEx pattern equivalente al CSS selector.
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

    def _get_basic_pattern(self, basic_selectors):
        '''
        Entrega el pattern correspondiente a un selector básico para el CustomRegEx
        Se entiende como básicos: *, p, .clase, #id, [attr]
        :param basic_selectors: str. Descripción de un selector básico
        :return: str. CustomRegEx pattern.
        '''
        bflag = basic_selectors[0] in '.#[:'
        if not bflag:
            self._specificity[ONES] += 1
        items = PATTERN.findall(basic_selectors)
        basic_pattern = [f'{items.pop(0) if not bflag else "__TAG__"}']
        while items:
            selector = items.pop(0)
            case, selector = selector[0], selector[1:]
            if case == '.':         # case == '.': #clase
                self._specificity[TENS] += 1
                basic_pattern.append(f'class=".*?\\b{selector}\\b.*?"')
            elif case == '#':       # case == '#': #id
                self._specificity[HUNDRES] += 1
                basic_pattern.append(f'id="{selector}"')
            elif case == ':':
                if selector[0] != ':':      # case == ':'
                    self._specificity[TENS] += 1
                else:                       # case == '::'
                    self._specificity[ONES] += 1
            else:                    # case == '[': [exp]
                self._specificity[TENS] += 1
                selector = selector[:-1]
                splt_sel = COMBINATORS.split(selector)
                case = len(splt_sel)
                if case == 1:      # Case [target]:
                    attr = splt_sel[0]
                    basic_pattern.append(f'{attr}')
                elif case == 3:
                    attr, case, value = splt_sel
                    value = value.strip('\'"')
                    if case == '=':
                        basic_pattern.append(f'{attr}="{value}"')
                    elif case == '&=':          # Antiguo '~='
                        basic_pattern.append(f'{attr}=".*?\\b{value}\\b.*?"')
                    elif case == '|=':
                        basic_pattern.append(f'{attr}="{value}-*.*?"')
                    elif case == '^=':
                        basic_pattern.append(f'{attr}="{value}.*?"')
                    elif case == '$=':
                        basic_pattern.append(f'{attr}=".*?{value}"')
                    elif case == '*=':
                        basic_pattern.append(f'{attr}=".+?{value}.+?"')
        basic_pattern = ' '.join(basic_pattern)
        return basic_pattern

    def _set_selector_pattern(self):
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
        selector_str = selector_str.replace('~=', '&=')     # Se hace para evitar conflicto entre combinator y
                                                            # y attributes.
        if selector_str == '*':
            return f'(?#<__TAG__>)'
        selector_str = selector_str.strip('\n\t ')
        splt_sel = COMBINATORS.split(selector_str)
        try:
            assert selector_str == ''.join(splt_sel), 'Bad split selector string'
        except AssertionError:
            raise AssertionError(f"SelectorStrError: Can't split selector str: {selector_str} != {''.join(splt_sel)}")
        split_selectors = [
            x.strip('\n\t ') for x in splt_sel
        ]
        assert len(split_selectors) % 2 == 1, 'Siempre núnero impar cuando se tienen combinators '
        linf, lsup = 0, len(split_selectors)
        selectors, combinators = split_selectors[linf:lsup:2], split_selectors[linf + 1:lsup:2]

        selectors = [self._get_basic_pattern(x) for x in selectors]
        self._freeze_specificity()

        while combinators:
            case = combinators.pop(0)
            sel_pattern = selectors.pop(0)
            inner_pattern = selectors.pop(0)
            if case == '':              # CustomRegx.ZIN
                sel_pattern = f'{sel_pattern} <{inner_pattern}>'
            elif case == '+':           # CustomRegx.NEXTTAG
                sel_pattern = f'{sel_pattern}><{inner_pattern}'
            elif case == '>':           # CustomRegx.CHILDREN
                sel_pattern = f'{sel_pattern} <{inner_pattern}>*'
            elif case == '~':           # CustomRegx.SIBLING
                sel_pattern = f'{sel_pattern}>*<{inner_pattern}'
            selectors.insert(0, sel_pattern)
        cp_pattern = f'(?#<{selectors.pop()}>)'
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


class CssWrapper:
    CP_PATTERN = re.compile('\n((?:[^\{\*]+?)|(?:\W*?\*))\ *?(\{.+?\})', re.DOTALL)

    def __init__(self, css_string, isfile=False):
        if isfile:
            with open(css_string, 'r') as f:
                css_string = f.read()

        self.selectors = None
        self.style_strings = None
        self.styles = None
        self.process_css_string(css_string)

    def process_css_string(self, css_string):
        css_tuples = self.CP_PATTERN.findall(css_string)
        selectors = []
        for select_str, style_str in css_tuples:
            selectors.extend([Selector(x, style_str) for x in select_str.split(',')])
        self.selectors = selectors
        self.styles = {}
        pass

    def findStyles(self, htmlstr, from_pos, to_pos):
        for indx, selector in enumerate(self.selectors):
            cp_patterns = selector.compiled_selector
            for cp_pattern in cp_patterns:
                #
                # Aqui se debe hacer match y ver como se encuentran los items en los compuestos.
                #
                # m = cp_pattern.match(htmlstr, from_pos, to_pos)
                spans = [
                    m.span()
                    for m in cp_pattern.finditer(htmlstr, from_pos, to_pos)
                    if m is not None
                ]
                for span in spans:
                    style_array = self.styles.setdefault(span, [])
                    if indx not in style_array:
                        style_array.append(indx)


    def findWidgets(self, htmlstr, wdg_map):
        self.styles = {}
        self.findStyles(htmlstr, 0, len(htmlstr))
        answ = [
            (key, wdg_map.get(key, None), style_array)
            for key, style_array in sorted(self.styles.items())
        ]
        return answ


def selectorPattern(selector_str):
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

    def getBasicPattern(base_selector):
        items = CustomRegEx.findall(pattern, base_selector)
        assert len(items) <= 2
        if len(items) == 2:
            # Se tiene en este punto un selector del tipo:
            # tag.clase, tag#id, .clase#id, #id.clase
            # De los cuales solo el primero (tag.clase) resulta relevante, los otros son redundantes
            # pues el #id se refiere a un solo elemento
            dmy = [sel for sel in items if sel[0] == '#']
            if dmy:
                items = dmy
        if len(items) == 1:
            selector = items[0]
            if CustomRegEx.match('[a-zA-z\d]+', selector):  # widget
                base_pattern = f'{selector}'
            elif selector[0] == '.':  # Clase
                base_pattern = f'__TAG__ class=".*?{selector[1:]}.*?"'
            elif selector[0] == '#':  # id
                base_pattern = f'__TAG__ id="{selector[1:]}"'
            else:
                raise AssertionError(f'Selector: {selector}, no conocido')
        elif len(items) == 2:
            sel1, sel2 = items
            assert sel1.isalpha() and sel2[0] == '.', f'Caso {sel1}{sel2} no encontrado todavia'
            base_pattern = f'{sel1} class="{sel2[1:]}"'
        return base_pattern

    if selector_str == '*':
        return [CustomRegEx.compile(f'(?#<__TAG__>)')]
    pattern = '[\.#]*?[a-zA-z\d,]+'
    selectors = selector_str.split(' ', 1)
    split_selectors = selectors[0].split(',')
    base_pattern = [getBasicPattern(x) for x in split_selectors]
    if len(selectors) == 2:
        if ',' in selectors[1]:
            raise Exception(f'Selector: {selector_str} no habilitado aún')
        inner_pattern = [getBasicPattern(x) for x in selectors[1].split(' ')]
        base_pattern = [f'{x} <{y}>' for x in base_pattern for y in inner_pattern]
    base_pattern = [CustomRegEx.compile(f'(?#<{x}>)') for x in base_pattern]
    return base_pattern


# def findWidgets(patterns, htmlstr, wdg_map):
#     answ = []
#     selected = []
#     for pattern in patterns:
#         cmpobj = CustomRegEx.compile(pattern)
#         selected.extend([m.span() for m in cmpobj.finditer(htmlstr)])
#         answ.extend([wdg_map.get(spn, None) for spn in selected])
#     zansw = sorted(set(zip(answ, selected)), key=lambda x: x[1])
#     answ, selected = list(zip(*zansw))
#     return answ, selected


if __name__ == '__main__':

    def test_prov(htmlstr, parser):
        wdg_map = getWidgetMap(htmlstr, k=-2)
        answ = parser.findWidgets(htmlstr, wdg_map)
        selected, widgets, styles = list(zip(*answ))
        for wdg_id, wdg_spn in zip(widgets, selected):
            pi, pf = wdg_spn
            print(wdg_id, htmlstr[pi:pf])

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



    filename = '/mnt/c/Users/Alex Montes/PycharmProjects/mywidgets/Tools/uiStyle/test.css'
    parser = CssWrapper(filename, isfile=True)
    for selector in parser.selectors:
        print(selector.selector_str, selector.specificity, selector.regex_pattern_str)

    htmlstr = '''
    <!DOCTYPE html>
    <html>
    <head>
    <style>
    p.center {
      text-align: center;
      color: red;
    }

    p.large {
      font-size: 300%;
    }
    </style>
    </head>
    <body>

    <h1 class="center">This heading will not be affected</h1>
    <div>
    <p class="center">This paragraph will be red and center-aligned.</p>
    <p class="center large">This paragraph will be red, center-aligned, and in a large font-size.</p> 
    </div>
    </body>
    </html>

    '''
    test_prov(htmlstr,parser)


    htmlstr = '''<head>
    <uno id="alex" />
    <dos />
    <tres>esto es el freeze</tres>
    </head>'''

    answ = getWidgetMap(htmlstr, k=-2)
    htmlstr = '''<!DOCTYPE html>
    <html>
    <head>
    <style>
    p {
      text-align: center;
      color: red;
    }
    </style>
    </head>
    <body>

    <p>Every paragraph will be affected by the style.</p>
    <p id="para1">Me too!</p>
    <p>And me!</p>

    </body>
    </html>'''

    wdg_map = getWidgetMap(htmlstr, k=-2)
    # id_pattern = '(?#<__TAG__ __TAG__=tag id="para1" >)'
    id_pattern = selectorPattern('#para1')

    htmlstr = '''
    <!DOCTYPE html>
    <html>
    <head>
    <style>
    .center {
      text-align: center;
      color: red;
    }
    </style>
    </head>
    <body>
    
    <h1 class="center">Red and center-aligned heading</h1>
    <p class="center">Red and center-aligned paragraph.</p> 
    
    </body>
    </html>'''

    pass

    wdg_map = getWidgetMap(htmlstr, k=-2)
    # class_pattern = '(?#<__TAG__ class="center" >)'
    class_pattern = selectorPattern('.center')

    htmlstr = '''
    <!DOCTYPE html>
    <html>
    <head>
    <style>
    p.center {
      text-align: center;
      color: red;
    }
    
    p.large {
      font-size: 300%;
    }
    </style>
    </head>
    <body>
    
    <h1 class="center">This heading will not be affected</h1>
    <div>
    <p class="center">This paragraph will be red and center-aligned.</p>
    <p class="center large">This paragraph will be red, center-aligned, and in a large font-size.</p> 
    </div>
    </body>
    </html>
    
    '''
    wdg_map = getWidgetMap(htmlstr, k=-2)
    # class_pattern = '(?#<__TAG__ class=".*?center.*?" >)'
    class_pattern = selectorPattern('.center')

    class_pattern = selectorPattern('body p h1')

    htmlstr = '''
    <!DOCTYPE html>
    <html>
    <head>
    <style>
    h1, h2, p {
      text-align: center;
      color: red;
    }
    </style>
    </head>
    <body>
    
    <h1>Hello World!</h1>
    <h2>Smaller heading!</h2>
    <p>This is a paragraph.</p>
    
    </body>
    </html>
    '''
    wdg_map = getWidgetMap(htmlstr, k=-2)
    # class_pattern = '(?#<p|h1|h2>)'
    class_pattern = selectorPattern('body,p,h1')
