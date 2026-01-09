from network import coms

def start():
    coms.load_config()
    coms.send_to_hosts("test", port=5005, timeout=2.0, send=True)
    coms.send_to_hosts("info", port=5005, timeout=2.0, send=True)

