

from logger import logger
import networking
from console import start_command_listener

version = '0.0.1'

def main():
    logger.info("MC Server Py is running version " + version)

    # Start connection listener daemon
    networking.start_server()

    # Start Command listener daemon
    start_command_listener()
            

if __name__ == "__main__":
    main()
