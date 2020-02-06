import argparse
import logging
import time

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation


def parse_args():
    """
    Handle generic command arguments and return as a dictionary
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-w', '--width', type=int, default=50,
                        help='Width of the active grid for the game of life')
    parser.add_argument('--height', type=int, default=50,
                        help='Height of the active grid for the game of life')
    parser.add_argument('-s', '--show', action='store_true', default=False,
                        help='Show matplotlib animation.')
    parser.add_argument('-r', '--repeat', action='store_true', default=False,
                        help='Repeat matplotlib animation, requires --show')
    parser.add_argument('-g', '--max_generations', type=int, default=50,
                        help='Maximum generation to run the game')
    parser.add_argument('-v', '--verbose', action='store_true', default=False,
                        help='Output info about operations')
    args = parser.parse_args()
    return vars(args)


class GameOfLife:

    def __init__(self,
                 width=50,
                 height=50,
                 max_generations=50,
                 show=False,
                 repeat=False,
                 verbose=False):
        self.width = width
        self.height = height
        self.size = (self.width, self.height)
        array = np.random.uniform(0, 1, self.size)
        self.grid = (array > 0.75).astype('int')
        self.next_grid = self.grid.copy()
        self.max_generations = max_generations

        # matplotlib animation settings
        self.interval = 100
        self.show = show
        self.repeat = repeat
        self.figsize = (5, 5)

        self.logger = logging.getLogger(__name__)
        for key in logging.Logger.manager.loggerDict:
            logging.getLogger(key).setLevel(logging.WARNING)
        if verbose:
            logging.basicConfig(level=logging.INFO)
            self.logger.setLevel(logging.INFO)

    def points(self):
        """ 
        Generator to return coordinates for points in the grid
        """
        for x in range(self.width):
            for y in range(self.height):
                yield x, y

    @staticmethod
    def point_radius(i, j):
        """ 
        Generator to return coordinates for points immediatley around point i, j
        """
        for x in [i-1, i, i+1]:
            for y in [j-1, j, j+1]:
                if(x == i and y == j):
                    pass
                else:
                    yield x, y

    def check_neighbors(self, point):
        """
        Return number of cells in current grid around point that are 1
        """
        live_neighbours = 0
        for x, y in self.point_radius(*point):
            # NOTE: Creates a "tordial array" by using modulus operations
            # To illustrate -- 5 % 5 = 0 and -1 % 5 = -1 while {0, 1...4} % 5 = {0, 1...4}
            # Arrays can already access the -1th position to wrap backwards but this enables
            # us to reach the 0th position when the max is exceeded to wrap forward.
            live_neighbours += self.grid[x % self.width][y % self.height]

            # NOTE: Short circuit the code here
            # Finding more than 3 live neighbors causes no difference in cell life.
            if live_neighbours > 3:
                break
        return live_neighbours

    @staticmethod
    def decide(point, alive, live_neighbours):
        """
        Decide if the cell at the given point will live or die.
        This logic focuses on change states to minimize the logic
        """
        if alive == 0 and live_neighbours == 3:
            return 1
        elif alive == 1 and live_neighbours != 2 and live_neighbours != 3:
            return 0
        return alive

    def step(self):
        """
        Run for each time step, this will scan the current grid and
        update it based on the rules of life
        """
        for point in self.points():
            live_neighbours = self.check_neighbors(point)
            alive = self.grid[point]
            self.next_grid[point] = self.decide(point, alive, live_neighbours)
        self.grid = self.next_grid.copy()

    def run(self):
        """
        Run the game of life for set maximum number of generations
        """
        generation = 0
        while generation <= self.max_generations:
            start_time = time.time()
            self.step()
            self.logger.info(f'Generation step took {time.time() - start_time}')
            generation += 1

    def handle_frame(self, frame):
        """
        Handler function for matplotlob animation
        """
        X, Y = np.meshgrid(range(self.width+1), range(self.height+1))
        plt.pcolormesh(X, Y, self.grid, cmap=plt.cm.RdBu)
        plt.title('Time={}'.format(frame))
        self.step()

    def animate(self):
        """
        Initialize and run the animation
        """
        fig = plt.figure(figsize=self.figsize)
        ani = animation.FuncAnimation(
            fig, self.handle_frame, frames=self.max_generations,
            interval=self.interval, repeat=self.repeat)
        plt.show()


if __name__ == "__main__":

    settings = parse_args()
    game = GameOfLife(**settings)

    if game.show:
        game.animate()
    else:
        game.run()
