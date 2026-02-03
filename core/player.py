import time
from logic.stabilizer import Stabilizer
from logic.input_buffer import InputBuffer
from logic.abilities import AbilityType, COOLDOWNS

class Player:
    def __init__(self, player_id, roi):
        self.player_id = player_id
        self.roi = roi
        self.hp = 100
        self.max_hp = 100
        self.stabilizer = Stabilizer()
        self.input_buffer = InputBuffer()
        self.cooldowns = {
            AbilityType.FIREBALL: 0,
            AbilityType.WALL: 0,
            AbilityType.HEAVY_ATTACK: 0
        }
        # Center of ROI for collision detection
        self.center_x = roi.x + roi.w / 2
        self.center_y = roi.y + roi.h / 2
        self.current_sign = None # The currently detected sign (unstabilized)

    def update_cooldowns(self, dt):
        for ability in self.cooldowns:
            if self.cooldowns[ability] > 0:
                self.cooldowns[ability] -= dt
                if self.cooldowns[ability] < 0:
                    self.cooldowns[ability] = 0

    def can_cast(self, ability_type):
        return self.cooldowns.get(ability_type, 0) <= 0

    def start_cooldown(self, ability_type):
        self.cooldowns[ability_type] = COOLDOWNS.get(ability_type, 1.0)

    def take_damage(self, amount):
        self.hp -= amount
        if self.hp < 0:
            self.hp = 0

    def reset(self):
        self.hp = 100
        self.input_buffer.clear()
        for ability in self.cooldowns:
            self.cooldowns[ability] = 0
