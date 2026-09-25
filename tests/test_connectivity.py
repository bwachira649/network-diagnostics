from network_diagnostics.collectors.connectivity import ping_host


def test_ping_localhost():
    """Localhost should be reachable."""
    result = ping_host("127.0.0.1", count=2)

    assert result["host"] == "127.0.0.1"
    assert result["attempts"] == 2
    assert result["successful"] >= 1
    assert result["packet_loss_percent"] < 100


def test_ping_invalid_count():
    """Ping count must be positive."""
    try:
        ping_host("127.0.0.1", count=0)
    except ValueError as error:
        assert str(error) == "Ping count must be at least 1."
    else:
        raise AssertionError("Expected ValueError was not raised.")