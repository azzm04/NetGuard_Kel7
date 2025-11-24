from netmiko import ConnectHandler
from .base_device import NetworkDevice # Import dari parent

class MikrotikDevice(NetworkDevice):
    def connect(self):
        device_params = {
            'device_type': 'mikrotik_routeros',
            'host': self.ip,
            'username': self.username,
            'password': self.password,
            'port': self.port,
        }
        try:
            # Melakukan koneksi SSH asli
            self.connection = ConnectHandler(**device_params)
            return True, f"Terhubung ke {self.ip}"
        except Exception as e:
            return False, str(e)

    def execute_command(self, command):
        if not self.connection:
            return "Error: Device not connected"
        try:
            output = self.connection.send_command(command)
            return output
        except Exception as e:
            return f"Command Failed: {e}"

    def disconnect(self):
        if self.connection:
            self.connection.disconnect()