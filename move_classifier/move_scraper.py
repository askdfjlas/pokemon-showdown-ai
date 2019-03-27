from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup as Soup

LINK = "https://pokemondb.net/move/all"
OUTPUT = "../data/moves/RAW_MOVES.tsv"

# Important indexes
PS_INDEX = 2  # Physical/Special uses an icon, so deal with these in a special way
TM_INDEX = 6  # Skip the TM info, which is irrelevant for battling purposes
LAST_INDEX = 8
NUM_INDEX = [3, 4, 8]  # Set dashes to 0s for these indexes


# Simplify the get request
def simple_get(url):
    try:
        with closing(get(url, stream=True)) as resp:
            if is_good_response(resp):
                return resp.content
            else:
                return None

    except RequestException as e:
        print("Error during requests to {0} : {1}".format(url, str(e)))
        return None


def is_good_response(resp):
    content_type = resp.headers['Content-Type'].lower()
    return (resp.status_code == 200
            and content_type is not None
            and content_type.find('html') > -1)


# Return bs4 object
def get_soup(url):
    raw = simple_get(url)

    return Soup(raw, "html.parser")


# Deal with the physical/special move icon
def parse_ps_icon(element):
    if element.text == '-':
        return '-'

    return "Physical" if "Physical" in str(element) else \
        ("Status" if "Status" in str(element) else "Special")


# Return 0s instead of dashes for numerical attributes
def parse_num(element):
    return '0' if element.text in ['—', ''] else element.text


# Returns table soup object where moves are stored
def get_move_table():
    page = get_soup(LINK)

    return page.find("table", {"id": "moves"})


# Write values to TSV file
def write_output(table):
    output_file = open(OUTPUT, "w")
    rows = table.findAll("tr")

    first = True
    for row in rows:
        # Skip the first row, which has column information
        if first:
            first = False

        # Iterate through the elements, and keep a count of the index
        c = 0
        for element in row.findAll("td"):
            # Skip TM information
            if c == TM_INDEX:
                c += 1
                continue

            # Physical/Special
            if c == PS_INDEX:
                output_file.write(parse_ps_icon(element))
            # Numerical Attribute
            elif c in NUM_INDEX:
                output_file.write(parse_num(element))
            else:
                output_file.write(element.text)

            output_file.write('\n' if c == LAST_INDEX else '\t')
            c += 1

    output_file.close()


# Main function
def main():
    table = get_move_table()
    write_output(table)


if __name__ == "__main__":
    main()
