"""
TEST FILE FOR DRIVING GAME STATE

Author: Adam Neto
Updated: 12/7/23
"""
import GameInfo

myGame = GameInfo.GameState()
myGame.draw_board()

playing = True
while playing:
    try:
        x = int(input(myGame.player + " player, next x: "))
        y = int(input(myGame.player + " player, next y: "))
        print()
        if not myGame.place_piece(x, y):
            print("Invalid move.")
        print()
    except ValueError:
        print("Enter integers only.")
    myGame.draw_board()
