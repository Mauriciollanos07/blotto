import numpy as np
import random

def get_ai_allocations(num_battlefields, rule):
    # Generate ai allocations that follow the rules selected
    print("-------------------------------")
    print("calling get_ai_allocations cuntion")
    print("-------------------------------")
    # create empty list for return value and resources variable to control how many ai has left
    allocs = []
    t_resources = 100

    print("-------------------------------")
    print(f"will execute {rule} conditional")
    print("-------------------------------")
    # if to control that no value is repeated in final list
    if rule == "RULES 2":
        for b in range(num_battlefields):
            allocs.append(random.choice([i for i in range(t_resources) if i not in allocs]))
        print(f"--------------------------------------")
        print(f"first allocs config is: {allocs}")

        while_i = 0

        while sum(allocs) > 100:
            while_i = while_i + 1
            print(f"--------------------------------------")
            print(f"while executed because sum(allocs) is: {sum(allocs)}")
            print(f"interation is: {while_i}")
            for a in range(len(allocs)):
                print(f"a is: {a}")
                print(f"alloc[{a}] before extraction is: {allocs[a]}")
                if allocs[a] > 10 and (allocs[a] - 10) not in allocs:
                    allocs[a] = allocs[a] - 10
                elif allocs[a] <= 10  and allocs[a] > 0 and(allocs[a] - 1) not in allocs:
                    allocs[a] = allocs[a] - 1
                elif allocs[a] <= 0:
                    allocs[a] = random.choice([i for i in range(t_resources) if i not in allocs])

                print(f"alloc after extraction is: {allocs[a]}")

            print(f"--------------------------------------")
            print(f"new allocs config is: {allocs}")
        print(f"--------------------------------------")
        print(f"while didn't axecute because sum(allocs) is: {sum(allocs)}")
        print(f"--------------------------------------")

        return allocs

    # Make sure random number is at least 1 to avoid leaving any battlefield empty
    elif rule == "RULES 4":
        return [random.randint(1, t_resources // num_battlefields) for _ in range(num_battlefields)]
    
    # Generic ai alloc
    else:
        return  [random.randint(0, t_resources // num_battlefields) for _ in range(num_battlefields)]

def validate_player_allocs(player_allocs, regla, TOTAL_RESOURCES):
    # Check the values submitted by the player to see if they follow the rules selected
    # Return a dictionary with True ot False keys, and an ampty string with True or a string describing erro when false
    validation = {"Message": "", "Valid": True}
    message = ""
    print(f"message before update")
    print(f"validation dict before update is: {validation}")

    if sum(player_allocs) > TOTAL_RESOURCES:
        print(f"Total resources exceeded first conditional executing")
        message = f"{message} PLAYER EXCEEDED TOTAL RESOURCES!"
        print(f"message after update is: {message}")
        validation["Message"] = f"{message}"
        validation["Valid"] = False
        print(f"validation dict after update is: {validation}")

    if regla == "RULES 2":
        compare = player_allocs.copy()
        print(f"player allocs is: {player_allocs} and compare is: {compare}")
        for b in range(len(compare)):
            comp_alloc = compare[-1]
            print(f"compare value is: {comp_alloc}")
            compare.remove(compare[-1])
            print(f"player allocs is: {player_allocs} and compare is: {compare}")
            if comp_alloc in compare:
                print(f"Rules 2 and repeated alloc found so...")
                message = f"{message} PLAYER REPEATED VALUES IN DIFFERENT BATTLEFIELDS!"
                print(f"message after update is: {message}")
                validation["Message"] = f"{message}"
                validation["Valid"] = False
                print(f"validation dict after update is: {validation}")
                break
            else:
                print(f"value not repeated and continue loop")
    elif regla == "RULES 3":
        for alloc in player_allocs:
            if alloc < 1:
                print(f"Rules 3 and empty field found so...")
                message = f"{message} PLAYER HAS LEFT AT LEAST ONE BATTLEFIELD EMPTY"
                print(f"message after update is: {message}")
                validation["Message"] = f"{message}"
                validation["Valid"] = False
                print(f"validation dict after update is: {validation}")
                break

    return validation
