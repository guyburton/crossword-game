from crossword import *
import string

def getInput(func):
    while True:
        try:
            return func()
        except InputError as e:
            print "Error in input:", e

class HumanPlayer(object):
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

