# 🌐 IP Rotator PRO

> Automatic IP rotation tool for Linux — rotate your public IP via Tor circuits

![Banner](banner.png)

![Python](https://img.shields.io/badge/Python-3.8+-blue)
![Linux](https://img.shields.io/badge/Platform-Linux-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

## 📖 About

**IP Rotator PRO** is a professional Python tool that automatically rotates 
your IP address at configurable intervals. It uses Tor circuits for real 
public IP rotation, perfect for privacy, web scraping, and penetration testing.

## ✨ Features

- ✅ Real public IP rotation via Tor circuits
- ✅ Configurable rotation interval
- ✅ Auto-detection of network interface
- ✅ Real-time statistics and history
- ✅ Colored terminal output
- ✅ Ctrl+C graceful shutdown

## 🛠️ Installation

```bash
# Install dependencies
sudo apt update
sudo apt install tor curl python3 -y

# Start Tor service
sudo systemctl enable tor
sudo systemctl start tor

# Clone repo
git clone https://github.com/asadullah-sayeedi/ip-rotator-pro.git
cd ip-rotator-pro
