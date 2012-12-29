import sys
import string

def getDictionaryWords():
    with open('converted_words.txt', 'r') as wordsfile:
        return [w.strip() for w in wordsfile]

# the size of the crossword grid
grid_size = 5
null_char = '.'
dictionary = getDictionaryWords()

print "Loaded ", len(dictionary), " dictionary words"

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
        return '\n'.join([''.join(self.getLetters(i)) for i in range(grid_size,grid_size*2)])

def getPossibleWords(letters):
    words = []
    words.append(letters)
    words.append(letters[1:5])
    words.append(letters[2:5])
    words.append(letters[0:4])
    words.append(letters[0:3])
    return [''.join(w) for w in words]

class Grid(BaseGrid): 
    def __init__(self):
        self.grid = [null_char] * grid_size * grid_size

    # sets the letter at the specified location
    def setLetter(self, row, col, letter):
        if row < 0 or row > 4:
            raise InputError("Row out of bounds: %x" % row)
        if col < 0 or col > 4:
            raise InputError("Col out of bounds: %x" % col)
        if self.getLetter(row, col) != null_char:
            raise InputError("Square already populated (%x,%x) = %s" % (row, col, self.getLetter(row, col))) 
        self.grid[col * grid_size + row] = letter
    
    # returns the 5 letters at the specified starting position
    # 0-4 are the horizontal words from the top
    # 5-9 are the vertical words from the left
    def getLetters(self, i):
        if i < 5:
            return self.grid[i * grid_size : i * grid_size + grid_size]
        return [self.getLetter(i-5, j) for j in range(0, 5)] 


    # returns a list of words from within the set of letters that are in the dictionary
    def getWords(self, letters):
        words = getPossibleWords(letters)
        return [w for w in words if w in dictionary]

    # returns a list of scoring words from the Grid
    def getScoringWords(self):
        scoring_words = []
        for i in range(0, grid_size * 2):
            letters = self.getLetters(i)
            words = self.getWords(letters)
            if words:
                longest_word = max(words, key=len)
                scoring_words.append(longest_word)
        return scoring_words

class Player(object):
    def __init__(self, personality):
        self.personality = personality
        self.grid = Grid()

    def clearGrid(self):
        self.grid = Grid()

    def chooseLetter(self):
        return self.personality.chooseLetter(BaseGrid(self.grid)).lower()

    def placeLetter(self, letter):
        data = self.personality.placeLetter(BaseGrid(self.grid), letter)
        if (self.grid.getLetter(data[0], data[1]) != null_char):
            raise InputException("Cannot place letter at %x,%x" % data)
        print self.name(), 'placed', letter, 'at', data
        self.grid.setLetter(data[0], data[1], letter)

    def name(self):
        return self.personality.name

def playGame(player_personalities):
    players = [Player(p) for p in player_personalities]

    def completeGame():
        for player in players:
            # take last turn
            letter = player.chooseLetter()
            player.placeLetter(letter)

        for player in players:
            # summarise game
            print player.grid
            scoring_words = player.grid.getScoringWords()
            print player.name(), "words:"
            print ', '.join(["%s %x" % (w, len(w)) for w in scoring_words])
            player.score = sum([len(x) for x in scoring_words])

        leaderboard = sorted(players, key=lambda player: player.score, reverse=True)
        print "Scoreboard:"
        print '\n'.join(["%s - %d" % (l.name(), l.score) for l in leaderboard])
        return leaderboard

    for player in players:
        player.clearGrid()
        
    turn = 0
    while True: 
        for player in players:
            print "# Turn", turn
            if turn >= grid_size * grid_size - 1:
                return completeGame()
            turn += 1
            letter = player.chooseLetter()
            print player.name(), "chose", letter

            for player in players:  
                player.placeLetter(letter)
                print player.grid


