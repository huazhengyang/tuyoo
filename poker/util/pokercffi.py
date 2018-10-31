# -*- coding: utf-8 -*-
"""
Created on 2015-5-12
@author: zqh
"""
"""
GeoHash封装
算法参照:https://github.com/yinqiwen/ardb/blob/master/doc/spatial-index.md
zhouxin,2014.4.15
"""
import os
from freetime.core import cffi_
__cdef_text = '\ntypedef enum\n{\n    GEOHASH_NORTH = 0,\n    GEOHASH_EAST,\n    GEOHASH_WEST,\n    GEOHASH_SOUTH,\n    GEOHASH_SOUTH_WEST,\n    GEOHASH_SOUTH_EAST,\n    GEOHASH_NORT_WEST,\n    GEOHASH_NORT_EAST\n} GeoDirection;\n\ntypedef struct\n{\n        uint64_t bits;\n        uint8_t step;\n} GeoHashBits;\n\ntypedef struct\n{\n        double max;\n        double min;\n} GeoHashRange;\n\ntypedef struct\n{\n        GeoHashBits hash;\n        GeoHashRange latitude;\n        GeoHashRange longitude;\n} GeoHashArea;\n\ntypedef struct\n{\n        GeoHashBits north;\n        GeoHashBits east;\n        GeoHashBits west;\n        GeoHashBits south;\n        GeoHashBits north_east;\n        GeoHashBits south_east;\n        GeoHashBits north_west;\n        GeoHashBits south_west;\n} GeoHashNeighbors;\n\nint geohash_encode(double latitude, double longitude, uint8_t step, GeoHashBits* hash);\nint geohash_decode(const GeoHashBits* hash, GeoHashArea* area);\nint geohash_get_neighbors(const GeoHashBits* hash, GeoHashNeighbors* neighbors);\nint des_decrypt(unsigned char *src, unsigned srclen, unsigned char *key, unsigned char *out);\nint des_encrypt(unsigned char *src, unsigned srclen, unsigned char *key, unsigned char *out);\n\n'
__sodir = (os.path.dirname(os.path.abspath(__file__)) + '/cffi/')
cffi_.loadCffi('pokerutil', __cdef_text, __sodir)
"""
POKER大模块使用的CFFI的集中定义装载
"""
(POKERC, POKERFFI) = cffi_.getCffi('pokerutil')