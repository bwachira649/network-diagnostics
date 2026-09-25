
from network_diagnostics.collectors.traffic import (
    get_network_traffic,
    measure_traffic_rate,
    monitor_traffic,
)


def test_get_network_traffic_returns_list():
    """Network traffic collection should return a list."""
    result = get_network_traffic()

    assert isinstance(result, list)


def test_network_traffic_has_expected_fields():
    """Each traffic record should contain expected counters."""
    result = get_network_traffic()

    for interface in result:
        assert "interface" in interface
        assert "bytes_sent" in interface
        assert "bytes_received" in interface
        assert "packets_sent" in interface
        assert "packets_received" in interface
        assert "errors_in" in interface
        assert "errors_out" in interface
        assert "drops_in" in interface
        assert "drops_out" in interface

        assert interface["bytes_sent"] >= 0
        assert interface["bytes_received"] >= 0
        assert interface["packets_sent"] >= 0
        assert interface["packets_received"] >= 0


def test_measure_traffic_rate():
    """Traffic-rate measurement should return structured results."""
    result = measure_traffic_rate(interval=0.1)

    assert isinstance(result, list)

    for interface in result:
        assert "interface" in interface
        assert "bytes_sent_per_second" in interface
        assert "bytes_received_per_second" in interface

        assert interface["bytes_sent_per_second"] >= 0
        assert interface["bytes_received_per_second"] >= 0


def test_measure_traffic_rate_invalid_interval():
    """Traffic-rate interval must be positive."""
    try:
        measure_traffic_rate(interval=0)
    except ValueError as error:
        assert str(error) == "Interval must be greater than 0."
    else:
        raise AssertionError("Expected ValueError was not raised.")


def test_monitor_traffic():
    """Continuous monitoring should produce timestamped results."""
    monitor = monitor_traffic(
        interval=0.1,
        iterations=2,
    )

    results = list(monitor)

    assert len(results) == 2

    for result in results:
        assert "timestamp" in result
        assert "interfaces" in result
        assert isinstance(result["timestamp"], str)
        assert isinstance(result["interfaces"], list)


def test_monitor_traffic_invalid_interval():
    """Monitoring interval must be positive."""
    try:
        monitor_traffic(interval=0)
    except ValueError as error:
        assert str(error) == "Interval must be greater than 0."
    else:
        raise AssertionError("Expected ValueError was not raised.")


def test_monitor_traffic_invalid_iterations():
    """Monitoring iterations must be positive."""
    try:
        monitor_traffic(
            interval=0.1,
            iterations=0,
        )
    except ValueError as error:
        assert str(error) == "Iterations must be at least 1."
    else:
        raise AssertionError("Expected ValueError was not raised.")