import sys
sys.path.insert(0, '../src')

import config
from grid import *
from test_utils import setWholeGrid

def testGetPossibleWordsFromLetterLine():
    words = getPossibleWordsFromLetterLine('abcde')
    print 'Possible Words:', words
    assert(len(words) == 6)
    assert((5+4+4+3+3+3) == sum([len(w) for w in words]))
    
def testGetAllValidWordsFromLetterLine():
    config.dictionary = ['abc', 'abcd', 'abcde', 'test']
    words = getAllValidWordsForLetterLine('abcde')
    print 'Valid Words:', words
    assert(len(words) == 3)
    
def testErrorSettingPopulatedCoord(): 
    grid = Grid()
    setWholeGrid(grid, 'z')
    try:
        grid.setLetter(0,0, 'a')
    except InputError:
        pass

def testGetScoringWords():
    config.dictionary = ['labia', 'buggy', 'buddy', 'age', 'main', 'bug', 'test']
    grid = Grid()
    for i in range(0,config.grid_size):
        word = config.dictionary[i]
        for j in range(0, len(word)):
            grid.setLetter(i, j, word[j])
        for j in range(len(word), grid_size):
            grid.setLetter(i, j, 'z')
            
    print grid
    scoring_words = grid.getScoringWords()
    print 'Scoring Words:', scoring_words
    
    assert(len(scoring_words) == 5)
    
    total_score = sum([len(s) for s in scoring_words])
    expected_score = sum([len(s) for s in config.dictionary[0:config.grid_size]])
    print total_score, "score should be", expected_score 
    assert total_score == expected_score