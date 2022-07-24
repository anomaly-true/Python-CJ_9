FEATURE_MESSAGES = {
    "centralwidget": (
        "When you move your mouse alot the theme changes..."
        "Talk about getting excersise while coding."
    ),
    "loginform": (
        "The password is useless without the username..."
        "You can guess a password but the username is longer so harder to guess."
    ),
    "toggle": ("Users don't always know what they want..." "So we choose it for them!"),
    "codeinput": (
        "We need to teach the users that they can't always just delete everything"
        "And except things to work."
    ),
}
ALL_THEMES = [
    "amber",
    "blue",
    "cyan",
    "lightgreen",
    "pink",
    "purple",
    "red",
    "teal",
    "yellow",
]


# REGEX

KEYWORDS = [
    "import",
    "from",
    "if",
    "return",
    "pass",
    "continue",
    "yield",
    "break",
    "as",
    "for",
    "from",
    "await",
    "assert",
    "del",
    "elif",
    "else",
    "try",
    "except",
    "finally",
    "raise",
    "with",
    "while",
]
LOGICAL = [
    "def",
    "class",
    "and",
    "not",
    "or",
    "is",
    "global",
    "nonlocal",
    "async",
    "in"
]
BRACKETS = [
    r"\(",
    r"\)",
    r"\[",
    r"\]",
    r"\{",
    r"\}",
]
