# Persona Output Contract

Every persona in this directory reports in the shape defined here, so findings from several
personas can be merged without translation. A persona that invents its own format is
incomplete.

## Run header

Start every run with this block, so a reader knows what was reviewed and against what:

```text
## Persona run
- Persona: sections/traceability
- STP: stps/sig-network/<feature>/stp.md @ <commit-sha>
- Requirements source: <Jira key(s), or "not linked">
- Findings: <count>
```

The commit SHA matters: a review against a stale head is worthless.

## Channels

| Channel | Meaning | Resolved by |
|---|---|---|
| CRITICAL | Blocks approval — missing traceability, empty sign-off, contradiction | STP author, then QE reviewer |
| HIGH | Template non-compliance, incomplete section, vague content | STP author |
| MEDIUM | Formatting or content improvement | STP author, optional |
| LOW | Style suggestion | STP author, optional |
| DECISION | A named human must answer before sign-off; not fixable by editing text | The persona owner (see the run matrix) |
| SIGN-OFF | A sign-off cell this persona's owner must complete | The owner writes their own name and date |

`DECISION` and `SIGN-OFF` exist because not every finding is a defect. "Is this out of scope?"
cannot be fixed by rewording — it needs a Product Manager. A persona that files it as HIGH
invites the author to close it with a prose edit, which is the failure `AGENTS.md` already warns
about for Out of Scope items.

## Finding format

One row per finding, most severe first:

| Channel | Violates | Location | Evidence | Fix |
|---|---|---|---|---|
| CRITICAL | `AGENTS.md` II.4.1 | `II.1 Testing Goals`, goal 3 | "Deploy a VM from each available boot source and verify it boots" — no failure-path goal exists for any P0 goal | Add a P0 negative goal: VM cannot start from an unavailable boot source, user sees a specific event |
| DECISION | `AGENTS.md` II.1 | `II.1 Out of Scope`, item 2 | "Upgrade from 4.21 not tested this cycle" — presented as a decision, no PM agreement recorded | PM to confirm or move it into scope |

## Evidence rule

No finding without a quoted STP line and the `AGENTS.md` section it violates. If you cannot quote
the text you are objecting to, you are speculating — drop the finding.

## Clearing rule

End every run with what you checked and found acceptable:

```text
## Cleared
- Feature Overview: 5 sentences, no internal component names
- Acceptance criteria: 7 items, all falsifiable
- II.4 Entry Criteria: both minimum criteria present and honestly marked
```

Silence is not evidence of a clean document. A run that lists nothing cleared is
indistinguishable from a run that skipped the section.

## Budget

Report only findings you would defend to the author's face, at most 10 per persona run, most
severe first. Padding a report with LOW findings hides the CRITICAL one.

## Never

- Never write a human's name or date into a sign-off cell.
- Never report a section another persona owns — read its `Do NOT report` list first.
- Never mark a `DECISION` as resolved because the text changed.
- Never report the same root cause twice under different wordings to look thorough.
