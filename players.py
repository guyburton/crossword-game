from itertools import chain
import re
import string
import random
import logging

from crossword import Grid, grid_size, null_char, dictionary, getPossibleWords

logger = logging.getLogger('players')
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())

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

# very basic cpu strategy
class BasicPlayer(object):
    def __init__(self, name):
        self.name = name
        self.remaining_words = '\n'.join(dictionary) 

    # scores the line based on possible remaining words in dictionary
    def scoreLine(self, line):
        scores = []
        for word in getPossibleWords(line):
            rx = re.compile(word.replace(null_char, '\\w'))
            matches = rx.findall(self.remaining_words)
            if matches:
                scores.append(len(max(matches, key=len)))
        if len(scores) == 0:
            return 0
        return max(scores)

    def placeLetter(self, grid, letter):
        possible_moves = [] 
        gridLogic = Grid()
        gridLogic.grid = grid.grid
        logger.debug("Placing %s in grid:" % letter)
        logger.debug(gridLogic)
        cols = range(0, grid_size)

        while len(cols) != 0:
            col = random.choice(cols)
            cols.remove(col)
            rows = range(0, grid_size)
            while len(rows) != 0:
                row = random.choice(rows)
                rows.remove(row)
                if grid.getLetter(row, col) != null_char:
                    logger.debug("%d, %d is already filled" % (row, col))
                    continue

                logger.debug("Checking %d, %d" % (row, col))
                horizontal_word = list(gridLogic.getLetters(row + grid_size))
                vertical_word = list(gridLogic.getLetters(col))
                logger.debug("Lines %s %s " % (horizontal_word, vertical_word))
                original_score = (self.scoreLine(horizontal_word), self.scoreLine(vertical_word))
                logger.debug("Original Score (%s, %s): %s" % (''.join(horizontal_word), ''.join(vertical_word), str(original_score)))
                horizontal_word[col] = letter
                vertical_word[row] = letter
                new_score = (self.scoreLine(horizontal_word), self.scoreLine(vertical_word))
                logger.debug("New Score (%s, %s, %s):" % (''.join(horizontal_word), ''.join(vertical_word), str(new_score)))

                if original_score == new_score:
                    return (row, col)

                possible_moves.append((row, col, (original_score[0] - new_score[0], original_score[1] - new_score[1])))
       
        best_move = max(possible_moves, key=lambda s: s[2][0] + s[2][1])
        return (best_move[0], best_move[1])

    def chooseLetter(self, grid):
        possible_moves = [] 
        gridLogic = Grid()
        gridLogic.grid = grid.grid
        logger.debug("Deciding which letter to choose")
        logger.debug(gridLogic)
        for col in range(0, grid_size):
            for row in range(0, grid_size):
                new_letter = grid.getLetter(row, col)
                if new_letter != null_char:
                    continue

                logger.debug("Checking %d %d" % (row, col))
                horizontal_word = list(gridLogic.getLetters(row + grid_size))
                vertical_word = list(gridLogic.getLetters(col))

                logger.debug("Lines %s %s" % (horizontal_word, vertical_word))
                original_score = (self.scoreLine(horizontal_word), self.scoreLine(vertical_word))
                logger.debug("Original Score (%s, %s): %s" % (''.join(horizontal_word), ''.join(vertical_word), str(original_score)))
                
                for letter in range(ord('a'), ord('z')+1):
                    horizontal_word[col] = chr(letter)
                    vertical_word[row] = chr(letter)
                    new_score = (self.scoreLine(horizontal_word), self.scoreLine(vertical_word))
                    logger.debug("New Score (%s, %s): %s" % (''.join(horizontal_word), ''.join(vertical_word), str(new_score)))

                    if original_score == new_score:
                        return chr(letter)

                    possible_moves.append((chr(letter), (original_score[0] - new_score[0], original_score[1] - new_score[1])))
        
        best_move = max(possible_moves, key=lambda s: s[1][0] + s[1][1])
        print best_move
        return best_move[0]

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

