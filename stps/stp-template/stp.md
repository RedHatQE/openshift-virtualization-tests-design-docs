# Openshift-virtualization-tests Test plan

## **[Feature Title/Name] - Quality Engineering Plan**

### **Metadata & Tracking**

| Field                  | Details                                                                |
|:-----------------------|:-----------------------------------------------------------------------|
| **Enhancement(s)**     | [Links to enhancement(s)]                                              |
| **Feature in Jira**    | [Link(s) to the relevant feature/epic in Jira]                         |
| **Jira Tracking**      | [Link to Jira Epic] (Tasks must be created to **block the epic**)      |
| **QE Owner(s)**        | [Name(s)]                                                              |
| **Owning SIG**         | <sig-xyz>                                                              |
| **Participating SIGs** | [List of participating SIGs]                                           |
| **Current Status**     | [Draft / QE Review Complete / Testing In Progress / GA Sign-off Ready] |

---

### **I. Motivation and Requirements Review (QE Review Guidelines)**

This section documents the mandatory QE review process. The goal is to understand the feature's value, technology, and testability prior to formal test planning.

#### **1. Requirement & User Story Review Checklist**

| Check                                  | Done | Details/Notes                                                                                                                                                                           | Comments |
|:---------------------------------------|:-----|:----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:---------|
| **Review Requirements**                | [ ]  | Reviewed the relevant requirements.                                                                                                                                                     |          |
| **Understand Value**                   | [ ]  | Confirmed clear user stories and understood.  <br/>Understand the difference between U/S and D/S requirements<br/> **What is the value of the feature for RH customers**.               |          |
| **Customer Use Cases**                 | [ ]  | Ensured requirements contain relevant **customer use cases**.                                                                                                                           |          |
| **Testability**                        | [ ]  | Confirmed requirements are **testable and unambiguous**.                                                                                                                                |          |
| **Acceptance Criteria**                | [ ]  | Ensured acceptance criteria are **defined clearly** (clear user stories; D/S requirements clearly defined in Jira).                                                                     |          |
| **Non-Functional Requirements (NFRs)** | [ ]  | Confirmed coverage for NFRs, including Performance, Security, Usability, Downtime, Connectivity, Monitoring (alerts/metrics), Scalability, Portability (e.g., cloud support), and Docs. |          |

- [KubeVirt Enhancements](https://github.com/kubevirt/enhancements/tree/main/veps)
- [OCP Enhancements](https://github.com/openshift/enhancements/tree/master/enhancements)

#### **2. Technology and Design Review**

| Check                            | Done | Details/Notes                                                                                                                                           | Comments |
|:---------------------------------|:-----|:--------------------------------------------------------------------------------------------------------------------------------------------------------|:---------|
| **Developer Handoff/QE Kickoff** | [ ]  | A meeting where Dev/Arch walked QE through the design, architecture, and implementation details. **Critical for identifying untestable aspects early.** |          |
| **Technology Challenges**        | [ ]  | Identified potential testing challenges related to the underlying technology.                                                                           |          |
| **Test Environment Needs**       | [ ]  | Determined necessary **test environment setups and tools**.                                                                                             |          |
| **API Extensions**               | [ ]  | Reviewed new or modified APIs and their impact on testing.                                                                                              |          |
| **Topology Considerations**      | [ ]  | Evaluated multi-cluster, network topology, and architectural impacts.                                                                                   |          |


### **II. Software Test Plan (STP)**

This STP serves as the **overall roadmap for testing**, detailing the scope, approach, resources, and schedule.

#### **1. Scope of Testing**

Briefly describe what will be tested. The scope must **cover functional and non-functional requirements**. Must ensure user stories are included and aligned to downstream user stories from Section I.

**In Scope:**
- [List key functional areas to be tested]
- [List non-functional requirements to be tested]
- [Reference specific user stories from Section I]

**Document Conventions (if applicable):** [Define acronyms or terms specific to this document]

#### **2. Testing Goals**

Define specific, measurable testing objectives for this feature, such as:

- [ ] [Goal 1: e.g., Achieve 90% feature coverage for core functionality]
- [ ] [Goal 2: e.g., Validate all user workflows end-to-end]
- [ ] [Goal 3: e.g., Verify backward compatibility with version X]

#### **3. Non-Goals (Testing Scope Exclusions)**

Explicitly document what is **out of scope** for testing. **Critical:** All non-goals require explicit stakeholder agreement to prevent "I assumed you were testing that" issues.

**Note:** Replace example rows with your actual non-goals. Each non-goal must have PM/Lead sign-off.

| Non-Goal                                                             | Rationale              | PM/ Lead Agreement |
|:---------------------------------------------------------------------|:-----------------------|:-------------------|
| [e.g., Testing of deprecated features]                               | [Why this is excluded] | [ ] Name/Date      |
| [e.g., Performance testing]                                          | [Why this is excluded] | [ ] Name/Date      |
| [e.g., Testing on XXX architecture]                                  | [Why this is excluded] | [ ] Name/Date      |

**Important Notes:**
- Non-goals without stakeholder agreement are considered **risks** and must be escalated (see Section II.7 - Risks and Limitations)
- Review non-goals during Developer Handoff/QE Kickoff meeting (see Section I.2 - Technology and Design Review)

#### **4. Test Strategy**

##### **A. Types of Testing**

The following types of testing must be reviewed and addressed.

**Note:** Mark "Y" if applicable, "N/A" if not applicable (with justification in Comments). Empty cells indicate incomplete review.

| Item (Testing Type)            | Applicable (Y/N or N/A) | Comments |
|:-------------------------------|:------------------------|:---------|
| Functional Testing             |                         |          |
| Automation Testing             |                         |          |
| Performance Testing            |                         |          |
| Security Testing               |                         |          |
| Usability Testing              |                         |          |
| Compatibility Testing          |                         |          |
| Regression Testing             |                         |          |
| Upgrade Testing                |                         |          |
| Backward Compatibility Testing |                         |          |

##### **B. Potential Areas to Consider**

**Note:** Mark "Y" if applicable, "N/A" if not applicable (with justification in Comment). Empty cells indicate incomplete review.

| Item                   | Description                                                                                                        | Applicable (Y/N or N/A) | Comment |
|:-----------------------|:-------------------------------------------------------------------------------------------------------------------|:------------------------|:--------|
| **Dependencies**       | Dependent on deliverables from other components/products? Identify what is tested by which team.                   |                         |         |
| **Monitoring**         | Does the feature require metrics and/or alerts?                                                                    |                         |         |
| **Cross Integrations** | Does the feature affect other features/require testing by other components? Identify what is tested by which team. |                         |         |
| **UI**                 | Does the feature require UI? If so, ensure the UI aligns with the requirements.                                    |                         |         |

#### **5. Test Environment**

**Note:** "N/A" means explicitly not applicable. Cannot leave empty cells.

| Environment Component                         | Configuration | Specification Examples                                                                        |
|:----------------------------------------------|:--------------|:----------------------------------------------------------------------------------------------|
| **Cluster Topology**                          |               | [e.g., 3-master/3-worker bare-metal, SNO, Compact Cluster, HCP]                               |
| **OCP & OpenShift Virtualization Version(s)** |               | [e.g., OCP 4.20 with OpenShift Virtualization 4.20]                                           |
| **CPU Virtualization**                        |               | [e.g., Nodes with VT-x (Intel) or AMD-V (AMD) enabled in BIOS]                                |
| **Compute Resources**                         |               | [e.g., Minimum per worker node: 8 vCPUs, 32GB RAM]                                            |
| **Special Hardware**                          |               | [e.g., Specific NICs for SR-IOV, GPU etc]                                                     |
| **Storage**                                   |               | [e.g., Minimum 500GB per node, specific StorageClass(es)]                                     |
| **Network**                                   |               | [e.g., OVN-Kubernetes (default), Secondary Networks, Network Plugins, IPv4, IPv6, dual-stack] |
| **Required Operators**                        |               | [e.g., NMState Operator]                                                                      |
| **Platform**                                  |               | [e.g., Bare metal, AWS, Azure, GCP etc]                                                       |
| **Special Configurations**                    |               | [e.g., Disconnected/air-gapped cluster, Proxy environment, FIPS mode enabled]                 |

#### **5.5. Testing Tools & Frameworks**

Document any **new or additional** testing tools, frameworks, or infrastructure required specifically for this feature.

**Note:** Only list tools that are **new** or **different** from standard testing infrastructure. Leave empty if using standard tools.

| Category           | Tools/Frameworks                                                  |
|:-------------------|:------------------------------------------------------------------|
| **Test Framework** | [e.g., New framework, custom test harness, or leave empty]        |
| **CI/CD**          | [e.g., Special test lane, custom pipeline config, or leave empty] |
| **Other Tools**    | [e.g., Special monitoring, performance tools, or leave empty]     |

#### **6. Entry and Exit Criteria**

##### **A. Entry Criteria**

The following conditions must be met before testing can begin:

- [ ] Requirements and design documents are **approved and merged**
- [ ] Test environment is **set up and configured** (see Section II.5 - Test Environment)
- [ ] Test cases are **reviewed and approved**
- [ ] [Add feature-specific entry criteria as needed]

#### **7. Risks and Limitations**

Document specific risks and limitations for this feature. If a risk category is not applicable, mark as "N/A" with justification in mitigation strategy.

**Note:** Empty "Specific Risk" cells mean this must be filled. "N/A" means explicitly not applicable with justification.

| Risk Category        | Specific Risk for This Feature                                                                                 | Mitigation Strategy                                                                            | Status |
|:---------------------|:---------------------------------------------------------------------------------------------------------------|:-----------------------------------------------------------------------------------------------|:-------|
| Timeline/Schedule    | [Describe your specific timeline risk, e.g., "Feature freeze in 2 weeks, complex test scenarios need 3 weeks"] | [Your specific mitigation, e.g., "Prioritize P1 scenarios, automate in parallel"]              | [ ]    |
| Test Coverage        | [Describe coverage gaps, e.g., "Cannot test multi-cluster scenarios due to infrastructure limits"]             | [Your mitigation, e.g., "Document limitation, test single cluster thoroughly"]                 | [ ]    |
| Test Environment     | [Describe environment risks, e.g., "Requires GPU hardware, limited availability"]                              | [Your mitigation, e.g., "Reserve GPU nodes early, schedule tests in advance"]                  | [ ]    |
| Untestable Aspects   | [List what cannot be tested, e.g., "Production scale with 10k VMs"]                                            | [Your mitigation, e.g., "Test at smaller scale, extrapolate results, prod monitoring"]         | [ ]    |
| Resource Constraints | [Describe resource issues, e.g., "Only 1 QE assigned, feature spans 3 components"]                             | [Your mitigation, e.g., "Focus automation on critical paths, coordinate with dev for testing"] | [ ]    |
| Dependencies         | [Describe dependency risks, e.g., "Depends on Storage team delivering feature X"]                              | [Your mitigation, e.g., "Coordinate with Storage QE, have backup test plan"]                   | [ ]    |
| Other                | [Any other specific risks]                                                                                     | [Mitigation strategy]                                                                          | [ ]    |

#### **8. Known Limitations**

Document any known limitations, constraints, or trade-offs in the feature implementation or testing approach.

**Examples:**
- Feature does not support IPv6 (only IPv4)
- No support for ARM64 architecture in this release

- [List limitation 1]
...

---

### **III. Test Case Descriptions & Traceability**

This section links requirements to test coverage, enabling reviewers to verify all requirements are tested.

#### **1. Requirements-to-Tests Mapping**

Map each requirement to its test coverage to verify complete coverage.

| Requirement ID    | Requirement Summary   | Test Scenario(s)                                           | Test Type(s)                | Priority |
|:------------------|:----------------------|:-----------------------------------------------------------|:----------------------------|:---------|
| [Jira-123]        | As a user...          | Verify VM can be created with new feature X                | Functional, UI              | P0       |
| [Jira-124]        | As an admin...        | Verify API for feature X is backward compatible            | API, Backward Compatibility | P0       |
| [Jira-125]        | NFR-2 (Security)      | Verify feature X follows RBAC permissions model            | Security, Functional        | P1       |
| [Jira-126]        | As a cluster admin... | Verify upgrade from version X to Y preserves feature state | Upgrade, Backward Compat.   | P2       |

---

### **IV. Sign-off and Approval**

This Software Test Plan requires approval from the following stakeholders:

* **Reviewers:**
  - [Name / @github-username]
  - [Name / @github-username]
* **Approvers:**
  - [Name / @github-username]
  - [Name / @github-username]
