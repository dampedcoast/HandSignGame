from enum import Enum
from core.player import Player
from cv.roi import get_default_rois
from logic.combat import CombatManager
from logic.abilities import check_combo, AbilityType

class GameState(Enum):
    START = 1
    PLAYING = 2
    GAME_OVER = 3

class GameManager:
    def __init__(self, frame_width=1280, frame_height=720):
        self.state = GameState.START
        rois = get_default_rois(frame_width, frame_height)
        self.players = {
            1: Player(1, rois[0]),
            2: Player(2, rois[1])
        }
        self.combat_manager = CombatManager()
        self.winner = None

    def update(self, dt):
        if self.state == GameState.PLAYING:
            # Update players
            for p in self.players.values():
                p.update_cooldowns(dt)
            
            # Update combat
            self.combat_manager.update(dt, self.players)
            
            # Check win condition
            if self.players[1].hp <= 0:
                self.winner = 2
                self.state = GameState.GAME_OVER
            elif self.players[2].hp <= 0:
                self.winner = 1
                self.state = GameState.GAME_OVER

    def process_hand_sign(self, player_id, sign):
        if self.state != GameState.PLAYING:
            return

        player = self.players.get(player_id)
        if not player:
            return

        player.current_sign = sign
        stabilized_sign = player.stabilizer.update(sign)
        if stabilized_sign:
            player.input_buffer.add_sign(stabilized_sign)
            sequence = player.input_buffer.get_sequence()
            ability = check_combo(sequence)
            
            if ability:
                self.trigger_ability(player, ability)
                player.input_buffer.clear()

    def trigger_ability(self, player, ability):
        if player.can_cast(ability):
            player.start_cooldown(ability)
            direction = 1 if player.player_id == 1 else -1
            
            # Spawn point: edge of player ROI towards opponent
            spawn_x = player.roi.x + player.roi.w if player.player_id == 1 else player.roi.x
            spawn_y = player.center_y
            
            if ability in [AbilityType.FIREBALL, AbilityType.HEAVY_ATTACK, AbilityType.WATER_BALL]:
                self.combat_manager.spawn_projectile(spawn_x, spawn_y, direction, ability.value, player.player_id)
            elif ability == AbilityType.WALL:
                # Wall spawns slightly ahead of player
                wall_x = spawn_x + (50 * direction)
                if player.player_id == 2: wall_x -= 40 # Adjust for wall width
                self.combat_manager.spawn_wall(wall_x, spawn_y - 75, player.player_id)

    def start_game(self):
        for p in self.players.values():
            p.reset()
        self.combat_manager.projectiles = []
        self.combat_manager.walls = []
        self.winner = None
        self.state = GameState.PLAYING

    def reset_to_start(self):
        self.state = GameState.START
