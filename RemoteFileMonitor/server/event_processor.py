from logger import log


class EventProcessor:

    def __init__(self, db_manager):
        self.db_manager = db_manager

    def process(self, message):

        message_type = message.get("type")

        if message_type == "heartbeat":
            self.process_heartbeat(message)

        elif message_type == "event":
            self.process_event(message)

        else:
            log(f"Unknown message: {message_type}")

    def process_event(self, message):

        data = message["data"]

        log("--------------------------------")
        log(f"CLIENT : {data['client']}")
        log(f"EVENT  : {data['event']}")
        log(f"FILE   : {data['file']}")
        log(f"PATH   : {data['path']}")
        log(f"TIME   : {data['time']}")
        log("--------------------------------")

        try:
            self.db_manager.save_event(
                client_id=data['client'],
                event_type=data['event'],
                file_name=data['file'],
                file_path=data['path'],
                timestamp=data['time']
            )
        except Exception as e:
            log(f"Lỗi khi lưu event vào CSDL: {e}")

    def process_heartbeat(self, message):

        data = message["data"]

        log(f"[Heartbeat] {data['client']} Online")

        try:
            self.db_manager.update_client_heartbeat(data['client'])
        except Exception as e:
            log(f"Lỗi khi cập nhật Heartbeat vào CSDL: {e}")