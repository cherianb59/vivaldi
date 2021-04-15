from pycallgraph import PyCallGraph
from pycallgraph.output import GraphvizOutput
from pycallgraph import Config
from pycallgraph import GlobbingFilter

config = Config()
config.trace_filter = GlobbingFilter(include=['*'],exclude=['logging*','threading*','multiprocessing*','posixpath*','genericpath*'])
#config.trace_filter = GlobbingFilter()


graphviz = GraphvizOutput()
graphviz.output_file = 'pycallgraph_random.png'

import importlib
import logging
import classes #import the module here, so that it can be reloaded.
importlib.reload(classes)

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)    

    
with PyCallGraph(output=graphviz, config=config):
    game = classes.Game(1)
    game.players = [classes.Player(game, 0,"pycallgraph_random"),classes.Player(game, 1,"pycallgraph_random")]
    game.start_game()
    game_result,turn_results = game.run_game()
    