# Persona Output Contract

Every persona reports in this shape, so findings from several personas merge without translation.

## Run header

Each persona starts its own report with this block:

```text
## Persona run
- Persona: sections/traceability
- STP: stps/sig-network/<feature>/stp.md
- Reviewed at: <commit sha the review was made against>
- Sources: <Jira key(s), VEP, feature request — or "not linked">
- Findings: <count>
```

`Reviewed at` must be a commit SHA, not "the working tree": supply it when you invoke the persona,
because a review against a stale head is worthless and the persona cannot discover it reliably on its
own.

Coverage is not part of a persona's own header — no persona knows which others ran. The merge owner
records it once, for the whole review:

```text
## Coverage
- Ran: sections/requirements, sections/traceability, lenses/test-quality
- Not run: sections/constraints, sections/strategy, sections/language-hygiene, sections/multi-sig,
  lenses/development, lenses/product-manager
- Reason: author pass before requesting review
```

A partial run is not a clean run, and only that block can say so.

## Severity

Four levels, defined once in `AGENTS.md` → `## Review Severity Levels`. Cite the level. Do not
restate the definitions here and do not invent a fifth.

## Disposition — a separate axis from severity

| Disposition | Meaning | Emitted by | Answered by |
|---|---|---|---|
| DECISION | A named human must answer before approval. Not resolved by editing text. | section personas and lenses | The role named in the finding — Product Manager, Dev Lead or QE Lead — never the persona runner and never the STP author as such |
| SIGN-OFF | A sign-off cell the persona's owner completes with their own name and date. Never pre-filled. | lenses only | That owner |

A finding carries one severity and optionally one disposition: a missing PM/Lead agreement is
CRITICAL **and** DECISION. There is no severity level meaning "needs a human", because severity says
how bad it is and disposition says who acts.

The run matrix says who *runs* a persona, not who answers its findings. Those differ: a section
persona run by the QE author routinely files a DECISION that only the Product Manager can answer, so
every DECISION row names its answering role in the Fix column.

A section persona never emits SIGN-OFF: sign-off cells belong to the people whose names go in them,
and those are the lenses.

## Finding format

Cite the rule with the exact heading text from `AGENTS.md` — `II.1 — Scope of Testing`, not `II.1`.
The examples below are the format, so copy their citation style:

| Severity | Disposition | Rule violated | Location | Evidence | Fix |
|---|---|---|---|---|---|
| CRITICAL | DECISION | `AGENTS.md` II.1 — Scope of Testing (Out of Scope) | `II.1 Out of Scope`, item 2 | "Upgrade from 4.21 not tested this cycle" — *PM/Lead Agreement:* carries no name or date | PM confirms it, or the item moves into scope |
| HIGH | — | `AGENTS.md` II.1 — Scope of Testing (Testing Goals) | `II.1 Testing Goals`, goal 3 | "Deploy a VM from each available boot source and verify it boots" — `absent:` any failure-path goal for a P0 goal | Add a P0 negative goal |
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

A section persona files defects about the document. A lens files what its role must decide or sign,
and cites the section finding (`see: sections/traceability`) instead of re-deriving it.

One exception: a lens that is the sole owner of a check files that check's defects.
[`test-quality`](./lenses/test-quality.md) owns falsifiability and nothing else does, so it files
defects about test design — while leaving tier, priority and traceability to
[`traceability`](./sections/traceability.md).

If a lens spots a defect no persona covers, it files it once, as DECISION, and names the persona that
should own it.

## Where the report goes

One report per persona, into a scratch directory outside version control — `review-out/<persona>.md`
with `review-out/` gitignored, or a PR review comment titled `## Persona run: <persona>`. The merge
owner collects them. Nobody writes findings into the STP, and nobody leaves the scratch files in the
tree.

## Clearing rule

End every run with what **you** checked and found acceptable:

```text
## Cleared
- Feature Overview: 5 sentences, no internal component names
- Acceptance criteria: 7 items, all individually listed and falsifiable
- II.4 Entry Criteria: both minimum criteria present and honestly marked
```

Only clear sections you own. Clearing another persona's section is reporting on it, which the Never
rules below forbid. Silence is not evidence of a clean document: a run that lists nothing cleared is
indistinguishable from a run that skipped the section.

## Budget

At most 10 findings per run, severity first, plus SIGN-OFF rows. Nine personas are not nine times ten
rows: the boundary rule and this budget exist so the merge stays readable.

## Never

- Never write a human's name or date into a sign-off cell.
- Never report a section another persona owns — read its `Do NOT report` list.
- Never mark a DECISION as resolved because the text changed.
- Never report one root cause twice to look thorough.
