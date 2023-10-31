from bauhaus import Encoding, proposition, constraint
from bauhaus.utils import count_solutions, likelihood

# These two lines make sure a faster SAT solver is used.
from nnf import config

config.sat_backend = "kissat"

# Encoding that will store all of your constraints
E = Encoding()


# To create propositions, create classes for them first, annotated with "@proposition" and the Encoding
@proposition(E)
class BasicPropositions:

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
    def __init__(self, black, white, empty, r, c, d, playable):
        self.black = black
        self.white = white
        self.empty = empty
        self.r = r
        self.c = c
        self.d = d
        self.playable = playable

    def __str__(self):
        return f"(is spot playable: {self.playable})"

# i think we need to have an 2d array for all the spots

# the propositions should be if a white piece is there, if a black piece is there, if it is playable, if r, if c, if d
# should loop through each spot, so each spot should be part of a 2d array?
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

# same for diagonals and columns
# then, if it is playable, passes to game info and game info finds all the other colour pieces to eliminate

# does game state update in run or in gameinfo?

w = BasicPropositions("w")  # spot has a white piece
b = BasicPropositions("b")  # spot has a black piece
e = BasicPropositions("e")  # spot is empty
p = BasicPropositions("p")  # spot is playable
r = BasicPropositions("r")  # row is playable
c = BasicPropositions("c")  # column is playable
d = BasicPropositions("d")  # diagonal is playable


# Build an example full theory for your setting and return it.
#
#  There should be at least 10 variables, and a sufficiently large formula to describe it (>50 operators).
#  This restriction is fairly minimal, and if there is any concern, reach out to the teaching staff to clarify
#  what the expectations are.



def still_playing():

    E.add_constraint(a & b)


def playable_spot(x, y):
    # Add custom constraints by creating formulas with the variables you created. 
    E.add_constraint((a | b) & ~x)
    # Implication
    E.add_constraint(y >> z)
    # Negate a formula
    E.add_constraint(~(x & y))
    # You can also add more customized "fancy" constraints. Use case: you don't want to enforce "exactly one"
    # for every instance of BasicPropositions, but you want to enforce it for a, b, and c.:
    constraint.add_exactly_one(E, a, b, c)

    return E


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
