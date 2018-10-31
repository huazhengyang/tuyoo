# -*- coding: utf-8 -*-
'''
Created on 2018年7月13日

@author: wangyonghui
'''

from dizhu.games.endgame.engine.move_player import get_resp_moves
from dizhu.games.endgame.engine.utils import get_rest_cards, format_input_cards
import freetime.util.log as ftlog

MAX_SCORE = 1000
MIN_SCORE = -1000

nodes_num = 0

def process_search(index, result_dict,
                   lorder_cards, farmer_cards, current_move, next_player, max_depth):
    score = minmax_search(result_dict, lorder_cards, farmer_cards, current_move, next_player, max_depth=max_depth, alpha=MIN_SCORE, beta=MAX_SCORE)
    result_dict[index] = {'move': current_move, 'score': score}
    return score


def minmax_search(result_dict, lorder_cards, farmer_cards, current_move, next_player, current_depth=0, max_depth=4, alpha=MIN_SCORE, beta=MAX_SCORE):
    current_depth += 1
    if next_player == 'farmer':
        if current_depth == max_depth:
            # get heuristic of each node
            return sum(farmer_cards)
            # return MIN_SCORE
        if len(lorder_cards) == 0:
            return MIN_SCORE  # lorder win, return MIN_SCORE

    elif next_player == 'lorder':
        if current_depth == max_depth:
            # get heuristic of each node
            return sum(lorder_cards)
            # return MAX_SCORE - max_depth
        if len(farmer_cards) == 0:
            return MAX_SCORE  # farmer win, return MAX_SCORE

    if next_player == 'farmer':  # the parameter next_player is current player
        # print '====================score:',score
        # score = sum(lorder_cards)
        score = MIN_SCORE  # For farmer, the default score is MIN_SCORE
        all_moves = get_resp_moves(farmer_cards, current_move)
        # a kind of optimization
        all_moves = sorted(all_moves, key=lambda x: len(x), reverse=True)
        for farmer_move in all_moves:
            fc = get_rest_cards(farmer_cards, farmer_move)
            # score = minmax_search(result_dict,
            #                                  lorder_cards,
            #                                  fc,
            #                                  farmer_move,
            #                                  'lorder', current_depth, max_depth)
            bestval= max(score,minmax_search(result_dict,
                                  lorder_cards,
                                  fc,
                                  farmer_move,
                                  'lorder', current_depth, max_depth,alpha,beta))
            # print '====================bestval_alpha:',bestval
            # beta = min(beta,bestval)
            alpha = max(alpha,bestval)
            # print '====================alpha:',alpha
            if beta <= alpha:
                break
            if bestval == MAX_SCORE:
                break
            # Current player is farmer, so once finds MIN_SCORE, he must choose it.
            # Cut Branches! Ignore the rest farmer moves.
            # if score == MAX_SCORE:
            #     break
        return bestval

    else:  # next_player is 'lorder', the parameter next_player is current player
        score = MAX_SCORE # For 'lorder', the default value is MAX_SCORE
        # score = sum(farmer_cards)
        all_moves = get_resp_moves(lorder_cards, current_move)
        # a kind of optimization
        all_moves = sorted(all_moves, key=lambda x: len(x), reverse=True)
        for lorder_move in all_moves:
            lc = get_rest_cards(lorder_cards, lorder_move)
            # score = minmax_search(result_dict,
            #                                  lc,
            #                                  farmer_cards,
            #                                  lorder_move,
            #                                  'farmer', current_depth, max_depth)
            bestval = min(score,minmax_search(result_dict,
                                  lc,
                                  farmer_cards,
                                  lorder_move,
                                  'farmer', current_depth, max_depth,alpha, beta))
            # print '====================bestval_beta:',bestval
            # alpha = max(alpha,bestval)
            beta = min(beta,bestval)
            # print '====================beta:', beta
            if beta <= alpha:
                break
            # Current player is lorder. So, once MIN_SCORE, choose it!
            # Cut Branches! Ignore the rest lorder moves.
            if bestval == MAX_SCORE:
                break
            # if score == MIN_SCORE:
            #     break
        return bestval


def start_engine(lorder_cards=list(), farmer_cards=list(), lorder_move=list(), max_depth=4):
    """
    根据地主出的牌， 机器人寻找最佳出牌
    """
    result_dict = {}
    bomb_dict=[]
    iSbomb = False

    lorder_cards = format_input_cards(lorder_cards)
    farmer_cards = format_input_cards(farmer_cards)
    lorder_move = format_input_cards(lorder_move)
    for i in range(len(farmer_cards)-3):
        if farmer_cards[i]==farmer_cards[i+3]:
            iSbomb = True
            bomb_dict = farmer_cards[i:i+4]
            break

    all_farmer_moves = get_resp_moves(format_input_cards(farmer_cards), lorder_move)

    all_farmer_moves = sorted(all_farmer_moves, key=lambda x: len(x), reverse=True)
    if iSbomb==True:
        all_farmer_moves.remove(bomb_dict)
        all_farmer_moves.pop()
        all_farmer_moves.append(bomb_dict)
        all_farmer_moves.append([])
    # print '================all_farmer_moves:',all_farmer_moves

    if ftlog.is_debug():
        ftlog.debug('start_engine lorder_move=', lorder_move, 'all_farmer_moves=', all_farmer_moves)

    if len(all_farmer_moves) == 1:  # Pass
        return all_farmer_moves[0], result_dict

    for index, move in enumerate(all_farmer_moves):
        fc = get_rest_cards(farmer_cards, move)
        score = process_search(index, result_dict, lorder_cards, fc, move, 'lorder', max_depth)
        if score == MAX_SCORE:
            break
    # print '====================result_dict:', result_dict

    for _, item in result_dict.items():
        if item['score'] == MAX_SCORE:
            return item['move'], result_dict

    if ftlog.is_debug():
        ftlog.debug('start_engine lorder_move=', lorder_move, 'all_farmer_moves=', all_farmer_moves, 'result_dict=', result_dict)


    allMoves = [it['move'] for it in result_dict.values()]
    allMoves.sort(key=lambda x: (-len(x), sum(x)))
    # print '==========allMoves:',allMoves

    if len(lorder_cards) == 0:
        # 地主不出
        allMoves.sort(key=lambda x: -len(set(x)))

    farmerCards = farmer_cards[:]
    if len(lorder_move) == 1:
        # 地主出的是单牌
        allMoves.sort(key=lambda x: -isSingleCard(x, farmerCards))
        # print '====================single_allMoves:',allMoves
    if ftlog.is_debug():
        ftlog.debug('start_engine allMoves=', allMoves)
    return allMoves[0], result_dict


def isSingleCard(card, farmerCards):
    if len(card) == 0:
        return -99
    if len(card) != 1:
        return -1
    count = 0
    for move in farmerCards:
        if card[0] == move:
            count += 1
    return 1 if count == 1 else 0
