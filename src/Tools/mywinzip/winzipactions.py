import os.path
import shutil
import tkinter.messagebox as tkMessageBox
import zipfile
import tempfile
import fnmatch
from enum import Enum
from typing import Literal


class CompressionMethod(Enum):
    MAXIMA = zipfile.ZIP_BZIP2
    DEFLATED = zipfile.ZIP_DEFLATED
    SUPERFAST = zipfile.ZIP_LZMA
    NOCOMPRESSION = zipfile.ZIP_STORED


class WinzipActions:
    def __init__(self):
        super().__init__()

        self.zf = None
        self.active_compression_method: CompressionMethod = CompressionMethod.NOCOMPRESSION.value
        self.zip_type: Literal['zip', 'pyzip'] = 'zip'
        self._recyclebin = set()

        self.filters = ['*.*;', '*.js,*.py;*.pyc', ';*.pyc', '*.pdf;']
        self.active_filter = 0

    def save(self, filename):
        srcfile, dstfile = self.zf.filename, filename
        isSaveAs = os.path.basename(self.zf.filename) != os.path.basename(filename)
        if not self._recyclebin:
            # El archivo no tiene elementos eliminados
            self.zf.close()
            shutil.copy(srcfile, dstfile)
            if isSaveAs:
                dstfile = os.path.join(os.path.dirname(srcfile), os.path.basename(filename))
                os.rename(srcfile, dstfile)
                self._loadzip(dstfile, mode='a')
        else:
            selected = [
                x for x in self.zf.namelist()
                if x.count(os.sep) == 0 or (x.count(os.sep) == 1 and x.endswith(os.sep))
            ]
            self._save_partial(dstfile, selected)
            self.zf.close()
            os.remove(srcfile)
            self.loadzip(dstfile, mode='a')
            self._recyclebin = set()

    def create_folder(self, filename, date_time):
        assert filename.endswith('/')
        zinfo = zipfile.ZipInfo(filename, date_time)
        # zinfo.external_attr = (st.st_mode & 0xFFFF) << 16  # Unix attributes
        zinfo.file_size = 0
        zinfo.external_attr |= 0x10  # MS-DOS directory flag
        zinfo.compress_size = 0
        zinfo.CRC = 0

        zf = self.zf
        with zf._lock:
            if zf._seekable:
                zf.fp.seek(zf.start_dir)
            zinfo.header_offset = zf.fp.tell()  # Start of header bytes
            if zinfo.compress_type == zipfile.ZIP_LZMA:
                # Compressed data includes an end-of-stream (EOS) marker
                zinfo.flag_bits |= 0x02

            zf._writecheck(zinfo)
            zf._didModify = True

            zf.filelist.append(zinfo)
            zf.NameToInfo[zinfo.filename] = zinfo
            zf.fp.write(zinfo.FileHeader(False))
            zf.start_dir = zf.fp.tell()

    def set_compression_method(self, name):
        try:
            self.active_compression_method = CompressionMethod[name].value
        except KeyError:
            raise KeyError("Not a valid 'CompressionMethod' member")

    def addFiles(self, files, zip_files, isdirectory, dest_folder=''):
        files = self.apply_filter(files, self.active_filter)
        if zip_files is None:
            sys_root = os.path.commonpath(files) if len(files) > 1 else os.path.dirname(files[0])
            if isdirectory:
                sys_root = os.path.dirname(sys_root)
            zip_files = [os.path.relpath(x, sys_root) + ('/' if x.endswith('/') else '') for x in files]
            # Cuando se agregan archivos en un directorio diferente al raiz del zip file
            if dest_folder:
                zip_files = [
                    os.path.join(dest_folder, x)
                    for x in zip_files
                ]
        compression = self.active_compression_method
        for fname, arcname in zip(files, zip_files):
            self.zf.write(fname, arcname, compress_type=compression)

    def extract(self, zinfo, dest_filename, pwd):
        if zinfo.is_dir():
            os.makedirs(dest_filename)
        else:
            os.makedirs(os.path.dirname(dest_filename), exist_ok=True)
            with self.zf.open(zinfo, pwd=pwd) as fsrc, open(dest_filename, 'wb') as fdst:
                shutil.copyfileobj(fsrc, fdst)

    def apply_filter(self, raw_files: list, filter_indx: int) -> list:
        if filter_indx:
            active_filter = self.filters[filter_indx]
            filter_items = active_filter.split(';')
            fltr_files = []
            if filter_item := filter_items[0]:      # == '+': Include
                for fltr in filter_item.split(','):
                    fltr_files.extend(fnmatch.filter(raw_files, fltr))
            if filter_item := filter_items[1]:      # == '-': Exclude
                fltr_files = fltr_files or raw_files[::]
                exc_files = []
                for fltr in filter_item.split(','):
                    exc_files.extend(fnmatch.filter(fltr_files, fltr))
                fltr_files = list(set(fltr_files).difference(exc_files))
        else:
            fltr_files = raw_files[::]
        return fltr_files

    def _loadzip(self, file, mode='r', compression=None, allowZip64=True, compresslevel=None, *, strict_timestamps=True):
        compression = compression or self.active_compression_method

        method, kw = zipfile.ZipFile, {'compresslevel': compresslevel, 'strict_timestamps': strict_timestamps}
        if self.zip_type == 'pyzip':
            method, kw = zipfile.PyZipFile, {'optimize': -1}

        tmpdir = tempfile.gettempdir()
        if mode == 'a':
            try:
                dstfile = shutil.copy(file, tmpdir)
                shutil.copystat(file, dstfile)
            except shutil.SameFileError:
                dstfile = file
        elif mode == 'x':
            filename = os.path.basename(file)
            dstfile = os.path.join(tmpdir, filename)
            if os.path.exists(dstfile):
                os.remove(dstfile)
        self.zf = method(dstfile, mode, compression, allowZip64, **kw)

    def _walk(self, d_name):
        namelist = self.zf.namelist()
        stack = [d_name]
        while stack:
            d_name = stack.pop()
            dirs = sorted(set(
                os.path.relpath(x, d_name).split('/', 1)[0] for x in namelist
                if x.startswith(d_name) and x.count('/') > d_name.count('/')
            ))
            files = [
                os.path.relpath(x, d_name) for x in namelist
                if not x.endswith('/') and x.startswith(d_name) and x.count('/') == d_name.count('/')
            ]
            answ = yield d_name, dirs, files
            if answ:
                stack.extend(dirs[::-1])
            yield

    def _save_partial(self, filename, selected, method=None, *, active_filter=0):
        infolist = []
        # En este punto se agregan solo los archivos, no los directorios
        selected = set(selected) - self._recyclebin
        for name in selected:
            zinfo = self.zf.getinfo(name)
            if zinfo.is_dir():
                pgen = self._walk(name)
                for root, dirs, files in pgen:
                    if root in self._recyclebin:
                        pgen.send(False)
                        continue
                    pgen.send(True)
                    files = set(os.path.join(root, x) for x in files) - self._recyclebin
                    infolist.extend(files)
            else:
                infolist.append(name)
        # Se filtran los archivos de acuerdo al filtro escogido
        infolist = self.apply_filter(infolist, filter_indx=active_filter)
        # Se agregan los directorios que se encuentran en la ruta de los archivos a agregar,
        # de esta forma no se agregan directorios que se encuentren vacíos luego de aplicar el filtro.
        dirs = set(infolist)
        for f_name in infolist:
            d_names = os.path.dirname(f_name).split('/')
            d_names = ['/'.join(d_names[:k + 1]) + '/' for k in range(len(d_names))]
            dirs.update(d_names)
        infolist = sorted(dirs)
        infolist = map(self.zf.getinfo, infolist)
        if os.path.exists(filename):
            os.remove(filename)
        method = method or zipfile.ZipFile
        try:
            with method(filename, mode='x') as new_zf:
                for zinfo in infolist:
                    if zinfo.is_dir():
                        new_zf.write(os.path.abspath('.'), zinfo.filename)
                    else:
                        data = self.zf.read(zinfo.filename)
                        new_zf.writestr(zinfo, data)
        except Exception as e:
            tkMessageBox.showerror(title='Saving Error', message=str(e))

    def dumpzip(self, infolist):
        lst_str = []
        lst_str.append(5 * (8 * '-' + ' ') + 16 * '-' + 2 * (' ' + 8 * '-'))
        prtStr1 = '{:^8} {:^8} {:^8} {:^8} {:^8} {:^16} {:^8} {:^8}'
        lst_str.append(prtStr1.format('Length', 'Method', 'Size', 'Ratio', 'Offset', 'Date Time',
                             'CRC-32', 'Name'))
        lst_str.append(5 * (8 * '-' + ' ') + 16 * '-' + 2 * (' ' + 8 * '-'))
        prtStr = '{:8d} {:8} {:8d} {:7d}% {:8d} {:16} {:8} {:8}'
        totsize = totcsize = ndir =0
        for zinfo in infolist:
            if zinfo.is_dir():
                ndir += 1
                continue
            totsize += zinfo.file_size
            totcsize += zinfo.compress_size
            method = 'Deflate' if zinfo.compress_type == zipfile.ZIP_DEFLATED else 'Stored'
            ratio = int(100.0 - 100.0 * zinfo.compress_size // zinfo.file_size) if zinfo.file_size else 0
            date_time = '{0}-{1}-{2} {3}:{4}'.format(*zinfo.date_time[:-1])
            CRC = '{:0>8x}'.format(int(zinfo.CRC))
            data = (zinfo.file_size, method, zinfo.compress_size,
                    ratio, zinfo.header_offset, date_time, CRC, zinfo.filename)
            lst_str.append(prtStr.format(*data))
        ratio = int(100.0 - 100.0 * totcsize // totsize)
        lst_str.append(8 * '-' + 10 * ' ' + 8 * '-' + ' ' + 8 * '-' + 27 * ' ' + 8 * '-')
        prtStr = '{:8}' + 10 * ' ' + '{:8}' + ' ' + '{:7}%' + 27 * ' ' + '{} files'
        lst_str.append(prtStr.format(totsize, totcsize, ratio, len(infolist) - ndir))
        return lst_str

    def delete_items(self, selected):
        to_delete = set()
        for name in selected:
            is_dir = name.endswith(os.sep)
            if is_dir:
                delta = [x for x in self.zf.NameToInfo if x.startswith(name)]
            else:
                delta = [name]
            to_delete.update(delta)
        self._recyclebin.update(to_delete)
        # self.onVarChange(attr_data=('view_recycle', 0))
        # self.menu_file.setSaveFlag(True)
        return sorted(to_delete)

    def restore_items(self, selected):
        to_delete = set()
        for name in selected:
            d_names = os.path.dirname(name).split(os.sep)
            delta = [os.path.join(*d_names[:k]) + os.sep for k in range(1, len(d_names) + 1)]
            is_dir = name.endswith(os.sep)
            if is_dir:
                delta.extend([x for x in self.zf.NameToInfo if x.startswith(name)])
            else:
                delta.append(name)
            to_delete.update(delta)
        to_delete.intersection_update(self._recyclebin)
        self._recyclebin.difference_update(to_delete)

        # Esta parte se puede utilizar para purgar el recycle bin de directorios vacíos
        # Se restauran los directorios que no contengan al menos un archivo
        # infolist = set(
        #     x for x in self._recyclebin
        #     if not x.endswith('/')
        # )
        # paths = set(os.path.dirname(filename) for filename in infolist)
        # paths.intersection_update(self._recyclebin)
        # self._recyclebin = infolist.union(paths)

        # self.onVarChange(attr_data=('view_recycle', 1))
        return sorted(to_delete)





