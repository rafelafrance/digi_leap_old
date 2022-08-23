"""Build lines of text from the OCR output."""
import collections
import functools
import unicodedata

import regex as re


class OcrResults:
    """Constants for working with OCR results."""

    # When there is no clear "winner" for a character in the multiple alignment of
    # a set of strings I sort the characters by unicode category as a tiebreaker
    category = {
        "Lu": 20,
        "Ll": 20,
        "Lt": 20,
        "Lm": 20,
        "Lo": 20,
        "Nd": 30,
        "Nl": 60,
        "No": 60,
        "Pc": 70,
        "Pd": 40,
        "Ps": 50,
        "Pe": 50,
        "Pi": 50,
        "Pf": 50,
        "Po": 10,
        "Sm": 99,
        "Sc": 90,
        "So": 90,
        "Zs": 80,
    }

    # As, above, but if a character has a category of "punctuation other" then I
    # sort by the character itself
    po = {
        ".": 1,
        ",": 2,
        ":": 2,
        ";": 2,
        "!": 5,
        '"': 5,
        "'": 5,
        "*": 5,
        "/": 5,
        "%": 6,
        "&": 6,
    }

    # Substitutions performed on a consensus sequence
    substitutions = [
        # Remove gaps
        ("⋄", ""),
        # Replace underscores with spaces
        ("_", " "),
        # Replace ™ trademark with a double quote
        ("™", '"'),
        # Remove space before some punctuation: x . -> x.
        (r"(\S)\s([;:.,\)\]\}])", r"\1\2"),
        # Compress spaces
        (r"\s\s+", " "),
        # Convert single capital letter, punctuation to capital dot: L' -> L.
        (r"(\p{L}\s\p{Lu})\p{Po}", r"\1."),
        # Add spaces around an ampersand &
        (r"(\w)&", r"\1 &"),
        (r"&(\w)", r"& \1"),
        # Handle multiple dots ..
        (r"\.\.+", r"\."),
        # Confusion between dots . and colons :
        (r"::", r"\.:"),
        # Double single quotes ’’ should be a double quote "
        (r"['’]['’]", r"\""),
    ]


def sort_lines(lines: list[str], line_align) -> list[str]:
    """Sort the lines by Levenshtein distance."""
    if len(lines) <= 2:
        return lines

    # levenshtein_all() returns a sorted array of tuples (score, index_1, index_2)
    distances = line_align.levenshtein_all(lines)

    order = {}  # Dicts preserve insertion order, sets do not
    for dist in distances:
        order[dist[1]] = 1
        order[dist[2]] = 1

    ordered = [lines[k] for k in order.keys()]
    return ordered


def align_lines(lines: list[str], line_align) -> list[str]:
    """Do a multiple alignment of the text copies."""
    aligned = line_align.align(lines)
    return aligned


def _char_key(char):
    """Get the character sort order."""
    order = OcrResults.category.get(unicodedata.category(char), 100)
    order = OcrResults.po.get(char, order)
    return order, char


def _char_options(aligned):
    options = []
    str_len = len(aligned[0])

    for i in range(str_len):
        counts = collections.Counter(s[i] for s in aligned).most_common()
        count = counts[0][1]
        chars = [c[0] for c in counts if c[1] == count]
        chars = sorted(chars, key=_char_key)  # Sort order is a fallback
        options.append(chars)
    return options


def _get_choices(options):
    """Recursively build all of the choices presented by a multiple alignment."""
    all_choices = []

    def _build_choices(opts, choice):
        if not opts:
            ln = "".join(choice)
            all_choices.append(ln)
            return
        for opt in opts[0]:
            _build_choices(opts[1:], choice + [opt])

    _build_choices(options, [])
    return all_choices


def _copies_key(choice, spell_well=None):
    hits = spell_well.hits(choice)
    count = sum(1 for c in choice if c not in "⋄_ ")
    return hits, count, choice


def consensus(aligned: list[str], spell_well, threshold=2**16) -> str:
    """Build a consensus string from the aligned copies.

    Look at all characters of the multiple alignment and choose the one that makes a
    string with the best score, or if there are too few or too many choices just choose
    characters by their sort order.
    """
    options = _char_options(aligned)
    count = functools.reduce(lambda x, y: x * len(y), options, 1)
    if count == 1 or count > threshold:
        cons = "".join([o[0] for o in options])
    else:
        key_func = functools.partial(_copies_key, spell_well=spell_well)
        choices = _get_choices(options)
        choices = sorted(choices, key=key_func, reverse=True)
        cons = choices[0]

    return cons


def substitute(line: str) -> str:
    """Perform simple substitutions on a consensus string."""
    for old, new in OcrResults.substitutions:
        line = re.sub(old, new, line)
    return line


def add_spaces(line, spell_well, vocab_len=3):
    """Add spaces between words.

    OCR engines will remove spaces between words. This function looks for a non-word
    and sees if adding a space will create 2 (or 1) word.
    For example: "SouthFlorida" becomes "South Florida".
    """
    tokens = spell_well.tokenize(line)

    new = []
    for token in tokens:
        if token.isspace() or spell_well.is_word(token) or len(token) < vocab_len:
            new.append(token)
        else:
            candidates = []
            for i in range(1, len(token) - 1):
                freq1 = spell_well.freq(token[:i])
                freq2 = spell_well.freq(token[i:])
                if freq1 or freq2:
                    sum_ = freq1 + freq2
                    count = int(freq1 > 0) + int(freq2 > 0)
                    candidates.append((count, sum_, i))
            if candidates:
                i = sorted(candidates, reverse=True)[0][2]
                new.append(token[:i])
                new.append(" ")
                new.append(token[i:])
            else:
                new.append(token)

    return line


def remove_spaces(line, spell_well):
    """Remove extra spaces in words.

    OCR engines will put spaces where there shouldn't be any. This is a simple
    scanner that looks for 2 non-words that make a new word when a space is removed.
    For example: "w est" becomes "west".
    """
    tokens = spell_well.tokenize(line)

    if len(tokens) <= 2:
        return line

    new = tokens[:2]

    for i in range(2, len(tokens)):
        prev = tokens[i - 2]
        between = tokens[i - 1]
        curr = tokens[i]

        if (
            between.isspace()
            and spell_well.is_word(prev + curr)
            and not (spell_well.is_word(prev) or spell_well.is_word(curr))
        ):
            new.pop()  # Remove between
            new.pop()  # Remove prev
            new.append(prev + curr)
        else:
            new.append(tokens[i])

    return "".join(new)


def correct(line, spell_well):
    new = []
    for token in spell_well.tokenize(line):
        if spell_well.is_letters(token):
            token = spell_well.correct(token)
        new.append(token)
    return "".join(new)
