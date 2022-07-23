from __future__ import annotations

from typing import TYPE_CHECKING

import jedi
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from qasync import asyncSlot
from qt_material import apply_stylesheet

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

    def __init__(self, connection: WebsocketConnection):
        super().__init__()
        uic.loadUi("./ui/home.ui", self)

        apply_stylesheet(self, theme="dark_purple.xml")

        self.connection = connection

        self.chat_box: QtWidgets.QTextEdit = self.findChild(
            QtWidgets.QTextEdit, "chatBox"
        )
        self.message_box: QtWidgets.QLineEdit = self.findChild(
            QtWidgets.QLineEdit, "messageBox"
        )
        self.send_button: QtWidgets.QPushButton = self.findChild(
            QtWidgets.QPushButton, "sendButton"
        )
        self.text_edit: QtWidgets.QTextEdit = self.findChild(
            QtWidgets.QTextEdit, "textEdit"
        )
#         self.text_edit.setMarkdown("""\
# ```py
# import unittest

# class LevelOneTest(unittest.TestCase):
#     pass
# ```
# """)
        self.text_edit.textChanged.connect(self.on_text_change)
        self.message_box.returnPressed.connect(self.send_message)
        self.send_button.clicked.connect(self.send_message)

        list_view: QtWidgets.QListView = self.findChild(QtWidgets.QListView, "listView")

        model = QtGui.QStandardItemModel()
        list_view.setModel(model)

        for i in map(str, range(100)):
            item = QtGui.QStandardItem(i)
            model.appendRow(item)

        first_entry_index = model.index(0, 0)
        selection_model = list_view.selectionModel()
        selection_model.select(first_entry_index, QtCore.QItemSelectionModel.Select)

    def append_message(self, message: str, author: str = None):
        """Appends a message to the chat box.

        :param message: The message to append to the chat box.
        :param username: The username of the message author.
        """
        if author is None:
            author = self.connection.username

        self.chat_box.setText(f"{self.chat_box.toPlainText()}\n{author}: {message}")

    def on_text_change(self):
        """Triggered when the user types in the main text edit.

        Runs jedi on the text inputted to act as an
        intellisence input.
        """
        print("text changed")
        cursor = self.text_edit.textCursor()
        line, column = cursor.blockNumber(), cursor.positionInBlock()
        script = jedi.Script(self.text_edit.toPlainText())

        completions = script.complete(line+1, column)
        if completions:
            print(completions)
        # for line in self.text_edit.toPlainText().splitlines():
        #     print(line)

    @asyncSlot()
    async def send_message(self):
        """Triggered when a user presses the send button."""
        message = self.message_box.text()
        self.append_message(message)

        self.message_box.clear()
        await self.connection.send(
            {"op": 0, "data": {"message": message, "author": self.connection.username}}
        )
