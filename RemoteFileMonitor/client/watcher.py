from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
from heartbeat import Heartbeat

from sender import TCPSender
from event import FileEvent

class FileWatcher(FileSystemEventHandler):

    def handle_event(self, event_type, path):

        event = FileEvent(event_type, path)

        self.sender.send(event)

        print(event.to_dict())

    def __init__(self):

        self.sender = TCPSender()

        self.heartbeat = Heartbeat(self.sender)

        self.heartbeat.start()

    def on_created(self, event):

        if event.is_directory:
            return

        self.handle_event("CREATE", event.src_path)

    def on_deleted(self, event):

        if event.is_directory:
            return

        self.handle_event("DELETE", event.src_path)

    def on_modified(self, event):

        if event.is_directory:
            return

        self.handle_event("MODIFY", event.src_path)

    def on_moved(self, event):

        if event.is_directory:
            return

        self.handle_event("RENAME", event.dest_path)


def start_monitor(path):

    observer = Observer()

    watcher = FileWatcher()

    observer.schedule(

        watcher,

        path,

        recursive=True

    )

    observer.start()

    print("=" * 60)

    print("WATCHDOG IS RUNNING")

    print(path)

    print("=" * 60)

    try:

        while True:

            time.sleep(1)

    except KeyboardInterrupt:

        watcher.heartbeat.stop()

        observer.stop()

    observer.join()
