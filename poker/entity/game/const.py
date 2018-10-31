# -*- coding: utf-8 -*-
"""

"""
__author__ = ['"Zhouhao" <zhouhao@tuyoogame.com>']

class BaseConst(object, ):
    """

    """

    class ConstError(TypeError, ):
        pass

    class ConstCaseError(ConstError, ):
        pass

    def __setattr__(self, name, value):
        pass

class TyGlobleConst(BaseConst, ):
    pass
import sys
sys.modules['tyGlobleConst'] = TyGlobleConst()
import tyGlobleConst
tyGlobleConst.VERTION = 0.1