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
- STP = Software Test Plan
- SR-IOV = Single Root I/O Virtualization
- KMP = Kubemacpool
- UDN = User Defined Network
- CUDN = Cluster User Defined Network
- BGP = Border Gateway Protocol
---

#### **1. Requirement & User Story Review Checklist**

| Check                                  | Done | Details/Notes                                                                                                                                                                           | Comments |
|:---------------------------------------|:-----|:----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:---------|
| **Review Requirements**                | [V]  | Reviewed the relevant requirements.                                                                                                                                                     |          |
| **Understand Value**                   | [V]  | Confirmed clear user stories and understood.  <br/>Understand the difference between U/S and D/S requirements<br/> **What is the value of the feature for RH customers**.               |          |
| **Customer Use Cases**                 | [V]  | Ensured requirements contain relevant **customer use cases**.                                                                                                                           |          |
| **Testability**                        | [V]  | Confirmed requirements are **testable and unambiguous**.                                                                                                                                |          |
| **Acceptance Criteria**                | [V]  | Ensured acceptance criteria are **defined clearly** (clear user stories; D/S requirements clearly defined in Jira).                                                                     |          |
| **Non-Functional Requirements (NFRs)** | [V]  | Confirmed coverage for NFRs, including Performance, Security, Usability, Downtime, Connectivity, Monitoring (alerts/metrics), Scalability, Portability (e.g., cloud support), and Docs. |          |


#### **2. Technology and Design Review**

| Check                            | Done | Details/Notes                                                                                                                                           | Comments                         |
|:---------------------------------|:-----|:--------------------------------------------------------------------------------------------------------------------------------------------------------|:---------------------------------|
| **Developer Handoff/QE Kickoff** | [ ]  | A meeting where Dev/Arch walked QE through the design, architecture, and implementation details. **Critical for identifying untestable aspects early.** | Done a while ago                 |
| **Technology Challenges**        | [V]  | Identified potential testing challenges related to the underlying technology.                                                                           | Adjusting existing tests to IPv6 |
| **Test Environment Needs**       | [V]  | Determined necessary **test environment setups and tools**.                                                                                             | IPv6 single-stack clusters       |
| **API Extensions**               | [V]  | Reviewed new or modified APIs and their impact on testing.                                                                                              |                                  |
| **Topology Considerations**      | [V]  | Evaluated multi-cluster, network topology, and architectural impacts.                                                                                   |                                  |


### **II. Software Test Plan (STP)**

#### **1. Scope of Testing**
The scope of testing for this plan is focused on IPv6 single-stack networking scenarios in OpenShift clusters,
ensuring that networking functionality works correctly when only IPv6 is configured.
This includes both functional and non-functional aspects relevant to IPv6 connectivity, services,
and pod-to-pod communication.

**In Scope:**
Ensuring all the following work and function correctly with IPv6-only configurations:
- Correct IPv6 address assignment on pods, VMs, services, and network attachments
- Ensuring Linux and OVS bridges functions
- Ensuring SR-IOV functions
- Testing IPv6 VM/Pod connectivity both on primary pod network and secondary interfaces
- Validating IPv6 network continuity following live migration
- Network policies behavior
- Services behavior
- CNV pre/post upgrade
- Bond function

**Out of Scope (Testing Scope Exclusions)**

| Out-of-Scope Item       | Rationale                                              | PM/ Lead Agreement |
|:------------------------|:-------------------------------------------------------|:-------------------|
| Service Mesh            | Limited support in single-stack IPv6 clusters          | [ ] Name/Date      |
| KMP                     | Covered in IPv4 tests                                  | [ ] Name/Date      |
| Jumbo frames            | Special infra is excluded                              | [ ] Name/Date      |
| CUDN                    | Currently unsupported, will be adjusted in a follow-up | [ ] Name/Date      |
| UDN                     | Currently unsupported, will be adjusted in a follow-up | [ ] Name/Date      |
| Flatoverlay             | Currently unsupported, will be adjusted in a follow-up | [ ] Name/Date      |
| BGP                     | -                                                      | [ ] Name/Date      |


#### **2. Testing Goals**

- [ ] Goal 1: Verify IPv6 connectivity across life-span of guest
- [ ] Goal 2: Consider new test cases


#### **3. Test Strategy**

| Item (Testing Type)            | Applicable (Y/N or N/A)   | Comments                                                                                                                                                                                                  |
|:-------------------------------|:--------------------------|:----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Functional Testing             | Y                         |                                                                                                                                                                                                           |
| Automation Testing             | Y                         |                                                                                                                                                                                                           |
| Performance Testing            | N                         |                                                                                                                                                                                                           |
| Security Testing               | N                         |                                                                                                                                                                                                           |
| Usability Testing              | N                         |                                                                                                                                                                                                           |
| Compatibility Testing          | N                         |                                                                                                                                                                                                           |
| Regression Testing             | Y                         |                                                                                                                                                                                                           |
| Upgrade Testing                | Y                         |                                                                                                                                                                                                           |
| Backward Compatibility Testing | N/A                       |                                                                                                                                                                                                           |
| Dependencies                   | N                         |                                                                                                                                                                                                           |
| Monitoring                     | N                         |                                                                                                                                                                                                           |
| Cross Integrations             | Y                         | Virt and Storage team might run tests on IPv6 <br/>single-stack clusters in the future. <br/>This will require masquerade IPv6 address <br/>configuration of primary inteface to <br/>enable ssh on guest |
| Cloud Testing                  | N/A                       | Supported on bare metal clusters only                                                                                                                                                                     |


#### **4. Test Environment**

| Environment Component                         | Configuration                              | Specification Examples                                                                        |
|:----------------------------------------------|:-------------------------------------------|:----------------------------------------------------------------------------------------------|
| **Cluster Topology**                          | Bare Metal                                 | [e.g., 3-master/3-worker bare-metal, SNO, Compact Cluster, HCP]                               |
| **OCP & OpenShift Virtualization Version(s)** | 4.21                                       | [e.g., OCP 4.20 with OpenShift Virtualization 4.20]                                           |
| **CPU Virtualization**                        | Default                                    | [e.g., Nodes with VT-x (Intel) or AMD-V (AMD) enabled in BIOS]                                |
| **Compute Resources**                         | Not required                               | [e.g., Minimum per worker node: 8 vCPUs, 32GB RAM]                                            |
| **Special Hardware**                          | Not required                               | [e.g., Specific NICs for SR-IOV, GPU etc]                                                     |
| **Storage**                                   | Default                                    | [e.g., Minimum 500GB per node, specific StorageClass(es)]                                     |
| **Network**                                   | IPv6 single-stack, Multi NIC, SR-IOV, VLAN | [e.g., OVN-Kubernetes (default), Secondary Networks, Network Plugins, IPv4, IPv6, dual-stack] |
| **Required Operators**                        | CNV, SR-IOV, NMState                       | [e.g., NMState Operator]                                                                      |
| **Platform**                                  | Bare metal                                 | [e.g., Bare metal, AWS, Azure, GCP etc]                                                       |
| **Special Configurations**                    | IPv6 single-stack cluster                  | [e.g., Disconnected/air-gapped cluster, Proxy environment, FIPS mode enabled]                 |


#### **5.5. Testing Tools & Frameworks**

| Category           | Tools/Frameworks                                                                                                                                |
|:-------------------|:------------------------------------------------------------------------------------------------------------------------------------------------|
| **Test Framework** |                                                                                                                                                 |
| **CI/CD**          | Dedicated IPv6 Single-Stack lane with special markers: -m "ipv6 or (tier2 and network and not special_infra and not ipv4 and not service_mesh)" |
| **Other Tools**    |                                                                                                                                                 |


#### **6. Entry Criteria**

The following conditions must be met before testing can begin:

- [ ] Requirements and design documents are **approved and merged**
- [ ] Test environment can be **set up and configured** (see Section II.5 - Test Environment)
- [ ] Appropriate setup for IPv6: Assigning addresses to primary and secondary interfaces.........


#### **7. Risks and Limitations**

**Note:** Empty "Specific Risk" cells mean this must be filled. "N/A" means explicitly not applicable with justification.

| Risk Category        | Specific Risk for This Feature                                                                                      | Mitigation Strategy | Status |
|:---------------------|:--------------------------------------------------------------------------------------------------------------------|:--------------------|:-------|
| Timeline/Schedule    |                                                                                                                     |                     | [ ]    |
| Test Coverage        |                                                                                                                     |                     | [ ]    |
| Test Environment     |                                                                                                                     |                     | [ ]    |
| Untestable Aspects   |                                                                                                                     |                     | [ ]    |
| Resource Constraints |                                                                                                                     |                     | [ ]    |
| Dependencies         |                                                                                                                     |                     | [ ]    |
| Other                | Other teams don't own IPv6 single-stack lane and we need to provide the infrastructure for enabling ssh to guest vm |                     | [ ]    |


#### **8. Known Limitations**

- N/A


### **III. Test Scenarios & Traceability**

| Requirement ID   | Requirement Summary | Test Scenario(s) | Test Type(s)   | Priority |
|:-----------------|:--------------------|:-----------------|:---------------|:---------|
| CNV-28924 (epic) |                     |                  | Functional, UI |          |
|                  |                     |                  |                |          |
|                  |                     |                  |                |          |
|                  |                     |                  |                |          |

---

### **IV. Sign-off and Approval**

This Software Test Plan requires approval from the following stakeholders:

* **Reviewers:**
  - Openshift Virtualization Network Team
* **Approvers:**
  - Edward Haas: Openshift Virtualization network Principal developer
  - Ruth Netser: Openshift Virtualization tech-lead
  - Petr Horacek: Openshift Virtualization network team lead
