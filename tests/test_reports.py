import json
from pathlib import Path

import pytest

import network_diagnostics.services.reports as reports


@pytest.fixture
def report_directory():
    """Create an isolated project-local directory for report tests."""
    directory = Path("reports") / "test-output"
    directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    yield directory

    for file in directory.glob("*.json"):
        file.unlink(missing_ok=True)

    try:
        directory.rmdir()
    except OSError:
        pass


def test_save_json_report_creates_file(report_directory: Path):
    """JSON report generation should create the requested file."""
    output_path = report_directory / "diagnostic.json"

    data = {
        "command": "summary",
        "status": "success",
        "interfaces": 3,
    }

    result = reports.save_json_report(
        data,
        output_path,
    )

    assert result == output_path
    assert output_path.exists()
    assert output_path.is_file()


def test_save_json_report_writes_valid_json(
    report_directory: Path,
):
    """Generated reports should contain valid JSON data."""
    output_path = report_directory / "diagnostic.json"

    data = {
        "hostname": "test-host",
        "status": "success",
        "metrics": {
            "latency_ms": 25.5,
        },
    }

    reports.save_json_report(
        data,
        output_path,
    )

    with output_path.open(
        "r",
        encoding="utf-8",
    ) as report_file:
        loaded = json.load(report_file)

    assert loaded == data


def test_save_json_report_rejects_non_dictionary(
    report_directory: Path,
):
    """Report data must be provided as a dictionary."""
    output_path = report_directory / "diagnostic.json"

    with pytest.raises(
        TypeError,
        match="Report data must be a dictionary.",
    ):
        reports.save_json_report(
            ["invalid"],
            output_path,
        )


def test_collect_diagnostic_report(monkeypatch):
    """Complete report collection should aggregate all diagnostics."""
    monkeypatch.setattr(
        reports,
        "get_network_summary",
        lambda: {
            "hostname": "test-host",
            "interface_count": 1,
            "active_interface_count": 1,
            "interfaces": [],
        },
    )

    monkeypatch.setattr(
        reports,
        "get_network_interfaces",
        lambda: [
            {
                "name": "Ethernet",
                "is_up": True,
                "speed_mbps": 1000,
                "mtu": 1500,
                "addresses": [],
                "bytes_sent": 1000,
                "bytes_received": 2000,
            }
        ],
    )

    monkeypatch.setattr(
        reports,
        "ping_host",
        lambda host, count: {
            "host": host,
            "success": True,
            "attempts": count,
            "successful": count,
            "failed": 0,
            "packet_loss_percent": 0.0,
            "average_latency_ms": 20.0,
        },
    )

    monkeypatch.setattr(
        reports,
        "resolve_hostname",
        lambda host: {
            "host": host,
            "success": True,
            "ipv4_addresses": ["192.0.2.1"],
            "ipv6_addresses": [],
            "lookup_time_ms": 10.0,
            "error": None,
        },
    )

    monkeypatch.setattr(
        reports,
        "check_tcp_port",
        lambda host, port, timeout: {
            "host": host,
            "port": port,
            "success": True,
            "latency_ms": 15.0,
            "error": None,
        },
    )

    monkeypatch.setattr(
        reports,
        "trace_route",
        lambda host, max_hops: {
            "host": host,
            "success": True,
            "hops": [
                {
                    "hop": 1,
                    "address": "192.0.2.1",
                    "status": "RESPONDED",
                }
            ],
            "hop_count": 1,
            "elapsed_ms": 100.0,
            "error": None,
        },
    )

    monkeypatch.setattr(
        reports,
        "get_network_traffic",
        lambda: [
            {
                "interface": "Ethernet",
                "bytes_sent": 1000,
                "bytes_received": 2000,
                "packets_sent": 10,
                "packets_received": 20,
                "errors_in": 0,
                "errors_out": 0,
                "drops_in": 0,
                "drops_out": 0,
            }
        ],
    )

    monkeypatch.setattr(
        reports,
        "measure_traffic_rate",
        lambda interval: [
            {
                "interface": "Ethernet",
                "bytes_sent_per_second": 100.0,
                "bytes_received_per_second": 200.0,
            }
        ],
    )

    result = reports.collect_diagnostic_report(
        host="example.com",
        port=443,
        ping_count=2,
        timeout=1.0,
        max_hops=5,
        traffic_interval=0.5,
    )

    assert "report" in result
    assert "summary" in result
    assert "interfaces" in result
    assert "connectivity" in result
    assert "dns" in result
    assert "tcp_port" in result
    assert "route" in result
    assert "traffic" in result

    assert result["report"]["target"] == "example.com"
    assert result["report"]["tcp_port"] == 443
    assert result["connectivity"]["successful"] == 2
    assert result["dns"]["success"] is True
    assert result["tcp_port"]["success"] is True
    assert result["route"]["hop_count"] == 1
    assert result["traffic"]["measurement_interval_seconds"] == 0.5


def test_collect_diagnostic_report_rejects_invalid_host():
    """Report collection should reject an empty target host."""
    with pytest.raises(
        ValueError,
        match="Host must not be empty.",
    ):
        reports.collect_diagnostic_report(
            host="",
        )


def test_collect_diagnostic_report_rejects_invalid_port():
    """Report collection should reject an invalid TCP port."""
    with pytest.raises(
        ValueError,
        match="Port must be between 1 and 65535.",
    ):
        reports.collect_diagnostic_report(
            port=70000,
        )


def test_create_timestamped_report_path():
    """Timestamped report paths should use the reports directory."""
    path = reports.create_timestamped_report_path()

    assert path.parent == Path("reports")
    assert path.name.startswith("network-diagnostic-")
    assert path.suffix == ".json"