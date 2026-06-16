# Kezo Scanner

**Advanced System Diagnostics & Network Utility**

Kezo Scanner is an elite, high-performance desktop network and system utility built with Python and PySide6. Designed for deep system analysis and network visibility, it provides precise diagnostics, real-time tracking, and granular configuration audits in one unified, sleek platform.

---

## 🔥 Elite Capabilities

- **Quantum-Speed Audits**: Blazing fast, highly-optimized algorithms ensure your entire network and system architecture is mapped rapidly.
- **Surgical Precision**: Scans deep into system layers to isolate and expose hidden open ports, active services, and potential network bottlenecks.
- **Actionable Intelligence**: Transforms raw, complex scan data into crystal-clear, comprehensive GUI dashboards. Know exactly what's happening under the hood.
- **Flexible Targeting**: Scan single IPs, hostnames, or full CIDR subnets (up to /24) with customized port ranges.
- **Data Export**: Seamlessly export your intelligence reports to CSV, JSON, or TXT for further analysis.
- **Persistent History**: Keeps track of your scan history locally, restoring your state on the next launch.

---

## 💻 System Requirements

To run Kezo Scanner smoothly, ensure your system meets the following requirements:

| Requirement     | Value                  |
|-----------------|------------------------|
| **OS**          | Ubuntu 21.04+ (or compatible Linux) |
| **Python**      | Python 3.7+            |
| **Display**     | X11 or Wayland         |

### Dependencies

The application relies on the following core Python packages (listed in `requirements.txt`):
- `PySide6 >= 6.2.0` (For the modern Qt6 GUI framework)

Additionally, the following Ubuntu system libraries are required (automatically installed via the setup script):
- `python3-venv`, `python3-pip`
- `libgl1-mesa-glx`, `libegl1`
- `libxkbcommon0`, `libdbus-1-3`

---

## 🚀 Seamless Deployment (Quick Start)

### 1. Acquire the Suite & Install Dependencies

Clone or download the repository, then run the included installation script to set up your environment:

```bash
cd system-scanner
bash install.bash
```

*This script will automatically verify your Python version, install necessary system libraries, create a secure virtual environment, and install all Python dependencies from `requirements.txt`.*

### 2. Initiate the Core

Execute the primary application launcher. The frictionless interface will auto-configure to your environment:

```bash
./run.sh
```

*(Alternatively, launch **Kezo Scanner** directly from your Ubuntu application menu if you used the installer!)*

### 3. Extract Intelligence

1. Enter a target (e.g., `192.168.1.1`, `localhost`, or `10.0.0.0/24`).
2. Specify your port range (e.g., `1-1024`, `22,80,443`).
3. Click **Scan** to unleash the engine.
4. Review the generated telemetry in the real-time table.
5. Click **Export** to securely save your insights.

---

## 🛠️ Manual Installation (Without bash scripts)

If you prefer to run it manually without the `install.bash` script:

```bash
# 1. Create a virtual environment
python3 -m venv venv

# 2. Activate the virtual environment
source venv/bin/activate

# 3. Install the dependencies
pip install -r requirements.txt

# 4. Run the application
python app.py
```

---

## 🛠️ Packaging for Distribution

If you wish to distribute Kezo Scanner as a standalone binary or package:

**PyInstaller Standalone Binary:**
```bash
bash build.sh
./dist/system-scanner/system-scanner
```

For `.deb` packages or `AppImage` builds, refer to the guides inside the `packaging/` directory.

---

## 🧹 Uninstallation

To completely remove the suite and its configurations:

```bash
bash uninstall.bash
```

---

## 🛡️ Ethics & Security Notice

Kezo Scanner is a powerful diagnostic utility designed strictly for **defensive, administrative, and educational use**. 
- Only scan networks and hosts that you own or have explicit authorization to audit.
- Use responsibly and in full compliance with local laws and organizational policies.
