"""Network summary diagnostics."""

from __future__ import annotations

import platform
import socket

from network_diagnostics.collectors.interfaces import (
    get_network_interfaces,
)


def get_network_summary() -> dict:
    """Collect a high-level summary of the local network environment."""
    interfaces = get_network_interfaces()

    active_interfaces = [
        interface
        for interface in interfaces
        if interface["is_up"]
    ]

    return {
        "hostname": socket.gethostname(),
        "operating_system": platform.system(),
        "os_release": platform.release(),
        "platform": platform.platform(),
        "active_interface_count": len(active_interfaces),
        "interface_count": len(interfaces),
        "interfaces": interfaces,
    }