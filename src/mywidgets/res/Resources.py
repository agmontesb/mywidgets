# -*- coding: utf-8 -*-
import os
import xml.etree.ElementTree as ET
import collections
import re
import inspect
from abc import abstractproperty
from PIL import Image
import itertools

from res.ResourceGenerator import android_resource_directories, \
    android_resource_tags, android_res_maping

NS_MAP = "xmlns:map"

directory_indx = lambda x: android_resource_directories.index(x)
element_indx = lambda x: android_resource_tags.index(x) + len(android_resource_directories)
rawtype_id = lambda x: (x / 16 ** 4) % 16 ** 2
rawtype_name = lambda x: (android_resource_directories + android_resource_tags)[x]
map_rawtype = lambda x: android_res_maping.get(x, x)
getClassName = lambda x: map_rawtype(rawtype_name(x))

isReference = lambda x: x[0] in ('@', '?') and (':' in x or '/' in 'x')

conf_fields = ('language', 'orientation', 'density', 'platform')
ConfContext = collections.namedtuple('ResConf', conf_fields)

class ResourceFilter(ConfContext):
    confzero = ConfContext(**dict.fromkeys(conf_fields))

    reject_patterns = confzero._replace(language=r'-([a-z]{2}-r[A-Z]{2})(?:-|$)',
                                        orientation=r'-(port|land)(?:-|$)',
                                        density=r'-(%s)(?:-|$)',
                                        platform=r'-(v[0-9]+)(?:-|$)')
    accept_patterns = confzero._replace(language=r'-([a-z]{2}-r[A-Z]{2})(?:-|$)',
                                        orientation=r'-(port|land)(?:-|$)',
                                        density=r'-([hlmxnotvany]+dpi)(?:-|$)',
                                        platform=r'-(v[0-9]+)(?:-|$)')

    @classmethod
    def makeResourceFilter(_cls, *args, **kwargs):
        defaults = dict(language='es', density='hdpi')
        if args:
            n = len(args)
            m = len(ConfContext._fields)
            n = min(m, n)
            kwargs = dict(zip(ConfContext._fields[:n], args[:n]))
        if kwargs:
            answ = dict.fromkeys(ConfContext._fields)
            answ.update(defaults)
            answ.update(kwargs)
            return _cls(**answ)

    def getRejectPatterns(self, reject_patterns, aconf):
        densities = ['ldpi', 'mdpi', 'hdpi', 'xhdpi', 'xxhdpi', 'xxxhdpi',
                     'nodpi', 'tvdpi', 'anydpi', 'nnndpi']
        indx = densities.index(aconf.density) + 1

        strDensities = '|'. join(densities[indx:])
        pattern = reject_patterns.density % strDensities
        return reject_patterns._replace(density=pattern)

    def applyRejectPatterns(self, aconf, reject_pattern, filtrado):
        compliant = filtrado
        for k in range(len(aconf)):
            if aconf[k] is None: continue
            pattern = reject_pattern[k]
            disc = lambda x: re.search(pattern, x).group(1) if re.search(pattern, x) else None
            applydisc = map(disc, compliant)
            dfilter = lambda x: x[0] == aconf[k] or x[0] is None
            wfilter = filter(dfilter, zip(applydisc, compliant))
            if not wfilter: return []
            compliant = zip(*wfilter)[1]
        return compliant

    def applyAcceptPatterns(self, aconf, accept_pattern, filtrado):
        compliant = filtrado
        for k in range(len(aconf)):
            if aconf[k] is None: continue
            pattern = accept_pattern[k]
            disc = lambda x: re.search(pattern, x).group(1) if re.search(pattern, x) else None
            applydisc = map(disc, compliant)
            vconf = re.search(pattern, '-' + aconf[k])
            vconf = vconf.group(1) if vconf else None
            dfilter = lambda x: x[0] == vconf
            wfilter = filter(dfilter, zip(applydisc, compliant))
            if not wfilter: return []
            compliant = zip(*wfilter)[1]
        return list(compliant)

    def __call__(self, tofilter, aconf=None):
        aconf = aconf or self
        rejectPattern = self.getRejectPatterns(self.reject_patterns, aconf)
        accept_patterns = self.accept_patterns._replace(density=rejectPattern.density)
        postReject = self.applyRejectPatterns(aconf, rejectPattern, tofilter)
        postAccept = self.applyAcceptPatterns(aconf, accept_patterns, postReject)
        return  postAccept


class Pointers(object):
    @abstractproperty
    def basepath(cls):
        pass

    def __init__(self):
        basepath = self.basepath
        resourcepath, directories, files = next(os.walk(basepath))
        self.resmap = resmap = {}
        for resdir in directories:
            prefix = resdir.split('-', 1)[0]
            members = resmap.setdefault(prefix, [])
            members.append(resdir)

    def _getResEntry(self, classname, pointer):
        obj = getattr(self, classname)
        idmap = dict((x[1], x[0]) for x in obj.__dict__.items() if not x[0].startswith('__'))
        try:
            return idmap[pointer].replace('__', '.')
        except KeyError:
            return '@na'

    def _mapid(self, pointer):
        restype = rawtype_id(pointer)
        classname = getClassName(restype)
        try:
            android_resource_directories[restype]
        except:
            if classname == 'id':
                fname = self._getResEntry(classname, pointer)
                fext, respos = '', None
            else:
                pointer, respos = self._valueids[pointer]
                classname = 'values'
                fname = self._values_[pointer]
                fext = self._fext_[0]
        else:
            fname = self._getResEntry(classname, pointer)
            resid = (pointer % 16 ** 4) / 16 ** 3
            fext = self._fext_[resid]
            respos = None
        return classname, '%s.%s' % (fname, fext), respos


class Resources(object):
    def __init__(self, context, resfilter=None, *args, **kwargs):
        super(Resources, self).__init__(*args, **kwargs)
        self.packageR = self.findResourcePointers(context)
        self.filter = resfilter
        pass

    def findResourcePointers(self, context):
        head = []
        tail = []
        out = []
        for name, x in context.items():
            if inspect.ismodule(x) and hasattr(x, 'R') and isinstance(x.R, Pointers):
                toappend = (name, x.R)
            elif isinstance(x, Pointers):
                toappend = (name, x)
            else:
                continue
            if name == 'R':
                head = [toappend]
            elif name == 'android':
                tail = [toappend]
            else:
                out.append(toappend)
        return head + out + tail

    def parse_nsmap(file):
        events = "start", "start-ns", "end-ns"
        root = None
        ns_map = []
        for event, elem in ET.iterparse(file, events):
            if event == "start-ns":
                ns_map.append(elem)
            elif event == "end-ns":
                ns_map.pop()
            elif event == "start":
                if root is None:
                    root = elem
                elem.set(NS_MAP, dict(ns_map))
        return ET.ElementTree(root)

    def _getValueFromString(self, xval, formato):
        if isReference(xval): return xval
        if formato == 'color':
            return xval[1:]
        if formato == 'boolean':
            return xval == 'true'
        if formato == 'dimension':
            pattern = r'([-+0-9.]+)(px|in|mm|dip|dp|sp)*'
            match = re.match(pattern, xval)
            value, units = match.groups()
            # value, units

            if units is None or units in ('dp', 'px', 'dip', 'sp'):
                answ = float(value)
            elif units == 'in':
                answ = 160 * float(value)
            elif units == 'mm':
                answ = 160 * float(value) / 25.4
            else:  # units == 'pt':
                answ = 160 * (1.0 / 72) * float(value)
            return answ
        if formato == 'float':
            return float(xval)
        if formato == 'integer':
            return int(xval)
        if formato == 'string':
            return xval
        if formato == 'fraction':
            return float(xval.rstrip('%p')) / 100

    def _unpack_pointer(self, pointer, reqtype = (None,)):
        pckname, R = self._getResourcePointer(pointer)
        if not isinstance(reqtype, tuple): reqtype = (reqtype,)
        restype = rawtype_id(pointer)
        if reqtype[0] and restype not in reqtype: raise LookupError('Identifier not the require type')
        classname, filename, respos = R._mapid(pointer)
        if classname == 'id':
            idname = '@%s:id/%s' % (pckname, filename[:-1]) \
                if pckname != 'R' else \
                '@id/%s' % filename[:-1]
            return (idname, 'id')

        filtrado = sorted(R.resmap[classname])
        if self.filter:
            filtrado = self.filter(filtrado)
            if classname in R.resmap[classname] and classname not in filtrado:
                filtrado.append(classname)

        basepath = R.basepath
        for filedir in filtrado:
            fullname = os.path.join(basepath, filedir, filename)
            if not os.path.exists(fullname): continue
            try:
                answ = fullname
                if respos is not None:
                    tag = rawtype_name(restype)
                    classname = getClassName(restype)
                    entry = R._getResEntry(classname, pointer)
                    xpath = "./%s[@name='%s']" % (tag, entry)
                    if classname == 'attr':
                        xpath = './' + xpath[1:]
                    root = ET.parse(answ).getroot()
                    answ = root.find(xpath)
                    if answ is None: raise LookupError('Identifier not found')
            except:
                pass
            else:
                break
        else:
            raise LookupError('Resource not for this configuration')

        return answ

    def finishPreloading(self):
        pass

    def flushLayoutCache(self):
        pass

    def getAnimation(self, id):
        pass

    def getAssets(self):
        pass

    def getBoolean(self, id):
        restype = element_indx('bool')
        xval =  self._unpack_pointer(id, restype).text
        return self._getValueFromString(xval, 'boolean')

    def getColor(self, id, theme=None):
        restype = element_indx('color')
        rgb = self._unpack_pointer(id, restype).text
        return self._getValueFromString(rgb, 'color')

    def getColorStateList(self, id, theme=None):
        restype = directory_indx('color')
        return self._unpack_pointer(id, restype)

    def getConfiguration(self):
        pass

    def getDimension(self, id):
        restype = element_indx('dimen')
        xval = self._unpack_pointer(id, restype).text
        return self._getValueFromString(xval, 'dimension')

    def getDimensionPixelOffset(self, id):
        pass

    def getDimensionPixelSize(self, id):
        pass

    def getDisplayMetric(self):
        pass

    def getDrawable(self, id, theme=None):
        restype = (directory_indx('drawable'), element_indx('drawable'))
        drawablefile = self._unpack_pointer(id, restype)
        try:
            image = Image.open(drawablefile)
            return image
        except Exception as e:
            if isinstance(drawablefile, (bytes, str)):
                with open(drawablefile, 'rb') as f:
                    xmlstr = f.read()
                return ET.XML(xmlstr)
        return drawablefile

    def getDrawableForDensity(self, id, density, theme=None):
        genfilter = self.filter
        densityfilter = lambda x: filter(lambda y: y == 'drawable-' + density, x)
        self.filter = densityfilter
        answ = self.getDrawable(id, theme)
        self.filter = genfilter
        return answ

    def getFont(self, id):
        restype = directory_indx('font')
        fontfile = self._unpack_pointer(id, restype)
        return fontfile

    def getFraction(self, id, base=1, pbase=1):
        restype = element_indx('fraction')
        fraction = self._unpack_pointer(id, restype).text
        bflag = fraction.endswith('p')
        fraction = self._getValueFromString(fraction, 'fraction')
        fbase = pbase if bflag else base
        return fbase*fraction

    def getIdentifier(self, name, defType='id', defPackage='R'):
        pck = group = entry = None
        x = name.replace('.', '__').strip('@+').split('/')
        if len(x) == 2:
            x, entry = x[0].split(':'), x[1]
            if len(x) == 2:
                pck, group = x
            else:
                group = x[0]
        else:
            entry = x[0]
        group = group or defType
        pck = pck or defPackage

        try:
            R = dict(self.packageR)[pck]
            return eval('R.%s.%s' % (group, entry))
        except Exception as e:
            return 0

    def getIntArray(self, id):
        restype = element_indx('integer-array')
        array = [x.text for x in self._unpack_pointer(id, restype)]
        return map(lambda x:self._getValueFromString(x, 'integer'), array)

    def getInteger(self, id):
        restype = element_indx('integer')
        xval = self._unpack_pointer(id, restype).text
        return self._getValueFromString(xval, 'integer')

    def getQuantityString(self, id):
        restype = element_indx('plurals')
        return self._unpack_pointer(id, restype)[0].text

    def getLayout(self, id):
        restype = directory_indx('layout')
        layoutfile = self._unpack_pointer(id, restype)
        with open(layoutfile, 'rb') as f:
            xmlstr = f.read()
        return ET.XML(xmlstr)

    def getResourceEntryName(self, resid):
        resname = self.getResourceName(resid)
        return resname.split('/')[-1]

    def getResourceName(self, resid):
        package, R = self._getResourcePointer(resid)
        classname = self.getResourceTypeName(resid)
        entry = R._getResEntry(classname, resid)
        answ = '@%s/%s' % (classname, entry)
        if package != 'R': answ = answ.replace('@', '@%s:' % package)
        return answ

    def _getResourcePointer(self, resid):
        rgprefix = resid/16**6
        aiter = itertools.dropwhile(lambda x: x[1].rid != rgprefix, self.packageR)
        try:
            return aiter.next()
        except Exception as e:
            raise LookupError('Resource ID not in this package')

    def getResourcePackageName(self, resid):
        pckname, _ = self._getResourcePointer(resid)
        return pckname

    def getResourceTypeName(self, resid):
        try:
            restype = rawtype_id(resid)
            return  getClassName(restype)
        except:
            raise LookupError('Resource ID not in this package')

    def getString(self, id):
        restype = element_indx('string')
        xval = self._unpack_pointer(id, restype).text
        return self._getValueFromString(xval, 'string')

    def getSystem(self):
        pass

    def getStringArray(self, id):
        restype = element_indx('string-array')
        sarray = [x.text for x in self._unpack_pointer(id, restype)]
        return map(lambda x: self._getValueFromString(x, 'string'), sarray)

    def getText(self, id, default=None):
        pass

    def getTextArray(self, id):
        pass

    def getValue(self, nameorid, outvalue, resolveRefs=False):
        fresource1 = ['_unpack_pointer', 'getAnimation',
                                        'getColorStateList', 'getDrawable',
                                        'getLayout', '_unpack_pointer', '_unpack_pointer', 'openRawResourceFd',
                                        'values', 'getXml', 'getFont',
                                        'getAnimation', 'getAnimation']
        fresource2 = ['getBoolean', 'getColor', 'getDimension', 'id', 'getFraction',
                        'getInteger', 'getIntArray',
                        'obtainTypedArray', '_unpack_pointer', '_unpack_pointer', 'declare-styleable',
                        'getString', 'getStringArray', 'getQuantityString']
        fresource = fresource1 + fresource2 + fresource1
        while True:
            if isinstance(nameorid, (bytes, str)):
                nameorid = self.getIdentifier(nameorid, defType='string')
            if not isinstance(nameorid, int):
                raise IOError('nameorid not a string or integer')
            restype = rawtype_id(nameorid)
            if fresource[restype] == 'id' or not resolveRefs: return nameorid
            method = getattr(self, fresource[restype])
            answ = method(nameorid)
            # if not resolveRefs: break
            if fresource[restype] in ['obtainTypedArray', 'getStringArray', 'getString']:
                pck = self.getResourcePackageName(nameorid)
                for k in range(len(answ)):
                    if isinstance(answ[k], (bytes, str)) and answ[k].startswith('@'):
                        if pck != 'R' and ':' not in answ[k]:
                            answ[k] = answ[k].replace('@', '@%s:' % pck)
                        answ[k] = self.getValue(answ[k], None, resolveRefs=True)
            if not isinstance(answ, (bytes, str)): break
            if not answ.startswith('@'): break
            nameorid = answ
        return answ

    def getValueForDensity(self, id, density, outvalue, resolveRefs=False):
        if isinstance(id, (bytes, str)):
            id = self.getIdentifier(id)
        pckname, R = self._getResourcePointer(id)
        resdir = R._mapid(id)[0]
        genfilter = self.filter
        densityfilter = lambda x: filter(lambda y: y == resdir + '-' + density, x)
        self.filter = densityfilter
        answ = self.getValue(id, outvalue, resolveRefs)
        self.filter = genfilter
        return answ

    def getXml(self, id):
        restype = directory_indx('xml')
        xmlfile = self._unpack_pointer(id, restype)
        with open(xmlfile, 'rb') as f:
            xmlstr = f.read()
        return ET.XML(xmlstr)

    def newTheme(self):
        pass

    def obtainAtributes(self, aset, attrs, resolveRefs=False):
        def styleableDef(styleableIds, xmlns=None):
            attrs_name = []
            restype = element_indx('attr')
            xmlns = xmlns or {}
            nameStr = '{{0}}:{1}' if xmlns else '{1}'
            for pointer in styleableIds:
                assert rawtype_id(pointer) == restype, "Not an attr resource"
                pckname, R = self._getResourcePointer(pointer)
                entry = R._getResEntry('attr', pointer)
                attrs_name.append(nameStr.format(pckname, entry))
            return attrs_name

        def getAttrData(pointer, prevfilename, root):
            pckname, R = self._getResourcePointer(pointer)
            dirname, filename, respos = R._mapid(pointer)
            entry = R._getResEntry('attr', pointer)
            if filename != prevfilename:
                prevfilename = filename
                fullname = os.path.join(R.basepath, dirname, filename)
                root = ET.parse(fullname).getroot()
            xpath = ".//%s[@name='%s']" % ('attr', entry)
            attr = root.find(xpath)
            name, formato, globs = attr.get('name'), attr.get('format'), None
            if formato is None:
                value = []
                for enum in list(attr):
                    value.append((enum.get('name'), eval(enum.get('value'))))
                formato, globs = enum.tag, dict(value)
            return formato, globs, filename, root

        prevfilename, root = '', None
        attrs_name = styleableDef(attrs)
        toprocess = list(set(aset).intersection(attrs_name))
        npos = [attrs_name.index(x) for x in toprocess]
        toprocess = sorted(zip(npos, toprocess))
        values = len(attrs) * [None]
        for indx, attr in toprocess:
            xval = aset[attr]
            formato, glob, prevfilename, root = getAttrData(attrs[indx], prevfilename, root)
            if not isinstance(glob, dict):
                formatos = formato.replace(' ', '').split(',')
                for formato in formatos:
                    try:
                        if xval.startswith('@') and '/' in xval:
                            xval = self.getValue(xval, None, resolveRefs=resolveRefs)
                            break
                        else:
                            if formato == 'reference': continue
                        xval = self._getValueFromString(xval, formato)
                    except Exception as e:
                        continue
                    else:
                        break
            else:
                xval = eval(xval, glob)
            values[indx] = xval
        return values

    def obtainAtributesOLD(self, aset, attrs):
        def styleableDef(styleableIds):
            style_lst = []
            restype = element_indx('attr')
            for styleid in styleableIds:
                attr = self._unpack_pointer(styleid, restype)
                name, formato, globs = attr.get('name'), attr.get('format'), None
                if formato is None:
                    value = []
                    for enum in list(attr):
                        value.append((enum.get('name'), eval(enum.get('value'))))
                    formato, globs = enum.tag, dict(value)
                style_lst.append((name, (formato, globs)))
            return style_lst

        style_attrs = collections.OrderedDict(styleableDef(attrs))
        values = len(attrs) * [None]
        toprocess = set(aset).intersection(style_attrs)
        keys = style_attrs.keys()
        for attr in toprocess:
            xval = aset[attr]
            indx = keys.index(attr)
            formato, glob = style_attrs[attr]
            if not isinstance(glob, dict):
                formatos = formato.replace(' ', '').split(',')
                for formato in formatos:
                    try:
                        if xval.startswith('@'):
                            if formato in ('reference', 'string'):
                                xval = self.getValue(xval, None, resolveRefs=True)
                                break
                        else:
                            if formato == 'reference': continue
                        xval = self._getValueFromString(xval, formato)
                    except Exception as e:
                        xval = str(e)
                    break
            else:
                xval = eval(xval, glob)
            values[indx] = xval
        return values

    def obtainTypedArray(self, id):
        restype = element_indx('array')
        y = self._unpack_pointer(id, restype)
        return [x.text for x in y.iter('item')]

    def openRawResourceFd(self, id):
        restype = directory_indx('raw')
        rawfile = self._unpack_pointer(id, restype)
        return open(rawfile, 'rb')

    def parseBundleExtra(self, tagName, attrs, outBundle):
        pass

    def parseBundleExtras(self, parser, outBundle):
        pass

    def updateConfiguration(self, config, metrics):
        pass





