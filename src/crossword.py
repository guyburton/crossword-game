from players.simple_players import *
import main_game
import config

def loadDictionary(): 
    with open('converted_words.txt', 'r') as wordsfile:
           config.dictionary = [w.strip() for w in wordsfile]    
    print "Loaded ", len(config.dictionary), " dictionary words"
       
def main():
    loadDictionary()
    
    print "Starting new game with 1 human player"
    player1 = HumanPlayer("Guy")
    player2 = ConstantPlayer("Kim", "e")
    players = [player1, player2]
    main_game.playGame(players)

if __name__ == "__main__":
    main()
    