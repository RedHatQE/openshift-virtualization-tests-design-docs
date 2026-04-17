# Openshift-virtualization-tests Test plan

## **Scratch Space Storage Class Selection Logic - Quality Engineering Plan**

### **Metadata & Tracking**

- **Enhancement(s):** https://github.com/kubevirt/containerized-data-importer/pull/4054
- **Feature Tracking:** https://issues.redhat.com/browse/CNV-72238
- **Epic Tracking:** https://issues.redhat.com/browse/CNV-79031
- **QE Owner(s):** Kate Shvaika (kshvaika@redhat.com)
- **Owning SIG:** sig-storage
- **Participating SIGs:** sig-storage

**Document Conventions (if applicable):**
- **SC** - Storage Class
- **HCO** - HyperConverged Cluster Operator
- **CDI** - Containerized Data Importer
- **PVC** - Persistent Volume Claim

### **Feature Overview**

Some VM disk provisioning operations require temporary scratch space. This feature changes the default storage class selection for scratch space: it now uses the same storage class as the target disk, instead of falling back to the cluster default. Administrators can configure a specific storage class for scratch space to override this behavior.

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
  - *List the key D/S requirements reviewed:*
    - When no scratch space storage class is configured, scratch space must use the same storage class as the target disk
    - When a scratch space storage class is explicitly configured by the administrator, it must override the default same-as-target behavior
    - Existing administrator configurations for scratch space storage class must continue to work unchanged

- [x] **Understand Value and Customer Use Cases**
  <!-- Understand why the feature matters to customers from a D/S perspective and what the real-world use cases are.
  Example: "Customers need to migrate VMs without network downtime to maintain SLA compliance during node maintenance." -->
  - *Describe the feature's value to customers:*
    - Ensures consistent storage provisioning behavior, reducing confusion and configuration errors
    - Aligns temporary resource allocation with production storage requirements
  - *List the customer use cases identified:*
    - As a VM owner, I want scratch space to use the same storage class as my disk so that provisioning is consistent

- [x] **Testability**
  <!-- Confirmed requirements are **testable and unambiguous**. -->
  - *Note any requirements that are unclear or untestable:* None - all requirements are testable through CDI operations (clone, import, upload) with various storage class configurations

- [x] **Acceptance Criteria**
  <!-- Acceptance criteria are the specific, verifiable conditions that must be met for the feature to be considered complete — they define *how we know it works*.
  Example: "VM migrates without network downtime exceeding 500ms", "VM deletion is blocked for non-admin users." -->
  - *List the acceptance criteria:*
    - When no explicit scratch space storage class is configured, scratch space uses the same storage class as the target PVC
    - When an explicit scratch space storage class is configured, scratch space uses that configured storage class
    - Automated tests verify both default (same-as-target) and explicitly configured scratch space storage class behaviors
  - *Note any gaps or missing criteria:* None

- [ ] **Non-Functional Requirements (NFRs)**
  <!-- Confirmed coverage for NFRs, including Performance, Security, Usability, Downtime, Connectivity, Monitoring (alerts/metrics), Scalability, Portability (e.g., cloud support), and Docs.-->
  - *List applicable NFRs and their targets:*
    - Existing CDI metrics should reflect scratch space creation
    - Documentation update is required to explain new default behavior
  - *Note any NFRs not covered and why:*
    Performance and scale testing are not included in this test plan

#### **2. Known Limitations**

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

If there are no feature limitations, remove the example items and state: "None — reviewed and confirmed with [Name/Date] that no feature limitations apply for this release." -->

- **[Feature Limitation 1]**
  - *Sign-off:* [Name/Date — confirms awareness and acceptance of this limitation]

- **[Feature Limitation 2]**
  - *Sign-off:* [Name/Date — confirms awareness and acceptance of this limitation]

Need to be updated: None identified at this time.


#### **3. Technology and Design Review**

<!-- **How to complete this checklist:**
1. **Checkbox**: Mark [x] if done
2. Complete the relevant, needed details for the checklist item -->

- [ ] **Developer Handoff/QE Kickoff**
  <!-- A meeting where Dev/Arch walked QE through the design, architecture, and implementation details. **Critical for identifying untestable aspects early.**-->
  - *Key takeaways and concerns:* [Summarize key points and concerns]

- [x] **Technology Challenges**
  <!-- Identified potential testing challenges related to the underlying technology.-->
  - *List identified challenges:*
    - Multiple CDI operations can trigger scratch space allocation (clone, import, upload)
  - *Impact on testing approach:*
    - Tests must cover all CDI operations that use scratch space

- [x] **API Extensions**
  <!-- Review new or modified APIs and their impact on testing. Covers both new tests for new APIs and updates to existing tests for modified APIs.
  Example: "New VirtualMachineSnapshot API v1beta2 — 3 new endpoints, 1 modified endpoint. Existing snapshot tests need updating." -->
  - *List new or modified APIs:*
    - No API changes - internal CDI logic change only
    - scratchSpaceStorageClass HCO config option unchanged
  - *Testing impact:*
    - No API testing updates required
    - Functional tests update required

- [x] **Test Environment Needs**
  <!-- Identified whether special environment setups are needed beyond standard infrastructure.-->
  - *See environment requirements in Section II.3 and testing tools in Section II.3.1*
    - Ability to modify HCO configuration (for scratchSpaceStorageClass override testing)

- [x] **Topology Considerations**
  <!-- Evaluated multi-cluster, network topology, and architectural impacts.-->
  - *Describe topology requirements:* Standard cluster topology sufficient
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

- **[P0]** Verify that disk provisioning operations automatically allocate scratch space using the same storage class as the target disk when no cluster-level override is configured
- **[P0]** Validate that cluster administrator configuration for scratch space storage class takes priority over the default behavior
- **[P0]** Confirm consistent scratch space storage class selection across all disk provisioning workflows (clone, import, upload)

**Out of Scope (Testing Scope Exclusions)**

The following items are explicitly Out of Scope for this test cycle and represent intentional exclusions.
No verification activities will be performed for these items, and any related issues found will not be classified as defects for this release.

<!-- **What does Out of Scope mean?**
Out of Scope items are areas where the product works, but QE has decided not to test them this cycle.
This is the most critical section in the STP — it explicitly documents the gap between what the product can do and what QE will verify.
Every item here is a conscious risk accepted by PM/Lead. If an untested area breaks in production, this section proves the decision was deliberate and agreed upon.
Each item requires PM/Lead sign-off.

**Difference from Risks:** A risk is something that *might* prevent testing — you plan to test it but it could be blocked and you provide a mitigation plan.
Out of Scope means you have *decided not to test it* — the decision is final and accepted by stakeholders.
Example: "MultiArch cluster might not be available" is a **risk**. "We will not test on bare-metal MultiArch clusters" is **out of scope**.

**Note:** Replace examples with your actual out-of-scope items. If there are no items, remove the examples and state: "None — reviewed and confirmed that all supported product functionality will be tested this cycle." -->

None

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

If there are no test limitations, remove the example items and state: "None — reviewed and confirmed that no test limitations apply for this release." -->

None — reviewed and confirmed that no test limitations apply for this release.

#### **2. Test Strategy**

<!-- The following test strategy considerations must be reviewed and addressed. Mark [x] if applicable,
leave unchecked if not applicable (with justification in Details). Unchecked items without details
indicate incomplete review.

Note: Strategy defines *which types of testing* apply and the high-level approach. Goals (Section II.1) define the specific, measurable objectives.
Example: Strategy says "Performance testing is applicable — we will measure migration stuntime." Goals say "[P0] Verify VM stuntime during live migration is below 500ms." -->

**Functional**

- [x] **Functional Testing** — Validates that the feature works according to specified requirements and user stories
  - *Details:*
    - Test new default scratch space SC selection (same-as-target)
    - Test scratchSpaceStorageClass config override behavior
    - Test all CDI operations that allocate scratch space
    - Validate behavior with various storage class configurations

- [x] **Automation Testing** — Confirms test automation plan is in place for CI and regression coverage (all tests are expected to be automated)
  - *Details:*
    - All functional tests will be automated

- [x] **Regression Testing** — Verifies that new changes do not break existing functionality
  - *Details:*
    - Verify existing CDI operations work with new scratch space logic
    - Confirm scratchSpaceStorageClass config continues to work as before (override behavior unchanged)

**Non-Functional**

- [x] **Performance Testing** — Validates feature performance meets requirements (latency, throughput, resource usage)
  - *Details:*
    - Test concurrent scratch space allocations

- [ ] **Scale Testing** — Validates feature behavior under increased load and at production-like scale (e.g., large number of VMs, nodes, or concurrent operations)
  - *Details:* N/A - inherits existing CDI scratch space scalability characteristics

- [ ] **Security Testing** — Verifies security requirements, RBAC, authentication, authorization, and vulnerability scanning
  - *Details:* N/A - no new RBAC or security requirements; uses existing CDI permissions

- [x] **Usability Testing** — Validates user experience and accessibility requirements
  - *Details:*
    - CDI events/logs should indicate which storage class was selected for scratch space

- [x] **Monitoring** — Does the feature require metrics and/or alerts?
  - *Details:*
    - Use existing CDI metrics for scratch space PVC creation

**Integration & Compatibility**

- [x] **Compatibility Testing** — Ensures feature works across supported platforms, versions, and configurations
  - *Details:*
    - Test with different storage providers

- [ ] **Upgrade Testing** — Validates upgrade paths from previous versions, data migration, and configuration preservation
  - *Details:* Not applicable

- [ ] **Dependencies** — Blocked by deliverables from other components/products. Identify what we need from other teams before we can test.
  - *Details:* Not applicable

- [x] **Cross Integrations** — Does the feature affect other features or require testing by other teams? Identify the impact we cause.
  - *Details:*
    - Impacts CDI data import/clone/upload workflows

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

- **Storage:** ocs-storagecluster-ceph-rbd-virtualization, hostpath-provisioner, custom SC
  <!-- Change if specific StorageClass(es) required -->

- **Network:** OVN-Kubernetes, IPv4
  <!-- Change if needed, e.g., Secondary Networks, IPv6, dual-stack -->

- **Required Operators:** N/A
  <!-- Add if needed, e.g., NMState Operator -->

- **Platform:** PSI, Bare metal
  <!-- Change if needed, e.g., AWS, Azure, GCP -->

- **Special Configurations:** N/A
  <!-- Change if needed, e.g., Disconnected/air-gapped, Proxy, FIPS mode -->

#### **3.1. Testing Tools & Frameworks**

<!-- Document any **new or additional** testing tools, frameworks, or infrastructure required specifically
for this feature. **Note:** Only list tools that are **new** or **different** from standard testing infrastructure. -->

- **Test Framework:** Standard

- **CI/CD:** Standard

- **Other Tools:** N/A

#### **4. Entry Criteria**

The following conditions must be met before testing can begin:

- [x] Requirements and design documents are **approved and merged**
- [x] CDI implementation of new scratch space selection logic is **complete and merged**
- [x] Test environment can be **set up and configured** (see Section II.3 - Test Environment)


#### **5. Risks**

<!-- Document specific risks for this feature. If a risk category is not applicable, mark as "N/A" with
justification in mitigation strategy. -->

**Timeline/Schedule**

- **Risk:** N/A
  - **Mitigation:** N/A
  - *Estimated impact on schedule:* N/A
  - *Sign-off:* TBD

**Test Coverage**

- **Risk:** N/A
  - **Mitigation:** N/A
  - *Areas with reduced coverage:* N/A
  - *Sign-off:* TBD

**Test Environment**

- **Risk:** N/A
  - **Mitigation:** Standard test environment is sufficient for testing this feature
  - *Missing resources or infrastructure:* N/A
  - *Sign-off:* TBD

**Untestable Aspects**

- **Risk:** Customer production storage configurations may differ from test environments
  - **Mitigation:** Focus on logic correctness rather than specific storage class types
  - *Alternative validation approach:* N/A
  - *Sign-off:* TBD

**Resource Constraints**

- **Risk:** N/A
  - **Mitigation:** N/A
  - *Current capacity gaps:* N/A
  - *Sign-off:* TBD

**Dependencies**

- **Risk:** N/A
  - **Mitigation:** N/A
  - *Dependent teams or components:* N/A
  - *Sign-off:* TBD

**Other**

- **Risk:** N/A
  - **Mitigation:** No external dependencies
  - *Sign-off:* TBD

---

### **III. Test Scenarios & Traceability**

<!-- This section links D/S requirements to test coverage, enabling reviewers to verify all requirements are tested. -->

- **[CNV-72238]** — As a user, I want import operations to use the same storage class for scratch space as my target DataVolume
  - *Test Scenario:* [Tier 2] Verify import requiring conversion allocates scratch space using target DataVolume storage class
  - *Priority:* P0

- **[CNV-72238]** — As a user, I want upload operations to use the same storage class for scratch space as my target DataVolume
  - *Test Scenario:* [Tier 2] Verify upload operation allocates scratch space using target DataVolume storage class
  - *Priority:* P0

- **[CNV-72238]** — As a user, I want clone operations to use the same storage class for scratch space as my source PVC
  - *Test Scenario:* [Tier 2] Verify PVC clone allocates scratch space using source PVC storage class
  - *Priority:* P0

- **[CNV-72238]** — As a cluster admin, I want scratchSpaceStorageClass configuration to propagate from HCO to CDI
  - *Test Scenario:* [Tier 2] Verify scratchSpaceStorageClass set in HCO CR propagates to CDI CR configuration
  - *Priority:* P0

- **[CNV-72238]** — As a cluster admin, I want to configure scratch space storage class for import operations
  - *Test Scenario:* [Tier 2] Verify import operation uses scratchSpaceStorageClass configured in HCO
  - *Priority:* P0

---

### **IV. Sign-off and Approval**

This Software Test Plan requires approval from the following stakeholders:

* **Reviewers:**
  - TBD
* **Approvers:**
  - TBD
