# DEPENDENCIAS
import json
import os
import subprocess



# MODULOS PROPIOS
import config
import network.coms
import network.master_lgc
import gui.gui




CONFIG_FILE = "config.json"


def load_config():
    if not os.path.exists(CONFIG_FILE):
        return {}
    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)


def main():
    config = load_config()
    if config.get("Position") == "":
        config.set_role()
        config.detect_interfaces()
    






if __name__ == "__main__":
    main()