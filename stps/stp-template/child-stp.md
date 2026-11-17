# Openshift-virtualization-tests Test plan

<!-- STRUCTURE IS FIXED.
This child template defines the section structure and field set for a participating SIG's scope. Fill
each field as it appears; do not add, rename, remove, or reorder sections, checklist items, fields,
or Section III keys. Repeating a line (another entry criterion, risk entry, or scenario) is content.

The only items you may omit are `Document Conventions (if applicable)` and, in a no-risk category,
the supplemental and `Sign-off` lines. Every risk category stays, marked `None — [why]` when this SIG
has no specific risk. A structural change is a separate PR that updates the template it changes and
the other four copies of the rule (AGENTS.md, docs/stp-guide.md, the `.coderabbit.yaml` structure
block, the `.pr_agent.toml` instructions) — see Template Structure Compliance in AGENTS.md.

Comments carry guidance only — never a field, key, or value — and are deleted before submitting.
Replace every placeholder; never delete the field it sits in.

Labels this template retired are listed under "Renamed Template Lines" in docs/stp-guide.md, with the
line that replaced each — a child STP written from an older template is re-shaped onto these lines
when it is next edited. -->

## **[Feature Title — SIG-Specific Scope] - Quality Engineering Plan**

### **Metadata & Tracking**

- **Feature Tracking:** [Link to the relevant feature in Jira]
- **Epic Tracking:** [Link to the SIG-specific tracking Jira Epic, or "Same as parent"]
- **QE Owner(s):** [Name (@github-handle, email)]
- **SIG:** [This SIG — the one this child STP covers]

**Document Conventions (if applicable):**
<!-- One term per line — keep this label and its bullet, and repeat the bullet once per term. Both
lines are the template's own shape, so neither is a new field. -->
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
  <!-- Any SIG-specific requirement that is unclear, ambiguous, or untestable — and why. -->
  - [Unclear or untestable SIG-specific requirement, or "None"]

- [ ] **Non-Functional Requirements (NFRs)**
  <!-- Only list NFRs specific to this SIG's scope. If all NFRs are covered by the parent, state
  that. Repeat the first line once per NFR, and fill the second once — these are content lines, not
  new fields. -->
  - [SIG-specific NFR and its target, or "None — all NFRs are covered by the parent STP"]
  - [SIG-specific NFR not covered and why, or "None"]

#### **2. Feature Limitations**

<!-- List only SIG-specific limitations. Feature-wide limitations belong in the parent STP.
If none, state "None — reviewed and confirmed with [Name/Date]." and keep the `*Sign-off:*` line. -->

- **[SIG-specific limitation]**
  - *Sign-off:* [Name/Date]

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
sign-off — "considered" alone is insufficient. -->

- **[P0]** [SIG-specific testing goal]
- **[P1]** [SIG-specific testing goal]
- **[P2]** [SIG-specific testing goal]

**Out of Scope (Testing Scope Exclusions)**

<!-- List items this SIG explicitly will not test. If something is out of scope for the
entire feature, it belongs in the parent STP — not here. If none, state "None — [why]" and keep the
`*Rationale:*` and `*Sign-off (Quality Owner or Product Manager):*` lines. -->

- **[Item]**
  - *Rationale:* [Why this SIG won't test it]
  - *Sign-off (Quality Owner or Product Manager):* [Name/Date]

**Test Limitations**

<!-- Constraints on this SIG's testing approach. If none, state "None — [why]" and keep the
`*Sign-off:*` line. -->

- **[Test Limitation]**
  - *Sign-off:* [Name/Date]

#### **2. Test Strategy**

<!-- Mark items that this SIG will test. For items covered by the parent STP or other SIGs,
uncheck and state "Covered by parent STP" or "Covered by [SIG name]". -->

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
  - *Details:* [SIG-specific, or "Not applicable for this STP"]

- [ ] **Upgrade Testing**
  - *Details:* [SIG-specific, or "Covered by parent STP"]

- [ ] **Dependencies**
  - *Details:* [SIG-specific blocking dependencies]

- [ ] **Cross Integrations**
  - *Details:* [SIG-specific, or "Covered by parent STP"]

**Infrastructure**

- [ ] **Cloud Testing**
  - *Details:* [SIG-specific, or "Not applicable"]

#### **3. Test Environment**

<!-- Covered in the parent STP; state here only what this SIG adds or overrides. If nothing, write
"None — covered by the parent STP". -->

- [SIG-specific environment requirement, or "None — covered by the parent STP"]

#### **3.1. Testing Tools & Frameworks**

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
A risk is an uncertainty: a constraint that is already true is a Test Limitation, and a testing
decision already taken is Out of Scope; neither belongs here.
A category with no SIG-specific risk keeps its Mitigation line, reads "None — [why]", and drops only
the supplemental and Sign-off lines. When the SIG has no specific risk anywhere, every category says
"None — no SIG-specific risk" and no Sign-off line is needed. -->

**Timeline/Schedule**

- **Risk:** [SIG-specific schedule risk, or "None — [why]"]
  - **Mitigation:** [Mitigation plan, or the one-line no-risk justification]
  - *Estimated impact on schedule:* [Delay or schedule impact]
  - *Sign-off:* [Name/Date]

**Test Coverage**

- **Risk:** [SIG-specific coverage risk, or "None — [why]"]
  - **Mitigation:** [Mitigation plan, or the one-line no-risk justification]
  - *Areas with reduced coverage:* [Affected areas]
  - *Sign-off:* [Name/Date]

**Test Environment**

- **Risk:** [SIG-specific environment risk, or "None — [why]"]
  - **Mitigation:** [Mitigation plan, or the one-line no-risk justification]
  - *Missing resources or infrastructure:* [What is unavailable]
  - *Sign-off:* [Name/Date]

**Untestable Aspects**

- **Risk:** [Untestable aspect for this SIG, or "None — [why]"]
  - **Mitigation:** [Alternative validation, or the one-line no-risk justification]
  - *Alternative validation approach:* [Fallback validation]
  - *Sign-off:* [Name/Date]

**Resource Constraints**

- **Risk:** [SIG-specific resource constraint, or "None — [why]"]
  - **Mitigation:** [Prioritization plan, or the one-line no-risk justification]
  - *Current capacity gaps:* [Staffing or skill gaps]
  - *Sign-off:* [Name/Date]

**Dependencies**

- **Risk:** [SIG-specific dependency, or "None — [why]"]
  - **Mitigation:** [Coordination plan, or the one-line no-risk justification]
  - *Dependent teams or components:* [External dependencies]
  - *Sign-off:* [Name/Date]

**Other**

<!-- A risk that does not fit the six categories above. If none applies, keep this category, write
"None — [why]" in the `Risk` line, keep the `Mitigation` line, and drop the `Sign-off` line. -->

- **Risk:** [Risk not covered above, or "None — [why]"]
  - **Mitigation:** [Plan, or the one-line no-risk justification]
  - *Sign-off:* [Name/Date]

---

### **III. Test Scenarios & Traceability**

<!-- List only this SIG's NEW test scenarios. Each scenario must trace to a Jira requirement.
Every non-regression Testing Goal above has a matching scenario here. Every SIG-specific Acceptance Criterion is
covered by a scenario here, or by named existing regression coverage in Test Strategy (II.2). Regression tests are
documented in Test Strategy (II.2), not in this section. The entry shape is the parent's: the tier is inline in
`Test Scenario`. -->

- **[Jira-ID]** — As a [role], I want [action], so that [benefit]
  - *Test Scenario:* [Tier N] [Description, with an observable pass criterion]
  - *Priority:* [P0/P1/P2, with an optional phase tag as in the parent STP]

---

### **IV. Sign-off and Approval**

This Software Test Plan requires sign-off from at least one person per function:

- Feature Owner: [Name / @github-handle]
- Quality Owner: [Name / @github-handle]
- Product Manager: [Name / @github-handle]
