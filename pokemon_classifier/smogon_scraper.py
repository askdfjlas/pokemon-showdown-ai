# Scrape all movesets and EVs from Smogon
import tsv_to_2d as tsv
import get_js

LINK = "https://www.smogon.com/dex/sm/pokemon/"
INPUT = "../data/pokemon/RAW_POKEMON.tsv"
OUTPUT = "../data/pokemon/COOKED2_POKEMON.tsv"  # :^)

EV_INDEXES = {"HP": 0, "Atk": 1, "Def": 2, "SpA": 3, "SpD": 4, "Spe": 5}  # Indexes for each EV stat


# Write to file additional data from Smogon for each entry
def write_smogon_data(rows):
    output_file = open(OUTPUT, "w")

    for row in rows:
        poke = row[0]  # Pokemon name
        moveset = get_js.get_soup(LINK + poke).find("div", {"class": "MovesetInfo"})

        if moveset is None:
            continue

        moves = moveset.findAll("ul", {"class": "MoveList"})
        for move in moves:
            row.append(move.find("a").text)  # Insert the first move (since more than one can be recommended)

        evs = [0 for i in range(6)]  # Initialize EVs to 0
        ev_list = moveset.find("ul", {"class": "evconfig"}).findAll("li")
        for value in ev_list:
            tup = value.text.split()  # Format: (Value, Stat)
            evs[EV_INDEXES[tup[1]]] = tup[0]

        row += evs
        tsv.write_row(row, output_file)  # Write row to output

    output_file.close()
    get_js.browser.quit()


# Main function
def main():
    rows = tsv.get_list(INPUT)
    write_smogon_data(rows)


if __name__ == "__main__":
    main()
