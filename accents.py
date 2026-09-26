"""The Accent Letters rules, in Python, for the GIMP plug-in.

Byte-for-byte the same behaviour as the website, the iOS/macOS and Android apps and every other
add-on. They cannot import from one another, so all of them are held to one shared fixture —
test/accent-conformance.json in the accentletters.wiki repository. gimp/test/conformance.py runs it
against this file.

Standard library only. GIMP ships its own Python and a plug-in cannot assume anything else is
installed, so there is no `regex` module here and no third-party Unicode tables.
"""

import unicodedata

# Letters with no canonical decomposition: NFD leaves them exactly as they are, so they need a table.
SPECIAL = {
    'ø': 'o', 'Ø': 'O', 'ł': 'l', 'Ł': 'L', 'đ': 'd', 'Đ': 'D', 'ħ': 'h', 'Ħ': 'H',
    'ı': 'i', 'ŧ': 't', 'Ŧ': 'T', 'ß': 'ss', 'ẞ': 'SS', 'æ': 'ae', 'Æ': 'AE',
    'œ': 'oe', 'Œ': 'OE', 'þ': 'th', 'Þ': 'Th', 'ð': 'd', 'Ð': 'D',
}
GERMAN = {'ä': 'ae', 'ö': 'oe', 'ü': 'ue', 'Ä': 'Ae', 'Ö': 'Oe', 'Ü': 'Ue'}


def _is_mark(ch):
    return unicodedata.category(ch).startswith('M')


def _is_latin(ch):
    """Whether a character belongs to the Latin script.

    Python's unicodedata exposes no script property, and the `regex` module that provides
    \\p{Script=Latin} is not in the standard library — so this reads the character's own Unicode
    name, which every Latin letter begins with ("LATIN SMALL LETTER E WITH ACUTE"). It is exact for
    letters, which is all that is asked of it: a non-letter is never stripped anyway.
    """
    try:
        return unicodedata.name(ch).startswith('LATIN')
    except ValueError:
        return False  # unnamed (control, private use, surrogate): never Latin, never stripped


def _clusters(text):
    """Split into (base, marks) pairs, walking the ORIGINAL text with no normalisation first.

    Anything this function does not strip has to come back byte for byte. Normalising to NFC up
    front rewrote text it then left alone — decomposed Cyrillic и + breve came back as й, and
    decomposed Hangul jamo were composed into 한 — while reporting nothing had changed. NFD up front
    is worse: it splits a Hangul syllable into jamo, which are letters, not marks.
    """
    out = []
    i = 0
    while i < len(text):
        base = text[i]
        i += 1
        marks = ''
        while i < len(text) and _is_mark(text[i]):
            marks += text[i]
            i += 1
        out.append((base, marks))
    return out


def _strip_cluster(base, marks, special=True, german=False):
    """One base character plus every combining mark that follows it.

    A cluster at a time, not a code point at a time, and both reasons were real bugs:

      - a + acute + dot-below has no single code point carrying both marks, so per-code-point
        stripping left one mark attached and returned a still-accented letter.
      - a combining mark is not always an accent. The Devanagari virama, Thai vowels, Arabic harakat
        and an emoji variation selector are all marks, so only a Latin base is ever stripped.
    """
    if german:
        # Read off the COMPOSED cluster so decomposed input spells out too — Swift and Kotlin
        # compare text by canonical equivalence and the surfaces must not disagree.
        composed = unicodedata.normalize('NFC', base + marks)
        if composed in GERMAN:
            return GERMAN[composed]

    if not _is_latin(base):
        return base + marks

    # Decompose the WHOLE cluster, so a mark NFC could not attach is dropped with the rest. NFD,
    # never NFKD: a compatibility decomposition would also rewrite ﬁ to fi and ½ to 1⁄2.
    bare = ''.join(c for c in unicodedata.normalize('NFD', base + marks) if not _is_mark(c))
    if special:
        bare = ''.join(SPECIAL.get(c, c) for c in bare)
    return bare


def remove_accents(text, special=True, german=False):
    """Strip the accents from Latin letters and leave everything else exactly as it arrived."""
    return ''.join(_strip_cluster(b, m, special, german) for b, m in _clusters(text))
