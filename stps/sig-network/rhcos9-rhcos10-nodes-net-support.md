# Openshift-virtualization-tests Test plan

## **[RHCOS9 and RHCOS10 Worker Nodes Support] - Quality Engineering Plan**

### **Metadata & Tracking**

- **Enhancement(s):** -
- **Feature Tracking:** https://redhat.atlassian.net/browse/VIRTSTRAT-83
- **Epic Tracking:** https://redhat.atlassian.net/browse/CNV-77027
- **QE Owner(s):** Asia Khromov
- **Owning SIG:** sig-virt
- **Participating SIGs:** All sigs

**Document Conventions (if applicable):**
RHCOS = Red Hat CoreOS, the immutable container-optimized OS used for OpenShift worker nodes
UDN = User Defined Network, a CRD used to define a UDN, at the project level
SR-IOV = Single Root I/O Virtualization, a hardware feature that allows a single physical function to appear as multiple virtual functions
OVN-K = OVN-Kubernetes, the default CNI network provider


### **Feature Overview**

Starting with OCP 4.22, OpenShift Virtualization must support heterogeneous clusters running both RHCOS 9 (el9, RHEL 9 kernel) and RHCOS 10 (el10, RHEL 10 kernel) worker nodes simultaneously - referred to as dual-stream clusters.
From a network perspective, the critical requirement is that VM live migration works correctly across node types without network disruption.
Network testing must explicitly validate migration scenarios on a mixed-node cluster, in addition to ensuring existing Tier 2 network coverage runs cleanly against RHCOS 10-only clusters.

---

### **I. Motivation and Requirements Review (QE Review Guidelines)**

#### **1. Requirement & User Story Review Checklist**


- [x] **Review Requirements**
  - *List the key D/S requirements reviewed:* VM live migration must work without network disruption in both directions on a mixed-node (RHEL 9 + RHEL 10) cluster, and overall network functionality must work on an all-RHEL 10 cluster.

- [x] **Understand Value and Customer Use Cases**
  - *Describe the feature's value to customers:* Customers can migrate their clusters from RHEL 9 to RHEL 10 nodes without service disruption, maintaining VM network connectivity and live migration capability throughout the transition.
  - *List the customer use cases identified:*
    - Live migrate a VM from an RHEL 9 node to an RHEL 10 node and back
    - Run a fully RHEL 10-only cluster with all existing network features functioning as expected

- [x] **Testability**
  - *Note any requirements that are unclear or untestable:* The use cases are testable through existing coverage and the additional tests to cover mixed-node migration scenarios.

- [x] **Acceptance Criteria**
  - *List the acceptance criteria:*
    - VM live migration completes without network disruption
    - All Tier 2 network tests pass on an all-RHEL 10 cluster

- [x] **Non-Functional Requirements (NFRs)**
  - *List applicable NFRs and their targets:* Coverage: Tier 2 network tests pass on RHCOS 10 nodes cluster
  - *Note any NFRs not covered and why:* To be reviewed in the main STP


#### **2. Known Limitations**

- Testing is limited to RHCOS-based worker nodes.
- Only a targeted subset of network tests covers the heterogeneous (mixed-node) cluster; full Tier 2 network coverage is not run against the dual-stream topology.


#### **3. Technology and Design Review**

- [x] **Developer Handoff/QE Kickoff**
  - *Key takeaways and concerns:* Performed through meetings and design review.

- [x] **Technology Challenges**
  - *List identified challenges:* Heterogeneous (mixed RHCOS 9 + RHCOS 10) cluster infrastructure must be provisioned and maintained; dedicated CI lanes are required to run tests against this topology.
  - *Impact on testing approach:* Without a dedicated lane providing the mixed-node cluster, migration scenarios between RHEL 9 and RHEL 10 nodes cannot be validated in CI.

- [x] **API Extensions**
  - *List new or modified APIs:* No new APIs required for this feature.
  - *Testing impact:* N/A

- [x] **Test Environment Needs**
  - *See environment requirements in Section II.3 and testing tools in Section II.3.1*

- [x] **Topology Considerations**
  - *Describe topology requirements:* Heterogeneous (mixed RHCOS 9 + RHCOS 10) cluster infrastructure.
  - *Impact on test design:* Adding migration tests between RHEL 9.8 and RHEL 10.2 nodes covering VMs with multiple network setups.

### **II. Software Test Plan (STP)**

#### **1. Scope of Testing**

**Testing Goals**

- **[P0]** Verify VM live migration completes without network disruption from an RHEL 9 node to an RHEL 10 node and back, across multiple network setups.
- **[P1]** Validate that all Tier 2 network tests pass on an all-RHEL 10 cluster.

**Out of Scope (Testing Scope Exclusions)**

To be reviewed in the main STP


#### **2. Test Strategy**

**Functional**

- [x] **Functional Testing** — Validates that the feature works according to specified requirements and user stories

- [x] **Automation Testing** — Confirms test automation plan is in place for CI and regression coverage (all tests are expected to be automated)
  - *Details:* New migration tests between RHEL 9 and RHEL 10 nodes will be automated and run in a dedicated CI lane against the mixed-node cluster; Tier 2 network tests will be run in an all-RHEL 10 cluster lane.

- [x] **Regression Testing** — Verifies that new changes do not break existing functionality
  - *Details:* Regression is covered by running existing Tier 2 network tests on an all-RHEL 10 cluster; regression is not planned on the mixed-node cluster, which is reserved for the targeted migration tests only.

**Non-Functional**

As this STP refers to network aspect of the feature, all non-functional aspects to be reviewed by the main STP for this feature.

**Integration & Compatibility**

Integration and compatibility testing is deferred to the main STP for this feature.

**Infrastructure**

Infrastructure testing is deferred to the main STP for this feature.


#### **3. Test Environment**

- **Cluster Topology:**
  - Mixed RHCOS 9 + RHCOS 10 worker-node cluster (for migration scenarios)
  - All-RHCOS 10 worker-node cluster (for Tier 2 network regression)

- **OCP & OpenShift Virtualization Version(s):** OCP 4.22 with OpenShift Virtualization 4.22

- **CPU Virtualization:** Agnostic

- **Compute Resources:** Agnostic

- **Special Hardware:** Agnostic

- **Storage:** Agnostic

- **Network:** OVN-K, Primary UDN, localnet, SR-IOV

- **Required Operators:** No new operators

- **Platform:** Agnostic

- **Special Configurations:** N/A


#### **3.1. Testing Tools & Frameworks**

- **Test Framework:** Standard

- **CI/CD:** Dedicated lane with heterogeneous cluster to run the required network tests

- **Other Tools:** N/A


#### **4. Entry Criteria**

The following conditions must be met before testing can begin:

- [x] Requirements and design documents are **approved and merged**
- [x] Test environment can be **set up and configured** (see Section II.3 - Test Environment)


#### **5. Risks**

**Timeline/Schedule**

- [x] **Risk:** Main STP is not ready
  - **Mitigation:** Focus on network aspect of the requested feature
  - *Estimated impact on schedule:* N/A

**Test Coverage**

- [x] **Risk:** Not testing Tier2 network tests on heterogeneous cluster.
  - **Mitigation:** Running regression on RHCOS10 cluster + dedicated tests on heterogeneous cluster provides sufficient coverage
  - *Areas with reduced coverage:*

**Test Environment**

- [x] **Risk:** Dedicated all-RHCOS 10 cluster for network Tier 2 regression is not yet available.
  - **Mitigation:** Coordinate with QE DevOps to provision a dedicated all-RHEL 10 cluster for network Tier 2 regression.
  - *Missing resources or infrastructure:* No RHCOS10 clusters available for network Tier2 regression.

**Untestable Aspects**

- [x] **Risk:** All components are testable


**Resource Constraints**

- [x] **Risk:** No special resource requirements


**Dependencies**

- [x] **Risk:** The main STP has not been started yet, which may leave gaps in overall test coverage alignment.
  - **Mitigation:** Proceed with the network-scoped STP independently; sync once the main STP is available to identify and resolve any overlaps or gaps.
  - *Dependent teams or components:* Virt team (main STP owner)

---


### **III. Test Scenarios & Traceability**

- **[CNV-77027]** — As a cluster admin, I want VMs to live migrate without network disruption between RHEL 9 and RHEL 10 nodes on a mixed-node cluster.
  - *Test Scenario:* [Tier 2] Verify VM with default pod network live migrates between RHEL 9 and RHEL 10 nodes (in both directions) without connectivity loss.
  - *Priority:* P0

- **[CNV-77027]** — As a cluster admin, I want VMs using primary UDN to live migrate across RHEL 9 and RHEL 10 nodes without network disruption.
  - *Test Scenario:* [Tier 2] Verify VM with primary UDN live migrates between RHEL 9 and RHEL 10 nodes (in both directions) without connectivity loss.
  - *Priority:* P0

- **[CNV-77027]** — As a cluster admin, I want VMs using localnet to live migrate across RHEL 9 and RHEL 10 nodes without network disruption.
  - *Test Scenario:* [Tier 2] Verify VM with localnet network live migrates between RHEL 9 and RHEL 10 nodes (in both directions) without connectivity loss.
  - *Priority:* P0

- **[CNV-77027]** — As a cluster admin, I want VMs using SR-IOV to live migrate across RHEL 9 and RHEL 10 nodes without network disruption.
  - *Test Scenario:* [Tier 2] Verify VM with SR-IOV network live migrates between RHEL 9 and RHEL 10 nodes (in both directions) without connectivity loss.
  - *Priority:* P0

- **[CNV-77027]** — As a cluster admin, I want VMs using passt binding to live migrate across RHEL 9 and RHEL 10 nodes without network disruption.
  - *Test Scenario:* [Tier 2] Verify VM with passt binding live migrates between RHEL 9 and RHEL 10 nodes (in both directions) without connectivity loss.
  - *Priority:* P0

- **[CNV-77027]** — As a cluster admin, I want VMs using Linux bridge to live migrate across RHEL 9 and RHEL 10 nodes without network disruption.
  - *Test Scenario:* [Tier 2] Verify VM with Linux bridge live migrates between RHEL 9 and RHEL 10 nodes (in both directions) without connectivity loss.
  - *Priority:* P0

---

### **IV. Sign-off and Approval**

This Software Test Plan requires approval from the following stakeholders:

* **Reviewers:**
  - QE Architect: Ruth Netser
  - Developers: Ananya Banerjee, Nir Dothan, Orel Misan
* **Approvers:**
  - QE Architect: Ruth Netser
  - Principal Developer: Edward Haas
