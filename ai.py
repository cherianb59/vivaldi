import logging
log = logging.getLogger(__name__)
import random 

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
			#self.player.id refers to the player who is choosing
            for i in range(2):
                #copy the attributes that will change
                old_will = self.game.players[self.player.id].will
                old_influence = self.game.influence               
                #put one card in the influence the other card in the will 
                self.game.players[self.player.id].update_will(cards[i])
                self.game.update_influence(cards[1-i])
                #score this choice
                self.game.scoring()
                #the relative score is important not the absolute score
                points_difference[i] = self.game.players[self.player.id].score - self.game.players[1 - self.player.id].score
                #undo changes
                self.game.players[self.player.id].will = old_will
                self.game.influence = old_influence
                self.game.scoring()
        
            if points_difference[0] > points_difference[1] :return(cards)
            else: return(cards[::-1])