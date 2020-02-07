from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from multiprocessing import Pool
from .core import GameOfLife, parse_args
import logging
import time


class ThreadPoolGameOfLife(GameOfLife):

    def handle_cell(self, point):
        live_neighbours = self.check_neighbors(point)
        alive = self.grid[point]
        self.next_grid[point] = self.decide(point, alive, live_neighbours)

    def step(self):
        start_time = time.time()
        with ThreadPoolExecutor(max_workers=10) as executor:
            coords = [point for point in self.points()]
            executor.map(self.handle_cell, coords)
        self.grid = self.next_grid.copy()
        self.logger.info(f'Generation step took {time.time() - start_time}')


class ProcessGameOfLife(GameOfLife):

    def handle_cell(self, point):
        live_neighbours = self.check_neighbors(point)
        alive = self.grid[point]
        return self.decide(point, alive, live_neighbours)

    def step(self):
        start_time = time.time()
        with ProcessPoolExecutor(max_workers=10) as executor:
            coords = [point for point in self.points()]
            values = executor.map(self.handle_cell, coords)
            for coord, val in zip(coords, values):
                self.next_grid[coord] = val
        self.grid = self.next_grid.copy()
        self.logger.info(f'Generation step took {time.time() - start_time}')


class PoolGameOfLife(GameOfLife):

    def handle_cell(self, point):
        live_neighbours = self.check_neighbors(point)
        alive = self.grid[point]
        return self.decide(point, alive, live_neighbours)

    def step(self):
        start_time = time.time()
        with Pool(processes=10) as executor:
            coords = [point for point in self.points()]
            values = executor.map(self.handle_cell, coords)
            for coord, val in zip(coords, values):
                self.next_grid[coord] = val
        self.grid = self.next_grid.copy()
        self.logger.info(f'Generation step took {time.time() - start_time}')


if __name__ == "__main__":

    settings = parse_args()
    game = ProcessGameOfLife(**settings)

    if game.show:
        game.animate()
    else:
        game.run()

