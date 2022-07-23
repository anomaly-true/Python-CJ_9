from PyQt5 import QtWidgets, uic
from qt_material import apply_stylesheet

# fmt: off
__all__ = (
    'Window',
)
# fmt: on


class Window(QtWidgets.QWidget):
    """Represents a PopUp window.

    Shows a window with a short message about the
    feature of the widget clicked to fit into the theme.

    :param feature: The feature message to display.
    """

    def __init__(self, feature: str):
        super().__init__()
        uic.loadUi("ui/popup.ui", self)
        apply_stylesheet(self, theme="light_purple.xml")

        self.feature_box: QtWidgets.QTextEdit = self.findChild(QtWidgets.QTextEdit, "featureBox")
        self.feature_box.setText(self.feature_box.toPlainText().replace("{feature}", feature))

        self.show()
