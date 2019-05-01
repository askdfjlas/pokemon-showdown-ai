# Get attributes given game state objects (current mon and poke lists)
from pokemon import *

# Move/Pokemon Types
TYPES = {"Normal": 0, "Fire": 1, "Water": 2, "Electric": 3, "Grass": 4, "Ice": 5, "Fighting": 6,
         "Poison": 7, "Ground": 8, "Flying": 9, "Psychic": 10, "Bug": 11, "Rock": 12, "Ghost": 13,
         "Dragon": 14, "Dark": 15, "Steel": 16, "Fairy": 17}

# Type effectiveness matrix
TYPE_EFFECT = [[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0.5, 0, 1, 1, 0.5, 1],
               [1, 0.5, 0.5, 1, 2, 2, 1, 1, 1, 1, 1, 2, 0.5, 1, 0.5, 1, 2, 1],
               [1, 2, 0.5, 1, 0.5, 1, 1, 1, 2, 1, 1, 1, 2, 1, 0.5, 1, 1, 1],
               [1, 1, 2, 0.5, 0.5, 1, 1, 1, 0, 2, 1, 1, 1, 1, 0.5, 1, 1, 1],
               [1, 0.5, 2, 1, 0.5, 1, 1, 0.5, 2, 0.5, 1, 0.5, 2, 1, 0.5, 1, 0.5, 1],
               [1, 0.5, 0.5, 1, 2, 0.5, 1, 1, 2, 2, 1, 1, 1, 1, 2, 1, 0.5, 1],
               [2, 1, 1, 1, 1, 2, 1, 0.5, 1, 0.5, 0.5, 0.5, 2, 0, 1, 2, 2, 0.5],
               [1, 1, 1, 1, 2, 1, 1, 0.5, 0.5, 1, 1, 1, 0.5, 0.5, 1, 1, 0, 2],
               [1, 2, 1, 2, 0.5, 1, 1, 2, 1, 0, 1, 0.5, 2, 1, 1, 1, 2, 1],
               [1, 1, 1, 0.5, 2, 1, 2, 1, 1, 1, 1, 2, 0.5, 1, 1, 1, 0.5, 1],
               [1, 1, 1, 1, 1, 1, 2, 2, 1, 1, 0.5, 1, 1, 1, 1, 0, 0.5, 1],
               [1, 0.5, 1, 1, 2, 1, 0.5, 0.5, 1, 0.5, 2, 1, 1, 0.5, 1, 2, 0.5, 0.5],
               [1, 2, 1, 1, 1, 2, 0.5, 1, 0.5, 2, 1, 2, 1, 1, 1, 1, 0.5, 1],
               [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 1, 1, 2, 1, 0.5, 1, 1],
               [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 1, 0.5, 0],
               [1, 1, 1, 1, 1, 1, 0.5, 1, 1, 1, 2, 1, 1, 2, 1, 0.5, 1, 0.5],
               [1, 0.5, 0.5, 0.5, 1, 2, 1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 0.5, 2],
               [1, 0.5, 1, 1, 1, 1, 2, 0.5, 1, 1, 1, 1, 1, 1, 2, 2, 0.5, 1]]


# Damage calculator, poke1 = attacking poke, poke2 = defending
def damage_calc(poke1, poke2, move, move_dict):
    # These all do (user's level) damage, which is almost always 100
    if move == "Seismic Toss" or move == "Night Shade":
        return 100

    obj = move_dict[move]
    move_obj = obj[0]

    # If the category isn't offensive, the move won't do any damage
    if obj[-1] not in ["Pure Offensive", "Offensive Cripple"]:
        return 0

    modifier = 1 # Initially set modifier to 1
    modifier *= 1.5 if (poke1.type1 == move_obj.type or poke1.type2 == move_obj.type) else 1  # STAB
    modifier *= TYPE_EFFECT[TYPES[move_obj.type]][TYPES[poke2.type1]] * \
                (TYPE_EFFECT[TYPES[move_obj.type]][TYPES[poke2.type2]] if poke2.type2 is not None else 1)

    if move_obj.category == "Physical":
        modifier *= 0.5 if poke1.status == Status.Burn else 1  # Halves attack if burned
        attack = poke1.attack*STAT_BOOSTS[poke1.boosts[STAT_NUMBERS["atk"]]]
        defense = poke2.defense*STAT_BOOSTS[poke2.boosts[STAT_NUMBERS["def"]]]

        return math.ceil(((42*move_obj.bp*attack/defense)/50 + 2) * modifier)
    else:
        spa = poke1.sp_attack * STAT_BOOSTS[poke1.boosts[STAT_NUMBERS["spa"]]]
        spd = poke2.sp_defense * STAT_BOOSTS[poke2.boosts[STAT_NUMBERS["spd"]]]

        return math.ceil(((42*move_obj.bp*spa/spd)/50 + 2) * modifier)


# Main function to manage game state
def write_game_state(current_mon, p1_poke, p2_poke, move_dict):
    print("\nP2 Move Analysis!")
    for move in p2_poke[current_mon[1]].moves:
        dmg = damage_calc(p2_poke[current_mon[1]], p1_poke[current_mon[0]], move, move_dict)
        print("Move {}: {}".format(move, dmg))

    print()
