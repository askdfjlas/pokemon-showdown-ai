# Pre-search battle logs to get Pokemon, their moves, max hp, abilities, and whether an item is held
# Currently doesn't scrape the exact items though, since identifying them is kind of uncommon
from battle_strings import *
from pokemon import *

# Suffixes to ignore, too lazy to account for power construct Zygarde forms
NAME_FILTER = ["Mega-X", "Mega-Y", "Mega", "Alola", "Resolute", "Unbound", "Ash",
               "Sunshine", "Rainy", "Snowy", "Sunny", "Zen"]


# Filter out suffixes which change throughout battle
def filter_name(name):
    for suffix in NAME_FILTER:
        if suffix in name:
            # Safe to do since there's no way a suffix is part of the name
            name = name.replace("-" + suffix, "")
            break

    return name


# Remove user comments
def filter_comments(lines):
    for i in range(len(lines)):
        arr = lines[i].split('|')

        if arr[0] == 'c':
            lines[i] = None

    # Rebuild the lines and return
    new_lines = []
    for line in lines:
        if line is not None:
            new_lines.append(line)

    return new_lines


# Get parity (P1 or P2) from a commonly used format
def get_parity(line):
    return 0 if "p1" in line.split('|')[2][:2] else 1


# Get P1/P2, and move or ability name
def get_move_ability(line):
    parity = 0 if "p1" in line.split('|')[2][:2] else 1
    move = line.split('|')[3]

    return parity, move


# Get P1/P2, Pokemon name, and max HP (if it is provided) from switch statement
def get_switch(line):
    parity = 0 if "p1" in line.split('|')[2][:2] else 1
    name = filter_name(line.split('|')[3].split(',')[0])
    hp = int(line.split('/')[-1].split(' ')[0])

    # Later showdown replays write percentages for hp, it's so stupid
    # Assume if hp = 100, then it's invalid
    # This is a decent assumption since any high elo person would use lvl. 100 mon and all mon have well above
    # 100 hp except for Shedinja which has 1
    if hp == 100:
        hp = None

    # Ditto
    if name == "Ditto":
        hp = None

    return parity, name, hp


# Each player's Pokemon and whether they have a held item are given pre-battle
def get_pre_battle(log):
    lines = filter_comments(log.split("\n"))

    # Dictionaries, so that future references to a Pokemon are in constant time
    # Since training is done on real tiers, species clause applies (no duplicate Pokemon)
    p1_poke = {}
    p2_poke = {}

    curr = 0
    while lines[curr] != "|start":
        curr_line = lines[curr]
        if "|poke|" in curr_line:
            arr = curr_line.split('|')[1:]
            new_poke = Pokemon()
            name = filter_name(arr[2].split(',')[0])

            new_poke.set_name(name)
            new_poke.set_item(True if arr[-1] == "item" else False)

            if arr[1] == "p1":
                p1_poke[name] = new_poke
            else:
                p2_poke[name] = new_poke

        curr += 1

    return curr, lines, p1_poke, p2_poke


# Continue reading through log, obtaining move, max hp, and ability info
def get_during_battle(curr, lines, p1_poke, p2_poke):
    # Current Pokemon in battle
    curr_mon = [None, None]

    # Iterate until end of battle
    while len(lines[curr]) != 5 and lines[curr][:5] != "|win|":
        curr_line = lines[curr]
        arr = curr_line.split('|')[1:]

        # Sending out and actually switching all count as switches, drags are different though
        if arr[0] in ["switch", "drag"]:
            sdt = get_switch(curr_line)

            [p1_poke, p2_poke][sdt[0]][sdt[1]].set_hp(sdt[2])
            curr_mon[sdt[0]] = sdt[1]

        # Append move
        if arr[0] == "move":
            mdt = get_move_ability(curr_line)

            [p1_poke, p2_poke][mdt[0]][curr_mon[mdt[0]]].append_move(mdt[1])

        # Some abilities...
        if arr[0] == "-ability":
            adt = get_move_ability(curr_line)

            [p1_poke, p2_poke][adt[0]][curr_mon[adt[0]]].set_ability(adt[1])

        # Others...  Why
        for el in arr:
            if len(el) >= 15 and el[:15] == "[from] ability:":
                ability = el.split(':')[-1][1:]
                parity = 0 if ("|p1a:" in curr_line or "|[of] p1a:" in curr_line) else 1

                [p1_poke, p2_poke][parity][curr_mon[parity]].set_ability(ability)

        curr += 1


# Testing
if __name__ == "__main__":
    for l in get_battle_strings():
        d = get_pre_battle(l)
        get_during_battle(d[0], d[1], d[2], d[3])

        print(d[2], d[3])

        # Just one test so it doesn't take too long, break after first iteration
        break
