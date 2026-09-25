
"""Network traffic monitoring."""

from __future__ import annotations

import time

import psutil


def get_network_traffic() -> list[dict]:
    """Collect network traffic counters for each interface."""
    counters = psutil.net_io_counters(pernic=True)

    results = []

    for interface, data in counters.items():
        results.append(
            {
                "interface": interface,
                "bytes_sent": data.bytes_sent,
                "bytes_received": data.bytes_recv,
                "packets_sent": data.packets_sent,
                "packets_received": data.packets_recv,
                "errors_in": data.errin,
                "errors_out": data.errout,
                "drops_in": data.dropin,
                "drops_out": data.dropout,
            }
        )

    return results


def measure_traffic_rate(
    interval: float = 1.0,
) -> list[dict]:
    """Measure network traffic rates over a time interval."""
    if interval <= 0:
        raise ValueError("Interval must be greater than 0.")

    before = psutil.net_io_counters(pernic=True)

    time.sleep(interval)

    after = psutil.net_io_counters(pernic=True)

    results = []

    for interface, current in after.items():
        previous = before.get(interface)

        if previous is None:
            continue

        bytes_sent_per_second = (
            current.bytes_sent - previous.bytes_sent
        ) / interval

        bytes_received_per_second = (
            current.bytes_recv - previous.bytes_recv
        ) / interval

        results.append(
            {
                "interface": interface,
                "bytes_sent_per_second": round(
                    max(0, bytes_sent_per_second),
                    2,
                ),
                "bytes_received_per_second": round(
                    max(0, bytes_received_per_second),
                    2,
                ),
            }
        )

    return results


def monitor_traffic(
    interval: float = 2.0,
    iterations: int | None = None,
):
    """Continuously monitor network traffic."""
    if interval <= 0:
        raise ValueError("Interval must be greater than 0.")

    if iterations is not None and iterations < 1:
        raise ValueError("Iterations must be at least 1.")

    def generate_results():
        """Generate timestamped traffic measurements."""
        completed = 0

        while iterations is None or completed < iterations:
            timestamp = time.strftime("%H:%M:%S")

            rates = measure_traffic_rate(
                interval=interval,
            )

            yield {
                "timestamp": timestamp,
                "interfaces": rates,
            }

            completed += 1

    return generate_results()