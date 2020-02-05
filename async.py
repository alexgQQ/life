import numpy as np
import asyncio
import argparse
import sys

import matplotlib.pyplot as plt
import matplotlib.animation as animation


size = (50, 50)
width, height = size
arr = np.random.uniform(0, 1, size)
grid = (arr > 0.75).astype('int')
new_grid = grid.copy()


async def get_radius(i, j):
    """ 
    Generator to return indices for points immediatley around i, j
    """
    for x in [i-1, i, i+1]:
        for y in [j-1, j, j+1]:
            if(x == i and y == j):
                pass
            else:
                yield x, y


async def get_neighbors(point):
    """
    Return number of cells in current grid around point that are 1
    """
    live_neighbours = 0
    global grid
    async for x, y in get_radius(*point):
        live_neighbours += grid[x % width][y % height]
    return live_neighbours


async def cell_step(point):
    global grid
    global new_grid
    value = grid[point]
    live = await get_neighbors(point)
    if value == 0 and live == 3:
        new_grid[point] = 1
    elif value == 1 and live != 2 and live != 3:
        new_grid[point] = 0


async def step_generation():
    """
    Run for each time step, this will scan the current grid and
    update it based on the rules of life
    """
    cells = []
    global grid
    for index, value in np.ndenumerate(grid):
        cells.append(cell_step(index))
    await asyncio.gather(*cells)


def update(frame):
    global grid, new_grid
    X, Y = np.meshgrid(range(width+1), range(height+1))
    plt.pcolormesh(X, Y, grid, cmap=plt.cm.RdBu)
    plt.title('Time={}'.format(frame))
    asyncio.run(step_generation())
    grid = new_grid


def step():
    asyncio.run(step_generation())
    grid = new_grid


parser = argparse.ArgumentParser()
parser.add_argument('-n', '--dimension', type=int, default=50,
                    help='Length of a single side of the play area')
parser.add_argument('-s', '--show', action='store_true', default=False,
                    help='Show matplotlib animation.')
parser.add_argument('-i', '--interval', type=int, default=100,
                    help='Delay between display intervals, requires --show')
parser.add_argument('-r', '--repeat', action='store_true', default=False,
                    help='Repeat matplotlib animation, requires --show')
parser.add_argument('-g', '--generations', type=int, default=50,
                    help='Maximum generation to run the game')
args = parser.parse_args()

size = (args.dimension, args.dimension)
max_generations = args.generations

if args.show:
    figsize = (5, 5)
    interval = args.interval
    repeat = args.repeat

    fig = plt.figure(figsize=figsize)
    ani = animation.FuncAnimation(
        fig, update, frames=max_generations,
        interval=interval, repeat=repeat)
    plt.show()

    sys.exit(0)

generation = 0
while generation <= max_generations:
    step()
    generation += 1
