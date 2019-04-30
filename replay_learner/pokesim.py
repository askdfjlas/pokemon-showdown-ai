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


# Simulate the battle! Slowly append entries to the final training set
def simulate(battle_string, poke_dict, move_dict):
    current, lines, p1_poke, p2_poke = pre_search.get_pre_battle(battle_string)  # Get pre-battle info
    pre_search.get_during_battle(current, lines, p1_poke, p2_poke)  # Populate with known info during the battle
    populate_pokes(p1_poke, p2_poke, poke_dict)  # Compute unknown stats from Smogon EVs
    print(p1_poke, p2_poke)


# Main function
def main():
    poke_dict = load_pokemon()
    move_dict = load_moves()

    for battle_string in get_battle_strings():
        simulate(battle_string, poke_dict, move_dict)
        break


if __name__ == "__main__":
    main()
