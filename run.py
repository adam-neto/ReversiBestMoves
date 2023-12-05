from bauhaus import Encoding, proposition, constraint, Or, And
from bauhaus.utils import count_solutions, likelihood

from nnf import config
from nnf import Var
from nnf import true
from nnf import false

import spots
from spots import SPOTS
from spots import WHITE_PLAYABLE
from spots import BLACK_PLAYABLE

config.sat_backend = "kissat"

BOARD_WIDTH = 8
BOARD_HEIGHT = 8

# Encoding that will store all of your constraints
E = Encoding()


# FOR THE FEEDBACK: so what we're confused about is what we should have our spots as (objects? or just a grid?) because
# we aren't sure how exactly to apply the constraints to them...


# @proposition(E)
# class SpotProps:
#
#     def __init__(self, x, y):
#         self.x = x
#         self.y = y
#
#     def __repr__(self):
#         return f"A.{self.data}"


# Different classes for propositions are useful because this allows for more dynamic constraint creation
# for propositions within that class. For example, you can enforce that "at least one" of the propositions
# that are instances of this class must be true by using a @constraint decorator.
# other options include: at most one, exactly one, at most k, and implies all.
# For a complete module reference, see https://bauhaus.readthedocs.io/en/latest/bauhaus.html
# piece placement on the board
# @proposition(E)
# class Piece:
#     def __init__(self, x, y, colour) -> None:
#         self.x = x
#         self.y = y
#         self.colour = colour
#
#     def __repr__(self) -> str:
#         return f"Piece({self.colour}, {self.x}, {self.y})"


# @proposition(E)
# class Spot(Piece):
#     def __init__(self, empty, piece, white_playable, black_playable):
#         self.empty = empty
#         self.piece = piece
#         self.wp = white_playable
#         self.bp = black_playable
#
#     def __str__(self):
#         return f"(is spot playable: {self.playable})"

# sets the constraint for each spot on the board
# spot_props = []
# for spot in SPOTS:
#     for wp in WHITE_PLAYABLE:
#         for bp in BLACK_PLAYABLE:
#             spot_props.append(Spot(spot, wp, bp))

# the propositions should be if a white piece is there, if a black piece is there, if it is playable, if r, if c, if d
# functions should be: check if spot it playable by row, check if spot is playable by column, check if game is over

# for s in spots : if at least one: p
# empty check: if not w and not b
# playable check: if empty and (row or column or diagonal)
# row check(coordinate user wants to play: x,y and assume white player):
#       for spot in spots[x]:
#           spot[y-1] = b and spot[y] = e and for 0 <= i <= (y-2):
#                at least one: spot[i] = w and for all: for i < j < (y-2):
#                   spot[j] = b
#           OR spot[y+1] = b and spot[y] = e and for (y+2) <= i < 8:
# #                at least one: spot[i] = w and for all: for (y+2) < j < i:
# #                   spot[j] = b

# same for diagonals and columns, all in GameInfo, but how to convert to constraints?
# then, if it is playable, passes to game info and game info finds all the other colour pieces to eliminate (POST DRAFT)

# I'm not sure how to set these props according to the spots.py file
# w = SpotProps("w")  # spot has a white piece
# b = SpotProps("b")  # spot has a black piece
# e = SpotProps("e")  # spot is empty
# p = SpotProps("p")  # spot is playable
# r = SpotProps("r")  # row is playable
# c = SpotProps("c")  # column is playable
# d = SpotProps("d")  # diagonal is playable

# draws the board after each turn
# TODO: update the board colours when a player successfully places a piece

# create hashable object
class Hashable:
    def __hash__(self):
        return hash(str(self))

    def __eq__(self, __value: object) -> bool:
        return hash(self) == hash(__value)

    def __repr__(self):
        return str(self)


# class for piece proposition
@proposition(E)
class Piece(Hashable):
    def __init__(self, colour, x, y):
        self.colour = colour
        self.x = x
        self.y = y

    def __str__(self):
        return f"{self.colour}{self.x}{self.y}"


# grid format for each piece colour
def piece_array(colour):
    board = []
    for j in range(BOARD_HEIGHT):
        row = []
        for i in range(BOARD_WIDTH):
            row.append(Piece(colour, i, j))
        board.append(row)
    return board


# create a grid of variables for each piece colour (w00, w01 etc.) that hold a boolean value
w = piece_array('w')
b = piece_array('b')


def set_board(board):
    # start proposition as true to add conjuncts to
    # there will always be either not a white piece or not a black piece on a position
    board_prop = ~Piece(f'w', f'0', f'0') | ~Piece(f'b', f'0', f'0')

    # set propositions of piece position for every position on the grid
    for j in range(BOARD_HEIGHT):
        for i in range(BOARD_WIDTH):
            # set boolean logic of current position on board
            if board[j][i] == 'w':
                # for spaces where we have a white piece, add that to the board proposition
                board_prop &= Piece(f'w', f'{i}', f'{j}')
                # in spaces we have a white piece, add the negation
                # so that bij being false will make the prop true
                board_prop &= ~Piece(f'b', f'{i}', f'{j}')
            elif board[j][i] == 'b':
                board_prop &= ~Piece(f'w', f'{i}', f'{j}')
                board_prop &= Piece(f'b', f'{i}', f'{j}')
            else:
                board_prop &= ~Piece(f'w', f'{i}', f'{j}')
                board_prop &= ~Piece(f'b', f'{i}', f'{j}')
    return board_prop


def row_sandwich(x, y):
    # start row prop as false because it uses disjunctions, not conjunctions
    # there will never be both pieces on the same position
    row_prop = Piece(f'w', f'{x}', f'{y}') & Piece(f'b', f'{x}', f'{y}')

    # count to the left
    temp_row_prop = ~Piece(f'w', f'{x}', f'{y}') & ~Piece(f'b', f'{x}', f'{y}')  # space must ALWAYS be empty for THIS disjunction to be true
    counter_x = 1
    while (x - counter_x) >= 1:  # stop scanning when at the space one away from the edge
        # add that the next to the left is black
        temp_row_prop &= Piece(f'b', f'{x - counter_x}', f'{y}')
        # add current sequence of black pieces as a disjunction, such that the end MUST be white
        counter_x += 1
        row_prop |= temp_row_prop & Piece(f'w', f'{x - counter_x}', f'{y}')

    # count to the right
    temp_row_prop = ~Piece(f'w', f'{x}', f'{y}') & ~Piece(f'b', f'{x}', f'{y}')  # space must ALWAYS be empty for THIS disjunction to be true
    counter_x = 1
    # stop scanning when at the space one away from the edge (BOARD_WIDTH-1 IS MAX INDEX)
    while (x + counter_x) <= (BOARD_WIDTH - 2):
        # add that the next to the right is black
        temp_row_prop &= Piece(f'b', f'{x + counter_x}', f'{y}')
        # add current sequence of black pieces as a disjunction, such that the end MUST be white
        counter_x += 1
        row_prop |= temp_row_prop & Piece(f'w', f'{x + counter_x}', f'{y}')

    return row_prop


def column_sandwich(x, y):
    # start col prop as false because it uses disjunctions, not conjunctions
    # there will never be both pieces on the same position
    col_prop = Piece(f'w', f'{x}', f'{y}') & Piece(f'b', f'{x}', f'{y}')

    # count upwards
    temp_col_prop = ~Piece(f'w', f'{x}', f'{y}') & ~Piece(f'b', f'{x}', f'{y}')  # space must ALWAYS be empty for THIS disjunction to be true
    counter_y = 1
    while (y - counter_y) >= 1:  # stop scanning when at the space one away from the edge
        # add that the next above is black
        temp_col_prop &= Piece(f'b', f'{x}', f'{y - counter_y}')
        # add current sequence of black pieces as a disjunction, such that the end MUST be white
        counter_y += 1
        col_prop |= temp_col_prop & Piece(f'w', f'{x}', f'{y - counter_y}')

    # count downwards
    temp_col_prop = ~Piece(f'w', f'{x}', f'{y}') & ~Piece(f'b', f'{x}', f'{y}')  # space must ALWAYS be empty for THIS disjunction to be true
    counter_y = 1
    while (y + counter_y) <= (BOARD_HEIGHT - 2):  # stop scanning when at the space one away from the edge
        # add that the next below is black
        temp_col_prop &= Piece(f'b', f'{x}', f'{y + counter_y}')
        # add current sequence of black pieces as a disjunction, such that the end MUST be white
        counter_y += 1
        col_prop |= temp_col_prop & Piece(f'w', f'{x}', f'{y + counter_y}')

    return col_prop


def diagonal_sandwich(x, y):
    # start diag prop as false because it uses disjunctions, not conjunctions
    # there will never be both pieces on the same position
    diag_prop = Piece(f'w', f'{x}', f'{y}') & Piece(f'b', f'{x}', f'{y}')

    # count up and left
    temp_diag_prop = ~Piece(f'w', f'{x}', f'{y}') & ~Piece(f'b', f'{x}', f'{y}')  # space must ALWAYS be empty for THIS disjunction to be true
    counter_xy = 1
    while (x - counter_xy) >= 1 and (y - counter_xy) >= 1:  # stop scanning when at the space one away from the edge
        # add that the next above and left is black
        temp_diag_prop &= Piece(f'b', f'{x - counter_xy}', f'{y - counter_xy}')
        # add current sequence of black pieces as a disjunction, such that the end MUST be white
        counter_xy += 1
        diag_prop |= temp_diag_prop & Piece(f'w', f'{x - counter_xy}', f'{y - counter_xy}')

    # count up and right
    temp_diag_prop = ~Piece(f'w', f'{x}', f'{y}') & ~Piece(f'b', f'{x}', f'{y}')  # space must ALWAYS be empty for THIS disjunction to be true
    counter_xy = 1
    while (x + counter_xy) <= (BOARD_WIDTH - 2) and (y - counter_xy) >= 1:
        # add that the next above and left is black
        temp_diag_prop &= Piece(f'b', f'{x + counter_xy}', f'{y - counter_xy}')
        # add current sequence of black pieces as a disjunction, such that the end MUST be white
        counter_xy += 1
        diag_prop |= temp_diag_prop & Piece(f'w', f'{x + counter_xy}', f'{y - counter_xy}')

    # count down and left
    temp_diag_prop = ~Piece(f'w', f'{x}', f'{y}') & ~Piece(f'b', f'{x}', f'{y}')  # space must ALWAYS be empty for THIS disjunction to be true
    counter_xy = 1
    while (x - counter_xy) >= 1 and (y + counter_xy) <= (BOARD_HEIGHT - 2):
        # add that the next above and left is black
        temp_diag_prop &= Piece(f'b', f'{x - counter_xy}', f'{y + counter_xy}')
        # add current sequence of black pieces as a disjunction, such that the end MUST be white
        counter_xy += 1
        diag_prop |= temp_diag_prop & Piece(f'w', f'{x - counter_xy}', f'{y + counter_xy}')

    # count down and right
    temp_diag_prop = ~Piece(f'w', f'{x}', f'{y}') & ~Piece(f'b', f'{x}', f'{y}')  # space must ALWAYS be empty for THIS disjunction to be true
    counter_xy = 1
    while (x + counter_xy) <= (BOARD_WIDTH - 2) and (y + counter_xy) <= (BOARD_HEIGHT - 2):
        # add that the next above and left is black
        temp_diag_prop &= Piece(f'b', f'{x + counter_xy}', f'{y + counter_xy}')
        # add current sequence of black pieces as a disjunction, such that the end MUST be white
        counter_xy += 1
        diag_prop |= temp_diag_prop & Piece(f'w', f'{x + counter_xy}', f'{y + counter_xy}')

    return diag_prop


# def mine_here(self, x, y):
#     # check if out of range
#     if 0 <= x < BOARD_WIDTH and 0 <= y < BOARD_HEIGHT:
#         if self.w[y][x]:
#             return true
#     return false
#
# def opp_here(self, x, y):
#     # check if out of range
#     if 0 <= x < BOARD_WIDTH and 0 <= y < BOARD_HEIGHT:
#         if self.b[y][x]:
#             return true
#     return false
#
# def empty(self, x, y):
#     if self.mine_here(x, y) or self.opp_here(x, y):
#         return false
#     return true
#
# def row_sandwich(self, x, y):
#     i = 1  # scan x values (increment)
#
#     # left side
#     while self.opp_here(x - i, y):
#         i += 1
#         if self.mine_here(x - i, y):
#             return true
#     i = 1  # reset i after test
#
#     # right side
#     while self.opp_here(x + i, y):
#         i += 1
#         if self.mine_here(x + i, y):
#             return true
#
# def column_sandwich(self, x, y):
#     j = 1  # scan y values (increment)
#
#     # above
#     while self.opp_here(x, y - j):
#         j += 1
#         if self.mine_here(x, y - j):
#             return true
#     j = 1  # reset j after failed test
#
#     # below
#     while self.opp_here(x, y + j):
#         j += 1
#         if self.mine_here(x, y + j):
#             return true
#
# def diagonal_sandwich(self, x, y):
#     i = 1  # scan x values (increment)
#     j = 1  # scan y values (increment)
#
#     # up-left
#     while self.opp_here(x - i, y - j):
#         i += 1
#         j += 1
#         if self.mine_here(x - i, y - j):
#             return true
#     i = 1  # reset i after failed test
#     j = 1  # reset j after failed test
#
#     # up-right
#     while self.opp_here(x + i, y - j):
#         i += 1
#         j += 1
#         if self.mine_here(x + i, y - j):
#             return true
#     i = 1  # reset i after failed test
#     j = 1  # reset j after failed test
#
#     # down-left
#     while self.opp_here(x - i, y + j):
#         i += 1
#         j += 1
#         if self.mine_here(x - i, y + j):
#             return true
#     i = 1  # reset i after failed test
#     j = 1  # reset j after failed test
#
#     # down-right
#     while self.opp_here(x + i, y + j):
#         i += 1
#         j += 1
#         if self.mine_here(x + i, y + j):
#             return true

def build_theory():
    # SHOULD SCAN FOR ANY POSSIBLE SANDWICH
    for j in range(BOARD_HEIGHT):
        for i in range(BOARD_WIDTH):
            row_sand = row_sandwich(i, j)
            col_sand = column_sandwich(i, j)
            diag_sand = diagonal_sandwich(i, j)
            # sandwich constraints include whether the position is empty
            print(f'{i}{j}{row_sand | col_sand | diag_sand}')
            E.add_constraint(row_sand | col_sand | diag_sand)
    return E


def draw_board(self):
    for j in range(BOARD_HEIGHT):
        row = ""
        for i in range(BOARD_WIDTH):
            if self.w[j][i]:
                row += "w" + " "
            elif self.b[j][i]:
                row += "b" + " "
            else:
                row += "." + " "
        print(row)


# TODO: deal with edge cases

#
#
#
# RENA'S WORK FROM HERE ON OUT
#
#
#
# # ensure user move is in board range
# def valid_move(x, y):
#     valid_x = 0 <= x <= 7
#     valid_y = 0 <= y <= 7
#     E.add_constraint(valid_x & valid_y)
#
#
# def is_spot_playable(x, y):
#     # check if empty
#     empty = SPOTS[x][y] == 'e'
#
#     # check if row is playable
#     playable = false
#     row_sand = false
#     col_sand = false
#     dia_sand = false
#     before = SPOTS[x][y - 1] == 'b'
#     after = SPOTS[x][y + 1] == 'b'
#     beside_b = before | after
#
#     if beside_b:
#         if before:
#             n = 2
#             while n < y:
#                 if SPOTS[x][y - n] == 'w':
#                     row_sand = true
#                     break
#                 elif SPOTS[x][y - n] == 'e':
#                     break
#                 n = n + 1
#         elif after:
#             n = 2
#             while n > 2:
#                 if SPOTS[x][y + n] == 'w':
#                     row_sand = true
#                     break
#                 elif SPOTS[x][y + n] == 'e':
#                     break
#                 n = n - 1
#
#         E.add_constraint(playable >> ((row_sand | col_sand | dia_sand) & empty))
#
#
# def get_next_play():
#     user_move = input("Player ---- enter your next coordinates: ").split(' ')
#     x = int(user_move[0])
#     y = user_move[1]
#     return x, y
#
#
# # each spot on the board should either be white, black, or neither (empty)
# def ensure_valid_board(E):
#     for i in range(BOARD_HEIGHT):
#         for j in range(BOARD_WIDTH):
#             E.add_constraint(e[i][j] >> (~w[i][j] & ~w[i][j]))
#             if spots.SPOTS[i][j] == 'w':
#                 E.add_constraint(w[i][j] & ~b[i][j])
#             elif spots.SPOTS[i][j] == 'b':
#                 E.add_constraint(~w[i][j] & b[i][j])
#
#
# def check_empty(x, y):
#     return
#
#
# def check_full():
#     print('check')
#     for j in range(BOARD_WIDTH):
#         for i in range(BOARD_HEIGHT):
#             E.add_constraint(~e[i][j])  # true if all spots are not empty
#
#
# # should check each spot for e, if none are !e then game is over
#
#
# def build_theory():
#     # if a spot is empty, it must not have black or white (is there a way to set e without adding a constraint?)
#     for spot in SPOTS:
#         for column in spot:
#             E.add_constraint(e >> ~b & ~w)
#
#     # TODO: run all the other conditionals here to ensure E is held
#
#     return E
#
#
# def check_row_sandwich(x, y):
#     for spots in SPOTS:
#         # rij → (((bi-1 j) ∧ (wi-n j ) ∧ (¬(ei-2 j ∨ ei-3 j ∨ … ∨ ei-(n+1) j)) ∨ ((bi+1 j) ∧ (wi+n j ) ∧ (¬(ei+2 j ∨
#         # ei+3 j ∨ … ∨ ei+(n-1) j))), where 2 <= n <= i
#         E.add_constraint(wp >> spots[1])
#
#
# # def example_theory():
# #     # the example theory will be built here, we are just working on setting the constraints
# #     return


def test1():
    board = [
        ['.', '.', '.', '.', '.', '.', '.', '.'],
        ['.', '.', '.', '.', '.', '.', '.', '.'],
        ['.', '.', '.', '.', '.', '.', '.', '.'],
        ['.', '.', '.', 'w', 'b', '.', '.', '.'],
        ['.', '.', '.', 'b', 'w', '.', '.', '.'],
        ['.', '.', '.', '.', '.', '.', '.', '.'],
        ['.', '.', '.', '.', '.', '.', '.', '.'],
        ['.', '.', '.', '.', '.', '.', '.', '.'],
    ]

    return set_board(board)


# TODO: error log to explain why the user can't move there

if __name__ == "__main__":
    # Don't compile until you're finished adding all your constraints!
    # MAKE PROPS 1 RETURN THE PROPOSITIONS FOR THE FIRST TEST CASE
    board1 = test1()
    print(board1)
    T = build_theory()
    #T.add_constraint(board1)
    T = T.compile()

    # After compilation (and only after), you can check some properties
    # of your model:

    print("\nSatisfiable: %s" % T.satisfiable())
    print("# Solutions: %d" % count_solutions(T))
    print("   Solution: %s" % T.solve())

    # print("\nVariable likelihoods:")
    # for v, vn in zip([w, b, e, r, d, c, p], 'wberdcp'):
    #     # Ensure that you only send these functions NNF formulas
    #     # Literals are compiled to NNF here
    #     print(" %s: %.2f" % (vn, likelihood(T, v)))
    # print()
