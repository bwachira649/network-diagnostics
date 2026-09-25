# Network Diagnostics & Monitoring Suite

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![Tests](https://img.shields.io/badge/Tests-41%20passed-success.svg)](#testing)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)](#platform-support)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](#license)

A professional cross-platform Python toolkit for network diagnostics, connectivity testing, service reachability analysis, traffic monitoring, and structured diagnostic reporting.

The application provides a unified command-line interface for investigating common network problems without relying on external cloud infrastructure. It combines Python networking APIs, operating-system diagnostic commands, traffic statistics, automated testing, and privacy-aware reporting in a modular application architecture.

---

## Overview

**Network Diagnostics & Monitoring Suite** is a practical network troubleshooting utility for investigating connectivity, DNS, TCP service, routing, and traffic-related issues.

The toolkit provides a single command-line interface for performing common network diagnostic operations and consolidating results into structured reports.

It can:

* Inspect local network interfaces
* Test network reachability and latency
* Resolve DNS hostnames
* Test TCP service availability
* Trace network paths
* Monitor network traffic
* Measure traffic rates over configurable intervals
* Generate consolidated JSON diagnostic reports
* Handle common network and command-execution failures
* Mask sensitive network information for safer sharing
* Validate core functionality through automated tests

The project follows a modular architecture that separates diagnostic collectors, reporting services, CLI functionality, and automated tests.

---

## Key Capabilities

### Network Interface Diagnostics

Discovers local network interfaces and reports:

* Interface status
* Link speed
* MTU
* Network addresses
* Traffic counters
* Packet statistics

### Connectivity Diagnostics

Tests destination reachability using platform-aware ICMP ping commands and reports:

* Successful attempts
* Failed attempts
* Packet loss
* Minimum latency
* Maximum latency
* Average latency
* Diagnostic execution time

### DNS Diagnostics

Resolves hostnames and reports:

* IPv4 addresses
* IPv6 addresses
* Lookup duration
* Resolution failures

### TCP Port Diagnostics

Tests TCP service reachability and provides:

* Destination resolution
* TCP port status
* Connection latency
* Connection failure classification
* DNS resolution error handling
* Timeout handling
* Network and host unreachable handling

### Route Diagnostics

Inspects the network path to a destination using platform-specific route tracing commands and records:

* Hop numbers
* Responding addresses
* Timeout hops
* Route completion status
* Diagnostic duration

### Network Traffic Monitoring

Collects per-interface network statistics including:

* Bytes sent
* Bytes received
* Packets sent
* Packets received
* Input/output errors
* Input/output drops

The toolkit also supports continuous traffic monitoring with configurable measurement intervals.

### Diagnostic Reporting

The reporting service combines multiple diagnostic sources into a structured JSON report containing:

* Network environment summary
* Interface information
* Connectivity results
* DNS results
* TCP port results
* Route diagnostics
* Traffic counters
* Traffic-rate measurements
* Report metadata

Reports use timestamped filenames for easier identification and archival.

---

## Privacy & Safe Sharing

Network diagnostic output can contain information that should not be publicly exposed.

The application therefore includes privacy-aware output handling that masks network information before it is displayed through supported CLI views or included in sanitized diagnostic reports.

For example:

```text
192.168.1.25
```

is displayed as:

```text
192.168.x.x
```

MAC addresses and IPv6 addresses are also partially masked.

Diagnostic reports include a privacy notice indicating that network addresses have been masked for safer sharing.

> Privacy masking is intended to reduce accidental exposure when sharing diagnostic evidence. It should not be treated as a complete security or anonymization mechanism.

---

## Project Demonstration

The project includes visual evidence captured during development and testing.

### Complete Network Diagnostic Report

![Network Diagnostic Report](docs/images/network-diagnostic-report.png)

### Network Environment Summary

![Network Environment Summary](docs/images/network-environment-summary.png)

### Network Interface Discovery

![Network Interface Discovery](docs/images/network-interface-discovery.png)

### Connectivity Diagnostics

![Connectivity Diagnostic](docs/images/connectivity-diagnostic.png)

### DNS Resolution

**Successful resolution:**

![DNS Resolution Success](docs/images/dns-resolution-success.png)

**Failed resolution:**

![DNS Resolution Failure](docs/images/dns-resolution-failure.png)

### TCP Port Diagnostics

**Reachable service:**

![TCP Port Open](docs/images/tcp-port-open.png)

**Unreachable service:**

![TCP Port Unreachable](docs/images/tcp-port-unreachable.png)

### Route Diagnostics

![Network Route Diagnostic](docs/images/network-route-diagnostic.png)

### Network Traffic Monitoring

**Single traffic measurement:**

![Network Traffic Monitor](docs/images/network-traffic-monitor.png)

**Continuous traffic monitoring:**

![Network Traffic Watch](docs/images/network-traffic-watch.png)

### Automated Testing

**CLI tests:**

![CLI Tests](docs/images/tests-cli.png)

**Network interface tests:**

![Interface Tests](docs/images/tests-interface-discovery.png)

---

## Video Demonstrations

### Complete Diagnostic Report

[▶ View the Network Diagnostic Report demonstration](docs/videos/network-diagnostic-report.mp4)

Demonstrates the complete diagnostic reporting workflow and generated results.

### Continuous Traffic Monitoring

[▶ View the Network Traffic Monitoring demonstration](docs/videos/network-traffic-watch.mp4)

Demonstrates real-time traffic-rate monitoring across network interfaces.

---

## CLI Usage

The application provides a command-oriented interface for common network troubleshooting operations.

### Display Network Interfaces

```cmd
python -m network_diagnostics.main interfaces
```

Displays detected interfaces, operational status, link speed, MTU, addresses, and traffic counters.

### Test Connectivity

```cmd
python -m network_diagnostics.main ping example.com
```

Tests reachability and reports packet loss and latency measurements.

### Resolve DNS

```cmd
python -m network_diagnostics.main dns example.com
```

Performs hostname resolution and reports IPv4/IPv6 results and lookup timing.

### Test a TCP Port

```cmd
python -m network_diagnostics.main port example.com 443
```

Tests TCP connectivity to the specified service port.

### Trace a Network Route

```cmd
python -m network_diagnostics.main route example.com
```

Inspects the network path toward the destination.

### Display Network Summary

```cmd
python -m network_diagnostics.main summary
```

Displays a high-level summary of the local network environment.

### Monitor Network Traffic

```cmd
python -m network_diagnostics.main traffic
```

Displays current network traffic counters.

For continuous monitoring:

```cmd
python -m network_diagnostics.main traffic --watch --interval 2
```

The interval can be adjusted according to the required monitoring frequency.

### Generate a Diagnostic Report

```cmd
python -m network_diagnostics.main report example.com
```

Generates a consolidated timestamped JSON diagnostic report.

The report command supports configurable options for:

* TCP port
* Ping count
* Connection timeout
* Maximum route hops
* Traffic measurement interval
* Report output directory

Example:

```cmd
python -m network_diagnostics.main report example.com --port 443 --count 4 --timeout 3 --max-hops 12 --interval 1
```

---

## Project Structure

```text
network-diagnostics/
├── config/
├── docs/
│   ├── images/
│   └── videos/
├── logs/
├── reports/
├── src/
│   └── network_diagnostics/
│       ├── collectors/
│       │   ├── connectivity.py
│       │   ├── dns.py
│       │   ├── interfaces.py
│       │   ├── ports.py
│       │   ├── routes.py
│       │   ├── summary.py
│       │   └── traffic.py
│       ├── services/
│       │   └── reports.py
│       ├── utils/
│       ├── config.py
│       ├── main.py
│       └── __init__.py
├── tests/
│   ├── test_connectivity.py
│   ├── test_dns.py
│   ├── test_interfaces.py
│   ├── test_main.py
│   ├── test_ports.py
│   ├── test_reports.py
│   ├── test_routes.py
│   ├── test_summary.py
│   └── test_traffic.py
├── .gitignore
├── LICENSE
├── pyproject.toml
├── requirements.txt
└── README.md
```

---

## Technology Stack

| Technology   | Purpose                                  |
| ------------ | ---------------------------------------- |
| Python 3.11+ | Application development                  |
| psutil       | Network interface and traffic statistics |
| socket       | DNS resolution and TCP networking        |
| subprocess   | Platform-specific network diagnostics    |
| argparse     | Command-line interface                   |
| JSON         | Structured diagnostic reports            |
| pytest       | Automated testing                        |
| Git          | Version control                          |
| GitHub       | Source control and project delivery      |

---

## Installation

### Windows

```cmd
git clone https://github.com/bwachira649/network-diagnostics.git
cd network-diagnostics
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install -e .
```

### Linux

```bash
git clone https://github.com/bwachira649/network-diagnostics.git
cd network-diagnostics
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install -e .
```

### macOS

```bash
git clone https://github.com/bwachira649/network-diagnostics.git
cd network-diagnostics
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install -e .
```

---

## Testing

Run the complete automated test suite:

```cmd
python -m pytest
```

### Windows Verification

The current Windows build has been validated with:

```text
41 passed in 20.95s
```

Test coverage includes:

* Connectivity diagnostics
* DNS resolution
* Network interface discovery
* CLI parsing and arguments
* Privacy masking
* TCP port diagnostics
* Report generation
* Route diagnostics
* Network summaries
* Traffic measurement
* Continuous traffic monitoring
* Input validation
* Error handling
* Test isolation and mocking

---

## Practical Skills Demonstrated

This project demonstrates practical experience with:

* Python application architecture
* Modular package design
* Network programming
* Socket programming
* DNS diagnostics
* TCP connectivity testing
* ICMP-based connectivity testing
* Network route analysis
* Network interface monitoring
* Network traffic measurement
* Platform-aware command execution
* Cross-platform application design
* CLI application development
* Structured JSON reporting
* Input validation
* Error handling
* Privacy-aware diagnostic output
* Automated testing with pytest
* Test isolation and mocking
* Git version control
* Technical documentation
* Evidence-driven software demonstration

---

## Development Workflow

The project was developed using an evidence-driven workflow:

```text
Build
  ↓
Test
  ↓
Capture Evidence
  ↓
Document
  ↓
Demonstrate
  ↓
Verify
  ↓
Publish
```

This workflow ensures that the project includes both functional implementation and visible evidence of testing and practical operation.

---

## Platform Support

### Windows

Primary development and testing platform.

Verified environment:

```text
Windows 11
Python 3.14.7
pytest 9.1.1
psutil 7.2.2
41 automated tests passing
```

### Linux

The application is designed for Linux using platform-aware diagnostic command handling.

Linux verification is the next cross-platform validation step.

### macOS

The application architecture uses Python standard-library networking functionality and platform-aware command handling.

macOS support is intended where the required system diagnostic commands are available.

---

## Project Status

### Windows Development

**Complete**

The Windows implementation has passed the complete automated test suite:

```text
41 passed
```

### Linux Verification

**Pending**

The project will be executed and validated on Linux as the next cross-platform verification stage.

### GitHub Release

**Pending**

The repository will be published after final documentation review and Linux verification.

---

## License

This project is released under the MIT License.

See the [LICENSE](LICENSE) file for the full license text.
