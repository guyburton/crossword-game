from players import *
from crossword import *


#def testGame():
#   player1 = RandomPlayer("Guy")
#    player2 = RandomPlayer("Kim")
#    player3 = ConstantPlayer("James", "Z")
#    players = [player1, player2, player3]
#    return playGame(players)

def testGame():
    player1 = BasicPlayer("Guy")
    player2 = ConstantPlayer("Kim", "e")
    players = [player1, player2]
    return playGame(players)

def main():
    players = [BasicPlayer(str(i)) for i in range(1,5)]
    #    players.append(BasicPlayer("basic"))
    games = []
    for i in range(0, 1):
        games.append(playGame(players))

    total_score = sum([sum([p.score for p in players]) for players in games])
    average_score = total_score / 3.0 / len(games)
    high_score = max(players, key=lambda player: player.score)
    print "Average Score:", average_score
    print "High Score:", high_score.score, "(%s)" % type(high_score.personality)

def tp1():
    grid = Grid()
    for i in range(0,5):
        word = dictionary[i]
        print word
        for j in range(0,5):
            grid.setLetter(i, j, word[j])

    scoring_words = grid.getScoringWords()

if __name__ == "__main__":
    main()

