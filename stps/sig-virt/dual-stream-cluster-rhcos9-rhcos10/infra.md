# OpenShift Virtualization Tests Test Plan

## **[Dual-Stream RHCOS Support — Infrastructure Scope] - Quality Engineering Plan**

### **Metadata & Tracking**

- **Enhancement(s):** [VIRTSTRAT-83](https://issues.redhat.com/browse/VIRTSTRAT-83) — no separate VEP or HLD for sig-infra; infrastructure validation is defined in this child STP.
- **Feature Tracking:** [VIRTSTRAT-83](https://issues.redhat.com/browse/VIRTSTRAT-83) (parent feature); sig-infra QE epic per [parent STP](./stp.md): [CNV-86242](https://issues.redhat.com/browse/CNV-86242)
- **Epic Tracking:** [CNV-85277](https://issues.redhat.com/browse/CNV-85277)
- **Parent STP:** [Dual-Stream RHCOS Support (parent)](./stp.md)
- **Feature Maturity:**
  - DP: N/A
  - TP: v4.22
  - GA: v5.0
- **QE Owner(s):** Michal Jankowski (@mijankow)
- **SIG:** sig-infra

**Document Conventions (if applicable):**

- RHCOS = Red Hat CoreOS, the immutable container-optimized OS used for OpenShift worker nodes.
- dual-stream cluster = a cluster running both RHCOS 9 and RHCOS 10 worker nodes simultaneously.

### **Feature Overview**

OpenShift Virtualization supports dual-stream clusters running both RHCOS 9 and RHCOS 10 worker nodes simultaneously.
Customers can upgrade their clusters from RHCOS 9 to RHCOS 10 nodes gradually, without service disruption — live migration must work correctly across node types.

**This child STP covers the CNV 5.0 GA validation scope** for sig-infra. CNV 4.22/4.23 Tech Preview coverage belongs to the earlier 4.22-era STP work and is **out of scope** for this document. This STP defines infrastructure test coverage for Windows on CNV 5.0 single-stream (RHCOS 9-only) and dual-stream worker topologies, RHEL guest OS operations on dual-stream clusters only, and RHEL live migration on dual-stream clusters only.

This STP covers the infrastructure-specific aspects of the feature, especially risks related to:

a) operating on VMs with Windows as guest OS
b) operating on VMs with RHEL as guest OS
c) live migration operations

---

### **I. Motivation and Requirements Review (QE Review Guidelines)**

#### **1. Requirement & User Story Review Checklist**

- [x] **Review Requirements**
  - *SIG-specific requirements:* See Acceptance Criteria and Testing Goals (Sections I.1 and II.1).

- [x] **Understand Value and Customer Use Cases**
  - *Describe the feature's value to customers:* Customers can run mixed RHCOS 9 and RHCOS 10 worker nodes and move VM workloads between them using live migration while gradually adopting RHCOS 10.
  - *List the customer use cases identified:*
    - As a cluster admin, I want Windows VMs to run correctly on CNV 5.0 single-stream (RHCOS 9-only) and dual-stream worker topologies, and RHEL VMs to run correctly on dual-stream topologies, so that guest OS support is preserved during cluster transition.
    - As a VM operator, I want to live-migrate RHEL VMs between RHCOS 9 and RHCOS 10 worker nodes on a dual-stream cluster without guest workload disruption.

- [x] **Acceptance Criteria**
  - On a CNV 5.0 / KubeVirt 1.9 cluster with RHCOS 9-only workers, a Windows VM reaches Running phase and passes guest connectivity checks.
  - On a CNV 5.0 / KubeVirt 1.9 dual-stream cluster, a Windows VM reaches Running phase and passes guest connectivity checks.
  - On a CNV 5.0 / KubeVirt 1.9 dual-stream cluster, a RHEL VM reaches Running phase after create and start operations.
  - On a CNV 5.0 / KubeVirt 1.9 dual-stream cluster, a RHEL VM live-migrated from an RHCOS 9 worker to an RHCOS 10 worker remains in Running phase for the full migration window.
  - While a RHEL VM live-migrates from an RHCOS 9 worker to an RHCOS 10 worker on a CNV 5.0 / KubeVirt 1.9 dual-stream cluster, a guest workload started before migration remains reachable throughout the migration window without interruption or guest restart.
  - On a CNV 5.0 / KubeVirt 1.9 dual-stream cluster, a RHEL VM live-migrated from an RHCOS 10 worker to an RHCOS 9 worker remains in Running phase for the full migration window.
  - While a RHEL VM live-migrates from an RHCOS 10 worker to an RHCOS 9 worker on a CNV 5.0 / KubeVirt 1.9 dual-stream cluster, a guest workload started before migration remains reachable throughout the migration window without interruption or guest restart.
  - After successful operation on a CNV 5.0 / KubeVirt 1.9 dual-stream cluster, a RHEL VM can be deleted.

- [x] **Testability**
  - *Note any SIG-specific requirements that are unclear or untestable:* Coverage maps to existing tests under `tests/infrastructure/instance_types/supported_os` in openshift-virtualization-tests. Dedicated CI lanes run these selections.

- [x] **Non-Functional Requirements (NFRs)**
  - *List applicable NFRs and their targets:* None — no new non-functional requirements introduced by this feature.
  - *Note any NFRs not covered and why:*
    - Performance: no new performance requirements introduced; covered by parent STP.
    - Security: no new auth changes; covered by parent STP.
    - Monitoring/Observability: no new infrastructure metrics or alerts required.
    - Scalability: no new scale requirements; existing cluster-level live migration parallelism limits apply (see parent STP).
    - UI: no UI changes; existing guest OS workflows are preserved.
    - Documentation: no new infrastructure documentation requirements; covered by parent STP.

#### **2. Known Limitations**

- **Testing is limited to RHCOS-based worker nodes.** Control plane and infrastructure nodes are out of scope — VMs are not scheduled or migrated on those nodes.
  - *Sign-off:* Ronen Sde-Or, 09/2026

#### **3. Technology and Design Review**

- [x] **Developer Handoff/QE Kickoff**
  - *Key takeaways and concerns:* See Testing Goals (Section II.1) and Test Strategy (Section II.2).

- [x] **Technology Challenges**
  - *List identified challenges:* Introducing a new RHCOS version and mixed cluster configuration may affect VM migration scenarios or Windows VM operation.
  - *Impact on testing approach:* Testing must validate Windows VM operations on CNV 5.0 single-stream and dual-stream topologies, RHEL VM operations on dual-stream clusters, and bidirectional RHEL live migration on dual-stream clusters.

- [x] **API Extensions**
  - *List new or modified user-facing APIs:* No new APIs required for this feature.
  - *Testing impact:* N/A

- [x] **Test Environment Needs**
  - *See environment requirements in Section II.3 and testing tools in Section II.3.1*

- [x] **Topology Considerations**
  - *Describe topology requirements:* CNV 5.0 dual-stream cluster with at least one RHCOS 9 and one RHCOS 10 worker node; CNV 5.0 single-stream RHCOS 9-only cluster for regression selections.
  - *Impact on test design:* Live migration tests run on dual-stream clusters only; VMs must be pinned to specific node types and verify cross-version migration for RHEL guests.

### **II. Software Test Plan (STP)**

#### **1. Scope of Testing**

**Testing Goals**

- **[P0]** As a cluster admin, Windows VMs reach Running phase and pass guest connectivity checks on CNV 5.0 single-stream (RHCOS 9-only) and dual-stream worker topologies.
- **[P0]** As a VM operator, RHEL VMs can be live-migrated between RHCOS 9 and RHCOS 10 worker nodes on a CNV 5.0 dual-stream cluster in both directions without guest workload disruption.
- **[P1]** As a cluster admin, RHEL VMs can be created, started, and deleted on a CNV 5.0 dual-stream cluster.
- **P0 failure-path coverage:** Negative scenarios for the P0 goals above (guest OS operation failures and unsuccessful RHEL live migration on dual-stream clusters) are **not tested in this child STP**. Rationale and PM/Lead agreement are documented under **P0 failure-path scenarios on dedicated CNV 5.0 infra lanes** in Out of Scope below. No Section III scenarios apply to those exclusions.

**Out of Scope (Testing Scope Exclusions)**

- **Non-RHCOS worker node variants and mixed control-plane configurations**
  - *Rationale:* This feature targets RHCOS worker nodes only; control plane and non-RHCOS worker variants are out of scope.
  - *PM/Lead Agreement:* Ronen Sde-Or, 09/2026

- **CNV 4.22/4.23 Tech Preview infra validation**
  - *Rationale:* This child STP covers CNV 5.0 GA infra validation only; Tech Preview coverage belongs to the parent STP and earlier 4.22-era work.
  - *PM/Lead Agreement:* Ruth Netser, 09/2026

- **P0 failure-path scenarios on dedicated CNV 5.0 infra lanes**
  - *Rationale:* Dedicated `supported_os` infra lanes validate successful Windows/RHEL guest operation and successful RHEL live migration only. Deliberate failure injection (guest OS faults, forced unsuccessful migration with recovery expectations) is not part of the lane selection and is not owned by this child STP.
  - *PM/Lead Agreement:* Ruth Netser, 09/2026

**Test Limitations**

- **Testing is limited to worker nodes.** Full infrastructure regression on every topology combination is not executed — targeted supported_os selections and dedicated CI lanes cover the infra scope (see Test Strategy, Section II.2).
  - *Sign-off:* Michal Jankowski, 09/2026

---

#### **2. Test Strategy**

**Functional**

- [x] **Functional Testing** — Validates Windows VM operations on CNV 5.0 single-stream (RHCOS 9-only) and dual-stream topologies, RHEL VM operations on dual-stream clusters only, and bidirectional RHEL live migration on dual-stream clusters.
  - *Details:* All coverage uses `tests/infrastructure/instance_types/supported_os`: Windows via `TestCommonPreferenceWindows` on RHCOS 9-only and dual-stream lanes; RHEL create/start/delete via `TestVMCreationAndValidation` / `TestVMDeletion` on dual-stream; RHEL live migration via `TestVMMigrationAndState` on dual-stream only. P0 failure-path scenarios are excluded per Out of Scope (Section II.1).

- [x] **Automation Testing** — Confirms test automation plan is in place for CI and regression coverage.
  - *Details:* All scenarios run in dedicated CI lanes (see Section II.3.1).

- [x] **Regression Testing** — Verifies that new changes do not break existing functionality.
  - *Details:* supported_os infrastructure regression selections per CNV 5.0 topology:
    - **CNV 5.0, RHCOS 9-only:** path `tests/infrastructure/instance_types/supported_os` with `-m infrastructure`; explicitly include `TestCommonPreferenceWindows`; deselect `TestVMMigrationAndState` in `test_rhel_os.py`; ignore CentOS and Fedora tests.
    - **CNV 5.0, dual-stream:** path `tests/infrastructure/instance_types/supported_os` — `TestCommonPreferenceWindows`; RHEL `TestVMCreationAndValidation`, `TestVMMigrationAndState`, and `TestVMDeletion` in `test_rhel_os.py`.

- [ ] **Self-Validation Testing** — Tests to include in the self-validation package
  - *Details:* Not in sig-infra child scope — see [parent STP § II.2 Test Strategy](./stp.md#2-test-strategy).

**Non-Functional**

- [ ] **Performance Testing**
  - *Details:* Not in sig-infra child scope — see [parent STP § II.2](./stp.md#2-test-strategy).

- [ ] **Scale Testing**
  - *Details:* Not in sig-infra child scope — see [parent STP § II.2](./stp.md#2-test-strategy).

- [ ] **Security Testing**
  - *Details:* Not in sig-infra child scope — see [parent STP § II.2](./stp.md#2-test-strategy).

- [ ] **Usability Testing**
  - *Details:* Not in sig-infra child scope — no UI changes; see [parent STP § II.2](./stp.md#2-test-strategy).

- [ ] **Monitoring**
  - *Details:* Not in sig-infra child scope — no new metrics or alerts; see [parent STP § II.2](./stp.md#2-test-strategy).

**Integration & Compatibility**

- [ ] **Compatibility Testing**
  - *Details:* Cross-version and platform compatibility for the dual-stream feature is owned by the [parent STP](./stp.md#2-test-strategy). This child STP documents sig-infra guest OS and migration selections only; bidirectional migration scenarios remain under Functional Testing above.

- [ ] **Upgrade Testing**
  - *Details:* Not in sig-infra child scope — see [parent STP § II.2](./stp.md#2-test-strategy).

- [x] **Dependencies**
  - *Details:* Dedicated CNV 5.0 CI lanes are provisioned and available ([CNV-92281](https://issues.redhat.com/browse/CNV-92281) — Closed / Done): `test-pytest-cnv-5.0-infrastructure-rhcos9`, `test-pytest-cnv-5.0-infrastructure-dualstream`.

- [ ] **Cross Integrations**
  - *Details:* Not in sig-infra child scope — see [parent STP § II.2](./stp.md#2-test-strategy).

**Infrastructure**

- [ ] **Cloud Testing**
  - *Details:* Not applicable; this feature targets bare-metal RHCOS nodes only.

#### **3. Test Environment**

Covered by the [parent STP](./stp.md). Infrastructure-specific requirements:

- **FIPS:** enabled (see parent STP, Section II.3)

- **Cluster Topology:**
  - **Dual-stream testing (CNV 5.0):** High-availability (HA) bare-metal cluster — 3-control-plane / 3-worker minimum, with at least one RHCOS 9 and one RHCOS 10 worker node. SNO or compact clusters are not supported.
  - **RHCOS 9-only testing (CNV 5.0):** Standard 3-control-plane / 3-worker bare-metal cluster with all workers on RHCOS 9.

- **OCP & OpenShift Virtualization Version(s):** OCP 5.0 with CNV 5.0 (KubeVirt 1.9)

- **CPU Virtualization:** VT-x (Intel) or AMD-V enabled

- **Compute Resources:** Minimum per worker node: 8 vCPUs, 32GB RAM

- **Special Hardware:** N/A

- **Storage:** ocs-storagecluster-ceph-rbd-virtualization — RWX shared storage with Block volume mode required for live migration scenarios

- **Network:** Standard — no special network configuration needed beyond the standard test environment.

- **Required Operators:** OpenShift Virtualization; OpenShift Data Foundation (provides `ocs-storagecluster-ceph-rbd-virtualization`)

- **Platform:** Bare metal. Dual-stream and single-stream clusters provisioned by QE DevOps tooling.

- **Special Configurations:** Worker nodes labeled by RHCOS version for VM scheduling and migration targeting; FIPS enabled per parent STP.

#### **3.1. Testing Tools & Frameworks**

- **Test Framework:** Standard. Tests require logic to identify nodes by RHCOS version, pin VMs to specific nodes before migration, and verify that migration crosses between RHCOS 9 and RHCOS 10 nodes.

- **CI/CD:** Two dedicated CNV 5.0 lanes cover the infrastructure testing goals ([CNV-92281](https://issues.redhat.com/browse/CNV-92281)):
  - `test-pytest-cnv-5.0-infrastructure-rhcos9` — `tests/infrastructure/instance_types/supported_os` selections (Section II.2)
  - `test-pytest-cnv-5.0-infrastructure-dualstream` — `tests/infrastructure/instance_types/supported_os` selections (Section II.2)

- **Other Tools:** N/A

#### **4. Entry Criteria**

The following conditions must be met before testing can begin:

- [x] Requirements and design documents are **approved and merged** (parent STP and this child STP)
- [x] Test environment can be **set up and configured** (see Section II.3)
- [x] Both dedicated CNV 5.0 CI lanes are provisioned and operational
- [x] `supported_os` infrastructure tests are available in openshift-virtualization-tests

#### **5. Risks**

**Test Coverage**

- **Risk:** Mixed RHCOS 9 and RHCOS 10 kernel versions may affect Windows VM operation or live migration behavior differently per node type.
  - **Mitigation:** Run targeted Windows scenarios on single-stream and dual-stream lanes and RHEL lifecycle/migration on dual-stream lanes; investigate failures per guest OS and node type.
  - *Areas with reduced coverage:* Full Gating infrastructure suite is not run on every topology — only the `supported_os` selections listed in Section II.2.
  - *Sign-off:* Michal Jankowski, 09/2026

**Dependencies**

- **Risk:** Dedicated CI lanes depend on QE DevOps provisioning and maintenance.
  - **Mitigation:** Track lane setup and execution status in [CNV-92281](https://issues.redhat.com/browse/CNV-92281).
  - *Third-party services or blockers:* QE DevOps team
  - *Sign-off:* Michal Jankowski, 09/2026

---

### **III. Test Scenarios & Traceability**

Scenarios below map to **existing** automated tests under
`tests/infrastructure/instance_types/supported_os` in
[openshift-virtualization-tests](https://github.com/RedHatQE/openshift-virtualization-tests)
(no new tests / no STD required). Lane names match Section II.3.1 CI/CD.

- **[CNV-85277]** — As a cluster admin, I want a Windows VM to run correctly on a CNV 5.0 cluster with RHCOS 9-only workers.
  - *Test Scenario:* [Tier 2] Verify Windows VM reaches Running phase and passes guest connectivity checks on RHCOS 9-only workers.
  - *Test location:* `tests/infrastructure/instance_types/supported_os/test_windows_os.py` — `TestCommonPreferenceWindows` (`test_create_vm`, `test_start_vm`, guest checks).
  - *CI lane:* `test-pytest-cnv-5.0-infrastructure-rhcos9`
  - *Priority:* P0

- **[CNV-85277]** — As a cluster admin, I want a Windows VM to run correctly on a CNV 5.0 dual-stream cluster.
  - *Test Scenario:* [Tier 2] Verify Windows VM reaches Running phase and passes guest connectivity checks on a CNV 5.0 dual-stream cluster.
  - *Test location:* `tests/infrastructure/instance_types/supported_os/test_windows_os.py` — `TestCommonPreferenceWindows` (`test_create_vm`, `test_start_vm`, guest checks).
  - *CI lane:* `test-pytest-cnv-5.0-infrastructure-dualstream`
  - *Priority:* P0

- **[CNV-85277]** — As a VM operator, I want a RHEL VM to remain Running while live-migrating from an RHCOS 9 worker to an RHCOS 10 worker on a CNV 5.0 dual-stream cluster.
  - *Test Scenario:* [Tier 2] Verify RHEL VM remains in Running phase for the full RHCOS 9 → RHCOS 10 migration window.
  - *Test location:* `tests/infrastructure/instance_types/supported_os/test_rhel_os.py` — `TestVMMigrationAndState` (`test_migrate_vm`).
  - *CI lane:* `test-pytest-cnv-5.0-infrastructure-dualstream`
  - *Priority:* P0

- **[CNV-85277]** — As a VM operator, I want guest workload continuity when live-migrating a RHEL VM from an RHCOS 9 worker to an RHCOS 10 worker on a CNV 5.0 dual-stream cluster.
  - *Test Scenario:* [Tier 2] Verify a guest workload started before RHCOS 9 → RHCOS 10 migration remains reachable throughout the migration window without interruption or guest restart.
  - *Test location:* `tests/infrastructure/instance_types/supported_os/test_rhel_os.py` — `TestVMMigrationAndState` (`test_pause_unpause_after_migrate`, `test_verify_virtctl_guest_agent_data_after_migrate`).
  - *CI lane:* `test-pytest-cnv-5.0-infrastructure-dualstream`
  - *Priority:* P0

- **[CNV-85277]** — As a VM operator, I want a RHEL VM to remain Running while live-migrating from an RHCOS 10 worker to an RHCOS 9 worker on a CNV 5.0 dual-stream cluster.
  - *Test Scenario:* [Tier 2] Verify RHEL VM remains in Running phase for the full RHCOS 10 → RHCOS 9 migration window.
  - *Test location:* `tests/infrastructure/instance_types/supported_os/test_rhel_os.py` — `TestVMMigrationAndState` (`test_migrate_vm`).
  - *CI lane:* `test-pytest-cnv-5.0-infrastructure-dualstream`
  - *Priority:* P0

- **[CNV-85277]** — As a VM operator, I want guest workload continuity when live-migrating a RHEL VM from an RHCOS 10 worker to an RHCOS 9 worker on a CNV 5.0 dual-stream cluster.
  - *Test Scenario:* [Tier 2] Verify a guest workload started before RHCOS 10 → RHCOS 9 migration remains reachable throughout the migration window without interruption or guest restart.
  - *Test location:* `tests/infrastructure/instance_types/supported_os/test_rhel_os.py` — `TestVMMigrationAndState` (`test_pause_unpause_after_migrate`, `test_verify_virtctl_guest_agent_data_after_migrate`).
  - *CI lane:* `test-pytest-cnv-5.0-infrastructure-dualstream`
  - *Priority:* P0

- **[CNV-85277]** — As a cluster admin, I want to create and start a RHEL VM on a CNV 5.0 dual-stream cluster.
  - *Test Scenario:* [Tier 2] Verify RHEL VM creation and start succeed on a CNV 5.0 dual-stream cluster; VM reaches Running phase.
  - *Test location:* `tests/infrastructure/instance_types/supported_os/test_rhel_os.py` — `TestVMCreationAndValidation` (`test_create_vm`, `test_start_vm`).
  - *CI lane:* `test-pytest-cnv-5.0-infrastructure-dualstream`
  - *Priority:* P1

- **[CNV-85277]** — As a cluster admin, I want to delete a RHEL VM on a CNV 5.0 dual-stream cluster after successful operation.
  - *Test Scenario:* [Tier 2] Verify RHEL VM deletion succeeds on a CNV 5.0 dual-stream cluster.
  - *Test location:* `tests/infrastructure/instance_types/supported_os/test_rhel_os.py` — `TestVMDeletion` (`test_vm_deletion`).
  - *CI lane:* `test-pytest-cnv-5.0-infrastructure-dualstream`
  - *Priority:* P1

- **[CNV-92281]** — As QE, I need dedicated CI lanes for CNV 5.0 infrastructure testing on dual-stream and RHCOS 9-only topologies.
  - *Test Scenario:* [Tier 2] Provision and validate `test-pytest-cnv-5.0-infrastructure-rhcos9` and `test-pytest-cnv-5.0-infrastructure-dualstream` lanes.
  - *Priority:* P0

---

### **IV. Sign-off and Approval**

This Software Test Plan requires approval from the following stakeholders:

* **Reviewers:**
  - QE Member (sig-infra): Geetika Kapoor (@geetikakay), Roni Kishner (@RoniKishner)
* **Approvers:**
  - QE Architect: Ruth Netser (@rnetser)
