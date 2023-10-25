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
        # hold current player
        self.player = "white"

        # initialize game board
        self.w = [[False for j in range(BOARD_WIDTH)] for i in range(BOARD_HEIGHT)]
        self.b = [[False for j in range(BOARD_WIDTH)] for i in range(BOARD_HEIGHT)]

        # initial white positions
        self.w[3][3] = True
        self.w[4][4] = True

        # initial black positions
        self.b[4][3] = True
        self.b[3][4] = True

    # check info for space availability
    # current player has piece at x,y
    def mine_here(self, x, y):
        if self.player == "white":
            if self.w[x][y]:
                return True
        else:
            if self.b[x][y]:
                return True
        return False

    # current player's opponent has piece at x,y
    def opp_here(self, x, y):
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

    # check sandwiching constraints

    # check if given space allows a sandwich (return boolean)
    def sandwich(self, x, y):
        # only calculate if space is empty
        if self.empty(x, y):
            i = 1  # var used to scan x values
            j = 1  # var used to scan y values

            # check row
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
            i = 1  # reset i after failed test

            # check column
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
            j = 1  # reset j after failed test

            # check diagonal (BUG: NEED TO ADD DIAGONAL CHECKS)

        else:
            return False

    # place a piece and alter the game state
    # BUG: needs to detect sandwiches
    def place_piece(self, x, y, player):
        # check space is empty
        if not self.w[x][y]:
            if not self.b[x][y]:
                if player == "white":
                    self.w[x][y] = True
                else:
                    self.b[x][y] = True

        # switch player after move
        if self.player == "white":
            self.player = "black"
        else:
            self.player = "white"
