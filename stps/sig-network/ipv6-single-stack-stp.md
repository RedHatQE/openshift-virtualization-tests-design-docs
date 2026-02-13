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
| **Current Status**     | QE Review Complete                         |

**Document Conventions:**
- IPv6 = Internet Protocol version 6
- KMP = Kubemacpool
- CUDN/UDN = User Defined Network, a CRD used to define a UDN, at the cluster level (CUDN) or project level (UDN)
- BGP = Border Gateway Protocol
- MTV = Migration Toolkit for Virtualization
- CCLM = Cross-Cluster Live Migration, a feature enabling VM migration between different clusters


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

| Check                            | Done | Details/Notes                                                                                    | Comments     |
|:---------------------------------|:-----|:-------------------------------------------------------------------------------------------------|:-------------|
| **Developer Handoff/QE Kickoff** | [x]  | Conducted meetings to align on testing strategy                                                  |              |
| **Technology Challenges**        | [x]  | Deployment of IPv6 clusters and adjusting existing tests to IPv6                                 |              |
| **Test Environment Needs**       | [x]  | IPv6 single-stack clusters                                                                       |              |
| **API Extensions**               | [x]  | No new IPv6 related APIs, IPv6 is already available through the existing API                     |              |
| **Topology Considerations**      | [x]  | Changes are limited to test coverage updates; no architectural or multi-cluster topology impact  |              |


### **II. Software Test Plan (STP)**

#### **1. Scope of Testing**
Ensure existing covered functionality for OpenShift Virtualization is preserved when it is deployed on an
IPv6 single-stack cluster. The focus is on the main functionalities of the product, covering network, virt
and storage domains.

**Testing Goals:**
Ensuring all existing functionality works correctly with IPv6-only configurations:
- [P0] sig-network T1
- [P0] sig-virt T1
- [P0] sig-storage T1
- [P0] sig-network T2 Gating
- [P0] sig-virt T2 Gating
- [P0] sig-storage T2 Gating
- [P0] sig-network T2 Regression
- [P1] UI
- [P1] Monitoring
- [P1] sig-virt T2 Regression
- [P1] sig-storage T2 Regression

**Note:** IOU and Infra sigs do not require dedicated IPv6 lanes; IPv6 network testing coverage is sufficient.

**Out of Scope (Testing Scope Exclusions)**

| Out-of-Scope Item | Rationale                                                          | PM/ Lead Agreement       |
|:------------------|:-------------------------------------------------------------------|:-------------------------|
| Cloud testing     | IPv6 single-stack configuration is not available on cloud clusters | [x] Ronen Sde-Or 01/2026 |


#### **2. Test Strategy**

| Item                           | Description                                                                                                                                                  | Applicable (Y/N or N/A) | Comments                                                                                  |
|:-------------------------------|:-------------------------------------------------------------------------------------------------------------------------------------------------------------|:------------------------|:------------------------------------------------------------------------------------------|
| Functional Testing             | Validates that the feature works according to specified requirements and user stories                                                                        | Y                       |                                                                                           |
| Automation Testing             | Ensures test cases are automated for continuous integration and regression coverage                                                                          | Y                       |                                                                                           |
| Performance Testing            | Validates feature performance meets requirements (latency, throughput, resource usage)                                                                       | N                       | No performance impact expected                                                            |
| Security Testing               | Verifies security requirements, RBAC, authentication, authorization, and vulnerability scanning                                                              | N                       | No additional security concerns                                                           |
| Usability Testing              | Validates user experience, UI/UX consistency, and accessibility requirements. Does the feature require UI? If so, ensure the UI aligns with the requirements | Y                       |                                                                                           |
| Compatibility Testing          | Ensures feature works across supported platforms, versions, and configurations                                                                               | Y                       | All existing components should work on IPv6 single-stack clusters                         |
| Regression Testing             | Verifies that new changes do not break existing functionality                                                                                                | Y                       |                                                                                           |
| Upgrade Testing                | Validates upgrade paths from previous versions, data migration, and configuration preservation                                                               | Y                       |                                                                                           |
| Backward Compatibility Testing | Ensures feature maintains compatibility with previous API versions and configurations                                                                        | N                       | No new APIs                                                                               |
| Dependencies                   | Dependent on deliverables from other components/products? Identify what is tested by which team.                                                             | N                       | IPv6 is a platform network capability                                                     |
| Cross Integrations             | Does the feature affect other features/require testing by other components? Identify what is tested by which team.                                           | Y                       | All relevant sigs should run tests on IPv6 clusters                                       |
| Monitoring                     | Does the feature require metrics and/or alerts?                                                                                                              | Y                       | Metrics should function correctly on IPv6 single-stack clusters                           |
| Cloud Testing                  | Does the feature require multi-cloud platform testing? Consider cloud-specific features.                                                                     | N/A                     | Out of scope; Not supported for IPv6 single-stack on Openshift on cloud provided clusters |


#### **3. Test Environment**

| Environment Component                         | Configuration                                                                      | Specification Examples                                          |
|:----------------------------------------------|:-----------------------------------------------------------------------------------|:----------------------------------------------------------------|
| **Cluster Topology**                          | Bare-Metal                                                                         |                                                                 |
| **OCP & OpenShift Virtualization Version(s)** | 4.21                                                                               |                                                                 |
| **CPU Virtualization**                        | Agnostic                                                                           |                                                                 |
| **Compute Resources**                         | Not required                                                                       |                                                                 |
| **Special Hardware**                          | Not required                                                                       |                                                                 |
| **Storage**                                   | Agnostic                                                                           |                                                                 |
| **Network**                                   | IPv6 single-stack cluster                                                          |                                                                 |
| **Required Operators**                        | All available covered operators in Tier1 & Tier2 tests. No new operator is needed. |                                                                 |
| **Platform**                                  | Bare-metal                                                                         |                                                                 |
| **Special Configurations**                    | IPv6 single-stack cluster                                                          | Access to the cluster for test clients (which usually use IPv4) |


#### **3.1. Testing Tools & Frameworks**

| Category           | Tools/Frameworks                                                                                                                                                                                |
|:-------------------|:------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Test Framework** | Infrastructure effort required to enable existing test suites to run on IPv6 single-stack clusters environment configuration                                                                    |
| **CI/CD**          | Dedicated IPv6 Single-Stack lanes with special markers:<br/>- Tier1 network<br/>- Tier1 compute<br/>- Tier1 storage<br/>- Tier2 network<br/>- Tier2 virt (node and cluster)<br/>- Tier2 storage |
| **Other Tools**    |                                                                                                                                                                                                 |


#### **4. Entry Criteria**

The following conditions must be met before testing can begin:

- [x] Requirements and design documents are **approved and merged**
- [x] Test environment can be **set up and configured** (see Section 3 - Test Environment)
- [x] Statically configure an IPv6 address to the primary pod network, to allow SSH access to the guest.


#### **5. Risks**

| Risk Category        | Specific Risk for This Feature                                                                                      | Mitigation Strategy                                                                  | Status        |
|:---------------------|:--------------------------------------------------------------------------------------------------------------------|:-------------------------------------------------------------------------------------|:--------------|
| Timeline/Schedule    | Adjustments are required for many tests and it would take time to merge them                                        | Split into smaller tasks and request an exception for merging additional adjustments | [in-progress] |
| Test Coverage        | There are some features which are under section 6. Known Limitations                                                | Coverage will be added in the following 4.21.z releases                              | [x]           |
| Test Environment     | N/A                                                                                                                 | No significant environment-related risks identified                                  | [x]           |
| Untestable Aspects   | N/A                                                                                                                 | All components are testable with exceptions (see section 6. Known Limitations)       | [x]           |
| Resource Constraints | N/A                                                                                                                 | No special resource requirements identified                                          | [x]           |
| Dependencies         | Collaboration with other teams required to troubleshoot failures in their test suites on IPv6 single-stack clusters | Coordinate with respective teams for debugging and provide IPv6 support              | [x]           |


#### **6. Known Limitations**

- KMP tests will not be adjusted for IPv6 single-stack; IPv4 test coverage is sufficient.
- Flat overlay network will not be tested as IPv6 support is not yet available.
- The following components will be adjusted in subsequent releases and are currently excluded from testing with special markers: MTV, BGP, jumbo frames, Service mesh, CCLM


### **III. Test Scenarios & Traceability**

Since this feature spans multiple features and SIGs, all existing tests are relevant and will be adjusted accordingly.

| Requirement ID   | Requirement Summary                                                         | Test Scenario(s)       | Tier   | Priority |
|:-----------------|:----------------------------------------------------------------------------|:-----------------------|:-------|:---------|
| CNV-28924 (epic) | All existing components, with exceptions (see section 6. Known Limitations) | All existing scenarios | Tier 2 | P0       |

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
