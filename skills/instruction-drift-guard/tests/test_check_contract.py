import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from check_contract import validate  # noqa: E402


def rules_hit(text, target_path, contract):
    return {f.rule for f in validate(text, target_path, contract).findings}


def test_clean_python_with_no_comments_contract():
    text = "def add(a, b):\n    return a + b\n"
    contract = {"no_comments": True}
    report = validate(text, "file.py", contract)
    assert report.is_clean, report.findings


def test_python_line_comment_is_flagged():
    text = "# this explains it\ndef add(a, b):\n    return a + b\n"
    contract = {"no_comments": True}
    assert "no-comments" in rules_hit(text, "file.py", contract)


def test_js_block_comment_is_flagged():
    text = "/* explains */\nfunction add(a, b) { return a + b; }\n"
    contract = {"no_comments": True}
    assert "no-comments" in rules_hit(text, "file.js", contract)


def test_no_comments_ignored_for_non_code_extension():
    text = "# This is a markdown heading, not a comment\n"
    contract = {"no_comments": True}
    report = validate(text, "notes.md", contract)
    assert report.is_clean


def test_banned_phrase_is_flagged_case_insensitively():
    text = "In today's fast-paced world, this matters.\n"
    contract = {"banned_phrases": ["in today's fast-paced world"]}
    assert "banned-phrase" in rules_hit(text, "notes.md", contract)


def test_banned_char_em_dash_is_flagged():
    text = "This is one idea—and this is another.\n"
    contract = {"banned_chars": ["—"]}
    assert "banned-char" in rules_hit(text, "notes.md", contract)


def test_curly_quotes_flagged_when_straight_required():
    text = "She said “hello” to me.\n"
    contract = {"quote_style": "straight"}
    assert "quote-style" in rules_hit(text, "notes.md", contract)


def test_straight_quotes_not_flagged_when_straight_required():
    text = 'She said "hello" to me.\n'
    contract = {"quote_style": "straight"}
    report = validate(text, "notes.md", contract)
    assert report.is_clean


def test_quote_style_ignored_for_code_files():
    # Code legitimately needs straight quotes for syntax even if the prose
    # contract wants curly quotes elsewhere — this must not misfire on code.
    text = 'x = "hello"\n'
    contract = {"quote_style": "curly"}
    report = validate(text, "file.py", contract)
    assert report.is_clean


def test_max_line_length_is_flagged():
    text = "x" * 150 + "\n"
    contract = {"max_line_length": 100}
    assert "line-length" in rules_hit(text, "notes.md", contract)


def test_short_line_not_flagged_for_length():
    text = "short line\n"
    contract = {"max_line_length": 100}
    report = validate(text, "notes.md", contract)
    assert report.is_clean


def test_empty_contract_flags_nothing():
    text = "# comment\nSome long line " + "x" * 200 + "\n"
    report = validate(text, "file.py", {})
    assert report.is_clean
