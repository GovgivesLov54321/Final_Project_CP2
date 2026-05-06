

import hashlib
import csv

def register(users):
    usernames = []
    for user in users:
        usernames.append(user["username"])
    valid_user = False
    while valid_user == False:
        username = input("Please input a username: ")
        if username in usernames:
            print("There is already a user with that username, please choose another.")
            continue
        else:
            valid_user = True
        password = input("Please input a password: ")
        password_encoded = password.encode("utf-8")
        hashed_password = hashlib.shake_128(password_encoded)
        hex_password = hashed_password.hexdigest(4)
        users.append({"username" : username, "password" : hex_password, "high score" : 0, "status" : "active"})
        return users
    
def display_profile(users):
    for user in users:
        if user["status"] == "active":
            print(f"Useranme: {user["username"]}\nHighscore: {user["high score"]}")

def load_csv():
    with open("docs/user_info.csv", "r") as user_list:
        content = csv.reader(user_list)
        row_count = sum(1 for row in content)
        user_list.seek(0)
        if row_count == 0:
            headers = ["username", "password", "high score", "status"]
        else:
            headers = next(content)
        rows = []
        for line in content:
            rows.append({headers[0] : line[0], headers[1] : line[1], headers[2] : line[2], headers[3] : line[3]})
        return rows
    
def save_changes(users):
    feildnames = ["username", "password", "high score", "status"]
    with open("docs/user_info.csv", "w", newline = "") as user_list:
        writer = csv.DictWriter(user_list, fieldnames = feildnames)
        writer.writeheader()
        writer.writerows(users)