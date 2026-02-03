import time

class Projectile:
    def __init__(self, x, y, direction, speed, damage, owner_id, ability_type=None):
        self.x = x
        self.y = y
        self.direction = direction # 1 for right, -1 for left
        self.speed = speed
        self.damage = damage
        self.owner_id = owner_id
        self.active = True
        self.radius = 20
        self.ability_type = ability_type

    def update(self, dt):
        self.x += self.direction * self.speed * dt
        # Simple boundary check
        if self.x < 0 or self.x > 2000: # Assuming 1280 wide, but some buffer
            self.active = False

class Wall:
    def __init__(self, x, y, owner_id, duration=2.0):
        self.x = x
        self.y = y
        self.owner_id = owner_id
        self.start_time = time.time()
        self.duration = duration
        self.active = True
        self.width = 40
        self.height = 150

    def update(self):
        if time.time() - self.start_time >= self.duration:
            self.active = False

class CombatManager:
    def __init__(self):
        self.projectiles = []
        self.walls = []

    def spawn_projectile(self, x, y, direction, ability_type, owner_id):
        if ability_type == "fireball":
            self.projectiles.append(Projectile(x, y, direction, speed=600, damage=10, owner_id=owner_id, ability_type=ability_type))
        elif ability_type == "heavy_attack":
            self.projectiles.append(Projectile(x, y, direction, speed=400, damage=25, owner_id=owner_id, ability_type=ability_type))
        elif ability_type == "water_ball":
            self.projectiles.append(Projectile(x, y, direction, speed=600, damage=10, owner_id=owner_id, ability_type=ability_type))

    def spawn_wall(self, x, y, owner_id):
        self.walls.append(Wall(x, y, owner_id))

    def update(self, dt, players):
        # Update projectiles
        for p in self.projectiles:
            if not p.active: continue
            p.update(dt)
            
            # Check collisions with other projectiles
            for other_p in self.projectiles:
                if not other_p.active or p == other_p: continue
                if p.owner_id != other_p.owner_id:
                    # Fireball and Waterball block each other
                    if (p.ability_type == "fireball" and other_p.ability_type == "water_ball") or \
                       (p.ability_type == "water_ball" and other_p.ability_type == "fireball"):
                        dist = ((p.x - other_p.x)**2 + (p.y - other_p.y)**2)**0.5
                        if dist < (p.radius + other_p.radius):
                            p.active = False
                            other_p.active = False
                            break
            
            if not p.active: continue

            # Check collisions with walls
            for w in self.walls:
                if not w.active: continue
                if w.owner_id != p.owner_id:
                    # Simple AABB check for wall and point/circle for projectile
                    if (w.x - 20 <= p.x <= w.x + w.width + 20 and
                        w.y <= p.y <= w.y + w.height):
                        p.active = False
                        w.active = False # Wall blocks one fireball
                        break
            
            if not p.active: continue
            
            # Check collisions with players
            for player_id, player in players.items():
                if player_id != p.owner_id:
                    # Player hit box (approximate center of ROI)
                    # We'll use the ROI center from player object later
                    dist_x = abs(p.x - player.center_x)
                    dist_y = abs(p.y - player.center_y)
                    if dist_x < 50 and dist_y < 100:
                        player.take_damage(p.damage)
                        p.active = False
                        break

        # Update walls
        for w in self.walls:
            if w.active:
                w.update()

        # Cleanup
        self.projectiles = [p for p in self.projectiles if p.active]
        self.walls = [w for w in self.walls if w.active]
