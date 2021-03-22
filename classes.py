#CONSTANTS
season_names = {"q":"Summer","w":"Autumn","e":"Winter","r":"Spring"} 
season_short = ["q","w","e","r"]
rank_quantity = {1:4, 2:6, 3:2}

import random 
random.seed(10)

class Card():
    def __init__(self, season, power):
        self.season = season
        self.power = power  
        
class Player:
    def __init__(self, name):
        self.name = name
        self.will = {"q":0,"w":0,"e":0,"r":0}
        self.score = 0 
        self.seasons_won = 0 
  
    def give_deck(self,deck):
        HAND_SIZE = 8
        #move cards into hand
        self.hand = deck[0:HAND_SIZE]
        self.deck = deck[HAND_SIZE:]

    #when given two cards, choose where to place
    def choose(self,cards,game):
        #TODO add algorithm to choose where to place
        print(len(cards),type(cards))
        random.shuffle(cards)
        self.update_will(cards[0])
        game.update_influence(cards[1])
        pass
    
    #choose two cards to give to the other player
    def ask(self):
        #TODO add algorithm to choose which cards to give
        random.shuffle(self.hand)
        c0 = self.hand[0] 
        c1 = self.hand[1] 
        del self.hand[0]
        del self.hand[1]
        return([c0,c1])
    
    def replenish(self):
        if len(self.deck) > 0:
            print(len(self.hand),type(self.hand))
            self.hand = self.hand + self.deck[0:2]
            self.deck = self.deck[2:]
        pass

    def update_will(self,card):
        self.will[card.season] += card.power
        pass
    
class Game:
    def __init__(self):
        self.influence = {"q":0,"w":0,"e":0,"r":0}
        
        self.turn_number = 0 
        #list of three empty lists
        self.full_deck =  [[] for _ in range(3)] 

        #create a full deck of cards
        #iterate through powers
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
                #print(card.season,card.power)
        p1_deck = sum(piles[0:3],[])
        p2_deck = sum(piles[4:7],[])

        return(p1_deck,p2_deck)

    def update_influence(self,card):
        self.influence[card.season] += card.power
        pass
    
    def scoring(self,players):
        for p in players:
            #calculate socre from scratch
            p.score = 0 
            p.seasons_won = 0 
            for s in season_short:
                #check that this player has maximum will
                if p.will[s] > max(x.will[s] for x in players if x.name != p.name ) :
                    p.score += self.influence[s] + p.will[s]
                    p.seasons_won += 1 
                else: p.score += p.will[s]
        
    def winner(self,players):
        for p in players:
            #check that this player has maximum score
            if p.score[s] > max(x.score[s] for x in players if x.name != p.name ) :
                return(p)
            #if they have tied for max points check seasons won
            if p.score[s] == max(x.score[s] for x in players if x.name != p.name ) :
                if p.seasons_won[s] > max(x.seasons_won[s] for x in players if x.name != p.name ) :
                    return(p)
        return(None)
    
    def start_game(self,players):
        pile_0, pile_1 = self.deal() 
        players[0].give_deck(pile_0) 
        players[1].give_deck(pile_1) 
        
    def run_turn(self,players):
        for i,p in enumerate(players):
        #only works for two players
            other_p = players[1-i]
            other_p.choose(p.ask(),self)
            p.replenish()
        self.scoring(players)    
        self.turn_number += 1 