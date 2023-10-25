"""
This file creates a Reversi game state
to be passed in for modelling
"""

# board size info (constant)
BOARD_WIDTH = 8
BOARD_HEIGHT = 8


class GameState:

    def __init__(self):
        # initialize game board
        w = [[False for j in range(BOARD_WIDTH)] for i in range(BOARD_HEIGHT)]
        b = [[False for j in range(BOARD_WIDTH)] for i in range(BOARD_HEIGHT)]

        # initial white positions
        w[3][3] = True
        w[4][4] = True

        # initial black positions
        b[4][3] = True
        b[3][4] = True
