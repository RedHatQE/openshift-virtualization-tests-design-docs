# CLAUDE.md

Project guidance for AI coding assistants.

> **Using a different AI tool?** Copy this file's content into your tool's config file (e.g.: `.cursorrules` for Cursor)

## Reviewing an STP pull request

Two files, two jobs:

- [`docs/review-personas/README.md`](./docs/review-personas/README.md#tell-your-assistant-to-use-them) —
  how to run a review: which persona, what it reads, the base-branch rule, the report format, and the rule
  that an assistant never approves or fills a sign-off. **This is the only copy of the procedure**, so
  follow it rather than re-deriving it.
- [`AGENTS.md`](./AGENTS.md) — the checklist those personas compress, and the audience split: the
  automated reviewers apply it to the diff, a human reviewer runs the personas.

## Key References

- `README.md` — Project overview, structure, and contributing guidelines
- `AGENTS.md` — AI review checklist for STP pull requests (review index and workflow; the template and guide hold the rules)
- `docs/review-personas/README.md` — reviewer personas for STP PRs: six by review focus, three by sign-off function
- `docs/stp-guide.md` — STP purpose, lifecycle and process guide
- `docs/testing-tiers.md` — Testing tier definitions
- `stps/stp-template/stp.md` — STP template with inline instructions
- `stps/stp-template/child-stp.md` — Per-SIG child STP template for multi-SIG features
- `.markdownlint.yaml` — Markdown linting configuration
