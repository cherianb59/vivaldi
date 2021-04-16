#CONSTANTS
HAND_SIZE = 8

season_names = {"h":"Summer","j":"Autumn","k":"Winter","l":"Spring"} 
season_short = ["h","j","k","l"]
powers_quantity = {1:4, 2:6, 3:2}
powers = [1,2,3]

#canonical order of all possible cards
cards = []
for p in powers:
    for s in season_short: 
        cards.append(s+str(p))
cards = tuple(cards)

#canonical order of all possible 2 card combinations and permutations
cards_ask = []
cards_choose = [] 
for i1,x1 in enumerate(cards):
    for i2,x2 in enumerate(cards):
        if i1 >= i2: cards_ask.append(tuple([x1,x2]))
cards_choose.append(tuple([x1,x2]))
cards_ask = tuple(cards_ask)
cards_choose = tuple(cards_choose)
cards_ask_lut = {x:i for i,x in enumerate(cards_ask)}
cards_choose_lut = {x:i for i,x in enumerate(cards_choose)}

import logging
log = logging.getLogger(__name__)

import importlib
import ai
importlib.reload(ai)
import random 
from collections import Counter

class Card():
    def __init__(self, season, power):
        self.season = season
        self.power = power  
        
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
    def __init__(self, game, id, AI_type):
        self.id = id
        self.name = "P"+str(id)
        self.will = {"h":0,"j":0,"k":0,"l":0}
        self.score = 0 
        self.seasons_won = 0 
        self.game = game
        self.ai = ai.PlayerAI(self,AI_type)
        self.hand_counter = [0 for x in cards]

    def __lt__(self, other): 
        return(self.score < other.score   )

    def __le__(self, other): 
        return(self.score <= other.score    )

    def __gt__(self, other): 
        return(self.score > other.score    )

    def __ge__(self, other): 
        return(self.score >= other.score    )
        
    def __eq__(self, other): 
        if self is None and other is None: return(True)
        else: return(self.score == other.score )

    def complete_serialize(self):
        state = []
        opposition = self.game.players[1 - p.id]
        
        state = state + [self.game.turn]
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
        return(state)
        
        
    def give_deck(self,deck):
        #move cards into hand
        
        self.hand = deck[0:HAND_SIZE]
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
        log.debug(''.join([self.name ,' ask ', str(self.hand[0]) , " ", str(self.hand[1]) ]))
        #remove cards from hand
        self.hand.remove(ask_cards[0])
        self.hand.remove(ask_cards[1])
        return(ask_cards)
    
    def replenish(self):
    #move cards from deck to hand
        if len(self.deck) > 0:
            self.hand = self.hand + self.deck[0:2]
            self.deck = self.deck[2:]

    def update_will(self,card):
        self.will[card.season] += card.power
    
    def hand_counter(self):
    #zero out the hand and then increment indexes if that cards is in the hand
        self.hand_counter = [0 for x in cards]
        for c in hand:
            self.hand_counter[cards_lut[str(c)]] += 1
    
class Game():
    def __init__(self, id, seed  = None):
        self.influence = {"h":0,"j":0,"k":0,"l":0}
        self.id = id
        #self.players =  [Player(self, 0, "random") , Player(self, 1, "random")] 
        if seed != None:
            random.seed(seed)
        self.game_stats = {}
        self.turn_stats = []
        self.turn_number = 0 
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
        #shuffle the three decks, place into 8 piles, igve the first three to first player next three to seond player, last two arent used
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
            #calculate socre from scratch
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
            #having more seasons is better but will never be woth more than points
            p.score = p.points +  float(p.seasons_won)/10      
            log.debug(p.will)
            log.debug(p.score)
        
    def winner(self):
        for p in self.players:
            opposition = p.game.players[1 - p.id]
            max_other_score = opposition.score 
            #check that this player has maximum score
            if p.score > max_other_score :
                return(p)
            #if they have tied for max points check seasons won
            if p.score == max_other_score :
                if p.seasons_won > opposition.seasons_won :
                    return(p)
            #if no one wins, its a draw
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
        self.game_stats['influence'] = self.influence
        for i,p in enumerate(self.players):
            p.replenish()
            self.game_stats["p" + str(i) + " score"] = p.score
            self.game_stats["p" + str(i) + " will"] = p.will
        self.game_stats['draw'] = (winner is None)
        if self.game_stats['draw'] == False: self.game_stats['winner'] = winner.name  
        else: self.game_stats['winner']=""
        return(self.game_stats,self.turn_stats)

