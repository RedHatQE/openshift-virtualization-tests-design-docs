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
   See `docs/stp-guide.md` Section II.8 (Constraints Summary) for definitions.
4. **Traceability is mandatory** — every test scenario must map to a Jira requirement ID with tier and priority.
5. **Concise and actionable** — no walls of text, no template boilerplate left in, no vague statements.

---

## Section-by-Section Review Checklist

### Metadata & Tracking

- [ ] Enhancement(s) links to a VEP, design doc, or HLD (not "N/A" without justification)
- [ ] Feature Tracking links to the feature-level Jira
- [ ] Epic Tracking links to the feature tracking epic (not the QE Jira)
- [ ] Feature Maturity lists each phase with its target version using the structured format:
  `DP: [version or N/A]`, `TP: [version or N/A]`, `GA: [version]`.
  Standard maturity phases: **Dev Preview (DP)**, **Tech Preview (TP)**, **General Availability (GA)**.
  A typical progression is DP → TP → GA across releases (e.g., DP in 4.22, TP in 4.23, GA in 5.0).
  For multi-phase features, the STP scope must clearly state which phase it covers.
- [ ] QE Owner(s) listed with name and contact
- [ ] Owning SIG and Participating SIGs are correct
- [ ] Document Conventions defines only feature-specific terms, not standard ones
  (VM, PVC, CDI, etc. are known to all reviewers — do not define them)
- [ ] Document Conventions uses a bulleted list with one term per line, not inline comma-separated text
- [ ] Reviewer should follow the linked feature request and tracking epic
  to verify:
  - Requirements in the STP align with the feature request definition
  - Acceptance criteria cover the scope defined in the feature epic
- [ ] VEP and design doc links are present and the STP content
  is consistent with those sources

### Feature Overview

- [ ] 2-8 sentences maximum
- [ ] Describes what the feature does from the user's perspective
- [ ] Explains why it matters to customers
- [ ] No implementation details (no API names, no internal component names)
- [ ] For multi-phase features (Dev Preview → Tech Preview → GA), states the current
  phase and which phase this STP covers
- [ ] Claims made in the Feature Overview (e.g., "isolated," "secure," "non-disruptive,"
  "seamless") must have matching acceptance criteria and test scenarios. If the feature
  doesn't test a claim: remove the claim from the Overview, document it in Out of Scope
  with Rationale and PM/Lead Agreement (name/date), or reference existing coverage
  elsewhere (do not use Out of Scope for work already covered by other teams/suites).

**Common rejection reasons:**
- Feature Overview makes claims ("hardware-isolated," "safe multi-tenant") with no matching
  acceptance criteria or test scenarios, and without documenting the gap in Out of Scope
  with Rationale and PM/Lead Agreement
- Feature Overview describes internal system changes instead of user capabilities

### I.1 — Requirement & User Story Review

- [ ] All checklist items have checkboxes marked `[x]` with content filled in
- [ ] Requirements are listed as specific, testable items — not a repetition of the Feature Overview
- [ ] Customer use cases are in user story format ("As a [role], I want to [action]")
- [ ] Acceptance criteria are individual list items — each is a specific, verifiable pass/fail condition
- [ ] Acceptance criteria describe observable user outcomes, not internal system behavior
- [ ] For features claiming seamless or non-disruptive behavior, acceptance criteria must include
  at least one condition that can *only* pass if disruption never occurred. A criterion that checks
  end-state alone (e.g., "X is present after the operation") is insufficient — it would also pass
  after a disruptive stop-and-restart cycle. The criterion must be one that *would fail* if a
  disrupt-then-restore sequence happened instead of the claimed seamless path.
- [ ] NFRs explicitly address: Monitoring, Observability, UI, Documentation, Performance, Security, Scalability
- [ ] NFRs not covered have justification
- [ ] Scalability NFR: if the feature relies on a platform mechanism (e.g., live migration) that
  has existing scale constraints (e.g., cluster-level parallelism limits), those constraints must
  be acknowledged — even if the feature itself introduces no new scale requirements. Saying "no new
  scale requirements" is not sufficient when the underlying mechanism imposes limits.
- [ ] UI NFR: "no UI changes introduced" does not justify dismissing UI testing. The question is
  whether UI testing adds value from a customer perspective. That determination belongs to PM or UX,
  not QE. If the answer is "not needed," it must be reasoned from customer value, not from the
  absence of code changes.

**Common rejection reasons:**
- Acceptance criteria say "feature works" instead of specifying HOW we know it works
- Acceptance criteria for seamless/non-disruptive features only verify end-state — a disrupt-then-restore
  sequence would produce the same passing result
- Requirements repeat the feature overview instead of listing actual D/S Jira requirements
- NFRs section says "N/A" without explaining why each NFR category doesn't apply
- Scalability NFR dismissed as "no new requirements" when the feature depends on a mechanism with
  existing cluster-level scale limits
- UI NFR dismissed with "no UI changes" without PM/UX input on whether testing adds customer value

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
  run on the feature cluster. Regression testing is primarily documented in Test Strategy (II.2),
  and regression tests are NOT included in the Test Scenarios table (III).
- [ ] At least one negative or failure-path Testing Goal exists for each P0 functional goal
  (e.g., "what happens if migration fails?", "what if the VM starts during the operation?",
  "what about error handling?"). If negative scenarios are out of scope, they must be
  documented in Out of Scope with PM/Lead agreement — "considered" alone is insufficient.
- [ ] Goals are ordered by priority (P0 first, then P1, then P2)
- [ ] Testing goals are fully actionable: they name all configuration dimensions needed to implement
  the test (e.g., for networking: both the binding type and the CNI in use). A goal that names
  only one dimension leaves test authors to guess the rest.
- [ ] Test scenarios that validate behavior *after* a feature operation has completed and the system
  has reached a stable state (e.g., "verify behavior after upgrade", "verify VM is migratable after
  feature completes") require explicit justification. Once stable, the system typically cannot
  distinguish how it arrived there. Such scenarios must name a concrete mechanism by which the
  feature's prior execution would produce a different outcome than a baseline reaching the same state.

**Out of Scope:**
- [ ] Each item has Rationale and PM/Lead Agreement with name and date
- [ ] Items are decisions QE made (not constraints imposed on QE — those are Test Limitations)
- [ ] Format per template: `- **Item** / *Rationale:* / *PM/Lead Agreement:*`
- [ ] Items are genuinely out of scope — if already tested elsewhere,
  document as existing coverage, not out of scope

**Test Limitations:**
- [ ] Each limitation has sign-off: `*Sign-off:* [Name/Date]`
- [ ] Items are constraints imposed on QE (not decisions QE made — those are Out of Scope)

**Common rejection reasons:**
- Testing goals use implementation language ("verify boot sources are provisioned")
  instead of user language ("deploy a VM from each available boot source")
- Out of Scope items have `[Name/Date]` placeholder instead of actual sign-offs
- Regression tests mixed with new functional tests in Testing Goals
- Missing priority levels on goals
- Testing goal names only one configuration dimension (e.g., binding type) when others are required
  (e.g., CNI) to make the goal implementable
- Test scenario added for post-stable-state behavior without justifying why the feature's
  execution history would produce a different outcome than baseline
- No negative or failure-path Testing Goal (with matching Section III scenario) for P0 goals — only happy-path coverage

### II.2 — Test Strategy

- [ ] All testing types are addressed (checked or unchecked with justification)
- [ ] All 14 testing types from the template are present (Functional, Automation, Regression, Self-Validation,
  Performance, Scale, Security, Usability, Monitoring, Compatibility, Upgrade, Dependencies,
  Cross Integrations, Cloud Testing)
- [ ] Unchecked items without details = incomplete review — flag this
- [ ] Self-Validation: if the feature introduces core operational scenarios, confirm whether
  any new tests should be included in the self-validation test package
- [ ] Usability Testing: if checked, must describe what QE tests (not "UI team owns it")
- [ ] If UI team owns UI testing, uncheck Usability and note in details
- [ ] Monitoring: explicitly state whether alerts/metrics are required
- [ ] Security: if Security NFR or Security Testing makes specific security claims
  (e.g., "prevents command injection," "restricts access to authorized commands"),
  a matching Testing Goal (II.1) and Section III scenario must exist. Vague security
  claims without test coverage create false confidence.
- [ ] Upgrade Testing: even if N/A, confirm the upgrade path was evaluated
- [ ] Performance/Scale: even if deferred, document the consideration and plans
- [ ] UI: if the feature has UI work, document who tests it (QE or UI team) with Jira link
- [ ] If any testing type's details state something "must be verified/tested/validated,"
  a corresponding Testing Goal (II.1) and Section III scenario must exist. Claims in
  Test Strategy that aren't backed by goals/scenarios are empty promises.
- [ ] Test Strategy details describe what is tested and how — not QE internal processes
  (triage workflows, bug filing conventions, defect classification). Keep process
  documentation in QE runbooks, not STPs.

**Common rejection reasons:**
- Usability checked but details say "UI team covers this" (contradictory)
- Items marked N/A without justification
- Upgrade Testing marked N/A without confirming upgrade path was considered
- Test Strategy details claim something "must be verified" but no Testing Goal or scenario covers it

### II.3 — Test Environment

- [ ] All fields filled or marked N/A (no empty fields)
- [ ] OCP and OpenShift Virtualization versions are explicit (exact versions
  preferred; qualified ranges like "4.22 and later" are acceptable)
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

### II.4.1 — Cross-Section Consistency

Reviewers must verify these cross-references between sections:

- [ ] Entry Criteria completion status (`[x]` vs `[ ]`) matches Dependencies and Test Limitations
  — do not mark entry criteria complete if Dependencies or Test Limitations describe the same
  item as a blocker
- [ ] Testability claims ("all requirements testable through existing suites") align with
  Automation Testing (II.2) and Section III — if new automation is required, Testability
  must say so
- [ ] Out of Scope "None" must be consistent with Test Strategy exclusions — if any testing
  type explicitly skips coverage (e.g., Cloud Testing says "no dedicated cloud scenarios"),
  that exclusion belongs in Out of Scope, not hidden in Test Strategy details
- [ ] Security/Monitoring claims in Test Strategy (II.2) must have matching Testing Goals
  in II.1 and Section III scenarios (see II.2 Security and must-be-verified rules)

### II.5 — Risks

- [ ] ALL 6 standard risk categories are addressed (even if no risk, include Mitigation with brief justification):
  Timeline/Schedule, Test Coverage, Test Environment, Untestable Aspects,
  Resource Constraints, Dependencies
- [ ] "Other" category is included only if risks exist that don't fit the 6 standard categories above
- [ ] When a risk exists: full entry required — Risk description, Mitigation strategy, Sign-off,
  and the category-specific supplemental field:
  *Estimated impact on schedule* (Timeline/Schedule),
  *Areas with reduced coverage* (Test Coverage),
  *Missing or unavailable environments* (Test Environment),
  *Missing resources or infrastructure* (Resource Constraints),
  *Third-party services or blockers* (Dependencies),
  *Reason untestable and mitigation approach* (Untestable Aspects)
- [ ] When no risk exists: only a short justification in the Mitigation field is needed
  (not just "N/A"); no Sign-off or category-specific supplemental fields are required
- [ ] Mitigations are specific and actionable (not "we will address this")

**Common rejection reasons:**
- All risks marked N/A (unrealistic — every feature has some risk)
- Missing sign-off on risk entries where a real risk is described
- Mitigation says "N/A" without explaining why no mitigation is needed
- Vague mitigations without specific actions
- Missing risk categories entirely

### III — Test Scenarios & Traceability

- [ ] Every scenario has a Jira Requirement ID (not "[TBD]").
  In the scenarios table, multiple test scenarios mapped to the same requirement
  may leave the Requirement ID cell blank in continuation rows.
- [ ] Requirement summaries use user story format ("As a [role], I want...")
- [ ] Each scenario has Tier (1, 2, or 3) and Priority (P0/P1/P2)
- [ ] Every Testing Goal from Section II.1 has a matching scenario here
- [ ] Every Acceptance Criterion from Section I.1 is traceable to a scenario
- [ ] Granularity: if one scenario can fail while another passes, they are separate items
- [ ] Scenario descriptions include observable pass criteria — not just "verify X works correctly."
  Define what "correctly" means (e.g., "metrics are non-zero and consistent with the observed
  migration workload," not "metrics are reported correctly")
- [ ] Scenario expected outcomes are correct — especially for security-sensitive operations.
  A scenario that expects success for a path-traversal input or injection payload validates
  a vulnerability as correct behavior. Verify the expected result matches the feature's
  intended security posture.
- [ ] Regression tests are NOT listed here (they belong in Test Strategy)

**Tier classification:**
- **Tier 1**: Single feature, isolated — API validation, basic CRUD, single operation
- **Tier 2**: End-to-end user workflows, multi-feature integration, upgrade paths
- **Tier 3**: Extended validation — tests with higher execution cost (longer runtime, heavier resource usage, or complex setup) that typically run in dedicated test cycles rather than standard CI lanes

**Common rejection reasons:**
- All requirement IDs are "[TBD]" — blocks approval
- Test scenarios describe implementation ("verify DataSource creation") instead of
  user outcomes ("verify VMs can be created from architecture-specific boot sources")
- Missing tier or priority
- Scenarios don't map back to acceptance criteria
- Scenario descriptions use unmeasurable language ("works correctly," "reported correctly")
  without defining observable pass criteria
- Scenario expects the wrong outcome (e.g., success for a path-traversal input that should
  be rejected) — a test with the wrong expected result validates bugs as features

### IV — Sign-off and Approval

- [ ] Reviewers listed with names and GitHub handles
- [ ] Approvers listed with explicit role labels (QE Lead, Dev Lead, PM at minimum)
  — each approver must include their role, name, and GitHub handle
- [ ] Reviewers listed with role context (QE, Development, SIG representatives)
- [ ] No placeholder text remaining

---

## Multi-SIG Features

When an STP spans multiple SIGs:

- All participating SIGs must be listed and must have confirmed their test scope
- Child STPs (per-SIG) should NOT duplicate the parent STP — they extend it
- Each SIG's regression responsibility must be explicitly documented
- Cross-SIG test scenarios (e.g., cross-architecture VM connectivity) must have a clear owner

### Directory Structure

Multi-SIG features use a **feature directory** under the owning SIG:

```text
stps/<owning-sig>/<feature-name>/
├── stp.md              ← parent STP (owned by the feature's primary SIG)
├── <sig-name>.md       ← child STP per participating SIG
└── ...
```

Example — multi-arch feature owned by sig-iuo with 4 participating SIGs:

```text
stps/sig-iuo/multiarch/
├── stp.md
├── network.md
├── storage.md
├── virt.md
└── infra.md
```

**Rules:**

- The parent STP (`stp.md`) defines the overall scope, requirements, and acceptance criteria
- Each child STP covers only the participating SIG's test scope — goals, scenarios, and risks
  specific to that SIG
- Child STPs should follow the child STP template (`stps/stp-template/child-stp.md`)
- Child STPs reference the parent for shared context (Feature Overview, requirements, acceptance
  criteria) — they do NOT repeat it
- The feature directory may include an `OWNERS` file listing reviewers from all participating SIGs
- Single-SIG features do NOT use a feature directory — place the STP directly under `stps/<sig>/`

### Child STP Review Checklist

- [ ] Parent STP lists all child STPs in the feature directory with links
- [ ] Child STP follows the child STP template (`stps/stp-template/child-stp.md`)
- [ ] Child STP does NOT duplicate Feature Overview, requirements, or acceptance criteria from parent
- [ ] Child STP defines only the participating SIG's test scope, scenarios, and risks
- [ ] When a child STP is added to a feature directory that already has a parent STP,
  verify the parent is updated to include the new child
- [ ] When a parent STP is added to a feature directory that already contains child STPs,
  verify the parent lists all existing children

---

## Content Quality Rules

### DO
- Write from the user's perspective ("As a VM admin, I want to...")
- Use specific, verifiable language in acceptance criteria
- Provide rationale for every out-of-scope item
- Link every test scenario to a Jira requirement
- Clearly separate: Feature Limitations | Test Limitations | Out of Scope | Risks
- Use the current template format for STPs being added or modified in the PR
  (do not retroactively enforce on already-merged STPs)
- Remove all template HTML comments and example text before submitting
- Include at least one negative or failure-path Testing Goal for each P0 functional goal,
  with a matching Section III scenario — or document the omission in Out of Scope with PM/Lead agreement
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
- Include QE internal process language in Test Strategy (triage, bug filing, defect classification)
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
