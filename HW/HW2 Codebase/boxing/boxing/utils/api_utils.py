import logging
import os
import requests

from boxing.utils.logger import configure_logger


logger = logging.getLogger(__name__)
configure_logger(logger)


# Default to decimal fractions if the environment variable is not set
RANDOM_ORG_URL = os.getenv("RANDOM_ORG_URL",
                           "https://www.random.org/decimal-fractions/?num=1&dec=2&col=1&format=plain&rnd=new")


def get_random(max: int) -> float:
    """
    Fetches a random float number between 1 and max inclusive from random.org.

    Args:
        max (int): The upper bound (inclusive) for the random number.

    Returns:
        float: A random number between 1 and max.

    Raises:
        RuntimeError: If the request to random.org fails (e.g., timeout, bad response).
        ValueError: If the response from random.org is not a valid float.
    """
    
    # Construct the URL for fetching integers from random.org
    url = f"https://www.random.org/integers/?num=1&min=1&col=1&base=10&format=plain&rnd=new&max={max}"

    try:
        # Log the request to random.org
        logger.info(f"Fetching random number from {url}")

        response = requests.get(url, timeout=5)

        # Check if the request was successful
        response.raise_for_status()

        random_number_str = response.text.strip()

        try:
            random_number = float(random_number_str)
        except ValueError:
            logger.error(f"Invalid response from random.org: {random_number_str}")
            raise ValueError(f"Invalid response from random.org: {random_number_str}")

        logger.info(f"Received random number: {random_number}")
        return random_number

    except requests.exceptions.Timeout:
        logger.error("Request to random.org timed out.")
        raise RuntimeError("Request to random.org timed out.")

    except requests.exceptions.RequestException as e:
        logger.error(f"Request to random.org failed: {e}")
        raise RuntimeError(f"Request to random.org failed: {e}")
