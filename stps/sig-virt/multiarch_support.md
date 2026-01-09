# Openshift-virtualization-tests Test plan

## VM creation and Live Migration on a multi arch cluster - Quality Engineering Plan**

### **Metadata & Tracking**

| Field                  | Details                                                                                                                                                          |
| :--------------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Enhancement(s)**     | [dic-on-heterogeneous-cluster](https://github.com/kubevirt/enhancements/blob/main/veps/sig-storage/dic-on-heterogeneous-cluster/dic-on-heterogeneous-cluster.md) |
| **Feature in Jira**    | [VIRTSTRAT-494](https://issues.redhat.com/browse/VIRTSTRAT-494)                                                                                                  |
| **Jira Tracking**      | [CNV-26818](https://issues.redhat.com/browse/CNV-26818)                                                                                                          |
| **QE Owner(s)**        | Akriti Gupta                                                                                                                                                     |
| **Owning SIG**         | sig-iuo                                                                                                                                                          |
| **Participating SIGs** | sig-infra, sig-storage, sig-virt                                                                                                                                 |
| **Current Status**     | Draft                                                                                                                                                            |

**Document Conventions (if applicable):** [Define acronyms or terms specific to this document]
- VM : Virtual Machine
---

### **I. Motivation and Requirements Review (QE Review Guidelines)**

This section documents the mandatory QE review process. The goal is to understand the feature's value,
technology, and testability before formal test planning.

#### **1. Requirement & User Story Review Checklist**

| Check                                  | Done | Details/Notes                                                                                                                                                                                                                            | Comments |
| :------------------------------------- | :--- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :------- |
| **Review Requirements**                | [V]  | Reviewed the relevant requirements.                                                                                                                                                                                                      |          |
| **Understand Value**                   | [V]  | Confirmed clear user stories and understood.  <br/>Ensures workload uptime and hardware flexibility by enabling seamless VM creation and architecture-safe live migration across x86 and ARM nodes within a single managed cluster.<br/> |          |
| **Customer Use Cases**                 | [V]  | Ensured requirements contain relevant **customer use cases**.                                                                                                                                                                            |          |
| **Testability**                        | [V]  | Confirmed requirements are **testable and unambiguous**.                                                                                                                                                                                 |          |
| **Acceptance Criteria**                | [V]  | Ensured acceptance criteria are **defined clearly** (clear user stories; D/S requirements clearly defined in Jira).                                                                                                                      |          |
| **Non-Functional Requirements (NFRs)** | [V]  | Confirmed coverage for NFRs, including Performance, Security, Usability, Downtime, Connectivity, Monitoring (alerts/metrics), Scalability, Portability (e.g., cloud support), and Docs.                                                  |          |


#### **2. Technology and Design Review**

| Check                            | Done | Details/Notes                                                                                                                                           | Comments |
| :------------------------------- | :--- | :------------------------------------------------------------------------------------------------------------------------------------------------------ | :------- |
| **Developer Handoff/QE Kickoff** | [V]  | A meeting where Dev/Arch walked QE through the design, architecture, and implementation details. **Critical for identifying untestable aspects early.** |          |
| **Technology Challenges**        | [V]  | Identified potential testing challenges related to the underlying technology.                                                                           |          |
| **Test Environment Needs**       | [V]  | Determined necessary **test environment setups and tools**.                                                                                             |          |
| **API Extensions**               | [V]  | Reviewed new or modified APIs and their impact on testing.                                                                                              |          |
| **Topology Considerations**      | [V]  | Evaluated multi-cluster, network topology, and architectural impacts.                                                                                   |          |


### **II. Software Test Plan (STP)**

This STP serves as the **overall roadmap for testing**, detailing the scope, approach, resources, and schedule.

#### **1. Scope of Testing**

This test plan checks if VMs schedules and live migrates correctly on a mixed architecture cluster

**In Scope:**
- Create VMs for both AMD and ARM and confirm the cluster automatically places them on respective architecture node.
- Test VM creation using both DataSources and Qcow2 images and ensure they always land on the right nodes.
- Verify that VMs can Live Migrate between nodes of the same type (x86 to x86 and ARM to ARM) without stopping.

**Out of Scope (Testing Scope Exclusions)**
**Note:** Replace example rows with your actual out-of-scope items.

| Out-of-Scope Item              | Rationale                                                                 | PM/ Lead Agreement |
| :----------------------------- | :------------------------------------------------------------------------ | :----------------- |
| Testing with container disk VM | There's no defaulting of the architecture based on the containerdisk arch | [ ] Name/Date      |



#### **2. Testing Goals**
- Validate Correct Architecture Scheduling: Confirm that 100% of amd64 and arm64 VMs are automatically placed on worker nodes with the matching CPU architecture.

- Verify Live Migration: Successfully migrate running VMs between same-arch nodes (x86 to x86, ARM to ARM).

- Verify Multi-Method Provisioning: Achieve 100% success rate for VM creation using both DataSources and Qcow2 images across both architectures.

#### **3. Test Strategy**

The following test strategy considerations must be reviewed and addressed. Mark "Y" if applicable,
"N/A" if not applicable (with justification in Comments). Empty cells indicate incomplete review.

| Item                           | Description                                                                                                        | Applicable (Y/N or N/A) | Comments |
| :----------------------------- | :----------------------------------------------------------------------------------------------------------------- | :---------------------- | :------- |
| Functional Testing             | Yes                                                                                                                |                         |          |
| Automation Testing             | Yes                                                                                                                |                         |          |
| Performance Testing            | N/A                                                                                                                |                         |          |
| Security Testing               | N/A                                                                                                                |                         |          |
| Usability Testing              | Yes                                                                                                                |                         |          |
| Compatibility Testing          | N/A                                                                                                                |                         |          |
| Regression Testing             | Yes                                                                                                                |                         |          |
| Upgrade Testing                | N/A                                                                                                                |                         |          |
| Backward Compatibility Testing | N/A                                                                                                                |                         |          |
| Dependencies                   | Dependent on deliverables from other components/products? Identify what is tested by which team.                   |                         |          |
| Cross Integrations             | Does the feature affect other features/require testing by other components? Identify what is tested by which team. |                         |          |
| Monitoring                     | Yes                                                                                                                |                         |          |
| Cloud Testing                  | N/A                                                                                                                |                         |          |

#### **4. Test Environment**

**Note:** "N/A" means explicitly not applicable. Cannot leave empty cells.

| Environment Component                         | Configuration         | Specification Examples                                                                        |
| :-------------------------------------------- | :-------------------- | :-------------------------------------------------------------------------------------------- |
| **Cluster Topology**                          | MultiArch cluster     | 3 control-plane and 4 worker nodes                                                            |
| **OCP & OpenShift Virtualization Version(s)** | OCP 4.21, CNV-4.21    | OCP 4.21 and OpenShift Virtualization 4.21                                                    |
| **CPU Virtualization**                        | Multi-arch cluster    | 3 amd64 control-plane, 2 amd64 workers, and 2 arm64 workers                                   |
| **Compute Resources**                         | N/A                   | [e.g., Minimum per worker node: 8 vCPUs, 32GB RAM]                                            |
| **Special Hardware**                          | N/A                   | [e.g., Specific NICs for SR-IOV, GPU etc.]                                                     |
| **Storage**                                   | io2-csi storage class | AWS EBS io2 CSI driver                                                                        |
| **Network**                                   | N/A                   | [e.g., OVN-Kubernetes (default), Secondary Networks, Network Plugins, IPv4, IPv6, dual-stack] |
| **Required Operators**                        | N/A                   | [e.g., NMState Operator]                                                                      |
| **Platform**                                  | N/A                   | [e.g., Bare metal, AWS, Azure, GCP etc.]                                                       |
| **Special Configurations**                    | N/A                   | [e.g., Disconnected/air-gapped cluster, Proxy environment, FIPS mode enabled]                 |

#### **4.1. Testing Tools & Frameworks**

Document any **new or additional** testing tools, frameworks, or infrastructure required specifically
for this feature. **Note:** Only list tools that are **new** or **different** from standard testing infrastructure.
Leave empty if using standard tools.

| Category           | Tools/Frameworks |
| :----------------- | :--------------- |
| **Test Framework** |                  |
| **CI/CD**          |                  |
| **Other Tools**    |                  |

#### **5. Entry Criteria**

The following conditions must be met before testing can begin:

- [ ] Requirements and design documents are **approved and merged**
- [V] Test environment can be **set up and configured** (see Section II.4 - Test Environment)
- [ ] Multi-CPU architecture support enabled in openshift-virtualization repo

#### **6. Risks**

Document specific risks for this feature. If a risk category is not applicable, mark as "N/A" with
justification in mitigation strategy.

**Note:** Empty "Specific Risk" cells mean this must be filled. "N/A" means explicitly not applicable
with justification.

| Risk Category        | Specific Risk for This Feature                                                     | Mitigation Strategy                                                                            | Status |
| :------------------- | :--------------------------------------------------------------------------------- | :--------------------------------------------------------------------------------------------- | :----- |
| Timeline/Schedule    | Code Freeze on Jan 12th                                                            | [Your specific mitigation, e.g., "Prioritize P1 scenarios, automate in parallel"]              | [ ]    |
| Test Coverage        | enable multi-arch cluster support is under WIP                                     | PR https://github.com/RedHatQE/openshift-virtualization-tests/pull/3147                        | [ ]    |
| Test Environment     | [Describe environment risks, e.g., "Requires GPU hardware, limited availability"]  | [Your mitigation, e.g., "Reserve GPU nodes early, schedule tests in advance"]                  | [ ]    |
| Untestable Aspects   | [List what cannot be tested, e.g., "Production scale with 10k VMs"]                | [Your mitigation, e.g., "Test at smaller scale, extrapolate results, prod monitoring"]         | [ ]    |
| Resource Constraints | [Describe resource issues, e.g., "Only 1 QE assigned, feature spans 3 components"] | [Your mitigation, e.g., "Focus automation on critical paths, coordinate with dev for testing"] | [ ]    |
| Dependencies         | [Describe dependency risks, e.g., "Depends on Storage team delivering feature X"]  | [Your mitigation, e.g., "Coordinate with Storage QE, have backup test plan"]                   | [ ]    |
| Other                | [Any other specific risks]                                                         | [Mitigation strategy]                                                                          | [ ]    |

#### **7. Known Limitations**

Testing on Container Disk VM is limited since, there's no defaulting of the architecture based on the containerdisk arch at the moment so VM won't schedule on expected architecture node unless manually providing spec.template.spec.architecture in the VM


### **III. Test Scenarios & Traceability**

This section links requirements to test coverage, enabling reviewers to verify all requirements are
tested.

| Requirement ID | Requirement Summary | Test Scenario(s)                                                               | Tier   | Priority |
| :------------- | :------------------ | :----------------------------------------------------------------------------- | :----- | :------- |
| [CNV-72102]    |                     | Deploy and Test with a Multi-Arch cluster with 4.21                            | Tier 2 | P2       |
| [CNV-74480]    |                     | Test updating amd64 cpuModel in HCO and check arm64 VM creations on ARM nodes. | Tier 2 | P0       |
| [CNV-75737]    |                     | Run Tier2 Tests on Multi-Arch Clusters (ARM64 and AMD64)                       | Tier 2 | P1       |
| [CNV-74481]    |                     | Update Tier2 automation to handle Multi-Arch scenarios                         | Tier 2 | P2       |
| [CNV-33896]    |                     | Run Conformance Tests on multi-arch cluster (ARM64 and AMD64)                  | Tier 1 | P1       |

---

### **IV. Sign-off and Approval**

This Software Test Plan requires approval from the following stakeholders:

* **Reviewers:**
  - dshchedr
  - vsibirsk
  - kbidarkar
  - SiboWang1997
  - jerry7z
  - SamAlber
* **Approvers:**
  - dshchedr
  - vsibirsk
