import sys
sys.path.insert(0, '../src')
import crossword
import main_game
from players.simple_players import *
import config

def testGameCompletion():
    crossword.loadDictionary()
    player1 = ConstantPlayer("Guy", "a")
    player2 = RandomPlayer("Kim")
    player3 = ReasonableLettersRandomPlayer("Scott")
    players = [player1, player2]
    leaderboard = main_game.playGame(players)
        
    # check all letters were filled
    for i in range(0, config.grid_size):
        for j in range(0, config.grid_size):
            assert leaderboard[0].grid.getLetter(i,j) != config.null_char
    
def testReasonableLettersRandomPlayer():
    crossword.loadDictionary()
    player3 = ReasonableLettersRandomPlayer("Scott")
    letters = dict([(chr(c),0) for c in range(ord('a'), ord('z')+1)])
    for i in range(0, 1000):
        letters[player3.chooseLetter(Grid())] += 1
        
    distribution = letters.items()
    distribution.sort()
    print distribution
    ## TODO assert something sensible