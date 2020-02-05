import pytest
import numpy as np

from .main import GameOfLife

# Keep config small so tests will run quickly
test_config = {
    'size': (20, 20),
    'max_generations': 20
}

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


# Run test 10 times and mark each one
@pytest.mark.parametrize('execution_number', range(10))
def test_run(persistant_state, execution_number):
    """
    Sanity test to make sure the game is consistent.
    Given an initial state, and expected end state should be able to be reached.
    """
    states = persistant_state
    start, expected_end = states
    game = GameOfLife(**test_config)
    game.grid = start
    game.run()
    end_result = game.grid
    np.testing.assert_array_equal(end_result, expected_end)
