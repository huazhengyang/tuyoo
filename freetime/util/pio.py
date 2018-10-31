# -*- coding: utf-8 -*-
import freetime.core.cffi_ as ftcffi
(_clib, _cdef) = ftcffi.getCffi('ft')
_ffibuf = _cdef.new('char[]', 65536)

def pwrite(fd, data, count, offset):
    pass

def pread(fd, count, offset):
    pass