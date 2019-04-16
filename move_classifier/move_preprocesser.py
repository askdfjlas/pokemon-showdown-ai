# Preprocess RAW_MOVES.tsv with existence of keywords so the decision tree can make splits

# Keywords to search in the move description
keywords = ["poison", "to sleep", "paralyze", "burn", "confuse", "raise user", "raises user",
            "lower opponent", "lowers opponent", "attack", "special attack", "speed", "defense",
            "special defense", "evasiveness", "recover", "cure", "heal", "restore", "z-move"]


# Indexes to ignore (Type, Physical/Special, Accuracy, PP)
bad_indexes = [1, 2, 4, 5]


# Main function
def main(input_f, output_f):
    input_data = open(input_f)
    output_data = open(output_f, "w")

    for line in input_data:
        arr = line.rstrip().split('\t')
        move_description = arr.pop(-2).lower()

        for i in range(len(bad_indexes)):  # Pop bad indexes
            arr.pop(bad_indexes[i] - i)

        for word in keywords:  # Each keyword is an attribute; set it to Y if it is contained in the description
            arr.append("Y" if word in move_description else "N")

        for i in range(len(arr)):  # Rewrite arr into another .tsv
            if arr[i] == '∞':  # Consistent with numeric attribute
                arr[i] = "100"

            output_data.write(arr[i] + ('\t' if i < len(arr) - 1 else '\n'))

    input_data.close()
    output_data.close()


if __name__ == "__main__":
    main("../data/moves/RAW_MOVES.tsv", "../data/moves/TESTING_MOVES.tsv")
