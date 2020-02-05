import time
import concurrent.futures
import sys
import numpy as np
import argparse
import logging

import matplotlib.pyplot as plt
import matplotlib.animation as animation

from toolbox.decorator import timeit


for key in logging.Logger.manager.loggerDict:
   logging.getLogger(key).setLevel(logging.CRITICAL)

logger = logging.getLogger(__name__)


class GameOfLife:

    def __init__(self, size=(100, 100)):
        self.width, self.height = size
        self.grid = self.init_grid(size)
        self.new_grid = self.grid.copy()

    @property
    def indices(self):
        values = getattr(self, '_indices', [])
        if not values:
            for x in range(self.width):
                for y in range(self.height):
                    values.append((x, y))
            self._indices = values
        return self._indices

    @staticmethod
    def init_grid(size):
        """
        Create random grid array with distribution of 0 and 1
        """
        arr = np.random.uniform(0, 1, size)
        return (arr > 0.75).astype('int')

    @staticmethod
    def get_radius(i, j):
        """ 
        Generator to return indices for points immediatley around i, j
        """
        for x in [i-1, i, i+1]:
            for y in [j-1, j, j+1]:
                if(x == i and y == j):
                    pass
                else:
                    yield x, y

    def get_neighbors(self, point):
        """
        Return number of cells in current grid around point that are 1
        """
        live_neighbours = 0
        for x, y in self.get_radius(*point):
            live_neighbours += self.grid[x % self.width][y % self.height]
        return live_neighbours

    def decide(self, point):
        live = self.get_neighbors(point)
        value = self.grid[point]

        if value == 0 and live == 3:
            self.new_grid[point] = 1
        elif value == 1 and live != 2 and live != 3:
            self.new_grid[point] = 0

    def step_generation(self):
        """
        Run for each time step, this will scan the current grid and
        update it based on the rules of life
        """
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            future_to_index = {executor.submit(self.decide, index): index for index in self.indices}
            for future in concurrent.futures.as_completed(future_to_index):
                index = future_to_index[future]
                try:
                    data = future.result()
                except Exception as exc:
                    print('%r generated an exception: %s' % (index, exc))

        self.grid = self.new_grid.copy()


def update(frame, game):
    game.step_generation()
    X, Y = np.meshgrid(range(game.width+1), range(game.height+1))
    plt.pcolormesh(X, Y, game.grid, cmap=plt.cm.RdBu)
    plt.title('Time={}'.format(frame))


if(__name__ == "__main__"):

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

    logger.setLevel(logging.INFO)

    size = (args.dimension, args.dimension)
    max_generations = args.generations
    game = GameOfLife(size=size)

    if args.show:
        figsize = (5, 5)
        interval = args.interval
        repeat = args.repeat

        fig = plt.figure(figsize=figsize)
        ani = animation.FuncAnimation(
            fig, update, frames=max_generations,
            interval=interval, repeat=repeat,
            fargs=(game,))
        plt.show()

        sys.exit(0)

    generation = 0
    while generation <= max_generations:
        game.step_generation()
        generation += 1
