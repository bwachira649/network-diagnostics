"""Command-line interface for Network Diagnostics."""

from __future__ import annotations

import argparse
import ipaddress

from network_diagnostics.collectors.connectivity import ping_host
from network_diagnostics.collectors.dns import resolve_hostname
from network_diagnostics.collectors.interfaces import get_network_interfaces
from network_diagnostics.collectors.ports import check_tcp_port
from network_diagnostics.collectors.routes import trace_route
from network_diagnostics.collectors.summary import get_network_summary
from network_diagnostics.collectors.traffic import (
    get_network_traffic,
    measure_traffic_rate,
    monitor_traffic,
)
from network_diagnostics.services.reports import (
    collect_diagnostic_report,
    create_timestamped_report_path,
    save_json_report,
)


def mask_address(address: str) -> str:
    """Mask sensitive network addresses for safe terminal display."""
    try:
        parsed = ipaddress.ip_address(address)
    except ValueError:
        parsed = None

    if parsed and parsed.version == 6:
        parts = address.split(":")

        if len(parts) > 3:
            return ":".join(parts[:4]) + ":****"

    if parsed and parsed.version == 4:
        octets = address.split(".")

        if len(octets) == 4:
            return ".".join(octets[:2]) + ".x.x"

    if "-" in address and len(address) >= 17:
        return address[:5] + "-**-**-**-**-**"

    return address


def mask_hostname(hostname: str) -> str:
    """Mask a local hostname for safe terminal display."""
    if not hostname:
        return hostname

    if len(hostname) <= 4:
        return "*" * len(hostname)

    return hostname[:-3] + "***"


def format_bytes(value: float) -> str:
    """Format a byte value using a readable unit."""
    units = ["B", "KB", "MB", "GB", "TB"]

    size = float(value)

    for unit in units:
        if size < 1024 or unit == units[-1]:
            return f"{size:.2f} {unit}"

        size /= 1024

    return f"{size:.2f} TB"


def display_interfaces() -> None:
    """Display local network interface information."""
    interfaces = get_network_interfaces()

    print()
    print("NETWORK INTERFACE DISCOVERY")
    print("=" * 70)
    print(f"Interfaces detected: {len(interfaces)}")

    if not interfaces:
        print("\nNo network interfaces detected.")
        return

    for interface in interfaces:
        status = "UP" if interface["is_up"] else "DOWN"

        print()
        print("-" * 70)
        print(f"Interface : {interface['name']}")
        print(f"Status    : {status}")
        print(f"Speed     : {interface['speed_mbps']} Mbps")
        print(f"MTU       : {interface['mtu']}")
        print(
            f"Traffic   : "
            f"{interface['bytes_received']:,} received / "
            f"{interface['bytes_sent']:,} sent"
        )

        print("Addresses:")

        for address in interface["addresses"]:
            safe_address = mask_address(address["address"])
            print(f"  - {safe_address}")

    print()
    print("=" * 70)


def display_connectivity(host: str, count: int = 4) -> None:
    """Run and display a connectivity diagnostic."""
    result = ping_host(host, count=count)

    print()
    print("CONNECTIVITY DIAGNOSTIC")
    print("=" * 70)
    print(f"Target          : {result['host']}")

    destination_ip = result["destination_ip"]

    print(
        f"Resolved IP     : "
        f"{mask_address(destination_ip) if destination_ip else 'Unknown'}"
    )

    print(f"Attempts        : {result['attempts']}")
    print(f"Successful      : {result['successful']}")
    print(f"Failed          : {result['failed']}")
    print(f"Packet Loss     : {result['packet_loss_percent']:.2f}%")

    if result["average_latency_ms"] is not None:
        print(f"Minimum Latency : {result['min_latency_ms']:.2f} ms")
        print(f"Maximum Latency : {result['max_latency_ms']:.2f} ms")
        print(f"Average Latency : {result['average_latency_ms']:.2f} ms")
    else:
        print("Latency         : No successful responses")

    print(f"Diagnostic Time : {result['elapsed_ms']:.2f} ms")
    print("=" * 70)
    print()


def display_dns(host: str) -> None:
    """Run and display a DNS resolution diagnostic."""
    result = resolve_hostname(host)

    print()
    print("DNS RESOLUTION DIAGNOSTIC")
    print("=" * 70)
    print(f"Hostname        : {result['host']}")
    print(f"Status          : {'SUCCESS' if result['success'] else 'FAILED'}")

    print("IPv4 Addresses  :")
    if result["ipv4_addresses"]:
        for address in result["ipv4_addresses"]:
            print(f"  - {mask_address(address)}")
    else:
        print("  - None")

    print("IPv6 Addresses  :")
    if result["ipv6_addresses"]:
        for address in result["ipv6_addresses"]:
            print(f"  - {mask_address(address)}")
    else:
        print("  - None")

    print(f"Lookup Time     : {result['lookup_time_ms']:.2f} ms")

    if result["error"]:
        print(f"Error           : {result['error']}")

    print("=" * 70)
    print()


def display_port(host: str, port: int, timeout: float = 3.0) -> None:
    """Run and display a TCP port diagnostic."""
    result = check_tcp_port(
        host,
        port,
        timeout=timeout,
    )

    print()
    print("TCP PORT DIAGNOSTIC")
    print("=" * 70)
    print(f"Target          : {result['host']}")

    destination_ip = result["destination_ip"]

    print(
        f"Resolved IP     : "
        f"{mask_address(destination_ip) if destination_ip else 'Unknown'}"
    )

    print(f"Port            : {result['port']}")
    print(f"Status          : {'OPEN' if result['success'] else 'UNREACHABLE'}")
    print(f"Response Time   : {result['latency_ms']:.2f} ms")

    if result["error"]:
        print(f"Error           : {result['error']}")

    print("=" * 70)
    print()


def display_route(host: str, max_hops: int = 12) -> None:
    """Run and display a network route diagnostic."""
    result = trace_route(
        host,
        max_hops=max_hops,
    )

    print()
    print("ROUTE / PATH DIAGNOSTIC")
    print("=" * 70)
    print(f"Target          : {result['host']}")
    print(f"Status          : {'SUCCESS' if result['success'] else 'FAILED'}")
    print(f"Maximum Hops    : {max_hops}")
    print(f"Detected Hops   : {result['hop_count']}")
    print()

    if result["hops"]:
        print(f"{'Hop':<8}{'Status':<14}Address")
        print("-" * 70)

        for hop in result["hops"]:
            if hop["address"]:
                address = mask_address(hop["address"])

                try:
                    address_type = (
                        "IPv6"
                        if ipaddress.ip_address(
                            hop["address"]
                        ).version == 6
                        else "IPv4"
                    )
                except ValueError:
                    address_type = "IP"

                display_address = f"{address_type}: {address}"
            else:
                display_address = "No response"

            print(
                f"{hop['hop']:<8}"
                f"{hop['status']:<14}"
                f"{display_address}"
            )
    else:
        print("No route hops were detected.")

    print()
    print(f"Diagnostic Time : {result['elapsed_ms']:.2f} ms")

    if result["error"]:
        print(f"Error           : {result['error']}")

    print("=" * 70)
    print()


def display_summary() -> None:
    """Display a high-level local network summary."""
    result = get_network_summary()

    print()
    print("NETWORK ENVIRONMENT SUMMARY")
    print("=" * 70)
    print(f"Hostname        : {mask_hostname(result['hostname'])}")
    print(f"Operating System: {result['operating_system']}")
    print(f"OS Release      : {result['os_release']}")
    print(f"Platform        : {result['platform']}")
    print(f"Interfaces      : {result['interface_count']}")
    print(f"Active          : {result['active_interface_count']}")
    print()

    print("INTERFACE OVERVIEW")
    print("-" * 70)

    for interface in result["interfaces"]:
        status = "UP" if interface["is_up"] else "DOWN"

        print(
            f"{interface['name']:<30}"
            f"{status:<8}"
            f"{interface['speed_mbps']} Mbps"
        )

        for address in interface["addresses"]:
            safe_address = mask_address(address["address"])
            print(f"  Address: {safe_address}")

    print("=" * 70)
    print()


def display_traffic(interval: float = 1.0) -> None:
    """Display network traffic counters and measured rates."""
    traffic = get_network_traffic()
    rates = measure_traffic_rate(interval=interval)

    rates_by_interface = {
        item["interface"]: item
        for item in rates
    }

    print()
    print("NETWORK TRAFFIC MONITOR")
    print("=" * 70)
    print(f"Measurement Interval: {interval:.2f} seconds")
    print()

    if not traffic:
        print("No network traffic data available.")
        print("=" * 70)
        print()
        return

    print(
        f"{'Interface':<30}"
        f"{'RX Rate':>14}"
        f"{'TX Rate':>14}"
    )
    print("-" * 70)

    for item in traffic:
        interface = item["interface"]
        rate = rates_by_interface.get(interface)

        if rate:
            rx_rate = format_bytes(
                rate["bytes_received_per_second"]
            )
            tx_rate = format_bytes(
                rate["bytes_sent_per_second"]
            )
        else:
            rx_rate = "N/A"
            tx_rate = "N/A"

        print(
            f"{interface:<30}"
            f"{rx_rate:>14}/s"
            f"{tx_rate:>14}/s"
        )

    print()
    print("TRAFFIC COUNTERS")
    print("-" * 70)

    for item in traffic:
        print()
        print(f"Interface: {item['interface']}")
        print(
            f"  Received : {format_bytes(item['bytes_received'])}"
        )
        print(
            f"  Sent     : {format_bytes(item['bytes_sent'])}"
        )
        print(
            f"  Packets  : "
            f"{item['packets_received']:,} received / "
            f"{item['packets_sent']:,} sent"
        )
        print(
            f"  Errors   : "
            f"{item['errors_in']} inbound / "
            f"{item['errors_out']} outbound"
        )
        print(
            f"  Drops    : "
            f"{item['drops_in']} inbound / "
            f"{item['drops_out']} outbound"
        )

    print("=" * 70)
    print()


def display_traffic_watch(
    interval: float = 2.0,
) -> None:
    """Continuously display network traffic rates."""
    print()
    print("CONTINUOUS NETWORK TRAFFIC MONITOR")
    print("=" * 70)
    print(f"Monitoring interval : {interval:.2f} seconds")
    print("Press Ctrl+C to stop.")
    print()

    print(
        f"{'Time':<10}"
        f"{'Interface':<30}"
        f"{'RX Rate':>14}"
        f"{'TX Rate':>14}"
    )
    print("-" * 70)

    try:
        for measurement in monitor_traffic(
            interval=interval,
        ):
            for item in measurement["interfaces"]:
                rx_rate = format_bytes(
                    item["bytes_received_per_second"]
                )
                tx_rate = format_bytes(
                    item["bytes_sent_per_second"]
                )

                print(
                    f"{measurement['timestamp']:<10}"
                    f"{item['interface']:<30}"
                    f"{rx_rate:>14}/s"
                    f"{tx_rate:>14}/s"
                )

    except KeyboardInterrupt:
        print()
        print()
        print("Monitoring stopped by user.")
        print("=" * 70)
        print()


def display_report(
    host: str = "example.com",
    port: int = 443,
    ping_count: int = 4,
    timeout: float = 3.0,
    max_hops: int = 12,
    traffic_interval: float = 1.0,
    output_directory: str = "reports",
) -> None:
    """Generate and save a complete diagnostic report."""
    print()
    print("GENERATING NETWORK DIAGNOSTIC REPORT")
    print("=" * 70)
    print(f"Target          : {host}")
    print(f"TCP Port        : {port}")
    print(f"Ping Attempts   : {ping_count}")
    print(f"Maximum Hops    : {max_hops}")
    print(
        f"Traffic Interval: "
        f"{traffic_interval:.2f} seconds"
    )
    print()

    print("Collecting diagnostics...")

    report = collect_diagnostic_report(
        host=host,
        port=port,
        ping_count=ping_count,
        timeout=timeout,
        max_hops=max_hops,
        traffic_interval=traffic_interval,
    )

    output_path = create_timestamped_report_path(
        output_directory=output_directory,
    )

    saved_path = save_json_report(
        report,
        output_path,
    )

    print("Report generated successfully.")
    print(f"Output          : {saved_path}")
    print(f"File Size       : {saved_path.stat().st_size:,} bytes")
    print("=" * 70)
    print()


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line argument parser."""
    parser = argparse.ArgumentParser(
        prog="network-diagnostics",
        description=(
            "Professional network diagnostics and monitoring suite."
        ),
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
    )

    subparsers.add_parser(
        "interfaces",
        help="Discover and display local network interfaces.",
    )

    ping_parser = subparsers.add_parser(
        "ping",
        help="Test host reachability and measure latency.",
    )
    ping_parser.add_argument(
        "host",
        help="Hostname or IP address to test.",
    )
    ping_parser.add_argument(
        "-c",
        "--count",
        type=int,
        default=4,
        help="Number of ping attempts (default: 4).",
    )

    dns_parser = subparsers.add_parser(
        "dns",
        help="Resolve a hostname and display DNS information.",
    )
    dns_parser.add_argument(
        "host",
        help="Hostname to resolve.",
    )

    port_parser = subparsers.add_parser(
        "port",
        help="Test TCP port reachability.",
    )
    port_parser.add_argument(
        "host",
        help="Hostname or IP address to test.",
    )
    port_parser.add_argument(
        "port",
        type=int,
        help="TCP port number to test.",
    )
    port_parser.add_argument(
        "-t",
        "--timeout",
        type=float,
        default=3.0,
        help="Connection timeout in seconds (default: 3.0).",
    )

    route_parser = subparsers.add_parser(
        "route",
        help="Trace the network path to a destination.",
    )
    route_parser.add_argument(
        "host",
        help="Hostname or IP address to trace.",
    )
    route_parser.add_argument(
        "-m",
        "--max-hops",
        type=int,
        default=12,
        help="Maximum number of hops (default: 12).",
    )

    subparsers.add_parser(
        "summary",
        help="Display a local network environment summary.",
    )

    traffic_parser = subparsers.add_parser(
        "traffic",
        help="Monitor network traffic and interface counters.",
    )
    traffic_parser.add_argument(
        "-i",
        "--interval",
        type=float,
        default=1.0,
        help="Measurement interval in seconds (default: 1.0).",
    )
    traffic_parser.add_argument(
        "-w",
        "--watch",
        action="store_true",
        help="Continuously monitor traffic until stopped.",
    )

    report_parser = subparsers.add_parser(
        "report",
        help="Generate a complete JSON network diagnostic report.",
    )
    report_parser.add_argument(
        "host",
        nargs="?",
        default="example.com",
        help="Diagnostic target (default: example.com).",
    )
    report_parser.add_argument(
        "-p",
        "--port",
        type=int,
        default=443,
        help="TCP port to test (default: 443).",
    )
    report_parser.add_argument(
        "-c",
        "--count",
        type=int,
        default=4,
        help="Number of ping attempts (default: 4).",
    )
    report_parser.add_argument(
        "-t",
        "--timeout",
        type=float,
        default=3.0,
        help="TCP connection timeout (default: 3.0).",
    )
    report_parser.add_argument(
        "-m",
        "--max-hops",
        type=int,
        default=12,
        help="Maximum route hops (default: 12).",
    )
    report_parser.add_argument(
        "-i",
        "--interval",
        type=float,
        default=1.0,
        help="Traffic measurement interval (default: 1.0).",
    )
    report_parser.add_argument(
        "-o",
        "--output-dir",
        default="reports",
        help="Directory for generated reports (default: reports).",
    )

    return parser


def main() -> None:
    """Parse CLI arguments and execute the selected command."""
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "interfaces":
        display_interfaces()

    elif args.command == "ping":
        if args.count < 1:
            parser.error("Ping count must be at least 1.")

        display_connectivity(
            args.host,
            count=args.count,
        )

    elif args.command == "dns":
        display_dns(args.host)

    elif args.command == "port":
        if not 1 <= args.port <= 65535:
            parser.error("Port must be between 1 and 65535.")

        if args.timeout <= 0:
            parser.error("Timeout must be greater than 0.")

        display_port(
            args.host,
            args.port,
            timeout=args.timeout,
        )

    elif args.command == "route":
        if not args.host.strip():
            parser.error("Route host must not be empty.")

        if args.max_hops < 1:
            parser.error("Maximum hops must be at least 1.")

        display_route(
            args.host,
            max_hops=args.max_hops,
        )

    elif args.command == "summary":
        display_summary()

    elif args.command == "traffic":
        if args.interval <= 0:
            parser.error("Interval must be greater than 0.")

        if args.watch:
            display_traffic_watch(
                interval=args.interval,
            )
        else:
            display_traffic(
                interval=args.interval,
            )

    elif args.command == "report":
        if not 1 <= args.port <= 65535:
            parser.error("Port must be between 1 and 65535.")

        if args.count < 1:
            parser.error("Ping count must be at least 1.")

        if args.timeout <= 0:
            parser.error("Timeout must be greater than 0.")

        if args.max_hops < 1:
            parser.error("Maximum hops must be at least 1.")

        if args.interval <= 0:
            parser.error("Interval must be greater than 0.")

        display_report(
            host=args.host,
            port=args.port,
            ping_count=args.count,
            timeout=args.timeout,
            max_hops=args.max_hops,
            traffic_interval=args.interval,
            output_directory=args.output_dir,
        )


if __name__ == "__main__":
    main()
