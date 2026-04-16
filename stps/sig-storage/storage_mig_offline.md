# Openshift-virtualization-tests Test plan

## **Offline Storage Migration - Quality Engineering Plan**

### **Metadata & Tracking**

- **Enhancement(s):** https://github.com/kubevirt/kubevirt-migration-controller/pull/32
- **Feature Tracking:** [CNV-73509](https://redhat.atlassian.net/browse/CNV-73509)
- **Epic Tracking:** [CNV-73500](https://redhat.atlassian.net/browse/CNV-73500)
- **QE Owner(s):** Jose Manuel Castano (joscasta@redhat.com)
- **Owning SIG:** sig-storage
- **Participating SIGs:** sig-storage

**Document Conventions:**
None

### **Feature Overview**

This feature extends the OpenShift Virtualization migration plan to support storage migration for offline (stopped) VMs in addition to existing online (running) VM support. It enables customers to migrate storage for VMs regardless of their running state, allowing mixed migration plans containing both offline and running VMs.

---

### **I. Motivation and Requirements Review (QE Review Guidelines)**

This section documents the mandatory QE review process. The goal is to understand the feature's value,
technology, and testability before formal test planning.

#### **1. Requirement & User Story Review Checklist**

<!-- **How to complete this checklist:**
1. **Checkbox**: Mark [x] if the check is complete; if the item cannot be checked - add an explanation why in the `details` section
2. Complete the relevant, needed details for the checklist item -->

- [x] **Review Requirements**
  <!-- Review the D/S (Downstream) requirements as defined in Jira. Understand the difference between Upstream (U/S) and D/S requirements.
  Example: "VMs must migrate without network downtime exceeding the defined threshold during node maintenance." -->
  - *List the key D/S requirements reviewed:* Reviewed the user cases for offline VM storage migration from CNV-82430 and CNV-73500

- [x] **Understand Value and Customer Use Cases**
  <!-- Understand why the feature matters to customers from a D/S perspective and what the real-world use cases are.
  Example: "Customers need to migrate VMs without network downtime to maintain SLA compliance during node maintenance." -->
  - *Describe the feature's value to customers:* Customers need to perform storage migration for offline VMs without requiring them to be running, providing flexibility in storage management operations.
  - *List the customer use cases identified:* Storage migration for mixed offline VMs and running VMs in one migration plan, allowing batch migration operations regardless of VM state.

- [x] **Testability**
  <!-- Confirmed requirements are **testable and unambiguous**. -->
  - *Note any requirements that are unclear or untestable:* Requirements are testable. Downstream build with the feature code is available for testing.

- [x] **Acceptance Criteria**
  <!-- Acceptance criteria are the specific, verifiable conditions that must be met for the feature to be considered complete — they define *how we know it works*.
  Example: "VM migrates without network downtime exceeding 500ms", "VM deletion is blocked for non-admin users." -->
  - *List the acceptance criteria:*
    - Storage migration completes successfully for offline VMs between ODF and HPP storage classes
    - Storage migration completes successfully for mixed offline VMs and running VMs
    - Storage migration completes successfully for offline VMs with hotplug disk
    - Source volume could be retained/cleaned up for an offline VM migration completed with retentionPolicy defined
    - Offline VM points to the origin volume when migration failed
    - Migration succeeded when starting a stopped VM during migration

  - *Note any gaps or missing criteria:* N/A

- [x] **Non-Functional Requirements (NFRs)**
  <!-- Confirmed coverage for NFRs, including Performance, Security, Usability, Downtime, Connectivity, Monitoring (alerts/metrics), Scalability, Portability (e.g., cloud support), and Docs.-->
  - *List applicable NFRs and their targets:* Documentation updates to reflect offline VM storage migration support and UI support for offline VM migrations. 
  - *Note any NFRs not covered and why:* Performance, Monitoring, Observability, Security and Scalability testing are not included in this test plan

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

None - reviewed and confirmed with Yan Du on Apr 7,2026.

#### **3. Technology and Design Review**

<!-- **How to complete this checklist:**
1. **Checkbox**: Mark [x] if done
2. Complete the relevant, needed details for the checklist item -->

- [x] **Developer Handoff/QE Kickoff**
  <!-- A meeting where Dev/Arch walked QE through the design, architecture, and implementation details. **Critical for identifying untestable aspects early.**-->
  - *Key takeaways and concerns:* Extend the offline VMs storage migration support

- [x] **Technology Challenges**
  <!-- Identified potential testing challenges related to the underlying technology.-->
  - *List identified challenges:* Offline migration uses a different mechanism than online migration, requiring separate test coverage
  - *Impact on testing approach:* Test cases must verify both offline VM migration mixed scenarios with both offline and running VMs in the same migration plan.

- [x] **API Extensions**
  <!-- Review new or modified APIs and their impact on testing. Covers both new tests for new APIs and updates to existing tests for modified APIs.
  Example: "New VirtualMachineSnapshot API v1beta2 — 3 new endpoints, 1 modified endpoint. Existing snapshot tests need updating." -->
  - *List new or modified APIs:* No new APIs - extends existing migration plan API to handle offline VMs
  - *Testing impact:* No API test updates required; functional tests will verify new behavior

- [x] **Test Environment Needs**
  <!-- Identified whether special environment setups are needed beyond standard infrastructure.-->
  - *See environment requirements in Section II.3 and testing tools in Section II.3.1*

- [x] **Topology Considerations**
  <!-- Evaluated multi-cluster, network topology, and architectural impacts.-->
  - *Describe topology requirements:* Standard 3-master/3-worker cluster sufficient
  - *Impact on test design:* No special topology requirements

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

- **[P0]** Verify offline VM storage migration completes between ODF and HPP storage classes, and the VM boots successfully after migration
- **[P0]** Verify storage migration completes for a migration plan containing both offline and running VMs
- **[P0]** Verify source volumes are retained or deleted according to retentionPolicy configuration when offline VM storage migration completes
- **[P1]** Verify offline VM storage migration completes when the VM has hotplug disks attached
- **[P2]** Verify offline VM continues pointing to the original volume when storage migration fails
- **[P2]** Verify storage migration completes when a stopped VM is started during the migration process

**Storage Class Coverage**

The following storage class migration combinations will be tested:
- **ODF (ocs-storagecluster-ceph-rbd-virtualization) ↔ HPP (hostpath-provisioner)
- **ODF ↔ ODF** — Same storage class migration
- **HPP ↔ HPP** — Same storage class migration

Storage classes **not covered** in this test plan:
- Cloud provider-specific storage classes (AWS EBS, Azure Disk, GCP PD) — Out of scope for initial release

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

None

#### **2. Test Strategy**

<!-- The following test strategy considerations must be reviewed and addressed. Mark [x] if applicable,
leave unchecked if not applicable (with justification in Details). Unchecked items without details
indicate incomplete review.

Note: Strategy defines *which types of testing* apply and the high-level approach. Goals (Section II.1) define the specific, measurable objectives.
Example: Strategy says "Performance testing is applicable — we will measure migration stuntime." Goals say "[P0] Verify VM stuntime during live migration is below 500ms." -->

**Functional**

- [x] **Functional Testing** — Validates that the feature works according to specified requirements and user stories
  <!-- Mark if this feature requires functional testing. Functional testing validates that the feature works as specified — as opposed to non-functional testing (performance, security, scale, etc.) which validates how well it works. -->
  - *Details:* Functional testing will verify offline VM storage migration and mixed offline/online VM migration scenarios

- [x] **Automation Testing** — Confirms test automation plan is in place for CI and regression coverage (all tests are expected to be automated)
  <!-- Example: "All Tier 2 tests automated by sprint 3, integrated into nightly CI lane." -->
  - *Details:* All test cases will be automated

- [x] **Regression Testing** — Verifies that new changes do not break existing functionality
  - *Details:* Verify that existing online VM storage migration functionality remains unaffected by the offline VM support additions

**Non-Functional**

- [ ] **Performance Testing** — Validates feature performance meets requirements (latency, throughput, resource usage)
  - *Details:* Performance testing for bulk offline migrations is tracked separately in CNV-82430 and will be covered by a separate test plan

- [ ] **Scale Testing** — Validates feature behavior under increased load and at production-like scale (e.g., large number of VMs, nodes, or concurrent operations)
  - *Details:* Not applicable

- [ ] **Security Testing** — Verifies security requirements, RBAC, authentication, authorization, and vulnerability scanning
  - *Details:* Not applicable

- [x] **Usability Testing** — Validates user experience and accessibility requirements
  - Does the feature require a UI? If so, ensure the UI aligns with the requirements (UI/UX consistency, accessibility)
  - Does the feature expose CLI commands? If so, validate usability and that needed information is available (e.g., status conditions, clear output)
  - Does the feature trigger backend operations that should be reported to the admin? If so, validate that the user receives clear feedback about the operation and its outcome (e.g., status conditions, events, or notifications indicating success or failure)
  - *Details:* UI testing will be covered in https://redhat.atlassian.net/browse/CNV-77503

- [ ] **Monitoring** — Does the feature require metrics and/or alerts?
  - *Details:* Not applicable

**Integration & Compatibility**

- [x] **Compatibility Testing** — Ensures feature works across supported platforms, versions, and configurations
  - Does the feature maintain backward compatibility with previous API versions and configurations?
  - *Details:* Feature maintains backward compatibility with existing migration API. Existing online VM migrations continue to work unchanged.

- [ ] **Upgrade Testing** — Validates upgrade paths from previous versions, data migration, and configuration preservation
  - *Details:* Not applicable

- [ ] **Dependencies** — Blocked by deliverables from other components/products. Identify what we need from other teams before we can test.
  <!-- Example: "Blocked on Storage team delivering CSI driver v2.0 — cannot test snapshot feature without it." -->
  - *Details:* No blocking dependencies

- [x] **Cross Integrations** — Does the feature affect other features or require testing by other teams? Identify the impact we cause.
  <!-- Example: "Our API change affects the UI team's VM details page — they need to update their tests." -->
  - *Details:* UI team needs to update their migration UI to support offline VM selection

**Infrastructure**

- [ ] **Cloud Testing** — Does the feature require multi-cloud platform testing? Consider cloud-specific features.
  - *Details:* Not applicable

#### **3. Test Environment**

<!-- **Note:** "N/A" means explicitly not applicable. All items must be filled or marked N/A. -->

- **Cluster Topology:** 3-master/3-worker bare-metal
  <!-- Change if different, e.g., SNO, Compact Cluster, HCP -->

- **OCP & OpenShift Virtualization Version(s):** OCP 4.22 with OpenShift Virtualization 4.22
  <!-- Specify exact versions to allow version traceability -->

- **CPU Virtualization:** VT-x (Intel) or AMD-V enabled
  <!-- Change only if specific CPU requirements exist -->

- **Compute Resources:** Minimum per worker node: 8 vCPUs, 32GB RAM
  <!-- Adjust based on feature requirements -->

- **Special Hardware:** N/A
  <!-- Fill if needed, e.g., SR-IOV NICs, GPUs -->

- **Storage:** ocs-storagecluster-ceph-rbd-virtualization, hostpath-provisioner
  <!-- Change if specific StorageClass(es) required -->

- **Network:** OVN-Kubernetes, IPv4
  <!-- Change if needed, e.g., Secondary Networks, IPv6, dual-stack -->

- **Required Operators:** N/A
  <!-- Add if needed, e.g., NMState Operator -->

- **Platform:** PSI
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

- [x] Requirements and design documents are **approved and merged**
- [x] Test environment can be **set up and configured** (see Section II.3 - Test Environment)

#### **5. Exit Criteria**

- [ ] All high-priority defects are resolved and verified
- [ ] Test coverage goals achieved
- [ ] Test automation merged (required for GA sign-off)
- [ ] All planned test cycles completed
- [ ] Test summary report approved
- [ ] Acceptance criteria met

#### **6. Risks**

<!-- Document specific risks for this feature. If a risk category is not applicable, mark as "N/A" with
justification in mitigation strategy. -->

**Timeline/Schedule**

- **Risk:** N/A
  - **Mitigation:** N/A
  - *Estimated impact on schedule:* None

**Test Coverage**

- **Risk:** N/A
  - **Mitigation:** All acceptance criteria are covered by planned test scenarios
  - *Areas with reduced coverage:* None

**Test Environment**

- **Risk:** N/A
  - **Mitigation:** Standard test environment is sufficient for testing this feature
  - *Missing resources or infrastructure:* None

**Untestable Aspects**

- **Risk:** N/A
  - **Mitigation:** N/A
  - *Alternative validation approach:* N/A

**Resource Constraints**

- **Risk:** N/A
  - **Mitigation:** N/A
  - *Current capacity gaps:* None

**Dependencies**

- **Risk:** N/A
  - **Mitigation:** No external dependencies
  - *Dependent teams or components:* UI team for UI updates (non-blocking)

**Other**

- **Risk:** N/A
  - **Mitigation:** No additional risks identified
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

- **[CNV-73500]** — As a VM owner, I want to migrate storage for offline VMs between ODF and HPP
  - *Test Scenario:* [Tier 2] Verify storage migration completes for offline VMs between ODF and HPP, and the VM boots sucessfully after migration
  - *Priority:* P0

- **[CNV-73500]** — As a VM owner, I want to migrate storage with mixed VM states (online and offline)
  - *Test Scenario:* [Tier 2] Verify storage migration completes for a migration plan containing both offline and running VMs
  - *Priority:* P0

- **[CNV-73500]** — As a VM owner, I want to migrate storage for offline VMs with hotplug disk
  - *Test Scenario:* [Tier 2] Verify storage migration completes successfully for offline VM with hotplug disk
  - *Priority:* P1

- **[CNV-73500]** — As a VM owner, I want to retain or delete the source volume for an offline VM
  - *Test Scenario:* [Tier 2] Verify source volume is retained or cleaned up for an offline VM when retentionPolicy is set in the Migration Plan
  - *Priority:* P0

- **[CNV-73500]** — As a VM owner, I want an offline VM to still point to the original volume when migration fails
  - *Test Scenario:* [Tier 2] Verify an offline VM still points to the original volume when migration fails
  - *Priority:* P2

- **[CNV-73500]** — As a VM owner, I want the migration to succeed when starting a stopped VM during migration
  - *Test Scenario:* [Tier 2] Verify migration succeeds when starting a stopped VM during the migration process
  - *Priority:* P2

---

### **IV. Sign-off and Approval**

This Software Test Plan requires approval from the following stakeholders:

* **Reviewers:**
  - QE Architect (OCP-V): Ruth Netser (`@rnetser`)
  - QE Members (OCP-V): Jenia Peimer (`@jpeimer`), Kate Shvaika (`@kshvaika`), Jose Manuel Castano (`@joscasta`)
* **Approvers:**
  - QE Architect (OCP-V): Ruth Netser (`@rnetser`)
  - Principal Developer: Alexander Wels (`@awels`)
