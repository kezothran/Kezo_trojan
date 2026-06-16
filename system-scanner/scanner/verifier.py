"""
Verifier: re-checks a specific host:port to confirm it is still open.
"""

from datetime import datetime
from scanner.network_utils import check_tcp_port, resolve_host
from scanner.constants import DEFAULT_TIMEOUT, VERIFIED_YES, VERIFIED_NO


def verify_target(host: str, port: int, timeout: float = DEFAULT_TIMEOUT) -> dict:
    """
    Verify a single host:port. Returns a dict with results.
    """
    # Resolve if hostname
    ok, resolved = resolve_host(host)
    if not ok:
        return {
            "host": host,
            "port": port,
            "verified": VERIFIED_NO,
            "detail": resolved,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

    is_open = check_tcp_port(resolved, port, timeout)

    return {
        "host": host,
        "port": port,
        "verified": VERIFIED_YES if is_open else VERIFIED_NO,
        "detail": "Port is open" if is_open else "Port is closed or filtered",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
