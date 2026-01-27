import socket
import logging
import datetime
import threading
import random
import time

HOST = ("127.0.0.1", 6666)
LOG_FILE = "server.log"
stop_event = threading.Event()

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s | %(message)s"
)

def send_log(command: str) -> None:
    logging.info(command)

def date_answer() -> str:
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def rnd_answer(command: list) -> str:
    try:
        return str(random.randint(min(int(command[1]), int(command[2])), max(int(command[1]), int(command[2]))))
    except Exception as e:
        return f"Something went wrong: {e}"
    
def handle_request(command: str) -> str:
    global stop_event
    try:
        if command == "time":
            return f"current date and time: {date_answer()}"
        elif command.startswith('rnd'):
            command = command.split()
            return f"random number from {int(command[1])} to {int(command[2])} is {rnd_answer(command)}"
        elif command == "stop":
            stop_event.set()
            return "Server is closed"
        else:
            return "Unknown command"
    except Exception as e:
        return f"Something went wrong: {e}"
    
def service_client(conn: socket, addr):
    command = conn.recv(1024).decode()
    send_log(command)
    answer = handle_request(command)
    conn.send(answer.encode())
    time.sleep(0.1)
    if answer == "Server is closed":
        conn.close()
        

def main():
    global stop_event
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(HOST)
    sock.listen(3)
    sock.settimeout(1.0)
    try:
        while not stop_event.is_set():
            try:
                conn, addr = sock.accept()
                thread = threading.Thread(target=service_client, args=(conn, addr))
                thread.daemon = True
                thread.start()
            except socket.timeout:
                continue
            except OSError:
                break
    except KeyboardInterrupt:
        print("Server is stopped")
    finally:
        sock.close()

if __name__ == "__main__":
    main()