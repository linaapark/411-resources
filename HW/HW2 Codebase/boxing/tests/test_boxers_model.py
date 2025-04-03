from contextlib import contextmanager
import re
import sqlite3

import pytest

from boxing.models.boxers_model import (
    Boxer,
    create_boxer,
    delete_boxer,
    get_leaderboard,
    get_boxer_by_id,
    get_boxer_by_name,
    get_weight_class,
    update_boxer_stats
)

######################################################
#
#    Fixtures
#
######################################################

def normalize_whitespace(sql_query: str) -> str:
    return re.sub(r'\s+', ' ', sql_query).strip()

# Mocking the database connection for tests
@pytest.fixture
def mock_cursor(mocker):
    mock_conn = mocker.Mock()
    mock_cursor = mocker.Mock()

    # Mock the connection's cursor
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = None  # Default return for queries
    mock_cursor.fetchall.return_value = []
    mock_cursor.commit.return_value = None

    # Mock the get_db_connection context manager from sql_utils
    @contextmanager
    def mock_get_db_connection():
        yield mock_conn  # Yield the mocked connection object

    mocker.patch("boxing.models.boxers_model.get_db_connection", mock_get_db_connection)

    return mock_cursor  # Return the mock cursor so we can set expectations per test


######################################################
#
#    Add and delete
#
######################################################


#1
def test_create_boxer(mock_cursor):
    """Test creating a new boxer in the catalog.

    """
    create_boxer(name="Boxer Name",weight= 120, height=62, reach=10.9, age=18)

    expected_query = normalize_whitespace("""
        INSERT INTO boxers (name, weight, height, reach, age)
        VALUES (?, ?, ?, ?, ?)
    """)
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    # Extract the arguments used in the SQL call (second element of call_args)
    actual_arguments = mock_cursor.execute.call_args[0][1]
    expected_arguments = ("Boxer Name", 120, 62, 10.9, 18)

    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."

#2
def test_create_boxer_duplicate(mock_cursor):
    """Test creating a boxer with a duplicate name(should raise an error).

    """
    # Simulate that the database will raise an IntegrityError due to a duplicate entry
    mock_cursor.execute.side_effect = sqlite3.IntegrityError("UNIQUE constraint failed: boxer.name")

    with pytest.raises(ValueError, match="Boxer with name 'Boxer  Name' already exists."):
        create_boxer(name="Boxer Name", weight = 120, height = 62, reach = 10.9, age = 18)


#3
def test_create_boxer_invalid_name():
    """Test error when trying to create a Boxer with an invalid weight (e.g., negative duration)

    """
    with pytest.raises(ValueError, match=r"Invalid boxer name: . \(must be a non-empty string\)."):
        create_boxer(name="", weight = -180, height = 62, reach = 10.9, age = 18)

#4
def test_create_boxer_invalid_weight():
    """Test error when trying to create a Boxer with an invalid weight (e.g., zero weight)

    """
    with pytest.raises(ValueError, match=r"Invalid weight: 0. \(Must be at least 125\)."):
        create_boxer(name="Boxer Name", weight = 0, height = 62, reach = 10.9, age = 18)

    with pytest.raises(ValueError, match=r"Invalid weight: invalid. \(Must be at least 125\)."):
        create_boxer(name="Boxer Name", weight = "Invalid", height = 62, reach = 10.9, age = 18)

#5
def test_create_boxer_invalid_height():
    """Test error when trying to create a Boxer with an invalid height (e.g., height zero)

    """
    with pytest.raises(ValueError, match=r"Invalid height: 0. \(Must be greater than 0\)."):
        create_boxer(name="Boxer Name", weight = 180, height = 0, reach = 10.9, age = 18)

    with pytest.raises(ValueError, match=r"Invalid height: invalid. \(Must be greater than 0\)."):
        create_boxer(name="Boxer Name", weight = 180, height = "invalid", reach = 10.9, age = 18)


#6
def test_create_boxer_invalid_reach():
    """Test error when trying to create a Boxer with an invalid reach  (e.g., reach zero)

    """
    with pytest.raises(ValueError, match=r"Invalid reach:  0. \(Must be greater than 0\)."):
        create_boxer(name="Boxer Name", weight = 180, height = 52, reach = 0, age = 18)

    with pytest.raises(ValueError, match=r"Invalid reach: invalid \(Must be greater than 0\)."):
        create_boxer(name="Boxer Name", weight = 180, height = 52, reach = "invalid", age = 18)


#7
def test_create_boxer_invalid_age():
    """Test error when trying to create a Boxer with an invalid age  (e.g., age 15)

    """
    with pytest.raises(ValueError, match=r"Invalid age:  15. \(Must be between 18 and 40\)."):
        create_boxer(name="Boxer Name", weight = 180, height = 52, reach = 0, age = 15)

    with pytest.raises(ValueError, match=r"Invalid age: invalid \(Must be between 18 and 40\)."):
        create_boxer(name="Boxer Name", weight = 180, height = 52, reach = 10.9, age = "invalid")


#8
def test_delete_song(mock_cursor):
    """Test deleting a boxer from the catalog by boxer ID.

    """
    # Simulate the existence of a boxer w/ id=1
    # We can use any value other than None
    mock_cursor.fetchone.return_value = (True)

    delete_boxer(1)

    expected_select_sql = normalize_whitespace("SELECT id FROM boxers WHERE id = ?")
    expected_delete_sql = normalize_whitespace("DELETE FROM boxers WHERE id = ?")

    # Access both calls to `execute()` using `call_args_list`
    actual_select_sql = normalize_whitespace(mock_cursor.execute.call_args_list[0][0][0])
    actual_delete_sql = normalize_whitespace(mock_cursor.execute.call_args_list[1][0][0])

    assert actual_select_sql == expected_select_sql, "The SELECT query did not match the expected structure."
    assert actual_delete_sql == expected_delete_sql, "The UPDATE query did not match the expected structure."

    # Ensure the correct arguments were used in both SQL queries
    expected_select_args = (1,)
    expected_delete_args = (1,)

    actual_select_args = mock_cursor.execute.call_args_list[0][0][1]
    actual_delete_args = mock_cursor.execute.call_args_list[1][0][1]

    assert actual_select_args == expected_select_args, f"The SELECT query arguments did not match. Expected {expected_select_args}, got {actual_select_args}."
    assert actual_delete_args == expected_delete_args, f"The UPDATE query arguments did not match. Expected {expected_delete_args}, got {actual_delete_args}."

#9
def test_delete_boxer_bad_id(mock_cursor):
    """Test error when trying to delete a non-existent boxer.

    """
    # Simulate that no boxer exists with the given ID
    mock_cursor.fetchone.return_value = None

    with pytest.raises(ValueError, match="Boxer with ID 999 not found"):
        delete_boxer(999)


######################################################
#
#    Get Song
#
######################################################

#10
def test_get_leaderboard(mock_cursor):
    """Test error when having and Invalid sort_by parameter.

    """
    mock_cursor.fetchone.return_value = None

    with pytest.raises(ValueError, match="Invalid sort_by parameter: hello"):
        get_leaderboard("hello")

#11
def test_get_boxer_by_id(mock_cursor):
    """Test getting a boxer by id.

    """
    
    mock_cursor.fetchone.return_value = (1, "Boxer Name", 180, 52, 10.9, 18, False)

    result = get_boxer_by_id(1)

    expected_result = Boxer(1, "Boxer Name", 180, 52, 10.9, 18)

    assert result == expected_result, f"Expected {expected_result}, got {result}"

    expected_query = normalize_whitespace("SELECT id, name, weight, height, reach, age FROM boxers WHERE id = ?")
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    actual_arguments = mock_cursor.execute.call_args[0][1]
    expected_arguments = (1,)

    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."

#12
def test_get_boxer_by_id_bad_id(mock_cursor):
    """Test error when getting a non-existent boxer.

    """
    mock_cursor.fetchone.return_value = None

    with pytest.raises(ValueError, match="Boxer with ID 999 not found"):
        get_boxer_by_id(999)

#13
def test_get_song_by_name(mock_cursor):
    """Test getting a song by name.

    """
    mock_cursor.fetchone.return_value = (1, "Boxer Name", 180, 52, 10.9, 18, False)

    result = get_song_by_name("Boxer Name")

    expected_result = Song(1, 1, "Boxer Name", 180, 52, 10.9, 18)

    assert result == expected_result, f"Expected {expected_result}, got {result}"

    expected_query = normalize_whitespace("SELECT id, name, weight, height, reach, age FROM boxers WHERE id = ?")
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    actual_arguments = mock_cursor.execute.call_args[0][1]
    expected_arguments = ("Boxer Name")

    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."

#14
def test_get_song_by_name_bad_name(mock_cursor):
    """Test error when getting a non-existent name.

    """
    mock_cursor.fetchone.return_value = None

    with pytest.raises(ValueError, match="Boxer with name 'Boxer Name' not found"):
        get_song_by_compound_key("Boxer Name")

######################################################
#
#    Get Weight Class
#
######################################################

#15
def get_weight_class_by_weight(mock_cursor):
    """Test getting a weight class by weight.

    """
    mock_cursor.fetchone.return_value = (200)
    if isinstance(weight, tuple):
        weight = weight[0] 
    result = get_weight_class(weight) 

    expected_result = 'MIDDLEWEIGHT'

    assert result == expected_result, f"Expected {expected_result}, got {result}"

    expected_query = normalize_whitespace("SELECT id, name, weight, height, reach, age FROM boxers WHERE name = ?")
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][2]) #edited indices

    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    actual_arguments = mock_cursor.execute.call_args[0][1]
    expected_arguments = (mock_cursor.weight)
    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."

#16
def test_get_weight_class_by_bad_weight(mock_cursor):
    """Test error when getting an invalid weight class via invalid weight.

    """
    mock_cursor.fetchone.return_value = None
    weight = 120
    with pytest.raises(ValueError, match=f"Invalid weight: {weight}. Weight must be at least 125."):
        get_weight_class(weight)


######################################################
#
#    Update Boxer
#
######################################################

#17
def test_update_boxer_stats(mock_cursor):
    """Test updating the stats of a boxer.

    """
    mock_cursor.fetchone.return_value = True

    boxer_id = 1
    result = 'win'
    update_boxer_stats(boxer_id, result)

    expected_query = normalize_whitespace("""
        UPDATE boxers SET fights = fights + 1, wins = wins + 1 WHERE id = ?
    """)
    actual_query = normalize_whitespace(mock_cursor.execute.call_args_list[1][0][0])

    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    actual_arguments = mock_cursor.execute.call_args_list[1][0][1]
    expected_arguments = (boxer_id,)

    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."


#18
def test_update_boxer_stats_bad_result(mock_cursor):
    """ Test updating a boxer's stats with an invalid result that is not a win or loss

    """
    mock_cursor.fetchone.return_value = None
    boxer_id = 1
    result = 'tie'
    with pytest.raises(ValueError, match=f"Invalid result: {result}. Expected 'win' or 'loss'."):
        update_boxer_stats(boxer_id, result)


#19
def test_update_boxer_stats_bad_id(mock_cursor):
    """ Test updating a boxer's stats with a non-existent/invalid ID

    """
    mock_cursor.fetchone.return_value = None
    boxer_id = 999
    result = 'win'
    with pytest.raises(ValueError, match=f"Boxer with ID {boxer_id} not found."):
        update_boxer_stats(boxer_id, result)