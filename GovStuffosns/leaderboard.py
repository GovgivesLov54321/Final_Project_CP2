# GNB - Code to make leaderboard look pretty

# End up here from Ally's main menu if user wants to view the leaderboard:

# Display options to User as: 1. View Leaderboard -- 2. Return to Main Menu
choice = input("Welcome to the Leaderboard, User!" \
"1. View Leaderboard" \
"2. Return to Main Menu")

# Define function as order_scores():
def order_scores():
    # read from Ally’s csv, the columns for top five scores
    # re-organize, by writing to have 5 largest scores in descending order


# Define function as prettify_list():
	# take from Ally’s renewed scores list, and print for every row in the csv in a certain format: (f"RANK NUMBER {row["rank number"]} == USERNAME {row["username"]} == SCORE {row["score"]})

# I believe this’ll also be used when showing the User if they made leaderboard or not: If this is the case, then just run the option 1

# If 1: 
    # Print the “=====HIGH SCORES=====” title thing up top
    # Run the “order_scores” function
    # Run the “prettify_list” function


# If 2:
    # Return to menu
