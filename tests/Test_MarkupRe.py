# -*- coding: utf-8 -*-
'''
Created on 27/10/2015

@author: Alex Montes Barrios
'''
import random
import pytest
import re

from src.Tools.uiStyle import MarkupRe

TAGPHOLDER = MarkupRe.TAGPHOLDER


def ExtCompObjEquality(a, b):
    return (a.req_attrs, a.var_list) == (b.req_attrs, b.var_list)


@pytest.fixture
def htmlString():
    html_str = '''
    <beg num="1">
        <blk1 num="2" />
        <span num="3">
            <blk1 num="4">
                <span num="5"/>
                <blk1 num="5.5">
                </blk1>
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
    return html_str


class TestHTMLPointer:
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

    @pytest.mark.parametrize(
        "seek_flag, required",
        [
         (True, ['<span num="3">']),
         (False, ['<span num="3">', '<span num="5"/>', '<span num="5.6"/>']),
        ]
    )
    def test_seek_to_end(self, seek_flag, required):
        cp_pattern = re.compile(r'<span(?:\s.*?/*)*>')

        pointer = MarkupRe.HTMLPointer(
            self.html_str, next_pattern=cp_pattern, seek_to_end=seek_flag
        )
        answer = [self.html_str[b:e].split('\n', 1)[0] for b, e in pointer()]
        assert answer == required

    @pytest.mark.parametrize(
        "zones, required",
        [
         ('[!--|out]', ['<blk1 num="2" />', '<blk1 num="4">', '<blk1></blk1>', '<blk1 num="12" />']),
         ('[!--]^[out]', ['<blk1 num="7">']),
        ]
    )
    def test_special_zones(self, zones, required):
        cp_pattern = re.compile(r'<blk1(?:\s.*?/*)*>')
        pointer = MarkupRe.HTMLPointer(
            self.html_str, next_pattern=cp_pattern, special_zones=zones
        )
        answer = [self.html_str[b:e].split('\n', 1)[0] for b, e in pointer()]
        assert answer == required

    @pytest.mark.parametrize(
        "spans, required",
        [
         (
            [(285, 514)],           # span iterator = list(tuple)
            ['<blk1 num="7">']
         ),
         (
            lambda x: MarkupRe.HTMLPointer(
                x, next_pattern=re.compile(r'<out(?:\s.*?/*)*>')
            )(),                    # span iterator = tuple generator
            ['<blk1 num="7">']
         ),
        ]
    )
    def test_it_span(self, spans, required):
        cp_pattern = re.compile(r'<blk1(?:\s.*?/*)*>')
        it_span_gen = spans if isinstance(spans, list) else spans(self.html_str)
        pointer = MarkupRe.HTMLPointer(
            self.html_str, next_pattern=cp_pattern, it_span=it_span_gen
        )
        answer = [self.html_str[b:e].split('\n', 1)[0] for b, e in pointer()]
        required = ['<blk1 num="7">']
        assert answer == required, 'it_span: List error'

class TestExtcompile:

    def test_ExtCompile(self):
        """
        Html tag m�nimo
        """
        requested = {TAGPHOLDER: {}}
        assert MarkupRe.compile('(?#<table>)', 0).req_attrs == requested

    def test_namedvars(self):
        """
        <a href="http://uno.html">texto</a>
        Html tag con variables url y label a los que se asigna el valor del atributo href y
        el texto respectivamente
        """
        actual = MarkupRe.compile('(?#<a href=url *=label>)', 0)
        assert (actual.tag_pattern, actual.req_attrs, actual.var_list) == (
            'a', 
            {TAGPHOLDER: {'*': '', 'href': ''}}, 
            [[f'{TAGPHOLDER}.href', 'url'], [f'{TAGPHOLDER}.*', 'label']]
        )

    def test_namedvarswithpattern(self):
        """
        <a href="http://uno/dos/tres.html">texto</a>
        Html tag con variables url y label a los que se asigna el valor del atributo href y
        el texto respectivamente ya que href cumple con el patrón "http://uno/.+?/tres.html"
        """
        actual = MarkupRe.compile('(?#<a href="http://uno/.+?/tres.html" href=url *=label>)', 0)
        assert actual.var_list == [[f'{TAGPHOLDER}.href', 'url'], [f'{TAGPHOLDER}.*', 'label']]

    def test_implicitvars(self):
        """
        <a href="http://uno.html">texto</a>
        Html tag con variable implícita href y variable label que recoge el texto
        """
        actual = MarkupRe.compile('(?#<a (href) *=label>)', 0)
        assert (actual.tag_pattern, actual.req_attrs, actual.var_list) == (
        'a', {TAGPHOLDER: {'*': '', 'href': ''}}, [[f'{TAGPHOLDER}.href', 'group1'], [f'{TAGPHOLDER}.*', 'label']])

    def test_cleanvars(self):
        """
        <a href="http://uno.html">texto</a>
        Html tag con variable implícita href y variable label que recoge el texto una vez se
        eliminan los espacios en el prefijo y el sufijo. Es decir si a.* = \n\r \testo es lo que vale \t\n
        la notación &label& hace que en label se almacene "esto es lo que vale"
        """
        first = MarkupRe.compile('(?#<a (href) *=label>)', 0)
        scnd = MarkupRe.compile('(?#<a (href) *=&label&>)', 0)
        assert first.req_attrs[TAGPHOLDER]['*'] != scnd.req_attrs[TAGPHOLDER]['*']

    def test_equivNotation(self):
        """
        Notación equivalente utilizando asociatividad que se expresa con las {}
        """
        first = MarkupRe.compile('(?#<a href span{src=icon *=label} div.id>)', 0)
        scnd = MarkupRe.compile('(?#<a href span.src=icon span.*=label div.id>)', 0)
        assert ExtCompObjEquality(first, scnd)

    def test_equivNotationII(self):
        """
        Notación equivalente utilizando asociatividad cuando se tienen el mismo tag en
        varios niveles
        """
        first = MarkupRe.compile(
            '(?#<table id td.*=grp1 td[2].b.*=grp2 td[2].a.href=grp2a td[2].a.src=grp2b td[3].*=grp3 td[4].*=grp4>)', 0)
        scnd = MarkupRe.compile('(?#<table id td{1.*=grp1 2{b.*=grp2 a{href=grp2a src=grp2b}} 3.*=grp3 4.*=grp4}>)',
                                0)
        assert ExtCompObjEquality(first, scnd)

    def test_tripleAsignation(self):
        """
        Notación equivalente utilizando doble asignación para declarar la variable y el parametro que
        se quiere
        """
        first = MarkupRe.compile('(?#<ese a.*="http//.+?/prueba" a.*=icon href=url>)', 0)
        scnd = MarkupRe.compile('(?#<ese a.*="http//.+?/prueba"=icon href=url>)', 0)
        assert ExtCompObjEquality(first, scnd)

    def test_raiseAsignationError(self):
        with pytest.raises(MarkupRe.MarkupReError):
            MarkupRe.compile('(?#<TAG ese a{*=icon a.*="http//esto/es/prueba" href=url>)', 0)

    def test_regexpFlags(self):
        requested = {TAGPHOLDER: {}}
        assert MarkupRe.compile('(?iLm)(?#<table>)', 0).req_attrs == requested


class TestExtRegexParser:

    @staticmethod
    def get_attr_str(str_in, x, y):
        return str_in[x:y]

    def setup_parser(self, pattern):
        cp = MarkupRe.compile(pattern)
        vars = ('var_list', 'req_attrs', 'opt_attrs')
        var_list, req_attrs, opt_attrs = [getattr(cp, var) for var in vars]
        parser = MarkupRe.MarkupParser(var_list, req_attrs, opt_attrs)
        return parser

    @pytest.mark.parametrize(
        "span, required",
        [
            ((10, 100), (20, 110)),
            ((-1, -1), (-1, -1)),
            (tuple(), tuple()),
        ]
    )
    def test_abs_coord(self, span, required):
        abs_coord = MarkupRe.MarkupParser.abs_coord
        offset = 10
        assert abs_coord(span, offset) == required

    def test_get_attrs_pos(self):
        get_attrs_pos = MarkupRe.MarkupParser.get_attrs_pos
        items = [
            'href0',
            'href1="el tiempo com"',
            "href2='el tiempo com'",
            # """href3="el 'tiempo' com\"""",
            # """href4='el "tiempo" com'""",
            # """href5='el tiempo com\"""",
            # """href6="el tiempo com'""",
            # """href7=''el tiempo' com'""",
            # """href8='el tiempo 'com''""",
        ]
        for k in range(10):
            case, elem = f'caso{k}', f'<a {" ".join(random.sample(items, len(items)))}>'
            answ = dict(get_attrs_pos(elem))
            answ.pop('__TAG__')
            error = 'href0' not in answ
            for key, value in answ.items():
                if value:
                    beg, end = value
                    attr_val_raw = elem[beg:end]
                    attr_val = attr_val_raw.replace('"', '').replace('\'', '')
                    error = error or attr_val != 'el tiempo com'
                else:
                    error = error or key != 'href0'
            if error:
                print(f'{case}, valid={not error}')
                print(elem)
                for key, val in sorted(answ.items()):
                    answ = elem[val[0]:val[1]].replace('"', '').replace('\'', '') if val else None
                    if (key == 'href0' and answ != None) or (key != 'href0' and answ != 'el tiempo com'):
                        print(f'{key}={answ}\n')
            assert not error

    @pytest.mark.parametrize(
        "args, required",
        [
            (('   <begin>texto<end> ', 0, 21), (3, 20)),
            (('   <begin>texto<end> ', 4, 21), (15, 20)),
            (('   <begin>texto<end> ', 0, 17), (3, 10)),
        ]
    )
    def test_get_attrs_pos(self, args, required):
        adjust_end_points = MarkupRe.MarkupParser.adjust_end_points
        assert adjust_end_points(*args) == required

    def test_errors(self):
        with pytest.raises(MarkupRe.MarkupReError):
            adjust_end_points = MarkupRe.MarkupParser.adjust_end_points
            adjust_end_points('   <begin texto end ', 0, 21)

    def test_parse_standard(self, htmlString):
        parser = MarkupRe.MarkupParser()
        root = parser.parse(htmlString, 0, len(htmlString))
        assert isinstance(root, MarkupRe.TreeElement)
        param_pos = root.attr_span()
        assert root.tag == MarkupRe.TAGPHOLDER
        assert self.get_attr_str(htmlString, *param_pos['__TAG__']) == 'beg'
        attrs = {key: value for key, value in root.attrs.items() if key not in MarkupRe.PSEUDO_ATTRS}
        assert all(value == self.get_attr_str(htmlString, *param_pos[key]) for key, value in attrs.items())

        answ = parser.parse(htmlString, 0, len(htmlString), lambda elem: elem.tag == 'blk1')
        assert isinstance(answ, list)
        assert all(elem.tag == 'blk1' for elem in answ)

    def test_parse_orphan(self):
        htmlString = '''
        <beg>
            <uno />
            <dos />
            <tres>
            <cuatro />
        </beg>
        '''
        parser = MarkupRe.MarkupParser()
        root = parser.parse(htmlString, 0, len(htmlString))
        assert isinstance(root, MarkupRe.TreeElement)
        assert len(root.children) == 4
        nodo = root.children[2]
        assert nodo.tag == 'tres'
        assert len(nodo.children) == 0

    @pytest.mark.parametrize("pattern, _class, bflag",
        [
            ('(?#<blk1 id="uno">)', MarkupRe.TreeElement, True),  # Necesario y suficiente
            ('(?#<blk1 id="uno" *=label>)', bool, True),          # Necesario pero no suficiente
            ('(?#<blk1 id="uno" a.*=label>)', bool, True),        # Necesario pero no suficiente
            ('(?#<blk1 id="dos">)', bool, False),                 # No cumple
        ]
    )
    def test_check_tagpholder(self, pattern, _class, bflag):
        data = '''
        <blk1 id="uno" class="tres">
            <a href="http://www.foo.com">
                texto1 texto2
            </a>
        </blk1>
        '''
        beg, end = MarkupRe.MarkupParser.adjust_end_points(data, 0, len(data))

        parser = self.setup_parser(pattern)
        pholder = parser.check_tagpholder(data, beg, end)
        assert isinstance(pholder, _class)
        value = pholder if isinstance(pholder, bool) else pholder.tag == TAGPHOLDER
        assert value == bflag

    @pytest.mark.parametrize("pattern",
        [
            '(?#<blk1 id="uno" class=clase>)',  # tagpholder
            '(?#<blk1 id="uno" class=clase a.href=url>)',  # general
        ]
    )
    def test_check_match(self, pattern):
        data = '''
        <blk1 id="uno" class="tres">
            <a href="http://www.foo.com">
                texto1 texto2
            </a>
        </blk1>
        '''
        attr_val = {'clase': 'tres', 'url': 'http://www.foo.com'}
        parser = self.setup_parser(pattern)
        var_pos = parser.check_match(data, 0, len(data))
        assert var_pos
        assert all(
            attr_val[var] == self.get_attr_str(data, *var_pos[k + 1])
            for k, (_, var) in enumerate(parser.var_list)
        )


class TestExtMatch:
    htmlStr = """
<span id="1" class="independiente">span0</span>
<script id="2">
    <span class="bloque1">span1</span>
    <a href="http://www.eltiempo.com.co">El Tiempo</a>
    <span class="bloque1">span2</span>
</script>
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

    @pytest.mark.parametrize("pattern, required, msg",
        [
            (
                '(?#<hijo exp .*>)',
                [('El primer comentario', 'El segundo comentario', 'El tercer comentario')],
                'Todos los comentarios'
            ),
            (
                '(?#<hijo id="hijo1" *=label>)',
                ['primer hijo'],
                'Comentario y variable independiente'
            ),
            (
                '(?#<hijo id=varid *=label>)',
                [('hijo1', 'primer hijo'), ('hijo2', ''), ('hijo3', 'tercer hijo')],
                'Utilizando variables para distinguir casos'
            ),
            (
                '(?#<hijo id="hijo[13]"=varid *=label>)',
                [('hijo1', 'primer hijo'), ('hijo3', 'tercer hijo')],
                'Utilizando variables para distinguir casos'
            ),
            (
                '(?#<hijo exp *=label>)',
                [''],
                'Utilizando atributos requeridos (exp) para distinguir un caso'),
        ]
    )
    def test_general(self, pattern, required, msg):
        answer = MarkupRe.findall(pattern, self.htmlStr)
        assert answer == required, f'{msg}'

    def test_multiple_attrs(self):
        htmlStr = """
        <span id="1" class="clase1">span1</span>
        <span id="1" class="clase2">span2</span>
        <span id="1" class="clase1 clase2">span3</span>
        <span id="1" class="clase2 clase1">span4</span>
        <span id="1" class="clase2 clase3">span5</span>
        """
        pattern = '(?#<span class=".*?\\bclase1\\b.*?" class=".*?\\bclase2\\b.*?" *=label>)'
        required = ['span3', 'span4']
        answer = MarkupRe.findall(pattern, htmlStr)
        assert answer == required

        # El valor almacenado para la variable 'clase' siempre corresponde al del
        # pattern definido por la variable
        pattern = '(?#<span class="(.*?)\\bclase1\\b.*?"=clase class=".*?\\bclase2\\b.*?" *=label>)'
        required = [('', 'span3'), ('clase2 ', 'span4')]
        answer = MarkupRe.findall(pattern, htmlStr)
        assert answer == required

        pattern = '(?#<span class="(.*?)\\bclase1\\b.*?" class=".*?\\bclase2\\b(.*?)"=clase *=label>)'
        required = [('', 'span3'), (' clase1', 'span4')]
        answer = MarkupRe.findall(pattern, htmlStr)
        assert answer == required


    def test_errors(self):
        with pytest.raises(MarkupRe.MarkupReError):
            'Error porque no se pueden utilizar variables cuando se tiene ".*" como variable requerida'
            MarkupRe.compile('(?#<span class=var1 .*>)')

        with pytest.raises(MarkupRe.MarkupReError):
            'Entrega error porque se utiliza (__TAG__) como tagpattern y con __TAG__=mi_nametag_var se intenta asignarle a otra variable'
            MarkupRe.compile('(?#<(__TAG__) __TAG__=mi_nametag_var *=label>)')

    def test_tag(self):
        answer = MarkupRe.findall('(?#<span|a *=label>)', self.htmlStr)
        required1 = ['span0', 'bloque1', 'bloque2', 'span3']
        assert answer == required1, 'Obtener texto de tags span o a'

        cmpobj = MarkupRe.compile('(?#<(span|a) *=label>)')
        answer = list(cmpobj.groupindex.keys())
        required2 = ['__TAG__', 'label']
        assert answer == required2, 'Al encerrar el tagpattern entre paréntesis el nametag se almacena en la variable __TAG__ '

        answer = cmpobj.findall(self.htmlStr)
        required3 = [('span', 'span0'), ('span', 'bloque1'), ('span', 'bloque2'), ('span', 'span3')]
        assert answer == required3, 'El primer componente de los tuples que conforman answer corresponde al nametag'

        cmpobj = MarkupRe.compile('(?#<span|a __TAG__=mi_nametag_var *=label>)')
        answer = list(cmpobj.groupindex.keys())
        required4 = ['mi_nametag_var', 'label']
        assert answer == required4, 'Al utilizar el atributo __TAG__ se puede asignar una variable que contendra el nametag de los tags que cumplen con el pattern buscado'

        answer = cmpobj.findall(self.htmlStr)
        assert answer == required3, 'El resultado es el mismo, cambia solo el nombre de la variable asociada al nametag'

        cmpobj = MarkupRe.compile('(?#<__TAG__ *="[sb].+?"=label>)')
        answer = cmpobj.findall(self.htmlStr)
        assert answer == required1, r'Al utilizar __TAG__ como tag attribute se hace el tagpattern = r"[a-zA-Z][^\s>]*", para con el primer resultado se asigna "[sb].+?" al *'

        cmpobj = MarkupRe.compile('(?#<(__TAG__) *=".+?"=label>)')
        answer = list(cmpobj.groupindex.keys())
        assert answer == required2, 'Se puede utiliza (__TAG__) para guardar el nametag en la variable __TAG__'

        cmpobj = MarkupRe.compile('(?#<__TAG__ __TAG__=mi_nametag_var *=".+?"=label>)')
        answer = list(cmpobj.groupindex.keys())
        assert answer == required4, 'Se puede utiliza __TAG__=nombrevar para guardar el nametag en una variable con nmbre propio'

        cmpobj = MarkupRe.compile('(?#<__TAG__ __TAG__=mi_nametag_var id=id>)', etags_str='[<!--]')
        answer = cmpobj.findall(self.htmlStr)
        required = [('span', '1'), ('script', '2'), ('bloque', '3'), ('span', '4')]
        assert answer == required, 'Utilizando __TAG__ como tagpattern'

        cmpobj = MarkupRe.compile('(?#<__TAG__ __TAG__="span|a"=mi_nametag_var *=label>)')
        answer = cmpobj.findall(self.htmlStr)
        assert answer == required3, 'Utilizando __TAG__="span|a"=mi_nametag_var se redefine el tagpattern a "span|a" y se asigna a la variable mi_nametag_var'

    def test_nzone(self):
        allspan = [('independiente', 'span0'),
                   ('bloque1', 'span1'), ('bloque1', 'span2'),  # En script
                   ('independiente', 'bloque1'), ('independiente', 'bloque2'),  # En bloque
                   ('bloque2', 'span1'), ('bloque2', 'span2'),  # En <!--
                   ('independiente', 'span3')]

        answer1 = MarkupRe.findall('(?#<span class=test *=label>)', self.htmlStr)
        required = [lista for lista in allspan if lista[0] == 'independiente']
        assert answer1 == required, 'Por default se excluyen Los tags buscados en self.htmlStr contenidos en zonas <!--xxx--> y script'
        answer2 = MarkupRe.findall('(?#<span class=test *=label __EZONE__="[!--|script]">)', self.htmlStr)
        assert answer1 == answer2, 'El resultado por default se obtiene haciendo __NZONE__="[!--|script]" '

        answer = MarkupRe.findall('(?#<span class=test *=label __EZONE__="">)', self.htmlStr)
        assert answer == allspan, 'Para no tener zonas de exclusi.n se hace __EZONE__=""'

        answer = MarkupRe.findall('(?#<span class=test *=label __EZONE__="[bloque]">)', self.htmlStr)
        required = [lista for lista in allspan if not lista[1].startswith('bloque')]
        assert answer == required, 'Se personaliza la zona de exclusi.n asignando a __NZONE__="xxx|zzz" donde xxx y zzz son tags'

        answer = MarkupRe.findall('(?#<span class=test *=label __EZONE__="^[!--|script]">)', self.htmlStr)
        required = [lista for lista in allspan if lista[0].startswith('bloque')]
        assert answer == required, 'Para incluir solo tags buscados en las zonas xxx y zzz se debe hacer __NZONE__="^[xxx|zzz]'

        answer = MarkupRe.findall('(?#<a href=url *=labe>)', self.htmlStr)
        required = []
        assert answer == required

        answer = MarkupRe.findall('(?#<a href=url *=label __EZONE__="^[script]">)', self.htmlStr)
        required = [('http://www.eltiempo.com.co', 'El Tiempo')]
        assert answer == required

        answer = MarkupRe.findall('(?#<a href=url *=label __EZONE__="^[!--]">)', self.htmlStr)
        required = [('http://www.elheraldo.com.co', 'El Heraldo')]
        assert answer == required

    def test_regexpflags(self):
        answer = MarkupRe.findall('(?iLm)(?#<hijo id="hijo1" *=label>)', self.htmlStr)
        required = ['primer hijo']
        assert answer == required, 'Comentario y variable independiente'

        answer = MarkupRe.findall('(?#<SPAN>)(?#<PARAM>)(?#<hijo id="hijo1" *=label>)', self.htmlStr)
        required = ['primer hijo']
        assert answer == required, 'Comentario y variable independiente'

        answer = MarkupRe.findall('(?#<SPAN>)(?iLm)(?#<PARAM>)(?#<hijo id="hijo1" *=label>)', self.htmlStr)
        required = ['primer hijo']
        assert answer == required, 'Comentario y variable independiente'

        answer = MarkupRe.findall(
            '(?#<SPAN>)(?iLm)(?#<PARAM>)(?# Esto es un comentario)(?#<hijo id="hijo1" *=label>)', self.htmlStr)
        required = ['primer hijo']
        assert answer == required, 'Comentario y variable independiente'


class TestOptionalVars:
    htmlStr = """
<parent>
    texto head header
    <son id="1" href="son1 base"></son>
    <son id="2" href="son2 base" href1="son2 alterno"></son>
    <son id="3" href1="son3 alterno" href2="son3 alterno2">texto son3</son>
    <son id="4" href="son4 base">
        <grandson href="grandson base">texto grandson</grandson>
    </son>
    texto head footer
</parent>
"""

    def test_general(self):
        answer = MarkupRe.findall('(?#<son id=id href=_url_>)', self.htmlStr)
        required = [('1', 'son1 base'), ('2', 'son2 base'), ('3', None), ('4', 'son4 base')]
        assert answer == required, 'Variable opcional _url_ registra valor solo cuando existe atributo'

        for var in ['_url_', '_url', 'url_']:
            pattern = '(?#<son id=id href=%s *=label>)' % var
            m = MarkupRe.compile(pattern)
            required = {'id': 1, 'label': 3, 'url': 2}
            assert m.groupindex == required, 'Los guiones bajos(_) solo denotan que la variable es opcional'

        answer = MarkupRe.findall('(?#<son id=_id_ href=_url_>)', self.htmlStr)
        required = [('1', 'son1 base'), ('2', 'son2 base'), ('3', None), ('4', 'son4 base')]
        assert answer == required, 'Todas las variables pueden ser opcionales'

        answer = MarkupRe.findall(r'(?#<son id=id href1="son2[^"]+"=_url_>)', self.htmlStr)
        required = [('1', None), ('2', 'son2 alterno'), ('3', None), ('4', None)]
        assert answer == required, 'Se escoge el valor si cumple con una condicion'

        answer = MarkupRe.findall(r'(?#<son id=id href1="son2 ([^"]+)"=_url_>)', self.htmlStr)
        required = [('1', None), ('2', 'alterno'), ('3', None), ('4', None)]
        assert answer == required, 'Si cumple con una condicion y tiene al menos un grupo siempre se almacena el grupo 1'

        answer = MarkupRe.findall('(?#<son id=id href=url href1=_url_>)', self.htmlStr)
        required = [('1', 'son1 base'), ('2', 'son2 alterno'), ('4', 'son4 base')]
        assert answer == required, 'En url se almacena el valor de href solo cuando no existe href1'

        answer = MarkupRe.findall(
            '(?#<son id=id href=url href1=_url_ grandson{href=__url__ *=label}>)',
            self.htmlStr
        )
        required = [('4', 'grandson base', 'texto grandson')]
        assert answer == required, 'La variable opcional puede estar ubicada en cualquier posición'

        answer = MarkupRe.findall('(?#<son id="3" href1=_url_ href2=__url__>)', self.htmlStr)
        required = ['son3 alterno2']
        assert answer == required, 'El valor almacanado es el de la variable opcional mas a la izquierda'

    def test_errors(self):
        with pytest.raises(MarkupRe.MarkupReError):
            'Error porque se utiliza la misma variable opcional con dos atributos'
            MarkupRe.compile('(?#<son id="3" href1=_url_ href2=_url_>)')


class TestCompoundPatterns:
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

    def test_zin(self):
        answer = MarkupRe.findall('(?#<bloque <span *=label>>)', self.htmlStr)
        required = ['bloque1', 'bloque2']
        assert answer == required
        pass

    def test_nxttag(self):
        answer = MarkupRe.findall('(?#<hijo id="hijo1"><__TAG__=name exp=label h1[3].*=head>)', self.htmlStr)
        required = [('hijo', 'hijo con varios comentarios', 'El tercer comentario')]
        assert answer == required

        answer = MarkupRe.findall('(?#<hijo id="hijo1"><hijo exp=label>)', self.htmlStr)
        required = ['hijo con varios comentarios']
        assert answer == required

        answer = MarkupRe.findall('(?#<h1 *="El segundo comentario"><*=label>)', self.htmlStr)
        required = ['El tercer comentario']
        assert answer == required

    def test_children(self):
        answer = MarkupRe.findall('(?#<SPAN>)(?#<bloque <__TAG__=name>*>)', self.htmlStr)
        required = ['span', 'parent', 'span']
        assert answer == required

        answer = MarkupRe.findall('(?#<bloque <__TAG__=name *="bloque2" class=clase>*>)', self.htmlStr)
        required = [('span', 'independiente')]
        assert answer == required

    def test_parent(self):
        with pytest.raises(MarkupRe.MarkupReError):
            MarkupRe.findall('(?#<*<bloque >__TAG__=name>)', self.htmlStr)
        pass

    def test_siblings(self):
        with pytest.raises(MarkupRe.MarkupReError):
            MarkupRe.findall('(?#<bloque >=<__TAG__=name>)', self.htmlStr)
        pass


class TestNestedCPatterns:
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

    def test_compile(self):
        regex_str = r'(?#' + '<<bloque<hijo id="hijo2">><h1 *="El segundo comentario">*>' + r')'
        comp_obj1 = MarkupRe.compile(regex_str)
        assert type(comp_obj1) == MarkupRe.CompoundRegexObject, 'NestedCPatterns: Not a zinwrapper object'
        assert comp_obj1.pattern == regex_str

        assert type(comp_obj1.spanRegexObj) == MarkupRe.CompoundRegexObject
        assert comp_obj1.spanRegexObj.pattern == '(?#<bloque<hijo id="hijo2">>)'
        assert type(comp_obj1.spanRegexObj.spanRegexObj) == MarkupRe.ExtRegexObject
        assert comp_obj1.spanRegexObj.spanRegexObj.pattern == '(?#<bloque>)'
        assert comp_obj1.spanRegexObj.srchRegexObj.pattern == '(?#<hijo id="hijo2">)'

        assert type(comp_obj1.srchRegexObj) == MarkupRe.ExtRegexObject
        assert comp_obj1.srchRegexObj.pattern == '(?#<__TAG__ __TAG__="h1" *="El segundo comentario">)'

    def test_equivalent_compile(self):
        first_pat = '(?#<bloque<hijo id="hijo2">>)'
        regex1_str = '(?#<bloque>)'
        regex1 = MarkupRe.compile(regex1_str)
        regex2_str = '(?#<hijo id="hijo2">)'
        regex2 = MarkupRe.compile(regex2_str)
        compound1 = MarkupRe.CompoundRegexObject(regex1, regex2, MarkupRe.CPatterns.ZIN)
        assert compound1.pattern == first_pat
        assert compound1 == MarkupRe.compile(first_pat)

        scnd_pat = '(?#<<bloque<hijo id="hijo2">><h1 *="El segundo comentario">*>)'
        regex3_str = '(?#<h1 *="El segundo comentario">)'
        regex3 = MarkupRe.compile(regex3_str)
        compound2 = MarkupRe.CompoundRegexObject(compound1, regex3, MarkupRe.CPatterns.CHILDREN)
        assert compound2.pattern == scnd_pat
        assert compound2 == MarkupRe.compile(scnd_pat)

    def test_finditer(self):
        regex_strs = [
            '<<bloque<hijo id="hijo2">><h1 *="El segundo comentario">*>',
            '<<parent<hijo id="hijo2">*><h1 *="El segundo comentario">*>',
            '<<bloque<parent id="root">><h1 *="El segundo comentario">>',
        ]
        for regex_str in regex_strs:
            comp_obj1 = MarkupRe.compile(r'(?#' + regex_str + r')')
            answer = [
                self.htmlStr[a:b] for a, b in
                [m.span() for m in comp_obj1.finditer(self.htmlStr)]
            ]
            required = ['<h1>El segundo comentario</h1>']
            assert answer == required

    def test_parameters(self):
        case = '<<parent id=idp<hijo id="hijo2"=idh>*><h1 *="El segundo comentario">*>'
        regex_str = f'(?#{case})'
        comp_obj1 = MarkupRe.compile(regex_str)
        match = comp_obj1.search(self.htmlStr)
        answer = match.parameters._asdict()
        required = dict(idp='root', idh='hijo2')
        assert answer == required