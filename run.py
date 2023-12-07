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


# if and only if nnf formula
def iff(left, right):
    return (~left | right) & (left | ~right)


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
sandwich = piece_array('s')


# sets the constraints for the states of each position on the board (white, black, empty)
def set_board(board):
    # start proposition as true to add conjuncts to
    # there will always be either not a white piece or not a black piece on a position
    board_prop = ~Piece(f'w', f'0', f'0') | ~Piece(f'b', f'0', f'0')

    # set propositions of piece position for every position on the grid
    for j in range(BOARD_HEIGHT):
        for i in range(BOARD_WIDTH):
            # set boolean logic of current position on board
            if board[j][i] == 'w':
                board_prop &= Piece(f'w', f'{i}', f'{j}')
                board_prop &= ~Piece(f'b', f'{i}', f'{j}')
            elif board[j][i] == 'b':
                board_prop &= ~Piece(f'w', f'{i}', f'{j}')
                board_prop &= Piece(f'b', f'{i}', f'{j}')
            else:
                board_prop &= ~Piece(f'w', f'{i}', f'{j}')
                board_prop &= ~Piece(f'b', f'{i}', f'{j}')
    return board_prop


# sandwich methods whether a space causes a sandwich through horizontally, vertically, and diagonally
def row_sandwich(x, y):
    # start row prop as false because it uses disjunctions, not conjunctions
    # there will never be both pieces on the same position
    row_prop = Piece(f'w', f'{x}', f'{y}') & Piece(f'b', f'{x}', f'{y}')

    # count to the left
    temp_row_prop = ~Piece(f'w', f'{x}', f'{y}') & ~Piece(f'b', f'{x}', f'{y}')
    counter_x = 1
    while (x - counter_x) >= 1:  # stop scanning when at the space one away from the edge
        # add that the next to the left is black
        temp_row_prop &= Piece(f'b', f'{x - counter_x}', f'{y}')
        # add current sequence of black pieces as a disjunction, such that the end MUST be white
        counter_x += 1
        row_prop |= temp_row_prop & Piece(f'w', f'{x - counter_x}', f'{y}')

    # count to the right
    temp_row_prop = ~Piece(f'w', f'{x}', f'{y}') & ~Piece(f'b', f'{x}', f'{y}')
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
    temp_col_prop = ~Piece(f'w', f'{x}', f'{y}') & ~Piece(f'b', f'{x}', f'{y}')
    while (y - counter_y) >= 1:  # stop scanning when at the space one away from the edge
        # add that the next above is black
        temp_col_prop &= Piece(f'b', f'{x}', f'{y - counter_y}')
        # add current sequence of black pieces as a disjunction, such that the end MUST be white
        counter_y += 1
        col_prop |= temp_col_prop & Piece(f'w', f'{x}', f'{y - counter_y}')

    # count downwards
    temp_col_prop = ~Piece(f'w', f'{x}', f'{y}') & ~Piece(f'b', f'{x}', f'{y}')
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
    temp_diag_prop = ~Piece(f'w', f'{x}', f'{y}') & ~Piece(f'b', f'{x}', f'{y}')
    counter_xy = 1
    while (x - counter_xy) >= 1 and (y - counter_xy) >= 1:  # stop scanning when at the space one away from the edge
        # add that the next above and left is black
        temp_diag_prop &= Piece(f'b', f'{x - counter_xy}', f'{y - counter_xy}')
        # add current sequence of black pieces as a disjunction, such that the end MUST be white
        counter_xy += 1
        diag_prop |= temp_diag_prop & Piece(f'w', f'{x - counter_xy}', f'{y - counter_xy}')

    # count up and right
    temp_diag_prop = ~Piece(f'w', f'{x}', f'{y}') & ~Piece(f'b', f'{x}', f'{y}')
    counter_xy = 1
    while (x + counter_xy) <= (BOARD_WIDTH - 2) and (y - counter_xy) >= 1:
        # add that the next above and left is black
        temp_diag_prop &= Piece(f'b', f'{x + counter_xy}', f'{y - counter_xy}')
        # add current sequence of black pieces as a disjunction, such that the end MUST be white
        counter_xy += 1
        diag_prop |= temp_diag_prop & Piece(f'w', f'{x + counter_xy}', f'{y - counter_xy}')

    # count down and left
    temp_diag_prop = ~Piece(f'w', f'{x}', f'{y}') & ~Piece(f'b', f'{x}', f'{y}')
    counter_xy = 1
    while (x - counter_xy) >= 1 and (y + counter_xy) <= (BOARD_HEIGHT - 2):
        # add that the next above and left is black
        temp_diag_prop &= Piece(f'b', f'{x - counter_xy}', f'{y + counter_xy}')
        # add current sequence of black pieces as a disjunction, such that the end MUST be white
        counter_xy += 1
        diag_prop |= temp_diag_prop & Piece(f'w', f'{x - counter_xy}', f'{y + counter_xy}')

    # count down and right
    temp_diag_prop = ~Piece(f'w', f'{x}', f'{y}') & ~Piece(f'b', f'{x}', f'{y}')
    counter_xy = 1
    while (x + counter_xy) <= (BOARD_WIDTH - 2) and (y + counter_xy) <= (BOARD_HEIGHT - 2):
        # add that the next above and left is black
        temp_diag_prop &= Piece(f'b', f'{x + counter_xy}', f'{y + counter_xy}')
        # add current sequence of black pieces as a disjunction, such that the end MUST be white
        counter_xy += 1
        diag_prop |= temp_diag_prop & Piece(f'w', f'{x + counter_xy}', f'{y + counter_xy}')

    return diag_prop


def build_theory():
    # SHOULD SCAN FOR ANY POSSIBLE SANDWICH
    # start prop as false because it uses disjunctions, not conjunctions
    # there will never be both pieces on the same position
    constraints = Piece(f'w', f'0', f'0') & Piece(f'b', f'0', f'0')
    for j in range(BOARD_HEIGHT):
        for i in range(BOARD_WIDTH):
            row_sand = row_sandwich(i, j)
            col_sand = column_sandwich(i, j)
            diag_sand = diagonal_sandwich(i, j)

            # sandwich constraints include whether the position is empty
            spot_constraint = row_sand | col_sand | diag_sand
            constraints |= spot_constraint

            # keep track of valid next moves
            E.add_constraint(iff(Piece(f's', f'{i}', f'{j}'), spot_constraint))
    E.add_constraint(constraints)
    return E


def test_theory(board):
    # start proposition as true to add conjuncts to
    # there will always be either not a white piece or not a black piece on a position

    # set propositions of piece position for every position on the grid
    for j in range(BOARD_HEIGHT):
        for i in range(BOARD_WIDTH):
            # set boolean logic of current position on board
            if board[j][i] == 'w':
                # for spaces where we have a white piece, add that to the board proposition
                E.add_constraint(Piece(f'w', f'{i}', f'{j}') & ~Piece(f'b', f'{i}', f'{j}'))
            elif board[j][i] == 'b':
                E.add_constraint(~Piece(f'w', f'{i}', f'{j}') & Piece(f'b', f'{i}', f'{j}'))
            else:
                E.add_constraint(~Piece(f'w', f'{i}', f'{j}') & ~Piece(f'b', f'{i}', f'{j}'))


def draw_solution(sol):
    if sol is None:
        print("No available moves.")
    else:
        for j in range(BOARD_HEIGHT):
            row = "\n"
            for i in range(BOARD_WIDTH):
                if sol[f'w{i}{j}']:
                    row += "w" + " "
                elif sol[f'b{i}{j}']:
                    row += "b" + " "
                elif sol[f's{i}{j}']:
                    row += "x" + " "
                else:
                    row += "." + " "
            print(row)


def draw_board(board):
    for j in range(BOARD_HEIGHT):
        row = "\n"
        for i in range(BOARD_WIDTH):
            if board[j][i] == 'w':
                row += "w" + " "
            elif board[j][i] == 'b':
                row += "b" + " "
            else:
                row += "." + " "
        print(row)


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

    return board


def test2():
    board = [
        ['.', '.', '.', '.', '.', '.', '.', '.'],
        ['.', '.', '.', '.', '.', '.', '.', '.'],
        ['.', '.', '.', '.', '.', '.', '.', '.'],
        ['.', '.', '.', 'w', 'b', '.', '.', '.'],
        ['.', '.', 'w', 'w', 'w', '.', '.', '.'],
        ['.', '.', 'b', 'w', '.', '.', '.', '.'],
        ['.', '.', '.', '.', '.', '.', '.', '.'],
        ['.', '.', '.', '.', '.', '.', '.', '.'],
    ]

    return board


def test3():
    board = [
        ['.', '.', '.', 'b', '.', '.', '.', 'b'],
        ['.', '.', '.', '.', 'b', '.', 'b', 'b'],
        ['b', '.', 'w', 'w', 'w', 'b', 'w', 'w'],
        ['b', 'b', 'b', 'w', 'w', 'w', 'b', 'w'],
        ['b', 'b', 'w', 'w', 'w', 'w', 'b', 'w'],
        ['b', 'w', 'w', 'w', 'w', '.', 'b', 'w'],
        ['b', 'b', 'b', '.', '.', '.', '.', 'w'],
        ['b', 'b', 'b', 'b', '.', '.', '.', '.'],
    ]

    return board


if __name__ == "__main__":
    # Don't compile until you're finished adding all your constraints!
    # MAKE PROPS 1 RETURN THE PROPOSITIONS FOR THE FIRST TEST CASE
    # board = test1()
    # board = test2()
    board = test3()

    test_theory(board)
    T = build_theory()
    T = T.compile()
    sol = T.solve()

    print("\nGiven game board: ")
    draw_board(board)
    print()
    print("\nPotential next moves: ")
    draw_solution(sol)

    # print(T)
    # T.introspect()

    # After compilation (and only after), you can check some properties
    # of your model:

    #print("\nSatisfiable: %s" % T.satisfiable())
    #print("GOT THIS FAR")
    #print("# Solutions: %d" % count_solutions(T))
    #print("   Solution: %s" % T.solve())

    # print("\nVariable likelihoods:")
    # for v, vn in zip([w, b, e, r, d, c, p], 'wberdcp'):
    #     # Ensure that you only send these functions NNF formulas
    #     # Literals are compiled to NNF here
    #     print(" %s: %.2f" % (vn, likelihood(T, v)))
    # print()
