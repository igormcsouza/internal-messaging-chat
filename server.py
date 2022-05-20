from datetime import datetime
import socket
import threading
import logging
import pickle
import time
from typing import Optional

from schemas import (
    ActiveConnectionSchema,
    MessageHistorySchema,
    MessageObjectSchema,
)


LOGGER = logging.basicConfig(
    level=logging.DEBUG,
    format="[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s",
    datefmt="%d%b%y %H:%M:%S",
)


class MessagingServer:
    def __init__(self, port: str = 7000, server_ip: str = None):
        self.server_ip = (
            server_ip
            if server_ip
            else socket.gethostbyname(socket.gethostname())
        )
        self.port = port

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.server_ip, self.port))

        # Use sqlite next
        self.active_connections: list[Optional[ActiveConnectionSchema]] = []
        self.message_history: list[Optional[MessageHistorySchema]] = []

    def _update_current_connection(
        self, current_connection: ActiveConnectionSchema
    ) -> None:
        for msg in self.message_history[current_connection.last :]:
            current_connection.connection.send(pickle.dumps(msg.message_object))
            time.sleep(0.2)

        current_connection.last = len(self.message_history)

    def _notify_everyone(self, unless: ActiveConnectionSchema = None):
        filtered_connections = (
            filter(lambda conn: conn == unless, self.active_connections)
            if unless is not None
            else self.active_connections
        )

        for connection in filtered_connections:
            self._update_current_connection(connection)

    def handle_client(
        self, conn: socket.socket, addrs: tuple[str, int]
    ) -> None:
        current_connection = ActiveConnectionSchema(conn, addrs)
        self.active_connections.append(current_connection)
        self._update_current_connection(current_connection)

        logging.debug(f"[CONNECTION] Got new connection from {addrs}")

        while True:
            try:
                object: MessageObjectSchema = pickle.loads(conn.recv(4096))
            except EOFError:
                logging.debug(f"[DISCONNECTED] Client {addrs} got disconnected")
                self.active_connections.remove(current_connection)
                break
            else:
                logging.debug(f"[{addrs}] {object.user}: {object.message}")
                self.message_history.append(
                    MessageHistorySchema(
                        object,
                        current_connection,
                        datetime.timestamp(datetime.now()),
                    )
                )
                self._notify_everyone(unless=current_connection)

    def _accept_new_connections(self) -> None:
        connection, address = self.server.accept()

        new_thread = threading.Thread(
            target=self.handle_client, args=(connection, address)
        )
        new_thread.start()

        logging.debug(f"[ACTIVE CONNECTIONS] {(threading.active_count() - 1)}")

    def go(self) -> None:
        self.server.listen()
        logging.info(
            f"[STARTED] Server is listening on {self.server_ip}:{self.port}"
        )

        try:
            while True:
                self._accept_new_connections()
        except KeyboardInterrupt:
            logging.info("[ENDED] Bye!")


if __name__ == "__main__":
    server = MessagingServer()
    raise SystemExit(server.go())
