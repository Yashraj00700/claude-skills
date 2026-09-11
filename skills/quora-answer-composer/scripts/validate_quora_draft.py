#!/usr/bin/env python3
"""Check a draft against Quora's own published formatting guidelines.

Flags the patterns most likely to trigger Quora's "very poor formatting"
collapse: manual list/blockquote characters instead of Quora's native
buttons, missing blank lines between paragraphs, bold overuse, and
overlong paragraphs. Rules are sourced from Quora's Help Center article
"What are good guidelines for formatting answers and posts on Quora?".
"""
from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field

MANUAL_LIST_RE = re.compile(r"^\s*([-*]|\d+[.)])\s+\S")
MANUAL_BLOCKQUOTE_RE = re.compile(r"^\s*>\s*\S")
BOLD_RE = re.compile(r"\*\*[^*\n]+\*\*")
WORD_RE = re.compile(r"\b\w+\b")

MAX_PARAGRAPH_WORDS = 120
MAX_BOLD_WORD_RATIO = 0.15


@dataclass
class Finding:
    line: int
    rule: str
    message: str


@dataclass
class Report:
    findings: list[Finding] = field(default_factory=list)

    @property
    def is_clean(self) -> bool:
        return not self.findings

    def add(self, line: int, rule: str, message: str) -> None:
        self.findings.append(Finding(line, rule, message))


def split_paragraphs(text: str) -> list[tuple[int, str]]:
    """Return (starting_line_number, paragraph_text) pairs."""
    paragraphs = []
    current: list[str] = []
    start_line = 1
    for i, line in enumerate(text.splitlines(), start=1):
        if line.strip() == "":
            if current:
                paragraphs.append((start_line, "\n".join(current)))
                current = []
            continue
        if not current:
            start_line = i
        current.append(line)
    if current:
        paragraphs.append((start_line, "\n".join(current)))
    return paragraphs


def check_missing_blank_lines(text: str, report: Report) -> None:
    lines = text.splitlines()
    for i in range(len(lines) - 1):
        cur, nxt = lines[i].strip(), lines[i + 1].strip()
        if not cur or not nxt:
            continue
        # Two consecutive non-blank, non-list lines that look like separate
        # sentences/paragraphs crammed together without the required blank line.
        if MANUAL_LIST_RE.match(lines[i]) or MANUAL_LIST_RE.match(lines[i + 1]):
            continue
        if cur.endswith((".", "!", "?")) and nxt[:1].isupper():
            report.add(
                i + 2,
                "paragraph-spacing",
                "No blank line before this line — Quora requires a full blank line between paragraphs.",
            )


def check_manual_lists_and_quotes(text: str, report: Report) -> None:
    for i, line in enumerate(text.splitlines(), start=1):
        if MANUAL_LIST_RE.match(line):
            report.add(
                i,
                "manual-list",
                f"Typed list marker on this line — use Quora's bullet/numbered list button instead: {line.strip()!r}",
            )
        if MANUAL_BLOCKQUOTE_RE.match(line):
            report.add(
                i,
                "manual-blockquote",
                f"Typed '>' blockquote — use Quora's blockquote button instead: {line.strip()!r}",
            )


def check_bold_overuse(text: str, report: Report) -> None:
    total_words = len(WORD_RE.findall(text))
    if total_words == 0:
        return
    bold_words = sum(len(WORD_RE.findall(m.group(0))) for m in BOLD_RE.finditer(text))
    ratio = bold_words / total_words
    if ratio > MAX_BOLD_WORD_RATIO:
        report.add(
            0,
            "bold-overuse",
            f"{ratio:.0%} of words are bolded (Quora: use bold 'sparingly', never 'mostly bold'). Cut it down.",
        )


def check_paragraph_length(text: str, report: Report) -> None:
    for start_line, para in split_paragraphs(text):
        if MANUAL_LIST_RE.match(para) or MANUAL_BLOCKQUOTE_RE.match(para):
            continue
        word_count = len(WORD_RE.findall(para))
        if word_count > MAX_PARAGRAPH_WORDS:
            report.add(
                start_line,
                "wall-of-text",
                f"Paragraph is {word_count} words — break it up with a subheading or paragraph split.",
            )


def validate(text: str) -> Report:
    report = Report()
    check_missing_blank_lines(text, report)
    check_manual_lists_and_quotes(text, report)
    check_bold_overuse(text, report)
    check_paragraph_length(text, report)
    return report


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: validate_quora_draft.py <draft-file>", file=sys.stderr)
        return 2

    text = open(sys.argv[1], encoding="utf-8").read()
    report = validate(text)

    if report.is_clean:
        print("Clean — no known Quora formatting-collapse triggers found.")
        return 0

    for f in sorted(report.findings, key=lambda f: f.line):
        loc = f"line {f.line}" if f.line else "overall"
        print(f"[{f.rule}] {loc}: {f.message}")
    print(f"\n{len(report.findings)} issue(s) found.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
