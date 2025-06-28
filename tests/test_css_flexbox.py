import collections
import tkinter
import re

import pytest

import mywidgets.userinterface as userinterface
from mywidgets.Tools.uiStyle.cssgrid import CssUnit
from src.Tools.uiStyle.cssflexbox import CssFlexBox

# Los casos de prueba provienen de la siguiente página
# https://css-tricks.com/snippets/css/complete-guide-grid/#prop-grid-template

def nth_child(x):
    if x.isdigit():
        return lambda y: y == int(x)
    x = x.replace(' ', '')
    a, b = map(int, re.findall(r'(\d+)[a-z]+([+-]\d+)', x)[0])
    return lambda y: not (y - b) % a


def last_child(nitems):
    return lambda y: y == nitems


def apply_selector(nitems:int, selectors:list[tuple[tuple[callable, ...], dict[str, str]]]) -> list[tuple[str, dict[str, str]]]:
    items = []
    for k in range(1, nitems + 1):
        item_name = f'item{k:0>2d}'
        attribs = dict(
            z
            for w in [conf for fncs, conf in selectors if all(fnc(k) for fnc in fncs)]
            for z in w.items()
        )
        items.append((item_name, attribs))
    return items


def process_items(cssgrid, items):
    [
        cssgrid.register_item(item_name, attribs)
        for item_name, attribs in items
    ]
    slaves_items = cssgrid.get_process_item_attribs()
    return dict(slaves_items)


class TestCssFlexBox:

    @pytest.mark.parametrize(
        "attrib, atemplate, required",
        [
            ('flex-direction', 'row', 'row'),
            ('flex-direction', 'row-reverse', 'row-reverse'),
            ('flex-direction', 'column', 'column'),
            ('flex-direction', 'column-reverse', 'column-reverse'),
            ('flex-wrap', 'nowrap', 'nowrap'),
            ('flex-wrap', 'wrap', 'wrap'),
            ('flex-wrap', 'wrap-reverse', 'wrap-reverse'),
        ]
    )
    def test_css_flexbox_container_basic_attribs_parsers(self, attrib, atemplate, required):
        acase, answ = CssFlexBox.parse_attr(attrib, atemplate)
        assert acase == 'to_store'
        assert answ == required

    @pytest.mark.parametrize(
        "attrib, atemplate, required",
        [
            ('order', '-5', ('to_store', '-5')),
            ('flex-grow', '5', ('to_store', '5')),
            ('flex-shrink', '5', ('to_store', '5')),
            ('flex-basis', '5px', ('to_store', '5px')),
            ('flex-basis', 'auto', ('to_store', 'auto')),
        ]
    )
    def test_css_flexbox_item_basic_parsers(self, attrib, atemplate, required):
        acase, answ = CssFlexBox.parse_attr(attrib, atemplate)
        if acase == 'to_process':
            answ = list(answ)
        assert (acase, answ) == required

    @pytest.mark.parametrize(
        "attrib, atemplate, required",
        [
            ('flex-flow', 'row nowrap', [('flex-direction', 'row'), ('flex-wrap', 'nowrap')]),
            ('gap', '10px 20px', [('row-gap', '10px'), ('column-gap', '20px')]),
            ('gap', '10px', [('row-gap', '10px')]),
            # ================ items-shorcuts ===========================
            ('flex', '1 2 10px', [('flex-grow', '1'), ('flex-shrink', '2'), ('flex-basis', '10px')]),
            ('flex', 'initial', [('flex-grow', '0'), ('flex-shrink', '1'), ('flex-basis', 'auto')]),
            ('flex', 'auto', [('flex-grow', '1'), ('flex-shrink', '1'), ('flex-basis', 'auto')]),
            ('flex', 'none', [('flex-grow', '0'), ('flex-shrink', '0'), ('flex-basis', 'auto')]),
            ('flex', '10', [('flex-grow', '10'), ('flex-shrink', '1'), ('flex-basis', '0px')]),
        ]
    )
    def test_css_flexbox_shortcut_parsers(self, attrib, atemplate, required):
        attribs = {attrib: atemplate}
        to_verify = CssFlexBox.canonalize_attribs(attribs)
        assert to_verify == dict(required)


    @pytest.mark.parametrize(
        "attrib, atemplate, errorclass",
        [
            ('flex-direction', 'row reverse', ValueError),
            ('flex-wrap', 'wrap reverse', ValueError),
            ('flex-wrap', 'row-reverse', ValueError),
            ('flex-grow', '-5', ValueError),
            ('flex-shrink', '-5', ValueError),
            ('flex-basis', 'content', ValueError),
        ]
    )
    def test_invalid_template_for_attribute(self, attrib, atemplate, errorclass):
        with pytest.raises(errorclass):
            CssFlexBox.parse_attr(attrib, atemplate)


    @pytest.mark.parametrize(
        "orders",
        [
            [1, 2, 3],
            [2, 1, 3],
            [3, 1, 2],
            [2, 3, 1],
        ]
    )
    def test_flex_algorithm_large_item(self, orders):
        grid = {
                  'flex-flow': 'row wrap',
                  'align-items': 'stretch',
                  'gap': '5px 5px',
                  'justify-content': 'flex-start',
                  'align-content': 'center',
        }
        cssflex = CssFlexBox(**grid)
        items = [
            ('big_item', {'flex': '1 1 200px', 'width': '200px', 'height': '50px'}),
            ('other_item1', {'flex': '1 1 20px', 'width': '20px', 'height': '25px'}),
            ('other_item2', {'flex': '1 1 20px', 'width': '20px', 'height': '25px'}),
        ]
        for order , (name, attrib) in zip(orders, items):
            attrib['order'] = f'{order}'
            cssflex.register_item(name, attrib)

        Event = collections.namedtuple('Event', 'width height')
        event = Event(width=120, height=80)

        slaves = cssflex.get_process_item_attribs(event)
        slaves = dict(slaves)
        assert 'flex-line' in slaves['big_item']
        flex_line = slaves['big_item']['flex-line']
        assert flex_line['n-widgets'] == 1
        pass

    @pytest.mark.parametrize(
        "case, req_width, max_width, min_width",
        [
            ('min-width < required width < max-width', 120, '150px', '75px'),
            ('required width > max-width', 200, '150px', '75px'),
            ('required width < min-width', 25, '150px', '75px'),
        ]
    )
    def test_flex_algorithm_limits(self, case, req_width, max_width, min_width):
        grid = {
                  'flex-flow': 'row wrap',
                  'align-items': 'stretch',
                  'gap': '5px 5px',
                  'justify-content': 'flex-start',
                  'align-content': 'center',
        }
        cssflex = CssFlexBox(**grid)
        items = [
            (
                'big_item',
                {'flex': '1 1 100px', 'width': '75px', 'height': '50px', 'max-width': max_width, 'min-width': min_width}
            ),
        ]
        for name, attrib in items:
            cssflex.register_item(name, attrib)

        Event = collections.namedtuple('Event', 'width height')
        event = Event(width=req_width, height=80)

        slaves = cssflex.get_process_item_attribs(event)
        slaves = dict(slaves)

        key = 'big_item'
        assert 'flex-line' in slaves[key]
        flex_line = slaves[key].pop('flex-line')
        assert flex_line['n-widgets'] == 1

        min_width, max_width = map(lambda x: CssUnit(x)._value(event, 'width'), (min_width, max_width))
        width = max(min_width, min(max_width, req_width))
        assert slaves[key]['width'] == width, case
        pass

    @pytest.mark.parametrize(
        "case, req_width, max_width, min_width",
        [
            ('active: <flexible', 300, 150, 75),
            ('active: flexible, flex-shrink', 360, 150, 75),
            ('active: flexible, flex-grow', 440, 150, 75),
            ('active: flexible>', 560, 150, 75),
        ]
    )
    def test_flex_algorithm_flextypes(self, case, req_width, max_width, min_width):
        grid = {
                  'flex-flow': 'row nowrap',
                  'align-items': 'stretch',
                  'justify-content': 'flex-start',
                  'align-content': 'center',
        }
        cssflex = CssFlexBox(**grid)
        basis = 100
        items = [
            (
                'flexible',
                {'flex': f'1 1 {basis}px', 'width': '100px', 'height': '50px'}
            ),
            (
                'inflexible',
                {'flex': f'0 0 {basis}px', 'width': '100px', 'height': '50px'}
            ),
            (
                'flex-grow',
                {'flex': f'1 0 {basis}px', 'width': '100px', 'height': '50px', 'max-width': f'{max_width}px'}
            ),
            (
                'flex-shrink',
                {'flex': f'0 1 {basis}px', 'width': '100px', 'height': '50px', 'min-width': f'{min_width}px'}
            ),
        ]
        for name, attrib in items:
            cssflex.register_item(name, attrib)

        Event = collections.namedtuple('Event', 'width height')
        event = Event(width=req_width, height=80)

        slaves = cssflex.get_process_item_attribs(event)
        slaves = dict(slaves)

        key = 'inflexible'
        assert slaves[key]['width'] == basis, case

        key = 'flex-grow'
        assert basis <= slaves[key]['width'] <= max_width, case

        key = 'flex-shrink'
        assert min_width <= slaves[key]['width'] <= basis, case

        key = 'flexible'
        assert slaves[key]['width'] <= basis or slaves[key]['width'] >= slaves['flex-grow']['width'], case
        assert slaves[key]['width'] >= basis or slaves[key]['width'] <= slaves['flex-shrink']['width'], case

        freeze = [wdg_width for key in slaves if (wdg_width := slaves[key]['width']) in (basis, min_width, max_width)]
        nfree = max(len(items) - len(freeze), 1)            # "flexible" always active
        assert slaves['flexible']['width'] == (req_width - sum(freeze)) // nfree
        pass

