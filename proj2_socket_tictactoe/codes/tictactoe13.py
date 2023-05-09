# added blinking n times
#
# ver7 : fix win error - problem with indent of if win: break
# ver8 : add random start turn, add RESTART game
# ver9 : add RESTART request & accept
# ver10: anybody can request to RESTART
# ver11: make game board more vivid, fixed restarting bug
# ver12: added action to player leaving, move LED to another func, fixed both quitting bug, start making notes
# ver13: move printing board to a func, change board frame from 3 to 4, finished making notes

import socket
import threading            # to use threading for the socket prg
import RPi.GPIO as GPIO     # to control the leds in raspberry pi
import time                 # to control the leds
from random import randint  # to generate random number to assign who starts the game

GPIO.setmode(GPIO.BCM)      # use the pin according to the GPIO module num
leds = [23, 24, 25, 1]      # leds1, 2, 3, 4
for i in leds:              # for all leds set them as output
    GPIO.setup(i, GPIO.OUT)

HOST = 'localhost'
PORT = 9999
board = []      # tictactoe game board
turn_flag = 0   # indicates whose turn it is
turn_cnt = 0    # increase each turn, when it reaches 5 start checking for win since minimum number of turn for a win is 5 (to minimise func call)
used_nums=[]    # collects the numbers used to prevent changing the area when already allocated
res_flag = 0    # sets whether someone has requested for a restart. if 1, the player requested must wait until the other responds. the other can only enter r or n when 1

BOARD_LEN = 3   # 3x3 board 

#send_message:str = ''

def init():    # initialising a new game by start or restart
    global board
    global turn_flag
    global turn_cnt
    global used_nums
    global res_flag

    turn_flag = randint(1, 2)   # randomly assign the order
    board = [[0, 0, 0],         # init board with 0, a 2D list for x-axis y-axis
             [0, 0, 0],
             [0, 0, 0]]
    turn_cnt = 0
    used_nums = []
    res_flag = 0

    print(f"Start with TurnID: {turn_flag}\n")  # tells who starts

    return 0

def print_board(frame):                             # print the board after each turn
    print()
    for y in range(frame):                          # for the length of y = 7
        print("\t", end='')                         # always insert \t at the beginning of each line
        if y == 0 or y == frame-1:                  # if it's the first line or the last line
            print("*", end='')                      # print * all the way to the end of x-axis
            for x in range(frame-1):                # two different * and ** to adjust the length (-1 since * is printed at the front)
                print("**", end = '')
        elif y == 1 or y == frame-2:                # if it's the second line or the second to the last line
            print("*", end='')                      # print * at the beginning
            for x in range(frame-1):                # for the rest of the x-axis (-1 since * is printed at the front)
                if x == frame-2:                    # print * at the end
                    print(" *", end='')
                else:                               # and space in the middle
                    print("  ", end='')
        else:                                       # for the remaining y-axis to print the board
            print("* ", end='')                     # print * at the beginning
            for x in range(frame):                  # for the x-axis
                if x == frame-1:                    # print * at the end (-1 since * is printed at the front)
                    print(" *", end='')
                elif x <= 1 or x == frame-2:        # for spaces after the first * and before the last * print once space
                    print(" ", end = '')
                else:                               # for the remaining area where the actual board is to be printed
                    item = board[y-2][x-2]          # bring the data in the board (-2 since x and y are both starting from 2 because of * and space)
                    if item == 1:                   # if it's filled by turn 1 user, print O
                        print("O", end = ' ')
                    elif item == 2:                 # if it's filled by turn 2 user, print X
                        print("X", end= ' ')
                    else:                           # if it's not filled yet, print -
                        print("-", end = ' ')       # spaces for visual convenience
        print()                                     # change line at the end of x-axis
    print()                                         # give extra space after the board is printed

def switch_turn_flag(turn_flag):                    # changes the turn to the other person between 1 and 2
    if turn_flag == 1:
        return 2
    else:
        return 1

def game_over(clnt, name, win_msg):                 # finishes game and shows different messages&leds depending on each situation
    led_times = 1   # multiple base for the number of times leds blink depending on how a player won the game (short for simple win, longer for a difficult win)

    if win_msg != 0:                                # if the game finished without somebody quitting
        print(win_msg)                              # print the message
        print("Game Over\n")
        print("Enter R to start a new game")
        print("==============================\n")
                            
        if 'both' in win_msg or 'and' in win_msg:   # if won by completing two lines
            led_times = 2                           # leds blink for longer
        elif 'tie' in win_msg:                      # if it's a tie
            led_times = 0                           # leds don't blink
    else:                                           # if the game finished because somebody quit
        print(f"{name} won by default")

    for i in range(led_times):                      # blink leds
        for j in range(4):                          # blinks 1 2 3 4 in order
            GPIO.output(leds[j], GPIO.HIGH)
            stop.wait(0.1)
            GPIO.output(leds[j], GPIO.LOW)
            stop.wait(0.1)
    for i in range(led_times * 5):                  # all 4 blink at the same time
        for j in range(4):
            GPIO.output(leds[j], GPIO.HIGH)    
        stop.wait(0.1)
        for j in range(4):
            GPIO.output(leds[j], GPIO.LOW)
        stop.wait(0.1)

    return 1                                        # set the variable (game) over to true

def check_horizontal(turn):                         # check if any line is completed horizontally
    global BOARD_LEN

    for y in range(BOARD_LEN):                      # for the vertical num of the board
        win = True                                  # reset the win flag as True
        for x in range(BOARD_LEN):                  # for the horizontal num of the board
            if board[y][x] != turn:                 # if the val in the board is not written by the player
                win = False                         # change win flag to False and skip this line
                break
        if win:                                     # if the above loop goes through successfully at least once, it's completed
            return 1
    return 0                                        # if the first for loop is finished without returning 1, it means none of the rows are completed

def check_vertical(turn):                           # check if any line is completed vertically
    global BOARD_LEN

    for y in range(BOARD_LEN):                      # for the vertical num of the board
        win = True                                  # reset the win flag as True
        for x in range(BOARD_LEN):                  # for the horizontal num of the board
            if board[x][y] != turn:                 # [x][y] is the other direction of horizontal
                win = False                         # change win flag to False if the value in the board is not the player's
                break
        if win:                                     # if the above loop goes through successfully at least once, it's completed
            return 1
    return 0                                        # if the first for loop is finished without returning 1, it means none of the rows are completed

def check_diag_159(turn):                           # check if \ is completed
    global BOARD_LEN

    for i in range(BOARD_LEN):                      # for the length of the board
        if board[i][i] != turn:                     # if \ (0,0) (1,1) (2,2) is not written by the player
            return 0                                # return false
    return 1                                        # if successfully go through all three, it's completed

def check_diag_357(turn):                           # check if / is completed
    global BOARD_LEN

    for i in range(BOARD_LEN):                      # for the length of the board
        if board[i][BOARD_LEN - 1 - i] != turn:     # if / (2,0) (1,1) (0,2) is not written by the player
            return 0                                # return false
    return 1                                        # if successfully go through all three, it's completed

def check_tie():                                    # check if it's a tie
    global BOARD_LEN

    for y in range(BOARD_LEN):                      # for the vertical num of the board
        for x in range(BOARD_LEN):                  # for the horizontal num of the board
            if board[y][x] == 0:                    # if any of the board is empty, return false
                return 0
    return 1                                        # otherwise the board is full, buf if anybody won, this func is not called so it's a tie

def check_win(turn, name):                          # from turn 5, start checking if anyone won
    win_msg = "Congratulations! " + name + " won by completing "    # default win message
    hori = False
    vert = False
    diag_159 = False
    diag_357 = False
    # horizoantal win
    if check_horizontal(turn):                      # if a horizontal line is completed, save it as True
        hori = True

    # vertical win
    if check_vertical(turn):                        # if a vertical line is completed, save it as True
        vert = True

    # diagonal win
    if check_diag_159(turn):                        # if a \ line is completed, save it as True
        diag_159 = True

    if check_diag_357(turn):                        # if a / line is completed, save it as True
        diag_357 = True

    if hori and vert:                               # if both hori and vert lines are completed
        return win_msg+"horizontal and vertical lines!"
    elif diag_159 and diag_357:                     # if both diagonal lines are completed
        return win_msg+"both diagonal lines!"
    elif diag_159 or diag_357:                      # if only one of the diagonal lines is completed
        if hori:                                    # if diagonal + horizontal
            return win_msg+"diagonal and horizontal lines!"
        elif vert:                                  # if diagonal + vertical
            return win_msg+"diagonal and vertical lines!"
        elif diag_159:                              # if the diagonal is \
            return win_msg+"a diagonal line! (\)"
        else:                                       # the remaining is /
            return win_msg+"a diagonal line! (/)"
    elif hori:                                      # if only horizontal line is completed
        return win_msg+"a horizontal line!"
    elif vert:                                      # if only vertical
        return win_msg+"a vertical line!"

    # tie
    if check_tie():                                 # if nobody won, but all areas are filled in
        return "It's a tie!"

    return 0                                        # if nothing happened return 0

'''
def sending_message(clnt):
    while True:
        if GPIO.input(leds[0]):
            pass
            #send_message = 'LED1 LIGHT ON checked'
            #clnt.sendall(send_message.encode(encoding='utf-8'))
        elif GPIO.input(leds[1]):
            pass
            #send_message = 'LED2 LIGHT ON checked'
            #clnt.sendall(send_message.encode(encoding='utf-8'))
'''
def received_message(clnt):
    global turn_flag
    global board
    global BOARD_LEN
    global turn_cnt
    global used_nums
    global res_flag

    frame = BOARD_LEN + 4                           # set the frame of the board with 1 space on each side --> 4
    win_msg = 0                                     # var to save the message when won
    over = 0                                        # flag when a game is over
    players = {}                                    # a dictionary of players to match turnID and name
    player_num = 0                                  # var to save the number of players

    while True:
        raw_data = clnt.recv(1024).decode(encoding='utf-8') # read message from the server
        raw_data = raw_data.split()                         # split the message into turnID, name, data
        turn = int(raw_data[0])                             # save the turnID as int
        name = raw_data[1]                                  # save the name as string

        if turn not in players:                             # if it's a new player
            players.update({turn : name})                   # add the info to the dictionary as turnID as key and name as the value
            player_num +=1                                  # increase the number of player

        if player_num == 2:                                 # if both players are registered
            op_name = players[switch_turn_flag(turn)]       # save the name of the opposite player as op_name

        if len(raw_data) < 4:                               # if the message from the server has no data part, the length is 3.
            print("** Empty input! (Enter R to RESTART the game) **")   # without this, it causes IndexError when try to access raw_data[3]
            continue                                        # all continue statements return to the beginning of the loop to get a new input

        data = raw_data[3]                                  # save data safely

        if data == "q" or data == "Q":                      # if a player entered q or Q
            if player_num  == 2:                            # if both players were registered, the other player wins by default
                try:                                        # it sometimes causes an TypeError when q is pressed after winning, so use try
                    over = game_over(clnt, op_name, over)
                    print(f"** {name} has left the game. **")  # shows who left
                except TypeError:
                    print(f"** {name} has left the game. (but with error) **")
                player_num -= 1                             # decrease the number of players
            else:                                           # if there is only one player, nobody wins and nothing happens
                print("Bye!")                               
                player_num -= 1                             # decrease the numer of players
            continue

        if res_flag == 1:                                   # if somebody requested for a restart
            if res_turn_flag != turn:                       # if a player sent a message when it's not his/her turn to respond to the request
                print("-> Please wait for the other player to respond") # ask to request and show who it's waiting for
                print(f"-> Waiting for {players[res_turn_flag]}")
                continue
            if data == "r" or data == "R":                  # if the person responded with r, restart the game
                print(f"** {name} accepted! **")
                print("-> Restarting game...\n")
                print("==============================\n")
                over = init()
                continue
            if data == "n" or data == "N":                  # if the person resonded with n, it doesn't restart
                print("-> RESTART request rejected")
                if over == 0:                               # if the request was made during the game, show whose turn it is
                    print(f"-> TurnID: {turn_flag}")
                else:                                       # if the request was made at the end of the game, shows nothing. just adjust line spacing
                    print()
                res_flag = 0                                # change the flag back to 0, so that the game continues normally after rejecting
                #res_turn_flag = switch_turn_flag(turn)
                continue
            else:                                           # if any other letter is entered, ask again to respond with r or n
                print("-> Please respond to the RESTART request (R or N)")
                continue

        if data == "r" or data == "R":                      # if entered r, request the other player to restart
            print(f"** {name} requested for a RESTART. (Enter R to accept OR N to reject) **")
            res_flag = 1                                    # set the flag to 1 so that the program only deals with the other player to respond b/w r or n
            res_turn_flag = switch_turn_flag(turn)          # set who has to respond
            continue

        if over == 1:                                       # if the game is over and a player enters anything, tell them it's over
            print("** The game is over **")
            continue

        if turn_flag != turn:                               # if the game is on-going and another player tries to intercept the turn, it tells it's not his/her turn
            print(f"** Not {name}'s turn! **")
            print(f"-> Your turnID: {turn}, This turn: {turn_flag}\n")
            continue

        '''                                                 # it can be used when too many values are entered, but it only takes the data from the 4th place so not necessary
        if len(raw_data) > 4:
            print("** Enter a single number! (Enter R to RESTART the game) **")
            continue
        '''

        try:                                                # check if the entered input can be converted into an int
            data = int(data)
        except ValueError:                                  # it prevents from the prg terminating when a letter other than q is entered during normal state
            print("** Enter an integer! (Enter R to RESTART the game) **")
            print(f"-> Your input: {raw_data[3]}\n")        # shows why the input was rejected
            continue

        if not 1 <= data <= 9:                              # checks if the number if between 1~9
            print("** Number must be between 1 and 9 **\n")
            continue

        if data in used_nums:                               # checks if the number is already used
            print(f"** {data} is already used**\n")
            continue

        turn_cnt += 1                                       # if the player goes through all the above stages, filling in a board is available, so increase turn count
        print("==============================\n")
        print(f"TurnID : {turn}")                           # prints the information about the player and the number given
        print(f"Name   : {name}")
        print(f"Number : {data}")
        print()
                    
        x = int(data % BOARD_LEN - 1)                       # calc the x-axis with the given number. 1, 6, 9 --> 0. -1 since 1%3 is 1, but index starts from 0
        y = int(data / BOARD_LEN)                           # calc the y-axis with the given number. 1, 2, 3 --> 0

        if data % BOARD_LEN == 0:                           # if the value % 3 == 0
            x += BOARD_LEN                                  # increase x value by 3. (3 % 3 - 1) becomes -1, so add 3 to make 2
            y -= 1                                          # decrease y value by 1. (3 / 3)     becomes 1, so take away 1 to make 0

        board[y][x] = turn                                  # fill in the board with the values. y comes first since it's a 2D array

        used_nums.append(data)                              # add the number to the used_nums
                    
        # show game board
        print_board(frame)                                  # displays the board
                  
        # check for win
        if turn_cnt >= 5:                                   # from 5th turn check for a win
            win_msg = check_win(turn, name)                 # if won, corresponding message is returned. if not, 0 is returned
            if win_msg != 0:                                # if a message is returned
                over = game_over(clnt, name, win_msg)       # somebody won. finish game and show who won
            else:                                           # if - is returned, the game is on-going. show who's next
                print("==============================\n")
                print(f"NEXT TurnID: {switch_turn_flag(turn_flag)}\n")
        else:                                               # if the turn has not reached 5, nobody can win so skip checking with functions
            print("==============================\n")
            print(f"NEXT TurnID: {switch_turn_flag(turn_flag)}\n")
        
        turn_flag = switch_turn_flag(turn_flag)             # switch the turn to the other player

with socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM, proto=0) as clnt:
    try:
        print("==============================\n")           # let the players know that the game has successfully started
        print("Game Start")
        init()

        clnt.connect((HOST, PORT))
        
        stop = threading.Event()                            # used to keep the leds on or off for certain amount of time

        #t1 = threading.Thread(target=sending_message, args=(clnt,))
        t2 = threading.Thread(target=received_message, args=(clnt,))
        
        #t1.start()
        t2.start()
        #t1.join()
        t2.join()

    except KeyboardInterrupt:
        print("Keyboard interrupt")

    finally:
        GPIO.cleanup()                                      # turn off everything before closing the prg
