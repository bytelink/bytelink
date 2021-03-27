import os
import typing as t
from configparser import SafeConfigParser
from textwrap import dedent

import colorama

colorama.init(autoreset=True)


def get_color(color: str) -> str:
    return getattr(colorama.Fore, color.upper())


def get_bright_color(color: str) -> str:
    return getattr(colorama.Style, "BRIGHT") + get_color(color)  # noqa: B009


def clear_screen() -> None:
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")


def config_parser(filename: str, section: str, variable: str, bool_: bool = False, int_: bool = False) -> t.Any:
    parser = SafeConfigParser()
    parser.read(filename)

    if bool_:
        return parser.getboolean(section, variable)
    elif int_:
        return parser.getint(section, variable)
    else:
        return parser.get(section, variable)


def on_startup() -> None:
    from .config import BANNER  # To prevent circular imports.

    version = config_parser("config.ini", "version", "VERSION")
    version = "v" + version if version != "" else "Version not found."

    clear_screen()
    message = dedent(f"""
    {BANNER}
    {get_bright_color("GREEN")} ZeroCOM Running. | {get_bright_color("YELLOW")}{version}
    """)

    print(message)
