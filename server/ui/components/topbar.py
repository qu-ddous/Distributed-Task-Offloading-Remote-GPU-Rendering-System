import time
from typing import Callable
import customtkinter as ctk

from client.ui.theme import *

class ServerTopbar(ctk.CTkFrame):
    def __init__(self, master, on_toggle_server: Callable[[], None]):
        super().__init__(master, fg_color=BG_CARD, height=64, corner_radius=0)
        self.on_toggle_server = on_toggle_server
        self.start_time = time.time()
        self.is_running = True

        self._build_topbar()
        self._update_uptime()
        self._periodic_ip_refresh()

    def _build_topbar(self):
        # Left title info
        self.title_container = ctk.CTkFrame(self, fg_color="transparent")
        self.title_container.pack(side="left", padx=22, pady=12)

        self.lbl_title = ctk.CTkLabel(
            self.title_container,
            text="GPU Worker Server",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=TEXT_PRIMARY
        )
        self.lbl_title.pack(anchor="w")

        self.lbl_subtitle = ctk.CTkLabel(
            self.title_container,
            text="Dedicated NVIDIA GPU render node for remote video processing",
            font=ctk.CTkFont(size=11),
            text_color=TEXT_MUTED
        )
        self.lbl_subtitle.pack(anchor="w")

        # Right Action cluster
        self.right_container = ctk.CTkFrame(self, fg_color="transparent")
        self.right_container.pack(side="right", padx=22, pady=12)

        # Stop / Start Server Button
        self.btn_toggle_server = ctk.CTkButton(
            self.right_container,
            text="■ Stop Server",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=ACCENT_RED,
            hover_color=ACCENT_RED_HOVER,
            text_color="#FFFFFF",
            corner_radius=8,
            height=34,
            width=110,
            command=self.on_toggle_server
        )
        self.btn_toggle_server.pack(side="right", padx=(10, 0))

        # Uptime pill
        self.uptime_pill = ctk.CTkFrame(self.right_container, fg_color="#F1F5F9", corner_radius=8, border_width=1, border_color=BORDER_COLOR)
        self.uptime_pill.pack(side="right", padx=(10, 0))
        
        self.lbl_uptime_icon = ctk.CTkLabel(self.uptime_pill, text="🕒", font=ctk.CTkFont(size=12))
        self.lbl_uptime_icon.pack(side="left", padx=(10, 4), pady=6)

        self.uptime_text_box = ctk.CTkFrame(self.uptime_pill, fg_color="transparent")
        self.uptime_text_box.pack(side="left", padx=(0, 10), pady=4)

        ctk.CTkLabel(self.uptime_text_box, text="Uptime", font=ctk.CTkFont(size=9, weight="bold"), text_color=TEXT_MUTED).pack(anchor="w")
        self.lbl_uptime_val = ctk.CTkLabel(self.uptime_text_box, text="00m 00s", font=ctk.CTkFont(size=11, weight="bold"), text_color=TEXT_PRIMARY)
        self.lbl_uptime_val.pack(anchor="w")

        # Server status badge
        self.status_badge = ctk.CTkFrame(self.right_container, fg_color="#D1FAE5", corner_radius=8, border_width=1, border_color="#86EFAC")
        self.status_badge.pack(side="right")

        self.lbl_status_dot = ctk.CTkLabel(self.status_badge, text="●", font=ctk.CTkFont(size=14), text_color=ACCENT_GREEN)
        self.lbl_status_dot.pack(side="left", padx=(10, 4), pady=6)

        self.status_text_box = ctk.CTkFrame(self.status_badge, fg_color="transparent")
        self.status_text_box.pack(side="left", padx=(0, 10), pady=4)

        from shared.discovery import get_local_ip, get_ethernet_ip, get_active_adapters
        adapters = get_active_adapters()
        eth_ip = get_ethernet_ip()
        my_ip = eth_ip or get_local_ip()

        is_cable = any(ad.get("is_cable") for ad in adapters if ad.get("ip") == my_ip)
        is_eth = any(ad.get("is_ethernet") for ad in adapters if ad.get("ip") == my_ip)

        self.cached_current_ip = my_ip
        if is_cable:
            self.cached_ip_label = f"🔌 Cable IP: {my_ip}:8000"
        elif is_eth:
            self.cached_ip_label = f"⚡ LAN IP: {my_ip}:8000"
        else:
            self.cached_ip_label = f"⚡ Server IP: {my_ip}:8000"

        self.lbl_status_title = ctk.CTkLabel(self.status_text_box, text="Server Running • v1.0.0", font=ctk.CTkFont(size=11, weight="bold"), text_color=ACCENT_GREEN)
        self.lbl_status_title.pack(anchor="w")

        self.lbl_status_sub = ctk.CTkLabel(self.status_text_box, text=self.cached_ip_label, font=ctk.CTkFont(size=10, weight="bold"), text_color=ACCENT_BLUE)
        self.lbl_status_sub.pack(anchor="w")

        btn_copy = ctk.CTkButton(
            self.status_badge,
            text="📋 Copy IP",
            width=72,
            height=26,
            font=ctk.CTkFont(size=10, weight="bold"),
            fg_color="#FFFFFF",
            hover_color="#E2E8F0",
            text_color=TEXT_PRIMARY,
            corner_radius=6,
            command=lambda: self._copy_ip(f"{self.cached_current_ip}")
        )
        btn_copy.pack(side="left", padx=(0, 6), pady=4)

        btn_fw = ctk.CTkButton(
            self.status_badge,
            text="🛡️ Unblock Firewall",
            width=110,
            height=26,
            font=ctk.CTkFont(size=10, weight="bold"),
            fg_color="#EDE9FE",
            hover_color="#DDD6FE",
            text_color="#6D28D9",
            corner_radius=6,
            command=self._fix_firewall_clicked
        )
        btn_fw.pack(side="left", padx=(0, 8), pady=4)

    def _fix_firewall_clicked(self):
        import ctypes
        from tkinter import messagebox
        try:
            cmd = (
                '/c netsh advfirewall firewall delete rule name="gpuworkerserver.exe" & ' 
                'netsh advfirewall firewall delete rule name="GPUWorkerServer" & ' 
                'netsh advfirewall firewall delete rule name="GPUWorkerServer_TCP" & ' 
                'netsh advfirewall firewall delete rule name="GPUWorkerServer_UDP" & ' 
                'netsh advfirewall firewall add rule name="GPUWorkerServer_TCP" dir=in action=allow protocol=TCP localport=8000 profile=any & ' 
                'netsh advfirewall firewall add rule name="GPUWorkerServer_UDP" dir=in action=allow protocol=UDP localport=8002 profile=any & ' 
                'netsh advfirewall firewall add rule name="GPUWorkerServer_ICMP" dir=in action=allow protocol=icmpv4:8,any profile=any'
            )
            res = ctypes.windll.shell32.ShellExecuteW(None, "runas", "cmd.exe", cmd, None, 1)
            if res > 32:
                messagebox.showinfo(
                    "Firewall Unblocked",
                    "Windows Defender Firewall rules have been updated successfully!\n\n"
                    "● All conflicting Block rules deleted.\n"
                    "● Port 8000 (TCP) allowed on Public & Private networks.\n"
                    "● Port 8002 (UDP Discovery) allowed.\n"
                    "● Direct Ethernet Cable connection is now 100% reachable!"
                )
            else:
                messagebox.showwarning("Firewall Notice", "UAC prompt was cancelled or elevation failed.")
        except Exception as e:
            messagebox.showerror("Firewall Error", f"Could not update firewall rules:\n{e}")

    def _copy_ip(self, ip_text: str):
        self.clipboard_clear()
        self.clipboard_append(ip_text)
        from tkinter import messagebox
        messagebox.showinfo("IP Copied", f"Server IP address copied:\n\n{ip_text}\n\nClient PC mein ye IP enter karke 'Test & Connect' dabayein!")

    def set_header_text(self, title: str, subtitle: str):
        self.lbl_title.configure(text=title)
        self.lbl_subtitle.configure(text=subtitle)

    def set_server_running_state(self, running: bool):
        self.is_running = running
        if running:
            self.status_badge.configure(fg_color="#D1FAE5", border_color="#86EFAC")
            self.lbl_status_dot.configure(text="●", text_color=ACCENT_GREEN)
            self.lbl_status_title.configure(text="Server Running • v1.0.0", text_color=ACCENT_GREEN)
            from shared.discovery import get_local_ip, get_ethernet_ip
            eth_ip = get_ethernet_ip()
            cur_ip = eth_ip or get_local_ip()
            self.cached_current_ip = cur_ip
            lbl = f"🔌 Cable IP: {cur_ip}:8000" if (eth_ip and eth_ip.startswith(("169.254.", "192.168.99."))) else f"⚡ Server IP: {cur_ip}:8000"
            self.lbl_status_sub.configure(text=lbl)
            self.btn_toggle_server.configure(text="■ Stop Server", fg_color=ACCENT_RED, hover_color=ACCENT_RED_HOVER)
        else:
            self.status_badge.configure(fg_color="#FEE2E2", border_color="#FCA5A5")
            self.lbl_status_dot.configure(text="●", text_color=ACCENT_RED)
            self.lbl_status_title.configure(text="Server Stopped", text_color=ACCENT_RED)
            self.lbl_status_sub.configure(text="Offline (Daemon Paused)")
            self.btn_toggle_server.configure(text="▶ Start Server", fg_color=ACCENT_GREEN, hover_color=ACCENT_GREEN_HOVER)

    def _periodic_ip_refresh(self):
        try:
            if self.is_running:
                from shared.discovery import get_local_ip, get_ethernet_ip, get_active_adapters
                adapters = get_active_adapters()
                eth_ip = get_ethernet_ip()
                my_ip = eth_ip or get_local_ip()
                self.cached_current_ip = my_ip

                is_cable = any(ad.get("is_cable") for ad in adapters if ad.get("ip") == my_ip)
                is_eth = any(ad.get("is_ethernet") for ad in adapters if ad.get("ip") == my_ip)

                if is_cable:
                    lbl = f"🔌 Cable IP: {my_ip}:8000"
                elif is_eth:
                    lbl = f"⚡ LAN IP: {my_ip}:8000"
                else:
                    lbl = f"⚡ Server IP: {my_ip}:8000"

                if self.lbl_status_sub.cget("text") != lbl:
                    self.lbl_status_sub.configure(text=lbl)
        except Exception:
            pass
        self.after(2000, self._periodic_ip_refresh)

    def _update_uptime(self):
        if self.is_running:
            diff = int(time.time() - self.start_time)
            hours = diff // 3600
            minutes = (diff % 3600) // 60
            seconds = diff % 60
            if hours > 0:
                self.lbl_uptime_val.configure(text=f"{hours}h {minutes}m {seconds}s")
            else:
                self.lbl_uptime_val.configure(text=f"{minutes}m {seconds}s")
        self.after(1000, self._update_uptime)

