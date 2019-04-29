# Code to generate decision tree from TRAINING_POKEMON.tsv
import dtree_build
import dtree_draw
import tsv_to_2d as tsv
import move_tree


# Attribute labels
labels = ["hp", "atk", "def", "spa", "spdef", "spd", "ev hp", "ev atk",
          "ev def", "ev spa", "ev spdef", "ev spd", "pure offensive",
          "pure cripple", "offensive cripple", "offensive setup", "defensive setup",
          "recovery", "status", "z-move", "situational"]


# Open up the test set, classify them, and write them to the output tsv
def classify_pokemon(tree, test_f, output_f):
    entries = tsv.get_list(test_f)
    output = open(output_f, "w")

    for entry in entries:
        poke = entry.pop(0)
        entry = move_tree.convert_numeric(entry)
        node = dtree_build.classify(entry, tree)  # Classify the row

        poke_class = ""
        for k in node:  # There are no non-pure nodes, so this works.
            poke_class = k

        output.write(poke+ '\t' + poke_class + '\n')  # Store as (move name, class) in .tsv


# Open up training set, create decision tree
def main(train_f, image_f, test_f, output_f):
    rows = tsv.get_list(train_f)
    for i in range(len(rows)):
        # Convert to numeric, then pop the Pokemon name
        rows[i] = move_tree.convert_numeric(rows[i])
        rows[i].pop(0)

    tree = dtree_build.buildtree(rows)
    dtree_draw.drawtree(tree, labels, jpeg=image_f)
    classify_pokemon(tree, test_f, output_f)


if __name__ == "__main__":
    main("../data/pokemon/TRAINING_POKEMON.tsv", "../data/trees/POKEMON_TREE.jpg",
         "../data/pokemon/TESTING_POKEMON.tsv", "../data/pokemon/CLASSIFIED_POKEMON.tsv")
