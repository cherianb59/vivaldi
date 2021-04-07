import classes #import the module here, so that it can be reloaded.
import pandas as pd
from collections import Counter

game_cols = ['p1_deck','p1 score','p2_deck','p2 score','p1 will','p2 will','influence','winner','draw']
game_data = {}
for c in game_cols: game_data[c] = []

def capture_data():
    for i in range(10000):
        game = classes.Game()
        players = [classes.Player("P1"),classes.Player("P2")]
        game.start_game(players)
        game_result,turn_results = game.run_game(players)
        for c in game_cols: game_data[c].append(game_result[c]) 
        del game
        del players   
capture_data()

data = pd.DataFrame(game_data)

for i in range(2):
    player = "p"+str(i+1)
    #these columns are dictionary that contain the number of cards in the deck, the numnbr of seasons, the cumulative power of each season
    data[player+"_deck_cards"] = data[player+"_deck"].apply(lambda x: Counter(x))
    data[player+"_deck_season"] = data[player+"_deck"].apply(lambda c: Counter(x[0] for x in c))
    data[player+"_deck_power"] = data[player+"_deck"].apply(lambda c:  Counter("".join(x[0]*int(x[1]) for x in c )))
    for s in season_short:
        data[player+"_deck_season_"+s] = data[player+"_deck_season"].apply(lambda x: x.get(s,0))
        data[player+"_deck_power_"+s] = data[player+"_deck_power"].apply(lambda x: x.get(s,0))
        for p in range(3):
            data[player+"_deck_"+s+str(p+1)] = data[player+"_deck_cards"].apply(lambda x: x.get(s+str(p+1),0))
    data = data.drop([player+"_deck_season"], axis=1)
    data = data.drop([player+"_deck_power"], axis=1)
    data = data.drop([player+"_deck_cards"], axis=1)
for s in season_short:
    data["diff_deck_season_"+s] = data["p1_deck_season_"+s] - data["p2_deck_season_"+s]
    data["diff_deck_power_"+s] = data["p1_deck_power_"+s] - data["p2_deck_power_"+s]
    for p in range(3):
        data["diff_deck_"+s+str(p+1)] = data["p1_deck_"+s+str(p+1)] - data["p2_deck_"+s+str(p+1)]

def var_4(a,b,c,d):
    in_list = [a,b,c,d]
    mean = sum(in_list)/4
    return(sum( (x-mean)**2 for x in in_list )/4)
    
data["diff_deck_season_var"] = var_4(data["p1_deck_season_q"],data["p1_deck_season_w"],data["p1_deck_season_e"],data["p1_deck_season_r"] )
data["diff_deck_power_var"] = var_4(data["p1_deck_power_q"],data["p1_deck_power_w"],data["p1_deck_power_e"],data["p1_deck_power_r"] )

from sklearn.tree import DecisionTreeClassifier # Import Decision Tree Classifier
from sklearn.model_selection import train_test_split # Import train_test_split function
from sklearn import metrics #Import scikit-learn metrics module for accuracy calculation

X = data[data['draw']==False].drop(['draw','influence'] + [col for col in data.columns if col.startswith('p1')] + [col for col in data.columns if col.startswith('p2')], axis=1)
y = X["winner"] == "P1"
X = X.drop(['winner'], axis=1)

from sklearn.model_selection import RepeatedKFold
from matplotlib import pyplot
import numpy as np
# import the regressor 
from sklearn.tree import DecisionTreeRegressor 
from sklearn.tree import DecisionTreeClassifier
from sklearn import metrics 

for j in range(5,56,10)    :
    for i in range(100,701,200)    :        
        #decision tree
        kfold = RepeatedKFold(n_splits=10, n_repeats=3,  random_state=7)
        test_accuracy = []
        train_accuracy = []
        test_mcc = []
        train_mcc = []
        for train, test in kfold.split(X, y):

            # Create Decision Tree classifer object
            classifier = DecisionTreeClassifier(random_state = 0,max_depth = j,min_samples_split=i) 

            # Train Decision Tree Classifer
            classifier = classifier.fit(X.iloc[train],y.iloc[train])

            #Predict the response for test dataset
            y_test_pred = classifier.predict(X.iloc[test])
            y_train_pred = classifier.predict(X.iloc[train])
            # Model Accuracy, how often is the classifier correct?
            test_accuracy.append(metrics.accuracy_score(y.iloc[test], y_test_pred))
            train_accuracy.append(metrics.accuracy_score(y.iloc[train],y_train_pred ))
            test_mcc.append(metrics.matthews_corrcoef(y.iloc[test], y_test_pred))
            train_mcc.append(metrics.matthews_corrcoef(y.iloc[train],y_train_pred ))
            
            importances = classifier.feature_importances_
            indices = np.argsort(importances)[::-1]
        
        print("Depth %d, min split %d, test_acc %f, train_acc %f , test_mcc %f train_mcc %f" % (j , i , np.mean(test_accuracy), np.mean(train_accuracy) , np.mean(test_mcc), np.mean(train_mcc)))
    #for f in range(X.shape[1]):
    #    print("%d. feature %s (%f)" % (f + 1, X.columns[indices[f]], importances[indices[f]]))

from sklearn.ensemble import RandomForestClassifier
test_accuracy = []
train_accuracy = []
test_mcc = []
train_mcc = []
for train, test in RepeatedKFold(n_splits=10, n_repeats=3,  random_state=7).split(X, y):

    # Build a forest and compute the impurity-based feature importances
    forest = RandomForestClassifier(n_estimators=1000,max_depth=5,random_state=100)

    forest.fit(X.iloc[train], y.iloc[train])
    
    #Predict the response for test dataset
    y_test_pred = forest.predict(X.iloc[test])
    y_train_pred = forest.predict(X.iloc[train])
    # Model Accuracy, how often is the classifier correct?
    test_accuracy.append(metrics.accuracy_score(y.iloc[test], y_test_pred))
    train_accuracy.append(metrics.accuracy_score(y.iloc[train],y_train_pred ))
    test_mcc.append(metrics.matthews_corrcoef(y.iloc[test], y_test_pred))
    train_mcc.append(metrics.matthews_corrcoef(y.iloc[train],y_train_pred ))
    
    importances = classifier.feature_importances_
    indices = np.argsort(importances)[::-1]
print("Depth %d, min split %d, test_acc %f, train_acc %f , test_mcc %f train_mcc %f" % (j , i , np.mean(test_accuracy), np.mean(train_accuracy) , np.mean(test_mcc), np.mean(train_mcc)))
for f in range(X.shape[1]):
    print("%d. feature %s (%f)" % (f + 1, X.columns[indices[f]], importances[indices[f]]))
            