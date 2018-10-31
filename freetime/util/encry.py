# -*- coding: utf-8 -*-
import freetime.core.cffi_ as ftcffi
(_clib, _cdef) = ftcffi.getCffi('ft')
_codestr = _cdef.new('char []', 65536)

def code(seed, data):
    pass