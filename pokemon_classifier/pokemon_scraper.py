# Scrape into .tsv of Pokemon with attributes
import move_scraper

LINK = "https://pokemondb.net/pokedex/all"
OUTPUT = "../data/pokemon/RAW_POKEMON.tsv"

# Important indexes
IGNORE_INDEXES = [0, 3]
NAME_INDEX = 1
TYPE_INDEX = 2

# Same Pokemon, different forms to include
# Currently doesn't deal with Alolan forms, Necrozma/Kyogre/Groudon, and other stuff
FORMS = ["Sandy", "Trash", "Heat", "Wash", "Frost", "Fan", "Mow", "Therian",
         "Black", "White", "Small", "Large", "Super", "Unbound", "Midnight",
         "Dusk"]


# Returns types listed in an element
def parse_types(row):
    types = []

    labels = row.findAll("a")
    for label in labels:
        types.append(label.text)

    # Set type 2 to None if it doesn't exist
    if len(types) == 1:
        types.append(None)

    return types


# Returns the "gray" sub-text if it exists
def parse_subtext(row):
    if row.find("small") is not None:
        words = row.find("small").text.split()

        for form in FORMS:
            if words[0] == form:
                return form

    return None


# Returns table soup object where pokemon are stored
def get_pokedex():
    page = move_scraper.get_soup(LINK)

    return page.find("table", {"id": "pokedex"})


# Write values to TSV file
def write_output(pokedex):
    output_file = open(OUTPUT, "w")
    rows = pokedex.findAll("tr")

    prev_pokemon = ""  # Store the previous Pokemon to ignore forms, mega, etc. for now
    for row in rows:
        arr = []  # Array to write to .csv

        c = 0
        for element in row.findAll("td"):
            if c in IGNORE_INDEXES:
                c += 1
                continue
            elif c == NAME_INDEX:
                poke = element.find("a").text
                if poke == prev_pokemon:
                    tag = parse_subtext(row)
                    # Super inconvenient since "Dusk Mane" conflicts with Dusk Lycanroc
                    if tag is None or poke == "Necrozma":
                        break  # Go to next poke if this one was a form/mega

                    poke += "-{}".format(tag)  # Add the tag (example: Landorus-Therian)
                else:
                    prev_pokemon = poke

                arr.append(poke)
            elif c == TYPE_INDEX:
                arr += parse_types(element)
            else:
                arr.append(element.text)

            c += 1

        if len(arr) > 0:  # If the pokemon was not a form of the previous one
            for i in range(len(arr)):
                output_file.write(str(arr[i]) + ('\n' if i == len(arr) - 1 else '\t'))

    output_file.close()


# Main function
def main():
    pokedex = get_pokedex()
    write_output(pokedex)


if __name__ == "__main__":
    main()
