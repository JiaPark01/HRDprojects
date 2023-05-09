# added blinking n times

import socket
import threading
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
leds = [23, 24, 25, 1]
for i in leds:
    GPIO.setup(i, GPIO.OUT)
    pass

HOST = 'localhost'
PORT = 9999
turn_flag = 1
board = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
used_nums = []
MAX = 3

send_message:str = ''

def check_win(turn):
    global MAX

    # horizontal win
    for y in range(MAX):
        win = True
        for x in range(MAX):
            if board[y][x] != turn:
                win = False
                break
        if win:
            return 1

    # vertical win
    for y in range(MAX):
        win = True
        for x in range(MAX):
            if board[x][y] != turn:
                win = False
                break
        if win:
            return 2

    # diagonal win \
    win = True
    for i in range(MAX):
        if board[i][i] != turn:
            win = False
            break
    if win:
        return 3
    
    # diagonal win /
    win = True
    for i in range(MAX):
        if board[i][MAX - 1 - i] != turn:
            win = False
            break
    if win:
        return 3

    tie = True
    for y in range(MAX):
        for x in range(MAX):
            if board[y][x] == 0:
                tie = False
                break
    if tie:
        return 4

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
    global used_nums
    global board
    global MAX

    while True:
        raw_data = clnt.recv(1024).decode(encoding='utf-8')
        raw_data = raw_data.strip().split()
    
        turn = int(raw_data[0])
        #print("turn: " + str(turn) + ".")
        name = raw_data[1]
        data = int(raw_data[3])
        over = 0
       
        if turn_flag == turn:
            if 1 <= data <= 9:
                if data not in used_nums:
                    print("================")
                    print("turn : " + str(turn))
                    print("Name : " + name)
                    print("data : " + str(data))
                    print()
                    
                    x = int(data % MAX - 1)
                    y = int(data / MAX)

                    if data % MAX == 0:
                        x += MAX
                        y -= 1

                    board[y][x] = turn

                    used_nums.append(data)
                    
                    # show game board
                    for i in range(MAX):
                        for j in board[i]:
                            if j == 1:
                                print("O", end = ' ')
                            elif j == 2:
                                print("X", end= ' ')
                            else:
                                print("-", end = ' ')
                        print()
                    print()
                    
                    # check for win
                    over = check_win(turn)
                    if over != 0:
                        if over != 4:
                            print(name + " won by completing", end = ' ')
                        if over == 1:
                            print("horizontal line!")
                        elif over == 2:
                            print("vertical line!")
                        elif over == 3:
                            print("diagonal line!")
                        elif over == 4:
                            print("A tie!")
                        print("Game over")

                    if (turn_flag == 1): turn_flag = 2
                    else: turn_flag = 1
                else:
                    print(str(data) + " is already used")
            else:
                print("Number must be between 1 and 9")
        else:
            print("Not " + name +"'s turn!\nYour turn: " + str(turn)+ ", This turn: " + str(turn_flag))
    

        #if data == 'led1_on':
            #GPIO.output(leds[0], GPIO.HIGH)
            #print('LED1 ON')   
            

with socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM, proto=0) as clnt:
    try:
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
