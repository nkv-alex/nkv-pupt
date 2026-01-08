# DEPENDENCIAS
import json
import os
import subprocess



# MODULOS PROPIOS
import config
import network
import network
import gui.gui
import worker_logic
from network import master_lgc
from network import coms
from gui import gui
from worker_logic import worker


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
    if config.get("Role") == "master":
        master_lgc.start()
        gui.gui.root.mainloop()
    elif config.get("Role") == "worker":
        worker.start()
    
    






if __name__ == "__main__":
    main()