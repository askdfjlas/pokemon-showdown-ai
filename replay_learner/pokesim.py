from pokemon import *
from battle_strings import *
import pre_search
import tsv_to_2d
import move_tree

POKE_DATA_F = "../data/pokemon/COOKED_POKEMON.tsv"
POKE_CLASSES_F = "../data/pokemon/CLASSIFIED_POKEMON.tsv"

MOVE_DATA_F = "../data/moves/RAW_MOVES.tsv"
MOVE_CLASSES_F = "../data/moves/CLASSIFIED_MOVES.tsv"

# Ranges of attributes from tsv files
TYPES_RANGE = (1, 3)
STATS_RANGE = (3, 9)
MOVES_RANGE = (9, 13)
EV_RANGE = (13, 19)

MOVE_END_RANGE = 4


# Load a dictionary of pokemon with their classes, EVs, and base stats, etc.
# Format: (name => [template pokemon, EV investment, class])
def load_pokemon():
    poke_dict = {}

    poke_data_list = tsv_to_2d.get_list(POKE_DATA_F)
    poke_classes_list = tsv_to_2d.get_list(POKE_CLASSES_F)

    for i in range(len(poke_data_list)):
        poke = move_tree.convert_numeric(poke_data_list[i])  # Make sure attributes like EVs are ints
        name = poke[0]
        template_mon = Pokemon()  # Use "template" Pokemon to later copy and calculate stats

        template_mon.set_name(name)  # Set name
        template_mon.set_types(poke[TYPES_RANGE[0]: TYPES_RANGE[1]])  # Set types
        template_mon.set_stats(poke[STATS_RANGE[0]: STATS_RANGE[1]])  # Set stats

        for move in poke[MOVES_RANGE[0]: MOVES_RANGE[1]]:  # Set moves
            template_mon.append_move(move)

        ev_investment = EV(poke[EV_RANGE[0]: EV_RANGE[1]])  # Record EV investment
        category = poke_classes_list[i][-1]  # Category of Pokemon

        poke_dict[name] = [template_mon, ev_investment, category]

    return poke_dict


# Load a dictionary of moves with their classes, BPs, types, etc.
# Format: (name => [move object, class])
def load_moves():
    move_dict = {}

    move_data_list = tsv_to_2d.get_list(MOVE_DATA_F)
    move_classes_list = tsv_to_2d.get_list(MOVE_CLASSES_F)

    for i in range(len(move_data_list)):
        move = move_tree.convert_numeric(move_data_list[i])  # Make sure attributes like bp are ints
        name = move[0]
        move_obj = Move(move[:MOVE_END_RANGE])  # Create move object
        label = move_classes_list[i][-1]

        move_dict[name] = [move_obj, label]

    return move_dict


# Populate poke stats for p1 and p2
def populate_pokes(p1_poke, p2_poke, poke_dict):
    for poke in list(p1_poke.values()) + list(p2_poke.values()):
        template, ev_object, category = poke_dict[poke.name]
        poke.populate(template, ev_object)


# Get pokes which each of the two players start out with
def get_starting_mon(curr, lines):
    starting = []

    while "|turn|1" not in lines[curr]:
        curr_line = lines[curr]
        arr = curr_line.split('|')[1:]

        # Someone sends out their poke
        if arr[0] == "switch":
            sdt = pre_search.get_switch(curr_line)
            starting.append(sdt[1])  # Order: (P1 mon, P2 mon)

        curr += 1

    return curr, starting


# Get P1/P2, damage dealt, and a [from] effect if possible
def get_damage(line):
    parity = 0 if "p1" in line.split('|')[2][:2] else 1
    arr = line.split('|')[1:]
    if len(arr) > 3:
        cause = arr[3][7:]
    else:
        cause = None

    if arr[2] == "0 fnt":
        return [parity, -1, cause]
    return [parity, int(arr[2].split('\\')[0]), cause]


# Simulate the battle! Slowly append entries to the final training set
def simulate(battle_string, poke_dict, move_dict):
    current, lines, p1_poke, p2_poke = pre_search.get_pre_battle(battle_string)  # Get pre-battle info
    pre_search.get_during_battle(current, lines, p1_poke, p2_poke)  # Populate with known info during the battle
    populate_pokes(p1_poke, p2_poke, poke_dict)  # Compute unknown stats from Smogon EVs

    # All pre-battle data computed, now on to the actual turns
    turn = 0
    current, current_mon = get_starting_mon(current, lines)  # Get pokes that the players first send out
    print("P1 sends out {}!\nP2 sends out {}!".format(current_mon[0], current_mon[1]))

    # Iterate until end of battle
    while len(lines[current]) != 5 and lines[current][:5] != "|win|":
        curr_line = lines[current]
        arr = curr_line.split('|')[1:]

        # Update turn count
        if arr[0] == "turn":
            turn += 1
            print("\n------ Turn {} ------\n".format(str(turn)))

        # Player switches
        if arr[0] == "switch":
            sdt = pre_search.get_switch(curr_line)
            poke_name = current_mon[sdt[0]]
            poke_object = [p1_poke, p2_poke][sdt[0]][poke_name]
            print("P{} swaps {} out, and sends out {}.".format(sdt[0] + 1, poke_name, sdt[1]))
            current_mon[sdt[0]] = sdt[1]
            poke_object.reset_boosts()  # Reset stat boosts

        # Player moves
        if arr[0] == "move":
            mdt = pre_search.get_move_ability(curr_line)
            print("P{}'s {} uses {}.".format(mdt[0] + 1, current_mon[mdt[0]], mdt[1]))

        # Poke takes damage
        if arr[0] == "-damage":
            ddt = get_damage(curr_line)
            poke_name = current_mon[ddt[0]]
            poke_object = [p1_poke, p2_poke][ddt[0]][poke_name]
            new_hp = math.floor(ddt[1]/100*poke_object.maxHP)
            d_taken = poke_object.currHP - new_hp

            if ddt[1] > 0:  # If the poke is still alive
                tp = "P{}'s {} takes {} points of damage {}and is now at {}/{} HP."
                print(tp.format(ddt[0] + 1, current_mon[ddt[0]],
                      d_taken, "from {} ".format(ddt[2]) if ddt[2] is not None else "",
                      new_hp, poke_object.maxHP))
            else:  # If it has fainted
                tp = "P{}'s {} takes {} points of damage {}and has now fainted."
                print(tp.format(ddt[0] + 1, current_mon[ddt[0]],
                                d_taken, "from {} ".format(ddt[2]) if ddt[2] is not None else ""))

            poke_object.update_hp(new_hp)  # Update HP

        current += 1


# Main function
def main():
    poke_dict = load_pokemon()
    move_dict = load_moves()

    for battle_string in get_battle_strings():
        simulate(battle_string, poke_dict, move_dict)
        break


if __name__ == "__main__":
    main()
