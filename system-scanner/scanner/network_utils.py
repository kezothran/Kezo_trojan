"""
Network utility helpers: input validation, DNS resolution, service lookup.
"""
from __future__ import annotations

import re
import socket
import ipaddress
from scanner.constants import COMMON_SERVICES, MIN_PORT, MAX_PORT


def validate_target(target: str) -> tuple[bool, str]:
    """
    Validate a scan target string.
    Returns (is_valid, cleaned_target_or_error_message).
    """
    target = target.strip()
    if not target:
        return False, "Target cannot be empty."

    # Check for CIDR notation (e.g. 192.168.1.0/24)
    if "/" in target:
        try:
            network = ipaddress.ip_network(target, strict=False)
            if network.num_addresses > 256:
                return False, "Subnet too large. Max /24 (256 hosts) supported."
            return True, target
        except ValueError:
            return False, f"Invalid subnet: {target}"

    # Check for IP address
    try:
        ipaddress.ip_address(target)
        return True, target
    except ValueError:
        pass

    # Check for valid hostname
    hostname_re = re.compile(
        r"^(?!-)[A-Za-z0-9-]{1,63}(?<!-)(\.[A-Za-z0-9-]{1,63})*$"
    )
    if hostname_re.match(target) or target == "localhost":
        return True, target

    return False, f"Invalid target: {target}"


def resolve_host(host: str) -> tuple[bool, str]:
    """Resolve a hostname to an IP. Returns (success, ip_or_error)."""
    try:
        ip = socket.gethostbyname(host)
        return True, ip
    except socket.gaierror as e:
        return False, f"DNS resolution failed for {host}: {e}"


def expand_targets(target: str) -> list[str]:
    """Expand a target string into a list of individual host IPs."""
    target = target.strip()

    # CIDR subnet
    if "/" in target:
        try:
            network = ipaddress.ip_network(target, strict=False)
            return [str(h) for h in network.hosts()]
        except ValueError:
            return []

    # Single host
    return [target]


def parse_port_range(port_str: str) -> tuple[bool, list[int] | str]:
    """
    Parse a port range string like '80', '20-100', '22,80,443', '1-1024'.
    Returns (is_valid, list_of_ports_or_error).
    """
    port_str = port_str.strip()
    if not port_str:
        return False, "Port range cannot be empty."

    ports = set()

    for part in port_str.split(","):
        part = part.strip()
        if "-" in part:
            pieces = part.split("-", 1)
            try:
                start = int(pieces[0].strip())
                end = int(pieces[1].strip())
            except ValueError:
                return False, f"Invalid port range: {part}"
            if start > end:
                return False, f"Start port {start} > end port {end}."
            if start < MIN_PORT or end > MAX_PORT:
                return False, f"Ports must be between {MIN_PORT} and {MAX_PORT}."
            if (end - start) > 10000:
                return False, "Port range too large. Max 10000 ports per range."
            ports.update(range(start, end + 1))
        else:
            try:
                p = int(part)
            except ValueError:
                return False, f"Invalid port number: {part}"
            if p < MIN_PORT or p > MAX_PORT:
                return False, f"Port {p} out of range ({MIN_PORT}-{MAX_PORT})."
            ports.add(p)

    return True, sorted(ports)


def guess_service(port: int) -> str:
    """Return a service name guess for a port number."""
    return COMMON_SERVICES.get(port, "Unknown")


def check_tcp_port(host: str, port: int, timeout: float) -> bool:
    """Try to connect to a TCP port. Returns True if open."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(timeout)
            result = sock.connect_ex((host, port))
            return result == 0
    except (socket.timeout, socket.error, OSError):
        return False
