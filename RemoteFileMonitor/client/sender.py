import json
import socket
import time

from config import SERVER_IP
from config import SERVER_PORT


class TCPSender:

    def __init__(self):

        self.socket = None

        self.connect()

    def connect(self):

        while True:

            try:

                self.socket = socket.socket(
                    socket.AF_INET,
                    socket.SOCK_STREAM
                )

                self.socket.connect(
                    (SERVER_IP, SERVER_PORT)
                )
                
                self.socket.settimeout(3)

                print()

                print("=" * 60)

                print("CONNECTED TO SERVER")

                print("=" * 60)

                return

            except Exception:

                print()

                print("Server Offline")

                print("Reconnect after 5 seconds...")

                time.sleep(5)

    def send(self, event):

        while True:

            try:

                self.socket.sendall(
                    event.to_json().encode()
                )

                # Đợi ACK từ Server
                try:
                    ack = self.socket.recv(1024)

                    if ack != b"ACK":
                        raise Exception("ACK Error")

                except socket.timeout:
                    raise Exception("Server Timeout")

                if ack == b"ACK":
                    return

                raise Exception("Invalid ACK")

            except Exception:

                print()
                print("Connection Lost.")
                print("Reconnect after 5 seconds...")

                try:
                    self.socket.close()
                except:
                    pass

                time.sleep(5)

                self.connect()

    def send_json(self, data):

            try:
                self.socket.sendall(
                    json.dumps(data).encode()
                )

            except Exception:

                print("Heartbeat send failed.")