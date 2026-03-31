# Openshift-virtualization-tests Test plan

## MultiArch Support enablement for ARM - Quality Engineering Plan

### **Metadata & Tracking**

- **Enhancement(s):** [VEP: Heterogeneous Cluster Support](https://github.com/kubevirt/enhancements/tree/main/veps/sig-storage/dic-on-heterogeneous-cluster)
- **Feature Tracking:** [VIRTSTRAT-494 - Multiarch Support enablement for ARM](https://issues.redhat.com/browse/VIRTSTRAT-494)
- **Epic Tracking:**
  - [CNV-67900](https://issues.redhat.com/browse/CNV-67900) — HCO Multi-arch support
  - [CNV-26818](https://issues.redhat.com/browse/CNV-26818) — Virt Multi-arch worker node support
  - [CNV-76714](https://issues.redhat.com/browse/CNV-76714) — Infra Multi-arch support
  - [CNV-76732](https://issues.redhat.com/browse/CNV-76732) — Storage Multi-arch support
  - [CNV-76741](https://issues.redhat.com/browse/CNV-76741) — Network Multi-arch support
  - [CNV-61832](https://issues.redhat.com/browse/CNV-61832) — UI Multi-arch support
- **QE Owner(s):** Harel Meir (@hmeir)
- **Owning SIG:** sig-iuo
- **Participating SIGs:** sig-virt, sig-infra, sig-storage, sig-network

**Document Conventions (if applicable):**

- **Multi-Arch:** Multi-Architecture, heterogeneous clusters with mixed CPU architectures (AMD64 + ARM64).
- **Multiarch support** - Golden images support achieved by activating a feature gate.
- **golden image**: pre-configured VM image that is automatically imported into a boot source
- **boot sources**: available for VM creation from golden images.
- **common golden images** - provided by Red Hat. Supports amd64, arm64, s390x architectures.
- **custom golden images** - User-defined images. Architecture support is the user's responsibility.
- **supported architectures** - The cluster scheduled worker node unique architectures.
- **legacy boot sources/templates** - boot sources that are not architecture-specific (e.g. `rhel9` vs `rhel9-arm64`)


### **Feature Overview**

Multi-architecture support enables OpenShift Virtualization to operate on heterogeneous clusters with mixed AMD64 and ARM64 worker nodes.
This feature targets customers adopting ARM-based infrastructure alongside existing AMD64 deployments.

---

### **I. Motivation and Requirements Review (QE Review Guidelines)**

This section documents the mandatory QE review process. The goal is to understand the feature's value,
technology, and testability before formal test planning.

#### **1. Requirement & User Story Review Checklist**

- **Review Requirements**
  - *List the key D/S requirements reviewed:*
    - Architecture-aware VM scheduling; users can select a VM's target architecture.
    - All VM-related operations (lifecycle, migration, networking, storage) are supported on both architectures.
    - Workload observability across architectures.
    - Existing VMs and workloads continue to be fully functional without regression.
- **Understand Value and Customer Use Cases**
  - *Describe the feature's value to customers:*
    - Customers can run ARM64 and AMD64 VMs in a single cluster, reducing operational overhead and enabling gradual ARM adoption.
    - VM creators can create ARM64 VMs using dedicated golden images and templates without the need to manually manage those.
  - *List the customer use cases identified:*
    - A VM admin deploys VMs on ARM64 nodes from available boot sources after ARM64 nodes are added to the cluster.
- **Testability**
  - *Note any requirements that are unclear or untestable:*
    - All requirements are testable on a heterogeneous AWS cluster.
- **Acceptance Criteria**
  - *List the acceptance criteria:*
    - VMs must be scheduled only on nodes matching their CPU architecture.
    - VM migration succeeds only between nodes of the same CPU architecture.
    - When multiarch support is enabled, architecture-specific boot sources and templates are available per supported architecture (ARM + AMD) for common golden images.
    - When multiarch support is enabled, architecture-specific boot sources and templates are available ONLY for custom golden images annotated with supported architectures.
    - When multiarch support is enabled, VMs can be created from legacy boot sources, scheduled on node with the default CPU architecture.
    - When multiarch support is enabled, adding a node with a new supported architecture results in architecture-specific boot sources and templates available for this architecture.
    - When multiarch support is enabled, removing all nodes of a supported architecture from a multi-arch cluster cleans up the corresponding architecture-specific boot sources.
    - When multiarch support is disabled and nodePlacement restricts scheduling to a specific supported architecture, VMs are scheduled only on nodes with this CPU architecture.
    - When multiarch support is enabled, new arch images can be pulled successfully only for golden images annotated with supported architectures using any pullMethod.
- **Non-Functional Requirements (NFRs)**
  - *List applicable NFRs and their targets:*
    - **Monitoring**: Platform must alert users about MultiArch misconfigurations, workload metrics across both architectures on multiarch cluster.
    - **Upgrade**: VMs survive upgrade on their correct architecture nodes. Arch-specific resources are preserved.
    - **Doc**: Drop the Tech Preview note from docs.
  - *Note any NFRs not covered and why:*
    - Performance/Scalability: deferred to a future cycle
    - Security: Not applicable — no new RBAC, auth, or privilege changes introduced

#### **2. Known Limitations**

The limitations are documented to ensure alignment between development, QA, and product teams.
The following topics will not be tested or supported.

- Cross-architecture live migration is not supported (AMD64 <-> ARM64).
- Multi-arch support is opt-in in 4.22 (default-enabled in 4.23+).
- Existing VMs are not updated: VMs that are already running will not automatically use new architecture-specific resources.
- Custom golden images require manual architecture configuration; the platform does not validate architecture annotation values.

#### **3. Technology and Design Review**

- **Developer Handoff/QE Kickoff**
  - *Key takeaways and concerns:*
    - Cross-SIG kickoff conducted with all 5 participating SIGs
    - Each SIG confirmed ownership of their multi-arch test scope
- **Technology Challenges**
  - *List identified challenges:*
    - Heterogeneous cluster provisioning requires AWS with Graviton instances
    - CPU model configuration per architecture needs validation
  - *Impact on testing approach:*
    - Tests are limited to AWS platform
- **API Extensions**
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
      - `vm.spec.template.spec.architecture` (string) - targets VM to specific CPU architecture
  - *Testing impact:*
    - VM creation with explicit architecture targeting must be tested.
    - Multiarch support enable/disable behavior must be tested.
- **Test Environment Needs**
  - *See environment requirements in Section II.3 and testing tools in Section II.3.1*
- **Topology Considerations**
  - *Describe topology requirements:* Feature targets MultiArch clusters only (3 amd64 control-plane, 2 amd64 workers, 2 arm64 workers)
  - *Impact on test design:* Live migration and upgrade tests require at least 2 nodes of the same architecture.
  - *Topologies not tested:* Multiarch support is auto-disabled on Single Node OpenShift (SNO) clusters, even if the feature gate is enabled.

### **II. Software Test Plan (STP)**

This STP serves as the **overall roadmap for testing**, detailing the scope, approach, resources, and schedule.

#### **1. Scope of Testing**

**Testing Goals**

New functional flows specific to heterogeneous multi-arch clusters:

- **[P0]** Enable multi-arch support and verify architecture-specific ARM64 and AMD64 boot sources become available for common golden images, named and labeled with their supported arch.
- **[P0]** Enable multi-arch support and verify architecture-specific boot sources become available for custom golden images only when annotated with supported architectures.
- **[P0]** Enable multi-arch support and verify alert fires when a custom golden image is annotated only with unsupported architectures, and arch-specific boot sources aren't created for it.
- **[P0]** Enable multi-arch support and verify alert fires when a custom golden image is missing an architecture annotation, and arch-specific boot sources aren't created for it.
- **[P1]** Verify alert cleaned up when MultiArch FG is disabled but nodePlacement restricts to single architecture, and arch-specific boot sources available only for this architecture.
- **[P1]** Verify upgrade preserves multi-arch configuration and VMs on both architectures
- **[P2]** Disable multi-arch support and verify architecture-specific boot sources and templates are removed
- **[P0]** Enable multi-arch support and verify architecture-specific ARM64 and AMD64 boot sources become available for common golden images, and VMs can be created from those.
- **[P0]** Enable multi-arch support and verify VMs created from legacy templates and boot sources are running on node with default CPU architecture.
- **[P0]** Enable multi-arch support and verify that adding ARM node results in template and boot sources creation
- **[P2]** Enable multi-arch support and verify that removing all ARM nodes results in template and boot sources cleanup
- **[P0]** Verify new arch-specific golden image can be pulled.
- **[P1]** Verify cross-architecture VM cloning is blocked with a clear, user-facing error message.
- **[P0]** Verify VMs are scheduled only on nodes matching their CPU architecture.
- **[P0]** Verify VM live migration succeeds between two same-architecture nodes.
- **[P0]** Verify cross-architecture migration is blocked with a clear, user-facing error message
- **[P0]** Verify VMs can be created from instancetypes.
- **[P0]** Verify VMs migrate to same-architecture nodes during upgrade and placement is preserved.
- **[P0]** Verify network connectivity between VMs running on different architectures (ARM64 VM <-> AMD64 VM)

**Regression Goals**

Existing test suites to run on the heterogeneous cluster to verify no degradation:

- **[P0]** sig-virt Tier 1 and Tier 2 on both architectures
- **[P0]** sig-iuo Tier 1 and Tier 2
- **[P0]** sig-infra Tier 1 and Tier 2
- **[P1]** sig-network Tier 1 and Tier 2 (currently zero ARM64 coverage)
- **[P1]** sig-storage Tier 1 and Tier 2 (currently zero ARM64 coverage)
- **[P2]** Observability tests on multi-arch cluster

**Per-SIG Testing Responsibilities**

> **NOTE:** Each SIG is responsible for ensuring their Tier 1 and Tier 2 executed regression suites cover all scenarios
> that may be affected by the multi-arch feature on heterogeneous clusters.

- **sig-iuo (owning SIG):** Multiarch support configuration, golden image provisioning lifecycle, alerts. Owns overall coordination.
  - *Regression:* Tier 1 and Tier 2 (iuo and observability)
- **sig-virt:** VM deployment on ARM64 and AMD64 nodes, same-arch live migration, cross-arch blocking, scheduling, CPU model per architecture.
  - *Regression:* Tier 1 and Tier 2
- **sig-infra:** Architecture-specific VM templates and backward compatibility, instance types.
  - *Regression:* Tier 1 and Tier 2
- **sig-storage:** Golden image import per architecture — verify correct golden images are imported and boot sources are available for each supported architecture.
  - *Regression:* Tier 1 and Tier 2
- **sig-network:** Network connectivity between VMs on different architectures.
  - *Regression:* Tier 1 and Tier 2

**Out of Scope (Testing Scope Exclusions)**

The following items are explicitly Out of Scope for this test cycle and represent intentional exclusions.
No verification activities will be performed for these items, and any related issues found will not be classified as defects for this release.

- **Update existing VMs**
  - *Rationale:* Old Running VMs won't use new arch-specific resources.
  - *PM/Lead Agreement:* [Name/Date]
- **Cross-arch live migration**
  - *Rationale:* Live migration between different architectures (e.g., amd64 to arm64) is not supported
  - *PM/Lead Agreement:* [Name/Date]
- **Custom golden image architecture validation**
  - *Rationale:* Custom golden images require manual architecture configuration; It is the user's responsibility to ensure correct architecture annotation values.
  - *PM/Lead Agreement:* [Name/Date]
- **s390x architecture**
  - *Rationale:* s390x architecture is not in the scope of this feature.
  - *PM/Lead Agreement:* [Name/Date]
- **GPU passthrough for ARM64**
  - *Rationale:* Not in scope per VIRTSTRAT-494.
  - *PM/Lead Agreement:* [Name/Date]

**Test Limitations**

- The tests are limited to AWS; no tests are done on bare metal clusters.
- 12-hour ARM cluster availability window.
- No Windows guest tested on ARM64.
- IPv6 single-stack and dual-stack not available on AWS — multi-arch testing is IPv4 only.

#### **2. Test Strategy**

**Functional**

- **Functional Testing** — Validates that the feature works according to specified requirements and user stories
  - *Details:* Validate heterogeneous cluster-specific functionality.
- **Automation Testing** — Confirms test automation plan is in place for CI and regression coverage
  - *Details:* All test cases automated in openshift-virtualization-tests repo.
- **Regression Testing** — Verifies that new changes do not break existing functionality
  - *Details:* Run existing Tier 1 and Tier 2 test suites on heterogeneous cluster
  for both architectures. See Section II.1 for per-SIG testing responsibilities.

**Non-Functional**

- **Performance Testing** — Validates feature performance meets requirements
  - *Details:* Out of scope for initial release. Planned for the future. [CNV-63088](https://redhat.atlassian.net/browse/CNV-63088)
- **Scale Testing** — Validates feature behavior under increased load
  - *Details:* Out of scope.
- **Security Testing** — Verifies security requirements, RBAC, authentication, authorization
  - *Details:* N/A — No security-specific requirements for this feature.
- **Usability Testing** — Validates user experience and accessibility requirements
  - *Details:* UI work was completed under [CNV-61832](https://redhat.atlassian.net/browse/CNV-61832). UI testing is owned by the UI team.
- **Monitoring** — Does the feature require metrics and/or alerts?
  - *Details:* Alerts and metrics for multiarch misconfigurations.

**Integration & Compatibility**

- **Compatibility Testing** — Ensures feature works across supported platforms, versions, and configurations
  - *Details:* Tests will be executed on AWS only.
- **Upgrade Testing** — Validates upgrade paths from previous versions
  - *Details:* Verify existing VMs and boot sources are preserved. Verify multi-arch support is preserved across upgrades.
- **Dependencies** — Blocked by deliverables from other components/products
  - *Details:* Each participating SIG owns their test automation.
- **Cross Integrations** — Does the feature affect other features or require testing by other teams?
  - *Details:* This STP coordinates testing across 5 SIGs. Each SIG is responsible for running their regression suites on the heterogeneous cluster.

**Infrastructure**

- **Cloud Testing** — Does the feature require multi-cloud platform testing?
  - *Details:* No; tests are executed on AWS only.

#### **3. Test Environment**

- **Cluster Topology:** MultiArch cluster with 3 control-plane and 4 worker nodes
- **OCP & OpenShift Virtualization Version(s):** OCP 4.22 with OpenShift Virtualization 4.22
- **CPU Virtualization:** MultiArch cluster (3 amd64 control-plane, 2 amd64 workers, 2 arm64 workers). AMD64 workers use hardware virtualization (VT-x), ARM64 Graviton workers use ARM virtualization extensions.
- **Compute Resources:** Minimum per worker node: 16 vCPUs, 32GB RAM
- **Special Hardware:** N/A
- **Storage:** io2-csi storage class (AWS EBS io2 CSI driver)
- **Network:** OVN-Kubernetes (default), IPv4
- **Required Operators:** N/A
- **Platform:** AWS (Graviton instances for ARM64 workers)
- **Special Configurations:** HCO configured with multi-arch support enabled

#### **3.1. Testing Tools & Frameworks**

- **Test Framework:** The framework supports running on a heterogeneous cluster; each sig must make sure that their tests run the VMs on the desired architecture.
- **CI/CD:** Jenkins job to deploy a heterogeneous cluster - Done.
- **Other Tools:** N/A

#### **4. Entry Criteria**

The following conditions must be met before testing can begin:

- [ ] Requirements and design documents are **approved and merged**
- [X] Test environment (MultiArch cluster) can be **set up and configured**
- [X] Multi-CPU architecture support enabled in openshift-virtualization-tests repo


#### **5. Risks**

**Timeline/Schedule**

- **Risk:** Cross-SIG coordination across 5 SIGs may delay test completion. Israel in war currently.
  - **Mitigation:** Establish clear ownership per SIG early; track in Jira.
  - *Estimated impact on schedule:* Small risk, marked as Yellow.

**Test Coverage**

- **Risk:** OS coverage on ARM64 is narrower than AMD64; network, storage, observability gotta feature out that will run on ARM.
  - **Mitigation:** storage, network and iuo teams need to detect arm related d/s tests and mark those.
  - *Areas with reduced coverage:* sig-network, sig-storage, observability.

**Test Environment**

- **Risk:** 12-hour ARM64 cluster availability window limits test execution time.
  - **Mitigation:** Prioritize test execution. Verify if the timeout can be longer.
  - *Missing resources or infrastructure:* Longer cluster availability for full regression runs.
- **Risk:** Adding or removing worker nodes to change cluster architecture mix is slow and costly.
  - **Mitigation:** Use HCO `nodePlacement` to simulate an architecture being present or absent (pick/unpick one architecture) instead of relying on physical node add/remove.

**Untestable Aspects**

- **Risk:** Special infrastructure cannot be validated on AWS platform
  - **Mitigation:** Validated on x86 nodes only; ARM coverage deferred until bare-metal ARM test environment is available
- **Risk:** Upgrade path from FG-disabled to FG-enabled-by-default is not testable in 4.22 (FG will be enabled by default not earlier than 4.23)
  - **Mitigation:** Full upgrade path testing deferred to 4.23

**Dependencies**

- **Risk:** Multi-CPU architecture support PR in openshift-virtualization-tests ([#3147](https://github.com/RedHatQE/openshift-virtualization-tests/pull/3147)) was merged without thorough review by all participating SIGs; additional changes may be required
  - **Mitigation:** Track follow-up review feedback from each SIG and address required changes promptly
  - *Dependent teams or components:* sig-virt, sig-infra, sig-storage, sig-network

**Others**
- **Risk:** Known non-blocker bugs may impact test results:
  1. [[UI] architecture is incorrect for fedora arm and inconsistent on UI for other os](https://issues.redhat.com/browse/CNV-68981)
  2. [[Storage] Arch-specific DataSources (arm64) persist after removing arm64 nodes](https://issues.redhat.com/browse/CNV-68996)
  - **Mitigation:** Make sure they are fixed & verified before GA

---

### **III. Test Scenarios & Traceability**

This section centralizes test scenarios for all participating SIGs. Each SIG's scenarios are grouped separately for clarity.

**sig-iuo — New Functional Tests**

- **[CNV-67900](https://redhat.atlassian.net/browse/CNV-67900)** — As a cluster Admin, I want available ARM64 and AMD64 boot sources for common golden images
  - *Test Scenario:* [Tier 2] With multi-arch support enabled, verify common architecture-specific boot sources become available with correct naming and labels
  - *Priority:* P0
- **[CNV-67900](https://redhat.atlassian.net/browse/CNV-67900)** — As a cluster Admin, I want architecture-specific boot sources for custom golden images when they are annotated with supported architectures.
  - *Test Scenario:* [Tier 2] Verify custom golden images only receive architecture-specific boot sources when annotated with supported architectures
  - *Priority:* P0
- **[CNV-67900](https://redhat.atlassian.net/browse/CNV-67900)** — As a cluster Admin, I want to be alerted for golden images with unsupported-architecture-only annotations, and boot sources are not available for those.
  - *Test Scenario:* [Tier 2] Create custom golden image annotated with unsupported architectures, verify alert is being fired and boot sources are not created.
  - *Priority:* P0
- **[CNV-67900](https://redhat.atlassian.net/browse/CNV-67900)** — As a cluster Admin, I want to be alerted for golden images without architecture annotation, and no boot sources created until I add one
  - *Test Scenario:* [Tier 2] Create custom golden image without architecture annotation, verify alert is being fired, and boot sources aren't created.
  - *Priority:* P0
- **[CNV-67900](https://redhat.atlassian.net/browse/CNV-67900)** — As a cluster Admin, I want no alert when limiting workload nodePlacement to a specific architecture.
  - *Test Scenario:* [Tier 2] Disable multiarch support, set nodePlacement to ARM architecture, and verify alert is cleaned up and boot sources available only for this architecture.
  - *Priority:* P1
- **[CNV-67900](https://redhat.atlassian.net/browse/CNV-67900)** — As a cluster Admin, I want multi-arch support preserved after upgrade
  - *Test Scenario:* [Tier 2] Verify upgrade preserves multi-arch configuration and VMs on both architectures
  - *Priority:* P1
- **[CNV-67900](https://redhat.atlassian.net/browse/CNV-67900)** — As a cluster Admin, I want related architecture-specific boot sources and templates removed when multi-arch support is disabled
  - *Test Scenario:* [Tier 2] Disable multi-arch support and verify related architecture-specific boot sources are removed
  - *Priority:* P2

**sig-infra — New Functional Tests**

- **[CNV-76714](https://redhat.atlassian.net/browse/CNV-76714)** — As a VM admin, I want to create VMs from architecture-specific templates and boot sources for each supported architecture.
  - *Test Scenario:* [Tier 2] Deploy and verify a running VM from each available on AMD64 and ARM64 nodes
  - *Priority:* P0
- **[CNV-76714](https://redhat.atlassian.net/browse/CNV-76714)** — As a VM admin, I want VMs created from legacy templates and boot sources to run on nodes with the cluster default CPU architecture
  - *Test Scenario:* [Tier 2] Deploy and verify a running VM from all legacy boot sources and templates on the default CPU architecture.
  - *Priority:* P0
- **[CNV-76714](https://redhat.atlassian.net/browse/CNV-76714)** — As a cluster Admin, I want boot sources and templates created when a node with a new supported architecture is added
  - *Test Scenario:* [Tier 2] Add an ARM64 node to a single-arch cluster with multiarch support enabled and verify architecture-specific boot sources and templates are created for the new architecture
  - *Priority:* P0
- **[CNV-76714](https://redhat.atlassian.net/browse/CNV-76714)** — As a cluster Admin, I want architecture-specific boot sources and templates cleaned up when all nodes of that architecture are removed
  - *Test Scenario:* [Tier 2] Remove all ARM64 nodes from a multi-arch cluster and verify architecture-specific boot sources and templates for ARM64 are cleaned up
  - *Priority:* P2

**sig-storage — New Functional Tests**

- **[CNV-76732](https://redhat.atlassian.net/browse/CNV-76732)** — As a cluster admin, I want golden images imported for the correct architecture
  - *Test Scenario:* [Tier 2] Verify golden image import pulls the correct architecture-specific image and boot sources become available
  - *Priority:* P0
- **[CNV-76732](https://redhat.atlassian.net/browse/CNV-76732)** — As a cluster admin, I want cross-architecture VM cloning to be blocked
  - *Test Scenario:* [Tier 2] Attempt to clone a VM to a node of a different architecture and verify the operation is blocked with a clear, user-facing error message
  - *Priority:* P1

**sig-virt — Functional Tests**

- **[CNV-26818](https://redhat.atlassian.net/browse/CNV-26818)** — As a VM admin, I want to run VMs from all available boot sources on each supported architecture
  - *Test Scenario:* [Tier 2] Deploy and verify a running VM from each available boot source on AMD64 and ARM64 nodes
  - *Priority:* P0
- **[CNV-26818](https://redhat.atlassian.net/browse/CNV-26818)** — As a cluster admin, I want live migration to succeed between two nodes of the same architecture
  - *Test Scenario:* [Tier 2] Deploy ARM VM and migrate it only to other ARM node.
  - *Priority:* P0
- **[CNV-26818](https://redhat.atlassian.net/browse/CNV-26818)** — As a cluster admin, I want cross-architecture migration to be blocked
  - *Test Scenario:* [Tier 2] Verify cross-arch migration fails with clear, user-facing error
  - *Priority:* P0
- **[CNV-26818](https://redhat.atlassian.net/browse/CNV-26818)** — As a VM admin, I want to create VMs from instancetypes on a multi-architecture cluster
  - *Test Scenario:* [Tier 2] Verify VMs can be created from instancetypes on both AMD64 and ARM64
  - *Priority:* P0
- **[CNV-26818](https://redhat.atlassian.net/browse/CNV-26818)** — As a cluster admin, I want VMs to migrate to same-arch nodes during upgrade
  - *Test Scenario:* [Tier 2] Verify arm64 and amd64 VMs are migrated to same-architecture nodes during upgrades and placement preserved
  - *Priority:* P0

**sig-network — New Functional Tests**

- **[CNV-76741](https://redhat.atlassian.net/browse/CNV-76741)** — As a VM admin, I want VMs on different architectures to communicate with each other
  - *Test Scenario:* [Tier 2] Verify network connectivity between an ARM64 VM and an AMD64 VM
  - *Priority:* P0

---

### **IV. Sign-off and Approval**

- **Reviewers:**
  - QE Members (sig-iuo):  @rllobilo @OhadRevah @albarker-rh
  - Dev Members (sig-iuo): @orenc1
  - QE Members (sig-network):
  - Dev Members (sig-network):
  - QE Members (sig-storage):
  - Dev Members (sig-storage):
  - QE Members (sig-virt):
  - Dev Members (sig-virt):
  - QE Members (sig-infra):
  - Dev Members (sig-infra):
- **Approvers:**
  - QE Architect: [Ruth Netser](@rnetser)
  - Principal Developer (sig-iuo): @nunnatsa
