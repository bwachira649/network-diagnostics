"""Diagnostic report generation services."""

from __future__ import annotations

import ipaddress
import json
from datetime import datetime
from pathlib import Path
from typing import Any

from network_diagnostics.collectors.connectivity import ping_host
from network_diagnostics.collectors.dns import resolve_hostname
from network_diagnostics.collectors.interfaces import get_network_interfaces
from network_diagnostics.collectors.ports import check_tcp_port
from network_diagnostics.collectors.routes import trace_route
from network_diagnostics.collectors.summary import get_network_summary
from network_diagnostics.collectors.traffic import (
    get_network_traffic,
    measure_traffic_rate,
)


def _mask_address(address: str | None) -> str | None:
    """Mask an IP or MAC address for safe report sharing."""
    if not address:
        return address

    try:
        parsed = ipaddress.ip_address(address)

        if parsed.version == 4:
            octets = address.split(".")

            if len(octets) == 4:
                return ".".join(octets[:2]) + ".x.x"

        if parsed.version == 6:
            parts = address.split(":")

            if len(parts) > 3:
                return ":".join(parts[:4]) + ":****"

    except ValueError:
        pass

    if "-" in address and len(address) >= 17:
        return address[:5] + "-**-**-**-**-**"

    return address


def _sanitize_interface(interface: dict[str, Any]) -> dict[str, Any]:
    """Create a privacy-safe copy of interface diagnostic data."""
    sanitized = dict(interface)

    sanitized["addresses"] = [
        {
            **address,
            "address": _mask_address(address.get("address")),
            "netmask": _mask_address(address.get("netmask")),
            "broadcast": _mask_address(address.get("broadcast")),
        }
        for address in interface.get("addresses", [])
    ]

    return sanitized


def _sanitize_interfaces(
    interfaces: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Sanitize a collection of network interfaces."""
    return [
        _sanitize_interface(interface)
        for interface in interfaces
    ]


def _sanitize_summary(summary: dict[str, Any]) -> dict[str, Any]:
    """Create a privacy-safe copy of network summary data."""
    sanitized = dict(summary)

    sanitized["interfaces"] = _sanitize_interfaces(
        summary.get("interfaces", [])
    )

    return sanitized


def _sanitize_connectivity(
    connectivity: dict[str, Any],
) -> dict[str, Any]:
    """Create a privacy-safe copy of connectivity results."""
    sanitized = dict(connectivity)

    sanitized["destination_ip"] = _mask_address(
        connectivity.get("destination_ip"),
    )

    return sanitized


def _sanitize_dns(dns: dict[str, Any]) -> dict[str, Any]:
    """Create a privacy-safe copy of DNS results."""
    sanitized = dict(dns)

    sanitized["ipv4_addresses"] = [
        _mask_address(address)
        for address in dns.get("ipv4_addresses", [])
    ]

    sanitized["ipv6_addresses"] = [
        _mask_address(address)
        for address in dns.get("ipv6_addresses", [])
    ]

    return sanitized


def _sanitize_port_result(
    port_result: dict[str, Any],
) -> dict[str, Any]:
    """Create a privacy-safe copy of TCP port results."""
    sanitized = dict(port_result)

    sanitized["destination_ip"] = _mask_address(
        port_result.get("destination_ip"),
    )

    return sanitized


def _sanitize_route(route: dict[str, Any]) -> dict[str, Any]:
    """Create a privacy-safe copy of route diagnostic data."""
    sanitized = dict(route)
    sanitized["hops"] = []

    for hop in route.get("hops", []):
        sanitized_hop = dict(hop)
        sanitized_hop["address"] = _mask_address(
            hop.get("address"),
        )
        sanitized["hops"].append(sanitized_hop)

    return sanitized


def save_json_report(
    data: dict[str, Any],
    output_path: str | Path,
) -> Path:
    """Save diagnostic data as a formatted JSON report."""
    if not isinstance(data, dict):
        raise TypeError("Report data must be a dictionary.")

    path = Path(output_path)

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with path.open(
        "w",
        encoding="utf-8",
    ) as report_file:
        json.dump(
            data,
            report_file,
            indent=4,
            sort_keys=True,
        )

        report_file.write("\n")

    return path


def collect_diagnostic_report(
    host: str = "example.com",
    port: int = 443,
    ping_count: int = 4,
    timeout: float = 3.0,
    max_hops: int = 12,
    traffic_interval: float = 1.0,
) -> dict[str, Any]:
    """Collect a complete privacy-safe network diagnostic report."""
    if not host.strip():
        raise ValueError("Host must not be empty.")

    if not 1 <= port <= 65535:
        raise ValueError("Port must be between 1 and 65535.")

    if ping_count < 1:
        raise ValueError("Ping count must be at least 1.")

    if timeout <= 0:
        raise ValueError("Timeout must be greater than 0.")

    if max_hops < 1:
        raise ValueError("Maximum hops must be at least 1.")

    if traffic_interval <= 0:
        raise ValueError(
            "Traffic interval must be greater than 0."
        )

    generated_at = datetime.now().astimezone().isoformat(
        timespec="seconds",
    )

    summary = get_network_summary()
    interfaces = get_network_interfaces()
    connectivity = ping_host(
        host,
        count=ping_count,
    )
    dns = resolve_hostname(host)
    port_result = check_tcp_port(
        host,
        port,
        timeout=timeout,
    )
    route = trace_route(
        host,
        max_hops=max_hops,
    )
    traffic = get_network_traffic()
    traffic_rates = measure_traffic_rate(
        interval=traffic_interval,
    )

    return {
        "report": {
            "generated_at": generated_at,
            "target": host,
            "tcp_port": port,
            "privacy": (
                "Network addresses are masked for safe sharing."
            ),
        },
        "summary": _sanitize_summary(summary),
        "interfaces": _sanitize_interfaces(interfaces),
        "connectivity": _sanitize_connectivity(connectivity),
        "dns": _sanitize_dns(dns),
        "tcp_port": _sanitize_port_result(port_result),
        "route": _sanitize_route(route),
        "traffic": {
            "counters": traffic,
            "rates": traffic_rates,
            "measurement_interval_seconds": traffic_interval,
        },
    }


def create_timestamped_report_path(
    output_directory: str | Path = "reports",
) -> Path:
    """Create a timestamped JSON report path."""
    timestamp = datetime.now().strftime(
        "%Y%m%d-%H%M%S",
    )

    return Path(output_directory) / (
        f"network-diagnostic-{timestamp}.json"
    )