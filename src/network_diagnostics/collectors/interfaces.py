"""Network interface discovery and diagnostics."""

from __future__ import annotations

import psutil


def get_network_interfaces() -> list[dict]:
    """Collect network interface information from the local system."""
    interfaces = psutil.net_if_addrs()
    interface_stats = psutil.net_if_stats()
    interface_counters = psutil.net_io_counters(pernic=True)

    results = []

    for name, addresses in interfaces.items():
        stats = interface_stats.get(name)
        counters = interface_counters.get(name)

        interface = {
            "name": name,
            "is_up": stats.isup if stats else False,
            "speed_mbps": stats.speed if stats else 0,
            "mtu": stats.mtu if stats else 0,
            "addresses": [],
            "bytes_sent": counters.bytes_sent if counters else 0,
            "bytes_received": counters.bytes_recv if counters else 0,
        }

        for address in addresses:
            interface["addresses"].append(
                {
                    "family": str(address.family),
                    "address": address.address,
                    "netmask": address.netmask,
                    "broadcast": address.broadcast,
                }
            )

        results.append(interface)

    return results