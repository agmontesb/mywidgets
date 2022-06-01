# -*- coding: utf-8 -*-
import importlib

import re
import pkg_resources
import pickle
import os
import xml.etree.ElementTree as ET

# Directorios
android_resource_directories = ['animator', 'anim',
                                'color', 'drawable',
                                'layout', 'menu', 'mipmap', 'raw',
                                'values', 'xml', 'font',
                                'interpolator', 'transition']

android_element_name = ['bool', 'color', 'dimen', 'id', 'fraction',
                        'integer', 'integer-array',
                        'array', 'attr', 'style', 'declare-styleable',
                        'string', 'string-array', 'plurals']

android_res_maping = dict([('integer-array', 'array'), ('string-array', 'array'),
                           ('interpolator', 'anim'),
                           ('transition', 'anim')])


# Resources derivados de values
android_resource_tags = android_element_name + android_resource_directories

classTemplate = """
    class {classname}(object):
<classbody>
<classdef>"""

_template1 = """# -*- coding: utf-8 -*-
import os
from res.Resources import Pointers, Resources


class ResourcePointers(Pointers):    
    @property
    def basepath(cls):
        basepath = os.path.dirname(__file__)
        relPathToResDirectory = r'<relpathtoresdirectory>'
        respath = os.path.join(basepath, relPathToResDirectory)
        return os.path.realpath(respath)
<classdef>


R = ResourcePointers()
R.rid = <resourceid>
"""

_template2 = """# -*- coding: utf-8 -*-
import os
from Android.Resources import Pointers, Resources


class ResourcePointers(Pointers):
    @property
    def basepath(cls):
        respath = r'<relpathtoresdirectory>'
        return respath
<classdef>


R = ResourcePointers()
R.rid = <resourceid>
"""

idtemplate = '0x{:0>2x}{:0>2x}{:0>4x}'
postemplate = '0x{:0>8x}'
xmlns = dict(android="http://schemas.android.com/apk/res/android",
             app="http://schemas.android.com/apk/res-auto")


def filesin(resdir, resmap, respath):
    '''
    Entrega lista de tuple en que se tiene nombre de archivo y primer directorio
    en que se encuentra
    '''
    unique = set()
    out = []
    items = sorted(filter(lambda x: x[1], resmap[resdir]))
    updateFlag = all(list(zip(*resmap[resdir]))[1])
    for item, scanFlag in items:
        dpath = os.path.join(respath, item)
        ldir = map(lambda x: (x, item), os.listdir(dpath))
        ldir = [x for x in ldir if x[0] not in unique]
        unique = unique.union([x[0] for x in ldir])
        out.extend(ldir)
    if updateFlag:
        unique = set(list(zip(*out))[1])
        resmap[resdir] = [(x[0], 1 if x[0] in unique else 0) for x in resmap[resdir]]
    return sorted(out)


def processres(rgprefix, classname, resmap, respath, classmapping):
    extmap = []
    restype = android_resource_directories.index(classname)
    respairs = classmapping.setdefault(classname, [])
    ids = classmapping.setdefault('id', set())
    lista = filesin(classname, resmap, respath)
    for fileid, x in enumerate(lista):
        hexval = idtemplate.format(rgprefix, restype, fileid)
        (reskey, fext), resval = os.path.splitext(x[0]), hexval
        fkey, fval = x[0].split('.', 1)
        respairs.append((fkey, resval))
        if fext != '.xml':
            extmap.append((resval, fval))
            continue
        if classname == 'values':
            continue
        filename = os.path.join(respath, x[1], x[0])
        print(x[1], x[0])
        with open(filename, 'rb') as f:
            xmlstr = f.read()
            xmlns = re.findall(b'xmlns:([^=]+)="([^"]+)', xmlstr)
            xmlns = dict(xmlns)
            root = ET.fromstring(xmlstr)
        xpath = "[@android:id]" if xmlns.get('android') else "[@id]"
        elementid = root.findall('.' + xpath, xmlns)
        elementid += root.findall('.//*' + xpath, xmlns)
        key = '{%s}%s' % (xmlns['android'], 'id') if xmlns.get('android') else 'id'
        id_map = dict((x.get(key), x) for x in elementid)

        for resid, item in enumerate(id_map.items()):
            prefix = item[0].split('/')[0]
            key = item[0].split('/')[-1]
            ids.add(key)
    return extmap


def processvalues(rgprefix, classname, resmap, respath, values):
    """Se procesa el diretorio valores"""
    restype = android_resource_directories.index(classname)
    lista = filesin(classname, resmap, respath)
    valueids = {}
    for fileid, x in enumerate(lista):
        if x[0] in ('public.xml', 'symbols.xml'):
            continue
        hexval = idtemplate.format(rgprefix, restype, fileid)
        filename = os.path.join(respath, x[1], x[0])
        if x[0].startswith('attrs'):
            values = processattrs(hexval, filename, values, valueids)
            continue
        root = ET.parse(filename).getroot()
        for resid, node in enumerate(list(root)):
            tag = node.tag
            if not node.attrib:
                continue
            if tag == 'item':
                tag = node.get('type')
                if tag == 'id':
                    tagmap = values.setdefault('id', set())
                    tagmap.add(node.get('name'))
                    continue
            tagmap = values.setdefault(tag, [])
            restag = android_resource_tags.index(tag)
            restag += len(android_resource_directories)
            key = node.get('name').replace('.', '__')
            pointer = idtemplate.format(rgprefix, restag, len(tagmap))
            tagmap.append((key, pointer))
            valueids[pointer] = (hexval, 1)
    return valueids


def processattrs(hexval, filepath, values, valueids):
    rgprefix = int(hexval[2:4], 16)
    restag = android_resource_tags.index('attr')
    restag += len(android_resource_directories)
    groupmembers = dict(values.setdefault('styleable', []))
    attrids = dict(values.setdefault('attr', []))
    root = ET.parse(filepath).getroot()
    for resid, attrelem in enumerate(root.findall('.//attr')):
        if attrelem.get('format') is None and len(attrelem) == 0: continue
        key = attrelem.get('name')
        pointer = idtemplate.format(rgprefix, restag, len(attrids))
        attrids[key] = pointer
        valueids[pointer] = (hexval, resid)

    for styleable in root.findall('.//declare-styleable'):
        name = styleable.get('name')
        members = [x.get('name') for x in styleable.findall('.//attr')]
        groupmembers[name] = members

    values['attr'] = attrids.items()
    values['styleable'] = groupmembers.items()
    return values


def _create_resource_manager(packagename, resourcepath=None, resman=None):
    '''

    :param packagename:
    :param resourcepath:
    :param resman:
    :return:
    '''
    modulesource = importlib.import_module(packagename)
    basepath = os.path.dirname(modulesource.__file__)
    # OJO: Solo durante desarrollo
    basepath = '/mnt/c/Users/Alex Montes/PycharmProjects/mywidgets/src/res'
    modulename = os.path.join(basepath, '%sManager.py' % packagename)
    resourcepath = resourcepath or basepath
    if not resourcepath.endswith('res'):
        resourcepath = os.path.join(resourcepath, 'res')

    resourcepath, directories, files = next(os.walk(resourcepath))
    resmap = {}
    for resdir in directories:
        prefix = resdir.split('-', 1)[0]
        members = resmap.setdefault(prefix, [])
        members.append((resdir, 1))

    pckname = os.path.basename(modulename)
    pckname = os.path.splitext(pckname)[0].lower()

    pkgargs = (__name__, 'data/resmanager_ids.txt')
    pkgfilename = pkg_resources.resource_filename(*pkgargs)
    if pkg_resources.resource_exists(*pkgargs):
        with open(pkgfilename, 'rb') as f:
            rgpmap = pickle.load(f)
    else:
        rgpmap = {}

    rgpdef = max(rgpmap.values() or [0]) + 1
    rgprefix = rgpmap.setdefault(pckname, rgpdef)

    if rgpmap[pckname] == rgpdef:
        # with open(pkgfilename, 'wb') as f:
        #     pickle.dump(rgpmap, f)
        pass
    try:
        relpath = os.path.relpath(resourcepath, basepath)
    except ValueError:
        module = _template2.replace('<relpathtoresdirectory>', resourcepath)
    else:
        module = _template1.replace('<relpathtoresdirectory>', relpath)
    module = module.replace('<resourceid>', '0x{:0>2x}'.format(rgprefix))

    # Se entran a procesar los diferentes tipos de recursos de acuerdo al archivo que se encuentra
    # definido
    classmapping = dict(id=set(), styleable=[])
    classnames = sorted(resmap.keys())
    extmap = []
    for aclass in classnames:
        dextmap = processres(rgprefix, aclass, resmap, resourcepath, classmapping)
        extmap.extend(dextmap)

    toswap = [(x, y) for x, y in android_res_maping.items() if x in classmapping]
    for fromclass, toclass in toswap:
        members = classmapping.setdefault(toclass, [])
        members.extend(classmapping.pop(fromclass))

    _fext_ = ['xml']
    if extmap:
        hexval, fext = zip(*sorted(extmap))
        _fext_.extend(sorted(set(fext)))
        assert len(_fext_) <= 15, "The number of types of resource files is greater than 16"
        ptype = 0
        for k in range(len(fext)):
            indx = _fext_.index(fext[k])
            restype = int(hexval[k][4:6], 16)
            if restype != ptype:
                if ptype != 0:
                    classmapping[classname] = zip(class_attrs, attr_vals)
                ptype = restype
                classname = android_resource_directories[restype]
                class_attrs, attr_vals = zip(*classmapping[classname])
                class_attrs = list(class_attrs)
                attr_vals = list(attr_vals)
            npos = attr_vals.index(hexval[k])
            newhexval = attr_vals[npos][:6] + '%x' % indx + attr_vals[npos][7:]
            attr_vals[npos] = newhexval
        else:
            classmapping[classname] = zip(class_attrs, attr_vals)

    valueids = {}
    _values_ = []
    if 'values' in classmapping:
        _values_ = classmapping.pop('values')
        valueids = processvalues(rgprefix, 'values', resmap, resourcepath, classmapping)
        toswap = [(x, y) for x, y in android_res_maping.items() if x in classmapping]
        for fromclass, toclass in toswap:
            members = classmapping.setdefault(toclass, [])
            members.extend(classmapping.pop(fromclass))

    defineids = classmapping.pop('id')
    styleable = classmapping.pop('styleable')

    """ Se generan los styleables"""
    attr = dict(classmapping.setdefault('attr', []))
    classbody = []
    for key1, value1 in sorted(styleable):
        if not resman:
            trnfunc = lambda x: "'@%s'" % x.replace(':', ':attr/') if ':' in x else attr.get(x, 'None')
        else:
            rid = resman.getIdentifier
            trn1 = lambda x: postemplate.format(rid('@%s' % x.replace(':', ':attr/')))
            trn2 = lambda x: attr.get(x, 'None')
            trnfunc = lambda x: trn1(x) if ':' in x else trn2(x)
        attridstr = map(trnfunc, value1)
        classbody.append((key1, '[' + ', '.join(attridstr) + ']'))
        members = [(key1 + '_' + x.replace(':', '_'), k) for k, x in enumerate(value1)]
        for key2, value2 in members:
            classbody.append((key2, value2))
    classmapping['styleable'] = classbody

    classbody = []
    """Se entran a generar los id para los declarados"""
    for resid, key in enumerate(sorted(defineids)):
        restype = android_resource_tags.index('id') + len(android_resource_directories)
        hexval = idtemplate.format(rgprefix, restype, resid)
        if ':' in key:
            if resman:
                rid = resman.getIdentifier
                hexval = postemplate.format(rid('@%s' % key.replace(':', ':id/')))
            else:
                hexval = "'@%s'" % key.replace(':', ':id/')
            key = key.split(':')[-1]
        key = key.split('/')[-1]
        classbody.append((key, hexval))
    classmapping['id'] = classbody

    for keyclass in sorted(classmapping):
        class_str = classTemplate.format(classname=keyclass.lower())
        strFmt = "        %s = %s"
        classpairs = classmapping[keyclass]
        if not classpairs: continue
        if keyclass != 'styleable':
            classpairs = sorted(classpairs)
        classbody = [strFmt % (key, value) for key, value in classpairs]
        classbody = '\n'.join(classbody)
        class_str = class_str.replace('<classbody>', classbody)
        module = module.replace('<classdef>', class_str)

    if valueids:
        strFmt = "                 {}: ({}, {}),"
        classbody = [strFmt.format(key, *value) for key, value in sorted(valueids.items())]
        classbody = '\n'.join(classbody)
        classbody = '\n    _valueids = {\n' + classbody + '\n                }\n<classdef>'
        module = module.replace('<classdef>', classbody)

    if _values_:
        strFmt = "                {1}: '{0}',"
        classbody = [strFmt.format(key, value) for key, value in sorted(_values_)]
        classbody = '\n'.join(classbody)
        classbody = '\n    _values_ = {\n' + classbody + '\n                }\n<classdef>'
        module = module.replace('<classdef>', classbody)

    if _fext_:
        _fext_ = map(lambda x: "'%s'" % x, _fext_)
        classbody = strFmt = "\n    _fext_ = [%s]\n<classdef>" % ', '.join(_fext_)
        module = module.replace('<classdef>', classbody)
    module = module.replace('<classdef>', '')

    with open(modulename, 'w') as f:
        f.write(module)

    return modulename


if __name__ == '__main__':
    packagename = 'Tools'
    resourcepath = '/mnt/c/Users/Alex Montes/PycharmProjects/AndroidApps/TestActivity/res'
    resman = None
    _create_resource_manager(packagename, resourcepath=resourcepath, resman=resman)
