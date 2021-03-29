class PlayerAI(object):
    def __init__(self, player, game, ai_type= "random"):
		self.player = player 
		self.game = game
        self.ai_type = ai_type
        
    def choose(self, cards, game):
        if self.ai_type = "random"
            random.shuffle(cards)
            return(cards[0],cards[1])		
        if self.ai_type = "minimax"
            temp_game = game 
        #try both pairs, whichever gives highest ponts choose that
            if > :
            return([cards[0],cards[1]])
            else: return([cards[1],cards[0]])