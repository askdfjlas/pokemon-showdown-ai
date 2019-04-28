# Return a soup object using a get request to a page, but wait for dynamically generated Javascript elements
from bs4 import BeautifulSoup as Soup
from selenium import webdriver

# Assume that a browser instance needs to be created if this file is imported
browser = webdriver.Chrome(executable_path="../chromedriver")


def get_soup(link):
    browser.get(link)

    return Soup(browser.page_source, "html.parser")


# Testing
if __name__ == "__main__":
    print(get_soup("https://www.smogon.com/dex/sm/pokemon/bulbasaur/"))
