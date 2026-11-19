# Review Personas

Nine reviewer personas for Software Test Plan pull requests. Each one is a prompt: hand it to any
AI assistant — Claude Code, Cursor, CodeRabbit, a local model, or a plain chat window — together
with the PR diff and the relevant files, and you get that reviewer's findings in a uniform format.

The rules live in [`AGENTS.md`](../../AGENTS.md). Personas do not restate rules; they name the
`AGENTS.md` section they own, so a rule change happens in one place.

## Two kinds of persona

| Type | The question it answers | Directory |
|---|---|---|
| **section** | Is this part of the STP correct? | [`sections/`](./sections/) |
| **lens** | Would this stakeholder approve? | [`lenses/`](./lenses/) |

A section persona owns slices of `AGENTS.md` and reports **defects**.
A lens persona owns one stakeholder's questions, reads the whole document plus that stakeholder's own
sources, and reports **decisions and sign-offs**.

Six section personas, plus one lens per approver named in `IV. Sign-off and Approval`: QE Lead, Dev
Lead, Product Manager.

| Section persona | Owns |
|---|---|
| [`requirements`](./sections/requirements.md) | Metadata, Feature Overview, requirements, NFRs |
| [`traceability`](./sections/traceability.md) | Testing Goals, scenarios, tiers, priorities, IDs |
| [`constraints`](./sections/constraints.md) | Known Limitations, Out of Scope, Test Limitations, Risks |
| [`strategy`](./sections/strategy.md) | Technology review, Test Strategy, Environment, Entry Criteria |
| [`language-hygiene`](./sections/language-hygiene.md) | Implementation vocabulary, conventions, placeholders, markdown |
| [`multi-sig`](./sections/multi-sig.md) | Parent/child STP structure, Section IV roles |

| Lens | Signs |
|---|---|
| [`product-manager`](./lenses/product-manager.md) | Section IV (PM), Out of Scope, Known Limitations, accepted risk |
| [`development`](./lenses/development.md) | Section IV (Dev Lead), Technology and Design, Test Environment |
| [`test-quality`](./lenses/test-quality.md) | Section IV (QE Lead), scenario design |

## Who runs what

| Persona | Run by | Output gates |
|---|---|---|
| `sections/requirements.md` | QE author or reviewer | merge |
| `sections/traceability.md` | QE author or reviewer | merge |
| `sections/constraints.md` | QE author or reviewer | merge |
| `sections/strategy.md` | QE reviewer | merge |
| `sections/language-hygiene.md` | anyone | merge |
| `sections/multi-sig.md` | owning-SIG QE | merge |
| `lenses/test-quality.md` | QE Lead | Section IV approval |
| `lenses/development.md` | Dev Lead | Section IV approval |
| `lenses/product-manager.md` | Product Manager | Section IV approval, Out of Scope sign-offs |

A lens run by the wrong role produces questions nobody will answer. A section persona run by a lens
owner produces template noise that buries the decision.

## Running one

Three levels of effort, all valid.

### Level 1 — paste it

```text
Read docs/review-personas/sections/traceability.md and follow it.
The STP under review is stps/sig-network/<feature>/stp.md.
The PR diff is:
<gh pr diff 123 output>
```

Anything that can read files and follow instructions works. No setup.

### Level 2 — one subagent per persona

Give each persona its own context so findings do not bleed between streams:

```bash
gh pr diff 123 > /tmp/pr.diff
for p in requirements traceability constraints; do
  claude -p "$(cat docs/review-personas/sections/$p.md)

Review /tmp/pr.diff plus the changed STP files.
Report per docs/review-personas/_output-contract.md." > "/tmp/review-$p.md"
done
```

Run at most three section personas in one pass on a large STP; past that the merge cost exceeds the
review value. Do not run lenses in the same pass as section personas — a lens needs the author's
answers to the defects first.

### Level 3 — a native tool adapter

Wrap the persona in whatever the tool wants: a Claude Code subagent, a Cursor rule, a CodeRabbit path
instruction. Commit the generation recipe, not the generated file — agent directories such as
`.claude/agents/` are machine-local and get overwritten. `.coderabbit.yaml` and `.pr_agent.toml`
show how this repository already feeds `AGENTS.md` to automated reviewers.

## Merging results

1. Collect every finding row from every persona.
2. Deduplicate: same location and same root cause is one finding. Keep the most actionable wording.
3. `DECISION` rows go to the owner in the run matrix — never to the STP author, who cannot answer
   them.
4. `SIGN-OFF` rows become the checklist for Section IV. The person writes their own name and date; no
   persona ever fills those in.
5. A `DECISION` is not resolved by editing text. It is resolved when the named human answers and the
   STP records the answer.

Findings format, channels, evidence and budget rules: [`_output-contract.md`](./_output-contract.md).

## Adding a persona

1. Decide the type: does it own part of `AGENTS.md`, or one stakeholder's questions?
2. Copy the closest existing file and change the frontmatter:

```yaml
---
persona: <file-name-without-extension>
type: section            # or: lens
owns:                    # section only — heading text from AGENTS.md, exact
  - II.5 — Risks
signs:                   # lens only — the Section IV role or heading this lens signs
  - IV — Sign-off and Approval (Approvers: QE Lead)
reads:                   # files, plus any external source the persona needs
  - AGENTS.md
---
```

Both `owns:` and `signs:` entries use the exact `AGENTS.md` heading text and may carry a
`(partial: ...)` or role suffix; the check matches the text before the suffix.

3. Write the `Do NOT report` list before the `Hunt for` list. The scope boundary is what makes nine
   personas useful instead of nine copies of the same review.
4. Compare against every other persona: if two would file the same finding, the boundary is wrong.
5. Add it to the run matrix above.

## Related

- [`AGENTS.md`](../../AGENTS.md) — the normative review standard
- [`docs/stp-guide.md`](../stp-guide.md) — STP lifecycle and structure
- [`docs/testing-tiers.md`](../testing-tiers.md) — tier definitions
