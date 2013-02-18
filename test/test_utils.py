import config
from grid import Grid

def setWholeGrid(grid, char):
    for i in range(0, config.grid_size):
        for j in range(0, config.grid_size):
            grid.setLetter(i,j, char)
