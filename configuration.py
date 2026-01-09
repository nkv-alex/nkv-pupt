import json
import os
import subprocess
import ipaddress
from typing import Dict

CONFIG_FILE = "./config.json"


def load_config() -> Dict:
    """Carga la configuración desde el archivo JSON. Devuelve dict vacío si no existe."""
    if not os.path.exists(CONFIG_FILE):
        return {}
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"[ERROR] No se pudo leer el archivo de configuración: {e}")
        return {}


def save_config(config: Dict) -> None:
    """Guarda la configuración en formato JSON bonito."""
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
    except IOError as e:
        print(f"[ERROR] No se pudo guardar la configuración: {e}")


def set_role() -> None:
    """Configura el rol del nodo (master/worker)"""
    config = load_config()
    current = config.get('role', 'not set')          # ← Recomiendo cambiar a 'role' (más claro)
    print(f"Current role: {current}")

    role = input("Select role (master/worker) [master]: ").strip().lower()
    
    if not role:
        role = "master"
    elif role not in ("master", "worker"):
        print("[WARN] Invalid role, defaulting to 'master'")
        role = "master"

    config['Position'] = role   # ← Sugerencia: usa 'role' en vez de 'Position'
    save_config(config)
    print(f"Rol actualizado correctamente a: {role}")


def detect_interfaces() -> Dict:
    """
    Detecta interfaces de red con IPv4 (excluyendo virtuales comunes)
    y permite clasificarlas como internas o externas.
    """
    config = load_config()

    # Aseguramos estructura básica
    if "interfaces" not in config:
        config["interfaces"] = {"Externals": {}, "Internals": {}}

    # Comando más limpio y portable (evita problemas con awk en algunos sistemas)
    cmd = r"""
    ip -o -4 addr show scope global \
      | awk -F'[ /]+' '{print $2, $4}' \
      | grep -vE '^(lo|docker|veth|br-|virbr|vmnet|tap|tun|wg|zabbix|pan)' || true
    """

    try:
        res = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            check=False
        )
    except Exception as e:
        print(f"[ERROR] Error ejecutando comando ip: {e}")
        return config.get("interfaces", {})

    out = res.stdout.strip()
    if not out:
        print("[INFO] No se encontraron interfaces IPv4 válidas (scope global)")
        return config["interfaces"]

    print("\n=== Detección de interfaces de red ===")
    updated = False

    for line in out.splitlines():
        if not line.strip():
            continue

        try:
            iface, addr = line.split()
            ip_interface = ipaddress.IPv4Interface(addr)
        except (ValueError, ipaddress.AddressValueError) as e:
            print(f"[WARN] Dirección inválida en {iface}: {addr} → {e}")
            continue

        # Sugerencia automática: privada → internal, pública → external
        suggested = "i" if ip_interface.ip.is_private else "e"
        default_str = "internal" if suggested == "i" else "external"

        print(f"\nInterfaz detectada: {iface}")
        print(f"   Dirección IP: {ip_interface}")
        print(f"   Sugerencia automática: {default_str}")

        while True:
            answer = input(f"¿Es interna (i) o externa (e)? [{suggested}]: ").strip().lower()
            
            if not answer:
                answer = suggested
            if answer in ('i', 'internal'):
                category = "Internals"
                break
            if answer in ('e', 'external'):
                category = "Externals"
                break
                
            print("   [?] Por favor responde con 'i'/'internal' o 'e'/'external'")

        config["interfaces"][category][iface] = str(ip_interface)
        updated = True

    if updated:
        save_config(config)
        print(f"[INFO] Configuración actualizada en {CONFIG_FILE}")
    else:
        print("[INFO] No se realizaron cambios en las interfaces")

    # Resumen final
    print("\nResumen final de interfaces:")
    print(f"  Internas: {list(config['interfaces']['Internals'].keys())}")
    print(f"  Externas: {list(config['interfaces']['Externals'].keys())}\n")

    return config["interfaces"]


if __name__ == "__main__":
    # Ejemplos de uso:
    # set_role()
    detect_interfaces()