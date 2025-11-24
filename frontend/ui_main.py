import customtkinter as ctk
import threading
from backend.mikrotik_device import MikrotikDevice

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class NetGuardUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("NetGuard - Router Admin Pro")
        self.geometry("800x600")
        self.resizable(False, False)

        # Layout Utama
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1) # Tab area expand

        # --- HEADER ---
        self.header_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="#1a1a1a")
        self.header_frame.grid(row=0, column=0, sticky="ew")
        ctk.CTkLabel(self.header_frame, text="NetGuard Admin Dashboard", font=("Roboto", 20, "bold")).pack(pady=15)

        # --- TABVIEW (MENU UTAMA) ---
        self.tabview = ctk.CTkTabview(self, width=750)
        self.tabview.grid(row=1, column=0, pady=10)
        
        self.tab_connect = self.tabview.add("Connection")
        self.tab_control = self.tabview.add("Interface Control")
        self.tab_tools = self.tabview.add("Tools & Backup")

        # ================= TAB 1: CONNECTION =================
        self.create_connection_tab()

        # ================= TAB 2: INTERFACE CONTROL =================
        self.create_control_tab()

        # ================= TAB 3: TOOLS =================
        self.create_tools_tab()

        # --- LOG AREA (BAWAH) ---
        ctk.CTkLabel(self, text="System Logs:", anchor="w").grid(row=2, column=0, sticky="w", padx=25)
        self.log_box = ctk.CTkTextbox(self, width=750, height=120, font=("Consolas", 12), text_color="#00ff00", fg_color="black")
        self.log_box.grid(row=3, column=0, pady=(0, 20))

        self.device = None

    # --- UI BUILDER METHODS ---
    def create_connection_tab(self):
        frame = ctk.CTkFrame(self.tab_connect, fg_color="transparent")
        frame.pack(pady=20)

        self.ip_entry = ctk.CTkEntry(frame, width=250, placeholder_text="IP Address")
        self.ip_entry.pack(pady=5)
        self.ip_entry.insert(0, "192.168.56.10")

        self.user_entry = ctk.CTkEntry(frame, width=250, placeholder_text="Username")
        self.user_entry.pack(pady=5)
        self.user_entry.insert(0, "admin")

        self.pass_entry = ctk.CTkEntry(frame, width=250, placeholder_text="Password", show="*")
        self.pass_entry.pack(pady=5)
        self.pass_entry.insert(0, "admin") # Sesuaikan pass router kamu (kosongkan stringnya jika tanpa pass)

        self.btn_connect = ctk.CTkButton(frame, text="CONNECT TO ROUTER", command=self.start_connection, width=250)
        self.btn_connect.pack(pady=15)

        self.lbl_status = ctk.CTkLabel(frame, text="Status: Disconnected", text_color="red")
        self.lbl_status.pack()

    def create_control_tab(self):
        # Penjelasan: Matikan Ether1 (Biasanya internet)
        ctk.CTkLabel(self.tab_control, text="Interface Management (Port Control)", font=("Roboto", 16)).pack(pady=10)
        
        btn_frame = ctk.CTkFrame(self.tab_control)
        btn_frame.pack(pady=10, padx=20, fill="x")

        # Tombol Interface Ether1
        ctk.CTkLabel(btn_frame, text="Port ether1 (Internet/NAT):").pack(pady=5)
        self.btn_disable_eth1 = ctk.CTkButton(btn_frame, text="MATIKAN PORT (Disable)", fg_color="#d32f2f", command=lambda: self.toggle_interface("ether1", "yes"))
        self.btn_disable_eth1.pack(pady=5)
        
        self.btn_enable_eth1 = ctk.CTkButton(btn_frame, text="HIDUPKAN PORT (Enable)", fg_color="#388e3c", command=lambda: self.toggle_interface("ether1", "no"))
        self.btn_enable_eth1.pack(pady=5)

    def create_tools_tab(self):
        # Identity
        ctk.CTkLabel(self.tab_tools, text="Router Identity", font=("Roboto", 14)).pack(pady=5)
        self.id_entry = ctk.CTkEntry(self.tab_tools, placeholder_text="Nama Baru Router")
        self.id_entry.pack(pady=5)
        ctk.CTkButton(self.tab_tools, text="Ganti Nama Router", command=self.change_identity).pack(pady=5)

        ctk.CTkLabel(self.tab_tools, text="-------------------------").pack(pady=10)

        # Backup
        ctk.CTkLabel(self.tab_tools, text="System Backup", font=("Roboto", 14)).pack(pady=5)
        ctk.CTkButton(self.tab_tools, text="DOWNLOAD FULL BACKUP (.RSC)", command=self.do_backup, fg_color="#f57f17", hover_color="#c46210").pack(pady=5)
        
        # Reboot
        ctk.CTkButton(self.tab_tools, text="REBOOT ROUTER", command=self.do_reboot, fg_color="#d32f2f", hover_color="#b71c1c").pack(pady=20)


    # --- LOGIC METHODS ---
    def log(self, msg):
        self.log_box.insert("end", f"> {msg}\n")
        self.log_box.see("end")

    def start_connection(self):
        self.btn_connect.configure(state="disabled", text="Connecting...")
        threading.Thread(target=self._process_connect).start()

    def _process_connect(self):
        ip = self.ip_entry.get()
        user = self.user_entry.get()
        pwd = self.pass_entry.get()
        
        self.log(f"Menghubungkan ke {ip}...")
        self.device = MikrotikDevice(ip, user, pwd)
        success, msg = self.device.connect()

        if success:
            self.log("BERHASIL: Terhubung ke RouterOS")
            self.lbl_status.configure(text="Status: CONNECTED", text_color="#00ff00")
            self.btn_connect.configure(text="CONNECTED", fg_color="green")
            
            # Auto fetch info
            info = self.device.execute_command("/system resource print")
            self.log(info)
        else:
            self.log(f"GAGAL: {msg}")
            self.lbl_status.configure(text="Status: Error Connection", text_color="red")
            self.btn_connect.configure(state="normal", text="CONNECT TO ROUTER")

    def toggle_interface(self, iface, state):
        if not self.device: return
        threading.Thread(target=lambda: self.log(self.device.set_interface_state(iface, state))).start()

    def change_identity(self):
        name = self.id_entry.get()
        if not name or not self.device: return
        threading.Thread(target=lambda: self.log(self.device.set_identity(name))).start()

    def do_backup(self):
        if not self.device: return
        self.log("Sedang memproses backup file...")
        threading.Thread(target=lambda: self.log(self.device.backup_configuration())).start()

    def do_reboot(self):
        if not self.device: return
        def run():
            self.log("Rebooting router...")
            self.device.execute_command("/system reboot\ny")
            self.log("Koneksi putus. Silakan restart aplikasi jika router sudah nyala.")
            self.device.disconnect()
        threading.Thread(target=run).start()

if __name__ == "__main__":
    app = NetGuardUI()
    app.mainloop()