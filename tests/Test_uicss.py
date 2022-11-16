import functools
import itertools
import random
import pytest

import src.Tools.uiStyle.uicss as uicss

P = 'div > p'


@pytest.fixture(scope="module")
def simple_selectors_html():
    filename = './css_files/simple_selectors.html'
    with open(filename, 'r') as f:
        html_str = f.read()
    return html_str


@pytest.fixture(scope="module")
def compound_selectors_html():
    filename = './css_files/compound_selectors.html'
    with open(filename, 'r') as f:
        html_str = f.read()
    return html_str


class TestSelector:

    @pytest.mark.parametrize(
        "type_test",
        [
            'specific',
            'general',
        ]
    )
    def test_generic__melement(self, type_test):
        def getMElement(test_case):
            if test_case == 'specific':
                css_str = '''
                .command {
                    font:Helvetica 8;
                    image:@drawable/btn_question;
                    compound:top;
                    relief:flat;
                    wraplength:64;
                }
                '''
                sels = sorted(uicss.XmlSerializer.process_css_string(css_str))
                attrs = dict(text="Filter", image="@drawable/btn_filter", side="left", command="Zip/Filters")
            elif test_case == 'general':
                nsels = random.randint(3, 6)
                sel_strs = random.sample([f'sel{k}' for k in range(nsels)], nsels)
                values = [random.sample(range(10), random.randint(1, 5)) for x in range(nsels)]
                style_strs = [
                    f'{{{";".join([f"key{k}:{k}" for k in values[x]])};}}'
                    for x in range(nsels)
                ]

                sels = [uicss.Selector(sel_str, style_str) for sel_str, style_str in zip(sel_strs, style_strs)]
                attrs = {f'key{k}': 10*k for k in random.sample(range(10), random.randint(1, 5))}
            return attrs, sels

        attrs, sels = getMElement(type_test)
        melem = uicss.MElement('tag', attrs, sels=sels)

        kattrs = attrs.keys()
        kraw_attrib = melem.raw_attrib.keys()
        kattrib = melem.attrib.keys()
        kstyle_str = functools.reduce(lambda t, x: t | x.keys(), [sel.style_str for sel in sels], set())

        assert kattrs == kraw_attrib, 'Original attributes not preserved'
        assert (kattrs | kstyle_str) == kattrib, 'Keys in final attributes not well generated'

        keys_from_sels = kattrib - kattrs
        keys_common = kattrs & kstyle_str

        assert all(attrs[key] == melem.attrib[key] for key in keys_common), 'Original attributes are not mandatory'
        attrs_pos = [
            dict.fromkeys(x.keys() & keys_from_sels, k) for k, x in enumerate(sel.style_str for sel in sels)
        ]
        attrs_pos = dict(itertools.chain(*(x.items() for x in attrs_pos)))
        assert all(sels[k].style_str[key] == melem.attrib[key] for key, k in attrs_pos.items()), \
        'The selector with greater specificity is not defying the final attribute'

    @pytest.mark.parametrize(
        "sel_str, count_str",
        [
            ('.intro', 'class="intro"'),
            ('#firstname', 'id="firstname"'),
            ('p', '<p'),
            ('p.intro', '<p class="intro">'),
            ('a[target]', 'target='),
            ('a[target=_blank]', '_blank'),
            ('img[title~=flower]', 'flower"'),
            ('p[lang|=en]', 'lang="en'),
            # ('div[class^="test"]', ''),
            # ('div[class$="test"]', ''),
            # ('div[class*="test"]', ''),
        ]
    )
    def test_simple_selectors(self, simple_selectors_html, sel_str, count_str):
        html_str = simple_selectors_html
        sel = uicss.Selector(sel_str)
        match_elems = sel.compiled_selector.findall(html_str)
        assert len(match_elems) == html_str.count(count_str)

    @pytest.mark.parametrize(
        "sel_str, start_list",
        [
            ('div + p', ['<p>My best friend is Mickey.</p>']),
            ('div p', ['<p>I live in Duckburg.</p>', '<p>I will not be styled.</p>']),
            ('div > p', ['<p>I live in Duckburg.</p>']),
            # ('p ~ ul', ''),
        ]
    )
    def test_compound_selectors(self, compound_selectors_html, sel_str, start_list):
        html_str = compound_selectors_html
        sel = uicss.Selector(sel_str)
        match_elems = sel.compiled_selector.findall(html_str)
        assert len(match_elems) == len(start_list)
        assert all(x.startswith(y) for x, y in zip(match_elems, start_list))

    def test_compiled_patterns(self):
        pass

    def test_invalid_selector_str(self):
        def helper_f(selector_str):
            sel = uicss.Selector(selector_str)
            assert not sel.is_valid
            assert sel.pattern.startswith('SelectorStrError')
            return sel

        selector_str = '(?#<nav'
        selector = helper_f(selector_str)

        selector_str = 'p, span, dos'
        selector = helper_f(selector_str)

    @pytest.mark.parametrize(
        "selector_str, specificity",
        [
            (':nth-of-type(3n)', (0, 0, 1, 0)),                             # pseudo class
            ('*', (0, 0, 0, 0)),                                            # universal selector (*)
            (':where', (0, 0, 0, 0)),                                       # pseudo-clalss :where()
            ('h1', (0, 0, 0, 1)),                                           # elemento
            ('::after', (0, 0, 0, 1)),                                      # seudo elemento
            ('.clase', (0, 0, 1, 0)),                                       # class
            ('[type="radio"]', (0, 0, 1, 0)),                               # attribute
            (':disabled', (0, 0, 1, 0)),                                    # pseudo class
            (':hover', (0, 0, 1, 0)),                                       # pseudo class
            ('#identifier', (0, 1, 0, 0)),                                  # id
            ('h1 + p::first-letter', (0, 0, 0, 3)),                         # # names can contain -
            ('li > a[href*="en-US"] > .inline-warning', (0, 0, 2, 2)),
        ]
    )
    def test_specifity(self, selector_str, specificity):
        selector = uicss.Selector(selector_str)
        assert selector.specificity == specificity

    def test_specificity_order(self):
        selector_strs = ['h1', '::after', '.clase', '[class]', ':disabled', '#identifier']
        sels = sorted([uicss.Selector(x) for x in selector_strs])
        assert [sel.selector_str for sel in sels] == selector_strs


class TestElementFactory:

    @pytest.mark.parametrize(
        "css_string1, css_string2",
        [
            (
                'li > a[href*="en-US"] > .inline-warning{a:1;}',
                """
                    li > a[href*="en-US"] > .inline-warning {
                        a:1;
                    }
                """
            ),
            (
                """
                    li > a[href*="en-US"] > .inline-warning {
                        a:1;
                    }
                """,
                """
                            /* Esto es un comentario */
                            li > a[href*="en-US"] > .inline-warning {
                                a:1;
                            }
                            /*
                            h1 + p::first-letter {
                                b:2;
                            } */
                        """
            ),
        ]
    )
    def test_css_string_equivalence(self, css_string1, css_string2):
        sels1 = uicss.XmlSerializer.process_css_string(css_string1)
        sels2 = uicss.XmlSerializer.process_css_string(css_string2)
        assert len(sels1) == len(sels2)
        assert all(sel1.selector_str == sel2.selector_str for sel1, sel2 in zip(sels1, sels2))
        assert all(map(lambda x: x.is_valid, [*sels1, *sels2]))




