import pygame
import sys
import random

# ---------------- SETTINGS ----------------
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

PlayerStart = (120, Height - 120)

pygame.init()

# ---------------- HELPERS ----------------
def load_image(path, scale, fallback_color):
    try:
        img = pygame.image.load(path).convert_alpha()
        return pygame.transform.scale(img, scale)
    except:
        surf = pygame.Surface(scale)
        surf.fill(fallback_color)
        return surf

# ---------------- PLAYER ----------------
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        # LOAD PNGs
        self.idle = load_image("docs/Frames/Idle.png", PlayerScale, (0,100,255))
        self.walk = [
            load_image("docs/Frames/WalkCharacter.png", PlayerScale, (0,100,255)),
            load_image("docs/Frames/WalkCharacter2.png", PlayerScale, (0,100,255))
        ]
        self.jump_img = load_image("docs/Frames/Jump.png", PlayerScale, (0,100,255))
        self.dash_img = load_image("docs/Frames/Dash.png", PlayerScale, (0,100,255))

        # FLIP
        self.walk_l = [pygame.transform.flip(f, True, False) for f in self.walk]
        self.idle_l = pygame.transform.flip(self.idle, True, False)
        self.jump_l = pygame.transform.flip(self.jump_img, True, False)
        self.dash_l = pygame.transform.flip(self.dash_img, True, False)

        self.image = self.idle
        self.rect = self.image.get_rect(topleft=PlayerStart)

        self.vel_y = 0
        self.on_ground = False
        self.jumps = 2

        self.facing_right = True
        self.walk_index = 0
        self.walk_timer = 0

        self.dash_timer = 0
        self.dash_cd = 0
        self.dash_vel = 0

    def update(self, dx, platforms, enemies):
        # DASH TIMERS
        if self.dash_cd > 0:
            self.dash_cd -= 1
        if self.dash_timer > 0:
            self.dash_timer -= 1
        else:
            self.dash_vel = 0  # FIX: stop dash cleanly

        # FACING
        if dx > 0: self.facing_right = True
        if dx < 0: self.facing_right = False

        # ANIMATION STATE
        if self.dash_timer > 0:
            self.image = self.dash_img if self.facing_right else self.dash_l

        elif not self.on_ground:
            self.image = self.jump_img if self.facing_right else self.jump_l

        elif dx != 0:
            self.walk_timer += 1
            if self.walk_timer >= 10:
                self.walk_timer = 0
                self.walk_index = (self.walk_index + 1) % len(self.walk)

            frames = self.walk if self.facing_right else self.walk_l
            self.image = frames[self.walk_index]

        else:
            self.image = self.idle if self.facing_right else self.idle_l

        # MOVEMENT
        move_x = dx + self.dash_vel
        self.rect.x += move_x

        for p in pygame.sprite.spritecollide(self, platforms, False):
            if move_x > 0:
                self.rect.right = p.rect.left
            elif move_x < 0:
                self.rect.left = p.rect.right

        # GRAVITY
        self.vel_y += Gravity
        if self.vel_y > MaxFall:
            self.vel_y = MaxFall

        self.rect.y += self.vel_y
        self.on_ground = False

        for p in pygame.sprite.spritecollide(self, platforms, False):
            if self.vel_y > 0:
                self.rect.bottom = p.rect.top
                self.vel_y = 0
                self.on_ground = True
                self.jumps = 2
            elif self.vel_y < 0:
                self.rect.top = p.rect.bottom
                self.vel_y = 0

        # ENEMY HIT
        for e in pygame.sprite.spritecollide(self, enemies, False):
            self.reset()

        # FLOOR
        if self.rect.bottom >= Height:
            self.rect.bottom = Height
            self.vel_y = 0
            self.on_ground = True
            self.jumps = 2

    def jump(self):
        if self.jumps > 0:
            self.vel_y = -JumpStrength
            self.jumps -= 1
            self.on_ground = False

    def dash(self):
        if self.dash_cd == 0:
            self.dash_timer = DashDuration
            self.dash_cd = DashCooldown
            self.dash_vel = DashBoost if self.facing_right else -DashBoost

    def reset(self):
        self.rect.topleft = PlayerStart
        self.vel_y = 0
        self.jumps = 2

# ---------------- PLATFORM ----------------
class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h):
        super().__init__()
        self.image = load_image("docs/Frames/Platform.png", (w,h), PlatformColor)
        self.rect = self.image.get_rect(topleft=(x,y))

# ---------------- ENEMY ----------------
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

# ---------------- EXIT ----------------
class Exit(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = load_image("docs/Frames/Pizza.png", ExitScale, ExitColor)
        self.rect = self.image.get_rect(topleft=(x,y))

# ---------------- MAIN ----------------
screen = pygame.display.set_mode((Width, Height))
clock = pygame.time.Clock()

player = Player()
platforms = pygame.sprite.Group()
enemies = pygame.sprite.Group()
exit_group = pygame.sprite.Group()
all_sprites = pygame.sprite.Group(player)

def regenerate():
    platforms.empty()
    enemies.empty()
    exit_group.empty()
    all_sprites.empty()
    all_sprites.add(player)

    # GROUND
    ground = Platform(0, Height-40, Width, 40)
    platforms.add(ground)
    all_sprites.add(ground)

    # STACKED PLATFORMS
    y = Height - 120
    for _ in range(NumberBasePlatforms):
        x = random.randint(40, Width-160)
        p = Platform(x, y, random.randint(100,200), 20)
        platforms.add(p)
        all_sprites.add(p)

        y -= random.randint(PlatformGapMin, PlatformGapMax)
        if y < 80:
            break

    # ENEMIES
    for _ in range(4):
        e = Enemy(random.randint(0,Width-50), random.randint(0,Height-200))
        enemies.add(e)
        all_sprites.add(e)

    # EXIT
    ex = Exit(random.randint(100,Width-100), 50)
    exit_group.add(ex)
    all_sprites.add(ex)

    player.reset()

regenerate()

# ---------------- GAME LOOP ----------------
while True:
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_SPACE:
                player.jump()
            if e.key == pygame.K_x:
                player.dash()#this now wont break yaya

    keys = pygame.key.get_pressed()
    dx = (keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]) * PlayerSpeed

    player.update(dx, platforms, enemies)
    enemies.update()

    if pygame.sprite.spritecollideany(player, exit_group):
        regenerate()

    screen.fill((30,30,50))
    all_sprites.draw(screen)

    pygame.display.flip()
    clock.tick(Frames)