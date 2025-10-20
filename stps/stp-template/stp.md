# Openshift-virtualization-tests Test plan

## **[Feature Title/Name] - Quality Engineering Plan**

### **Metadata & Tracking**

| Field                  | Details                                                                |
|:-----------------------|:-----------------------------------------------------------------------|
| **Enhancement(s)**     | [Links to enhancement(s)]                                              |
| **Feature in Jira**    | [Link(s) to the relevant feature/epic in Jira                          |
| **Jira Tracking**      | [Link to Jira Epic] (Tasks must be created to **block the epic**)      |
| **QE Owner(s)**        | [Name(s)]                                                              |
| **Owning SIG**         | <sig-xyz>                                                              |
| **Participating SIGs** | [List of participating SIGs)                                           |
| **Current Status**     | [Draft / QE Review Complete / Testing In Progress / GA Sign-off Ready] |

---

### **I. Motivation and Requirements Review (QE Review Guidelines)**

This section documents the mandatory QE review process. The goal is to understand the feature's value, technology, and testability prior to formal test planning.

#### **1. Requirement & User Story Review Checklist**

| Check                                  | Status (Y/N) | Details/Notes                                                                                                                                                                           | Comments |
|:---------------------------------------|:-------------|:----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:---------|
| **Review Requirements**                |              | Reviewed the relevant requirements.                                                                                                                                                     |          |
| **Understand Value**                   |              | Confirmed clear user stories and understood.  <br/>Understand the difference between U/S and D/S requirements<br/> **What is the value of the feature for RH customers**.               |          |
| **Customer Use Cases**                 |              | Ensured requirements contain relevant **customer use cases**.                                                                                                                           |          |
| **Testability**                        |              | Confirmed requirements are **testable and unambiguous**.                                                                                                                                |          |
| **Acceptance Criteria**                |              | Ensured acceptance criteria are **defined clearly** (clear user stories; D/S requirements clearly defined in Jira).                                                                     |          |
| **Non-Functional Requirements (NFRs)** |              | Confirmed coverage for NFRs, including Performance, Security, Usability, Downtime, Connectivity, Monitoring (alerts/metrics), Scalability, Portability (e.g., cloud support), and Docs. |          |

- [KubeVirt Enhancements](https://github.com/kubevirt/enhancements/tree/main/veps)
- [OCP Enhancements](https://github.com/openshift/enhancements/tree/master/enhancements)

#### **2. Technology and Design Review**

| Check                            | Status    | Details/Notes                                                                                                                                           | Comments |
|:---------------------------------|:----------|:--------------------------------------------------------------------------------------------------------------------------------------------------------|:---------|
| **Developer Handoff/QE Kickoff** | [ ]       | A meeting where Dev/Arch walked QE through the design, architecture, and implementation details. **Critical for identifying untestable aspects early.** |          |
| **Technology Challenges**        | [ ]       | Identified potential testing challenges related to the underlying technology.                                                                           |          |
| **Test Environment Needs**       | [ ]       | Determined necessary **test environment setups and tools**.                                                                                             |          |
| **API Extensions**               | [ ]       | Reviewed new or modified APIs and their impact on testing.                                                                                              |          |
| **Topology Considerations**      | [ ]       | Evaluated multi-cluster, network topology, and architectural impacts.                                                                                   |          |


### **II. Software Test Plan (STP)**

This STP serves as the **overall roadmap for testing**, detailing the scope, approach, resources, and schedule.

#### **1. Introduction and Scope**

- **Purpose:** This document describes the overall approach to testing for [Feature name + link]. It outlines the testing objectives, scope, methodology, and resources required to ensure the **quality and reliability** of the software.
- **Scope of Testing:** Briefly describe what will be tested. The scope must **cover functional and non-functional requirements**. Must ensure user stories are included and aligned to downstream user stories.
- **Document Conventions:** [Define any document conventions, e.g., acronyms, definitions specific to this document.]

#### **2. Test Objectives**

The primary goals of this test plan are to:

- **Verify** that the software meets all specified requirements.
- **Identify and report** software defects and issues.
- **Ensure** the software performs as expected under various conditions.
- **Assess** the overall quality and readiness of the software for release.

#### **3. Motivation**

This section captures the feature motivation from a QE perspective, focusing on testing goals and priorities.

##### **A. User Stories (Testing Perspective)**

Document key user stories that drive testing priorities:

- **As a** [user role], **I want** [capability] **so that** [benefit].
  - **QE Focus:** [What aspects of this user story are critical to test]
- **As a** [user role], **I need** [functionality] **because** [reason].
  - **QE Focus:** [Key test scenarios for this user story]

##### **B. Testing Goals**

Define specific, measurable testing objectives for this feature:

- [ ] [Goal 1: e.g., Achieve 90% feature coverage for core functionality]
- [ ] [Goal 2: e.g., Validate all user workflows end-to-end]
- [ ] [Goal 3: e.g., Ensure performance meets defined SLAs]
- [ ] [Goal 4: e.g., Verify backward compatibility with version X]
- [ ] [Goal 5: e.g., Confirm security requirements are met]

##### **C. Non-Goals (Testing Scope Exclusions)**

Explicitly document what is **out of scope** for testing. **Critical:** All non-goals require explicit stakeholder agreement to prevent "I assumed you were testing that" issues.

| Non-Goal                                                             | Rationale              | PM/ Lead Agreement |
|:---------------------------------------------------------------------|:-----------------------|:-------------------|
| [e.g., Testing of deprecated features]                               | [Why this is excluded] | [ ] Name/Date      |
| [e.g., Performance testing beyond defined load limits]               | [Why this is excluded] | [ ] Name/Date      |
| [e.g., UI testing in unsupported browsers]                           | [Why this is excluded] | [ ] Name/Date      |
| [e.g., Testing on ARM64 architecture]                                | [Why this is excluded] | [ ] Name/Date      |
| [e.g., Testing of third-party integrations not officially supported] | [Why this is excluded] | [ ] Name/Date      |

**Important Notes:**
- Non-goals without stakeholder agreement are considered **risks** and must be escalated
- Review non-goals during a Developer Handoff/QE Kickoff meeting

#### **4. Test Strategy**

##### **A. Types of Testing**

The following types of testing must be reviewed and addressed.
If a testing type is not applicable, it should NOT be removed from the table, should be marked as "N/A", and a justification should be provided.

| Item (Testing Type)            | Addressed (Y/N) | Comments | Details                                                                          |
|:-------------------------------|:----------------|:---------|:---------------------------------------------------------------------------------|
| Functional Testing             |                 |          | Verifying that the software functions as specified.                              |
| Automation Testing             |                 |          | Example: Automate all P1 scenarios, focus on API-level automation.               |
| Performance Testing            |                 |          | Evaluating responsiveness, stability, and scalability under various loads.       |
| Security Testing               |                 |          | Identifying vulnerabilities and weaknesses.                                      |
| Usability Testing              |                 |          | Assessing ease of use and user-friendliness.                                     |
| Compatibility Testing          |                 |          | Checking compatibility with different deployments.                               |
| Regression Testing             |                 |          | Ensuring new changes do not adversely affect existing functionalities.           |
| Upgrade Testing                |                 |          | Verifying successful software upgrade capability.                                |
| Backward Compatibility Testing |                 |          | Ensuring the new version works with older versions or data, such as API changes. |

##### **B. Potential Areas to Consider**
If a testing area is not applicable, it should NOT be removed from the table, should be marked as "N/A", and a justification should be provided.

| Item                   | Description                                                                                                        | Addressed (Y/N) | Comment | Source |
|:-----------------------|:-------------------------------------------------------------------------------------------------------------------|:----------------|:--------|:-------|
| **Dependencies**       | Dependent on deliverables from other components/products? Identify what is tested by which team.                   |                 |         |        |
| **Monitoring**         | Does the feature require metrics and/or alerts?                                                                    |                 |         |        |
| **Cross Integrations** | Does the feature affect other features/require testing by other components? Identify what is tested by which team. |                 |         |        |
| **UI**                 | Does the feature require UI? If so, ensure the UI aligns with the requirements.                                    |                 |         |        |

#### **5. Test Environment**

| Environment Component       | Value | Specification Examples                                                                |
|:----------------------------|:------|:--------------------------------------------------------------------------------------|
| **Cluster Topology**        |       | [e.g., 3-master/3-worker bare-metal, SNO, Compact Cluster, Hypershift hosted cluster] |
| **OCP & OpenShift Virtualization Version(s)**    |       | [e.g., OCP 4.20 with OpenShift Virtualization 4.20]                                                        |
| **CPU Virtualization**      |       | [e.g., Nodes with VT-x (Intel) or AMD-V (AMD) enabled in BIOS]                        |
| **Compute Resources**       |       | [e.g., Minimum per worker node: 8 vCPUs, 32GB RAM]                                    |
| **Special Hardware**        |       | [e.g., Specific NICs for SR-IOV, GPU etc]                                             |
| **Storage (Disk)**          |       | [e.g., Minimum 500GB per node]                                                        |
| **Storage Class**           |       | [e.g., ocs-storagecluster-ceph-rbd-virtualization, specific CSI driver like Ceph-RBD] |
| **CNI (Container Network)** |       | [e.g., OVN-Kubernetes (default), OpenShift-SDN]                                       |
| **Secondary Networks**      |       | [e.g., Required NetworkAttachmentDefinitions (NADs) for SR-IOV, bridge, macvlan]      |
| **Network Plugins**         |       | [e.g., Multus CNI for secondary networks]                                             |
| **Network Features**        |       | [e.g., IPv4, IPv6, dual-stack]                                                        |
| **Required Operators**      |       | [e.g., NMState Operator]                                                              |
| **Platform**                |       | [e.g., Bare metal, AWS, Azure, GCP etc]                                               |
| **Special Configurations**  |       | [e.g., Disconnected/air-gapped cluster, Proxy environment, FIPS mode enabled]         |

#### **6. Entry and Exit Criteria**

##### **A. Entry Criteria**

The following conditions must be met before testing can begin:

- Requirements and design documents are **approved and stable**.
- Test environment is **set up and configured**.
- Test cases are **reviewed and approved**.

##### **B. Exit Criteria**

The following conditions must be met for testing to be considered complete:

- All **high-priority defects are resolved and verified**.
- **Test coverage goals are achieved**.
- **Test automation merged** (required for GA sign-off).
- All planned test cycles are completed.
- Test summary report is approved.
- Acceptance criteria are met.

#### **7. Risk Management**
If a risk is not applicable, it should NOT be removed from the table, should be marked as "N/A", and a justification should be provided.

| Risk                       | Risk Description Examples                                                                                                       | Mitigation Strategy                                                                                                                                                        | Comments |
|:---------------------------|:--------------------------------------------------------------------------------------------------------------------------------|:---------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:---------|
| Timeline/Schedule Risk     | Feature development completed too close to code-freeze, leaving insufficient time for regression, performance, or soak testing. | QE engaged early (Section I), phased testing of components as ready, automation framework prepared in parallel.                                                            |          |
| Insufficient test coverage | Critical functionality may not be adequately tested, leading to bugs in production.                                             | Regular reviews of test cases against requirements, coverage analysis, risk-based testing prioritization.                                                                  |          |
| Unstable test environment  | Test environment instability causing test failures, delays, and unreliable results.                                             | Dedicated environment setup and maintenance, environment health monitoring, quick rollback procedures.                                                                     |          |
| Untestable aspects         | Certain functionalities cannot be tested due to technical or resource limitations.                                              | Explicitly document untestable aspects (see Section 6), ensure all stakeholders acknowledge and accept the risk, consider production monitoring as alternative validation. |          |
| Resource constraints       | Insufficient QE resources (people, infrastructure, tools) to complete testing within timeline.                                  | Early identification and allocation of resources, prioritize critical test scenarios, leverage automation to maximize coverage.                                            |          |
| Integration concerns       | Dependencies on external systems, components, or teams that may cause delays or compatibility issues.                           | [Specify mitigation strategy based on specific integration]                                                                                                                |          |
| Other                      | [Specify risk description]                                                                                                      | [Specify mitigation strategy]                                                                                                                                              |          |

#### **8. Limitations**

- [List any known limitations or trade-offs in the implementation]
- [Document constraints or edge cases that are not covered]

---

### **III. Test Case Descriptions & Traceability**

This section links the strategic plan (STP) to the tactical test cases (which are managed externally). It provides the critical bridge between requirements (Section I) and test execution, enabling reviewers to verify complete coverage.

#### **1. Test Case Repository**

All test cases for this feature are managed in: **[Link to Polarion]**

#### **2. Traceability Matrix**

This matrix maps requirements to high-level test scenarios that validate them. This is **not** a list of all test steps, but a **high-level proof of coverage** that enables stakeholders to answer: *"Do we have test coverage for all requirements?"*
Example:

| Requirement / User Story (from Section I) | Mapped Test Scenarios (High-Level)                         | Priority | Test Type(s)                | Automation Status         |
|:------------------------------------------|:-----------------------------------------------------------|:---------|:----------------------------|:--------------------------|
| [Jira-123] As a user...                   | Verify VM can be created with new feature X                | P1       | Functional, UI              | Automated (in CI)         |
| [Enhancement-XYZ] NFR-1 (Performance)     | Validate performance of 100 VM creations under load        | P2       | Performance                 | Manual (Scripts in Git)   |
| [Jira-124] As an admin...                 | Verify API for feature X is backward compatible            | P1       | API, Backward Compatibility | Automated (e2e suite)     |
| [Jira-125] NFR-2 (Security)               | Verify feature X follows RBAC permissions model            | P1       | Security, Functional        | Automated (in CI)         |
| [Jira-126] As a cluster admin...          | Verify upgrade from version X to Y preserves feature state | P1       | Upgrade, Backward Compat.   | Automated (upgrade suite) |


#### **3. Test Scenario Descriptions**

Provide brief descriptions of key test scenarios for stakeholder understanding:

##### **High Priority (P1) Scenarios**

- **[Test Scenario Name]:** [Brief description of what this test validates and why it's critical]
  - **Requirements Covered:** [List of requirement IDs]
  - **Test Approach:** [High-level approach, for example,: automated end-to-end, manual exploratory]

##### **Medium Priority (P2) Scenarios**

- **[Test Scenario Name]:** [Description]
  - **Requirements Covered:** [IDs]
  - **Test Approach:** [Approach]

#### **4. Traceability Maintenance**

- **Owner:** [Name/Team responsible for maintaining traceability]
- **Update Frequency:** [e.g., Updated during each sprint/milestone]
- **Review Process:** [How and when traceability is reviewed with stakeholders]
- **Tool:** [Tool used to maintain traceability - Jira, Excel, TestRail, etc.]

---

### **IV. Sign-off and Approval**

#### **1. Final Sign-off Checklist**

| Requirement                        | Status (Y/N) | Notes                                                                         | Source |
|:-----------------------------------|:-------------|:------------------------------------------------------------------------------|:-------|
| **Tier 1 / Tier 2 Tests Defined**  |              | Reviewed and worked with Dev on what will be covered in T1 and T2.            |        |
| **Automation Merged**              |              | **Automation must be merged for GA sign-off**.                                |        |
| **Tests in Release Checklist Job** |              | Made sure tests are running as part of one of the **release checklist jobs**. |        |
| **Documentation Reviewed**         |              | Reviewed the feature documentation.                                           |        |
| **Feature Sign-off**               |              | QE officially signs off the feature.                                          |        |

#### **2. Approval**

This Software Test Plan requires approval from the following stakeholders:

* Reviewers:
  - TBD
  - "@alice.doe"
* Approvers:
  - TBD
  - "@oscar.doe"
