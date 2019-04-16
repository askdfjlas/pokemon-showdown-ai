# Code to generate decision tree from TRAINING_MOVES.tsv
import dtree_build, dtree_draw


# Attribute labels
labels = ["power", "activation chance", "poison", "to sleep", "paralyze", "burn", "confuse",
          "raise user", "raises user", "lower opponent", "lowers opponent", "attack", "special attack",
          "speed", "defense", "special defense", "evasiveness", "recover", "cure", "heal", "restore", "z-move"]


def main(input_f, image_f):
    data = open(input_f)
    moves = []
    rows = []

    for line in data:
        arr = line.rstrip().split('\t')
        moves.append(arr.pop(0))
        entry = []

        for element in arr:
            try:
                element = int(element)
            except ValueError:
                pass

            entry.append(element)

        rows.append(entry)

    tree = dtree_build.buildtree(rows)
    dtree_draw.drawtree(tree, labels, jpeg=image_f)


if __name__ == "__main__":
    main("../data/moves/TRAINING_MOVES.tsv", "../data/trees/MOVE_TREE.jpg")
