from __future__ import annotations

import asyncio
from random import choice

from aiohttp import ClientConnectionError, ClientSession
from connection import WebsocketConnection, WebsocketHandler
from PyQt5 import QtGui, QtWidgets, uic
from qasync import asyncClose, asyncSlot
from qt_material import apply_stylesheet
from qtwidgets import AnimatedToggle

from . import home


class Window(QtWidgets.QMainWindow):
    """Represents the graphical login screen."""

    def __init__(self, loop: asyncio.AbstractEventLoop, session: ClientSession):
        super().__init__()
        uic.loadUi("./ui/login.ui", self)

        button: QtWidgets.QPushButton = self.findChild(
            QtWidgets.QPushButton, "loginButton"
        )
        button.clicked.connect(self.on_login)

        central_widget: QtWidgets.QVBoxLayout = self.findChild(
            QtWidgets.QVBoxLayout, "verticalLayout_7"
        )
        toggle = AnimatedToggle(checked_color="#FFFFFF", pulse_checked_color="#000000")
        toggle.setMaximumSize(100, 100)
        toggle.clicked.connect(self.theme_toggle)
        central_widget.addChildWidget(toggle)

        self.error_message: QtWidgets.QLabel = self.findChild(
            QtWidgets.QLabel, "errorMessage"
        )
        self.username_input: QtWidgets.QLineEdit = self.findChild(
            QtWidgets.QLineEdit, "usernameLineEdit"
        )
        self.password_input: QtWidgets.QLineEdit = self.findChild(
            QtWidgets.QLineEdit, "passwordLineEdit"
        )

        self.username_input.returnPressed.connect(self.on_login)
        self.password_input.returnPressed.connect(self.on_login)

        self.loop = loop
        self.session = session

        self.light_mode: bool = False
        self.is_running: bool = True

        self.theme_colour: str = "purple"
        apply_stylesheet(self, theme=f"light_{self.theme_colour}.xml")

    @asyncClose
    async def closeEvent(self, event: QtGui.QCloseEvent):
        """Represents the default close event.

        Asynchronously closes the aiohttp session.
        """
        await self.session.close()

    @asyncSlot()
    async def theme_toggle(self):
        """Called when the light mode toggle is clicked."""
        if self.light_mode:
            apply_stylesheet(self, theme=f"dark_{self.theme_colour}.xml")
            self.light_mode = choice([True, False, False])
        else:
            apply_stylesheet(self, theme=f"light_{self.theme_colour}.xml")
            self.light_mode = choice([True, True, False])

    @asyncSlot()
    async def on_login(self):
        """Called when the user presses the login button.

        Makes a `GET` request to the server /login with the
        username and password.
        """
        username_text = self.username_input.text()
        password_text = self.password_input.text()

        if not all([text for text in [username_text, password_text]]):
            return self.error_message.setText("ERROR: Please fill out all fields")

        async with self.session.get(
            "http://127.0.0.1:8080/login",
            json={"username": username_text, "password": password_text},
        ) as request:
            response = await request.json()
            print(response)
            if "error" in response:
                return self.error_message.setText("ERROR: " + response["error"])

        self.destroy()

        try:
            websocket = await WebsocketHandler.from_user(self.session, response["token"])

            connection = WebsocketConnection(
                username=response["username"], session=self.session, websocket=websocket
            )

            home_window = home.Window(connection)
            home_window.show()

            while True:
                await websocket.listen(home_window)
        except ClientConnectionError:
            self.is_running = False
            print("Websocket disconnected")
