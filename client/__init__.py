import socket
import sys
import time
import typing as t

from utils.config import HEADER_LENGTH
from utils.logger import get_logging
from utils.utils import on_startup


class Client:
    def __init__(self, address: tuple, username: str) -> None:
        self.host = address[0]
        self.port = address[1]
        self.username = username

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.start_timer = time.perf_counter()
        self.startup_duration = None

    @staticmethod
    def get_header(message: bytes) -> bytes:
        return f"{len(message):<{HEADER_LENGTH}}".encode("utf-8")

    def connect(self) -> None:
        try:
            self.socket.connect((self.host, self.port))
        except ConnectionRefusedError:
            on_startup("Client")
            print(get_logging("error", "Connection could not be established. Invalid HOST/PORT."))
            sys.exit(1)
        else:
            end = time.perf_counter()
            self.startup_duration = round((end - self.start_timer) * 1000, 2)

            on_startup("Client", self.startup_duration)

            print(get_logging("success", f"Connected to remote host at [{self.host}:{self.port}]."))

        self.socket.setblocking(False)

    def disconnect(self) -> None:
        self.socket.close()

    def initialize(self) -> None:
        # Send the specified uname.
        uname = self.username.encode("utf-8")
        uname_header = self.get_header(uname)

        # Send the message
        self.socket.send(uname_header + uname)

    def receive_message(self) -> tuple:
        username_header = self.socket.recv(HEADER_LENGTH)

        if not len(username_header):
            print("\n" + get_logging("error", "Server has closed the connection."))
            sys.exit(1)

        username_len = int(username_header.decode('utf-8').strip())
        username = self.socket.recv(username_len).decode('utf-8')

        msg_length = int(self.socket.recv(HEADER_LENGTH).decode('utf-8').strip())
        msg = self.socket.recv(msg_length).decode('utf-8')

        return username, msg

    def send_message(self, message: t.Optional[str] = None) -> None:
        if message:
            message = message.replace("\n", "").encode("utf-8")
            message_header = self.get_header(message)

            self.socket.send(message_header + message)
