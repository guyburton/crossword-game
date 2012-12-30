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

class PotentialMove(object):
    def __str__(self):
        return "Move: %s %s %s %s %s" % (self.value, self.original_score_horizontal, self.original_score_vertical, self.new_score_horizontal, self.original_score_horizontal)
    pass

param1 = 5000 # multiple of scoring points when comparing to number of words available
param2 = 100  # threshold for score when picking best move at random
rx_cache = {}
class Decision(object):
    # scores the line based on possible remaining words in dictionary
    # returns a list of tuples (max_score, matches)
    def scoreLine(self, line):
        scores = {}
        for i in range(0, grid_size):
            scores[i] = 0
        all_words = ''.join(line)
        if all_words in rx_cache:
            return rx_cache[all_words]
        for word in getPossibleWords(line):
            rx = re.compile(word.replace(null_char, '\\w'))   
            matches = rx.findall(remaining_words)
            if matches:
                max_score = len(max(matches, key=len))
                scores[max_score - 1] += len(matches)

        score_array = np.array([scores[i] for i in range(0,grid_size)])
        rx_cache[all_words] = score_array
        return score_array

    # this is how we score a word 
    def lineariseScore(self, move):
        def highestScoringMove(move_score):
            for i in range(grid_size-1, 0, -1):
                if move_score[i] != 0:
                    return (i, move_score[i])
            return (0,0)
        def createVectors(line1, line2):
            line1_scores = highestScoringMove(line1)
            line2_scores = highestScoringMove(line2)
            return (np.array([line1_scores[0], line2_scores[0]]), np.array([line1_scores[1], line2_scores[1]]))
        print "move", move

        original = createVectors(move.original_score_horizontal, move.original_score_vertical) 
        original_max_scores = original[0]
        original_possibilities = original[1]
        new = createVectors(move.new_score_horizontal, move.new_score_vertical) 
        new_max_scores = new[0]
        new_possibilities = new[1]

        if new_max_scores[0] == original_max_scores[0]:
            assert new_possibilities[0] <= original_possibilities[0]    
        if new_max_scores[1] == original_max_scores[1]:
            assert new_possibilities[1] <= original_possibilities[1]

        score = np.sum(original_max_scores - new_max_scores) * param1 + \
                np.linalg.norm(original_possibilities - new_possibilities)

        return score * -1

    # possibilities are (move, new_score, original_score)
    def selectBestMove(self, possibilities):
        scored_possibilities = [(x, self.lineariseScore(x)) for x in possibilities] 
        max_score = max(scored_possibilities, key=lambda s: s[1])[1]
        values = [x for x in scored_possibilities if math.fabs(x[1] - max_score) < param2] 
        return random.choice(values)[0]

    def getDecisionReturnValue(self, move):
        return move.value

    def calculateNewScore(self, hline, vline):
        return self.scoreLine(hline), self.scoreLine(vline)

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
                self.original_score_horizontal = self.scoreLine(self.horizontal_word)
                self.original_score_vertical = self.scoreLine(self.vertical_word)

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
                horizontal_word = self.horizontal_word
                vertical_word = self.vertical_word
                horizontal_word[col] = letter
                vertical_word[row] = letter
                
                move = PotentialMove()
                move.value = (row, col)
                move.original_score_horizontal = self.original_score_horizontal
                move.original_score_vertical = self.original_score_vertical
                move.new_score_horizontal = self.scoreLine(horizontal_word)
                move.new_score_vertical = self.scoreLine(vertical_word)
                return [move]

        decision = PlaceLetterDecision()
        return decision.makeMove(grid)

    def chooseLetter(self, grid):
        class LetterDecision(Decision):
            def assessGridPosition(self, row, col):
                possible_moves = []
           
                horizontal_word = self.horizontal_word
                vertical_word = self.vertical_word

                for l in range(ord('a'), ord('z')+1):
                    letter = chr(l)
                    horizontal_word[col] = letter
                    vertical_word[row] = letter
                    move = PotentialMove()
                    move.value = letter
                    move.original_score_horizontal = self.original_score_horizontal
                    move.original_score_vertical = self.original_score_vertical
                    move.new_score_horizontal = self.scoreLine(horizontal_word)
                    move.new_score_vertical = self.scoreLine(vertical_word)
                    possible_moves.append(move)
                return possible_moves

        decision = LetterDecision()
        return decision.makeMove(grid)

def testDecisionMoveScoring():
    def checkCombination(x,y,g,h,a,b,p,q, result):
        d = Decision()
        d.original_score = ([(x,y)],[(g,h)])
        score = d.lineariseScore(([(a,b)],[(p,q)]))
        print score
        assert math.fabs(result-score) < 1
   
    checkCombination(5, 1000, 5, 1000, 4, 1000, 4, 1000, -10000) 
    checkCombination(5, 1000, 5, 1000, 4, 1000, 5, 1000, -5000)
    checkCombination(5, 1000, 4, 1000, 5, 1000, 4, 1000, 0) 
    checkCombination(5, 1000, 4, 1000, 5, 1000, 4, 500, -500) 
    checkCombination(5, 500, 4, 1000, 4, 1000, 4, 1000, -5500) 
    checkCombination(5, 50, 4, 10, 4, 100, 3, 20, -10050.9901951)


def testSelectBestMove():
    def createScore(moves1, possibilities1, moves2, possibilities2):
        return ([(moves1,possibilities1)],[(moves2,possibilities2)])

    def checkCombination(x,y,g,h, moves):
        d = Decision()
        d.original_score = createScore(x,y,g,h)

        found_move1 = False
        for i in range(0,100): # because randomness used
            move = d.selectBestMove(moves)
            print "move:", move
            found_move1 = found_move1 or move[0] == 'move1'

        assert found_move1
   
    checkCombination(5, 1000, 5, 1000, [
        ('move1', createScore(5, 1000, 5, 1000)), \
        ('move2', createScore(4, 1000, 4, 1000))  \
    ])
    checkCombination(5, 1000, 5, 1000, [
        ('move1', createScore(4, 1000, 4, 1000)), \
        ('move2', createScore(4, 1000, 4, 500))  \
    ])
    checkCombination(5, 1000, 5, 1000, [
        ('move1', createScore(4, 1000, 4, 1000)), \
        ('move2', createScore(4, 1000, 4, 1000))  \
    ])
    checkCombination(5, 2000, 5, 2000, [
        ('move1', createScore(4, 1000, 4, 1000)), \
        ('move2', createScore(4, 1050, 4, 1050))  \
    ])
