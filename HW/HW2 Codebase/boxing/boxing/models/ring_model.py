import logging
import math
from typing import List

from boxing.models.boxers_model import Boxer, update_boxer_stats
from boxing.utils.logger import configure_logger
from boxing.utils.api_utils import get_random


logger = logging.getLogger(__name__)
configure_logger(logger)


class RingModel:
    """
    A class to manage a ring of boxers.

    Attributes:
        ring (int): The list of boxers in the ring
                        
    """

    def __init__(self):
        """Initializes the RingModel with an empty List made with Boxers.

        """
        self.ring: List[Boxer] = []

    ##################################################
    # Boxer Management Functions
    ##################################################

    def fight(self) -> str:
        """Constructor for a fight.

        Creates a fights with at least two boxers.

        """
        logger.info("Received request to create the fight")
    
        if len(self.ring) < 2:
            raise ValueError("There must be two boxers to start a fight.")

        boxer_1, boxer_2 = self.get_boxers()

        skill_1 = self.get_fighting_skill(boxer_1)
        skill_2 = self.get_fighting_skill(boxer_2)

        # Compute the absolute skill difference
        # And normalize using a logistic function for better probability scaling
        delta = abs(skill_1 - skill_2)
        normalized_delta = 1 / (1 + math.e ** (-delta))

        random_number = get_random()

        if random_number < normalized_delta:
            winner = boxer_1
            loser = boxer_2
        else:
            winner = boxer_2
            loser = boxer_1

        update_boxer_stats(winner.id, 'win')
        update_boxer_stats(loser.id, 'loss')

        self.clear_ring()

        return winner.name

    def clear_ring(self):
        "DO WE NEED TO ADD THE IF SELF>CHECH_IFEMPTY"
        """Clears all boxers from the ring.

        Clears all boxers from the ring.

        """
        logger.info("Received request to clear the playlist")

        try:
            if not self.ring:
                return
        except ValueError:
            logger.warning("Clearing an empty ring")

        self.ring.clear()
        logger.info("Successfully cleared the ring")

    def enter_ring(self, boxer: Boxer):
        """Adds a boxer to the ringt.

        Args:
            boxer (Boxer): The boxer to add to the ring.

        Raises:
            TypeError: If the boxer is not a valid Boxer instance.
            ValueError: If a boxer with the same 'name' already exists.

        """
        logger.info("Received request to add a boxer to the ring")

        if not isinstance(boxer, Boxer):
            logger.error("Invalid type: Boxer is not a valid Boxer instance")
            raise TypeError(f"Invalid type: Expected 'Boxer', got '{type(boxer).__name__}'")

        if len(self.ring) >= 2:
            raise ValueError("Ring is full, cannot add more boxers.")

        self.ring.append(boxer)
        logger.info(f"Successfully added boxer to ring: {boxer.name} - {boxer.weight} ({boxer.height})")

    ##################################################
    # Ring Retrieval Functions
    ##################################################

    def get_boxers(self) -> List[Boxer]:
        """Returns a list of all the boxers in the ring.

        Returns:
            Ring[Boxer]: A list of all boxers in the ring.

        Raises:
            ValueError: If the ring is empty.

        """
        if not self.ring:
            pass
        else:
            pass

        logger.info("Retrieving all boxers in the ring")
        return self.ring

    def get_fighting_skill(self, boxer: Boxer) -> float:
        """Returns the fighting skills of the ring in a float value.

        Args: 
            boxer (Boxer): The boxer to get fighting skills .

        Returns:
            the fighting skills in a float value

        """

        # Arbitrary calculations
        age_modifier = -1 if boxer.age < 25 else (-2 if boxer.age > 35 else 0)
        skill = (boxer.weight * len(boxer.name)) + (boxer.reach / 10) + age_modifier

        logger.info("Fighting skills were calculated")
        return skill
