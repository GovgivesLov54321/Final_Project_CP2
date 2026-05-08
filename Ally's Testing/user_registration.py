import hashlib
import csv
import pygame

# ─────────────────────────────────────────────
# PYGAME PLACEHOLDER — replace with your game
# ─────────────────────────────────────────────
def launch_game(username, high_score):
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Game")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 48)
    small_font = pygame.font.SysFont(None, 32)

    running = True
    while running:
        screen.fill((30, 30, 46))

        title      = font.render("Game Placeholder", True, (205, 214, 244))
        user_text  = small_font.render(f"Logged in as: {username}", True, (166, 227, 161))
        score_text = small_font.render(f"High Score: {high_score}", True, (250, 219, 99))
        quit_text  = small_font.render("Press ESC or close window to quit", True, (180, 180, 180))

        screen.blit(title,      (800 // 2 - title.get_width() // 2,      200))
        screen.blit(user_text,  (800 // 2 - user_text.get_width() // 2,  290))
        screen.blit(score_text, (800 // 2 - score_text.get_width() // 2, 330))
        screen.blit(quit_text,  (800 // 2 - quit_text.get_width() // 2,  420))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
# ──────────────────────────────────
