# Code to generate decision tree from TRAINING_MOVES.tsv
import dtree_build
import dtree_draw


# Attribute labels
labels = ["power", "activation chance", "poison", "to sleep", "paralyze", "burn", "confuse",
          "raise user", "raises user", "lower opponent", "lowers opponent", "attack", "special attack",
          "speed", "defense", "special defense", "evasiveness", "recover", "cure", "heal", "restore", "z-move"]


# Convert numeric attributes to integers, parameter is a single row
def convert_numeric(arr):
    entry = []
    for element in arr:
        # Convert numerical attributes to ints
        try:
            element = int(element)
        except ValueError:
            pass

        entry.append(element)

    return entry


# Open up the test set, classify them, and write them to the output tsv
def classify_moves(tree, test_f, output_f):
    test_file = open(test_f)
    output = open(output_f, "w")

    for line in test_file:
        arr = line.rstrip().split('\t')
        move_name = arr.pop(0)
        entry = convert_numeric(arr)
        node = dtree_build.classify(entry, tree)  # Classify the row

        move_class = ""
        for k in node:  # There are no non-pure nodes, so this works.
            move_class = k

        output.write(move_name + '\t' + move_class + '\n')  # Store as (move name, class) in .tsv

    test_file.close()
    output.close()


# Open up training set, create decision tree
def main(train_f, image_f, test_f, output_f):
    data = open(train_f)
    moves = []
    rows = []

    # Create a 2D array to pass into the function which creates the tree
    for line in data:
        arr = line.rstrip().split('\t')
        moves.append(arr.pop(0))
        entry = convert_numeric(arr)  # Convert arr into integers where appropriate

        rows.append(entry)

    data.close()
    tree = dtree_build.buildtree(rows)
    dtree_draw.drawtree(tree, labels, jpeg=image_f)
    classify_moves(tree, test_f, output_f)


if __name__ == "__main__":
    main("../data/moves/TRAINING_MOVES.tsv", "../data/trees/MOVE_TREE.jpg",
         "../data/moves/TESTING_MOVES.tsv", "../data/moves/CLASSIFIED_MOVES.tsv")
