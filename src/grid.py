from config import grid_size, null_char
import config

# Thrown if a player input is incorrect
class InputError(Exception):
    def __init__(self, desc):
        self.msg = desc
    def __str__(self):
        return self.msg
        
class BaseGrid(object):
    def __init__(self):
        self.grid = [0] * grid_size * grid_size
    def __init__(self, grid):
        self.grid = list(grid.grid)

    # returns the letter at the specified grid location
    def getLetter(self, row, col):
        return self.grid[col * grid_size + row]

    # prints the grid
    def __str__(self):
        return '\n'.join([''.join(self.getLetterLine(i)) for i in range(grid_size, grid_size*2)])
        
    # returns the 5 letters at the specified starting position
    # 0-4 are the horizontal words from the top
    # 5-9 are the vertical words from the left
    def getLetterLine(self, i):
        if i < grid_size:
            return self.grid[i * grid_size : i * grid_size + grid_size]
        return [self.getLetter(i - grid_size, j) for j in range(0, grid_size)]

# returns the 5 possible word configurations
# TODO make this generic for grid_size
def getPossibleWordsFromLetterLine(letters):
    words = []
    words.append(letters[0:5])
    words.append(letters[0:4])
    words.append(letters[0:3])
    words.append(letters[1:4])
    words.append(letters[1:5])
    words.append(letters[2:5])
    return [''.join(w) for w in words]

# returns a list of words from within the set of letters that are in the dictionary
def getAllValidWordsForLetterLine(letters):
    words = getPossibleWordsFromLetterLine(letters)
    return [w for w in words if w in config.dictionary]
    
class Grid(BaseGrid): 
    def __init__(self):
        self.grid = [null_char] * grid_size * grid_size

    # sets the letter at the specified location
    def setLetter(self, row, col, letter, force=False):
        if row < 0 or row > 4:
            raise InputError("Row out of bounds: %x" % row)
        if col < 0 or col > 4:
            raise InputError("Col out of bounds: %x" % col)
        if self.getLetter(row, col) != null_char and not force:
            raise InputError("Square already populated (%x,%x) = %s" % (row, col, self.getLetter(row, col))) 
        self.grid[col * grid_size + row] = letter

    # returns a list of scoring words from the Grid
    def getScoringWords(self):
        scoring_words = []
        for i in range(0, grid_size * 2):
            letterLine = self.getLetterLine(i)
            words = getAllValidWordsForLetterLine(letterLine)
            if words:
                longest_word = max(words, key=len)
                scoring_words.append(longest_word)
        return scoring_words
