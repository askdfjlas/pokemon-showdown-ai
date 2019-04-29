# Preprocess COOKED_POKEMON.tsv to show
import tsv_to_2d as tsv

bad_indexes = [1, 2]  # Indexes to ignore (Types)
MOVES_START = 7  # Endpoints of move section
MOVES_END = 11

# Move class labels hashed to indexes
MOVE_TYPE_BUCKETS = {"Pure Offensive": 0, "Pure Cripple": 1, "Offensive Cripple": 2,
                     "Offensive Setup": 3, "Defensive Setup": 4, "Recovery": 5, "Status": 6,
                     "Z-Move": 7, "Situational": 8}
NUM_MOVE_TYPES = 9


# Main function
def main(input_f, output_f, move_f):
    move_dict = tsv.get_dict(move_f)  # Moves hashed to their class label
    rows = tsv.get_list(input_f)
    output_data = open(output_f, "w")

    for row in rows:
        arr = []

        # Strip types
        for i in range(len(row)):
            if i not in bad_indexes:
                arr.append(row[i])

        # Populate move buckets
        move_buckets = [0 for i in range(NUM_MOVE_TYPES)]
        for move in arr[MOVES_START: MOVES_END]:
            if "Hidden Power" in move:  # Force all hidden powers to resolve to "Hidden Power"
                move = "Hidden Power"
            if move != "None":
                move_buckets[MOVE_TYPE_BUCKETS[move_dict[move]]] += 1

        # Remove original moves
        for i in range(MOVES_START, MOVES_END):
            arr.pop(MOVES_START)

        # Write to file
        tsv.write_row(arr + move_buckets, output_data)

        print(move_buckets)


if __name__ == "__main__":
    main("../data/pokemon/COOKED_POKEMON.tsv", "../data/pokemon/TESTING_POKEMON.tsv",
         "../data/moves/CLASSIFIED_MOVES.tsv")
