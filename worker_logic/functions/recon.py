import os
import subprocess
import psutill


def run(cmd, check=True):
    return subprocess.run(cmd, shell=True, check=check, capture_output=True, text=True)

def recon():
    a = psutill.disk_usage("/")
    b = psutill.cpu_percent()
    c = psutill.virtual_memory()
    
    str(a,b,c)
    
    res="Disco duro usado: " + a +" Cpu usado: " + b + " Ram usado: " + c
    return res