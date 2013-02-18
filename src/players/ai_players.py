from itertools import chain
import re
import math
import string
import random
import logging
import numpy as np

from config import grid_size, null_char, min_word_length
from player import PlayerPersonality
from grid import getPossibleWordsFromLetterLine
import config

logger = logging.getLogger('players')
decision_log = logging.getLogger('decision')
rx_log = logging.getLogger('rx')

randomness=0.15

coefficients = [
    lambda x3: 1 * x3,
    lambda x4: 10 * x4,
    lambda x5: 100 * x5
]

class PotentialMove(object):
    def __str__(self):
        return "Move: '%s' %s %s %s %s" % (
            self.value, 
            self.original_score_horizontal, 
            self.original_score_vertical, 
            self.new_score_horizontal, 
            self.new_score_vertical)
    
def findAllPossibleWordsForLine(word):
    for i in range(len(word), 0):
        if word[i] == null_char:
            word[i] = '\\w'
        else:
            break
    # internal nulls should be matched by exactly one 
    rx = re.compile('^' + word.replace(null_char, '\\w') + '$')
    matches = [d for d in config.dictionary if rx.match(d)]
    rx_log.debug('using regex:' + rx.pattern + 
        ' found %d valid words (%d letters)' % (len(matches), len(word)))
    return matches
    
# this is how we score a word 
def lineariseScore(move):
    # this method combines the possibilities 
    def sumMove(move_possibilities):
        move_score = sum([coefficients[i](move_possibilities[i])
            for i in range(0, grid_size - min_word_length + 1)])
        decision_log.debug("Scored %s = %d" % (str(move_possibilities), move_score))
        return move_score
    
    original = [sumMove(move.original_score_horizontal), sumMove(move.original_score_vertical)]
    new = [sumMove(move.new_score_horizontal), sumMove(move.new_score_vertical)]
    score = 0.0
    if original[0] > 0:
        score += new[0] / float(original[0])
    if original[1] > 0:
        score += new[1] / float(original[1])
    decision_log.debug("Scored %s = %s" % (str(move), str(score)))
    assert score >= 0
    score *= (1 + (randomness/2) - random.random() * randomness)
    return score
    
# scores the line based on possible remaining words in dictionary
# returns a list of tuples (max_score, matches)
def scoreLine(line):
    decision_log.debug('Scoring line: "' + ''.join(line) +'"')
    decision_log.debug('cache size: %d' % len(rx_cache))
    scores = dict((i, 0) for i in range(min_word_length, grid_size+1))
    
    all_words = ''.join(line)
    if all_words in rx_cache:
        decision_log.debug('Found cached result for ' + all_words + ' ' + str(rx_cache[all_words]))
        return rx_cache[all_words]
    for word in getPossibleWordsFromLetterLine(line):
        matches = findAllPossibleWordsForLine(word)
        if matches:
            max_score = len(max(matches, key=len))
            scores[max_score] += len(matches)
    
    decision_log.debug(
        'Score possibilities: ' + str(scores) + 
        ' Total: %d possible words' % sum(scores.values()))
        
    # normalise array to size of dictionary
    score_array = np.array([float(scores[i]) for i in scores])
    rx_cache[all_words] = score_array
    return score_array
    
rx_cache = {}
class Decision(object):
    # possibilities are (move, new_score, original_score)
    def selectBestMove(self, possibilities):
        logger.debug('found possible moves: \n' + 
                    '<Letter> *orig score* horizontal, vertical,' +
                    ' *new score* horizontal, vertical\n' + 
                    '\n'.join([str(s) for s in possibilities]))
        
        decision_log.debug('Linearising move scores to make decision')
        scored_possibilities = [(x, lineariseScore(x)) for x in possibilities]
        decision_log.info('Scored possibilities:\n' + '\n'.join(
            [str(s[0]) + ' = ' + str(s[1]) for s in scored_possibilities]))
        max_score = max(scored_possibilities, key=lambda s: s[1])
        #values = [x for x in scored_possibilities if x[1] - max_score) < param2] 
        return max_score

    def makeMove(self, grid):
        possible_moves = [] 
        logger.warn('Grid:\n' + grid.__str__())
        logger.info('Searching for empty cells')
        for col in range(0, grid_size):
            for row in range(0, grid_size):
                if grid.getLetter(col, row) != null_char:
                    continue
                logger.debug('Found empty cell at %d, %d' % (col, row))
                
                self.horizontal_word = list(grid.getLetterLine(col + grid_size))
                self.vertical_word = list(grid.getLetterLine(row))
                logger.info('Intersecting Lines: ' + 
                    ''.join(self.horizontal_word) + ' ' + 
                    ''.join(self.vertical_word))
                assert null_char in self.horizontal_word
                assert null_char in self.vertical_word
                
                self.original_score_horizontal = scoreLine(self.horizontal_word)
                self.original_score_vertical = scoreLine(self.vertical_word)
                
                logger.debug('Assessing grid position')
                possibilities = self.assessGridPosition(row, col)
                possible_moves.extend(possibilities)

        logger.info('Selecting best move')
        best_move = self.selectBestMove(possible_moves)
        
        logger.warn("Best Move: %s = %d" % (str(best_move[0]), best_move[1]))
        return best_move[0].value

class LetterDecision(Decision):
    def assessGridPosition(self, row, col):
        possible_moves = []
        horizontal_word = self.horizontal_word
        vertical_word = self.vertical_word
    
        for l in range(ord('a'), ord('z')+1):
            letter = chr(l)
            horizontal_word[row] = letter
            vertical_word[col] = letter
            move = PotentialMove()
            move.value = (letter, row, col)
            move.original_score_horizontal = self.original_score_horizontal
            move.original_score_vertical = self.original_score_vertical
            move.new_score_horizontal = scoreLine(horizontal_word)
            move.new_score_vertical = scoreLine(vertical_word)
        
            if (sum(move.new_score_horizontal) + 
                sum(move.new_score_vertical) > 0):
                possible_moves.append(move)
   
        return possible_moves
        
class PlaceLetterDecision(Decision):
    def __init__(self, letter):
        self.letter = letter
    def assessGridPosition(self, row, col):
        horizontal_word = self.horizontal_word
        vertical_word = self.vertical_word
        assert horizontal_word[row] == null_char
        assert vertical_word[col] == null_char
        horizontal_word[row] = self.letter
        vertical_word[col] = self.letter
        
        move = PotentialMove()
        move.value = (col, row)
        move.original_score_horizontal = self.original_score_horizontal
        move.original_score_vertical = self.original_score_vertical
        move.new_score_horizontal = scoreLine(horizontal_word)
        move.new_score_vertical = scoreLine(vertical_word)
        return [move]  
        
# basic cpu strategy
class BasicPlayer(PlayerPersonality):
    def __init__(self, name):
        # caches position when choosing a letter to avoid duplicate work
        self.nextCoord = None
        self.name = name
        
    def placeLetter(self, grid, letter):
        logger.warn('%s making decision where to place letter' % self.name)
        if self.nextCoord != None:
            coord = self.nextCoord
            self.nextCoord = None
            return coord
        return PlaceLetterDecision(letter).makeMove(grid)

    def chooseLetter(self, grid):
        logger.warn('%s choosing letter' % self.name)
        decision = LetterDecision().makeMove(grid)
        self.nextCoord = (decision[2], decision[1])
        return decision[0]