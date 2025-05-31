# auto_tester.py

import os
import json
import pytest

# Import your own adventure.py
import adventure

# -------------- 1.0 Check submitted files (3/3) ---------------

def test_1_0_submitted_files_exist():
    """
    1.0 Check submitted files (3/3)
    Ensure the following files exist in the repository root directory:
      - adventure.py
      - custom.json
      - map.pdf
    """
    cwd = os.getcwd()
    required = ["adventure.py", "custom.json", "map.pdf"]
    missing = [f for f in required if not os.path.exists(os.path.join(cwd, f))]
    assert not missing, f"Missing files: {missing}. Please check if they are in the project root directory."


# -------------- 1.1 Evaluate constants (3/3) ---------------

@pytest.fixture(scope="module")
def game_data():
    """
    Preload custom.json for subsequent tests
    """
    with open("custom.json", "r", encoding="utf-8") as f:
        return json.load(f)

def test_1_1_constants_exist_and_types():
    """
    1.1 Evaluate constants (3/3)
      - Check that adventure.py has both START and FINISH constants
      - They should both be string type
    """
    assert hasattr(adventure, "START"), "Missing constant START in adventure.py"
    assert hasattr(adventure, "FINISH"), "Missing constant FINISH in adventure.py"
    assert isinstance(adventure.START, str), "START must be a string (str)"
    assert isinstance(adventure.FINISH, str), "FINISH must be a string (str)"

def test_1_1_start_not_equal_finish():
    """
    1.1 (continued) START != FINISH
    """
    assert adventure.START != adventure.FINISH, "Constants START and FINISH cannot be the same."

def test_1_1_finish_room_exists_somewhere(game_data):
    """
    1.1 (continued) Ensure the FINISH string exists in either keys or moves of custom.json
    """
    finish = adventure.FINISH
    # If FINISH is one of the top-level room names in custom.json, that's fine
    if finish in game_data:
        return
    # Otherwise, it must appear in the moves field of some room
    found = any(
        finish in info.get("moves", {}).values()
        for info in game_data.values()
    )
    assert found, f"FINISH = '{finish}' not found in custom.json (neither in top-level keys nor in any moves)."


# -------------- 1.2 Evaluate move_user (2/2) ---------------

def test_1_2_move_user_valid(game_data):
    """
    1.2 Evaluate move_user (2/2)
    Test that moving from 'Recruit Training Camp' to 'north' should lead to 'Interior Wall Research Lab'
    (Note: This uses existing data from custom.json, no need to generate_map)
    """
    start_room = "Recruit Training Camp"
    new_room = adventure.move_user(game_data, start_room, "north")
    assert new_room == "Interior Wall Research Lab", (
        f"move_user('{start_room}', 'north') should return 'Interior Wall Research Lab', but got '{new_room}'"
    )

def test_1_2_move_user_invalid_direction_returns_same(game_data):
    """
    1.2 (continued) If given a non-existent direction, like 'fly', should return the same room name
    """
    start_room = "Recruit Training Camp"
    same = adventure.move_user(game_data, start_room, "fly")
    assert same == start_room, f"For invalid direction should return '{start_room}', but returned '{same}'"


# -------------- 1.3 Evaluate describe (3/3) ---------------

def test_1_3_describe_includes_text_and_moves(game_data):
    """
    1.3 Evaluate describe (3/3)
    describe(data, room) should output:
      1) The room's text description
      2) List all possible directions, e.g. "'north' to go to Interior Wall Research Lab"
    """
    room = "Recruit Training Camp"
    desc = adventure.describe(game_data, room).lower()
    # Check that it includes a key phrase from the text
    assert "dusty training grounds" in desc, f"describe('{room}') does not include the room's text content."
    # Check that it includes at least one direction
    assert "'north' to go to interior wall research lab" in desc, (
        f"describe('{room}') does not list the direction 'north' → 'Interior Wall Research Lab'."
    )
    # Check any other direction
    assert "'east' to go to shiganshina district" in desc, (
        f"describe('{room}') does not list the direction 'east' → 'Shiganshina District'."
    )

def test_1_3_describe_lists_objects_sentence(game_data):
    """
    1.3 (continued) If the room has objects, it should include:
      "You see training dummy and wooden sword."
    """
    room = "Recruit Training Camp"
    desc = adventure.describe(game_data, room)
    assert "You see training dummy and wooden sword." in desc, (
        f"In '{room}' you should see the text \"You see training dummy and wooden sword.\""
    )

def test_1_3_describe_handles_no_objects(game_data):
    """
    1.3 (continued) If the room has no objects, 'You see' should not appear
    """
    room = "Wilderness Outside Wall"
    desc = adventure.describe(game_data, room)
    assert "You see" not in desc, f"In '{room}' there should not be \"You see ...\" text, but it appeared."


# -------------- 1.4 Final sanity check START != FINISH (1/1) ---------------

def test_1_4_start_finish_not_same_again():
    """
    1.4 Final sanity check: Confirm again that START != FINISH
    """
    assert adventure.START != adventure.FINISH, "Double check: START cannot equal FINISH."

