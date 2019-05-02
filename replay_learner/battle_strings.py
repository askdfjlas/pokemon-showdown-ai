# Iterator for battle strings

from bs4 import BeautifulSoup as soup

SUFFIX = "../data/replays/Gen7OU-"
NUM_REPLAYS = 100


def get_battle_strings():
    for i in range(1, NUM_REPLAYS + 1):
        raw = open(SUFFIX + str(i) + ".html")
        obj = soup(raw, "html.parser")
        raw.close()

        # Yield the battle log
        yield obj.find("script", class_="battle-log-data").decode_contents()


# Testing
if __name__ == "__main__":
    for s in get_battle_strings():
        print(s)
