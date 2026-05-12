import pygame
import csv

CSV_PATH = "docs/Storage Places/scores.csv"


Background       = (30, 30, 46)
TitleColor    = (255, 215, 0)    # gold
HeaderColor   = (180, 180, 220)
GoldColor     = (255, 215, 0)
SilverColor   = (192, 192, 192)
BronzeColor   = (205, 127, 50)
DefaultColor  = (220, 220, 240)
RowAltColor  = (40, 40, 60)    # subtle alternating row tint
ButtonColor   = (100, 100, 200)
ButtonHover   = (130, 130, 230)

RAnks = [GoldColor, SilverColor, BronzeColor]


def load_scores():
    """Return a list of (username, high_score) sorted highest first."""
    try:
        with open(CSV_PATH, mode="r", newline="") as f:
            reader = csv.DictReader(f)
            users = [
                (row["username"], int(row["high score"]))
                for row in reader
            ]
        users.sort(key=lambda x: x[1], reverse=True)
        return users
    except FileNotFoundError:
        return []


def show_leaderboard(screen: pygame.Surface) -> None:
    """
    Display the leaderboard on the given surface.
    Blocks until the player closes the overlay (Back button or ESCAPE / Q).

    Parameters
    ----------
    screen : pygame.Surface
        The existing pygame display surface.
    """
    WIDTH, HEIGHT = screen.get_size()

    # Fonts
    TitleFont  = pygame.font.SysFont(None, 64)
    headerFont = pygame.font.SysFont(None, 36)
    RowFont    = pygame.font.SysFont(None, 32)
    BTNFont    = pygame.font.SysFont(None, 36)

    # Geometry
    TableTop    = 150
    RowH        = 44
    ColRankX   = WIDTH // 2 - 280
    ColNameX   = WIDTH // 2 - 180
    COL_SCORE_X  = WIDTH // 2 + 160
    MaxVisible  = 10              # rows shown at once
    ScrollSpeed = 1               # rows per scroll tick

    # Back button
    btn_rect = pygame.Rect(WIDTH // 2 - 80, HEIGHT - 70, 160, 44)

    scores = load_scores()
    scroll_offset = 0              # index of first visible row
    clock = pygame.time.Clock()

    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q, pygame.K_BACKSPACE):
                    running = False

                # Arrow-key scrolling
                if event.key == pygame.K_DOWN:
                    scroll_offset = min(scroll_offset + ScrollSpeed,
                                        max(0, len(scores) - MaxVisible))
                if event.key == pygame.K_UP:
                    scroll_offset = max(scroll_offset - ScrollSpeed, 0)

            if event.type == pygame.MOUSEWHEEL:
                scroll_offset -= event.y * ScrollSpeed
                scroll_offset = max(0, min(scroll_offset,
                                           max(0, len(scores) - MaxVisible)))

            if event.type == pygame.MOUSEBUTTONDOWN:
                if btn_rect.collidepoint(event.pos):
                    running = False

       
        screen.fill(Background)

        # Subtle top gradient strip
        for i in range(80):
            alpha = int(80 * (1 - i / 80))
            s = pygame.Surface((WIDTH, 1), pygame.SRCALPHA)
            s.fill((80, 80, 120, alpha))
            screen.blit(s, (0, i))

        title_surf = TitleFont.render(" LEADERBOARD", True, TitleColor)
        screen.blit(title_surf, (WIDTH // 2 - title_surf.get_width() // 2, 50))

        # Decorative underline
        pygame.draw.line(screen, GoldColor,
                         (WIDTH // 2 - 200, 118), (WIDTH // 2 + 200, 118), 2)

  
        def blit_centered_x(surf, cx, y):
            screen.blit(surf, (cx - surf.get_width() // 2, y))

        hdr_rank  = headerFont.render("RANK",     True, HeaderColor)
        hdr_name  = headerFont.render("PLAYER",   True, HeaderColor)
        hdr_score = headerFont.render("HIGH SCORE", True, HeaderColor)

        blit_centered_x(hdr_rank,  ColRankX,  TableTop)
        blit_centered_x(hdr_name,  ColNameX,  TableTop)
        blit_centered_x(hdr_score, COL_SCORE_X, TableTop)

        pygame.draw.line(screen, HeaderColor,
                         (ColRankX - 40, TableTop + 30),
                         (COL_SCORE_X + 80, TableTop + 30), 1)

        visible = scores[scroll_offset: scroll_offset + MaxVisible]

        for i, (username, score) in enumerate(visible):
            rank    = scroll_offset + i + 1
            row_y   = TableTop + 40 + i * RowH

            # Alternating row background
            if i % 2 == 0:
                pygame.draw.rect(screen, RowAltColor,
                                 (ColRankX - 40, row_y - 4,
                                  COL_SCORE_X - ColRankX + 120, RowH - 2),
                                 border_radius=4)

            # Rank colour (gold / silver / bronze for top 3)
            color = RAnks[rank - 1] if rank <= 3 else DefaultColor

            rank_surf  = RowFont.render(f"#{rank}",    True, color)
            name_surf  = RowFont.render(username,       True, color)
            score_surf = RowFont.render(f"{score:,}",  True, color)

            blit_centered_x(rank_surf,  ColRankX,  row_y)
            blit_centered_x(name_surf,  ColNameX,  row_y)
            blit_centered_x(score_surf, COL_SCORE_X, row_y)

    
        if not scores:
            empty = RowFont.render("No scores yet — be the first!", True, HeaderColor)
            screen.blit(empty, (WIDTH // 2 - empty.get_width() // 2,
                                TableTop + 60))

        if len(scores) > MaxVisible:
            hint = pygame.font.SysFont(None, 24).render(
                f"▲▼  scroll   ({scroll_offset + 1}–"
                f"{min(scroll_offset + MaxVisible, len(scores))} of {len(scores)})",
                True, (140, 140, 160)
            )
            screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2, HEIGHT - 100))

        hover = btn_rect.collidepoint(mouse_pos)
        pygame.draw.rect(screen, ButtonHover if hover else ButtonColor,
                         btn_rect, border_radius=8)
        btn_surf = BTNFont.render("Back", True, (255, 255, 255))
        screen.blit(btn_surf, (btn_rect.centerx - btn_surf.get_width() // 2,
                                btn_rect.centery - btn_surf.get_height() // 2))

        pygame.display.flip()
        clock.tick(60)



if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Leaderboard")
    show_leaderboard(screen)
    pygame.quit()