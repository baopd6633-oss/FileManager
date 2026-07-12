import json
import socket
import time
import threading
import os

from config import SERVER_IP
from config import SERVER_PORT


class TCPSender:

    def __init__(self):

        self.socket = None
        self.lock = threading.Lock()
        self.monitored_path = None

        self.connect()

    def connect(self):

        while True:

            try:
                with self.lock:
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

                # Khi vừa kết nối, tự động gửi danh sách file lên Server
                thread = threading.Thread(target=self.send_file_list, daemon=True)
                thread.start()

                return

            except Exception:

                print()

                print("Server Offline")

                print("Reconnect after 5 seconds...")

                time.sleep(5)

    def send(self, event):

        while True:

            try:
                with self.lock:
                    self.socket.sendall(
                        event.to_json().encode()
                    )

                    # Đợi ACK từ Server
                    try:
                        ack_bytes = self.socket.recv(4096)
                        self.handle_response(ack_bytes)
                    except socket.timeout:
                        raise Exception("Server Timeout")

                return

            except Exception:

                print()
                print("Connection Lost.")
                print("Reconnect after 5 seconds...")

                try:
                    with self.lock:
                        self.socket.close()
                except:
                    pass

                time.sleep(5)

                self.connect()

    def send_json(self, data):

        try:
            with self.lock:
                self.socket.sendall(
                    json.dumps(data).encode()
                )
                try:
                    ack_bytes = self.socket.recv(4096)
                    self.handle_response(ack_bytes)
                except socket.timeout:
                    pass

        except Exception:

            print("Heartbeat send failed.")

    def handle_response(self, ack_bytes):
        if not ack_bytes:
            return
        try:
            response = json.loads(ack_bytes.decode())
            if response.get("status") == "ACK":
                command = response.get("command")
                if command:
                    # Chạy xử lý lệnh trên luồng riêng để tránh deadlock và block luồng gửi nhận chính
                    thread = threading.Thread(
                        target=self.handle_server_command,
                        args=(command,),
                        daemon=True
                    )
                    thread.start()
        except Exception:
            # Tương thích ngược với phản hồi dạng text b"ACK" cũ
            pass

    def handle_server_command(self, command):
        action = command.get("action")
        rel_path = command.get("path")
        content = command.get("content", "")
        new_rel_path = command.get("new_path")
        
        if not self.monitored_path:
            print("Monitored path not set on sender, cannot execute command.")
            return

        try:
            # Sandbox bảo vệ: quy đổi ra đường dẫn tuyệt đối và đảm bảo nằm trong thư mục giám sát
            monitored_abs = os.path.abspath(self.monitored_path).replace("\\", "/")
            
            if rel_path:
                target_path = os.path.abspath(os.path.join(self.monitored_path, rel_path)).replace("\\", "/")
                if not target_path.startswith(monitored_abs):
                    print(f"Access Denied: path '{target_path}' is outside sandbox '{monitored_abs}'")
                    return
            else:
                target_path = None

            if new_rel_path:
                new_target_path = os.path.abspath(os.path.join(self.monitored_path, new_rel_path)).replace("\\", "/")
                if not new_target_path.startswith(monitored_abs):
                    print(f"Access Denied: path '{new_target_path}' is outside sandbox '{monitored_abs}'")
                    return
            else:
                new_target_path = None

            if action == "CREATE_FILE" or action == "WRITE_FILE":
                if target_path:
                    os.makedirs(os.path.dirname(target_path), exist_ok=True)
                    with open(target_path, "w", encoding="utf-8") as f:
                        f.write(content)
                    print(f"Executed remote command: {action} on {rel_path}")
                    # Tự động gửi lại danh sách file mới cập nhật lên Server
                    self.send_file_list()

            elif action == "DELETE_FILE":
                if target_path and os.path.exists(target_path):
                    if os.path.isdir(target_path):
                        import shutil
                        shutil.rmtree(target_path)
                    else:
                        os.remove(target_path)
                    print(f"Executed remote command: DELETE_FILE on {rel_path}")
                    # Tự động gửi lại danh sách file mới cập nhật lên Server
                    self.send_file_list()

            elif action == "RENAME_FILE":
                if target_path and new_target_path and os.path.exists(target_path):
                    os.makedirs(os.path.dirname(new_target_path), exist_ok=True)
                    os.rename(target_path, new_target_path)
                    print(f"Executed remote command: RENAME_FILE from {rel_path} to {new_rel_path}")
                    # Tự động gửi lại danh sách file mới cập nhật lên Server
                    self.send_file_list()

            elif action == "GET_FILE_LIST":
                self.send_file_list()

        except Exception as e:
            print(f"Error executing command {action}: {e}")

    def send_file_list(self):
        if not self.monitored_path or not os.path.exists(self.monitored_path):
            return
        
        files_list = []
        try:
            monitored_abs = os.path.abspath(self.monitored_path)
            for root, dirs, files in os.walk(monitored_abs):
                for file in files:
                    full_path = os.path.abspath(os.path.join(root, file))
                    rel_path = os.path.relpath(full_path, monitored_abs)
                    files_list.append({
                        "name": file,
                        "path": full_path.replace("\\", "/"),
                        "rel_path": rel_path.replace("\\", "/"),
                        "size": os.path.getsize(full_path)
                    })
            
            from config import CLIENT_NAME
            self.send_json({
                "type": "file_list",
                "data": {
                    "client": CLIENT_NAME,
                    "files": files_list
                }
            })
            print("Sent current file list to server.")
        except Exception as e:
            print(f"Error sending file list: {e}")