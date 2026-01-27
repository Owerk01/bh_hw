import socket

HOST = ("127.0.0.1", 6666)

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(HOST)
    sock.send(b"stop")
    print(sock.recv(1024).decode())
    sock.close()

if __name__ == "__main__":
    main()