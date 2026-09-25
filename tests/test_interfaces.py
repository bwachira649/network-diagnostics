from network_diagnostics.collectors.interfaces import get_network_interfaces


def test_get_network_interfaces_returns_list():
    """Network interface discovery should return a list."""
    result = get_network_interfaces()

    assert isinstance(result, list)


def test_network_interfaces_have_expected_fields():
    """Each discovered interface should contain the expected fields."""
    result = get_network_interfaces()

    for interface in result:
        assert "name" in interface
        assert "is_up" in interface
        assert "speed_mbps" in interface
        assert "mtu" in interface
        assert "addresses" in interface
        assert "bytes_sent" in interface
        assert "bytes_received" in interface