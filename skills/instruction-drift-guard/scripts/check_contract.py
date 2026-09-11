#!/usr/bin/env python3
"""Re-check a piece of output against a style contract declared earlier in
the session. Designed to be run repeatedly through a long session, since
that's exactly when style-instruction drift happens (see SKILL.md for the
cited GitHub issues this is built to catch).
"""
from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path

import yaml

CODE_COMMENT_PATTERNS = {
    ".py": ("#", None),
    ".sh": ("#", None),
    ".rb": ("#", None),
    ".js": ("//", ("/*", "*/")),
    ".ts": ("//", ("/*", "*/")),
    ".jsx": ("//", ("/*", "*/")),
    ".tsx": ("//", ("/*", "*/")),
    ".go": ("//", ("/*", "*/")),
    ".rs": ("//", ("/*", "*/")),
    ".c": ("//", ("/*", "*/")),
    ".cpp": ("//", ("/*", "*/")),
    ".java": ("//", ("/*", "*/")),
}

CURLY_QUOTES = "“”‘’"


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


def load_contract(path: str) -> dict:
    return yaml.safe_load(Path(path).read_text()) or {}


def is_code_file(path: str, contract: dict) -> bool:
    code_exts = set(contract.get("code_extensions", CODE_COMMENT_PATTERNS.keys()))
    return Path(path).suffix in code_exts


def check_no_comments(lines: list[str], ext: str, report: Report) -> None:
    line_marker, block_markers = CODE_COMMENT_PATTERNS.get(ext, (None, None))
    if line_marker is None:
        return
    in_block = False
    for i, line in enumerate(lines, start=1):
        stripped = line.strip()
        if block_markers:
            start, end = block_markers
            if in_block:
                report.add(i, "no-comments", "Inside a banned block comment")
                if end in stripped:
                    in_block = False
                continue
            if start in stripped:
                report.add(i, "no-comments", f"Block comment found: {stripped[:60]!r}")
                if end not in stripped[stripped.index(start) + len(start):]:
                    in_block = True
                continue
        if stripped.startswith(line_marker):
            report.add(i, "no-comments", f"Comment line found: {stripped[:60]!r}")


def check_banned_phrases(lines: list[str], phrases: list[str], report: Report) -> None:
    lowered_phrases = [p.lower() for p in phrases]
    for i, line in enumerate(lines, start=1):
        low = line.lower()
        for phrase, original in zip(lowered_phrases, phrases):
            if phrase in low:
                report.add(i, "banned-phrase", f"Banned phrase {original!r} found")


def check_banned_chars(lines: list[str], chars: list[str], report: Report) -> None:
    for i, line in enumerate(lines, start=1):
        for ch in chars:
            if ch in line:
                report.add(i, "banned-char", f"Banned character {ch!r} found")


def check_quote_style(lines: list[str], style: str, report: Report) -> None:
    for i, line in enumerate(lines, start=1):
        if style == "straight":
            for ch in line:
                if ch in CURLY_QUOTES:
                    report.add(i, "quote-style", f"Curly quote {ch!r} found, contract requires straight quotes")
                    break
        elif style == "curly":
            if '"' in line or "'" in line:
                report.add(i, "quote-style", "Straight quote found, contract requires curly quotes")


def check_line_length(lines: list[str], max_len: int, report: Report) -> None:
    for i, line in enumerate(lines, start=1):
        if len(line.rstrip("\n")) > max_len:
            report.add(i, "line-length", f"Line is {len(line.rstrip())} chars, contract max is {max_len}")


def validate(text: str, target_path: str, contract: dict) -> Report:
    report = Report()
    lines = text.splitlines(keepends=True)
    ext = Path(target_path).suffix

    if contract.get("no_comments") and is_code_file(target_path, contract):
        check_no_comments(lines, ext, report)

    if contract.get("banned_phrases"):
        check_banned_phrases(lines, contract["banned_phrases"], report)

    if contract.get("banned_chars"):
        check_banned_chars(lines, contract["banned_chars"], report)

    if contract.get("quote_style") and not is_code_file(target_path, contract):
        check_quote_style(lines, contract["quote_style"], report)

    if contract.get("max_line_length"):
        check_line_length(lines, contract["max_line_length"], report)

    return report


DEFAULT_CONTRACT_NAMES = [".instruction-contract.yaml", "instruction-contract.yaml"]


def find_default_contract(start: Path) -> Path | None:
    """Walk up from `start` looking for a default-named contract file, so a
    long session can re-run this with just a target path, no retyping."""
    for directory in [start, *start.parents]:
        for name in DEFAULT_CONTRACT_NAMES:
            candidate = directory / name
            if candidate.is_file():
                return candidate
    return None


def main() -> int:
    if len(sys.argv) == 2:
        target_path = sys.argv[1]
        found = find_default_contract(Path(target_path).resolve().parent)
        if found is None:
            names = " or ".join(DEFAULT_CONTRACT_NAMES)
            print(f"No contract path given and no {names} found in {target_path}'s directory or its parents.", file=sys.stderr)
            return 2
        contract_path = str(found)
    elif len(sys.argv) == 3:
        contract_path, target_path = sys.argv[1], sys.argv[2]
    else:
        print("Usage: check_contract.py [contract.yaml] <target-file>", file=sys.stderr)
        print(f"  (if contract.yaml is omitted, looks for {' or '.join(DEFAULT_CONTRACT_NAMES)} in the target's directory or its parents)", file=sys.stderr)
        return 2

    contract = load_contract(contract_path)
    text = Path(target_path).read_text(encoding="utf-8")
    report = validate(text, target_path, contract)

    if report.is_clean:
        print(f"Clean — {target_path} follows the contract in {contract_path}.")
        return 0

    for f in sorted(report.findings, key=lambda f: f.line):
        print(f"[{f.rule}] line {f.line}: {f.message}")
    print(f"\n{len(report.findings)} violation(s) of the style contract found.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
