from __future__ import annotations

import asyncio

from aiohttp import ClientSession
from PyQt5 import QtGui, QtWidgets, uic
from qasync import asyncClose, asyncSlot

from . import home


class Window(QtWidgets.QMainWindow):
    """Represents the graphical login screen.

    Attributes
    ----------
    portal_window: :class:`home.Window`
        The home window instance that will be created when
        the user successfully makes the login request.
    """

    portal_window: home.Window

    def __init__(self, loop: asyncio.AbstractEventLoop, session: ClientSession):
        super().__init__()
        uic.loadUi('ui/login.ui', self)

        button: QtWidgets.QPushButton = self.findChild(QtWidgets.QPushButton, "loginButton")
        button.clicked.connect(self.on_login)

        self.error_message: QtWidgets.QLabel = self.findChild(QtWidgets.QLabel, "errorMessage")
        self.username_input: QtWidgets.QLineEdit = self.findChild(QtWidgets.QLineEdit, "usernameLineEdit")
        self.password_input: QtWidgets.QLineEdit = self.findChild(QtWidgets.QLineEdit, "passwordLineEdit")

        self.username_input.returnPressed.connect(self.on_login)
        self.password_input.returnPressed.connect(self.on_login)

        self.loop = loop
        self.session = session

    @asyncClose
    async def closeEvent(self, event: QtGui.QCloseEvent):
        """Represents the default close event.

        Asynchronously closes the aiohttp session.
        """
        await self.session.close()

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

        async with self.session.get("http://127.0.0.1:8082/login", json={
            "username": username_text,
            "password": password_text
        }) as request:
            response = await request.json()
            print(response)
