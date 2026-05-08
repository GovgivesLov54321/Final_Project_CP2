import hashlib
from user_registration import *
import os
import pygame
import sys
import csv

# Helper function to clear the console
def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

information = load_csv("stats.csv")

# PYGAME PLACEHOLDER — replace with your game

def launch_game(username, high_score):
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Game")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 48)
    small_font = pygame.font.SysFont(None, 32)

    running = True
    while running:
        screen.fill((30, 30, 46))  # Dark background

        # Placeholder text
        title = font.render("Game Placeholder", True, (205, 214, 244))
        user_text = small_font.render(f"Logged in as: {username}", True, (166, 227, 161))
        score_text = small_font.render(f"High Score: {high_score}", True, (250, 219, 99))
        quit_text = small_font.render("Press ESC or close window to quit", True, (180, 180, 180))

        screen.blit(title,      (800 // 2 - title.get_width() // 2,      200))
        screen.blit(user_text,  (800 // 2 - user_text.get_width() // 2,  290))
        screen.blit(score_text, (800 // 2 - score_text.get_width() // 2, 330))
        screen.blit(quit_text,  (800 // 2 - quit_text.get_width() // 2,  420))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


def log_in(information):
    information = sign_out(information)
    # Loop to get username
    while True:
        clear()
        username = input("Please enter your username (or type 'exit' to go back): ").strip()
        if username.lower() == "exit":
            return information, "exit"
        user_found = False
        for i in information:
            if i["username"] == username:
                user_found = True
                break
        if user_found:
            break
        else:
            print("Username does not exist. Please try again.")
            input("Press Enter to continue...")

    # Loop to get password
    while True:
        clear()
        password = input("Please enter your password (or type 'exit' to go back): ").strip()
        if password.lower() == "exit":
            return information, "exit"
        # Hash the input password
        mixer = hashlib.shake_128()
        mixer.update(password.encode('utf-8'))
        f_password = str(mixer.hexdigest(4))
        correct = False
        for i in information:
            if f_password == i["password"]:
                i["status"] = "active"
                active_user = i          # Keep a reference to pass to Pygame
                correct = True
                break
        if correct:
            clear()
            save_csv(information)        # Persist active status
            launch_game(active_user["username"], active_user["high score"])
            return information, "game"
        else:
            print("Incorrect password. Please try again.")
            input("Press Enter to continue...")

def view_delete(information):
    while True:
        clear()
        for idx, i in enumerate(information, start=1):
            print(f"{idx}. Username: {i['username']}  |  Status: {i['status']}  |  Highscore: {i['high score']}")

        choice = input("\nType 'remove' to delete an account, or 'exit' to go back: ").strip().lower()
        if choice == "exit":
            return information
        elif choice == "remove":
            while True:
                num = input("Enter the number of the account to remove (or 'exit' to go back): ").strip()
                if num.lower() == "exit":
                    break
                if num.isdigit() and 1 <= int(num) <= len(information):
                    information.pop(int(num) - 1)
                    print("Account removed successfully!")
                    input("Press Enter to continue...")
                    break
                else:
                    print("Invalid input. Try again.")
        else:
            print("Invalid choice.")
            input("Press Enter to continue...")

def sign_out(information):
    for i in information:
        if i["status"] == "active":
            i["status"] = "inactive"
    return information

def view_profile(information):
    clear()
    for i in information:
        if i["status"] == "active":
            print(f"--- Your Profile ---\nUsername: {i['username']}\nHighscore: {i['high score']}")
            input("\nPress Enter to continue...")
            clear()
            return
    print("No active user found.")
    input("\nPress Enter to continue...")

def valid_password(password):
    if len(password) < 6:
        print("Password must be at least 6 characters long.")
        return False
    if not any(char.isdigit() for char in password):
        print("Password must include at least one number.")
        return False
    if not any(char.isalpha() for char in password):
        print("Password must include at least one letter.")
        return False
    return True


def load_csv():
    # Attempt to load the data; if file doesn't exist, return an empty list
    try:
        with open('users.csv', mode='r', newline='') as f:
            reader = csv.DictReader(f)
            return list(reader)
    except FileNotFoundError:
        return []

def save_csv(information):
    if not information:
        return
    # Save the current list of users back to the CSV
    with open('users.csv', mode='w', newline='') as f:
        fieldnames = information[0].keys()
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(information)

def main_menu():
    global information
    while True:
        clear()
        print("=== WELCOME TO THE GAME ===")
        print("1. Login & Play")
        print("2. Create New Account") # Assumes this is in user_registration.py
        print("3. View/Delete Accounts")
        print("4. Exit")
        
        choice = input("\nSelect an option: ")
        
        if choice == '1':
            information, result = log_in(information)
            # After game closes, ensure we save any highscore updates
            save_csv(information)
        elif choice == '2':
            # This calls your imported user_registration functions
            information = registration(information) 
            save_csv(information)
        elif choice == '3':
            information = view_delete(information)
            save_csv(information)
        elif choice == '4':
            sys.exit()

if __name__ == "__main__":
    main_menu()
