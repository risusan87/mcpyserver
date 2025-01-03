import json
import networking
from core.logger import logger
from core.console import start_command_listener

import py_minecraft_server.nbt as nbt
from py_minecraft_server.level import Region, Chunk

_version = '0.0.1'

def main():
    logger.info("MC Server Py is running version " + _version)

    # Start connection listener daemon
    networking.start_server(port=25565)

    # Start Command listener daemon
    start_command_listener()
            
if __name__ == "__main__":
    r = Region.load(chunk_coord=(0, 0))
    print('region {r.x}, {r.z} is loaded')
    print('loading chunk 0, 0')
    c: Chunk = Region.get_chunk(x=0, z=0)
    c.load()
    print('chunk 0, 0 is loaded')
    s = c._chunk_data.__str__()
    with open('chunk.json', 'w') as f:
        f.write(json.dumps(json.loads(s), indent=4))
    
