# Openshift-virtualization-tests Test plan

## Multiarch Support enablement for ARM - Quality Engineering Plan

### **Metadata & Tracking**

| Field                  | Details                                                                                                                          |
|:-----------------------|:---------------------------------------------------------------------------------------------------------------------------------|
| **Enhancement(s)**     | [dic-on-heterogeneous-cluster](https://github.com/kubevirt/enhancements/tree/main/veps/sig-storage/dic-on-heterogeneous-cluster) |
| **Feature in Jira**    | [VIRTSTRAT-494 - Multiarch Support enablement for ARM](https://issues.redhat.com/browse/VIRTSTRAT-494)                           |
| **Jira Tracking**      | [CNV-67900](https://issues.redhat.com/browse/CNV-67900)                                                                          |
| **QE Owner(s)**        | Harel Meir                                                                                                                       |
| **Owning SIG**         | sig-iuo                                                                                                                          |
| **Participating SIGs** | sig-infra, sig-storage, sig-virt, sig-network                                                                                    |
| **Current Status**     | Review                                                                                                                           |

---

**Document Conventions (if applicable):** [Define acronyms or terms specific to this document]

| Term                  | Definition                                                                                             |
|:----------------------|:-------------------------------------------------------------------------------------------------------|
| **MultiArch cluster** | Heterogeneous cluster with 3 amd64 control-plane nodes, 2 amd64 worker nodes, and 2 arm64 worker nodes |
| **HA cluster**        | Homogeneous cluster with 3 control-plane nodes and 3 amd64 worker nodes                                |
| **MultiArch FG**      | `enableMultiArchBootImageImport` feature gate in HCO CR.                                               |
| **Related resources** | Golden image associated resources: `DataImportCron`, `DataSource`, `DataVolume`, `VolumeSnapshot`      |
| **nodeInfo**          | HCO status field tracking cluster architectures (`status.nodeInfo`)                                    |

### **Feature Overview**

<!-- Provide a brief (2-4 sentences) description of the feature being tested.
Include: what it does, why it matters to customers, and key technical components. -->

This feature enables ARM VM support in mixed-architecture (amd64/arm64) OpenShift Virtualization clusters. Architecture-specific golden image resources (`DataImportCron`, `DataSource`, `DataVolume`) are automatically managed per supported architecture, controlled by the `enableMultiArchBootImageImport` feature gate in HCO.
For 4.22 the feature gate is disabled by default, moving to enabled-by-default not earlier than 4.23. This STP covers sig-iuo responsibilities while documenting cross-SIG testing ownership.

---

### **I. Motivation and Requirements Review (QE Review Guidelines)**

This section documents the mandatory QE review process. The goal is to understand the feature's value,
technology, and testability before formal test planning.

#### **1. Requirement & User Story Review Checklist**

<!-- **How to complete this checklist:**
1. **Done column**: Mark [x] when the check is complete
2. **Details/Notes column**: Summary of the topic (e.g., list key requirements, describe customer value, note acceptance criteria)
3. **Comments column**: Document any concerns, gaps, or follow-up items needed -->

| Check                                  | Done | Details/Notes                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   | Comments                         |
|:---------------------------------------|:-----|:------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:---------------------------------|
| **Review Requirements**                | [x]  | - VMs can be created on Multiarch cluster using openshift-virtualization API's(e.g instancetypes,templates,golden-images,etc..)  <br/> - VMs must only run,managed and migrate on/to nodes supporting their architecture (e.g., ARM VMs on ARM nodes)<br/> - Multiarch Nodes labeled to differentiate supported architectures.<br/>- ARM-compatible images can be imported and run<br/>  - Unified monitoring and logging across Multiarch VMs                                                                                                  |                                  |
| **Understand Value**                   | [x]  | - Allow users to run ARM-based VMs alongside x86-based VMs within the same OpenShift Virtualization cluster, enabling a true multiarch environment.  <br/> - Allow users to define custom golden images with multi-architecture support for easier import & VMs creation.                                                                                                                                                                                                                                                                       |                                  |
| **Customer Use Cases**                 | [x]  | - **Developers**: Test and validate apps across x86 and ARM without separate infrastructure<br/> - **Admins**: Consolidate heterogeneous workloads on a single cluster<br/> - **Enterprises/ISVs**: Reduce cost and complexity when adopting ARM for edge and efficiency                                                                                                                                                                                                                                                                        |                                  |
| **Testability**                        | [X]  | Everything is testable, despite upgrade to a version which this FG enabled by default. (currently disabled by default)                                                                                                                                                                                                                                                                                                                                                                                                                          | Should be done in 4.23 timeframe |
| **Acceptance Criteria**                | [x]  | - HCO accurately reports node architectures <br/> - VMs can be created and managed on Multiarch cluster using standard OpenShift Virtualization APIs.  <br/>  - Golden images annotated and arch-specific related resources created only for supported architectures,named with arch suffix and ready to use<br/> - Unsupported-only arch annotations result in fail status in HCO `dataImportCronTemplates` - CDI pulls new images according to the image's arch and pullMethod(pod/node). <br/>- VMs are scheduled and migrated successfully. |                                  |
| **Non-Functional Requirements (NFRs)** | [x]  | - **Monitoring**: 3 new alerts and metrics<br/> - **Regression**: All teams should run T1+T2 tests on Multiarch cluster <br/>- **Upgrade**: VMs survive upgrade with correct architecture placement preserved<br/> - **UI**: New boot sources and VMs creation pages(templates/instancetype)<br/> - **Doc**: Drop the TP note from docs<br/>                                                                                                                                                                                                    |                                  |

#### **2. Technology and Design Review**

<!-- **How to complete this checklist:**
1. **Done column**: Mark [x] when the review is complete
2. **Details/Notes column**: Summary of the item (e.g., list technology challenges, special environment needs, significant API changes)
3. **Comments column**: Note any blockers, risks, or items requiring follow-up -->

| Check                            | Done | Details/Notes                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    | Comments                                               |
|:---------------------------------|:-----|:-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:-------------------------------------------------------|
| **Developer Handoff/QE Kickoff** | [x]  | Met with Nahshon from HCO team                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |                                                        |
| **Technology Challenges**        | [x]  | Can use HA cluster, but should be verified on Multiarch cluster which is available only for 12 hours                                                                                                                                                                                                                                                                                                                                                                                                                                             | Initial testing on HA, final verification on Multiarch |
| **Test Environment Needs**       | [x]  | MultiArch cluster, HA cluster                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |                                                        |
| **API Extensions**               | [x]  | **HCO**: `status.nodeInfo` (controlPlaneArchitectures, workloadsArchitectures), `status.dataImportCronTemplates` (originalSupportedArchitectures, conditions)<br/> **SSP**: `enableMultipleArchitectures`, `cluster` fields (workloadArchitectures, controlPlaneArchitectures)<br/> **CDI**: `platform.architecture` field in `DataVolumeSourceRegistry`, arch-specific `DataSource` (`<name>-<arch>`), legacy `DataSource` redirects to arch-specific one  <br/> **Kubevirt**: `VirtualMachineInstanceSpec.Architecture` to target architecture |                                                        |
| **Topology Considerations**      | [x]  | Related resources should be created per worker node architecture. Currently its ARM64 and AMD64.                                                                                                                                                                                                                                                                                                                                                                                                                                                 |                                                        |


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
- **[P0]** Verify HCO monitors the cluster's nodes architectures correctly, and updated in addition/removal of nodes (sig-iuo).
- **[P0]** Verify golden images are annotated only with supported architectures and related resources are created only for those, named with the architecture suffix (sig-iuo).
- **[P1]** Verify golden images annotated only with unsupported architectures present fail status in HCO dataImportCronTemplates status (sig-iuo).
- **[P0]** Verify arch-specific templates created with correct configurations ([sig-infra](https://issues.redhat.com/browse/CNV-76714)).
- **[P0]** Verify VMs created from arch-specific templates run on matching architecture nodes (sig-infra).
- **[P0]** Verify CDI imports correct architecture-specific images via `platform.architecture` ([sig-storage](https://issues.redhat.com/browse/CNV-76732)).
- **[P0]** Verify Datasource new pointer API ([sig-storage](https://issues.redhat.com/browse/CNV-76732)).

- **[P0]** Verify VMs scheduled only on nodes matching their CPU architecture ([sig-virt](https://issues.redhat.com/browse/CNV-26818)).
- **[P0]** Verify VM migration between same-architecture nodes works correctly (sig-virt).

**Monitoring Goals**:
- **[P1]** Verify alert `HCOGoldenImageWithNoSupportedArchitecture` fires when DataImportCronTemplate annotated with unsupported architectures, and `kubevirt_hco_dataimportcrontemplate_with_supported_architectures` metric reports the appropriate value.
- **[P1]** Verify alert `HCOMultiArchGoldenImagesDisabled` fires when running on a multi-arch cluster while Multiarch FG is disabled, and `kubevirt_hco_multi_arch_boot_images_enabled` metric reports the appropriate value.
- **[P1]** Verify alert `HCOGoldenImageWithNoArchitectureAnnotation` fires when a custom golden image lacks an architecture annotation, and `kubevirt_hco_dataimportcrontemplate_with_architecture_annotation` metric reports the appropriate value.
- **[P1]** Verify `HCOMultiArchGoldenImagesDisabled` alert does not fire when Multiarch FG is disabled but nodePlacement restricts to supported architectures only.

**Backward Compatibility Goals**:
- **[P0]** Verify Legacy Datasources points to default arch-annotated Datasources (sig-iuo).
- **[P0]** Verify custom golden images without arch annotation remain functional (sig-iuo).
- **[P0]** Verify legacy `DataSource` API backward-compatible with new CDI arch-specific naming (sig-storage).

**Upgrade Goals**:
- **[P0]** Verify ARM64 and AMD64 VMs are migrated to same-architecture nodes during upgrades and related resources are preserved (sig-iuo, sig-virt).
- **[P0]** Verify functional tests pass post-upgrade to version when FG is enabled by default (all sigs).

**Regression Goals**:

all participating-sigs run regression on multiarch cluster

- **[P0]** sig-iuo: Run Tier 1 and Tier 2 test suites on multiarch clusters with both CPU architectures.
- **[P0]** sig-infra: Run Tier 1 and Tier 2 test suites on multiarch clusters with both CPU architectures.
- **[P0]** sig-storage: Run Tier 1 and Tier 2 test suites on multiarch clusters with both CPU architectures.
- **[P0]** sig-virt: Run Tier 1 and Tier 2 test suites on multiarch clusters with both CPU architectures.
- **[P0]** sig-network: Run Tier 1 and Tier 2 test suites on multiarch clusters with both CPU architectures.



**Out of Scope (Testing Scope Exclusions)**

<!-- Explicitly document what is **out of scope** for testing.
**Critical:** All out-of-scope items require explicit stakeholder agreement to prevent "I assumed you were testing
that" issues; each out-of-scope item must have PM/Lead sign-off.

- Items without stakeholder agreement are considered **risks** and must be escalated
- Review the items during Developer Handoff/QE Kickoff meeting

**Note:** Replace example rows with your actual out-of-scope items. -->

| Non-Goal                            | Rationale                                                                         | PM/ Lead Agreement |
|:------------------------------------|:----------------------------------------------------------------------------------|:-------------------|
| Update existing VM                  | Running VMs won't use new arch-specific resources                                 | [ ] Name/Date      |
| Performance Testing                 | Feature not scale related                                                         | [ ] Name/Date      |
| Security Testing                    | Feature not security related                                                      | [ ] Name/Date      |
| Testing with s390x architecture     | Feature scope is ARM enablement only                                              | [ ] Name/Date      |

#### **2. Test Strategy**

<!-- The following test strategy considerations must be reviewed and addressed. Mark "Y" if applicable,
"N/A" if not applicable (with justification in Comments). Empty cells indicate incomplete review. -->

| Item                           | Description                                                                                                                                                  | Applicable (Y/N or N/A) | Comments                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
|:-------------------------------|:-------------------------------------------------------------------------------------------------------------------------------------------------------------|:------------------------|:-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Functional Testing             | Validates that the feature works according to specified requirements and user stories                                                                        | Y                       |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| Automation Testing             | Ensures test cases are automated for continuous integration and regression coverage                                                                          | Y                       | All test cases should be automated at openshift-virtualization-tests repo.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| Performance Testing            | Validates feature performance meets requirements (latency, throughput, resource usage)                                                                       | N/A                     | Not related to scale.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| Security Testing               | Verifies security requirements, RBAC, authentication, authorization, and vulnerability scanning                                                              | N/A                     | Not related to security.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| Usability Testing              | Validates user experience, UI/UX consistency, and accessibility requirements. Does the feature require UI? If so, ensure the UI aligns with the requirements | Y                       | [UI/UX design doc](https://docs.google.com/document/d/18UKIXiAlyLTABQZdvDD5N85A6uM2CdBbif4eN1dVj-0/edit?usp=sharing) specify requirements.<br/>Done by UI team [CNV-62535](https://issues.redhat.com/browse/CNV-62535)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| Compatibility Testing          | Ensures feature works across supported platforms, versions, and configurations                                                                               | Y                       | sig-infra owns cross-arch VM creation validation ([CNV-76714](https://issues.redhat.com/browse/CNV-76714))                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| Regression Testing             | Verifies that new changes do not break existing functionality                                                                                                | Y                       | All participating SIGs run t1 and t2 on multiarch clusters.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| Upgrade Testing                | Validates upgrade paths from previous versions, data migration, and configuration preservation                                                               | Y                       | **sig-iuo & sig-virt:** VMs migrated and updated successfully, related resources preserved<br/>                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| Backward Compatibility Testing | Ensures feature maintains compatibility with previous API versions and configurations                                                                        | Y                       | **sig-iuo:** Legacy Datasource pointers, custom golden images without arch annotation<br/> **sig-storage:** Legacy `DataSource` API backward-compatible with new CDI arch-specific naming                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| Dependencies                   | Dependent on deliverables from other components/products? Identify what is tested by which team.                                                             | Y                       | Allowing multi-cpu architecture on openshift-virtualization-tests. Review the [PR](https://github.com/RedHatQE/openshift-virtualization-tests/pull/3147) whenever its ready to review.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| Cross Integrations             | Does the feature affect other features/require testing by other components? Identify what is tested by which team.                                           | Y                       | **IUO**: HCO node architecture tracking (`status.nodeInfo`), FG activation/propagation, new metrics & alerts, upgrade<br/> **[SSP/Infra](https://issues.redhat.com/browse/CNV-76714)**: Templates creation & utilization, new SSP API (`enableMultipleArchitectures`, `cluster` fields)<br/> **[Storage](https://issues.redhat.com/browse/CNV-76732)**: CDI-importer architecture selection, legacy `DataSource` backward compatibility, new CDI `platform` API<br/> **[Virt](https://issues.redhat.com/browse/CNV-26818)**: VM scheduling to correct architecture nodes, VM migration between same-arch nodes, upgrade, defaultCPUModel<br/> **[Network](https://issues.redhat.com/browse/CNV-76741)**: Network-related multiarch testing |
| Monitoring                     | Does the feature require metrics and/or alerts?                                                                                                              | Y                       | **Alerts + Metrics:**<br/> [`HCOGoldenImageWithNoSupportedArchitecture`](https://kubevirt.io/monitoring/runbooks/HCOGoldenImageWithNoSupportedArchitecture) + `kubevirt_hco_dataimportcrontemplate_with_supported_architectures`,<br/> [`HCOMultiArchGoldenImagesDisabled`](https://kubevirt.io/monitoring/runbooks/HCOMultiArchGoldenImagesDisabled.html) + `kubevirt_hco_multi_arch_boot_images_enabled`,<br/> [`HCOGoldenImageWithNoArchitectureAnnotation`](https://kubevirt.io/monitoring/runbooks/HCOGoldenImageWithNoArchitectureAnnotation) + `kubevirt_hco_dataimportcrontemplate_with_architecture_annotation`                                                                                                                   |
| Cloud Testing                  | Does the feature require multi-cloud platform testing? Consider cloud-specific features.                                                                     | Y                       | Testing environment AWS cluster                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |

#### **3. Test Environment**

<!-- **Note:** "N/A" means explicitly not applicable. Cannot leave empty cells. -->

| Environment Component                         | Configuration            | Comments                                                    |
|:----------------------------------------------|:-------------------------|:------------------------------------------------------------|
| **Cluster Topology**                          | MultiArch cluster        | 3 control-plane and 3-4 worker nodes                        |
| **OCP & OpenShift Virtualization Version(s)** | OCP 4.22, CNV-4.22       | OCP 4.22 and OpenShift Virtualization 4.22                  |
| **CPU Virtualization**                        | Multi-arch cluster       | 3 amd64 control-plane, 2 amd64 workers, and 2 arm64 workers |
| **Compute Resources**                         | N/A                      | No special compute requirements                             |
| **Special Hardware**                          | N/A                      | No special hardware required                                |
| **Storage**                                   | io2-csi storage class    | AWS EBS io2 CSI driver                                      |
| **Network**                                   | OVN-Kubernetes (default) | No special network requirements                             |
| **Required Operators**                        | N/A                      | N/A                                                         |
| **Platform**                                  | AWS                      | ARM64 workers available on AWS                              |
| **Special Configurations**                    | N/A                      | No special configurations required                          |

#### **3.1. Testing Tools & Frameworks**

<!-- Document any **new or additional** testing tools, frameworks, or infrastructure required specifically
for this feature. **Note:** Only list tools that are **new** or **different** from standard testing infrastructure.
Leave empty if using standard tools. -->

| Category           | Tools/Frameworks                                                                                                                                                                                                                                                                             |
|:-------------------|:---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Test Framework** | MultiArch cluster                                                                                                                                                                                                                                                                            |
| **CI/CD**          | Dedicated t2 jenkins jobs with multiarch markers:<br/> - `test-pytest-cnv-4.22-iuo-multiarch`<br/> - `test-pytest-cnv-4.22-observability-multiarch` <br/>- `test-pytest-cnv-4.22-ssp-multiarch`<br/> - `test-pytest-cnv-4.22-storage-multiarch`<br/> - `test-pytest-cnv-4.22-virt-multiarch` |
| **Other Tools**    |                                                                                                                                                                                                                                                                                              |

#### **4. Entry Criteria**

The following conditions must be met before testing can begin:

- [x] VEP [dic-on-heterogeneous-cluster](https://github.com/kubevirt/enhancements/tree/main/veps/sig-storage/dic-on-heterogeneous-cluster) is **approved and merged**
- [x] Test environment (MultiArch cluster) can be **set up and configured**
- [ ] Multi-CPU architecture support enabled in openshift-virtualization-tests repo
- [ ] related sigs multiarch t2 jenkins jobs created

#### **5. Risks**

<!-- Document specific risks for this feature. If a risk category is not applicable, mark as "N/A" with
justification in mitigation strategy.

**Note:** Empty "Specific Risk" cells mean this must be filled. "N/A" means explicitly not applicable
with justification. -->

| Risk Category        | Specific Risk for This Feature                                                                                                                                                                                                                                          | Mitigation Strategy                                                                                                                                         | Status |
|:---------------------|:------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:------------------------------------------------------------------------------------------------------------------------------------------------------------|:-------|
| Timeline/Schedule    | Israel in war currently, some sigs are impacted                                                                                                                                                                                                                         | N/A                                                                                                                                                         | [X]    |
| Test Coverage        | Should be coordinated with all cnv-sigs                                                                                                                                                                                                                                 | Review & sync with other sigs                                                                                                                               | [ ]    |
| Test Environment     | N/A                                                                                                                                                                                                                                                                     | N/A                                                                                                                                                         | [X]    |
| Untestable Aspects   | N/A                                                                                                                                                                                                                                                                     | N/A                                                                                                                                                         | [X]    |
| Resource Constraints | MultiArch cluster available only for 12 hours; limited number of AWS clusters available                                                                                                                                                                                 | Test automation on HA cluster first, final verification on MultiArch. Verify that DevOps are investigating increasing the number of available AWS clusters. | [ ]    |
| Dependencies         | Allowing multi-cpu architecture on openshift-virtualization-tests                                                                                                                                                                                                       | Review the [PR](https://github.com/RedHatQE/openshift-virtualization-tests/pull/3147) whenever its ready to review.                                         | [ ]    | | [ ]    |
| Non-blocker bugs     | 1. [[UI] architecture is incorrect for fedora arm and inconsistent on UI for other os](https://issues.redhat.com/browse/CNV-68981)<br/> 2. [[Storage] Arch-specific DataSources (arm64) persist after removing arm64 nodes](https://issues.redhat.com/browse/CNV-68996) | Make sure they are fixed & verified                                                                                                                         | [ ]    |

#### **6. Known Limitations**

<!-- Document any known limitations, constraints, or trade-offs in the feature implementation or testing approach.

**Examples:**
- Feature does not support IPv6 (only IPv4)
- No support for ARM64 architecture in this release -->

- Existing VMs are not updated: VMs that are already running will not automatically use new architecture-specific resources. Users must recreate VMs to take advantage of new resources.
- Platform variant format not supported: Formats like `linux/arm64/v8` are not supported at this time; this may be enhanced in future releases if needed.
- Architecture validation not performed: The system does not validate custom golden image architectures. It is the user's responsibility to ensure correct configuration.



---

### **III. Test Scenarios & Traceability (HCO)**

This table covers HCO (sig-iuo) test cases only. Other participating SIGs track their scenarios in their own deliverables.

<!-- This section links requirements to test coverage, enabling reviewers to verify all requirements are
tested. -->

<!-- **Requirement ID:**
- Use Jira issue key (e.g., CNV-12345)
- Each row should trace back to a specific testable requirement in Jira

**Requirement Summary:** Brief description from the Jira issue (user story format preferred) -->

| Requirement ID                                          | Requirement Summary                                                                                                                                                    | Test Scenario(s)                                                                                                                                                            | Tier   | Priority |
|:--------------------------------------------------------|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------------|:----------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:-------|:---------|
| [CNV-67900](https://issues.redhat.com/browse/CNV-67900) | As an Admin, I want HCO to detect and report node architectures so that the system is aware of available architectures in the cluster                                  | Verify HCO monitors the cluster's node architectures correctly, and updates on addition/removal of nodes                                                                    | Tier 1 | P0       |
|                                                         | As a User, I want golden images to be annotated only with supported architectures so that I only see relevant boot sources                                             | Verify golden images are annotated only with supported architectures                                                                                                        | Tier 1 | P0       |
|                                                         | As an Admin, I want to see a failure status for golden images annotated only with unsupported architectures so that I can identify misconfigured boot sources          | Verify golden images annotated only with unsupported architectures present fail status in HCO `dataImportCronTemplates` status                                              | Tier 1 | P1       |
|                                                         | As a User, I want arch-specific resources to be created and ready to use so that I can boot VMs from the correct architecture images                                   | Verify arch-specific related resources are created only for supported architectures, named with architecture suffix, and are ready to use                                   | Tier 2 | P0       |
|                                                         | As an Admin, I want to receive an alert and metric when a golden image has no supported architecture so that I can take corrective action                              | Verify `HCOGoldenImageWithNoSupportedArchitecture` alert fires and `kubevirt_hco_dataimportcrontemplate_with_supported_architectures` metric reports the appropriate value  | Tier 2 | P1       |
|                                                         | As an Admin, I want to receive an alert and metric when the Multiarch FG is disabled on a multi-arch cluster so that I am aware of the misconfiguration                | Verify `HCOMultiArchGoldenImagesDisabled` alert fires and `kubevirt_hco_multi_arch_boot_images_enabled` metric reports the appropriate value                                | Tier 2 | P1       |
|                                                         | As an Admin, I want to receive an alert and metric when a custom golden image is missing an architecture annotation so that I can update it accordingly                | Verify `HCOGoldenImageWithNoArchitectureAnnotation` alert fires and `kubevirt_hco_dataimportcrontemplate_with_architecture_annotation` metric reports the appropriate value | Tier 2 | P1       |
|                                                         | As an Admin, I want the alert not to fire when nodePlacement limits scheduling to supported architectures only so that I am not alerted unnecessarily                  | Verify `HCOMultiArchGoldenImagesDisabled` not fired when Multiarch FG is disabled but nodePlacement restricts to supported architectures only                               | Tier 2 | P1       |
|                                                         | As an Admin, I want legacy DataSources to remain backward-compatible so that existing workflows are not disrupted after enabling multi-arch support                    | Verify legacy DataSources point to default arch-annotated DataSources                                                                                                       | Tier 2 | P0       |
|                                                         | As an Admin, I want custom golden images without architecture annotations to remain functional so that non-annotated images continue to work                           | Verify custom golden images without arch annotation remain functional                                                                                                       | Tier 2 | P0       |
|                                                         | As an Admin, I want VMs to migrate to same-architecture nodes during upgrades so that workloads remain stable and architecture-compatible                              | Verify ARM64 and AMD64 VMs are migrated to same-architecture nodes during upgrades and related resources are preserved                                                      | Tier 2 | P0       |
|                                                         | As an Admin, I want functional validation to pass post-upgrade when the Multiarch FG is enabled by default so that the upgrade does not break multi-arch functionality | Verify functional tests pass post-upgrade to version when Multiarch FG is enabled by default                                                                                | Tier 2 | P0       |



---

### **IV. Sign-off and Approval**

This Software Test Plan requires approval from the following stakeholders:

* **Reviewers:**
  - [QE Lead / @rnester]
  - [sig-iuo representative / @nunnatsa @rllobilo @OhadRevah @albarker-rh]
  - [sig-storage representative]
  - [sig-virt representative]
  - [sig-infra representative]

* **Approvers:**
  - [QE Lead / @rnester]
