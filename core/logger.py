import logging
import threading
import os

class Logger(logging.Logger):

    def __init__(self):

        os.makedirs('resources/logs', exist_ok=True)

        self.logger = logging.getLogger('file_and_console')
        self.logger.setLevel(logging.DEBUG)

        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)

        # Create file handler
        file_handler = logging.FileHandler('resources/logs/app.log')
        file_handler.setLevel(logging.DEBUG)

        # Create formatter
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)

        # Add handlers to the logger
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)

    def info(self, msg, log_thread=True):
        self.logger.info(f'{"[" + threading.current_thread().name + "] " if log_thread else ""}{msg}')

    def debug(self, msg):
        self.logger.debug(f'[{threading.current_thread().name}] {msg}')

    def error(self, msg):
        self.logger.error(f'[{threading.current_thread().name}] {msg}')

    def warning(self, msg):
        self.logger.warning(f'[{threading.current_thread().name}] {msg}')

    def critical(self, msg):
        self.logger.critical(f'[{threading.current_thread().name}] {msg}')

    def exception(self, msg):
        self.logger.exception(f'[{threading.current_thread().name}] {msg}')

logger = Logger()