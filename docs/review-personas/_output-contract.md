# Persona Output Contract

Every persona reports in this shape, so findings from several personas merge without translation.

## Run header

```text
## Persona run
- Persona: sections/traceability
- STP: stps/sig-network/<feature>/stp.md
- Reviewed at: <commit sha>
- Sources: <Jira key(s), VEP, feature request — or "not linked">
- Personas not run: <names, or "none">
- Findings: <count>
```

The SHA matters: a review against a stale head is worthless. The `Personas not run` line matters
because a partial run is not a clean run.

## Severity

Four levels, defined once in `AGENTS.md` → `## Review Severity Levels`. Cite the level; do not
restate the definitions here and do not invent a fifth.

## Disposition — a separate axis from severity

| Disposition | Meaning | Resolved by |
|---|---|---|
| DECISION | A named human must answer before approval. Not resolved by editing text. | The persona's owner — see [who runs what](./README.md#who-runs-what) |
| SIGN-OFF | A sign-off cell this persona's owner completes with their own name and date. Never pre-filled, by anyone. | That owner |

A finding carries one severity and optionally one disposition: a missing PM/Lead agreement is
CRITICAL **and** DECISION. There is no severity level meaning "needs a human", because severity says
how bad it is and disposition says who acts.

## Finding format

| Severity | Disposition | Rule violated | Location | Evidence | Fix |
|---|---|---|---|---|---|
| CRITICAL | DECISION | `AGENTS.md` II.1 Out of Scope | `II.1 Out of Scope`, item 2 | "Upgrade from 4.21 not tested this cycle" — *PM/Lead Agreement:* carries no name or date | PM confirms it, or the item moves into scope |
| HIGH | — | `AGENTS.md` II.4.1 | `II.1 Testing Goals`, goal 3 | "Deploy a VM from each available boot source and verify it boots" — `absent:` any failure-path goal for a P0 goal | Add a P0 negative goal |
| — | SIGN-OFF | `stps/stp-template/stp.md` IV | `IV Approvers`, Product Manager | Feature request read; scope matches the promise | PM writes their name and date |

**Rule violated** names the `AGENTS.md` section — or, for a lens finding, the VEP, design doc or
feature request that contradicts the STP. A lens finding based only on the STP text is a defect, and
defects belong to the section personas.

## Evidence rule

Quote the text you object to. For a finding of absence — a missing requirement ID, a missing
sign-off, a missing child-STP link — quote the nearest existing anchor (the heading, the neighbouring
row, the empty cell) and prefix the what-is-missing with `absent:`. Without an anchor there is
nothing for the author to find.

## Boundary rule

A section persona files defects. A lens files only what its role must decide or sign, and cites the
section finding (`see: sections/traceability`) instead of re-deriving it. If a lens spots a defect no
section persona covers, it files it once, as DECISION, and names the persona that should own it.

## Where the report goes

One report per persona: a file `review-<persona>.md`, or a PR review comment titled
`## Persona run: <persona>`. The merge owner collects them. Nobody writes findings into the STP.

## Clearing rule

End every run with what you checked and found acceptable:

```text
## Cleared
- Feature Overview: 5 sentences, no internal component names
- Acceptance criteria: 7 items, all individually listed and falsifiable
- II.4 Entry Criteria: both minimum criteria present and honestly marked
```

Silence is not evidence of a clean document. A run that lists nothing cleared is indistinguishable
from a run that skipped the section.

## Budget

At most 10 findings per run, severity first, plus the SIGN-OFF rows. Nine personas are not nine
times ten rows: the boundary rule and this budget exist so the merge stays readable.

## Never

- Never write a human's name or date into a sign-off cell.
- Never report a section another persona owns — read its `Do NOT report` list.
- Never mark a DECISION as resolved because the text changed.
- Never report one root cause twice to look thorough.
