import sys
sys.path.insert(0, '../src')
import crossword
from grid import Grid
import main_game
from players.ai_players import Decision, PotentialMove,lineariseScore
import config
from test_utils import setWholeGrid
import logging

logger = logging.getLogger('players')
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler(sys.stdout))
logger = logging.getLogger('decision')
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler(sys.stdout))

# these tests compare two moves against each other and check which wins

def compareScores(moveRiskWeightings):
    move = PotentialMove()
    move.value = 'test'
    move.original_score_horizontal = [1,1,1]
    move.original_score_vertical = [1,1,1]
    move.new_score_horizontal = moveRiskWeightings[0]
    move.new_score_vertical = moveRiskWeightings[1]
    score1 = lineariseScore(move)
    move.new_score_horizontal = moveRiskWeightings[2] 
    move.new_score_vertical = moveRiskWeightings[3]
    score2 = lineariseScore(move)
    return (score1, score2)
    
def testMoreWordsAreBetter():
    scores = compareScores([[1,0,0],[0,0,0], [1,0,0], [1,0,0]])
    print scores[0], scores[1]
    assert scores[0] < scores[1]

def testBiggerWordsAreBetter():
    scores = compareScores([[1,0,0],[0,0,0], [1,1,0], [0,0,0]])
    print scores[0], scores[1]
    assert scores[0] < scores[1]
    