# Pokemon and related entities
from enum import Enum


# Class for an EV investment
class EV:
    def __init__(self, arr):
        self.hp = arr[0]
        self.attack = arr[1]
        self.defense = arr[2]
        self.sp_attack = arr[3]
        self.sp_defense = arr[4]
        self.speed = arr[5]


class Status(Enum):
    # Enum for status effects (ignoring confuse for now)
    Healthy = 0
    Poison = 1
    Toxic = 2
    Burn = 3
    Paralyze = 4
    Sleep = 5
    Freeze = 6


class Move:
    def __init__(self, arr):
        self.name = arr[0]
        self.type = arr[1]
        self.category = arr[2]
        self.bp = arr[3]


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
        if "Hidden Power" in move:
            move = "Hidden Power"
        if move not in self.moves and move != "None":
            self.moves.append(move)

    def set_types(self, t):
        self.type1 = t[0]
        self.type2 = t[1] if t[1] != "None" else None

    def set_ability(self, s):
        self.ability = s

    def set_item(self, b):
        self.item = b

    def set_hp(self, i):
        if self.maxHP is None:
            self.maxHP = i

    def set_stats(self, arr):
        if self.maxHP is None:
            self.set_hp(int(arr[0]))
            self.attack = int(arr[1])
            self.defense = int(arr[2])
            self.sp_attack = int(arr[3])
            self.sp_defense = int(arr[4])
            self.speed = int(arr[5])
