from collections import deque
import logging
import time

class ServerLogHandler(logging.Handler):
    """
    In-memory rotating log handler capturing all server and worker logs
    with timestamp, level, and message for the GUI Activity Logs & Console.
    """
    def __init__(self, max_records=2000):
        super().__init__()
        self.max_records = max_records
        self.logs = deque(maxlen=max_records)
        self.listeners = []

    def emit(self, record):
        try:
            msg = self.format(record)
            entry = {
                "time": time.strftime("%H:%M:%S", time.localtime(record.created)),
                "level": record.levelname,
                "name": record.name,
                "message": record.getMessage(),
                "raw": msg
            }
            self.logs.append(entry)
            for listener in list(self.listeners):
                try:
                    listener(entry)
                except Exception:
                    pass
        except Exception:
            self.handleError(record)

    def add_listener(self, callback):
        if callback not in self.listeners:
            self.listeners.append(callback)

    def remove_listener(self, callback):
        if callback in self.listeners:
            self.listeners.remove(callback)

    def get_recent_logs(self, limit=100):
        return list(self.logs)[-limit:]

    def clear(self):
        self.logs.clear()

server_log_bus = ServerLogHandler()
formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
server_log_bus.setFormatter(formatter)

