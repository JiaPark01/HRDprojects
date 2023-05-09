# added blinking n times
#
# ver7 : fix win error - problem with indent of if win: break
# ver8 : add random start turn, add RESTART game
# ver9 : add RESTART request & accept
# ver10: anybody can request to RESTART
# ver11: make game board more vivid, fixed restarting bug
# ver12: added action to player leaving, move LED to another func, fixed both quitting bug

import socket
import threading
import RPi.GPIO as GPIO
import time
from random import randint

GPIO.setmode(GPIO.BCM)
leds = [23, 24, 25, 1]
for i in leds:
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

def switch_turn_flag(turn_flag):    # changes the turn to the other person
    if turn_flag == 1:
        return 2
    else:
        return 1

def game_over(clnt, name, win_msg): # finishes game and shows different messages&leds depending on each situation
    led_times = 1       # multiple base for the number of times leds blink depending on how a player won the game (short for simple win, longer for a difficult win)

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

    frame = len(board) + 3                          # set the frame of the board with 1 space on each side --> 4
    win_msg = 0
    over = 0
    players = {}
    player_num = 0

    while True:
        raw_data = clnt.recv(1024).decode(encoding='utf-8')
        raw_data = raw_data.strip().split()
        turn = int(raw_data[0])
        name = raw_data[1]          

        if turn not in players:
            players.update({turn : name})
            player_num +=1

        if player_num == 2:
            op_name = players[switch_turn_flag(turn)]

        if len(raw_data) < 4:
            print("** Empty input! (Enter R to RESTART the game) **")
            continue

        data = raw_data[3]

        if data == "q" or data == "Q":
            if player_num  == 2:
                print(f"** {name} has left the game. **")
                try:
                    over = game_over(clnt, op_name, over)
                except TypeError:
                    print("Bye!")
                player_num -= 1
            else:
                print("Bye!")
                player_num -= 1
            continue

        if res_flag == 1:
            if res_turn_flag != turn:
                print("-> Please wait for the other player to respond")
                print(f"-> Waiting for TurnID: {res_turn_flag}")
                continue
            if data == "r" or data == "R":
                print(f"** {name} accepted! **")
                print("-> Restarting game...\n")
                print("==============================\n")
                over = init()
                continue
            if data == "n" or data == "N":
                print("-> RESTART request rejected")
                if over == 0:
                    print(f"-> TurnID: {turn_flag}")
                else:
                    print()
                res_flag = 0
                res_turn_flag = switch_turn_flag(turn)
                continue
            else:
                print("-> Please respond to the RESTART request (R or N)")
                continue

        if data == "r" or data == "R":
            print(f"** {name} requested for a RESTART. (Enter R to accept OR N to reject) **")
            res_flag = 1
            res_turn_flag = switch_turn_flag(turn)
            continue

        if over == 1:
            print("** The game is over **")
            continue

        if turn_flag != turn:
            print(f"** Not {name}'s turn!**\n-> Your turnID: {turn}, This turn: {turn_flag}\n")
            continue

        '''
        if len(raw_data) > 4:
            print("** Enter a single number! (Enter R to RESTART the game) **")
            continue
        '''

        try:
            data = int(data)
        except ValueError:
            print("** Enter an integer! (Enter R to RESTART the game) **")
            print(f"-> Your input: {raw_data[3]}\n")
            continue

        if not 1 <= data <= 9:
            print("** Number must be between 1 and 9 **\n")
            continue

        if data in used_nums:
            print(f"** {data} is already used**\n")
            continue

        turn_cnt += 1
        print("==============================\n")
        print(f"TurnID : {turn}")
        print(f"Name   : {name}")
        print(f"Number : {data}")
        print()
                    
        x = int(data % BOARD_LEN - 1)
        y = int(data / BOARD_LEN)

        if data % BOARD_LEN == 0:
            x += BOARD_LEN
            y -= 1

        board[y][x] = turn

        used_nums.append(data)
                    
        # show game board
        print()
        for y in range(frame+1):
            print("\t", end='')
            if y == 0 or y == frame:
                print("*", end='')
                for x in range(frame):
                    print("**", end = '')
            elif y == 1 or y == frame-1:
                print("*", end='')
                for x in range(frame):
                    if x == frame - 1:
                        print(" *", end='')
                    else:
                        print("  ", end='')
            else:
                print("* ", end='')
                for x in range(frame+1):
                    if x == frame:
                        print(" *", end='')
                    elif x <= 1 or x == frame-1:
                        print(" ", end = '')
                    else:
                        item = board[y-2][x-2]
                        if item == 1:
                            print("O", end = ' ')
                        elif item == 2:
                            print("X", end= ' ')
                        else:
                            print("-", end = ' ')
            print()
        print()
                  
        # check for win
        if turn_cnt >= 5:
            win_msg = check_win(turn, name)
            if win_msg != 0:
                over = game_over(clnt, name, win_msg)                
            else:
                print("==============================\n")
                print(f"NEXT TurnID: {switch_turn_flag(turn_flag)}\n")
        else:
            print("==============================\n")
            print(f"NEXT TurnID: {switch_turn_flag(turn_flag)}\n")
        
        turn_flag = switch_turn_flag(turn_flag)

with socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM, proto=0) as clnt:
    try:
        print("==============================\n")
        print("Game Start")
        init()

        clnt.connect((HOST, PORT))
        
        stop = threading.Event()

        #t1 = threading.Thread(target=sending_message, args=(clnt,))
        t2 = threading.Thread(target=received_message, args=(clnt,))
        
        #t1.start()
        t2.start()
        #t1.join()
        t2.join()

    except KeyboardInterrupt:
        print("Keyboard interrupt")

    finally:
        GPIO.cleanup()
