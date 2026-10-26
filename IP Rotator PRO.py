#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════╗
║         MAC + IP CHANGER PRO v3.0                            ║
║         واقعاً IP محلی رو عوض می‌کنه!                          ║
╚══════════════════════════════════════════════════════════════╝
"""

import os
import sys
import time
import random
import signal
import subprocess
import re
from datetime import datetime

class C:
    R='\033[91m'; G='\033[92m'; Y='\033[93m'; B='\033[94m'
    M='\033[95m'; Cy='\033[96m'; W='\033[97m'; BOLD='\033[1m'; X='\033[0m'

def log(msg, color=C.W):
    print(f"{C.B}[{datetime.now().strftime('%H:%M:%S')}]{C.X} {color}{msg}{C.X}")

def banner():
    os.system('clear')
    print(f"""{C.Cy}{C.BOLD}
╔══════════════════════════════════════════════════════════════╗
║      MAC + IP CHANGER PRO v3.0 - REAL IP ROTATION            ║
╚══════════════════════════════════════════════════════════════╝
{C.X}""")

class RealIPChanger:
    def __init__(self, interval=60):
        self.interval = interval
        self.running = False
        self.iface = self.get_interface()
        self.count = 0
        self.history = []
    
    def cmd(self, command, timeout=20):
        try:
            r = subprocess.run(command, shell=True, capture_output=True,
                             text=True, timeout=timeout)
            return r.returncode == 0, r.stdout.strip(), r.stderr.strip()
        except:
            return False, "", ""
    
    def get_interface(self):
        """پیدا کردن کارت شبکه"""
        ok, out, _ = self.cmd("ip route | grep default | awk '{print $5}' | head -1")
        if ok and out:
            return out.strip()
        # fallback
        ok, out, _ = self.cmd("ls /sys/class/net | grep -v lo | head -1")
        return out.strip() if ok else "eth0"
    
    def get_local_ip(self):
        """گرفتن IP محلی فعلی"""
        ok, out, _ = self.cmd(
            f"ip -4 addr show {self.iface} | grep -oP '(?<=inet\\s)\\d+(\\.\\d+){{3}}'"
        )
        return out.strip() if (ok and out) else "None"
    
    def get_gateway(self):
        """گرفتن gateway"""
        ok, out, _ = self.cmd("ip route | grep default | awk '{print $3}' | head -1")
        return out.strip() if ok else None
    
    def get_subnet(self):
        """گرفتن subnet فعلی"""
        ip = self.get_local_ip()
        if ip and ip != "None":
            return ".".join(ip.split('.')[:3])
        return "192.168.1"
    
    # ═══════════════════════════════════════════════════════════
    # روش ۱: تغییر MAC (مطمئن‌ترین روش)
    # ═══════════════════════════════════════════════════════════
    
    def change_mac(self):
        """تغییر MAC address"""
        # MAC random بساز
        mac = "02:%02x:%02x:%02x:%02x:%02x" % tuple(random.randint(0,255) for _ in range(5))
        
        # خاموش کردن interface
        self.cmd(f"sudo ip link set {self.iface} down")
        time.sleep(1)
        
        # تغییر MAC
        ok, _, err = self.cmd(f"sudo ip link set {self.iface} address {mac}")
        
        if not ok:
            # روش جایگزین با macchanger
            self.cmd(f"sudo macchanger -r {self.iface}")
        
        # روشن کردن
        self.cmd(f"sudo ip link set {self.iface} up")
        time.sleep(1)
        
        log(f"  [*] New MAC: {mac}", C.Cy)
        return True
    
    def renew_dhcp(self):
        """گرفتن IP جدید از DHCP"""
        # Release
        self.cmd(f"sudo dhclient -r {self.iface}", timeout=15)
        time.sleep(1)
        
        # Renew
        self.cmd(f"sudo dhclient {self.iface}", timeout=25)
        time.sleep(2)
    
    # ═══════════════════════════════════════════════════════════
    # روش ۲: IP استاتیک رندوم
    # ═══════════════════════════════════════════════════════════
    
    def set_static_ip(self):
        """ست کردن IP استاتیک رندوم"""
        subnet = self.get_subnet()
        gateway = self.get_gateway()
        
        # IP رندوم
        new_ip = f"{subnet}.{random.randint(50, 250)}"
        
        # حذف IP قبلی و ست کردن جدید
        self.cmd(f"sudo ip addr flush dev {self.iface}")
        self.cmd(f"sudo ip addr add {new_ip}/24 dev {self.iface}")
        self.cmd(f"sudo ip link set {self.iface} up")
        
        if gateway:
            self.cmd(f"sudo ip route add default via {gateway}")
        
        return new_ip
    
    # ═══════════════════════════════════════════════════════════
    # چرخش اصلی
    # ═══════════════════════════════════════════════════════════
    
    def rotate(self):
        """تغییر IP"""
        self.count += 1
        
        print(f"\n{C.B}{'═'*60}{C.X}")
        log(f"{C.BOLD}{C.M}🔄 IP CHANGE #{self.count}{C.X}", C.M)
        print(f"{C.B}{'═'*60}{C.X}")
        
        old_ip = self.get_local_ip()
        log(f"  {C.R}[-] Old IP: {old_ip}{C.X}", C.R)
        
        # ═══ تغییر MAC + DHCP (مطمئن‌ترین) ═══
        log(f"  {C.Y}[*] Changing MAC address...{C.X}", C.Y)
        self.change_mac()
        
        log(f"  {C.Y}[*] Requesting new DHCP lease...{C.X}", C.Y)
        self.renew_dhcp()
        
        # ═══ تأیید تغییر ═══
        time.sleep(2)
        new_ip = self.get_local_ip()
        
        print(f"{C.B}{'─'*60}{C.X}")
        
        if new_ip != old_ip and new_ip != "None":
            self.history.append(new_ip)
            log(f"  {C.G}{C.BOLD}[✓] NEW IP: {new_ip}{C.X}", C.G)
            log(f"  {C.G}[✓] IP SUCCESSFULLY CHANGED!{C.X}", C.G)
            result = True
        else:
            log(f"  {C.R}[!] IP unchanged: {new_ip}{C.X}", C.R)
            log(f"  {C.DIM}    DHCP gave same IP, trying static method...{C.X}", C.DIM)
            
            # تلاش با روش استاتیک
            static_ip = self.set_static_ip()
            time.sleep(2)
            check = self.get_local_ip()
            
            if check != old_ip:
                self.history.append(check)
                log(f"  {C.G}[✓] NEW IP (static): {check}{C.X}", C.G)
                result = True
            else:
                result = False
        
        print(f"{C.B}{'─'*60}{C.X}")
        log(f"  {C.Cy}📊 Total unique IPs: {len(set(self.history))}{C.X}", C.Cy)
        
        return result
    
    def countdown(self, seconds):
        """شمارش معکوس"""
        for i in range(seconds, 0, -1):
            if not self.running:
                break
            bar_len = 30
            filled = int(bar_len * (seconds - i) / seconds)
            bar = '█' * filled + '░' * (bar_len - filled)
            print(f"\r  {C.Cy}[{bar}]{C.X} {C.Y}next in {i:3d}s{C.X}  ", end="", flush=True)
            time.sleep(1)
        print()
    
    def start(self):
        banner()
        
        log(f"{C.BOLD}{C.Cy}[*] INITIALIZING{C.X}\n", C.Cy)
        log(f"  Interface: {C.M}{self.iface}{C.X}", C.W)
        log(f"  Current IP: {C.M}{self.get_local_ip()}{C.X}", C.W)
        log(f"  Interval: {C.M}{self.interval}s{C.X}", C.W)
        log(f"  Method: {C.M}MAC change + DHCP{C.X}", C.W)
        log(f"\n  Press {C.R}Ctrl+C{C.X} to stop\n", C.W)
        
        # چک macchanger
        ok, _, _ = self.cmd("which macchanger")
        if not ok:
            log(f"[!] Install macchanger: sudo apt install macchanger", C.Y)
        
        self.running = True
        self.rotate()
        
        while self.running:
            try:
                self.countdown(self.interval)
                if self.running:
                    self.rotate()
            except KeyboardInterrupt:
                break
        
        self.stop()
    
    def stop(self):
        self.running = False
        print(f"\n{C.B}{'═'*60}{C.X}")
        log(f"{C.BOLD}{C.R}🛑 STOPPED{C.X}", C.R)
        log(f"  Total changes: {self.count}", C.Cy)
        log(f"  Unique IPs: {len(set(self.history))}", C.Cy)
        
        if self.history:
            print(f"\n  {C.Cy}IP History:{C.X}")
            for i, ip in enumerate(self.history, 1):
                log(f"    {i}. {ip}", C.G)
        print(f"{C.B}{'═'*60}{C.X}")

# ═════════════════════════════════════════════════════════════════

def main():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('-i', '--interval', type=int, default=60)
    args = p.parse_args()
    
    if os.geteuid() != 0:
        print(f"{C.R}[!] Run with sudo!{C.X}")
        sys.exit(1)
    
    changer = RealIPChanger(interval=args.interval)
    signal.signal(signal.SIGINT, lambda s, f: setattr(changer, 'running', False))
    
    try:
        changer.start()
    except KeyboardInterrupt:
        changer.stop()

if __name__ == '__main__':
    main()