import logging
log = logging.getLogger(__name__)
import random 

class PlayerAI():
    def __init__(self, player, game, ai_type= "random"):
        self.player = player 
        self.game = game
        self.ai_type = ai_type

    def ask(self, hand):
    #move the asked cards to the start of the hand and return the hand
        if self.ai_type == "random":
            log.debug(''.join([self.player.name,' random ask']))
            random.shuffle(hand)
            return(hand[0:2])        
        if self.ai_type == "minimax":            
            log.debug(''.join([self.player.name,' minimax ask']))
            #try all the choices and find the best one, assume the other player will use minimax to choose the cards
            ask_max_points_difference = -999
            ask_option = None
            
             opposition = self.game.players[1 - self.player.id]
            
            #store things that are going to change and need to be reverted
            opposition_ai = opposition.ai_type
            old_will = opposition.will
            old_influence = self.game.influence               
            
            for ask_candidate in hand : 
                opposition.ai_type = "minimax"
                #give the opposition the candidate cards, they will choose which card gets played where
                ask_chosen = opposition.choose(ask_candidate)
                #score this choice                
                #TODO choose already find the best scoring, dont need to recalculate
                opposition.update_will(ask_chosen[0])
                self.game.update_influence(ask_chosen[1])
                self.game.scoring()
                points_difference = self.player.score - opposition.score
                #revert changes
                opposition.ai_type = opposition_ai 
                opposition.will = old_will
                self.game.influence = old_influence
                #compare to best choice
                if points_difference >= ask_max_points_difference:
                    ask_max_points_difference = points_difference
                    ask_option = ask_candidate
            return(ask_option)
        
    def choose(self, cards):
        opposition = self.game.players[1 - self.player.id]
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
                #TODO Check old_will, old_influcence doesnt get updated
                old_will = self.player.will
                old_influence = self.game.influence               
                #put one card in the influence the other card in the will 
                self.player.update_will(cards[i])
                self.game.update_influence(cards[1-i])
                #score this choice
                self.game.scoring()
                #the relative score is important not the absolute score
                points_difference[i] = self.player.score - opposition.score
                #undo changes
                self.game.players[self.player.id].will = old_will
                self.game.influence = old_influence
                self.game.scoring()
        
            if points_difference[0] > points_difference[1] :return(cards)
            else: return(cards[::-1])