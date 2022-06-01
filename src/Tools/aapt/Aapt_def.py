# -*- coding: utf-8 -*-
import ctypes
import os
import sys
import io
import zipfile
import contextlib
import codecs
from collections import namedtuple
import functools
from ctypes import *

import Tools.aapt.ResourcesTypes as ru


def cprint(*args, sep=' ', end='\n', sfile=sys.stdout, flush=False, to_string=None):
    if isinstance(to_string, list):
        line = sep.join(args) + end
        to_string.append(line)
    else:
        print(*args, sep=sep, end=end, file=sfile, flush=flush)


def printHeader(base=16, to_string=''):
    headerStr = ' '.join(['OFFSET  '] + ['{:0>2x}'.format(x).upper() for x in range(base)])
    sepStr = lambda k: ('-' if k == 2 else '').join([k * '-' if (x + 1) % 4 else k * '+' for x in range(base)])
    cprint(len(headerStr) * '-', to_string=to_string)
    cprint(headerStr, to_string=to_string)
    cprint(8 * '-' + '-' + sepStr(2) + '   ' + sepStr(1), to_string=to_string)


def printHexIoData(data, offset, size=-1, base=16, shift=0, label='', to_string=''):
    offset = offset or 0
    assert data.seek(offset) == offset
    size = 0x7FFF if size < 0 else size
    linf = shift // base
    lsup = (size - 1) // base + 1
    for nlin in range(linf, lsup):
        colinf = (shift % base) if shift and nlin == linf else 0
        colsup = min(base * (nlin + 1), size) - base * nlin
        codes = ((colsup - colinf) * c_uint8)()
        breaded = data.readinto(codes)
        lsup = min(breaded, colsup - colinf)
        pos = map(lambda x: '{:0>2x}'.format(x).upper(), codes[:lsup])
        chars = label or ''.join(map(lambda x: chr(x) if 31 < x < 127 else '.', codes[:lsup]))
        saddr = '{:0>8x}'.format(base * nlin)
        cprint(saddr + ' ' + colinf * '   ' + ' '.join(pos) + (base - colsup + 1) * '   ' + chars, to_string=to_string)
        if lsup < colsup - colinf:
            break


@contextlib.contextmanager
def ioData(data=None, offset=0, output=None, to_string=None):
    dataFlag = bool(data)
    if dataFlag:
        closeFlag = False
        if not hasattr(data, 'readinto'):
            if isinstance(data, (bytes, str)):
                if os.path.exists(data):
                    data = io.FileIO(data, 'rb')
                    closeFlag = True
                else:
                    data = io.BytesIO(data)
            else:
                raise ArgumentError('data must be an io object or a raw string')
        dataPtr = data.tell()
        offset += dataPtr
        data.seek(offset)
    outFlag = isinstance(output, (bytes, str)) or isinstance(to_string, list)
    if outFlag:
        global cprint
        def dec_closure(file_obj, to_string):
            def dec_function(f):
                @functools.wraps(f)
                def wrapper(*args, **kwargs):
                    kwargs['sfile'] = file_obj
                    kwargs['to_string'] = to_string
                    return f(*args, **kwargs)
                return wrapper
            return dec_function
        if output:
            output = codecs.getwriter('utf-8')(open(output, 'wb'))
        cprint = dec_closure(output, to_string)(cprint)
    try:
        yield data if dataFlag else None
    finally:
        if outFlag:
            output and output.close()
            if isinstance(to_string, list):
                # en este punto se tiene que cprint esta 'decorated' por lo cual debemos 'undecorate'
                # esta función, un método es este
                cprint = cprint.__wrapped__
        if dataFlag:
            if closeFlag:
                data.close()
            else:
                data.seek(dataPtr)


def dumpHexData(data, offset=0, size=-1, base=16, outFile=None, to_string=''):
    with ioData(data, offset, output=outFile, to_string=to_string) as iodata:
        cprint('BASE = {:0>8x}'.format(iodata.tell()))
        printHeader(base, to_string=to_string)
        printHexIoData(iodata, iodata.tell(), size, base)


def ctypeStructTable(data, ctypeStruct, offset, shift=0, lprefix=''):
    ctypeStruct_inst = ru.readResHeader(data, ctypeStruct, offset=offset + shift)
    return ctypeInstanceTable(ctypeStruct_inst, shift=shift, lprefix=lprefix)


def ctypeInstanceTable(ctypeStruct_inst, shift=0, lprefix=''):
    base = 16
    answ = []
    ctypeStruct = type(ctypeStruct_inst)
    for fname, fclass in ctypeStruct._fields_:
        field = getattr(ctypeStruct, fname)
        value = getattr(ctypeStruct_inst, fname)
        if issubclass(fclass, (Structure, Union)):
            dshift = shift + field.offset
            bflag = lprefix.endswith('.*')
            if bflag:
                label = lprefix[:-2]
            if issubclass(fclass, Structure):
                if not bflag:
                    label = ('' if not lprefix else (lprefix + '.')) + fname
                    answ.append((label, None, dshift // base, dshift % base, sizeof(value)))
            else:
                label = lprefix.rstrip('.*') + '.*'      # El asterisco indica que esta instance deriva de una Union
            dansw = ctypeInstanceTable(value, shift=dshift, lprefix=label)
            answ.extend(dansw)
        else:
            if lprefix.endswith('.*'):
                lprefix = lprefix[:-2]
            label = ('' if not lprefix else (lprefix + '.')) + fname
            field_offset = shift + field.offset
            saddr = (field_offset // base)
            loff = field_offset % base
            size = field.size
            answ.append((label, value, saddr, loff, size))
    return answ


def dumpHexCtypeStruct(data, ctypeStruct, offset=0, outFile=None, shift=0, pheader=True, lprefix='', to_string=''):
    base = 16
    if pheader:
        printHeader(base=base, to_string=to_string)
    table = ctypeStructTable(data, ctypeStruct, offset, shift=shift, lprefix=lprefix)
    for field_name, field_value, field_nlin, field_off, field_size in table:
        p_pos = offset + shift + base * field_nlin + field_off
        byte_array = ru.readResHeader(data, (field_size * ctypes.c_uint8), offset=p_pos)
        byte_array = ' '.join(map(lambda x: "{:0>2x}".format(x).upper(), byte_array))
        saddr = base * field_nlin
        out_str = f'{field_off * "   "}{byte_array}'
        suffix = f'{field_name} {field_value} {field_size}'
        nlines = (len(out_str) - 1) // (3 * base) + 1
        for nlin in range(nlines):
            to_print = out_str[(3 * base) * nlin: (3 * base) * (nlin + 1)]
            roff = max(base * 3 - len(to_print), 0)
            cprint(f'{saddr:0>8x} {to_print}{roff * " "}  {suffix}', to_string=to_string)
            suffix = ''
            saddr += base
    if pheader:
        size = sizeof(ctypeStruct)
        data.seek(0)
        dumpHexData(data, offset=offset, size=size, base=base, outFile=outFile, to_string=to_string)


def aapt(**kwargs):
    aaptArgs = dict(
        action='',
        v=False,
        a=False,
        filename='',
        logFile=None,
        values=None,
        include_meta_data=False,
        what='',
        assets=[]
    )
    aaptArgs.update(**kwargs)
    Args = type('Args', (object,), aaptArgs)
    # Checking positional args
    if Args.action not in ['crawl', 'l', 'list', 'd', 'dump']:
        raise ArgumentError('Valid actions are "l[ist]", "d[ump]"')
    if os.path.splitext(Args.filename)[-1] not in ['.zip', '.jar', '.apk']:
        raise ArgumentError('Valid files are "zip", "jar" and "apk"')
    with ioData(output=Args.logFile):
        if Args.action in ['l', 'list']:
            if not (Args.v or Args.a):
                nopt = 1
            elif Args.a:
                nopt = 2
            elif Args.v:
                nopt = 0
            listApk(Args.filename, opt=nopt)
            return
        zf = zipfile.ZipFile(Args.filename)
        targetFunc = None
        args = ()
        kwargs = {}
        if Args.action == 'crawl':
            targetFunc = ResTableCrawler
            Args.assets = Args.assets or ['resources.arsc']
        elif Args.action in ['d', 'dump']:
            if Args.what in ['strings', 'resources', 'configurations']:
                targetFunc = dumpResources
                Args.assets = ('resources.arsc',)
                args = (Args.what,)
                kwargs = dict(incValues=Args.values, )
            elif Args.what in ['permissions', 'xmltree', 'xmlstrings']:
                targetFunc = dumpXmlTree
                if Args.what == 'permissions':
                    Args.assets = ('AndroidManifest.xml',)
                args = (Args.what,)
                # kwargs = dict(outFile=Args.logFile)
        for filename in Args.assets:
            file = io.BytesIO(zf.read(filename))
            with ioData(file, offset=0):
                targetFunc(file, *args, **kwargs)
    pass


class ResChunkHeader(ru.ResChunk_header):
    typeMap = {
        0x0000: 'RES_NULL_TYPE',
        0x0001: 'RES_STRING_POOL_TYPE',
        0x0002: 'RES_TABLE_TYPE',
        0x0003: 'RES_XML_TYPE',

        #  Chunk types in RES_XML_TYPE
        0x0100: 'RES_XML_FIRST_CHUNK_TYPE',
        0x0100: 'RES_XML_START_NAMESPACE_TYPE',
        0x0101: 'RES_XML_END_NAMESPACE_TYPE',
        0x0102: 'RES_XML_START_ELEMENT_TYPE',
        0x0103: 'RES_XML_END_ELEMENT_TYPE',
        0x0104: 'RES_XML_CDATA_TYPE',
        0x017f: 'RES_XML_LAST_CHUNK_TYPE',
        #  This contains a uint32_t array mapping strings in the string
        #  pool back to resource identifiers.  It is optional.
        0x0180: 'RES_XML_RESOURCE_MAP_TYPE',

        #  Chunk types in RES_TABLE_TYPE
        0x0200: 'RES_TABLE_PACKAGE_TYPE',
        0x0201: 'RES_TABLE_TYPE_TYPE',
        0x0202: 'RES_TABLE_TYPE_SPEC_TYPE',
        0x0203: 'RES_TABLE_LIBRARY_TYPE',
    }

    @property
    def typeName(self):
        return self.typeMap.get(self.type)

    def isValid(self):
        return self.typeName and self.headerSize <= self.size

    def hasData(self):
        return self.typeName in [
            'RES_STRING_POOL_TYPE',
            'RES_TABLE_TYPE_TYPE',
            'RES_TABLE_TYPE_SPEC_TYPE',
            'RES_XML_START_NAMESPACE_TYPE',
            'RES_XML_END_NAMESPACE_TYPE',
            'RES_XML_START_ELEMENT_TYPE',
            'RES_XML_END_ELEMENT_TYPE',
            'RES_XML_CDATA_TYPE',
            'RES_XML_RESOURCE_MAP_TYPE',
        ]


class ResTableTypeSpec(ru.ResTable_typeSpec):
    confFlagsMap = dict(
        ACONFIGURATION_MCC=0x0001,
        ACONFIGURATION_MNC=0x0002,
        ACONFIGURATION_LOCALE=0x0004,
        ACONFIGURATION_TOUCHSCREEN=0x0008,
        ACONFIGURATION_KEYBOARD=0x0010,
        ACONFIGURATION_KEYBOARD_HIDDEN=0x0020,
        ACONFIGURATION_NAVIGATION=0x0040,
        ACONFIGURATION_ORIENTATION=0x0080,
        ACONFIGURATION_DENSITY=0x0100,
        ACONFIGURATION_SCREEN_SIZE=0x0200,
        ACONFIGURATION_VERSION=0x0400,
        ACONFIGURATION_SCREEN_LAYOUT=0x0800,
        ACONFIGURATION_UI_MODE=0x1000,
        ACONFIGURATION_SMALLEST_SCREEN_SIZE=0x2000,
        ACONFIGURATION_LAYOUTDIR=0x4000,
        ACONFIGURATION_SCREEN_ROUND=0x8000,
        ACONFIGURATION_COLOR_MODE=0x10000,
    )
    confFlagsMap = {value: key[1:] for key, value in confFlagsMap.items()}

    def __init__(self, data, offset=None):
        offset = offset or data.tell()
        data.seek(offset)
        data.readinto(self)
        if self.entryCount:
            self.data = (self.entryCount * c_uint32)()
            data.readinto(self.data)
        else:
            self.data = None

    def confFlags(self, idx):
        try:
            flags = self.data[idx]
        except:
            return

        mflags = lambda flags: functools.reduce(
            lambda t, x, strFlags=bin(flags): ([1 << (len(strFlags) - 1 - x)] + t) if strFlags[x] == '1' else t,
            range(len(bin(flags))), []
        )
        return ' | '.join([self.confFlagsMap[x] for x in mflags(flags)]) if flags else 'CONFIGURATION_DEFAULT'


class ResTableType(ru.ResTable_type):
    def __init__(self, data, offset=None):
        headerOffset = offset or data.tell()
        data.seek(headerOffset)
        data.readinto(self)
        self.res_entry = []
        self.res_value = []
        self.idx = []
        if not self.entryCount: return
        offset = headerOffset + self.entriesStart
        sparseOffset = offset
        data.seek(offset)
        bFlag = self.flags & ru.ResTable_type.FLAG_SPARSE
        if bFlag:
            entries = (self.res_entry * ru.ResTable_sparseTypeEntry)()
            data.readinto(entries)
        for k in range(self.entryCount):
            if bFlag:
                self.idx.append(entries[k].idx)
                offset = entries[k].offset + headerOffset
            if data.tell() != offset:
                data.seek(offset)
            entry = ru.ResTable_entry()
            offset += data.readinto(entry)
            self.res_entry.append(entry)
            value = ru.Res_value()
            offset += data.readinto(value)
            self.res_value.append(value)

    def getEntryAt(self, idx):
        if self.flags & ru.ResTable_type.FLAG_SPARSE:
            try:
                idx = self.idx.index(idx)
            except:
                return
        try:
            return self.res_entry[idx], self.res_value[idx]
        except:
            pass


class GenCrawler(object):
    _allowed_cases_ = None

    def crawl(self, file, offset=0):
        stack = []
        while True:
            rch = ru.readResHeader(file, ResChunkHeader, offset=offset)
            if not rch.isValid():
                raise ArgumentError('Error at 0x{:0>8x}, 0x{:0>4x} not a valid type'.format(offset, rch.type))
            elif self._allowed_cases_ and rch.type not in self.allowedCases:
                raise ArgumentError('Element at 0x{:0>8x} not an allowed RES_CHUNK_TYPE'.format(offset))
            stack.append((offset, rch.type, rch.typeName, rch.headerSize, rch.size))
            yield len(stack) - 1, offset, rch
            offset += rch.headerSize
            if rch.hasData():
                offset += stack[-1][4] - stack[-1][3]
                stack.pop()
            if offset >= stack[0][4]:
                break


class ResourceCrawler(GenCrawler):
    _allowedCases_ = [
        ru.ResChunk_header.RES_STRING_POOL_TYPE,
        ru.ResChunk_header.RES_TABLE_TYPE,
        ru.ResChunk_header.RES_TABLE_LIBRARY_TYPE,
        ru.ResChunk_header.RES_TABLE_TYPE_SPEC_TYPE,
        ru.ResChunk_header.RES_TABLE_TYPE_TYPE,
        ru.ResChunk_header.RES_TABLE_PACKAGE_TYPE
    ]

    def __init__(self):
        super(ResourceCrawler, self).__init__()
        self._resetcrawler_()

    def _resetcrawler_(self):
        self.nPackage = 0
        self.entryName = None
        self.entryValue = []
        self.configData = []

    def getValueRep(self, stringPool, resvalue):
        case = resvalue.dataType
        if case == resvalue.TYPE_STRING:
            prtStr = '(string8)' if stringPool.isUTF8() else '(string16)'
            return prtStr + ' "%s"' % stringPool.stringAt(resvalue.data)
        elif case == resvalue.TYPE_FLOAT:
            return '(float) **************'
        elif case == resvalue.TYPE_DIMENSION or case == resvalue.TYPE_FRACTION:
            MANTISSA_MULT = 1.0 // (1 << resvalue.COMPLEX_MANTISSA_SHIFT)
            RADIX_MULTS = [
                1.0 * MANTISSA_MULT, 1.0 // (1 << 7) * MANTISSA_MULT,
                1.0 // (1 << 15) * MANTISSA_MULT, 1.0 // (1 << 23) * MANTISSA_MULT]
            complex = resvalue.data
            fvalue = (complex & (resvalue.COMPLEX_MANTISSA_MASK << resvalue.COMPLEX_MANTISSA_SHIFT)) \
                     * RADIX_MULTS[(complex >> resvalue.COMPLEX_RADIX_SHIFT) & resvalue.COMPLEX_RADIX_MASK]
            if case == resvalue.TYPE_DIMENSION:
                fkey = 'dimension'
                COMPLEX_UNITS = ["px", "dp", "sp", "pt", "in", "mm"]
            else:
                fkey = 'fraction'
                COMPLEX_UNITS = ["%", "%p"]
            funits = COMPLEX_UNITS[(complex >> resvalue.COMPLEX_UNIT_SHIFT) & resvalue.COMPLEX_UNIT_MASK]
            return '({}) {:0.6f}{}'.format(fkey, fvalue, funits)
        elif resvalue.TYPE_FIRST_INT <= case <= resvalue.TYPE_LAST_INT:
            if case == resvalue.TYPE_INT_DEC:
                return '(integer) %s' % resvalue.data
            if case == resvalue.TYPE_INT_HEX:
                return '(integer) 0x{:0>8x}'.format(resvalue.data)
            if case == resvalue.TYPE_INT_BOOLEAN:
                return '(boolean) %s' % bool(resvalue.data)
            if case == resvalue.TYPE_INT_COLOR_ARGB8:
                return '(color) #{:0>8x}'.format(resvalue.data)
            if case == resvalue.TYPE_INT_COLOR_RGB8:
                return '(color) #{:0>8x}'.format(resvalue.data)
            if case == resvalue.TYPE_INT_COLOR_ARGB4:
                return '(color) #{:0>4x}'.format(resvalue.data)
            if case == resvalue.TYPE_INT_COLOR_RGB4:
                return '(color) #{:0>4x}'.format(resvalue.data)
        if case == resvalue.TYPE_NULL:
            return '(null) ' + 'UNDIFINED' if not resvalue.data else 'EMPTY'
        else:
            if case == resvalue.TYPE_REFERENCE:
                fkey = 'reference'
            elif case == resvalue.TYPE_ATTRIBUTE:
                fkey = 'attribute'
            elif case == resvalue.TYPE_DYNAMIC_REFERENCE:
                fkey = 'dynamic reference'
            elif case == resvalue.TYPE_DYNAMIC_ATTRIBUTE:
                fkey = 'dynamic attribute'
            return '({}) 0x{:0>8x}'.format(fkey, resvalue.data)

    def crawl(self, file):
        crawler = super(ResourceCrawler, self).crawl(file)
        for dummy, offset, rch in crawler:
            self.rch = rch
            case = rch.type
            if case == ru.ResChunk_header.RES_TABLE_TYPE_TYPE:
                nConfig += 1
                rtt = ru.readResHeader(file, ru.ResTable_type, offset=offset)
                if self.startResTableTypeHandler(nPackage, nConfig, rtt):
                    break
                notSparse = not rtt.flags & ru.ResTable_type.FLAG_SPARSE
                resClass = c_uint32 if notSparse else ru.ResTable_sparseTypeEntry
                indx = ru.readResHeader(file, (rtt.entryCount * resClass), offset=offset + rtt.header.headerSize)
                for k in range(rtt.entryCount):
                    if notSparse:
                        if indx[k] == ru.ResTable_type.NO_ENTRY: continue
                        eOff = offset + rtt.entriesStart + indx[k]
                    else:
                        eOff = offset + rtt.entriesStart + indx[k].offset  # OJO dice que debe dividirse por 4
                    entry = ru.readResHeader(file, ru.ResTable_entry, offset=eOff)
                    if not entry.flags & ru.ResTable_entry.FLAG_COMPLEX:
                        value = ru.readResHeader(file, ru.Res_value, offset=eOff + sizeof(entry))
                        s, r, t, d = value.size, value.res0, value.dataType, value.data
                        strValue = 't=0x{:0>2x} d=0x{:0>8x} (s=0x{:0>4x} r=0x{:0>2x})'.format(t, d, s, r)
                    else:
                        rtme = ru.readResHeader(file, ru.ResTable_map_entry, offset=eOff + sizeof(entry))
                        rtm = ru.readResHeader(file, (rtme.count * ru.ResTable_map),
                                               offset=eOff + sizeof(entry) + sizeof(rtme))
                        value = (rtme.parent, rtm)
                        strValue = '<bag>'
                    entryid, entryname, entryvalue = k, entry.key, value
                    if self.entryDataHandler(nConfig, entryid, entryname, entryvalue):
                        break
                if self.endResTableTypeHandler(nPackage, nConfig):
                    break
                header = ru.readResHeader(file, ru.ResChunk_header)
                if header.type == case: continue
                if self.endResTableTypeSpecHandler(nPackage):
                    break
                if header.type == ru.ResChunk_header.RES_TABLE_TYPE:
                    if self.endResTablePackageHandler(nPackage):
                        break
            elif case == ru.ResChunk_header.RES_TABLE_TYPE_SPEC_TYPE:
                rtts = ru.readResHeader(file, ru.ResTable_typeSpec, offset=offset)
                offset += rtts.header.headerSize
                if not rtts.entryCount:
                    continue
                nConfig = -1
                flags = ru.readResHeader(file, (rtts.entryCount * c_uint32), offset=offset)
                if self.startResTableTypeSpecHandler(nPackage, rtts, flags):
                    break
                self.entryName = (rtts.entryCount * ru.ResStringPool_ref)()
                self.configData = []
            elif case == ru.ResChunk_header.RES_TABLE_PACKAGE_TYPE:
                nPackage += 1
                rtp = ru.readResHeader(file, ru.ResTable_package, offset=offset)
                if self.startResTablePackageHandler(nPackage, rtp):
                    break
            elif case == ru.ResChunk_header.RES_STRING_POOL_TYPE:
                stringpool = ru.ResStringPool(file, offset=offset)
                dmySpArr += 1
                if self.stringPoolHandler(dmySpArr, stringpool):
                    break
            elif case == ru.ResChunk_header.RES_TABLE_TYPE:
                dmySpArr = 0
                nPackage = -1
                rth = ru.readResHeader(file, ru.ResTable_header, offset=offset)
                if self.startResTableHandler(rth.packageCount):
                    break
            elif case == ru.ResChunk_header.RES_TABLE_LIBRARY_TYPE:
                pass

    @staticmethod
    def startResTableHandler(packageCount):
        pass

    @staticmethod
    def stringPoolHandler(spType, stringPool):
        pass

    @staticmethod
    def startResTablePackageHandler(nPackage, rtp):
        pass

    @staticmethod
    def endResTablePackageHandler(nPackage):
        pass

    @staticmethod
    def startResTableTypeSpecHandler(nPackage, rtts, flags):
        pass

    @staticmethod
    def endResTableTypeSpecHandler(nPackage):
        pass

    @staticmethod
    def startResTableTypeHandler(nPackage, nConfig, rtt):
        pass

    @staticmethod
    def endResTableTypeHandler(nPackage, nConfig):
        pass

    @staticmethod
    def entryDataHandler(nConfig, entryid, entryname, entryvalue):
        pass


def dumpResources(file, what, incValues=False, include_meta_data=False, outFile=None, to_string=None):
    INDENT = '  '
    spArray = []
    rtpArray = []
    flagsArray = []
    rttArray = []
    rttsArray = []
    entryInfo = {}
    configData = []

    rc = ResourceCrawler()

    with ioData(file, 0, output=outFile, to_string=to_string) as file:
        if what == 'strings':
            def handler(spType, dmySp):
                nStrings = dmySp.stringCount()
                encoding = 'UTF-8' if dmySp.isUTF8() else 'UTF-8'
                sorted = 'sorted' if dmySp.isSorted() else 'non-sorted'
                nStyles = dmySp.styleCount()
                bytes = rc.rch.size
                prtStr = 'String pool of {0} unique {1} {2} strings, ' \
                         '{0} entries and {3} styles using {4} bytes:'.format(
                    nStrings, encoding, sorted, nStyles, bytes,
                )
                cprint(prtStr)
                for k in range(nStrings):
                    cprint('String #%s: %s' % (k, dmySp.stringAt(k)))
                # return 1

            rc.stringPoolHandler = handler

        if what == 'resources':
            def handler(packageCount):
                cprint('Package Groups (%s)' % packageCount)

            rc.startResTableHandler = handler

            def handler(spType, stringPool):
                spArray.append(stringPool)

            rc.stringPoolHandler = handler

            def handler(nPackage, rtp):
                rtpArray.append(rtp)
                pckName = bytearray(rtp.name).decode('UTF-16').split('\0', 1)[0]
                prtStr = 'Package {} id=0x{:0>2x} name={}'.format(nPackage, rtp.id, pckName)
                cprint(1 * INDENT + prtStr)

            rc.startResTablePackageHandler = handler

            def handler(nPackage, rtts, flags):
                rttsArray.append(rtts)
                flagsArray.append(flags)

            rc.startResTableTypeSpecHandler = handler

            def handler(nPackage):
                rtp = rtpArray[-1]
                pckName = bytearray(rtp.name).decode('UTF-16').split('\0', 1)[0]
                flags = flagsArray.pop()
                rtts = rttsArray.pop()
                prtStr = 'type {} configCount={} entryCount={}'
                prtStr = prtStr.format(rtts.id - 1, len(configData), rtts.entryCount)
                cprint(2 * INDENT + prtStr)
                for k in range(rtts.entryCount):
                    resId = ru.Res_MAKEID(rtp.id - 1, rtts.id - 1, k)
                    strId = '%s:%s/%s' % (pckName, spArray[1].stringAt(rtts.id - 1), spArray[2].stringAt(entryInfo[k]))
                    prtStr = 'spec resource 0x{:0>8x} {}: flags=0x{:0>8x}'.format(resId, strId, flags[k])
                    cprint(3 * INDENT + prtStr)
                while configData:
                    rtt = rttArray.pop(0)
                    entryValue = configData.pop(0)
                    cprint(3 * INDENT + 'config %s:' % rtt.config.toString())
                    for idx, value in entryValue:
                        ename = spArray[2].stringAt(entryInfo[idx])
                        resId = ru.Res_MAKEID(rtp.id - 1, rtt.id - 1, idx)
                        strId = '%s:%s/%s' % (pckName, spArray[1].stringAt(rtts.id - 1), ename)
                        isBag = isinstance(value, tuple)
                        if isBag:
                            strValue = '<bag>'
                        else:
                            s, r, t, d = value.size, value.res0, value.dataType, value.data
                            strValue = 't=0x{:0>2x} d=0x{:0>8x} (s=0x{:0>4x} r=0x{:0>2x})'.format(t, d, s, r)
                        prtStr = '{}resource 0x{:0>8x} {}: {}'
                        cprint(4 * INDENT + prtStr.format('spec ' if not incValues else '', resId, strId, strValue))
                        if incValues:
                            if not isBag:
                                ptrStr = rc.getValueRep(spArray[0], value)
                                cprint(5 * INDENT + ptrStr.format(value.data))
                            else:
                                ptrStr = 'Parent=0x{:0>8x}(Resolved=0x{:0<8x}), Count={}'
                                cprint(5 * INDENT + ptrStr.format(value[0].ident, 0x7f, len(value[1])))
                                ptrStr = '#{} (Key=0x{:0>8x}): {}'
                                for k, rtm in enumerate(value[1]):
                                    cprint(5 * INDENT + ptrStr.format(k, rtm.name.ident,
                                                                     rc.getValueRep(spArray[0], rtm.value)))
                entryInfo.clear()

            rc.endResTableTypeSpecHandler = handler

            def handler(nPackage, nConfig, rtt):
                rttArray.append(rtt)
                configData.append([])

            rc.startResTableTypeHandler = handler

            def handler(nConfig, entryid, entryname, entryvalue):
                entryValue = configData[-1]
                if entryid not in entryInfo:
                    entryInfo[entryid] = entryname
                entryValue.append((entryid, entryvalue))

            rc.entryDataHandler = handler

        rc.crawl(file)


def ResTableCrawler(file, logFile=None):
    def reportData(indent, data):
        fmtStr = indent * INDENT + '0x{1:0>4x} {2} 0x{0:0>8x} {3} {4}'
        cprint(fmtStr.format(*data).upper())

    rc = GenCrawler()
    INDENT = '    '
    # print('Crawling: %s' % filename)
    with ioData(file, 0, output=logFile) as file:
        for depth, offset, rch in rc.crawl(file):
            reportData(depth, (offset, rch.type, rch.typeName, rch.headerSize, rch.size))
            if rch.hasData():
                data = (offset + rch.headerSize, 0xFFFF, 'ARRAY_TYPE', 0, rch.size - rch.headerSize)
                reportData(depth + 1, data)


class NameSpace(object):
    def __init__(self):
        self._prefix = []
        self._uri = []

    def add(self, prefix, uri):
        self._prefix.append(prefix)
        self._uri.append(uri)

    def remove(self, prefix, uri):
        k = self._indexFor(uri)
        if k < 0:
            raise ArgumentError('(%s, %s) not in namespace' % (prefix, uri))
        self._prefix.pop(k)
        self._uri.pop(k)

    def prefixForUri(self, uri):
        k = self._indexFor(uri)
        if k < 0:
            raise ArgumentError('uri=%s not in namespace' % uri)
        return self._prefix[k]

    def _indexFor(self, uri):
        kmax = len(self._uri)
        kmin = 0
        k = kmax - 1
        while kmin <= k < kmax and self._uri[k] != uri:
            k -= 1
        return k


def dumpXmlTree(filename, dcase='xmltree', outFile=None, to_string=''):
    if dcase not in ['xmlstrings', 'xmltree', 'permissions']:
        raise ArgumentError('dcase="%s" is not a valid case' % dcase)
    namespace = NameSpace()
    dmySp = None
    dmyAttrsIds = None
    INDENT = '  '
    depth = -1
    rc = GenCrawler()
    with ioData(filename, 0, output=outFile, to_string=to_string) as file:
        for dummy, offset, rch in rc.crawl(file):
            case = rch.type
            try:
                cData = XmlFactory(file, dmySp, namespace, attrIds=dmyAttrsIds, offset=offset)
                cType = cData[0]
                if cType == ru.ResChunk_header.RES_XML_START_ELEMENT_TYPE:
                    depth += 1
                    if dcase == 'xmltree':
                        cprint(depth * INDENT + 'E: {2} (line={1})'.format(*cData))
                        for key, value, resId in cData[3]:
                            key = key.split('}')[-1]
                            resId = '(0x{:0>8x})'.format(resId) if resId else ''
                            if isinstance(value, (bytes, str)):
                                prtStr = 'A: {0}{2}="{1}" (Raw: "{1}")'.format(key, value, resId)
                            else:
                                prtStr = 'A: {0}{3}=(type 0x{1:0>2x})(0x{2:0>8x})'.format(key, value.dataType,
                                                                                          value.data, resId)
                            cprint((depth + 1) * INDENT + prtStr)
                    elif dcase == 'permissions' and cData[2] == 'uses-permission':
                        cprint("%s: name='%s'" % (cData[2], cData[3][0][1]))
                elif cType == ru.ResChunk_header.RES_XML_END_ELEMENT_TYPE:
                    depth -= 1
                elif cType == ru.ResChunk_header.RES_XML_START_NAMESPACE_TYPE:
                    depth += 1
                    if dcase == 'xmltree':
                        cprint(depth * INDENT + 'N: {2}={3}'.format(*cData))
                elif cType == ru.ResChunk_header.RES_XML_END_NAMESPACE_TYPE:
                    depth -= 1
            except Exception as e:
                if case == ru.ResChunk_header.RES_STRING_POOL_TYPE:
                    dmySp = ru.ResStringPool(file, offset=offset)
                    if dcase == 'xmlstrings':
                        nStrings = dmySp.stringCount()
                        encoding = 'UTF-8' if dmySp.isUTF8() else 'UTF-8'
                        sorted = 'sorted' if dmySp.isSorted() else 'non-sorted'
                        nStyles = dmySp.styleCount()
                        nbytes = rch.size
                        prtStr = 'String pool of {0} unique {1} {2} strings, ' \
                                 '{0} entries and {3} styles using {4} bytes:'.format(
                            nStrings, encoding, sorted, nStyles, nbytes,
                        )
                        cprint(prtStr)
                        for k in range(nStrings):
                            cprint('String #%s: %s' % (k, dmySp.stringAt(k)))
                        break
                elif case == ru.ResChunk_header.RES_XML_RESOURCE_MAP_TYPE:
                    nids = (rch.size - rch.headerSize) // sizeof(c_uint32)
                    offset += rch.headerSize
                    dmyAttrsIds = ru.readResHeader(file, (nids * c_uint32), offset)
                elif case == ru.ResChunk_header.RES_XML_TYPE:
                    pass
                else:
                    raise e


def XmlFactory(data, resStringPool, namespace, attrIds=None, offset=None):
    _StateClass = namedtuple(
        '_StateClass', 'byte_index, line_number, column_number, depth, event_type, event_data'
    )
    stringAt = resStringPool.stringAt

    def fullTagName(ns, name):
        ns = stringAt(ns) or ''
        if ns:
            ns = '{%s}%s:' % (ns, namespace.prefixForUri(ns))
        name = stringAt(name)
        return ns + name

    headerOffset = offset or data.tell()
    resXMLTree_node = ru.readResHeader(data, ru.ResXMLTree_node, headerOffset)
    offset = headerOffset + resXMLTree_node.header.headerSize

    case = resXMLTree_node.header.type
    if not ru.ResChunk_header.RES_XML_FIRST_CHUNK_TYPE <= case <= ru.ResChunk_header.RES_XML_LAST_CHUNK_TYPE:
        raise ArgumentError('Element at 0x{:0>8x} not a RES_XML_CHUNK_TYPE'.format(headerOffset))
    elif case == ru.ResChunk_header.RES_XML_START_ELEMENT_TYPE:
        resXMLTree_attrExt = ru.readResHeader(data, ru.ResXMLTree_attrExt, offset)
        tag = fullTagName(resXMLTree_attrExt.ns, resXMLTree_attrExt.name)
        offset = headerOffset + resXMLTree_node.header.headerSize + resXMLTree_attrExt.attributeStart
        attributeSize = resXMLTree_attrExt.attributeSize
        attributeCount = resXMLTree_attrExt.attributeCount
        attr = ru.readResHeader(data, (attributeCount * ru.ResXMLTree_attribute), offset)
        assert attributeSize * attributeCount == sizeof(attr)
        attribs = []
        for k in range(attributeCount):
            ns, name, rawvalue, typedvalue = attr[k].ns, attr[k].name, attr[k].rawValue, attr[k].typedValue
            key = fullTagName(ns, name)
            value = stringAt(rawvalue) or typedvalue
            attribs.append((key, value, attrIds[name.index] if attrIds and '}' in key else None))
        return (case, resXMLTree_node.lineNumber, tag, attribs)
    elif case == ru.ResChunk_header.RES_XML_END_ELEMENT_TYPE:
        resXMLTree_endElementExt = ru.readResHeader(data, ru.ResXMLTree_endElementExt, offset)
        tag = fullTagName(resXMLTree_endElementExt.ns, resXMLTree_endElementExt.name)
        return (case, resXMLTree_node.lineNumber, tag,)
    elif case == ru.ResChunk_header.RES_XML_START_NAMESPACE_TYPE or \
            case == ru.ResChunk_header.RES_XML_END_NAMESPACE_TYPE:
        dataHeader = ru.readResHeader(data, ru.ResXMLTree_namespaceExt, offset)
        prefix = stringAt(dataHeader.prefix)
        uri = stringAt(dataHeader.uri)
        if case == ru.ResChunk_header.RES_XML_START_NAMESPACE_TYPE:
            namespace.add(prefix, uri)
        else:
            namespace.remove(prefix, uri)
        return (case, resXMLTree_node.lineNumber, prefix, uri)
    elif case == ru.ResChunk_header.RES_XML_CDATA_TYPE:
        dataHeader = ru.readResHeader(data, ru.ResXMLTree_cdataExt, offset)
        data = stringAt(dataHeader.data)
        typedData = str(dataHeader.typedData)
        return (case, resXMLTree_node.lineNumber, data, typedData)


def listApk(filename, opt=1):
    if not zipfile.is_zipfile(filename):
        raise ArgumentError('File: "%s" not a valid apk file')
    zf = zipfile.ZipFile(filename, 'r')
    if opt == 0:
        prtStr1 = '{:^8} {:^8} {:^8} {:^8} {:^8} {:^16} {:^8} {:^8}'
        cprint(prtStr1.format('Length', 'Method', 'Size', 'Ratio', 'Offset', 'Date Time',
                             'CRC-32', 'Name'))
        cprint(5 * (8 * '-' + ' ') + 16 * '-' + 2 * (' ' + 8 * '-'))
        prtStr = '{:8d} {:8} {:8d} {:7d}% {:8d} {:16} {:8} {:8}'
        totsize = totcsize = 0
        for zinfo in zf.infolist():
            totsize += zinfo.file_size
            totcsize += zinfo.compress_size
            method = 'Deflate' if zinfo.compress_type == zipfile.ZIP_DEFLATED else 'Stored'
            ratio = int(100.0 - 100.0 * zinfo.compress_size // zinfo.file_size)
            date_time = '{0}-{1}-{2} {3}:{4}'.format(*zinfo.date_time[:-1])
            CRC = '{:0>8x}'.format(int(zinfo.CRC))
            data = (zinfo.file_size, method, zinfo.compress_size,
                    ratio, zinfo.header_offset, date_time, CRC, zinfo.filename)
            cprint(prtStr.format(*data))
        ratio = int(100.0 - 100.0 * totcsize // totsize)
        cprint(8 * '-' + 10 * ' ' + 8 * '-' + ' ' + 8 * '-' + 27 * ' ' + 8 * '-')
        prtStr = '{:8}' + 10 * ' ' + '{:8}' + ' ' + '{:7}%' + 27 * ' ' + '{} files'
        cprint(prtStr.format(totsize, totcsize, ratio, len(zf.namelist())))
    else:
        cprint('\n'.join(zf.namelist()))
        if opt > 1:
            cprint('\n\nResource table:')
            file = io.BytesIO(zf.read('resources.arsc'))
            dumpResources(file, what='resources')
            cprint('\n\nAndroid manifest:')
            file = io.BytesIO(zf.read('AndroidManifest.xml'))
            dumpXmlTree(file)


if __name__ == '__main__':
    import ResourcesTypes as ru

    base_path = '/mnt/c/Users/Alex Montes/PycharmProjects/TestFiles'
    apk = os.path.join(base_path, 'TeaTV-v9.9.6r_build_111-Mod_v2.apk')
    zf = zipfile.ZipFile(apk)
    data = io.BytesIO(zf.read('resources.arsc'))

    case = 'manifest'
    if case == 'test':
        import collections

        cprint('ended')
    elif case == 'gencrawler':
        gcrawl = GenCrawler()
        k = 0
        for nstack, file_pos, rch in gcrawl.crawl(data, offset=k):
            msg = f'{nstack=} {file_pos=} {rch.typeName=}'
            if rch.typeName == 'RES_TABLE_TYPE_TYPE':
                continue
                rtt = ru.readResHeader(data, ru.ResTable_type, offset=file_pos)
                msg += f' ({rtt.config.toString()})'
            cprint(msg)
        pass
    elif case == 'dumpHexCtypeStruct':
        dumpHexCtypeStruct(data, ru.ResTable_type, offset=194592)
        # table = ctypeStructTable(data, ru.ResTable_type, offset=194592)
        # [cprint(row) for row in table]
    elif case == 'dumpHex':
        dumpHexData(data, offset=194592, size=84, base=16)
    elif case == 'dumpResources':
        with ioData(data, 0, output=os.path.join(base_path, 'test.txt')) as file:
            dumpResources(file, 'resources', incValues=True)
    elif case == 'commandline':
        kwargs = dict(
            # logFile='/media/amontesb/HITACHI/BASURA/ResourceTypesData/test.txt',
            filename=apk,  # file.{zip, jar, apk}
            action='dump',  # l[ist], d[ump]
            # parametros
            # list ->           -a -v
            # dump ->           --values, --include-meta-data WHAT [asset [asset ...]
            what='resources',
            assets=['AndroidManifest.xml', 'res/layout/activity_main.xml', ],
        )
        aapt(**kwargs)
        pass
    elif case == 'apk':
        listApk(apk, 1)
    elif case == 'resources':
        ResTableCrawler(apk)
        dumpResources(apk)
    elif case == 'manifest':
        ResTableCrawler(apk)
        dmySp = ru.ResStringPool(apk, 0X00000008)
        namespace = NameSpace()
        dumpXmlChunk = lambda x: XmlFactory(file, dmySp, namespace, offset=x)
        cprint(dumpXmlChunk(0X000006FC))
        cprint(dumpXmlChunk(0X00000714))
        cprint(dumpXmlChunk(0x00000950))
        cprint(dumpXmlChunk(0X00000C00))
        dumpXmlTree(apk, dcase='permissions')
