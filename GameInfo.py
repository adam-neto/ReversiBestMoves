"""
This file creates a Reversi game state
to be passed in for modelling
"""

# board size info (constant)
BOARD_WIDTH = 8
BOARD_HEIGHT = 8


class GameState:

    # initialize game state
    def __init__(self):
        # initialize game board
        self.w = [[False for j in range(BOARD_WIDTH)] for i in range(BOARD_HEIGHT)]
        self.b = [[False for j in range(BOARD_WIDTH)] for i in range(BOARD_HEIGHT)]

        # initial white positions
        self.w[3][3] = True
        self.w[4][4] = True

        # initial black positions
        self.b[4][3] = True
        self.b[3][4] = True

    def place_piece(self, x, y, player):
        # check space is empty
        if not self.w[x][y]:
            if not self.b[x][y]:
                if player == "white":
                    self.w[x][y] = True
                else:
                    self.b[x][y] = True
