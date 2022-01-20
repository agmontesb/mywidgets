import Tools.uiStyle.CustomRegEx as CustomRegEx


def getWidgetMap(htmlstr, k=-1):
    cmpobj = CustomRegEx.compile('(?#<__TAG__ __TAG__=tag id=_id_ >)')

    from_pos = 0
    to_pos = len(htmlstr)
    answ = []
    it = cmpobj.finditer(htmlstr, from_pos, to_pos)
    stack = [(m.span(), m.groups()) for m in it]

    while stack:
        (pini, pfin), (tag, id) = stack.pop(0)
        if id is None:
            k += 1
            id = str(k)
        answ.append(((pini, pfin), (tag, id)))

        from_pos = htmlstr[pini:pfin].find('>') + pini + 1
        to_pos = htmlstr[pini:pfin].rfind('<') + pini

        bflag = from_pos != -1 and to_pos != -1 and from_pos < to_pos
        if bflag:
            it = cmpobj.finditer(htmlstr, from_pos, to_pos)
            stack = [(m.span(), m.groups()) for m in it] + stack
    wdg_map = {key: value[1]for key, value in answ}
    return wdg_map

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
            if CustomRegEx.match('[a-zA-z\d]+', selector):           # widget
                base_pattern = f'{selector}'
            elif selector[0] == '.':         # Clase
                base_pattern = f'__TAG__ class=".*?{selector[1:]}.*?"'
            elif selector[0] == '#':       # id
                base_pattern = f'__TAG__ id="{selector[1:]}"'
            else:
                raise AssertionError(f'Selector: {selector}, no conocido')
        elif len(items) == 2:
            sel1, sel2 = items
            assert sel1.isalpha() and sel2[0] == '.', f'Caso {sel1}{sel2} no encontrado todavia'
            base_pattern = f'{sel1} class="{sel2[1:]}"'
        return base_pattern

    pattern = '[\.#]*?[a-zA-z\d,]+'
    selectors = selector_str.split(' ', 1)
    split_selectors = selectors[0].split(',')
    base_pattern = [getBasicPattern(x) for x in split_selectors]
    if len(selectors) == 2:
        if ',' in selectors[1]:
            raise Exception(f'Selector: {selector_str} no habilitado aún')
        inner_pattern = [getBasicPattern(x) for x in selectors[1].split(' ')]
        base_pattern = [f'{x} <{y}>*' for x in base_pattern for y in inner_pattern]
    base_pattern = [f'(?#<{x}>)' for x in base_pattern]
    return base_pattern

def findWidgets(patterns, htmlstr, wdg_map):
    answ = []
    selected = []
    for pattern in patterns:
        cmpobj = CustomRegEx.compile(pattern)
        selected.extend([m.span() for m in cmpobj.finditer(htmlstr)])
        answ.extend([wdg_map.get(spn, None) for spn in selected])
    zansw = sorted(set(zip(answ, selected)), key=lambda x: x[1])
    answ, selected = list(zip(*zansw))
    return answ, selected


if __name__ == '__main__':
    # Selectores válidos
    selectors = {}
    selectors['validos'] = [
        'tag1 tag2 tag3 tag4',
        'tag',
        'tag1,tag2',
        'tag.clase',
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
        for selector in selectores:
            sel_pattern = selectorPattern(selector)
            print(f'{selector}, {sel_pattern}')



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
    print(findWidgets(id_pattern, htmlstr, wdg_map)[0])

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
    print(findWidgets(class_pattern, htmlstr, wdg_map)[0])

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
    widgets, selected = findWidgets(class_pattern, htmlstr, wdg_map)
    for wdg_id, wdg_spn in zip(widgets, selected):
        pi, pf = wdg_spn
        print(wdg_id, htmlstr[pi:pf])

    class_pattern = selectorPattern('body p h1')
    widgets, selected = findWidgets(class_pattern, htmlstr, wdg_map)
    for wdg_id, wdg_spn in zip(widgets, selected):
        pi, pf = wdg_spn
        print(wdg_id, htmlstr[pi:pf])



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
    widgets, selected = findWidgets(class_pattern, htmlstr, wdg_map)
    for wdg_id, wdg_spn in zip(widgets, selected):
        pi, pf = wdg_spn
        print(wdg_id, htmlstr[pi:pf])
