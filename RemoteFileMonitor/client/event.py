import json
import os
from datetime import datetime
from config import CLIENT_NAME

class FileEvent:

    def __init__(self, event_type, path):

        self.client = CLIENT_NAME

        self.event = event_type

        self.path = path

        self.file = os.path.basename(path)

        self.time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def to_dict(self):

        return {

            "client": self.client,

            "event": self.event,

            "file": self.file,

            "path": self.path,

            "time": self.time

        }
    def to_json(self):
        return json.dumps({
            "type": "event",
            "data": self.to_dict()
        })
