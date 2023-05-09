# added blinking n times
#
# ver7 : fix win error - problem with indent of if win: break
# ver8 : add random start turn, add RESTART game
# ver9 : add RESTART request & accept
# ver10: anybody can request to RESTART

import socket
import threading
import RPi.GPIO as GPIO
import time
from random import randint

GPIO.setmode(GPIO.BCM)
leds = [23, 24, 25, 1]
for i in leds:
    GPIO.setup(i, GPIO.OUT)
    pass

HOST = 'localhost'
PORT = 9999
board = []
turn_flag = 0
turn_cnt = 0
led_times = 1
used_nums=[]
res_flag = 0

'''
turn_flag = 1
board = [[0, 0, 0],
         [0, 0, 0],
         [0, 0, 0]]
'''
MAX = 3

send_message:str = ''

def init():
    global board
    global turn_flag
    global turn_cnt
    global led_times
    global used_nums
    global res_flag

    turn_flag = randint(1, 2)
    board = [[0, 0, 0],
             [0, 0, 0],
             [0, 0, 0]]
    turn_cnt = 0
    led_times = 1
    used_nums = []
    res_flag = 0

    print(f"Start with TurnID: {turn_flag}\n")

    return 1

def switch_turn_flag(turn_flag):
    if turn_flag == 1:
        return 2
    else:
        return 1

def check_horizontal(turn):
    global MAX

    for y in range(MAX):
        win = True
        for x in range(MAX):
            if board[y][x] != turn:
                win = False
                break
        if win:
            return 1
    return 0

def check_vertical(turn):
    global MAX

    for y in range(MAX):
        win = True
        for x in range(MAX):
            if board[x][y] != turn:
                win = False
                break
        if win:
            return 1
    return 0

def check_diag_159(turn):
    global MAX

    for i in range(MAX):
        if board[i][i] != turn:
            return 0
    return 1

def check_diag_357(turn):
    global MAX

    for i in range(MAX):
        if board[i][MAX - 1 - i] != turn:
            return 0
    return 1

def check_tie():
    global MAX

    for y in range(MAX):
        for x in range(MAX):
            if board[y][x] == 0:
                return 0
    return 1

def check_win(turn, name):
    win_msg = "Congratulations! " + name + " won by completing "

    # horizoantal win
    if check_horizontal(turn):
        # multiple +
        if check_vertical(turn):
            return win_msg+"horizontal and vertical lines!"
        else:
            return win_msg+"horizontal line!"

    # vertical win
    if check_vertical(turn):
        return win_msg+"vertical line!"

    # diagonal win
    if check_diag_159(turn):
        # multiple X
        if check_diag_357(turn):
            return win_msg+"both diagonal lines!"
        else:
            return win_msg+"a diagonal line! (\)"
    
    # diagonal win
    if check_diag_357(turn):
        return win_msg+"a diagonal line! (/)"

    # tie
    if check_tie():
        return "It's a tie!"

    return 0


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

def received_message(clnt):
    global turn_flag
    global board
    global MAX
    global turn_cnt
    global led_times
    global used_nums
    global res_flag

    while True:
        raw_data = clnt.recv(1024).decode(encoding='utf-8')
        raw_data = raw_data.strip().split()
        turn = int(raw_data[0])
        name = raw_data[1]

        if len(raw_data) < 4:
            print("** Empty input! (Enter R to RESTART the game) **")
            continue

        data = raw_data[3]

        if res_flag == 1:
            if res_turn_flag != turn:
                print("-> Please wait for the other player to respond\n")
                continue
            if data == "r" or data == "R":
                print("-> Restarting game...\n")
                print("==============================\n")
                init()
            if data == "n" or data == "N":
                print("-> RESTART request rejected. Please continue\n")
                res_flag = 0
                res_turn_flag = switch_turn_flag(turn)
                continue
            else:
                print("-> Please respond to the RESTART request (R or N)\n")
                continue
        
        if data == "r" or data == "R":
            print(f"** {name} requested for a RESTART. Enter R to accept OR N to reject **")
            res_flag = 1
            res_turn_flag = switch_turn_flag(turn)
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
                    
        x = int(data % MAX - 1)
        y = int(data / MAX)

        if data % MAX == 0:
            x += MAX
            y -= 1

        board[y][x] = turn

        used_nums.append(data)
                    
        # show game board
        for y in board:
            print("\t", end='')
            for item in y:
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
            over = check_win(turn, name)
            if over != 0:
                print(over)
                print("Game over\n")
                print("Enter R to start a new game")
                print("==============================\n")
                                        
                if 'both' in over or 'and' in over:
                    led_times = 2
                for i in range(led_times):
                    for j in range(4):
                        GPIO.output(leds[j], GPIO.HIGH)
                        stop.wait(0.1)
                        GPIO.output(leds[j], GPIO.LOW)
                        stop.wait(0.1)
                for i in range(led_times * 5):
                    for j in range(4):
                        GPIO.output(leds[j], GPIO.HIGH)    
                    stop.wait(0.1)
                    for j in range(4):
                        GPIO.output(leds[j], GPIO.LOW)
                    stop.wait(0.1)
            else:
                print("==============================\n")
                print(f"NEXT TurnID: {turn_flag}\n")
        else:
            print("==============================\n")
            print(f"NEXT TurnID: {turn_flag}\n")
        

        turn_flag = switch_turn_flag(turn_flag)  

        #if data == 'led1_on':
            #GPIO.output(leds[0], GPIO.HIGH)
            #print('LED1 ON')   
            

with socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM, proto=0) as clnt:
    try:
        print("==============================\n")
        print("Game Start")
        init()

        clnt.connect((HOST, PORT))
        
        stop = threading.Event()

        t1 = threading.Thread(target=sending_message, args=(clnt,))
        t2 = threading.Thread(target=received_message, args=(clnt,))
        
        t1.start()
        t2.start()
        t1.join()
        t2.join()

    except KeyboardInterrupt:
        print("Keyboard interrupt")

    finally:
        GPIO.cleanup()
