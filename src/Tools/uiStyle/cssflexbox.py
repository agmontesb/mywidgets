import collections
import itertools
import tkinter

import userinterface
from Tools.uiStyle.cssgrid import CssUnit

TEST_ID = 1
TESTFILE = ['@tests:css_files/cssflexbox_test', '@doc:showcase/cssflexbox_direction']


class CssFlexBox:

    __slots__ = (
        'flex_direction', 'flex_wrap',
        'align_items',
        'justify_content', 'align_content',
        'row_gap', 'column_gap',
        '_master', 'slaves', 'memory',
    )

    manager = 'pack'

    def __init__(self, **flexbox):
        self.parse_container_declaration_block(flexbox)
        pass

    def init_container_state(self) -> None:
        self.flex_direction = 'row'
        self.flex_wrap = 'nowrap'
        self.align_items = 'stretch'
        self.justify_content = 'flex-start'
        self.align_content = 'center'
        self.row_gap = CssUnit('0px')
        self.column_gap = CssUnit('0px')
        self._master = None
        self.slaves = []
        self.memory = (0, 0)

    def parse_container_declaration_block(self, decblock: dict[str, str]) -> None:
        self.init_container_state()
        to_process: list = [(key, decblock[key]) for key in decblock.keys() & self.container_parsers.keys()]
        while to_process:
            attr_key, template = to_process.pop()
            acase, answ = self.parse_attr(attr_key, template.strip())
            if acase == 'to_process':
                to_process.extend(answ)
                continue
            attr_key = attr_key.replace('-', '_')
            match attr_key:
                case 'row_gap' | 'column_gap':
                    value = CssUnit(answ)
                case _:
                    value = answ
            setattr(self, attr_key, value)

    @property
    def master(self):
        if self._master is None:
            raise AttributeError('No master configured for this grid')
        return self._master

    def register_item(self, widget, item_attribs: dict) -> int:
        '''
        Almacena los atributos del item de forma canónica y le asigna una prioridad para su procesamiento
        '''
        item_attribs, _ = self.filter_item_attribs(item_attribs)
        base_attribs = self.canonalize_attribs(item_attribs)

        grid_params = {
            'order': 0,
            'flex-grow': 0, 'flex-shrink': 1, 'flex-basis': 'auto',
            'align-self': self.align_items,
            'min-width': CssUnit('0px'), 'min-height': CssUnit('0px'),
        }
        to_process = list(base_attribs.items())
        while to_process:
            key, template = to_process.pop()
            case, val = self.parse_attr(key, template.strip())
            if case == 'to_process':
                to_process.extend(val)
                continue
            match key:
                case 'order' | 'flex-grow' | 'flex-shrink':
                    value = int(val)
                case 'flex-basis' | 'width' | 'min-width' | 'max-width' | 'height' | 'max-height' | 'min-height':
                    value = CssUnit(val)
                case _:
                    value = val
            grid_params[key] = value
        self.slaves.append((str(widget), grid_params))
        return grid_params['order']

    def config_master(self, master):
        self._master = master
        isResponsive = True
        if isResponsive:
            master.bind("<Configure>", self.resize)
        else:
            self._config_master(master)

    def resize(self, event: tkinter.Event):
        if event.widget != self.master or self.memory == (event.width, event.height):
            return
        w, h = event.width, event.height
        master = self.master
        # print(str(master), w, h)
        isResponsive = True
        if isResponsive:
            # Se elimina el mapeo de widgets asociados al container
            [
                getattr(master.nametowidget(wdg_name), f'{self.manager}_forget')()
                for wdg_name, _ in self.slaves
            ]
            [
                wdg.destroy()
                for wdg in getattr(master, f'{self.manager}_slaves')()
            ]
            # Se procede a mapear nuevamente los widgets en el container
            self._config_master(event)
            self.memory = w, h

    @staticmethod
    def set_justify_content(fline_slaves, flex_attr, flex_gap, flex_side, flex_fill, bg_color, justify_content):
        frst_wdg: tkinter.Widget
        try:
            frst_wdg, *slaves, last_wdg = fline_slaves
            to_gap = [*slaves, last_wdg]
        except ValueError:
            # Solo se tiene un widget
            frst_wdg = last_wdg = fline_slaves[0]
            to_gap = []
        fline = frst_wdg.pack_info()['in']
        # Se crean los gaps entre los widgets
        for k, wdg in enumerate(to_gap):
            attrs = {'name': f'fgap{k + 1:0>2d}', flex_attr: flex_gap, 'bg': bg_color}
            wdg_gap = tkinter.Frame(fline, **attrs)
            match justify_content:
                case 'flex-start' | 'start' | 'left' | 'flex-end' | 'end' | 'right':
                    wdg_gap.pack(before=wdg, side=flex_side, fill=flex_fill)
                case 'center':
                    wdg_gap.pack(before=wdg, side=flex_side, fill=flex_fill)
                case 'space-between' | 'space-around' | 'space-evenly':
                    wdg_gap.pack(before=wdg, side=flex_side, fill='both', expand=1)
        # Se crean los gaps de los extremos
        frst_gap = tkinter.Frame(fline, name=f'fgap_frst', bg=bg_color)
        last_gap = tkinter.Frame(fline, name=f'fgap_last', bg=bg_color)
        pack_attrs = dict(side=flex_side, fill='both', expand=1)
        match justify_content:
            case 'flex-end' | 'end' | 'right':
                frst_gap.pack(before=frst_wdg, **pack_attrs)
            case 'center' | 'space-evenly':
                frst_gap.pack(before=frst_wdg, **pack_attrs)
                last_gap.pack(after=last_wdg, **pack_attrs)
            case 'space-around':
                # Esto se tiene que corregir para que se amplie solo la mitad en estos gaps
                frst_gap.pack(before=frst_wdg, **pack_attrs)
                last_gap.pack(after=last_wdg, **pack_attrs)
            case _:
                # no se mapea los gaps extremos para que no aparezca espacio al comienzo y el final
                pass

    def _config_master(self, event):
        master = self.master
        master_name = str(master)
        equiv = [
            ('in', 'in_'),
        ]

        axis = int('column' in self.flex_direction)
        flex_side, cross_side = (('left', 'right'), ('top', 'bottom'))[:: 1 - 2 * axis]
        flex_side = flex_side['reverse' in self.flex_direction]
        cross_side = cross_side['reverse' in self.flex_wrap]
        flex_fill, cross_fill = ('y', 'x')[:: 1 - 2 * axis]
        flex_attr, cross_attr = ('width', 'height')[:: 1 - 2 * axis]
        frst_wdg = master.nametowidget(self.slaves[0][0])

        processed_slaves = self.get_process_item_attribs(event)
        nline = 0
        while nline < len(processed_slaves):
            _, gp = processed_slaves[nline]
            flex_line = gp.pop('flex-line')
            nline += flex_line['n-widgets']

            fline = tkinter.Frame(master, name=f'flex_line{nline:0>2d}', bg=master['bg'])
            fline.pack(expand=0, side=cross_side, fill=cross_fill)
            fline.lower(belowThis=frst_wdg)
            gp['flex-line'] = fline

        fline = None
        for name, item_attrs in processed_slaves:
            wdg = master.nametowidget(name)
            fline = item_attrs.pop('flex-line', None) or fline
            align_self = item_attrs.pop('align-self')

            wdg.configure(**item_attrs)
            # Se mapea el wdg
            attrs = dict(side=flex_side, in_=fline)
            match align_self:
                case 'stretch':
                    attrs['fill'] = ('y', 'x')[axis]
                case 'flex-start' | 'start' | 'self-start':
                    attrs['anchor'] = ('n', 'w')[axis]
                case 'center':
                    attrs['anchor'] = 'center'
                case 'flex-end' | 'end' | 'self-end':
                    attrs['anchor'] = ('s', 'e')[axis]
            wdg.pack(**attrs)
        pass
        row_gap, column_gap = map(lambda x, attr: x._value(event, attr), (self.row_gap, self.column_gap), ('height', 'width'))

        flex_gap, cross_gap = (column_gap, row_gap)[::1 - 2 * axis]
        flines = []
        for fline in master.winfo_children():
            fline_name = fline.winfo_name()
            if not fline_name.startswith('flex_line'):
                break
            flines.append(fline)
            self.set_justify_content(
                fline.slaves(), flex_attr, flex_gap, flex_side, flex_fill, master['bg'], self.justify_content
            )

        self.set_justify_content(
            flines, cross_attr, cross_gap, cross_side, cross_fill, master['bg'], self.align_content
        )
        pass
            # try:
            #     frst_wdg, *slaves, last_wdg = fline.slaves()
            #     to_gap = [*slaves, last_wdg]
            # except ValueError:
            #     # Solo se tiene un widget
            #     slaves, last_wdg = [], frst_wdg
            #     to_gap = []
            # # Se crean los gaps entre los widgets
            # for k, wdg in enumerate(to_gap):
            #     attrs = {'name': f'fgap{k:0>2d}', flex_attr: flex_gap, 'bg': master['bg']}
            #     wdg_gap = tkinter.Frame(fline, **attrs)
            #     match self.justify_content:
            #         case 'flex-start' | 'start' | 'left' | 'flex-end' | 'end' | 'right':
            #             wdg_gap.pack(before=wdg, side=flex_side, fill=flex_fill)
            #         case 'center':
            #             wdg_gap.pack(before=wdg, side=flex_side, fill=flex_fill)
            #         case 'space-between' | 'space-around' | 'space-evenly':
            #             wdg_gap.pack(before=wdg, side=flex_side, fill='both', expand=1)
            # # Se crean los gaps de los extremos
            # frst_gap = tkinter.Frame(fline, name=f'fgap_frst', bg=master['bg'])
            # last_gap = tkinter.Frame(fline, name=f'fgap_last', bg=master['bg'])
            # pack_attrs = dict(side=flex_side, fill='both', expand=1)
            # match self.justify_content:
            #     case 'flex-end' | 'end' | 'right':
            #         frst_gap.pack(before=frst_wdg, **pack_attrs)
            #     case 'center' | 'space-evenly':
            #         frst_gap.pack(before=frst_wdg, **pack_attrs)
            #         last_gap.pack(after=last_wdg, **pack_attrs)
            #     case 'space-around':
            #         # Esto se tiene que corregir para que se amplie solo la mitad en estos gaps
            #         frst_gap.pack(before=frst_wdg, **pack_attrs)
            #         last_gap.pack(after=last_wdg, **pack_attrs)
            #     case _:
            #         # no se mapea los gaps extremos para que no aparezca espacio al comienzo y el final
            #         pass


        # if DEBUG:
        #     nrows, ncolumns = self.nrows, self.ncolumns
        #     if not self.grid_row_gap and self.grid_auto_flow == 'column':
        #         ncolumns = len(self.slaves) // nrows
        #     if not self.grid_column_gap and self.grid_auto_flow == 'row':
        #         nrows = len(self.slaves) // ncolumns
        #
        #     for row in range(0, 2 * nrows + 1, 2):
        #         frm = tkinter.Frame(master, name=f'row_{row // 2 + 1}', height=1, width=1, bg='black')
        #         frm.grid(row=row, column=0, columnspan=2 * ncolumns + 1, sticky='ew')
        #         frm.lower()  # Con esto se manda estos al fondo del stacking order
        #     for col in range(0, 2 * ncolumns + 1, 2):
        #         frm = tkinter.Frame(master, name=f'col_{col // 2 + 1}', height=1, width=1, bg='black')
        #         frm.grid(row=0, column=col, rowspan=2 * nrows + 1, sticky='ns')
        #         frm.lower()  # Con esto se manda estos al fondo del stacking order
        pass

    def get_process_item_attribs(self, event: tkinter.Event) -> list[tuple[str, dict]]:
        '''
        Se implementa aquí el algoritmo de posicionamiento de los items del container
        '''
        slaves = []
        ordered_slaves = sorted(
            self.slaves,
            key=lambda x: x[1].get('order', 0)
        )
        axis = int('column' in self.flex_direction)
        flex_axis, cross_axis = ('width', 'height')[:: 1 - 2 * axis]
        row_gap, column_gap = map(lambda x, attr: x._value(event, attr), (self.row_gap, self.column_gap), ('height', 'width'))
        flex_gap, cross_gap = (column_gap, row_gap)[::1 - 2 * axis]

        main_size = getattr(event, flex_axis)
        nline = -1
        frst_pos = 0
        while frst_pos < len(ordered_slaves):
            nline += 1
            fline = []
            line_size = 0
            for name, grid_params in ordered_slaves[frst_pos:]:
                wdg = None

                gp = {key: grid_params[key] for key in ('flex-grow', 'flex-shrink', 'align-self')}
                for key in (flex_axis, cross_axis):
                    try:
                        value = grid_params.get(key)._value(event, key)
                    except AttributeError:
                        master = self.master
                        wdg = wdg or master.nametowidget(name)
                        value = getattr(wdg, f'winfo_{key}')() or getattr(wdg, f'winfo_req{key}')()
                    gp[key] = value

                min_key, max_key = f'min-{flex_axis}', f'max-{flex_axis}'
                pairs = zip(
                    (min_key, max_key),
                    (0, main_size)
                )
                for key, default in pairs:
                    try:
                        css_unitsize = grid_params.get(key)
                        value = css_unitsize._value(event, flex_axis)
                    except AttributeError:
                        value = default
                    gp[key] = value

                try:
                    css_unitsize = grid_params['flex-basis']
                    wdg_size = css_unitsize._value(event, flex_axis)
                except AttributeError:
                    wdg_size = gp[flex_axis]
                gp[flex_axis] = wdg_size

                bsize = line_size + wdg_size + flex_gap * len(fline) > main_size
                if self.flex_wrap != 'nowrap' and bsize and fline:
                    break
                line_size += wdg_size
                fline.append((name, gp))

            gap_size = flex_gap * max(0, len(fline) - 1)
            # Se debe generar acá una flex line
            free_space = main_size - line_size - gap_size

            isFlexGrow = free_space >= 0
            ckey, okey = ('flex-shrink', 'flex-grow')[:: 1 - 2 * isFlexGrow]
            fnc = (lambda x: x['flex-grow']) if isFlexGrow else (lambda x: x['flex-shrink'] * x[flex_axis])
            weight_sum = sum(fnc(gp) for _, gp in fline)

            while free_space and weight_sum:
                leftover = 0
                for _, params in fline:
                    weight = fnc(params)
                    ratio = weight / weight_sum if weight_sum else 0
                    delta = round(free_space * ratio)
                    wdg_size = params.pop(flex_axis) + delta
                    params[flex_axis] = max(params[min_key], min(params[max_key], wdg_size))
                    if inc := wdg_size - params[flex_axis]:
                        params[ckey] = 0
                        leftover += inc
                free_space = leftover
                weight_sum = sum(fnc(gp) for _, gp in fline)

            fline = [
                (name, {key: params[key] for key in (flex_axis, cross_axis, 'align-self')})
                for name, params in fline
            ]
            fline[0][1]['flex-line'] = {
                'free-space': free_space + gap_size, 'n-widgets': len(fline),
                cross_axis: max(x[cross_axis] for _, x in fline),
            }
            slaves.extend(fline)
            frst_pos += len(fline)
        return slaves

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
        to_verify = dict(to_verify)
        return to_verify

    @classmethod
    def parse_attr(cls, attr_key, template):
        parsers = cls.container_parsers if attr_key in cls.container_attribs else cls.item_parsers
        try:
            method = parsers[attr_key]
            return method(template)
        except KeyError:
            raise Exception(f'No parser registered for attribute: {attr_key}')

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

        # ==============================- Parsers -======================================================

    @staticmethod
    def check_value(value: str, value_list: list[str]):
        try:
            value_list.index(value)
            return 'to_store', value
        except ValueError:
            raise ValueError(f'{value} is not a valid value, it must one of : {", ".join(value_list)}')

    @staticmethod
    def split_pattern(template, base_values):
        return 'to_process', zip(base_values, template.split(' ', len(base_values) - 1))

    @staticmethod
    def validate_temp(template, predicate):
        if predicate(template):
            return 'to_store', template
        raise ValueError('Invalid value for this property')

    @staticmethod
    def validate_flex_basis(template):
        dmy = CssUnit(template)
        bflag = isinstance(dmy, CssUnit) or template == 'auto'
        if bflag:
            return 'to_store', template
        raise ValueError('Invalid value for this property')

    @staticmethod
    def parse_item_flex(template: str):
        match template:
            case 'initial':
                # Valor por defecto. widget puede encoger pero no crecer.
                template = '0 1 auto'
            case 'auto':
                # Full flexible. widget puede encoger y crecer.
                template = '1 1 auto'
            case 'none':
                # Widget no puede encogerse o crecer.
                template = '0 0 auto'
            case template if template.isdigit():
                template = f'{template} 1 0px'
            case _:
                pass
        return CssFlexBox.split_pattern(template, ['flex-grow', 'flex-shrink', 'flex-basis'])

    container_parsers = {
        'flex-direction': lambda temp: CssFlexBox.check_value(temp, ['row', 'row-reverse', 'column', 'column-reverse']),
        'flex-wrap': lambda temp: CssFlexBox.check_value(temp, ['nowrap', 'wrap', 'wrap-reverse']),
        'flex-flow': lambda temp: CssFlexBox.split_pattern(temp, ['flex-direction', 'flex-wrap']),
        'justify-content': lambda temp: CssFlexBox.check_value(
            temp,
            'flex-start | flex-end | center | space-between | space-around | space-evenly | start | end | left | right'.split(' | ')
        ),
        'align-items': lambda temp: CssFlexBox.check_value(
            temp,
            'stretch | flex-start | flex-end | center | start | end | self-start | self-end'.split(' | ')
        ),
        'align-content': lambda temp: CssFlexBox.check_value(
            temp,
            'flex-start | flex-end | center | space-between | space-around | space-evenly | stretch | start | end'.split(' | ')
        ),
        'row-gap': lambda x: CssFlexBox.validate_temp(x, lambda y: isinstance(x, str)),
        'column-gap': lambda x: CssFlexBox.validate_temp(x, lambda y: isinstance(x, str)),
        'gap': lambda temp: CssFlexBox.split_pattern(temp, ['row-gap', 'column-gap']),
    }

    item_parsers = {
        'order': lambda x: CssFlexBox.validate_temp(x, lambda y: x.lstrip('-+').isdigit()),
        'flex-grow': lambda x: CssFlexBox.validate_temp(x, lambda y: not x.startswith('-') and x.lstrip('-+').isdigit()),
        'flex-shrink': lambda x: CssFlexBox.validate_temp(x, lambda y: not x.startswith('-') and x.lstrip('-+').isdigit()),
        'flex-basis': lambda x: CssFlexBox.validate_temp(x, lambda y: isinstance(CssUnit(x), CssUnit) or x in 'auto|content'),
        'flex': parse_item_flex,
        'align-self': lambda temp: CssFlexBox.check_value(
            temp,
            'auto | flex-start | flex-end | center | stretch'.split(' | ')
        ),
        # Se agregan acá estos parámetros porque hasta ahora no se tiene forma de procesarlos/recuperarlos
        'width': lambda x: CssFlexBox.validate_temp(x, lambda y: isinstance(CssUnit(x), CssUnit)),
        'max-width': lambda x: CssFlexBox.validate_temp(x, lambda y: isinstance(CssUnit(x), CssUnit)),
        'min-width': lambda x: CssFlexBox.validate_temp(x, lambda y: isinstance(CssUnit(x), CssUnit)),
        'height': lambda x: CssFlexBox.validate_temp(x, lambda y: isinstance(CssUnit(x), CssUnit)),
        'max-height': lambda x: CssFlexBox.validate_temp(x, lambda y: isinstance(CssUnit(x), CssUnit)),
        'min-height': lambda x: CssFlexBox.validate_temp(x, lambda y: isinstance(CssUnit(x), CssUnit)),
    }


def main():
    tk = tkinter
    class TestCssFlexBox(tk.Tk):
        def __init__(self):
            super().__init__()
            self.geometry('500x500')
            filename = TESTFILE[TEST_ID]

            self.wdg_tree = userinterface.getLayout(filename, withCss=True)
            self.setTestGui()
            pass

        def setTestGui(self):
            userinterface.newPanelFactory(
                master=self,
                selpane=self.wdg_tree,
                genPanelModule=None,
                setParentTo='master',
                registerWidget=None,
            )
            pass

    master = TestCssFlexBox()
    master.mainloop()
    pass


if __name__ == '__main__':
    main()
