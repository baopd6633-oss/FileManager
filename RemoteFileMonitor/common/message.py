import json


class Message:

    def __init__(self, message_type, data):

        self.type = message_type

        self.data = data

    def to_dict(self):

        return {

            "type": self.type,

            "data": self.data

        }

    def to_json(self):

        return json.dumps(

            self.to_dict()

        )

    @staticmethod
    def from_json(text):

        obj = json.loads(text)

        return Message(

            obj["type"],

            obj["data"]

        )