from __future__ import annotations

import os

import toml

# Hard-coded constants
VERSION = "0.1.0"
PROTOCOL_VERSION = 1

# Logging setting
DEBUG = bool(os.environ.get("BYTELINK_DEBUG", 0))
LOG_FILE = os.environ.get("BYTELINK_LOG_FILE", None)
LOG_FILE_MAX_SIZE = int(os.environ.get("BYTELINK_LOG_FILE_SIZE_MAX", 1_048_576))  # in bytes (default: 1MiB)

# Config file location, in this case it's `config.toml` in root
CONFIG_FILE = os.environ.get("BYTELINK_CONFIG_FILE", "config.toml")
config = toml.load(CONFIG_FILE)
server_config = config["server"]["config"]


class Config:
    IP = server_config["ip"]
    PORT = server_config["port"]
    MOTD = server_config["motd"]

    PASSWORD = config["server"]["auth"]["password"]

    # Load the max connections, It's `None` if 0 is specified.
    MAX_CONNECTIONS = server_config["max-connections"] if server_config["max-connections"] != 0 else None
