# Openshift-virtualization-tests Test plan

<!-- TEMPLATE RULES (delete all HTML comments before submitting)

- **Keep the structure fixed:** fill in the existing sections, checklist items, metadata fields, and
  Section III keys as shown. Do not add, rename, reorder, or delete fields.
- **Only two fields may be omitted:** `Document Conventions` (when no terms apply), and a no-risk
  category's category-specific field + `Sign-off` line. Unused `[P0]`/`[P1]`/`[P2]` example goal
  lines may also be dropped.
- **Repeating lines is allowed:** add as many content lines as needed (requirements, use cases,
  acceptance criteria, NFRs, limitations, out-of-scope items, challenges, APIs, topology items,
  goals, entry criteria, risk entries, scenarios, or terms).
- **No empty or bare answers:** replace every placeholder with real content. When a field does not
  apply, write "None" or "N/A" with a brief reason.
- **Editing an existing STP?** Update only the entries you touch to match this template; leave
  untouched legacy entries as they are.
- **Need a new field?** Propose it in a separate template PR that updates the template together with
  the review guidance (`docs/stp-guide.md`, `AGENTS.md`, `.coderabbit.yaml`, `.pr_agent.toml`).
  Otherwise, put extra details as plain prose in an existing field or in the design doc / VEP. -->

## **[Feature Title/Name] - Quality Engineering Plan**

### **Metadata & Tracking**

- **Enhancement(s):** [Links to enhancement(s); KubeVirt, OpenShift, etc.]
- **Feature Tracking:** [Link to the relevant feature in Jira]
- **Epic Tracking:** [Link to the tracking Jira Epic]
  <!-- Tasks must be created to block the feature -->
- **Feature Maturity:**
  <!-- List each maturity phase with its target version. Use N/A for phases that don't apply.
  Standard phases: Dev Preview (DP), Tech Preview (TP), General Availability (GA).
  All three lines stay: a feature already GA with no prior phases writes `DP: N/A` and `TP: N/A`
  rather than dropping the lines.

  Example:
  - DP: N/A
  - TP: 4.22
  - GA: 5.0

  If goals or scenarios must also pass at an intermediate phase, see the optional phase tag under Testing Goals priority levels. -->

  - DP: [version or N/A]
  - TP: [version or N/A]
  - GA: [version]
- **QE Owner(s):** [Name(s)]
- **Owning SIG:** [sig-xyz]
- **Participating SIGs:** [sig-abc, sig-def]
- **Child STPs:** [child STP links, or "None — single-SIG feature"]
  <!-- In multi-SIG features, list all child STPs in the feature directory.
  A single-SIG feature keeps this field and writes "None — single-SIG feature" — do not delete the
  field. Child STPs have no such field in their own template.

  Example:
  - [sig-network](./network.md)
  - [sig-storage](./storage.md)
  - [sig-virt](./virt.md) -->

**Document Conventions**
<!-- Optional: if no feature-specific terms apply, omit both this label and the bullet below.
Otherwise keep the label and repeat the bullet once per term. -->
- **[term]** — [define a term specific to this document]

### **Feature Overview**

<!-- Provide a brief (2-8 sentences) description of the feature being tested.
Include: what it does, why it matters to customers, and the user-visible lifecycle context.
If the feature spans multiple releases (e.g., Tech Preview → GA), describe how the test scope
for this STP relates to those phases; the STP always targets GA. -->

[Brief description of the feature and its purpose]

---

### **I. Motivation and Requirements Review (QE Review Guidelines)**

This section documents the mandatory QE review process. The goal is to understand the feature's value,
technology, and testability before formal test planning.

*This section records the quality interpretation of the feature. Its purpose is to expose misunderstandings
before testing starts, so reviewers should check it against their own understanding of the feature.*

#### **1. Requirement & User Story Review Checklist**

<!-- **How to complete this checklist:**
1. **Checkbox**: Mark [x] when complete; if an item cannot be checked, explain why in the bullet(s) directly under that checklist item.
2. Fill in the details under each item. -->

- [ ] **Review Requirements**
  <!-- List the downstream (D/S) feature requirements from the Feature Tracking Jira issue (not an
  engineering implementation epic). Upstream (U/S) VEPs often have wider scope — include only the
  D/S commitments for this OpenShift Virtualization release.

  Keep requirements at the product level: state the expected behavior and condition without
  duplicating user stories (put those in Use cases) or detailed test steps (put those in Section III).
  - Weak: "Support live migration." — too vague to verify
  - Strong: "Live migration causes minimal network disruption to running VMs."
  - Strong: "A VM keeps running when its guest agent is unavailable and its liveness probe is paused."

  Do not restate the Feature Overview or describe internal implementation.
  Repeat the bullet below once per requirement. -->
  - [Requirement — expected behavior and condition]

- [ ] **Understand Value and Customer Use Cases**
  <!-- Two different things, both required:

  **Value** — the customer cost of *not* having the feature: the workflow that breaks, the SLA that
  cannot be met, the workaround customers pay for today. Not a restatement of the requirement, and
  not a list of product capabilities.
  Example: "Node maintenance forces VMs offline, so customers schedule outages and break their
  availability SLAs."

  **Use cases** — who does what, and to what end, in user-story form:
  "As a [role], I want [action], so that [benefit]".
  - Name a concrete role a customer would recognize (VM owner, cluster admin, SRE running a
    fleet) — never a generic "user".
  - Name the action and the outcome, not the mechanism.
  - Each use case must trace to a Section III scenario, or to named existing regression coverage in
    Test Strategy. If neither covers it, add the scenario or record the gap as a signed-off Out of
    Scope or Test Limitation entry (do not silently drop a valid customer use case).
  Example: "As a cluster admin draining a node during business hours, I want running VMs to keep
  serving traffic, so that planned maintenance does not need a maintenance window." -->
  - *Value:* [The customer cost of not having this feature]
  - *Use cases:*
    - As a [role], I want to [action], so that [benefit]

- [ ] **Testability**
  <!-- Confirm requirements are testable and unambiguous. List any requirement that cannot be tested
  as written and why — or write "None — all requirements are testable and unambiguous".
  Example: "Integration with third-party app X — cannot be validated due to missing test hardware or
  licensing." -->
  - *Unclear or untestable requirements:* [Requirement and why, or "None — all requirements are testable and unambiguous"]

- [ ] **Acceptance Criteria**
  <!-- Verifiable pass/fail conditions that define when the feature is done.
  How sections differ:
  - **Acceptance Criteria (I.1):** product outcomes that prove the feature is done.
  - **Testing Goals (II.1):** prioritized testing objectives (P0/P1/P2) that cover those criteria.
  - **Test Scenarios (III):** concrete individual tests (Tier 1/2/3) that verify each goal.

  - One criterion per bullet, describing observable user outcomes (not internal system behavior).
  - Every value claim above ("non-disruptive", "no downtime", "isolated") needs a criterion that
    would fail if disruption occurred (an end-state check alone is not enough).
  Examples: "VM migrates with network downtime under 500ms", "Non-admin users are blocked from
  deleting VMs."
  Repeat the first bullet per criterion. -->
  - [Acceptance criterion — observable, falsifiable pass/fail condition]
  - *Gaps or missing criteria:* [Gap or missing criterion, or "None — acceptance criteria cover all requirements and value claims"]

- [ ] **Non-Functional Requirements (NFRs)**
  <!-- Every NFR category listed below must be addressed: fill in the measurable target under
  *Applicable NFRs*, or move any category that does not apply / is not covered under
  *Non-applicable or uncovered NFRs* with a brief reason ("N/A" alone is not a reason).
  Examples: "Performance: Host CPU overhead stays under 5% during feature operation",
  "Security: RBAC prevents non-admin users from deleting VMs", "Scalability: Supports 500 VMs". -->
  - *Applicable NFRs:*
    - Monitoring: [Target, or move below with reason]
    - Observability: [Target, or move below with reason]
    - UI: [Target, or move below with reason]
    - Usability: [Target, or move below with reason]
    - Documentation: [Target, or move below with reason]
    - Performance: [Target, or move below with reason]
    - Security: [Target, or move below with reason]
    - Scalability: [Target, or move below with reason]
    - Portability: [Target, or move below with reason]
    - Downtime/Connectivity: [Target, or move below with reason]
  - *Non-applicable or uncovered NFRs:*
    - [NFR category and why it does not apply or is not covered, or "None — all listed NFRs apply and are covered"]

#### **2. Feature Limitations**

The limitations are documented to ensure alignment between development, QA, and product teams.
The following are confirmed product constraints accepted before testing begins.

<!-- **Difference from Risks:** Limitations are *known facts* — confirmed constraints that are accepted before testing begins.
Risks are *uncertainties* — things that might happen and could impact testing.
Example: "Feature does not support IPv6" is a **limitation** (known, confirmed, won't change this release).
"IPv6 cluster might not be available for testing" is a **risk** (uncertain, needs a mitigation plan). -->

<!-- Document limitations in the feature itself — constraints, trade-offs, or unsupported scenarios in the product implementation.

**Examples:**
- The feature only supports YYY storage class
- Feature does not support IPv6 (only IPv4)
- No support for ARM64 architecture in this release
- The feature is incompatible with ZZZ feature

If there are no feature limitations, replace the placeholder item below with
"None — reviewed and confirmed with [Name] that no feature limitations apply for this release." and
keep its `*Sign-off:*` line — only a risk category's supplemental and `Sign-off` lines may be
dropped. Repeat the two-line entry once per limitation. -->

- **[Feature Limitation]**
  - *Sign-off:* [Name — confirms awareness and acceptance of this limitation]

#### **3. Technology and Design Review**

<!-- **How to complete this checklist:**
1. **Checkbox**: Mark [x] if done
2. Complete the relevant, needed details for the checklist item -->

- [ ] **Developer Handoff/QE Kickoff**
  <!-- A meeting where Dev/Arch walked QE through the design, architecture, and implementation details. **Critical for identifying untestable aspects early.**
  Summarize the actual takeaways and concerns raised — not "meeting held". -->
  - *Key takeaways and concerns:* [What was learned, and what worries QE]

- [ ] **Technology Challenges**
  <!-- Identify the potential testing challenges related to the underlying technology, and their
  impact on how the feature will be tested. Repeat the first bullet per challenge, and the impact
  bullet per challenge if the impacts differ. -->
  - [Testing challenge]
  - *Impact on testing approach:* [How the challenge changes the test approach]

- [ ] **API Extensions**
  <!-- Review new or modified user-facing APIs and their impact on testing. Covers both new tests
  for new APIs and updates to existing tests for modified APIs. No internal component APIs.
  Example: "New VirtualMachineSnapshot API v1beta2 — 3 new endpoints, 1 modified endpoint.
  Existing snapshot tests need updating."
  Repeat the first bullet per API, and the testing-impact bullet per API. -->
  - [New or modified user-facing API]
  - *Testing impact:* [How the API change affects existing and new tests]

- [ ] **Test Environment Needs**
  <!-- Identified whether special environment setups are needed beyond standard infrastructure.-->
  - *See environment requirements in Section II.3 and testing tools in Section II.3.1*

- [ ] **Topology Considerations**
  <!-- Cluster and network topology only — not internal resource creation.
  State the cluster requirements and their impact on test design.
  Evaluated multi-cluster, network topology, and architectural impacts.
  Repeat the first bullet per topology item, and the impact bullet per item. -->
  - [Cluster and network topology required]
  - *Impact on test design:* [How the topology shapes the test design]

### **II. Software Test Plan (STP)**

This STP serves as the **overall roadmap for testing**, detailing the scope, approach, resources, and schedule.

#### **1. Scope of Testing**

<!-- Briefly describe what will be tested. The scope must **cover functional and non-functional requirements**.
Must ensure user stories are included and aligned to downstream user stories from Section I. -->

**Testing Goals**

<!-- Testing goals are specific, measurable objectives — they say *what* must be verified and *how* success is measured.

Define specific, measurable testing objectives for this feature using **SMART criteria**
(Specific, Measurable, Achievable, Relevant, Time-bound).
Each goal should tie back to requirements from Section I and be independently verifiable.

**How to Define Good Testing Goals:**
- **Specific**: Clearly state what will be tested (not "test the feature" but "validate VM live migration
  with SR-IOV networks")
- **Measurable**: Define quantifiable success criteria (e.g., "95% of VM migrations complete within xxx seconds")
- **Achievable**: Realistic given resources and timeline
- **Relevant**: Directly supports feature acceptance criteria and user stories
- **Verifiable**: Can be objectively confirmed as complete

**Priority Levels:**
- **P0**: Blocks GA - must be complete before release
- **P1**: High priority - required for full feature coverage
- **P2**: Nice-to-have - can be deferred if timeline constraints exist

**Phase tag (optional):** Priorities refer to GA. If a goal or scenario must also pass at an intermediate phase
(e.g. Tech Preview), add a phase tag: `**[P0][TP]**` for a goal, `- *Priority:* P0 [TP]` for a scenario. Use the
phase names from Feature Maturity (from the parent STP for a child STP).

**How to write Testing Goals** (higher-level objectives than Section III test scenarios; prioritized
coverage of Section I.1 Acceptance Criteria):
- List one goal per bullet, ordered **P0 first, then P1, then P2**. Omit priority levels that do not apply.
- Pair each **P0 functional goal** with a **negative/failure-path goal** (and matching Section III
  scenario) — e.g. operation fails, VM starts mid-operation, or invalid input.
- If a P0 negative path is not tested, record it in **Out of Scope** with Quality Owner or Product
  Manager sign-off — unless it is also an Acceptance Criterion, in which case Section III (or named
  existing regression coverage in Test Strategy) must cover it. -->

<!-- **Examples (flat list, P0 first — do not add category subheadings):**
- **[P0]** VM live migration is supported with the new network binding plugin on OVN-Kubernetes and secondary networks
- **[P0]** Live migration with an invalid network binding configuration fails cleanly without disrupting the running VM
- **[P0]** RBAC restricts non-admin users from accessing cluster-wide feature configuration
- **[P0]** Live migration meets the performance baseline (<30s for <8GB VMs) with zero data loss under 100ms latency
- **[P0]** Cluster upgrade preserves existing VM feature configurations without manual intervention
- **[P1]** Hotplug/hotunplug works with the new storage class without VM restart
- **[P1]** Feature operates in disconnected/air-gapped environments using a local image registry
- **[P1]** Prometheus metrics and Alertmanager alerts report feature health and failures
- **[P2]** Real-time VM resource metrics are exposed during feature operation -->

- **[P0]** [Functional goal — what is verified and how success is measured; add a phase tag such as `[P0][TP]` only if needed]
- **[P0]** [Negative / failure-path goal for the P0 functional goal above — expected error or recovery behaviour]
- **[P1]** [High-priority functional, non-functional, or integration goal — what is verified and how success is measured]
- **[P2]** [Nice-to-have goal — what is verified and how success is measured]

**Out of Scope (Testing Scope Exclusions)**

The following items are explicitly Out of Scope for this test cycle and represent intentional exclusions.
No verification activities will be performed for these items, and any related issues found will not be classified as defects for this release.

<!-- **What does Out of Scope mean?**
Out of Scope items are areas where the product works, but QE has decided not to test them this cycle.
This is the most critical section in the STP — it explicitly documents the gap between what the product can do and what QE will verify.
Every item here is a conscious decision accepted by the Quality Owner or Product Manager. If an untested area breaks in production, this section proves the decision was deliberate and agreed upon.
Each item requires Quality Owner or Product Manager sign-off.

**Difference from Risks:** A risk is something that *might* prevent testing — you plan to test it but it could be blocked and you provide a mitigation plan.
Out of Scope means you have *decided not to test it* — the decision is final and accepted by stakeholders.
Example: "MultiArch cluster might not be available" is a **risk**. "We will not test on bare-metal MultiArch clusters" is **out of scope**.

**Difference from existing coverage:** Areas already covered by existing regression suites or other teams are
not Out of Scope; record them under Regression Testing in Test Strategy (II.2).

**Examples:**
- **Interface settings independent of the new network binding (e.g., NIC model)** — Rationale: feature
  is agnostic to vNIC emulation towards the guest, so no feature-specific test is planned.
- **Special guest OS coverage (e.g., Windows)** — Rationale: feature is expected to work with Windows
  guests, but validation uses Fedora-based guests this cycle.

**Note:** Repeat the three-line entry below once per out-of-scope item. If there are none, replace the
placeholder item with "None — reviewed and confirmed that all supported product functionality will
be tested this cycle." and keep its `*Rationale:*` and `*Sign-off (Quality Owner or Product Manager):*` lines. -->

- **[Out-of-scope item]**
  - *Rationale:* [Why QE decided not to test this item this cycle]
  - *Sign-off (Quality Owner or Product Manager):* [Name]

**Test Limitations**

<!-- Document limitations in the test approach — things that constrain how or what we can test, not the feature itself.
These are distinct from feature limitations (Section I.2) which describe product constraints.

**Difference from Out of Scope:** Test Limitations are constraints *imposed on QE* (e.g., no hardware, no cluster, no environment).
Out of Scope are *decisions made by QE* (e.g., we choose not to test Windows guests).
Example: "No bare-metal MultiArch cluster available" is a **test limitation** (QE can't test it even if they wanted to).
"Windows guest OS will not be tested" is **out of scope** (QE chose not to test it).

**Examples:**
- CPU xxx will not be tested due to lack of hardware
- Real integration with [Third-Party Service] cannot be tested; external calls will be mocked using static data due to access/licensing constraints
- Performance testing limited to 100 VMs due to lab capacity
- IPv6 testing constrained to single-stack due to dual-stack cluster unavailability

Repeat the two-line entry below once per limitation. If there are no test limitations, replace the
placeholder item with "None — reviewed and confirmed that no test limitations apply for this release."
and keep its `*Sign-off:*` line. -->

- **[Test Limitation]**
  - *Sign-off:* [Name — confirms awareness and acceptance of this limitation]

#### **2. Test Strategy**

<!-- The following test strategy considerations must be reviewed and addressed. Mark [x] if applicable,
leave unchecked if not applicable (with justification in Details). Unchecked items without details
indicate incomplete review.

Note: Strategy defines *which types of testing* apply and the high-level approach. Goals (Section II.1) define the specific, measurable objectives.
Example: Strategy says "Performance testing is applicable — we will measure migration stuntime." Goals say "[P0] Verify VM stuntime during live migration is below 500ms." -->

**Functional**

- [ ] **Functional Testing** — Validates that the feature works according to specified requirements and user stories
  <!-- Mark if this feature requires functional testing. Functional testing validates that the feature works as specified — as opposed to non-functional testing (performance, security, scale, etc.) which validates how well it works. -->
  - *Details:* [ Add details ]

- [ ] **Automation Testing** — Confirms test automation plan is in place for CI and regression coverage (all tests are expected to be automated)
  <!-- Example: "All Tier 2 tests automated by sprint 3, integrated into nightly CI lane." -->
  - *Details:* [ Add details ]

- [ ] **Regression Testing** — Verifies that new changes do not break existing functionality
  - *Details:* [ Add details ]

- [ ] **Self-Validation Testing** — Should any of the new tests be included in the self-validation test package?
  <!-- The self-validation package is a curated subset of tests that run as product health checks.
  Consider whether any new test scenarios validate core feature functionality that should
  be part of self-validation. Self-validation tests should be fast, reliable, and cover
  critical operational scenarios. -->
  - *Details:* [ Add details ]

**Non-Functional**

- [ ] **Performance Testing** — Validates feature performance meets requirements (latency, throughput, resource usage)
  - *Details:* [ Add details ]

- [ ] **Scale Testing** — Validates feature behavior under increased load and at production-like scale (e.g., large number of VMs, nodes, or concurrent operations)
  - *Details:* [ Add details ]

- [ ] **Security Testing** — Verifies security requirements, RBAC, authentication, authorization, and vulnerability scanning
  - *Details:* [ Add details ]

- [ ] **Usability Testing** — Validates user experience and accessibility requirements
  <!-- Consider, and answer in Details:
  - Does the feature require a UI? If so, does it align with the requirements (UI/UX consistency,
    accessibility)?
  - Does the feature expose CLI commands? If so, validate usability, and that needed information is
    available (e.g., status conditions, clear output).
  - Does the feature trigger backend operations that should be reported to the admin? If so,
    validate that the user receives clear feedback about the operation and its outcome (e.g.,
    status conditions, events, or notifications indicating success or failure). -->
  - *Details:* [ Add details ]

- [ ] **Monitoring** — Does the feature require metrics and/or alerts?
  - *Details:* [ Add details ]

**Integration & Compatibility**

- [ ] **Compatibility Testing** — Ensures feature works across supported platforms, versions, and configurations
  <!-- Does the feature maintain backward compatibility with previous API versions and configurations? -->
  - *Details:* [ Add details ]

- [ ] **Upgrade Testing** — Validates upgrade paths from previous versions, data migration, and configuration preservation
  - *Details:* [ Add details ]

- [ ] **Dependencies** — Blocked by deliverables from other components/products. Identify what we need from other teams before we can test.
  <!-- Example: "Blocked on Storage team delivering CSI driver v2.0 — cannot test snapshot feature without it." -->
  - *Details:* [ Add details ]

- [ ] **Cross Integrations** — Does the feature affect other features or require testing by other teams? Identify the impact we cause.
  <!-- Example: "Our API change affects the UI team's VM details page — they need to update their tests." -->
  - *Details:* [ Add details ]

**Infrastructure**

- [ ] **Cloud Testing** — Does the feature require multi-cloud platform testing? Consider cloud-specific features.
  - *Details:* [ Add details ]

#### **3. Test Environment**

<!-- **Note:** "N/A" means explicitly not applicable. All items must be filled or marked N/A.
Keep every field below — none may be added, removed, or renamed. Replace each value with the actual
value for this feature, or write the value followed by how it differs from the default shown.
A field that truly does not apply keeps its line and reads `N/A` plus the reason. -->

- **Cluster Topology:** 3-master/3-worker bare-metal
  <!-- Change if different, e.g., SNO, Compact Cluster, HCP -->

- **OCP & OpenShift Virtualization Version(s):** [e.g., OCP 4.20 with OpenShift Virtualization 4.20]
  <!-- Specify exact versions to allow version traceability -->

- **CPU Virtualization:** VT-x (Intel) or AMD-V enabled
  <!-- Change only if specific CPU requirements exist -->

- **Compute Resources:** Minimum per worker node: 8 vCPUs, 32GB RAM
  <!-- Adjust based on feature requirements -->

- **Special Hardware:** [Special hardware required, e.g., SR-IOV NICs, GPUs, or "N/A — standard hardware only"]

- **Storage:** ocs-storagecluster-ceph-rbd-virtualization
  <!-- Change if specific StorageClass(es) required -->

- **Network:** OVN-Kubernetes, IPv4
  <!-- Change if needed, e.g., Secondary Networks, IPv6, dual-stack -->

- **Required Operators:** [Additional operators required, e.g., NMState Operator, or "N/A — standard OpenShift Virtualization operators only"]

- **Platform:** Bare metal
  <!-- Change if needed, e.g., AWS, Azure, GCP -->

- **Special Configurations:** [Special cluster configs, e.g., Disconnected/air-gapped, Proxy, FIPS mode, or "N/A — standard connected cluster"]

#### **3.1. Testing Tools & Frameworks**

<!-- Document any **new or additional** testing tools, frameworks, or infrastructure required specifically
for this feature. **Note:** Only list tools that are **new** or **different** from standard testing infrastructure.

Keep every field below — none may be added, removed, or renamed. Keep `Standard` for `Test Framework`
when no custom framework is needed; for `CI/CD` and `Other Tools`, replace the placeholder with the
required lane/tool or `N/A` plus the reason. -->

- **Test Framework:** Standard
  <!-- Change if needed, e.g., new framework, custom test harness, significant changes in tests infrastructure code etc -->

- **CI/CD:** [Special test lane or custom pipeline config, or "N/A — standard CI lanes cover this feature"]

- **Other Tools:** [Additional monitoring/performance tools, or "N/A — no extra tooling needed"]

#### **4. Entry Criteria**

The following conditions must be met before testing can begin:

<!-- Add feature-specific entry criteria as needed, and mark each item [x] when it holds. At STP
approval time, unchecked environment criteria are expected — but a checked item must not contradict
a listed dependency or test limitation. When no feature-specific criterion applies, write "None —
the two criteria above cover this feature" in the third line and mark it [x]: the box records that
the question was answered, and "None" is a complete answer. -->

- [ ] Requirements and design documents are **approved and merged**
- [ ] Test environment can be **set up and configured** (see Section II.3 - Test Environment)
- [ ] [Feature-specific entry criterion, or "None — the two criteria above cover this feature"]

#### **5. Risks**

<!-- Document specific risks for this feature. A risk is an uncertainty — something that might
prevent planned testing. A constraint that is already true is a Test Limitation, and a testing
decision already taken is Out of Scope; neither belongs here. A risk category with no risk keeps its
Mitigation line plus a one-line justification (not just "N/A") — no Sign-off or supplemental field
is needed. A category with a real risk needs the full entry, including Sign-off (name). Repeat
the entry for each risk inside a category.

No-risk form (drop the category-specific field and `Sign-off` line):
- **Risk:** None — [why no risk applies]
  - **Mitigation:** Not applicable — [same reason] -->

**Timeline/Schedule**

<!-- The specific scheduling or deadline risk that might delay testing, and how scope, priorities,
resources, or the timeline will be adjusted in response. -->

- **Risk:** [Scheduling or deadline risk]
  - **Mitigation:** [How scope, priorities, or resources adjust to meet the timeline]
  - *Estimated impact on schedule:* [Delay or schedule impact]
  - *Sign-off:* [Name — confirms awareness and acceptance of this risk]

**Test Coverage**

<!-- Coverage that may go unverified if something blocks it, and the alternative strategy or the
reduction that would be accepted. Confirmed gaps are Test Limitations; agreed exclusions are Out of
Scope. -->

- **Risk:** [Coverage gap and which areas remain unverified]
  - **Mitigation:** [Alternative testing strategy, or the accepted reduced coverage]
  - *Areas with reduced coverage:* [Affected areas]
  - *Sign-off:* [Name — confirms awareness and acceptance of this risk]

**Test Environment**

<!-- Hardware, software, or infrastructure that may limit testing, and how the required resources
will be secured or the plan adapted. A resource already confirmed unavailable is a Test
Limitation. -->

- **Risk:** [Environment resource or infrastructure that might be unavailable during testing]
  - **Mitigation:** [How the required resources are secured, or how the plan adapts]
  - *Missing resources or infrastructure:* [What is unavailable]
  - *Sign-off:* [Name — confirms awareness and acceptance of this risk]

**Untestable Aspects**

<!-- Scenarios or conditions that may not be reproducible in a test environment, and the alternative
validation method (smaller-scale test, unit test, production monitoring). An aspect already
confirmed untestable is a Test Limitation. -->

- **Risk:** [Scenario or condition that may not be reproducible in a test environment]
  - **Mitigation:** [Alternative validation method]
  - *Alternative validation approach:* [The fallback validation method]
  - *Sign-off:* [Name — confirms awareness and acceptance of this risk]

**Resource Constraints**

<!-- Staffing, skill, or capacity that may limit test execution, and how work will be prioritized,
cross-trained, or coordinated. A shortfall already confirmed is a Test Limitation. -->

- **Risk:** [Staffing, skill, or capacity shortfall that could affect test execution]
  - **Mitigation:** [How work is prioritized, cross-trained, or coordinated]
  - *Current capacity gaps:* [Staffing or skill gaps]
  - *Sign-off:* [Name — confirms awareness and acceptance of this risk]

**Dependencies**

<!-- External team or component dependencies that could block testing, and the coordination plan,
fallback strategy, or stub implementation. -->

- **Risk:** [External team or component dependency that could block testing]
  - **Mitigation:** [Coordination plan, fallback strategy, or stub implementation]
  - *Dependent teams or components:* [External dependencies]
  - *Sign-off:* [Name — confirms awareness and acceptance of this risk]

**Other**

<!-- Only for risks that do not fit the six categories above. If none apply, keep this category,
write `None — [why]` in the `Risk` line, write `Not applicable — [same reason]` in the `Mitigation`
line, and drop the `Sign-off` line — do not delete the category. Add any context the entry needs. -->

- **Risk:** [Risk not covered above — or write: None — <reason>]
  - **Mitigation:** [Specific plan to reduce or eliminate this risk, or "Not applicable — <same reason>"]
  - *Sign-off:* [Name — confirms awareness and acceptance of this risk]

---

### **III. Test Scenarios & Traceability**

<!-- This section links D/S requirements to test coverage, enabling reviewers to verify all
requirements are tested.

**What goes here:** New test scenarios specific to this feature. Each scenario traces to a D/S Jira
requirement. **Granularity:** if one scenario can fail while another passes, they are separate
entries (e.g., VMs with feature X vs without, alerts with different trigger conditions; for a DP/TP
Feature Gate, focus on the gate enabled — only add a disabled-gate scenario for explicit safety
cases such as disabling the gate while workloads are running). **What does NOT go here:** regression
tests (covered in Test Strategy).

The entry shape is fixed — the Jira key in bold, the requirement as a user story with a concrete
role and a benefit, then exactly two keys: `Test Scenario` (tier inline as `[Tier N]`) and
`Priority`. The role must be one a customer would recognize (VM owner, cluster admin, SRE running a
fleet — never a generic "user") and the benefit must state the outcome, matching the use-case rules
in Section I.1. The same inline tier is used in a child STP. Tier definitions are in
`docs/testing-tiers.md` — Tier 1 is a functional test on a cluster, Tier 2 an end-to-end workflow
test, Tier 3 an extended validation test; use it rather than guessing a tier.

Every non-regression Testing Goal (II.1) has a matching scenario here; a regression goal refers to
its coverage in Test Strategy (II.2). Every Acceptance Criterion (I.1) is covered by a scenario here,
or by named existing regression coverage in Test Strategy (II.2).

Copy the entry below once per scenario. The bracketed text is replaced — except the labels that keep
their brackets: `[Jira-ID]` takes the real key, `[Tier N]` the tier number. `[role]`, `[action]`,
`[benefit]`, `[P0/P1/P2]` and the scenario text are replaced without brackets.

- **[Jira-123]** — As a cluster admin, I want to create a VM with feature X, so that VM workloads start without a separate configuration step
  - *Test Scenario:* [Tier 1] Verify VM can be created with new feature X
  - *Priority:* P0
- **[Jira-124]** — As a VM owner, I want the feature X API to reject invalid input, so that a bad request fails fast instead of corrupting a VM
  - *Test Scenario:* [Tier 1] Verify API for feature X rejects invalid field values
  - *Priority:* P0
- **[Jira-125]** — As a cluster admin, I want non-admin users blocked from deleting VMs, so that a single tenant cannot remove another tenant's workload
  - *Test Scenario:* [Tier 2] Verify non-admin user cannot delete a VM
  - *Priority:* P1
- **[Jira-126]** — As a cluster admin, I want an upgrade to preserve feature X state, so that maintenance does not require reconfiguring running VMs
  - *Test Scenario:* [Tier 2] Verify upgrade from version X to Y preserves feature state
  - *Priority:* P2
- **[Jira-127]** — As a Windows VM owner, I want feature X to work on NTFS guests, so that existing Windows workloads can adopt the feature
  - *Test Scenario:* [Tier 3] Verify feature X works on Windows guest with NTFS filesystem
  - *Priority:* P1 -->

- **[Jira-ID]** — As a [role], I want [action], so that [benefit]
  - *Test Scenario:* [Tier N] [scenario, with an observable pass criterion]
  - *Priority:* [P0/P1/P2]

---

### **IV. Sign-off and Approval**

This Software Test Plan requires sign-off from at least one person per function:

- Feature Owner: [Name / @github-handle]
- Quality Owner: [Name / @github-handle]
- Product Manager: [Name / @github-handle]
