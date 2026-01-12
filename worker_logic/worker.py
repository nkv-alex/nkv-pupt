#!/usr/bin/env python3
"""
listener.py — escucha en la LAN por discovery y mensajes
Uso seguro: solo en redes/hosts bajo tu control
"""
import socket
import platform
import uuid
import subprocess
import yaml
import os
import shutil


from worker_logic.functions import recon

BROADCAST_PORT = 5005
BUFFER_SIZE = 1024
DISCOVER_PREFIX = "DISCOVER_REQUEST"
RESPONSE_PREFIX = "DISCOVER_RESPONSE"

_last_addr = None
_last_sock = None

ip_hostname_map = []  

def run(cmd, check=True):
    return subprocess.run(cmd, shell=True, check=check, capture_output=True, text=True)




def respuesta(mensaje: str):
    """
    Envía una respuesta al último host que envió un mensaje.
    Args:
        mensaje (str): texto de la respuesta
    """
    global _last_addr, _last_sock
    if not _last_addr or not _last_sock:
        print("[listener] No hay contexto de conexión previo para enviar respuesta.")
        return

    ip, port = _last_addr
    full_msg = f"{RESPONSE_PREFIX}:{mensaje}:{platform.node()}:{uuid.getnode()}"
    _last_sock.sendto(full_msg.encode(), _last_addr)
    print(f"[listener] Respuesta enviada a {ip}:{port} → {mensaje}")


def recon():
    ''' devuelve estadistica del sistema'''
    a = recon.recon()



def start(bind_ip="0.0.0.0", port=BROADCAST_PORT):
    global _last_addr, _last_sock

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((bind_ip, port))
    hostname = platform.node()
    print(f"[listener] escuchando UDP en {bind_ip}:{port} — host: {hostname}")

    while True:
        try:
            data, addr = sock.recvfrom(BUFFER_SIZE)
            text = data.decode(errors="ignore").strip()
            ip, _ = addr

            # Actualiza el contexto global
            _last_addr = addr
            _last_sock = sock

            # Si es un mensaje DISCOVER
            if text.startswith(DISCOVER_PREFIX):
                respuesta("DISCOVER MSG")
                print(f"[listener] recibido DISCOVER de {ip}, respondido.")
                continue

            # Procesar payload dinámico con match-case
            match text:
                case "test":
                    print(f"[listener] Acción 1 ejecutada por {ip}")
                    respuesta("te escucho")
                
                case "info":
                    respuesta(f"Host: {hostname}, IP: {ip}")

                case "recon":
                    a = recon.recon()
                    respuesta({a})              

                case _:
                    print(f"[listener] mensaje desconocido de {ip}: '{text}'")
                    respuesta("none")

        except KeyboardInterrupt:
            print("[listener] detenido por usuario.")
            break
        except Exception as e:
            print(f"[listener] error: {e}")

