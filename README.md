# claude-skills

Personal [Claude Agent Skills](https://docs.claude.com/en/docs/claude-code/skills) — drop into `.claude/skills/` and Claude Code picks them up automatically.

## Skills

| Skill | What it does |
|---|---|
| [`lead-enrichment`](skills/lead-enrichment/SKILL.md) | Turns a company list into 5–10 verified decision-maker contacts per company (Parallel → Apollo → MillionVerifier pipeline) |
| [`lead-research-assistant`](skills/lead-research-assistant/SKILL.md) | Finds high-quality target companies for your product/service and gives an actionable outreach strategy |

## Install

```bash
git clone https://github.com/Yashraj00700/claude-skills
cp -r claude-skills/skills/lead-enrichment ~/.claude/skills/
cp -r claude-skills/skills/lead-research-assistant ~/.claude/skills/
```

Each skill needs its own API keys (documented inside each `SKILL.md`) — nothing is hardcoded.

## License

MIT
