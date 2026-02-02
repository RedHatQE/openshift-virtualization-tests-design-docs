# Openshift-virtualization-tests Test plan

## **CBT - Quality Engineering Plan**

### **Metadata & Tracking**

| Field                  | Details                                                                |
|:-----------------------|:-----------------------------------------------------------------------|
| **Enhancement(s)**     | [VEP #25: Storage agnostic incremental backup using qemu (CBT)](https://github.com/kubevirt/enhancements/blob/main/veps/sig-storage/incremental-backup.md) |
| **Feature in Jira**    | [CNV-61530](https://issues.redhat.com/browse/CNV-61530)               |
| **Jira Tracking**      | [CNV-61530](https://issues.redhat.com/browse/CNV-61530) (Tasks must be created to **block the epic**) |
| **QE Owner(s)**        | Dalia Frank                                                            |
| **Owning SIG**         | sig-storage                                                            |
| **Participating SIGs** | sig-storage                                                            |
| **Current Status**     | Draft                                                                  |

**Document Conventions (if applicable):**

| Term        | Definition |
|:------------|:-----------|
| **CBT**     | Changed Block Tracking |
| **Push mode** | Backup mode where the hypervisor writes backup data to a user-provided PVC. |
| **Pull mode** | Backup mode where the hypervisor exposes an NBD export and the client pulls backup data; scratch space on a PVC is used during the backup. |

### **Feature Overview**

CBT (Changed Block Tracking) enables storage-agnostic incremental backup of VMs using QEMU, saving only changed blocks since the last backup. The main consumers are backup vendors and cluster admins. Backups can run in push mode, where the user provides a filesystem-based PVC to store backup data (size is estimated first; data is written to a hot-plugged PVC and then detached, and the user manages moving it e.g. to remote storage), or in pull mode, where the user provides a PVC for scratch space and libvirt exposes an NBD export so external components can pull backup data or query the dirty bitmap.

**Motivation:** Current backup options rely on CSI storage and create a full snapshot with each backup, leading to longer backup times, higher storage use (in-cluster and off-site), and large data transfers when copying off-site. Leveraging QEMU’s incremental backup with CBT saves only changes since the last backup, reducing backup time, storage usage, and off-site copy size.

---

### **I. Motivation and Requirements Review (QE Review Guidelines)**

This section documents the mandatory QE review process. The goal is to understand the feature's value,
technology, and testability before formal test planning.

#### **1. Requirement & User Story Review Checklist**

| Check                                  | Done | Details/Notes                                                                                                                                                                           | Comments |
|:---------------------------------------|:-----|:----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:---------|
| **Review Requirements**                | [ ]  | Reviewed the relevant requirements.                                                                                                                                                     |          |
| **Understand Value**                   | [ ]  | Confirmed clear user stories and understood.  <br/>Understand the difference between U/S and D/S requirements<br/> **What is the value of the feature for RH customers**.               |          |
| **Customer Use Cases**                 | [ ]  | Ensured requirements contain relevant **customer use cases**.                                                                                                                           |          |
| **Testability**                        | [ ]  | Confirmed requirements are **testable and unambiguous**.                                                                                                                                |          |
| **Acceptance Criteria**                | [ ]  | Ensured acceptance criteria are **defined clearly** (clear user stories; D/S requirements clearly defined in Jira).                                                                     |          |
| **Non-Functional Requirements (NFRs)** | [ ]  | Confirmed coverage for NFRs, including Performance, Security, Usability, Downtime, Connectivity, Monitoring (alerts/metrics), Scalability, Portability (e.g., cloud support), and Docs. |          |

#### **2. Technology and Design Review**

| Check                            | Done | Details/Notes                                                                                                                                           | Comments |
|:---------------------------------|:-----|:--------------------------------------------------------------------------------------------------------------------------------------------------------|:---------|
| **Developer Handoff/QE Kickoff** | [ ]  | A meeting where Dev/Arch walked QE through the design, architecture, and implementation details. **Critical for identifying untestable aspects early.** |          |
| **Technology Challenges**        | [ ]  | Identified potential testing challenges related to the underlying technology.                                                                           |          |
| **Test Environment Needs**       | [ ]  | Determined necessary **test environment setups and tools**.                                                                                             |          |
| **API Extensions**               | [ ]  | Reviewed new or modified APIs and their impact on testing.                                                                                              |          |
| **Topology Considerations**      | [ ]  | Evaluated multi-cluster, network topology, and architectural impacts.                                                                                  |          |


### **II. Software Test Plan (STP)**

#### **1. Scope of Testing**

**Testing Goals**

- **[P0]** [List key functional areas to be tested with priority]
- **[P1]** [List non-functional requirements to be tested with priority]
- **[P2]** [Reference specific user stories from Section I with priority]

**Out of Scope (Testing Scope Exclusions)**

| Out-of-Scope Item                                                    | Rationale              | PM/ Lead Agreement |
|:---------------------------------------------------------------------|:-----------------------|:-------------------|
| [e.g., Testing of deprecated features]                               | [Why this is excluded] | [ ] Name/Date      |
| [e.g., Performance testing]                                          | [Why this is excluded] | [ ] Name/Date      |
| [e.g., Testing on XXX architecture]                                  | [Why this is excluded] | [ ] Name/Date      |

#### **2. Test Strategy**

| Item                           | Description                                                                                                                                                  | Applicable (Y/N or N/A) | Comments |
|:-------------------------------|:-------------------------------------------------------------------------------------------------------------------------------------------------------------|:------------------------|:---------|
| Functional Testing             | Validates that the feature works according to specified requirements and user stories                                                                        |                         |          |
| Automation Testing             | Ensures test cases are automated for continuous integration and regression coverage                                                                          |                         |          |
| Performance Testing            | Validates feature performance meets requirements (latency, throughput, resource usage)                                                                       |                         |          |
| Security Testing               | Verifies security requirements, RBAC, authentication, authorization, and vulnerability scanning                                                              |                         |          |
| Usability Testing              | Validates user experience, UI/UX consistency, and accessibility requirements. Does the feature require UI? If so, ensure the UI aligns with the requirements |                         |          |
| Compatibility Testing          | Ensures feature works across supported platforms, versions, and configurations                                                                               |                         |          |
| Regression Testing             | Verifies that new changes do not break existing functionality                                                                                               |                         |          |
| Upgrade Testing                | Validates upgrade paths from previous versions, data migration, and configuration preservation                                                               |                         |          |
| Backward Compatibility Testing | Ensures feature maintains compatibility with previous API versions and configurations                                                                        |                         |          |
| Dependencies                   | Dependent on deliverables from other components/products? Identify what is tested by which team.                                                             |                         |          |
| Cross Integrations             | Does the feature affect other features/require testing by other components? Identify what is tested by which team.                                           |                         |          |
| Monitoring                     | Does the feature require metrics and/or alerts?                                                                                                              |                         |          |
| Cloud Testing                  | Does the feature require multi-cloud platform testing? Consider cloud-specific features.                                                                     |                         |          |

#### **3. Test Environment**

| Environment Component                         | Configuration | Specification Examples                                                                        |
|:----------------------------------------------|:--------------|:----------------------------------------------------------------------------------------------|
| **Cluster Topology**                          |               | [e.g., 3-master/3-worker bare-metal, SNO, Compact Cluster, HCP]                               |
| **OCP & OpenShift Virtualization Version(s)** |               | [e.g., OCP 4.20 with OpenShift Virtualization 4.20]                                          |
| **CPU Virtualization**                        |               | [e.g., Nodes with VT-x (Intel) or AMD-V (AMD) enabled in BIOS]                                |
| **Compute Resources**                         |               | [e.g., Minimum per worker node: 8 vCPUs, 32GB RAM]                                           |
| **Special Hardware**                          |               | [e.g., Specific NICs for SR-IOV, GPU etc]                                                    |
| **Storage**                                   |               | [e.g., Minimum 500GB per node, specific StorageClass(es)]                                    |
| **Network**                                   |               | [e.g., OVN-Kubernetes (default), Secondary Networks, Network Plugins, IPv4, IPv6, dual-stack] |
| **Required Operators**                        |               | [e.g., NMState Operator]                                                                      |
| **Platform**                                  |               | [e.g., Bare metal, AWS, Azure, GCP etc]                                                      |
| **Special Configurations**                    |               | [e.g., Disconnected/air-gapped cluster, Proxy environment, FIPS mode enabled]                |

#### **3.1. Testing Tools & Frameworks**

| Category           | Tools/Frameworks                                                  |
|:-------------------|:------------------------------------------------------------------|
| **Test Framework** | [e.g., New framework, custom test harness, or leave empty]         |
| **CI/CD**          | [e.g., Special test lane, custom pipeline config, or leave empty] |
| **Other Tools**    | [e.g., Special monitoring, performance tools, or leave empty]     |

#### **4. Entry Criteria**

The following conditions must be met before testing can begin:

- [ ] Requirements and design documents are **approved and merged**
- [ ] Test environment can be **set up and configured** (see Section II.3 - Test Environment)
- [ ] [Add feature-specific entry criteria as needed]

#### **5. Risks**

| Risk Category        | Specific Risk for This Feature                                                                                 | Mitigation Strategy                                                                            | Status |
|:---------------------|:---------------------------------------------------------------------------------------------------------------|:-----------------------------------------------------------------------------------------------|:-------|
| Timeline/Schedule    | [Describe your specific timeline risk]                                                                        | [Your specific mitigation]                                                                     | [ ]    |
| Test Coverage        | [Describe coverage gaps]                                                                                       | [Your mitigation]                                                                             | [ ]    |
| Test Environment     | [Describe environment risks]                                                                                   | [Your mitigation]                                                                              | [ ]    |
| Untestable Aspects   | [List what cannot be tested]                                                                                   | [Your mitigation]                                                                             | [ ]    |
| Resource Constraints | [Describe resource issues]                                                                                     | [Your mitigation]                                                                              | [ ]    |
| Dependencies         | [Describe dependency risks]                                                                                    | [Your mitigation]                                                                              | [ ]    |
| Other                | [Any other specific risks]                                                                                     | [Mitigation strategy]                                                                          | [ ]    |

#### **6. Known Limitations**

- [List limitation 1]
- [List limitation 2]

---

### **III. Test Scenarios & Traceability**

| Requirement ID    | Requirement Summary   | Test Scenario(s)                                           | Tier   | Priority |
|:------------------|:----------------------|:-----------------------------------------------------------|:-------|:---------|
| [Jira-123]        | As a user...          | Verify VM can be created with new feature X                | Tier 1 | P0       |
| [Jira-124]        | As an admin...        | Verify API for feature X is backward compatible            | Tier 2 | P0       |
| [Jira-125]        | NFR-2 (Security)      | Verify feature X follows RBAC permissions model            | ...    | P1       |
| [Jira-126]        | As a cluster admin... | Verify upgrade from version X to Y preserves feature state | ....   | P2       |

---

### **IV. Sign-off and Approval**

This Software Test Plan requires approval from the following stakeholders:

* **Reviewers:**
  - [Name / @github-username]
  - [Name / @github-username]
* **Approvers:**
  - [Name / @github-username]
  - [Name / @github-username]
