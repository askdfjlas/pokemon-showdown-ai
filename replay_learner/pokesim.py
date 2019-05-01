# Simulate the entire battle through logs and create the training set!
from battle_strings import *
from get_attributes import *
import pre_search
import tsv_to_2d as tsv
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

    poke_data_list = tsv.get_list(POKE_DATA_F)
    poke_classes_list = tsv.get_list(POKE_CLASSES_F)

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

    move_data_list = tsv.get_list(MOVE_DATA_F)
    move_classes_list = tsv.get_list(MOVE_CLASSES_F)

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

    while len(starting) < 2:  # While both poke have not been loaded yet
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
    parity = pre_search.get_parity(line)
    arr = line.split('|')[1:]
    if len(arr) > 3:
        cause = arr[3][7:]
    else:
        cause = None

    if arr[2] == "0 fnt":
        return [parity, -1, cause]

    # This replay format is idiotic
    return [parity, int(arr[2].split('\\')[0]), cause, int(arr[2].split()[0].split('/')[1]) > 100]


# Get P1/P2, amount healed, and a [from] effect if possible
def get_heal(line):
    parity = pre_search.get_parity(line)
    arr = line.split('|')[1:]
    if len(arr) > 3:
        cause = arr[3][7:]
    else:
        cause = None

    # This replay format is idiotic
    return [parity, int(arr[2].split('\\')[0]), cause, int(arr[2].split()[0].split('/')[1]) > 100]


# Get stat boosts
def get_boost(line):
    parity = pre_search.get_parity(line)
    arr = line.split('|')[1:]
    return [parity, arr[-2], arr[-1]]


# Get statuses (burn, toxic, etc.)
def get_status(line):
    parity = pre_search.get_parity(line)
    return [parity, line.split('|')[3]]


# Cure a status
def get_cure_status(line):
    print(line)
    parity = pre_search.get_parity(line)
    return [parity, line.split('|')[2].split()[-1]]


# Simulate the battle! Slowly append entries to the final training set
def simulate(battle_string, poke_dict, move_dict):
    current, lines, p1_poke, p2_poke = pre_search.get_pre_battle(battle_string)  # Get pre-battle info
    pre_search.get_during_battle(current, lines, p1_poke, p2_poke)  # Populate with known info during the battle
    populate_pokes(p1_poke, p2_poke, poke_dict)  # Compute unknown stats from Smogon EVs

    # All pre-battle data computed, now on to the actual turns
    turn = 0
    current, current_mon = get_starting_mon(current, lines)  # Get pokes that the players first send out
    print("P1 sends out {}!\nP2 sends out {}!".format(current_mon[0], current_mon[1]))

    forced_swaps = [False, False]  # Forced swaps occur when a user must decide their next Poke to send out
    # Iterate until end of battle
    while len(lines[current]) != 5 and lines[current][:5] != "|win|":
        curr_line = lines[current]
        arr = curr_line.split('|')[1:]

        # Update turn count
        if arr[0] == "turn":
            forced_swaps = [False, False]  # Reset force swaps
            turn += 1
            print("\n------ Turn {} ------\n".format(str(turn)))
            write_game_state(current_mon, p1_poke, p2_poke, move_dict)

        # Player switches or gets a poke dragged in (the latter case they have no control over)
        if arr[0] in ["switch", "drag"]:
            parity = arr[0] == "switch"
            sdt = pre_search.get_switch(curr_line)
            poke_name = current_mon[sdt[0]]
            poke_object = [p1_poke, p2_poke][sdt[0]][poke_name]
            if forced_swaps[sdt[0]]:
                print("Forced swap: ", end="")
            print("P{} {} {} out, and sends out {}.".format(sdt[0] + 1, "swaps" if parity else "drags",
                                                            poke_name, sdt[1]))
            current_mon[sdt[0]] = sdt[1]
            poke_object.reset_boosts()  # Reset stat boosts

        # Player moves
        if arr[0] == "move":
            mdt = pre_search.get_move_ability(curr_line)
            print("P{}'s {} uses {}.".format(mdt[0] + 1, current_mon[mdt[0]], mdt[1]))

            # U-turn and Volt Switch are the only 2 moves in the game which create forced swaps
            if mdt[1] in ["U-turn", "Volt Switch"]:
                forced_swaps[mdt[0]] = True

        # Poke takes damage
        if arr[0] == "-damage":
            ddt = get_damage(curr_line)
            poke_name = current_mon[ddt[0]]
            poke_object = [p1_poke, p2_poke][ddt[0]][poke_name]

            # Calculate HP depending on format of replay
            new_hp = ddt[1] if ddt[-1] else math.floor(ddt[1]/100*poke_object.maxHP)
            d_taken = poke_object.currHP - new_hp

            if ddt[1] > 0:  # If the poke is still alive
                tp = "P{}'s {} takes {} points of damage {}and is now at {}/{} HP."
                print(tp.format(ddt[0] + 1, poke_name,
                      d_taken, "from {} ".format(ddt[2]) if ddt[2] is not None else "",
                      new_hp, poke_object.maxHP))
            else:  # If it has fainted
                tp = "P{}'s {} takes {} points of damage {}and has now fainted."
                print(tp.format(ddt[0] + 1, poke_name,
                      d_taken, "from {} ".format(ddt[2]) if ddt[2] is not None else ""))

                forced_swaps[ddt[0]] = True  # Faints create forced swaps

            poke_object.update_hp(new_hp)  # Update HP

        # Poke gets healed
        if arr[0] == "-heal":
            hdt = get_heal(curr_line)
            poke_name = current_mon[hdt[0]]
            poke_object = [p1_poke, p2_poke][hdt[0]][poke_name]

            # Calculate HP depending on format of replay
            new_hp = hdt[1] if hdt[-1] else math.floor(hdt[1] / 100 * poke_object.maxHP)
            d_healed = new_hp - poke_object.currHP

            tp = "P{}'s {} heals {} points of damage {}and is now at {}/{} HP."
            print(tp.format(hdt[0] + 1, poke_name,
                  d_healed, "from {} ".format(hdt[2]) if hdt[2] is not None else "",
                  new_hp, poke_object.maxHP))

            poke_object.update_hp(new_hp)  # Update HP

        # Poke gets a stat boost
        if arr[0] == "-boost" or arr[0] == "-unboost":
            parity = arr[0] == "-boost"
            bdt = get_boost(curr_line)
            poke_name = current_mon[bdt[0]]
            poke_object = [p1_poke, p2_poke][bdt[0]][poke_name]
            tp = "P{}'s {}'s {} gets {} by {} stage(s)."
            print(tp.format(bdt[0] + 1, poke_name, bdt[1],
                            "raised" if parity else "lowered",
                            bdt[2]))

            poke_object.boost(bdt[1], int(bdt[2]) if parity else -int(bdt[2]))  # Boost stat of poke object

        # Poke gets a status
        if arr[0] == "-status":
            sdt = get_status(curr_line)
            poke_name = current_mon[sdt[0]]
            poke_object = [p1_poke, p2_poke][sdt[0]][poke_name]
            tp = "P{}'s {} is inflicted with {}."
            print(tp.format(sdt[0] + 1, poke_name, sdt[1]))

            poke_object.set_status(sdt[1])  # Set status

        # Poke gets its status cured
        if arr[0] == "-curestatus":
            cdt = get_cure_status(curr_line)
            poke_name = cdt[1]

            # It's impossible to know if poke_name is a nickname for curestatus, they fixed it later I guess...
            if poke_name in [p1_poke, p2_poke][cdt[0]]:
                poke_object = [p1_poke, p2_poke][cdt[0]][poke_name]
                tp = "P{}'s {} has its status cured."
                print(tp.format(cdt[0] + 1, poke_name))

                poke_object.cure_status()  # Cure status

        # Reset all stats
        if arr[0] == "-clearallboost":
            print("All stats have been reset!")
            p1_poke[current_mon[0]].reset_boosts()
            p2_poke[current_mon[1]].reset_boosts()

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
