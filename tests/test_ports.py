from network_diagnostics.collectors.ports import check_tcp_port


def test_check_tcp_port():
    """A reachable TCP service should be detected."""
    result = check_tcp_port("example.com", 443)

    assert result["host"] == "example.com"
    assert result["port"] == 443
    assert result["success"] is True
    assert result["destination_ip"] is not None
    assert result["latency_ms"] >= 0
    assert result["error"] is None


def test_check_invalid_port():
    """Ports outside the valid TCP range should be rejected."""
    try:
        check_tcp_port("example.com", 0)
    except ValueError as error:
        assert str(error) == "Port must be between 1 and 65535."
    else:
        raise AssertionError("Expected ValueError was not raised.")


def test_check_port_above_range():
    """Ports above 65535 should be rejected."""
    try:
        check_tcp_port("example.com", 65536)
    except ValueError as error:
        assert str(error) == "Port must be between 1 and 65535."
    else:
        raise AssertionError("Expected ValueError was not raised.")


def test_check_empty_host():
    """An empty host should be rejected."""
    try:
        check_tcp_port("", 443)
    except ValueError as error:
        assert str(error) == "Host must not be empty."
    else:
        raise AssertionError("Expected ValueError was not raised.")


def test_check_invalid_timeout():
    """A non-positive timeout should be rejected."""
    try:
        check_tcp_port("example.com", 443, timeout=0)
    except ValueError as error:
        assert str(error) == "Timeout must be greater than 0."
    else:
        raise AssertionError("Expected ValueError was not raised.")