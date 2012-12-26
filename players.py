import re
import string
import random
from crossword import Grid, grid_size

# A player should have:
#   a name attribute
#   a placeLetter(grid, letter) method
#   a chooseLetter(grid) method

class RandomPlayer(object):
    def __init__(self, name):
        self.name = name

    def placeLetter(self, grid, letter):
        while True:
            x = random.choice(range(0, grid_size)) 
            y = random.choice(range(0, grid_size))
            if grid.getLetter(x,y) == 0:
                return (x,y,letter)
        raise Exception("No free slots");

    # default implementation randomly places letters
    def chooseLetter(self, grid):
        return random.choice(string.letters).lower()

class ConstantPlayer(RandomPlayer):
    def __init__(self, name, letter):
        self.letter = letter
        self.name = name

    def chooseLetter(self, grid):
        return self.letter

class HumanPlayer(object):
    def getInput(func):
        while True:
            try:
                return func()
            except InputError as e:
                print "Error in input:", e

    def chooseLetter(self, grid):
        def promptForLetter():
            print "Current crossword:"
            grid.printGrid()
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
            return (x,y,letter.lower())
       
        print "Current crossword:"
        grid.printGrid()
        return getInput(promptForCoords)

