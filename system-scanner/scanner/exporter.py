"""
Exporter: save scan results to CSV, JSON, or TXT.
"""
from __future__ import annotations

import os
import csv
import json
from datetime import datetime


def export_csv(results: list[dict], filepath: str):
    """Export results to a CSV file."""
    if not results:
        raise ValueError("No results to export.")

    fieldnames = ["host", "port", "state", "service", "verified", "timestamp"]

    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in results:
            writer.writerow({k: row.get(k, "") for k in fieldnames})


def export_json(results: list[dict], filepath: str):
    """Export results to a JSON file."""
    if not results:
        raise ValueError("No results to export.")

    export_data = {
        "app": "System Scanner",
        "exported_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_results": len(results),
        "results": results,
    }

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(export_data, f, indent=2, ensure_ascii=False)


def export_txt(results: list[dict], filepath: str):
    """Export results as a readable TXT summary."""
    if not results:
        raise ValueError("No results to export.")

    lines = [
        "=" * 60,
        "  System Scanner — Scan Results",
        f"  Exported: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"  Total results: {len(results)}",
        "=" * 60,
        "",
        f"{'Host':<20} {'Port':<8} {'State':<10} {'Service':<16} {'Verified':<10} {'Timestamp'}",
        "-" * 90,
    ]

    for r in results:
        lines.append(
            f"{r.get('host', ''):<20} "
            f"{r.get('port', ''):<8} "
            f"{r.get('state', ''):<10} "
            f"{r.get('service', ''):<16} "
            f"{r.get('verified', ''):<10} "
            f"{r.get('timestamp', '')}"
        )

    lines.append("")
    lines.append("=" * 60)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def export_results(results: list[dict], filepath: str, fmt: str = "csv"):
    """
    Export results to a file.
    fmt: 'csv', 'json', or 'txt'.
    """
    fmt = fmt.lower().strip()
    if fmt == "csv":
        export_csv(results, filepath)
    elif fmt == "json":
        export_json(results, filepath)
    elif fmt == "txt":
        export_txt(results, filepath)
    else:
        raise ValueError(f"Unsupported export format: {fmt}")
