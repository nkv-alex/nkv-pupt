import json
import os
import subprocess
import ipaddress

CONFIG_FILE = "./config.json"

def load_config():
    if not os.path.exists(CONFIG_FILE):
        return {}
    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)
    
def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)

def set_role():
    config = load_config()
    current = config['Position']
    print(f"Current role: {current}")

    role = input("Select role (master/worker) [master]: ").strip().lower()
    if role == "":
        role = "master"
    if role not in ("master", "worker"):
        print("[WARN] Invalid role, using 'master'")
        role = "master"

    config['Position'] = role
    save_config(config)

def detect_interfaces():
    """Detect interfaces and saves it in config.json."""
    config = load_config()
    
    # Initialize interfaces structure if not present
    if "interfaces" not in config:
        config["interfaces"] = {"Externals": {}, "Internals": {}}
    
    try:
        res = subprocess.run(
            "ip -o -4 addr show | awk '{print $2,$4}' | grep -Ev '^(lo|docker|veth|br-|virbr|vmnet|tap)' || true",
            capture_output=True,
            text=True,
            check=False,
            shell=True
        )
    except Exception as e:
        print(f"[ERROR] Error running 'ip': {e}")
        return config.get("interfaces", {})
    
    out = res.stdout.strip()
    if not out:
        print("[ERROR] No interfaces with assigned IPv4 found.")
        return config.get("interfaces", {})

    print("\n=== Interface detection ===")

    updated = False
    for line in out.splitlines():
        parts = line.split()
        if len(parts) < 2:
            continue

        iface, addr = parts[0], parts[1]
        try:
            ipif = ipaddress.IPv4Interface(addr)
        except Exception:
            print(f"[WARN] Invalid address in {iface}: {addr}, skipping.")
            continue

        suggested = "i" if ipif.ip.is_private else "e"
        tipo = input(f"\nDetected interface: {iface}\n  IP address: {ipif}\nIs this interface internal (i) or external (e)? [{suggested}]: ").strip().lower()

        if tipo == "":
            tipo = suggested
        if tipo not in ("i", "e", "internal", "external"):
            tipo = suggested

        category = "Internals" if tipo.startswith("i") else "Externals"
        config["interfaces"][category][iface] = str(ipif)
        updated = True

    if updated:
        save_config(config)
        print(f"[INFO] Configuration updated in {CONFIG_FILE}")
    else:
        print("[INFO] No changes in interfaces.")

    print("\nFinal summary:")
    print(f"  Internal: {list(config['interfaces']['Internals'].keys())}")
    print(f"  External: {list(config['interfaces']['Externals'].keys())}")

    return config["interfaces"]