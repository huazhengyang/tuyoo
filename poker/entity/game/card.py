# -*- coding: utf-8 -*-
"""

"""
__author__ = ['Wangtao', '"Zhouhao" <zhouhao@tuyoogame.com>']

class Card(object, ):
    """

    """
    CARD_NUM = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A', '', '']
    CARD_COLOR = ['S', 'H', 'C', 'D', 'j', 'J']
    CARD_COLOR_DICT = {'S': u'\u9ed1\u6843', 'C': u'\u6885\u82b1', 'H': u'\u7ea2\u6843', 'D': u'\u65b9\u5757', 'j': u'\u5c0f\u738b', 'J': u'\u5927\u738b'}

    def __init__(self, _type, number):
        pass

    @staticmethod
    def cmp(a, b):
        """

        """
        pass

    def __str__(self):
        pass

    def __repr__(self):
        pass

    def __int__(self):
        pass

    def toShortInt(self):
        """
            515 => 53  616 => 54
        """
        pass

    @staticmethod
    def _split_card_value(int_card):
        """

        """
        pass

    @classmethod
    def _splitShort(cls, cardId):
        """

        """
        pass

    @classmethod
    def fromInt(cls, int_card):
        pass

    @classmethod
    def fromShortInt(cls, cardId):
        pass

    @classmethod
    def intToShort(cls, int_card):
        """
            515 => 53  616 => 54
        """
        pass

    @classmethod
    def shortToInt(cls, cardId):
        """
            53 => 515   54 => 616
        """
        pass

    @classmethod
    def getCardColorNumByCardId(cls, cardId):
        """
        返回值：    [花色， 牌面值]
        """
        pass

    @classmethod
    def getCardStr(cls, color, num):
        pass
if (__name__ == '__main__'):
    import sys
    reload(sys)
    sys.setdefaultencoding('utf8')
    for cardIndex in xrange(54):
        cardObj1 = Card.fromShortInt((cardIndex + 1))
        print cardObj1.shortToInt((cardIndex + 1)), cardObj1.getCardStr(cardObj1.t, cardObj1.n), Card.getCardColorNumByCardId((cardIndex + 1))