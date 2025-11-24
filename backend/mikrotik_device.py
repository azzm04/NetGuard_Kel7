from netmiko import ConnectHandler
from .base_device import NetworkDevice
from datetime import datetime

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

    # --- FITUR 1: INTERFACE CONTROL ---
    def set_interface_state(self, interface_name, state):
        """State: 'yes' (disable/mati) atau 'no' (enable/hidup)"""
        if not self.connection: return "Not connected"
        
        # command: /interface set [find name=ether1] disabled=yes
        cmd = f"/interface set [find name={interface_name}] disabled={state}"
        try:
            self.connection.send_command(cmd)
            status = "DIMATIKAN" if state == 'yes' else "DIHIDUPKAN"
            return f"Sukses: Interface {interface_name} berhasil {status}."
        except Exception as e:
            return f"Gagal: {e}"

    # --- FITUR 2: BACKUP CONFIG ---
    def backup_configuration(self):
        if not self.connection: return "Not connected"
        
        try:
            # Ambil seluruh config
            config_text = self.connection.send_command("/export")
            
            # Buat nama file unik berdasarkan waktu
            filename = f"backup_router_{datetime.now().strftime('%Y%m%d_%H%M%S')}.rsc"
            
            # Simpan ke laptop (File I/O)
            with open(filename, "w") as f:
                f.write(config_text)
                
            return f"Sukses! Config disimpan di file: {filename}"
        except Exception as e:
            return f"Gagal Backup: {e}"

    # --- FITUR 3: IDENTITY ---
    def set_identity(self, new_name):
        if not self.connection: return "Not connected"
        try:
            self.connection.send_command(f"/system identity set name={new_name}")
            return f"Nama router berubah menjadi: {new_name}"
        except Exception as e:
            return f"Gagal ganti nama: {e}"

    def disconnect(self):
        if self.connection:
            self.connection.disconnect()