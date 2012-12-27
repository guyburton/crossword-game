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

class BasicPlayer(RandomPlayer):
    def placeLetter(self, grid, letter):
        # construct a regex from the current grid to find dictionary words which could fit
        # select a coord which minimises the number of decreases in word matches in all 10
        # dimensions (max 10 * 25 * 4 possibilities to check)
        
        gGrid = Grid()
        gGrid.grid = grid.grid

        all_words = '\n'.join(dictionary)

        def scorePosition():
            scoring_words = []
            for i in range(0,grid_size*2):
                letters = gGrid.getLetters(i)
                possible_words = gGrid.getPossibleWords(letters)
                possible_words = [w.replace(null_char, '\\w') for w in possible_words if null_char in w]
                # print "Regexes:",possible_words
                
                # we now have the complete list of words we could make with our remaining placings
                # pick the longest to score the position
                # this approach is flawed in the sense that not all the possibilities can simultaneously be made
        
                possibilities = []
                for possible_word in possible_words:
                    rx = re.compile(possible_word)
                    matches = rx.findall(all_words)
                    #print "Words:", matches
                    if matches:
                        longest_match = max(matches, key=len)
                        if type(longest_match) is list:
                            longest_match = random.choice(longest_match)
                        #print "scored word"
                        #print longest_match
                        possibilities.append(longest_match)
                if possibilities:
                    longest_word = max(possibilities, key=len)
                    if type(longest_word) is list:
                        longest_word = random.choice(longest_word)
                    scoring_words.append(longest_word)

            #print "Scoring Words"
            #print scoring_words
            score = sum([len(x) for x in scoring_words])
            #print score
            return score

        # try placing letter at each available grid position
        # score the position and store
        scores = []
        for i in range(0,5):
            for j in range(0,5):
                if gGrid.getLetter(i,j) == null_char:
                    gGrid.grid[j * grid_size + i] = letter
                    scores.append((i,j, scorePosition()))
                    gGrid.grid[j * grid_size + i] = null_char
            
        # submit the highest scoring position
        print "Possible scores"
        print scores
        best_score = max(scores, lambda s: s[2])
        if type(best_score) is list:
            best_score = random.choice(best_score)
        print "Best potential grid score:", best_score
        return (best_score[0], best_score[1])

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
    grid.printGrid()

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
            return (x,y)
       
        print "Current crossword:"
        grid.printGrid()
        return getInput(promptForCoords)

