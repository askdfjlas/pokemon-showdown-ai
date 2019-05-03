# Main file for running the bot using a chrome instance
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from pokesim import *
import dtree_build
import move_tree
import time

LINK = "https://play.pokemonshowdown.com/"
USERNAME = "MachineLearningBot"
PASSWORD_FILE = "../data/password.txt"
TEAM_FILE = "../data/team.txt"


def get_switch(line):
    parity = 0 if "p1" in line.split('|')[2][:2] else 1
    name = pre_search.filter_name(line.split('|')[3].split(',')[0])
    hp = int(line.split('/')[-1].split('|')[0].split(' ')[0])

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

    # This replay format...
    return [parity, int(arr[2].split('/')[0]), cause, int(arr[2].split()[0].split('/')[1]) > 100]


# Get P1/P2, amount healed, and a [from] effect if possible
def get_heal(line):
    parity = pre_search.get_parity(line)
    arr = line.split('|')[1:]
    if len(arr) > 3:
        cause = arr[3][7:]
    else:
        cause = None

    # This replay format...
    return [parity, int(arr[2].split('/')[0]), cause, int(arr[2].split()[0].split('/')[1]) > 100]


def wait_load(browser, name):
    while len(browser.find_elements_by_name(name)) == 0:  # Wait until everything loads
        time.sleep(1)


def get_battle_log(browser):
    append_string = ""
    for entry in browser.get_log('browser'):
        if "\\n\\n" in entry["message"]:
            arr = entry["message"].replace("\\n", "\n").split('\n')
            append_string += "\n".join(arr[2:-1])

    return append_string


def get_move_options(browser):
    polling = 0
    while True:
        if len(browser.find_elements_by_name("chooseTeamPreview")) != 0:
            return "chooseTeamPreview"
        if len(browser.find_elements_by_name("selectMove")) != 0:
            return "selectMove"
        if len(browser.find_elements_by_name("chooseSwitch")) != 0:
            polling += 1
            if polling == 2:
                return "chooseSwitch"

        time.sleep(2)


def click_button(browser, name):
    wait_load(browser, name)
    button = browser.find_elements_by_xpath("//button[@name='{}']".format(name))[0]
    button.click()


def fill_textbox(browser, name, text):
    box = browser.find_elements_by_xpath("//input[@name='{}']".format(name))[0]
    box.send_keys(text)
    return box


def login(browser):
    password_txt = open(PASSWORD_FILE)
    password = ""
    for line in password_txt:
        password = line
    password_txt.close()
    browser.get(LINK)

    click_button(browser, "login")  # Click login button
    username_form = fill_textbox(browser, "username", USERNAME)  # Type in username
    username_form.submit()
    wait_load(browser, "password")
    password_form = fill_textbox(browser, "password", password)  # Type in password
    password_form.submit()


def load_team(browser):
    team_file = open(TEAM_FILE)
    team_str = team_file.read()
    team_file.close()

    team_btn = browser.find_elements_by_xpath("//button[@value='teambuilder']")[0]
    team_btn.click()
    click_button(browser, "newTop")
    click_button(browser, "import")
    textbox = browser.find_elements_by_xpath("//textarea")[0]
    textbox.send_keys(team_str)
    click_button(browser, "saveImport")
    click_button(browser, "closeRoom")


# Write the entire row, requires lots of attributes
def get_state(poke1, poke2, p1_poke, p2_poke, move_dict, poke_dict, decisions_1, decisions_2, forced):
    # Current and opposing mon stats
    cpc = poke_dict[poke1.name][-1]  # Class
    chp = discretize(math.ceil(poke1.currHP/poke1.maxHP*100))
    cstatus = str(poke1.status)[7:]
    cboosts = poke1.boosts

    opc = poke_dict[poke2.name][-1]
    ohp = discretize(math.ceil(poke2.currHP/poke2.maxHP*100))
    ostatus = str(poke2.status)[7:]
    oboosts = poke2.boosts

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

    # Make the final list!!!
    # [convert_bool(b) for b in binary_swaps] + [convert_bool(b) for b in binary_moves] + \
    final_list = \
        [cpc, chp, cstatus] + cboosts + \
        [opc, ohp, ostatus] + oboosts + \
        [forced_swap, remain, faster] + \
        [discretize(i) for i in [mdm_dmg, mdm_hp, mdm2_dmg, mdm2_hp] +  # Discretize all the damage calculations
            [mdm_dmg_srp, mdm_hp_srp, mdm2_dmg_srp, mdm2_hp_srp] +
            [o_mdm_dmg, o_mdm_hp, o_mdm2_dmg, o_mdm2_hp] +
            [o_mdm_dmg_srp, o_mdm_hp_srp, o_mdm2_dmg_srp, o_mdm2_hp_srp]]

    return final_list, decisions_2


def get_game_state(current_mon, p1_poke, p2_poke, move_dict, poke_dict, forced):
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

    return get_state(poke1, poke2, p1_poke, p2_poke, move_dict, poke_dict, decisions_1, decisions_2, forced)


# Simulate one turn of the battle, copied from pokesim
def simulate_turn(append_string, current_mon, p1_poke, p2_poke):
    lines = append_string.split('\n')
    current = 0

    forced_swaps = [False, False]  # Forced swaps occur when a user must decide their next Poke to send out
    non_forced = [None, None]  # Decisions which aren't forced swaps
    forced_decisions = [None, None]  # Decisions which are forced swaps
    # Iterate until end of battle
    while current < len(lines) and len(lines[current]) != 5 and lines[current][:5] != "|win|":
        curr_line = lines[current]
        arr = curr_line.split('|')[1:]

        if len(arr) < 1:
            current += 1
            continue

        # Player switches or gets a poke dragged in (the latter case they have no control over)
        if arr[0] in ["switch", "drag"]:
            parity = arr[0] == "switch"
            sdt = get_switch(curr_line)
            print(sdt)
            print(current_mon)
            poke_name = current_mon[sdt[0]]
            poke_object = [p1_poke, p2_poke][sdt[0]][poke_name]
            if forced_swaps[sdt[0]]:
                print("Forced swap: ", end="")
                forced_decisions[sdt[0]] = sdt[1]
            else:
                non_forced[sdt[0]] = sdt[1]
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

            non_forced[mdt[0]] = mdt[1]

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

    return p1_poke, p2_poke, current_mon


def get_class_list(d):
    l = []
    for k in d:
        l.append((k, int(d[k][:-1])))

    return sorted(l, key=lambda x: x[1], reverse=True)


def recommend_move(l, decisions, poke, move_dict, poke_list, poke_dict):
    for t in l:
        if t[0] == "MDM":
            return decisions[0]
        if t[0] == "MDM2":
            return decisions[1]
        if t[0] == "SDP":
            return decisions[2]
        if t[0] == "SRP":
            return decisions[3]
        if t[0] == "SHP":
            return decisions[5]
        if t[0] in ["Pure Cripple", "Offensive Cripple", "Offensive Setup", "Defensive Setup", "Recovery",
                    "Situational"]:
            for m in poke.moves:
                if move_dict[m][-1] == t[0]:
                    return m
        else:
            for k in poke_list:
                poke = poke_list[k]
                if poke_dict[poke.name][-1] == t[0]:
                    return poke.name

    return None


def use_move(move, browser, move_dict):
    if move == "Landorus-Therian":
        move = "Landorus"
    if move in move_dict:
        click_button(browser, "selectMove")
        button = browser.find_elements_by_xpath("//button[@name='chooseMove' and @data-move='{}']".format(move))[0]
        button.click()
    else:
        if len(browser.find_elements_by_xpath("//button[@name='chooseSwitch']")) > 0:
            click_button(browser, "selectSwitch")
        buttons = browser.find_elements_by_xpath("//button[@name='chooseSwitch']")
        for button in buttons:
            inner = browser.execute_script("return arguments[0].innerText;", button)
            if move in inner:
                button.click()
                return


# Begin the battle!
def start_battle(browser, tree):
    # Load the poke objects
    poke_dict = load_pokemon()
    move_dict = load_moves()

    wait_load(browser, "chooseTeamPreview")
    battle_string = get_battle_log(browser)

    current, lines, p1_poke, p2_poke = pre_search.get_pre_battle(battle_string)  # Get pre-battle info
    populate_pokes(p1_poke, p2_poke, poke_dict)  # Compute unknown stats from Smogon EVs

    start = -1
    current_mon = [None, None]
    while True:
        state = get_move_options(browser)
        append_string = get_battle_log(browser)
        if start < 1:
            if start == 0:
                current, current_mon = get_starting_mon(0, append_string.split('\n'))
            start += 1
        else:
            p1_poke, p2_poke, current_mon = simulate_turn(append_string, current_mon, p1_poke, p2_poke)
        if state == "selectMove":
            arr, options = get_game_state(current_mon, p1_poke, p2_poke, move_dict, poke_dict, False)
            arr = move_tree.convert_numeric(arr)
            node = dtree_build.classify(arr, tree)  # Classify the row
            l = get_class_list(node)
            move = recommend_move(l, options, p2_poke[current_mon[1]], move_dict, p2_poke, poke_dict)
            print(move)
            if move == p2_poke[current_mon[1]].name or move is None:
                click_button(browser, "selectMove")
                click_button(browser, "chooseMove")
            else:
                use_move(move, browser, move_dict)
        elif state == "chooseSwitch":
            arr, options = get_game_state(current_mon, p1_poke, p2_poke, move_dict, poke_dict, True)
            arr = move_tree.convert_numeric(arr)
            node = dtree_build.classify(arr, tree)  # Classify the row
            l = get_class_list(node)
            move = recommend_move(l, options, p2_poke[current_mon[1]], move_dict, p2_poke, poke_dict)
            print(move)
            use_move(move, browser, move_dict)
        elif state == "chooseTeamPreview":
            click_button(browser, "chooseTeamPreview")


def asdf(TRAINING_SET):
    # Open up training set, create decision tree
    rows = tsv.get_list(TRAINING_SET)
    for i in range(len(rows)):
        # Convert to numeric, then pop the Pokemon name
        rows[i] = move_tree.convert_numeric(rows[i])

    tree = dtree_build.buildtree_h(rows, len(rows[0]) - 2, 0, min_samples=20, min_gain=0.01)

    return tree


def main():
    print("Making tree...")
    tree = asdf("../data/learning/TRAINING_SET.tsv")

    # Browser settings for getting logs
    d = DesiredCapabilities.CHROME
    d["loggingPrefs"] = {"browser": "ALL"}
    browser = webdriver.Chrome(executable_path="../chromedriver", desired_capabilities=d)
    login(browser)
    load_team(browser)

    # Main loop, check the page every 2 seconds
    while True:
        if len(browser.find_elements_by_name("acceptChallenge")) > 0:  # If there is a challenge
            click_button(browser, "acceptChallenge")
            start_battle(browser, tree)

        time.sleep(2)


if __name__ == "__main__":
    main()
