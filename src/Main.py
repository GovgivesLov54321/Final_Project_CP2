import pygame
import sys
import random
import math

# --- Config ---
Width, Height = 800, 600
Frames = 60

Gravity        = 0.5
JumpStrength   = 13
MaxFall        = 15
PlayerSpeed    = 5
DashBoost      = 18
DashDuration   = 12
DashCooldown   = 90

PlayerScale = (50, 70)
EnemyScale  = (40, 40)
ExitScale   = (40, 60)

PlatformColor = (100, 100, 100)
EnemyColor    = (200,   0,   0)
ExitColor     = (  0, 220,   0)

PlatformGapMin      = 70
PlatformGapMax      = 130
NumberBasePlatforms = 8

PlayerStart = (120, Height - 120)

BackgroundTop    = ( 25,  15,  50)
BackgroundBot    = ( 25,  15,  50)
CAccent    = (130,  80, 255)
CGold      = (255, 210,  60)
ColorRed       = (255,  60,  60)
ColorWhite     = (255, 255, 255)
ColorDashFill = (255, 255, 0)
ColorDashEmpty= ( 30,  30,  60)
ColorHealthFill   = (220,  50,  50)
ColorHealthEmpty  = ( 60,  20,  20)

pygame.init()
screen = pygame.display.set_mode((Width, Height))
pygame.display.set_caption("Platformer")
clock = pygame.time.Clock()

try:
    font_big   = pygame.font.SysFont("consolas", 36, bold=True)
    font_med   = pygame.font.SysFont("consolas", 22, bold=True)
    font_small = pygame.font.SysFont("consolas", 16)
except:
    font_big   = pygame.font.SysFont(None, 36)
    font_med   = pygame.font.SysFont(None, 22)
    font_small = pygame.font.SysFont(None, 16)


def draw_text_shadow(surf, text, font, color, pos, shadow=(2, 2), shadow_color=(0,0,0,160)):
    sx, sy = pos[0]+shadow[0], pos[1]+shadow[1]
    sh = font.render(text, True, (20, 10, 30))
    surf.blit(sh, (sx, sy))
    t = font.render(text, True, color)
    surf.blit(t, pos)
    return t.get_width()


def load_image(path, scale, fallback_color):
    try:
        img = pygame.image.load(path).convert_alpha()
        return pygame.transform.scale(img, scale)
    except:
        surf = pygame.Surface(scale, pygame.SRCALPHA)
        surf.fill(fallback_color)
        return surf


# --- BACKGROUND: use only the imported PNG ---
# This will prefer the PNG you load. If it fails to load, a solid fallback color is used.
Background = load_image("docs/Frames/BG.png", (Width, Height), (20, 20, 40))

# Disable generated gradient and star layers (we only want the PNG)
gradient_bg = None
StarLayers = []
StarOffsets = []
StarSpeeds  = []

# --- Screen effects ---
ShakeTimer    = 0
ShakeStrength = 0

def trigger_shake(strength, duration):
    global ShakeTimer, ShakeStrength
    ShakeTimer    = duration
    ShakeStrength = strength

def get_shake_offset():
    global ShakeTimer
    if ShakeTimer > 0:
        ShakeTimer -= 1
        mag = ShakeStrength * (ShakeTimer / 8)
        return (random.randint(-int(mag), int(mag)),
                random.randint(-int(mag), int(mag)))
    return (0, 0)


FlashTimer  = 0
FlashColor  = (255,255,255)
FlashAlpha  = 0

def trigger_flash(color=(255,255,255), alpha=120, duration=8):
    global FlashTimer, FlashColor, FlashAlpha
    FlashTimer = duration
    FlashColor = color
    FlashAlpha = alpha

FlashSurface = pygame.Surface((Width, Height))

def draw_flash(surf):
    global FlashTimer
    if FlashTimer > 0:
        a = int(FlashAlpha * FlashTimer / 8)
        FlashSurface.fill(FlashColor)
        FlashSurface.set_alpha(a)
        surf.blit(FlashSurface, (0,0))
        FlashTimer -= 1


Particles = []   # each: [x, y, vx, vy, life, max_life, color, size, gravity]

def spawn_particles(x, y, n, color, speed=3, size=3, gravity=0.15, spread=360):
    for _ in range(n):
        angle = math.radians(random.uniform(0, spread))
        spd   = random.uniform(speed*0.4, speed)
        vx    = math.cos(angle)*spd + random.uniform(-0.5,0.5)
        vy    = math.sin(angle)*spd + random.uniform(-0.5,0.5)
        life  = random.randint(15, 35)
        sz    = random.uniform(size*0.4, size)
        Particles.append([float(x), float(y), vx, vy, life, life, color, sz, gravity])

def spawn_dust(x, y, facing_right=True):
    dir_x = -1 if facing_right else 1
    for _ in range(6):
        vx = dir_x * random.uniform(0.5, 2.5)
        vy = random.uniform(-1.5, 0.2)
        life = random.randint(12, 22)
        sz = random.uniform(2, 5)
        Particles.append([float(x), float(y), vx, vy, life, life, (180,160,140), sz, 0.05])

def update_draw_particles(surf):
    dead = []
    for p in Particles:
        p[0] += p[2]; p[1] += p[3]
        p[3] += p[8]        # gravity component
        p[2] *= 0.92        # friction
        p[4] -= 1
        if p[4] <= 0:
            dead.append(p)
            continue
        alpha_ratio = p[4] / p[5]
        r,g,b = p[6]
        sz = max(1, int(p[7] * alpha_ratio))
        color = (int(r*alpha_ratio), int(g*alpha_ratio), int(b*alpha_ratio))
        pygame.draw.circle(surf, color, (int(p[0]), int(p[1])), sz)
    for p in dead:
        Particles.remove(p)

score = 0
level = 1
lives = 3

DeathFade      = 0     # counts down from 30 after death
RespawnFade    = 0     # counts down from 20 after respawn
FadeSurf = pygame.Surface((Width, Height))
FadeSurf.fill((0,0,0))

GlowSurf = pygame.Surface((Width, Height), pygame.SRCALPHA)


def DrawPlatformOutline(surf, rect, color, radius=12, alpha=60):
    expanded = rect.inflate(radius*2, radius*2)
    pygame.draw.rect(GlowSurf, (0,0,0,0), expanded)   # clear
    s = pygame.Surface((expanded.width, expanded.height), pygame.SRCALPHA)
    r,g,b = color
    for i in range(radius, 0, -3):
        a = int(alpha * (i/radius)**2)
        pygame.draw.rect(s, (r,g,b,a), (radius-i, radius-i,
                                         rect.width+i*2, rect.height+i*2), border_radius=4)
    surf.blit(s, expanded.topleft)


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.idle     = load_image("docs/Frames/Idle.png",          PlayerScale, (0,100,255))
        self.walk     = [load_image("docs/Frames/WalkCharacter.png",  PlayerScale, (0,100,255)),
                         load_image("docs/Frames/WalkCharacter2.png", PlayerScale, (0,100,255))]
        self.jump_img = load_image("docs/Frames/Jump.png",           PlayerScale, (0,100,255))
        self.dash_img = load_image("docs/Frames/Dash.png",           PlayerScale, (0,100,255))

        self.walk_l  = [pygame.transform.flip(f,True,False) for f in self.walk]
        self.idle_l  = pygame.transform.flip(self.idle, True, False)
        self.jump_l  = pygame.transform.flip(self.jump_img, True, False)
        self.dash_l  = pygame.transform.flip(self.dash_img, True, False)

        self.image = self.idle
        self.rect  = self.image.get_rect(topleft=PlayerStart)

        self.vel_y       = 0
        self.on_ground   = False
        self.jumps       = 2
        self.coyote_timer= 0
        self.facing_right= True
        self.walk_index  = 0
        self.walk_timer  = 0
        self.dash_timer  = 0
        self.dash_cd     = 0
        self.dash_vel    = 0
        self.prev_on_ground = False
        self.trail       = []    # [(x,y,age)] for dash trail

    def update(self, DirectionX, platforms, enemies):
        global score, lives, DeathFade

        if self.dash_cd > 0:   self.dash_cd -= 1
        if self.dash_timer > 0:
            self.dash_timer -= 1
            self.trail.append((self.rect.centerx, self.rect.centery, 0))
        else:
            self.dash_vel = 0

        # age / prune trail
        self.trail = [(x,y,a+1) for x,y,a in self.trail if a < 10]

        if DirectionX > 0: self.facing_right = True
        if DirectionX < 0: self.facing_right = False

        # ANIMATION
        if self.dash_timer > 0:
            self.image = self.dash_img if self.facing_right else self.dash_l
        elif not self.on_ground:
            self.image = self.jump_img if self.facing_right else self.jump_l
        elif DirectionX != 0:
            self.walk_timer += abs(DirectionX)
            if self.walk_timer >= 10:
                self.walk_timer = 0
                self.walk_index = (self.walk_index+1) % len(self.walk)
            frames = self.walk if self.facing_right else self.walk_l
            self.image = frames[self.walk_index]
        else:
            self.image = self.idle if self.facing_right else self.idle_l

        # HORIZONTAL
        move_x = DirectionX + self.dash_vel
        for _ in range(abs(int(move_x))):
            self.rect.x += 1 if move_x > 0 else -1
            for p in pygame.sprite.spritecollide(self, platforms, False):
                if move_x > 0: self.rect.right = p.rect.left
                else:          self.rect.left  = p.rect.right
                break

        # GRAVITY
        self.vel_y += Gravity * (0.3 if self.dash_timer > 0 else 1)
        if self.vel_y > MaxFall: self.vel_y = MaxFall
        self.rect.y += self.vel_y

        self.prev_on_ground = self.on_ground
        self.on_ground = False

        for p in pygame.sprite.spritecollide(self, platforms, False):
            if p.kind == "hazard" and self.vel_y > 0:
                self.die()
                return
            if self.vel_y > 0:
                self.rect.bottom = p.rect.top
                # LAND DUST
                if not self.prev_on_ground:
                    spawn_dust(self.rect.centerx, self.rect.bottom, self.facing_right)
                self.vel_y = 0
                if not self.on_ground: self.jumps = 2
                self.on_ground = True
            elif self.vel_y < 0:
                self.rect.top = p.rect.bottom
                self.vel_y = 0

        if self.on_ground:
            self.coyote_timer = 6
        else:
            self.coyote_timer -= 1

        if self.on_ground:
            for p in pygame.sprite.spritecollide(self, platforms, False):
                if p.kind == "moving":
                    self.rect.x += p.speed

        # ENEMY STOMP
        for e in pygame.sprite.spritecollide(self, enemies, False):
            if self.vel_y > 0 and self.rect.bottom <= e.rect.top + 20:
                spawn_particles(e.rect.centerx, e.rect.centery, 14,
                                (255,120,60), speed=5, size=4)
                trigger_shake(4, 6)
                trigger_flash((255,200,100), 80, 6)
                enemies.remove(e)
                AllSprites.remove(e)
                self.vel_y = -10
                score += 100
            else:
                self.die()
                return

        # FLOOR
        if self.rect.bottom >= Height:
            self.rect.bottom = Height
            self.vel_y = 0
            self.on_ground = True
            self.jumps = 2

        self.rect.left  = max(0, self.rect.left)
        self.rect.right = min(Width, self.rect.right)

    def die(self):
        global lives, DeathFade, RespawnFade
        spawn_particles(self.rect.centerx, self.rect.centery, 20,
                        ColorRed, speed=6, size=5)
        trigger_shake(8, 14)
        trigger_flash(ColorRed, 140, 10)
        lives -= 1
        DeathFade   = 30
        RespawnFade = 20
        self.reset()

    def jump(self):
        if self.jumps > 0 or self.coyote_timer > 0:
            self.vel_y = -JumpStrength
            self.jumps -= 1
            self.on_ground = False
            spawn_dust(self.rect.centerx, self.rect.bottom, self.facing_right)

    def dash(self):
        if self.dash_cd == 0:
            self.dash_timer = DashDuration
            self.dash_cd    = DashCooldown
            self.dash_vel   = DashBoost if self.facing_right else -DashBoost
            spawn_particles(self.rect.centerx, self.rect.centery, 10,
                            ColorDashFill, speed=4, size=3)
            trigger_flash(ColorDashFill, 60, 5)

    def reset(self):
        self.rect.topleft = PlayerStart
        self.vel_y = 0
        self.jumps = 2
        self.trail = []

    def DrawTrail(self, surf):
        for tx, ty, age in self.trail:
            alpha_ratio = 1 - age/10
            r,g,b = ColorDashFill
            color = (int(r*alpha_ratio), int(g*alpha_ratio), int(b*alpha_ratio))
            sz = max(1, int(6*alpha_ratio))
            pygame.draw.circle(surf, color, (tx,ty), sz)

    def DrawDash(self, surf):
        """Circular cooldown indicator around the player."""
        cx, cy = self.rect.centerx, self.rect.bottom + 8
        total  = DashCooldown
        remain = self.dash_cd
        ratio  = 1 - remain/total if remain > 0 else 1
        radius = 14
        pygame.draw.circle(surf, ColorDashEmpty, (cx,cy), radius, 3)
        if ratio > 0:
            start_angle = -math.pi/2
            end_angle   = start_angle + ratio*2*math.pi
            steps = max(2, int(ratio*32))
            pts = [(cx + radius*math.cos(start_angle + (end_angle-start_angle)*i/(steps-1)),
                    cy + radius*math.sin(start_angle + (end_angle-start_angle)*i/(steps-1)))
                   for i in range(steps)]
            if len(pts) >= 2:
                pygame.draw.lines(surf, ColorDashFill, False, pts, 3)


class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h, kind="normal"):
        super().__init__()
        self.kind = kind
        if kind == "hazard":
            self.image = load_image("docs/Frames/HazardPlatform.png", (w,h), (200,50,50))
        elif kind == "moving":
            self.image = load_image("docs/Frames/MovingPlatform.png", (w,h), (100,60,200))
        else:
            self.image = load_image("docs/Frames/Platform.png", (w,h), PlatformColor)
        self.rect     = self.image.get_rect(topleft=(x,y))
        self.glow_anim= random.uniform(0, math.pi*2)

        if kind == "moving":
            self.start_x = x
            self.range   = random.randint(60, 140)
            self.speed   = random.choice([-2, 2])
        else:
            self.speed = 0

    def update(self):
        self.glow_anim += 0.05
        if self.kind == "moving":
            self.rect.x += self.speed
            if abs(self.rect.x - self.start_x) > self.range:
                self.speed *= -1

    def draw_glow(self, surf):
        if self.kind == "moving":
            pulse = 0.5 + 0.5*math.sin(self.glow_anim)
            alpha = int(30 + 40*pulse)
        elif self.kind == "hazard":
            pulse = 0.5 + 0.5*math.sin(self.glow_anim*2)
            alpha = int(40 + 60*pulse)


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = load_image("docs/Frames/SpikyGuy.png", EnemyScale, EnemyColor)
        self.rect  = self.image.get_rect(topleft=(x,y))
        self.vel   = random.choice([-3,3])
        self.bob   = random.uniform(0, math.pi*2)

    def update(self):
        self.rect.x += self.vel
        self.bob    += 0.08
        if self.rect.left < 0 or self.rect.right > Width:
            self.vel *= -1

    def draw_indicator(self, surf):
        cx = self.rect.centerx
        ty = self.rect.top - 12 - int(3*math.sin(self.bob))
        pts = [(cx, ty), (cx-6, ty+8), (cx+6, ty+8)]


class Exit(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = load_image("docs/Frames/Pizza.png", ExitScale, ExitColor)
        self.rect  = self.image.get_rect(topleft=(x,y))
        self.pulse = 0.0

    def update(self):
        self.pulse += 0.06

    def draw_glow(self, surf):
        p = 0.5 + 0.5*math.sin(self.pulse)
        alpha = int(50 + 80*p)


# Sprites
player      = Player()
platforms   = pygame.sprite.Group()
enemies     = pygame.sprite.Group()
exit_group  = pygame.sprite.Group()
AllSprites = pygame.sprite.Group(player)


def regenerate():
    global level
    platforms.empty(); enemies.empty(); exit_group.empty(); AllSprites.empty()
    AllSprites.add(player)

    ground = Platform(0, Height-40, Width, 40)
    platforms.add(ground); AllSprites.add(ground)

    y = Height - 120
    prev_x = Width // 2

    for _ in range(NumberBasePlatforms):
        x    = prev_x + random.randint(-120, 120)
        x    = max(40, min(Width-160, x))
        prev_x = x
        kind = random.choice(["normal","normal","moving","hazard"])
        w    = random.randint(100, 200)
        p    = Platform(x, y, w, 20, kind)
        platforms.add(p); AllSprites.add(p)
        y -= random.randint(PlatformGapMin, PlatformGapMax)
        if y < 80: break

    for _ in range(4):
        e = Enemy(random.randint(0,Width-50), random.randint(0,Height-200))
        enemies.add(e); AllSprites.add(e)

    ex = Exit(random.randint(100, Width-100), 50)
    exit_group.add(ex); AllSprites.add(ex)

    player.reset()

regenerate()


#Hud 
hud_surf = pygame.Surface((Width, Height), pygame.SRCALPHA)

def draw_hud(surf):
    hud_surf.fill((0,0,0,0))

    # ─ SCORE ─
    draw_text_shadow(hud_surf, f"SCORE  {score:06d}", font_med, CGold, (16, 12))

    # ─ LEVEL ─
    draw_text_shadow(hud_surf, f"LVL {level}", font_med, CAccent, (Width-90, 12))

    # ─ LIVES ─
    lx = 16
    draw_text_shadow(hud_surf, "LIVES", font_small, (180,180,200), (lx, 44))
    for i in range(3):
        cx = lx + 58 + i*22
        cy = 52
        color = ColorHealthFill if i < lives else ColorHealthEmpty
        pygame.draw.circle(hud_surf, color, (cx, cy), 8)
        pygame.draw.circle(hud_surf, (255,255,255,60), (cx,cy), 8, 1)

    #dash cooldown bar
    BarX, BarY, barW, BarH = Width//2 - 50, Height-28, 100, 10
    pygame.draw.rect(hud_surf, ColorDashEmpty+(180,), (BarX-1, BarY-1, barW+2, BarH+2), border_radius=6)
    ratio = 1 - player.dash_cd / DashCooldown
    fill_w = int(barW * ratio)
    if fill_w > 0:
        pygame.draw.rect(hud_surf, ColorDashFill+(220,), (BarX, BarY, fill_w, BarH), border_radius=5)
    label = "DASH" if ratio >= 1 else f"DASH  {int(ratio*100)}%"
    lbl = font_small.render(label, True, ColorDashFill if ratio>=1 else (120,160,200))
    hud_surf.blit(lbl, (BarX + barW//2 - lbl.get_width()//2, BarY - 18))

    #game over 
    if lives <= 0:
        draw_text_shadow(hud_surf, "GAME OVER — press R", font_big, ColorRed, (Width//2-180, Height//2-20))

    surf.blit(hud_surf, (0,0))


#level transtion
transition_timer = 0

def start_transition():
    global transition_timer, level, score
    transition_timer = 40
    level += 1
    score += 500
    trigger_flash((200,255,200), 200, 15)
    trigger_shake(3, 8)
    spawn_particles(Width//2, Height//2, 30, CGold, speed=6, size=5)
    regenerate()

trans_surf = pygame.Surface((Width, Height))
trans_surf.fill((30,255,120))


#Main pygame loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit(); sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                player.jump()
            if event.key == pygame.K_x:
                player.dash()
            if event.key == pygame.K_r and lives <= 0:
                lives = 3; score = 0; level = 1
                regenerate()

    keys = pygame.key.get_pressed()
    dx   = (keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]) * PlayerSpeed

    if lives > 0:
        player.update(dx, platforms, enemies)
        enemies.update()
        platforms.update()
        for ex in exit_group: ex.update()

        if pygame.sprite.spritecollideany(player, exit_group):
            start_transition()

    #draw
    shake_off = get_shake_offset()

    # Render to a temp surface so shake can offset the whole scene
    scene = pygame.Surface((Width, Height))

    # Background: prefer the loaded PNG; fallback to solid fill if missing
    if Background and Background.get_size() == (Width, Height):
        scene.blit(Background, (0, 0))
    else:
        scene.fill((20, 20, 40))

    # Platform glows (behind sprites)
    for p in platforms:
        p.draw_glow(scene)
    for ex in exit_group:
        ex.draw_glow(scene)

    # Sprites
    player.DrawTrail(scene)
    AllSprites.draw(scene)

    # Enemy stomp indicators
    for e in enemies:
        e.draw_indicator(scene)

    # Dash ring under player
    player.DrawDash(scene)

    # Particles
    update_draw_particles(scene)

    # Flash overlay
    draw_flash(scene)

    # Death fade
    if DeathFade > 0:
        a = int(200 * DeathFade/30)
        FadeSurf.set_alpha(a)
        scene.blit(FadeSurf, (0,0))
        DeathFade -= 1
    if RespawnFade > 0:
        a = int(180 * RespawnFade/20)
        FadeSurf.set_alpha(a)
        scene.blit(FadeSurf, (0,0))
        RespawnFade -= 1

    # Level transition flash
    if transition_timer > 0:
        a = int(220 * transition_timer/40)
        trans_surf.set_alpha(a)
        scene.blit(trans_surf, (0,0))
        # big centred text
        if transition_timer > 10:
            draw_text_shadow(scene, f"LEVEL {level}!", font_big, ColorWhite,
                             (Width//2-70, Height//2-20))
        transition_timer -= 1

    # Blit scene to screen with shake offset
    screen.blit(scene, shake_off)

    # HUD drawn directly on screen (not shaken)
    draw_hud(screen)

    pygame.display.flip()
    clock.tick(Frames)
