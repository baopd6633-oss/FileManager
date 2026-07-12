import threading
import time

class Heartbeat(threading.Thread):

    def __init__(self, sender):
        super().__init__(daemon=True)
        self.sender = sender
        self.running = True

    def run(self):

        print("Heartbeat Started")

        while self.running:

            print("Heartbeat Send")

            self.sender.send_json({
                "type":"heartbeat",
                "data":{
                    "client":"CLIENT_01"
                }
            })

            time.sleep(5)

    def stop(self):
        self.running = False