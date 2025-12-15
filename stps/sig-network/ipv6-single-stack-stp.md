# Openshift-virtualization-tests Test plan

## **IPv6 single stack - Quality Engineering Plan**

### **Metadata & Tracking**

| Field                  | Details                                    |
|:-----------------------|:-------------------------------------------|
| **Enhancement(s)**     | -                                          |
| **Feature in Jira**    | https://issues.redhat.com/browse/CNV-28924 |
| **Jira Tracking**      | https://issues.redhat.com/browse/CNV-72402 |
| **QE Owner(s)**        | Asia Khromov (azhivovk@redhat.com)         |
| **Owning SIG**         | sig-network                                |
| **Participating SIGs** | sig-network                                |
| **Current Status**     | Draft                                      |

**Document Conventions:**
- IPv6 = Internet Protocol version 6
- VMI = Virtual Machine Instance
- SR-IOV = Single Root I/O Virtualization
- KMP = Kubemacpool
- CUDN/UDN = User Defined Network, A CRD used to define a UDN, at the cluster level (CUDN) or project level (UDN)
- BGP = Border Gateway Protocol
- MTV = Migration Toolkit for Virtualization


### **Feature Overview**
OpenShift Virtualization functionality on IPv6 single-stack clusters.
During feature verification, we ensure that core networking, storage,
and virtualization workflows function correctly without relying on IPv4.
The testing effort focuses on adapting existing test coverage to run in IPv6-only
environments, including network configuration, service exposure, and VM connectivity.
This work is critical for customers deploying OpenShift Virtualization in IPv6-mandated
infrastructures and ensures readiness for GA without impacting cluster topology or architecture.

### **I. Motivation and Requirements Review (QE Review Guidelines)**

#### **1. Requirement & User Story Review Checklist**

| Check                                  | Done | Details/Notes                                                                                                                     | Comments |
|:---------------------------------------|:-----|:----------------------------------------------------------------------------------------------------------------------------------|:---------|
| **Review Requirements**                | [x]  | Ensure that core networking, storage, and virtualization workflows function correctly without relying on IPv4                     |          |
| **Understand Value**                   | [x]  | Customers should be able to use IPv6 single-stack clusters with full CNV functionality                                            |          |
| **Customer Use Cases**                 | [x]  | Customers deploying CNV in IPv6-mandated infrastructures require full virtualization capabilities without IPv4 dependency         |          |
| **Testability**                        | [x]  | The use cases are testable through existing coverage of dependent features                                                        |          |
| **Acceptance Criteria**                | [x]  | All CNV networking, storage, and virtualization features function correctly on IPv6 single-stack clusters without IPv4 dependency |          |
| **Non-Functional Requirements (NFRs)** | [x]  | UI, metrics and documentation are required                                                                                        |          |


#### **2. Technology and Design Review**

| Check                            | Done  | Details/Notes                                                                                                                                           | Comments                                                                                                                        |
|:---------------------------------|:------|:--------------------------------------------------------------------------------------------------------------------------------------------------------|:--------------------------------------------------------------------------------------------------------------------------------|
| **Developer Handoff/QE Kickoff** | [x]   | A meeting where Dev/Arch walked QE through the design, architecture, and implementation details. **Critical for identifying untestable aspects early.** |                                                                                                                                 |
| **Technology Challenges**        | [x]   | Identified potential testing challenges related to the underlying technology.                                                                           | Adjusting existing tests to IPv6                                                                                                |
| **Test Environment Needs**       | [x]   | Determined necessary **test environment setups and tools**.                                                                                             | IPv6 single-stack clusters                                                                                                      |
| **API Extensions**               | [N/A] | Reviewed new or modified APIs and their impact on testing.                                                                                              |                                                                                                                                 |
| **Topology Considerations**      | [x]   | Evaluated multi-cluster, network topology, and architectural impacts.                                                                                   | Changes are limited to test coverage updates; no architectural or multi-cluster topology impact.                                |


### **II. Software Test Plan (STP)**

#### **1. Scope of Testing**
Ensure existing covered functionality for OpenShift Virtualization is preserved when it is deployed on an
IPv6 single-stack cluster. The focus is on the main functionalities of the product, covering network, virt
and storage domains.

**Testing Goals:**
Ensuring all existing functionality works correctly with IPv6-only configurations with a focus on:
- [P0] IPv6 VM connectivity
- [P0] L2 bridge connectivity
- [P0] VM migration coverage
- [P0] SR-IOV
- [P0] Virt Tier2 gating
- [P0] Storage Tier2 gating
- [P1] Flatoverlay
- [P1] Jumbo frames
- [P1] CNV upgrade
- [P1] Network policies
- [P1] Network services
- [P1] Localnet
- [P1] UDN
- [P1] CUDN
- [P1] BGP
- [P1] MTV import
- [P1] Service mesh

**Out of Scope (Testing Scope Exclusions)**

| Out-of-Scope Item | Rationale                                                          | PM/ Lead Agreement       |
|:------------------|:-------------------------------------------------------------------|:-------------------------|
| Cloud testing     | IPv6 single-stack configuration is not available on cloud clusters | [x] Ronen Sde-Or 01/2026 |


#### **2. Test Strategy**

| Item (Testing Type)            | Applicable (Y/N or N/A) | Comments                                                       |
|:-------------------------------|:------------------------|:---------------------------------------------------------------|
| Functional Testing             | Y                       |                                                                |
| Automation Testing             | Y                       |                                                                |
| Performance Testing            | N                       |                                                                |
| Security Testing               | N                       |                                                                |
| Usability Testing              | Y                       |                                                                |
| Compatibility Testing          | N                       |                                                                |
| Regression Testing             | Y                       |                                                                |
| Upgrade Testing                | Y                       |                                                                |
| Backward Compatibility Testing | N                       | New feature                                                    |
| Dependencies                   | N                       |                                                                |
| Monitoring                     | Y                       |                                                                |
| Cross Integrations             | N                       |                                                                |
| Cloud Testing                  | N/A                     | No cloud configuration for IPv6 single-stack on cloud clusters |


#### **3. Test Environment**

| Environment Component                         | Configuration                              | Specification Examples |
|:----------------------------------------------|:-------------------------------------------|:-----------------------|
| **Cluster Topology**                          | Bare-Metal                                 |                        |
| **OCP & OpenShift Virtualization Version(s)** | 4.21                                       |                        |
| **CPU Virtualization**                        | Default                                    |                        |
| **Compute Resources**                         | Not required                               |                        |
| **Special Hardware**                          | Not required                               |                        |
| **Storage**                                   | Default                                    |                        |
| **Network**                                   | IPv6 single-stack, Multi NIC, VLAN, SR-IOV |                        |
| **Required Operators**                        | CNV, NMState, MTV, Istio                   |                        |
| **Platform**                                  | Bare-metal                                 |                        |
| **Special Configurations**                    | IPv6 single-stack cluster                  | IPv6 proxy             |


#### **3.1. Testing Tools & Frameworks**

| Category           | Tools/Frameworks                                       |
|:-------------------|:-------------------------------------------------------|
| **Test Framework** |                                                        |
| **CI/CD**          | Dedicated IPv6 Single-Stack lanes with special markers |
| **Other Tools**    |                                                        |


#### **4. Entry Criteria**

The following conditions must be met before testing can begin:

- [x] Requirements and design documents are **approved and merged**
- [x] Test environment can be **set up and configured** (see Section 3 - Test Environment)
- [in-progress] Appropriate setup for IPv6: Assigning addresses to primary interface


#### **5. Risks**

| Risk Category        | Specific Risk for This Feature                                                                                     | Mitigation Strategy                                                                  | Status        |
|:---------------------|:-------------------------------------------------------------------------------------------------------------------|:-------------------------------------------------------------------------------------|:--------------|
| Timeline/Schedule    | Many adjustments are required for all network tests and it would take time to merge them                           | Splitting to small tasks and get an exception for merging more necessary adjustments | [in-progress] |
| Test Coverage        | Missing coverage for IPv6                                                                                          | Adjusting existing automation tests to IPv6                                          | [in-progress] |
| Test Environment     | Bare-metal IPv6 single-stack clusters                                                                              | Most of the customers use bare-metal clusters                                        | [x]           |
| Untestable Aspects   | Cloud IPv6 single-stack cluster                                                                                    | Unavailable configuration, not covered                                               | [x]           |
| Resource Constraints | N/A - Team capacity sufficient; IPv6 test execution fits within existing CI infrastructure                         |                                                                                      | [x]           |
| Dependencies         | N/A - All required operators (CNV, NMState, MTV) are stable; no external cross-team blockers identified            |                                                                                      | [x]           |
| Other                | Other sigs don't own IPv6 single-stack lane and we need to provide the infrastructure for enabling ssh to guest vm | Provide network adjustments to enable ssh and create IPv6 lanes for other sigs       | [in-progress] |


#### **6. Known Limitations**

- IPv6 single-stack configuration is not available on cloud clusters


### **III. Test Scenarios & Traceability**

| Requirement ID   | Requirement Summary                                                                                           | Test Scenario(s)                                                                                                                                                                                                                                                                           | Tier   | Priority |
|:-----------------|:--------------------------------------------------------------------------------------------------------------|:-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:-------|:---------|
| CNV-28924 (epic) | As an admin, I can establish basic IPv6 connectivity for VMs on IPv6 single-stack cluster                     | 1) Verify pod network connectivity preserves<br/>2) Pod network connectivity preserves in L2 bridge presence                                                                                                                                                                               | Tier 2 | P0       |
|                  | As an admin, I can create L2 bridge on VMs and have IPv6 connectivity                                         | 1) Verify basic connectivity over L2 bridges preserves                                                                                                                                                                                                                                     | Tier 2 | P0       |
|                  | As an admin, I can live-migrate a VM on IPv6 single-stack cluster                                             | 1) Verify masquerade connectivity preserves after migration<br/>2) Verify HTTP service preserves post migration                                                                                                                                                                            | Tier 2 | P0       |
|                  | As an admin, I can configure SR-IOV networking on VMs in IPv6 single-stack cluster                            | 1) Verify basic sriov network connectivity preserves<br/>2) Verify custom MTU connectivity preserves<br/>3) Verify basic vlan connectivity preserves<br/>4) Verify sriov network no connectivity no vlan to vlan<br/>5) Verify sriov interfaces present post reboot<br/>6) sriov migration | Tier 2 | P0       |
|                  | As an admin, I can create IPv6 services for VMs on IPv6 single-stack cluster                                  | 1) Verify single-stack service created via manifest<br/>2) Verify default ip family single-stack service created via manifest<br/>3) Verify single-stack service created via virtctl                                                                                                       | Tier 2 | P1       |
|                  | As an admin, I can apply network policies to VMs on IPv6 single-stack cluster                                 | 1) Verify network policy allows all http<br/>2) Verify network policy allows http on single port<br/>3) Verify network policy denies all http                                                                                                                                              | Tier 2 | P1       |

---

### **IV. Sign-off and Approval**

This Software Test Plan requires approval from the following stakeholders:

* **Reviewers:**
  - QE Architect: Ruth Netser
  - QE Members: Yossi Segev, Anat Wax, Sergei Volkov
* **Approvers:**
  - QE Architect: Ruth Netser
  - Product Manager/Owner: Ronen Sde-Or, Petr Horacek
  - Principal Developer: Edward Haas
