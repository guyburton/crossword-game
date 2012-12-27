from itertools import chain
import re
import string
import random
from crossword import Grid, grid_size, null_char, dictionary

# A player should have:
#   a name attribute
#   a placeLetter(grid, letter) method
#   a chooseLetter(grid) method

class RandomPlayer(object):
    def __init__(self, name):
        self.name = name

    def placeLetter(self, grid, letter):
        blank_indexes = []
        for i in range(0, grid_size):
            for j in range(0, grid_size):
                if grid.getLetter(i,j) == null_char:
                    blank_indexes.append((i,j))
        return random.choice(blank_indexes)

    # default implementation randomly places letters
    def chooseLetter(self, grid):
        letter = random.choice(string.letters).lower()
        return letter

class ConstantPlayer(RandomPlayer):
    def __init__(self, name, letter):
        self.letter = letter
        self.name = name

    def chooseLetter(self, grid):
        return self.letter

class BasicPlayer(object):
    def __init__(self, name):
        self.name = name
        self.remaining_words = '\n'.join(dictionary) 

    def scorePosition(self, gGrid):
        scoring_words = []
        for i in range(0,grid_size*2):
            letters = gGrid.getLetters(i)
            possible_words = gGrid.getPossibleWords(letters)
            possible_words = [w for w in possible_words if null_char in w]
            # this approach is flawed in the sense that not all the possibilities can simultaneously be made
            possibilities = []
            for possible_word in possible_words:
                rx = re.compile(possible_word.replace(null_char, '\\w'))
                matches = rx.findall(self.remaining_words)
                if matches:
                    longest_match = max(matches, key=len)
                    if type(longest_match) is list:
                        longest_match = random.choice(longest_match)
                    possibilities.append(longest_match)
            if possibilities:
                longest_word = max(possibilities, key=len)
                if type(longest_word) is list:
                    longest_word = random.choice(longest_word)
                scoring_words.append(longest_word)
        
        score = sum([len(x) for x in scoring_words])
        return score

    def chooseLetter(self, grid):
        # do the same as placeLetter, except instead of working on all possible grids with
        # the placing letter filled, we work on the actual grid, choosing the highest
        # possible scoring word
        gGrid = Grid()
        gGrid.grid = grid.grid
        
        for i in range(0,grid_size*2):
            letters = gGrid.getLetters(i)
            possible_words = gGrid.getPossibleWords(letters)
            possible_words = [w for w in possible_words if null_char in w]
            # this approach is flawed in the sense that not all the possibilities can simultaneously be made
            for possible_word in possible_words:
                rx = re.compile(possible_word.replace(null_char, '\\w'))
                matches = rx.findall(self.remaining_words)
                if matches:
                    match = max(matches, key=len)
                    matched_word = random.choice([m for m in matches if len(m) == len(match)])
                    return matched_word[possible_word.index(null_char)]

    def placeLetter(self, grid, letter):
        # construct a regex from the current grid to find dictionary words which could fit
        # select a coord which minimises the number of decreases in word matches in all 10
        # dimensions (max 10 * 25 * 4 possibilities to check)
        gGrid = Grid()
        gGrid.grid = grid.grid

        # try placing letter at each available grid position
        # score the position and store
        scores = []
        for i in range(0,5):
            for j in range(0,5):
                if gGrid.getLetter(i,j) == null_char:
                    gGrid.grid[j * grid_size + i] = letter
                    scores.append((i,j, self.scorePosition(gGrid)))
                    gGrid.grid[j * grid_size + i] = null_char
            
        # submit the highest scoring position
        print "Possible scores:"
        print scores
        best_score = max(scores, key=lambda s: s[2])
        #if type(best_score) is list:
        #    print "Picking random choice from best scores"
        #    best_score = random.choice(best_score)
        choice = random.choice([x for x in scores if x[2] == best_score[2]])
        print "Best potential grid score:", choice

        return (choice[0], choice[1])

def testBasicPlayer():
    player = BasicPlayer("test")
    grid = Grid()
    grid.setLetter(3, 0, 'i')
    grid.setLetter(4, 0, 'i')
    for i in range(0,5):
        for j in range(1,5):
            grid.setLetter(i,j,'a')
    coords = player.placeLetter(grid, 'a')
    print "Player chose coords:", coords
    grid.setLetter(coords[0], coords[1], 'a')
    print grid 

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

