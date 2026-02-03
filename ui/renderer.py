import pygame
import cv2
import numpy as np
from core.game_manager import GameState

class Renderer:
    def __init__(self, width=1280, height=720):
        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Ninja Duel: Cloud9 x JetBrains")
        self.font_large = pygame.font.SysFont("Arial", 64, bold=True)
        self.font_small = pygame.font.SysFont("Arial", 24)
        self.width = width
        self.height = height

    def render(self, frame, game_manager):
        # Convert OpenCV frame (BGR) to Pygame surface (RGB)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = np.rot90(frame)
        frame = cv2.flip(frame, 0)
        surface = pygame.surfarray.make_surface(frame)
        
        # Scale to screen if necessary
        if surface.get_size() != (self.width, self.height):
            surface = pygame.transform.scale(surface, (self.width, self.height))
            
        self.screen.blit(surface, (0, 0))

        # Draw ROI Boxes
        for player in game_manager.players.values():
            roi = player.roi
            color = (0, 255, 0) if player.player_id == 1 else (0, 0, 255)
            pygame.draw.rect(self.screen, color, (roi.x, roi.y, roi.w, roi.h), 3)
            
            # Draw HP Bar
            self.draw_hp_bar(player)
            
            # Draw Cooldowns
            self.draw_cooldowns(player)

            # Draw Current Sign
            self.draw_current_sign(player)

        # Draw Projectiles
        for p in game_manager.combat_manager.projectiles:
            if p.ability_type == "heavy_attack":
                continue # Purple for Heavy Attack
            elif p.ability_type == "water_ball":
                color = (0, 0, 255) # Blue for Water Ball
            else:
                color = (255, 100, 0) # Fireball (Default)
            pygame.draw.circle(self.screen, color, (int(p.x), int(p.y)), p.radius)

        # Draw Walls
    #    for w in game_manager.combat_manager.walls:
    #         color = (100, 100, 255, 128) # Semi-transparent blue
    #         s = pygame.Surface((w.width, w.height), pygame.SRCALPHA)
    #         s.fill((100, 100, 255, 180))
    #         self.screen.blit(s, (w.x, w.y))
    
        # Game State Overlays
        if game_manager.state == GameState.START:
            self.draw_overlay("PRESS SPACE TO START", (255, 255, 255))
        elif game_manager.state == GameState.GAME_OVER:
            winner_text = f"PLAYER {game_manager.winner} WINS!"
            self.draw_overlay(winner_text, (255, 215, 0))
            sub_text = self.font_small.render("PRESS R TO RESTART", True, (255, 255, 255))
            self.screen.blit(sub_text, (self.width//2 - sub_text.get_width()//2, self.height//2 + 50))

        pygame.display.flip()

    def draw_hp_bar(self, player):
        roi = player.roi
        bar_w = 300
        bar_h = 20
        x = roi.x + (roi.w - bar_w) // 2
        y = roi.y - 40
        
        # Background
        pygame.draw.rect(self.screen, (100, 0, 0), (x, y, bar_w, bar_h))
        # Fill
        fill_w = int(bar_w * (player.hp / player.max_hp))
        pygame.draw.rect(self.screen, (0, 255, 0), (x, y, fill_w, bar_h))
        # Border
        pygame.draw.rect(self.screen, (255, 255, 255), (x, y, bar_w, bar_h), 2)
        
        label = self.font_small.render(f"P{player.player_id} HP: {int(player.hp)}", True, (255, 255, 255))
        self.screen.blit(label, (x, y - 30))

    def draw_cooldowns(self, player):
        roi = player.roi
        x = roi.x
        y = roi.y + roi.h + 10
        for i, (ability, cd) in enumerate(player.cooldowns.items()):
            color = (255, 255, 255) if cd <= 0 else (150, 150, 150)
            text = f"{ability.value}: {cd:.1f}s"
            img = self.font_small.render(text, True, color)
            self.screen.blit(img, (x, y + i * 25))

    def draw_current_sign(self, player):
        if player.current_sign:
            roi = player.roi
            text = f"SIGN: {player.current_sign.upper()}"
            color = (255, 255, 0) # Yellow for visibility
            img = self.font_small.render(text, True, color)
            
            # Position it inside or near the ROI
            x = roi.x + 5
            y = roi.y + 5
            self.screen.blit(img, (x, y))

    def draw_overlay(self, text, color):
        img = self.font_large.render(text, True, color)
        bg = pygame.Surface((img.get_width() + 40, img.get_height() + 40))
        bg.fill((0, 0, 0))
        bg.set_alpha(150)
        x = self.width // 2 - bg.get_width() // 2
        y = self.height // 2 - bg.get_height() // 2
        self.screen.blit(bg, (x, y))
        self.screen.blit(img, (self.width // 2 - img.get_width() // 2, self.height // 2 - img.get_height() // 2))

    def quit(self):
        pygame.quit()
