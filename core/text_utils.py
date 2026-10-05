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

def wrong_script(text, language):
    """True if the text uses a script that does not belong to the video's language.

    Japanese or Chinese letters are wrong in every video. Arabic letters are also wrong in an English video.
    Latin letters are fine in an Arabic video (SSD, RAM), so they are not checked there.
    """
    if has_foreign_script(text):
        return True
    return language == "en" and bool(re.search(r"[\u0600-\u06FF]", text))