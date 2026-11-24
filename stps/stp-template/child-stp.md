# Openshift-virtualization-tests Test plan

<!-- STRUCTURE IS FIXED.
This child template defines the section structure and field set for a participating SIG's scope. Fill
each field as it appears; do not add, rename, remove, or reorder sections, checklist items, fields,
or Section III keys. Repeating a content line — a requirement, acceptance criterion, NFR,
feature or test limitation, out-of-scope exclusion, challenge, API, topology item, goal,
environment requirement, entry criterion, risk entry, scenario, or Document Conventions term —
is content, not a new field.

The only required-structure fields you may omit are `Document Conventions (if applicable)` and, in a
no-risk category, the category-specific field (where present — Other has none) and the `Sign-off`
line (unused example goal priority rows are repeatable content, not required fields). Every risk
category heading stays as written; a category with no SIG-specific risk keeps its `Risk` line and
fills it with `None — [reason]`. A structural change is a separate PR that updates the template it
changes and the other four copies of the rule (AGENTS.md, docs/stp-guide.md, the `.coderabbit.yaml`
structure block, the `.pr_agent.toml` instructions) — see Template Structure Compliance in AGENTS.md.

Comments carry guidance only — never a field, key, or value — and are deleted before submitting.
Replace every placeholder; never delete a required field (only the omissions listed above and unused
example goal priorities may be dropped).

An older child STP is re-shaped onto these lines in the entries it edits; the entries a PR leaves
alone keep their approved shape. -->

## **[Feature Title — SIG-Specific Scope] - Quality Engineering Plan**

### **Metadata & Tracking**

- **Feature Tracking:** [Link to the relevant feature in Jira]
- **Epic Tracking:** [Link to the SIG-specific tracking Jira Epic, or "Same as parent"]
- **QE Owner(s):** [Name (@github-handle, email)]
- **SIG:** [sig-xyz — the SIG this child STP covers]

**Document Conventions (if applicable):**
<!-- If no SIG-specific terms apply, omit both the label and its bullet. Otherwise keep the label and
repeat the bullet once per term — both lines are the template's own shape, not new fields. -->
- **[term]** — [define a term specific to this SIG's scope only]

### **Feature Overview**

<!-- In child STPs: describe this SIG's scope within the parent feature.
Do NOT repeat the parent's Feature Overview. -->

[Describe what this SIG covers within the feature and why it requires separate test planning.]

---

### **I. Motivation and Requirements Review (QE Review Guidelines)**

*This section records the quality interpretation of the SIG's part of the feature. Its purpose is to expose
misunderstandings before testing starts, so reviewers should check it against their own understanding.*

<!-- In child STPs: this section covers only SIG-specific review items.
Feature-wide requirements, acceptance criteria, and NFRs are defined in the parent STP. -->

#### **1. Requirement & User Story Review Checklist**

- [ ] **Review Requirements**
  <!-- List the requirements this SIG owns, or "None — all requirements are in the parent STP".
  A requirement states a behavior and the condition it must hold under, so a test can pass or fail
  on it. Repeat the line per requirement — content lines, not new fields. -->
  - [SIG-specific requirement, or "None — all requirements are in the parent STP"]

- [ ] **Acceptance Criteria**
  <!-- Only list acceptance criteria specific to this SIG's scope, each an observable pass/fail
  condition. Repeat the line per criterion. -->
  - [SIG-specific acceptance criterion, or "None — all acceptance criteria are in the parent STP"]

- [ ] **Testability**
  <!-- Any SIG-specific requirement that is unclear, ambiguous, or untestable, and why. Repeat the
  line per requirement. -->
  - [Unclear or untestable SIG-specific requirement and why, or "None — [reason]"]

- [ ] **Non-Functional Requirements (NFRs)**
  <!-- Only list NFRs specific to this SIG's scope. Repeat the nested bullet under either label as
  needed — these are the template's own nested lines, not new fields. If all NFRs are covered by the
  parent STP, state that under the first label and write "N/A — all NFRs are covered by the parent
  STP" under the second. -->
  - *SIG-specific NFRs:*
    - [SIG-specific NFR and its target, or "None — all NFRs are covered by the parent STP"]
  - *NFRs not covered or N/A:*
    - [SIG-specific NFR not covered or not applicable and why, "None — all SIG-specific NFRs are covered", or "N/A — all NFRs are covered by the parent STP"]

#### **2. Feature Limitations**

<!-- List only SIG-specific limitations. Feature-wide limitations belong in the parent STP.
If none, state "None — reviewed and confirmed with [Name]" and keep the `*Sign-off:*` line. -->

- **[SIG-specific limitation, or "None — reviewed and confirmed with [Name]"]**
  - *Sign-off:* [Name]

#### **3. Technology and Design Review**

- [ ] **Developer Handoff/QE Kickoff**
  - *Key takeaways and concerns:* [SIG-specific technical concerns]

- [ ] **Technology Challenges**
  <!-- The SIG-specific technical challenges, and their impact on how this SIG tests the feature. -->
  - [SIG-specific testing challenge]
  - *Impact on testing approach:* [Impact on this SIG's tests]

- [ ] **API Extensions**
  <!-- New APIs belong in the parent STP. List here only if this SIG tests existing APIs
  in a SIG-specific way, otherwise state "N/A — see parent STP". -->
  - [SIG-specific testing of an existing user-facing API, or "N/A — see parent STP"]
  - *Testing impact:* [Impact]

- [ ] **Test Environment Needs**
  - *See environment requirements in Section II.3 and testing tools in Section II.3.1*

- [ ] **Topology Considerations**
  <!-- Cluster and network topology the SIG needs — not internal resource creation. -->
  - [SIG-specific topology requirement]
  - *Impact on test design:* [Impact]

### **II. Software Test Plan (STP)**

#### **1. Scope of Testing**

**Testing Goals**

<!-- List only this SIG's testing goals. Feature-wide goals belong in the parent STP.
Order by priority: P0 first, then P1, then P2. Priorities refer to GA. As in the parent STP, an optional phase tag
(e.g. `[P0][TP]`) marks goals that must also pass at an intermediate phase; phase names come from the parent STP.

Each P0 functional goal needs a negative or failure-path goal next to it — with a matching
Section III scenario — or the omission documented in Out of Scope with Quality Owner or Product Manager
sign-off — "considered" alone is insufficient. A negative path that is also an Acceptance Criterion
cannot be moved to Out of Scope: Section III covers it (or named existing regression coverage in Test
Strategy). The `[P0]`/`[P1]`/`[P2]` lines below are repeatable goal examples: keep only the priority
levels that apply (omit `[P1]` or `[P2]` if this SIG has none, and omit a negative `[P0]` line if it
was waived in Out of Scope). -->

- **[P0]** [SIG-specific testing goal]
- **[P0]** [SIG-specific negative or failure-path testing goal]
- **[P1]** [SIG-specific testing goal]
- **[P2]** [SIG-specific testing goal]

**Out of Scope (Testing Scope Exclusions)**

<!-- List items this SIG explicitly will not test. If something is out of scope for the
entire feature, it belongs in the parent STP — not here. If none, state "None — [why]" and keep the
`*Rationale:*` and `*Sign-off (Quality Owner or Product Manager):*` lines. -->

- **[Item]**
  - *Rationale:* [Why this SIG won't test it]
  - *Sign-off (Quality Owner or Product Manager):* [Name]

**Test Limitations**

<!-- Constraints on this SIG's testing approach. If none, state "None — [why]" and keep the
`*Sign-off:*` line. -->

- **[Test Limitation]**
  - *Sign-off:* [Name]

#### **2. Test Strategy**

<!-- Mark items that this SIG will test. For items covered by the parent STP or other SIGs,
uncheck and state "Covered by parent STP" or "Covered by [SIG name]"; where an item does not apply
to this SIG at all, uncheck and state "N/A — [reason]". -->

**Functional**

- [ ] **Functional Testing**
  - *Details:* [SIG-specific functional testing approach]

- [ ] **Automation Testing**
  - *Details:* [SIG-specific automation plan]

- [ ] **Regression Testing**
  - *Details:* [Which existing SIG test suites run on the feature cluster]

- [ ] **Self-Validation Testing** — Tests to include in the self-validation package
  - *Details:* [SIG-specific, or "Covered by parent STP"]

**Non-Functional**

- [ ] **Performance Testing**
  - *Details:* [SIG-specific, or "Covered by parent STP"]

- [ ] **Scale Testing**
  - *Details:* [SIG-specific, or "Covered by parent STP"]

- [ ] **Security Testing**
  - *Details:* [SIG-specific, or "Covered by parent STP"]

- [ ] **Usability Testing**
  - *Details:* [SIG-specific, or "Covered by parent STP"]

- [ ] **Monitoring**
  - *Details:* [SIG-specific; state whether alerts/metrics are required, or "Covered by parent STP"]

**Integration & Compatibility**

- [ ] **Compatibility Testing**
  - *Details:* [SIG-specific, "Covered by parent STP", or "N/A — [reason]"]

- [ ] **Upgrade Testing**
  - *Details:* [SIG-specific, or "Covered by parent STP"]

- [ ] **Dependencies**
  - *Details:* [SIG-specific blocking dependencies]

- [ ] **Cross Integrations**
  - *Details:* [SIG-specific, or "Covered by parent STP"]

**Infrastructure**

- [ ] **Cloud Testing**
  - *Details:* [SIG-specific, "Covered by parent STP", or "N/A — [reason]"]

#### **3. Test Environment**

<!-- Covered in the parent STP; state here only what this SIG adds or overrides. Repeat the line
per requirement. If nothing applies, write "None — covered by the parent STP". -->

- [SIG-specific environment requirement, or "None — covered by the parent STP"]

#### **3.1. Testing Tools & Frameworks**

<!-- List only tools this SIG adds that are new or non-standard to the feature's testing. `Standard`
and `N/A` stay as they are when no such tool applies. -->

- **Test Framework:** Standard

- **CI/CD:** [SIG-specific CI lanes, or N/A]

- **Other Tools:** N/A

#### **4. Entry Criteria**

<!-- Covered by the parent STP. Add SIG-specific entry criteria below — repeating the line for each
one is content, not a new field. If none apply, write "None — covered by the parent STP". A child STP
carries no completion status here: the parent tracks it. -->

- [SIG-specific entry criterion, or "None — covered by the parent STP"]

#### **5. Risks**

Feature-wide risks are stated in the parent STP ([Risks](./stp.md#5-risks)) and are not repeated here.

<!-- List only risks specific to this SIG, grouped under the same categories as the parent.
Keep every category below — the field names are the ones the parent template defines.
A risk is an uncertainty: something that might happen and could block testing. A constraint that is
already true is a Test Limitation, and a testing decision already taken is Out of Scope; neither
belongs here.

No SIG-specific risk in a category: write `None — [reason]` in `Risk` and `Not applicable — [same
reason]` in `Mitigation`, and drop the category-specific field (where present — Other has none) and
the `Sign-off` line. The reason is this SIG's own, e.g. "None — schedule is fully governed by the
parent STP milestone with no SIG-specific gating"; "None — no SIG-specific risk" is not a reason.
When the SIG has no specific risk anywhere, each category still gives its own reason. -->

**Timeline/Schedule**

- **Risk:** [What might delay this SIG's testing, or "None — reason"]
  - **Mitigation:** [Mitigation plan, or "Not applicable — same reason"]
  - *Estimated impact on schedule:* [Delay or schedule impact]
  - *Sign-off:* [Name]

**Test Coverage**

- **Risk:** [Which areas might end up under-tested, or "None — reason"]
  - **Mitigation:** [Mitigation plan, or "Not applicable — same reason"]
  - *Areas with reduced coverage:* [Affected areas]
  - *Sign-off:* [Name]

**Test Environment**

- **Risk:** [What environment resource might be unavailable, or "None — reason"]
  - **Mitigation:** [Mitigation plan, or "Not applicable — same reason"]
  - *Missing resources or infrastructure:* [What is unavailable]
  - *Sign-off:* [Name]

**Untestable Aspects**

- **Risk:** [What this SIG might not be able to verify, or "None — reason"]
  - **Mitigation:** [Alternative validation, or "Not applicable — same reason"]
  - *Alternative validation approach:* [Fallback validation]
  - *Sign-off:* [Name]

**Resource Constraints**

- **Risk:** [What capacity might fall short, or "None — reason"]
  - **Mitigation:** [Prioritization plan, or "Not applicable — same reason"]
  - *Current capacity gaps:* [Staffing or skill gaps]
  - *Sign-off:* [Name]

**Dependencies**

- **Risk:** [Which external dependency might slip or change, or "None — reason"]
  - **Mitigation:** [Coordination plan, or "Not applicable — same reason"]
  - *Dependent teams or components:* [External dependencies]
  - *Sign-off:* [Name]

**Other**

<!-- An uncertainty that does not fit the six categories above. -->

- **Risk:** [Other uncertainty for this SIG, or "None — reason"]
  - **Mitigation:** [Plan, or "Not applicable — same reason"]
  - *Sign-off:* [Name]

---

### **III. Test Scenarios & Traceability**

<!-- List only this SIG's NEW test scenarios. Each scenario must trace to a Jira requirement.
Every non-regression Testing Goal above has a matching scenario here. Every SIG-specific Acceptance Criterion is
covered by a scenario here, or by named existing regression coverage in Test Strategy (II.2). Regression tests are
documented in Test Strategy (II.2), not in this section. The entry shape is the parent's: the tier is inline in
`Test Scenario`; how Tier 1 / Tier 2 / Tier 3 are defined is in `docs/testing-tiers.md`. -->

- **[Jira-ID]** — As a [role], I want [action], so that [benefit]
  - *Test Scenario:* [Tier N] [Description, with an observable pass criterion]
  - *Priority:* [P0/P1/P2, with an optional phase tag as in the parent STP]

---

### **IV. Sign-off and Approval**

<!-- Signed by this SIG's Feature Owner and Quality Owner, plus the feature's Product Manager. -->

This Software Test Plan requires sign-off from at least one person per function:

- Feature Owner: [Name / @github-handle]
- Quality Owner: [Name / @github-handle]
- Product Manager: [Name / @github-handle]
