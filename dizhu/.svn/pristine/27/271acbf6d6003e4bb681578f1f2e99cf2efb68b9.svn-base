# -*- coding=utf-8 -*-
'''
Created on 2015年5月7日

@author: zqh
'''
import random


class CardRander(object):

    def __init__(self):
        self._card_list = list(range(54))
        random.shuffle(self._card_list) 
        self._rand_cars = []
        pass
    
    def escapeCards(self, cards):
        if isinstance(cards, int):
            self.__escapeCard(cards)
        elif isinstance(cards, (list, tuple)):
            for card in cards:
                self.__escapeCard(card)
    
    def __escapeCard(self, card):
        try:
            self._card_list.remove(card)
        except:
            pass
        
    def randCard(self, count, goodcard=False):
        if count > len(self._card_list):
            result = self._card_list
        else:
            result = self._card_list[0:count]
        
        self._rand_cars.append(result)
        self._card_list = list(set(self._card_list) - set(result))
        random.shuffle(self._card_list)        
        return result
    
