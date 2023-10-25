"""
This file creates a Reversi game state
to be passed in for modelling
It also contains methods for updating
the game state, and checking if
positions hold available moves

Author: Adam Neto
Date Updated: 10/25/23
"""

# board size info (constant)
BOARD_WIDTH = 8
BOARD_HEIGHT = 8


class GameState:

    # initialize game state
    def __init__(self):
        # hold current player
        self.player = "white"

        # initialize game board (booleans for each black and white)
        self.w = [[False for j in range(BOARD_WIDTH)] for i in range(BOARD_HEIGHT)]
        self.b = [[False for j in range(BOARD_WIDTH)] for i in range(BOARD_HEIGHT)]

        # initial white positions
        self.w[BOARD_WIDTH/2 - 1][BOARD_HEIGHT/2 - 1] = True    # middle top-left starter
        self.w[BOARD_WIDTH/2][BOARD_HEIGHT/2] = True            # middle bottom-right starter

        # initial black positions
        self.b[BOARD_WIDTH/2][BOARD_HEIGHT/2 - 1] = True        # middle top-right starter
        self.b[BOARD_WIDTH/2 - 1][BOARD_HEIGHT/2] = True        # middle bottom-left starter

    # SPACE AVAILABILITY
    # current player has piece at x,y
    def mine_here(self, x, y):
        # check if out of range
        if 0 <= x < BOARD_WIDTH and 0 <= y < BOARD_HEIGHT:
            if self.player == "white":
                if self.w[x][y]:
                    return True
            else:
                if self.b[x][y]:
                    return True
        return False

    # current player's opponent has piece at x,y
    def opp_here(self, x, y):
        # check if out of range
        if 0 <= x < BOARD_WIDTH and 0 <= y < BOARD_HEIGHT:
            if self.player == "white":
                if self.b[x][y]:
                    return True
            else:
                if self.w[x][y]:
                    return True
        return False

    def empty(self, x, y):
        if self.mine_here(x, y) or self.opp_here(x, y):
            return False
        return True

    # SANDWICHING CONSTRAINTS
    def row_sand(self, x, y):
        i = 1  # scan x values (increment)

        # left side
        while self.opp_here(x - i, y):
            i -= 1
            if self.mine_here(x - i, y):
                return True
        i = 1  # reset i after failed test

        # right side
        while self.opp_here(x + i, y):
            i += 1
            if self.mine_here(x + i, y):
                return True

        # no row sandwich if we get to this point
        return False

    def column_sand(self, x, y):
        j = 1  # scan y values (increment)

        # above
        while self.opp_here(x - j, y):
            j -= 1
            if self.mine_here(x - j, y):
                return True
        j = 1  # reset j after failed test

        # below
        while self.opp_here(x + j, y):
            j += 1
            if self.mine_here(x + j, y):
                return True

        # no column sandwich if we get to this point
        return False

    def diagonal_sand(self, x, y):
        i = 1  # scan x values (increment)
        j = 1  # scan y values (increment)

        # up-left
        while self.opp_here(x - i, y - j):
            i -= 1
            j -= 1
            if self.mine_here(x - i, y - j):
                return True
        i = 1  # reset i after failed test
        j = 1  # reset j after failed test

        # up-right
        while self.opp_here(x + i, y - j):
            i += 1
            j -= 1
            if self.mine_here(x + i, y - j):
                return True
        i = 1  # reset i after failed test
        j = 1  # reset j after failed test

        # down-left
        while self.opp_here(x - i, y + j):
            i -= 1
            j += 1
            if self.mine_here(x - i, y + j):
                return True
        i = 1  # reset i after failed test
        j = 1  # reset j after failed test

        # down-right
        while self.opp_here(x + i, y + j):
            i += 1
            j += 1
            if self.mine_here(x + i, y + j):
                return True

        # no diagonal sandwich if we get to this point
        return False

    # check if there are ANY sandwich possibilities
    def sandwich(self, x, y):
        # only calculate if space is empty
        if self.empty(x, y):
            # check for sandwiches
            if self.row_sand(x, y) or self.column_sand(x, y) or self.diagonal_sand(x, y):
                return True
            else:
                return False
        else:
            return False

    # place a piece and alter the game state
    def place_piece(self, x, y):
        # check if space is playable
        if self.sandwich(x, y):
            # place piece and switch player
            if self.player == "white":
                self.w[x][y]
                self.player = "black"
            else:
                self.b[x][y]
                self.player = "white"
