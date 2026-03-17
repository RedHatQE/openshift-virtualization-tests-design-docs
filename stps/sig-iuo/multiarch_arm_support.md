# Openshift-virtualization-tests Test plan

## MultiArch Support enablement for ARM - Quality Engineering Plan

### **Metadata & Tracking**

- **Enhancement(s):** [dic-on-heterogeneous-cluster](https://github.com/kubevirt/enhancements/tree/main/veps/sig-storage/dic-on-heterogeneous-cluster)
- **Feature Tracking:** [VIRTSTRAT-494 - Multiarch Support enablement for ARM](https://issues.redhat.com/browse/VIRTSTRAT-494)
- **Epic Tracking:** [CNV-67900](https://issues.redhat.com/browse/CNV-67900)
- **QE Owner(s):** Harel Meir
- **Owning SIG:** sig-iuo
- **Participating SIGs:** sig-infra, sig-storage, sig-virt, sig-network

**Document Conventions (if applicable):**


| Term                   | Definition                                                                                             |
| ---------------------- | ------------------------------------------------------------------------------------------------------ |
| **MultiArch cluster**  | Heterogeneous cluster with 3 amd64 control-plane nodes, 2 amd64 worker nodes, and 2 arm64 worker nodes |
| **HA cluster**         | Homogeneous cluster with 3 control-plane nodes and 3 amd64 worker nodes                                |
| **MultiArch FG**       | `enableMultiArchBootImageImport` feature gate in HCO CR                                                |
| **Related resources**  | Golden image associated resources: `DataImportCron`, `DataSource`, `DataVolume`, `VolumeSnapshot`      |
| **nodeInfo**           | HCO status field tracking cluster architectures (`status.nodeInfo`)                                    |
| **DICT**               | DataImportCronTemplate - template for creating DataImportCron resources                                |
| **DIC**                | DataImportCron - periodically imports images from a registry into a DataSource                         |
| **arch-annotation**    | `ssp.kubevirt.io/dict.architectures` — DICT annotation listing supported CPU architectures             |
| **arch-label**         | `template.kubevirt.io/architecture` — label indicating the target CPU architecture of a resource       |
| **Pointer DataSource** | A DataSource that references another arch-specific DataSource via `spec.source.dataSource`             |


### **Feature Overview**

MultiArch Support enables running ARM (aarch64) virtual machines alongside x86 (amd64) VMs on a single OpenShift Virtualization cluster with mixed-architecture worker nodes. The feature spans the full VM lifecycle: architecture-aware golden image import, VM template creation, VM scheduling, and live migration. It is controlled by the Multiarch feature gate in HCO (disabled by default in 4.22, enabled not earlier than 4.23).

---

### **I. Motivation and Requirements Review (QE Review Guidelines)**

This section documents the mandatory QE review process. The goal is to understand the feature's value,
technology, and testability before formal test planning.

#### **1. Requirement & User Story Review Checklist**

- **Review Requirements**
  - Users can create, start, stop, and delete VMs on a Multiarch cluster using standard OpenShift Virtualization APIs.
  - Platform must detect and report which CPU architectures are available in the cluster (worker and control-plane nodes)
  - VMs must run only on nodes matching their target CPU architecture.
  - VMs must migrate only between nodes of the same architecture.
  - Automatically provision architecture-correct golden images and templates via Multiarch FG activation.
  - Unified monitoring and logging across MultiArch VMs
- **Understand Value and Customer Use Cases**
  - *Describe the feature's value to customers:*
    - Run ARM-based VMs alongside x86-based VMs on a single cluster, eliminating the need for separate infrastructure per architecture
    - Automatically provision architecture-correct golden images and templates, so users don't need to manually manage per-arch resources
  - *List the customer use cases identified:*
    - **Developer validates ARM app**: A developer creates an ARM64 VM from an arch-specific template, deploys their app, and tests it alongside their existing x86 VM — on the same cluster, using the same storage and network
    - **Admin enables MultiArch on existing cluster**: An admin adds ARM worker nodes to an existing cluster, enables the MultiArch FG, and the platform automatically creates ARM-specific golden images, DataSources, and templates without disrupting existing x86 workloads
    - **QE migrates workloads to ARM**: QE team runs ARM VM test environments in the same OpenShift cluster used for x86-based CI/CD pipelines
    - An admin upgrades MultiArch cluster -  existing ARM and x86 VMs survive the upgrade on their correct architecture nodes without manual intervention
- **Testability**
  - Upgrade to a version where FG is enabled by default until 4.23 timeframe (FG disabled by default in 4.22)

- **Acceptance Criteria**
  - **Architecture detection**: HCO `nodeInfo` monitors and report all unique nodes architectures, and propogate it to SSP.
  - **Feature gate toggle**: Enabling MultiArch FG triggers golden images support. HCO propagates the FG value to SSP via `spec.enableMultipleArchitectures`. Disabling it removes arch-specific resources while preserving existing VMs.
  - **HCO DICT filtering**: when golden images support is enabled - only DICTs with `arch-annotation` are filtered to include only cluster-supported architectures.
  - **Arch-specific resource creation**: For each supported architecture, a DICT named with arch-suffix is created, which produces related resources with arch-label.
  - **Pointer DataSource**: SSP updates legacy DataSource with `spec.source.dataSource` pointing to the default arch DataSource.
  - **Image import**: CDI pulls only the correct arch image — via `platform.architecture` field for `pullMethod==pod`, or via nodeAffinity scheduling for `pullMethod==node`.
  - **VM scheduling**: A VM with `spec.architecture: arm64` runs only on arm64 nodes; a VM with `spec.architecture: amd64` runs only on amd64 nodes.
  - **VM migration**: Live migration succeeds only between same-arch nodes.
  - **Backward compatibility**: Custom DICTs without arch annotation continue working as before. VM can be created from pointer Datasoures.
  - **NodePlacement alternative**: When nodePlacement restricts scheduling to supported architectures only, VMs created for those even if MultiArch FG is disabled.
  - **Upgrade**: VMs survive upgrade on their correct architecture nodes. Arch-specific resources are preserved.
  - **Regression**: T1 and T2 tests passing on multiarch cluster for each participating-sig.
  - *gaps:*
    - Upgrade to FG-enabled-by-default version testable only in 4.23
- **Non-Functional Requirements (NFRs)**
  - **Monitoring**: Platform must alert admins about MultiArch misconfigurations (unsupported arch, FG disabled on MultiArch cluster, missing annotations)
  - **Doc**: Drop the Tech Preview note from docs
  - *Note any NFRs not covered and why:*
    - Performance/Scalability: Not applicable — feature does not introduce new scale-sensitive operations
    - Security: Not applicable — no new RBAC, auth, or privilege changes introduced

#### **2. Known Limitation**

- Existing VMs are not updated: VMs that are already running will not automatically use new architecture-specific resources. Users must recreate VMs to take advantage of new resources.
- Platform variant format not supported: Formats like `linux/arm64/v8` are not supported at this time; this may be enhanced in future releases if needed.
- Architecture validation not performed: The system does not validate custom golden image architectures. It is the user's responsibility to ensure correct architecture annotation values.
- Special Infra(Like SRIOV,GPU, Multinics etc) tests are not testable since the test platform is AWS.

#### **3. Technology and Design Review**

- [x] **Developer Handoff/QE Kickoff**
  - *Key takeaways and concerns:*
    - Met with Nahshon from HCO team
    - MultiArch FG is disabled by default in 4.22, and enabled not earlier than 4.23
    - The design maintains the existing workflow (HCO -> DICT -> SSP -> DIC -> DataSource -> CDI) while adding architecture awareness at each layer
    - Common DICTs receive `arch-annotation` annotation at HCO image build time; custom DICTs rely on user-supplied annotations

- [x] **Technology Challenges**
  - *List identified challenges:*
    - MultiArch cluster available only for 12 hours on AWS
    - Need to coordinate testing across 5 SIGs
  - *Impact on testing approach:*
    - Initial testing and most Tier 1 tests can run on HA (homogeneous) cluster by verifying annotations, labels, and fields
    - Final verification and Tier 2 (end-to-end) tests require MultiArch cluster

- [x] **API Extensions**
  - *List new or modified APIs:*
    - **HCO**:
      - `spec.featureGates.enableMultiArchBootImageImport` (bool) - enables/disables golden images support
      - `status.nodeInfo.controlPlaneArchitectures` ([]string) - lists control-plane node architectures
      - `status.nodeInfo.workloadsArchitectures` ([]string) - lists worker node architectures
      - `status.dataImportCronTemplates[].status.originalSupportedArchitectures` (string) - preserves original annotation values
      - `status.dataImportCronTemplates[].status.conditions` - deployment conditions including `UnsupportedArchitectures` reason
    - **SSP**:
      - `spec.enableMultipleArchitectures` (bool) - feature activation flag
      - `spec.cluster.workloadArchitectures` ([]string) - worker arch list from HCO
      - `spec.cluster.controlPlaneArchitectures` ([]string) - control-plane arch list from HCO
    - **CDI**:
      - `DataVolumeSourceRegistry.platform.architecture` (string) - specifies target CPU architecture for import
      - `DataSourceSource.dataSource.namespace` (string) - Pointer DataSource namespace
      - `DataSourceSource.dataSource.name` (string) - Pointer DataSource name
    - **KubeVirt**:
      - `VirtualMachineInstanceSpec.Architecture` (string) - targets VM to specific CPU architecture
  - *Testing impact:*
    - New API fields require validation tests at each layer

- [x] **Test Environment Needs**
  - *See environment requirements in Section II.3 and testing tools in Section II.3.1*

- [x] **Topology Considerations**
  - *Describe topology requirements:*
    - Related resources should be created per supported worker node architecture (ARM64 and AMD64)
    - Control-plane assumed homogeneous (single architecture); used as default arch for Pointer DataSources
    - Worker nodes identified by `node-role.kubernetes.io/worker` label
    - Node architecture detected from `status.nodeInfo.architecture` field
  - *Impact on test design:*
    - Tests must verify resources are created per-architecture, not per-node
    - Tests must verify dynamic behavior when nodes are added/removed from cluster

### **II. Software Test Plan (STP)**

This STP serves as the **overall roadmap for testing**, detailing the scope, approach, resources, and schedule.

#### **1. Scope of Testing**

**Testing Goals**

**sig-iuo**

- **[P0]** Verify HCO detects worker node architectures correctly and updates when nodes are added/removed.
- **[P0]** Verify DICT annotations are filtered to include only cluster-supported architectures, and related resources are created with correct naming suffix and labels.
- **[P0]** Verify DICTs annotated with only unsupported architectures show error in DICT status, and related resources aren't created.
- **[P0]** Verify custom DICTs without arch-annotation continue working without filtering.
- **[P1]** Verify alert fires when DICT annotated with unsupported architectures, and corresponding metric reports the appropriate value.
- **[P1]** Verify alert fires when running on a MultiArch cluster while MultiArch FG is disabled, and corresponding metric reports the appropriate value.
- **[P1]** Verify alert fires when a custom golden image lacks an architecture annotation, and corresponding metric reports the appropriate value.
- **[P1]** Verify alert does not fire when MultiArch FG is disabled but nodePlacement restricts to supported architectures only.
- **[P0]** Verify arch-specific resources are preserved after upgrade.

**sig-infra**

- **[P0]** Verify healthy VMs can be created from an arch-specific template.
- **[P0]** Verify arch-specific VM templates are created with correct `arch-label` label and correct DataSource reference.
- **[P0]** Verify SSP creates Pointer DataSources that reference the default arch-specific DataSource.
- **[P1]** Verify SSP removes legacy (unsuffixed) DICs when a DICT transitions from non-annotated to annotated for custom golden images.

**sig-storage** ([CNV-76732](https://issues.redhat.com/browse/CNV-76732) — CDI import, Pointer DataSource, backward compatibility):

- **[P0]** Verify CDI imports the correct arch-specific image from registry.
- **[P0]** Verify CDI-importer uses nodeAffinity for `pullMethod==node` and platform field for `pullMethod==pod`.
- **[P0]** Verify CDI reconciles Pointer DataSources by copying `status.source` from the referenced arch-specific DataSource.
- **[P0]** Verify VMs can be created from Pointer DataSources.
- **[P1]** Verify CDI propagates `arch-label` and `cdi.kubevirt.io/storage.import.datasource-name` labels from DIC to resulting DataSource CRs.

**sig-virt**:

- **[P0]** Verify VMs start, stop, restart, and delete operations work correctly for on a MultiArch cluster.
- **[P0]** Verify VMs are scheduled only on nodes matching their CPU architecture.
- **[P0]** Verify VMs can be created from instancetypes.
- **[P0]** Verify live migration of a VM between two same-architecture nodes completes successfully.
- **[P1]** Verify `defaultCPUModel` configuration works correctly per architecture on MultiArch cluster.

**Regression Goals**:

All participating SIGs run regression on MultiArch cluster(without special-infra):

- **[P0]** sig-iuo: Run Tier 1 and Tier 2 test suites on MultiArch clusters with both CPU architectures(iuo and observability).
- **[P0]** sig-infra: Run Tier 1 and Tier 2 test suites on MultiArch clusters with both CPU architectures.
- **[P0]** sig-storage: Run Tier 1 and Tier 2 test suites on MultiArch clusters with both CPU architectures.
- **[P0]** sig-virt: Run Tier 1 and Tier 2 test suites on MultiArch clusters with both CPU architectures.
- **[P0]** sig-network: Run Tier 1 and Tier 2 test suites on MultiArch clusters with both CPU architectures.

**Out of Scope (Testing Scope Exclusions)**

The following items are explicitly Out of Scope for this test cycle and represent intentional exclusions.
No verification activities will be performed for these items, and any related issues found will not be classified as defects for this release.

- **Update existing VMs**
  - *Rationale:* Running VMs won't use new arch-specific resources; users must recreate VMs
  - *PM/Lead Agreement:* [ ] Name/Date
- **Testing with s390x architecture**
  - *Rationale:* Feature scope is ARM enablement only for 4.22; s390x not in scope
  - *PM/Lead Agreement:* [ ] Name/Date

#### **2. Test Strategy**

**Functional**

- [x] **Functional Testing** — Validates that the feature works according to specified requirements and user stories
  - *Details:* Validates MultiArch golden image support across all 4 components (HCO, SSP, CDI, KubeVirt). Tests cover architecture detection, annotation filtering, resource creation with arch suffixes, image import, VM scheduling, and migration.

- [x] **Automation Testing** — Confirms test automation plan is in place for CI and regression coverage (all tests are expected to be automated)
  - *Details:* All test cases automated in openshift-virtualization-tests repo.

- [x] **Regression Testing** — Verifies that new changes do not break existing functionality
  - *Details:* All participating SIGs run T1 and T2 on MultiArch cluster.

**Non-Functional**

- [ ] **Performance Testing** — Validates feature performance meets requirements (latency, throughput, resource usage)
  - *Details:* Feature is not scale-related.

- [ ] **Scale Testing** — Validates feature behavior under increased load and at production-like scale
  - *Details:* Feature is not scale-related.

- [ ] **Security Testing** — Verifies security requirements, RBAC, authentication, authorization, and vulnerability scanning
  - *Details:* No new RBAC or security-related changes introduced.

- [x] **Usability Testing** — Validates user experience and accessibility requirements
  - Does the feature require a UI? Yes - new boot sources and VM creation pages (templates/instancetype)
  - [UI/UX design doc](https://docs.google.com/document/d/18UKIXiAlyLTABQZdvDD5N85A6uM2CdBbif4eN1dVj-0/edit?usp=sharing) specifies requirements.
  - Done by UI team [CNV-62535](https://issues.redhat.com/browse/CNV-62535)
  - *Details:* UI testing owned by UI team. QE validates that backend changes surface correctly through status conditions and events.

- [x] **Monitoring** — Does the feature require metrics and/or alerts?
  - *Details:* 3 new alerts with corresponding metrics:
    - [`HCOGoldenImageWithNoSupportedArchitecture`](https://kubevirt.io/monitoring/runbooks/HCOGoldenImageWithNoSupportedArchitecture) + `kubevirt_hco_dataimportcrontemplate_with_supported_architectures`
    - [`HCOMultiArchGoldenImagesDisabled`](https://kubevirt.io/monitoring/runbooks/HCOMultiArchGoldenImagesDisabled.html) + `kubevirt_hco_multi_arch_boot_images_enabled`
    - [`HCOGoldenImageWithNoArchitectureAnnotation`](https://kubevirt.io/monitoring/runbooks/HCOGoldenImageWithNoArchitectureAnnotation) + `kubevirt_hco_dataimportcrontemplate_with_architecture_annotation`

**Integration & Compatibility**

- [x] **Compatibility Testing** — Ensures feature works across supported platforms, versions, and configurations
  - Does the feature maintain backward compatibility with previous API versions and configurations? Yes
  - *Details:* Pointer Datasources should remain functional, and

- [x] **Upgrade Testing** — Validates upgrade paths from previous versions, data migration, and configuration preservation
  - *Details:* sig-iuo: VMs migrated and updated successfully, related resources preserved. Verify functional tests pass post-upgrade to version when MultiArch FG is enabled by default.

- [x] **Dependencies** — Blocked by deliverables from other components/products. Identify what we need from other teams before we can test.
  - *Details:* Allowing multi-cpu architecture on openshift-virtualization-tests. Review the [PR](https://github.com/RedHatQE/openshift-virtualization-tests/pull/3147) whenever its ready to review. Related openshift-python-wrapper PRs: [#2604](https://github.com/RedHatQE/openshift-python-wrapper/pull/2604), [#2603](https://github.com/RedHatQE/openshift-python-wrapper/pull/2603).

- [x] **Cross Integrations** — Does the feature affect other features or require testing by other teams? Identify the impact we cause.
  - *Details:*
    - **IUO (sig-iuo)**: HCO node architecture tracking (`status.nodeInfo`), FG activation & propagation, new metrics & alerts, upgrade
    - **[SSP/Infra](https://issues.redhat.com/browse/CNV-76714)**: Templates creation & utilization, new SSP API
    - **[Storage](https://issues.redhat.com/browse/CNV-76732)**: CDI-importer architecture selection, legacy `DataSource` backward compatibility, new CDI `platform` API
    - **[Virt](https://issues.redhat.com/browse/CNV-26818)**: VM scheduling to correct architecture nodes, VM migration between same-arch nodes, upgrade, defaultCPUModel
    - **[Network](https://issues.redhat.com/browse/CNV-76741)**: regression only.

**Infrastructure**

- [ ] **Cloud Testing** — Does the feature require multi-cloud platform testing? Consider cloud-specific features.
  - *Details:* No cloud testing required.

#### **3. Test Environment**

- **Cluster Topology:** MultiArch cluster with 3 control-plane and 4 worker nodes
- **OCP & OpenShift Virtualization Version(s):** OCP 4.22 with OpenShift Virtualization 4.22
- **CPU Virtualization:** MultiArch cluster (3 amd64 control-plane, 2 amd64 workers, 2 arm64 workers)
- **Compute Resources:** N/A - No special compute requirements
- **Special Hardware:** N/A
- **Storage:** io2-csi storage class (AWS EBS io2 CSI driver)
- **Network:** OVN-Kubernetes (default), IPv4
- **Required Operators:** N/A
- **Platform:** AWS (ARM64 workers available on AWS)
- **Special Configurations:** N/A

#### **3.1. Testing Tools & Frameworks**

- **Test Framework:** Standard (MultiArch cluster)
- **CI/CD:** Dedicated T2 jenkins jobs with MultiArch markers:
  - `test-pytest-cnv-4.22-iuo-multiarch`
  - `test-pytest-cnv-4.22-observability-multiarch`
  - `test-pytest-cnv-4.22-ssp-multiarch`
  - `test-pytest-cnv-4.22-storage-multiarch`
  - `test-pytest-cnv-4.22-virt-multiarch`
- **Other Tools:** N/A

#### **4. Entry Criteria**

The following conditions must be met before testing can begin:

- [x] VEP [dic-on-heterogeneous-cluster](https://github.com/kubevirt/enhancements/tree/main/veps/sig-storage/dic-on-heterogeneous-cluster) is **approved and merged**
- [x] Test environment (MultiArch cluster) can be **set up and configured**
- [ ] Multi-CPU architecture support enabled in openshift-virtualization-tests repo
- [ ] Related SIGs MultiArch T2 jenkins jobs created

#### **5. Risks**

**Timeline/Schedule**

- **Risk:** Israel in war currently, some SIGs are impacted
  - **Mitigation:** N/A - external factor
  - *Estimated impact on schedule:* Variable, depends on situation

**Test Coverage**

- **Risk:** Feature spans 5 SIGs; test coverage must be coordinated across all teams
  - **Mitigation:** Review & sync with other SIGs; this centralized STP tracks all SIG responsibilities
  - *Areas with reduced coverage:* Cross-SIG integration scenarios

**Test Environment**

- **Risk:** No special infra tests since its AWS cluster
  - **Mitigation:** N/A
  - *Missing resources or infrastructure:* SRIOV, GPU, Multinic etc

**Untestable Aspects**

- **Risk:** N/A
  - **Mitigation:** N/A
  - *Alternative validation approach:* N/A

**Resource Constraints**

- **Risk:** MultiArch cluster available only for 12 hours; limited number of AWS clusters available
  - **Mitigation:** Test automation on HA cluster first, final verification on MultiArch.
  - *Current capacity gaps:* Limited MultiArch cluster availability.

**Dependencies**

- **Risk:** Allowing multi-cpu architecture on openshift-virtualization-tests
  - **Mitigation:** Review the [PR](https://github.com/RedHatQE/openshift-virtualization-tests/pull/3147) whenever its ready to review.
  - *Dependent teams or components:* sig-virt

**Other**

- **Risk:** Known non-blocker bugs may impact test results:
  1. [[UI] architecture is incorrect for fedora arm and inconsistent on UI for other os](https://issues.redhat.com/browse/CNV-68981)
  2. [[Storage] Arch-specific DataSources (arm64) persist after removing arm64 nodes](https://issues.redhat.com/browse/CNV-68996)
  - **Mitigation:** Make sure they are fixed & verified before GA

---

### **III. Test Scenarios & Traceability**

This section centralizes test scenarios for all participating SIGs. Each SIG's scenarios are grouped separately for clarity.

#### sig-iuo

- **[CNV-67900](https://issues.redhat.com/browse/CNV-67900)** — As an Admin, I want HCO to detect and report node architectures so that the system is aware of available architectures in the cluster
  - *Test Scenario:* [Tier 1] Verify HCO `nodeInfo` reflects actual worker node architectures
  - *Priority:* P0
- **[CNV-67900](https://issues.redhat.com/browse/CNV-67900)** — As an Admin, I want HCO to update reported architectures when the cluster topology changes so that the system stays in sync
  - *Test Scenario:* [Tier 2] Verify HCO `nodeInfo` updates when an architecture is effectively removed (simulate by setting nodePlacement to target only arm64, then verify `nodeInfo` reports only arm64)
  - *Priority:* P0
- **[CNV-67900](https://issues.redhat.com/browse/CNV-67900)** — As a User, I want golden images to be annotated only with supported architectures so that I only see relevant boot sources
  - *Test Scenario:* [Tier 1] Verify `arch-annotation` on DICTs in HCO only contains architectures present in the cluster (intersection of original annotation and cluster archs)
  - *Priority:* P0
- **[CNV-67900](https://issues.redhat.com/browse/CNV-67900)** — As an Admin, I want to see a failure status for golden images annotated only with unsupported architectures so that I can identify misconfigured boot sources
  - *Test Scenario:* [Tier 1] Verify DICTs annotated only with unsupported architectures are excluded from SSP and show `Deployed=False, Reason=UnsupportedArchitectures` in HCO `status.dataImportCronTemplates`
  - *Priority:* P0
- **[CNV-67900](https://issues.redhat.com/browse/CNV-67900)** — As a User, I want arch-specific resources to be created and ready to use so that I can boot VMs from the correct architecture images
  - *Test Scenario:* [Tier 2] Verify Golden images related resources are created for each supported architecture with correct naming suffix and reach ready state
  - *Priority:* P0
- **[CNV-67900](https://issues.redhat.com/browse/CNV-67900)** — As an Admin, I want to receive an alert when a golden image has no supported architecture so that I can take corrective action
  - *Test Scenario:* [Tier 2] Verify `HCOGoldenImageWithNoSupportedArchitecture` alert fires and `kubevirt_hco_dataimportcrontemplate_with_supported_architectures` metric reports the appropriate value
  - *Priority:* P1
- **[CNV-67900](https://issues.redhat.com/browse/CNV-67900)** — As an Admin, I want to receive an alert when the MultiArch FG is disabled on a MultiArch cluster so that I am aware of the misconfiguration
  - *Test Scenario:* [Tier 2] Verify `HCOMultiArchGoldenImagesDisabled` alert fires and `kubevirt_hco_multi_arch_boot_images_enabled` metric reports the appropriate value
  - *Priority:* P1
- **[CNV-67900](https://issues.redhat.com/browse/CNV-67900)** — As an Admin, I want to receive an alert when a custom golden image is missing an architecture annotation so that I can update it accordingly
  - *Test Scenario:* [Tier 2] Verify `HCOGoldenImageWithNoArchitectureAnnotation` alert fires and `kubevirt_hco_dataimportcrontemplate_with_architecture_annotation` metric reports the appropriate value
  - *Priority:* P1
- **[CNV-67900](https://issues.redhat.com/browse/CNV-67900)** — As an Admin, I want the alert not to fire when nodePlacement limits scheduling to supported architectures only so that I am not alerted unnecessarily
  - *Test Scenario:* [Tier 2] Verify `HCOMultiArchGoldenImagesDisabled` does not fire when MultiArch FG is disabled but nodePlacement restricts to supported architectures only
  - *Priority:* P1
- **[CNV-67900](https://issues.redhat.com/browse/CNV-67900)** — As an Admin, I want custom golden images without architecture annotations to remain functional so that non-annotated images continue to work
  - *Test Scenario:* [Tier 2] Verify custom DICTs without `arch-annotation` pass through to SSP without architecture filtering and create resources normally
  - *Priority:* P0

#### sig-infra


#### sig-storage


#### sig-virt


---

### **IV. Sign-off and Approval**

This Software Test Plan requires approval from the following stakeholders:

- **Reviewers:**
  - [QE Lead / @rnester]
  - [sig-iuo representative / @nunnatsa @rllobilo @OhadRevah @albarker-rh]
  - [sig-storage representative]
  - [sig-virt representative]
  - [sig-infra representative]
- **Approvers:**
  - [QE Lead / @rnester]
