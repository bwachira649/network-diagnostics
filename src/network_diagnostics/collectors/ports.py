"""TCP port and service diagnostics."""

from __future__ import annotations

import socket
import time


def _classify_connection_error(error_code: int) -> str:
    """Return a human-readable description for a socket error code."""
    if error_code in {10035, 10060}:
        return "Connection timed out or was unreachable."

    if error_code in {10061}:
        return "Connection refused by the destination."

    if error_code in {10051, 10065}:
        return "Network or host is unreachable."

    return f"Connection failed with error code {error_code}."


def check_tcp_port(
    host: str,
    port: int,
    timeout: float = 3.0,
) -> dict:
    """Test whether a TCP port is reachable on a host."""
    if not host.strip():
        raise ValueError("Host must not be empty.")

    if not 1 <= port <= 65535:
        raise ValueError("Port must be between 1 and 65535.")

    if timeout <= 0:
        raise ValueError("Timeout must be greater than 0.")

    start_time = time.perf_counter()

    try:
        destination_ip = socket.gethostbyname(host)

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(timeout)
            result = sock.connect_ex((destination_ip, port))

        success = result == 0

        if success:
            error = None
        else:
            error = _classify_connection_error(result)

    except socket.gaierror as exc:
        destination_ip = None
        success = False
        error = f"DNS resolution failed: {exc}"

    except OSError as exc:
        destination_ip = None
        success = False
        error = str(exc)

    elapsed_ms = (time.perf_counter() - start_time) * 1000

    return {
        "host": host,
        "destination_ip": destination_ip,
        "port": port,
        "success": success,
        "latency_ms": round(elapsed_ms, 2),
        "error": error,
    }