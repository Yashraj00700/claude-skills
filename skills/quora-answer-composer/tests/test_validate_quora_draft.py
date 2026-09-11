import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from validate_quora_draft import validate  # noqa: E402


def rules_hit(text):
    return {f.rule for f in validate(text).findings}


def test_clean_answer_has_no_findings():
    text = (
        "This is a normal paragraph with a reasonable length and no issues.\n"
        "\n"
        "This is a second paragraph, separated by a blank line as Quora requires.\n"
    )
    report = validate(text)
    assert report.is_clean, report.findings


def test_missing_blank_line_between_paragraphs_is_flagged():
    text = "First paragraph ends here.\nSecond paragraph starts immediately.\n"
    assert "paragraph-spacing" in rules_hit(text)


def test_manual_dash_list_is_flagged():
    text = "Some intro text.\n\n- first item\n- second item\n"
    assert "manual-list" in rules_hit(text)


def test_manual_numbered_list_is_flagged():
    text = "Some intro text.\n\n1. first item\n2. second item\n"
    assert "manual-list" in rules_hit(text)


def test_manual_blockquote_is_flagged():
    text = "Some intro text.\n\n> a quoted line\n"
    assert "manual-blockquote" in rules_hit(text)


def test_bold_overuse_is_flagged():
    text = " ".join(f"**word{i}**" for i in range(20))
    assert "bold-overuse" in rules_hit(text)


def test_light_bold_is_not_flagged():
    text = "This is a long paragraph with just **one** bolded word among many many other plain words here today."
    assert "bold-overuse" not in rules_hit(text)


def test_long_paragraph_is_flagged():
    text = " ".join(["word"] * 150) + "\n"
    assert "wall-of-text" in rules_hit(text)


def test_short_paragraph_is_not_flagged_for_length():
    text = "A short paragraph.\n"
    assert "wall-of-text" not in rules_hit(text)


def test_list_lines_are_exempt_from_paragraph_spacing_check():
    # Consecutive list items shouldn't trigger the paragraph-spacing rule
    # even without a blank line between them — but they DO trigger
    # manual-list, which is the correct, more specific finding.
    text = "- item one.\n- Item two.\n"
    hits = rules_hit(text)
    assert "manual-list" in hits
    assert "paragraph-spacing" not in hits


def test_empty_input_is_clean():
    assert validate("").is_clean
