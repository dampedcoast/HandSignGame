# main.py
# PNG projectiles:
# - Fireball: P1->P2 uses fireball.png, P2->P1 uses fireball2.png
# - Heavy Attack: both directions use heavyattack.png
# - Water Ball: both directions use WaterBall.png
# Wall: skeleton_nobg.gif (green-screen keyed)

import os
import cv2
import pygame
import time

from cv.camera import Camera
from cv.yolo_detector import YOLODetector
from core.game_manager import GameManager, GameState
from ui.renderer import Renderer
from logic.abilities import AbilityType

from ui.vfx_overlay import overlay_png_at_point, overlay_gif_greenscreen_at_point
from ui.vfx_gif import GifVFX


def load_sound(path: str, volume: float = 1.0):
    try:
        s = pygame.mixer.Sound(path)
        s.set_volume(volume)
        return s
    except Exception as e:
        print(f"[WARN] Could not load sound: {path} ({e})")
        return None


def play_sound(sound):
    if sound is not None:
        sound.play()


def roi_center(rx1, ry1, rx2, ry2):
    return (int((rx1 + rx2) / 2), int((ry1 + ry2) / 2))


class PNGProjectile:
    def __init__(self, png_bgra, start_pos, end_pos, travel_time=0.6, size_px=260, alpha=1.0):
        self.png = png_bgra
        self.start = start_pos
        self.end = end_pos
        self.travel_time = max(0.05, float(travel_time))
        self.size_px = int(size_px)
        self.alpha = float(alpha)

        self.t0 = time.time()
        self.done = False
        self.pos = start_pos

    def update(self):
        if self.done:
            return False

        t = (time.time() - self.t0) / self.travel_time
        if t >= 1.0:
            t = 1.0
            self.done = True

        x = int(self.start[0] + (self.end[0] - self.start[0]) * t)
        y = int(self.start[1] + (self.end[1] - self.start[1]) * t)
        self.pos = (x, y)
        return True


def main():
    WIDTH, HEIGHT = 1280, 720
    FPS = 30
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    # ---- Audio init ----
    pygame.mixer.pre_init(44100, -16, 2, 512)
    pygame.init()
    pygame.mixer.init()

    BG_VOL = 0.7
    SFX_VOL = 0.95

    bg_music_path = os.path.join(BASE_DIR, "sound_Effects", "background_music.mp3")

    fire_sfx = load_sound(os.path.join(BASE_DIR, "sound_Effects", "fire_sound.mp3"), volume=SFX_VOL)
    water_sfx = load_sound(os.path.join(BASE_DIR, "sound_Effects", "water_sound.mp3"), volume=SFX_VOL)
    heavy_sfx = load_sound(os.path.join(BASE_DIR, "sound_Effects", "heavy_sound.mp3"), volume=SFX_VOL)
    wall_sfx = load_sound(os.path.join(BASE_DIR, "sound_Effects", "earth_sound.mp3"), volume=SFX_VOL)

    print("[INFO] Sounds loaded:",
          "fire", fire_sfx is not None,
          "water", water_sfx is not None,
          "heavy", heavy_sfx is not None,
          "wall", wall_sfx is not None)

    # ---- Game components ----
    camera = Camera(width=WIDTH, height=HEIGHT)

    model_path = os.path.join(BASE_DIR, "model", "best.pt")
    detector = YOLODetector(model_path=model_path, confidence=0.5)

    game_manager = GameManager(frame_width=WIDTH, frame_height=HEIGHT)
    renderer = Renderer(width=WIDTH, height=HEIGHT)

    # ==========================================================
    # PNG PROJECTILES (load once)
    # ==========================================================
    fireball1_path = os.path.join(BASE_DIR, "assets", "vfx", "fireball.png")
    fireball2_path = os.path.join(BASE_DIR, "assets", "vfx", "fireball2.png")
    heavy_path = os.path.join(BASE_DIR, "assets", "vfx", "heavyattack.png")
    water_path = os.path.join(BASE_DIR, "assets", "vfx", "WaterBall.png")  # case-sensitive on some systems

    fireball1_png = cv2.imread(fireball1_path, cv2.IMREAD_UNCHANGED)  # BGRA
    fireball2_png = cv2.imread(fireball2_path, cv2.IMREAD_UNCHANGED)  # BGRA
    heavy_png = cv2.imread(heavy_path, cv2.IMREAD_UNCHANGED)          # BGRA
    water_png = cv2.imread(water_path, cv2.IMREAD_UNCHANGED)          # BGRA

    print("[INFO] fireball.png loaded?", fireball1_png is not None, fireball1_path)
    print("[INFO] fireball2.png loaded?", fireball2_png is not None, fireball2_path)
    print("[INFO] heavyattack.png loaded?", heavy_png is not None, heavy_path)
    print("[INFO] WaterBall.png loaded?", water_png is not None, water_path)

    # Tunings
    FIREBALL_SIZE = 260
    FIREBALL_TRAVEL_TIME = 0.6

    HEAVY_SIZE = 300
    HEAVY_TRAVEL_TIME = 0.35

    WATER_SIZE = 240
    WATER_TRAVEL_TIME = 0.55

    projectiles = []  # list[PNGProjectile]

    # ==========================================================
    # WALL: Skeleton GIF (green-screen keyed)
    # ==========================================================
    skeleton_gif_path = os.path.join(BASE_DIR, "assets", "vfx", "skeleton_nobg.gif")
    print("[INFO] Skeleton GIF exists?", os.path.exists(skeleton_gif_path), skeleton_gif_path)

    skeleton_active_until = {1: 0.0, 2: 0.0}
    skeleton_anim = {1: None, 2: None}
    SKELETON_SIZE = 420
    SKELETON_DURATION = 5.0
    GREEN_TOL = 90  # tweak 70-130

    # ==========================================================
    # Positions for VFX
    # ==========================================================
    last_hand_center = {1: None, 2: None}
    last_body_center = {1: None, 2: None}

    # ---- Wrap trigger_ability to play SFX + spawn VFX ----
    _original_trigger = game_manager.trigger_ability

    def spawn_fireball_png(caster_id: int):
        target_id = 2 if caster_id == 1 else 1
        start = last_hand_center.get(caster_id)
        end = last_body_center.get(target_id)
        if start is None or end is None:
            print(f"[VFX] Missing positions start={start} end={end}, cannot spawn fireball")
            return

        end = (end[0], end[1] - 60)
        png = fireball1_png if caster_id == 1 else fireball2_png
        if png is None:
            print("[VFX] Fireball PNG missing (fireball.png/fireball2.png)")
            return

        projectiles.append(PNGProjectile(
            png_bgra=png,
            start_pos=start,
            end_pos=end,
            travel_time=FIREBALL_TRAVEL_TIME,
            size_px=FIREBALL_SIZE,
            alpha=1.0
        ))

    def spawn_heavy_png(caster_id: int):
        target_id = 2 if caster_id == 1 else 1
        start = last_hand_center.get(caster_id)
        end = last_body_center.get(target_id)
        if start is None or end is None:
            print(f"[VFX] Missing positions start={start} end={end}, cannot spawn heavy")
            return

        end = (end[0], end[1] - 40)
        if heavy_png is None:
            print("[VFX] heavyattack.png missing")
            return

        projectiles.append(PNGProjectile(
            png_bgra=heavy_png,
            start_pos=start,
            end_pos=end,
            travel_time=HEAVY_TRAVEL_TIME,
            size_px=HEAVY_SIZE,
            alpha=1.0
        ))

    def spawn_water_png(caster_id: int):
        target_id = 2 if caster_id == 1 else 1
        start = last_hand_center.get(caster_id)
        end = last_body_center.get(target_id)
        if start is None or end is None:
            print(f"[VFX] Missing positions start={start} end={end}, cannot spawn water")
            return

        end = (end[0], end[1] - 50)
        if water_png is None:
            print("[VFX] WaterBall.png missing")
            return

        projectiles.append(PNGProjectile(
            png_bgra=water_png,
            start_pos=start,
            end_pos=end,
            travel_time=WATER_TRAVEL_TIME,
            size_px=WATER_SIZE,
            alpha=1.0
        ))

    def start_skeleton_wall(player_id: int):
        if not os.path.exists(skeleton_gif_path):
            return
        skeleton_active_until[player_id] = time.time() + SKELETON_DURATION
        skeleton_anim[player_id] = GifVFX(skeleton_gif_path, loop=True, fps=30)

    def trigger_with_sound_and_vfx(player, ability):
        # ---- sound ----
        if ability == AbilityType.FIREBALL:
            play_sound(fire_sfx)
        elif ability == AbilityType.WATER_BALL:
            play_sound(water_sfx)
        elif ability == AbilityType.HEAVY_ATTACK:
            play_sound(heavy_sfx)
        elif ability == AbilityType.WALL:
            play_sound(wall_sfx)

        # ---- game logic ----
        result = _original_trigger(player, ability)

        # ---- caster id ----
        caster_id = getattr(player, "player_id", None) or getattr(player, "id", None)
        if caster_id is None:
            caster_id = 1 if player is game_manager.players[1] else 2
        caster_id = int(caster_id)

        # ---- VFX ----
        if ability == AbilityType.FIREBALL:
            spawn_fireball_png(caster_id)
        elif ability == AbilityType.HEAVY_ATTACK:
            spawn_heavy_png(caster_id)
        elif ability == AbilityType.WATER_BALL:
            spawn_water_png(caster_id)
        elif ability == AbilityType.WALL:
            start_skeleton_wall(caster_id)

        return result

    game_manager.trigger_ability = trigger_with_sound_and_vfx

    # ---- Background music control ----
    music_started = False

    def start_background_music():
        nonlocal music_started
        if music_started:
            return
        try:
            pygame.mixer.music.load(bg_music_path)
            pygame.mixer.music.set_volume(BG_VOL)
            pygame.mixer.music.play(-1)
            music_started = True
            print("[INFO] Background music started:", bg_music_path)
        except Exception as e:
            print(f"[WARN] Could not start background music: {bg_music_path} ({e})")

    def stop_background_music():
        nonlocal music_started
        if music_started:
            pygame.mixer.music.stop()
            music_started = False

    # ---- Main loop ----
    clock = pygame.time.Clock()
    last_time = time.time()
    last_state = game_manager.state

    running = True
    while running:
        dt = time.time() - last_time
        last_time = time.time()

        # music transitions
        if game_manager.state != last_state:
            if game_manager.state == GameState.PLAYING:
                start_background_music()
            elif game_manager.state in (GameState.GAME_OVER, GameState.START):
                stop_background_music()
            last_state = game_manager.state

        frame = camera.get_frame()
        if frame is None:
            break

        # ---------------------------
        # YOLO only while playing
        # ---------------------------
        if game_manager.state == GameState.PLAYING:
            p1_sign = None
            p2_sign = None

            for player_id, player in game_manager.players.items():
                roi = player.roi
                rx1, ry1 = max(0, int(roi.x)), max(0, int(roi.y))
                rx2, ry2 = min(WIDTH, int(roi.x + roi.w)), min(HEIGHT, int(roi.y + roi.h))
                if rx2 <= rx1 or ry2 <= ry1:
                    continue

                # body center always available
                last_body_center[player_id] = roi_center(rx1, ry1, rx2, ry2)

                roi_frame = frame[ry1:ry2, rx1:rx2]
                detections = detector.detect(roi_frame)

                if detections:
                    best = max(detections, key=lambda d: d["conf"])
                    label = best.get("label")

                    if player_id == 1:
                        p1_sign = label
                    else:
                        p2_sign = label

                    # bbox is XYXY (from your prints)
                    if "bbox" in best and best["bbox"] is not None:
                        bx1, by1, bx2, by2 = best["bbox"]  # xyxy ROI coords
                        fx1, fy1 = rx1 + bx1, ry1 + by1
                        fx2, fy2 = rx1 + bx2, ry1 + by2
                        last_hand_center[player_id] = (int((fx1 + fx2) / 2), int((fy1 + fy2) / 2))
                    else:
                        last_hand_center[player_id] = last_body_center[player_id]

            game_manager.process_hand_sign(1, p1_sign)
            game_manager.process_hand_sign(2, p2_sign)

        # ---------------------------
        # Events
        # ---------------------------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

                # Start / Restart
                if game_manager.state == GameState.START and event.key == pygame.K_SPACE:
                    game_manager.start_game()
                elif game_manager.state == GameState.GAME_OVER and event.key == pygame.K_r:
                    game_manager.start_game()

                # Keyboard abilities (sound+vfx handled in wrapper)
                if game_manager.state == GameState.PLAYING:
                    # Player 1
                    if event.key == pygame.K_1:
                        game_manager.trigger_ability(game_manager.players[1], AbilityType.FIREBALL)
                    elif event.key == pygame.K_2:
                        game_manager.trigger_ability(game_manager.players[1], AbilityType.WALL)
                    elif event.key == pygame.K_3:
                        game_manager.trigger_ability(game_manager.players[1], AbilityType.HEAVY_ATTACK)
                    elif event.key == pygame.K_4:
                        game_manager.trigger_ability(game_manager.players[1], AbilityType.WATER_BALL)

                    # Player 2
                    if event.key == pygame.K_8:
                        game_manager.trigger_ability(game_manager.players[2], AbilityType.FIREBALL)
                    elif event.key == pygame.K_9:
                        game_manager.trigger_ability(game_manager.players[2], AbilityType.WALL)
                    elif event.key == pygame.K_0:
                        game_manager.trigger_ability(game_manager.players[2], AbilityType.HEAVY_ATTACK)
                    elif event.key == pygame.K_MINUS:
                        game_manager.trigger_ability(game_manager.players[2], AbilityType.WATER_BALL)

        game_manager.update(dt)

        # ---------------------------
        # Draw PNG projectiles (fireball + heavy + water)
        # ---------------------------
        alive = []
        for proj in projectiles:
            if not proj.update():
                continue

            frame = overlay_png_at_point(
                base_bgr=frame,
                png_bgra=proj.png,
                center_xy=proj.pos,
                size_px=proj.size_px,
                alpha=proj.alpha
            )
            alive.append(proj)
        projectiles = alive

        # ---------------------------
        # Draw Skeleton (WALL)
        # ---------------------------
        now = time.time()
        for pid in (1, 2):
            if skeleton_anim[pid] is None:
                continue
            if now > skeleton_active_until[pid]:
                skeleton_anim[pid] = None
                continue

            eff_frame = skeleton_anim[pid].update()
            if eff_frame is None:
                skeleton_anim[pid] = None
                continue

            pos = last_body_center.get(pid)
            if pos is None:
                continue

            frame = overlay_gif_greenscreen_at_point(
                base_bgr=frame,
                gif_bgr=eff_frame,
                center_xy=pos,
                size_px=SKELETON_SIZE,
                key_green=(0, 255, 0),
                tol=GREEN_TOL,
                alpha=1.0
            )

        renderer.render(frame, game_manager)
        clock.tick(FPS)

    camera.release()
    renderer.quit()
    pygame.mixer.music.stop()


if __name__ == "__main__":
    main()
