---
name: instruction-drift-guard
description: Mechanically re-checks Claude's own output against style/formatting rules stated earlier in a long session — catches the well-documented drift where explicit instructions (no comments, no em-dashes, specific tone, quote style) get followed for the first few turns and then quietly ignored as the session grows. Use when the user says "check you're still following my rules", "verify the style contract", "why did you add comments again", or when a long session is producing output that feels like it's drifted from earlier instructions.
---

# Instruction Drift Guard

## Why this exists

This is a real, heavily validated problem, not a guess:

- [anthropics/claude-code#77136](https://github.com/anthropics/claude-code/issues/77136) (423 reactions): "Claude... increasingly default to repetitive rhetorical tics and often struggle to produce coherent prose despite explicit style instructions."
- [anthropics/claude-code#65961](https://github.com/anthropics/claude-code/issues/65961) (219 reactions): "Claude verbose code comments by default — ignores instructions to stop."
- [anthropics/claude-code#1599](https://github.com/anthropics/claude-code/issues/1599) (61 reactions): "Claude clobbers correct typographic marks and can't be told otherwise."

Community reports (r/ClaudeCode, r/ClaudeAI, collected independently) describe the same pattern: by the 4th or 5th interaction in a session, style/formatting instructions stop being followed, as if the CLAUDE.md rules never existed.

**The architectural reason:** instructions sitting in a memory file (CLAUDE.md, an earlier turn, a system prompt) are passive context. Nothing re-checks them as the session grows and a recency-weighted context window buries them under newer turns. A skill loaded once at the start of a task has the same problem over a long enough session — it's read once, not re-verified.

**The fix this skill provides:** turn "remember the rule" into "mechanically re-check the rule," at any point in a session, as many times as needed. A regex/heuristic check doesn't degrade with context length the way model attention does.

## Workflow

1. At the start of a task with real style constraints, write them once as a **contract** — either inline or as a small YAML file (see `contract.example.yaml`).
2. At any point in the session — after the first output, after the tenth — run:
   ```bash
   python3 scripts/check_contract.py contract.yaml path/to/current-output
   ```
3. Fix whatever it flags. Re-run. This is cheap enough to run after every substantial turn in a long session, which is exactly when drift happens.

## What the contract can check

| Rule | Catches |
|---|---|
| `no_comments: true` | Code comments added despite "no comments" instructions ([#65961](https://github.com/anthropics/claude-code/issues/65961)) |
| `banned_phrases: [...]` | LLM rhetorical tics — "delve", "tapestry", "it's important to note", "in today's fast-paced world", boilerplate hedging |
| `quote_style: straight \| curly` | Typographic-mark drift — smart quotes creeping in when the user wants straight ones or vice versa ([#1599](https://github.com/anthropics/claude-code/issues/1599)) |
| `max_line_length` | Line-length rules quietly abandoned over a long session |
| `banned_chars: [...]` | Any character/pattern the user explicitly banned (e.g. em-dashes) |

## Honest limits

This checks *mechanical, regex-checkable* style rules — not tone, not correctness, not whether the code works. It's a narrow, re-runnable gate for the specific class of drift that's actually documented (formatting/style instructions), not a general "is this good" judge.
