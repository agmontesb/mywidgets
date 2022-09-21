import bisect
import collections
import itertools
import re
import tkinter

import userinterface

DEBUG = True


class CssGrid:

    manager = 'grid'

    def __init__(self, **grid):
        self.row_names, self.col_names = {}, {}
        self.row_tracks, self.column_tracks = [], []
        self.areas = {}
        self.nrows = self.ncolumns = 0
        self.row_gap = self.column_gap = 0
        self.align_items = self.justify_items = 'center'
        self.align_content = self.justify_content = 'start'
        self.grid_auto_columns = self.grid_auto_rows = '0px'
        self.grid_auto_flow = 'row'
        self.rows_responsive = self.columns_responsive = None
        self.taken = set()
        self.next = 0
        self.slaves = []
        self.slaves_order = []
        self.memory = (0, 0)

        self.parse_template(grid)
        pass

    def get_n_from_xy(self, x, y):
        if 'row' in self.grid_auto_flow:
            return self.ncolumns * x + y
        return self.nrows * y + x

    def get_xy_from_n(self, n):
        if 'row' in self.grid_auto_flow:
            x = n // self.ncolumns
            y = n % self.ncolumns
        else:
            y = n // self.nrows
            x = n % self.nrows
        return x, y

    def norm_n_pos(self, x, y, nrows, ncols, slaves=None):
        ntracks = self.ncolumns if 'row' in self.grid_auto_flow else self.nrows

        deltax = deltay = 0
        if x >= 0 and (x + nrows - 1 >= self.nrows):
            deltax = x + nrows - self.nrows
            self.row_tracks += deltax * [self.grid_auto_rows]
        elif x < 0:
            deltax = x
            self.row_tracks = (-deltax) * [self.grid_auto_rows] + self.row_tracks

        if y >= 0 and (y + ncols - 1 >= self.ncolumns):
            deltay = y + ncols - self.ncolumns
            self.column_tracks += deltay * [self.grid_auto_columns]
        elif y < 0:
            deltay = y
            self.column_tracks = (-deltay) * [self.grid_auto_columns] + self.column_tracks

        deltax, deltay = (deltay, deltax) if 'row' in self.grid_auto_flow else (deltax, deltay)
        deltay = min(deltay, 0)
        if self.taken:
            cases = (deltax, 0) if deltax < 0 else (0, deltax)
            cases += (deltay * (ntracks + abs(deltax)),)
            fncs = (
                    lambda x, inc: x + inc * (x // ntracks + 1),    # deltax < 0
                    lambda x, inc: x + inc * (x // ntracks),        # deltax > 0
                    lambda x, inc: x + inc                          # deltay > 0
                )
            for k, delta in enumerate(cases):
                if not delta:
                    continue
                fnc = fncs[k]
                delta = abs(delta)
                self.taken = {fnc(x, delta) for x in self.taken}
                [
                    x.__setitem__('n-pos', fnc(x['n-pos'], delta))
                    for _, x in slaves
                ]

        self.nrows = len(self.row_tracks)
        self.ncolumns = len(self.column_tracks)

        x -= deltay
        y -= min(deltax, 0)

        return self.get_n_from_xy(x, y)

    def get_insertion_position(self, x, y, nrows=1, ncols=1):
        taken = self.taken
        isRowAutoFlow = 'row' in self.grid_auto_flow
        isDense = 'dense' in self.grid_auto_flow
        priority = self.positioning_priority(x, y)
        if priority == 1:
            pass
        elif priority == 4:
            # items sin ninguna restricción en su posicionamiento
            n = None
            if len(taken) < self.nrows * self.ncolumns:
                taken = [-1, *sorted(self.taken), self.nrows * self.ncolumns]
                availables = itertools.chain(
                    *[range(x + 1, y) for x, y in zip(taken, taken[1:]) if y - x - 1 > 0]
                )
                n_zero = -1 if isDense else self.next
                it = itertools.dropwhile(lambda x, a=n_zero: x < a, availables)
                while True:
                    try:
                        n = next(it)
                        # Se calcula el número de posiciones para posicionar el item
                        req_pos = self.enumerate_area_items(n=n, nrows=nrows, ncols=ncols)
                        if len(req_pos) == nrows * ncols and req_pos.isdisjoint(self.taken):
                            x, y = self.get_xy_from_n(n)
                            break
                    except StopIteration:
                        n = None
                        break
            if n is None:
                n = self.ncolumns * self.nrows
                x, y = self.get_xy_from_n(n)
            self.next = n
        else:
            if priority == 2:
                locked_coord = x if isRowAutoFlow else y
            else:   # priority == 3
                locked_coord = y if isRowAutoFlow else x
            # Item con restricción de posicionamiento sobre una row o col específica.
            ntracks = self.ncolumns if isRowAutoFlow else self.nrows
            nother = self.nrows if isRowAutoFlow else self.ncolumns
            if priority == 2 and locked_coord >= nother:
                # Red implícita. Item a colocar en un grid-auto-flow ubicado en la red implícita.
                x, y = (locked_coord, 0) if isRowAutoFlow else (0, locked_coord)
            elif priority == 3 and locked_coord >= ntracks:
                # Red implícita. Item a colocar en un no grid-auto-flow ubicado en la red implícita.
                x, y = (0, locked_coord) if isRowAutoFlow else (locked_coord, 0)
            else:
                # Red explícita, colocar item sobre grid-auto-flow (priority==2)
                # o sobre no grid-auto-flow (priority==3)
                if priority == 2:
                    linf = locked_coord * ntracks
                    lsup = linf + ntracks
                    step = 1
                else:
                    linf = locked_coord
                    lsup = linf + ntracks * nother
                    step = ntracks
                nviables = set(range(linf, lsup, step))
                nreal = nviables - taken
                if not isDense:
                    linf = max(taken & nviables) if taken & nviables else -1
                    nreal = {x for x in nreal if x > linf}
                for n in sorted(nreal):
                    req_pos = self.enumerate_area_items(n=n, nrows=nrows, ncols=ncols)
                    if req_pos.isdisjoint(self.taken):
                        x, y = self.get_xy_from_n(n)
                        break
                else:
                    # No se pudo ubicar espacio disponible en la red explícita, se coloca
                    # en la periferia de la red implícita
                    x0, y0 = self.get_xy_from_n(lsup - step)
                    dx, dy = (0, 1) if priority == 2 else (1, 0)
                    x, y = x0 + dx, y0 + dy
        return x, y

    def init_grid_state(self):
        self.row_names, self.col_names = {}, {}
        self.row_tracks, self.column_tracks = [], []
        self.areas = {}
        self.nrows = self.ncolumns = 0
        self.row_gap = self.column_gap = 0
        self.align_items = self.justify_items = 'stretch'
        self.align_content = self.justify_content = 'start'
        self.grid_auto_columns = self.grid_auto_rows = '0px'
        self.grid_auto_flow = 'row'
        self.rows_responsive = self.columns_responsive = None
        self.taken = set()
        self.next = 0
        self.slaves = []
        self.slaves_order = []
        self.memory = (0, 0)

    def parse_template(self, grid):
        self.init_grid_state()
        to_process: list = [(key, grid[key]) for key in grid.keys() & self.container_parsers.keys()]
        while to_process:
            attr_key, template = to_process.pop()
            acase, answ = self.parse_attr(attr_key, template.strip())
            if acase == 'to_process':
                to_process.extend(answ)
                continue
            match attr_key:
                case 'grid-template-rows':
                    drow, self.row_tracks, responsive = answ
                    self.row_names.update(drow)
                    if responsive:
                        responsive, data = responsive
                        if responsive in ('auto-fit', 'auto-fill'):
                            self.grid_auto_rows = data
                    self.rows_responsive = responsive
                case 'grid-template-columns':
                    dcol, self.column_tracks, responsive = answ
                    self.col_names.update(dcol)
                    if responsive:
                        responsive, data = responsive
                        if responsive in ('auto-fit', 'auto-fill'):
                            self.grid_auto_columns = data
                    self.columns_responsive = responsive
                case 'grid-template-areas':
                    self.areas, drow, dcol = answ
                    self.row_names.update(drow)
                    self.col_names.update(dcol)
                case 'column-gap' | 'grid-column-gap' | 'row-gap' | 'grid-row-gap':
                    if not isinstance(answ, list):
                        answ = int(answ.strip(' px'))
                    else:
                        answ = list(map(lambda x: int(x.strip(' px')), answ))
                    if 'column' in attr_key:
                        self.column_gap = answ
                    else:
                        self.row_gap = answ
                case 'gap' | 'grid-gap':
                    self.row_gap, self.column_gap = map(lambda x: int(x.strip(' px')), answ)
                case 'justify-items':
                    self.justify_items = answ
                case 'align-items':
                    self.align_items = answ
                case 'place-items':
                    self.align_items, self.justify_items = answ
                case 'justify-content':
                    self.justify_content = answ
                case 'align-content':
                    self.align_content = answ
                case 'place-content':
                    self.align_content, self.justify_content = answ
                case 'grid-auto-columns':
                    self.grid_auto_columns = answ
                case 'grid-auto-rows':
                    self.grid_auto_rows = template.strip()
                case 'grid-auto-flow':
                    self.grid_auto_flow = template.strip()

        self.nrows = self.nrows_explicit = len(self.row_tracks)
        self.ncolumns = self.ncolumns_explicit = len(self.column_tracks)

    def tkinter_master_params(self, row_span, col_span):
        answ = {}
        track_names = ('row', 'column')
        for track_name in track_names:
            tracks = getattr(self, f'{track_name}_tracks')
            ctracks = collections.defaultdict(list)
            [ctracks[key].append(k) for k, key in enumerate(tracks)]

            method = f'{track_name}configure'
            params_base = []
            minmax = {}
            tot_min_size = 0
            free_tracks = 0
            # Ajuste de minsize y weight
            to_process = list(ctracks.items())
            while to_process:
                key, track_ids = to_process.pop()
                if key == 'auto':
                    key = '1fr'
                if key.endswith('px'):
                    min_size = int(key[:-2])
                    params_base.append((track_ids, dict(minsize=min_size, weight=0)))
                    tot_min_size += min_size
                elif key.endswith('fr') or key.endswith('%'):
                    key = key.rstrip('fr%')
                    params_base.append((track_ids, dict(weight=int(key))))
                    free_tracks += 1
                elif key.startswith('minmax(') and key.endswith(')'):
                    min_size, max_size = [x.strip() for x in key[7:-1].split(',')]
                    min_size = int(min_size.strip('px'))
                    if max_size.endswith('fr') or max_size.endswith('%'):
                        max_size = int(max_size.strip('%').strip('fr'))
                        tot_min_size += min_size
                        free_tracks += 1
                    else:
                        minmax[tuple(track_ids)] = (min_size, int(max_size.strip('px')))
                        continue
                    params_base.append((track_ids, dict(minsize=min_size, weight=max_size)))
                else:
                    params_base.append((track_ids, dict(weight=10)))
                    free_tracks += 1

            if minmax:
                setattr(self, f'{track_name}s_responsive', 'minmax')
                conf = []
                delta_size = 0
                params_minmax = []
                max_items = []
                for track_ids, (tmin, tmax) in minmax.items():
                    params_minmax.append((track_ids, dict(minsize=tmin, weight=1)))
                    delta_size += tmin * len(track_ids)
                    max_items.append((tmax, track_ids, tmin))
                conf.append((tot_min_size + delta_size, params_base + params_minmax))
                max_items.sort()

                total_frs = free_tracks + sum([len(x[1]) for x in max_items])
                for k, (tmax, track_ids, tmin) in enumerate(max_items):
                    params_minmax = []
                    delta_size = free_tracks * tmax
                    for tmax, track_ids, _ in max_items[:k + 1]:
                        delta_size += tmax * len(track_ids)
                        params_minmax.append((track_ids, dict(minsize=tmax, weight=0)))
                    for _, track_ids, tmin in max_items[k + 1:]:
                        delta_size += tmax * len(track_ids)
                        params_minmax.append((track_ids, dict(minsize=tmin, weight=1)))
                    conf.append((min_size + delta_size, params_base + params_minmax))
                    total_frs -= len(track_ids)
                size_lim, params = zip(*conf)
                n = bisect.bisect_left(size_lim, (row_span, col_span)[track_name == 'column'])
                n = max(0, n - 1)
                answ[method] = params[n]
            else:
                answ[method] = params_base

        pos = ['start', 'end', 'center', 'stretch']
        row_place, column_place = self.justify_content, self.align_content
        if row_place == column_place == 'center':
            sticky = ''
        elif row_place in pos and column_place in pos:
            sticky = self.get_equiv_placement(row_place, column_place)
        elif row_place in pos and column_place not in pos:
            sticky = self.get_equiv_placement(row_place, 'center')
        elif row_place not in pos and column_place in pos:
            sticky = self.get_equiv_placement('center', column_place)
        elif row_place not in pos and column_place not in pos:
            sticky = ''
        answ['grid_anchor'] = [(sticky or 'center', {})]
        return answ

    def config_master(self, master):
        if (self.columns_responsive, self.rows_responsive) == (None, None):
            self._config_master(master)
        else:
            master.bind("<Configure>", lambda event, name=str(master): self.resize(event, name))

    def resize(self, event, name=None):
        if str(event.widget) != name:
            return
        master = event.widget

        # Se resetea la grilla anterior para que se inicie siempre como en el principio
        ncolumns, nrows = master.grid_size()
        if ncolumns:
            master.columnconfigure(list(range(ncolumns)), minsize=0, weight=0)
        if nrows:
            master.rowconfigure(list(range(nrows)), minsize=0, weight=0)

        w, h = event.width, event.height
        bflag = False
        isRowAutoFlow = self.grid_auto_flow == 'row'
        if self.rows_responsive in ('auto-fit', 'auto-fill'):
            if m := re.match(r'minmax\((.+?),.+?\)', self.grid_auto_rows):
                min_size = m.group(1)
            else:
                min_size = self.grid_auto_rows
            base = int(min_size.strip(' px')) + self.column_gap
            nrows = h // base
            if self.rows_responsive == 'auto-fit':
                if isRowAutoFlow:
                    nrows = self.slaves // self.ncolumns + (1 if self.slaves % self.ncolumns else 0)
                else:
                    nrows = min(nrows, len(self.slaves))
            self.nrows = nrows
            self.row_tracks = nrows * [self.grid_auto_rows]
            bflag = True

        if self.columns_responsive in ('auto-fit', 'auto-fill'):
            if m := re.match(r'minmax\((.+?),.+?\)', self.grid_auto_columns):
                min_size = m.group(1)
            else:
                min_size = self.grid_auto_columns
            base = int(min_size.strip(' px')) + self.row_gap
            ncols = w // base
            if self.columns_responsive == 'auto-fit':
                if not isRowAutoFlow:
                    ncols = self.slaves // self.nrows + (1 if self.slaves % self.nrows else 0)
                else:
                    ncols = min(ncols, len(self.slaves))
            self.ncolumns = ncols
            self.column_tracks = ncols * [self.grid_auto_columns]
            bflag = True

        # flag_minmax = 'minmax' in (self.columns_responsive, self.rows_responsive)
        # if bflag or flag_minmax:

        # Se elimina la grilla anterior si la hubiera.
        [x.destroy() for x in master.grid_slaves() if x.winfo_name()[:4] in ('row_', 'col_')]
        # Se elimina el mapeo de widgets asociados al grid container
        [
            wdg.grid_forget()
            for wdg in master.grid_slaves()
        ]
        # Se procede a mapear nuevamente los widgets en el grid container
        self._config_master(master, w, h)
        self.memory = w, h

    def _config_master(self, master, width=0, height=0):
        equiv = [
            ('grid-column-start', 'column'),
            ('grid-row-start', 'row'),
            ('grid-column-span', 'columnspan'),
            ('grid-row-span', 'rowspan'),
            ('sticky-self', 'sticky'),
            ('grid-row-gap', 'pady'),
            ('grid-column-gap', 'padx'),
            ('in', 'in_'),
        ]
        order = []
        self.taken = set()
        self.next = 0

        for name, item_attrs in self.get_process_item_attribs():
            wdg = master.nametowidget(name)
            if zindex := item_attrs.pop('z-index', None):
                order.append((zindex, name))
            # Se traduce la n-pos a su posición (x, y) de acuerdo al dato final de nrows y ncolumns
            # x, y = self.get_xy_from_n(item_attrs.pop('n-pos'))
            # item_attrs.update({'grid-row-start': x, 'grid-column-start': y})

            # Se transforman los attributos a sus equivalentes en tkinter
            item_attrs = {key: item_attrs.pop(ckey) for ckey, key in equiv if item_attrs.get(ckey, None) is not None}
            for key in {'row', 'column'}:
                item_attrs[key] = 2 * item_attrs[key] + 1
            for key in {'rowspan', 'columnspan'}:
                item_attrs[key] = 2 * item_attrs[key] - 1
            # Se mapea el widget en el master
            wdg.grid(**item_attrs)

        # Se ajusta el stacking order si así se requiriera
        if order:
            order.sort()
            # en este punto se tiene en wdg el widget con el stacking order más alto ya que fue
            # el último en ser creado.
            for zindex, name in order:
                lstwdg, wdg = wdg, master.nametowidget(name)
                wdg.lift(lstwdg)

        nrows, ncolumns = 2 * self.nrows + 1, 2 * self.ncolumns + 1
        h, w = self.row_gap, self.column_gap

        row_ids, col_ids = range(0, nrows, 2)[1:-1], range(0, ncolumns, 2)[1:-1]
        row_place, column_place = self.justify_content, self.align_content
        gaps = {}

        width -= (self.nrows - 1) * h
        height -= (self.ncolumns - 1) * w

        track_params = self.tkinter_master_params(height, width)
        static_rows = all(x.get('weight', 0) == 0 for _, x in track_params.get('rowconfigure', []))
        static_columns = all(x.get('weight', 0) == 0 for _, x in track_params.get('columnconfigure', []))

        cases = ['space-around', 'space-between', 'space-evenly']
        it = [
            ('rows', column_place, static_rows, h),
            ('columns', row_place, static_columns, w),
        ]
        for track_name, track_place, static_track, size in it:
            ntracks = 2 * getattr(self, f'n{track_name}') + 1
            track_ids = range(0, ntracks, 2)[1:-1]
            size = (h, w)[track_name == 'columns']
            key = f'{track_name[:-1]}configure'
            if track_place in cases and static_track:
                data = []
                n = cases.index(column_place)
                data.append((list(track_ids), dict(minsize=size, weight=2)))
                weight = (1, 0, 2)[n]
                data.append(([0, ntracks - 1], dict(minsize=size, weight=weight)))
                gaps[key] = data
            else:
                gaps[key] = [(list(track_ids), dict(minsize=size, weight=0))]

        if DEBUG:
            for row in range(0, nrows, 2):
                frm = tkinter.Frame(master, name=f'row_{row // 2 + 1}', height=1, width=1, bg='black')
                frm.grid(row=row, column=0, columnspan=ncolumns, sticky='ew')
                frm.lower()  # Con esto se manda estos al fondo del stacking order
            for col in range(0, ncolumns, 2):
                frm = tkinter.Frame(master, name=f'col_{col // 2 + 1}', height=1, width=1, bg='black')
                frm.grid(row=0, column=col, rowspan=nrows, sticky='ns')
                frm.lower()  # Con esto se manda estos al fondo del stacking order

        tkinter_params = {}
        for key in list(track_params.keys()):
            if key not in ('rowconfigure', 'columnconfigure'):
                tkinter_params[key] = track_params.pop(key)
                continue
            track_data = track_params.pop(key)
            data = gaps.pop(key, [])
            for track_ids, conf in track_data:
                track_ids = [2 * x + 1 for x in track_ids]
                data.append((track_ids, conf))
            tkinter_params[key] = data

        for method_name, params in tkinter_params.items():
            method = getattr(master, method_name)
            for arg, kwargs in params:
                method(arg, **kwargs)
        pass

    def get_process_item_attribs(self):
        # item = {key: item_attribs[key] for key in (item_attribs.keys() & self.item_parsers.keys())}

        slaves = []
        ordered_slaves = sorted(zip(self.slaves_order, self.slaves), key=lambda x: x[0])
        for priority, (name, item_attrs) in ordered_slaves:
            # Se inicializan los parámetros del child con la proxima posición y el
            # 'justify-self' y 'align-self' con los generales definidos a nivel del container.
            grid_params = {'justify-self': self.justify_items, 'align-self': self.align_items}
            to_process = list(item_attrs.items())
            while to_process:
                key, template = to_process.pop()
                case, val = self.parse_attr(key, template.strip())
                if case == 'to_store':
                    grid_params[key] = val
                    continue
                if case == 'to_process':
                    to_process.extend(val)
                    continue
                _, track, *suffix = key.split('-')
                suffix = '' if not suffix else suffix[0]
                if track == 'area':
                    grid_params.update(self.areas[val])
                elif track == 'self':
                    grid_params[key] = val if val != 'auto' else 'center'
                elif case == 'auto':
                    # default_pos = self.get_xy_from_n(self.next)
                    # grid_params[key] = default_pos[track == 'column']
                    pass
                elif case == 'item':
                    if val < 0:
                        # Referencia a línea negativa
                        assert suffix
                        base = 1 + (self.nrows_explicit if suffix == 'rows' else self.ncolumns_explicit)
                        val = (base + val) % base
                    grid_params[key] = val
                elif case == 'item_name':
                    if val == 'auto':
                        continue
                    track_names = self.col_names if track == 'column' else self.row_names
                    if val in self.areas:
                        val = f'{val}-{suffix}'
                    try:
                        line_name, pos = val.rsplit(' ', 1)
                        val = track_names[line_name][int(pos) - 1]
                    except ValueError:
                        val = track_names[val]
                        if isinstance(val, tuple):
                            val = val[0]
                    grid_params[key] = val
                    pass
                elif case == 'span':
                    if suffix == 'end':
                        grid_params[f'grid-{track}-span'] = val
                    else:
                        grid_params[key] = f'span {val}'
                elif case == 'span_name':
                    val = self.col_names[val]
                    grid_params[f'grid-{track}-span'] = val
                    pass
            grid_params = self.norm_grid_params(priority, grid_params)
            nrows, ncols = grid_params.get('grid-row-span', 1), grid_params.get('grid-column-span', 1)
            x, y = grid_params['grid-row-start'], grid_params['grid-column-start']
            grid_params['n-pos'] = self.norm_n_pos(x, y, nrows, ncols, slaves=slaves)

            self.update_taken(grid_params)
            slaves.append((name, grid_params))
        return slaves

    def register_item(self, widget, item_attribs: dict) -> int:
        '''
        Almacena los atributos del item de forma canónica y le asigna una prioridad para su procesamiento
        '''
        item_attribs, _ = self.filter_item_attribs(item_attribs)
        # Por default se tiene que cada item tiene al menos un span de 1
        base_attribs = self.canonalize_attribs(item_attribs)
        base_attribs = {'grid-column-end': 'span 1', 'grid-row-end': 'span 1', **base_attribs}

        x, y = base_attribs.get('grid-row-start', None), base_attribs.get('grid-column-start')
        x = None if x == 'auto' else x
        y = None if y == 'auto' else y
        k = self.positioning_priority(x, y)
        self.slaves.append((str(widget), base_attribs))
        self.slaves_order.append(k)
        return k

    def positioning_priority(self, x: int | None, y: int | None) -> int:
        xIsNone, yIsNone = x is None, y is None
        if xIsNone and yIsNone:
            #  automatic grid position in both axes
            return 4
        if not (xIsNone or yIsNone):
            # auto-positioned
            return 1
        isRowAutoFlow = 'row' in self.grid_auto_flow
        if (isRowAutoFlow and yIsNone) or (not isRowAutoFlow and xIsNone):
            #  items LOCKED to the 'grid-auto-flow' track
            return 2
        # if (not isRowAutoFlow and x) or (isRowAutoFlow and y):
        # items NOT LOCKED to the 'grid-auto-flow' track
        return 3

    def norm_grid_params(self, priority: int, grid_params: dict) -> dict:
        keys = {'grid-column-start', 'grid-row-start'}
        to_norm = grid_params.keys() & keys
        for key in to_norm:
            if isinstance(grid_params[key], int):
                continue
            ckey = key.replace('-start', '-end')
            assert ckey in grid_params and isinstance(grid_params[ckey], int)
            val = int(grid_params[key][5:])
            grid_params[key] = grid_params[ckey] - val

        keys = {'grid-column-end', 'grid-row-end'}
        to_norm = grid_params.keys() & keys
        for key in to_norm:
            # assert key.endswith('end')
            nkey = key.replace('-end', '')
            grid_params[f'{nkey}-span'] = grid_params.pop(key) - grid_params[f'{nkey}-start']

        x, y = grid_params.get('grid-row-start', None), grid_params.get('grid-column-start', None)
        nrows, ncols = grid_params.get('grid-row-span', 1), grid_params.get('grid-column-span', 1)
        row_offset = col_offset = 0
        if x and x < 0:
            row_offset = x
            nrows = nrows + row_offset
            x = 0
            if not nrows:
                y = y or 0
        if y and y < 0:
            col_offset = y
            ncols = ncols + col_offset
            y = 0
            if not ncols:
                x = x or 0
        x, y = self.get_insertion_position(x, y, nrows=nrows, ncols=ncols)
        grid_params['grid-row-start'], grid_params['grid-column-start'] = x + row_offset, y + col_offset

        row_place, column_place = grid_params.pop('justify-self'), grid_params.pop('align-self')
        grid_params['sticky-self'] = self.get_equiv_placement(row_place, column_place)
        return grid_params

    def get_equiv_placement(self, row_place, column_place):
        placement_val = ['start', 'end', 'center', 'stretch']
        sticky = ''
        try:
            k = placement_val.index(column_place)
            sticky += ['n', 's', '', 'ns'][k]
        except:
            pass
        try:
            k = placement_val.index(row_place)
            sticky += ['w', 'e', '', 'we'][k]
        except:
            pass
        return sticky

    def enumerate_area_items(self, n=None, row=None, col=None, nrows=1, ncols=1) -> set:
        if n is None:
            n = self.get_n_from_xy(row, col)
        if 'row' in self.grid_auto_flow:
            y_zero = n % self.ncolumns
            ncols = min(self.ncolumns - y_zero, ncols)
            return set(n + y + x * self.ncolumns for x in range(nrows) for y in range(ncols))
        x_zero = n % self.nrows
        nrows = min(self.nrows - x_zero, nrows)
        return set(n + x + y * self.nrows for y in range(ncols) for x in range(nrows))

    def update_taken(self, grid_params):
        n = grid_params['n-pos']
        nrows = grid_params.get('grid-row-span', 1)
        ncols = grid_params.get('grid-column-span', 1)
        taken = self.enumerate_area_items(n=n, nrows=nrows, ncols=ncols)
        self.taken.update(taken)

    @classmethod
    def canonalize_attribs(cls, attribs):
        '''
        Transforma todos los shorcuts en attrs a su equivalente en attributos básicos
        '''
        to_process = list(attribs.items())
        to_verify = []
        while to_process:
            attr_key, template = to_process.pop()
            acase, answ = cls.parse_attr(attr_key, template)
            if acase != 'to_process':
                to_verify.append((attr_key, template.strip()))
            else:
                to_process.extend(answ)
        return dict(to_verify)


    @staticmethod
    def grid_template_pattern(template):
        if template != 'none':
            # Reemplazamos las macros dentro del template
            wtemplate = template
            responsive = None
            if m := re.search(r'repeat\(([^,]+?),(.+)\)(?=\s|$)', template):
                linf, lsup = m.span()
                match m.groups():
                    case rep, what if rep.isdigit():
                        repeated = re.sub(r'\]\s*?\[', ' ', int(rep) * what)
                        wtemplate = template[:linf] + repeated.strip() + template[lsup:]
                    case rep, what if rep in ('auto-fit', 'auto-fill'):
                        responsive = (rep, what.strip())
                        wtemplate = ''      # acá es posible definir columnas iniciales, para despúes
            elif m := re.search(r'minmax\(\d+px,\s*\d+px\)', template):
                responsive = ('minmax', m.group())
                pass

            # Agregamos nombre de inicio y fin de columnas
            wtemplate = f'[@]{wtemplate}[@]'
            wtemplate = wtemplate.replace('][', ' ')
            split_pattern = re.compile(r'\s*(?:\[.+?\])+\s*|(?<!,)\s+?')
            line_names = collections.defaultdict(list)
            line_grid_names = [
                list(zip(lname.strip('[ ]').split(' '), (lname.count(' ') + 1) * [k]))
                for k, lname in enumerate(split_pattern.findall(wtemplate))
                if lname.strip()
            ]
            [line_names[key].append(val) for key, val in itertools.chain(*line_grid_names)]
            line_names.pop('@')
            line_names = {key: (value[0] if len(value) == 1 else tuple(value)) for key, value in line_names.items()}
            track_sizes = split_pattern.split(wtemplate)[1:-1]
        else:
            # De acuerdo con el attr 'grid', se resetean estos parámetros
            line_names, track_sizes, responsive = {}, [], None
        return 'to_store', (line_names, track_sizes, responsive)

    @staticmethod
    def grid_gap(template):
        try:
            template.index(' ')
            answ = template.split(' ')
        except ValueError:
            answ = template
        return 'to_store', answ

    @staticmethod
    def gap(template):
        try:
            row_gap, column_gap = template.strip().split(' ')
        except ValueError:
            row_gap = column_gap = template
        return 'to_process', [('grid-row-gap', row_gap), ('grid-column-gap', column_gap)]

    @staticmethod
    def grid_template(template):
        answ = []
        template_areas = ''.join(re.findall(r'".+?"', template))
        if template_areas:
            template_areas = re.sub(r'\]\s*?\[', ' ', template_areas)
            answ.append(('grid-template-areas', template_areas))
        template_rows, template_columns = re.sub(r' ".+?" ', ' ', template).split('/')
        answ.append(('grid-template-rows', template_rows))
        answ.append(('grid-template-columns', template_columns))
        return 'to_process', answ

    @staticmethod
    def grid_template_areas(template_area):
        if template_area != 'none':
            template_area = template_area.replace('""', '\n').replace('"', '')
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
                vals = [min(rows), min(cols), max(rows) + 1, max(cols) + 1]
                pareas[key] = dict(zip(keys, vals))
        else:
            # De acuerdo con el attr 'grid', se resetean estos parámetros
            pareas, row_names, col_names = {}, {}, {}
        return 'to_store', (pareas, row_names, col_names)

    @staticmethod
    def grid_child(template: str):
        if template == 'auto':
            return 'auto', True
        bSpan = 'span' in template
        if bSpan:
            template = template.replace('span ', '')
        try:
            val = int(template)
            key = 'span' if bSpan else 'item'
            val -= (0 if bSpan or val < 0 else 1)
            return key, val
        except ValueError:
            #    template.isascii():
            key = 'span_name' if bSpan else 'item_name'
            return key, template.strip()

    @staticmethod
    def to_store(template):
        return 'to_store', template.strip()

    @staticmethod
    def grid_area(template):
        isAreaName = '/' not in template
        if isAreaName:
            name = template
            template = f'{name}-start / {name}-start / {name}-end / {name}-end'
            # return 'area_name', template
        keys = ['grid-row-start', 'grid-column-start', 'grid-row-end', 'grid-column-end']
        vals = [x.strip() for x in template.split('/')]
        return 'to_process', zip(keys, vals)

    @staticmethod
    def grid_item(template: str, keys: tuple[str, str]):
        if '/' not in template:
            try:
                n = int(template)
                template = f'{n} / span 1'
            except:
                if 'span' not in template:
                    template = f'{template} / span 1'
                else:
                    template = f'auto / {template}'
        vals = [x.strip() for x in template.split('/')]
        return 'to_process', zip(keys, vals)

    @staticmethod
    def place_items(template, keys=None):
        if '/' not in template:
            template = f'{template} / {template}'
        vals = [x.strip() for x in template.split('/')]
        if keys:
            return 'to_process', zip(keys, vals)
        return 'to_store', vals

    @staticmethod
    def parse_grid(template):
        if template == 'none':
            defaults = [
                ('grid-template-rows', 'none'), ('grid-template-columns', 'none'),
                ('grid-template-areas', 'none'), ('grid-auto-rows', '0px'),
                ('grid-auto-columns', '0px'), ('grid-auto-flow', 'rows')
            ]
            return 'to_process', defaults
        if 'auto-flow' not in template:
            return 'to_process', [('grid-template', template)]
        answ = []
        for track, template_track in zip(('row', 'column'), template.split('/')):
            if 'auto-flow' not in template_track:
                answ.append((f'grid-template-{track}s', template_track.strip()))
            else:
                suffix = " dense" if 'dense' in template_track else ""
                answ.append(('grid-auto-flow', f'{track}{suffix}'))
                auto_flow = f'auto-flow{suffix}'
                auto_track = template_track.replace(auto_flow, '').strip()
                if auto_track:
                    answ.append((f'grid-auto-{track}s', auto_track))
        return 'to_process', answ

    @classmethod
    @property
    def container_attribs(cls):
        return list(cls.container_parsers.keys())

    @classmethod
    def filter_container_attribs(cls, attribs: dict):
        other_attribs = attribs.copy()
        item_attribs = {key: other_attribs.pop(key) for key in other_attribs.keys() & cls.container_attribs}
        return item_attribs, other_attribs

    @classmethod
    @property
    def item_attribs(cls):
        return list(cls.item_parsers.keys())

    @classmethod
    def filter_item_attribs(cls, attribs: dict):
        other_attribs = attribs.copy()
        item_attribs = {key: other_attribs.pop(key) for key in other_attribs.keys() & cls.item_attribs}
        return item_attribs, other_attribs

    @classmethod
    def parse_attr(cls, attr_key, template):
        parsers = cls.container_parsers if attr_key in cls.container_attribs else cls.item_parsers
        try:
            method = parsers[attr_key]
            return method(template)
        except KeyError:
            raise Exception(f'No parser registered for attribute: {attr_key}')

    container_parsers = {
        'grid-template-areas': grid_template_areas,
        'grid-template-rows': grid_template_pattern,
        'grid-template-columns': grid_template_pattern,
        'grid-template': grid_template,
        'column-gap': grid_gap,
        'row-gap': grid_gap,
        'grid-column-gap': grid_gap,
        'grid-row-gap': grid_gap,
        'gap': gap,
        'grid-gap': gap,
        'justify-items': grid_gap,
        'align-items': grid_gap,
        'place-items': lambda x: CssGrid.place_items(x, keys=['align-items', 'justify-items']),
        'justify-content': grid_gap,
        'align-content': grid_gap,
        'place-content': lambda x: CssGrid.place_items(x, keys=['align-content', 'justify-content']),
        'grid-auto-columns': grid_gap,
        'grid-auto-rows': grid_gap,
        'grid-auto-flow': grid_gap,
        'grid': parse_grid,
    }
    # items attributes =====================================================
    item_parsers = {
        'grid-column-start': grid_child,
        'grid-column-end': grid_child,
        'grid-row-start': grid_child,
        'grid-row-end': grid_child,
        'grid-area': grid_area,
        'grid-column': lambda x: CssGrid.grid_item(x, ('grid-column-start', 'grid-column-end')),
        'grid-row': lambda x: CssGrid.grid_item(x, ('grid-row-start', 'grid-row-end')),
        'align-self': grid_child,
        'justify-self': grid_child,
        'place-self': lambda x: CssGrid.place_items(x, ('align-self', 'justify-self')),
        'z-index': grid_child,
        'in': to_store,
    }


def frst_main():
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
    dmy1 = [container.register_item(x) for x in items]

    container.grid_auto_flow = 'column'
    container.taken = set()
    container.next = 0
    dmy2 = [container.register_item(x) for x in items]
    pass


def main():
    tk = tkinter
    class TestCssGrid(tk.Tk):
        def __init__(self):
            super().__init__()
            self.geometry('500x500')
            self.memory = (0, 0)
            self.packer = {
                'h=w': dict(anchor='news'),
                'h>w': dict(anchor='w'),
                'h<w': dict(side='left'),
            }
            filename = '@tests:css_files/cssgrid_test'

            self.wdg_tree = userinterface.getLayout(filename, withCss=True)
            self.grid()
            self.rowconfigure(0, weight=1)
            self.columnconfigure(0, weight=1)
            self.setTestGui()
            pass

        def setGui(self):
            self.bind("<Configure>", self.resize)
            for k in range(9):
                lbl = tk.Label(self, text=f'Item {k}', bg='blue')
                # lbl.pack(side='left', expand='yes')

        def resize(self, event:tk.Event):
            if event.widget == self:
                cell_size = 50
                pad_size = 10
                base = cell_size + pad_size
                w, h = event.width, event.height
                nW, nH = self.memory
                nrows, ncols = h // base, w // base
                if ncols != nW:
                    self.columnconfigure(list(range(ncols)), weight=0, minsize=cell_size, pad=pad_size)
                    self.rowconfigure(list(range(nrows)), weight=0, minsize=cell_size, pad=pad_size)
                    self.anchor='center'
                    for n, wdg in enumerate(self.winfo_children()):
                        wdg.grid_forget()
                        x = n // ncols
                        y = n % ncols
                        wdg.grid(row=x, column=y, sticky='nsew')
                    self.memory = (ncols, nrows)

        def setTestGui(self):
            userinterface.newPanelFactory(
                master=self,
                selpane=self.wdg_tree,
                genPanelModule=None,
                setParentTo='master',
                registerWidget=None,
            )
            pass

    master = TestCssGrid()
    master.mainloop()
    pass


if __name__ == '__main__':
    main()
