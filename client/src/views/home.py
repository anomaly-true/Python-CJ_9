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


class LevelsView:
    """Holds information about the levels list view.

    :param list_view: The list view containing the `model`
    :param model: The item model containing all the levels.
    :param selection_model: The item selection model used
                            to select the level.
    """

    def __init__(
        self,
        list_view: QtWidgets.QListView,
        *,
        model: QtGui.QStandardItemModel,
        selection_model: QtCore.QItemSelectionModel,
    ):
        self.list_view = list_view
        self.model = model
        self.selection_model = selection_model

    @classmethod
    def from_window(cls, window: Window) -> LevelsView:
        """Creastes the ItemModel from the main window.

        :param window: The main window.
        """
        list_view: QtWidgets.QListView = window.findChild(QtWidgets.QListView, "listView")
        list_view.mousePressEvent = window.list_view_mouse_press

        list_view.setMouseTracking(True)
        list_view.mouseMoveEvent = lambda _: None

        model = QtGui.QStandardItemModel()
        list_view.setModel(model)

        for i in map(str, range(1, 100)):
            item = QtGui.QStandardItem(f"Level {i}")
            model.appendRow(item)

        level_selection_model = list_view.selectionModel()
        return cls(list_view, model=model, selection_model=level_selection_model)


class Widgets:
    """Manages all the widgets.

    Keeps code clean and systematic.

    :param window: The window with all the widgets.
    """

    def __init__(self, window: Window):
        self.levels_view: LevelsView = LevelsView.from_window(window)

        # fmt: off
        self.message_box: QtWidgets.QLineEdit = window.findChild(QtWidgets.QLineEdit, "messageBox")
        self.send_button: QtWidgets.QPushButton = window.findChild(QtWidgets.QPushButton, "sendButton")
        self.code_input: QtWidgets.QTextEdit = window.findChild(QtWidgets.QTextEdit, "codeInput")
        self.code_output: QtWidgets.QTextEdit = window.findChild(QtWidgets.QTextEdit, "codeOutput")
        self.run_button: QtWidgets.QPushButton = window.findChild(QtWidgets.QPushButton, "runCode")
        self.next_level: QtWidgets.QPushButton = window.findChild(QtWidgets.QPushButton, "nextLevel")
        self.chat_box: QtWidgets.QListView = window.findChild(QtWidgets.QListView, "chatBox")
        self.level_complete: QtWidgets.QWidget = window.findChild(QtWidgets.QWidget, "levelComplete")
        # fmt: on

        self.message_box.returnPressed.connect(window.send_message)
        self.send_button.clicked.connect(window.send_message)
        self.run_button.clicked.connect(window.run_code)

        self.next_level.clicked.connect(window.next_level)

        self.chat_box_model = QtGui.QStandardItemModel()
        self.chat_box.setModel(self.chat_box_model)

        self.highlighter = Highlighter()
        self.highlighter.setDocument(self.code_input.document())

    def set_level(self, level: int, /) -> Level:
        """Sets the code input text.

        :param level: The code level.
        :return: The Level object created according
                the the level.
        """
        self.level_complete.hide()
        self.code_output.clear()

        self.levels_view.list_view.reset()
        entry_index = self.levels_view.model.index(level - 1, 0)
        self.levels_view.selection_model.select(
            entry_index, QtCore.QItemSelectionModel.Select
        )

        return Level(self.code_input, level=level)


class Level:
    """Represents an individual level.

    :param code_input: The code input TextEdit to set
                        the markdown to.
    :param level: The level to represent.
    """

    def __init__(self, code_input: QtWidgets.QTextEdit, *, level: int):
        self.level = level

        level: Dict[int, Union[str, int]] = constants.LEVELS.get(level)

        self.output: str = level["output"].strip()
        self.response_code = level["response_code"]

        code: str = level["code"]
        code_input.setMarkdown(f"```py\n{code}\n```")


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
        self.completed_levels = []

        self.widgets = Widgets(self)
        self.level = self.widgets.set_level(1)

    def next_level(self):
        """Sets the level to the next_level."""
        self.level = self.widgets.set_level(self.level.level + 1)

    def list_view_mouse_press(self, event: QtGui.QMouseEvent):
        """List view mouse press event.

        Handles the mouse press event of the list view
        ensuring that users can't skip levels.

        :param event: The mouse press event.
        """
        position = self.mapFromGlobal(QtGui.QCursor.pos())
        row = self.widgets.levels_view.list_view.indexAt(position).row()

        if not self.completed_levels:
            return
        if row in self.completed_levels + [max(self.completed_levels) + 1]:
            super(
                QtWidgets.QListView, self.widgets.levels_view.list_view
            ).mousePressEvent(event)
            self.widgets.set_level(row)

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
        print(response["output"].strip(), self.level.output)
        if (
            response["output"].strip() == self.level.output
            and response["code"] == self.level.response_code
        ):
            self.widgets.level_complete.show()
            self.completed_levels.append(self.level.level)

    @asyncSlot()
    async def send_message(self):
        """Triggered when a user presses the send button."""
        message = self.widgets.message_box.text()
        self.append_message(message)

        self.widgets.message_box.clear()
        await self.connection.send(
            {"op": 0, "data": {"message": message, "author": self.connection.username}}
        )
