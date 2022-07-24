from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, Union

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


class Widgets:
    """Manages all the widgets.

    Keeps code clean and systematic.

    :param window: The window with all the widgets.
    """

    def __init__(self, window: Window):
        # fmt: off
        self.message_box: QtWidgets.QLineEdit = window.findChild(QtWidgets.QLineEdit, "messageBox")
        self.send_button: QtWidgets.QPushButton = window.findChild(QtWidgets.QPushButton, "sendButton")
        self.code_input: QtWidgets.QTextEdit = window.findChild(QtWidgets.QTextEdit, "codeInput")
        self.code_output: QtWidgets.QTextEdit = window.findChild(QtWidgets.QTextEdit, "codeOutput")
        self.run_button: QtWidgets.QPushButton = window.findChild(QtWidgets.QPushButton, "runCode")
        self.chat_box: QtWidgets.QListView = window.findChild(QtWidgets.QListView, "chatBox")
        self.game_label: QtWidgets.QLabel = window.findChild(QtWidgets.QLabel, "gameLabel")
        self.run_code_layout: QtWidgets.QWidget = window.findChild(QtWidgets.QWidget, "runCodeLayout")
        # fmt: on

        self.message_box.returnPressed.connect(window.send_message)
        self.send_button.clicked.connect(window.send_message)
        self.run_button.clicked.connect(window.run_code)

        self.chat_box_model = QtGui.QStandardItemModel()
        self.chat_box.setModel(self.chat_box_model)

        self.highlighter = Highlighter()
        self.highlighter.setDocument(self.code_input.document())

        self.run_code_layout.hide()

class Window(QtWidgets.QMainWindow):
    """Represents the home window.

    Used to connect the websocket connection and the
    user input.

    :param connection: The websocket connection dataclass instance
                    used to manage message sending.
    :attr _popup: The popup window to display feature messages.
    """

    _popup: popup.Window

    def __init__(self, connection: WebsocketConnection):
        super().__init__()
        uic.loadUi("./ui/home.ui", self)
        apply_stylesheet(self, theme="dark_purple.xml")

        self.connection = connection
        self.widgets = Widgets(self)
        self.phase = 0

    def parse_mouse_press(self, event: QtGui.QMouseEvent, widget_name: str):
        """Parses a mouse press event.

        Avoids repetitive code when displaying feature
        messages.

        :param event: The mouse press event.
        :param widget_name: The name of the widget pressed.
        """
        if event.button() == QtCore.Qt.RightButton:
            feature_message = constants.FEATURE_MESSAGES.get(widget_name)
            self._popup = popup.Window(feature_message)

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
        self.widgets.chat_box_model.appendRow(message_item)

        if author == self.connection.username:
            entry_index = self.widgets.chat_box_model.index(
                self.widgets.chat_box_model.rowCount() - 1, 0
            )
            selection_model = self.widgets.chat_box.selectionModel()
            selection_model.select(entry_index, QtCore.QItemSelectionModel.Select)

    @asyncSlot()
    async def run_code(self):
        """Triggered when run code button is clicked.

        Manages the execution of code and the processing
        of the code output.
        """
        self.widgets.code_output.setPlainText("Running code...")

        async with self.connection.session.post(
            "https://emkc.org/api/v2/piston/execute",
            json={
                "language": "py",
                "version": "3.10",
                "files": [{"content": self.widgets.code_input.toPlainText()}],
            },
        ) as request:
            response: Dict[Any, Union[str, int]] = (await request.json())["run"]
        self.widgets.code_output.setMarkdown(
            f"```py\n$ python code.py\n{response['output']}```\nCode exited with code {response['code']}"
        )

    @asyncSlot()
    async def send_message(self):
        """Triggered when a user presses the send button."""
        message = self.widgets.message_box.text()
        self.append_message(message)

        self.widgets.message_box.clear()
        await self.connection.send(
            {"op": 0, "data": {"message": message, "author": self.connection.username}}
        )
