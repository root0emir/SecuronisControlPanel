import tkinter as tk
from tkinter import font
import psutil
import platform
import datetime
import socket
import subprocess
import re
import time
import os
import json
import requests
import threading
from concurrent.futures import ThreadPoolExecutor

class LinuxSystemPanel:
    def __init__(self, root):
        self.root = root
        self.root.title("Linux System Control Panel")
        self.root.geometry("1200x750")
        self.root.configure(bg="#000000")
            
        self.executor = ThreadPoolExecutor(max_workers=4)
              
        self.title_font = font.Font(family="Ubuntu", size=12, weight="bold")
        self.bold_font = font.Font(family="Ubuntu", size=10, weight="bold")
        self.normal_font = font.Font(family="Ubuntu", size=9)
        
        self.root.grid_columnconfigure(0, weight=0, minsize=220)
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
             
        self.sidebar = tk.Frame(root, bg="#121212", padx=15, pady=15)
        self.sidebar.grid(row=0, column=0, sticky="nswe")
        
        tk.Label(self.sidebar, 
                text="Securonis System Panel", 
                bg="#121212", 
                fg="#00ff00",
                font=self.title_font).pack(pady=(0, 30), anchor="w")
        
        # Menü butonları
        menu_items = [
            ("System Info", 0),
            ("Hardware Info", 1),
            ("Privacy Status", 2),
            ("Network Info", 3),
            ("Disk Info", 4),
            ("Processes", 5),
            ("Services", 6),
            ("About", 7)
        ]
        
        for text, index in menu_items:
            self.create_menu_button(text, index)
        
        self.main_area = tk.Frame(root, bg="#000000")
        self.main_area.grid(row=0, column=1, sticky="nswe")
        
        self.show_system_info()

    def get_system_info(self):
        mem = psutil.virtual_memory()
        swap = psutil.swap_memory()
        return { 
            "Hostname": socket.gethostname(),
            "OS": self.get_os_info(),
            "Kernel": platform.version(),
            "Uptime": str(datetime.timedelta(seconds=int(time.time() - psutil.boot_time())))[:-7],
            "CPU": f"{psutil.cpu_percent()}% ({psutil.cpu_count()} cores @ {psutil.cpu_freq().current:.0f}MHz)",
            "RAM": f"{mem.used/1024/1024:.1f}MB / {mem.total/1024/1024:.1f}MB ({mem.percent}%)",
            "Swap": f"{swap.used/1024/1024:.1f}MB / {swap.total/1024/1024:.1f}MB",
            "Temperature": self.get_cpu_temp(),
            "Load Avg": self.get_load_avg(),
            "Battery": self.get_battery_info(),
            "Last Boot": datetime.datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S"),
            "System Time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Timezone": self.get_timezone(),
            "Desktop Environment": self.get_desktop_environment(),
            "Display Manager": self.get_display_manager(),
            "Shell": os.environ.get('SHELL', 'N/A'),
            "Python Version": platform.python_version(),
            "System Language": self.get_system_language()
        }

    def get_os_info(self):
        try:
            with open('/etc/os-release', 'r') as f:
                lines = f.readlines()
                os_info = {}
                for line in lines:
                    if '=' in line:
                        key, value = line.strip().split('=', 1)
                        os_info[key] = value.strip('"')
                return f"{os_info.get('NAME', 'Unknown')} {os_info.get('VERSION', '')}"
        except:
            return f"{platform.system()} {platform.release()}"

    def get_timezone(self):
        try:
            return subprocess.check_output(['timedatectl', 'show', '--property=Timezone']).decode().strip().split('=')[1]
        except:
            return "N/A"

    def get_desktop_environment(self):
        try:
            return os.environ.get('XDG_CURRENT_DESKTOP', 'N/A')
        except:
            return "N/A"

    def get_display_manager(self):
        try:
            return subprocess.check_output(['systemctl', 'list-units', '--type=service', '--state=running', 'display-manager.service']).decode()
        except:
            return "N/A"

    def get_system_language(self):
        try:
            return os.environ.get('LANG', 'N/A')
        except:
            return "N/A"

    def get_cpu_temp(self):
        try:
            temps = psutil.sensors_temperatures()
            if 'coretemp' in temps:
                return f"{temps['coretemp'][0].current}°C"
            elif 'k10temp' in temps:
                return f"{temps['k10temp'][0].current}°C"
            elif 'acpitz' in temps:
                return f"{temps['acpitz'][0].current}°C"
            with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
                return f"{int(f.read()) / 1000}°C"
        except:
            return "N/A"

    def get_load_avg(self):
        try:
            with open("/proc/loadavg", "r") as f:
                load = f.read().split()[:3]
            return ", ".join(load)
        except:
            return "N/A"

    def get_battery_info(self):
        try:
            bat = psutil.sensors_battery()
            if bat:
                return f"{bat.percent}% ({'Charging' if bat.power_plugged else 'Discharging'})"
            return "No Battery"
        except:
            return "N/A"

    def show_hardware_info(self):
        content = tk.Frame(self.main_area, bg="#000000")
        content.pack(fill="both", expand=True, padx=25, pady=25)
        
        tk.Label(content, 
                text="HARDWARE INFORMATION", 
                font=self.title_font,
                bg="#000000",
                fg="#00ff00").pack(anchor="w", pady=(0, 20))
        
        # CPU Details
        cpu_frame = tk.Frame(content, bg="#000000")
        cpu_frame.pack(fill="x", pady=10)
        
        tk.Label(cpu_frame,
                text="CPU Details:",
                bg="#000000",
                fg="#00ff00",
                font=self.bold_font).pack(anchor="w")
        
        cpu_info = self.get_cpu_details()
        for key, value in cpu_info.items():
            frame = tk.Frame(cpu_frame, bg="#000000")
            frame.pack(fill="x", pady=2)
            tk.Label(frame,
                    text=f"{key}:",
                    bg="#000000",
                    fg="#00ff00",
                    width=20,
                    anchor="w").pack(side="left")
            tk.Label(frame,
                    text=value,
                    bg="#000000",
                    fg="#00ff00").pack(side="left", padx=10)
        
        # GPU Details
        gpu_frame = tk.Frame(content, bg="#000000")
        gpu_frame.pack(fill="x", pady=10)
        
        tk.Label(gpu_frame,
                text="GPU Details:",
                bg="#000000",
                fg="#00ff00",
                font=self.bold_font).pack(anchor="w")
        
        gpu_info = self.get_gpu_details()
        for key, value in gpu_info.items():
            frame = tk.Frame(gpu_frame, bg="#000000")
            frame.pack(fill="x", pady=2)
            tk.Label(frame,
                    text=f"{key}:",
                    bg="#000000",
                    fg="#00ff00",
                    width=20,
                    anchor="w").pack(side="left")
            tk.Label(frame,
                    text=value,
                    bg="#000000",
                    fg="#00ff00").pack(side="left", padx=10)

    def get_cpu_details(self):
        try:
            with open('/proc/cpuinfo', 'r') as f:
                cpu_info = {}
                for line in f:
                    if ':' in line:
                        key, value = line.split(':', 1)
                        cpu_info[key.strip()] = value.strip()
                
                return {
                    "Model": cpu_info.get('model name', 'N/A'),
                    "Vendor": cpu_info.get('vendor_id', 'N/A'),
                    "Cores": f"{psutil.cpu_count()} ({psutil.cpu_count(logical=False)} physical)",
                    "Thread Count": str(psutil.cpu_count(logical=True)),
                    "Cache Sizes": self.get_cpu_cache_sizes(),
                    "Max Speed": f"{psutil.cpu_freq().max:.0f}MHz",
                    "Current Speed": f"{psutil.cpu_freq().current:.0f}MHz",
                    "Min Speed": f"{psutil.cpu_freq().min:.0f}MHz"
                }
        except:
            return {"Error": "Could not fetch CPU details"}

    def get_cpu_cache_sizes(self):
        try:
            with open('/sys/devices/system/cpu/cpu0/cache/index0/size', 'r') as f:
                l1 = f.read().strip()
            with open('/sys/devices/system/cpu/cpu0/cache/index1/size', 'r') as f:
                l2 = f.read().strip()
            with open('/sys/devices/system/cpu/cpu0/cache/index2/size', 'r') as f:
                l3 = f.read().strip()
            return f"L1: {l1}, L2: {l2}, L3: {l3}"
        except:
            return "N/A"

    def get_gpu_details(self):
        try:
            # NVIDIA GPU
            nvidia = subprocess.check_output(['nvidia-smi', '--query-gpu=gpu_name,memory.total,memory.used,memory.free', '--format=csv,noheader']).decode()
            if nvidia:
                name, total, used, free = nvidia.strip().split(',')
                return {
                    "GPU": name,
                    "Total Memory": f"{total.strip()}",
                    "Used Memory": f"{used.strip()}",
                    "Free Memory": f"{free.strip()}"
                }
            
            # Intel/AMD GPU
            with open('/sys/kernel/debug/dri/0/i915_frequency_info', 'r') as f:
                gpu_info = f.read()
                return {
                    "GPU": "Intel/AMD Integrated Graphics",
                    "Frequency Info": gpu_info
                }
        except:
            return {"GPU": "N/A"}

    def show_services(self):
        content = tk.Frame(self.main_area, bg="#000000")
        content.pack(fill="both", expand=True, padx=25, pady=25)
        
        tk.Label(content, 
                text="SYSTEM SERVICES", 
                font=self.title_font,
                bg="#000000",
                fg="#00ff00").pack(anchor="w", pady=(0, 20))
        
        # Servis listesi
        services = self.get_system_services()
        
        for service in services:
            frame = tk.Frame(content, bg="#000000")
            frame.pack(fill="x", pady=2)
            
            tk.Label(frame,
                    text=f"{service['name']}:",
                    bg="#000000",
                    fg="#00ff00",
                    width=40,
                    anchor="w").pack(side="left")
            
            color = "#00ff00" if service['status'] == "active" else "#ff0000"
            tk.Label(frame,
                    text=service['status'],
                    bg="#000000",
                    fg=color).pack(side="left", padx=10)

    def get_system_services(self):
        try:
            output = subprocess.check_output(['systemctl', 'list-units', '--type=service', '--state=running']).decode()
            services = []
            for line in output.split('\n'):
                if 'running' in line:
                    name = line.split()[0]
                    status = 'active'
                    services.append({'name': name, 'status': status})
            return services
        except:
            return []

    def switch_tab(self, index):
        for widget in self.main_area.winfo_children():
            widget.destroy()
        
        tabs = [
            self.show_system_info,
            self.show_hardware_info,
            self.show_privacy_status,
            self.show_network_info,
            self.show_disk_info,
            self.show_processes,
            self.show_services,
            self.show_about
        ]
        if index < len(tabs):
            tabs[index]()

    def show_privacy_status(self):
        content = tk.Frame(self.main_area, bg="#000000")
        content.pack(fill="both", expand=True, padx=25, pady=25)
        
        tk.Label(content, 
                text="PRIVACY & SECURITY STATUS", 
                font=self.title_font,
                bg="#000000",
                fg="#00ff00").pack(anchor="w", pady=(0, 20))
        
        # loading mesage
        loading_label = tk.Label(content, 
                               text="Loading security information...", 
                               bg="#000000",
                               fg="#00ff00")
        loading_label.pack(pady=20)
        
        # security infos asenkron
        def update_security_info():
            security_info = {
                "Firewall Status": self.check_firewall(),
                "VPN Status": self.check_vpn(),
                "Tor Status": self.check_tor(),
                "DNS Status": self.check_dns(),
                "Public IP": self.get_public_ip(),
                "System Updates": self.check_updates(),
                "Antivirus": self.check_antivirus(),
                "SELinux": self.check_selinux(),
                "AppArmor": self.check_apparmor(),
                "System Encryption": self.check_encryption(),
                "Secure Boot": self.check_secure_boot()
            }
            
            # loading 
            loading_label.destroy()
            
            # security info
            for i, (key, value) in enumerate(security_info.items()):
                frame = tk.Frame(content, bg="#000000")
                frame.pack(fill="x", pady=5)
                
                tk.Label(frame, 
                        text=f"{key}:", 
                        bg="#000000", 
                        fg="#00ff00",
                        font=self.bold_font, 
                        width=20, 
                        anchor="w").pack(side="left")
                
                color = "#00ff00" if value in ["Active", "Enabled", "Up to Date", "Protected"] else "#ff0000" if value in ["Inactive", "Disabled", "Not Found", "Unprotected"] else "#ffff00"
                tk.Label(frame, 
                        text=value, 
                        bg="#000000",
                        fg=color).pack(side="left", padx=10)
        
        # Asenkron 
        threading.Thread(target=update_security_info, daemon=True).start()

    def check_firewall(self):
        try:
            # UFW 
            ufw_status = subprocess.check_output(['ufw', 'status'], stderr=subprocess.PIPE, timeout=1).decode()
            if "Status: active" in ufw_status:
                return "Active"
            
            # iptables 
            iptables_status = subprocess.check_output(['iptables', '-L'], stderr=subprocess.PIPE, timeout=1).decode()
            if "Chain INPUT" in iptables_status:
                return "Active (iptables)"
            
            return "Inactive"
        except:
            return "Not Found"

    def check_vpn(self):
        try:
            # VPN arayüzlerini kontrol et
            interfaces = psutil.net_if_stats()
            vpn_interfaces = ['tun0', 'tun1', 'wg0', 'ppp0']
            
            for interface in vpn_interfaces:
                if interface in interfaces and interfaces[interface].isup:
                    return "Active"
            
            # OpenVPN servisini kontrol et
            openvpn_status = subprocess.check_output(['systemctl', 'is-active', 'openvpn'], stderr=subprocess.PIPE, timeout=1).decode()
            if "active" in openvpn_status:
                return "Active (OpenVPN)"
            
            return "Inactive"
        except:
            return "Not Found"

    def check_tor(self):
        try:
            # Tor servisini kontrol et
            tor_status = subprocess.check_output(['systemctl', 'is-active', 'tor'], stderr=subprocess.PIPE, timeout=1).decode()
            if "active" in tor_status:
                return "Active (Service Running)"
            return "Inactive"
        except:
            return "Not Found"

    def check_dns(self):
        try:
            # DNS ayarlarını kontrol et
            with open('/etc/resolv.conf', 'r') as f:
                dns_content = f.read()
            
            # DNS sağlayıcılarını kontrol et
            dns_providers = {
                '1.1.1.1': 'Cloudflare',
                '8.8.8.8': 'Google',
                '9.9.9.9': 'Quad9',
                '208.67.222.222': 'OpenDNS'
            }
            
            for ip, provider in dns_providers.items():
                if ip in dns_content:
                    return f"Using {provider}"
            
            return "Using Default DNS"
        except:
            return "Unknown"

    def get_public_ip(self):
        try:
            # IP bilgisini al
            response = requests.get('https://api.ipify.org?format=json', timeout=2)
            ip = response.json()['ip']
            return f"{ip}"
        except:
            return "Could not fetch IP"

    def show_network_info(self):
        content = tk.Frame(self.main_area, bg="#000000")
        content.pack(fill="both", expand=True, padx=25, pady=25)
        
        tk.Label(content, 
                text="NETWORK INFORMATION", 
                font=self.title_font,
                bg="#000000",
                fg="#00ff00").pack(anchor="w", pady=(0, 20))
        
        # Ağ bilgilerini al
        net_info = self.get_network_info()
        
        for i, (key, value) in enumerate(net_info.items()):
            frame = tk.Frame(content, bg="#000000")
            frame.pack(fill="x", pady=5)
            
            tk.Label(frame, 
                    text=f"{key}:", 
                    bg="#000000", 
                    fg="#00ff00",
                    font=self.bold_font, 
                    width=20, 
                    anchor="w").pack(side="left")
            tk.Label(frame, 
                    text=value, 
                    bg="#000000",
                    fg="#00ff00").pack(side="left", padx=10)

    def show_disk_info(self):
        content = tk.Frame(self.main_area, bg="#000000")
        content.pack(fill="both", expand=True, padx=25, pady=25)
        
        tk.Label(content, 
                text="DISK INFORMATION", 
                font=self.title_font,
                bg="#000000",
                fg="#00ff00").pack(anchor="w", pady=(0, 20))
        
        # Disk bilgilerini al
        disks = self.get_disk_info()
        
        for disk in disks:
            frame = tk.Frame(content, bg="#000000")
            frame.pack(fill="x", pady=10)
            
            tk.Label(frame, 
                    text=f"{disk['Mount']}:", 
                    bg="#000000", 
                    fg="#00ff00",
                    font=self.bold_font, 
                    width=20, 
                    anchor="w").pack(side="left")
            
            canvas = tk.Canvas(frame, height=20, bg="#121212", highlightthickness=0)
            canvas.pack(side="left", fill="x", expand=True, padx=10)
            percent = float(disk['Used'].replace('%', ''))
            canvas.create_rectangle(0, 0, percent*2, 20, fill="#006400", outline="")
            
            tk.Label(frame, 
                    text=f"{disk['Used']} of {disk['Size']} (Free: {disk['Free']})", 
                    bg="#000000",
                    fg="#00ff00").pack(side="left", padx=10)

    def show_processes(self):
        content = tk.Frame(self.main_area, bg="#000000")
        content.pack(fill="both", expand=True, padx=25, pady=25)
        
        tk.Label(content, 
                text="TOP PROCESSES", 
                font=self.title_font,
                bg="#000000",
                fg="#00ff00").pack(anchor="w", pady=(0, 20))
        
        # CPU kullanan prosesler
        tk.Label(content,
                text="By CPU Usage:",
                bg="#000000",
                fg="#00ff00",
                font=self.bold_font).pack(anchor="w", pady=(10, 5))
        
        for p in sorted(psutil.process_iter(['pid', 'name', 'cpu_percent']), 
                      key=lambda p: p.info['cpu_percent'], 
                      reverse=True)[:5]:
            frame = tk.Frame(content, bg="#000000")
            frame.pack(fill="x", pady=2)
            tk.Label(frame, 
                    text=f"{p.info['name']}:", 
                    bg="#000000", 
                    fg="#00ff00",
                    width=30, 
                    anchor="w").pack(side="left")
            tk.Label(frame, 
                    text=f"{p.info['cpu_percent']:.1f}%", 
                    bg="#000000",
                    fg="#00ff00").pack(side="left")

    def show_about(self):
        content = tk.Frame(self.main_area, bg="#000000")
        content.pack(fill="both", expand=True, padx=25, pady=25)
        
        tk.Label(content, 
                text="ABOUT THIS PANEL", 
                font=self.title_font,
                bg="#000000",
                fg="#00ff00").pack(anchor="w", pady=(0, 20))
        
        about_text = """
        Linux System Control Panel v1.0
        
        Features:
        - Real-time system monitoring
        - Privacy status checking
        - Network information display
        - Disk usage visualization
        - Process management
        
        Python Libraries Used:
        - psutil {psutil_version}
        - platform
        - tkinter
        
        Developed for Linux enthusiasts
        """.format(psutil_version=psutil.__version__)
        
        tk.Label(content, 
                text=about_text, 
                bg="#000000",
                fg="#00ff00",
                justify="left").pack(anchor="w")

    def check_updates(self):
        try:
            # APT kontrolü
            apt_status = subprocess.check_output(['apt', 'list', '--upgradable'], stderr=subprocess.PIPE, timeout=1).decode()
            if "Listing..." in apt_status and "upgradable" in apt_status:
                return "Updates Available"
            return "Up to Date"
        except:
            return "Unknown"

    def check_antivirus(self):
        try:
            # ClamAV kontrolü
            clamav_status = subprocess.check_output(['systemctl', 'is-active', 'clamav-daemon'], stderr=subprocess.PIPE, timeout=1).decode()
            if "active" in clamav_status:
                return "Active (ClamAV)"
            return "Not Found"
        except:
            return "Not Found"

    def check_selinux(self):
        try:
            selinux_status = subprocess.check_output(['getenforce'], stderr=subprocess.PIPE, timeout=1).decode().strip()
            return selinux_status
        except:
            return "Not Found"

    def check_apparmor(self):
        try:
            apparmor_status = subprocess.check_output(['aa-status'], stderr=subprocess.PIPE, timeout=1).decode()
            if "apparmor module is loaded" in apparmor_status:
                return "Active"
            return "Inactive"
        except:
            return "Not Found"

    def check_encryption(self):
        try:
            # LUKS kontrolü
            luks_status = subprocess.check_output(['lsblk', '-f'], stderr=subprocess.PIPE, timeout=1).decode()
            if "crypto_LUKS" in luks_status:
                return "Enabled"
            return "Not Found"
        except:
            return "Not Found"

    def check_secure_boot(self):
        try:
            secure_boot = subprocess.check_output(['mokutil', '--sb-state'], stderr=subprocess.PIPE, timeout=1).decode()
            if "SecureBoot enabled" in secure_boot:
                return "Enabled"
            return "Disabled"
        except:
            return "Not Found"

    def get_network_info(self):
        try:
            net = psutil.net_io_counters()
            addrs = psutil.net_if_addrs()
            return {
                "IP Address": self.get_ip_address(),
                "MAC Address": self.get_mac_address(),
                "Download": f"{net.bytes_recv/1024/1024:.1f} MB",
                "Upload": f"{net.bytes_sent/1024/1024:.1f} MB",
                "Packets": f"↓{net.packets_recv} ↑{net.packets_sent}",
                "Interfaces": self.get_interface_status()
            }
        except:
            return {
                "IP Address": "N/A",
                "MAC Address": "N/A",
                "Download": "N/A",
                "Upload": "N/A",
                "Packets": "N/A",
                "Interfaces": "N/A"
            }

    def get_ip_address(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
        except:
            return "N/A"

    def get_mac_address(self):
        try:
            mac = psutil.net_if_addrs()[list(psutil.net_if_addrs().keys())[0]][0].address
            return mac if mac.count(':') == 5 else "N/A"
        except:
            return "N/A"

    def get_interface_status(self):
        try:
            stats = psutil.net_if_stats()
            return "\n".join([f"{k}: {'Up' if v.isup else 'Down'}" for k, v in stats.items()])
        except:
            return "N/A"

    def get_disk_info(self):
        try:
            partitions = []
            for part in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(part.mountpoint)
                    partitions.append({
                        "Mount": part.mountpoint,
                        "Used": f"{usage.percent}%",
                        "Size": f"{usage.total/1024/1024/1024:.1f} GB",
                        "Free": f"{usage.free/1024/1024/1024:.1f} GB",
                        "Type": part.fstype
                    })
                except:
                    continue
            return partitions
        except:
            return []

    def create_menu_button(self, text, index):
        btn = tk.Button(self.sidebar,
                      text=text,
                      bg="#121212",
                      fg="#00ff00",
                      activebackground="#252525",
                      activeforeground="#00ff00",
                      borderwidth=0,
                      font=self.bold_font,
                      anchor="w",
                      padx=15,
                      pady=12,
                      command=lambda: self.switch_tab(index))
        btn.pack(fill="x", pady=3)

    def show_system_info(self):
        content = tk.Frame(self.main_area, bg="#000000")
        content.pack(fill="both", expand=True, padx=25, pady=25)
        
        tk.Label(content, 
                text="SYSTEM INFORMATION", 
                font=self.title_font,
                bg="#000000",
                fg="#00ff00").pack(anchor="w", pady=(0, 20))
        
        info_frame = tk.Frame(content, bg="#000000")
        info_frame.pack(fill="x")
        
        system_info = self.get_system_info()
        
        for i, (key, value) in enumerate(system_info.items()):
            tk.Label(info_frame, 
                    text=f"{key}:", 
                    bg="#000000", 
                    fg="#00ff00",
                    font=self.bold_font, 
                    width=20, 
                    anchor="w").grid(row=i, column=0, sticky="w", pady=2)
            tk.Label(info_frame, 
                    text=value, 
                    bg="#000000",
                    fg="#00ff00").grid(row=i, column=1, sticky="w", padx=10, pady=2)
        
        self.create_usage_bars(content)

    def create_usage_bars(self, parent):
        frame = tk.Frame(parent, bg="#000000")
        frame.pack(fill="x", pady=20)
        
        # CPU Usage
        cpu_frame = tk.Frame(frame, bg="#000000")
        cpu_frame.pack(fill="x", pady=5)
        tk.Label(cpu_frame, 
                text="CPU Usage:", 
                bg="#000000",
                fg="#00ff00",
                font=self.bold_font).pack(side="left")
        
        cpu_canvas = tk.Canvas(cpu_frame, height=20, bg="#121212", highlightthickness=0)
        cpu_canvas.pack(side="left", fill="x", expand=True, padx=10)
        cpu_percent = psutil.cpu_percent()
        cpu_canvas.create_rectangle(0, 0, cpu_percent*2, 20, fill="#006400", outline="")
        tk.Label(cpu_frame, 
                text=f"{cpu_percent}%", 
                bg="#000000",
                fg="#00ff00").pack(side="left")
        
        # RAM Usage
        ram_frame = tk.Frame(frame, bg="#000000")
        ram_frame.pack(fill="x", pady=5)
        tk.Label(ram_frame, 
                text="RAM Usage:", 
                bg="#000000",
                fg="#00ff00",
                font=self.bold_font).pack(side="left")
        
        ram_canvas = tk.Canvas(ram_frame, height=20, bg="#121212", highlightthickness=0)
        ram_canvas.pack(side="left", fill="x", expand=True, padx=10)
        ram_percent = psutil.virtual_memory().percent
        ram_canvas.create_rectangle(0, 0, ram_percent*2, 20, fill="#006400", outline="")
        tk.Label(ram_frame, 
                text=f"{ram_percent}%", 
                bg="#000000",
                fg="#00ff00").pack(side="left")

if __name__ == "__main__":
    root = tk.Tk()
    app = LinuxSystemPanel(root)
    root.mainloop() 
