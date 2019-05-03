# Main file for running the bot using a chrome instance
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import time

LINK = "https://play.pokemonshowdown.com/"
USERNAME = "MachineLearningBot"
PASSWORD_FILE = "../data/password.txt"
TEAM_FILE = "../data/team.txt"


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


# Begin the battle!
def start_battle(browser):
    battle_string = ""
    while True:
        state = get_move_options(browser)
        if state == "selectMove":
            battle_string += get_battle_log(browser)
            print(battle_string)
            click_button(browser, "selectMove")
            click_button(browser, "chooseMove")
        elif state == "chooseSwitch":
            click_button(browser, "chooseSwitch")
        elif state == "chooseTeamPreview":
            click_button(browser, "chooseTeamPreview")


def main():
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
            start_battle(browser)

        time.sleep(2)


if __name__ == "__main__":
    main()
