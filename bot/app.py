# Main file for running the bot using a chrome instance
from selenium import webdriver
import time

LINK = "https://play.pokemonshowdown.com/"
USERNAME = "MachineLearningBot"
PASSWORD_FILE = "../data/password.txt"


def wait_load(browser, name):
    while len(browser.find_elements_by_name(name)) == 0:  # Wait until everything loads
        time.sleep(1)


def get_move_options(browser):
    polling = 0
    while True:
        if len(browser.find_elements_by_name("selectMove")) != 0:
            return "selectMove"
        if len(browser.find_elements_by_name("chooseSwitch")) != 0:
            polling += 1
            if polling == 2:
                return "chooseSwitch"

        time.sleep(2)


def click_button(browser, name):
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
    browser.get(LINK)
    wait_load(browser, "login")

    click_button(browser, "login")  # Click login button
    username_form = fill_textbox(browser, "username", USERNAME)  # Type in username
    username_form.submit()
    wait_load(browser, "password")
    password_form = fill_textbox(browser, "password", password)  # Type in password
    password_form.submit()


# Begin the battle!
def start_battle(browser):
    while True:
        if get_move_options(browser) == "selectMove":
            click_button(browser, "selectMove")
            wait_load(browser, "chooseMove")
            click_button(browser, "chooseMove")
        else:
            click_button(browser, "chooseSwitch")


def main():
    browser = webdriver.Chrome(executable_path="../chromedriver")
    login(browser)

    # Main loop, check the page every 2 seconds
    while True:
        if len(browser.find_elements_by_name("acceptChallenge")) > 0:  # If there is a challenge
            click_button(browser, "acceptChallenge")
            start_battle(browser)

        time.sleep(2)


if __name__ == "__main__":
    main()
