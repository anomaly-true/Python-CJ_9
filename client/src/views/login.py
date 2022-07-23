from __future__ import annotations

from random import choice

from aiohttp import ClientConnectionError, ClientSession
from connection import WebsocketConnection, WebsocketHandler
from constants import ALL_THEMES, FEATURE_MESSAGES
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from qasync import asyncClose, asyncSlot
from qt_material import apply_stylesheet
from qtwidgets import AnimatedToggle

from . import home, popup

# fmt: off
__all__ = (
    'Window',
)
# fmt: on


class Window(QtWidgets.QMainWindow):
    """Represents the graphical login screen.

    :attr popup: The popup window that is attatched to the
                 Window class in order to keep it visible and
                 isn't immediately destroyed because of local
                 variables being deleted.
    :param session: The session used to login.
    """

    popup: popup.Window

    def __init__(self, session: ClientSession):
        super().__init__()
        uic.loadUi("./ui/login.ui", self)

        button: QtWidgets.QPushButton = self.findChild(
            QtWidgets.QPushButton, "loginButton"
        )
        button.clicked.connect(self.on_login)

        vertical_box: QtWidgets.QVBoxLayout = self.findChild(
            QtWidgets.QVBoxLayout, "verticalLayout_7"
        )

        toggle = AnimatedToggle(checked_color="#FFFFFF", pulse_checked_color="#000000")
        toggle.setMaximumSize(100, 100)
        toggle.clicked.connect(self.theme_toggle)
        vertical_box.addChildWidget(toggle)

        self.error_message: QtWidgets.QLabel = self.findChild(
            QtWidgets.QLabel, "errorMessage"
        )
        self.username_input: QtWidgets.QLineEdit = self.findChild(
            QtWidgets.QLineEdit, "usernameLineEdit"
        )
        self.password_input: QtWidgets.QLineEdit = self.findChild(
            QtWidgets.QLineEdit, "passwordLineEdit"
        )
        self.username_input.mousePressEvent = self.login_form_mouse_press
        self.password_input.mousePressEvent = self.login_form_mouse_press

        self.username_input.returnPressed.connect(self.on_login)
        self.password_input.returnPressed.connect(self.on_login)

        self.session = session

        self.light_mode: bool = True
        self.is_running: bool = True

        self.theme_colour: str = choice(ALL_THEMES)
        apply_stylesheet(self, theme=f"light_{self.theme_colour}.xml")

        central_widget: QtWidgets.QWidget = self.findChild(QtWidgets.QWidget, "centralwidget")
        central_widget.setMouseTracking(True)
        central_widget.mouseMoveEvent = self.on_mouse_move
        central_widget.mousePressEvent = self.central_widget_mouse_press
        self.mouse_moves = []

    def parse_mouse_press(self, event: QtGui.QMouseEvent, widget_name: str):
        """Parses a mouse press event.

        Created to avoid repetitive code.

        :param: event: The mouse press event.
        :param widget_name: The name of the widget pressed.
        """
        if event.button() == QtCore.Qt.RightButton:
            feature_message = FEATURE_MESSAGES.get(widget_name)
            self.popup = popup.Window(feature_message)

    def central_widget_mouse_press(self, event: QtGui.QMouseEvent):
        """Central widget clicked."""
        self.parse_mouse_press(event, "centralwidget")

    def login_form_mouse_press(self, event: QtGui.QMouseEvent):
        """Login form clicked."""
        self.parse_mouse_press(event, "loginform")

    def toggle_mouse_press(self, event: QtGui.QMouseEvent):
        """Toggle button clicked."""
        self.parse_mouse_press(event, "toggle")

    def on_mouse_move(self, event):
        """Triggered when the mouse moves.

        Sometimes changes the theme according to the ammount
        of mouse moves.

        :param: event: The mouse move event.
        """
        if event.buttons() == QtCore.Qt.NoButton:
            self.mouse_moves.append(0)
            if len(self.mouse_moves) % 500 == 0:
                apply_stylesheet(self, theme=f"{'light' if self.light_mode else 'dark'}_{choice(ALL_THEMES)}.xml")

    def theme_toggle(self):
        """Called when the light mode toggle is clicked."""
        self.light_mode = choice([True, False, False])
        apply_stylesheet(self, theme=f"{'light' if self.light_mode else 'dark'}_{self.theme_colour}.xml")

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

        async with self.session.get(
            "http://127.0.0.1:8080/login",
            json={"username": username_text, "password": password_text},
        ) as request:
            response = await request.json()
            print(response)
            if "error" in response:
                return self.error_message.setText("ERROR: " + response["error"])

        try:
            websocket = await WebsocketHandler.from_user(self.session, response["token"])

            connection = WebsocketConnection(
                username=response["username"], session=self.session, websocket=websocket
            )

            self.destroy()
            home_window = home.Window(connection)
            home_window.show()

            while True:
                await websocket.listen(home_window)
        except ClientConnectionError:
            self.is_running = False
            print("Websocket disconnected")
