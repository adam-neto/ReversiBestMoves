"""
TEST FILE FOR DRIVING GAME STATE

Author: Adam Neto
Updated: 11/2/23
"""
import GameInfo

myGame = GameInfo.GameState()
myGame.draw_board()

playing = True
while playing:
    print()
    x = int(input(myGame.player + " player, next x: "))
    y = int(input(myGame.player + " player, next y: "))
    print()
    if not myGame.place_piece(x, y):
        print("Invalid move")
        myGame.scan_board()
    myGame.draw_board()
