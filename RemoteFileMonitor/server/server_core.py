import socket
import threading

from client_handler import ClientHandler
from logger import log
from database import DatabaseManager
from config import DB_PATH


class ServerCore:

    def __init__(self, host, port):

        self.host = host
        self.port = port
        self.db_manager = DatabaseManager(DB_PATH)

        self.server = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM
        )

        self.server.setsockopt(
            socket.SOL_SOCKET,
            socket.SO_REUSEADDR,
            1
        )

        self.server.bind((host, port))

        self.server.listen()

        self.server.settimeout(1)

        self.running = True

        self.clients = []

        self.threads = []

    def start(self):

        log(f"Server started at {self.host}:{self.port}")

        while self.running:

            try:

                client_socket, address = self.server.accept()

            except socket.timeout:

                continue

            except OSError:

                break

            log(f"Client Connected : {address}")

            self.clients.append(client_socket)

            handler = ClientHandler(

                client_socket,

                address,

                self,

                self.db_manager

            )

            thread = threading.Thread(

                target=handler.handle

            )

            thread.start()

            self.threads.append(thread)

    def remove_client(self, client_socket):

        if client_socket in self.clients:

            self.clients.remove(client_socket)

        # Dọn dẹp danh sách thread đã hoàn thành để tránh rò rỉ bộ nhớ
        self.threads = [t for t in self.threads if t.is_alive()]

    def shutdown(self):

        log("Stopping Server...")

        self.running = False

        for client in self.clients:

            try:

                client.shutdown(socket.SHUT_RDWR)

            except:

                pass

            try:

                client.close()

            except:

                pass

        self.clients.clear()

        self.server.close()

        for thread in self.threads:

            thread.join(timeout=2)

        log("Server Stopped")