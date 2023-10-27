"""
This file creates a Reversi game state
to be passed in for modelling
It also contains methods for updating
the game state, and checking if
positions hold available moves

Author: Adam Neto
Date Updated: 10/26/23
"""

# board size info (constant)
BOARD_WIDTH = 8
BOARD_HEIGHT = 8


class GameState:

    # initialize game state
    def __init__(self):
        # hold current player
        self.player = "white"

        # hold coordinates of pieces being sandwiched each turn
        self.sandwiched = []

        # initialize game board (booleans for each black and white)
        self.w = [[False for j in range(BOARD_WIDTH)] for i in range(BOARD_HEIGHT)]
        self.b = [[False for j in range(BOARD_WIDTH)] for i in range(BOARD_HEIGHT)]

        # initial white positions
        self.w[int(BOARD_WIDTH / 2 - 1)][int(BOARD_HEIGHT / 2 - 1)] = True  # middle top-left starter
        self.w[int(BOARD_WIDTH / 2)][int(BOARD_HEIGHT / 2)] = True  # middle bottom-right starter

        # initial black positions
        self.b[int(BOARD_WIDTH / 2)][int(BOARD_HEIGHT / 2 - 1)] = True  # middle top-right starter
        self.b[int(BOARD_WIDTH / 2 - 1)][int(BOARD_HEIGHT / 2)] = True  # middle bottom-left starter

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
    # store sandwiched positions as to not double count
    def append_sandwiched(self, temp_sandwiched):
        for pos in temp_sandwiched:
            if pos not in self.sandwiched:
                self.sandwiched.append(pos)

    def row_sand(self, x, y):
        temp_sandwiched = []  # hold temporary sandwiched coordinates
        i = 1  # scan x values (increment)

        # left side
        while self.opp_here(x - i, y):
            temp_sandwiched.append([x - i, y])
            i += 1
            if self.mine_here(x - i, y):
                self.append_sandwiched(temp_sandwiched)
        temp_sandwiched = []  # reset temp sandwiched values
        i = 1  # reset i after test

        # right side
        while self.opp_here(x + i, y):
            temp_sandwiched.append([x + i, y])
            i += 1
            if self.mine_here(x + i, y):
                self.append_sandwiched(temp_sandwiched)

    def column_sand(self, x, y):
        temp_sandwiched = []  # hold temporary sandwiched coordinates
        j = 1  # scan y values (increment)

        # above
        while self.opp_here(x, y - j):
            temp_sandwiched.append([x, y - j])
            j += 1
            if self.mine_here(x, y - j):
                self.append_sandwiched(temp_sandwiched)
        temp_sandwiched = []  # reset temp sandwiched values
        j = 1  # reset j after failed test

        # below
        while self.opp_here(x, y + j):
            temp_sandwiched.append([x, y + j])
            j += 1
            if self.mine_here(x, y + j):
                self.append_sandwiched(temp_sandwiched)

    def diagonal_sand(self, x, y):
        temp_sandwiched = []  # hold temporary sandwiched coordinates
        i = 1  # scan x values (increment)
        j = 1  # scan y values (increment)

        # up-left
        while self.opp_here(x - i, y - j):
            temp_sandwiched.append([x - i, y - j])
            i += 1
            j += 1
            if self.mine_here(x - i, y - j):
                self.append_sandwiched(temp_sandwiched)
        temp_sandwiched = []  # reset temp sandwiched values
        i = 1  # reset i after failed test
        j = 1  # reset j after failed test

        # up-right
        while self.opp_here(x + i, y - j):
            temp_sandwiched.append([x + i, y - j])
            i += 1
            j += 1
            if self.mine_here(x + i, y - j):
                self.append_sandwiched(temp_sandwiched)
        temp_sandwiched = []  # reset temp sandwiched values
        i = 1  # reset i after failed test
        j = 1  # reset j after failed test

        # down-left
        while self.opp_here(x - i, y + j):
            temp_sandwiched.append([x - i, y + j])
            i += 1
            j += 1
            if self.mine_here(x - i, y + j):
                self.append_sandwiched(temp_sandwiched)
        temp_sandwiched = []  # reset temp sandwiched values
        i = 1  # reset i after failed test
        j = 1  # reset j after failed test

        # down-right
        while self.opp_here(x + i, y + j):
            temp_sandwiched.append([x + i, y + j])
            i += 1
            j += 1
            if self.mine_here(x + i, y + j):
                self.append_sandwiched(temp_sandwiched)

    # check if there are ANY sandwich possibilities
    def sandwich(self, x, y):
        # only calculate if in range
        if 0 <= x < BOARD_WIDTH and 0 <= y < BOARD_HEIGHT:
            # only calculate if space is empty
            if self.empty(x, y):
                # check for sandwiches
                self.row_sand(x, y)
                self.column_sand(x, y)
                self.diagonal_sand(x, y)
                if len(self.sandwiched) > 0:
                    return True
        return False

    # place a piece and alter the game state
    def place_piece(self, x, y):
        # check if space is playable
        if self.sandwich(x, y):
            # place piece and switch player
            if self.player == "white":
                self.w[x][y] = True

                # swap sandwiched pieces
                for pos in self.sandwiched:
                    self.w[pos[0]][pos[1]] = True
                    self.b[pos[0]][pos[1]] = False
                self.player = "black"
            else:
                self.b[x][y] = True

                # swap sandwiched pieces
                for pos in self.sandwiched:
                    self.b[pos[0]][pos[1]] = True
                    self.w[pos[0]][pos[1]] = False
                self.player = "white"
            self.sandwiched = []
            return True
        return False

    def check_full(self):
        for j in range(BOARD_WIDTH):
            for i in range(BOARD_HEIGHT):
                if not (self.w[i][j] or self.b[i][j]):
                    return False
        return True

    # draw the current board (only after each turn)
    def draw_board(self):
        total_white = 0;
        total_black = 0;
        for j in range(BOARD_WIDTH):
            row = ""
            for i in range(BOARD_HEIGHT):
                if self.w[i][j]:
                    row += "w" + " "
                    total_white += 1
                elif self.b[i][j]:
                    row += "b" + " "
                    total_black += 1
                else:
                    row += "." + " "
            print(row)

        if self.check_full():
            print("Game over. Final Score:")
            print("White: " + str(total_white))
            print("Black: " + str(total_black))
