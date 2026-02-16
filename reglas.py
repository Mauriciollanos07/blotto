import random

def get_ai_allocations(num_battlefields, rule):
    """Function to generate AI allocations based on the selected rule. Returns a list of AI allocations for each battlefield.
        Args:
            num_battlefields (int): The number of battlefields in the game.
            rule (str): The selected rule for generating AI allocations.
        Returns:
            list: A list of AI allocations for each battlefield.
    """
    allocs = []
    t_resources = 100

    # if to control that no value is repeated in final list
    if rule == "RULES 2":
        while len(allocs) < num_battlefields:
            alloc = random.randint(0, t_resources // num_battlefields)
            if alloc not in allocs:
                allocs.append(alloc)

        return allocs

    # Make sure random number is at least 1 to avoid leaving any battlefield empty
    elif rule == "RULES 3":
        return [random.randint(1, t_resources // num_battlefields) for _ in range(num_battlefields)]
    
    # Generic ai alloc
    else:
        return  [random.randint(0, t_resources // num_battlefields) for _ in range(num_battlefields)]

def validate_player_allocs(player_allocs, rule, TOTAL_RESOURCES):
    """Function to validate player allocations based on the selected rule. Returns a dictionary with a message and a boolean indicating if the allocations are valid.
        Args:
            player_allocs (list): List of player allocations for each battlefield.
            rule (str): The selected rule for validation.
            TOTAL_RESOURCES (int): The total resources available for allocation.
        Returns:
            dict: A dictionary containing a message and a boolean indicating if the allocations are valid.
    """
    validation = {"Message": "", "Valid": True}
    message = ""

    # Every rule set includes this validation, so it is outside of the if statements
    if sum(player_allocs) > TOTAL_RESOURCES:
        message += f"{message} PLAYER EXCEEDED TOTAL RESOURCES! (NOT ALLOWED IN {rule})"
        validation["Message"] = f"{message}"
        validation["Valid"] = False

    # Rules 2 indicates that no value can be repeated in the player's allocations, so we check if the length of the list is equal to the length of the set of the list (which removes duplicates). If they are not equal, it means there are repeated values.
    if rule == "RULES 2":
        if len(player_allocs) != len(set(player_allocs)):
            message += f"{message} PLAYER HAS REPEATED VALUES (NOT ALLOWED IN {rule})"
            validation["Message"] = f"{message}"
            validation["Valid"] = False

    # In rules 3, no battlefield can be left empty, so we check if there is a 0 in the player's allocations. If there is, it means at least one battlefield is left empty.
    elif rule == "RULES 3":
        if 0 in player_allocs:
            message += f"{message} PLAYER HAS LEFT AT LEAST ONE BATTLEFIELD EMPTY (NOT ALLOWED IN {rule})"
            validation["Message"] = f"{message}"
            validation["Valid"] = False


    return validation
