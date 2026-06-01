# Openshift-virtualization-tests Test plan

## **Scratch Space Storage Class Selection Logic - Quality Engineering Plan**

### **Metadata & Tracking**

- **Enhancement(s):** https://github.com/kubevirt/containerized-data-importer/pull/4054
- **Feature Tracking:** https://issues.redhat.com/browse/CNV-72238
- **Epic Tracking:** https://issues.redhat.com/browse/CNV-79031
- **Feature Maturity:**
  - DP: N/A
  - TP: N/A
  - GA: 4.22
- **QE Owner(s):** Kate Shvaika (kshvaika@redhat.com)
- **Owning SIG:** sig-storage
- **Participating SIGs:** sig-storage

**Document Conventions (if applicable):** N/A


### **Feature Overview**

Some volume provisioning operations (such as registry imports, image uploads, or certain http imports) require an additional temporary PVC known as a scratch space PVC to act as an intermediary step in processing the data prior to writing it to the target PVC. This feature changes the default storage class selection for scratch space PVCs: it now uses the same storage class as the target volume, instead of falling back to the cluster default. Administrators can still configure a specific scratch space storage class to override this behavior by using the CDI config field `scratchSpaceStorageClass`

---

### **I. Motivation and Requirements Review (QE Review Guidelines)**

This section documents the mandatory QE review process. The goal is to understand the feature's value,
technology, and testability before formal test planning.

#### **1. Requirement & User Story Review Checklist**

- [x] **Review Requirements**
  - *List the key D/S requirements reviewed:*
    - When no scratch space storage class is configured, scratch space must use the same storage class as the target volume
    - When a scratch space storage class is explicitly configured by the administrator, it must override the default same-as-target behavior
    - Existing administrator configurations for scratch space storage class must continue to work unchanged

- [x] **Understand Value and Customer Use Cases**
  - *Describe the feature's value to customers:*
    - Ensures consistent storage provisioning behavior, reducing confusion and configuration errors
    - Aligns temporary resource allocation with production storage requirements
  - *List the customer use cases identified:*
    - As a VM owner, I want scratch space to use the same storage class as my volume so that provisioning is consistent

- [x] **Testability**
  - *Note any requirements that are unclear or untestable:* None - all requirements are testable through volume provisioning operations (import, upload) with various storage class configurations

- [x] **Acceptance Criteria**
  - *List the acceptance criteria:*
    - When no explicit scratch space storage class is configured, scratch space uses the same storage class as the target PVC
    - When an explicit scratch space storage class is configured, scratch space uses that configured storage class
  - *Note any gaps or missing criteria:* None

- [x] **Non-Functional Requirements (NFRs)**
  - *List applicable NFRs and their targets:*
    - **Documentation:** Documentation update is required to explain new default behavior
  - *Note any NFRs not covered and why:*
    - **UI:** Not applicable. backend storage class selection logic only, no UI changes.
    - **Monitoring:** Not applicable. Existing metrics reflect scratch space creation, no new metrics required
    - **Observability:** Not applicable. Scratch space allocation is logged through existing CDI events
    - **Performance:** Not applicable. No impact on provisioning performance
    - **Security:** Not applicable. Uses existing CDI RBAC for storage operations, no new security requirements.
    - **Scalability:** Not applicable. Selection logic scales with existing CDI controller capabilities


#### **2. Known Limitations**

None — reviewed and confirmed with Kate Shvaika, Danny Sanatar / 2026-05-05 that no feature limitations apply for this release.


#### **3. Technology and Design Review**

- [x] **Developer Handoff/QE Kickoff**
  - *Key takeaways and concerns:* Reviewed changes in Scratch Space Storage Class Selection Logic with the developer. Untestable aspects were not identified.

- [x] **Technology Challenges**
  - *List identified challenges:*
    - Multiple volume provisioning operations can trigger scratch space allocation (import, upload)
  - *Impact on testing approach:*
    - Tests must cover all volume provisioning operations that use scratch space

- [x] **API Extensions**
  - *List new or modified APIs:*
    - No API changes - internal logic change only
    - Cluster configuration option for scratch space storage class unchanged
  - *Testing impact:*
    - No API testing updates required
    - Functional tests update required

- [x] **Test Environment Needs**
  - *See environment requirements in Section II.3 and testing tools in Section II.3.1*
    - Ability to modify HCO configuration (for scratchSpaceStorageClass override testing)

- [x] **Topology Considerations**
  - *Describe topology requirements:* Standard cluster topology sufficient
  - *Impact on test design:* No special topology requirements

### **II. Software Test Plan (STP)**

This STP serves as the **overall roadmap for testing**, detailing the scope, approach, resources, and schedule.

#### **1. Scope of Testing**

**Testing Goals**

- **[P0]** Verify that volume provisioning operations automatically allocate scratch space using the same storage class as the target volume when no cluster-level override is configured
- **[P0]** Validate that cluster administrator configuration for scratch space storage class takes priority over the default behavior
- **[P0]** Confirm consistent scratch space storage class selection across all volume provisioning workflows (import, upload)

**Out of Scope (Testing Scope Exclusions)**

None — reviewed and confirmed that all supported product functionality will be tested this cycle.
- *Rationale:* Feature changes default storage class selection logic for scratch space only. Scope is narrow and well-defined with clear testable behaviors (default same-as-target vs configured override). All user-facing functionality can be verified through standard disk provisioning operations.
- *PM/Lead Agreement:* Adam Litke, May 26 2026


**Test Limitations**

None — reviewed and confirmed with Kate Shvaika/2026-05-05 that no test limitations apply for this release.

#### **2. Test Strategy**

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

- [ ] **Performance Testing** — Validates feature performance meets requirements (latency, throughput, resource usage)
  - *Details:* N/A - no impact on provisioning performance

- [ ] **Scale Testing** — Validates feature behavior under increased load and at production-like scale (e.g., large number of VMs, nodes, or concurrent operations)
  - *Details:* N/A - Selection logic scales with existing CDI controller capabilities

- [ ] **Security Testing** — Verifies security requirements, RBAC, authentication, authorization, and vulnerability scanning
  - *Details:* N/A - no new security requirements

- [ ] **Usability Testing** — Validates user experience and accessibility requirements
  - *Details:* N/A - Backend storage class selection logic only

- [ ] **Monitoring** — Does the feature require metrics and/or alerts?
  - *Details:* N/A - no new metrics required


**Integration & Compatibility**

- [x] **Compatibility Testing** — Ensures feature works across supported platforms, versions, and configurations
  - Does the feature maintain backward compatibility with previous API versions and configurations?
  - *Details:*  Test with different storage class types (OCS, HPP)

- [x] **Upgrade Testing** — Validates upgrade paths from previous versions, data migration, and configuration preservation
  - *Details:* Verify existing scratchSpaceStorageClass configurations are preserved during upgrade. Verify new default behavior (same-as-target) applies to operations started after upgrade.

- [x] **Dependencies** — Blocked by deliverables from other components/products. Identify what we need from other teams before we can test.
  - *Details:* Not applicable. No Dependencies.

- [x] **Cross Integrations** — Does the feature affect other features or require testing by other teams? Identify the impact we cause.
  - *Details:* Not applicable. Changes do not affect other features.


**Infrastructure**

- [x] **Cloud Testing** — Does the feature require multi-cloud platform testing? Consider cloud-specific features.
  - *Details:* Not applicable

#### **3. Test Environment**

- **Cluster Topology:** standard 3-master/3-worker

- **OCP & OpenShift Virtualization Version(s):** OCP 4.22 with OpenShift Virtualization 4.22

- **CPU Virtualization:** VT-x (Intel) or AMD-V enabled

- **Compute Resources:** Minimum per worker node: 8 vCPUs, 32GB RAM

- **Special Hardware:** N/A

- **Storage:** ocs-storagecluster-ceph-rbd-virtualization, hostpath-provisioner, custom SC

- **Network:** OVN-Kubernetes, IPv4

- **Required Operators:** N/A

- **Platform:** PSI, Bare metal

- **Special Configurations:** N/A

#### **3.1. Testing Tools & Frameworks**

- **Test Framework:** Standard

- **CI/CD:** Standard

- **Other Tools:** N/A

#### **4. Entry Criteria**

The following conditions must be met before testing can begin:

- [x] Requirements and design documents are **approved and merged**
- [x] CDI implementation of new scratch space selection logic is **complete and merged**
- [x] Test environment can be **set up and configured** (see Section II.3 - Test Environment)


#### **5. Risks**

**Timeline/Schedule**

- **Risk:** N/A
  - **Mitigation:** Standard test timeline is sufficient for planned test scenarios. Feature scope is narrow with straightforward test cases.
  - *Estimated impact on schedule:* None
  - *Sign-off:* Kate Shvaika/2026-05-05

**Test Coverage**

- **Risk:** N/A
  - **Mitigation:** All acceptance criteria are covered by planned test scenarios.
  - *Areas with reduced coverage:* None
  - *Sign-off:* Kate Shvaika/2026-05-05

**Test Environment**

- **Risk:** N/A
  - **Mitigation:** Standard test environment with multiple storage classes is sufficient for testing this feature
  - *Missing resources or infrastructure:* None
  - *Sign-off:* Kate Shvaika/2026-05-05

**Untestable Aspects**

- **Risk:** N/A
  - **Mitigation:** All scenarios can be reproduced in test environment
  - *Alternative validation approach:* None
  - *Sign-off:* Kate Shvaika/2026-05-05

**Resource Constraints**

- **Risk:** N/A
  - **Mitigation:** Current QE team capacity is sufficient for planned test execution
  - *Current capacity gaps:* None
  - *Sign-off:* Kate Shvaika/2026-05-05

**Dependencies**

- **Risk:** N/A
  - **Mitigation:** No external dependencies.
  - *Dependent teams or components:* Documentation team for behavior change documentation (non-blocking)
  - *Sign-off:* Kate Shvaika/2026-05-05

**Other**

- **Risk:** N/A
  - **Mitigation:** No additional mitigation required
  - *Sign-off:* Kate Shvaika/2026-05-05

---

### **III. Test Scenarios & Traceability**

- **[CNV-72238]** — As a user, I want import operations to use the same storage class for scratch space as my target DataVolume
  - *Test Scenario:* [Tier 2] Verify import requiring conversion allocates scratch space using target DataVolume storage class
  - *Priority:* P0

- **[CNV-72238]** — As a user, I want upload operations to use the same storage class for scratch space as my target DataVolume
  - *Test Scenario:* [Tier 2] Verify upload operation allocates scratch space using target DataVolume storage class
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
  - QE Architect: Ruth Netser (@rnetser)
  - QE Members (OCP-V): Jenia Peimer (@jpeimer), Jose Manuel Castano (@joscasta)
  - Developer: Danny Sanatar (@dsanatar)
* **Approvers:**
  - QE Architect: Ruth Netser (@rnetser)
  - QE Lead: Jenia Peimer (@jpeimer)
