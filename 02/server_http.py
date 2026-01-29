import socket
import json
import threading
import os
import datetime
import re

HOST = ("127.0.0.1", 8080)
OK = "HTTP/1.1 200 OK"
HEADERS = "Host: some.ru\nHost1: some1.ru\nContent-Type: text/html; charset=utf-8\n\n"
ERR_404 = "HTTP/1.1 404 Not Found\n\n"
LOGIN_PATTERN = re.compile(r'^[a-zA-Z0-9]{6,}$')
PASSWORD_PATTERN = re.compile(r'^(?=.*\d).{8,}$')

def send_message(message: str, sock):
    try:
        sock.send(message.encode())
    except Exception as e:
        print(f"Something went wrong: {e}")

def send_http_exception(message: str, sock):
    try:
        sock.send(b"HTTP/1.1 400 Error\n")
        sock.send(b"Content-Type: text/html; charset=utf-8\nConnection: close\nContent-Length: 85\n\n")
        sock.send(message.encode())
    except Exception as e:
        print(f"Something went wrong: {e}")

def check_file(filename: str) -> bool:
    if '.' not in filename:
        return False
    extension = filename.split('.')[-1]
    if extension in ["txt", "jpg", "png", "gif", "ico", "json", "html"]:
        return True
    else:
        return False
    
def check_login(login: str) -> bool:
    if LOGIN_PATTERN.search(login):
        return True
    else:
        return False

def check_password(password: str) -> bool:
    if PASSWORD_PATTERN.search(password):
        return True
    else:
        return False

def send_file(filename: str, conn):
    try:
        with open (filename.lstrip('/'), "rb") as f:
            send_message(OK, conn)
            send_message(HEADERS, conn)
            conn.send(f.read())
    except IOError:
        send_http_exception(ERR_404, conn)

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

def sign_up(login: str, password: str, conn) -> bool:
    try:
        if not check_login(login):
            send_message("Login must consist of only latin letters and numbers, minimum 6 characters", conn)
            return False
        if not check_password(password):
            send_message("Password must consist of only latin letters, at least one digit and any other symbols, minimum 8 characters", conn)
            return False
        check_result = check_exist(login=login, password=password)

        if check_result == "login_password":
            send_message(message=f"{datetime.datetime.now().strftime('%Y-%m-%d, %H:%M:%S')} - Error of registration {login} - User with this login and password already exists", sock=conn)
            return False
        if check_result == "login":
            send_message(message=f"{datetime.datetime.now().strftime('%Y-%m-%d, %H:%M:%S')} - Error of registration {login} - User with this login already exists", sock=conn)
            return False
        if check_result == "password":
            send_message(message=f"{datetime.datetime.now().strftime('%Y-%m-%d, %H:%M:%S')} - Error of registration {login} - User with this password already exists", sock=conn)
            return False
        
        with open("users.json", "r") as f:
            users = json.load(f)
        users.append({"login": login, "password": password})
        with open("users.json", "w") as f:
            json.dump(users, f, indent = 2)

        send_message(message=f"{datetime.datetime.now().strftime('%Y-%m-%d, %H:%M:%S')} - User {login} was registrated", sock=conn)
        return True
    except Exception as e:
        send_message(f"Something went wrong: {e}", conn)

def sign_in(login: str, password: str, conn) -> bool:
    try:
        check_result = check_exist(login=login, password=password)

        if check_result == "No_matches":
            send_message(message=f"{datetime.datetime.now().strftime('%Y-%m-%d, %H:%M:%S')} - Error of signing in {login} - Incorrect login and password", sock=conn)
            return False
        if check_result == "login":
            send_message(message=f"{datetime.datetime.now().strftime('%Y-%m-%d, %H:%M:%S')} - Error of signing in {login} - Incorrect password", sock=conn)
            return False
        if check_result == "password":
            send_message(message=f"{datetime.datetime.now().strftime('%Y-%m-%d, %H:%M:%S')} - Error of signing in {login} - Incorrect login", sock=conn)
            return False

        send_message(message=f"{datetime.datetime.now().strftime('%Y-%m-%d, %H:%M:%S')} - User {login} - Signed in successfully", sock=conn)
        return True
    except Exception as e:
        send_message(f"Something went wrong: {e}", conn)

def check_http(string: list) -> bool:
    if len(string) != 3:
        return False

    if not string[2].startswith("HTTP"):
        return False
    
    return True

def handle_http(http: list, conn):
    try:
        if not http[0] == "GET":
            send_message(message="Unsupported method", sock=conn)

        if http[1] == "/":
            send_file("1.html", conn)
        elif "/test/" in http[1]:
            parts = http[1].split('/')
            num = parts[parts.index("test") + 1]
            answer = f"Test with number {num} is running"
            send_message(OK, conn)
            send_message(HEADERS, conn)
            send_message(answer, conn)
        elif "/message/" in http[1]:
            parts = http[1].split('/')
            login, text = parts[parts.index("message") + 1], parts[parts.index("message") + 2]
            answer = f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - message from user {login} - {text}"
            send_message(OK, conn)
            send_message(HEADERS, conn)
            send_message(answer, conn)
        elif check_file(http[1]):
            send_file(http[1], conn)
        else:
            send_message(OK, conn)
            send_message(HEADERS, conn)
            send_message("Unsupported command", conn)
    except Exception as e:
        send_http_exception(f"Something went wrong: {e}", conn)

def handle_not_html(parts: list, conn):
    try:
        if len(parts) != 3:
            send_message(message="Incorret format of command",sock=conn)
            return
            
        # reg user1 pass_user1
        if parts[0] == "reg":
            sign_up(login=parts[1], password=parts[2], conn=conn)
        elif parts[0] == "signin":
            sign_in(login=parts[1], password=parts[2], conn=conn)
    except Exception as e:
        send_http_exception(f"Something went wrong: {e}", conn)

def handle_client(conn):
    try:
        while 1:
            message = conn.recv(1024).decode()
            first_string = message.split('\n')[0].split()
            is_http = check_http(string=first_string)

            if is_http:
                handle_http(first_string, conn)
            else:
                handle_not_html(first_string, conn)      
    except ConnectionError:
        print("Client broke connection")
    except Exception as e:
        if is_http:
            send_http_exception(f"Something went wrong: {e}", conn)
        else:
            send_message(f"Something went wrong: {e}", conn)
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
        print("Server is closed")
    except Exception as e:
        print(f"Somethng went wrong: {e}")
    
    sock.close()

if __name__ == "__main__":
    main()