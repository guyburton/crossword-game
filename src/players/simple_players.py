from grid import Grid
from player import PlayerPersonality
import config
import string
import random
import numpy as np

def getInput(func):
    while True:
        try:
            return func()
        except InputError as e:
            print "Error in input:", e

class HumanPlayer(PlayerPersonality):
    def chooseLetter(self, grid):
        def promptForLetter():
            print "Current crossword:"
            print grid 
            print "Enter the letter you would like to add:"
            letter = ''
            while len(letter) != 1 or letter not in string.letters:
                letter = raw_input()
            return letter
        return getInput(promptForLetter)

    def placeLetter(self, letter):
        def promptForCoords():
            rx = re.compile('(\d),(\d)')
            match = None
            while not match:
                print "Enter the grid location you would like to add it x,y:"
                coords = raw_input()
                match = rx.match(coords)
            x = int(match.group(1)) - 1
            y = int(match.group(2)) - 1
            return (x,y)
       
        print "Current crossword:"
        print grid 
        return getInput(promptForCoords)


# A player should have:
#   a name attribute
#   a placeLetter(grid, letter) method
#   a chooseLetter(grid) method

class RandomPlayer(object):
    def __init__(self, name):
        self.name = name

    def placeLetter(self, grid, letter):
        blank_indexes = []
        for i in range(0, config.grid_size):
            for j in range(0, config.grid_size):
                if grid.getLetter(i,j) == config.null_char:
                    blank_indexes.append((i,j))
        return random.choice(blank_indexes)

    # default implementation randomly places letters
    def chooseLetter(self, grid):
        letter = random.choice(string.letters).lower()
        return letter

class ReasonableLettersRandomPlayer(RandomPlayer):
    def __init__(self, name):
        self.name = name
        allwords = ''.join(config.dictionary)
        letter_probabilities = [allwords.count(chr(f)) for f in range(ord('a'), ord('z')+1)]
        assert sum(letter_probabilities) == len(allwords)
        
        self.letter_cumulative_probabilities = np.cumsum(np.array(letter_probabilities))
        self.normaliser = len(allwords)
    
    def chooseLetter(self, grid):
        value = random.random() * self.normaliser
        c = ord('a')
        for probability in self.letter_cumulative_probabilities:
            if value < probability:
                return chr(c)
            c += 1
        assert False
    
class ConstantPlayer(RandomPlayer):
    def __init__(self, name, letter):
        self.letter = letter
        self.name = name

    def chooseLetter(self, grid):
        return self.letter

