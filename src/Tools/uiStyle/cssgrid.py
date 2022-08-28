import collections
import itertools
import re
import functools

class CssGridContainer:
    '''
    Traduce el css grid al tkinter grid.
    '''

    def __init__(self, grid_template_columns, grid_template_rows):
        self.parameters = {
            'grid-template-columns': '[line-name]? <track-size> ... ... ...',
            'grid-template-rows': '[line-name]? <track-size> ... ... ...',
            'grid-template-areas': '<grid-area-name> | . | none | ...',
            'column-gap': '<line-size>',
            'row-gap': '<line-size>',
            'justify-items': 'start | end | center | stretch',
            'align-items': 'start | end | center | stretch',
            'justify-content': 'start | end | center | stretch | space-around | space-between | space-evenly',
            'align-content': 'start | end | center | stretch | space-around | space-between | space-evenly',
            'grid-auto-columns': '<track-size> ... ...',
            'grid-auto-rows': '<track-size> ... ...',
            'grid-auto-flow': ' row | column | row dense | column dense'
        }
        self.synonims = {
            'grid-column-gap': 'column-gap',
            'grid-row-gap': 'row-gap',
            'gap': 'grid-gap',

        }
        self.equivalents = {
            'grid-template': '<grid-template-areas> | <grid-template-rows> / <grid-template-columns>',
            'gap': '<row-gap> <column-gap>',
            'place-items': '<align-items> / <justify-items>',
            'place-content': '<align-content> / <justify-content>',
            'grid': 'none | <grid-template> | '
                    '<grid-template-rows> / [ auto-flow && dense? ] <grid-auto-columns>? |'
                    '[ auto-flow && dense? ] <grid-auto-rows>? / <grid-template-columns>'
        }
        pass

    def attribs(self):
        return self.parameters | self.synonims | self.equivalents


class CssGridItem:
    def __init__(self):
        self.parameters = {
            'grid-column-start': '<number> | <name> | span <number> | span <name> | auto',
            'grid-column-end': '<number> | <name> | span <number> | span <name> | auto',
            'grid-row-start': '<number> | <name> | span <number> | span <name> | auto',
            'grid-row-end': '<number> | <name> | span <number> | span <name> | auto',
            'grid-area': '<name> | <row-start> / <column-start> / <row-end> / <column-end>',
            'justify-self': 'start | end | center | stretch',
            'align-self': 'start | end | center | stretch',
        }

        self.synonims = {}

        self.equivalents = {
            'grid-column': '<grid-column-start> / <grid-column-end>',
            'grid-column': '<grid-row-start> / <grid-row-end>',
            'place-self': '<align-self> / <justify-self>'
        }

    def attribs(self):
        return self.parameters | self.synonims | self.equivalents


class CssGrid:
    def __init__(self, **grid):
        self.row_names, self.col_names = {}, {}
        self.row_tracks, self.col_tracks = {}, {}
        self.areas = {}
        self.nrows = self.ncols = 0
        self.grid_auto_flow = 'row'
        self.taken = set()
        self.next = 0

        self.parsers = {
            'grid-template-areas': self.grid_template_areas,
            'grid-template-rows': self.grid_template_pattern,
            'grid-template-columns': self.grid_template_pattern,
            'grid-column-start': self.grid_child,
            'grid-column-end': self.grid_child,
            'grid-row-start': self.grid_child,
            'grid-row-end': self.grid_child,
            'grid-area': self.grid_area,
            'grid-column': self.grid_item,
            'grid-row': self.grid_item,
        }
        self.parse_template(grid)
        pass

    def get_n_position(self, x, y):
        if self.grid_auto_flow == 'row':
            return self.ncols * x + y
        if self.grid_auto_flow == 'column':
            return self.nrows * y + x

    def get_xy_position(self, nrows=1, ncols=1):
        if len(self.taken) < self.nrows * self.ncols:
            taken = self.taken
            if 'dense' in self.grid_auto_flow:
                availables = set(x for x in range(self.nrows * self.ncols)) - taken
                n = min(availables)
            else:
                n = self.next
                while True:
                    req_pos: set = self.enumerate_area_items(n=n, nrows=nrows, ncols=ncols)
                    if req_pos.isdisjoint(taken):
                        break
                    n += 1
                    if n >= self.nrows * self.ncols:
                        raise Exception("Can't find a explicit grid position for item")
                self.next = n
        else:
            assert False, 'Se excede grid explícita'

        if self.grid_auto_flow == 'row':
            x = n // self.ncols
            y = n % self.ncols
        elif self.grid_auto_flow == 'column':
            y = n // self.nrows
            x = n % self.nrows
        return {'grid-row-start': x, 'grid-column-start': y}

    def parse_template(self, grid):
        self.row_names, self.col_names = {}, {}
        self.row_tracks, self.col_tracks = {}, {}
        self.areas = {}
        self.nrows = self.ncols = 0
        self.grid_auto_flow = 'row'

        dmy = [
            (key, fnc(param))
            for parser, fnc in self.parsers.items()
            for key, param in grid.items() if key == parser
        ]
        for key, answ in dmy:
            if key.endswith('columns'):
                dcol, self.col_tracks = answ
                self.col_names.update(dcol)
            elif key.endswith('rows'):
                drow, self.row_tracks = answ
                self.row_names.update(drow)
            elif key.endswith('areas'):
                self.areas, drow, dcol = answ
                self.row_names.update(drow)
                self.col_names.update(dcol)
        self.nrows = len(self.row_tracks)
        self.ncols = len(self.col_tracks)

    def parse_child(self, item: dict):
        grid_params = self.get_xy_position()
        to_process = list(item.items())
        while to_process:
            key, template = to_process.pop()
            fnc = self.parsers[key]
            case, val = fnc(template)
            _, track, *suffix = key.split('-')
            if track == 'area':
                # grid_params.update(answ)
                if case == 'area_name':
                    grid_params = self.areas[val]
                elif case == 'area_coord':
                    to_process.extend(val)
            elif not suffix:
                if case == 'track-item':
                    keys = [f'grid-{track}-start', f'grid-{track}-end']
                    to_process.extend((key, x) for key, x in zip(keys, val) if x)
            else:
                if case == 'auto':
                    pass
                elif case == 'item':
                    grid_params[key] = val
                elif case == 'span':
                    grid_params[f'grid-{track}-span'] = val
                elif case == 'span_name':
                    val = self.col_names[val]
                    grid_params[f'grid-{track}-span'] = val
                    pass
                elif case == 'item_name':
                    track_names = self.col_names if track == 'column' else self.row_names
                    val = track_names[val]
                    grid_params[key] = val
                    pass
        grid_params = self.norm_grid_params(grid_params)
        self.update_taken(grid_params)
        return grid_params

    def norm_grid_params(self, grid_params: dict):
        keys = {'grid-column-start', 'grid-column-span', 'grid-row-start', 'grid-row-span'}
        to_norm = grid_params.keys() - keys
        for key in to_norm:
            assert key.endswith('end')
            nkey = key.replace('-end', '')
            grid_params[f'{nkey}-span'] = grid_params.pop(key) - grid_params[f'{nkey}-start']
        return grid_params

    def enumerate_area_items(self, n=None, row=None, col=None, nrows=1, ncols=1):
        if n is None:
            n = self.get_n_position(row, col)
        if 'row' in self.grid_auto_flow:
            return set(n + y + x * self.ncols for x in range(nrows) for y in range(ncols))
        return set(n + x + y * self.nrows for y in range(ncols) for x in range(nrows))

    def update_taken(self, grid_params):
        row, nrows = grid_params['grid-row-start'], grid_params.get('grid-row-span', 1)
        col, ncols = grid_params['grid-column-start'], grid_params.get('grid-column-span', 1)
        taken = self.enumerate_area_items(row=row, col=col, nrows=nrows, ncols=ncols)
        self.taken.update(taken)

    @staticmethod
    def grid_template_pattern(template):
        # Reemplazamos las macros dentro del template
        wtemplate = re.sub(r'repeat\(([0-9]+?),(.+?)\)', lambda m: int(m.group(1)) * m.group(2), template)
        # Agregamos nombre de inicio y fin de columnas
        wtemplate = f'[@]{wtemplate}[@]'
        split_pattern = re.compile(r'\s*(?:\[.+?\])+\s*|\s+?')
        line_names = collections.defaultdict(list)
        line_grid_names = [
            list(zip(lname.strip('[ ]').split(']['), (lname.count('][') + 1) * [k]))
            for k, lname in enumerate(split_pattern.findall(wtemplate))
            if lname.strip()
        ]
        [line_names[key].append(val) for key, val in itertools.chain(*line_grid_names)]
        line_names.pop('@')
        line_names = {key: (value[0] if len(value) == 1 else tuple(value)) for key, value in line_names.items()}
        track_sizes = split_pattern.split(wtemplate)[1:-1]
        return line_names, track_sizes

    @staticmethod
    def grid_template_areas(template_area):
        pareas = collections.defaultdict(list)
        [
            pareas[key].append((x, y))
            for x, row in enumerate(template_area.split('\n'))
            for y, key in
            enumerate(row.strip().split(' '))
        ]
        row_names, col_names = {}, {}
        keys = ['grid-row-start', 'grid-column-start', 'grid-row-end', 'grid-column-end']
        for key in pareas:
            if '.' in key:
                continue
            rows, cols = zip(*pareas[key])
            row_names.update({f'{key}-start': min(rows), f'{key}-end': max(rows) + 1})
            col_names.update({f'{key}-start': min(cols), f'{key}-end': max(cols) + 1})
            vals = [min(rows) + 1, min(cols) + 1, max(rows) + 2, max(cols) + 2]
            pareas[key] = dict(zip(keys, vals))
        return pareas, row_names, col_names

    @staticmethod
    def grid_child(template: str):
        if template == 'auto':
            return 'auto', True
        bSpan = 'span' in template
        if bSpan:
            template = template.split(' ', 1)[-1]
        if template.isdigit():
            key = 'span' if bSpan else 'item'
            val = int(template) - (0 if bSpan else 1)
            return key, val
        if template.isascii():
            key = 'span_name' if bSpan else 'item_name'
            return key, template

    @staticmethod
    def grid_area(template):
        isAreaName = '/' not in template
        if isAreaName:
            return 'area_name', template
        keys = ['grid-row-start', 'grid-column-start', 'grid-row-end', 'grid-column-end']
        vals = [x.strip() for x in template.split('/')]
        return 'area_coord', zip(keys, vals)

    @staticmethod
    def grid_item(template: str):
        if '/' not in template:
            if template.isdigit():
                n = int(template)
                template = f'{n} / {n + 1}'
            elif 'span' not in template:
                template = f'{template} / span 1'
            else:
                template = f' / {template}'
        vals = [x.strip() for x in template.split('/')]
        return 'track-item', vals



def main():
    grid = {
        'grid-template-columns': '[first] 40px [line2] 50px [line3] auto [col4-start] 50px [five] 40px [end]',
        'grid-template-rows': '[row1-start] 25% [row1-end] 100px [third-line] auto [last-line]',
        'grid-template-areas': 'header header header header\nmain main . sidebar\nfooter footer footer footer'
    }
    container = CssGrid(**grid)

    grid = {
        'grid-template-columns': '[first] 25px 25px 25px [col4-start] 25px [five] 25px [end]',
        'grid-template-rows': '[row1-start] 25px [row1-end] 25px [third-line] 25px [last-line]',
    }

    # container.parse_template(grid)
    item = []
    item.append({
        'grid-column-start': '2',
        'grid-column-end': 'five',
        'grid-row-start': 'row1-start',
        'grid-row-end': '3',
    })
    # answ = container.parse_child(item[-1])
    item.append({
        'grid-column-start': '1',
        'grid-column-end': 'span col4-start',
        'grid-row-start': '2',
        'grid-row-end': 'span 2',
    })
    # answ = container.parse_child(item[-1])
    item.append({
        'grid-area': '1 / col4-start / last-line / 6',
    })
    # answ = container.parse_child(item[-1])

    item.append({
        'grid-column': '3 / span 2',
        'grid-row': ' third-line / 4',
    })
    # answ = container.parse_child(item[-1])

    grid = {
        'grid-template-columns': '60px 60px 60px 60px 60px',
        'grid-template-rows': '30px 30px',
    }

    container.parse_template(grid)

    items = [
        {'grid-column': '1', 'grid-row': '1 / 3'},      # item-a
        {},                                              # item-b
        {},                                              # item-c
        {},                                              # item-d
        {'grid-column': '5', 'grid-row': '1 / 3'},      # item-e
    ]
    dmy1 = [container.parse_child(x) for x in items]

    container.grid_auto_flow = 'column'
    container.taken = set()
    container.next = 0
    dmy2 = [container.parse_child(x) for x in items]
    pass

if __name__ == '__main__':
    main()
