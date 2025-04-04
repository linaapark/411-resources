from dataclasses import asdict

import pytest
import unittest
from unittest.mock import patch
from pytest_mock import MockerFixture

from boxing.models.ring_model import RingModel
from boxing.models.boxers_model import Boxer

@pytest.fixture()
def ring_model():
    """Fixture to provide a new instance of RingModel for each test."""
    return RingModel()

"""Fixtures providing sample songs for the tests."""
@pytest.fixture
def sample_boxer1():
    return Boxer(1, "Boxer One", 150, 62, 10.9, 18)

@pytest.fixture
def sample_boxer2():
    return Boxer(2, "Boxer Two", 220, 52, 18.0, 20)

@pytest.fixture
def sample_ring(sample_boxer1, sample_boxer2):
    return [sample_boxer1, sample_boxer2]

@pytest.fixture
def mock_update_boxer_stats(mocker):
    """Mock the update_boxer_stats function for testing purposes."""
    return mocker.patch("boxing.models.ring_model.update_boxer_stats")

##################################################
# Add / Remove Boxer Management Test Cases
##################################################

#1
def test_add_boxer_to_ring(ring_model, sample_boxer1):
    """Test adding a boxer to the ring.

    """
    ring_model.enter_ring(sample_boxer1)
    assert len(ring_model.ring) == 1
    assert ring_model.ring[0].name == 'Boxer One'

#2
def test_clear_ring(ring_model, sample_boxer1):
    """Test clearing the entire ring.

    """
    ring_model.enter_ring(sample_boxer1)

    ring_model.clear_ring()
    assert len(ring_model.ring) == 0, "Ring should be empty after clearing"

#3
def test_add_bad_boxer_to_ring(ring_model, sample_boxer1):
    """Test error when a invalid boxer enters ring.

    """
    with pytest.raises(TypeError, match=f"Invalid type: Expected 'Boxer', got '{type(asdict(sample_boxer1)).__name__}'"):
        ring_model.enter_ring(asdict(sample_boxer1))

#4
def test_full_ring(ring_model, sample_boxer1, sample_boxer2):
    """Test error when we try to add a boxer to a full ring.

    """
    ring_model.enter_ring(sample_boxer1)
    ring_model.enter_ring(sample_boxer2)
    assert len(ring_model.ring) == 2
    with pytest.raises(ValueError, match="Ring is full, cannot add more boxers."):
        ring_model.enter_ring(sample_boxer1)


##################################################
# Boxer Retrieval Functions
##################################################
#5
def test_get_boxers(ring_model, sample_ring):
    """Test successfully retrieving all boxers from the ring.

    """
    ring_model.ring.extend(sample_ring)

    all_boxers = ring_model.get_boxers()

    assert len(all_boxers) == 2
    assert all_boxers[0].name == 'Boxer One'
    assert all_boxers[1].name == 'Boxer Two'

#6
def test_get_empty_boxers(ring_model, sample_ring):
    """Test retrieving all boxers from empty ring.

    """
    with pytest.raises(ValueError, match="Ring is empty"):
        all_boxers = ring_model.get_boxers()

#7
def test_get_fighting_skill(ring_model, sample_boxer1):
    """Test retrieving fighting skills.
    
    """
    fighting_skill = ring_model.get_fighting_skill(sample_boxer1)

    assert fighting_skill == 1350.09

##################################################
# Fight/Overall
##################################################
#8
def test_fight(ring_model, sample_ring, sample_boxer1, sample_boxer2, mock_update_boxer_stats):
    """Test starting a fight.

    """
    ring_model.ring.extend(sample_ring)

    winner = ring_model.fight()

    if winner == sample_boxer1.name:
        winner_id = sample_boxer1.id
        loser_id = sample_boxer2.id
    else:
        winner_id = sample_boxer2.id
        loser_id = sample_boxer1.id

    mock_update_boxer_stats.assert_any_call(winner_id, 'win')
    mock_update_boxer_stats.assert_any_call(loser_id, 'loss')


    assert len(ring_model.ring) == 0, "Ring should be cleared once finished"

#9
def test_fight_bad(ring_model, sample_boxer1):
    """Testing the fewer than two aspect of the fight.
    
    """
    ring_model.enter_ring(sample_boxer1)

    assert len(ring_model.ring) == 1
    with pytest.raises(ValueError, match="There must be two boxers to start a fight."):
        ring_model.fight()