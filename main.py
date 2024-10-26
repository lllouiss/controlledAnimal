import pygame as py
import win32api
import win32con
import win32gui
import random
import time
import pygetwindow as gw
import threading
import socket
import webbrowser


class Death:
    def __init__(self):
        py.init()

        # windows = gw.getAllTitles()
        # print(windows)

        screen_info = py.display.Info()
        self.screen_width = screen_info.current_w
        self.screen_height = screen_info.current_h

        self.window_screen = py.display.set_mode((self.screen_width, self.screen_height), py.NOFRAME)

        self.hwnd = py.display.get_wm_info()["window"]

        win32gui.SetWindowLong(self.hwnd, win32con.GWL_EXSTYLE, win32gui.GetWindowLong(
            self.hwnd, win32con.GWL_EXSTYLE) | win32con.WS_EX_LAYERED)
        win32gui.SetLayeredWindowAttributes(self.hwnd, win32api.RGB(255, 0, 128), 0, win32con.LWA_COLORKEY)

        self.spielerfigur_left = py.image.load("dead_scaled_left.png")
        self.spielerfigur_right = py.image.load("dead_scaled_right.png")
        self.spielerfigur = self.spielerfigur_left  # Standardfigur nach links

        # Initial position of the player figure
        self.posX, self.posY = self.screen_width // 2, self.screen_height // 2
        # Target position
        self.targetX, self.targetY = self.posX, self.posY
        # Movement speed
        self.speed = 5

        self.last_move_time = time.time()
        self.move_interval = 4

        self.activeAction = "move"

        self.running = True

    def randomPosition(self):
        newX = random.randrange(self.spielerfigur.get_width(), self.screen_width - self.spielerfigur.get_width())
        newY = random.randrange(self.spielerfigur.get_height(), self.screen_height - self.spielerfigur.get_height())
        return newX, newY

    def moveTowards(self, pos, target, speed):
        if pos < target:
            return min(pos + speed, target)
        elif pos > target:
            return max(pos - speed, target)
        return pos

    def moveRandom(self):
        self.targetX, self.targetY = self.randomPosition()  # Neue Zielposition

    def actionController(self):
        if time.time() - self.last_move_time > self.move_interval:
            self.move_interval = 4
            if self.activeAction == "move":
                self.moveRandom()
            if self.activeAction == "stop":
                self.running = False
            if self.activeAction == "hello":
                webbrowser.open("https://www.google.com/search?q=hallo")
                self.activeAction = "move"
            self.last_move_time = time.time()  # Timer zurücksetzen

            if self.targetX < self.posX:
                self.spielerfigur = self.spielerfigur_left
            else:
                self.spielerfigur = self.spielerfigur_right

    def ask(self):
        while self.running:
            try:
                client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client_socket.connect(('localhost', 2451))  # Verbindung zum Server herstellen 192.168.1.100

                # Nachricht vom Server empfangen
                while self.running:
                    data = client_socket.recv(1024)  # Empfangene Daten vom Server (maximal 1024 Bytes)
                    print(data.decode())
                    self.activeAction = data.decode()
                    self.move_interval = 0
                client_socket.close()

            except Exception as e:
                pass

    def update(self):
        while self.running:
            for event in py.event.get():
                if event.type == py.QUIT:
                    self.running = False
                elif event.type == py.MOUSEBUTTONDOWN:
                    print("Klick erkannt")

            win32gui.SetWindowPos(
                self.hwnd,
                win32con.HWND_TOPMOST,
                0, 0, 0, 0,
                win32con.SWP_NOMOVE | win32con.SWP_NOSIZE
            )
            self.actionController()
            # Move towards the target position smoothly
            self.posX = self.moveTowards(self.posX, self.targetX, self.speed)
            self.posY = self.moveTowards(self.posY, self.targetY, self.speed)

            self.window_screen.fill((255, 0, 128))  # Hintergrundfarbe
            self.window_screen.blit(self.spielerfigur, (self.posX, self.posY))  # Figur zeichnen

            py.display.update()
            py.time.delay(20)

    def start(self):
        ask = threading.Thread(target=self.ask)
        ask.start()
        self.update()
        ask.join()


if __name__ == "__main__":
    app = Death()
    app.start()
