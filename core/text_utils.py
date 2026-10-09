import re

# --- searching: make different spellings of one Arabic word identical ---
_MARKS = re.compile("[\u064B-\u0652\u0640]")  # diacritics (harakat) and tatweel (the stretching letter)
_LETTERS = str.maketrans({"أ": "ا", "إ": "ا", "آ": "ا", "ة": "ه", "ى": "ي"})

# --- checking the model's output: is it written in the video's language? ---
_ARABIC = re.compile("[\u0621-\u064A]")  # Arabic letters only (no digits, marks or punctuation)
_LATIN = re.compile("[A-Za-z]")
_FOREIGN = re.compile("[\u0400-\u04FF\u3040-\u30FF\u3400-\u9FFF\uAC00-\uD7AF]")  # Cyrillic, Japanese, Chinese, Korean
ARABIC_SHARE = 0.5  # in an Arabic video, at least this share of the letters must be Arabic

#makes different spellings of an Arabic word equal, so search works
def normalize_arabic(text):
    """Make different spellings of the same Arabic word identical, for searching only.

    Show the user the original text, never the normalized one.
    """
    return _MARKS.sub("", text).translate(_LETTERS)

#checks that the model’s text is in the right language.
def wrong_script(text, language):
    """True if the text is written in a script that does not belong to the video's language.

    Cyrillic, Japanese, Chinese and Korean are wrong in every video.
    English video: any Arabic letter is wrong.
    Arabic video: Arabic must be most of the letters. A few English terms (SSD, RAM) are fine.
    Symbols and emoji (→, ≤, €) are never checked.
    """
    if _FOREIGN.search(text):
        return True
    arabic = len(_ARABIC.findall(text))
    if language == "en":
        return arabic > 0
    if language == "ar":
        letters = arabic + len(_LATIN.findall(text))
        return letters > 0 and arabic / letters < ARABIC_SHARE
    return False