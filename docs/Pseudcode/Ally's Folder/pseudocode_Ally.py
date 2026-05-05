# START PROGRAM

#     call initialize_system
#     call load_user_database

#     while program is running

#         choice = show_main_menu
#
#         if choice == "login"
#             call handle_login
#
#         else if choice == "signup"
#             call handle_signup

#         else if choice == "guest"
#             call start_guest_game

#         else if choice == "exit"
#             call terminate_program

#     end while

# END PROGRAM

# --------------------------------------------------
# initialization (gui + visuals)

# function initialize_system
#     create main window
#     set resolution and title
#     load background assets (animated drawings, messy art style)
#     load button animations (hover, click effects)
#     start looping background animation
# end function

# --------------------------------------------------
# loading and saving users (csv system)

# function load_user_database
#     try to open "users.csv"

#     if file exists
#         read each line
#         split by comma into username and password
#         store in dictionary or list

#     else
#         create "users.csv"
#         initialize empty user list

# end function

# function save_user_database
#     open "users.csv" in write mode

#     for each user in database
#         write username + "," + password

#     close file
# end function

# --------------------------------------------------
# main menu (animated gui)

# function show_main_menu
#     draw animated background
#     display title text

#     draw buttons:
#         login
#         signup
#         play as guest
#         exit

#     add hover effects (button grows or changes color)
#     add click animation
#     wait for user click
#     return selected option
# end function

# --------------------------------------------------
# login system

# function handle_login
#     username = get input
#     password = get input

#     if username is empty or password is empty
#         display "fields cannot be empty"
#         return

#     if username exists in database
#         if password matches stored password
#             display "login successful"
#             call start_game(username)
#         else
#             display "incorrect password"
#     else
#         display "user not found"
# end function

# --------------------------------------------------
# signup system

# function handle_signup
#     username = get input
#     password = get input

#     if username or password is empty
#         display error and return

#     if username already exists
#         display "username taken"
#         return

#     add user to database
#     call save_user_database

#     display "account created"
# end function

# --------------------------------------------------
# guest mode

# function start_guest_game
#     generate random number
#     guest_name = "guest_" + number

#     display "playing as " + guest_name
#     call start_game(guest_name)
# end function

# --------------------------------------------------
# starting the game

# function start_game(player_name)
#     load game scene
#     display welcome message

#     while game is running
#         update game logic
#         render graphics
#         handle player input
#     end while
# end function

# --------------------------------------------------
# error handling (basic idea)

# function safe_input(prompt)
#     try
#         get user input
#     catch error
#         display "invalid input"
#         retry input
# end function

# --------------------------------------------------
# closing the program

# function terminate_program
#     call save_user_database
#     close window
#     stop program
# end function

# HI THIHIHTIHTIHTIT
