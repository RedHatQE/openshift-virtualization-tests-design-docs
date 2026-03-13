# Openshift-virtualization-tests Test plan

## **[Feature Title/Name] - Quality Engineering Plan**

### **Metadata & Tracking**

- **Enhancement(s):** [Links to enhancement(s); KubeVirt, OpenShift, etc.]
- **Feature Tracking:** [Link to the relevant feature in Jira]
- **Epic Tracking:** [Link to the tracking Jira Epic]
  <!-- Tasks must be created to block the feature -->
- **QE Owner(s):** [Name(s)]
- **Owning SIG:** [sig-xyz]
- **Participating SIGs:** [List of participating SIGs]

**Document Conventions (if applicable):** [Define acronyms or terms specific to this document]

### **Feature Overview**

<!-- Provide a brief (2-4 sentences) description of the feature being tested.
Include: what it does, why it matters to customers, and key technical components. -->

[Brief description of the feature and its purpose]

---

### **I. Motivation and Requirements Review (QE Review Guidelines)**

This section documents the mandatory QE review process. The goal is to understand the feature's value,
technology, and testability before formal test planning.

#### **1. Requirement & User Story Review Checklist**

<!-- **How to complete this checklist:**
1. **Checkbox**: Mark [x] if the check is complete; if the item cannot be checked - add an explanation why in the `details` section
2. Complete the relevant, needed details for the checklist item -->

- [ ] **Review Requirements**
  <!-- Review the D/S (Downstream) requirements as defined in Jira. Understand the difference between Upstream (U/S) and D/S requirements.
  Example: "VMs must migrate without network downtime exceeding the defined threshold during node maintenance." -->
  - *List the key D/S requirements reviewed:* [Summarize requirements here]

- [ ] **Understand Value and Customer Use Cases**
  <!-- Understand why the feature matters to customers from a D/S perspective and what the real-world use cases are.
  Example: "Customers need to migrate VMs without network downtime to maintain SLA compliance during node maintenance." -->
  - *Describe the feature's value to customers:* [Describe the customer value here]
  - *List the customer use cases identified:* [List use cases here]

- [ ] **Testability**
  <!-- Confirmed requirements are **testable and unambiguous**. -->
  - *Note any requirements that are unclear or untestable:* [List unclear or untestable requirements, or "None"]

- [ ] **Acceptance Criteria**
  <!-- Acceptance criteria are the specific, verifiable conditions that must be met for the feature to be considered complete — they define *how we know it works*.
  Example: "VM migrates without network downtime exceeding 500ms", "VM deletion is blocked for non-admin users." -->
  - *List the acceptance criteria:* [Add acceptance criteria here]
  - *Note any gaps or missing criteria:* [Describe gaps, or "None"]

- [ ] **Non-Functional Requirements (NFRs)**
  <!-- Confirmed coverage for NFRs, including Performance, Security, Usability, Downtime, Connectivity, Monitoring (alerts/metrics), Scalability, Portability (e.g., cloud support), and Docs.-->
  - *List applicable NFRs and their targets:* [e.g., Resource Efficiency: < 5% CPU overhead on host during feature operation, Security: RBAC enforced, Scalability: supports 500 VMs]
  - *Note any NFRs not covered and why:* [e.g., "Scalability — no test environment with 500+ VMs available", or "None"]

#### **2. Known Limitations**

The limitations are documented to ensure alignment between development, QA, and product teams.
The following topics will not be tested or supported.

<!-- Document any known limitations, constraints, or trade-offs in the feature implementation or testing approach.

**Examples:**
Feature related:
- The feature is only supports YYY storage class
- Feature does not support IPv6 (only IPv4)
- No support for ARM64 architecture in this release
- The feature is incompatible with ZZZ feature

Tests related:
- CPU xxx will not be tested due to lack of hardware
- Integration with [Third-Party Service] is excluded; all external calls will be mocked using static data-->

- [Limitation 1]
- [Limitation 2]

#### **3. Technology and Design Review**

<!-- **How to complete this checklist:**
1. **Checkbox**: Mark [x] if done
2. Complete the relevant, needed details for the checklist item -->

- [ ] **Developer Handoff/QE Kickoff**
  <!-- A meeting where Dev/Arch walked QE through the design, architecture, and implementation details. **Critical for identifying untestable aspects early.**-->
  - *Key takeaways and concerns:* [Summarize key points and concerns]

- [ ] **Technology Challenges**
  <!-- Identified potential testing challenges related to the underlying technology.-->
  - *List identified challenges:* [Describe challenges here]
  - *Impact on testing approach:* [Describe impact on testing]

- [ ] **API Extensions**
  <!-- Review new or modified APIs and their impact on testing. Covers both new tests for new APIs and updates to existing tests for modified APIs.
  Example: "New VirtualMachineSnapshot API v1beta2 — 3 new endpoints, 1 modified endpoint. Existing snapshot tests need updating." -->
  - *List new or modified APIs:* [Add APIs here]
  - *Testing impact:* [Describe testing impact]

- [ ] **Test Environment Needs**
  <!-- Identified whether special environment setups are needed beyond standard infrastructure.-->
  - *See environment requirements in Section II.3 and testing tools in Section II.3.1*

- [ ] **Topology Considerations**
  <!-- Evaluated multi-cluster, network topology, and architectural impacts.-->
  - *Describe topology requirements:* [Add topology requirements here]
  - *Impact on test design:* [Describe impact on test design]

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
- **P0**: Blocking GA - must be complete before release
- **P1**: High priority - required for full feature coverage
- **P2**: Nice-to-have - can be deferred if timeline constraints exist -->

<!-- **Example - Functional Goals**:
- **[P0]** Verify VM live migration completes successfully with new network binding plugin across
  OVN-Kubernetes and secondary networks
- **[P1]** Validate hotplug/hotunplug operations work with new storage class without VM restart
- **[P0]** Confirm RBAC permissions model correctly restricts non-admin users from accessing
  cluster-wide configuration API
- **[P2]** Validate new metrics with real-time VM performance data (CPU, memory, network, disk I/O)

**Example - Quality Goals**:
- **[P0]** Verify VM live migration completes in <30 seconds for VMs with <8GB memory
  (performance baseline from VEP-XXXX)
- **[P1]** Confirm feature operates correctly in disconnected/air-gapped environments with local
  image registry
- **[P0]** Validate zero data loss during live migration under network latency up to 100ms

**Example - Integration Goals**:
- **[P0]** Verify backward compatibility: upgrade from OCP 4.19 to 4.20 preserves existing VM
  configurations without manual intervention
- **[P0]** Confirm interoperability with OpenShift Service Mesh when VMs use Istio sidecar injection
- **[P1]** Test integration with OpenShift monitoring stack: metrics appear in Prometheus,
  alerts fire correctly in Alertmanager -->

- **[P0]** [List key functional areas to be tested with priority]
- **[P1]** [List non-functional requirements to be tested with priority]
- **[P2]** [Reference specific user stories from Section I with priority]

**Out of Scope (Testing Scope Exclusions)**

The following items are explicitly Out of Scope for this test cycle and represent intentional exclusions.
No verification activities will be performed for these items, and any related issues found will not be classified as defects for this release.

<!-- Explicitly document what is **out of scope** for testing.
This section define the test boundaries; for example: test coverage by other teams, edge cases, low priority, etc.
**Critical:** All out-of-scope items require explicit stakeholder agreement to prevent "I assumed you were testing
that" issues; each out-of-scope item must have PM/Lead sign-off.

- Items without stakeholder agreement are considered **risks** and must be escalated
- Review the items during Developer Handoff/QE Kickoff meeting

**Note:** Replace examples with your actual out-of-scope items. If there are no items; delete the checklist and add `None`-->

- [ ] **[e.g., Testing of deprecated features]**
  - *Rationale:* [Why this is excluded]
  - *PM/Lead Agreement:* [Name/Date]

- [ ] **[e.g., Performance testing]**
  - *Rationale:* [Why this is excluded]
  - *PM/Lead Agreement:* [Name/Date]

- [ ] **[e.g., Testing on XXX architecture]**
  - *Rationale:* [Why this is excluded]
  - *PM/Lead Agreement:* [Name/Date]

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

**Non-Functional**

- [ ] **Performance Testing** — Validates feature performance meets requirements (latency, throughput, resource usage)
  - *Details:* [ Add details ]

- [ ] **Scale Testing** — Validates feature behavior under increased load and at production-like scale (e.g., large number of VMs, nodes, or concurrent operations)
  - *Details:* [ Add details ]

- [ ] **Security Testing** — Verifies security requirements, RBAC, authentication, authorization, and vulnerability scanning
  - *Details:* [ Add details ]

- [ ] **Usability Testing** — Validates user experience and accessibility requirements
  - Does the feature require a UI? If so, ensure the UI aligns with the requirements (UI/UX consistency, accessibility)
  - Does the feature expose CLI commands? If so, validate usability and that needed information is available (e.g., status conditions, clear output)
  - Does the feature trigger backend operations that should be reported to the admin? If so, validate that the user receives clear feedback about the operation and its outcome (e.g., status conditions, events, or notifications indicating success or failure)
  - *Details:* [ Add details ]

- [ ] **Monitoring** — Does the feature require metrics and/or alerts?
  - *Details:* [ Add details ]

**Integration & Compatibility**

- [ ] **Compatibility Testing** — Ensures feature works across supported platforms, versions, and configurations
  - Does the feature maintain backward compatibility with previous API versions and configurations?
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

<!-- **Note:** "N/A" means explicitly not applicable. All items must be filled or marked N/A. -->

- **Cluster Topology:** 3-master/3-worker bare-metal
  <!-- Change if different, e.g., SNO, Compact Cluster, HCP -->

- **OCP & OpenShift Virtualization Version(s):** [e.g., OCP 4.20 with OpenShift Virtualization 4.20]
  <!-- Specify exact versions to allow version traceability -->

- **CPU Virtualization:** VT-x (Intel) or AMD-V enabled
  <!-- Change only if specific CPU requirements exist -->

- **Compute Resources:** Minimum per worker node: 8 vCPUs, 32GB RAM
  <!-- Adjust based on feature requirements -->

- **Special Hardware:** N/A
  <!-- Fill if needed, e.g., SR-IOV NICs, GPUs -->

- **Storage:** ocs-storagecluster-ceph-rbd-virtualization
  <!-- Change if specific StorageClass(es) required -->

- **Network:** OVN-Kubernetes, IPv4
  <!-- Change if needed, e.g., Secondary Networks, IPv6, dual-stack -->

- **Required Operators:** N/A
  <!-- Add if needed, e.g., NMState Operator -->

- **Platform:** Bare metal
  <!-- Change if needed, e.g., AWS, Azure, GCP -->

- **Special Configurations:** N/A
  <!-- Change if needed, e.g., Disconnected/air-gapped, Proxy, FIPS mode -->

#### **3.1. Testing Tools & Frameworks**

<!-- Document any **new or additional** testing tools, frameworks, or infrastructure required specifically
for this feature. **Note:** Only list tools that are **new** or **different** from standard testing infrastructure. -->

- **Test Framework:** Standard
  <!-- Change if needed, e.g., new framework, custom test harness, significant changes in tests infrastructure code etc  -->

- **CI/CD:** N/A
  <!-- Change if needed, e.g., special test lane, custom pipeline config -->

- **Other Tools:** N/A
  <!-- Fill if needed, e.g., special monitoring, performance tools -->

#### **4. Entry Criteria**

The following conditions must be met before testing can begin:

- [ ] Requirements and design documents are **approved and merged**
- [ ] Test environment can be **set up and configured** (see Section II.3 - Test Environment)
- [ ] [Add feature-specific entry criteria as needed]

#### **5. Risks**

<!-- Document specific risks for this feature. If a risk category is not applicable, mark as "N/A" with
justification in mitigation strategy. -->

**Timeline/Schedule**

- [ ] **Risk:** [Describe the specific scheduling or deadline risk that could delay testing]
  - **Mitigation:** [Propose how to adjust scope, priorities, or resources to meet the timeline]
  - *Estimated impact on schedule:* [Add estimated delay or schedule impact]

**Test Coverage**

- [ ] **Risk:** [Describe gaps in test coverage and which areas remain unverified]
  - **Mitigation:** [Propose alternative testing strategies or acceptance of reduced coverage]
  - *Areas with reduced coverage:* [List affected areas]

**Test Environment**

- [ ] **Risk:** [Describe hardware, software, or infrastructure constraints that limit testing]
  - **Mitigation:** [Propose how to secure required resources or adapt the test plan]
  - *Missing resources or infrastructure:* [List what is unavailable]

**Untestable Aspects**

- [ ] **Risk:** [Describe scenarios or conditions that cannot be reproduced in a test environment]
  - **Mitigation:** [Propose alternative validation methods such as smaller-scale tests or production monitoring]
  - *Alternative validation approach:* [Describe fallback validation method]

**Resource Constraints**

- [ ] **Risk:** [Describe staffing, skill, or capacity limitations affecting test execution]
  - **Mitigation:** [Propose how to prioritize work, cross-train, or coordinate with other teams]
  - *Current capacity gaps:* [Describe staffing or skill gaps]

**Dependencies**

- [ ] **Risk:** [Describe external team or component dependencies that could block testing]
  - **Mitigation:** [Propose coordination plans, fallback strategies, or stub implementations]
  - *Dependent teams or components:* [List external dependencies]

**Other**

- [ ] **Risk:** [Describe any additional risks not covered by the categories above]
  - **Mitigation:** [Propose a specific plan to reduce or eliminate this risk]
  <!-- If more context is needed for this item, add an entry with any relevant details-->

---

### **III. Test Scenarios & Traceability**

<!-- This section links D/S requirements to test coverage, enabling reviewers to verify all requirements are tested.

**What goes here:** New test scenarios specific to this feature. Each scenario should trace to a D/S Jira requirement.
**Granularity:** If one scenario can fail while another passes, they should be separate items. For example:
- Different conditions (VMs with feature X vs without) → separate scenarios
- Feature Gate enable/disable → separate scenarios (different expected behavior)
- Multiple alerts → separate if different trigger conditions, group if same flow
**What does NOT go here:** Regression tests (covered in Test Strategy). -->

<!-- **Requirement ID:**
- Use Jira issue key (e.g., CNV-12345)

**Requirement Summary:** Brief description from the Jira issue (user story format preferred) -->

- **[Jira-123]** — As a user...
  - *Test Scenario:* [Tier 1] Verify VM can be created with new feature X
  - *Priority:* P0

- **[Jira-124]** — As an admin...
  - *Test Scenario:* [Tier 2] Verify API for feature X is backward-compatible
  - *Priority:* P0

- **[Jira-125]** — As an admin user, I want to block non-admin users from deleting VMs
  - *Test Scenario:* [Tier 2] Verify non-admin user cannot delete a VM
  - *Priority:* P1

- **[Jira-126]** — As a cluster admin...
  - *Test Scenario:* [Tier 2] Verify upgrade from version X to Y preserves feature state
  - *Priority:* P2

---

### **IV. Sign-off and Approval**

This Software Test Plan requires approval from the following stakeholders:

* **Reviewers:**
  - [Name / @github-username]
  - [Name / @github-username]
* **Approvers:**
  - [Name / @github-username]
  - [Name / @github-username]
