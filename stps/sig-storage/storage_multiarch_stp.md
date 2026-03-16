# Openshift-virtualization-tests Test plan

## CDI support for heterogeneous multi-arch clusters - Quality Engineering Plan

### **Metadata & Tracking**

| Field                  | Details                                                                                                                          |
|:-----------------------|:---------------------------------------------------------------------------------------------------------------------------------|
| **Enhancement(s)**     | [dic-on-heterogeneous-cluster](https://github.com/kubevirt/enhancements/tree/main/veps/sig-storage/dic-on-heterogeneous-cluster) |
| **Feature in Jira**    | [VIRTSTRAT-494](https://issues.redhat.com/browse/VIRTSTRAT-494)                                                                  |
| **Jira Tracking**      | [CNV-73892](https://issues.redhat.com/browse/CNV-73892)                                                                          |
| **QE Owner(s)**        | Yan Du                                                                                                                           |
| **Owning SIG**         | sig-storage                                                                                                                      |
| **Participating SIGs** | sig-storage                                                                                                                      |
| **Current Status**     | draft                                                                                                                            |

**Document Conventions:**
- **CDI**: Containerized Data Importer - responsible for importing VM disk images into Kubernetes
- **DIC**: DataImportCron - automates periodic import of VM images
- **SSP**: Scheduling, Scale and Performance Operator - manages VM templates and common resources
- **HCO**: Hyperconverged Cluster Operator - orchestrates OpenShift Virtualization deployment
- **IUO**: Integration/Update Operator - handles feature gate management and upgrades
- **VEP**: Virtualization Enhancement Proposal - design document for new features
- **Pull Method**: Mechanism for importing images (Pod-based or Node-based)

### **I. Motivation and Requirements Review (QE Review Guidelines)**

This section documents the mandatory QE review process. The goal is to understand the feature's value,
technology, and testability before formal test planning.

#### **1. Requirement & User Story Review Checklist**

<!-- **How to complete this checklist:**
1. **Done column**: Mark [x] when the check is complete
2. **Details/Notes column**: Summary of the topic (e.g., list key requirements, describe customer value, note acceptance criteria)
3. **Comments column**: Document any concerns, gaps, or follow-up items needed -->

| Check                                  | Done | Details/Notes                                                                                                                                                                           | Comments |
|:---------------------------------------|:-----|:----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:---------|
| **Review Requirements**                | [x]  | Reviewed the relevant requirements.                                                                                                                                                     |          |
| **Understand Value**                   | [x]  | Confirmed clear user stories and understood.  <br/>Understand the difference between U/S and D/S requirements<br/> **What is the value of the feature for RH customers**.               |          |
| **Customer Use Cases**                 | [x]  | Ensured requirements contain relevant **customer use cases**.                                                                                                                           |          |
| **Testability**                        | [x]  | Confirmed requirements are **testable and unambiguous**.                                                                                                                                |          |
| **Acceptance Criteria**                | [x]  | Ensured acceptance criteria are **defined clearly** (clear user stories; D/S requirements clearly defined in Jira).                                                                     |          |
| **Non-Functional Requirements (NFRs)** | [x]  | Confirmed coverage for NFRs, including Performance, Security, Usability, Downtime, Connectivity, Monitoring (alerts/metrics), Scalability, Portability (e.g., cloud support), and Docs. |          |


#### **2. Technology and Design Review**

<!-- **How to complete this checklist:**
1. **Done column**: Mark [x] when the review is complete
2. **Details/Notes column**: Summary of the item (e.g., list technology challenges, special environment needs, significant API changes)
3. **Comments column**: Note any blockers, risks, or items requiring follow-up -->

| Check                            | Done | Details/Notes                                                                                                                                           | Comments |
|:---------------------------------|:-----|:--------------------------------------------------------------------------------------------------------------------------------------------------------|:---------|
| **Developer Handoff/QE Kickoff** | [x]  | A meeting where Dev/Arch walked QE through the design, architecture, and implementation details. **Critical for identifying untestable aspects early.** |          |
| **Technology Challenges**        | [x]  | Identified potential testing challenges related to the underlying technology.                                                                           |          |
| **Test Environment Needs**       | [x]  | Determined necessary **test environment setups and tools**.                                                                                             |          |
| **API Extensions**               | [x]  | Reviewed new or modified APIs and their impact on testing.                                                                                              |          |
| **Topology Considerations**      | [x]  | Evaluated multi-cluster, network topology, and architectural impacts.                                                                                   |          |


### **II. Software Test Plan (STP)**

This STP serves as the **overall roadmap for testing**, detailing the scope, approach, resources, and schedule.

#### **1. Scope of Testing**

<!-- Briefly describe what will be tested. The scope must **cover functional and non-functional requirements**.
Must ensure user stories are included and aligned to downstream user stories from Section I. -->

**Testing Goals**

<!-- Define specific, measurable testing objectives for this feature using **SMART criteria**
(Specific, Measurable, Achievable, Relevant, Time-bound).
Each goal should tie back to requirements from Section I and be independently verifiable.
**How to Define Good Testing Goals:**
- **Specific**: Clearly state what will be tested (not "test the feature" but "validate VM live migration
  with SR-IOV networks")
- **Measurable**: Define quantifiable success criteria (e.g., "95% of VM migrations complete within xxx seconds")
- **Achievable**: Realistic given resources and timeline
- **Relevant**: Directly supports feature acceptance criteria and user stories
- **Verifiable**: Can be objectively confirmed as complete
**Priority Levels:**
- **P0**: Blocking GA - must be complete before release
- **P1**: High priority - required for full feature coverage
- **P2**: Nice-to-have - can be deferred if timeline constraints exist -->

<!-- **Example - Functional Goals**:
- **[P0]** Verify VM live migration completes successfully with new network binding plugin across
  OVN-Kubernetes and secondary networks
- **[P1]** Validate hotplug/hotunplug operations work with new storage class without VM restart
- **[P0]** Confirm RBAC permissions model correctly restricts non-admin users from accessing
  cluster-wide configuration API
- **[P2]** Validate new metrics with real-time VM performance data (CPU, memory, network, disk I/O)
**Example - Quality Goals**:
- **[P0]** Verify VM live migration completes in <30 seconds for VMs with <8GB memory
  (performance baseline from VEP-XXXX)
- **[P1]** Confirm feature operates correctly in disconnected/air-gapped environments with local
  image registry
- **[P0]** Validate zero data loss during live migration under network latency up to 100ms
**Example - Integration Goals**:
- **[P0]** Verify backward compatibility: upgrade from OCP 4.19 to 4.20 preserves existing VM
  configurations without manual intervention
- **[P0]** Confirm interoperability with OpenShift Service Mesh when VMs use Istio sidecar injection
- **[P1]** Test integration with OpenShift monitoring stack: metrics appear in Prometheus,
  alerts fire correctly in Alertmanager -->

**Functional Goals**:

- **[P0]** Verify multi-arch image matching architecture with pull method Pod

- **[P0]** Verify multi-arch image matching architecture with pull method Node

- **[P0]** Validate DataSource pointing to another DataSource

**Out of Scope (Testing Scope Exclusions)**


| Out-of-Scope Item               | Rationale                                                                                           | PM/ Lead Agreement |
|:--------------------------------|:----------------------------------------------------------------------------------------------------|:-------------------|
| Performance Testing             | Out of scope for this test plan                                                                     | [ ] Name/Date      |
| Security Testing                | Out of scope for this test plan                                                                     | [ ] Name/Date      |
| Usability testing               | Should be done by UI team                                                                           | [ ] Name/Date      |
| Backward Compatibility Testing  | VM creation using architecture-specific DataSources and legacy DataSource covered by SSP test plan  | [ ] Name/Date      |

#### **2. Test Strategy**

  <!-- The following test strategy considerations must be reviewed and addressed. Mark "Y" if applicable,
  "N/A" if not applicable (with justification in Comments). Empty cells indicate incomplete review. -->


| Item                           | Description                                                                                                                                                  | Applicable (Y/N or N/A) | Comments                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
|:-------------------------------|:-------------------------------------------------------------------------------------------------------------------------------------------------------------|:------------------------|:-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Functional Testing             | Validates that the new storage API works for both pull modes                                                                                                 | Y                       | Validates that the new storage API                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| Automation Testing             | Ensures test cases are automated for continuous integration and regression coverage                                                                          | Y                       | Ensures test cases are automated                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| Performance Testing            | Validates feature performance meets requirements (latency, throughput, resource usage)                                                                       | N                       | No performance testing currently                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| Security Testing               | Verifies security requirements, RBAC, authentication, authorization, and vulnerability scanning                                                              | N                       | Not security relevant                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| Usability Testing              | Validates user experience, UI/UX consistency, and accessibility requirements. Does the feature require UI? If so, ensure the UI aligns with the requirements | N                       | UI testing will be covered by UI team                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| Compatibility Testing          | Ensures feature works across supported platforms, versions, and configurations                                                                               | N                       | No compatibility testing currently                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| Regression Testing             | Verifies that new changes do not break existing functionality                                                                                                | Y                       | Verifies that new api changes do not break existing functionality                                                                                                                                                                                                                                                                                                                                                                                                        |
| Upgrade Testing                | Validates upgrade paths from previous versions, data migration, and configuration preservation                                                               | Y                       | Validates upgrade paths from previous versions, data migration, and configuration preservation                                                                                                                                                                                                                                                                                                                                                                           |
| Backward Compatibility Testing | Ensures feature maintains compatibility with previous API versions and configurations                                                                        | Y                       | Ensures feature maintains compatibility with previous API versions and configurations                                                                                                                                                                                                                                                                                                                                                                                    |
| Dependencies                   | Dependent on deliverables from other components/products? Identify what is tested by which team.                                                             | N                       | Dependent on deliverables from other components/products? Identify what is tested by which team                                                                                                                                                                                                                                                                                                                                                                          |
| Cross Integrations             | Does the feature affect other features/require testing by other components? Identify what is tested by which team.                                           | Y                       | **IUO**: HCO node architecture tracking (`status.nodeInfo`), FG activation/propagation, new metrics & alerts, upgrade<br/> **SSP**: Templates creation & utilization, new SSP API (`enableMultipleArchitectures`, `cluster` fields)<br/> **Storage**: CDI-importer architecture selection, legacy `DataSource` backward compatibility, new CDI `platform` API<br/> **Virt**: VM scheduling to correct architecture nodes, VM migration between same-arch nodes, upgrade  |
| Monitoring                     | Does the feature require metrics and/or alerts?                                                                                                              | N                       | No Monitoring testing currently                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| Cloud Testing                  | Does the feature require multi-cloud platform testing? Consider cloud-specific features.                                                                     | N                       | The testing is limited to AWS clusters                                                                                                                                                                                                                                                                                                                                                                                                                                   |


#### **3. Test Environment**

  <!-- **Note:** "N/A" means explicitly not applicable. Cannot leave empty cells. -->



| Environment Component                         | Configuration            | Specification Examples                                        |
|:----------------------------------------------|:-------------------------|:--------------------------------------------------------------|
| **Cluster Topology**                          | MultiArch cluster        | No specific Cluster Topology required                         |
| **OCP & OpenShift Virtualization Version(s)** | OCP 4.22, CNV-4.22       | OCP 4.22 with OpenShift Virtualization 4.22 on AWS            |
| **CPU Virtualization**                        | Multi-arch cluster       | 3 amd64 control-plane, 2 amd64 workers, and 1-2 arm64 workers |
| **Compute Resources**                         | N/A                      | No special compute requirements                               |
| **Special Hardware**                          | N/A                      | No special hardware required                                  |
| **Storage**                                   | io2-csi storage class    | AWS EBS io2 CSI driver                                        |
| **Network**                                   | OVN-Kubernetes (default) | No special network requirements                               |
| **Required Operators**                        | N/A                      | N/A                                                           |
| **Platform**                                  | AWS                      | ARM64 workers available on AWS                                |
| **Special Configurations**                    | N/A                      | No special configurations required                            |

#### **3.1. Testing Tools & Frameworks**

  <!-- Document any **new or additional** testing tools, frameworks, or infrastructure required specifically
  for this feature. **Note:** Only list tools that are **new** or **different** from standard testing infrastructure.
  Leave empty if using standard tools. -->

| Category           | Tools/Frameworks   |
|:-------------------|:-------------------|
| **Test Framework** | MultiArch cluster  |
| **CI/CD**          |                    |
| **Other Tools**    |                    |

#### **4. Entry Criteria**

  The following conditions must be met before testing can begin:

- [x] VEP [dic-on-heterogeneous-cluster](https://github.com/kubevirt/enhancements/tree/main/veps/sig-storage/dic-on-heterogeneous-cluster) is approved and merged

- [x] CDI support arch-specific registry imports

- [ ] Test environment (MultiArch cluster) can be set up and configured

- [x] Feature gate enableMultiArchBootImageImport can be enabled



#### **5. Risks**

  <!-- Document specific risks for this feature. If a risk category is not applicable, mark as "N/A" with
  justification in mitigation strategy.
  **Note:** Empty "Specific Risk" cells mean this must be filled. "N/A" means explicitly not applicable
  with justification. -->


| Risk Category        | Specific Risk for This Feature | Mitigation Strategy | Status |
|:---------------------|:-------------------------------|:--------------------|:-------|
| Timeline/Schedule    | N/A                            |                     | [ ]    |
| Test Coverage        | N/A                            |                     | [ ]    |
| Test Environment     | N/A                            |                     | [ ]    |
| Untestable Aspects   | N/A                            |                     | [ ]    |
| Resource Constraints | N/A                            |                     | [ ]    |
| Dependencies         | N/A                            |                     | [ ]    |
| Other                | N/A                            |                     | [ ]    |

#### **6. Known Limitations**

<!-- Document any known limitations, constraints, or trade-offs in the feature implementation or testing approach.

**Examples:**
- Feature does not support IPv6 (only IPv4)
- No support for ARM64 architecture in this release -->

---

### **III. Test Scenarios & Traceability**

<!-- This section links requirements to test coverage, enabling reviewers to verify all requirements are
tested. -->

<!-- **Requirement ID:**
- Use Jira issue key (e.g., CNV-12345)
- Each row should trace back to a specific testable requirement in Jira
**Requirement Summary:** Brief description from the Jira issue (user story format preferred) -->

| Requirement ID | Requirement Summary                                                             | Test Scenario(s)                                                                                                                              | Tier   | Priority |
|:---------------|:--------------------------------------------------------------------------------|:----------------------------------------------------------------------------------------------------------------------------------------------|:-------|:---------|
| TBD            | Pull multi-arch image matching architecture with pull method Pod                | Verify the import succeeded with spec.registry.pullMethod: pod and spec.registry.platform.architecture: arm64                                 | Tier 1 | P0       |
| TBD            | Pull failed when multi-arch image with absent architecture with pull method Pod | Verify the import failed with spec.registry.pullMethod: pod and spec.registry.platform.architecture: absent                                   | Tier 1 | P1       |
| TBD            | node selector for multi-arch image architecture with pull method Node           | Verify the import pod label has "Unschedulable" condition with spec.registry.pullMethod: node and spec.registry.platform.architecture: absent | Tier 1 | P1       |
| TBD            | DataSource pointing to another DataSource                                       | Verify the import succeeded when define the DataSource to another DataSource                                                                  | Tier 1 | P1       |
| TBD            | Cross-architecture VM cloning                                                   | Clone amd64 VM, verify clone uses amd64 DataSource. Attempt cross-arch clone, verify appropriate error                                        | Tier 2 | P1       |

---

### **IV. Sign-off and Approval**

This Software Test Plan requires approval from the following stakeholders:

* **Reviewers:**
  - [Name / @github-username]
  - [Name / @github-username]
* **Approvers:**
  - [Name / @github-username]
  - [Name / @github-username]
