import socket
import threading
import pickle
import time
import json
import struct
import fcntl
import uuid 
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")



def load_config():
    if not os.path.exists(CONFIG_FILE):
        return {}
    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)


_config = load_config()
interfaces = _config.get('interfaces', {})

def get_broadcast(iface):
    print("enviado brodcast")
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        return socket.inet_ntoa(fcntl.ioctl(
            s.fileno(),
            0x8919,  # 
            struct.pack('256s', iface.encode('utf-8')[:15])
        )[20:24])
    except Exception as e:
        print(f"[net] Error getting broadcast for {iface}: {e}")
        return "255.255.255.255"
    finally:
        try:
            s.close()
        except Exception:
            pass



def send_to_hosts(payload, port=5005, timeout=2.0, send=True):

    DISCOVER_MESSAGE_PREFIX = "DISCOVER_REQUEST"
    RESPONSE_PREFIX = "DISCOVER_RESPONSE"
    HOSTS_FILE = os.path.join(BASE_DIR, "network", "host.json")

    config = load_config()
    print(f"[coms] Loaded config: {config}")
    interfaces = config.get('interfaces', {})
    print(f"[coms] Using interfaces from config: {interfaces}")
    internals = interfaces.get("Internal", {}).keys()
    print(f"[coms] Using internal interfaces: {list(internals)}")

    def save_hosts(discovered):
        try:
            with open(HOSTS_FILE, "w") as f:
                json.dump(discovered, f, indent=2)
            print(f"[store] {len(discovered)} hosts saved in {HOSTS_FILE}")
        except Exception as e:
            print(f"[store] Error saving hosts: {e}")

    discovered_total = {}

    for iface in internals:
        broadcast_ip = get_broadcast(iface)
        print(f"[discover:{iface}] using broadcast {broadcast_ip}")

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.settimeout(timeout)

        token = str(uuid.uuid4())[:8]
        discover_msg = f"{DISCOVER_MESSAGE_PREFIX}:{token}"
        sock.sendto(discover_msg.encode(), (broadcast_ip, port))
        print(f"[discover:{iface}] Broadcast sent, waiting {timeout}s...")

        start_time = time.time()
        while True:
            try:
                data, addr = sock.recvfrom(1024)
                text = data.decode(errors="ignore")
                ip, _ = addr
                if text.startswith(RESPONSE_PREFIX):
                    parts = text.split(":", 2)
                    # Solo guardar ip:nodeid
                    nodeid = parts[2] if len(parts) > 2 else ""
                    discovered_total[ip] = nodeid.strip()
                    print(f"[discover:{iface}] response from {ip} -> nodeid: {nodeid}")
            except socket.timeout:
                break
            if time.time() - start_time > timeout:
                break

    if not discovered_total:
        print("[discover] No listeners detected.")
        return {}

    print(f"[discover] Total {len(discovered_total)} hosts found:")
    for ip, nodeid in discovered_total.items():
        print(f"  - {ip} (nodeid: {nodeid})")

    save_hosts(discovered_total)

    if send:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(2.0)
        for ip in discovered_total.keys():
            try:
                sock.sendto(payload.encode(), (ip, port))
                print(f"[send] payload sent to {ip}")
                try:
                    data, addr = sock.recvfrom(1024)
                    print(f"[recv] response from {addr[0]}: {data.decode(errors='ignore')}")
                except socket.timeout:
                    print(f"[recv] no response from {ip}")
            except Exception as e:
                print(f"[send] failed to send to {ip}: {e}")

    return discovered_total

def send_ip(ip, payload, port=5005, timeout=2.0):
    """Envía un payload UDP a una IP específica."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(timeout)
        sock.sendto(payload.encode(), (ip, port))
        print(f"[send_ip] Payload enviado a {ip}:{port}")
        try:
            data, addr = sock.recvfrom(1024)
            print(f"[send_ip] Respuesta de {addr[0]}: {data.decode(errors='ignore')}")
        except socket.timeout:
            print(f"[send_ip] Sin respuesta de {ip}")
    except Exception as e:
        print(f"[send_ip] Error enviando a {ip}: {e}")
    finally:
        try:
            sock.close()
        except Exception:
            pass