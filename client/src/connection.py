from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Dict

from aiohttp import ClientSession, ClientWebSocketResponse, WSMsgType

if TYPE_CHECKING:
    from views import home


@dataclass
class WebsocketConnection:
    """Dataclass to hold information about the WebSocket connection."""

    username: str
    session: ClientSession
    websocket: WebsocketHandler

    def __init__(self, username: str, session: ClientSession, websocket: WebsocketHandler) -> None:
        self.username = username
        self.session = session
        self.websocket = websocket

    async def send(self, message: Dict[Any, Any]) -> None:
        """Sends a message though the WebSocket connection.

        Shorthand for calling `self.connection.websocket.socket.send_json`

        :param message: The message to send.
        """
        await self.websocket.socket.send_json(message)


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

    async def parse(self, data: Dict[Any, Any], home_window: home.Window):
        """Parses messages from the websocket connection.

        :param data: The data received in dict format.
        :param home_window: The home window.
        """
        op = data.get("op")

        if op == self.MESSAGE:
            home_window.append_message(**data["data"])

    async def listen(self, home_window: home.Window):
        """Listens to incoming websocket messages.

        :param home_window: The home window.
        """
        async for message in self.socket:
            if message.type == WSMsgType.TEXT:
                await self.parse(message.data, home_window)
