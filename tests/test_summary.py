from network_diagnostics.collectors.summary import get_network_summary


def test_get_network_summary():
    """Network summary should contain the expected system fields."""
    result = get_network_summary()

    assert isinstance(result, dict)
    assert result["hostname"]
    assert result["operating_system"]
    assert result["os_release"]
    assert result["platform"]

    assert isinstance(result["interface_count"], int)
    assert result["interface_count"] >= 0

    assert isinstance(result["active_interface_count"], int)
    assert result["active_interface_count"] >= 0

    assert (
        result["active_interface_count"]
        <= result["interface_count"]
    )


def test_network_summary_interfaces():
    """Network summary should include structured interface data."""
    result = get_network_summary()

    assert isinstance(result["interfaces"], list)

    for interface in result["interfaces"]:
        assert "name" in interface
        assert "is_up" in interface
        assert "speed_mbps" in interface
        assert "mtu" in interface
        assert "addresses" in interface
        assert "bytes_sent" in interface
        assert "bytes_received" in interface