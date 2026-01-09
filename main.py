# DEPENDENCIAS
import json
import os
import subprocess
import tkinter as tk
from tkinter import ttk
import ipaddress

# MODULOS PROPIOS
from network import master_lgc
from network import coms
from gui import gui
from worker_logic import worker
import configuration

CONFIG_FILE = "./config.json"


def load_config():
    if not os.path.exists(CONFIG_FILE):
        return {}
    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)


def main():
    files = load_config()
    if files.get("Position") == "":
        configuration.set_role()
        configuration.detect_interfaces()
    if files.get("Position") == "master":
        master_lgc.start()
        gui.gui_start()
    elif files.get("Position") == "worker":
        worker.start()
    
    






if __name__ == "__main__":
    main()