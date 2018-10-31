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
import math
from poker.util.pokercffi import POKERC
from poker.util.pokercffi import POKERFFI
DEFAULT_STEP = 26
QUERY_STEP = 17

def encode(lat, lon, step=DEFAULT_STEP):
    """
    给定经纬度，返回geohash-int，step为精度
    26步最精确，误差0.6m
    """
    pass

def decode(geobit, step=DEFAULT_STEP):
    """
    给出GEO的锚点, 计算相邻的4各经度纬度数据
    """
    pass

def get_neighbors(geobit, step=DEFAULT_STEP):
    """
    给定geohash-int，返回相邻8块的geohash-int
    """
    pass

def _deg2rad(d):
    pass

def get_distance(geoint1, geoint2, step=DEFAULT_STEP):
    """
    计算两者之间的距离 单位：米
    """
    pass