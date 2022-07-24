import re

import constants
from PyQt5 import QtGui

# fmt: off
__all__ = (
    'Highlighter'
)
# fmt: on


class Highlighter(QtGui.QSyntaxHighlighter):
    """Highlighter class for highlighting text."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._mapping = {}
        self.set_up()

    def highlightBlock(self, text_block):
        """Called when the text block changes.

        :param text_block: The text block to highlight.
        """
        for pattern, fmt in self._mapping.items():
            for match in re.finditer(pattern, text_block):
                start, end = match.span()
                self.setFormat(start, end - start, fmt)

    def set_up(self):
        """Set up the highlighting."""
        functions = [
            s for s in globals()["__builtins__"] if s.islower() and not s.startswith("_")
        ]
        keywords = list(map(lambda m: "" + m, constants.KEYWORDS))

        # fmt: off
        syntax_dictionary = {
            "integers": {
                "colour": "acc4a0",
                "pattern": r"[0-9]",
            },
            "variables": {
                "colour": "8bc3e0",
                "pattern": r".+?(?==)",
            },
            "functions": {
                "colour": "d2d2a3",
                "pattern": r"(?:(?![^\(\n\r])|$)|".join(functions),
            },
            "quotes": {
                "colour": "c78c74",
                "pattern": r"\"(.*?)\"",
            },
            "keywords": {
                "colour": "c586c0",
                "pattern": r"(?:(?![^\s\n\r])|$)|".join(keywords),
            },
            "import": {
                "colour": "47af9a",
                "pattern": r"(?m)(?<=\bimport ).*",
            },
            "logical": {
                "colour": "569cd6",
                "pattern": r"(?:(?![^\s\n\r])|$)|".join(constants.LOGICAL),
            },
            "class": {
                "colour": "47af9a",
                "pattern": r"(?m)((?<=\bclass ).*(.*?).+?(?=:))",
            },
            "def": {
                "colour": "d2d2a3",
                "pattern": r"(?m)(?<=\bdef ).*(.*?)\(",
            },
            "brackets": {
                "colour": "f8d101",
                "pattern": "|".join(constants.BRACKETS),
            },
        }
        # fmt: on

        for syntax in syntax_dictionary.values():
            class_format = QtGui.QTextCharFormat()
            class_format.setForeground(QtGui.QColor("#" + syntax["colour"]))
            class_format.setFontWeight(QtGui.QFont.Bold)

            self._mapping[syntax["pattern"]] = class_format
