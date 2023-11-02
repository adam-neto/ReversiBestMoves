from bauhaus import Encoding, proposition, constraint
from bauhaus.utils import count_solutions, likelihood

from nnf import config
from nnf import Var
from nnf import true

from spots import SPOTS
from spots import WHITE_PLAYABLE
from spots import BLACK_PLAYABLE

config.sat_backend = "kissat"

BOARD_WIDTH = 8
BOARD_HEIGHT = 8

# Encoding that will store all of your constraints
E = Encoding()

#FOR THE FEEDBACK: so what we're confused about is what we should have our spots as (objects? or just a grid?) because
# we aren't sure how exactly to apply the constraints to them...


@proposition(E)
class SpotProps:

    def __init__(self, data):
        self.data = data

    def __repr__(self):
        return f"A.{self.data}"

    # I HAVE OFFICIALLY ENTERED THE REPOSITORY. CONSIDER YOUR SELF ENDED.


# Different classes for propositions are useful because this allows for more dynamic constraint creation
# for propositions within that class. For example, you can enforce that "at least one" of the propositions
# that are instances of this class must be true by using a @constraint decorator.
# other options include: at most one, exactly one, at most k, and implies all.
# For a complete module reference, see https://bauhaus.readthedocs.io/en/latest/bauhaus.html
@constraint.at_least_one(E)
@proposition(E)
class Hashable:
    def __hash__(self):
        return hash(str(self))

    def __eq__(self, __value: object) -> bool:
        return hash(self) == hash(__value)

    def __repr__(self):
        return str(self)


@proposition(E)
class Spot(Hashable):
    def __init__(self, piece, white_playable, black_playable):
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
g = SpotProps("g") # game is still going

#draws the board after each turn
# TODO: update the board colours when a player successfully places a piece
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

def get_next_play:
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


def check_full():
    for j in range(BOARD_WIDTH):
        for i in range(BOARD_HEIGHT):
            # should check each spot for e, if none are !e then game is over


def build_theory():
    # if a spot is empty, it must not have black or white (is there a way to set e without adding a constraint?)
    for spot in SPOTS:
        for column in spot:
            E.add_constraint(e >> ~b & ~w)


def check_row_sandwich(x,y):



"""def playable_spot(x, y):
    # Add custom constraints by creating formulas with the variables you created.
    E.add_constraint((a | b) & ~x)
    # Implication
    E.add_constraint(y >> z)
    # Negate a formula
    E.add_constraint(~(x & y))
    # You can also add more customized "fancy" constraints. Use case: you don't want to enforce "exactly one"
    # for every instance of BasicPropositions, but you want to enforce it for a, b, and c.:
    constraint.add_exactly_one(E, a, b, c)

    return E"""

def example_theory():
    # ???

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
    for v, vn in zip([w, b, e, s, r, d, c], 'wbesrdc'):
        # Ensure that you only send these functions NNF formulas
        # Literals are compiled to NNF here
        print(" %s: %.2f" % (vn, likelihood(T, v)))
    print()