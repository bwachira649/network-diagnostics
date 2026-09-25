"""Network route and path diagnostics."""

from __future__ import annotations

import ipaddress
import platform
import re
import subprocess
import time


def _extract_ip_address(text: str) -> str | None:
    """Extract the first valid IPv4 or IPv6 address from text."""
    candidates = re.findall(
        r"(?:[0-9a-fA-F]{0,4}:){2,}[0-9a-fA-F:.]+"
        r"|(?:\d{1,3}\.){3}\d{1,3}",
        text,
    )

    for candidate in candidates:
        try:
            ipaddress.ip_address(candidate)
            return candidate
        except ValueError:
            continue

    return None


def trace_route(host: str, max_hops: int = 12) -> dict:
    """Trace the network path to a destination host."""
    if not host.strip():
        raise ValueError("Host must not be empty.")

    if max_hops < 1:
        raise ValueError("Maximum hops must be at least 1.")

    if platform.system().lower() == "windows":
        command = [
            "tracert",
            "-d",
            "-h",
            str(max_hops),
            host,
        ]
    else:
        command = [
            "traceroute",
            "-n",
            "-m",
            str(max_hops),
            host,
        ]

    start_time = time.perf_counter()

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=max(30, max_hops * 3),
        )

        output = result.stdout + result.stderr
        success = result.returncode == 0

    except FileNotFoundError as exc:
        elapsed_ms = (time.perf_counter() - start_time) * 1000

        return {
            "host": host,
            "success": False,
            "hops": [],
            "hop_count": 0,
            "elapsed_ms": round(elapsed_ms, 2),
            "error": f"Route diagnostic command unavailable: {exc}",
        }

    except subprocess.TimeoutExpired:
        elapsed_ms = (time.perf_counter() - start_time) * 1000

        return {
            "host": host,
            "success": False,
            "hops": [],
            "hop_count": 0,
            "elapsed_ms": round(elapsed_ms, 2),
            "error": "Route diagnostic timed out.",
        }

    elapsed_ms = (time.perf_counter() - start_time) * 1000

    hops = []

    for line in output.splitlines():
        line = line.strip()

        hop_match = re.match(r"^(\d+)\s+(.*)$", line)

        if not hop_match:
            continue

        hop_number = int(hop_match.group(1))
        hop_data = hop_match.group(2).strip()

        if (
            "*" in hop_data
            or "Request timed out" in hop_data
        ):
            hops.append(
                {
                    "hop": hop_number,
                    "address": None,
                    "status": "TIMEOUT",
                }
            )
            continue

        address = _extract_ip_address(hop_data)

        if address:
            hops.append(
                {
                    "hop": hop_number,
                    "address": address,
                    "status": "RESPONDED",
                }
            )
        else:
            hops.append(
                {
                    "hop": hop_number,
                    "address": None,
                    "status": "UNKNOWN",
                }
            )

    return {
        "host": host,
        "success": success,
        "hops": hops,
        "hop_count": len(hops),
        "elapsed_ms": round(elapsed_ms, 2),
        "error": None if success else output.strip(),
    }