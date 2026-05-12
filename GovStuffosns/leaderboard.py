# GNB - Code to make leaderboard look pretty
import csv
import pygame


# PYGAME SETUP

pygame.init()

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600

screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Leaderboard")

font = pygame.font.SysFont("arial", 28)
small_font = pygame.font.SysFont("arial", 22)

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GOLD = (255, 215, 0)
GRAY = (180, 180, 180)


# END UP HERE FROM ALLY'S MENU

# Ally's stuff can call leaderboard_main()
# when user chooses leaderboard option


# READ CSV FUNCTION

def score_csv_reader():

    rows = []

    # read from Ally’s csv file
    try:
        with open("docs/Storage Places/scores.csv", "r", newline="") as csv_file:

            content = csv.DictReader(csv_file)

            # put each row into list
            for row in content:
                rows.append(row)

    except FileNotFoundError:
        print("scores.csv file not found.")

    return rows


# FORMAT NEW ROW

# this helps format incoming score data
# from Ally's game system

def new_row_format(new_row):

    formatted_row = {
        "rank number": "",
        "username": str(new_row["username"]),
        "score": int(new_row["score"])
    }

    return formatted_row


# ORDER SCORES

def order_scores(csv_rows, new_row=None):

    # helper function for sorting
    def get_ratio(csv_row):
        return float(csv_row["ratio"])

    rank = 1

    # if a new row comes from Ally's game
    if new_row is not None:

        new_row = new_row_format(new_row)
        csv_rows.append(new_row)

    # sort highest ratios first
    csv_rows.sort(key=get_ratio, reverse=True)

    # only keep top 5
    csv_rows = csv_rows[:5]

    # give rankings
    for row in csv_rows:
        row["rank number"] = rank
        rank += 1

    # save updated rankings
    with open("docs/Storage Places/scores.csv", "w", newline="") as file:

        fieldnames = [
            "rank number",
            "username",
            "score"
        ]

        writer = csv.DictWriter(file, fieldnames=fieldnames)

        writer.writeheader()

        for row in csv_rows:
            writer.writerow(row)

    return csv_rows


# DRAW LEADERBOARD

def prettify_list(rows):

    screen.fill(BLACK)

    # title
    title = font.render("===== HIGH SCORES =====", True, GOLD)
    screen.blit(title, (190, 40))

    # column labels
    headers = small_font.render(
        "RANK    USERNAME    SCORE",
        True,
        WHITE
    )

    screen.blit(headers, (100, 120))

    y_position = 180

    # print every row nicely
    for row in rows:

        leaderboard_text = (
            f"{row['rank number']}        "
            f"{row['username']}        "
            f"{row['score']}        "
        )

        text_surface = small_font.render(
            leaderboard_text,
            True,
            GRAY
        )

        screen.blit(text_surface, (100, y_position))

        y_position += 50

    # small instructions
    back_text = small_font.render(
        "Press ESC to return to menu",
        True,
        WHITE
    )

    screen.blit(back_text, (240, 520))

    pygame.display.update()


# MAIN LEADERBOARD FUNCTION

def leaderboard_main():

    running = True

    # read csv
    rows = score_csv_reader()

    # organize scores
    ordered_rows = order_scores(rows)

    while running:

        # draw leaderboard
        prettify_list(ordered_rows)

        # pygame events
        for event in pygame.event.get():

            # close window
            if event.type == pygame.QUIT:
                running = False

            # keyboard controls
            if event.type == pygame.KEYDOWN:

                # return to Ally's menu
                if event.key == pygame.K_ESCAPE:
                    running = False

    pygame.quit()
