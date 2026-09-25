from network_diagnostics.collectors.routes import trace_route


def test_trace_route():
    """A reachable destination should produce route information."""
    result = trace_route("example.com", max_hops=10)

    assert result["host"] == "example.com"
    assert result["success"] is True
    assert result["hop_count"] >= 1
    assert isinstance(result["hops"], list)
    assert result["elapsed_ms"] >= 0
    assert result["error"] is None


def test_trace_route_hops_have_expected_fields():
    """Each discovered hop should contain the expected fields."""
    result = trace_route("example.com", max_hops=10)

    for hop in result["hops"]:
        assert "hop" in hop
        assert "address" in hop
        assert "status" in hop

        assert isinstance(hop["hop"], int)
        assert hop["hop"] >= 1

        assert hop["status"] in {
            "RESPONDED",
            "TIMEOUT",
            "UNKNOWN",
        }


def test_trace_route_empty_host():
    """An empty host should be rejected."""
    try:
        trace_route("")
    except ValueError as error:
        assert str(error) == "Host must not be empty."
    else:
        raise AssertionError("Expected ValueError was not raised.")


def test_trace_route_invalid_max_hops():
    """Maximum hops must be at least one."""
    try:
        trace_route("example.com", max_hops=0)
    except ValueError as error:
        assert str(error) == "Maximum hops must be at least 1."
    else:
        raise AssertionError("Expected ValueError was not raised.")