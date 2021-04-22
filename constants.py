#CONSTANTS
HAND_SIZE = 8

season_names = {"h":"Summer","j":"Autumn","k":"Winter","l":"Spring"} 
season_short = ["h","j","k","l"]
powers_quantity = {1:4, 2:6, 3:2}
powers = [1,2,3]

#canonical order of all possible cards and look up tables
cards = []
for p in powers:
    for s in season_short: 
        cards.append(s+str(p))
cards = tuple(cards)
cards_lut = {x:i for i,x in enumerate(cards)}

#canonical order of all possible 2 card combinations and permutations
cards_ask = []
cards_choose = [] 
for i1,x1 in enumerate(cards):
    for i2,x2 in enumerate(cards):
        if i1 >= i2: cards_ask.append(tuple([x1,x2]))
        cards_choose.append(tuple([x1,x2]))
        
cards_ask = tuple(cards_ask)
cards_ask_lut = {x:i for i,x in enumerate(cards_ask)}

cards_choose = tuple(cards_choose)
cards_choose_lut = {x:i for i,x in enumerate(cards_choose)}
