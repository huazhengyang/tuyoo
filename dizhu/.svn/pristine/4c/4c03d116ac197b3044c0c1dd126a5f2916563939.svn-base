# -*- coding:utf-8 -*-
'''
Created on 2018年1月23日

@author: wangyonghui
'''
from dizhu.entity import dizhu_red_envelope_bomb


def _mk_red_envelope_rich_text(userName, roomName, count):
    # 纯文本颜色
    RICH_COLOR_PLAIN = 'FFFFFF'
    # 黄色文本
    RICH_COLOR_YELLOW = 'FCF02D'
    return [
        [RICH_COLOR_YELLOW, '喜从天降！'],
        [RICH_COLOR_PLAIN, '恭喜'],
        [RICH_COLOR_YELLOW, userName],
        [RICH_COLOR_PLAIN, '在'],
        [RICH_COLOR_YELLOW, roomName],
        [RICH_COLOR_PLAIN, '中抢到'],
        [RICH_COLOR_YELLOW, str(count)],
        [RICH_COLOR_YELLOW, '红包券！']
    ]

dizhu_red_envelope_bomb._mk_red_envelope_rich_tex = _mk_red_envelope_rich_text
