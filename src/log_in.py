import pygame
import hashlib
import csv
from Main import launch_game

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Game Login")

FONT = pygame.font.SysFont(None, 40)
SMALL_FONT = pygame.font.SysFont(None, 28)

# ─────────────────────────────────────────────
# CSV FUNCTIONS
# ─────────────────────────────────────────────

def load_csv():
    try:
        with open("docs/Storage Places/scores.csv", mode="r", newline="") as f:
            reader = csv.DictReader(f)
            data = list(reader)
            for user in data:
                user["high score"] = int(user["high score"])
            return data
    except FileNotFoundError:
        return []

def save_csv(data):
    with open("docs/Storage Places/scores.csv", mode="w", newline="") as f:
        fieldnames = ["username", "password", "high score"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for user in data:
            user_copy = user.copy()
            user_copy["high score"] = str(user_copy["high score"])
            writer.writerow(user_copy)

# ─────────────────────────────────────────────
# INPUT BOX CLASS
# ─────────────────────────────────────────────

class InputBox:
    def __init__(self, x, y, w, h, text=''):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = (200, 200, 200)
        self.text = text
        self.active = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)

        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key == pygame.K_RETURN:
                pass
            else:
                self.text += event.unicode

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect, 2)
        txt_surface = FONT.render(self.text, True, (255, 255, 255))
        screen.blit(txt_surface, (self.rect.x + 5, self.rect.y + 5))

# ─────────────────────────────────────────────
# BUTTON CLASS
# ─────────────────────────────────────────────

class Button:
    def __init__(self, x, y, w, h, text):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text

    def draw(self, screen):
        pygame.draw.rect(screen, (100, 100, 200), self.rect)
        txt = FONT.render(self.text, True, (255, 255, 255))
        screen.blit(txt, (
            self.rect.centerx - txt.get_width() // 2,
            self.rect.centery - txt.get_height() // 2
        ))

    def clicked(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos)

# ─────────────────────────────────────────────
# LOGIN SCREEN LOOP
# ─────────────────────────────────────────────

def login_screen():
    users = load_csv()

    username_box = InputBox(300, 200, 200, 40)
    password_box = InputBox(300, 260, 200, 40)

    login_button = Button(300, 330, 200, 50, "Login")
    register_button = Button(300, 400, 200, 50, "Register")

    message = ""

    running = True
    while running:
        screen.fill((30, 30, 46))

        title = FONT.render("LOGIN SYSTEM", True, (255, 255, 255))
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 100))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

            username_box.handle_event(event)
            password_box.handle_event(event)

            if login_button.clicked(event):
                username = username_box.text.strip()
                password = password_box.text.strip()

                user = next((u for u in users if u["username"] == username), None)

                if not user:
                    message = "User not found"
                else:
                    mixer = hashlib.shake_128()
                    mixer.update(password.encode("utf-8"))
                    hashed = mixer.hexdigest(4)

                    if hashed != user["password"]:
                        message = "Incorrect password"
                    else:
                        message = "Login successful!"

                        final_score = launch_game(user["username"], user["high score"])

                        if final_score is None:
                            final_score = user["high score"]

                        if final_score > user["high score"]:
                            user["high score"] = final_score

                        save_csv(users)
                        message = "Game exited"

            if register_button.clicked(event):
                username = username_box.text.strip()
                password = password_box.text.strip()

                if any(u["username"] == username for u in users):
                    message = "Username already exists"
                else:
                    mixer = hashlib.shake_128()
                    mixer.update(password.encode("utf-8"))
                    hashed = mixer.hexdigest(4)

                    users.append({
                        "username": username,
                        "password": hashed,
                        "high score": 0
                    })

                    save_csv(users)
                    message = "Account created"

        username_box.draw(screen)
        password_box.draw(screen)
        login_button.draw(screen)
        register_button.draw(screen)

        msg_surface = SMALL_FONT.render(message, True, (255, 200, 200))
        screen.blit(msg_surface, (WIDTH//2 - msg_surface.get_width()//2, 480))

        pygame.display.flip()

# ─────────────────────────────────────────────

if __name__ == "__main__":
    login_screen()