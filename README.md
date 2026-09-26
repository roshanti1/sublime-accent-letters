# Accent Letters for Sublime Text

Two commands in the command palette:

| Command | What it does |
| --- | --- |
| **Accent Letters: Insert Accented Letter** | Search 682 letters from 55 languages, typed at every cursor |
| **Accent Letters: Remove Accents** | Rewrite the selection without its accents |

Search by the letter itself, its Unicode name, its accent mark, a language, a code point or an Alt
code — `two dots`, `spanish`, `00e9` and `é` all find é.

## Settings

Preferences ▸ Package Settings, or the palette entry **Preferences: Accent Letters Settings**.

| Setting | Default | |
| --- | --- | --- |
| `convert_special` | `true` | ø ł đ ß æ œ þ have no plain form in Unicode, so they go through a table: ø → o, ß → ss, æ → ae |
| `german_style` | `"drop"` | `"drop"` gives ä → a. `"spell"` gives ä → ae |

## Requirements

Sublime Text 4. The package declares Python 3.8 in `.python-version`; ST3's plugin host is Python
3.3, which has no f-strings, and ST3 has been end-of-life for years.

## What it will not do

Anything that is not a Latin letter comes back exactly as it arrived. The Devanagari virama, Thai
vowels and an emoji variation selector are all combining marks, and stripping marks by category
rewrites those scripts into different words. **Remove Accents** needs a selection — it will not
rewrite a whole file because nothing was selected.

## Building

```
node extension/build.mjs   # refreshes letters.json
node sublime/build.mjs     # checks, then writes dist/AccentLetters.sublime-package
```

`build.mjs` refuses to package if a palette caption names a command no class defines, if
`.python-version` is not 3.8, or if the harness fails.

## Tests

```
python3 sublime/test/harness.py   # stubs Sublime, drives the real plugin
python3 test/conformance.py       # the shared accent fixture, against every Python surface
```

The harness stubs `sublime` and `sublime_plugin` and exercises the row shaping, the shipped
settings defaults and the accent rules. It cannot prove the quick panel looks right — only that
every row is well formed and every search term still matches.
