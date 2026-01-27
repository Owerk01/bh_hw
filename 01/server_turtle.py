import socket
import turtle
import threading

HOST = ("127.0.0.1", 6666)

screen = turtle.Screen()
screen.setup(1000, 1000)

t = turtle.Turtle('turtle')
t.speed(0)
t.color('blue')

def move_up():
    t.setheading(90)
    t.forward(10)
    
def move_right():
    t.setheading(0)
    t.forward(10)

def move_left():
    t.setheading(180)
    t.forward(10)

def move_down():
    t.setheading(270)
    t.forward(10)

def handle_client(conn):
    try:
        while 1:
            command = conn.recv(1024).decode()

            if command == "Up":
                move_up()
            elif command == "Down":
                move_down()
            elif command == "Right":
                move_right()
            elif command == "Left":
                move_left()
    except Exception as e:
        print(f"Somethng went wrong: {e}")
    finally:
        conn.close()

def start_server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(HOST)
    screen.listen()
    sock.listen(3)
    
    while(1):
        try:
            conn, addr = sock.accept()
            
            client_thread = threading.Thread(target=handle_client, args=(conn,))
            client_thread.daemon = True
            client_thread.start()
        except Exception as e:
            break;
        
    sock.close()

server_thread = threading.Thread(target=start_server)
server_thread.daemon = True
server_thread.start()

screen.listen
screen.mainloop()