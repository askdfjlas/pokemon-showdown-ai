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
# Slightly inaccurate by a few points due to the ceiling and lack of integer truncation, although that doesn't matter
def damage_calc(poke1, poke2, move, move_dict):
    # These all do (user's level) damage, which is almost always 100
    if move == "Seismic Toss" or move == "Night Shade":
        return 100

    obj = move_dict[move]
    move_obj = obj[0]

    # If the category isn't offensive, the move won't do any damage
    if obj[-1] not in ["Pure Offensive", "Offensive Cripple"]:
        return 0

    modifier = 1  # Initially set modifier to 1
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


# Find the most damaging move to the current opposing Pokemon
def find_mdm(poke1, poke2, move_dict):
    max_dmg = 0
    mdm = None

    for move in poke1.moves:
        dmg = damage_calc(poke1, poke2, move, move_dict)
        if dmg > max_dmg:
            max_dmg = dmg
            mdm = move

    return mdm if max_dmg > 0 else None  # If no move does damage, return None


# Find the Pokemon which eats MDM the best in terms of HP% damage (SRP) and HP% remaining (SHP)
def find_srp_shp(poke1, p2_poke, mdm, move_dict):
    if mdm is None:  # If mdm does not exist
        return None, None

    min_dmg = float("inf")
    max_remain = 0
    srp = None
    shp = None

    for key in p2_poke:
        poke = p2_poke[key]

        # Skip fainted mons, include the current one
        if poke.fainted is True:
            continue

        dmg = damage_calc(poke1, poke, mdm, move_dict)/poke.maxHP*100
        remain = poke.currHP/poke.maxHP*100 - dmg

        if dmg < min_dmg:
            min_dmg = dmg
            srp = poke.name
        if remain > max_remain:
            max_remain = remain
            shp = poke.name

    return srp, shp


# Find the Pokemon which can tank MDM and do the most damage (SDP)
def find_sdp(poke1, p2_poke, mdm, move_dict):
    if mdm is None:  # If mdm does not exist
        return None

    sdp = None
    max_dmg = 0

    for key in p2_poke:
        poke = p2_poke[key]

        # Skip fainted mons, include the current one
        if poke.fainted is True:
            continue
        # Check if it can live a mdm from poke1
        if poke.currHP - damage_calc(poke1, poke, mdm, move_dict) <= 0:
            continue

        best_move = find_mdm(poke, poke1, move_dict)  # Find its best move and how much dmg it deals
        if best_move is None:  # If there is no best move, continue
            continue
        dmg = damage_calc(poke, poke1, best_move, move_dict)

        if dmg > max_dmg:
            max_dmg = dmg
            sdp = poke.name

    return sdp


# Main function to manage game state, find "decisions" like MDM for P1
def write_game_state(current_mon, p1_poke, p2_poke, move_dict):
    poke1 = p1_poke[current_mon[0]]
    poke2 = p2_poke[current_mon[1]]

    # MDM (Most Damaging Move)
    mdm_1 = find_mdm(poke1, poke2, move_dict)
    mdm_2 = find_mdm(poke2, poke1, move_dict)

    # SRP (Swap Resist Poke) and SHP (Swap HP% Poke)
    (srp_1, shp_1) = find_srp_shp(poke2, p1_poke, mdm_2, move_dict)
    (srp_2, shp_2) = find_srp_shp(poke1, p2_poke, mdm_1, move_dict)

    # MDM2 (Most Damaging Move 2)
    mdm2_1 = find_mdm(poke1, p2_poke[srp_2], move_dict) if (srp_2 is not None) else None
    mdm2_2 = find_mdm(poke2, p1_poke[srp_1], move_dict) if (srp_1 is not None) else None

    # SDP (Swap Damage Poke)
    sdp_1 = find_sdp(poke2, p1_poke, mdm_2, move_dict)
    sdp_2 = find_sdp(poke1, p2_poke, mdm_1, move_dict)

    print("mdm 1 and 2: {} {}".format(mdm_1, mdm_2))
    print("srp 1 and 2: {} {}".format(srp_1, srp_2))
    print("shp 1 and 2: {} {}".format(shp_1, shp_2))
    print("mdm 2 1 and 2: {} {}".format(mdm2_1, mdm2_2))
    print("sdp 1 and 2: {} {}".format(sdp_1, sdp_2))
