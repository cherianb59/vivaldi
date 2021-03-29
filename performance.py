import importlib
import logging
import cProfile
import classes #import the module here, so that it can be reloaded.
importlib.reload(classes)

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)    
#logging.basicConfig(level=logging.DEBUG)    

def longterm():
    results = [0,0,0] 

    for i in range(100000):
        game = classes.Game(id = i, seed= i )
        game.start_game()
        game_result,turn_results = game.run_game()
        result = game_result["winner"]       
        if result != "":
            if   result == "P0" : results[0] += 1
            elif result == "P1" : results[1] += 1
        else: results[2] += 1
        del game
    print(results)
cProfile.run('longterm()')
