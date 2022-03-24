from textwrap import dedent

from .utils import config_parser, get_bright_color

# Constants.
BANNER = dedent(f"""{get_bright_color("CYAN")}
 ____               _____
/_  / ___ _______  / ___/__  __ _
 / /_/ -_) __/ _ \\/ /__/ _ \\/  ' \\
/___/\\__/_/  \\___/\\___/\\___/_/_/_/
""")

# Server related config.
IP = config_parser("server", "IP")
PORT = config_parser("server", "port", cast=int)
HEADER_LENGTH = config_parser("server", "HEADER_LEN", cast=int)
MOTD = config_parser("server", "MOTD")

# Authentication config.
PASSWORD = config_parser("auth", "PASSWORD")

# Max connections.
MAX_CONNECTIONS = config_parser("server", "MAX_CONNECTIONS")
MAX_CONNECTIONS = None if MAX_CONNECTIONS == "" else MAX_CONNECTIONS
