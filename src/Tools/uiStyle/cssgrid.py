

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
            'grid-auto-flow'' row | column | row dense | column dense': ,
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
