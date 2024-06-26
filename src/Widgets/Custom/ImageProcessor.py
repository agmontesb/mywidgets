import os
import pickle
from PIL import Image, ImageTk, ImageFont, ImageColor, ImageDraw, ImageChops
import xml.etree.ElementTree as ET
import urllib
import re
import functools

TEXTURE_DIRECTORY = 'c:/testFiles/Confluence'
IMAGECACHE_DIRECTORY = 'c:/testFiles/imagecahe'


''' Font awesome'''
FA_WINDOW_MAX = 'fa-window-maximize'
FA_WINDOW_MIN = 'fa-window-minimize'
FA_WINDOW_RES = 'fa-window-restore'


''' Bitmaps'''
ROMBO         = '018003c007e00ff01ff83ffc7ffeffffffff7ffe3ffc1ff80ff007e003c00180'
FLECHA_IZQ    = '0180038007800f801f803fff7fffffffffff7fff3fff1f800f80078003800180'
FLECHA_I      = '0180038007000e001c0038007000ffffffff700038001c000e00070003800180'
CFLECHA_I     = '0180038007000e001c0038007000e000e000700038001c000e00070003800180'
CFLECHA_DOBLE = '01830387070e0e1c1c38387070e0e1c0e1c070e038701c380e1c070e03870183'
WINDOW_MAX    = '00007ffe7ffe7ffe6006600660066006600660066006600660067ffe7ffe0000'
WINDOW_RES    = '00007fe07fe06060606067fe67fe666666667fe67fe60606060607fe07fe0000'
WINDOW_MIN    = '0000000000000000000000003ffc3ffc3ffc3ffc000000000000000000000000'

# FLECHA_DER    = '07e007e007e007e007e007e007e0ffffffff7ffe3ffc1ff80ff007e003c00180'
# FLECHA_ABAJO  = '018001c001e001f001f8fffcfffefffffffffffefffc01f801f001e001c00180'
# FLECHA_ARRIBA = '0180038007800f801f803fff7fffffffffff7fff3fff1f800f80078003800180'
CIRCULO       = '01000fe01ff03ff87ffc7ffc7ffcfffe7ffc7ffc7ffc3ff81ff00fe001000000'
ANILLO        = '01000fe01ff03ef8783c701c701ce00e701c701c783c3ef81ff00fe001000000'


dataB = [
         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]

datab = [
         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
         [0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0],
         [0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0],
         [0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0],
         [0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0],
         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]


def memoize(obj, serialize=True):
    cache = obj.cache = {}

    @functools.wraps(obj)
    def memoizer(*args, **kwargs):
        key = str(args) + str(sorted(kwargs))
        if key not in cache:
            answ = obj(*args, **kwargs)
            try:
                to_store = pickle.dumps(answ)
            except TypeError:
                to_store = answ
            cache[key] = to_store
        else:
            try:
                answ = pickle.loads(cache[key])
            except Exception:
                answ = cache[key]
        return answ
    return memoizer


def bitMapToString(bitMap):
    hNum = ''
    for j in range(len(bitMap)):
        for i in range(int(len(bitMap[0])/4)):
            hNum += "{0:x}".format(sum(elem*2**(3-k) for k, elem in enumerate(bitMap[j][4*i:4*(i+1)])))
    return hNum


def getBitmapIconImageTk(imageStr):
    imSize = int((len(4*imageStr))**0.5)
    imString = imageStr.decode('hex')
    im = Image.frombytes('1',(imSize,imSize),imString)
    im = ImageTk.BitmapImage(im)
    return im


def _parseXml(settingXmlFile):
    try:
        root = ET.parse(settingXmlFile).getroot()
    except:  # ParseError
        from xml.sax.saxutils import quoteattr
        with open(settingXmlFile, 'r') as f:
            content = f.read()
            content = re.sub(r'(?<==)(["\'])(.*?)\1', lambda x: quoteattr(x.group(2)), content)
        root = ET.fromstring(content)
    return root


def _getThemeColour(srchcolor, theme='confluence'):
    # if not re.match('[0-9ABCDEF]{8}\Z', srchcolor.upper()):
    #     import xbmc
    #     pathName, skinDir = xbmc.translatePath('special://skin'), xbmc.getSkinDir()
    #     colorXml = theme + '.xml'
    #     files = ['defaults.xml', colorXml]
    #     color = None
    #     while files:
    #         filename = files.pop()
    #         filename = os.path.join(pathName, skinDir, 'Colors', filename)
    #         if not os.path.exists(filename): continue
    #         colors = _parseXml(filename)
    #         color = colors.find('.//color[@name="%s"]' % srchcolor)
    #         if color is not None: break
    if not re.match(r'[0-9ABCDEF]{8}\Z', srchcolor.upper()):
        try:
            colorTuple = ImageColor.getrgb(srchcolor)
            if len(colorTuple) == 3:
                colorTuple += (255, )
        except ValueError:
            srchcolor = 'FFFF0000'
        else:
            return colorTuple
    color = [int(srchcolor[k:k+2], 16) for k in range(0, 8, 2)]
    transp, red, green, blue = color
    return red, green, blue, transp


def _imageFile(imageFile):
    if not os.path.dirname(imageFile):
        imageFile = os.path.join(TEXTURE_DIRECTORY, imageFile)
    if not os.path.exists(imageFile):
        return None
    return imageFile

def _eqTkFont(fontname, size=50, res='720p', fontset='Default'):
    # import xbmcaddon
    # pathName, skinDir = xbmc.translatePath('special://skin'), xbmc.getSkinDir()
    # fontXml = os.path.join(pathName, skinDir, res, 'font.xml')
    # fonts = xbmcaddon.Addon._parseXml(fontXml)
    # fontset = fonts.find('.//fontset[@id="%s"]' % fontset)
    # font = fontset.find('.//font[name="%s"]' % fontname)
    # if font is None: font = fontset.find('.//font[name="font13"]')
    # if font is not None:
    #     keys = ['filename', 'size', 'style']
    #     attrib = dict((chld.tag, chld.text) for chld in font.getchildren() if chld.tag in keys)
    #     filename = attrib['filename']
    #     size = int(attrib['size'])
    #     if attrib.has_key('style'):
    #         # Here we must find a way to detect the correct filename
    #         pass
    # else:
    #     filename = 'arial.ttf'
    #     size = 20
    # path = xbmc.translatePath('special://xbmc/')
    # fullname1 = os.path.join(path, 'addons', skinDir, 'fonts', filename)
    # fullname2 = os.path.join(path, 'media', 'fonts', filename)
    # for fullname in [fullname1, fullname2]:
    #     if os.path.exists(fullname):
    #         filename = fullname
    #         break
    return ImageFont.truetype(fontname, size)


# @memoize
# He decidido transformar a getCacheTexture la versión memoize de esta función
def getTexture(imageFile, Width, Height, aspectratio='stretch', **options):
    defaults = dict(
        flipx=False, flipy=False,
        aspectratio='stretch', colorkey='',
        border=0, bordertexture='', bordersize=0,
        colordiffuse='', diffuse='',
    )

    if isinstance(imageFile, (bytes, str)):
        imageFile = _imageFile(imageFile)
        if not imageFile:
            return None
        imageFile = Image.open(imageFile)
    im = imageFile
    bbox = im.getbbox()
    im = im.crop(bbox)
    iw, ih = im.size

    Width = Width or iw
    Height = Height or ih

    if options.get('flipx', False):
        im = im.transpose(Image.FLIP_LEFT_RIGHT)

    if options.get('flipy', False):
        im = im.transpose(Image.FLIP_TOP_BOTTOM)

    if options.get('colorkey', ''):
        colorkey = options.get('colorkey')
        colorTuple = _getThemeColour(colorkey)
        if im.mode == 'RGB':
            im.putalpha(128)
        base = Image.new(im.mode, (iw, ih), colorTuple)
        im = Image.alpha_composite(base, im)
    if aspectratio == 'stretch':
        width, height = Width, Height
    elif aspectratio == 'keep':
        width, height = min(Width, int((1.0*iw*Height)//ih)), min(Height, int((1.0*ih*Width)//iw))
    elif aspectratio == 'scale':
        width, height = max(Width, int((1.0*iw*Height)//ih)), max(Height, int((1.0*ih*Width)//iw))
    elif aspectratio == 'center':
        width, height = iw, ih

    dstIm = Image.new(im.mode, (width, height), (128, 128, 128, 128))

    brdSectors = lambda w, h: [(    0,     0,     l,     t),
                               (    l,     0, w - r,     t),
                               (w - r,     0,     w,     t),
                               (    0,     t,     l, h - b),
                               (w - r,     t,     w, h - b),
                               (    0, h - b,     l,     h),
                               (    l, h - b, w - r,     h),
                               (w - r, h - b,     w,     h)]
    coreRegion = lambda w, h:  (    l,     t, w - r, h - b)

    border = options.get('border', 0)
    if isinstance(border, (bytes, str)):
        border = map(int, border.split(','))
    else:
        border = (border, )
    border *= 4
    l, t, r, b = border[:4]

    coreSrc = coreRegion(iw, ih)
    coreRgn = im.crop(coreSrc)

    if options.get('bordertexture', '') and options.get('bordersize', 0):
        bordertexture = options["bordertexture"]
        im = Image.open(bordertexture)
        iw, ih = im.size

        bordersize = options['bordersize']
        if isinstance(bordersize, int):
            bordersize = (bordersize, )
        bordersize *= 4
        l, t, r, b = bordersize[:4]

    srcSectors = brdSectors(iw, ih)
    dstSectors = brdSectors(width, height)
    for srcBox, dstBox in zip(srcSectors, dstSectors):
        dstSize = (dstBox[2] - dstBox[0], dstBox[3] - dstBox[1])
        if dstSize[0] <= 0 or dstSize[1] <= 0: continue
        region = im.crop(srcBox)
        region = region.resize(dstSize)
        dstIm.paste(region, dstBox)

    coreDst = coreRegion(width, height)
    dstSize = (coreDst[2] - coreDst[0], coreDst[3] - coreDst[1])
    if dstSize[0] > 0 and dstSize[1] > 0:
        coreReg = coreRgn.resize(dstSize)
        dstIm.paste(coreReg, coreDst)

    colordiffuse = options.get('colordiffuse', '')
    if colordiffuse:
        colorTuple = _getThemeColour(colordiffuse)
        colordiffuse = Image.new(im.mode, (width, height), colorTuple)

    diffuse = options.get('diffuse', '') or colordiffuse
    if diffuse:
        dstIm = ImageChops.multiply(dstIm, diffuse)

    xOff, yOff = (Width - width)//2, (Height - height)//2
    if aspectratio == 'scale': xOff = yOff = 0
    if xOff >= 0:
        x1s, x2s = 0, min(Width, width)
        x1d, x2d = xOff + x1s, xOff + x2s
    else:
        xOff = -xOff
        x1d, x2d = 0, Width
        x1s, x2s = xOff + x1d, xOff + x2d

    if yOff >= 0:
        y1s, y2s = 0, min(Height, height)
        y1d, y2d = yOff + y1s, yOff + y2s
    else:
        yOff = -yOff
        y1d, y2d = 0, Height
        y1s, y2s = yOff + y1d, yOff + y2d


    retIm = Image.new(im.mode, (Width, Height), (128, 128, 128, 128))
    region = dstIm.crop((x1s, y1s, x2s, y2s))
    retIm.paste(region, (x1d, y1d, x2d, y2d))
    return retIm

@memoize
def getCacheTexture(imageFile, Width, Height, aspectratio='stretch', isphotoimage=True, **options):
    img = getTexture(imageFile, Width, Height, aspectratio=aspectratio, **options)
    if isphotoimage:
        img = ImageTk.PhotoImage(img)
    return img
# getCacheTexture = memoize(getTexture)


def getLabel(label, font, textcolor, background=None, xpos=0, ypos=0, **options):
    SPACING = 4
    align = 'left'
    if isinstance(font, (bytes, str)):
        fnt = _eqTkFont(font)
        pass
    else:
        fnt = font
    width = options.get('width', 0)
    if options.get('haspath', False) and width:
        lblwidth = fnt.getsize(label)[0]
        if lblwidth > width:
            newfile = os.path.basename(label)
            path = os.path.dirname(label)
            drive, path = os.path.splitdrive(path)
            while True:
                path, end = os.path.split(path)
                filename = newfile
                newfile = os.path.join(end, filename)
                newpath = os.path.join(drive, os.path.sep + '...', newfile)
                if fnt.getsize(newpath)[0] > width: break
            label = os.path.join(drive, os.path.sep + '...', filename)
        pass
    elif options.get('wrapmultiline', False) and width:
        lines = label.split('\n')
        label = ''
        for line in lines:
            words = line.split(' ')
            line = ''
            for word in words:
                lblwidth = fnt.getsize(line + ' ' + word)[0]
                if lblwidth > width:
                    label += line[1:] + '\n'
                    line = ' ' + word
                else:
                    line += ' ' + word
            label += line[1:] + '\n'
            pass
        label = label[:-1]

    txt = Image.new('RGBA', (width, 10), (255, 255, 255, 0))
    d = ImageDraw.Draw(txt)
    txtsize = d.textsize(label, fnt, spacing=SPACING)
    txtsize = (txtsize[0] or (txtsize[1] + 1), txtsize[1])   # Esto es una tonteria para tener en cuenta cuando txsize[0] es 0
    bshadow = options.get('shadowcolor', None)
    if bshadow: txtsize = (1 + txtsize[0], 1 + txtsize[1])

    txt = Image.new('RGBA', txtsize, (255, 255, 255, 0))
    d = ImageDraw.Draw(txt)
    if bshadow:
        shadowcolor = options['shadowcolor']
        colorTuple = _getThemeColour(shadowcolor)
        d.text((1, 1), label, font=fnt, fill=colorTuple, align=align, spacing=SPACING)
    colorTuple = _getThemeColour(textcolor)
    d.text((0, 0), label, font=fnt, fill=colorTuple, align=align, spacing=SPACING)
    if options.get('angle', 0):
        angle = options['angle']
        txt = txt.rotate(angle, expand=1)

    if background:
        Width, Height = background.size
        imgW, imgH = txt.size
        if options.get('alignment') == 'center':
            xpos += (Width - imgW)//2
        elif options.get('alignment') == 'right':
            xpos += (Width - imgW)
        if options.get('yalignment') == 'center':
            ypos += (Height - imgH)//2

        background.paste(txt, box=(xpos, ypos), mask=txt)
    else:
        background = txt
    if options.get('isPhotoImage', False):
        background = ImageTk.PhotoImage(background)
    return background


@memoize
def staticFile(filename_url):
    if filename_url.startswith("http"):
        filename_url, headers = urllib.urlretrieve(filename_url)
    return filename_url


@memoize
def ccsCharCodeMap(css_url):
    with open(css_url, 'r') as f:
        content = f.read()
    pattern = r'^\.(fa-[a-z-]+):before\s\{\s+content:\s"\\([^"]+)";\s}$'
    charcode = re.findall(pattern, content, re.MULTILINE)
    charcode = map(lambda x: (x[0], chr(int(x[1], 16))), charcode)
    charcode = dict(charcode)
    # pattern = r'^((?:\.fa-[a-z-]+:before,\s)+)\.fa-[a-z-]+:before\s\{\s+content:\s"\\([a-f0-9]+)";'
    # alias = re.findall(pattern, content, re.MULTILINE)
    # pattern = r'\.(fa-[a-z-]+):before,\s'
    # alias = map(lambda x: (re.findall(pattern, x[0]), unichr(int(x[1], 16))), alias)
    # for seq, value in alias:
    #     aliasMap = dict.fromkeys(seq, value)
    #     charcode.update(aliasMap)
    return charcode


def fontAwesomeIcon(iconStr, **styleRequested):
    def processCSS(cssDict, cssToProcess):
        toProcess = re.findall(r'([^:]+):([^;]+);', cssToProcess)
        toProcess = map(lambda x: (x[0].strip(' \n'), x[1].strip(' \n')), toProcess)
        cssDict.update(toProcess)

    style = dict([('size', 240), ('color', 'ffff0000'), ('aspectratio', 'keep'),
                    ('isPhotoImage', False)])

    iconStr = 'fa-file fa-9x fa-ul fa-li fa-pulse'
    iconStr = iconStr.strip()
    if iconStr[:4] not in ['fas ', 'far ', 'fab ']:
        iconStr = 'fas ' + iconStr


    rootdir = os.path.dirname(__file__)
    css_url = os.path.join(rootdir, 'FontAwesome', 'fontawesome-all.css')
    css_url = staticFile(css_url)
    with open(css_url, 'r') as f:
        css_content = f.read()

    css_params = {}
    prefix, sep, iconStr = iconStr.partition(' ')
    pattern = r'@font-face\s\{([^}]+)}\s+(\.fa,)*\s\.%s' % prefix
    match = re.search(pattern, css_content, re.MULTILINE|re.DOTALL)
    processCSS(css_params, match.group(1))

    pattern = r'^\.fa[^{]*\.%s,*[^{]* \{([^{]+)\}$' % prefix
    match = re.search(pattern, css_content, re.MULTILINE|re.DOTALL)
    processCSS(css_params, match.group(1))

    pattern = r'^\.%s(:.+?)* \{(.+?)\}$'
    for iconStr in iconStr.split(' '):
        match = re.search(pattern % iconStr, css_content, re.MULTILINE|re.DOTALL)
        if match is None: continue
        processCSS(css_params, match.group(2))

    print(css_params)

    pattern = r'url\("([^(]+)"\) format\("([^(]+)"\)'
    sources = dict(map(lambda x: (x[1], x[0]), re.findall(pattern, css_params['src'])))
    ttf_file = os.path.basename(sources['truetype'])

    ttf_url = os.path.join(rootdir, 'FontAwesome', ttf_file)
    ttf_url = staticFile(ttf_url)

    style.update(styleRequested)

    charCode = chr(int(css_params['content'].strip('"\\'), 16))
    imgFont = ImageFont.truetype(ttf_url, 150)
    imageFile = getLabel(charCode, imgFont, style['color'])
    size = style.get('size')
    if isinstance(size, tuple):
        width, height = size
    else:
        width = height = size
    iconImg = getTexture(imageFile, width, height, aspectratio=style['aspectratio'])
    if style['isPhotoImage']:
        iconImg = ImageTk.PhotoImage(iconImg)
    return iconImg


def getFontAwesomeIcon(charname, **optionsreq):
    """
    parámetros:
    charname: nombre codigo del icono. ej. 'fa gear'
    optionsreq: Diccionario con las siguientes opciones
            size        : Tamaño en pixeles del icono requerido. Un entero
                          para iconos cuadrados, o una tupla con (ancho, alto). default=24
            color       : rgb color, rgb tuple. Default='white'
            isPhotoImage: True for a ImageTk.PhotoImage, default=False
    """
    options = dict([('size', 24), ('color', 'FFFFFF00'), ('aspectratio', 'keep'),
                    ('isPhotoImage', False)])
    options.update(optionsreq)
    rootdir = os.path.dirname(__file__)
    ttf_url = os.path.join(rootdir, 'FontAwesome', 'fa-solid-900.ttf')
    ttf_url = staticFile(ttf_url)
    css_url = os.path.join(rootdir, 'FontAwesome', 'fontawesome-all.css')
    css_url = staticFile(css_url)
    faMap = ccsCharCodeMap(css_url)
    charCode = faMap.get(charname)
    assert charCode is not None, '%s is not a define Font Awesome name' % charname
    imgFont = ImageFont.truetype(ttf_url, 150)
    imageFile = getLabel(charCode, imgFont, options['color'])
    size = options.get('size')
    if isinstance(size, tuple):
        width, height = size
    else:
        width = height = size
    iconImg = getTexture(imageFile, width, height, aspectratio=options['aspectratio'])
    if options['isPhotoImage']:
        iconImg = ImageTk.PhotoImage(iconImg)
    return iconImg


