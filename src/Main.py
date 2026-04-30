import pygame
import sys
import random

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


def load_image(path, scale, fallback_color):
    try:
        img = pygame.image.load(path).convert_alpha()
        return pygame.transform.scale(img, scale)
    except:
        surf = pygame.Surface(scale)
        surf.fill(fallback_color)
        return surf


# BACKGROUND
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
        self.rect = self.image.get_rect(topleft=PlayerStart)

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
        # DASH TIMERS
        if self.dash_cd > 0:
            self.dash_cd -= 1
        if self.dash_timer > 0:
            self.dash_timer -= 1
        else:
            self.dash_vel = 0

        # FACING
        if dx > 0: self.facing_right = True
        if dx < 0: self.facing_right = False

        # ANIMATION
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

        # HORIZONTAL (ANTI-TUNNEL)
        move_x = dx + self.dash_vel
        for _ in range(abs(int(move_x))):
            self.rect.x += 1 if move_x > 0 else -1

            for p in pygame.sprite.spritecollide(self, platforms, False):
                if move_x > 0:
                    self.rect.right = p.rect.left
                else:
                    self.rect.left = p.rect.right
                break

        # GRAVITY
        if self.dash_timer > 0:
            self.vel_y += Gravity * 0.3
        else:
            self.vel_y += Gravity

        if self.vel_y > MaxFall:
            self.vel_y = MaxFall

        self.rect.y += self.vel_y
        self.on_ground = False

        for p in pygame.sprite.spritecollide(self, platforms, False):
            # HAZARD (only hurts when landing on it)
            if p.kind == "hazard" and self.vel_y > 0:
                self.reset()
                return

            if self.vel_y > 0:
                self.rect.bottom = p.rect.top
                self.vel_y = 0

                if not self.on_ground:
                    self.jumps = 2

                self.on_ground = True

            elif self.vel_y < 0:
                self.rect.top = p.rect.bottom
                self.vel_y = 0

        # COYOTE TIME
        if self.on_ground:
            self.coyote_timer = 6
        else:
            self.coyote_timer -= 1

        # MOVING PLATFORM CARRY
        if self.on_ground:
            for p in pygame.sprite.spritecollide(self, platforms, False):
                if p.kind == "moving":
                    self.rect.x += p.speed

        # ENEMY INTERACTION (STOMP)
        for e in pygame.sprite.spritecollide(self, enemies, False):
            if self.vel_y > 0 and self.rect.bottom <= e.rect.top + 20:
                enemies.remove(e)
                all_sprites.remove(e)
                self.vel_y = -10
            else:
                self.reset()

        # FLOOR
        if self.rect.bottom >= Height:
            self.rect.bottom = Height
            self.vel_y = 0
            self.on_ground = True
            self.jumps = 2

        # SCREEN CLAMP
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
        self.rect.topleft = PlayerStart
        self.vel_y = 0
        self.jumps = 2


class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h, kind="normal"):
        super().__init__()

        self.kind = kind

        if kind == "hazard":
            self.image = load_image(
                "docs/Frames/HazardPlatform.png",
                (w, h),
                (255, 80, 80)
            )
        else:
            self.image = load_image(
                "docs/Frames/Platform.png",
                (w, h),
                PlatformColor
            )

        self.rect = self.image.get_rect(topleft=(x, y))

        if kind == "moving":
            self.image = load_image(
                "docs/Frames/MovingPlatform.png",
                (w, h),
                (255, 80, 80)
            )
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

    ground = Platform(0, Height-40, Width, 40)
    platforms.add(ground)
    all_sprites.add(ground)

    y = Height - 120
    prev_x = Width // 2

    for _ in range(NumberBasePlatforms):
        x = prev_x + random.randint(-120, 120)
        x = max(40, min(Width-160, x))
        prev_x = x

        kind = random.choice(["normal", "normal", "moving", "hazard"])

        p = Platform(x, y, random.randint(100,200), 20, kind)
        platforms.add(p)
        all_sprites.add(p)

        y -= random.randint(PlatformGapMin, PlatformGapMax)
        if y < 80:
            break

    for _ in range(4):
        e = Enemy(random.randint(0,Width-50), random.randint(0,Height-200))
        enemies.add(e)
        all_sprites.add(e)

    ex = Exit(random.randint(100,Width-100), 50)
    exit_group.add(ex)
    all_sprites.add(ex)

    player.reset()


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
        regenerate()

    screen.blit(Background, (0,0))
    all_sprites.draw(screen)

    pygame.display.flip()
    clock.tick(Frames)