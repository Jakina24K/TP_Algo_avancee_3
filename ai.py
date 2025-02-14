# ai.py
import math
from game import GameState

def minimax(state, depth, maximizing_player):
    if depth == 0 or state.is_terminal():
        return state.evaluate(), state
    if maximizing_player:
        max_eval = -math.inf
        best_state = None
        for child in state.get_successors():
            eval, _ = minimax(child, depth - 1, False)
            if eval > max_eval:
                max_eval = eval
                best_state = child
        return max_eval, best_state
    else:
        min_eval = math.inf
        best_state = None
        for child in state.get_successors():
            eval, _ = minimax(child, depth - 1, True)
            if eval < min_eval:
                min_eval = eval
                best_state = child
        return min_eval, best_state

def alphabeta(state, depth, alpha, beta, maximizing_player):
    if depth == 0 or state.is_terminal():
        return state.evaluate(), state
    if maximizing_player:
        max_eval = -math.inf
        best_state = None
        for child in state.get_successors():
            eval, _ = alphabeta(child, depth - 1, alpha, beta, False)
            if eval > max_eval:
                max_eval = eval
                best_state = child
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        return max_eval, best_state
    else:
        min_eval = math.inf
        best_state = None
        for child in state.get_successors():
            eval, _ = alphabeta(child, depth - 1, alpha, beta, True)
            if eval < min_eval:
                min_eval = eval
                best_state = child
            beta = min(beta, eval)
            if beta <= alpha:
                break
        return min_eval, best_state
