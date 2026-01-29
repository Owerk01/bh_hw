import socket

HOST = ("127.0.0.1", 8080)

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(HOST)

    try:
        while 1:
            command = input("Enter command: ")
            sock.send(command.encode())
            print(sock.recv(1024).decode(), "\n")
    except KeyboardInterrupt:
        print("\nConnection was broken")
    sock.close()

if __name__ == "__main__":
    main()