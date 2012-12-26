from players import *
from crossword import *

def testGame():
    player1 = RandomPlayer("Guy")
    player2 = RandomPlayer("Kim")
    player3 = ConstantPlayer("James", "Z")
    players = [player1, player2, player3]
    return playGame(players)

def testDistribution():
    players = [RandomPlayer(str(i)) for i in range(1,5)]
    games = []
    for i in range(0, 100):
        games.append(playGame(players))

    total_score = sum([sum([p.score for p in players]) for players in games])
    average_score = total_score / 3.0 / len(games)
    print "Average Score:", average_score

def tp1():
    grid = Grid()
    for i in range(0,5):
        word = dictionary[i]
        print word
        for j in range(0,5):
            grid.setLetter(i, j, word[j])

    scoring_words = grid.getScoringWords()

