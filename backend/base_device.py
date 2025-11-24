from abc import ABC, abstractmethod

class NetworkDevice(ABC):
    def __init__(self, ip, username, password, port=22):
        self.ip = ip
        self.username = username
        self.password = password
        self.port = port
        self.connection = None

    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def execute_command(self, command):
        pass

    @abstractmethod
    def disconnect(self):
        pass