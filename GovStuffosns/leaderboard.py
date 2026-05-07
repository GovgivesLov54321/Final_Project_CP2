# GNB - Code to make leaderboard look pretty
import csv
import pygame

# End up here from Ally's main menu if user wants to view the leaderboard:

# Display options to User as: 1. View Leaderboard -- 2. Return to Main Menu
choice = input("Welcome to the Leaderboard, User!" \
"1. View Leaderboard" \
"2. Return to Main Menu")

# Define function as score_csv_reader():
def score_csv_reader():
    # read from Ally’s csv, the columns for top five scores
    with open("docs\Storage Places\scores.csv", "r+") as csv_file:
        content = csv.reader()
        headers = next(content)
        rows = []
        
        for x in content:
            rows.append({headers[0]:x[0],headers[1]:x[1],headers[2]:x[2]})
        #return the list
        return rows

# Define function as order_scores():
def order_scores(csv_rows, new_row):
    # re-organize, by writing to have 5 largest scores in descending order
    #function for rank finding
    def get_ratio(csv_row):
        return float(csv_row["ratio"])
    rank = 1

    #use the incoming new row which has (blank,username,p1 score, p2 score, p2 bot, win/lose ratio)
    #compare it to all of the other scores currently in the file
    new_row = new_row_format(new_row)
    csv_rows.append(new_row)

    #what .sort does is take numerical values and put them in order from greatest to least, if reverse is active, it does least to greatest
    csv_rows.sort(key=get_ratio,reverse=True)

    #after they are sorted so highest is on the top we can just assign each of the inline scores a rank one after another in order
    for row in csv_rows:
        row["rank number"] = rank
        rank+=1

    #write all the data to the csv file
    with open("Files/score_data.csv", "w",newline="") as file:
        fieldnames = ["rank number","username","player one score","player two score","Bot","ratio"]
        writer = csv.DictWriter(file,fieldnames=fieldnames)
        writer.writeheader()
        for x in csv_rows:
            writer.writerow({"rank number":x["rank number"],"username":x["username"],"player one score":x["player one score"],"player two score":x["player two score"],"Bot":x["Bot"],"ratio":x["ratio"]})
    #return the list of properly ranked stuff
    return csv_rows


# Define function as prettify_list():
def prettify_list():
    print("===== HIGH SCORES =====")
	# take from Ally’s renewed scores list, and print for every row in the csv in a certain format: (f"RANK NUMBER {row["rank number"]} == USERNAME {row["username"]} == SCORE {row["score"]})
    print(f"RANK NUMBER {row["rank number"]} == USERNAME {row["username"]} == SCORE {row["player one score"]}")
    

# I believe this’ll also be used when showing the User if they made leaderboard or not: If this is the case, then just run the option 1

# Define function as leaderboard_main():
def leaderboard_main():
    # If 1: 
        # Print the “=====HIGH SCORES=====” title thing up top
        # Run the “order_scores” function
        # Run the “prettify_list” function


    # If 2:
        # Return to menu

