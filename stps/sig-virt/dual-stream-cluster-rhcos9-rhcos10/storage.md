# Openshift-virtualization-tests Test plan

## **[RHCOS9 and RHCOS10 Worker Nodes Support] - Quality Engineering Plan**

### **Metadata & Tracking**

- **Enhancement(s):**
  - https://redhat.atlassian.net/browse/CNV-77018 - no VEP for this feature.
  - https://redhat.atlassian.net/browse/CNV-85250
- **Feature Tracking:** https://redhat.atlassian.net/browse/VIRTSTRAT-83
- **Epic Tracking:**
  - https://redhat.atlassian.net/browse/CNV-77018
  - https://redhat.atlassian.net/browse/CNV-85250
- **Feature Maturity:**
  - DP: N/A
  - TP: v4.22
  - GA: v5.0
- **QE Owner(s):** Kate Shvaika (kshvaika@redhat.com), Ahmad Hafe (ahafe@redhat.com)
- **Owning SIG:** sig-virt
- **Participating SIGs:** sig-virt, sig-storage

**Document Conventions (if applicable):**
- RHCOS = Red Hat CoreOS, the immutable container-optimized OS used for OpenShift worker nodes.
- dual-stream cluster = a cluster running both RHCOS9 and RHCOS10 worker nodes simultaneously.
- hotplug = attaching a storage volume (PVC) to a running VM without restart.
- snapshot = a point-in-time copy of a VM's disk state, capturing the VM's data and filesystem; snapshots can be created while the VM is running or stopped.
- restore = the process of recovering a VM from a snapshot, returning it to the state captured at snapshot time.

### **Feature Overview**

Starting with OCP 4.22, OpenShift Virtualization supports dual-stream clusters running both RHCOS9 and RHCOS10 worker nodes simultaneously.

**Note:** this STP covers storage testing for dual-stream clusters starting from OCP 4.22 and should be reviewed when RHCOS9 or RHCOS10 support changes.

Customers can upgrade their clusters from RHCOS9 to RHCOS10 nodes gradually. VM live migration, hotplugged storage, and snapshots must work correctly across node types without data loss or corruption.

This STP covers storage testing for dual-stream clusters: hotplug storage operations, live migration with attached volumes, and snapshot/restore across RHCOS9 and RHCOS10 nodes.



---

### **I. Motivation and Requirements Review (QE Review Guidelines)**

This section documents the mandatory QE review process. The goal is to understand the feature's value,
technology, and testability before formal test planning.

#### **1. Requirement & User Story Review Checklist**

- [x] **Review Requirements**
  - *List the key D/S requirements reviewed:* See Acceptance Criteria and Testing Goals (Sections I.1 and II.1).

- [x] **Understand Value and Customer Use Cases**
  - *Describe the feature's value to customers:* Customers can upgrade their clusters from RHCOS9 to RHCOS10 nodes gradually while maintaining VM availability and storage operations.
  - *List the customer use cases identified:*
    - Migrate VMs with hotplugged storage between RHCOS9 and RHCOS10 nodes without data loss.
    - Snapshot a VM on RHCOS 9 and restore it on RHCOS 10 (or vice versa) without data loss.

- [x] **Testability**
  - *Note any requirements that are unclear or untestable:* All requirements are testable. Tests will cover VM migration with hotplugged storage and snapshot/restore operations across RHCOS9 and RHCOS10 nodes. New automated tests will be added to cover hotplug storage migration and snapshot/restore scenarios across RHCOS9 and RHCOS10 nodes.

- [x] **Acceptance Criteria**
  - *List the acceptance criteria:*
    - VM with hotplugged storage volume live migrates successfully in both directions (RHCOS9 ↔ RHCOS10) without data loss or corruption.
    - VM snapshots created on RHCOS9 can be restored on RHCOS10 and vice versa without data loss or corruption.
  - *Note any gaps or missing criteria:* None

- [x] **Non-Functional Requirements (NFRs)**
  - *List applicable NFRs and their targets:* None — no new non-functional requirements introduced by this feature.
  - *Note any NFRs not covered and why:*
    - Performance: no new performance requirements introduced.
    - Security: no new auth changes.
    - Monitoring/Observability: no new storage metrics or alerts required.
    - Scalability: no new scale requirements for storage functionality.
    - UI/Docs: existing user-facing storage functionality is preserved; no UI or documentation updates are needed to express support for a dual-stream cluster.

#### **2. Known Limitations**

None — reviewed and confirmed with Kate Shvaika May 20, 2026 that no feature limitations apply for this release.

#### **3. Technology and Design Review**

- [x] **Developer Handoff/QE Kickoff**
  - *Key takeaways and concerns:* See Testing Goals (Section II.1) and Test Strategy (Section II.2).

- [x] **Technology Challenges**
  - *List identified challenges:* Mixed RHCOS9 and RHCOS10 kernel versions may affect storage subsystem behavior (hotplug mechanisms, snapshot/restore compatibility) differently per node.
  - *Impact on testing approach:* Tests must explicitly validate storage hotplug, live migration, and snapshot/restore operations across RHCOS versions to detect kernel-related incompatibilities.

- [x] **API Extensions**
  - *List new or modified APIs:* No new APIs required for this feature.
  - *Testing impact:* N/A

- [x] **Test Environment Needs**
  - *See environment requirements in Section II.3 and testing tools in Section II.3.1*

- [x] **Topology Considerations**
  - *Describe topology requirements:* See Section II.3 - Test Environment.
  - *Impact on test design:* Adding migration tests with hotplugged storage and snapshot/restore tests between RHCOS9 and RHCOS10 nodes.

### **II. Software Test Plan (STP)**

This STP serves as the **overall roadmap for testing**, detailing the scope, approach, resources, and schedule.

#### **1. Scope of Testing**

**Testing Goals**

- **[P0]** Verify VM with hotplugged storage volume live migrates successfully between RHCOS9 and RHCOS10 nodes in both directions without data loss or corruption.
- **[P0]** Verify VM snapshots created on RHCOS9 can be restored on RHCOS10 and vice versa without data loss or corruption on a dual-stream cluster.

**Out of Scope (Testing Scope Exclusions)**

- **Non-RHCOS worker node variants**
  - *Rationale:* This feature targets RHCOS-based nodes only; non-RHCOS worker variants are out of scope for this release.
  - *PM/Lead Agreement:* Adam Litke, May 25 2026

**Test Limitations**

None — reviewed and confirmed that no test limitations apply for this release.

#### **2. Test Strategy**

**Functional**

- [x] **Functional Testing** — Validates that the feature works according to specified requirements and user stories
  - *Details:* Validate VM live migration with hotplugged storage and snapshot/restore operations on a dual-stream cluster between RHCOS9 and RHCOS10 nodes.

- [x] **Automation Testing** — Confirms test automation plan is in place for CI and regression coverage (all tests are expected to be automated)
  - *Details:* All new migration tests with storage hotplug and snapshot/restore tests will be automated and run in dedicated CI lanes (see Section II.3.1).

- [ ] **Regression Testing** — Verifies that new changes do not break existing functionality
  - *Details:* Not applicable. Existing Tier 2 storage tests have already been validated on dual-stream cluster. This STP covers only new cross-version migration and snapshot/restore scenarios.

**Non-Functional**

- [ ] **Performance Testing** — Validates feature performance meets requirements (latency, throughput, resource usage)
  - *Details:* From a storage perspective, no dedicated performance testing is required. Potential performance implications of running a dual-stream cluster (e.g., migration timing, I/O throughput differences between RHCOS9 and RHCOS10) should be covered by the parent STP.

- [ ] **Scale Testing** — Validates feature behavior under increased load and at production-like scale
  - *Details:* From a storage perspective, no dedicated scale testing is required. Scale implications of running a dual-stream cluster should be covered by the parent STP.

- [ ] **Security Testing** — Verifies security requirements, RBAC, authentication, authorization
  - *Details:* From a storage perspective, no dedicated security testing is required. Security implications in a dual-stream cluster should be covered by the parent STP.

- [ ] **Usability Testing** — Validates user experience and accessibility requirements
  - *Details:* From a storage perspective, no UI or CLI changes are introduced.

- [ ] **Monitoring** — Does the feature require metrics and/or alerts?
  - *Details:* From a storage perspective, no new metrics or alerts are required. Node version exposure and cluster-level observability should be covered by the parent STP.

**Integration & Compatibility**

- [ ] **Compatibility Testing** — Ensures feature works across supported platforms, versions, and configurations
  - *Details:* Not applicable for this STP.

- [ ] **Upgrade Testing** — Validates upgrade paths from previous versions
  - *Details:* Not applicable for this STP.

- [x] **Dependencies** — Blocked by deliverables from other components/products.
  - *Details:* Dedicated CI lanes must be provisioned by QE DevOps before testing can begin (see Section II.4 - Entry Criteria).

- [ ] **Cross Integrations** — Does the feature affect other features or require testing by other teams?
  - *Details:* This STP covers the storage scope only. Cross-integration testing is covered by the parent STP.

**Infrastructure**

- [ ] **Cloud Testing** — Does the feature require multi-cloud platform testing?
  - *Details:* Not applicable

#### **3. Test Environment**

- **Cluster Topology:**
  - Dual-stream cluster with at least one RHCOS9 and one RHCOS10 worker node - for live migration and snapshot/restore scenarios with storage

- **OCP & OpenShift Virtualization Version(s):** OCP 4.22+ with OpenShift Virtualization 4.22+

- **CPU Virtualization:** VT-x (Intel) or AMD-V enabled

- **Compute Resources:** Minimum per worker node: 8 vCPUs, 32GB RAM

- **Special Hardware:** N/A

- **Storage:** ocs-storagecluster-ceph-rbd-virtualization

- **Network:** OVN-Kubernetes, IPv4

- **Required Operators:** N/A

- **Platform:** Bare metal

- **Special Configurations:** N/A

#### **3.1. Testing Tools & Frameworks**

- **Test Framework:** Standard. Tests require logic to identify nodes by RHCOS version, create VM on specific nodes via nodeAffinity, hotplug storage to VM, verify live migration crosses between RHCOS9 and RHCOS10 nodes, and validate snapshot/restore operations work across RHCOS versions.

- **CI/CD:** dedicated lane required for a dual-stream cluster topology (see Cluster Topology above).

- **Other Tools:** N/A

#### **4. Entry Criteria**

The following conditions must be met before testing can begin:

- [x] Requirements and design documents are **approved and merged**
- [x] Test environment can be **set up and configured** (see Section II.3 - Test Environment)

#### **5. Risks**

**Timeline/Schedule**

- **Risk:** N/A
  - **Mitigation:** Test implementation is straightforward; no timeline concerns identified.
  - *Estimated impact on schedule:* None
  - *Sign-off:* Kate Shvaika/2026-05-20

**Test Coverage**

- **Risk:** N/A
  - **Mitigation:** Required scenarios covered by new automated tests (see Section III).
  - *Areas with reduced coverage:* None
  - *Sign-off:* Kate Shvaika/2026-05-20

**Test Environment**

- **Risk:** N/A
  - **Mitigation:** Dedicated CI lanes can be provisioned on demand by QE DevOps.
  - *Missing resources or infrastructure:* None
  - *Sign-off:* Kate Shvaika/2026-05-20

**Untestable Aspects**

- **Risk:** N/A
  - **Mitigation:** All test scenarios are reproducible.
  - *Alternative validation approach:* N/A
  - *Sign-off:* Kate Shvaika/2026-05-20

**Resource Constraints**

- **Risk:** N/A
  - **Mitigation:** No special resource requirements.
  - *Current capacity gaps:* None
  - *Sign-off:* Kate Shvaika/2026-05-20

**Dependencies**

- **Risk:** N/A
  - **Mitigation:** No external dependencies
  - *Dependent teams or components:* None
  - *Sign-off:* Kate Shvaika/2026-05-20

---

### **III. Test Scenarios & Traceability**

#### **VM live migration with hotplugged storage (CNV-96771)**

- **[CNV-77018]** — As a cluster admin, I want VMs with hotplugged storage to live migrate without data loss or corruption from RHCOS9 to RHCOS10 nodes on a dual-stream cluster.
  - *Test Tier:* Tier 2
  - *Priority:* P0

- **[CNV-77018]** — As a cluster admin, I want VMs with hotplugged storage to live migrate without data loss or corruption from RHCOS10 to RHCOS9 nodes on a dual-stream cluster.
  - *Test Tier:* Tier 2
  - *Priority:* P0

#### **Snapshot/Restore Across RHCOS Versions (CNV-96772)**

- **[CNV-96772]** — As a cluster admin, I want to snapshot a VM on RHCOS 9 and restore it on RHCOS 10 without data loss or corruption on a dual-stream cluster.
  - *Test Tier:* Tier 2
  - *Priority:* P0

- **[CNV-96772]** — As a cluster admin, I want to snapshot a VM on RHCOS 10 and restore it on RHCOS 9 without data loss or corruption on a dual-stream cluster.
  - *Test Tier:* Tier 2
  - *Priority:* P0

---

### **IV. Sign-off and Approval**

This Software Test Plan requires approval from the following stakeholders:

* **Reviewers:**
  - QE Architect: Ruth Netser (@rnetser)
  - Developer: Arnon Gilboa
  - QE Members: Jenia Peimer (@jpeimer), Jose Manuel Castano (@joscasta)
* **Approvers:**
  - QE Architect: Ruth Netser (@rnetser)
