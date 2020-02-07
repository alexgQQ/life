import pytest
import numpy as np

from .core import GameOfLife
from .pool import ThreadPoolGameOfLife, ProcessGameOfLife, PoolGameOfLife


# Keep config small so tests will run quickly
test_config = {
    'width': 20,
    'height': 20,
    'max_generations': 20,
}

runs_per_class = 10
ground_truth_class = GameOfLife
classes_to_test = [
    GameOfLife,
    ThreadPoolGameOfLife,
    ProcessGameOfLife,
    PoolGameOfLife,
]

parameters = []
for test_class in classes_to_test:
    for _ in range(runs_per_class):
        parameters.append(test_class)


@pytest.fixture
def persistant_state():
    """
    Execute a game and save the initial grid and final grid.
    Fixture to test other implemetations handle the same state in the same way.
    """
    game = GameOfLife(**test_config)
    start = game.grid
    game.run()
    end = game.grid
    return start, end


@pytest.mark.parametrize('test_class', parameters)
def test_game_of_life(persistant_state, test_class):
    """
    Sanity test to make sure the game is consistent.
    Given an initial state, and expected end state should be able to be reached.
    """
    starting_state, expected_end = persistant_state
    game = test_class(**test_config)
    game.grid = starting_state
    game.run()
    np.testing.assert_array_equal(game.grid, expected_end)
