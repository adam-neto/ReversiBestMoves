from bauhaus import Encoding, proposition, constraint
from bauhaus.utils import count_solutions, likelihood

from nnf import config, false
from nnf import Var
from nnf import true

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


@proposition(E)
class SpotProps:

    def __init__(self, data):
        self.data = data

    def __repr__(self):
        return f"A.{self.data}"


# Different classes for propositions are useful because this allows for more dynamic constraint creation
# for propositions within that class. For example, you can enforce that "at least one" of the propositions
# that are instances of this class must be true by using a @constraint decorator.
# other options include: at most one, exactly one, at most k, and implies all.
# For a complete module reference, see https://bauhaus.readthedocs.io/en/latest/bauhaus.html
# piece placement on the board
@proposition(E)
class Piece:
    def __init__(self, x, y, colour) -> None:
        self.x = x
        self.y = y
        self.colour = colour

    def __repr__(self) -> str:
        return f"Piece({self.colour}, {self.x}, {self.y})"


@proposition(E)
class Spot(Piece):
    def __init__(self, empty, piece, white_playable, black_playable):
        self.empty = empty
        self.piece = piece
        self.wp = white_playable
        self.bp = black_playable

    def __str__(self):
        return f"(is spot playable: {self.playable})"


# sets the constraint for each spot on the board
spot_props = []
for spot in SPOTS:
    for wp in WHITE_PLAYABLE:
        for bp in BLACK_PLAYABLE:
            spot_props.append(Spot(spot, wp, bp))

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
w = SpotProps("w")  # spot has a white piece
b = SpotProps("b")  # spot has a black piece
e = SpotProps("e")  # spot is empty
p = SpotProps("p")  # spot is playable
r = SpotProps("r")  # row is playable
c = SpotProps("c")  # column is playable
d = SpotProps("d")  # diagonal is playable


# draws the board after each turn
# TODO: update the board colours when a player successfully places a piece


#
def draw_board(self):
    total_white = 0
    total_black = 0
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


# TODO: deal with edge cases

# ensure user move is in board range
def valid_move(x, y):
    valid_x = 0 <= x <= 7
    valid_y = 0 <= y <= 7
    E.add_constraint(valid_x & valid_y)


def is_spot_playable(x, y):
    # check if empty
    empty = SPOTS[x][y] == 'e'

    # check if row is playable
    playable = false
    row_sand = false
    col_sand = false
    dia_sand = false
    before = SPOTS[x][y - 1] == 'b'
    after = SPOTS[x][y + 1] == 'b'
    beside_b = before | after

    if beside_b:
        if before:
            n = 2
            while n < y:
                if SPOTS[x][y - n] == 'w':
                    row_sand = true
                    break
                elif SPOTS[x][y - n] == 'e':
                    break
                n = n + 1
        elif after:
            n = 2
            while n > 2:
                if SPOTS[x][y + n] == 'w':
                    row_sand = true
                    break
                elif SPOTS[x][y + n] == 'e':
                    break
                n = n + 1

        E.add_constraint(playable >> ((row_sand | col_sand | dia_sand) & empty))


def get_next_play():
    user_move = input("Player ---- enter your next coordinates: ").split(' ')
    x = int(user_move[0])
    y = user_move[1]
    return x, y


# each spot on the board should either be white, black, or neither (empty)
def ensure_valid_board(E):
    for i in range(BOARD_HEIGHT):
        for j in range(BOARD_WIDTH):
            E.add_constraint(e[i][j] >> (~w[i][j] & ~w[i][j]))
            if spots.SPOTS[i][j] == 'w':
                E.add_constraint(w[i][j] & ~b[i][j])
            elif spots.SPOTS[i][j] == 'b':
                E.add_constraint(~w[i][j] & b[i][j])


def check_empty(x, y):
    return


def check_full():
    print('check')
    for j in range(BOARD_WIDTH):
        for i in range(BOARD_HEIGHT):
            E.add_constraint(~e[i][j])  # true if all spots are not empty


# should check each spot for e, if none are !e then game is over


def build_theory():
    # if a spot is empty, it must not have black or white (is there a way to set e without adding a constraint?)
    for spot in SPOTS:
        for column in spot:
            E.add_constraint(e >> ~b & ~w)

    # TODO: run all the other conditionals here to ensure E is held

    return E


def check_row_sandwich(x, y):
    for spots in SPOTS:
        # rij → (((bi-1 j) ∧ (wi-n j ) ∧ (¬(ei-2 j ∨ ei-3 j ∨ … ∨ ei-(n+1) j)) ∨ ((bi+1 j) ∧ (wi+n j ) ∧ (¬(ei+2 j ∨
        # ei+3 j ∨ … ∨ ei+(n-1) j))), where 2 <= n <= i
        E.add_constraint(wp >> spots[1])


def example_theory():
    # the example theory will be built here, we are just working on setting the constraints
    return


# TODO: error log to explain why the user can't move there

if __name__ == "__main__":
    T = example_theory()
    # Don't compile until you're finished adding all your constraints!
    T = T.compile()
    # After compilation (and only after), you can check some of the properties
    # of your model:
    print("\nSatisfiable: %s" % T.satisfiable())
    print("# Solutions: %d" % count_solutions(T))
    print("   Solution: %s" % T.solve())

    print("\nVariable likelihoods:")
    for v, vn in zip([w, b, e, r, d, c, p], 'wberdcp'):
        # Ensure that you only send these functions NNF formulas
        # Literals are compiled to NNF here
        print(" %s: %.2f" % (vn, likelihood(T, v)))
    print()
