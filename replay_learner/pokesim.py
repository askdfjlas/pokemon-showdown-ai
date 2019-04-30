from pokemon import *
from battle_strings import *
import pre_search
import tsv_to_2d

POKE_DATA_F = "../data/pokemon/COOKED_POKEMON.tsv"
POKE_CLASSES_F = "../data/pokemon/CLASSIFIED_POKEMON.tsv"

MOVE_DATA_F = "../data/moves/RAW_MOVES.tsv"
MOVE_CLASSES_F = "../data/moves/CLASSIFIED_MOVES.tsv"

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
        poke = poke_data_list[i]
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
        move = move_data_list[i]
        name = move[0]
        move_obj = Move(move[:MOVE_END_RANGE])  # Create move object
        label = move_classes_list[i][-1]

        move_dict[name] = [move_obj, label]

    return move_dict


# Main function
def main():
    poke_dict = load_pokemon()
    move_dict = load_moves()


if __name__ == "__main__":
    main()
