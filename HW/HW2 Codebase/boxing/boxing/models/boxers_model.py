from dataclasses import dataclass
import logging
import sqlite3
from typing import Any, List

from boxing.utils.sql_utils import get_db_connection
from boxing.utils.logger import configure_logger


logger = logging.getLogger(__name__)
configure_logger(logger)


@dataclass
class Boxer:
    id: int
    name: str
    weight: int
    height: int
    reach: float
    age: int
    weight_class: str = None

    def __post_init__(self):
        """
        Initializes the weight class based on the boxer's weight using the get_weight_class function.
        """
        self.weight_class = get_weight_class(self.weight)  # Automatically assign weight class


def create_boxer(name: str, weight: int, height: int, reach: float, age: int) -> None:
    """Creates a boxer.

        Args:
            name (str): The name of the boxer.
            weight (int): The weight of the boxer in kilograms.
            height (int): The height of the boxer in centimeters.
            reach (float): The reach of the boxer in meters.
            age (int): The age of the boxer in years.

        Raises:
            TypeError: If the name is not a valid string instance.
            TypeError: If the weight is not a valid int instance.
            TypeError: If the height is not a valid int instance.
            TypeError: If the reach is not a valid floatinstance.
            TypeError: If the age is not a valid int instance.

            ValueError: if any field is invalid.
            sqlite3.IntegrityError: If a boxer with the smae compound key (name, weight, height, reach, age) already exists.
            sqlite3.Error: For any other database errors.
    """
    logger.info(f"Recieved request to create a boxer: {name} - {weight} ({height})")

    if not isinstance(name, str) or not name.strip():
        logger.warning("Invalid boxer name provided.")
        raise ValueError("Invalid boxer name: must be a non-empty string.")

    if weight < 125:
        raise ValueError(f"Invalid weight: {weight}. Must be at least 125.")
    if height <= 0:
        raise ValueError(f"Invalid height: {height}. Must be greater than 0.")
    if reach <= 0:
        raise ValueError(f"Invalid reach: {reach}. Must be greater than 0.")
    if not (18 <= age <= 40):
        raise ValueError(f"Invalid age: {age}. Must be between 18 and 40.")

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            # Check if the boxer already exists (name must be unique)
            cursor.execute("SELECT 1 FROM boxers WHERE name = ?", (name,))
            if cursor.fetchone():
                raise ValueError(f"Boxer with name '{name}' already exists")

            cursor.execute("""
                INSERT INTO boxers (name, weight, height, reach, age)
                VALUES (?, ?, ?, ?, ?)
            """, (name, weight, height, reach, age))

            conn.commit()

            logger.info(f"Successfully created a boxer: {name} - {weight} ({height})")

    except sqlite3.IntegrityError:
        logger.error(f"Boxer already exists: {name} - {weight} ({height})")
        raise ValueError(f"Boxer with name '{name}' already exists")

    except sqlite3.Error as e:
        logger.error(f"Database error while creating song: {e}")
        raise e
        # raise sqlite3.Error(f"Database error: {e}")
    


def delete_boxer(boxer_id: int) -> None:
    """Permanently removes a boxer.

        Args:
            boxer_id (int): The boxer's id number to delete.

        Raises:
            ValueError: If the id does not exist.
            sqlite.Error: If any database error occurs
            
    """
    logger.info("Recieved request to delete a boxer")
    
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            # Check if the boxer exists before attemtping deletion
            cursor.execute("SELECT id FROM boxers WHERE id = ?", (boxer_id,))
            
            if cursor.fetchone() is None:
                raise ValueError(f"Boxer with ID {boxer_id} not found.")

            cursor.execute("DELETE FROM boxers WHERE id = ?", (boxer_id,))
            conn.commit()

            logger.info(f"Successfully deleted boxer with ID {boxer_id}")

    except sqlite3.Error as e:
        logger.error(f"Database error while deleting boxer: {e}")
        raise e

def get_leaderboard(sort_by: str = "wins") -> List[dict[str, Any]]:
    """Retrieves all boxers from the catalog.

    Args:
        sort_by (str): If the boxer won display that winner first.

    Returns:
        list[dict]: A list of dictionaries representing the boxers based on wins.

    Raises:
        sqlite3.Error: If any database error occurs.

    """
    logger.info("Recieved request to  a get leaderboard")

    query = """
        SELECT id, name, weight, height, reach, age, fights, wins,
               (wins * 1.0 / fights) AS win_pct
        FROM boxers
        WHERE fights > 0
    """

    if sort_by == "win_pct":
        query += " ORDER BY win_pct DESC"
    elif sort_by == "wins":
        query += " ORDER BY wins DESC"
    else:
        raise ValueError(f"Invalid sort_by parameter: {sort_by}")

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()

        leaderboard = []
        for row in rows:
            boxer = {
                'id': row[0],
                'name': row[1],
                'weight': row[2],
                'height': row[3],
                'reach': row[4],
                'age': row[5],
                'weight_class': get_weight_class(row[2]),  # Calculate weight class
                'fights': row[6],
                'wins': row[7],
                'win_pct': round(row[8] * 100, 1)  # Convert to percentage
            }
            leaderboard.append(boxer)

            logger.info(f"Successfully got leaderboard:")

        return leaderboard

    except sqlite3.Error as e:
        raise e


def get_boxer_by_id(boxer_id: int) -> Boxer:
    """Gets boxer details from boxer id.

        Args:
            id (int): The boxer's id number.


        Raises:
            ValueError: If the id is not a valid int instance, boxer is not found.

            
    """

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            logger.info(f"Attempting to retrieve boxer with ID {boxer_id}")
            cursor.execute("""
                SELECT id, name, weight, height, reach, age
                FROM boxers 
                WHERE id = ?
            """, (boxer_id,))

            row = cursor.fetchone()

            if row:
                logger.info(f"Boxer with ID {boxer_id} found")
                boxer = Boxer(
                    id=row[0], name=row[1], weight=row[2], height=row[3],
                    reach=row[4], age=row[5]
                )
                return boxer
            else:
                logger.info(f"Bixer with ID {boxer_id} not found")
                raise ValueError(f"Boxer with ID {boxer_id} not found.")

    except sqlite3.Error as e:
        logger.error(f"Database error while retrieving boxer by ID {boxer_id}: {e}")
        raise e


def get_boxer_by_name(boxer_name: str) -> Boxer:
    """Gets boxer details from boxer name.

        Args:
            name (str): The name of the boxer.

        Returns: THe Boxer corresponding to the name.

        Raises:
            ValueError: If the Boxer is not found.
            sqlite3.Error: If any database error occurs.
            
    """

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            logger.info(f"Attempting to retrieve Boxer with name '{boxer_name}' ")
            cursor.execute("""
                SELECT id, name, weight, height, reach, age
                FROM boxers 
                WHERE name = ?
            """, (boxer_name,))

            row = cursor.fetchone()

            if row:
                logger.info(f"Boxer with name '{boxer_name}' found")
                boxer = Boxer(
                    id=row[0], name=row[1], weight=row[2], height=row[3],
                    reach=row[4], age=row[5]
                )
                return boxer
            else:
                logger.info(f"Boxer with name '{boxer_name}' not found")
                raise ValueError(f"Boxer '{boxer_name}' not found.")

    except sqlite3.Error as e:
        raise e


def get_weight_class(weight: int) -> str:
    """GEts the weight class of a specific weight.

        Args:
            weight (int): The weight of the boxer in kilograms.

        Returns:
            str: The weight class of that weight 

        Raises:
            TypeError: If the weight is not a valid int instance.
            
    """
    logger.info(f"Attempting to retrieve weight class with weight '{weight}' ")

    if weight >= 203:
        weight_class = 'HEAVYWEIGHT'
    elif weight >= 166:
        weight_class = 'MIDDLEWEIGHT'
    elif weight >= 133:
        weight_class = 'LIGHTWEIGHT'
    elif weight >= 125:
        weight_class = 'FEATHERWEIGHT'
    else:
        raise ValueError(f"Invalid weight: {weight}. Weight must be at least 125.")
    
    logger.info(f"Successfully retrieved weight class for weight '{weight}'")
    return weight_class
    


def update_boxer_stats(boxer_id: int, result: str) -> None:
    """ Updates boxer stats with the given results

        Args:
            id (int): The boxer's id number.

        Raises:
            TypeError: If the id is not a valid int instance.
            
    """
    logger.info(f"Recieved request to update boxer with boxer ID: '{boxer_id}' with result: '{result}' ")

    if result not in {'win', 'loss'}:
        raise ValueError(f"Invalid result: {result}. Expected 'win' or 'loss'.")

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT id FROM boxers WHERE id = ?", (boxer_id,))
            if cursor.fetchone() is None:
                raise ValueError(f"Boxer with ID {boxer_id} not found.")

            if result == 'win':
                cursor.execute("UPDATE boxers SET fights = fights + 1, wins = wins + 1 WHERE id = ?", (boxer_id,))
            else:  # result == 'loss'
                cursor.execute("UPDATE boxers SET fights = fights + 1 WHERE id = ?", (boxer_id,))

            conn.commit()
            logger.info(f"Successfully updated boxer with ID: {boxer_id} ")

    except sqlite3.Error as e:
        raise e
    
