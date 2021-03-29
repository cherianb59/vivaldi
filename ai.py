import logging
log = logging.getLogger(__name__)
import random 
from copy import deepcopy 

class PlayerAI():
    def __init__(self, player, game, ai_type= "random"):
        self.player = player 
        self.game = game
        self.ai_type = ai_type
        
    def choose(self, cards):
        if self.ai_type == "random":
            log.debug(''.join([self.player.name,' random choose']))
            random.shuffle(cards)
            return(cards)        
        #try both pairs, choose whichever gives highest points 
        if self.ai_type == "minimax":
            
            log.debug(''.join([self.player.name,' minimax choose']))
            points_difference = [0,0]
            print(''.join([self.player.name , " cards to choose "] + [x.print_card_short()+" " for x in cards]))
            print(" ".join([p.name + " will: " + str(p.will) for p in self.game.players]))
            print(self.game.influence)
            for i in range(2):
                #make a copy of the game, use this copy to test choices
                #TODO deepcopy is slow, copy the game state and reload after checking minimax
                temp_game = deepcopy(self.game)
                #put one card in the influence the other card in the will 
                temp_game.players[self.player.id].update_will(cards[i])
                temp_game.update_influence(cards[1-i])
                print(" ".join(["choice ",str(i)]+[p.name + " will: " + str(p.will) for p in temp_game.players]))
                print(temp_game.influence)
                #score this choice
                temp_game.scoring()
                #the relative score is important not the absolute score
                print(str(i)+" "+str(temp_game.players[self.player.id].score) + " " + str(temp_game.players[1-self.player.id].score))
                points_difference[i] = temp_game.players[self.player.id].score - temp_game.players[1-self.player.id].score
                del temp_game
        
            if points_difference[0] > points_difference[1] :return(cards)
            else: return(cards[::-1])