"""Network connectivity diagnostics."""

from __future__ import annotations

import platform
import re
import subprocess
import time


def ping_host(host: str, count: int = 4) -> dict:
    """Test host reachability and measure response latency."""
    if count < 1:
        raise ValueError("Ping count must be at least 1.")

    command = ["ping"]

    if platform.system().lower() == "windows":
        command.extend(["-n", str(count)])
    else:
        command.extend(["-c", str(count)])

    command.append(host)

    start_time = time.perf_counter()

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        timeout=max(10, count * 3),
    )

    elapsed_ms = (time.perf_counter() - start_time) * 1000
    output = result.stdout + result.stderr

    latency_values = [
        float(value)
        for value in re.findall(
            r"time[=<]\s*(\d+(?:\.\d+)?)\s*ms",
            output,
            flags=re.IGNORECASE,
        )
    ]

    destination_match = re.search(
        r"Pinging\s+\S+\s+\[([^\]]+)\]",
        output,
        flags=re.IGNORECASE,
    )

    if destination_match:
        destination_ip = destination_match.group(1)
    elif host in {"127.0.0.1", "localhost", "::1"}:
        destination_ip = host
    else:
        destination_ip = None


    successful = len(latency_values)
    failed = count - successful
    packet_loss = (failed / count) * 100

    return {
        "host": host,
        "destination_ip": destination_ip,
        "success": result.returncode == 0,
        "attempts": count,
        "successful": successful,
        "failed": failed,
        "packet_loss_percent": round(packet_loss, 2),
        "min_latency_ms": (
            round(min(latency_values), 2)
            if latency_values
            else None
        ),
        "max_latency_ms": (
            round(max(latency_values), 2)
            if latency_values
            else None
        ),
        "average_latency_ms": (
            round(sum(latency_values) / len(latency_values), 2)
            if latency_values
            else None
        ),
        "elapsed_ms": round(elapsed_ms, 2),
    }