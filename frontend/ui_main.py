import customtkinter as ctk
import threading
import time
from backend.mikrotik_device import MikrotikDevice

# --- KONFIGURASI TEMA ---
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class NetGuardUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- SETUP WINDOW UTAMA ---
        self.title("NetGuard - Network Management System")
        self.geometry("700x600") # Saya tambah sedikit tingginya agar muat tombol baru
        self.resizable(False, False)

        # Grid Layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0) # Header
        self.grid_rowconfigure(1, weight=0) # Form
        self.grid_rowconfigure(2, weight=1) # Log

        # --- 1. HEADER ---
        self.header_frame = ctk.CTkFrame(self, corner_radius=0)
        self.header_frame.grid(row=0, column=0, sticky="ew")
        
        self.header_label = ctk.CTkLabel(
            self.header_frame, 
            text="NetGuard Dashboard", 
            font=("Roboto Medium", 24)
        )
        self.header_label.pack(pady=15)

        # --- 2. FORM KONEKSI ---
        self.form_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.form_frame.grid(row=1, column=0, pady=20)

        # Input IP
        self.ip_entry = ctk.CTkEntry(self.form_frame, width=300, placeholder_text="IP Address")
        self.ip_entry.pack(pady=5)
        self.ip_entry.insert(0, "192.168.56.10") # Autofill IP

        # Input User
        self.user_entry = ctk.CTkEntry(self.form_frame, width=300, placeholder_text="Username")
        self.user_entry.pack(pady=5)
        self.user_entry.insert(0, "admin")       # Autofill User

        # Input Password
        self.pass_entry = ctk.CTkEntry(self.form_frame, width=300, placeholder_text="Password", show="*")
        self.pass_entry.pack(pady=5)
        self.pass_entry.insert(0, "admin")       # Autofill Pass (sesuai request Anda)

        # TOMBOL CONNECT (Biru)
        self.btn_connect = ctk.CTkButton(
            self.form_frame, 
            text="CONNECT TO ROUTER", 
            command=self.start_connection_thread,
            font=("Roboto Medium", 14),
            height=40,
            fg_color="#1f538d", 
            hover_color="#14375e"
        )
        self.btn_connect.pack(pady=15)

        # TOMBOL REBOOT (Merah - Fitur Baru)
        # Awalnya disabled (abu-abu) agar tidak terpencet sembarangan
        self.btn_reboot = ctk.CTkButton(
            self.form_frame,
            text="REBOOT SYSTEM ⚠️",
            command=self.start_reboot_thread,
            font=("Roboto Medium", 14),
            height=40,
            fg_color="#d32f2f",      # Merah bahaya
            hover_color="#b71c1c",
            state="disabled"         # Mati default-nya
        )
        self.btn_reboot.pack(pady=5)

        # --- 3. LOG AREA ---
        self.log_label = ctk.CTkLabel(self, text="System Logs / Output:", anchor="w")
        self.log_label.grid(row=2, column=0, sticky="w", padx=20)

        self.log_box = ctk.CTkTextbox(
            self, 
            width=660, 
            height=200, 
            font=("Consolas", 12), 
            text_color="#00ff00", 
            fg_color="black"
        )
        self.log_box.grid(row=3, column=0, padx=20, pady=(0, 20))
        
        self.device = None

    # --- FUNGSI LOGGING ---
    def log(self, message):
        self.log_box.insert("end", f"> {message}\n")
        self.log_box.see("end")

    # --- LOGIKA KONEKSI ---
    def start_connection_thread(self):
        self.btn_connect.configure(state="disabled", text="Connecting...")
        threading.Thread(target=self.process_connection).start()

    def process_connection(self):
        ip = self.ip_entry.get()
        user = self.user_entry.get()
        pwd = self.pass_entry.get()

        self.log(f"Menghubungkan ke {ip}...")
        
        self.device = MikrotikDevice(ip, user, pwd)
        success, msg = self.device.connect()

        if success:
            self.log("-------------------------------")
            self.log("STATUS: LOGIN BERHASIL!")
            self.log("-------------------------------")
            
            # Ambil info awal
            info = self.device.execute_command("/system resource print")
            self.log(info)

            # NYALAKAN TOMBOL REBOOT KARENA SUDAH KONEK
            self.btn_reboot.configure(state="normal")
            self.btn_connect.configure(text="CONNECTED", fg_color="green")
            
        else:
            self.log(f"GAGAL: {msg}")
            self.btn_connect.configure(state="normal", text="CONNECT TO ROUTER")

    # --- LOGIKA REBOOT (FITUR BARU) ---
    def start_reboot_thread(self):
        # Matikan tombol biar gak dipencet 2x
        self.btn_reboot.configure(state="disabled") 
        threading.Thread(target=self.process_reboot).start()

    def process_reboot(self):
        self.log("-------------------------------")
        self.log("PERINGATAN: Mengirim perintah reboot...")
        self.log("-------------------------------")
        
        # Command reboot mikrotik butuh konfirmasi "y" (yes)
        # "\ny" artinya tekan Enter lalu tekan y
        output = self.device.execute_command("/system reboot\ny")
        
        self.log("Output Router:")
        self.log(output)
        self.log("Router sedang restart... Koneksi diputus.")

        # Kembalikan UI ke state awal (karena koneksi putus)
        self.device.disconnect()
        self.btn_connect.configure(state="normal", text="CONNECT TO ROUTER", fg_color="#1f538d")
        self.btn_reboot.configure(state="disabled") # Matikan lagi tombol reboot

if __name__ == "__main__":
    app = NetGuardUI()
    app.mainloop()