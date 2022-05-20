import logging
import pickle
import socket
import threading

from schemas import MessageObjectSchema


LOGGER = logging.basicConfig(
    level=logging.DEBUG,
    format="[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s",
    datefmt="%d%b%y %H:%M:%S",
)


class MessageClient:

    FORMAT = "utf-8"

    def __init__(
        self, port: str = 7000, server_ip: str = None, username: str = "unknown"
    ):
        self.port = port
        self.server_ip = (
            server_ip
            if server_ip
            else socket.gethostbyname(socket.gethostname())
        )
        self.username = username.lower()

        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((self.server_ip, self.port))

        logging.debug("[BOUND] Connection Successful")

    def _handle_send_message(self):
        while True:
            message = input("Type the message: ")
            self.client.send(
                pickle.dumps(MessageObjectSchema(self.username, message))
            )

    def _handle_incomming_message(self):
        while True:
            object: MessageObjectSchema = pickle.loads(self.client.recv(4096))
            logging.info(f"[NEW MESSAGE] {object.user}: {object.message}")

    def go(self):
        send_message_thread = threading.Thread(target=self._handle_send_message)
        get_message_pool = threading.Thread(
            target=self._handle_incomming_message
        )
        send_message_thread.start()
        get_message_pool.start()


if __name__ == "__main__":
    client = MessageClient(server_ip="172.19.120.26")
    raise SystemExit(client.go())
