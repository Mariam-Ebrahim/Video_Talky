import re

_MARKS = re.compile("[\u064B-\u0652\u0640]")  # diacritics (harakat) and tatweel (the stretching letter)
_LETTERS = str.maketrans({"أ": "ا", "إ": "ا", "آ": "ا", "ة": "ه", "ى": "ي"})


def normalize_arabic(text):
    """Make different spellings of the same Arabic word identical, for searching only.

    Show the user the original text, never the normalized one.
    """
    return _MARKS.sub("", text).translate(_LETTERS)

def has_foreign_script(text):
    """True if the text has letters outside Latin and Arabic, e.g. Japanese or Chinese characters."""
    return bool(re.search(r"[^\u0000-\u024F\u0600-\u06FF\u2000-\u206F\s]", text))