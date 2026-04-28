# Openshift-virtualization-tests Test plan

## **[RHCOS 9 and RHCOS 10 Worker Nodes Support] - Quality Engineering Plan**

### **Metadata & Tracking**

- **Enhancement(s):** [CNV-77027](https://issues.redhat.com/browse/CNV-77027) - no VEP or HLD exists for this feature.
- **Feature Tracking:** https://redhat.atlassian.net/browse/VIRTSTRAT-83
- **Epic Tracking:** https://redhat.atlassian.net/browse/CNV-77027
- **QE Owner(s):** Asia Khromov (@azhivovk)
- **Owning SIG:** sig-virt
- **Participating SIGs:** sig-virt, sig-network

- **Target Release(s):**
  - DP: N/A
  - TP: v4.22
  - GA: v5.0

**Document Conventions:**
- RHCOS = Red Hat CoreOS, the immutable container-optimized OS used for OpenShift worker nodes.
- dual-stream cluster = a cluster running both RHCOS 9 and RHCOS 10 worker nodes simultaneously.
- UDN = User Defined Network, a namespace-scoped network that provides isolated connectivity for pods and VMs.
- OVN-K = OVN-Kubernetes, the cluster networking solution that provides pod-to-pod connectivity in OpenShift.
- SR-IOV = Single Root I/O Virtualization, a hardware feature that allows a single physical function to appear as multiple virtual functions.
- common-network-types = primary network (OVN-K overlay), primary UDN, localnet, Linux bridge

### **Feature Overview**
Starting with OCP 4.22, OpenShift Virtualization supports dual-stream clusters running both RHCOS 9 and RHCOS 10 worker nodes simultaneously (dual-stream clusters). **Note:** this STP is specific to the OCP 4.22 release cycle and should be reviewed when RHCOS 9 or RHCOS 10 support changes.
Customers can upgrade their clusters from RHCOS 9 to RHCOS 10 nodes, gradually, without service disruption - live migration must work correctly across node types without network interruption.

This STP covers the network-specific aspects of the feature: validating live migration across node types for all common-network-types, and ensuring all existing network functionality works correctly on an RHCOS 10 cluster.

---

### **I. Motivation and Requirements Review (QE Review Guidelines)**

#### **1. Requirement & User Story Review Checklist**


- [x] **Review Requirements**
  - *List the key D/S requirements reviewed:* See Acceptance Criteria and Testing Goals (Sections I.1 and II.1).

- [x] **Understand Value and Customer Use Cases**
  - *Describe the feature's value to customers:* Customers can upgrade their clusters from RHCOS 9 to RHCOS 10 nodes, gradually, without service disruption, maintaining VM network connectivity and live migration capability throughout the transition.
  - *List the customer use cases identified:*
    - As a cluster admin, I want to upgrade my cluster gradually by adding new nodes that support only RHCOS 10; due to node replacements and additions, VMs may live migrate as part of that process without workload disruption.
    - As a cluster admin, I want all existing VM network features (including live migration for node maintenance or load balancing) to work on an RHCOS 10 cluster so that I can complete my cluster upgrade without losing functionality.

- [x] **Testability**
  - *Note any requirements that are unclear or untestable:* The use cases are testable through existing coverage and the additional tests to cover dual-stream migration scenarios.

- [x] **Acceptance Criteria**
  - *List the acceptance criteria:*
    - VM live migration completes without network disruption in both directions (RHCOS 9 ↔ RHCOS 10), across all common-network-types.
    - All Tier 2 network tests pass on an RHCOS 10 cluster
  - *Note any gaps or missing criteria:* None

- [x] **Non-Functional Requirements (NFRs)**
  - *List applicable NFRs and their targets:* None — no new non-functional requirements introduced by this feature.
  - *Note any NFRs not covered and why:*
    - Performance: no new performance requirements introduced.
    - Security: no new auth changes.
    - Monitoring/Observability: no new network metrics or alerts required.
    - Scalability: no new scale requirements for network functionality.
    - UI/Docs: existing user-facing network functionality is preserved; no UI or documentation updates are needed to express support for a dual-stream cluster.


#### **2. Known Limitations**

- **Testing is limited to RHCOS-based worker nodes.** Control plane and infrastructure nodes are out of scope — VMs are not scheduled or migrated on those nodes.
  - *Sign-off:* Ronen Sde-Or, 04/2026


#### **3. Technology and Design Review**

- [x] **Developer Handoff/QE Kickoff**
  - *Key takeaways and concerns:* See Testing Goals (Section II.1) and Test Strategy (Section II.2).

- [x] **Technology Challenges**
  - *List identified challenges:* Mixed RHCOS 9 and RHCOS 10 kernel versions may affect network functionality and interoperability with user-space binaries, potentially behaving differently per node.
  - *Impact on testing approach:* Tests must explicitly validate live migration for each common-network-type to detect kernel-related incompatibilities (see Section II.3).

- [x] **API Extensions**
  - *List new or modified APIs:* No new APIs required for this feature.
  - *Testing impact:* N/A

- [x] **Test Environment Needs**
  - *See environment requirements in Section II.3 and testing tools in Section II.3.1*

- [x] **Topology Considerations**
  - *Describe topology requirements:* See Section II.3 - Test Environment.
  - *Impact on test design:* Adding migration tests between RHCOS 9 and RHCOS 10 nodes covering VMs with multiple network setups.

### **II. Software Test Plan (STP)**

#### **1. Scope of Testing**

**Testing Goals**

- **[P0]** Verify VM live migration completes without network disruption from an RHCOS 9 node to an RHCOS 10 node and back, across all common-network-types.
- **[P1]** Validate that all existing network features work correctly for VMs running on an RHCOS 10 cluster.

**Out of Scope (Testing Scope Exclusions)**

- **Non-RHCOS worker node variants**
  - *Rationale:* This feature targets RHCOS-based nodes only; non-RHCOS worker variants are out of scope for this release.
  - *PM/Lead Agreement:* Ronen Sde-Or, 04/2026

- **SR-IOV cross-version migration**
  - *Rationale:* SR-IOV involves physical NIC passthrough, which is hardware-level functionality not affected by RHCOS kernel version differences. Running a dedicated CI lane for this single scenario is not justified given the limited benefit.
  - *PM/Lead Agreement:* Ronen Sde-Or, 04/2026

**Test Limitations**

- **Full Tier 2 network regression is not run against the dual-stream cluster.** Running a full regression there would not guarantee that all live migrations cross between RHCOS 9 and RHCOS 10 nodes — enforcing this constraint across all scenarios would be too complex. Instead, targeted migration tests explicitly validate cross-version migrations for each common-network-type.
  - *Sign-off:* Ronen Sde-Or, 04/2026


#### **2. Test Strategy**

**Functional**

- [x] **Functional Testing** — Validates that the feature works according to specified requirements and user stories
  - *Details:* Validate VM live migration on a dual-stream cluster across all common-network-types.

- [x] **Automation Testing** — Confirms test automation plan is in place for CI and regression coverage (all tests are expected to be automated)
  - *Details:* All new migration tests will be automated and run in dedicated CI lanes (see Section II.3.1).

- [x] **Regression Testing** — Verifies that new changes do not break existing functionality
  - *Details:* Regression is covered by running existing Tier 2 network tests on the RHCOS 10 cluster; the dual-stream cluster is reserved for targeted migration tests only (see Section II.3.1).

**Non-Functional**

- [ ] **Performance Testing** — Validates feature performance meets requirements (latency, throughput, resource usage)
  - *Details:* From a network perspective, no dedicated performance testing is required. Potential performance implications of running a dual-stream cluster (e.g., migration timing, network throughput differences between RHCOS 9 and RHCOS 10) should be covered by the parent STP.

- [ ] **Scale Testing** — Validates feature behavior under increased load and at production-like scale
  - *Details:* From a network perspective, no dedicated scale testing is required. Scale implications of running a dual-stream cluster should be covered by the parent STP.

- [ ] **Security Testing** — Verifies security requirements, RBAC, authentication, authorization
  - *Details:* From a network perspective, no dedicated security testing is required. Security implications in a dual-stream cluster should be covered by the parent STP.

- [ ] **Usability Testing** — Validates user experience and accessibility requirements
  - *Details:* From a network perspective, no UI or CLI changes are introduced; existing user-facing network functionality is preserved.

- [ ] **Monitoring** — Does the feature require metrics and/or alerts?
  - *Details:* From a network perspective, no new metrics or alerts are required. Node version exposure and cluster-level observability should be covered by the parent STP.

**Integration & Compatibility**

- [ ] **Compatibility Testing** — Ensures feature works across supported platforms, versions, and configurations
  - *Details:* Not applicable for this STP.

- [ ] **Upgrade Testing** — Validates upgrade paths from previous versions
  - *Details:* The upgrade scenario is already simulated by the dual-stream cluster migration tests; no additional upgrade-specific network tests are needed.

- [x] **Dependencies** — Blocked by deliverables from other components/products.
  - *Details:* Dedicated CI lanes must be provisioned by QE DevOps before testing can begin (see Section II.4 - Entry Criteria).

- [ ] **Cross Integrations** — Does the feature affect other features or require testing by other teams?
  - *Details:* This STP covers the network scope only; cross-integration testing is covered by the parent STP.

**Infrastructure**

- [ ] **Cloud Testing** — Does the feature require multi-cloud platform testing?
  - *Details:* Not applicable; this feature targets bare-metal RHCOS nodes only.


#### **3. Test Environment**

- **Cluster Topology:**
  - Dual-stream cluster with at least one RHCOS 9 and one RHCOS 10 worker node — for migration scenarios
  - RHCOS 10 cluster: for Tier 2 network regression

- **OCP & OpenShift Virtualization Version(s):** OCP 4.22 with OpenShift Virtualization 4.22

- **CPU Virtualization:** VT-x (Intel) or AMD-V enabled

- **Compute Resources:** Minimum per worker node: 8 vCPUs, 32GB RAM

- **Special Hardware:** N/A

- **Storage:** ocs-storagecluster-ceph-rbd-virtualization

- **Network:** Standard — no special network configuration needed beyond the standard test environment.

- **Required Operators:** No new operators

- **Platform:** Bare metal

- **Special Configurations:** N/A


#### **3.1. Testing Tools & Frameworks**

- **Test Framework:** Standard. Tests require logic to identify nodes by RHCOS version, pin VMs to specific nodes before migration, and verify that migration crosses between RHCOS 9 and RHCOS 10 nodes.

- **CI/CD:** Two dedicated lanes required — one per cluster topology (see Cluster Topology above).

- **Other Tools:** N/A


#### **4. Entry Criteria**

The following conditions must be met before testing can begin:

- [x] Requirements and design documents are **approved and merged**
- [x] Test environment can be **set up and configured** (see Section II.3 - Test Environment)
- [x] Dedicated dual-stream cluster CI lane is provisioned and operational
- [x] Dedicated RHCOS 10 cluster CI lane for Tier 2 network regression is provisioned and operational


#### **5. Risks**

**Timeline/Schedule**

- **Risk:** Main STP is not ready
  - **Mitigation:** Focus on network aspect of the requested feature
  - *Estimated impact on schedule:* N/A
  - *Sign-off:* Martin Tessun, 04/2026


**Test Coverage**

- **Risk:** None.
  - **Mitigation:** All relevant common-network-types are explicitly tested with cross-version migrations on the dual-stream cluster; full Tier 2 regression is not required there as it would not provide additional value for cross-version migration validation.
  - *Areas with reduced coverage:* None

**Test Environment**

- **Risk:** None.
  - **Mitigation:** Dedicated CI lanes can be provisioned on demand by QE DevOps.
  - *Missing resources or infrastructure:* None

**Untestable Aspects**

- **Risk:** None.
  - **Mitigation:** All components are testable
  - *Alternative validation approach:* N/A

**Resource Constraints**

- **Risk:** No special resource requirements.
  - **Mitigation:** N/A
  - *Current capacity gaps:* None


**Dependencies**

- **Risk:** The main STP has not been started yet, which may leave gaps in overall test coverage alignment.
  - **Mitigation:** Proceed with the network-scoped STP independently; sync once the main STP is available to identify and resolve any overlaps or gaps.
  - *Dependent teams or components:* Virt team (main STP owner)
  - *Sign-off:* Martin Tessun, 04/2026

---


### **III. Test Scenarios & Traceability**

- **[CNV-77027]** — As a cluster admin, I want VMs using the primary network to live migrate without network disruption between RHCOS 9 and RHCOS 10 nodes on a dual-stream cluster.
  - *Test Scenario:* [Tier 2] Verify VM with the primary network live migrates between RHCOS 9 and RHCOS 10 nodes (in both directions) without connectivity loss.
  - *Priority:* P0

- **[CNV-77027]** — As a cluster admin, I want VMs using primary UDN to live migrate across RHCOS 9 and RHCOS 10 nodes without network disruption.
  - *Test Scenario:* [Tier 2] Verify VM with primary UDN live migrates between RHCOS 9 and RHCOS 10 nodes (in both directions) without connectivity loss.
  - *Priority:* P0

- **[CNV-77027]** — As a cluster admin, I want VMs using localnet to live migrate across RHCOS 9 and RHCOS 10 nodes without network disruption.
  - *Test Scenario:* [Tier 2] Verify VM with localnet network live migrates between RHCOS 9 and RHCOS 10 nodes (in both directions) without connectivity loss.
  - *Priority:* P0


- **[CNV-77027]** — As a cluster admin, I want VMs using Linux bridge to live migrate across RHCOS 9 and RHCOS 10 nodes without network disruption.
  - *Test Scenario:* [Tier 2] Verify VM with Linux bridge live migrates between RHCOS 9 and RHCOS 10 nodes (in both directions) without connectivity loss.
  - *Priority:* P0

---

### **IV. Sign-off and Approval**

This Software Test Plan requires approval from the following stakeholders:

* **Reviewers:**
  - QE Architect: Ruth Netser (@rnetser)
  - Developers: Ananya Banerjee (@frenzyfriday), Nir Dothan (@nirdothan), Orel Misan (@orelmisan)
* **Approvers:**
  - QE Architect: Ruth Netser (@rnetser)
  - Principal Developer: Edward Haas (@EdDev)
  - Product Manager/Owner: Ronen Sde-Or (@ronensdeor)
