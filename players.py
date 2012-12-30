from itertools import chain
import re
import math
import string
import random
import logging
import numpy as np

from crossword import *

logger = logging.getLogger('players')
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())

remaining_words = '\n'.join(dictionary) 

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


param1 = 5000 # multiple of scoring points when comparing to number of words available
param2 = 100  # threshold for score when picking best move at random

class Decision(object):
    # scores the line based on possible remaining words in dictionary
    def scoreLine(self, line):
        scores = []
        for word in getPossibleWords(line):
            rx = re.compile(word.replace(null_char, '\\w'))
            matches = rx.findall(remaining_words)
            if matches:
                scores.append((len(max(matches, key=len)), len(matches)))
        if len(scores) == 0:
            return (0,0)
        return max(scores, key=lambda s: s[0] * param1 + s[1])

    # this is how we score a word 
    # move is ((word1 max score, word1 possibilities), (word2 max score, word2 possibilities))
    def scoreMove(self, move):
        move = move[1]

        original_max_scores = np.array([self.original_score[0][0], self.original_score[1][0]])
        original_possibilities = np.array([self.original_score[0][1], self.original_score[1][1]])
        new_max_scores = np.array([move[0][0], move[1][0]])
        new_possibilities = np.array([move[0][1], move[1][1]])

        score = np.sum(original_max_scores - new_max_scores) * param1 + \
                np.linalg.norm(original_possibilities - new_possibilities)

        return score * -1

    def selectBestMove(self, possibilities): 
        scored_possibilities = [(x, self.scoreMove(x)) for x in possibilities]
        max_score = max(scored_possibilities, key=lambda s: s[1])[1]
        values = [x for x in scored_possibilities if math.fabs(x[1] - max_score) < param2] 
        return random.choice(values)[0]

    def getDecisionReturnValue(self, move):
        return move[0]

    def makeMove(self, grid):
        self.grid = grid
        possible_moves = [] 
        logger.debug(grid)
        for col in range(0, grid_size):
            for row in range(0, grid_size):
                if grid.getLetter(row, col) != null_char:
                    continue

                logger.debug("Checking %d %d" % (row, col))
                self.horizontal_word = list(getLetters(grid, row + grid_size))
                self.vertical_word = list(getLetters(grid, col))
                logger.debug("Lines %s %s " % (self.horizontal_word, self.vertical_word))
                self.original_score = (self.scoreLine(self.horizontal_word), self.scoreLine(self.vertical_word))
                logger.debug("Original Score (%s, %s): %s" % (''.join(self.horizontal_word), ''.join(self.vertical_word), str(self.original_score)))

                possibilities = self.assessGridPosition(row, col)
                possible_moves.extend(possibilities)

        best_move = self.selectBestMove(possible_moves)
        logger.debug("Best Move: %s" % str(best_move))
        return self.getDecisionReturnValue(best_move)

# very basic cpu strategy
class BasicPlayer(object):
    def __init__(self, name):
        self.name = name

    def placeLetter(self, grid, letter):
        class PlaceLetterDecision(Decision):
            def assessGridPosition(self, row, col):
                possible_moves = [] 
                horizontal_word = self.horizontal_word
                vertical_word = self.vertical_word
                horizontal_word[col] = letter
                vertical_word[row] = letter
                new_score = (self.scoreLine(horizontal_word), self.scoreLine(vertical_word))
                #logger.debug("New Score (%s, %s, %s):" % (''.join(horizontal_word), ''.join(vertical_word), str(new_score)))
                possible_moves.append(((row, col), new_score))
                return possible_moves

        decision = PlaceLetterDecision()
        return decision.makeMove(grid)

    def chooseLetter(self, grid):
        class LetterDecision(Decision):
            def assessGridPosition(self, row, col):
                possible_moves = []
           
                horizontal_word = self.horizontal_word
                vertical_word = self.vertical_word

                letters = range(ord('a'), ord('z')+1)
                while len(letters) > 0:
                    letter = chr(random.choice(letters))
                    letters.remove(ord(letter))
                    horizontal_word[col] = letter
                    vertical_word[row] = letter
                    new_score = (self.scoreLine(horizontal_word), self.scoreLine(vertical_word))
                    #logger.debug("New Score (%s, %s): %s" % (''.join(horizontal_word), ''.join(vertical_word), str(new_score)))

                    possible_moves.append((letter, new_score)) 
                return possible_moves

        decision = LetterDecision()
        return decision.makeMove(grid)

def testDecisionMoveScoring():
    def checkCombination(x,y,g,h,a,b,p,q, result):
        d = Decision()
        d.original_score = ((x,y),(g,h))
        score = d.scoreMove(('a', ((a,b),(p,q))))
        print score
        assert math.fabs(result-score) < 1
   
    checkCombination(5, 1000, 5, 1000, 4, 1000, 4, 1000, -10000) 
    checkCombination(5, 1000, 5, 1000, 4, 1000, 5, 1000, -5000)
    checkCombination(5, 1000, 4, 1000, 5, 1000, 4, 1000, 0) 
    checkCombination(5, 1000, 4, 1000, 5, 1000, 4, 500, -500) 
    checkCombination(5, 500, 4, 1000, 4, 1000, 4, 1000, -5500) 

