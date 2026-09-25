from network_diagnostics import main


def test_build_parser_registers_all_commands():
    """CLI parser should register the CLI command group."""
    parser = main.build_parser()

    subparser_action = next(
        action
        for action in parser._actions
        if action.dest == "command"
    )

    assert set(subparser_action.choices) == {
        "interfaces",
        "ping",
        "dns",
        "port",
        "route",
        "summary",
        "traffic",
        "report",
    }


def test_report_command_arguments():
    """Report command should expose its diagnostic options."""
    parser = main.build_parser()

    args = parser.parse_args(
        [
            "report",
            "example.com",
            "--port",
            "443",
            "--count",
            "2",
            "--timeout",
            "1",
            "--max-hops",
            "5",
            "--interval",
            "0.5",
            "--output-dir",
            "test-reports",
        ]
    )

    assert args.command == "report"
    assert args.host == "example.com"
    assert args.port == 443
    assert args.count == 2
    assert args.timeout == 1
    assert args.max_hops == 5
    assert args.interval == 0.5
    assert args.output_dir == "test-reports"


def test_traffic_watch_arguments():
    """Traffic command should support continuous monitoring options."""
    parser = main.build_parser()

    args = parser.parse_args(
        [
            "traffic",
            "--watch",
            "--interval",
            "2",
        ]
    )

    assert args.command == "traffic"
    assert args.watch is True
    assert args.interval == 2


def test_mask_address_ipv4():
    """IPv4 addresses should be masked for terminal display."""
    assert main.mask_address(
        "192.168.1.25",
    ) == "192.168.x.x"


def test_mask_address_ipv6():
    """IPv6 addresses should be masked for terminal display."""
    result = main.mask_address(
        "2606:4700:10::1234",
    )

    assert result.startswith("2606:4700:10:")
    assert result.endswith(":****")


def test_mask_address_mac():
    """MAC addresses should be partially masked."""
    result = main.mask_address(
        "78-04-AB-CD-EF-12",
    )

    assert result == "78-04-**-**-**-**-**"


def test_mask_hostname():
    """Local hostnames should be partially masked."""
    assert main.mask_hostname(
        "GROUP56-021",
    ) == "GROUP56-***"


def test_format_bytes():
    """Byte formatting should produce readable units."""
    assert main.format_bytes(512) == "512.00 B"
    assert main.format_bytes(1024) == "1.00 KB"
    assert main.format_bytes(
        1024 * 1024,
    ) == "1.00 MB"


def test_display_connectivity_masks_destination_ip(
    monkeypatch,
    capsys,
):
    """Connectivity output should mask the resolved destination IP."""
    monkeypatch.setattr(
        main,
        "ping_host",
        lambda host, count: {
            "host": host,
            "destination_ip": "192.168.1.25",
            "attempts": count,
            "successful": count,
            "failed": 0,
            "packet_loss_percent": 0.0,
            "min_latency_ms": 10.0,
            "max_latency_ms": 20.0,
            "average_latency_ms": 15.0,
            "elapsed_ms": 100.0,
        },
    )

    main.display_connectivity(
        "example.com",
        count=2,
    )

    output = capsys.readouterr().out

    assert "Resolved IP     : 192.168.x.x" in output
    assert "192.168.1.25" not in output