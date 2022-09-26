import tkinter
import re

import pytest

import userinterface
from src.Tools.uiStyle.cssgrid import CssGrid

# Los casos de prueba provienen de la siguiente página
# https://css-tricks.com/snippets/css/complete-guide-grid/#prop-grid-template


class TestCssGridParsers:

    @pytest.mark.parametrize(
        "attrib, atemplate, required",
        [
            (
                'grid-template-columns',
                '[first] 40px [line2] 50px [line3] auto [col4start] 50px [five] 40px [end]',
                (
                    dict(first=0, line2=1, line3=2, col4start=3, five=4, end=5),
                    ['40px', '50px', 'auto', '50px', '40px'],
                    ''
                )
            ),
            (
                'grid-template-rows',
                '[row1-start] 25% [row1-end row2-start] 25% [row2-end]',
                (
                    {'row1-start': 0, 'row1-end': 1, 'row2-start': 1, 'row2-end': 2},
                    ['25%', '25%'],
                    ''
                )
            ),
            (
                'grid-template-columns',
                'repeat(3, 20px [col-start])',
                (
                    {'col-start': (1, 2, 3)},
                    ['20px', '20px', '20px'],
                    ''
                )
            ),
            (
                'grid-template-columns',
                '30px repeat(3, 1fr) 30px',
                (
                    {},
                    ['30px', '1fr', '1fr', '1fr', '30px'],
                    ''
                )
            ),
            (
                'grid-template-columns',
                'repeat(auto-fill, 1fr)',
                (
                        {},
                        [],
                        ('auto-fill', '1fr')
                )
            ),
            (
                'grid-template-areas',
                '"header header header header""main main . sidebar""footer footer footer footer"',
                (
                    {
                        'header': {'grid-row-start': 0, 'grid-column-start': 0, 'grid-row-end': 1, 'grid-column-end': 4},
                        'main': {'grid-row-start': 1, 'grid-column-start': 0, 'grid-row-end': 2, 'grid-column-end': 2},
                        'sidebar': {'grid-row-start': 1, 'grid-column-start': 3, 'grid-row-end': 2, 'grid-column-end': 4},
                        'footer': {'grid-row-start': 2, 'grid-column-start': 0, 'grid-row-end': 3, 'grid-column-end': 4},
                        '.': [(1, 2)],
                    },
                    {'header-start': 0, 'header-end': 1, 'main-start': 1, 'main-end': 2, 'sidebar-start': 1, 'sidebar-end': 2, 'footer-start': 2, 'footer-end': 3},
                    {'header-start': 0, 'header-end': 4, 'main-start': 0, 'main-end': 2, 'sidebar-start': 3, 'sidebar-end': 4, 'footer-start': 0, 'footer-end': 4},
                )
            ),
            ('row-gap', '15px', '15px'),
            ('column-gap', '25px', '25px'),
            ('justify-items', 'center', 'center'),
            ('align-items', 'start', 'start'),
            ('justify-content', 'center', 'center'),
            ('align-content', 'start', 'start'),
            ('grid-auto-rows', '40px', '40px'),
            ('grid-auto-columns', '60px', '60px'),
            ('grid-auto-flow', 'column', 'column'),
            ('grid-auto-flow', 'row dense', ['row', 'dense']),
        ]
    )
    def test_css_grid_container_parser(self, attrib, atemplate, required):
        acase, answ = CssGrid.parse_attr(attrib, atemplate)
        assert acase == 'to_store'
        assert answ == required

    @pytest.mark.parametrize(
        "attrib, atemplate, required",
        [
            ('grid-area', 'header',
                (
                    'to_process', [
                        ('grid-row-start', 'header-start'),
                        ('grid-column-start', 'header-start'),
                        ('grid-row-end', 'header-end'),
                        ('grid-column-end', 'header-end')
                    ]
                )
            ),
            ('grid-area', '1 / col4-start / last-line / 6',
                (
                    'to_process', [
                        ('grid-row-start', '1'),
                        ('grid-column-start', 'col4-start'),
                        ('grid-row-end', 'last-line'),
                        ('grid-column-end', '6')
                    ]
                )
            ),
            ('grid-column-start', '2', ('item', 1)),
            ('grid-column-end', 'five', ('item_name', 'five')),
            ('grid-row-start', 'row1-start', ('item_name', 'row1-start')),
            ('grid-row-end', '3', ('item', 2)),
            ('grid-column-end', 'span col4-start', ('span_name', 'col4-start')),
            ('grid-row-end', 'span 2', ('span', 2)),
            ('grid-column-end', '-1', ('item', -1)),
            ('justify-self', 'center', ('item_name', 'center')),
            ('align-self', 'start', ('item_name', 'start')),
        ]
    )
    def test_css_grid_item_parser(self, attrib, atemplate, required):
        acase, answ = CssGrid.parse_attr(attrib, atemplate)
        if acase == 'to_process':
            answ = list(answ)
        assert (acase, answ) == required

    @pytest.mark.parametrize(
        "attrib, atemplate, required",
        [
            (
                'gap', '15px 10px', [
                    ('grid-row-gap', '15px'),
                    ('grid-column-gap', '10px'),
                ]
            ),
            (
                'grid-template',
                '[row1-start] "header header header" 25px [row1-end][row2-start] "footer footer footer" 25px [row2-end] / auto 50px auto',
                [
                    ('grid-template-rows', '[row1-start] 25px [row1-end][row2-start] 25px [row2-end]'),
                    ('grid-template-columns', 'auto 50px auto'),
                    ('grid-template-areas', '"header header header""footer footer footer"')
                ]
            ),
            (
                'place-items', 'center', [
                    ('align-items', 'center'),
                    ('justify-items', 'center'),
                ]
            ),
            (
                'place-content', 'center / stretch', [
                    ('align-content', 'center'),
                    ('justify-content', 'stretch'),
                ]
            ),
            (
                'grid', '100px 300px / 3fr 1fr', [
                    ('grid-template-rows', '100px 300px'),
                    ('grid-template-columns', '3fr 1fr')
                ]
            ),
            (
                'grid', 'auto-flow / 200px 1fr', [
                    ('grid-auto-flow', 'row'),
                    ('grid-template-columns', '200px 1fr')
                ]
            ),
            (
                'grid', 'auto-flow dense 100px / 1fr 2fr', [
                    ('grid-auto-flow', 'row dense'),
                    ('grid-auto-rows', '100px'),
                    ('grid-template-columns', '1fr 2fr')
                ]
            ),
            (
                'grid', '100px 300px / auto-flow 200px', [
                    ('grid-template-rows', '100px 300px'),
                    ('grid-auto-flow', 'column'),
                    ('grid-auto-columns', '200px')
                ]
            ),
            (
                'grid',
                '[row1-start] "header header header" 1fr [row1-end][row2-start] "footer footer footer" 25px [row2-end] / auto 50px auto',
                [
                    ('grid-template-rows', '[row1-start] 1fr [row1-end][row2-start] 25px [row2-end]'),
                    ('grid-template-columns', 'auto 50px auto'),
                    ('grid-template-areas', '"header header header""footer footer footer"')
                ]
            ),
            # ================ items-shorcuts ===========================
            ('grid-column', '3 / span 2', [('grid-column-start', '3'), ('grid-column-end', 'span 2')]),
            ('grid-row', 'third-line / 4', [('grid-row-start', 'third-line'), ('grid-row-end', '4')]),
            (
                    'grid-area', '1 / col4-start / last-line / 6', [
                        ('grid-row-start', '1'),
                        ('grid-column-start', 'col4-start'),
                        ('grid-row-end', 'last-line'),
                        ('grid-column-end', '6'),
                    ]
            ),
            ('place-self', 'center', [('align-self', 'center'), ('justify-self', 'center')]),
        ]
    )
    def test_css_grid_shortcuts_parser(self, attrib, atemplate, required):
        attribs = {attrib: atemplate}
        to_verify = CssGrid.canonalize_attribs(attribs)
        assert to_verify == dict(required)

    def test_naming_and_positioning_items_by_grid_areas(self):
        # https://learncssgrid.com/#grid-container
        grid = {
            'grid-template-areas': '"header header"\n"content sidebar"\n"footer footer"',
            'grid-template-rows': '150px 1fr 100px',
            'grid-template-columns': '1fr 200px',
        }
        cssgrid = CssGrid(**grid)
        item_attrs = {
            'grid-row-start': 'header',
            'grid-row-end': 'header',
            'grid-column-start': 'header',
            'grid-column-end': 'header',
        }
        cssgrid.register_item('header1', item_attrs)
        item_attrs = {
            'grid-row': 'header',
            'grid-column': 'header',
        }
        cssgrid.register_item('header2', item_attrs)
        item_attrs = {
            'grid-area': 'header',
        }
        cssgrid.register_item('header3', item_attrs)
        slaves = dict(cssgrid.slaves)
        assert slaves['header1'] == slaves['header2']
        assert slaves['header1'] == slaves['header3']

        pos_keys = {'grid-row-span', 'grid-column-span'}
        attrs = slaves['header1']
        assert attrs.keys() & pos_keys == pos_keys
        assert attrs['grid-row-span'] == 1
        assert attrs['grid-column-span'] == 2

    def test_naming_and_positioning_items_by_grid_lines_with_the_same_name(self):
        # https://learncssgrid.com/#grid-container
        grid = {
            'grid-template-rows': 'repeat(3, [row-start] 1fr [row-end])',
            'grid-template-columns': 'repeat(3, [col-start] 1fr [col-end])',
        }
        cssgrid = CssGrid(**grid)
        item_attrs = {
            'grid-row': '2 / span 2',
            'grid-column': '1 / span 2',
        }
        cssgrid.register_item('item1', item_attrs)

        item_attrs = {
            'grid-row': 'row-start 2 / row-end 3',
            'grid-column': 'col-start / col-start 3',
        }
        cssgrid.register_item('item2', item_attrs)
        slaves = dict(cssgrid.slaves)

        attrs = slaves['item2']
        assert slaves['item1'] == attrs
        pos_keys = {'grid-row-span', 'grid-column-span'}
        assert attrs.keys() & pos_keys == pos_keys
        assert attrs['grid-row-span'] == 2
        assert attrs['grid-column-span'] == 2

    @pytest.mark.parametrize(
        "grid, item_name, item_attribs, required",
        [
            (
                 {'grid-auto-flow': 'row'}, 'full-position-row-flow',
                 {'grid-column-start': '2', 'grid-column-end': '8', 'grid-row-start': '5', 'grid-row-end': 'span 3'},
                 1
            ),
            (
                {'grid-auto-flow': 'column'}, 'full-position-column-flow',
                {'grid-column-start': '2', 'grid-column-end': '8', 'grid-row-start': '5', 'grid-row-end': 'span 3'},
                1
            ),
            (
                    {'grid-auto-flow': 'row'}, 'row-full-position-flow-row',
                    {'grid-column-end': '8', 'grid-row-start': '5', 'grid-row-end': 'span 3'},
                    2
            ),
            (
                {'grid-auto-flow': 'column'}, 'row-full-position-flow-column',
                {'grid-column-end': '8', 'grid-row-start': '5', 'grid-row-end': 'span 3'},
                3
            ),
            (
                {'grid-auto-flow': 'row'}, 'default-position',
                {'grid-column-end': '8', 'grid-row-end': 'span 3'},
                4
            ),
            (
                {'grid-auto-flow': 'row'}, 'default-position',
                {},
                4
            ),
            (
                {'grid-auto-flow': 'row'}, 'row-position-flow-row',
                {'grid-column': 'span 3', 'grid-row': '2 / 4'},
                2
            ),
        ]
    )
    def test_item_ordering(self, grid, item_name, item_attribs, required):
        cssgrid = CssGrid(**grid)
        priority = cssgrid.register_item(item_name, item_attribs)
        assert priority == required

    def test_insertion_point_explicit_grid(self):
        '''
            x, y Grid                       n-pos Grid
            #   | 1 - 2 - 3 - 4 - 5 - 6 - 7            | 1  2  3  4  5  6
            # 1 ---------------------------         ---------------------
            #   |   x   y   x       z   z         1 |  0  1  2  3  4  5
            # 2 ---------------------------         ---------------------
            #   |           x   z   w   w         2 |  6  7  8  9 10 11
            # 3 ---------------------------         ---------------------
            #   |   x   x   y   z   w   w         3 | 12 13 14 15 16 17
            # 4 ---------------------------         ---------------------
            #  |            y                  4 | 18 19 20 21 22 23
            # 5 ---------------------------         ---------------------
        '''
        grid = {
            'grid-template-rows': 'repeat(4, 50px)',
            'grid-template-columns': 'repeat(6, 50px)',
        }
        cssgrid = CssGrid(**grid)
        # Absolute position (x)
        cssgrid.register_item('p(1, 1)', {'grid-row': '1', 'grid-column': '1'})
        cssgrid.register_item('p(3, 1)', {'grid-row': '3', 'grid-column': '1 / 3'})
        cssgrid.register_item('p(1, 3)', {'grid-row': '1 / 3', 'grid-column': '3'})

        # auto-grid-flow position (y)
        cssgrid.register_item('p(1, _)', {'grid-row': '1'})
        cssgrid.register_item('p(3, _)', {'grid-row': '3 / 5'})

        # NO auto-grid-flow position (z)
        cssgrid.register_item('p(_, 5)', {'grid-column': '5 / 7'})
        cssgrid.register_item('p(_, 4)', {'grid-column': '4', 'grid-row': 'span 2'})

        # auto position (w)
        cssgrid.register_item('p(_, _)', {'grid-column': 'span 2', 'grid-row': 'span 2'})


        slaves_items = cssgrid.get_process_item_attribs()
        slaves = dict(slaves_items)
        n_pos = lambda x: slaves[x]['n-pos']
        area_item = lambda x: cssgrid.enumerate_area_items(n=slaves[x]['n-pos'], nrows=slaves[x]['grid-row-span'], ncols=slaves[x]['grid-column-span'])

        assert n_pos('p(1, 1)') == 0
        assert area_item('p(1, 1)') == {0}
        assert n_pos('p(3, 1)') == 12
        assert area_item('p(3, 1)') == {12, 13}
        assert n_pos('p(1, 3)') == 2
        assert area_item('p(1, 3)') == {2, 8}
        assert n_pos('p(1, _)') == 1
        assert area_item('p(1, _)') == {1}
        assert n_pos('p(3, _)') == 14
        assert area_item('p(3, _)') == {14, 20}
        assert n_pos('p(_, 5)') == 4
        assert area_item('p(_, 5)') == {4, 5}
        assert n_pos('p(_, 4)') == 9
        assert area_item('p(_, 4)') == {9, 15}
        assert n_pos('p(_, _)') == 10
        assert area_item('p(_, _)') == {10, 11, 16, 17}

        taken = {0, 1, 2, 4, 5, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 20}
        assert cssgrid.taken == taken

    @pytest.mark.parametrize(
        "item_name, item_attribs, pos, area",
        [
            ('p(1, _)', {'grid-row': '1', 'grid-column': 'span 2'}, 2, {2, 3}),
            ('p(_, _)', {'grid-column': 'span 2', 'grid-row': 'span 2'}, 6, {6, 7, 9, 10}),
        ]
    )
    def test_insertion_point_implicit_grid(self, item_name, item_attribs, pos, area):
        '''
            x, y Grid                       n-pos Grid
            #   | 1  2  3  4  5  6             | 1  2  3  4  5  6
            # --------------------         ---------------------
            # 1 | x  x  y  y                1 |  0  1  2
            # 2 | x  x                      2 |  3  4  5
            # 3 | w  w                      3 |  6  7  8
            # 4 | w  w                      4 |
        '''
        grid = {
            'grid-template-rows': 'repeat(3, 50px)',
            'grid-template-columns': 'repeat(3, 50px)',
        }
        cssgrid = CssGrid(**grid)
        cssgrid.register_item('p(1, 1)', {'grid-row': '1 / 3', 'grid-column': '1 / 3'})

        cssgrid.register_item(item_name, item_attribs)

        slaves_items = cssgrid.get_process_item_attribs()
        slaves = dict(slaves_items)
        n_pos = lambda x: slaves[x]['n-pos']
        area_item = lambda x: cssgrid.enumerate_area_items(n=slaves[x]['n-pos'], nrows=slaves[x]['grid-row-span'], ncols=slaves[x]['grid-column-span'])

        assert n_pos(item_name) == pos
        assert area_item(item_name) == area

    @pytest.mark.parametrize(
        "item_name, item_attribs, pos, area",
        [
            ('p(2, _)', {'grid-column': 'span 1', 'grid-row': 'span 2 / 2'}, 1, {1, 3}),
            ('p(1, _)', {'grid-column': 'span 2 / auto', 'grid-row': 'span 1 / 1'}, 0, {0, 1}),
            ('p(_, 1)', {'grid-column': 'span 1 / 1', 'grid-row': 'span 2'}, 0, {0, 3}),
            ('p(_1, _1)', {'grid-column': 'span 2 / 1', 'grid-row': 'span 2 / 1'}, 0, {0, 1, 4, 5}),
            ('p(_, 2)', {'grid-column': 'span 2 / 2', 'grid-row': 'span 1'}, 6, {6, 7}),
            ('p(_, 2)', {'grid-column': 'span 3 / 3', 'grid-row': 'span 1'}, 9, {9, 10, 11}),
        ]
    )
    def test_insertion_point_offset_grid(self, item_name, item_attribs, pos, area):
        '''
            x, y Grid                       n-pos Grid
            #   | 1  2  3  4  5  6             | 1  2  3  4  5  6
            # --------------------         ---------------------
            # 1 | x                          1 |  0  1
            # 2 | x  x                       2 |  2  3
            # 3 |    x                       3 |  4  5
            # 4 |                            4 |
        '''
        grid = {
            'grid-template-rows': 'repeat(3, 50px)',
            'grid-template-columns': 'repeat(2, 50px)',
        }
        cssgrid = CssGrid(**grid)
        cssgrid.register_item('p(1, 1)', {'grid-row': '1 / 3', 'grid-column': '1 / 2'})
        cssgrid.register_item('p(2, 2)', {'grid-row': '2 / 4', 'grid-column': '2 / 3'})

        cssgrid.register_item(item_name, item_attribs)

        slaves_items = cssgrid.get_process_item_attribs()
        slaves = dict(slaves_items)
        n_pos = lambda x: slaves[x]['n-pos']
        area_item = lambda x: cssgrid.enumerate_area_items(n=slaves[x]['n-pos'], nrows=slaves[x]['grid-row-span'], ncols=slaves[x]['grid-column-span'])

        assert n_pos(item_name) == pos
        assert area_item(item_name) == area

    def test_insertion_point_pattern(self):
        '''
        https://css-tricks.com/exploring-css-grids-implicit-grid-and-auto-placement-powers/#top-of-site
        '''

        def nth_child(x):
            if x.isdigit():
                return lambda y: y == int(x)
            x = x.replace(' ', '')
            a, b = map(int, re.findall(r'(\d+)[a-z]+([+-]\d+)', x)[0])
            return lambda y: not (y - b) % a

        def last_child(nitems):
            return lambda y: y == nitems

        def apply_selector(nitems, selectors):
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

        def process_items(grid, items):
            cssgrid = CssGrid(**grid)
            [
                cssgrid.register_item(item_name, attribs)
                for item_name, attribs in items
            ]
            slaves_items = cssgrid.get_process_item_attribs()
            return dict(slaves_items)

        bbox = lambda x: (
            slaves[x]['grid-row-start'], slaves[x]['grid-column-start'],
            slaves[x]['grid-row-span'], slaves[x]['grid-column-span'],
        )

        # Dinamic Layout 1

        for k in range(4):
            selectors = [
                ((nth_child('2'),), {'grid-column-start': '2'}),
                ((nth_child('3'), last_child(k + 1)), {'grid-column': 'span 2'}),
            ]
            grid = {}
            conf = apply_selector(k + 1, selectors)
            slaves = process_items(grid, conf)
            req = [(0, 0, 1, 1), (0, 1, 1, 1), (1, 0, 1, 1 if k != 2 else 2), (1, 1, 1, 1)]
            assert all(bbox(key) == req[k] for k, (key, _) in enumerate(conf))

        # Dinamic Layout 2

        for k in range(4):
            selectors = [
                ((nth_child('4'),), {'grid-column-start': '2'}),
                ((nth_child('3'), last_child(k + 1)), {'grid-column': 'span 2'}),
            ]
            grid = {}
            conf = apply_selector(k + 1, selectors)
            slaves = process_items(grid, conf)
            req = [(0, 0, 1, 1), (0, 1, 1, 1) if k != 1 else (1, 0, 1, 1), (1, 0, 1, 1 if k != 2 else 2), (1, 1, 1, 1)]
            assert all(bbox(key) == req[k] for k, (key, _) in enumerate(conf))

        # Grid patterns 1

        grid = {
            'grid-auto-rows': '100px',
            'grid-auto-columns': '1fr',
            'grid-gap': '5px',
        }
        selectors = [
            ((nth_child('4n + 1'), ), {'grid-column': 'span 2'}),
            ((nth_child('4n + 4'), ), {'grid-column': '2 /span 2'}),
        ]
        nitems = 12
        items = apply_selector(nitems, selectors)

        req = [(0, 0, 1, 2), (0, 2, 1, 1), (1, 0, 1, 1), (1, 1, 1, 2)]
        slaves = process_items(grid, items)

        assert all(
            bbox(key) == ((pt := req[k % 4])[0] + 2 * (k // 4), pt[1], pt[2], pt[3])
            for k, (key, _) in enumerate(items)
        )

        # Grid patterns 2
        grid = {
            'grid-auto-flow': 'dense',
            'grid-auto-rows': '100px',
            'grid-auto-columns': '1fr',
            'grid-gap': '5px',
        }
        selectors = [
            ((nth_child('6n + 2'), ), {'grid-column': '1'}),
            ((nth_child('6n + 3'), ), {'grid-area': 'span 2 / 2'}),
            ((nth_child('6n + 4'), ), {'grid-row': 'span 2'}),
        ]

        nitems = 12
        items = apply_selector(nitems, selectors)

        req = [(0, 0, 1, 1), (1, 0, 1, 1), (0, 1, 2, 1), (2, 0, 2, 1), (2, 1, 1, 1), (3, 1, 1, 1)]
        slaves = process_items(grid, items)

        base = 6
        assert all(
            bbox(key) == ((pt := req[k % base])[0] + 4 * (k // base), pt[1], pt[2], pt[3])
            for k, (key, _) in enumerate(items)
        )


        grid = {
            'grid-auto-rows': '100px',
            'grid-auto-columns': '1fr',
            'grid-gap': '5px',
        }
        selectors = [
            ((nth_child('6n + 2'), ), {'grid-column': '1'}),
            ((nth_child('6n + 3'), ), {'grid-area': 'span 2 / 2'}),
            ((nth_child('6n + 4'), ), {'grid-area': 'span 2 / 1'}),
        ]
        nitems = 12
        items = apply_selector(nitems, selectors)

        req = [(0, 0, 1, 1), (1, 0, 1, 1), (1, 1, 2, 1), (2, 0, 2, 1), (3, 1, 1, 1), (4, 0, 1, 1)]
        slaves = process_items(grid, items)

        base = 6
        assert all(
            bbox(key) == ((pt := req[k % base])[0] + 4 * (k // base), pt[1], pt[2], pt[3])
            for k, (key, _) in enumerate(items[:6])
        )

        grid = {
            'grid-auto-flow': 'dense',
            'grid-auto-rows': '100px',
            'grid-auto-columns': '1fr',
            'grid-gap': '5px',
        }
        selectors = [
            ((nth_child('10n + 8'), ), {'grid-column': '1'}),
            ((nth_child('10n + 9'), ), {'grid-column': '2'}),
            ((nth_child('10n + 2'), ), {'grid-column': '3'}),
            ((nth_child('10n + 3'), ), {'grid-column': '4'}),
            ((nth_child('10n + 1'), ), {'grid-area': 'span 2 / span 2'}),
            ((nth_child('10n + 10'), ), {'grid-area': 'span 2 / span 2'}),
        ]
        nitems = 20
        items = apply_selector(nitems, selectors)

        req = [
            (0, 0, 2, 2), (0, 2, 1, 1), (0, 3, 1, 1), (1, 2, 1, 1), (1, 3, 1, 1),
            (2, 0, 1, 1), (2, 1, 1, 1), (3, 0, 1, 1), (3, 1, 1, 1), (2, 2, 2, 2),
        ]
        slaves = process_items(grid, items)
        base = 10
        assert all(
            bbox(key) == ((pt := req[k % base])[0] + 4 * (k // base), pt[1], pt[2], pt[3])
            for k, (key, _) in enumerate(items)
        )

        grid = {
            'grid-auto-flow': 'dense',
            'grid-auto-rows': '100px',
            'grid-auto-columns': '1fr',
            'grid-gap': '5px',
        }
        selectors = [
            ((nth_child('10n + 2'), ), {'grid-column': 'span 2'}),
            ((nth_child('10n + 5'), ), {'grid-column': 'span 2'}),
            ((nth_child('10n + 7'), ), {'grid-column': 'span 2'}),
            ((nth_child('10n + 8'), ), {'grid-column': 'span 2'}),
            ((nth_child('10n + 9'), ), {'grid-column': '3'}),
            ((nth_child('10n + 3'), ), {'grid-column': '4'}),
            ((nth_child('10n + 1'), ), {'grid-row': 'span 2'}),
            ((nth_child('10n + 10'), ), {'grid-row': 'span 2'}),
        ]
        nitems = 20
        items = apply_selector(nitems, selectors)

        req = [
            (0, 0, 2, 1), (0, 1, 1, 2), (0, 3, 1, 1), (1, 1, 1, 1), (1, 2, 1, 2),
            (2, 0, 1, 1), (2, 1, 1, 2), (3, 0, 1, 2), (3, 2, 1, 1), (2, 3, 2, 1),
        ]
        slaves = process_items(grid, items)
        base = 10
        assert all(
            bbox(key) == ((pt := req[k % base])[0] + 4 * (k // base), pt[1], pt[2], pt[3])
            for k, (key, _) in enumerate(items)
        )

    def test_auto_fill(self):
        grid = {
            'grid-template-columns': 'repeat(auto-fill, minmax(100px, 1fr))',
        }
        cssgrid = CssGrid(**grid)

        with pytest.raises(AttributeError):
            cssgrid.master

        app = tkinter.Tk()
        cssgrid.config_master(app)
        for k in range(1, 8):
            wdg = tkinter.Label(app, name=f'item{k:0>2d}')
            cssgrid.register_item(wdg, {})

        confs = [
            {'widget': app, 'width': 12, 'height': 500},
            {'widget': app, 'width': 500, 'height': 500},
            {'widget': app, 'width': 700, 'height': 500},
            {'widget': app, 'width': 1200, 'height': 500},
            {'widget': app, 'width': 12, 'height': 500},
        ]
        for data in confs:
            event = tkinter.Event()
            [setattr(event, attr_name, value) for attr_name, value in data.items()]
            cssgrid.resize(event)

            nslaves = len(cssgrid.slaves)
            assert cssgrid.ncolumns == max(1, data['width'] // 100)
            delta = 1 if nslaves != cssgrid.ncolumns else 0
            assert cssgrid.nrows == min(nslaves, nslaves // cssgrid.ncolumns + delta)

    def test_auto_fit(self):
        grid = {
            'grid-template-columns': 'repeat(auto-fit, minmax(100px, 1fr))',
        }
        cssgrid = CssGrid(**grid)

        with pytest.raises(AttributeError):
            cssgrid.master

        app = tkinter.Tk()
        cssgrid.config_master(app)
        for k in range(1, 8):
            wdg = tkinter.Label(app, name=f'item{k:0>2d}')
            cssgrid.register_item(wdg, {})

        confs = [
            {'widget': app, 'width': 12, 'height': 500},
            {'widget': app, 'width': 500, 'height': 500},
            {'widget': app, 'width': 700, 'height': 500},       # nslaves == ncolumns
            {'widget': app, 'width': 1200, 'height': 500},      # nslaves == ncolumns
            {'widget': app, 'width': 12, 'height': 500},
        ]
        for data in confs:
            event = tkinter.Event()
            [setattr(event, attr_name, value) for attr_name, value in data.items()]
            cssgrid.resize(event)

            nslaves = len(cssgrid.slaves)
            assert cssgrid.ncolumns == min(nslaves, max(1, data['width'] // 100))
            delta = 1 if nslaves != cssgrid.ncolumns else 0
            assert cssgrid.nrows == min(nslaves, nslaves // cssgrid.ncolumns + delta)

    def test_minmax(self):
        max_size = '300px'
        grid = {
            'grid-template-columns': f'50px minmax(50px, {max_size}) minmax(50px, 1fr)',
            'grid-template-rows': '50px 50px 50px',
            'gap': '10px 10px',
        }
        cssgrid = CssGrid(**grid)

        with pytest.raises(AttributeError):
            cssgrid.master

        assert cssgrid.isResponsive('column')

        with pytest.raises(AttributeError):
            cssgrid.isResponsive('column', 1)

        app = tkinter.Tk()
        cssgrid.config_master(app)
        for k in range(1, 8):
            wdg = tkinter.Label(app, name=f'item{k:0>2d}')
            cssgrid.register_item(wdg, {})

        confs = [
            {'widget': app, 'width': 740, 'height': 500},
            {'widget': app, 'width': 1200, 'height': 500},
            {'widget': app, 'width': 12, 'height': 500},
            {'widget': app, 'width': 500, 'height': 500},
            {'widget': app, 'width': 12, 'height': 500},
        ]
        for data in confs:
            event = tkinter.Event()
            [setattr(event, attr_name, value) for attr_name, value in data.items()]
            cssgrid.resize(event)

            assert not cssgrid.isResponsive('column', 1)
            assert not cssgrid.isResponsive('column', 2) if data['width'] >= 670 else cssgrid.isResponsive('column', 2)
            assert cssgrid.isResponsive('column', 3)
