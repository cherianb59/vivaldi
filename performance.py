import importlib
import logging
import cProfile
import classes #import the module here, so that it can be reloaded.
importlib.reload(classes)

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)    

def longterm():
    results = [0,0,0] 

    for i in range(10000):
        game = classes.Game()
        players = [classes.Player("P1"),classes.Player("P2")]
        game.start_game(players)
        result = game.run_game(players)
        if result != None:
            if   result.name == "P1" : results[0] += 1
            elif result.name == "P2" : results[1] += 1
        else: results[2] += 1
        del game
        del players   
    print(results)
cProfile.run('longterm()')
