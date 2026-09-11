# claude-skills

Personal [Claude Agent Skills](https://docs.claude.com/en/docs/claude-code/skills) — drop into `.claude/skills/` and Claude Code picks them up automatically.

## Skills

| Skill | What it does |
|---|---|
| [`lead-enrichment`](skills/lead-enrichment/SKILL.md) | Turns a company list into 5–10 verified decision-maker contacts per company (Parallel → Apollo → MillionVerifier pipeline) |
| [`lead-research-assistant`](skills/lead-research-assistant/SKILL.md) | Finds high-quality target companies for your product/service and gives an actionable outreach strategy |
| [`quora-answer-composer`](skills/quora-answer-composer/SKILL.md) | Drafts Quora answers outside Quora's buggy editor (cursor-jump/draft-loss bugs) and validates them against Quora's own formatting guidelines before you paste — catches the manual-bullet, missing-paragraph-spacing, and bold-overuse patterns that trigger Quora's "very poor formatting" collapse. Includes a real test suite (`tests/`). |

## Install

```bash
git clone https://github.com/Yashraj00700/claude-skills
cp -r claude-skills/skills/lead-enrichment ~/.claude/skills/
cp -r claude-skills/skills/lead-research-assistant ~/.claude/skills/
cp -r claude-skills/skills/quora-answer-composer ~/.claude/skills/
```

Each skill needs its own API keys (documented inside each `SKILL.md`) — nothing is hardcoded.

## License

MIT
