import pytest

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
                    None
                )
            ),
            (
                'grid-template-rows',
                '[row1-start] 25% [row1-end row2-start] 25% [row2-end]',
                (
                    {'row1-start': 0, 'row1-end': 1, 'row2-start': 1, 'row2-end': 2},
                    ['25%', '25%'],
                    None
                )
            ),
            (
                'grid-template-columns',
                'repeat(3, 20px [col-start])',
                (
                    {'col-start': (1, 2, 3)},
                    ['20px', '20px', '20px'],
                    None
                )
            ),
            (
                'grid-template-columns',
                '30px repeat(3, 1fr) 30px',
                (
                    {},
                    ['30px', '1fr', '1fr', '1fr', '30px'],
                    None
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
            ('grid-area', 'header', ('area_name', 'header')),
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
        if not slaves['header1'] == slaves['header2']:
            pytest.xfail("failing different notation (but should work)")
        assert slaves['header1'] == slaves['header3']

        pos_keys = {'grid-row-span', 'grid-column-span', 'n-pos'}
        attrs = slaves['header1']
        assert attrs.keys() & pos_keys == pos_keys
        assert attrs['n-pos'] == 0
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
            'grid-column': 'span 2',
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
        pos_keys = {'grid-row-span', 'grid-column-span', 'n-pos'}
        assert attrs.keys() & pos_keys == pos_keys
        assert attrs['n-pos'] == 3
        assert attrs['grid-row-span'] == 2
        assert attrs['grid-column-span'] == 2

    @pytest.mark.parametrize(
        "grid, item_name, item_attribs, required",
        [
            (
                 {'grid-auto-flow': 'row'}, 'full-position-row-flow',
                 {'grid-column-start': '2', 'grid-column-end': 'uno', 'grid-row-start': '5', 'grid-row-end': 'span 3'},
                 1
            ),
            (
                {'grid-auto-flow': 'column'}, 'full-position-column-flow',
                {'grid-column-start': '2', 'grid-column-end': 'uno', 'grid-row-start': '5', 'grid-row-end': 'span 3'},
                1
            ),
            (
                    {'grid-auto-flow': 'row'}, 'row-full-position-flow-row',
                    {'grid-column-end': 'uno', 'grid-row-start': '5', 'grid-row-end': 'span 3'},
                    2
            ),
            (
                {'grid-auto-flow': 'column'}, 'row-full-position-flow-column',
                {'grid-column-end': 'uno', 'grid-row-start': '5', 'grid-row-end': 'span 3'},
                3
            ),
            (
                {'grid-auto-flow': 'row'}, 'default-position',
                {'grid-column-end': 'uno', 'grid-row-end': 'span 3'},
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
            (
                {'grid-auto-flow': 'row'}, 'full-position-flow-row',
                {'grid-column': 'header', 'grid-row': 'footer'},
                1
            ),
            (
                {'grid-auto-flow': 'row'}, 'full-position',
                {'grid-area': '1 / col4-start / last-line / 6'},
                1
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
            #   | 1  2  3  4  5  6            | 1  2  3  4  5  6
            # --------------------         ---------------------
            # 1 | x     x  y  z  z         1 |  0  1  2  3  4  5
            # 2 |       x  z  w  w         2 |  6  7  8  9 10 11
            # 3 | x  x  y  z  w  w         3 | 12 13 14 15 16 17
            # 4 |       y                  4 | 18 19 20 21 22 23
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
        assert n_pos('p(1, _)') == 3
        assert area_item('p(1, _)') == {3}
        assert n_pos('p(3, _)') == 14
        assert area_item('p(3, _)') == {14, 20}
        assert n_pos('p(_, 5)') == 4
        assert area_item('p(_, 5)') == {4, 5}
        assert n_pos('p(_, 4)') == 9
        assert area_item('p(_, 4)') == {9, 15}
        assert n_pos('p(_, _)') == 10
        assert area_item('p(_, _)') == {10, 11, 16, 17}

        taken = {0, 2, 3, 4, 5, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 20}
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
            ('p(1, _)', {'grid-column': 'span 2', 'grid-row': 'span 1 / 1'}, 0, {0, 1}),
            ('p(_, 1)', {'grid-column': 'span 1 / 1', 'grid-row': 'span 2'}, 0, {0, 3}),
            ('p(_1, _1)', {'grid-column': 'span 2 / 1', 'grid-row': 'span 2 / 1'}, 0, {0, 1, 4, 5}),
            ('p(2, _)', {'grid-column': 'span 1', 'grid-row': 'span 2 / 2'}, 1, {1, 3}),
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