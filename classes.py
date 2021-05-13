
import logging
log = logging.getLogger(__name__)

import importlib
import ai
importlib.reload(ai)
import random 
from keras.models import load_model         
from constants import *

def str_to_Card(in_str):
    '''convert str representation of a card back to a Card object'''
    return(Card(in_str[0], int(in_str[1])))

class Card():
    def __init__(self, season, power=None):
        #multipe ways to define card, Card("h1") , Card("h",1) Card(["h",1])
        if power==None and len(season)==2:
            self.season = season[0]
            self.power = int(season[1])
        else:    
            self.season = season
            self.power = power  
        #todo add list version
    def print_card(self):
        return("".join(["Season:",self.season," Power: ",str(self.power)]))
              
    def __repr__(self):
    #what python prints    if print(Class) is called
        return("".join([self.season,str(self.power)]))
        
    #comparison functions
    def __le__(self, other):
        return(self.score == other.season and self.power <= other.power )
        
    def __lt__(self, other):
        return(self.season == other.season and self.power < other.power )
        
    def __ge__(self, other):
        return(self.season == other.season and self.power >= other.power )
        
    def __gt__(self, other): 
        return(self.season == other.season and self.power > other.power )
        
    def __eq__(self, other): 
        return(self.power == other.power and self.season == other.season)
        
    def __ne__(self, other): 
        return(self.power != other.power or self.season != other.season)
        
class Player():
    def __init__(self,  id, game, AI_type):
        self.id = id
        self.name = "P"+str(id)
        self.game = game 
        self.hand_counter = [0 for x in cards]
        self.ai = ai.PlayerAI(self,AI_type)
        self.reset()
        self.ask_history = []
        self.ask_history_win = []
        self.choose_history = []
        self.choose_history_win = []

    def reset(self):
        self.will = {"h":0,"j":0,"k":0,"l":0}
        self.score = 0 
        self.seasons_won = 0 
        self.win = 0         
        self.hand = []

    def __lt__(self, other): 
        return(self.score < other.score)

    def __le__(self, other): 
        return(self.score <= other.score)

    def __gt__(self, other): 
        return(self.score > other.score)

    def __ge__(self, other): 
        return(self.score >= other.score)
        
    def __eq__(self, other): 
        if self is None and other is None: return(True)
        else: return(self.score == other.score )

    def initialize_ai(self):
        self.ai.initialize_ai()

    def train_ai(self):
        self.ai.train()
            
    def load_ai(self):
        self.ai.choose_ai = load_model(self.name + '_choose_ai_%d.h5' % self.id)
        self.ai.ask_ai = load_model(self.name + '_ask_ai_%d.h5' % self.id)
        print('loaded ai')

    def save_ai(self):
        self.ai.choose_ai.save(self.name + '_choose_ai_%d.h5' % self.id)
        self.ai.ask_ai.save(self.name + '_ask_ai_%d.h5' % self.id)
        print('saved ai')
    
    def flush_history(self):
        """use for memory purposes and when some data might be irrelevant"""
        self.choose_history = []
        self.choose_history_win = []
        self.ask_history = []
        self.ask_history_win = []

    def update_win_history(self):
        #make the history_win length equal to history length 
        self.choose_history_win += [self.win] * (len(self.choose_history) - len(self.choose_history_win))
        self.ask_history_win += [self.win] * (len(self.ask_history) - len(self.ask_history_win))
        
    def complete_serialize(self):
        '''
        encode the game state for this player, we dont know the oppositions hand
        '''
        state = []
        state = state + [self.game.turn_number]
        if self.game.turn_number != 0 :
            opposition = self.game.players[1 - self.id]
            
            #players will
            state = state + [self.will[x] for x in season_short]
            state = state + [self.score]
            #opponents will
            state = state + [opposition.will[x] for x in season_short]
            state = state + [opposition.score]
            #influence
            state = state + [self.game.influence[x] for x in season_short]
            #my hand
            state = state + self.hand_counter            
        else : 
            state = state + [0] * len(season_short)
            state = state + [0]
            state = state + [0] * len(season_short)
            state = state + [0]
            state = state + [0] * len(season_short)
            state = state + self.hand_counter
        return(state)
        
    def give_deck(self,deck):
        #move cards into hand
        
        self.hand = deck[0:HAND_SIZE]
        self.hand_count()
        #convert hand to list of how much of each card. used for neural network, needs state of game to have similar representation for similar states.
            
        self.deck = deck[HAND_SIZE:]
        
        log.debug(''.join([self.name ,' hand '] + [str(x)+" " for x in self.hand]))
        log.debug(''.join([self.name ,' deck '] + [str(x)+" " for x in self.deck]))

    #when given two cards, choose where to place
    def choose(self,cards):
        #Make the ai choose the cards
        chosen_cards = self.ai.choose(list(cards))
        log.debug(''.join([self.name ,' choice ', "Will:",str(chosen_cards[0]) , " influence:", str(chosen_cards[1]) ]))
        self.update_will(chosen_cards[0])
        self.game.update_influence(chosen_cards[1])
        return(chosen_cards)
        
    #choose two cards to give to the other player
    def ask(self):
        #move the asked cards to the first two positions of the hand
        ask_cards = self.ai.ask()
        log.debug(''.join([self.name ,' ask ', str(ask_cards[0]) , " ", str(ask_cards[1]) ]))
        #remove cards from hand
        self.hand.remove(ask_cards[0])
        self.hand.remove(ask_cards[1])
        self.hand_count()
        return(ask_cards)
    
    def replenish(self):
    #move cards from deck to hand
        if len(self.deck) > 0:
            self.hand = self.hand + self.deck[0:2]
            self.deck = self.deck[2:]
        self.hand_count()

    def update_will(self,card):
        self.will[card.season] += card.power
    
    def hand_count(self):
    #zero out the hand and then increment card indexes if that cards is in the hand
        self.hand_counter = [0 for x in cards]
        for c in self.hand:
            self.hand_counter[cards_lut[str(c)]] += 1
                                
class Game():
    def __init__(self, id, pre_existing_players = None, seed  = None):
        self.influence = {"h":0,"j":0,"k":0,"l":0}
        self.id = id
        
        self.turn_number = 0
        
        if not pre_existing_players:
            self.players = [Player(0,self,"random"),Player(1,self,"random")]
            self.players[0].initialize_ai()
        else:
            self.players = pre_existing_players
            
        for p in self.players: p.reset()
            
        #use spcified seed, otherwise use id as rng seed
        if seed != None: random.seed(seed)
        else : random.seed(id)
            
        #store stats for game and turn
        self.game_stats = {}
        self.turn_stats = []
         
        #list of three empty lists, one for each power of card
        self.full_deck =  [[] for _ in range(3)] 

        #create a full deck of cards
        #iterate through powers then seasons
        for p in powers_quantity:
            for s in season_short: 
                for i in range(powers_quantity[p]):
                    self.full_deck[p - 1].append(Card(s,p))
        
    #deal teh cards
    def deal(self):
        num_piles = 8
        #shuffle the three decks, place into 8 piles, igve the first three to first player next three to seond player, last two piles arent used
        piles = [[] for _ in range(num_piles)]
        for j in powers_quantity:
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
            self.game_stats[str(self.players[i].name) + "_deck"] = [str(x) for x in piles[i]]
            log.debug(''.join(['Deck ' + self.players[i].name + ': ']+ ["".join([str(x) + " " for x in piles[i]])]))
            self.players[i].give_deck(piles[i]) 
                
    def update_influence(self,card):
        self.influence[card.season] += card.power
        pass
    
    def scoring(self):
        log.debug(self.influence)
        for p in self.players:
            #calculate score from scratch
            opposition = p.game.players[1 - p.id]
            p.score = 0 
            p.points = 0 
            p.seasons_won = 0 
            for s in season_short:
                if p.will[s] > opposition.will[s] :
                    p.points += self.influence[s] + p.will[s]
                    p.seasons_won += 1 
                elif p.will[s] == opposition.will[s] :
                    pass
                else: p.points += p.will[s]
            #combine seasons and points into score, having more seasons is better but will never be woth more than points
            p.score = p.points +  float(p.seasons_won)/10      
            log.debug(p.will)
            log.debug(p.score)
        
    def winner(self):
        for p in self.players:
            opposition = p.game.players[1 - p.id]
            #check that this player has maximum score
            if p.score > opposition.score  :
                p.win = 1
                opposition.win = 0 
                return(p)
        return(None)
    
    def run_turn(self):
        turn_stats={}
        self.turn_number += 1 
        for i,p in enumerate(self.players):
        #players[1-i] only works for two players
            turn_stats["p" + str(i) + " hand"] = [str(x) for x in p.hand]
            opposition  = self.players[1-i]
            ask = p.ask()
            turn_stats["p" + str(i) + " ask"] = [str(x) for x in ask]
            choose = opposition.choose(ask)
            turn_stats["p" + str(1-i) + " choose"] = [str(x) for x in choose]
        #at the end of the turn figure out the scores
        self.scoring()    
        turn_stats['influence'] = self.influence
        #add cards to the hand record player stats
        for i,p in enumerate(self.players):
            p.replenish()
            turn_stats["p" + str(i) + " score"] = p.score
            turn_stats["p" + str(i) + " will"] = p.will
        turn_stats["turn"] = self.turn_number
        self.turn_stats.append(turn_stats)
    
    def run_game(self):
        while self.turn_number < 8:
            self.run_turn()
        #find the winner store the stats
        winner = self.winner()
        for player in self.players:
            player.update_win_history()        
        self.game_stats['influence'] = self.influence
        for i,p in enumerate(self.players):
            self.game_stats["p" + str(i) + " score"] = p.score
            self.game_stats["p" + str(i) + " will"] = p.will
        self.game_stats['draw'] = (winner is None)
        if self.game_stats['draw'] == False: self.game_stats['winner'] = winner.name  
        else: self.game_stats['winner']=""
        return(self.game_stats,self.turn_stats)

