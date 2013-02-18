import sys
sys.path.insert(0, '../src')
import crossword
import main_game
from players.ai_players import *
from players.simple_players import *
import config
import logging

logger = logging.getLogger('players')
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler(sys.stdout))
logger = logging.getLogger('decision')
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler(sys.stdout))

def main():
    crossword.loadDictionary()
    
    num_players = 1
    games = []
    for i in range(0, 1):
        players = [BasicPlayer("Player " + str(i + 1)) for i in range(0,num_players)]
        players.append(ReasonableLettersRandomPlayer("Random Player"))
        players.append(ReasonableLettersRandomPlayer("Random Player"))
        players.append(ReasonableLettersRandomPlayer("Random Player"))
        games.append(main_game.playGame(players))

    total_score = 0
    high_score = 0
    for scoreboard in games:
        for p in scoreboard:
            total_score += p.score
            if p.score > high_score:
                high_score = p.score
    average_score = total_score / len(players) / len(games)
    print "Average Score:", average_score
    print "High Score:", high_score

if __name__ == "__main__":
    main()

