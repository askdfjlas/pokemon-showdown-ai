# Pokemon and related entities
from enum import Enum


class Status(Enum):
    # Enum for status effects (ignoring confuse for now)
    Healthy = 0
    Poison = 1
    Toxic = 2
    Burn = 3
    Paralyze = 4
    Sleep = 5
    Freeze = 6


class Pokemon:
    def __init__(self):
        self.name = None
        self.moves = []
        self.ability = None
        self.item = False

        # (Estimated) Stats
        self.maxHP = None
        self.attack = None
        self.defense = None
        self.sp_attack = None
        self.sp_defense = None
        self.speed = None
        self.type1 = None
        self.type2 = None

        # Game state
        self.currHP = None
        self.status = Status.Healthy
        self.fainted = False

    # A nice print method
    def __repr__(self):
        print_str = "\nName: " + self.name + '\n' + 15*'-' + "\nMoves:\n"

        for move in self.moves:
            print_str += move + '\n'

        print_str += 15*'-' + "\nAbility: " + str(self.ability) + "\nItem: " + str(self.item) + "\n"\
            + 15*'-' + '\n' + "HP: " + str(self.maxHP) + "\nAttack: " + str(self.attack) +\
            "\nDefense: " + str(self.defense) + "\nSp. Attack: " + str(self.sp_attack) +\
            "\nSp. Defense: " + str(self.sp_defense) + "\nSpeed: " + str(self.speed) + "\nType(s): " +\
            str(self.type1) + (" " + str(self.type2) if self.type2 is not None else "") + '\n' + 15*'-' +\
            "\nCurrent HP: " + str(self.currHP) + '/' + str(self.maxHP) + "\nStatus: " + \
            str(self.status) + "\nFainted: " + str(self.fainted) + '\n'

        return print_str

    # Setters
    def set_name(self, s):
        self.name = s

    def append_move(self, move):
        # If the move hasn't been used before
        if move not in self.moves:
            self.moves.append(move)

    def set_ability(self, s):
        self.ability = s

    def set_item(self, b):
        self.item = b

    def set_hp(self, i):
        self.maxHP = i
