from contextlib import asynccontextmanager
import threading
import socket
from instaui import ui


START_PORT, END_PORT = 40000, 40100


class TestServer:
    def __init__(self) -> None:
        self.connected = threading.Event()
        self._server = ui.server(debug=False)
        self.port = _find_available_port(START_PORT, END_PORT)

        @asynccontextmanager
        async def lifespan_wrapper(app):
            self.connected.set()
            yield

        self._server.router.lifespan_context = lifespan_wrapper

        self.server_thread = threading.Thread(
            target=self._server.run,
            kwargs={"port": self.port, "reload": False, "log_level": "warning"},
            daemon=True,
        )

        self._is_started = False

    @property
    def url(self) -> str:
        return f"http://localhost:{self.port}"

    def start(self) -> None:
        if self._is_started:
            return
        self._is_started = True
        self.server_thread.start()

    def wait_for_connection(self, timeout: float = 10) -> None:
        self.connected.wait(timeout=timeout)

    def stop(self) -> None:
        self._server.try_close_server()


def _find_available_port(start_port: int, end_port: int):
    for port in range(start_port, end_port + 1):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(("localhost", port))
                return port
        except OSError:
            continue
    raise Exception(f"No available port in range {start_port} - {end_port}")
