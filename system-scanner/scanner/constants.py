"""
Constants and defaults for System Scanner.
"""

APP_NAME = "System Scanner"
APP_VERSION = "1.0.0"
APP_AUTHOR = "System Scanner Project"

# Default scan settings
DEFAULT_PORT_RANGE = "1-1024"
DEFAULT_TIMEOUT = 1.0
MAX_TIMEOUT = 10.0
MIN_TIMEOUT = 0.1
MAX_PORT = 65535
MIN_PORT = 1
MAX_THREADS = 100

# Common service names for well-known ports
COMMON_SERVICES = {
    20: "FTP-Data",
    21: "FTP",
    22: "SSH",
    23: "Telnet",
    25: "SMTP",
    53: "DNS",
    67: "DHCP",
    68: "DHCP",
    69: "TFTP",
    80: "HTTP",
    110: "POP3",
    111: "RPCBind",
    119: "NNTP",
    123: "NTP",
    135: "MSRPC",
    137: "NetBIOS-NS",
    138: "NetBIOS-DGM",
    139: "NetBIOS-SSN",
    143: "IMAP",
    161: "SNMP",
    162: "SNMP-Trap",
    179: "BGP",
    389: "LDAP",
    443: "HTTPS",
    445: "SMB",
    465: "SMTPS",
    514: "Syslog",
    515: "LPD",
    520: "RIP",
    587: "SMTP-Sub",
    631: "IPP/CUPS",
    636: "LDAPS",
    993: "IMAPS",
    995: "POP3S",
    1080: "SOCKS",
    1433: "MSSQL",
    1434: "MSSQL-Mon",
    1521: "Oracle",
    1723: "PPTP",
    2049: "NFS",
    3306: "MySQL",
    3389: "RDP",
    5432: "PostgreSQL",
    5900: "VNC",
    5901: "VNC-1",
    6379: "Redis",
    8080: "HTTP-Alt",
    8443: "HTTPS-Alt",
    8888: "HTTP-Alt2",
    9090: "Prometheus",
    9200: "Elasticsearch",
    11211: "Memcached",
    27017: "MongoDB",
}

# History settings
HISTORY_FILE = "history.json"
MAX_HISTORY_ENTRIES = 500

# Scan states
STATE_OPEN = "Open"
STATE_CLOSED = "Closed"
STATE_FILTERED = "Filtered"
STATE_ERROR = "Error"

# Verification states
VERIFIED_YES = "Yes"
VERIFIED_NO = "No"
VERIFIED_PENDING = "—"
