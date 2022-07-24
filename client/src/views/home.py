from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict

import constants
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from qasync import asyncSlot
from qt_material import apply_stylesheet

from . import popup
from .highlighter import Highlighter

if TYPE_CHECKING:
    from ..connection import WebsocketConnection

# fmt: off
__all__ = (
    'Window',
)
# fmt: on


class Window(QtWidgets.QMainWindow):
    """Represents the home window.

    Used to connect the websocket connection and the
    user input.
    """

    popup: popup.Window

    def __init__(self, connection: WebsocketConnection):
        super().__init__()
        uic.loadUi("./ui/home.ui", self)

        apply_stylesheet(self, theme="dark_purple.xml")

        self.connection = connection

        self.message_box: QtWidgets.QLineEdit = self.findChild(
            QtWidgets.QLineEdit, "messageBox"
        )
        self.send_button: QtWidgets.QPushButton = self.findChild(
            QtWidgets.QPushButton, "sendButton"
        )
        self.code_input: QtWidgets.QTextEdit = self.findChild(
            QtWidgets.QTextEdit, "codeInput"
        )
        self.code_input.setMarkdown(
            """
```py
import unittest

class Test(unittest.TestCase):
    pass
```
"""
        )
        # self.code_input.mousePressEvent = self.code_output_mouse_press

        self.code_output: QtWidgets.QTextEdit = self.findChild(
            QtWidgets.QTextEdit, "codeOutput"
        )
        self.message_box.returnPressed.connect(self.send_message)
        self.send_button.clicked.connect(self.send_message)

        self.run_button: QtWidgets.QPushButton = self.findChild(
            QtWidgets.QPushButton, "pushButton"
        )
        self.run_button.clicked.connect(self.run_code)

        self.chat_box: QtWidgets.QListView = self.findChild(
            QtWidgets.QListView, "chatBox"
        )
        self.chat_box_model = QtGui.QStandardItemModel()
        self.chat_box.setModel(self.chat_box_model)

        list_view: QtWidgets.QListView = self.findChild(QtWidgets.QListView, "listView")

        model = QtGui.QStandardItemModel()
        list_view.setModel(model)

        for i in map(str, range(100)):
            item = QtGui.QStandardItem(i)
            model.appendRow(item)

        first_entry_index = model.index(0, 0)
        selection_model = list_view.selectionModel()
        selection_model.select(first_entry_index, QtCore.QItemSelectionModel.Select)

        self.highlighter = Highlighter()
        self.highlighter.setDocument(self.code_input.document())

        font = QtGui.QFontDatabase.systemFont(QtGui.QFontDatabase.FixedFont)
        self.code_input.setFont(font)

    def parse_mouse_press(self, event: QtGui.QMouseEvent, widget_name: str):
        """Parses a mouse press event.

        Created to avoid repetitive code.

        :param: event: The mouse press event.
        :param widget_name: The name of the widget pressed.
        """
        if event.button() == QtCore.Qt.RightButton:
            feature_message = constants.FEATURE_MESSAGES.get(widget_name)
            self.popup = popup.Window(feature_message)

    def code_output_mouse_press(self, event: QtGui.QMouseEvent):
        """Central widget clicked."""
        print(QtWidgets.QTextEdit, self.code_input)
        super(QtWidgets.QTextEdit, self.code_input).mousePressEvent(event)
        print("?")
        # self.parse_mouse_press(event, "codeinput")

    def append_message(self, message: str, author: str = None):
        """Appends a message to the chat box.

        :param message: The message to append to the chat box.
        :param username: The username of the message author.
        """
        if not message:
            return
        if author is None:
            author = self.connection.username

        message_item = QtGui.QStandardItem(f"[ {author} ] {message}")
        self.chat_box_model.appendRow(message_item)

        entry_index = self.chat_box_model.index(self.chat_box_model.rowCount() - 1, 0)
        selection_model = self.chat_box.selectionModel()
        selection_model.select(entry_index, QtCore.QItemSelectionModel.Select)

    @asyncSlot()
    async def run_code(self):
        """Triggered when run code button is clicked."""
        self.code_output.setPlainText("Running code...")
        async with self.connection.session.post(
            "https://emkc.org/api/v2/piston/execute",
            json={
                "language": "py",
                "version": "3.10",
                "files": [{"content": self.code_input.toPlainText()}],
            },
        ) as request:
            response: Dict[Any, Any] = (await request.json())["run"]
        self.code_output.setMarkdown(
            f"```py\n$ python code.py\n{response['output']}```\nCode exited with code {response['code']}"
        )

    @asyncSlot()
    async def send_message(self):
        """Triggered when a user presses the send button."""
        message = self.message_box.text()
        self.append_message(message)

        self.message_box.clear()
        await self.connection.send(
            {"op": 0, "data": {"message": message, "author": self.connection.username}}
        )
