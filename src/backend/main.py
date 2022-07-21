from __future__ import annotations

import sys
import uuid
from typing import Any, Dict

from fastapi import FastAPI, WebSocket, WebSocketDisconnect

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

    @classmethod
    async def from_websocket(cls, websocket: WebSocket) -> WebsocketConnection:
        """
        Creates a `WebsocketConnection` from a websocket connection.

        :param ws: The websocket connection to use.
        """
        await websocket.accept()
        self = cls(websocket)
        return self

    async def parse(self, data: Dict[Any, Any]):
        """
        Parses a message from the websocket connection.

        :param message: Message from the websocket.
        """
        print(data)

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
        print(self.active_connections)
        return connection

    def disconnect(self, connection: WebsocketConnection):
        """Disconnects from the websocket connection.

        :param connection: The websocket to disconnect from.
        """
        print(self.active_connections)
        del self.active_connections[connection.id]

    async def broadcast(self, message: str):
        """Broadcasts a message to every connected websocket connection

        :param message: Message to broadcast.
        """
        for id, connection in self.active_connections.items():
            await connection.ws.send_json(message)


manager = ConnectionManager()


@app.websocket("/ws")
async def websocket_connect(websocket: WebSocket):
    """Default websocket connection connection."""
    connection = await manager.connect(websocket)
    try:
        await connection.ws.send_json({"op": 0, "message": "Hello, world!"})
        while True:
            await connection.listen()
    except WebSocketDisconnect:
        manager.disconnect(connection)
