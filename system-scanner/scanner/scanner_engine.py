"""
Scanner engine: multi-threaded TCP port scanner with progress reporting.
"""
from __future__ import annotations

import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

from scanner.network_utils import (
    validate_target,
    resolve_host,
    expand_targets,
    parse_port_range,
    check_tcp_port,
    guess_service,
)
from scanner.constants import (
    DEFAULT_TIMEOUT,
    MAX_THREADS,
    STATE_OPEN,
    STATE_CLOSED,
    VERIFIED_PENDING,
)


class ScanResult:
    """Holds one scan result row."""

    def __init__(self, host, port, state, service, timestamp=None):
        self.host = host
        self.port = port
        self.state = state
        self.service = service
        self.verified = VERIFIED_PENDING
        self.timestamp = timestamp or datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def to_dict(self):
        return {
            "host": self.host,
            "port": self.port,
            "state": self.state,
            "service": self.service,
            "verified": self.verified,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, d):
        r = cls(d["host"], d["port"], d["state"], d["service"], d.get("timestamp"))
        r.verified = d.get("verified", VERIFIED_PENDING)
        return r


def run_scan(target_str, port_str, timeout=DEFAULT_TIMEOUT,
             progress_callback=None, log_callback=None, cancel_check=None):
    """
    Run a full scan. Returns a list of ScanResult (open ports only).

    progress_callback(current, total) — called after each port checked.
    log_callback(message) — called for log messages.
    cancel_check() — returns True if scan should stop.
    """
    log = log_callback or (lambda m: None)
    check_cancel = cancel_check or (lambda: False)

    # Validate target
    valid, msg = validate_target(target_str)
    if not valid:
        log(f"[ERROR] {msg}")
        return []

    # Parse ports
    valid, ports_or_err = parse_port_range(port_str)
    if not valid:
        log(f"[ERROR] {ports_or_err}")
        return []
    ports = ports_or_err

    # Expand targets (handles CIDR)
    hosts_raw = expand_targets(target_str)
    hosts = []
    for h in hosts_raw:
        ok, resolved = resolve_host(h)
        if ok:
            hosts.append(resolved)
        else:
            log(f"[WARN] {resolved}")

    if not hosts:
        log("[ERROR] No valid hosts to scan.")
        return []

    total_tasks = len(hosts) * len(ports)
    log(f"[INFO] Scanning {len(hosts)} host(s), {len(ports)} port(s) "
        f"({total_tasks} checks, timeout={timeout}s)")

    results = []
    done_count = 0
    start_time = time.time()

    thread_count = min(MAX_THREADS, total_tasks)

    def scan_one(host, port):
        is_open = check_tcp_port(host, port, timeout)
        return host, port, is_open

    with ThreadPoolExecutor(max_workers=thread_count) as executor:
        futures = {}
        for host in hosts:
            for port in ports:
                if check_cancel():
                    log("[WARN] Scan cancelled by user.")
                    return results
                f = executor.submit(scan_one, host, port)
                futures[f] = (host, port)

        for future in as_completed(futures):
            if check_cancel():
                log("[WARN] Scan cancelled by user.")
                executor.shutdown(wait=False, cancel_futures=True)
                return results

            done_count += 1
            try:
                host, port, is_open = future.result()
                if is_open:
                    service = guess_service(port)
                    r = ScanResult(host, port, STATE_OPEN, service)
                    results.append(r)
                    log(f"[OPEN] {host}:{port} ({service})")
            except Exception as e:
                h, p = futures[future]
                log(f"[ERROR] {h}:{p} — {e}")

            if progress_callback:
                progress_callback(done_count, total_tasks)

    elapsed = time.time() - start_time
    log(f"[INFO] Scan complete. {len(results)} open port(s) found "
        f"in {elapsed:.1f}s")

    # Sort results by host then port
    results.sort(key=lambda r: (r.host, r.port))
    return results
