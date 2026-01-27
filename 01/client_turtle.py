import socket
from pynput import keyboard

HOST = ("127.0.0.1", 6666)

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(HOST)

def press(command):
    try:
        if command == keyboard.Key.up:
            sock.send(b"Up")
        elif command == keyboard.Key.down:
            sock.send(b"Down")
        elif command == keyboard.Key.right:
            sock.send(b"Right")
        elif command == keyboard.Key.left:
            sock.send(b"Left")
    except Exception as e:
        print(f"Something went wrong: {e}")
        listener.stop()
        sock.close()
        return False
    
with keyboard.Listener(on_press=press) as listener:
    listener.join()

sock.close()