import json
from event_processor import EventProcessor
from logger import log


class ClientHandler:

    def __init__(self, socket, address, server, db_manager):

        self.socket = socket

        self.address = address

        self.server = server
        self.db_manager = db_manager
        self.processor = EventProcessor(db_manager)
        self.client_id = None

    def handle(self):

        log(f"Client Connected : {self.address}")

        try:
            while True:

                data = self.socket.recv(4096)

                if not data:
                    break
                message = json.loads(data.decode())

                # Lưu client_id và cập nhật trạng thái ONLINE ở gói tin đầu tiên
                if self.client_id is None:
                    try:
                        self.client_id = message.get("data", {}).get("client")
                        if self.client_id:
                            self.db_manager.update_client_status(
                                self.client_id,
                                "ONLINE",
                                ip_address=self.address[0],
                                port=self.address[1]
                            )
                    except Exception as e:
                        log(f"Lỗi khi lưu thông tin client kết nối: {e}")

                self.processor.process(message)

                self.socket.send(b"ACK")

        except Exception as e:

            log(str(e))

        finally:
            try:
                self.socket.close()
            except:
                pass

            self.server.remove_client(self.socket)

            # Cập nhật trạng thái OFFLINE khi ngắt kết nối
            if self.client_id:
                try:
                    self.db_manager.update_client_status(self.client_id, "OFFLINE")
                except Exception as e:
                    log(f"Lỗi khi cập nhật trạng thái OFFLINE cho {self.client_id}: {e}")

            log(f"Client Disconnected : {self.address}")
        