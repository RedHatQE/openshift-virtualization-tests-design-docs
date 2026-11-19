# Review Personas

Nine reviewer personas for Software Test Plan pull requests. Each file is a prompt: hand it to your
AI assistant together with the PR diff and the relevant files, and you get that reviewer's findings in
a uniform format.

The rules live in [`AGENTS.md`](../../AGENTS.md). Personas paraphrase the checks of the `AGENTS.md`
section they own and name that section in every finding, so a rule change and the persona that
enforces it are updated in the same PR.

## Two kinds of persona

| Type | The question it answers | Directory |
|---|---|---|
| **section** | Is this part of the STP correct? | [`sections/`](./sections/) |
| **lens** | Would this stakeholder approve? | [`lenses/`](./lenses/) |

A section persona owns slices of `AGENTS.md` and files **defects**.
A lens persona carries one stakeholder's questions, reads the whole document plus that stakeholder's
own sources, and files **the decisions and sign-offs that role owes** — plus the defects that block
them.

**One root cause, one owner.** A section persona files the defect; the matching lens files only the
decision the defect forces on its owner, citing the section finding. A rule never appears in two
section personas, and never in two lenses.

Six section personas, plus one lens per approver in `IV. Sign-off and Approval` — QE Lead, Dev Lead,
Product Manager. That list is a minimum: add a lens in the same PR that adds an approver role to the
template.

| Section persona | Owns |
|---|---|
| [`requirements`](./sections/requirements.md) | Metadata and links, Feature Overview, requirements, NFRs |
| [`traceability`](./sections/traceability.md) | Testing Goals, scenarios, tiers, priorities, IDs |
| [`constraints`](./sections/constraints.md) | Known Limitations, Out of Scope, Test Limitations, Risks |
| [`strategy`](./sections/strategy.md) | Technology review, Test Strategy, Test Environment, Tools, Entry Criteria, cross-section consistency |
| [`language-hygiene`](./sections/language-hygiene.md) | User perspective, evidence, conventions, placeholders, concision, markdown |
| [`multi-sig`](./sections/multi-sig.md) | Child STPs, parent/child structure, Section IV roles |

| Lens | Signs |
|---|---|
| [`product-manager`](./lenses/product-manager.md) | Product Manager approval; Out of Scope agreements; accepted limitations and business risk |
| [`development`](./lenses/development.md) | Dev Lead approval; accepted technical limitations and risk |
| [`test-quality`](./lenses/test-quality.md) | QE Lead approval; scenario design it will vouch for |

## Who runs what

This table is also called *the run matrix* below — same thing.

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
| `lenses/product-manager.md` | Product Manager | Section IV approval, Out of Scope agreements |

A lens run by the wrong role produces questions nobody will answer. A section persona run by a lens
owner produces template noise that buries the decision.

## Running one

The YAML block at the top of each persona is metadata for humans and tooling; quote a value that
contains a colon, or YAML reads it as a mapping. The prose after it is the prompt. `reads:` lists what
to give the assistant: repository paths, plus any external source — feature request, VEP — that only
a human can paste.

### Level 1 — paste it

```text
Read docs/review-personas/sections/traceability.md, AGENTS.md, and
docs/review-personas/_output-contract.md, and follow them.

STP: stps/sig-network/<feature>/stp.md
Reviewed at: <commit sha>
Diff:
<paste `gh pr diff 123` output here>
```

In a chat window with no file access, paste the contents of those three files as one message, then
the STP and the diff. All three are needed: every finding cites an `AGENTS.md` section, and every
persona reports in the contract's format.

### Level 2 — one subagent per persona

Run each persona in its own context so findings do not bleed between streams. Keep the diff inside
the repository — an agent confined to its working directory cannot read `/tmp` — write the reports to
one scratch directory, and grant the file access explicitly, because with output redirected nobody is
there to answer a permission prompt:

```bash
mkdir -p review-out                     # gitignore this, or delete it when done
SHA=$(gh pr view 123 --json headRefOid --jq .headRefOid)
gh pr diff 123 > review-out/pr.patch
for p in requirements traceability constraints strategy language-hygiene multi-sig; do
  claude -p "Follow the persona in docs/review-personas/sections/$p.md together with
AGENTS.md and docs/review-personas/_output-contract.md. Review review-out/pr.patch and the
changed STP files. Reviewed at: $SHA. Report per the output contract." \
    --allowedTools Read \
    > "review-out/$p.md"
done
rm review-out/pr.patch                  # the reports stay; the diff need not
```

`Read` is enough once the patch is on disk — grant `Bash` too only if you want the persona to run
`git`/`gh` itself, which also lets a review write into the tree it is reviewing. The flag name is
CLI-specific: check `claude --help` (or your tool's equivalent) before an unattended run.

Run all six section personas. A run that skips some is not a clean run, and the merge owner records
what was skipped in the `## Coverage` block.

### The lens pass

Lenses run **after** the author has answered the section findings — a lens asked too early re-asks
questions QE is about to fix. Each lens needs what its role reads, and no assistant can fetch Jira:

- `lenses/product-manager`: paste the feature request and its acceptance criteria
- `lenses/development`: paste the VEP/design doc, and point it at the implementation PR
- `lenses/test-quality`: needs only the STP and `docs/testing-tiers.md`

Run them in any order, in separate contexts, and treat a lens that reports "no design source linked"
as correct behaviour — it stops rather than guesses.

### Level 3 — a native tool adapter

Wrap the persona in whatever the tool wants: a subagent, an editor rule, a CodeRabbit path
instruction. Commit the generation recipe, not the generated file — `.claude/` is gitignored here and
agent directories get overwritten on upgrade. `.coderabbit.yaml` and `.pr_agent.toml` show how this
repository already feeds `AGENTS.md` to automated reviewers.

## Merging results

1. Collect every finding row from every persona.
2. Deduplicate: same location and same root cause is one finding. Keep the most actionable wording.
3. A `DECISION` row names the role that answers it — Product Manager, Dev Lead, QE Lead — not the
   persona's runner and not the STP author as such. The run matrix says who runs a persona, not who
   owns its findings.
4. `SIGN-OFF` rows become the checklist for Section IV. The person writes their own name and date; no
   persona ever fills those in.
5. A `DECISION` is not resolved by editing text. It is resolved when the named human answers and the
   STP records the answer.

Channels, format, evidence and budget rules: [`_output-contract.md`](./_output-contract.md).

## Adding a persona

1. Decide the type: does it own part of `AGENTS.md`, or one stakeholder's questions?
2. Copy the closest existing file. Frontmatter:

```yaml
---
persona: <file-name-without-extension>
type: section            # or: lens
owns:                    # section only — heading text from AGENTS.md
  - II.5 — Risks
signs:                   # lens only — the sign-off cells this role completes
  - "IV — Sign-off and Approval (Approvers: QE Lead)"
  - "II.5 — Risks (Sign-off)"
reads:                   # repository paths, plus external sources a human pastes
  - AGENTS.md
---
```

Quote any value containing a colon. `- II.5 — Risks (Sign-off)` survives unquoted, but
`- II.1 — Scope of Testing (partial: Testing Goals)` is silently parsed as a mapping rather than a
string, so the convention is to quote them all.

`owns:` takes an `AGENTS.md` heading, optionally suffixed `(partial: ...)` naming the sub-part this
persona owns when a heading is split. `signs:` takes a sign-off **cell** — the section whose per-item
cells this role fills, so `II.5 — Risks (Sign-off)` means every risk's `*Sign-off:*` — or the role's
cell in `IV`. Never a section with no cell behind it: a section with nothing to sign is a defect
area, and defect areas are `owns:`. Where a lens vouches for a section that has no cell at all, that
goes in its prose. Keep both exact: a mistyped heading currently fails nothing, so review is the only
thing that catches it.

**Precedence, stated once:** the template renders the structure and the field names, `AGENTS.md`
defines the checks, and a persona overrides neither. Where a persona and `AGENTS.md` disagree,
`AGENTS.md` wins and both change in the same PR; where `AGENTS.md` and the template disagree on a
field's name, the template wins and the divergence is a finding against `AGENTS.md`.

3. Body order: role paragraph; one preamble `##` when the persona needs an external source or a
   decision rule, named for what it establishes (`## Before you judge`, `## First: get the design`);
   one `##` per thing it hunts; `## What you emit` for a lens; `## Do NOT report`; `## Output`.
4. Write `Do NOT report` first. The scope boundary is what makes nine personas useful instead of nine
   copies of the same review.
5. Compare against every other persona: if two would file the same finding, the boundary is wrong.
6. Add it to the run matrix above.

## Related

- [`AGENTS.md`](../../AGENTS.md) — the normative review standard
- [`docs/stp-guide.md`](../stp-guide.md) — STP lifecycle and structure
- [`docs/testing-tiers.md`](../testing-tiers.md) — tier definitions
