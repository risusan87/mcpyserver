
class PlayerMP:
    def __init__(self, uuid: str, name: str):
        self._uuid = uuid
        self._name = name

    def get_uuid(self):
        return self._uuid
    
    def get_name(self):
        return self._name
