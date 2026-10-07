import math
import random
import pygame

WIDTH, HEIGHT = 800, 600
PLAYER_W, PLAYER_H = 20, 28
BARREL_R, BARREL_SPEED = 10, 140
WALK_SPEED, CLIMB_SPEED, JUMP_SPEED, GRAVITY = 170, 110, 380, 900
COYOTE_TIME, JUMP_BUFFER_TIME = 0.10, 0.12  # jump-forgiveness windows (seconds)
GIRDER_HALF_THICKNESS = 4  # platforms are drawn 8px thick
BG = (15, 15, 25)

# (x_left, x_right, y_at_left, y_at_right)
PLATFORMS = [
    (0, 800, 570, 570),
    (0, 740, 480, 505),
    (60, 800, 410, 385),
    (0, 740, 310, 330),
    (0, 600, 200, 200),
]
# (x, lower platform index, upper platform index)
LADDERS = [(650, 0, 1), (120, 1, 2), (640, 2, 3), (140, 3, 4)]
KONG_POS = (60, 200)
PRINCESS_POS = (540, 200)

POPUP_LIFETIME = 0.8  # seconds a floating label stays on screen
LAST_AWARD = [100]  # points given for the most recent barrel jump
POPUPS = []  # active floating labels: {"pos", "age", "text"}


def update_popups(dt):
    for popup in POPUPS:
        popup["age"] += dt
        popup["pos"].y -= 40 * dt
    POPUPS[:] = [p for p in POPUPS if p["age"] < POPUP_LIFETIME]


def platform_y(platform, x):
    x1, x2, y1, y2 = platform
    return y1 + (y2 - y1) * (x - x1) / (x2 - x1)


def theme_color(score):
    """Return an (r, g, b) background colour for the current score, or None for the default."""
    if score <= 0:
        return None
    warm = (70, 28, 18)  # warm dark red-orange reached at score 3000
    t = min(score / 3000, 1.0)
    return tuple(int(BG[i] + (warm[i] - BG[i]) * t) for i in range(3))


def on_barrel_jumped(player, barrel):
    """Called when the player clears a barrel; spawns a floating label with the points earned."""
    POPUPS.append({"pos": pygame.Vector2(barrel.pos), "age": 0.0, "text": f"+{LAST_AWARD[0]}"})


def score_multiplier(score):
    """Return a multiplier applied to points earned from clearing a barrel, or None for the default 1x."""
    if score >= 1000:
        return 2
    return None


class Player:
    def __init__(self):
        self.reset()

    def reset(self):
        self.pos = pygame.Vector2(40, PLATFORMS[0][2])
        self.vel = pygame.Vector2()
        self.on_ground = True
        self.ladder = None
        self.coyote = 0.0
        self.jump_buffer = 0.0

    def center(self):
        return pygame.Vector2(self.pos.x, self.pos.y - PLAYER_H / 2)

    def find_ladder(self, going_up):
        for index, (lx, lower, upper) in enumerate(LADDERS):
            top = platform_y(PLATFORMS[upper], lx)
            bottom = platform_y(PLATFORMS[lower], lx)
            if abs(self.pos.x - lx) > 10:
                continue
            if going_up and top + 2 < self.pos.y <= bottom + 3:
                return index
            if not going_up and top - 3 <= self.pos.y < bottom - 2:
                return index
        return None

    def jump(self):
        if self.ladder is not None:
            return
        if self.on_ground or self.coyote > 0:
            self.vel.y = -JUMP_SPEED
            self.on_ground = False
            self.coyote = 0.0
            self.jump_buffer = 0.0
        else:
            # Pressed slightly too early: remember it and jump on landing.
            self.jump_buffer = JUMP_BUFFER_TIME

    def update(self, dt, keys):
        self.coyote = max(0.0, self.coyote - dt)
        self.jump_buffer = max(0.0, self.jump_buffer - dt)
        self._move(dt, keys)
        if self.on_ground and self.ladder is None:
            self.coyote = COYOTE_TIME
            if self.jump_buffer > 0:
                self.jump()

    def _move(self, dt, keys):
        move = keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]
        vertical = keys[pygame.K_DOWN] - keys[pygame.K_UP]
        if self.ladder is None and vertical:
            found = self.find_ladder(going_up=vertical < 0)
            if found is not None:
                self.ladder = found
                self.pos.x = LADDERS[found][0]
                self.vel.update(0, 0)
                self.on_ground = False
        if self.ladder is not None:
            self.climb(dt, vertical)
            return
        self.pos.x = max(10, min(WIDTH - 10, self.pos.x + move * WALK_SPEED * dt))
        if self.on_ground and self.vel.y >= 0:
            for plat in PLATFORMS:
                if plat[0] <= self.pos.x <= plat[1]:
                    py = platform_y(plat, self.pos.x)
                    if abs(py - self.pos.y) <= 8:
                        self.pos.y = py
                        return
            self.on_ground = False
        previous = self.pos.y
        self.vel.y = min(self.vel.y + GRAVITY * dt, 700)
        self.pos.y += self.vel.y * dt
        if self.vel.y < 0:
            # Girders are solid from below: bump the head instead of jumping up through them,
            # so the only way up a level is the ladder.
            for plat in PLATFORMS:
                if plat[0] <= self.pos.x <= plat[1]:
                    ceiling = platform_y(plat, self.pos.x) + GIRDER_HALF_THICKNESS
                    if previous - PLAYER_H >= ceiling > self.pos.y - PLAYER_H:
                        self.pos.y = ceiling + PLAYER_H
                        self.vel.y = 0
                        break
        if self.vel.y >= 0:
            for plat in PLATFORMS:
                if plat[0] <= self.pos.x <= plat[1]:
                    py = platform_y(plat, self.pos.x)
                    if previous <= py + 3 and self.pos.y >= py:
                        self.pos.y = py
                        self.vel.y = 0
                        self.on_ground = True
                        break

    def climb(self, dt, vertical):
        lx, lower, upper = LADDERS[self.ladder]
        self.pos.y += vertical * CLIMB_SPEED * dt
        top = platform_y(PLATFORMS[upper], lx)
        bottom = platform_y(PLATFORMS[lower], lx)
        if self.pos.y <= top:
            self.pos.y = top
            self.ladder = None
            self.on_ground = True
        elif self.pos.y >= bottom:
            self.pos.y = bottom
            self.ladder = None
            self.on_ground = True


class Barrel:
    def __init__(self):
        self.plat = 4
        self.direction = 1
        self.ladder = None
        self.vy = 0
        self.scored = False
        self.skip = set()
        self.angle = 0.0
        self.pos = pygame.Vector2(KONG_POS[0] + 40, PLATFORMS[4][2] - BARREL_R)

    def update(self, dt):
        if self.ladder is not None:
            lx, lower, _ = LADDERS[self.ladder]
            self.pos.y += 90 * dt
            floor = platform_y(PLATFORMS[lower], lx)
            if self.pos.y + BARREL_R >= floor:
                self.plat = lower
                self.ladder = None
                self.pos.y = floor - BARREL_R
            return
        if self.plat is None:
            previous = self.pos.y + BARREL_R
            self.vy += GRAVITY * dt
            self.pos.y += self.vy * dt
            feet = self.pos.y + BARREL_R
            for index, plat in enumerate(PLATFORMS):
                if plat[0] <= self.pos.x <= plat[1]:
                    py = platform_y(plat, self.pos.x)
                    if previous <= py + 2 and feet >= py:
                        self.plat, self.vy = index, 0
                        self.pos.y = py - BARREL_R
                        break
            return
        plat = PLATFORMS[self.plat]
        slope = plat[3] - plat[2]
        if slope:
            self.direction = 1 if slope > 0 else -1
        old_x = self.pos.x
        self.pos.x += self.direction * BARREL_SPEED * dt
        self.angle += self.direction * BARREL_SPEED / BARREL_R * dt
        if not plat[0] <= self.pos.x <= plat[1]:
            self.plat, self.vy = None, 0
            return
        self.pos.y = platform_y(plat, self.pos.x) - BARREL_R
        for index, (lx, _, upper) in enumerate(LADDERS):
            # Detect "passed over the ladder this frame" so it works at any frame rate.
            crossed = (old_x - lx) * (self.pos.x - lx) <= 0
            if upper == self.plat and crossed and index not in self.skip:
                self.skip.add(index)
                if random.random() < 0.3:
                    self.ladder = index
                    self.pos.x = lx


def draw_scene(screen, font, player, barrels, score, lives, state):
    screen.fill(theme_color(score) or BG)
    for x1, x2, y1, y2 in PLATFORMS:
        pygame.draw.line(screen, (210, 55, 55), (x1, y1), (x2, y2), 8)
    for lx, lower, upper in LADDERS:
        top = platform_y(PLATFORMS[upper], lx)
        bottom = platform_y(PLATFORMS[lower], lx)
        pygame.draw.line(screen, (220, 190, 80), (lx - 8, top), (lx - 8, bottom), 3)
        pygame.draw.line(screen, (220, 190, 80), (lx + 8, top), (lx + 8, bottom), 3)
        for y in range(int(top) + 8, int(bottom), 12):
            pygame.draw.line(screen, (220, 190, 80), (lx - 8, y), (lx + 8, y), 2)
    pygame.draw.rect(screen, (150, 90, 40), (KONG_POS[0] - 25, KONG_POS[1] - 50, 50, 50))
    pygame.draw.circle(screen, (255, 150, 200), (PRINCESS_POS[0], PRINCESS_POS[1] - 14), 10)
    for barrel in barrels:
        cx, cy = round(barrel.pos.x), round(barrel.pos.y)
        pygame.draw.circle(screen, (170, 100, 40), (cx, cy), BARREL_R)
        spoke = (cx + math.cos(barrel.angle) * (BARREL_R - 2), cy + math.sin(barrel.angle) * (BARREL_R - 2))
        pygame.draw.line(screen, (90, 50, 20), (cx, cy), spoke, 2)
    body = pygame.Rect(0, 0, PLAYER_W, PLAYER_H)
    body.midbottom = (round(player.pos.x), round(player.pos.y))
    pygame.draw.rect(screen, (50, 180, 240), body)
    for popup in POPUPS:
        label = font.render(popup["text"], True, (255, 255, 120))
        label.set_alpha(int(255 * (1 - popup["age"] / POPUP_LIFETIME)))
        screen.blit(label, label.get_rect(center=(popup["pos"].x, popup["pos"].y - 20)))
    hud = font.render(f"Score {score}   Lives {lives}   R = reset", True, (240, 240, 240))
    screen.blit(hud, (10, 8))
    if state != "play":
        text = "YOU WIN! Press R" if state == "win" else "GAME OVER - Press R"
        label = font.render(text, True, (255, 255, 120))
        screen.blit(label, label.get_rect(center=(WIDTH // 2, HEIGHT // 2)))


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Donkey Kong")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 28)
    player, barrels = Player(), []
    score, lives, state, spawn_timer = 0, 3, "play", 1.0
    running = True
    while running:
        dt = min(clock.tick(60) / 1000, 0.05)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                if state == "play":
                    player.jump()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                player.reset()
                barrels.clear()
                POPUPS.clear()
                score, lives, state, spawn_timer = 0, 3, "play", 1.0
        update_popups(dt)
        if state == "play":
            player.update(dt, pygame.key.get_pressed())
            spawn_timer -= dt
            if spawn_timer <= 0:
                barrels.append(Barrel())
                spawn_timer = random.uniform(1.8, 3.2)
            for barrel in barrels:
                barrel.update(dt)
                hit_range = BARREL_R + PLAYER_W / 2
                if player.center().distance_squared_to(barrel.pos) < hit_range ** 2:
                    lives -= 1
                    player.reset()
                    barrels.clear()
                    spawn_timer = 1.0
                    state = "play" if lives > 0 else "lose"
                    break
                above = 0 < barrel.pos.y - player.pos.y + BARREL_R < 40
                if not player.on_ground and above and abs(barrel.pos.x - player.pos.x) < 12 and not barrel.scored:
                    barrel.scored = True
                    award = int(100 * (score_multiplier(score) or 1))
                    score += award
                    LAST_AWARD[0] = award
                    on_barrel_jumped(player, barrel)
            barrels[:] = [b for b in barrels if b.pos.y < HEIGHT + 30]
            if player.center().distance_to(pygame.Vector2(PRINCESS_POS)) < 24:
                score += 1000
                state = "win"
        draw_scene(screen, font, player, barrels, score, lives, state)
        pygame.display.flip()
    pygame.quit()


if __name__ == "__main__":
    main()