
import os
import threading

from logger import logger
from networking import stop_server

def _command_listener():
    while True:
        command = input()
        _handle(command)

def _handle(command):
    if command == 'stop':
        stop_server()
        os._exit(0)
    else:
        logger.info(f'Unknown command: {command}', log_thread=False)    

def start_command_listener():
    command_listener_thread = threading.Thread(target=_command_listener)
    command_listener_thread.start()
