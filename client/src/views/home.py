from __future__ import annotations

from typing import TYPE_CHECKING

from PyQt5 import QtWidgets, uic
from qasync import asyncSlot
from qt_material import apply_stylesheet

if TYPE_CHECKING:
    from ..connection import WebsocketConnection


class Window(QtWidgets.QMainWindow):
    """Represents the home window.

    Used to connect the websocket connection and the
    user input.
    """

    def __init__(self, connection: WebsocketConnection):
        super().__init__()
        uic.loadUi('ui/home.ui', self)

        apply_stylesheet(self, theme='dark_purple.xml')

        self.connection = connection

        self.chat_box: QtWidgets.QTextEdit = self.findChild(QtWidgets.QTextEdit, "chatBox")
        self.message_box: QtWidgets.QLineEdit = self.findChild(QtWidgets.QLineEdit, "messageBox")
        self.send_button: QtWidgets.QPushButton = self.findChild(QtWidgets.QPushButton, "sendButton")

        self.message_box.returnPressed.connect(self.send_message)
        self.send_button.clicked.connect(self.send_message)

    @asyncSlot()
    async def send_message(self):
        """Triggered when a user presses the send button."""
        text = self.message_box.text()
        self.chat_box.setText(f"{self.chat_box.toPlainText()}\n{self.connection.username}: {text}")
        self.message_box.clear()
