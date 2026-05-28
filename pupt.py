#!/usr/bin/env python3
# Requisitos: sudo apt install nmap iproute2
#             pip3 install paramiko --break-system-packages

import subprocess, socket, threading, getpass, sys

try:
    import paramiko
except ImportError:
    print("Instala paramiko: pip3 install paramiko --break-system-packages")
    sys.exit(1)

hosts = []

#Detectar interfaces de red
def obtener_interfaces():
    ifaces = []
    try:
        r = subprocess.run(["ip", "-o", "-4", "addr", "show"],
                           capture_output=True, text=True)
        for linea in r.stdout.splitlines():
            partes = linea.split()
            nombre = partes[1]
            if nombre == "lo":
                continue
            cidr   = partes[3]          
            ip     = cidr.split("/")[0]
            prefijo = cidr.split("/")[1]
            import ipaddress
            red = str(ipaddress.IPv4Network(cidr, strict=False))
            ifaces.append({"nombre": nombre, "ip": ip, "red": red})
    except Exception as e:
        print(f"Error leyendo interfaces: {e}")
    return ifaces

def elegir_interfaz():
    ifaces = obtener_interfaces()
    if not ifaces:
        print("No se encontraron interfaces de red.")
        sys.exit(1)
    if len(ifaces) == 1:
        i = ifaces[0]
        print(f"Interfaz: {i['nombre']}  {i['ip']}  ({i['red']})")
        return i
    print("\nInterfaces disponibles:")
    for n, i in enumerate(ifaces, 1):
        print(f"  {n}) {i['nombre']:<10} {i['ip']:<18} {i['red']}")
    while True:
        try:
            op = int(input("\nElige interfaz: ")) - 1
            return ifaces[op]
        except (ValueError, IndexError):
            print("Inválido.")

#Escaneo
def escanear():
    global hosts
    hosts = []
    iface = elegir_interfaz()
    ip_local = iface["ip"]
    red      = iface["red"]

    print(f"\nEscaneando {red} en {iface['nombre']} ...")
    r = subprocess.run(
        ["nmap", "-sn", "-T4", red],
        capture_output=True, text=True, timeout=90
    )

    ip_act = None
    for l in r.stdout.splitlines():
        if "Nmap scan report for" in l:
            ip_act = l.split()[-1].strip("()")
        elif "Host is up" in l and ip_act and ip_act != ip_local:
            try:    nombre = socket.gethostbyaddr(ip_act)[0]
            except: nombre = ip_act
            hosts.append({"ip": ip_act, "nombre": nombre, "ssh": False})
            ip_act = None

    # comprobar SSH en paralelo
    def chk(h):
        try:
            s = socket.create_connection((h["ip"], 22), timeout=2)
            s.close(); h["ssh"] = True
        except: pass
    ts = [threading.Thread(target=chk, args=(h,)) for h in hosts]
    [t.start() for t in ts]; [t.join() for t in ts]

    print(f"\n{'#':>3}  {'IP':<18} {'NOMBRE':<30} SSH")
    print("-" * 58)
    for i, h in enumerate(hosts, 1):
        print(f"{i:>3}  {h['ip']:<18} {h['nombre']:<30} {'SI' if h['ssh'] else 'no'}")
    print()

#SSH
def conectar(ip, usuario, password):
    c = paramiko.SSHClient()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    c.connect(ip, username=usuario, password=password, timeout=10)
    return c

def shell(cliente, ip):
    print(f"\nConectado a {ip}. Escribe 'salir' para volver al menú.\n")
    while True:
        cmd = input(f"{ip}$ ").strip()
        if cmd in ("salir", "exit", "quit"):
            break
        if not cmd:
            continue
        _, out, err = cliente.exec_command(cmd, timeout=30)
        print(out.read().decode(errors="replace"), end="")
        print(err.read().decode(errors="replace"), end="")

#Menú
def main():
    while True:
        print("\n1) Escanear red")
        print("2) Conectar a equipo de la lista")
        print("3) Conectar a IP manual")
        print("0) Salir")
        op = input("\nOpción: ").strip()

        if op == "1":
            escanear()

        elif op == "2":
            if not hosts:
                print("Primero escanea la red.")
                continue
            try:
                n = int(input("Número: ")) - 1
                h = hosts[n]
            except: print("Inválido."); continue
            if not h["ssh"]: print("Sin SSH."); continue
            u = input("Usuario: ").strip() or getpass.getuser()
            p = getpass.getpass("Contraseña: ")
            try:
                c = conectar(h["ip"], u, p)
                shell(c, h["ip"])
                c.close()
            except Exception as e:
                print(f"Error: {e}")

        elif op == "3":
            ip = input("IP: ").strip()
            u  = input("Usuario: ").strip() or getpass.getuser()
            p  = getpass.getpass("Contraseña: ")
            try:
                c = conectar(ip, u, p)
                shell(c, ip)
                c.close()
            except Exception as e:
                print(f"Error: {e}")

        elif op == "0":
            sys.exit(0)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nSaliendo.")
