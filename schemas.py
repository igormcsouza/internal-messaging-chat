from dataclasses import dataclass
import socket


@dataclass
class MessageObjectSchema:
    user: str
    message: str


@dataclass
class ActiveConnectionSchema:
    connection: socket.socket
    address: str
    last: int = 0


@dataclass
class MessageHistorySchema:
    message_object: MessageObjectSchema
    current_connection: ActiveConnectionSchema
    timestamp: float
