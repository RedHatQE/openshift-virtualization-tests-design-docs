# Openshift-virtualization-tests Test plan

## Multi-Architecture Boot Image Import and DataSource Lifecycle - Quality Engineering Plan

### **Metadata & Tracking**

| Field                  | Details                                                                                                                                                          |
| :--------------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Enhancement(s)**     | [dic-on-heterogeneous-cluster](https://github.com/kubevirt/enhancements/blob/main/veps/sig-storage/dic-on-heterogeneous-cluster/dic-on-heterogeneous-cluster.md) |
| **Feature in Jira**    | [VIRTSTRAT-494](https://issues.redhat.com/browse/VIRTSTRAT-494)                                                                                                  |
| **Jira Tracking**      | [CNV-75960](https://issues.redhat.com/browse/CNV-75960)                                                                                                          |
| **Parent STP**         | [HCO support for heterogeneous multi-arch clusters](https://github.com/RedHatQE/openshift-virtualization-tests-design-docs/pull/12)                              |
| **QE Owner(s)**        | Geetika Kapoor                                                                                                                                                   |
| **Owning SIG**         | sig-infra                                                                                                                                                      |
| **Participating SIGs** | sig-virt, sig-iuo, sig-storage                                                                                                                                   |
| **Current Status**     | Draft                                                                                                                                                            |

---

### **Feature Overview**

This feature enables automatic provisioning and lifecycle management of architecture-specific bootable volumes on heterogeneous clusters. When `enableMultiArchBootImageImport` is enabled, the system creates architecture-labeled DataSources for each supported architecture (amd64, arm64, s390x), prevents duplicate volumes, and automatically cleans up stale resources when cluster architecture changes. This ensures VMs always use the correct architecture-specific golden images without manual intervention, supporting seamless operation across mixed-architecture environments.

---

**Document Conventions:**

| Term                               | Definition                                                                                                |
| :--------------------------------- | :-------------------------------------------------------------------------------------------------------- |
| **VM**                             | Virtual Machine                                                                                           |
| **DV**                             | DataVolume                                                                                                |
| **DS**                             | DataSource                                                                                                |
| **PVC**                            | PersistentVolumeClaim                                                                                     |
| **DIC**                            | DataImportCron                                                                                            |
| **SSP**                            | Scheduling, Scale and Performance operator                                                                |
| **enableMultiArchBootImageImport** | Feature gate controlling multi-arch boot image import behavior in HCO CR                                  |
| **Architecture-specific DS**       | DataSource with architecture suffix (example: `<os>-amd64`, `<os>-arm64`)                                 |
| **Legacy DataSource**              | Original non-suffixed DataSource that redirects to architecture-specific version                          |
| **Heterogeneous cluster**          | Cluster with worker nodes of different CPU architectures (primarily amd64 and arm64)                      |
| **Stale DataSource**               | DataSource for architecture no longer present in cluster (example: arm64 DS after removing ARM nodes)        |
| **Golden Image**                   | Pre-configured bootable OS volume used as template for VM creation                                        |

---

### **I. Motivation and Requirements Review (QE Review Guidelines)**

This section documents the mandatory QE review process. The goal is to understand the feature's value,
technology, and testability before formal test planning.

#### **1. Requirement & User Story Review Checklist**

| Check                                  | Done | Details/Notes                                                                                                                                                                                                                                                                        | Comments |
| :------------------------------------- | :--- | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :------- |
| **Review Requirements**                | [x]  | Reviewed the relevant requirements for multi-arch boot image import feature from VEP and Jira tracking                                                                                                                                                                               |          |
| **Understand Value**                   | [x]  | Enables automatic provisioning of architecture-specific bootable volumes (golden images) on heterogeneous clusters. Prevents duplicate volumes and ensures proper lifecycle management of DataSources when cluster architecture changes (example: node addition/removal).                |          |
| **Customer Use Cases**                 | [x]  | Heterogeneous clusters (amd64/arm64) requiring OS golden images for both architectures. Dynamic cluster scaling where nodes of different architectures are added/removed. Migration from single-arch to multi-arch clusters without manual cleanup.                              |          |
| **Testability**                        | [x]  | Requirements are testable through cluster configuration changes and resource observation. Needs clarification about using dedicated lanes or test markers.                                                                                                                                                                                            |          |
| **Acceptance Criteria**                | [x]  | Bootable volumes labeled correctly by architecture. No duplicate volumes when toggling enableMultiArchBootImageImport. Stale DataSources cleaned up when nodes are removed. Post-deployment images (example: Windows, Alpine) handled correctly.                                               |          |
| **Non-Functional Requirements (NFRs)** | [x]  | NFRs (Performance, Monitoring, Scalability) are out of scope for this test plan. Basic usability validation of naming conventions is in scope.                |          |

#### **2. Technology and Design Review**

| Check                            | Done | Details/Notes                                                                                                                   | Comments                                         |
| :------------------------------- | :--- | :------------------------------------------------------------------------------------------------------------------------------ | :----------------------------------------------- |
| **Developer Handoff/QE Kickoff** | [x]  | Discussions held within team on DataImportCron lifecycle, cleanup triggers                                 | Covered in parent STP and in team discussions |
| **Technology Challenges**        | [x]  | Can use HA cluster, but should be verified on Multiarch cluster which is available only for 12 hours behavior   |                                                  |
| **Test Environment Needs**       | [x]  | Multi-arch cluster with ability to add/remove nodes dynamically.                        |         Dynamic adding of nodes could be challenging and not possible.                                               |
| **API Extensions**               | [x]  | **HCO**: `status.nodeInfo` (controlPlaneArchitectures, workloadsArchitectures), `status.dataImportCronTemplates` (originalSupportedArchitectures, conditions)<br/> **SSP**: `enableMultipleArchitectures`, `cluster` fields (workloadArchitectures, controlPlaneArchitectures)<br/> **CDI**: `platform.architecture` field in `DataVolumeSourceRegistry`, arch-specific `DataSource` (`<name>-<arch>`), legacy `DataSource` redirects to arch-specific one                  |                                                  |

---

### **II. Software Test Plan (STP)**

This STP serves as the **overall roadmap for testing**, detailing the scope, approach, resources, and schedule.

#### **1. Scope of Testing**

This test plan validates the enableMultiArchBootImageImport feature behavior, bootable volume lifecycle management, and DataSource cleanup on heterogeneous clusters.

**In Scope:**

- Verify bootable volume re-import behavior when enableMultiArchBootImageImport is toggled from false to true
- Validate proper architecture labeling on VolumeSnapshots, PVCs, and DataSources
- Test duplicate volume detection and prevention
- Verify DataSource lifecycle when cluster nodes are added or removed
- Test golden image availability and selection based on cluster architecture
- Validate post-deployment image imports (Windows, Alpine, custom images)
- Test behavior on homogeneous vs heterogeneous clusters
- Verify handling of architecture-incompatible images (example: Windows on ARM)
- Test VM creation using architecture-specific DataSources
- Verify correct VirtualMachinePreference is picked up based on architecture
- Validate legacy DataSource redirection to architecture-specific variants

**Out of Scope (Testing Scope Exclusions)**

| Out-of-Scope Item                                  | Rationale                                                                              | PM/Lead Agreement |
| :------------------------------------------------- | :------------------------------------------------------------------------------------- | :---------------- |
| Performance benchmarking of image import times     | Out of scope for this test plan                                                        |    |
| Testing with non-standard storage classes          | Out of scope for this test plan                                                        |     |
| Testing on clusters with >3 architectures          | Out of scope for this test plan                        |     |
| Manual DataImportCron creation/modification        | Managed by SSP operator                          |   |
| HCO nodeInfo architecture tracking                 | Covered in [parent STP](https://github.com/RedHatQE/openshift-virtualization-tests-design-docs/pull/12)                                                   |     |
| VM scheduling to correct architecture nodes        | Covered under [Virt Multi-arch STP](https://github.com/RedHatQE/openshift-virtualization-tests-design-docs/pull/19)                  |     |
| Performance, Usability, Monitoring, Scalability NFRs | Out of scope for this test plan                |     |
| Cross-version compatibility and upgrade testing    | Covered in [parent STP](https://github.com/RedHatQE/openshift-virtualization-tests-design-docs/pull/12)                                                                  |      |
| Heterogeneous storage classes testing              | Valid test case but out of scope from this test plan                            |      |

#### **2. Test Objectives**

The primary objectives of testing for this feature are:

- **Verify functional requirements:** Ensure all architecture-specific DataSource creation, labeling, and lifecycle behaviors work correctly according to the VEP specifications
- **Identify and report defects:** Document deviations from expected behavior, especially around duplicate prevention and cleanup mechanisms
- **Ensure feature quality:** Validate the feature performs as expected across heterogeneous cluster configurations (amd64/arm64 combinations)
- **Assess release readiness:** Determine if the feature meets acceptance criteria for GA release, including automation coverage
- **Validate backward compatibility:** Ensure legacy DataSource redirection maintains existing user workflows without disruption

#### **3. Motivation**

**User Stories Driving Test Priorities:**

As a **cluster administrator** managing a heterogeneous cluster, I need confidence that:
- Architecture-specific golden images are created correctly without duplicates when I enable the feature
- The system automatically cleans up stale resources when I remove nodes of a specific architecture
- I can migrate from single-arch to multi-arch configurations seamlessly
- Post-deployment images (example: Windows, Alpine) are handled correctly on multi-arch clusters

As a **VM operator**, I need to ensure that:
- VMs automatically select the correct architecture-specific DataSource and VirtualMachinePreference based on node placement
- VM creation fails gracefully with clear error messages when architecture-incompatible images are used
- All existing scripts and tools continue working with legacy DataSource names


**Testing Goals:**

**Note**: These goals complement the parent STP for HCO-level architecture tracking. See [parent STP](https://github.com/RedHatQE/openshift-virtualization-tests-design-docs/pull/12) for coordination testing.

**Functional Goals**:
- **[P0]** Verify bootable volume re-import creates architecture-labeled resources without duplicates when enableMultiArchBootImageImport is toggled
- **[P0]** Verify VM creation automatically selects correct architecture-specific DataSource based on node placement
- **[P0]** Verify DataSource cleanup when all nodes of specific architecture are removed
- **[P1]** Verify post-deployment images (example: Windows, Alpine) create architecture-specific resources on heterogeneous
- **[P1]** Verify graceful handling of architecture-incompatible scenarios (example: ARM VM with x86-only image)
- **[P1]** Verify proper architecture labeling on VolumeSnapshots, PVCs, and DataSources matches source image architecture

**Backward Compatibility Goals**:
- **[P0]** Verify legacy DataSource redirection to architecture-specific variants maintains existing workflows and scripts
- **[P1]** Verify single-arch clusters continue working unchanged when feature is enabled
- **[P1]** Verify disabling enableMultiArchBootImageImport after enabling results in proper cleanup


#### **4. Test Strategy**

The following test strategy considerations must be reviewed and addressed. Mark "Y" if applicable,
"N/A" if not applicable (with justification in Comments). Empty cells indicate incomplete review.

| Item                           | Description                                                                                                        | Applicable (Y/N or N/A) | Comments                                                                                                                                             |
| :----------------------------- | :----------------------------------------------------------------------------------------------------------------- | :---------------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------- |
| Functional Testing             | Core feature validation                                                                                            | Y                       | Primary focus: DataSource lifecycle, labeling, duplicate prevention                                                                                  |
| Automation Testing             | Automated test coverage                                                                                            | Y                       | Full automation for all scenarios in openshift-virtualization-tests framework                                                                        |
| Performance Testing            | Import time and resource utilization                                                                               | N/A                     | Out of scope for this test plan                                                                                      |
| Usability Testing              | Clarity of labels and naming                                                                                       | Y                       | Validate naming conventions (arch suffix) are clear and consistent across all golden images                                                          |
| Regression Testing             | Ensure existing single-arch behavior unchanged                                                                     | Y                       | Critical - must not break existing functionality. Validate single-arch clusters work identically                                                     |
| Backward Compatibility Testing | Disabling multi-arch after enabling                                                                                | Y                       | Test toggle behavior and cleanup                                                                            |
| Dependencies                   | CDI operator                                                                                                       | Y                       | CDI imports and DataSource API validation                            |
| Cross Integrations             | VM creation using multi-arch datasources                                                       | Y                       | DataSource availability and selection for VM creation |
| Monitoring                     | Metrics and alerts for failed imports                                                                              | N/A                     | Out of scope for this test plan                                                                                  |

#### **5. Test Environment**

**Note:** "N/A" means explicitly not applicable. Cannot leave empty cells.

| Environment Component                         | Configuration                        | Specification Examples                                                       |
| :-------------------------------------------- | :----------------------------------- | :--------------------------------------------------------------------------- |
| **Cluster Topology**                          | Multi-arch heterogeneous cluster     | 3 control-plane (amd64), 2 amd64 workers, 2 arm64 workers                   |
| **OCP & OpenShift Virtualization Version(s)** | OCP 4.21, CNV 4.21                   | Versions supporting enableMultiArchBootImageImport                           |
| **CPU Virtualization**                        | Mixed amd64 and arm64                | Ability to add/remove nodes of specific architectures dynamically            |
| **Compute Resources**                         | N/A                | No special compute requirements                                            |
| **Special Hardware**                          | N/A                                  | Standard compute nodes sufficient                                            |
| **Storage**                                   | io2-csi storage class | AWS EBS io2 CSI driver                      |
| **Network**                                   | Default networking                   | OVN-Kubernetes or OpenShiftSDN                                               |
| **Required Operators**                        | SSP, CDI, HCO                        | N/A |
| **Platform**                                  | AWS                                  | Platform must support multi-arch node provisioning                           |
| **Special Configurations**                    | N/A                                  | Standard configuration                                                       |

#### **5.1. Testing Tools & Frameworks**

Document any **new or additional** testing tools, frameworks, or infrastructure required specifically
for this feature.

| Category           | Tools/Frameworks                                                |
| :----------------- | :-------------------------------------------------------------- |
| **Test Framework** | pytest, openshift-virtualization-tests framework                |
| **CI/CD**          | Existing CNV-QE pipeline with multi-arch cluster support        |
| **Other Tools**    | oc CLI, jq for JSON parsing, kubectl, virtctl |

#### **6. Entry Criteria**

The following conditions must be met before testing can begin:

- [x] Requirements and design documents are **approved and merged**
- [x] Test environment with multi-arch cluster can be **set up and configured**
- [ ] enableMultiArchBootImageImport feature is **available in target release**
- [ ] SSP operator supports architecture-aware DataImportCron management
- [x] Test automation framework supports multi-arch cluster provisioning

#### **7. Exit Criteria**

The following conditions must be met before feature sign-off:

- [ ] Key P0/P1 test scenarios executed and passing (TC-01, TC-03, TC-06, TC-07, TC-11)
- [ ] **Test automation merged** to openshift-virtualization-tests repository
- [ ] Tests running successfully in release checklist CI jobs
- [ ] All critical and high-priority defects resolved and verified, or documented as known limitations with workarounds
- [ ] QE formal sign-off provided

#### **8. Risks**

Document specific risks for this feature.

| Risk Category        | Specific Risk for This Feature                                                                | Mitigation Strategy                                                                                                    | Status                     |
| :------------------- | :-------------------------------------------------------------------------------------------- | :--------------------------------------------------------------------------------------------------------------------- | :------------------------- |
| Timeline/Schedule    | Multi-arch cluster provisioning can be time-consuming & unstable.  | ticket raised: [CNV-76482](https://issues.redhat.com/browse/CNV-76482)              | [x] Discussed with Devops manager |
| Test Coverage        | Edge cases around timing of node removal and DataSource cleanup                               | Add testing around those scenarios                      | [ ]                        |
| Test Environment     | Limited availability of arm64 hardware in CI (12-hour windows)                                | Ticket raised with Devops for a better solution | [x] Infra coordination ongoing |
| Untestable Aspects   | Very large-scale environment (50+ OS images across multiple architectures)                                | Testing limited to specific images like RHEL, Fedora. Document scale limitations  or add cards for scale team                                     | [ ]                        |
| Known Bugs Blocking Testing | [CNV-75084](https://issues.redhat.com/browse/CNV-75084) - Bootable volumes re-imported after enabling feature<br/>[CNV-68996](https://issues.redhat.com/browse/CNV-68996) - Arch-specific DataSources persist after removing nodes | Track & triage bug fixes. Revalidate after bug resolution. This could impact exit criteria timeline | [x] Tracking bugs actively |

#### **9. Known Limitations**

- **DataSource cleanup not functional**: Bug [CNV-68996](https://issues.redhat.com/browse/CNV-68996) prevents arch-specific DataSources from being cleaned up after removing nodes. This impacts TC-07 testing.
- **Duplicate volume creation issue**: Bug [CNV-75084](https://issues.redhat.com/browse/CNV-75084) causes bootable volumes to be re-imported when feature is enabled. This impacts TC-06 testing.
- **Architecture-incompatible images**: Some OS images (example: Windows Server) may not have ARM64 variants. VM creation will fail gracefully with clear error messaging
- **Manual label modification risk**: Architecture detection relies on node labels; manual modification could cause inconsistencies until next reconciliation cycle
- **Storage-dependent performance**: Import times vary significantly based on storage backend (CSI driver) and network conditions
- **s390x architecture support**: While supported in theory, practical testing limited to amd64/arm64 due to hardware availability

---

### **III. Test Scenarios & Traceability**

This section links requirements to test coverage, enabling reviewers to verify all requirements are tested.


**Traceability Matrix:**

| Requirement ID | Requirement Summary                           | Test Scenario(s)                                                                                                                 | Tier   | Priority | Known Issues |
| :------------- | :-------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------- | :----- | :------- | :----------- |
| TC-01          | Golden images on multi-arch cluster           | Deploy multi-arch cluster with enableMultiArchBootImageImport=true. Verify all bootable volumes have architecture-specific labels (example: rhel9, rhel9-amd64, rhel9-arm64) | Tier 1 | P0       |              |
| TC-02          | Images added post-deployment                  | Add new DataImportCron (Windows/Alpine) on existing multi-arch cluster. Verify architecture-specific images created for available node types | Tier 2 | P1       |              |
| TC-03          | Correct image selection based on architecture | Create VMs on multi-arch cluster without specifying architecture. Verify VM automatically uses correct architecture-specific DataSource | Tier 1 | P0       |              |
| TC-04          | Behavior on homogeneous cluster               | Enable enableMultiArchBootImageImport on single-arch (amd64) cluster. Verify only amd64 images imported, no duplicates         | Tier 1 | P1       |              |
| TC-05          | Windows ARM incompatibility                   | Attempt to create Windows VM on ARM node when only x86 image available. Verify graceful failure with clear error message       | Tier 2 | P1       |              |
| TC-06          | Duplicate volume prevention                   | Enable enableMultiArchBootImageImport on cluster with existing bootable volumes. Verify no duplicate volumes created, proper architecture labels applied | Tier 1 | P0       | [CNV-75084](https://issues.redhat.com/browse/CNV-75084)    |
| TC-07          | DataSource cleanup on node removal            | Remove all arm64 nodes from multi-arch cluster. Verify arm64 DataSources cleaned up, no orphaned resources                      | Tier 1 | P0       | [CNV-68996](https://issues.redhat.com/browse/CNV-68996)    |
| TC-08          | DataSource persistence with partial node removal | Remove single arm64 node from cluster with multiple arm64 nodes. Verify all DataSources remain, VM creation still works      | Tier 2 | P1       |              |
| TC-09          | Toggle enableMultiArchBootImageImport         | Enable/disable/re-enable feature multiple times. Verify idempotent behavior, no resource leaks                                  | Tier 2 | P2       |              |
| TC-10          | VolumeSnapshot label validation               | Verify all VolumeSnapshots have correct architecture labels matching source image architecture                                  | Tier 2 | P1       |              |
| TC-11          | Mixed architecture VM creation                | Create both amd64 and arm64 VMs from same base image (centos-stream9). Verify each uses correct architecture-specific DataSource | Tier 1 | P0       |              |
| TC-12          | Resource cleanup on feature disable           | Disable enableMultiArchBootImageImport on multi-arch cluster. Verify proper cleanup of architecture-specific resources          | Tier 2 | P2       |              |
| TC-13          | DataImportCron scheduling                     | Configure scheduled DataImportCron on multi-arch cluster. Verify imports execute for all architectures without conflicts        | Tier 2 | P2       |              |

---

### **IV. Sign-off and Approval**

**Final Sign-off Checklist:**

Before feature sign-off, verify:
- [ ] Tier 1 tests defined and automated (TC-01, TC-03, TC-04, TC-06, TC-07, TC-11)
- [ ] Tier 2 tests defined and automated (TC-02, TC-05, TC-08, TC-09, TC-10, TC-12, TC-13)
- [ ] **Test automation merged** to main branch of openshift-virtualization-tests
- [ ] Tests running in release checklist CI jobs without failures
- [ ] All P0 test scenarios passing (100% pass rate required) or documented with known bug reference


---

This Software Test Plan requires approval from the following stakeholders:

**Reviewers:**

**Approvers:**
