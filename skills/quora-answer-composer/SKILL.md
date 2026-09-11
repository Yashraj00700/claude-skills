---
name: quora-answer-composer
description: Draft, validate, and clean up Quora answers before pasting them into Quora's editor — catches the exact patterns that trigger Quora's "very poor formatting" collapse (manual bullets instead of Quora's list buttons, missing paragraph spacing, bold overuse) and avoids Quora's known editor bugs (cursor jumping mid-edit, drafts silently disappearing) by drafting outside the editor entirely. Use when the user asks to "write a Quora answer", "format this for Quora", "why did Quora collapse my answer", or "fix my Quora formatting".
---

# Quora Answer Composer

## Why this exists

Quora's own editor has well-documented, long-standing problems:
- Cursor jumps to a random position mid-edit and deletes the wrong text (Android keyboard/content-bridge bug, reported for years).
- Drafts silently vanish — "no saved drafts" shown despite autosave, or lost on app crash.
- Answers get auto-collapsed with a "very poor formatting" notice and no specific diagnostic — Quora doesn't tell you what's wrong.
- The comment box has no rich formatting at all (no bold, lists, or blockquote), unlike the main answer editor.

None of that is fixable from outside Quora. What *is* fixable: never compose or edit for long inside Quora's box in the first place, and make sure what you paste in already follows Quora's own formatting rules so it never gets flagged.

## Workflow

1. **Draft in a local file, not in Quora.** Write the full answer as a plain-text/Markdown file first. This is the actual mitigation for the cursor-jump and draft-loss bugs — you're never at risk of losing more than what's unsaved in your editor of choice.
2. **Run the validator** against the draft:
   ```bash
   python3 scripts/validate_quora_draft.py path/to/draft.md
   ```
   It reports every line that would likely trigger Quora's formatting flags, per Quora's own published guidelines (see References).
3. **Fix what it flags**, re-run until clean.
4. **Paste the cleaned text into Quora once**, then apply Quora's native toolbar buttons for any list/blockquote/bold the validator told you to convert manually — Quora does not preserve Markdown syntax, only its own toolbar-applied formatting survives.

## Rules the validator checks (from Quora's own Help Center guidelines)

- **Paragraph spacing** — Quora requires a full blank line between paragraphs, even one-sentence ones. Missing this reads as a wall of text and is a common collapse trigger.
- **Manual list characters** (`-`, `*`, `1.`, `1)` typed as plain text) — Quora's guideline is explicit: *"use the numbered and bullet point list functions... rather than using your own customized list style."* Typed dashes/numbers don't become real list items and read as broken formatting.
- **Manual blockquotes** (`>` typed as plain text) — same issue; Quora has a real blockquote button, a typed `>` doesn't invoke it.
- **Bold overuse** — Quora's guideline: bold/italic/underline "sparingly," never "all bold, or mostly bold." The validator flags when more than ~15% of words are wrapped in `**bold**`.
- **Wall-of-text paragraphs** — paragraphs over ~120 words are flagged for a readability break, per Quora's "break up large blocks of text" guidance.

## References

- Quora Help Center: "What are good guidelines for formatting answers and posts on Quora?"
- Direct user reports of cursor-jump, draft-loss, and unexplained-collapse bugs on quora.com (community threads, not official docs — cited for the *problem*, not the *rule*).
