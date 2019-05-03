# Get attributes given game state objects (current mon and poke lists), and write to a file
from pokemon import *
import tsv_to_2d as tsv

OUTPUT_F = "../data/learning/TRAINING_SET.tsv"

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

DECISIONS = ["MDM", "MDM2", "SDP", "SRP", "SHP"]  # Numbers marked to decision (class label) names
D_DICT = {"MDM": 0, "MDM2": 1, "SDP": 2, "SRP": 3, "SHP": 4}  # Decisions marked to numbers
MOVE_TYPES = {"Pure Cripple": 0, "Offensive Cripple": 1, "Offensive Setup": 2, "Defensive Setup": 3,
              "Recovery": 4, "Z-Move": 5, "Situational": 6, "Pure Offensive": 7}
SWAP_TYPES = {"Physical Wall": 0, "Special Wall": 1, "Physical Attacker": 2, "Special Attacker": 3,
              "Physical Sweeper": 4, "Special Sweeper": 5}
SWAP_CLASSES = {"SDP", "SRP", "SHP", "Physical Wall", "Special Wall", "Physical Attacker",
                "Special Attacker", "Physical Sweeper", "Special Sweeper"}


# Damage calculator, poke1 = attacking poke, poke2 = defending
# Slightly inaccurate by a few points due to the ceiling and lack of integer truncation, although that doesn't matter
def damage_calc(poke1, poke2, move, move_dict):
    if move is None:  # No damage if there is no move
        return 0
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


# Get the class label, or the user's decision
def get_class_label(move, decisions, move_dict, poke_dict):
    if move is None:
        return None
    for i in range(len(decisions)):
        if move == decisions[i]:
            return DECISIONS[i]  # Return one of the 5 possible decisions
    if move in move_dict:
        category = move_dict[move][-1]  # Write the class of the move
        return category if category != "Pure Offensive" else "MDM"  # If pure offensive, then AI might as well use MDM
    return poke_dict[move][-1]  # Move is a swap into a poke, write the class of this poke


# Get number of alive poke
def get_number_remaining(poke_list):
    count = 0
    for key in poke_list:
        poke = poke_list[key]
        if poke.fainted is False:
            count += 1

    return count


# Return a binary list of available move decisions
def get_binary_moves(poke, decisions, move_dict):
    # Check MDM and MDM2
    binary = [el is not None for el in decisions[:2]]
    move_arr = [False, False, False, False, False, False, False, False]  # Which moves are available
    for move in poke.moves:
        category = move_dict[move][-1]
        move_arr[MOVE_TYPES[category]] = True

    return binary + move_arr


# Return a binary list of available swap decisions
def get_binary_swaps(current_poke, pokes, decisions, poke_dict):
    binary = [el is not None for el in decisions[2:]]
    poke_arr = [False, False, False, False, False, False]  # Which swaps are available
    for key in pokes:
        poke = pokes[key]
        if poke.fainted is True or poke.name == current_poke.name:
            continue
        category = poke_dict[poke.name][-1]
        poke_arr[SWAP_TYPES[category]] = True

    return binary + poke_arr


# Converts True/False to "Y/N"
def convert_bool(b):
    return 'Y' if b else 'N'


# Preprocess numeric data in approximately intervals of 5%
def discretize(num):
    num = int(num)
    if num <= 0:
        return 0
    if num < 5:
        return 2
    if num > 100:
        return 100
    return int(num/5)*5


# Write the entire row, requires lots of attributes
def write_state(poke1, poke2, p1_poke, p2_poke, move_dict, poke_dict, decisions_1, decisions_2, label, forced, output):
    if label is None or label == "Situational":  # No decision in this category is made or it is situational
        return
    # Current and opposing mon stats
    cpc = poke_dict[poke1.name][-1]  # Class
    chp = discretize(math.ceil(poke1.currHP/poke1.maxHP*100))
    cstatus = str(poke1.status)[7:]
    cboosts = poke1.boosts

    opc = poke_dict[poke2.name][-1]
    ohp = discretize(math.ceil(poke2.currHP/poke2.maxHP*100))
    ostatus = str(poke2.status)[7:]
    oboosts = poke2.boosts

    # Binary attributes for available options, swap and moves
    #binary_moves = get_binary_moves(poke1, decisions_1, move_dict)
    #binary_swaps = get_binary_swaps(poke1, p1_poke, decisions_1, poke_dict)

    # Damage calc numeric attributes, extremely ugly
    # Damage and HP% to opposing after MDM and MDM2
    mdm_dmg = int(damage_calc(poke1, poke2, decisions_1[D_DICT["MDM"]], move_dict)/poke2.maxHP * 100)
    mdm_hp = int((poke2.currHP/poke2.maxHP)*100) - mdm_dmg
    mdm2_dmg = int(damage_calc(poke1, poke2, decisions_1[D_DICT["MDM2"]], move_dict)/poke2.maxHP * 100)
    mdm2_hp = int((poke2.currHP/poke2.maxHP)*100) - mdm2_dmg

    # Damage to opposing SRP after MDM and MDM2
    o_srp = p2_poke[decisions_2[D_DICT["SRP"]]] if decisions_2[D_DICT["SRP"]] is not None else None
    mdm_dmg_srp = int((damage_calc(poke1, o_srp, decisions_1[D_DICT["MDM"]], move_dict)/o_srp.maxHP)*100) \
        if o_srp is not None else 0
    mdm_hp_srp = int((o_srp.currHP/o_srp.maxHP)*100) - mdm_dmg_srp if o_srp is not None else 100
    mdm2_dmg_srp = int((damage_calc(poke1, o_srp, decisions_1[D_DICT["MDM2"]], move_dict)/o_srp.maxHP)*100) \
        if o_srp is not None else 0
    mdm2_hp_srp = int((o_srp.currHP/o_srp.maxHP)*100) - mdm2_dmg_srp if o_srp is not None else 100

    # Damage and HP% to current poke after opponent's MDM and MDM2
    o_mdm_dmg = int(damage_calc(poke2, poke1, decisions_2[D_DICT["MDM"]], move_dict)/poke1.maxHP * 100)
    o_mdm_hp = int((poke2.currHP/poke2.maxHP)*100) - o_mdm_dmg
    o_mdm2_dmg = int(damage_calc(poke2, poke1, decisions_2[D_DICT["MDM2"]], move_dict)/poke1.maxHP * 100)
    o_mdm2_hp = int((poke2.currHP/poke2.maxHP)*100) - o_mdm2_dmg

    # Damage and HP% to SRP after opponent's MDM and MDM2
    srp = p1_poke[decisions_1[D_DICT["SRP"]]] if decisions_1[D_DICT["SRP"]] is not None else None
    o_mdm_dmg_srp = int((damage_calc(poke2, srp, decisions_2[D_DICT["MDM"]], move_dict)/srp.maxHP) * 100) \
        if srp is not None else 0
    o_mdm_hp_srp = int((srp.currHP/srp.maxHP)*100) - o_mdm_dmg_srp if srp is not None else 100
    o_mdm2_dmg_srp = int((damage_calc(poke2, srp, decisions_2[D_DICT["MDM2"]], move_dict)/srp.maxHP) * 100) \
        if srp is not None else 0
    o_mdm2_hp_srp = int((srp.currHP/srp.maxHP)*100) - o_mdm2_dmg_srp if srp is not None else 100

    remain = get_number_remaining(p1_poke)  # Number of remaining poke
    forced_swap = convert_bool(forced)  # Whether swap is forced
    poke1_speed = STAT_BOOSTS[poke1.boosts[STAT_NUMBERS["spd"]]]*poke1.speed
    poke2_speed = STAT_BOOSTS[poke2.boosts[STAT_NUMBERS["spd"]]]*poke2.speed
    faster = convert_bool(poke1_speed > poke2_speed)  # Is my poke faster?
    sub_label = "Swap" if label in SWAP_CLASSES else "Attack"

    # Make the final list!!!
    # [convert_bool(b) for b in binary_swaps] + [convert_bool(b) for b in binary_moves] + \
    final_list = \
        [cpc, chp, cstatus] + cboosts + \
        [opc, ohp, ostatus] + oboosts + \
        [forced_swap, remain, faster] + \
        [discretize(i) for i in [mdm_dmg, mdm_hp, mdm2_dmg, mdm2_hp] +  # Discretize all the damage calculations
            [mdm_dmg_srp, mdm_hp_srp, mdm2_dmg_srp, mdm2_hp_srp] +
            [o_mdm_dmg, o_mdm_hp, o_mdm2_dmg, o_mdm2_hp] +
            [o_mdm_dmg_srp, o_mdm_hp_srp, o_mdm2_dmg_srp, o_mdm2_hp_srp]] + \
        [sub_label, label]  # !!!

    tsv.write_row(final_list, output)  # Write rows to file!


# Main function to manage game state, find "decisions" like MDM for P1
def write_game_state(current_mon, p1_poke, p2_poke, move_dict, poke_dict, non_forced, forced, output):
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

    # Find class labels and write a row
    decisions_1 = [mdm_1, mdm2_1, sdp_1, srp_1, shp_1]
    decisions_2 = [mdm_2, mdm2_2, sdp_2, srp_2, shp_2]
    label_1 = get_class_label(non_forced[0], decisions_1, move_dict, poke_dict)
    label_1_f = get_class_label(forced[0], decisions_1, move_dict, poke_dict)
    label_2 = get_class_label(non_forced[1], decisions_2, move_dict, poke_dict)
    label_2_f = get_class_label(forced[1], decisions_1, move_dict, poke_dict)

    # Finally, write states
    write_state(poke1, poke2, p1_poke, p2_poke, move_dict, poke_dict, decisions_1, decisions_2, label_1, False, output)
    write_state(poke1, poke2, p1_poke, p2_poke, move_dict, poke_dict, decisions_1, decisions_2, label_1_f, True, output)
    write_state(poke2, poke1, p2_poke, p1_poke, move_dict, poke_dict, decisions_2, decisions_1, label_2, False, output)
    write_state(poke2, poke1, p2_poke, p1_poke, move_dict, poke_dict, decisions_2, decisions_1, label_2_f, True, output)
