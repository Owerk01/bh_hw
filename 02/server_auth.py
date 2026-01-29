import socket
import json
import threading
import os

HOST = ("127.0.0.1", 8080)

def send_message(message: str, sock):
    sock.send(message.encode())

def check_exist(login: str, password: str) -> str:
    with open("users.json", "r") as f:
        users = json.load(f)

    for user in users:
        if user["login"] == login and user["password"] == password:
            return "login_password"
        if user["login"] == login:
            return "login"
        if user["password"] == password:
            return "password"
    return "No_matches"

def sign_up(login: str, password: str, conn) -> str:
    check_result = check_exist(login=login, password=password)

    if check_result == "login_password":
        send_message(message="User with this login and password already exists", sock=conn)
        return False
    if check_result == "login":
        send_message(message="User with this login already exists", sock=conn)
        return False
    if check_result == "password":
        send_message(message="User with this password already exists", sock=conn)
        return False
    
    with open("users.json", "r") as f:
        users = json.load(f)
    users.append({"login": login, "password": password})
    with open("users.json", "w") as f:
        json.dump(users, f, indent = 2)

    send_message(message="Registration was successful", sock=conn)
    return True

def sign_in(login: str, password: str, conn) -> str:
    check_result = check_exist(login=login, password=password)

    if check_result == "No_matches":
        send_message(message="Incorrect login and password", sock=conn)
        return False
    if check_result == "login":
        send_message(message="Incorrect password", sock=conn)
        return False
    if check_result == "password":
        send_message(message="Incorrect login", sock=conn)
        return False

    send_message(message="Signed in successfully", sock=conn)
    return True

def handle_client(conn):
    try:
        while 1:
            command = conn.recv(1024).decode().strip()
            parts = command.split()

            if len(parts) != 3:
                send_message(message="Incorret format of command",sock=conn)
                continue
            # reg user1 pass_user1
            if parts[0] == "reg":
                sign_up(login=parts[1], password=parts[2], conn=conn)
            elif parts[0] == "signin":
                sign_in(login=parts[1], password=parts[2], conn=conn)
    except ConnectionError:
        print("Client broke connection")
    finally:
        conn.close()

def main():
    if not os.path.exists("users.json"):
        with open("users.json", "w", encoding="utf-8") as f:
            json.dump([], f)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(HOST)
    sock.listen(3)
    sock.settimeout(1)

    try:
        while 1:
            try:
                conn, addr = sock.accept()
                client_thread = threading.Thread(target=handle_client, args=(conn,))
                client_thread.daemon = True
                client_thread.start()
            except socket.timeout:
                continue
    except KeyboardInterrupt:
        print("\nServer is closed")
    except Exception as e:
        print(f"Somethng went wrong: {e}")
    
    sock.close()

if __name__ == "__main__":
    main()