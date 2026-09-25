"""DNS resolution diagnostics."""

from __future__ import annotations

import socket
import time


def resolve_hostname(host: str) -> dict:
    """Resolve a hostname and collect IPv4/IPv6 addresses."""
    if not host.strip():
        raise ValueError("Hostname must not be empty.")

    start_time = time.perf_counter()

    try:
        results = socket.getaddrinfo(
            host,
            None,
            type=socket.SOCK_STREAM,
        )

        ipv4_addresses = sorted(
            {
                result[4][0]
                for result in results
                if result[0] == socket.AF_INET
            }
        )

        ipv6_addresses = sorted(
            {
                result[4][0]
                for result in results
                if result[0] == socket.AF_INET6
            }
        )

        success = bool(ipv4_addresses or ipv6_addresses)
        error = None

    except socket.gaierror as exc:
        ipv4_addresses = []
        ipv6_addresses = []
        success = False
        error = str(exc)

    elapsed_ms = (time.perf_counter() - start_time) * 1000

    return {
        "host": host,
        "success": success,
        "ipv4_addresses": ipv4_addresses,
        "ipv6_addresses": ipv6_addresses,
        "lookup_time_ms": round(elapsed_ms, 2),
        "error": error,
    }