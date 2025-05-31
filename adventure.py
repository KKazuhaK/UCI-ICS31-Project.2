import json
import random
import os

# Constants for game locations
FINISH = "Eren's Basement"  # The end goal of the game
START = "Recruit Training Camp"  # Default starting location

SEPARATOR = "=" * 50  # Formatting separator for display
PICKABLE_TYPES = {"special", "equipment", "weapon", "tool", "consumable", "document"}  # Types of items player can collect

def main():
    # Load game world data from JSON file
    with open('custom.json') as f:
        original_data = json.load(f)
    
    # Get player username
    username = input("Please enter your username: ")
    
    # Initialize player state
    inventory = []
    game_state = {}
    data = original_data
    is_new_user = True
    
    # Load saved game data if available
    save_data = load_save_data()
    
    # Check if returning player who hasn't won yet
    if username in save_data and not save_data[username].get("game_state", {}).get("won", False):
        is_new_user = False
        current_location = save_data[username]["location"]
        inventory = save_data[username].get("inventory", [])
        game_state = save_data[username].get("game_state", {})
        
        # Restore picked up objects state
        if "picked_up_objects" in save_data[username]:
            for loc, objects in save_data[username]["picked_up_objects"].items():
                if loc in data:
                    data[loc]["objects"] = objects

        # Restore custom paths (like secret passages)
        if "custom_paths" in save_data[username]:
            for loc, paths in save_data[username]["custom_paths"].items():
                if loc in data:
                    for direction, destination in paths.items():
                        data[loc]["moves"][direction] = destination
        
        # Display welcome back message
        print("\n" + SEPARATOR)
        print("SAVE LOADED")
        print(SEPARATOR)
        print(f"Welcome back, {username}! Resuming from {current_location} with {len(inventory)} items.")
    else:
        # Either new player or player who has won - start at random location
        current_location = random.choice([loc for loc in data.keys() if loc != FINISH])
        
        if username in save_data:
            # Player has won before, start at new random location
            is_new_user = False
            print("\n" + SEPARATOR)
            print("SAVE LOADED")
            print(SEPARATOR)
            print(f"Welcome back, {username}! Since you've already discovered the secrets, you'll start at a new location.")
        else:
            # Brand new player
            print(f"Welcome, new explorer {username}! Starting at {current_location}.")
    
    # Start the game with current state
    play_game(data, username, current_location, inventory, game_state, is_new_user)

def move_user(data, current, move):
    # Handles movement between rooms
    if move in data[current]['moves']:
        return data[current]['moves'][move]
    return current

def describe(data, current):
    # Generates description text for the current location
    description = data[current]['text'] + "\n"
    
    # Add object descriptions if present
    if 'objects' in data[current] and data[current]['objects']:
        names = [obj["name"] for obj in data[current]['objects']]
        
        if len(names) == 1:
            description += f"You see {names[0]}."
        else:
            # Avoid change orginal list
            items_copy = names.copy()
            last_item = items_copy.pop()
            description += f"You see {', '.join(items_copy)} and {last_item}."
        
        # Add hint for pickup if pickable items exist
        has_pickable = any(obj["type"] in PICKABLE_TYPES for obj in data[current]['objects'])
        if has_pickable:
            description += "\n(You can type 'pickup' to collect items)"
    
    # Add available movement options
    description += "\n\nYour options are:"
    for move, destination in data[current]['moves'].items():
        description += f"\n'{move}' to go to {destination}"
    
    return description

def can_access(data, current, direction, inventory):
    # Checks if player can access a direction based on inventory requirements
    if current == "Wall Maria Watchtower" and direction == "north":
        if "ODM gear" not in inventory:
            return False, "You need ODM gear to venture outside the walls!"
    
    
    # Check if player can climb from the forest to the wall
    if current == "Titan Forest" and direction == "climb":
        if "ODM gear" not in inventory:
            return False, "You need ODM gear to climb up to the Wall!"
    
    # Check if player can use the secret tunnel between forest and command center
    if current == "Titan Forest" and direction == "tunnel":
        if "expedition map" not in inventory:
            return False, "You need an expedition map to navigate the secret tunnel!"
    
    return True, ""

def display_location(data, current):
    # Helper function to display current location information
    print(f"Location: {current}")
    print(describe(data, current))

def play_game(data, username, current, inventory=None, game_state=None, is_new_user=False):
    # Main game loop
    print('\nWelcome to the Attack on Titan Adventure Game:')
    print('Your mission: Explore the world, find Grisha\'s journals, and discover the truth in Eren\'s Basement.')
    
    # First help section for new users
    if is_new_user:
        print("\n" + SEPARATOR)
        print("HOW TO PLAY")
        print(SEPARATOR)
        print("Commands:")
        print("  [direction] - Move in that direction (e.g., north, south)")
        print("  special directions - Some locations have special moves (climb, tunnel)")
        print("  pickup - Pick up all items in the room")
        print("  look - Examine your current location again")
        print("  inventory - Check your items")
        print("  help - Show this help information")
        print("  exit/quit - Exit the game")
    else:
        print('Type "help" for available commands.')
    
    print()
    
    # Initialize inventory and game state if not provided
    if inventory is None:
        inventory = []
    
    if game_state is None:
        game_state = {}
        
    game_over = False
    
    # Display initial location
    print("\n" + SEPARATOR)
    print("STARTING LOCATION")
    print(SEPARATOR)
    display_location(data, current)
    
    # Main game loop
    while not game_over:
        # Check victory condition
        has_won = current == FINISH and "Grisha's journals" in inventory

        if has_won:
            print(SEPARATOR)
            print("YOU WON AND FIND THE TRUTH!")
            print(SEPARATOR)
            print("Congratulations! You've discovered the secrets of the titans and collected the crucial journals!")
            print("You now understand the truth about the world beyond the walls!")
            
            game_state["won"] = True
            save_game(username, current, inventory, game_state, data)
            game_over = True
            continue
        elif current == FINISH:
            # Player reached the basement but doesn't have the journals
            print("\n" + SEPARATOR)
            print("PARTIAL DISCOVERY")
            print(SEPARATOR)
            print("You've found Eren's Basement, but without Grisha's journals, the secrets remain hidden.")
            print("Keep exploring to find the full truth!")
        
        # Get available moves from current location
        available_moves = list(data[current]['moves'].keys())
        
        # Get user command
        command = input("\nWhat would you like to do? ").lower().split()
        
        print("\n" + SEPARATOR)

        # Handle empty command
        if not command:
            print("LOCATION UPDATE")
            print(SEPARATOR)
            display_location(data, current)
            continue
        
        # Handle movement commands
        if len(command) == 1 and command[0] in available_moves:
            direction = command[0]
            
            print(f"MOVING: {direction.upper()}")
            print(SEPARATOR)
            
            # Check if player can access this direction
            can_move, message = can_access(data, current, direction, inventory)
            if not can_move:
                print(message)
                continue
            
            # Move to new location
            new_location = move_user(data, current, direction)
            current = new_location
            
            save_game(username, current, inventory, game_state, data)  # 添加这行
            display_location(data, current)
        
        # Handle invalid directions
        elif len(command) == 1 and command[0] in ['north', 'south', 'east', 'west', 'up', 'down', 'inside', 'outside']:
            print("INVALID DIRECTION")
            print(SEPARATOR)
            print(f"You can't go {command[0]} from here.")
            display_location(data, current)
            
        # Handle exit commands
        elif command[0] in ['exit', 'quit']:
            print("GAME ENDING")
            print(SEPARATOR)
            print("Thanks for playing!")
            game_over = True
            
        # Handle help command
        elif command[0] == 'help':
            print("HELP INFORMATION")
            print(SEPARATOR)
            print("Commands:")
            print("  [direction] - Move in that direction (e.g., north, south)")
            print("  special directions - Some locations have special moves (climb, tunnel)")
            print("  pickup - Pick up all items in the room")
            print("  look - Examine your current location again")
            print("  inventory - Check your items")
            print("  help - Show this help information")
            print("  exit/quit - Exit the game")
            
            display_location(data, current)
            
        # Handle inventory command
        elif command[0] == 'inventory':
            print("INVENTORY CONTENTS")
            print(SEPARATOR)
            if inventory:
                print("You are carrying:")
                for item in inventory:
                    print(f"- {item}")
            else:
                print("Your inventory is empty.")
            
            display_location(data, current)
            
        # Handle pickup command
        elif command[0] == 'pickup':
            if 'objects' in data[current] and data[current]['objects']:
                print("ITEM COLLECTION")
                print(SEPARATOR)
                
                # Find first pickable item
                picked_up = False
                for i, obj in enumerate(data[current]['objects']):
                    if obj['type'] in PICKABLE_TYPES:
                        # Pick up only this one item
                        item_name = obj['name']
                        inventory.append(item_name)
                        data[current]['objects'].pop(i)
                        picked_up = True
                        
                        print(f"You picked up: {item_name}")
                        
                        # Special item interactions
                        if item_name.lower() == "odm gear":
                            print("With this gear, you can now travel beyond the walls!")
                        elif item_name.lower() == "thunder spear":
                            print("This powerful weapon will help you fight titans!")
                        elif item_name.lower() == "mysterious vial":
                            print("You feel a strange power emanating from this vial...")
                        elif item_name.lower() == "expedition map":
                            print("This detailed map will help you navigate hidden paths!")
                        
                        save_game(username, current, inventory, game_state, data)
                        break
                
                if not picked_up:
                    print("There are no special items to pick up here.")
            else:
                print("EMPTY ROOM")
                print(SEPARATOR)
                print("There is nothing here to pick up.")
    
            display_location(data, current)
            
        # Handle look command
        elif command[0] == 'look':
            print("LOCATION DETAILS")
            print(SEPARATOR)
            display_location(data, current)
            
        # Handle invalid commands
        else:
            print("INVALID COMMAND")
            print(SEPARATOR)
            print(f"I don't understand '{' '.join(command)}'. Type 'help' for assistance.")
            
            display_location(data, current)
    
def save_game(username, location, inventory, game_state=None, world_data=None):
    # Save game state to file
    save_data = load_save_data()
    
    if game_state is None:
        game_state = {}
    
    # Track objects and custom paths for saving
    picked_up_objects = {}
    custom_paths = {}
    
    if world_data:
        for location_name, location_data in world_data.items():
            if 'objects' in location_data:
                picked_up_objects[location_name] = location_data['objects']
            if 'moves' in location_data:
                custom_paths[location_name] = location_data['moves']
    
    # Create save data structure
    save_data[username] = {
        "location": location,
        "inventory": inventory,
        "game_state": game_state,
        "picked_up_objects": picked_up_objects,
        "custom_paths": custom_paths
    }
    
    # Write save data to file
    write_save_data(save_data)

def load_save_data():
    if not os.path.exists('save.json') or os.path.getsize('save.json') == 0:
        return {}
    with open('save.json', 'r') as f:
        return json.load(f)

def write_save_data(save_data):
    with open('save.json', 'w') as f:
        json.dump(save_data, f, indent=2, sort_keys=True)


if __name__ == '__main__':
    main()