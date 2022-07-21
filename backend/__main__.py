from __future__ import annotations

import sys
import traceback
import uuid
from typing import Any, Dict

from fastapi import FastAPI, WebSocket

debug = sys.argv[1] == "debug"
app = FastAPI(
    debug=debug
)


class WebsocketConnection:
    """Represents a websocket connection.

    Holds any information related to a websocket connection
    in order to cleanly manage connections.
    """

    def __init__(self, ws: WebSocket):
        self.ws = ws
        self.id = uuid.uuid4()

    async def send_json(self, data: Dict[Any, Any]):
        """
        Sends a message to the websocket connection.

        :param message: The message to send.
        """
        try:
            await self.ws.send_json(data)
        except Exception as exc:
            print("EXCEPTION RAISED FROM SENDING A MESSAGE; printing exception...")
            traceback.print_exception(exc)

    @classmethod
    async def from_websocket(cls, ws: WebSocket) -> WebsocketConnection:
        """
        Creates a `WebsocketConnection` from a websocket connection.

        :param ws: The websocket connection to use.
        """
        await ws.accept()
        self = cls(ws)
        return self

    async def parse(self, message: Dict[Any, Any]):
        """
        Parses a message from the websocket connection.

        :param message: Message from the websocket.
        """

    async def listen(self):
        """Listens for messages from the websocket connection."""
        message = await self.ws.receive_json()
        await self.parse(message)


class ConnectionManager:
    """Represents the connection manager.

    Handles all inbound websocket connection and disconnect
    messages.
    """

    def __init__(self):
        self.active_connections: Dict[str, WebsocketConnection] = {}

    async def connect(self, websocket: WebSocket):
        """Connects to the websocket connection.

        :param websocket: The websocket to connect to.
        """
        connection = await WebsocketConnection.from_websocket(websocket)
        self.active_connections[connection.id] = connection
        return connection

    def disconnect(self, websocket: WebsocketConnection):
        """Disconnects from the websocket connection.

        :param websocket: The websocket to disconnect from.
        """
        del self.active_connections[websocket.id]

    async def broadcast(self, message: str):
        """Broadcasts a message to every connected websocket connection

        :param message: Message to broadcast.
        """
        for id, connection in self.active_connections.items():
            await connection.send_json(message)


manager = ConnectionManager()


@app.websocket("/ws/")
async def websocket_connect(websocket: WebSocket):
    """Default websocket connection connection."""
    connection = await manager.connect(websocket)
    while True:
        try:
            await connection.listen()
        except Exception as exc:
            print("EXCEPTION RAISED FROM LISTENING; printing exception...")
            traceback.print_exception(exc)
