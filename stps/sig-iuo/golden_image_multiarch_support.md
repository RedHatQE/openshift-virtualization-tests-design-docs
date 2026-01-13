# Openshift-virtualization-tests Test plan

## HCO support for heterogeneous multi-arch clusters (golden images support) - Quality Engineering Plan

### **Metadata & Tracking**

| Field                  | Details                                                                                                                          |
|:-----------------------|:---------------------------------------------------------------------------------------------------------------------------------|
| **Enhancement(s)**     | [dic-on-heterogeneous-cluster](https://github.com/kubevirt/enhancements/tree/main/veps/sig-storage/dic-on-heterogeneous-cluster) |
| **Feature in Jira**    | [VIRTSTRAT-494](https://issues.redhat.com/browse/VIRTSTRAT-494)                                                                  |
| **Jira Tracking**      | [CNV-67900](https://issues.redhat.com/browse/CNV-67900)                                                                          |
| **QE Owner(s)**        | Harel Meir                                                                                                                       |
| **Owning SIG**         | sig-iuo                                                                                                                          |
| **Participating SIGs** | sig-infra, sig-storage, sig-virt                                                                                                 |
| **Current Status**     | Draft                                                                                                                            |

---

**Document Conventions (if applicable):** [Define acronyms or terms specific to this document]

| Term                  | Definition                                                                                               |
|:----------------------|:---------------------------------------------------------------------------------------------------------|
| **MultiArch cluster** | Heterogeneous cluster with 3 amd64 control-plane nodes, 2 amd64 worker nodes, and 1-2 arm64 worker nodes |
| **HA cluster**        | Homogeneous cluster with 3 control-plane nodes and 3 amd64 worker nodes                                  |
| **MultiArch FG**      | `enableMultiArchBootImageImport` feature gate in HCO CR.                                                 |
| **Related resources** | Golden image associated resources: `DataImportCron`, `DataSource`, `DataVolume`, `VolumeSnapshot`        |
| **nodeInfo**          | HCO status field tracking cluster architectures (`status.nodeInfo`)                                      |

### **Feature Overview**

<!-- Provide a brief (2-4 sentences) description of the feature being tested.
Include: what it does, why it matters to customers, and key technical components. -->

This feature enables golden images support for heterogeneous clusters, where nodes may have different CPU architectures. It allows customers to create persistent virtual machines with specific architectures by automatically managing architecture-specific `DataImportCron` and `DataSource` resources for each supported architecture in the cluster. The feature is controlled by the `enableMultiArchBootImageImport` feature gate in the HyperConverged CR, and involves coordination between HCO (which tracks cluster node architectures), SSP (which creates architecture-specific templates), and CDI (which imports the correct architecture-specific images).

---

### **I. Motivation and Requirements Review (QE Review Guidelines)**

This section documents the mandatory QE review process. The goal is to understand the feature's value,
technology, and testability before formal test planning.

#### **1. Requirement & User Story Review Checklist**

<!-- **How to complete this checklist:**
1. **Done column**: Mark [x] when the check is complete
2. **Details/Notes column**: Summary of the topic (e.g., list key requirements, describe customer value, note acceptance criteria)
3. **Comments column**: Document any concerns, gaps, or follow-up items needed -->

| Check                                  | Done | Details/Notes                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             | Comments                         |
|:---------------------------------------|:-----|:----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:---------------------------------|
| **Review Requirements**                | [x]  | - Nodes must be properly labeled to differentiate supported architectures<br/> - Allow migration across same-arch nodes<br/> - ARM + x86 workload observability<br/> -	VMs must only run on nodes supporting their architecture (e.g., ARM VMs on ARM nodes)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |                                  |
| **Understand Value**                   | [x]  | **User Stories & Value:**<br/> 1. *As a VM creator*, I want to create VMs with specific architectures to run architecture-specific applications. **Value**: Enable users to create persistent VMs with specific architectures on heterogeneous clusters.<br/> 2. *As a cluster admin*, I want to define custom golden images with multi-architecture support. **Value**: Allow users to define custom golden images with multi-architecture support.<br/> 3. *As a cluster admin*, I want custom golden images for specific architectures ensuring VMs run only on matching nodes. **Value**: Reliable VM deployment by automatically matching image architectures to compatible node hardware without breaking existing workflows.<br/> 4. *As a VM creator*, I want my existing tools and scripts to continue working without changes. **Value**: Backward compatibility for users with existing scripts/tools referencing specific DataSource CRs.     |                                  |
| **Customer Use Cases**                 | [x]  | **UC1 - Hybrid Development/Testing**: Developer builds app targeting x86 servers and ARM edge devices, running test VMs for both architectures in a single cluster.<br/> **UC2 - Edge + Data Center Integration**: Operator provisions ARM VMs for edge workloads and x86 VMs for core workloads within the same management plane.<br/> **UC3 - ISV Application Validation**: QA team runs ARM VM test environments in the same cluster used for x86-based CI/CD pipelines.                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |                                  |
| **Testability**                        | [X]  | Everything is testable, despite upgrade to a version which this FG enabled by default.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    | Should be done in 4.22 timeframe |
| **Acceptance Criteria**                | [x]  | - HCO must consistently report accurate node architectures<br/> - common golden images should only be annotated with architectures that are actually supported<br/> - Related resources should be created only for golden images annotated with architectures that are actually supported<br/> - custom golden images without arch-annotation should be backward-compatible<br/>-Non supported architectures shouldn't result in resource creation<br/>-Legacy Datasources should be backward-compatible<br/>- Trigger alert when a golden image is annotated with an unsupported architecture<br/> - Trigger alert when running on a multi-arch cluster while Multiarch FG is disabled<br/> - Trigger alert when a custom golden image lacks an architecture annotation<br/> - VMs migrate across worker nodes of the same architecture during upgrades                                                                                                  |                                  |
| **Non-Functional Requirements (NFRs)** | [x]  | - **Usability**: New boot sources and VMs creation<br/> - **Monitoring**: 3 new alerts<br/> - **Regression**: Run IUO T2 tests (must-gather, nodeplacement, golden images tests in particular)<br/> - **Doc**: Should be documented by doc team                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |                                  |

#### **2. Technology and Design Review**

<!-- **How to complete this checklist:**
1. **Done column**: Mark [x] when the review is complete
2. **Details/Notes column**: Summary of the item (e.g., list technology challenges, special environment needs, significant API changes)
3. **Comments column**: Note any blockers, risks, or items requiring follow-up -->

| Check                            | Done | Details/Notes                                                                                                                                                                                                                                                                                                                                                                                                                                              | Comments                                               |
|:---------------------------------|:-----|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:-------------------------------------------------------|
| **Developer Handoff/QE Kickoff** | [x]  | Met with Nahshon from HCO team                                                                                                                                                                                                                                                                                                                                                                                                                             |                                                        |
| **Technology Challenges**        | [x]  | Can use HA cluster, but should be verified on Multiarch cluster which is available only for 12 hours                                                                                                                                                                                                                                                                                                                                                       | Initial testing on HA, final verification on Multiarch |
| **Test Environment Needs**       | [x]  | MultiArch cluster, HA cluster                                                                                                                                                                                                                                                                                                                                                                                                                              |                                                        |
| **API Extensions**               | [x]  | **HCO**: `status.nodeInfo` (controlPlaneArchitectures, workloadsArchitectures), `status.dataImportCronTemplates` (originalSupportedArchitectures, conditions)<br/> **SSP**: `enableMultipleArchitectures`, `cluster` fields (workloadArchitectures, controlPlaneArchitectures)<br/> **CDI**: `platform.architecture` field in `DataVolumeSourceRegistry`, arch-specific `DataSource` (`<name>-<arch>`), legacy `DataSource` redirects to arch-specific one |                                                        |
| **Topology Considerations**      | [x]  | Related resources should be created per worker node architecture. Currently its ARM64 and AMD64.                                                                                                                                                                                                                                                                                                                                                           |                                                        |


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
- **[P0]** Verify HCO monitors the cluster's nodes architectures correctly, and updated in addition/removal of nodes.
- **[P0]** Verify golden images are annotated only with architectures that are actually supported in HCO+SSP.
- **[P0]** Verify related resources created only for golden images annotated with supported architecture, named with the architecture suffix, and are ready to use.
- **[P1]** Verify Golden images annotated only with unsupported architectures should present the fail status in HCO dataImportCronTemplates status.


**Monitoring Goals**:
- **[P1]** Verify alert fired when golden image is annotated with an unsupported architecture.
- **[P1]** Verify alert fired when running on a multi-arch cluster while Multiarch FG is disabled.
- **[P1]** Verify alert fired when a custom golden image lacks an architecture annotation

**Backward compatibility Goals**:
- **[P0]** Verify Legacy Datasources points to default arch-annotated Datasources.
- **[P0]** Verify nodePlacement affects related resources creation.

**Upgrade goals**
- **[P0]** Verify ARM64 and AMD64 vms are migrated across worker nodes of the same architecture during upgrades
- **[P0]** Verify related resources preserved after upgrade.
- **[P1]** Verify the functional test post-upgrade to version when FG is enabled by default.




**Out of Scope (Testing Scope Exclusions)**

<!-- Explicitly document what is **out of scope** for testing.
**Critical:** All out-of-scope items require explicit stakeholder agreement to prevent "I assumed you were testing
that" issues; each out-of-scope item must have PM/Lead sign-off.

- Items without stakeholder agreement are considered **risks** and must be escalated
- Review the items during Developer Handoff/QE Kickoff meeting

**Note:** Replace example rows with your actual out-of-scope items. -->

| Non-Goal                         | Rationale                                                            | PM/ Lead Agreement |
|:---------------------------------|:---------------------------------------------------------------------|:-------------------|
| Update existing VM               | If a VM is already running, it won't use the arch-specific resources | [ ] Name/Date      |
| Performance Testing              | Feature not scale related                                            | [ ] Name/Date      |
| Security Testing                 | Feature not security related                                         | [ ] Name/Date      |
| Usability testing                | Should be done by UI team                                            | [ ] Name/Date      |
| Compatibility                    | Should be done by Virt/SSP team(create vms from multiple archs)      | [ ] Name/Date      |
| Templates creation & utilization | Should be done by SSP team                                           | [ ] Name/Date      |
| Imports & datasource new API     | Should be done by Storage team                                       | [ ] Name/Date      |
| Testing with s390x architecture  | The feature is "Multiarch Support enablement for ARM"                | [ ] Name/Date      |

#### **2. Test Strategy**

<!-- The following test strategy considerations must be reviewed and addressed. Mark "Y" if applicable,
"N/A" if not applicable (with justification in Comments). Empty cells indicate incomplete review. -->

| Item                           | Description                                                                                                                                                  | Applicable (Y/N or N/A) | Comments                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
|:-------------------------------|:-------------------------------------------------------------------------------------------------------------------------------------------------------------|:------------------------|:------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Functional Testing             | Validates that the feature works according to specified requirements and user stories                                                                        | Y                       | nodes architecture monitoring, arch-annotations, related resources creation                                                                                                                                                                                                                                                                                                                                                                                             |
| Automation Testing             | Ensures test cases are automated for continuous integration and regression coverage                                                                          | Y                       | All test cases should be automated at openshift-virtualization-tests repo.                                                                                                                                                                                                                                                                                                                                                                                              |
| Performance Testing            | Validates feature performance meets requirements (latency, throughput, resource usage)                                                                       | N/A                     | Not related to scale.                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| Security Testing               | Verifies security requirements, RBAC, authentication, authorization, and vulnerability scanning                                                              | N/A                     | Not related to security.                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| Usability Testing              | Validates user experience, UI/UX consistency, and accessibility requirements. Does the feature require UI? If so, ensure the UI aligns with the requirements | Y                       | [UI/UX design doc](https://docs.google.com/document/d/18UKIXiAlyLTABQZdvDD5N85A6uM2CdBbif4eN1dVj-0/edit?usp=sharing) specify requirements.<br/>Done by UI team [CNV-62535](https://issues.redhat.com/browse/CNV-62535)                                                                                                                                                                                                                                                  |
| Compatibility Testing          | Ensures feature works across supported platforms, versions, and configurations                                                                               | N/A                     | Should be done by SSP/Virt team                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| Regression Testing             | Verifies that new changes do not break existing functionality                                                                                                | N/A                     |                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| Upgrade Testing                | Validates upgrade paths from previous versions, data migration, and configuration preservation                                                               | Y                       | VMs migrated and updated successfully, related resources preserved.                                                                                                                                                                                                                                                                                                                                                                                                     |
| Backward Compatibility Testing | Ensures feature maintains compatibility with previous API versions and configurations                                                                        | Y                       | Legacy Datasource pointers, custom golden images without arch annotation.                                                                                                                                                                                                                                                                                                                                                                                               |
| Dependencies                   | Dependent on deliverables from other components/products? Identify what is tested by which team.                                                             | N/A                     |                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| Cross Integrations             | Does the feature affect other features/require testing by other components? Identify what is tested by which team.                                           | Y                       | **IUO**: HCO node architecture tracking (`status.nodeInfo`), FG activation/propagation, new metrics & alerts, upgrade<br/> **SSP**: Templates creation & utilization, new SSP API (`enableMultipleArchitectures`, `cluster` fields)<br/> **Storage**: CDI-importer architecture selection, legacy `DataSource` backward compatibility, new CDI `platform` API<br/> **Virt**: VM scheduling to correct architecture nodes, VM migration between same-arch nodes, upgrade |
| Monitoring                     | Does the feature require metrics and/or alerts?                                                                                                              | Y                       | [`HCOMultiArchGoldenImagesDisabled`](https://kubevirt.io/monitoring/runbooks/HCOMultiArchGoldenImagesDisabled.html),<br/> [`HCOGoldenImageWithNoArchitectureAnnotation`](https://kubevirt.io/monitoring/runbooks/HCOGoldenImageWithNoArchitectureAnnotation),<br/> [`HCOGoldenImageWithNoSupportedArchitecture`](https://kubevirt.io/monitoring/runbooks/HCOGoldenImageWithNoSupportedArchitecture)                                                                     |
| Cloud Testing                  | Does the feature require multi-cloud platform testing? Consider cloud-specific features.                                                                     | N/A                     | not related to cloud                                                                                                                                                                                                                                                                                                                                                                                                                                                    |

#### **3. Test Environment**

<!-- **Note:** "N/A" means explicitly not applicable. Cannot leave empty cells. -->

| Environment Component                         | Configuration            | Comments                                                      |
|:----------------------------------------------|:-------------------------|:--------------------------------------------------------------|
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
|:-------------------|:------------------|
| **Test Framework** | MultiArch cluster |
| **CI/CD**          |                   |
| **Other Tools**    |                   |

#### **4. Entry Criteria**

The following conditions must be met before testing can begin:

- [X] VEP [dic-on-heterogeneous-cluster](https://github.com/kubevirt/enhancements/tree/main/veps/sig-storage/dic-on-heterogeneous-cluster) is **approved and merged**
- [x] Test environment (MultiArch cluster) can be **set up and configured**
- [ ] Multi-CPU architecture support enabled in openshift-virtualization repo

#### **5. Risks**

<!-- Document specific risks for this feature. If a risk category is not applicable, mark as "N/A" with
justification in mitigation strategy.

**Note:** Empty "Specific Risk" cells mean this must be filled. "N/A" means explicitly not applicable
with justification. -->

| Risk Category                      | Specific Risk for This Feature                                                                                                                                                                                                                                                                                                                                                                                                      | Mitigation Strategy                                                                                                 | Status |
|:-----------------------------------|:------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:--------------------------------------------------------------------------------------------------------------------|:-------|
| Timeline/Schedule                  | Code-Freeze this week                                                                                                                                                                                                                                                                                                                                                                                                               | Prioritize HCO-specific testing this week. Upgrade automation can wait, since its impacting 4.22 anyway             | [ ]    |
| Test Coverage                      |                                                                                                                                                                                                                                                                                                                                                                                                                                     |                                                                                                                     | [X]    |
| Test Environment                   | Requires additional ARM64 workers node - [Jira ticket](https://issues.redhat.com/browse/CNV-73894)                                                                                                                                                                                                                                                                                                                                  | Can be done manually                                                                                                | [ ]    |
| Untestable Aspects                 |                                                                                                                                                                                                                                                                                                                                                                                                                                     |                                                                                                                     | [X]    |
| Resource Constraints               | N/A                                                                                                                                                                                                                                                                                                                                                                                                                                 | N/A                                                                                                                 | [ ]    |
| Dependencies                       | Allowing multi-cpu architecture on openshift-virtualization-tests                                                                                                                                                                                                                                                                                                                                                                   | Review the [PR](https://github.com/RedHatQE/openshift-virtualization-tests/pull/3147) whenever its ready to review. | [ ]    |
| Blocker Bug for legacy DataSources | [CNV-75762](https://issues.redhat.com/browse/CNV-75762)                                                                                                                                                                                                                                                                                                                                                                             | on POST - Storage QE to verify                                                                                      | [ ]    |
| Other non-blocker bugs             | 1. [[UI] architecture is incorrect for fedora arm and inconsistent on UI for other os](https://issues.redhat.com/browse/CNV-68981)<br/> 2. [[Storage] Arch-specific DataSources (arm64) persist after removing arm64 nodes](https://issues.redhat.com/browse/CNV-68996)<br/> 3. [[Storage] Bootable volumes are re-imported after set enableMultiArchBootImageImport to true for AMD64](https://issues.redhat.com/browse/CNV-75084) |                                                                                                                     | [ ]    |

#### **6. Known Limitations**

<!-- Document any known limitations, constraints, or trade-offs in the feature implementation or testing approach.

**Examples:**
- Feature does not support IPv6 (only IPv4)
- No support for ARM64 architecture in this release -->

- Existing VMs are not updated: VMs that are already running will not automatically use new architecture-specific resources. Users must recreate VMs to take advantage of new resources.
- Platform variant format not supported: Formats like `linux/arm64/v8` are not supported at this time; this may be enhanced in future releases if needed.
- Architecture validation not performed: The system does not validate custom golden image architectures. It is the user's responsibility to ensure correct configuration.



---

### **III. Test Scenarios & Traceability**

<!-- This section links requirements to test coverage, enabling reviewers to verify all requirements are
tested. -->

<!-- **Requirement ID:**
- Use Jira issue key (e.g., CNV-12345)
- Each row should trace back to a specific testable requirement in Jira

**Requirement Summary:** Brief description from the Jira issue (user story format preferred) -->

| Requirement ID | Requirement Summary                                                                                                     | Test Scenario(s)                                                                                                                                        | Tier   | Priority |
|:---------------|:------------------------------------------------------------------------------------------------------------------------|:--------------------------------------------------------------------------------------------------------------------------------------------------------|:-------|:---------|
|                | As a VM creator, I want to create VMs with specific architectures to run architecture-specific applications             | Verify HCO monitors the cluster's nodes architectures correctly, and updated in addition/removal of nodes                                               | Tier 1 | P0       |
|                | As a cluster admin, I want to define custom golden images with multi-architecture support                               | Verify golden images are annotated only with architectures that are actually supported in HCO+SSP                                                       | Tier 1 | P0       |
|                | As a VM creator/cluster admin, I want to create VMs / custom golden images for specific architectures                   | Verify related resources created only for golden images annotated with supported architecture, named with the architecture suffix, and are ready to use | Tier 2 | P0       |
|                | As a cluster admin, I want to define custom golden images for specific architectures ensuring VMs run on matching nodes | Verify golden images annotated only with unsupported architectures present the fail status in HCO dataImportCronTemplates status                        | Tier 1 | P1       |
|                | As a cluster admin, I want custom golden images for specific architectures ensuring VMs run only on matching nodes      | Verify alert fired when golden image is annotated with an unsupported architecture                                                                      | Tier 1 | P1       |
|                | As a VM creator/cluster admin, I want to create VMs / custom golden images for specific architectures                   | Verify alert fired when running on a multi-arch cluster while Multiarch FG is disabled                                                                  | Tier 1 | P1       |
|                | As a cluster admin, I want to define custom golden images with multi-architecture support                               | Verify alert fired when a custom golden image lacks an architecture annotation                                                                          | Tier 1 | P1       |
|                | As a VM creator, I want my existing tools and scripts to continue working without changes                               | Verify legacy Datasources point to default arch-annotated Datasources                                                                                   | Tier 2 | P0       |
|                | As a cluster admin, I want custom golden images for specific architectures ensuring VMs run only on matching nodes      | Verify nodePlacement affects related resources creation                                                                                                 | Tier 2 | P0       |
|                | As a VM creator, I want to create VMs with specific architectures to run architecture-specific applications             | Verify ARM64 and AMD64 VMs are migrated across worker nodes of the same architecture during upgrades                                                    | Tier 2 | P0       |
|                | As a VM creator/cluster admin, I want to create VMs / custom golden images for specific architectures                   | Verify related resources preserved after upgrade                                                                                                        | Tier 2 | P0       |
|                | As a VM creator/cluster admin, I want to create VMs / define custom golden images with multi-architecture support       | Verify the functional tests post-upgrade to version when Multiarch FG is enabled by default                                                             | Tier 2 | P1       |

---

### **IV. Sign-off and Approval**

This Software Test Plan requires approval from the following stakeholders:

* **Reviewers:**
  - [Name / @github-username]
  - [Name / @github-username]
* **Approvers:**
  - [Name / @github-username]
  - [Name / @github-username]
