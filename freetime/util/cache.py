# -*- coding: utf-8 -*-
import collections
from datetime import datetime
import functools
from heapq import nsmallest
from itertools import ifilterfalse
from operator import itemgetter
import freetime.util.log as ftlog
import json
from copy import deepcopy
from time import time

class Counter(dict, ):
    """

    """

    def __missing__(self, key):
        pass

def lru_cache(maxsize=100, cache_key_args_index=1):
    """

    Arguments to the cached function must be hashable.
    Cache performance statistics stored in f.hits and f.misses.
    Clear the cache with f.clear().
    http://en.wikipedia.org/wiki/Cache_algorithms#Least_Recently_Used

    """
    pass

def lfu_cache(maxsize=100, cache_key_args_index=1):
    """

    Arguments to the cached function must be hashable.
    Cache performance statistics stored in f.hits and f.misses.
    Clear the cache with f.clear().
    http://en.wikipedia.org/wiki/Least_Frequently_Used

    """
    pass

def _count_pps_info(wrapper):
    pass
_cache_groups = {}
_cache_wrappers = {}

def cloneData(data):
    """
    使用JSON的loads和dump克隆一个数据对象
    """
    pass

def lfu_time_cache(maxsize=100, mainindex=0, subindex=1, group=None):
    """

    Arguments to the cached function must be hashable.
    Cache performance statistics stored in f.hits and f.misses.
    Clear the cache with f.clear().
    http://en.wikipedia.org/wiki/Least_Frequently_Used

    """
    pass

def lfu_alive_cache(maxsize=100, cache_key_args_index=0, alive_second=30):
    """

    Arguments to the cached function must be hashable.
    Cache performance statistics stored in f.hits and f.misses.
    Clear the cache with f.clear().
    http://en.wikipedia.org/wiki/Least_Frequently_Used

    """
    pass