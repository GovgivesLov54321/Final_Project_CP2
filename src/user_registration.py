import hashlib
import csv


def load_csv():
    try:
        with open("docs/Storage Places/user_data.csv", mode="r", newline="") as f:
            reader = csv.DictReader(f)
            return list(reader)
    except FileNotFoundError:
        return []


def save_csv(data):
    with open("docs/Storage Places/user_data.csv", mode="w", newline="") as f:
        fieldnames= ["username", "password", "status", "high score"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)


def valid_password(password):
    if len(password) < 6:
        print("Password must be at least 6 characters.")
        return False
    if not any(c.isdigit() for c in password):
        print("Password must contain a number.")
        return False
    if not any(c.isalpha() for c in password):
        print("Password must contain a letter.")
        return False
    return True


def registration():
    users = load_csv()

    username = input("Choose a username: ").strip()

    for u in users:
        if u["username"] == username:
            print("Username already exists.")
            return

    while True:
        password = input("Choose a password: ").strip()
        if valid_password(password):
            break

    mixer = hashlib.shake_128()
    mixer.update(password.encode("utf-8"))
    hashed = mixer.hexdigest(4)

    new_user = {
        "username": username,
        "password": hashed,
        "status": "inactive",
        "high score": "0"
    }

    users.append(new_user)
    save_csv(users)

    print("Account created successfully!")