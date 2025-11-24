import customtkinter as ctk
import threading
from backend.mikrotik_device import MikrotikDevice
from datetime import datetime

# --- KONFIGURASI TEMA ---
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class NetGuardUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("NetGuard")
        self.geometry("900x800")
        self.resizable(False, False)

        # Layout Utama
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # --- HEADER MODERN ---
        self.create_header()

        # --- INFO SIDEBAR ---
        self.create_info_panel()

        # --- MAIN CONTENT AREA ---
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        self.main_container.grid_columnconfigure(1, weight=1)
        self.main_container.grid_rowconfigure(0, weight=1)

        # Info Panel (Left)
        self.left_panel = ctk.CTkFrame(self.main_container, width=200, corner_radius=10)
        self.left_panel.grid(row=0, column=0, sticky="ns", padx=(0, 10))
        self.left_panel.grid_propagate(False)
        self.create_left_info_panel()

        # --- TABVIEW (MENU UTAMA) ---
        self.tabview = ctk.CTkTabview(self.main_container, width=650)
        self.tabview.grid(row=0, column=1, sticky="nsew")
        
        self.tab_connect = self.tabview.add("🔌 Connection")
        self.tab_control = self.tabview.add("⚙️ Control")
        self.tab_tools = self.tabview.add("🛠️ Tools")
        self.tab_about = self.tabview.add("ℹ️ About")
        self.tab_team = self.tabview.add("👥 Team")

        # ================= TABS =================
        self.create_connection_tab()
        self.create_control_tab()
        self.create_tools_tab()
        self.create_about_tab()
        self.create_team_tab()

        # --- LOG AREA (BAWAH) ---
        self.create_log_section()

        # --- FOOTER ---
        self.create_footer()

        self.device = None
        self.connection_time = None

    def create_header(self):
        """Header dengan gradient effect"""
        self.header_frame = ctk.CTkFrame(self, corner_radius=0, height=80, fg_color="#1a237e")
        self.header_frame.grid(row=0, column=0, sticky="ew")
        
        header_container = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        header_container.pack(expand=True, fill="both", padx=20)
        
        # Title
        title_label = ctk.CTkLabel(
            header_container, 
            text="🛡️ NetGuard Admin Dashboard", 
            font=("Roboto", 28, "bold"),
            text_color="#ffffff"
        )
        title_label.pack(side="left", pady=15)
        
        # Subtitle
        subtitle = ctk.CTkLabel(
            header_container, 
            text="MikroTik Router Management System",
            font=("Roboto", 11),
            text_color="#90caf9"
        )
        subtitle.pack(side="left", padx=15, pady=15)

    def create_info_panel(self):
        """Panel info di atas tabview"""
        pass  # Simplified, moved to left panel

    def create_left_info_panel(self):
        """Panel info kiri dengan statistik"""
        # Header
        header = ctk.CTkLabel(
            self.left_panel, 
            text="📊 System Info", 
            font=("Roboto", 16, "bold")
        )
        header.pack(pady=(15, 10), padx=10)
        
        # Separator
        separator = ctk.CTkFrame(self.left_panel, height=2, fg_color="#3f51b5")
        separator.pack(fill="x", padx=15, pady=5)
        
        # Status Card
        self.status_frame = ctk.CTkFrame(self.left_panel, corner_radius=8, fg_color="#263238")
        self.status_frame.pack(pady=10, padx=10, fill="x")
        
        self.lbl_connection_status = ctk.CTkLabel(
            self.status_frame, 
            text="⚫ Disconnected",
            font=("Roboto", 12, "bold"),
            text_color="#ef5350"
        )
        self.lbl_connection_status.pack(pady=8)
        
        # Stats
        stats_frame = ctk.CTkFrame(self.left_panel, fg_color="transparent")
        stats_frame.pack(pady=10, padx=10, fill="x")
        
        self.lbl_uptime = ctk.CTkLabel(stats_frame, text="Uptime: --", font=("Roboto", 10))
        self.lbl_uptime.pack(anchor="w", pady=2)
        
        self.lbl_router_model = ctk.CTkLabel(stats_frame, text="Model: --", font=("Roboto", 10))
        self.lbl_router_model.pack(anchor="w", pady=2)
        
        self.lbl_version = ctk.CTkLabel(stats_frame, text="RouterOS: --", font=("Roboto", 10))
        self.lbl_version.pack(anchor="w", pady=2)
        
        # Quick Actions
        separator2 = ctk.CTkFrame(self.left_panel, height=2, fg_color="#3f51b5")
        separator2.pack(fill="x", padx=15, pady=15)
        
        quick_label = ctk.CTkLabel(self.left_panel, text="⚡ Quick Actions", font=("Roboto", 12, "bold"))
        quick_label.pack(pady=(5, 10))
        
        self.btn_quick_info = ctk.CTkButton(
            self.left_panel, 
            text="📈 System Resource",
            width=160,
            height=32,
            command=self.show_system_resource,
            state="disabled"
        )
        self.btn_quick_info.pack(pady=5)
        
        self.btn_quick_backup = ctk.CTkButton(
            self.left_panel,
            text="💾 Quick Backup",
            width=160,
            height=32,
            fg_color="#00695c",
            hover_color="#004d40",
            command=self.do_backup,
            state="disabled"
        )
        self.btn_quick_backup.pack(pady=5)

    def create_connection_tab(self):
        # Scrollable frame untuk menghindari terpotong
        container = ctk.CTkScrollableFrame(self.tab_connect, fg_color="transparent")
        container.pack(expand=True, fill="both", padx=20, pady=15)
        
        # Connection Card
        conn_card = ctk.CTkFrame(container, corner_radius=15, fg_color="#1e1e1e", border_width=2, border_color="#3f51b5")
        conn_card.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(
            conn_card, 
            text="🔐 Router Connection", 
            font=("Roboto", 16, "bold")
        ).pack(pady=(15, 10))

        # Form Frame
        form_frame = ctk.CTkFrame(conn_card, fg_color="transparent")
        form_frame.pack(pady=10, padx=20)

        # Input fields dengan icons
        input_container = ctk.CTkFrame(form_frame, fg_color="transparent")
        input_container.pack()
        
        self.ip_entry = ctk.CTkEntry(
            input_container, 
            width=300, 
            height=40,
            placeholder_text="🌐 IP Address (e.g., 192.168.1.1)",
            font=("Roboto", 12)
        )
        self.ip_entry.pack(pady=6)
        self.ip_entry.insert(0, "192.168.56.10")

        self.user_entry = ctk.CTkEntry(
            input_container, 
            width=300, 
            height=40,
            placeholder_text="👤 Username",
            font=("Roboto", 12)
        )
        self.user_entry.pack(pady=6)
        self.user_entry.insert(0, "admin")

        self.pass_entry = ctk.CTkEntry(
            input_container, 
            width=300, 
            height=40,
            placeholder_text="🔑 Password",
            show="●",
            font=("Roboto", 12)
        )
        self.pass_entry.pack(pady=6)
        self.pass_entry.insert(0, "admin")

        # Connect Button
        self.btn_connect = ctk.CTkButton(
            conn_card, 
            text="🚀 CONNECT TO ROUTER",
            command=self.start_connection,
            width=300,
            height=45,
            font=("Roboto", 14, "bold"),
            fg_color="#3f51b5",
            hover_color="#303f9f"
        )
        self.btn_connect.pack(pady=15)

        # Network Monitor Section
        monitor_card = ctk.CTkFrame(container, corner_radius=15, fg_color="#1e1e1e", border_width=2, border_color="#00695c")
        monitor_card.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(
            monitor_card,
            text="📡 Network Monitoring",
            font=("Roboto", 16, "bold")
        ).pack(pady=(15, 5))
        
        ctk.CTkLabel(
            monitor_card,
            text="Scan and monitor all connected devices on your network",
            font=("Roboto", 10),
            text_color="#9e9e9e"
        ).pack(pady=(0, 10))

        self.btn_scan = ctk.CTkButton(
            monitor_card,
            text="🔍 SCAN CONNECTED DEVICES",
            command=self.scan_devices,
            width=300,
            height=40,
            font=("Roboto", 13, "bold"),
            fg_color="#00695c",
            hover_color="#004d40",
            state="disabled"
        )
        self.btn_scan.pack(pady=(5, 15))

    def create_control_tab(self):
        container = ctk.CTkFrame(self.tab_control, fg_color="transparent")
        container.pack(expand=True, fill="both", padx=20, pady=20)
        
        ctk.CTkLabel(
            container,
            text="⚙️ Interface Management",
            font=("Roboto", 18, "bold")
        ).pack(pady=(0, 5))
        
        ctk.CTkLabel(
            container,
            text="Control router network interfaces (ports)",
            font=("Roboto", 11),
            text_color="#9e9e9e"
        ).pack(pady=(0, 20))

        # Interface Card
        iface_card = ctk.CTkFrame(container, corner_radius=15, fg_color="#1e1e1e")
        iface_card.pack(fill="x", pady=10)
        
        ctk.CTkLabel(
            iface_card,
            text="🔌 Port: ether1 (WAN/Internet)",
            font=("Roboto", 14, "bold")
        ).pack(pady=(20, 15))

        btn_frame = ctk.CTkFrame(iface_card, fg_color="transparent")
        btn_frame.pack(pady=(0, 20))

        self.btn_disable_eth1 = ctk.CTkButton(
            btn_frame,
            text="🔴 DISABLE PORT",
            fg_color="#d32f2f",
            hover_color="#b71c1c",
            width=180,
            height=40,
            font=("Roboto", 12, "bold"),
            command=lambda: self.toggle_interface("ether1", "yes")
        )
        self.btn_disable_eth1.pack(side="left", padx=10)

        self.btn_enable_eth1 = ctk.CTkButton(
            btn_frame,
            text="🟢 ENABLE PORT",
            fg_color="#388e3c",
            hover_color="#2e7d32",
            width=180,
            height=40,
            font=("Roboto", 12, "bold"),
            command=lambda: self.toggle_interface("ether1", "no")
        )
        self.btn_enable_eth1.pack(side="left", padx=10)

    def create_tools_tab(self):
        container = ctk.CTkFrame(self.tab_tools, fg_color="transparent")
        container.pack(expand=True, fill="both", padx=20, pady=20)

        # Identity Section
        id_card = ctk.CTkFrame(container, corner_radius=15, fg_color="#1e1e1e")
        id_card.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(id_card, text="🏷️ Router Identity", font=("Roboto", 14, "bold")).pack(pady=(15, 10))
        
        self.id_entry = ctk.CTkEntry(
            id_card,
            placeholder_text="Enter new router name",
            width=350,
            height=40,
            font=("Roboto", 12)
        )
        self.id_entry.pack(pady=8)
        
        ctk.CTkButton(
            id_card,
            text="✏️ Change Router Name",
            command=self.change_identity,
            width=250,
            height=38,
            fg_color="#3f51b5",
            hover_color="#303f9f"
        ).pack(pady=(5, 15))

        # Backup Section
        backup_card = ctk.CTkFrame(container, corner_radius=15, fg_color="#1e1e1e")
        backup_card.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(backup_card, text="💾 System Backup", font=("Roboto", 14, "bold")).pack(pady=(15, 5))
        ctk.CTkLabel(
            backup_card,
            text="Download complete router configuration",
            font=("Roboto", 10),
            text_color="#9e9e9e"
        ).pack()
        
        ctk.CTkButton(
            backup_card,
            text="📥 DOWNLOAD BACKUP (.RSC)",
            command=self.do_backup,
            width=300,
            height=40,
            font=("Roboto", 12, "bold"),
            fg_color="#f57f17",
            hover_color="#c46210"
        ).pack(pady=15)

        # Reboot Section
        reboot_card = ctk.CTkFrame(container, corner_radius=15, fg_color="#1e1e1e", border_width=2, border_color="#d32f2f")
        reboot_card.pack(fill="x")
        
        ctk.CTkLabel(reboot_card, text="⚠️ Danger Zone", font=("Roboto", 14, "bold"), text_color="#ef5350").pack(pady=(15, 5))
        ctk.CTkLabel(
            reboot_card,
            text="This will restart the router and disconnect all users",
            font=("Roboto", 10),
            text_color="#9e9e9e"
        ).pack()
        
        ctk.CTkButton(
            reboot_card,
            text="🔄 REBOOT ROUTER",
            command=self.do_reboot,
            width=250,
            height=40,
            font=("Roboto", 12, "bold"),
            fg_color="#d32f2f",
            hover_color="#b71c1c"
        ).pack(pady=15)

    def create_log_section(self):
        """Enhanced log section"""
        log_frame = ctk.CTkFrame(self, fg_color="transparent")
        log_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=(5, 0))
        
        log_header = ctk.CTkFrame(log_frame, fg_color="#1e1e1e", corner_radius=8)
        log_header.pack(fill="x", pady=(0, 5))
        
        ctk.CTkLabel(
            log_header,
            text="📋 System Logs",
            font=("Roboto", 12, "bold")
        ).pack(side="left", padx=15, pady=8)
        
        self.btn_clear_log = ctk.CTkButton(
            log_header,
            text="🗑️ Clear",
            width=80,
            height=28,
            command=self.clear_logs,
            fg_color="#424242",
            hover_color="#616161"
        )
        self.btn_clear_log.pack(side="right", padx=15, pady=8)
        
        self.log_box = ctk.CTkTextbox(
            log_frame,
            width=870,
            height=110,
            font=("Consolas", 11),
            text_color="#00ff00",
            fg_color="#0d0d0d",
            border_width=2,
            border_color="#3f51b5"
        )
        self.log_box.pack()
        self.log(f"[{self.get_timestamp()}] NetGuard v2.5 initialized. Ready to connect.")

    def create_footer(self):
        """Footer dengan informasi"""
        footer = ctk.CTkFrame(self, corner_radius=0, height=35, fg_color="#1a1a1a")
        footer.grid(row=3, column=0, sticky="ew")
        
        footer_text = ctk.CTkLabel(
            footer,
            text="NetGuard v2.5 © 2025 | MikroTik Router Management | Made with ❤️",
            font=("Roboto", 10),
            text_color="#757575"
        )
        footer_text.pack(pady=8)

    # --- LOGIC METHODS ---
    def get_timestamp(self):
        return datetime.now().strftime("%H:%M:%S")

    def log(self, msg):
        timestamp = self.get_timestamp()
        self.log_box.insert("end", f"[{timestamp}] {msg}\n")
        self.log_box.see("end")

    def clear_logs(self):
        self.log_box.delete("0.0", "end")
        self.log(f"Logs cleared.")

    def start_connection(self):
        self.btn_connect.configure(state="disabled", text="⏳ Connecting...")
        threading.Thread(target=self._process_connect).start()

    def _process_connect(self):
        ip = self.ip_entry.get()
        user = self.user_entry.get()
        pwd = self.pass_entry.get()
        
        self.log(f"Connecting to {ip}...")
        self.device = MikrotikDevice(ip, user, pwd)
        success, msg = self.device.connect()

        if success:
            self.connection_time = datetime.now()
            self.log("✅ SUCCESS: Connected to RouterOS")
            self.lbl_connection_status.configure(text="🟢 Connected", text_color="#66bb6a")
            self.btn_connect.configure(text="✅ CONNECTED", fg_color="#388e3c", state="disabled")
            
            # Enable buttons
            self.btn_scan.configure(state="normal")
            self.btn_quick_info.configure(state="normal")
            self.btn_quick_backup.configure(state="normal")

            # Fetch router info
            self.update_router_info()
        else:
            self.log(f"❌ FAILED: {msg}")
            self.lbl_connection_status.configure(text="🔴 Connection Failed", text_color="#ef5350")
            self.btn_connect.configure(state="normal", text="🚀 CONNECT TO ROUTER")

    def update_router_info(self):
        """Update router information in left panel"""
        if not self.device: return
        
        def fetch_info():
            try:
                resource = self.device.execute_command("/system resource print")
                identity = self.device.execute_command("/system identity print")
                
                # Parse and update (simplified)
                self.lbl_router_model.configure(text="Model: MikroTik Router")
                self.lbl_version.configure(text="RouterOS: 7.x")
                
                # Log full info
                self.log("📊 Router information retrieved")
            except Exception as e:
                self.log(f"⚠️ Error fetching info: {e}")
        
        threading.Thread(target=fetch_info).start()

    def show_system_resource(self):
        """Show system resource info"""
        if not self.device: return
        
        def fetch():
            self.log("📊 Fetching system resources...")
            info = self.device.execute_command("/system resource print")
            self.log(info)
        
        threading.Thread(target=fetch).start()

    def scan_devices(self):
        if not self.device: return
        
        def run_scan():
            self.log("🔍 Scanning network (Reading ARP Table)...")
            result = self.device.get_arp_table()
            self.log("\n" + "="*50)
            self.log("📡 CONNECTED DEVICES:")
            self.log(result)
            self.log("="*50 + "\n")
        
        threading.Thread(target=run_scan).start()

    def toggle_interface(self, iface, state):
        if not self.device: return
        action = "Disabling" if state == "yes" else "Enabling"
        self.log(f"{action} interface {iface}...")
        threading.Thread(target=lambda: self.log(self.device.set_interface_state(iface, state))).start()

    def change_identity(self):
        name = self.id_entry.get()
        if not name or not self.device: return
        self.log(f"Changing router identity to: {name}")
        threading.Thread(target=lambda: self.log(self.device.set_identity(name))).start()

    def do_backup(self):
        if not self.device: return
        self.log("💾 Creating backup configuration...")
        threading.Thread(target=lambda: self.log(self.device.backup_configuration())).start()

    def do_reboot(self):
        if not self.device: return
        
        def run():
            self.log("⚠️ REBOOTING ROUTER...")
            self.device.execute_command("/system reboot\ny")
            self.log("🔌 Connection closed. Router is rebooting...")
            self.device.disconnect()
            
            # Reset UI
            self.btn_scan.configure(state="disabled")
            self.btn_quick_info.configure(state="disabled")
            self.btn_quick_backup.configure(state="disabled")
            self.btn_connect.configure(state="normal", text="🚀 CONNECT TO ROUTER", fg_color="#3f51b5")
            self.lbl_connection_status.configure(text="⚫ Disconnected", text_color="#ef5350")
        
        threading.Thread(target=run).start()

    def create_about_tab(self):
        """About App - Informasi Aplikasi"""
        container = ctk.CTkScrollableFrame(self.tab_about, fg_color="transparent")
        container.pack(expand=True, fill="both", padx=20, pady=15)
        
        # Header
        header_frame = ctk.CTkFrame(container, fg_color="#1a237e", corner_radius=15)
        header_frame.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(
            header_frame,
            text="🛡️ NetGuard",
            font=("Roboto", 32, "bold"),
            text_color="#ffffff"
        ).pack(pady=(20, 5))
        
        ctk.CTkLabel(
            header_frame,
            text="Router Admin",
            font=("Roboto", 16),
            text_color="#90caf9"
        ).pack(pady=(0, 20))
        
        # Description Card
        desc_card = ctk.CTkFrame(container, corner_radius=15, fg_color="#1e1e1e")
        desc_card.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(
            desc_card,
            text="📖 Tentang Aplikasi",
            font=("Roboto", 16, "bold")
        ).pack(pady=(20, 10), padx=20, anchor="w")
        
        description_text = """NetGuard adalah aplikasi manajemen router MikroTik yang 
dirancang untuk mempermudah administrator jaringan dalam mengelola 
dan memonitor perangkat RouterOS.

Aplikasi ini menyediakan antarmuka grafis yang intuitif untuk 
melakukan berbagai tugas administratif seperti monitoring jaringan, 
kontrol interface, backup konfigurasi, dan banyak lagi."""
        
        ctk.CTkLabel(
            desc_card,
            text=description_text,
            font=("Roboto", 12),
            text_color="#b0b0b0",
            justify="left",
            wraplength=550
        ).pack(pady=(0, 20), padx=30, anchor="w")
        
        # Features Card
        features_card = ctk.CTkFrame(container, corner_radius=15, fg_color="#1e1e1e")
        features_card.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(
            features_card,
            text="✨ Fitur Utama",
            font=("Roboto", 16, "bold")
        ).pack(pady=(20, 15), padx=20, anchor="w")
        
        features = [
            ("🔐", "Koneksi Aman", "Koneksi SSH yang aman ke RouterOS"),
            ("📡", "Network Monitoring", "Scan dan monitor perangkat yang terhubung"),
            ("⚙️", "Interface Control", "Kontrol port/interface router secara real-time"),
            ("💾", "Backup & Restore", "Backup konfigurasi router dengan mudah"),
            ("📊", "System Resource", "Monitor resource dan performa router"),
            ("🔄", "Remote Reboot", "Reboot router dari jarak jauh")
        ]
        
        for icon, title, desc in features:
            feature_frame = ctk.CTkFrame(features_card, fg_color="#263238", corner_radius=10)
            feature_frame.pack(fill="x", padx=20, pady=5)
            
            ctk.CTkLabel(
                feature_frame,
                text=f"{icon} {title}",
                font=("Roboto", 13, "bold"),
                text_color="#ffffff"
            ).pack(anchor="w", padx=15, pady=(10, 2))
            
            ctk.CTkLabel(
                feature_frame,
                text=desc,
                font=("Roboto", 10),
                text_color="#9e9e9e"
            ).pack(anchor="w", padx=15, pady=(0, 10))
        
        ctk.CTkLabel(features_card, text="").pack(pady=5)
        
        # Tech Stack Card
        tech_card = ctk.CTkFrame(container, corner_radius=15, fg_color="#1e1e1e")
        tech_card.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(
            tech_card,
            text="🔧 Teknologi yang Digunakan",
            font=("Roboto", 16, "bold")
        ).pack(pady=(20, 10), padx=20, anchor="w")
        
        tech_text = """• Python - Bahasa pemrograman utama
• CustomTkinter - Modern GUI framework
• RouterOS API/SSH - Komunikasi dengan MikroTik
• Threading - Multi-tasking untuk operasi jaringan"""
        
        ctk.CTkLabel(
            tech_card,
            text=tech_text,
            font=("Roboto", 12),
            text_color="#b0b0b0",
            justify="left"
        ).pack(pady=(0, 20), padx=30, anchor="w")
        
        # Info Card
        info_card = ctk.CTkFrame(container, corner_radius=15, fg_color="#0d47a1")
        info_card.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(
            info_card,
            text="💡 Project Information",
            font=("Roboto", 14, "bold")
        ).pack(pady=(15, 5))
        
        ctk.CTkLabel(
            info_card,
            text="Dibuat untuk memenuhi tugas mata kuliah Pemrograman Berorientasi Objek \nTeknik Komputer",
            font=("Roboto", 11),
            text_color="#bbdefb"
        ).pack(pady=(0, 15))

    def create_team_tab(self):
        """Team Profile - 4 Anggota Kelompok"""
        container = ctk.CTkScrollableFrame(self.tab_team, fg_color="transparent")
        container.pack(expand=True, fill="both", padx=20, pady=15)
        
        # Header
        ctk.CTkLabel(
            container,
            text="👥 Meet Our Team",
            font=("Roboto", 24, "bold")
        ).pack(pady=(10, 5))
        
        ctk.CTkLabel(
            container,
            text="Tim Pengembang NetGuard Project",
            font=("Roboto", 12),
            text_color="#9e9e9e"
        ).pack(pady=(0, 20))
        
        # Team Members Data (Ganti dengan data asli)
        team_members = [
            {
                "name": "Azzam Syaiful Islam",
                "nim": "21120123120023120035",
                "role": "Backend Developer",
                "color": "#1976d2"
            },
            {
                "name": "Nandito Adi Syahputra",
                "nim": "21120123120023",
                "role": "Frontend Developer",
                "color": "#388e3c"
            },
            {
                "name": "Muhmammad Danial Irfani",
                "nim": "21120123130061",
                "role": "Project Manager",
                "color": "#f57c00"
            },
            {
                "name": "Mustofa Ahmad Rusli",
                "nim": "21120123120034",
                "role": "System Analyst",
                "color": "#7b1fa2"
            }
        ]
        
        # Create member cards in 2x2 grid
        for i in range(0, 4, 2):
            row_frame = ctk.CTkFrame(container, fg_color="transparent")
            row_frame.pack(fill="x", pady=10)
            
            for j in range(2):
                if i + j < len(team_members):
                    member = team_members[i + j]
                    self.create_member_card(row_frame, member, side="left" if j == 0 else "right")
        
        # Contact Info
        contact_card = ctk.CTkFrame(container, corner_radius=15, fg_color="#1e1e1e")
        contact_card.pack(fill="x", pady=(20, 10))
        
        ctk.CTkLabel(
            contact_card,
            text="📧 Contact Information",
            font=("Roboto", 14, "bold")
        ).pack(pady=(15, 10))
        
        ctk.CTkLabel(
            contact_card,
            text="Universitas Diponegoro\nProgram Studi Teknik Komputer\nEmail: netguard.team@undip.ac.id",
            font=("Roboto", 10),
            text_color="#b0b0b0",
            justify="center"
        ).pack(pady=(0, 15))

    def create_member_card(self, parent, member, side):
        """Helper untuk membuat card member tim"""
        card = ctk.CTkFrame(parent, corner_radius=15, fg_color="#1e1e1e", width=280, height=200)
        card.pack(side=side, padx=10, expand=True, fill="both")
        card.pack_propagate(False)
        
        # Header dengan warna unik
        header = ctk.CTkFrame(card, corner_radius=12, fg_color=member["color"], height=60)
        header.pack(fill="x", padx=10, pady=10)
        header.pack_propagate(False)
        
        ctk.CTkLabel(
            header,
            text="👤",
            font=("Roboto", 32)
        ).pack(pady=10)
        
        # Content
        content_frame = ctk.CTkFrame(card, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=15, pady=(0, 10))
        
        ctk.CTkLabel(
            content_frame,
            text=member["name"],
            font=("Roboto", 14, "bold"),
            text_color="#ffffff"
        ).pack(anchor="w", pady=(5, 2))
        
        ctk.CTkLabel(
            content_frame,
            text=member["nim"],
            font=("Roboto", 10),
            text_color="#90caf9"
        ).pack(anchor="w", pady=(0, 8))
        
        ctk.CTkLabel(
            content_frame,
            text=member["role"],
            font=("Roboto", 11, "bold"),
            text_color=member["color"]
        ).pack(anchor="w", pady=(0, 5))
        
        ctk.CTkLabel(
    content_frame,
    text="",
    font=("Roboto", 9),
    text_color="#9e9e9e",
    wraplength=240,
    justify="left"
).pack(anchor="w")

if __name__ == "__main__":
    app = NetGuardUI()
    app.mainloop()