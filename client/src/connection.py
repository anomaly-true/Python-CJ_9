from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

from aiohttp import ClientSession, ClientWebSocketResponse, WSMsgType


@dataclass
class WebsocketConnection:
    """Dataclass to hold information about the WebSocket connection."""

    username: str
    session: ClientSession
    websocket: ClientWebSocketResponse

    def __init__(self, username: str, session: ClientSession, websocket: WebsocketHandler) -> None:
        self.username = username
        self.session = session
        self.websocket = websocket


class WebsocketHandler:
    """
    Represents a websocket connection.

    Attributes
    ----------
    MESSAGE
        A message has been sent from a client.
    """

    MESSAGE = 0

    def __init__(
        self,
        *,
        websocket: ClientWebSocketResponse,
    ) -> None:
        self.socket = websocket

    @classmethod
    async def from_user(
        cls,
        session: ClientSession,
        token: str
    ) -> WebsocketHandler:
        """Handles the websocket connection.

        :param session: The session used to make the websocket connection.
        :param loop: The event loop used to make the websocket connection.
        """
        websocket = await session.ws_connect(f"http://127.0.0.1:8080/ws/{token}")
        self = cls(websocket=websocket)
        return self

    async def parse(self, data: Dict[Any, Any]):
        """Parses messages from the websocket connection.

        :param data: The data received in dict format.
        """
        print(data)
        await self.socket.send_json(data)

    async def listen(self):
        """Listens to incoming websocket messages."""
        async for message in self.socket:
            if message.type == WSMsgType.TEXT:
                await self.parse(message.data)
