import logging
log = logging.getLogger(__name__)
import random 
from itertools import combinations
import copy
import numpy as np
from numpy.random import choice as rchoice

from constants import *

import keras
from keras.models import Sequential
from keras.constraints import maxnorm
from keras.optimizers import SGD
from keras.layers import Dense, Dropout, Activation, Flatten

from classes import Card 

def choose_from_probs(probs, constraint_mask = None):
    #will almost always make optimal decision; 
    if constraint_mask is not None:
        probs = probs * constraint_mask
    #mask max options 
    #selects the greedy action with probability ? and a random action with probability ? to ensure good coverage of the state-action space.
    #0.001 is a hardcoded hyper parameter and represents exploring options that arent the best option 
    probs = probs * (probs==np.max(probs)) + (probs**2 * 0.01 + 0.001)/len(probs)
    if constraint_mask is not None:
        probs = probs * constraint_mask
    probs = probs/np.sum(probs)
    choice = rchoice(range(len(probs)), size=1, p=probs)
    return choice[0]

class PlayerAI():
    '''
    This class handles decision making
    three options random
                minimax depth 1 minimax depth2
                neural network - this works by creating a network for each type of decision, the input consists of the game state and the decision that was made and the output is the result of the game                           (win/loss/draw). In essence an evaluation function. The network makes decisions by evaluating each possible candidate and using the choice that gives the highest output. 
    '''
    def __init__(self, player, ai_type= "random"):
        self.player = player 
        self.ai_type = ai_type
        self.game = self.player.game
        if ai_type == "nn":
            self.n_epochs = 5
            self.initialize_ai()
            
    def initialize_ai(self):
        self.construct_input()
        self.input_dim = len(self.current_input)
        self.construct_choose_ai()
        self.construct_ask_ai()        

    def construct_input(self):
        #construct input for each player state 
        self.current_input = self.player.complete_serialize()    

    def construct_choose_ai(self):
        """
        each possible two cards is an input
        """
        additional_inputs = 12*12
        self.choose_ai = self.generic_ai(additional_inputs)    

    def construct_ask_ai(self):
        """
        each possible two card combination is an input
        """
        additional_inputs = 13*6
        self.ask_ai = self.generic_ai(additional_inputs)    
        
    def generic_ai(self, additional_inputs):
        #hyper parameters
        ai = Sequential()
        ai.add(Dense(512, input_shape = (int(self.input_dim + additional_inputs),) ) )
        ai.add(Dropout(0.1))
        ai.add(Activation('relu'))
        ai.add(Dense(256))
        ai.add(Dropout(0.05))
        ai.add(Activation('relu'))
        ai.add(Dense(128))
        ai.add(Dropout(0.05))
        ai.add(Activation('relu'))
        ai.add(Dense(2))
        ai.add(Activation('softmax'))
        opt = keras.optimizers.SGD(nesterov=True,momentum=0.1)
        ai.compile(loss='categorical_crossentropy',
                  optimizer=opt,
                  metrics=['accuracy'])
        return ai 

    def create_ask_mask(self, hand) :
        mask = np.zeros(len(cards_ask))
        # make all combinations of cards in hand and if they exist in cards_ask_lut then change the mask to 1
        for i1,c1 in enumerate(hand):
            for i2,c2 in enumerate(hand):
                #dont pick same card in hand
                if i1!=i2:
                    #iterating twice will give both orders of pairs
                    if cards_lut[str(c1)]>= cards_lut[str(c2)]:
                        mask[cards_ask_lut[str(c1),str(c2)]] = 1                
        return(mask)

    def create_choose_mask(self,choose_cards) :
        #make whole mask zero except for two permutations of the choose cards
        mask = np.zeros(len(cards_choose))
        mask[cards_choose_lut[(str(choose_cards[0]),str(choose_cards[1]))]] = 1                
        mask[cards_choose_lut[(str(choose_cards[1]),str(choose_cards[0]))]] = 1                
        return(mask)
                    
    def eval_choose(self):
        #try all two card combinations adding this to the game state and passing it to the NN will return the prob of winning.
        #
        extra_input = np.identity(12*12)
        input = self.merge_input(extra_input)
        preds = self.choose_ai.predict(input)
        return preds[:,1]        

    def record_choose(self, choose_choice):
        extra_input = np.zeros( (1,12*12) )
        extra_input[0,choose_choice] = 1
        input = self.merge_input(extra_input)
        self.player.choose_history.append(input)
                
    def eval_ask(self):
        extra_input = np.identity(13*6)
        input = self.merge_input(extra_input)
        preds = self.ask_ai.predict(input)
        return preds[:,1]        

    def record_ask(self, ask_choice):
        extra_input = np.zeros( (1,13*6) )
        extra_input[0,ask_choice] = 1
        input = self.merge_input(extra_input)
        self.player.ask_history.append(input)
    
    def merge_input(self, extra_input):
        self.construct_input()
        extra_input_height = extra_input.shape[0]
        return np.column_stack((np.repeat([self.current_input], extra_input_height, 0), extra_input))
    
    def construct_input(self):
        #construct input for each player state 
        self.current_input = self.player.complete_serialize()
        
    def train(self):
        """trains both AI
        any network without training data will be skipped
        choose | ask 
        """
        if len(self.player.choose_history) != 0:
            choose_x = np.asarray(self.player.choose_history)[:,0,:] 
            choose_y = keras.utils.to_categorical(self.player.choose_history_win, 2)
            self.choose_ai.fit(choose_x, choose_y, epochs = 10, batch_size = 100, verbose=0)    
            
        if len(self.player.ask_history) != 0:
            ask_x = np.asarray(self.player.ask_history)[:,0,:] 
            ask_y = keras.utils.to_categorical(self.player.ask_history_win, 2)
            self.ask_ai.fit(ask_x, ask_y, epochs = 10, batch_size = 100, verbose=0)    
        
    def ask(self):
        opposition = self.game.players[1 - self.player.id]
    
        if self.ai_type in ("human") :
            log.debug(''.join([self.player.name,' human ask']))
            print("Game: ",self.game.influence,"Player: ",self.player.will,"Opposition: ",opposition.will)
            print([ c for c in self.player.hand])
            c1 = int(input("card 1 index"))
            c2 = int(input("card 2 index"))
            return([self.player.hand[c1],self.player.hand[c2]])
                
        if self.ai_type in ("random") :
            log.debug(''.join([self.player.name,' random ask']))
            random.shuffle(self.player.hand)
            return(self.player.hand[0:2])        
        
        if self.ai_type in ("nn") :
            log.debug(''.join([self.player.name,' nn ask']))
            ask_mask = self.create_ask_mask(self.player.hand)
            probs = self.eval_ask()
            ask_choice = choose_from_probs(probs, constraint_mask = ask_mask)
            self.record_ask(ask_choice)
            return([Card(i) for i in cards_ask[ask_choice]])
        
        if self.ai_type in ("minimax","minimax2"):            
            log.debug(''.join([self.player.name,' minimax ask']))
            #try all the choices and find the best one, assume the other player will use minimax to choose the cards
            ask_max_points_difference = -999
            ask_option = None
                        
            #store vars that are going to change and need to be reverted
            opposition_ai = copy.copy(opposition.ai.ai_type)
            old_will = copy.copy(opposition.will)
            old_influence = copy.copy(self.game.influence)
            
            opposition.ai_type = "minimax"
            
            for ask_candidate in combinations(self.player.hand,2) : 
                
                log.debug(''.join([self.player.name,' ask candidate'] + [ str(c) for c in ask_candidate] ))
                #give the opposition the candidate cards, they will choose which card gets played where
                ask_chosen = opposition.choose(ask_candidate)
                log.debug(''.join([opposition.name,' ask chosen'] + [ str(c) for c in ask_chosen] ))
                #score this choice                
                #TODO choose already find the best scoring, dont need to recalculate
                log.debug(''.join([opposition.name,' add to will ',str(ask_chosen[0]), " add to influence ", str(ask_chosen[1])] ))
                opposition.update_will(ask_chosen[0])
                self.game.update_influence(ask_chosen[1])
                log.debug(''.join([opposition.name,' will: ', str(opposition.will), " influence: ", str(self.game.influence)] ))
                self.game.scoring()
                points_difference = self.player.score - opposition.score
                
                log.debug(''.join(["player score:", str(self.player.score) ,"opposition score:",  str(opposition.score), " points diff: ",str(points_difference)] ))
                #revert changes
                opposition.will = copy.copy(old_will)
                self.game.influence = copy.copy(old_influence)
                #compare to best choice
                if points_difference >= ask_max_points_difference:
                    ask_max_points_difference = points_difference
                    ask_option = ask_candidate
            opposition.ai_type = copy.copy(opposition_ai)
            
            return(ask_option)
    #TODO split this funcion    
    def choose(self, cards):
        opposition = self.game.players[1 - self.player.id]
        
        if self.ai_type in ("human") :
            log.debug(''.join([self.player.name,' human choose']))
            print("Game: ",self.game.influence,"Player: ",self.player.will,"Opposition: ",opposition.will)
            print([ (i,c) for i,c in enumerate(cards)])
            swap = input("(S)wap?")
            if swap != "S": return(cards)
            else: return(cards[::-1])

        if self.ai_type == "random":
            log.debug(''.join([self.player.name,' random choose']))
            random.shuffle(cards)
            return(cards)        
        #try both pairs, choose whichever gives highest points 
        
        if self.ai_type in ("nn") :
            log.debug(''.join([self.player.name,' NN choose']))
            probs = self.eval_choose()
            choose_choice = choose_from_probs(probs, constraint_mask = self.create_choose_mask(cards))
            self.record_choose(choose_choice)
            #TODO convert choice back to cards
            return([Card(i) for i in cards_choose[choose_choice]])
        
        if self.ai_type in ("minimax","minimax2"):            
            log.debug(''.join([self.player.name,' minimax choose']))
            points_difference = [0,0]
            #self.player.id refers to the player who is choosing
            for i in range(2):
                #copy the attributes that will change
                #TODO Check old_will, old_influcence doesnt get updated
                old_will = copy.copy(self.player.will)
                old_influence = copy.copy(self.game.influence)
                old_opposition_will = copy.copy(opposition.will)
                
                #put one card in the influence the other card in the will 
                log.debug(''.join([self.player.name,' add to will ',str(cards[i]), " add to influence ", str(cards[1-i])] ))
                self.player.update_will(cards[i])
                self.game.update_influence(cards[1-i])
                log.debug(''.join([self.player.name,' will: ',str(self.player.will), " influence: ", str(self.game.influence)] ))                #score this choice
                
                '''# implement another depth level for minimax for each of my choices of where to place, figure out my opponents choice based on all my ask possibilities
                if self.ai_type = 'minimax2':
                    self.ask()
                    opposition.ai.ai_type = 'minimax'
                    opposition.ai.choose()
                    opposition_will = copy.copy(opposition.will)
                    opposition.update_will(cards[i])
                    self.game.update_influence(cards[1-i])
                '''
                #the relative score is important not the absolute score
                self.game.scoring()
                points_difference[i] = self.player.score - opposition.score
                log.debug(''.join(["player score:", str(self.player.score) ,"opposition score:",  str(opposition.score), " points diff: ",str(points_difference[i]) ] ))
                
                #undo changes
                self.player.will = copy.copy(old_will)
                #opposition.ai.ai_type = copy.copy(old_opposition_ai)
                #opposition.will = copy.copy()
                #opposition.will = copy.copy(old_opposition_will)
                self.game.influence = copy.copy(old_influence)
                self.game.scoring()
                
            if points_difference[0] > points_difference[1] : return(cards)
            else: return(cards[::-1])

    

    
