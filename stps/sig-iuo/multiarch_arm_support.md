# Openshift-virtualization-tests Test plan

## MultiArch Support enablement for ARM - Quality Engineering Plan

### **Metadata & Tracking**

- **Enhancement(s):** [VEP: Heterogeneous Cluster Support](https://github.com/kubevirt/enhancements/tree/main/veps/sig-storage/dic-on-heterogeneous-cluster)
- **Feature Tracking:** [VIRTSTRAT-494 -  MultiArch Support enablement for ARM](https://redhat.atlassian.net/browse/VIRTSTRAT-494)
- **Epic Tracking:**
  - [CNV-67900](https://redhat.atlassian.net/browse/CNV-67900) — HCO Multi-arch support
  - [CNV-26818](https://redhat.atlassian.net/browse/CNV-26818) — Virt Multi-arch worker node support
  - [CNV-76714](https://redhat.atlassian.net/browse/CNV-76714) — Infra Multi-arch support
  - [CNV-76732](https://redhat.atlassian.net/browse/CNV-76732) — Storage Multi-arch support
  - [CNV-76741](https://redhat.atlassian.net/browse/CNV-76741) — Network Multi-arch support
  - [CNV-61832](https://redhat.atlassian.net/browse/CNV-61832) — UI Multi-arch support
- **Feature Maturity:**
  - DP: N/A
  - TP: 4.21
  - GA: 4.22
- **QE Owner(s):** Harel Meir (@hmeir)
- **Owning SIG:** sig-iuo
- **Participating SIGs:** sig-virt, sig-infra, sig-storage, sig-network

**Document Conventions (if applicable):**

- **Multi-Arch:** Multi-Architecture, heterogeneous clusters with mixed CPU architectures (AMD64 + ARM64).
- **Golden image**: pre-configured VM image that is automatically imported into a boot source
- **Multiarch golden images support** - Allows deploying architecture-specific VMs from dedicated boot sources.

### **Feature Overview**

Multi-architecture support enables OpenShift Virtualization to operate on heterogeneous clusters with mixed AMD64 and ARM64 worker nodes.
This feature targets customers adopting ARM-based infrastructure alongside existing AMD64 deployments.
This STP covers the Tech Preview phase in 4.21/4.22, where multi-arch support is opt-in via feature gate. The feature gate is expected to be enabled by default in 4.23+.

---

### **I. Motivation and Requirements Review (QE Review Guidelines)**

This section documents the mandatory QE review process. The goal is to understand the feature's value,
technology, and testability before formal test planning.

#### **1. Requirement & User Story Review Checklist**

- [x] **Review Requirements**
  - *List the key D/S requirements reviewed:*
    - Architecture-aware VM scheduling; users can select a VM's target architecture.
    - All VM-related operations (lifecycle, migration, networking, storage) are supported on both architectures.
    - Workload observability across architectures.
    - Existing VMs and workloads continue to be fully functional without regression.
- [x] **Understand Value and Customer Use Cases**
  - *Describe the feature's value to customers:*
    - Customers can run ARM64 and AMD64 VMs in a single cluster, reducing operational overhead and enabling gradual ARM adoption.
  - *List the customer use cases identified:*
    - As a VM admin, I want to deploy VMs on ARM64 nodes from available boot sources after ARM64 nodes are added to the cluster.
- [x] **Testability**
  - *Note any requirements that are unclear or untestable:*
    - All requirements are testable on a heterogeneous AWS cluster.
- [x] **Acceptance Criteria**
  - *List the acceptance criteria:*
    - VM lifecycle operations are consistent with single-architecture cluster behavior on their matching CPU architecture.
    - VMs communicate regardless of the CPU architecture of their host nodes.
    - Architecture-specific golden images are provisioned for each supported architecture, and VMs can be created on matching nodes.
    - VM scheduling respects nodePlacement constraints, allowing users to target a specific supported architecture.
    - VMs survive cluster upgrade on their correct architecture nodes; arch-specific resources are preserved.
  - *Note any gaps or missing criteria:* None
- [x] **Non-Functional Requirements (NFRs)**
  - *List applicable NFRs and their targets:*
    - **Monitoring**: Platform must alert users about MultiArch misconfigurations, workload metrics across both architectures on multiarch cluster.
    - **Upgrade**: VMs survive upgrade on their correct architecture nodes. Arch-specific resources are preserved.
    - **Doc**: Drop the Tech Preview note from docs.
    - **UI**: UI testing owned by the UI team under [CNV-61832](https://redhat.atlassian.net/browse/CNV-61832).
  - *Note any NFRs not covered and why:*
    - Performance/Scalability: deferred to a future cycle
    - Security: Not applicable — no new RBAC, auth, or privilege changes introduced

#### **2. Known Limitations**

The limitations are documented to ensure alignment between development, QA, and product teams.
The following are confirmed product constraints accepted before testing begins.

- Cross-architecture live migration is not supported (AMD64 <-> ARM64).
  - *Sign-off:* Martin Tessun (@mtessun) / 2026-04-15
- Multi-arch support is opt-in in 4.22 (default-enabled in 4.23+).
  - *Sign-off:* Martin Tessun (@mtessun) / 2026-04-15
- Existing VMs are not updated: VMs that are already running will not automatically use new architecture-specific resources.
  - *Sign-off:* Martin Tessun (@mtessun) / 2026-04-15
- Custom golden images require manual architecture configuration; the platform does not validate architecture annotation values.
  - *Sign-off:* Martin Tessun (@mtessun) / 2026-04-15
- The default architecture for golden image boot sources is not user-configurable. The system automatically selects the default by control-plane node architecture.
  - *Sign-off:* Martin Tessun (@mtessun) / 2026-04-15

#### **3. Technology and Design Review**

- [x] **Developer Handoff/QE Kickoff**
  - *Key takeaways and concerns:*
    - Cross-SIG kickoff conducted with all 5 participating SIGs
    - Each SIG confirmed ownership of their multi-arch test scope
- [x] **Technology Challenges**
  - *List identified challenges:*
    - Heterogeneous cluster provisioning requires AWS with Graviton instances
    - CPU model configuration per architecture needs validation
  - *Impact on testing approach:*
    - Tests are limited to AWS platform
- [x] **API Extensions**
  - *List new or modified APIs:*
    - `vm.spec.template.spec.architecture` (string) — targets VM to specific CPU architecture
    - Multiarch golden images support enable/disable
  - *Testing impact:*
    - Multiarch golden images support must be tested.
- [x] **Test Environment Needs**
  - *See environment requirements in Section II.3 and testing tools in Section II.3.1*
- [x] **Topology Considerations**
  - *Describe topology requirements:* Feature targets MultiArch clusters only (3 amd64 control-plane, 2 amd64 workers, 2 arm64 workers)
  - *Impact on test design:* Live migration and upgrade tests require at least 2 nodes of the same architecture.
  - *Topologies not tested:* Multiarch golden images support is auto-disabled on Single Node OpenShift (SNO) clusters, even if the feature gate is enabled.

### **II. Software Test Plan (STP)**

This STP serves as the **overall roadmap for testing**, detailing the scope, approach, resources, and schedule.

#### **1. Scope of Testing**

**Testing Goals**

New functional flows specific to heterogeneous multi-arch clusters:

- **[P0]** Verify that VMs can be created on ARM and AMD node from every available boot source.
- **[P0]** Verify UDN connectivity between VMs running on ARM64 and AMD64 nodes.
- **[P0]** Verify ClusterIP/masquerade connectivity between VMs running on ARM64 and AMD64 nodes.
- **[P1]** Verify an alert fires when a golden image is annotated only with unsupported architectures.
- **[P1]** Verify an alert fires when a golden image is missing an architecture annotation.
- **[P1]** Verify an alert fires when multiarch golden images support is disabled.
- **[P1]** Verify no alert fires when nodePlacement restricts to a single architecture.
- **[P2]** Verify only base boot sources exists when disabling multiarch golden images support.

**Regression Goals**

> **NOTE:** Each SIG is responsible for ensuring their Tier 1 and Tier 2 executed regression suites cover all scenarios
> that may be affected by the multi-arch feature on heterogeneous clusters.
> Existing test suites to run on the heterogeneous cluster to verify no degradation, with both ARM64 and AMD architectures:

- **[P0]** sig-virt Tier 1 and Tier 2
- **[P0]** sig-iuo hco + observability Tier 1 and Tier 2
- **[P0]** sig-infra Tier 1 and Tier 2
- **[P0]** sig-network Tier 1 and Tier 2
- **[P0]** sig-storage Tier 1 and Tier 2

**Out of Scope (Testing Scope Exclusions)**

The following items are explicitly Out of Scope for this test cycle and represent intentional exclusions.
No verification activities will be performed for these items, and any related issues found will not be classified as defects for this release.

- **s390x architecture**
  - *Rationale:* s390x architecture is not in the scope of this feature.
  - *PM/Lead Agreement:* Martin Tessun (@mtessun) / 2026-04-15
- **Architecture-specific resource cleanup after node removal**
  - *Rationale:* Removing all nodes of a given architecture and verifying automatic cleanup of related boot sources and templates is time-consuming to test, and customers can perform manual cleanup if needed.
  - *PM/Lead Agreement:* Martin Tessun (@mtessun) / 2026-04-15
- **Cross Cluster Live Migration (CCLM) on multi-arch clusters**
  - *Rationale:* CCLM on heterogeneous clusters is not in scope for this release.
  - *PM/Lead Agreement:* Martin Tessun (@mtessun) / 2026-04-15

**Test Limitations**

- The tests are limited to AWS; no tests are done on bare metal clusters.
  - *Sign-off:* Martin Tessun (@mtessun) / 2026-04-15
- No Windows guest tested on ARM64 nodes.
  - *Sign-off:* Martin Tessun (@mtessun) / 2026-04-15
- IPv6 single-stack and dual-stack not available on AWS — multi-arch testing is IPv4 only.
  - *Sign-off:* Martin Tessun (@mtessun) / 2026-04-15
- SR-IOV, Multi-NIC, and GPU passthrough cannot be validated on AWS.
  - *Sign-off:* Martin Tessun (@mtessun) / 2026-04-15
#### **2. Test Strategy**

**Functional**

- **Functional Testing** — Validates that the feature works according to specified requirements and user stories
  - *Details:* Validate heterogeneous cluster-specific functionality.
- **Automation Testing** — Confirms test automation plan is in place for CI and regression coverage
  - *Details:* All test cases automated in openshift-virtualization-tests repo.
- **Regression Testing** — Verifies that new changes do not break existing functionality
  - *Details:* Run existing Tier 1 and Tier 2 test suites on heterogeneous cluster for both architectures. See Section II.1 for per-SIG testing responsibilities.

**Non-Functional**

- **Performance Testing** — Validates feature performance meets requirements
  - *Details:* Out of scope for initial release. Planned for the future. [CNV-63088](https://redhat.atlassian.net/browse/CNV-63088)
- **Scale Testing** — Validates feature behavior under increased load
  - *Details:* Deferred — heterogeneous cluster scale limits not yet defined. Planned for a future cycle alongside performance testing.
- **Security Testing** — Verifies security requirements, RBAC, authentication, authorization
  - *Details:* N/A — No security-specific requirements for this feature.
- **Usability Testing** — Validates user experience and accessibility requirements
  - *Details:* UI testing is owned by the UI QE team under [CNV-61832](https://redhat.atlassian.net/browse/CNV-61832).
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
- **Storage:** io2-csi,ocs
- **Network:** OVN-Kubernetes (default), IPv4
- **Required Operators:** N/A
- **Platform:** AWS (Graviton instances for ARM64 workers)
- **Special Configurations:** Multi-arch support enabled via cluster deployment

#### **3.1. Testing Tools & Frameworks**

- **Test Framework:** The framework supports running on a heterogeneous cluster; each sig must make sure that their tests run the VMs on the desired architecture.
- **CI/CD:** Jenkins job to deploy a heterogeneous cluster - Done.
- **Other Tools:** N/A

#### **4. Entry Criteria**

The following conditions must be met before testing can begin:

- [] Requirements and design documents are **approved and merged**
- [X] Test environment (MultiArch cluster) can be **set up and configured** (see Section II.3 - Test Environment)
- [X] Multi-CPU architecture support enabled in openshift-virtualization-tests repo

#### **5. Risks**

**Timeline/Schedule**

- **Risk:** Cross-SIG coordination across 5 SIGs may delay test completion. Regional instability may affect team availability and velocity.
  - **Mitigation:** Establish clear ownership per SIG early; track in Jira.
  - *Estimated impact on schedule:* Small risk, marked as Yellow.
  - *Sign-off:* Martin Tessun (@mtessun) / 2026-04-15

**Test Environment**

- **Risk:** Only 2 worker nodes per architecture — during upgrades, all VMs of a given arch are concentrated on a single node, risking resource pressure.
  - **Mitigation:** Split the upgrade VMS between the architectures, or add aditional worker node.
  - *Missing resources or infrastructure:* Additional worker nodes per architecture for upgrade testing.
  - *Sign-off:* Martin Tessun (@mtessun) / 2026-04-30
- **Risk:** Multiarch cluster availability window limits test execution time.
  - **Mitigation:** DEVOPS added option to extend cluster lifetime to 2 days. [CNV-83491](https://redhat.atlassian.net/browse/CNV-83491).
  - *Missing resources or infrastructure:* Longer cluster availability for full regression runs.
  - *Sign-off:* Martin Tessun (@mtessun) / 2026-04-15

**Untestable Aspects**

- **Risk:** SR-IOV, Multi-NIC, and GPU passthrough cannot be validated on AWS platform
  - **Mitigation:** Validated on x86 nodes only; ARM coverage deferred until bare-metal ARM test environment is available
  - *Alternative validation approach:* Rely on x86-only validation; revisit when bare-metal ARM environment becomes available.
  - *Sign-off:* Martin Tessun (@mtessun) / 2026-04-15
- **Risk:** Upgrade path from FG-disabled to FG-enabled-by-default is not testable in 4.22 (FG will be enabled by default not earlier than 4.23)
  - **Mitigation:** Full upgrade path testing deferred to 4.23
  - *Alternative validation approach:* Validate FG-enabled path in 4.22; full FG-disabled-to-enabled upgrade path deferred to 4.23.
  - *Sign-off:* Martin Tessun (@mtessun) / 2026-04-30

**Resource Constraints**

- **Mitigation:** No resource constraints identified — all SIGs have allocated QE capacity for this feature.

**Dependencies**

- **Risk:** Multi-CPU architecture support PR in openshift-virtualization-tests ([#3147](https://github.com/RedHatQE/openshift-virtualization-tests/pull/3147)) was merged without thorough review by all participating SIGs; additional changes may be required
  - **Mitigation:** Track follow-up review feedback from each SIG and address required changes promptly
  - *Dependent teams or components:* sig-virt, sig-infra, sig-storage, sig-network
  - *Sign-off:* Martin Tessun (@mtessun) / 2026-04-15
---

### **III. Test Scenarios & Traceability**

This section centralizes test scenarios for all participating SIGs. Each SIG's scenarios are grouped separately for clarity.

#### sig-iuo — New Functional Tests

- **[CNV-67900](https://redhat.atlassian.net/browse/CNV-67900)** — As a cluster Admin, I want to provide architecture-specific golden images to VM creators
  - *Test Scenario:* [Tier 2] Given multi-arch support enabled, Verify common architecture-specific boot sources become available with correct naming and labels
  - *Priority:* P0
- **[CNV-67900](https://redhat.atlassian.net/browse/CNV-67900)** — As a cluster Admin, I want alerting when golden image is annotated with unsupported architectures.
  - *Test Scenario:* [Tier 2] Given multiarch support enabled, alert fired when golden image annotated with unsupported architectures.
  - *Priority:* P1
- **[CNV-67900](https://redhat.atlassian.net/browse/CNV-67900)** — As a cluster Admin, I want alerting when golden image lacks architecture annotation.
  - *Test Scenario:* [Tier 2] Given multiarch support enabled, alert fired when golden image isn't annotated with architecture annotation.
  - *Priority:* P1
- **[CNV-67900](https://redhat.atlassian.net/browse/CNV-67900)** — As a cluster Admin, I want alerting when multiarch golden images support is disabled on a multi-architecture cluster
  - *Test Scenario:* [Tier 2] Disable multiarch golden images support on a multi-architecture cluster and verify an alert fires
  - *Priority:* P1
- **[CNV-67900](https://redhat.atlassian.net/browse/CNV-67900)** — As a cluster Admin, I want no alerting when restricting workloads placement to one architecture.
  - *Test Scenario:* [Tier 2] Disable multiarch golden images support, set nodePlacement to a single architecture, and verify no misconfiguration alert fires
  - *Priority:* P1
- **[CNV-67900](https://redhat.atlassian.net/browse/CNV-67900)** — As a cluster Admin, I want only base boot sources when disabling multiarch golden images support
  - *Test Scenario:* [Tier 2] Disable multiarch golden images support, Verify only base boot sources exists.
  - *Priority:* P2

#### sig-infra — New Functional Tests

None

#### sig-storage — New Functional Tests

None

#### sig-virt — New Functional Tests

None

#### sig-network — New Functional Tests

- **[CNV-76741](https://redhat.atlassian.net/browse/CNV-76741)** — As a VM admin, I want VMs on different architectures to communicate with each other via UDN (primary interface)
  - *Test Scenario:* [Tier 2] Verify network connectivity between an ARM64 VM and an AMD64 VM using UDN as the primary network interface
  - *Priority:* P0
- **[CNV-76741](https://redhat.atlassian.net/browse/CNV-76741)** — As a VM admin, I want VMs on different architectures to communicate with each other via primary masquerade networking
  - *Test Scenario:* [Tier 2] Verify network connectivity between an ARM64 VM and an AMD64 VM using primary masquerade networking
  - *Priority:* P0

---

### **IV. Sign-off and Approval**

- **Reviewers:**
  - QE Member (sig-iuo): @OhadRevah
  - sig-network: @yossisegev
  - sig-storage: @jpeimer
  - sig-virt:  @vsibirsk @akri3i
  - sig-infra: @geetikakay
- **Approvers:**
  - QE Architect: [Ruth Netser] (@rnetser)
  - Principal Developer (sig-iuo): @nunnatsa
  - Product Manager: [Martin Tessun] @mtessun
