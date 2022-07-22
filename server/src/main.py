from __future__ import annotations

import sys
import uuid
from typing import Any, Dict

import databases
import pydantic
from app import models
from app.database import SQLALCHEMY_DATABASE_URL, engine
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from starlette.responses import FileResponse

debug = sys.argv[1] == "debug"
app = FastAPI(debug=debug)
database = databases.Database(SQLALCHEMY_DATABASE_URL)
models.Base.metadata.create_all(bind=engine)


@app.on_event("startup")
async def connect():  # noqa: D103
    await database.connect()


@app.on_event("shutdown")
async def shutdown():  # noqa: D103
    await database.disconnect()


class LoginModel(pydantic.BaseModel):
    """The user login body"""

    username: str
    password: str


class WebsocketConnection:
    """Represents a websocket connection.

    Holds any information related to a websocket connection
    in order to cleanly manage connections.

    Attributes
    ----------
    MESSAGE
        A user has sent a message.
    """

    MESSAGE = 0

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
        op = data.get("op")

        if op == self.MESSAGE:
            await manager.broadcast(data, ignore=self.id)

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

    async def broadcast(self, message: Dict[Any, Any], *, ignore: str):
        """Broadcasts a message to every connected websocket connection

        :param message: Message to broadcast.
        """
        for id, connection in self.active_connections.items():
            if id == ignore:
                continue
            await connection.ws.send_json(message)


manager = ConnectionManager()


@app.get("/")
async def home():
    """Renders the home page."""
    return FileResponse("views/home.html")


@app.get("/login")
async def login(body: LoginModel):
    """Retrieves user data from username and password.

    :param body: The body received from the request.
    """
    response = await database.fetch_one(
        "SELECT * FROM users WHERE username=:username AND password=:password",
        values={"username": body.username, "password": body.password},
    )
    if response is None:
        return {"error": "Please enter a valid username and password."}
    return response


@app.get("/register")
async def register_details():
    """Register an account."""
    return FileResponse("views/register.html")


@app.post("/register")
async def create_account(body: LoginModel):
    """Creates an account from username and password.

    :param body: The body received from the request.
    """
    query = models.User.__table__.insert().values(
        username=body.username, password=body.password, token=str(uuid.uuid4())
    )
    try:
        await database.execute(query)
    except Exception:
        return


@app.websocket("/ws/{token}")
async def websocket_connect(websocket: WebSocket, _: str):
    """Default websocket connection connection."""
    connection = await manager.connect(websocket)
    try:
        while True:
            await connection.listen()
    except WebSocketDisconnect:
        manager.disconnect(connection)
