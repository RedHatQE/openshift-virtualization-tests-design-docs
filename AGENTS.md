# AI Review Guide for STP Pull Requests

This document defines the review standards for Software Test Plans (STPs) in this repository.
It is used by AI review tools (CodeRabbit, Claude Code) and human reviewers.

For template structure and STP lifecycle, see `docs/stp-guide.md` and `stps/stp-template/stp.md`.

Assisted-by: Claude <noreply@anthropic.com>

---

## Core Principles

1. **User perspective only** — STPs describe what users experience, not how the system works internally.
   No API field names, CRD names, internal component references, or implementation mechanisms.
2. **Every claim needs evidence** — sign-offs, Jira links, dates. No empty placeholders in approved STPs.
3. **Distinguish constraint categories** — Feature Limitations, Test Limitations, Out of Scope, and Risks
   are four distinct concepts. Never mix them.
4. **Traceability is mandatory** — every test scenario must map to a Jira requirement ID with tier and priority.
5. **Concise and actionable** — no walls of text, no template boilerplate left in, no vague statements.

---

## Section-by-Section Review Checklist

### Metadata & Tracking

- [ ] Enhancement(s) links to a VEP, design doc, or HLD (not "N/A" without justification)
- [ ] Feature Tracking links to the feature-level Jira
- [ ] Epic Tracking links to the feature tracking epic (not the QE Jira)
- [ ] QE Owner(s) listed with name and contact
- [ ] Owning SIG and Participating SIGs are correct
- [ ] Document Conventions defines only feature-specific terms, not standard ones
  (VM, PVC, CDI, etc. are known to all reviewers — do not define them)

### Feature Overview

- [ ] 2-8 sentences maximum
- [ ] Describes what the feature does from the user's perspective
- [ ] Explains why it matters to customers
- [ ] No implementation details (no API names, no internal component names)

### I.1 — Requirement & User Story Review

- [ ] All checklist items have checkboxes marked `[x]` with content filled in
- [ ] Requirements are listed as specific, testable items — not a repetition of the Feature Overview
- [ ] Customer use cases are in user story format ("As a [role], I want to [action]")
- [ ] Acceptance criteria are individual list items — each is a specific, verifiable pass/fail condition
- [ ] Acceptance criteria describe observable user outcomes, not internal system behavior
- [ ] NFRs explicitly address: Monitoring, Observability, UI, Documentation, Performance, Security, Scalability
- [ ] NFRs not covered have justification

**Common rejection reasons:**
- Acceptance criteria say "feature works" instead of specifying HOW we know it works
- Requirements repeat the feature overview instead of listing actual D/S Jira requirements
- NFRs section says "N/A" without explaining why each NFR category doesn't apply

### I.2 — Known Limitations

- [ ] Each limitation has a sign-off: `*Sign-off:* [Name/Date]`
- [ ] Limitations are constraints (not scope decisions)
- [ ] If no limitations: "None — reviewed and confirmed with [Name/Date]"
- [ ] Open bugs that affect the feature are listed with Jira links

**Common rejection reasons:**
- "None identified" without sign-off confirmation
- Test limitations listed here instead of in Section II.1
- Out-of-scope decisions listed here instead of in Section II.1

### I.3 — Technology and Design Review

- [ ] All items use `[x]` checkboxes
- [ ] Developer Handoff describes actual meeting takeaways, not just "meeting conducted"
- [ ] Technology Challenges lists specific challenges and their impact on testing
- [ ] API Extensions mentions only user-facing APIs — no internal component APIs
- [ ] Topology Considerations specifies cluster requirements and impact on test design
- [ ] Topology Considerations describes cluster and network topology — not internal resource creation

**Common rejection reasons:**
- Developer Handoff is a single generic sentence with no substance
- API Extensions lists 10+ internal API fields (belongs in design doc, not STP)
- Technology Challenges mentions implementation mechanisms instead of testing impact

### II.1 — Scope of Testing

**Testing Goals:**
- [ ] Written from end-user perspective ("Deploy a VM from..." not "Verify DataImportCron creates...")
- [ ] Each goal has priority: P0 (blocks GA), P1 (required for coverage), P2 (nice-to-have)
- [ ] Goals are SMART: Specific, Measurable, Achievable, Relevant, Verifiable
- [ ] Distinguish between new functional tests and regression tests
- [ ] If regression goals are included in Testing Goals, they identify which SIG test suites
  run on the feature cluster (regression is also addressed in Test Strategy Section II.2)
- [ ] Negative and edge-case scenarios are considered (e.g., "what happens if migration fails?",
  "what if the VM starts during the operation?", "what about error handling?")
- [ ] Goals are ordered by priority (P0 first, then P1, then P2)

**Out of Scope:**
- [ ] Each item has Rationale and PM/Lead Agreement with name and date
- [ ] Items are decisions QE made (not constraints imposed on QE — those are Test Limitations)
- [ ] Format per template: `- **Item** / *Rationale:* / *PM/Lead Agreement:*`
- [ ] Items are genuinely out of scope — NOT items already covered by other teams or existing tests
  ("already covered in 4.21" is NOT out of scope — it's existing coverage)

**Test Limitations:**
- [ ] Each limitation has sign-off: `*Sign-off:* [Name/Date]`
- [ ] Items are constraints imposed on QE (not decisions QE made — those are Out of Scope)

**Common rejection reasons:**
- Testing goals use implementation language ("verify boot sources are provisioned")
  instead of user language ("deploy a VM from each available boot source")
- Out of Scope items have `[Name/Date]` placeholder instead of actual sign-offs
- Regression tests mixed with new functional tests in Testing Goals
- Missing priority levels on goals

### II.2 — Test Strategy

- [ ] All testing types are addressed (checked or unchecked with justification)
- [ ] All 13 testing types from the template are present (Functional, Automation, Regression,
  Performance, Scale, Security, Usability, Monitoring, Compatibility, Upgrade, Dependencies,
  Cross Integrations, Cloud Testing)
- [ ] Unchecked items without details = incomplete review — flag this
- [ ] Usability Testing: if checked, must describe what QE tests (not "UI team owns it")
- [ ] If UI team owns UI testing, uncheck Usability and note in details
- [ ] Monitoring: explicitly state whether alerts/metrics are required
- [ ] Upgrade Testing: even if N/A, confirm the upgrade path was evaluated
- [ ] Performance/Scale: even if deferred, document the consideration and future plans
- [ ] UI: if the feature has UI work, document who tests it (QE or UI team) with Jira link

**Common rejection reasons:**
- Usability checked but details say "UI team covers this" (contradictory)
- Items marked N/A without justification
- Upgrade Testing marked N/A without confirming upgrade path was considered

### II.3 — Test Environment

- [ ] All fields filled or marked N/A (no empty fields)
- [ ] OCP and OpenShift Virtualization versions are exact (not "4.x")
- [ ] Storage class specified (not generic)
- [ ] Platform specified (Bare metal, AWS, etc.)
- [ ] Special Configurations documented if non-standard

### II.3.1 — Testing Tools & Frameworks

- [ ] Only lists NEW or non-standard tools
- [ ] Standard tools (pytest, etc.) are NOT listed
- [ ] CI/CD: if a special Jenkins job or lane is needed, document it

### II.4 — Entry Criteria

- [ ] At minimum: requirements approved + test environment configured
- [ ] Feature-specific entry criteria added where applicable
- [ ] Items marked `[x]` when completed, `[ ]` when pending

### II.5 — Risks

- [ ] ALL 7 risk categories are addressed (even if N/A with justification):
  Timeline/Schedule, Test Coverage, Test Environment, Untestable Aspects,
  Resource Constraints, Dependencies, Other
- [ ] Each risk has: Risk description, Mitigation strategy, Sign-off
- [ ] N/A risks have brief justification (not just "N/A")
- [ ] Mitigations are specific and actionable (not "we will address this")

**Common rejection reasons:**
- All risks marked N/A (unrealistic — every feature has some risk)
- Missing sign-off fields on risk entries
- Vague mitigations without specific actions
- Missing risk categories entirely

### III — Test Scenarios & Traceability

- [ ] Every scenario has a Jira Requirement ID (not "[TBD]").
  Continuation rows sharing the same epic may leave the ID blank.
- [ ] Requirement summaries use user story format ("As a [role], I want...")
- [ ] Each scenario has Tier (1 or 2) and Priority (P0/P1/P2)
- [ ] Every Testing Goal from Section II.1 has a matching scenario here
- [ ] Every Acceptance Criterion from Section I.1 is traceable to a scenario
- [ ] Granularity: if one scenario can fail while another passes, they are separate items
- [ ] Regression tests are NOT listed here (they belong in Test Strategy)

**Tier classification:**
- **Tier 1**: Single feature, isolated — API validation, basic CRUD, single operation
- **Tier 2**: End-to-end user workflows, multi-feature integration, upgrade paths

**Common rejection reasons:**
- All requirement IDs are "[TBD]" — blocks approval
- Test scenarios describe implementation ("verify DataSource creation") instead of
  user outcomes ("verify VMs can be created from architecture-specific boot sources")
- Missing tier or priority
- Scenarios don't map back to acceptance criteria

### IV — Sign-off and Approval

- [ ] Reviewers listed with names and GitHub handles
- [ ] Approvers listed (QE Lead, PM, Dev Lead at minimum)
- [ ] No placeholder text remaining

---

## Multi-SIG Features

When an STP spans multiple SIGs:

- All participating SIGs must be listed and must have confirmed their test scope
- Child STPs (per-SIG) should NOT duplicate the parent STP — they extend it
- Each SIG's regression responsibility must be explicitly documented
- Cross-SIG test scenarios (e.g., cross-architecture VM connectivity) must have a clear owner

---

## Content Quality Rules

### DO
- Write from the user's perspective ("As a VM admin, I want to...")
- Use specific, verifiable language in acceptance criteria
- Provide rationale for every out-of-scope item
- Link every test scenario to a Jira requirement
- Clearly separate: Feature Limitations | Test Limitations | Out of Scope | Risks
- Use the current template format (checklists for Section I, checklists for Test Strategy)
- Remove all template HTML comments and example text before submitting
- Consider negative and edge-case test scenarios (error handling, partial failures, concurrent operations)
- Document what is NOT tested with explicit sign-off — anything untested must be visible
- Order testing goals by priority (P0 first)

### DON'T
- Use implementation terms (API field names, CRD names, internal component names)
- Leave template placeholder text ("[Add details]", "[Name/Date]", "[TBD]")
- Mark all risks as N/A
- Mix constraint categories (limitations vs. out-of-scope vs. risks)
- List standard tools in Testing Tools section
- Define standard acronyms in Document Conventions (VM, PVC, CDI are known)
- Repeat the Feature Overview in the Requirements section
- Leave checklist items unchecked when content is filled in
- List items as "Out of Scope" when they are already covered by existing tests or other teams
- Describe Topology Considerations in terms of internal resource creation — use cluster/network topology only
- Submit child STPs that duplicate content from the parent STP

---

## Formatting Rules

- Follow `.markdownlint.yaml` configuration
- Code blocks must specify language (MD040)
- Images must have alt text (MD045)
- No multiple consecutive blank lines
- Trailing whitespace will be removed by pre-commit hooks
- Files must end with a newline
- Inline HTML is allowed for complex formatting

---

## Review Severity Levels

| Level | Meaning | Action |
|-------|---------|--------|
| **CRITICAL** | Blocks approval. Missing traceability, empty sign-offs, contradictions | Must fix before merge |
| **HIGH** | Template non-compliance, incomplete sections, vague content | Must fix before merge |
| **MEDIUM** | Formatting issues, minor content improvements | Should fix |
| **LOW** | Style suggestions, optional enhancements | Nice to have |
