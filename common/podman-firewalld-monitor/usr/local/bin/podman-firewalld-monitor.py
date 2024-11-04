#!/usr/bin/python3

import dbus
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib
import subprocess
import sys
import logging


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('/var/log/podman-firewalld-monitor.log')
    ]
)

def reload_podman_networks(connection=None):
    """Reload all podman networks"""
    try:
        logging.info("Firewalld reload detected, reloading Podman networks")
        subprocess.run(['/usr/bin/podman', 'network', 'reload', '--all'], 
                      check=True,
                      capture_output=True,
                      text=True)
        logging.info("Podman networks reloaded successfully")
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to reload Podman networks: {e.stderr}")

def handle_reloaded(*args, **kwargs):
    """Handle the Reloaded signal from firewalld"""
    reload_podman_networks()

def main():
    try:
   
        DBusGMainLoop(set_as_default=True)
        
  
        bus = dbus.SystemBus()
        
        # Create proxy object for firewalld
        proxy = bus.get_object(
            "org.fedoraproject.FirewallD1",
            "/org/fedoraproject/FirewallD1"
        )
        
        proxy.connect_to_signal("Reloaded", handle_reloaded)
        
        logging.info("Started monitoring firewalld reloads")
        
        loop = GLib.MainLoop()
        loop.run()
        
    except dbus.exceptions.DBusException as e:
        logging.error(f"Failed to connect to D-Bus: {e}")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()