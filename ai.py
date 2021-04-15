import logging
log = logging.getLogger(__name__)
import random 
from itertools import combinations
import copy

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
        self.n_epochs = 5

    def initialize_ai(self):
        self.construct_input()
        self.input_dim = len(self.current_input)

        self.construct_dice_ai()
        self.construct_buy_ai()        

    def construct_input(self):
        #construct input for each player state 
        self.current_input = self.player.complete_serialize()    

    def construct_choose_ai(self):
        """
        there is only one extra input: whether to place as is or to swap 
        """
        additional_inputs = 1
        self.choose_ai = self.generic_ai(additional_inputs)    

    def construct_ask_ai(self):
        """
        each possible two card combination is an input
        """
        additional_inputs = 13*12/2
        self.ask_ai = self.generic_ai(additional_inputs)    
        
    def generic_ai(self, additional_inputs):
        ai = Sequential()
        ai.add(Dense(512, input_shape = (self.input_dim + additional_inputs,) ) )
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

    def decide_choose(self):
        """
        returns whether to place the cards as they are or to switch 
        """
        probs = self.AI.eval_choose()
        choice = choose_from_probs(probs)
        
        if choice == 0  :return(cards)
        else: return(cards[::-1])
            
    def eval_choose(self):
        #0 = as is, 1 = swap
        extra_input = np.identity(1)
        input = self.merge_input(extra_input)
        preds = self.choose_ai.predict(input)
        return preds[:,1]        


    def train(self):
        """trains both AI
        any network without training data will be skipped
        choose | ask 
        """
        if len(player.choose_history) != 0:
            choose_x = np.asarray(player.choose_history)[:,0,:] 
            choose_y = keras.utils.to_categorical(player.choose_history_win, 2)
            self.choose_ai.fit(choose_x, choose_y, epochs = 10, batch_size = 100, verbose=0)    
        if len(player.ask_history) != 0:
            ask_x = np.asarray(player.ask_history)[:,0,:] 
            ask_y = keras.utils.to_categorical(player.ask_history_win, 2)
            self.ask_ai.fit(ask_x, ask_y, epochs = 10, batch_size = 100, verbose=0)    
        
    def ask(self, hand):
    #move the asked cards to the start of the hand and return the hand
        if self.ai_type in ("random") :
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
            opposition_ai = copy.copy(opposition.ai.ai_type)
            old_will = copy.copy(opposition.will)
            old_influence = copy.copy(self.game.influence)
            
            opposition.ai_type = "minimax"
            
            for ask_candidate in combinations(hand,2) : 
                
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
                
                #print(ask_candidate, points_difference, opposition.will, self.game.influence)
                log.debug(''.join(["player score:", str(self.player.score) ,"opposition score:",  str(opposition.score), " points diff: ",str(points_difference)] ))
                #revert changes
                opposition.will = copy.copy(old_will)
                self.game.influence = copy.copy(old_influence)
                #compare to best choice
                if points_difference >= ask_max_points_difference:
                    ask_max_points_difference = points_difference
                    ask_option = ask_candidate
            opposition.ai_type = opposition_ai 
            
            return(ask_option)
        
    def choose(self, cards):
        opposition = self.game.players[1 - self.player.id]
        if self.ai_type == "random":
            log.debug(''.join([self.player.name,' random choose']))
            random.shuffle(cards)
            return(cards)        
        #try both pairs, choose whichever gives highest points 
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

    

    
