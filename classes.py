#CONSTANTS
season_names = {"q":"Summer","w":"Autumn","e":"Winter","r":"Spring"} 
season_short = ["q","w","e","r"]
rank_quantity = {1:4, 2:6, 3:2}
import logging
log = logging.getLogger(__name__)

import importlib
import ai
importlib.reload(ai)
import random 

class Card():
    def __init__(self, season, power):
        self.season = season
        self.power = power  
    def print_card(self):
        return("".join(["Season:",self.season," Power: ",str(self.power)]))
    def print_card_short(self):
        return("".join([self.season,str(self.power)]))
    
class Player():
    def __init__(self, game, id, AI_type):
        self.id = id
        self.name = "P"+str(id)
        self.will = {"q":0,"w":0,"e":0,"r":0}
        self.score = 0 
        self.seasons_won = 0 
        self.game = game
        self.ai = ai.PlayerAI(self,self.game,AI_type)
        
    def give_deck(self,deck):
        HAND_SIZE = 8
        #move cards into hand
        
        self.hand = deck[0:HAND_SIZE]
        self.deck = deck[HAND_SIZE:]
        log.debug(''.join([self.name ,' hand '] + [x.print_card_short()+" " for x in self.hand]))
        log.debug(''.join([self.name ,' deck '] + [x.print_card_short()+" " for x in self.deck]))

    #when given two cards, choose where to place
    def choose(self,cards):
        #Make the ai choose the cards
        chosen_cards = self.ai.choose(cards)
        log.debug(''.join([self.name ,' choice ', "Will:",chosen_cards[0].print_card_short() , " influence:", chosen_cards[1].print_card_short() ]))
        self.update_will(chosen_cards[0])
        self.game.update_influence(chosen_cards[1])
        return(chosen_cards)
        
    
    #choose two cards to give to the other player
    def ask(self):
        #TODO add algorithm to choose which cards to give
        random.shuffle(self.hand)
        c0 = self.hand[0] 
        c1 = self.hand[1] 
        log.debug(''.join([self.name ,' ask ', c0.print_card_short() , " ", c1.print_card_short() ]))
        del self.hand[1]
        del self.hand[0]
        return([c0,c1])
    
    def replenish(self):
        if len(self.deck) > 0:
            self.hand = self.hand + self.deck[0:2]
            self.deck = self.deck[2:]
        pass

    def update_will(self,card):
        self.will[card.season] += card.power
        pass
    
class Game():
    def __init__(self, id, seed  = None):
        self.influence = {"q":0,"w":0,"e":0,"r":0}
        self.id = id
        self.players =  [Player(self, 0, "minimax") , Player(self, 1, "random")] 
        if seed != None:
            random.seed(seed)
        self.game_stats = {}
        self.turn_stats = []
        self.turn_number = 0 
        #list of three empty lists, one for each power of card
        self.full_deck =  [[] for _ in range(3)] 

        #create a full deck of cards
        #iterate through powers then seasons
        for j in rank_quantity:
            for c in season_short: 
                for i in range(rank_quantity[j]):
                    self.full_deck[j-1].append(Card(c,j))
        
    #deal teh cards
    def deal(self):
        num_piles = 8
        piles = [[] for _ in range(num_piles)]
        for j in rank_quantity:
            random.shuffle(self.full_deck[j-1])
            for i, card in enumerate(self.full_deck[j-1]):
                pile_num = i%num_piles
                piles[pile_num].append(card)
        p1_deck = sum(piles[0:3],[])
        p2_deck = sum(piles[4:7],[])
        return(p1_deck,p2_deck)

    def start_game(self):
        log.debug('Starting Game: '+str(id) )
        piles = self.deal()
        #create piles, then for each player give them a pile
        for i in range(2):
            self.game_stats[str(self.players[i].name) + "_deck"] = [x.print_card_short() for x in piles[i]]
            log.debug(''.join(['Deck ' + self.players[i].name + ': ']+ ["".join([x.print_card_short()+" " for x in piles[i]])]))
            self.players[i].give_deck(piles[i]) 
                
    def update_influence(self,card):
        self.influence[card.season] += card.power
        pass
    
    def scoring(self):
        log.debug(self.influence)
        for p in self.players:
            #calculate socre from scratch
            p.score = 0 
            p.seasons_won = 0 
            for s in season_short:
                max_other = max(x.will[s] for x in self.players if x.name != p.name )
                #check that this player has maximum will
                if p.will[s] > max_other :
                    p.score += self.influence[s] + p.will[s]
                    p.seasons_won += 1 
                elif p.will[s] == max_other :
                    pass
                else: p.score += p.will[s]
            log.debug(p.will)
            log.debug(p.score)
        
    def winner(self):
        for p in self.players:
            max_other_score = max(x.score for x in self.players if x.name != p.name )
            #check that this player has maximum score
            if p.score > max_other_score :
                return(p)
            #if they have tied for max points check seasons won
            if p.score == max_other_score :
                if p.seasons_won > max(x.seasons_won for x in self.players if x.name != p.name ) :
                    return(p)
            #if no one wins, its a draw
        return(None)
    
    def run_turn(self):
        turn_stats={}
        self.turn_number += 1 
        
        for i,p in enumerate(self.players):
        #players[1-i] only works for two players
            turn_stats["p" + str(i) + " hand"] = [x.print_card_short() for x in p.hand]
            other_p = self.players[1-i]
            ask = p.ask()
            turn_stats["p" + str(i) + " ask"] = [x.print_card_short() for x in ask]
            choose = other_p.choose(ask)
            turn_stats["p" + str(1-i) + " choose"] = [x.print_card_short() for x in choose]
        #at the end of the turn figure out the scores, not necessary but probably useful for learning    
        self.scoring()    
        turn_stats['influence'] = self.influence
        #player stats
        for i,p in enumerate(self.players):
            p.replenish()
            turn_stats["p" + str(i) + " score"] = p.score
            turn_stats["p" + str(i) + " will"] = p.will
        turn_stats["turn"] = self.turn_number
        self.turn_stats.append(turn_stats)
    
    def run_game(self):
        while self.turn_number <= 8:
            self.run_turn()
        #find the winner store the stats
        winner = self.winner()
        self.game_stats['influence'] = self.influence
        for i,p in enumerate(self.players):
            p.replenish()
            self.game_stats["p" + str(i) + " score"] = p.score
            self.game_stats["p" + str(i) + " will"] = p.will
        self.game_stats['draw'] = (winner == None)
        if self.game_stats['draw'] == False: self.game_stats['winner'] = winner.name  
        else: self.game_stats['winner']=""
        return(self.game_stats,self.turn_stats)
