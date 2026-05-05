# login.py

import hashlib
from user_registration import *
import os

# Helper function to clear the console
def clear():
    os.system('cls' if os.name == 'nt' else 'clear')


information = load_csv()

# Function for logging in
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
                correct = True
                break

        if correct:
            clear()
            return information, "game"
        else:
            print("Incorrect password. Please try again.")
            input("Press Enter to continue...")


def view_delete(information):
    while True:
        clear()
        # Display all accounts
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
                    information.pop(int(num)-1)
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


# Optional: Profile viewer for logged-in users
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


# Optional: Password requirement checker (used in registration)
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