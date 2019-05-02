# Code to generate decision tree from TRAINING_SET.tsv
from dtree_to_json import *
import tsv_to_2d as tsv
import move_tree
import json

TRAINING_SET = "../data/learning/TRAINING_SET.tsv"

# Attribute labels
labels = ["cpc", "cph", "cps", "cpb_atk", "cpb_def", "cpb_spa", "cpb_spd", "cpb_spe",
          "opc", "oph", "ops", "opb_atk", "opb_def", "opb_spa", "opb_spd", "opb_spe",
          "b_sdp", "b_srp", "b_shp", "b_phys_wall", "b_spe_wall", "b_phys_attack",
          "b_spe_attack", "b_phys_sweep", "b_spe_sweep", "b_mdm", "b_mdm2", "b_pure_cripple",
          "b_offensive_cripple", "b_offensive_setup", "b_defensive_setup", "b_recovery", "b_z",
          "b_situational", "b_pure_offense", "forced swap", "remaining poke", "faster",
          "mdm_dmg", "mdm_hp", "mdm2_dmg", "mdm2_hp", "mdm_dmg_srp", "mdm_hp_srp",
          "mdm2_dmg_srp", "mdm2_hp_srp", "o_mdm_dmg", "o_mdm_hp", "o_mdm2_dmg", "o_mdm2_hp",
          "o_mdm_dmg_srp", "o_mdm_hp_srp", "o_mdm2_dmg_srp", "o_mdm2_hp_srp"]


# Open up training set, create decision tree
def main(json_f):
    rows = tsv.get_list(TRAINING_SET)
    for i in range(len(rows)):
        # Convert to numeric, then pop the Pokemon name
        rows[i] = move_tree.convert_numeric(rows[i])

    tree = dtree_build.buildtree(rows, min_samples=30, min_gain=0)
    json_tree = dtree_to_jsontree(tree, labels)

    # create json data for d3.js interactive visualization
    with open(json_f, "w") as write_file:
        json.dump(json_tree, write_file)

    return tree


if __name__ == "__main__":
    main("../data/learning/MAIN_TREE.json")
