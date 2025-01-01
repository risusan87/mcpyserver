
import networking
from core.logger import logger
from core.console import start_command_listener

_version = '0.0.1'

def main():
    logger.info("MC Server Py is running version " + _version)

    # Start connection listener daemon
    networking.start_server(port=25565)

    # Start Command listener daemon
    start_command_listener()
            
from minecraft_py.level.region import Region
if __name__ == "__main__":
    r = Region(0, 0)
    r.load()
