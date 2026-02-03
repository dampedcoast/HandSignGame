from enum import Enum

class AbilityType(Enum):
    FIREBALL = "fireball"
    WALL = "wall"
    HEAVY_ATTACK = "heavy_attack"
    WATER_BALL = "water_ball"

# Mapping sequences of signs to abilities
# Each sequence is a list of sign names (strings)
COMBOS = {
    AbilityType.WALL: ["hare", "snake"],
    AbilityType.FIREBALL: ["snake", "ram"],
    AbilityType.HEAVY_ATTACK: ["dragon", "dog"],
    AbilityType.WATER_BALL: ["hare", "ram"]
}

COOLDOWNS = {
    AbilityType.FIREBALL: 1.0,
    AbilityType.WALL: 3.0,
    AbilityType.HEAVY_ATTACK: 5.0,
    AbilityType.WATER_BALL: 1.0
}

def check_combo(sequence):
    # Check for the longest matching combo at the end of the sequence
    for ability, combo in sorted(COMBOS.items(), key=lambda x: len(x[1]), reverse=True):
        if len(sequence) >= len(combo):
            if sequence[-len(combo):] == combo:
                return ability
    return None
