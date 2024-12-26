
from enum import Enum

class ConnectionState(Enum):
    HANDSHAKE = 0
    STATUS = 1
    LOGIN = 2
    CONFIGURATION = 3
    PLAY = 4
    CLOSE = 5

class ProtocolVersion(Enum):
    MC_1_21_4 = 769
    MC_1_21_3 = 768
    MC_1_21_2 = 768
    MC_1_21_1 = 767
    MC_1_21 = 767

    def to_mc_version(self) -> str:
        """
        Returns version in the format '1.X.X'
        Example: '1.21.4'
        """
        return self.name.replace('MC_', '').replace('_', '.')

    def from_protocol_version(protocol_version: int) -> 'ProtocolVersion':
        """
        Returns the ProtocolVersion enum for the given protocol version.
        """
        for version in ProtocolVersion:
            if protocol_version == version.value:
                return version
        raise ValueError(f'Protocol version {protocol_version} not supported')