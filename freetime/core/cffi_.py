# -*- coding: utf-8 -*-
"""
所有加载过的cffi句柄都在ft_cffi中管理：
    key是so的文件名
    value是lib和ffi句柄
自定义的扩展cffi代码，请使用loadCffi方法加载
框架用到的cffi代码，在freetime/core/cffi/ft.so中, 此处预先load，键值是"ft"
"""
from cffi import FFI
import os
_ft_cffi = {}
_FT_CDEF = 'int ftcode(int seed, char *data, int datalen, char *out); \n    ssize_t ftpread(int fd, void *buf, size_t count, size_t offset); \n    ssize_t ftpwrite(int fd, const void *buf, size_t count, size_t offset);'

def loadCffi(libname, cdef_text, libpath):
    pass

def loadFTCffi():
    pass

def getCffi(libname):
    pass
loadFTCffi()