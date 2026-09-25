from network_diagnostics.collectors.dns import resolve_hostname


def test_resolve_hostname():
    """A valid hostname should resolve successfully."""
    result = resolve_hostname("example.com")

    assert result["host"] == "example.com"
    assert result["success"] is True
    assert result["ipv4_addresses"] or result["ipv6_addresses"]
    assert result["lookup_time_ms"] >= 0
    assert result["error"] is None


def test_resolve_invalid_hostname():
    """An invalid hostname should return a failed diagnostic result."""
    result = resolve_hostname(
        "this-host-does-not-exist.invalid"
    )

    assert result["host"] == "this-host-does-not-exist.invalid"
    assert result["success"] is False
    assert result["ipv4_addresses"] == []
    assert result["ipv6_addresses"] == []
    assert result["error"] is not None


def test_resolve_empty_hostname():
    """An empty hostname should raise a validation error."""
    try:
        resolve_hostname("")
    except ValueError as error:
        assert str(error) == "Hostname must not be empty."
    else:
        raise AssertionError("Expected ValueError was not raised.")
