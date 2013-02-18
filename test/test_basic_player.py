import sys
sys.path.insert(0, '../src')
import crossword
from grid import Grid
import main_game
from players.ai_players import BasicPlayer, findAllPossibleWordsForLine, rx_cache
import config
from test_utils import setWholeGrid
import logging

logger = logging.getLogger('players')
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler(sys.stdout))
logger = logging.getLogger('decision')
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler(sys.stdout))
logger = logging.getLogger('rx')
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler(sys.stdout))

def testRegexMatchingSimple1():
    rx_cache.clear()
    config.dictionary = ['abc']
    matches = findAllPossibleWordsForLine('a.c')
    assert len(matches) == 1
    assert matches[0] == 'abc'

def testRegexMatchingSimple2():
    rx_cache.clear()
    config.dictionary = ['abc', 'abcd']
    matches = findAllPossibleWordsForLine('a.c.')
    print matches
    assert len(matches) == 1
    assert matches[0] == 'abcd'

def testRegexMatchingSimple3():
    rx_cache.clear()
    config.dictionary = ['abc', 'abcd', 'abcde']
    matches = findAllPossibleWordsForLine('a.c.')
    print matches
    assert len(matches) == 1
    assert matches[0] == 'abcd'

def testPlacesLetterToCompleteWordFromDictionary():
    rx_cache.clear()
    config.dictionary = ['abc']
    grid = Grid()
    player = BasicPlayer('test')
    setWholeGrid(grid, 'z')
    grid.setLetter(0,0,'a', True)
    grid.setLetter(0,1,'b', True)
    grid.setLetter(0,2, config.null_char, True)

    coord = player.placeLetter(grid, 'c')
    print "coord", coord
    assert coord == (0,2)

def testChoosesLetterToCompleteWordFromDictionary():
    rx_cache.clear()
    config.dictionary = ['abc']
    grid = Grid()
    player = BasicPlayer('test')
    setWholeGrid(grid, 'z')
    grid.setLetter(0,0,'a', True)
    grid.setLetter(0,1,'b', True)
    grid.setLetter(0,2, config.null_char, True)
    
    letter = player.chooseLetter(grid)
    assert letter == 'c'
    
def testScoreComparisonForSingleRow():
    rx_cache.clear()
    config.dictionary = ['abcd']
    grid = Grid()
    player = BasicPlayer('test')
    setWholeGrid(grid, 'z')
    grid.setLetter(0,0,'a', True)
    grid.setLetter(0,1,'b', True)
    grid.setLetter(0,2, config.null_char, True)
    grid.setLetter(0,3, config.null_char, True)

    for i in range(0, 10):
        # 0,2 is clearly the best position to place the letter c
        coord = player.placeLetter(grid, 'c')
        print "coord", coord
        assert coord == (0,2)
    
def testScoreComparisonForSingleRowForChooseLetter():
    rx_cache.clear()
    config.dictionary = ['abcd']
    grid = Grid()
    player = BasicPlayer('test')
    setWholeGrid(grid, 'z')
    grid.setLetter(0,0,'a', True)
    grid.setLetter(0,1,'b', True)
    grid.setLetter(0,2, config.null_char, True)
    grid.setLetter(0,3, config.null_char, True)

    # player could reasonably pick 'c' or 'd'
    letter = player.chooseLetter(grid)
    print "letter", letter
    assert letter in ['c', 'd']
    
def testGridPlacementNoPossibilities():
    rx_cache.clear()
    config.dictionary = ['abcd']
    grid = Grid()
    player = BasicPlayer('test')
    coord = player.placeLetter(grid, 'x')
    
    # the corners do the least 'damage' (still allow 4 letter words on both rows and cols)
    print "coord", coord
    assert coord in [(0,0), (0,4), (4,0), (4,4)]
    
def testEmptyGridChoosing():
    rx_cache.clear()
    config.dictionary = ['abcde']
    grid = Grid()
    player = BasicPlayer('test')
    letter = player.chooseLetter(grid)
    coord = player.placeLetter(grid, letter)
    
    # least damaging placement is a in top left corner
    print "letter", letter
    assert letter == 'a'
    assert coord == (0,0)