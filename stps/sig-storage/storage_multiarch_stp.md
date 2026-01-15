# Openshift-virtualization-tests Test plan

## CDI support for heterogeneous multi-arch clusters - Quality Engineering Plan

### **Metadata & Tracking**

| Field                  | Details                                                                                                                          |
|:---------------------- |:-------------------------------------------------------------------------------------------------------------------------------- |
| **Enhancement(s)**     | [dic-on-heterogeneous-cluster](https://github.com/kubevirt/enhancements/tree/main/veps/sig-storage/dic-on-heterogeneous-cluster) |
| **Feature in Jira**    | [VIRTSTRAT-494](https://issues.redhat.com/browse/VIRTSTRAT-494)                                                                  |
| **Jira Tracking**      | [CNV-73892](https://issues.redhat.com/browse/CNV-73892)                                                                          |
| **QE Owner(s)**        | Yan Du                                                                                                                           |
| **Owning SIG**         | sig-storage                                                                                                                      |
| **Participating SIGs** | sig-infra, sig-storage, sig-virt                                                                                                 |
| **Current Status**     | Draft                                                                                                                            |

---

**Document Conventions (if applicable):** [Define acronyms or terms specific to this document]

### **I. Motivation and Requirements Review (QE Review Guidelines)**

This section documents the mandatory QE review process. The goal is to understand the feature's value,
technology, and testability before formal test planning.

#### **1. Requirement & User Story Review Checklist**

<!-- **How to complete this checklist:**
1. **Done column**: Mark [x] when the check is complete
2. **Details/Notes column**: Summary of the topic (e.g., list key requirements, describe customer value, note acceptance criteria)
3. **Comments column**: Document any concerns, gaps, or follow-up items needed -->

| Check                                  | Done | Details/Notes                                                                                                                                                                                                                              | Comments |
|:-------------------------------------- |:---- |:------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |:-------- |
| **Review Requirements**                | [x]  | Reviewed the relevant requirements                                                                                                                                                                                                         |          |
| **Understand Value**                   | [x]  | CDI changes to support arch-specific registry imports for both pull modes                                                                                                                                                                  |          |
| **Customer Use Cases**                 | [x]  | VM creation with architecture-specific DataSources                                                                                                                                                                                         |          |
| **Testability**                        | [x]  | Requirements are testable and unambiguous                                                                                                                                                                                                   |          |
| **Acceptance Criteria**                | [x]  | When importing an image from a [OCI Image Index](https://specs.opencontainers.org/image-spec/image-index/), I want to optionally specify a `platform` field to influence which image variant is selected from the multi-platform manifest. |          |
| **Non-Functional Requirements (NFRs)** | [x]  | NFRs (Performance, Usability, Monitoring, Scalability) are out of scope for this test plan                                                                                                                                                 |          |

#### **2. Technology and Design Review**

<!-- **How to complete this checklist:**
1. **Done column**: Mark [x] when the review is complete
2. **Details/Notes column**: Summary of the item (e.g., list technology challenges, special environment needs, significant API changes)
3. **Comments column**: Note any blockers, risks, or items requiring follow-up -->

| Check                            | Done | Details/Notes                                                                                                                                                                                                                                                                                                                                                                                                                                              | Comments |
|:-------------------------------- |:---- |:---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |:-------- |
| **Developer Handoff/QE Kickoff** | [x]  | Discuss within team for the feature                                                                                                                                                                                                                                                                                                                                                                                                                        |          |
| **Technology Challenges**        | [x]  | Can use HA cluster, but should be verified on Multiarch cluster which is available only for 12 hours                                                                                                                                                                                                                                                                                                                                                       |          |
| **Test Environment Needs**       | [x]  | MultiArch cluster                                                                                                                                                                                                                                                                                                                                                                                                                                          |          |
| **API Extensions**               | [x]  | **HCO**: `status.nodeInfo` (controlPlaneArchitectures, workloadsArchitectures), `status.dataImportCronTemplates` (originalSupportedArchitectures, conditions)<br/> **SSP**: `enableMultipleArchitectures`, `cluster` fields (workloadArchitectures, controlPlaneArchitectures)<br/> **CDI**: `platform.architecture` field in `DataVolumeSourceRegistry`, arch-specific `DataSource` (`<name>-<arch>`), legacy `DataSource` redirects to arch-specific one |          |

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

  | Non-Goal                       | Rationale                                                                                          | PM/ Lead Agreement |
  |:------------------------------ |:-------------------------------------------------------------------------------------------------- |:------------------ |
  | Performance Testing            | Out of scope for this test plan                                                                    | [ ] Name/Date      |
  | Security Testing               | Out of scope for this test plan                                                                    | [ ] Name/Date      |
  | Usability testing              | Should be done by UI team                                                                          | [ ] Name/Date      |
  | Backward Compatibility Testing | VM creation using architecture-specific DataSources and legacy DataSource covered by SSP test plan | [ ] Name/Date      |

  #### **2. Test Strategy**

  <!-- The following test strategy considerations must be reviewed and addressed. Mark "Y" if applicable,
  "N/A" if not applicable (with justification in Comments). Empty cells indicate incomplete review. -->

  | Item                           | Description                                                                                                                                                  | Applicable (Y/N or N/A) | Comments                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
  |:------------------------------ |:------------------------------------------------------------------------------------------------------------------------------------------------------------ |:----------------------- |:----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
  | Functional Testing             | Validates that the new storage api                                                                                                                           | Y                       |                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
  | Automation Testing             | Ensures test cases are automated                                                                                                                             | Y                       |                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
  | Performance Testing            | Validates feature performance meets requirements (latency, throughput, resource usage)                                                                       | N/A                     |                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
  | Security Testing               | Verifies security requirements, RBAC, authentication, authorization, and vulnerability scanning                                                              | N/A                     |                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
  | Usability Testing              | Validates user experience, UI/UX consistency, and accessibility requirements. Does the feature require UI? If so, ensure the UI aligns with the requirements | N/A                     | Should be done by UI team                                                                                                                                                                                                                                                                                                                                                                                                                                               |
  | Compatibility Testing          | Ensures feature works across supported platforms, versions, and configurations                                                                               | N/A                     |                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
  | Regression Testing             | Verifies that new api changes do not break existing functionality                                                                                            | Y                       |                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
  | Upgrade Testing                | Validates upgrade paths from previous versions, data migration, and configuration preservation                                                               | Y                       |                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
  | Backward Compatibility Testing | Ensures feature maintains compatibility with previous API versions and configurations                                                                        | Y                       |                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
  | Dependencies                   | Dependent on deliverables from other components/products? Identify what is tested by which team.                                                             | N/A                     |                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
  | Cross Integrations             | Does the feature affect other features/require testing by other components? Identify what is tested by which team.                                           | Y                       | **IUO**: HCO node architecture tracking (`status.nodeInfo`), FG activation/propagation, new metrics & alerts, upgrade<br/> **SSP**: Templates creation & utilization, new SSP API (`enableMultipleArchitectures`, `cluster` fields)<br/> **Storage**: CDI-importer architecture selection, legacy `DataSource` backward compatibility, new CDI `platform` API<br/> **Virt**: VM scheduling to correct architecture nodes, VM migration between same-arch nodes, upgrade |
  | Monitoring                     | Does the feature require metrics and/or alerts?                                                                                                              | N/A                     |                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
  | Cloud Testing                  | Does the feature require multi-cloud platform testing? Consider cloud-specific features.                                                                     | N/A                     | not related to cloud                                                                                                                                                                                                                                                                                                                                                                                                                                                    |

  #### **3. Test Environment**

  <!-- **Note:** "N/A" means explicitly not applicable. Cannot leave empty cells. -->

  | Environment Component                         | Configuration            | Comments                                                      |
  |:--------------------------------------------- |:------------------------ |:------------------------------------------------------------- |
  | **Cluster Topology**                          | MultiArch cluster        | 3 control-plane and 3-4 worker nodes                          |
  | **OCP & OpenShift Virtualization Version(s)** | OCP 4.21, CNV-4.21       | OCP 4.21 and OpenShift Virtualization 4.21                    |
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

  | Category           | Tools/Frameworks  |
  |:------------------ |:----------------- |
  | **Test Framework** | MultiArch cluster |
  | **CI/CD**          |                   |
  | **Other Tools**    |                   |

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

  | Risk Category        | Specific Risk for This Feature                          | Mitigation Strategy | Status |
  |:-------------------- |:------------------------------------------------------- |:------------------- |:------ |
  | Timeline/Schedule    | Code-Freeze                                             |                     | [ ]    |
  | Test Coverage        |                                                         |                     | [ ]    |
  | Test Environment     | [CNV-76482](https://issues.redhat.com/browse/CNV-76482) |                     | [ ]    |
  | Untestable Aspects   | N/A                                                     |                     | [ ]    |
  | Resource Constraints | N/A                                                     |                     | [ ]    |
  | Dependencies         | N/A                                                     |                     | [ ]    |
  | Known Bugs           | [CNV-75762](https://issues.redhat.com/browse/CNV-75762) |                     | [ ]    |

  #### **6. Known Limitations**

  <!-- Document any known limitations, constraints, or trade-offs in the feature implementation or testing approach.
  **Examples:**

- s390x is not testable due to hardware availability, the test will limit to amd64/arm64

---

### **III. Test Scenarios & Traceability**

<!-- This section links requirements to test coverage, enabling reviewers to verify all requirements are
tested. -->

<!-- **Requirement ID:**
- Use Jira issue key (e.g., CNV-12345)
- Each row should trace back to a specific testable requirement in Jira
**Requirement Summary:** Brief description from the Jira issue (user story format preferred) -->

| Requirement ID | Requirement Summary                                                             | Test Scenario(s)                                                                                                                              | Tier   | Priority |
|:-------------- |:------------------------------------------------------------------------------- |:--------------------------------------------------------------------------------------------------------------------------------------------- |:------ |:-------- |
|                | Pull multi-arch image matching architecture with pull method Pod                | Verify the import succeeded with spec.registry.pullMethod: pod and spec.registry.platform.architecture: arm64 and                             | Tier 1 | P1       |
|                | Pull failed when multi-arch image with absent architecture with pull method Pod | Verify the import failed with spec.registry.pullMethod: pod and spec.registry.platform.architecture: absent                                   | Tier 1 | P0       |
|                | node selector for multi-arch image architecture with pull method Node           | Verify the import pod label has "Unschedulable" condition with spec.registry.pullMethod: node and spec.registry.platform.architecture: absent | Tier 1 | P0       |
|                | DataSource pointing to another DataSource                                       | Verify the import succeeded when define the DataSource to another DataSource                                                                  | Tier 1 | P1       |

---

### **IV. Sign-off and Approval**

This Software Test Plan requires approval from the following stakeholders:

* **Reviewers:**
  - [Name / @github-username]
  - [Name / @github-username]
* **Approvers:**
  - [Name / @github-username]
  - [Name / @github-username]
