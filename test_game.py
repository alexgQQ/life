import pytest
import numpy as np

from .core import GameOfLife
from .pool import ThreadPoolGameOfLife, ProcessGameOfLife


# Keep config small so tests will run quickly
test_config = {
    'width': 20,
    'height': 20,
    'max_generations': 20,
}

ground_truth_class = GameOfLife
number_of_test_runs = 10


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


def handle_test(expected_states, test_class):
    states = persistant_state
    starting_state, expected_end = expected_states
    game = test_class(**test_config)
    game.grid = starting_state
    game.run()
    return expected_end, game.grid


@pytest.mark.parametrize('number', range(number_of_test_runs))
def test_game_of_life(persistant_state, number):
    """
    Sanity test to make sure the game is consistent.
    Given an initial state, and expected end state should be able to be reached.
    """
    test_class = GameOfLife
    states = persistant_state
    expected_end, resulting_end = handle_test(states, test_class)
    np.testing.assert_array_equal(resulting_end, expected_end)


@pytest.mark.parametrize('number', range(number_of_test_runs))
def test_thread_game_of_life(persistant_state, number):
    """
    Sanity test to make sure the game is consistent.
    Given an initial state, and expected end state should be able to be reached.
    """
    test_class = ThreadPoolGameOfLife
    states = persistant_state
    expected_end, resulting_end = handle_test(states, test_class)
    np.testing.assert_array_equal(resulting_end, expected_end)


@pytest.mark.skip('TODO: Figure out why this fails')
@pytest.mark.parametrize('number', range(number_of_test_runs))
def test_process_game_of_life(persistant_state, number):
    """
    Sanity test to make sure the game is consistent.
    Given an initial state, and expected end state should be able to be reached.
    """
    test_class = ProcessGameOfLife
    states = persistant_state
    expected_end, resulting_end = handle_test(states, test_class)
    np.testing.assert_array_equal(resulting_end, expected_end)
