import os
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

LOG_DIR = "C:\\ProgramData\\FIM\\Events Logs"

# Ensure the log directory exists
os.makedirs(LOG_DIR, exist_ok=True)

def configure_logging(log_file):
    logger = logging.getLogger(log_file)
    handler = logging.FileHandler(log_file)
    formatter = logging.Formatter('[%(asctime)s] - %(user)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger

class DirectoryEventHandler(FileSystemEventHandler):
    def __init__(self, logger):
        super().__init__()
        self.logger = logger

    def log_event(self, event_type, src_path, dest_path=None):
        user = os.getlogin()
        if dest_path:
            message = f"{event_type} - {src_path} -> {dest_path}"
        else:
            message = f"{event_type} - {src_path}"
        self.logger.info(message, extra={'user': user})

    def on_created(self, event):
        if event.is_directory:
            self.log_event("Directory Created", event.src_path)
        else:
            self.log_event("File Created", event.src_path)

    def on_deleted(self, event):
        if event.is_directory:
            self.log_event("Directory Deleted", event.src_path)
        else:
            self.log_event("File Deleted", event.src_path)

    def on_modified(self, event):
        if event.is_directory:
            self.log_event("Directory Modified", event.src_path)
        else:
            self.log_event("File Modified", event.src_path)

    def on_moved(self, event):
        if event.is_directory:
            self.log_event("Directory Moved", event.src_path, event.dest_path)
        else:
            self.log_event("File Moved", event.src_path, event.dest_path)

class DirectoryMonitor:
    def __init__(self):
        self.observers = {}

    def start_monitoring(self, directory_path, log_file):
        if directory_path in self.observers:
            self.stop_monitoring(directory_path)

        logger = configure_logging(log_file)
        event_handler = DirectoryEventHandler(logger)
        observer = Observer()
        observer.schedule(event_handler, path=directory_path, recursive=True)
        observer.start()
        self.observers[directory_path] = observer

    def stop_monitoring(self, directory_path):
        if directory_path in self.observers:
            self.observers[directory_path].stop()
            self.observers[directory_path].join()
            del self.observers[directory_path]

    def stop_all(self):
        for observer in list(self.observers.values()):
            observer.stop()
            observer.join()
        self.observers.clear()
