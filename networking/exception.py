
class ProtocolError(Exception):
    '''
    Exception raised when unexpected bytes, values, or structures are encountered in the incoming packet buffer.
    '''
    pass

class DataCorruptedError(Exception):
    '''
    Exception raised when the incoming packet buffer is likely corrupted which fails to digest into certain data types.
    '''
    pass