import importlib
import classes #import the module here, so that it can be reloaded.
importlib.reload(classes)

def print_hand(card):
    print("".join(["Season:",card.season," Power: ",str(card.power)]))

if game: del game
if players: del players   
    
game = classes.Game()
for s in game.influence:
    assert game.influence[s] == 0 
players = [classes.Player("P1"),classes.Player("P2")]

game.start_game(players)

for p in players:
    for s in p.will:
        assert p.will[s] == 0 
    assert len(p.hand) == 8 


for p in players:
    print("hand")
    for c in p.hand:
        print_hand(c)
    print("deck")
    for c in players[0].deck:
        print_hand(c)    
