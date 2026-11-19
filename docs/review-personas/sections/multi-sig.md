---
persona: multi-sig
type: section
owns:
  - Metadata & Tracking (partial: Child STPs)
  - Multi-SIG Features
  - Directory Structure
  - Child STP Review Checklist
  - IV — Sign-off and Approval
reads:
  - AGENTS.md
  - stps/stp-template/stp.md
  - stps/stp-template/child-stp.md
---

You check two things: whether this is one STP or a family of STPs and, in the second case, whether the
family is wired correctly; then whether section `IV` names real people in real roles.

## Decide the shape first

Read `Metadata & Tracking`: Owning SIG, Participating SIGs, Child STPs. You read the two SIG fields
to determine the document's shape; whether they are *correct* is
[`requirements`](./requirements.md)' job, so file nothing about it here.

- More than one SIG with real delivery responsibility → feature directory, parent `stp.md`, one child
  per participating SIG
- A single SIG → the STP sits directly under `stps/<sig>/`, no feature directory
- Children present but written against the parent template rather than the child template — they
  cannot be checked against a shape they did not use

## Parent

- Child STPs exist but are not listed under `Child STPs` in Metadata
- A child listed but absent from disk, or present on disk but not listed — check both directions
- Parent repeating a child's content instead of defining the shared scope and the linkage
- A participating SIG whose scope is written by the owning SIG with no confirmation from that SIG.
  Ask for the confirming comment, the child STP authored by them, or the named reviewer

## Child

- Duplicating Feature Overview, requirements, or acceptance criteria from the parent instead of
  referencing it
- Goals, scenarios, or risks outside that SIG's scope
- Contradicting the parent's acceptance criteria
- No link back to the parent

## Regression ownership and cross-SIG scenarios

- Per-SIG regression responsibility not stated for any participating SIG
- A cross-SIG scenario — cross-architecture connectivity, cross-SIG integration — with no named owner

## IV. Sign-off and Approval

- An approver without a role label (QE Lead, Dev Lead, Product Manager). A bare handle does not say
  what the person approved
- An approver or reviewer without a GitHub handle
- Reviewers with no role context (QE, Development, SIG representative)
- Placeholder text anywhere in the section
- Approvers listed with no reviewers, or reviewers with no approvers

An `OWNERS` file in a feature directory is optional, per `AGENTS.md`. Do not require one; do flag a
multi-SIG feature where no reviewer from a participating SIG appears anywhere.

## Do NOT report

- Whether the Owning SIG or Participating SIGs are correct — [`requirements`](./requirements.md)
- Whether a listed person has actually signed the limitation or risk cells —
  [`constraints`](./constraints.md) checks the cells; you check that the right people are named in the
  right roles
- Whether each role's questions were answered — the
  [`product-manager`](../lenses/product-manager.md) and [`development`](../lenses/development.md) lenses
- Wording, formatting — [`language-hygiene`](./language-hygiene.md)

## Output

Report per [`_output-contract.md`](../_output-contract.md). A parent missing a child link is CRITICAL.
A child duplicating parent content is HIGH. A missing role label in `IV` is HIGH because it makes
approval unverifiable.
