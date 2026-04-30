import pygame
import sys
import random
import csv
import os

Width, Height = 800, 600
Frames = 60

Gravity = 0.5
JumpStrength = 15
MaxFall = 15
PlayerSpeed = 5

DashBoost = 18
DashDuration = 12
DashCooldown = 90

PlayerScale = (50, 70)
EnemyScale = (40, 40)
ExitScale = (40, 60)

PlatformColor = (100, 100, 100)
EnemyColor = (200, 0, 0)
ExitColor = (0, 220, 0)

PlatformGapMin = 70
PlatformGapMax = 130
NumberBasePlatforms = 8

CsvPath = "docs/Csv/stats.csv"

wins = 0
deaths = 0

pygame.init()
font = pygame.font.SysFont(None, 30)


def log_event(event_type):
    file_exists = os.path.isfile(CsvPath)

    # FIX: ensure folder exists
    os.makedirs(os.path.dirname(CsvPath), exist_ok=True)

    with open(CsvPath, "a", newline="") as f:
        writer = csv.writer(f)

        if not file_exists:
            writer.writerow(["event", "wins", "deaths"])

        writer.writerow([event_type, wins, deaths])


def load_image(path, scale, fallback_color):
    try:
        img = pygame.image.load(path).convert_alpha()
        return pygame.transform.scale(img, scale)
    except:
        surf = pygame.Surface(scale)
        surf.fill(fallback_color)
        return surf


Background = load_image("docs/Frames/BG.png", (Width, Height), (20, 20, 40))


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        self.idle = load_image("docs/Frames/Idle.png", PlayerScale, (0,100,255))
        self.walk = [
            load_image("docs/Frames/WalkCharacter.png", PlayerScale, (0,100,255)),
            load_image("docs/Frames/WalkCharacter2.png", PlayerScale, (0,100,255))
        ]
        self.jump_img = load_image("docs/Frames/Jump.png", PlayerScale, (0,100,255))
        self.dash_img = load_image("docs/Frames/Dash.png", PlayerScale, (0,100,255))

        self.walk_l = [pygame.transform.flip(f, True, False) for f in self.walk]
        self.idle_l = pygame.transform.flip(self.idle, True, False)
        self.jump_l = pygame.transform.flip(self.jump_img, True, False)
        self.dash_l = pygame.transform.flip(self.dash_img, True, False)

        self.image = self.idle
        self.rect = self.image.get_rect(topleft=(120, Height - 120))

        self.vel_y = 0
        self.on_ground = False
        self.jumps = 2
        self.coyote_timer = 0

        self.facing_right = True
        self.walk_index = 0
        self.walk_timer = 0

        self.dash_timer = 0
        self.dash_cd = 0
        self.dash_vel = 0

    def update(self, dx, platforms, enemies):

        if self.dash_cd > 0:
            self.dash_cd -= 1
        if self.dash_timer > 0:
            self.dash_timer -= 1
        else:
            self.dash_vel = 0

        if dx > 0: self.facing_right = True
        if dx < 0: self.facing_right = False

        if self.dash_timer > 0:
            self.image = self.dash_img if self.facing_right else self.dash_l
        elif not self.on_ground:
            self.image = self.jump_img if self.facing_right else self.jump_l
        elif dx != 0:
            self.walk_timer += abs(dx)
            if self.walk_timer >= 10:
                self.walk_timer = 0
                self.walk_index = (self.walk_index + 1) % len(self.walk)

            frames = self.walk if self.facing_right else self.walk_l
            self.image = frames[self.walk_index]
        else:
            self.image = self.idle if self.facing_right else self.idle_l

        # FIXED movement
        move_x = dx + self.dash_vel
        self.rect.x += move_x

        for p in pygame.sprite.spritecollide(self, platforms, False):
            if move_x > 0:
                self.rect.right = p.rect.left
            elif move_x < 0:
                self.rect.left = p.rect.right

        if self.dash_timer > 0:
            self.vel_y = 0
        else:
            self.vel_y += Gravity

        if self.vel_y > MaxFall:
            self.vel_y = MaxFall

        self.rect.y += self.vel_y
        self.on_ground = False

        for p in pygame.sprite.spritecollide(self, platforms, False):

            # FIX: hazard always deadly
            if p.kind == "hazard":
                pygame.time.delay(80)
                self.reset()
                return

            if self.vel_y > 0:
                self.rect.bottom = p.rect.top
                self.vel_y = 0
                self.jumps = 2
                self.on_ground = True
            elif self.vel_y < 0:
                self.rect.top = p.rect.bottom
                self.vel_y = 0

        if self.on_ground:
            self.coyote_timer = 6
        else:
            self.coyote_timer -= 1

        for e in pygame.sprite.spritecollide(self, enemies, False):
            # FIXED stomp detection
            if self.vel_y > 0 and self.rect.centery < e.rect.centery:
                e.kill()
                self.vel_y = -10
            else:
                pygame.time.delay(80)
                self.reset()

        if self.rect.bottom >= Height:
            self.rect.bottom = Height
            self.vel_y = 0
            self.on_ground = True
            self.jumps = 2

        self.rect.left = max(0, self.rect.left)
        self.rect.right = min(Width, self.rect.right)

    def jump(self):
        if self.jumps > 0 or self.coyote_timer > 0:
            self.vel_y = -JumpStrength
            self.jumps -= 1
            self.on_ground = False

    def dash(self):
        if self.dash_cd == 0:
            self.dash_timer = DashDuration
            self.dash_cd = DashCooldown
            self.dash_vel = DashBoost if self.facing_right else -DashBoost

    def reset(self):
        global deaths
        deaths += 1
        log_event("death")

        self.rect.topleft = (120, Height - 120)
        self.vel_y = 0
        self.jumps = 2

        # FIX: reset dash state
        self.dash_timer = 0
        self.dash_cd = 0
        self.dash_vel = 0
        self.on_ground = False


class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h, kind="normal"):
        super().__init__()
        self.kind = kind

        color = (255,80,80) if kind == "hazard" else PlatformColor
        self.image = load_image("docs/Frames/Platform.png", (w, h), color)
        self.rect = self.image.get_rect(topleft=(x, y))

        if kind == "moving":
            self.start_x = x
            self.range = random.randint(60, 140)
            self.speed = random.choice([-2, 2])

    def update(self):
        if self.kind == "moving":
            self.rect.x += self.speed
            if abs(self.rect.x - self.start_x) > self.range:
                self.speed *= -1


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = load_image("docs/Frames/SpikyGuy.png", EnemyScale, EnemyColor)
        self.rect = self.image.get_rect(topleft=(x,y))
        self.vel = random.choice([-3,3])

    def update(self):
        self.rect.x += self.vel
        if self.rect.left < 0 or self.rect.right > Width:
            self.vel *= -1


class Exit(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = load_image("docs/Frames/Pizza.png", ExitScale, ExitColor)
        self.rect = self.image.get_rect(topleft=(x,y))


screen = pygame.display.set_mode((Width, Height))
clock = pygame.time.Clock()

platforms = pygame.sprite.Group()
enemies = pygame.sprite.Group()
exit_group = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()


def regenerate():
    global player

    platforms.empty()
    enemies.empty()
    exit_group.empty()
    all_sprites.empty()

    player = Player()
    all_sprites.add(player)

    ground = Platform(0, Height-40, Width, 40)
    platforms.add(ground)
    all_sprites.add(ground)

    y = Height - 120
    prev_x = Width // 2
    created_platforms = []

    for _ in range(NumberBasePlatforms):
        x = prev_x + random.randint(-80, 80)
        x = max(40, min(Width-160, x))
        prev_x = x

        kind = random.choice(["normal", "normal", "moving", "hazard"])

        p = Platform(x, y, random.randint(100,200), 20, kind)
        platforms.add(p)
        all_sprites.add(p)
        created_platforms.append(p)

        y -= random.randint(PlatformGapMin, PlatformGapMax)
        if y < 80:
            break

    for _ in range(4):
        e = Enemy(random.randint(0,Width-50), random.randint(0,Height-200))
        enemies.add(e)
        all_sprites.add(e)

    top = min(created_platforms, key=lambda p: p.rect.y)
    ex = Exit(top.rect.centerx, top.rect.y - 60)
    exit_group.add(ex)
    all_sprites.add(ex)


regenerate()

while True:
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_SPACE:
                player.jump()
            if e.key == pygame.K_x:
                player.dash()

    keys = pygame.key.get_pressed()
    dx = (keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]) * PlayerSpeed

    player.update(dx, platforms, enemies)
    enemies.update()
    platforms.update()

    if pygame.sprite.spritecollideany(player, exit_group):
        wins += 1
        log_event("win")
        regenerate()

    screen.blit(Background, (0,0))
    all_sprites.draw(screen)

    text = font.render(f"Wins: {wins}  Deaths: {deaths}", True, (255,255,255))
    screen.blit(text, (10, 10))

    pygame.display.flip()
    clock.tick(Frames)