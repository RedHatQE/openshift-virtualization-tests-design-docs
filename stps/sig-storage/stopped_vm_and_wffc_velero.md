# Openshift-virtualization-tests Test plan

## **Velero Backup/Restore: Stopped VM and WFFC Support - Quality Engineering Plan**

### **Metadata & Tracking**

- **Enhancement(s):** N/A (Technical Debt / Test Automation)
- **Feature Tracking:** [CNV-44308](https://redhat.atlassian.net/browse/CNV-44308)
- **Epic Tracking:** [CNV-12960](https://redhat.atlassian.net/browse/CNV-12960) — CNV Storage Technical Debt Backlog
- **Feature Maturity:**
  - DP: N/A
  - TP: N/A
  - GA: 5.0
- **Test coverage target:** Originally backlogged for 4.21; retargeted to 5.0 in [CNV-44308](https://redhat.atlassian.net/browse/CNV-44308).
- **QE Owner(s):** Adam Cinko (@acinko-rh)
- **Owning SIG:** sig-storage
- **Participating SIGs:** None

**Document Conventions (if applicable):** None

### **Feature Overview**

This plan targets CNV v5.0.0 and closes test coverage gaps for existing GA Velero/OADP backup and restore behavior. Administrators can protect stopped VMs with block or filesystem disks and VMs using WaitForFirstConsumer (WFFC) storage. This plan covers stopped-VM backup and restore, running- and stopped-VM backup and restore with WFFC storage, preservation of VM configuration and guest data, and recovery when a backup dependency or snapshot is unavailable. These customer-visible outcomes help administrators confirm that their workloads can be recovered after a failure.

---

### **I. Motivation and Requirements Review (QE Review Guidelines)**

This section documents the mandatory QE review process. The goal is to understand the feature's value,
technology, and testability before formal test planning.

#### **1. Requirement & User Story Review Checklist**

- [x] **Review Requirements**
  - _Traceability basis:_ [CNV-44308](https://redhat.atlassian.net/browse/CNV-44308) is a QE automation task under the [CNV-12960 technical-debt epic](https://redhat.atlassian.net/browse/CNV-12960). Neither ticket links product-level D/S requirements for this existing behavior. This plan therefore uses CNV-44308 as its Jira tracking ID, with the local coverage requirements R1–R6 below to distinguish the outcomes verified by each scenario; these labels are not product Jira IDs.
  - _Coverage requirements (CNV-44308):_
    - **R1 — Stopped-VM backup:** Administrators can back up a powered-off VM, including its configuration and stored data, with block or filesystem storage.
    - **R2 — Stopped-VM recovery:** A restored stopped VM retains its configuration and data, remains powered off, and starts only when requested.
    - **R3 — WFFC backup:** Administrators can back up running and stopped VMs using WFFC storage in block and filesystem modes.
    - **R4 — WFFC recovery:** A restored VM retains its WFFC storage class and saved startup policy, starts successfully with bound storage, and retains its data. When zone-aware storage is enabled, its storage placement matches the scheduled worker's zone.
    - **R5 — Backup failure reporting:** An unavailable backup dependency causes a clear backup failure without leftover backup artifacts.
    - **R6 — Restore failure reporting:** A missing or invalid snapshot causes a clear restore failure without a partially restored VM or storage.

- [x] **Understand Value and Customer Use Cases**
  - _Feature value to customers:_ Customers using OADP/Velero for disaster recovery and migration need confidence that all VM states are protected. Stopped VMs represent valid production workloads (e.g., template VMs, scheduled-off VMs, maintenance windows), and WFFC is the recommended StorageClass binding mode for multi-zone clusters. Without test coverage, regressions in these scenarios could cause data loss during DR operations.
  - _Customer use cases identified:_
    - As a cluster admin, I want to back up and restore template VMs that remain in a stopped state, so that my VM templates survive a disaster recovery event
    - As a cluster admin, I need to recover VMs that were powered off during a scheduled maintenance window, so that maintenance activity doesn't put those workloads at risk
    - As a cluster admin, I want to back up and restore VMs using WFFC StorageClasses within the same cluster and namespace, so that WaitForFirstConsumer workloads are protected by the same disaster-recovery flow as other VMs
    - As a cluster admin, I expect a restored VM in a multi-zone cluster to come up with its storage co-located in the zone where it is scheduled, so that zone-local data access is preserved after restore

- [x] **Testability**
  - _Requirements unclear or untestable:_ None. All requirements are testable through the existing OADP/Velero test framework. The existing `data_protection/oadp/` infrastructure supports parameterized VM configurations and DataVolume modes.

- [x] **Acceptance Criteria**
  - _Acceptance criteria:_
    - Velero successfully backs up a stopped VM with DataMover
    - Stopped VM is restored in the powered-off state (not auto-started), and can then be explicitly started successfully
    - Data written while the VM is running, before it is stopped and backed up, is present after restore and VM start
    - Restored stopped VM preserves, unchanged from before backup, its resource configuration (CPU/memory, network interfaces) and its DataVolume storage attributes (size, StorageClass, volume mode); Velero-injected changes -- new resource identifiers (UID/resourceVersion), restore-tool labels/annotations, and object status -- are expected and are excluded from the comparison
    - Velero successfully backs up a VM with a WFFC StorageClass DataVolume
    - A restored running-source WFFC VM configured for automatic startup starts automatically without an explicit start request; a restored stopped-source WFFC VM remains powered off until explicitly started
    - Restored WFFC storage retains its storage class and binds successfully, without requiring binding before a VM start request; placement matches the scheduled worker's zone when that storage topology is enabled. Both block and filesystem volumes are covered.
    - An unavailable OADP/DataMover dependency causes a failed or partially failed backup with an identifying error and no leftover backup artifacts, for block and filesystem volumes
    - A missing or invalid snapshot causes a failed or partially failed restore with an identifying error and no partially restored VM or storage, for block and filesystem volumes
  - _Gaps or missing criteria:_ The Jira description is minimal ("Add stopped VM and WFFC to velero tests plan and automate the tests"). Section II.3 defines the OCS and HPP storage classes and the snapshot-capable OCS WFFC test class. Compatible OADP/Velero/DataMover versions and dated Storage Ecosystem confirmation of the topology configuration remain required before execution.

- [x] **Non-Functional Requirements (NFRs)**
  - _Applicable NFRs and their targets:_
    - Backup and restore of a single VM complete without indefinite hangs or timeouts; concrete duration thresholds are a test-implementation detail deferred to the STD (performance benchmarking itself is out of scope -- see the Performance note below)
    - Tests must be idempotent and not leave orphaned resources in the cluster
  - _NFRs not covered and why:_
    - Performance: Not covered — benchmarking of backup/restore duration is out of scope for this test debt task (see Section II.1, Out of Scope)
    - Scalability: This feature introduces no new scale requirements; it relies on the existing OADP/Velero backup mechanism, which already has its own concurrency and throughput limits for bulk/multi-VM backups. Validating those existing platform-level concurrency/throughput constraints would exercise the OADP/Velero platform's own scaling behavior rather than functionality introduced by this test debt task, so it is not exercised here
    - Security: Positive scenarios use an authorized account. Existing OADP authorization coverage has not been established for allowed and denied backup, snapshot, restore, or cross-namespace operations. Inclusion of these checks requires a QE Architect/PM scope decision; this is pending, not an approved exclusion (see Section II.2, Security Testing).
    - Monitoring/Observability: No new metrics or alerts introduced by this test debt task (see Section II.2, Monitoring)
    - UI: No new UI changes are included. PM/UX must confirm whether exercising an existing customer UI adds value; that review is pending.
    - Documentation: No new user-facing documentation required; this is QE test coverage for existing product behavior

#### **2. Known Limitations**

- **Velero backup of stopped VMs with WFFC StorageClass requires the DataMover feature**
  - *Sign-off:* [PM name/date]

#### **3. Technology and Design Review**

- [x] **Developer Handoff/QE Kickoff**
  - _Key takeaways and concerns:_ This is a QE-driven test automation task. No developer handoff is required as the product functionality (Velero backup/restore of stopped VMs and WFFC volumes) already exists. The focus is on closing test coverage gaps.

- [x] **Technology Challenges**
  - _Identified challenges:_
    - OADP operator compatibility with the target versions remains unverified. CNV-44308 records an OADP testing block on main on 2025-08-27; this is historical evidence, not confirmation of a current block.
    - WFFC DataMover testing requires storage that supports both deferred binding and snapshots. The common HPP classes provide deferred binding but lack snapshot support; use the OCS WFFC test class specified in Section II.3 for these backup/restore scenarios.
  - _Impact on testing approach:_ Confirm snapshot support and binding mode for the selected class before executing the scenarios. Availability of an HPP WFFC class alone does not satisfy the DataMover prerequisites.

- [x] **API Extensions**
  - _New or modified APIs:_ None. This task uses existing Velero/OADP APIs and KubeVirt VM APIs.
  - _Testing impact:_ No API changes; existing test automation is reused.

- [x] **Test Environment Needs**
  - _See environment requirements in Section II.3 and testing tools in Section II.3.1_

- [x] **Topology Considerations**
  - _Topology requirements:_ A multi-node cluster is required. The P2 topology scenario additionally requires workers in at least two zones and zone-aware storage; P0/P1 coverage does not require multiple zones.
  - _Impact on test design:_ The P2 topology scenario requires the zone-aware OCS configuration in Section II.3. A WFFC class alone does not demonstrate zone-local storage; confirm the storage topology before executing that scenario.

### **II. Software Test Plan (STP)**

This STP serves as the **overall roadmap for testing**, detailing the scope, approach, resources, and schedule.

#### **1. Scope of Testing**

This test plan covers the addition of two new VM configuration categories to the existing Velero/OADP backup and restore test suite:

1. **Stopped VM backup/restore** -- Covering powered-off VMs with block and filesystem volumes; restored VMs remain powered off until an administrator starts them, and retain their configuration and data.
2. **WFFC StorageClass backup/restore** -- Covering running and stopped VMs with block and filesystem volumes using the OCS WFFC test class; restored volumes bind successfully, and the P2 scenario checks placement against the scheduled worker's zone.

Both categories are tested using the DataMover backup path (Velero with CSI DataMover) which is the primary backup mechanism for OpenShift Virtualization.

_Storage coverage:_ Run stopped-VM block and filesystem scenarios on `ocs-storagecluster-ceph-rbd-virtualization`. Run the running- and stopped-VM WFFC scenarios on `ocs-storagecluster-ceph-rbd-virtualization-wffc`, the test class defined in Section II.3, in both supported volume modes. The common HPP classes are documented in the environment matrix with their snapshot limitation.

_Startup policy:_ Configure running WFFC sources for automatic startup. Stop stopped-source VMs before backup and retain their powered-off startup setting. Preserve the saved startup policy during restore, without a restore-time override: running WFFC sources must start automatically, while stopped sources must remain off until explicitly started. A manual start must not mask a failure of the running-source automatic-start check.

**Testing Goals**

- [P0] A cluster administrator can back up and restore a stopped VM with a block DataVolume using DataMover; its configuration and data are preserved, it remains powered off, and it starts when requested.
- [P0] A cluster administrator can back up and restore a stopped VM with a filesystem DataVolume using DataMover; its configuration and data are preserved, it remains powered off, and it starts when requested.
- [P0] When OADP/DataMover is unavailable, Velero reports a failed or partially failed backup with an error identifying the unavailable dependency, and leaves no backup artifacts; this outcome applies to block and filesystem DataVolumes.
- [P0] When a block or filesystem snapshot is missing or invalid, Velero reports a failed or partially failed restore with an error identifying the snapshot problem and leaves no partially created VM, DataVolume, or PVC.
- [P1] A cluster administrator can back up and restore a running VM configured for automatic startup with a WFFC DataVolume; the restored VM starts automatically, its volume binds, and its data is readable, in both block and filesystem modes.
- [P1] A cluster administrator can restore a stopped VM with a WFFC DataVolume in both block and filesystem modes; it remains powered off until explicitly started. Request startup without first waiting for a Pending volume to bind, then confirm bound storage, a running VM, and readable data.
- [P1] Data written before backup is readable after restore in all four configuration groups: stopped VM with block storage, stopped VM with filesystem storage, running VM with WFFC storage, and stopped VM with WFFC storage. Exercise both block and filesystem modes for each WFFC group.
- [P2] After restoring and starting a stopped VM with a WFFC DataVolume on zone-aware OCS storage, its PV and scheduled worker report the same zone.

_Priority note:_ Stopped VM backup/restore is prioritized P0 because it is a previously completely untested VM state for Velero, representing a higher risk of undetected regressions. WFFC StorageClass coverage is prioritized P1 because it extends an existing, well-established backup/restore path (running VMs) with an additional storage-binding dimension, representing incremental rather than foundational risk.

_Implementation note:_ The two failure-path P0 goals above define the observable pass/fail (Backup/Restore phase, surfaced failure condition, and a post-run check for leftover artifacts). The concrete failure-injection mechanism -- how OADP/DataMover unavailability or a missing/corrupted snapshot is simulated non-destructively in a shared CI suite -- is a test-implementation detail to be designed in the STD before automation.

_WFFC binding note:_ The source volume is already bound at backup time, so backup does not exercise deferred binding. During restore, DataMover can consume and bind storage before the VM starts, depending on the restore configuration; Pending immediately after restore is therefore not a universal requirement. For a stopped source, confirm the restored VM is powered off as soon as it is available, then explicitly request startup without waiting for a Pending volume to bind or for the entire restore to complete. Finally, wait for restore completion, bound storage, a running VM, and readable data. Record the restore binding configuration with results; the P2 check must still demonstrate placement consistent with the scheduled worker's zone.

**Out of Scope (Testing Scope Exclusions)**

The following items are explicitly Out of Scope for this test cycle and represent intentional exclusions.
No verification activities will be performed for these items during this test cycle.

- **Windows guest OS backup/restore scenarios**
  - *Rationale:* Existing Windows VM restore coverage already exists in `tests/data_protection/oadp/test_velero.py`; this test debt task targets RHEL guest coverage only and does not extend Windows coverage further
  - *PM/Lead Agreement:* [Name/Date]

- **CSI-only backup (without DataMover)**
  - *Rationale:* This task targets the DataMover backup path only, which is the primary backup mechanism for OpenShift Virtualization
  - *PM/Lead Agreement:* [Name/Date]

- **Velero schedule-based automated backups**
  - *Rationale:* Only on-demand backup/restore is tested; scheduled backups do not exercise different stopped-VM or WFFC code paths
  - *PM/Lead Agreement:* [Name/Date]

- **Multi-namespace backup/restore with stopped VMs or WFFC StorageClass DataVolumes**
  - *Rationale:* The existing multi-namespace backup/restore test (`test_restore_multiple_namespaces`) only exercises a running VM with no WFFC StorageClass; it does not cover stopped VMs or WFFC. This combination is genuinely untested, not covered elsewhere, and is deferred from this test debt task's scope to keep the initial pass focused on single-namespace stopped-VM and WFFC coverage.
  - *PM/Lead Agreement:* [Name/Date]

- **Backup/restore of VMs with hotplugged volumes**
  - *Rationale:* Separate feature scope, unrelated to stopped VM or WFFC coverage
  - *PM/Lead Agreement:* [Name/Date]

- **Performance benchmarking of backup/restore duration for new scenarios**
  - *Rationale:* Performance testing is not in scope for this test debt task (see Section I.1, NFRs)
  - *PM/Lead Agreement:* [Name/Date]

**Test Limitations**

- **OADP operator availability on the test cluster is required; installation or compatibility issues block execution. CNV-44308 records such a block on 2025-08-27; target-cluster readiness is still unverified.**
  - *Sign-off:* [PM name/date]

- **Zone-aware storage provisioning is cluster-dependent; WFFC topology binding behavior may not be fully exercised on single-zone clusters**
  - *Sign-off:* [PM name/date]

#### **2. Test Strategy**

**Functional**

- [x] **Functional Testing** -- Validates that the feature works according to specified requirements and user stories
  - _Details:_ The scenarios follow three distinct workflow shapes:
    - _Positive backup/restore (the five functional scenarios):_ create a VM, write test data while it is running, stop it if the scenario uses a stopped source, perform a Velero backup, delete the original resources, and submit the restore. For stopped sources, confirm the restored VM is powered off as soon as it is available and explicitly request startup without waiting for pending storage to bind or for restore completion. For the running WFFC source, require automatic startup without a manual start. Finally, confirm restore completion, bound storage, a running VM, and data integrity.
    - _Failure-path (the two P0 negative scenarios):_ drive the backup or restore into the injected failure condition and assert it fails observably (a non-successful phase plus a surfaced failure condition) leaving no leftover artifacts; there is no delete-restore-verify step.
    - _Topology (the P2 scenario):_ restore and start the stopped WFFC VM and assert its storage binds in a zone consistent with the node where the VM is scheduled.

- [x] **Automation Testing** -- Confirms test automation plan is in place for CI and regression coverage (all tests are expected to be automated)
  - _Details:_ All tests are automated in Python/pytest within the `tests/data_protection/oadp/` directory of the openshift-virtualization-tests repository. Tests use the existing parameterized framework and Polarion markers for traceability, and run in the existing nightly CI lane.

- [x] **Regression Testing** -- Verifies that new changes do not break existing functionality
  - _Details:_ Existing Velero backup/restore tests must continue to pass. The new `stopped_vm` fixture and parameterization must not alter the behavior of existing test cases that use `stopped_vm=False`.

- [ ] **Self-Validation Testing** -- Should any of the new tests be included in the self-validation test package?
  - _Details:_ N/A. These scenarios extend edge-case backup/restore state coverage (stopped VMs, WFFC binding) rather than core operational health checks; not proposed for the self-validation package at this time.

**Non-Functional**

- [ ] **Performance Testing** -- Validates feature performance meets requirements (latency, throughput, resource usage)
  - _Details:_ N/A. Performance testing is not in scope for this test debt task.

- [ ] **Scale Testing** -- Validates feature behavior under increased load and at production-like scale
  - _Details:_ N/A. Scale testing is not in scope for this test debt task.

- [ ] **Security Testing** -- Verifies security requirements, RBAC, authentication, authorization, and vulnerability scanning
  - _Details:_ Pending QE Architect/PM scope decision for service-account permission checks covering allowed and denied backup, snapshot, restore, and cross-namespace operations. Existing positive tests use authorized access; they do not demonstrate denied-access coverage. No existing OADP RBAC test is cited as coverage, and this item is not approved as N/A.

- [ ] **Usability Testing** -- Validates user experience and accessibility requirements
  - _Details:_ PM/UX confirmation of whether testing the existing customer UI adds value is pending (see Section I.1). Absence of UI or CLI changes does not establish that usability testing is unnecessary.

- [ ] **Monitoring** -- Does the feature require metrics and/or alerts?
  - _Details:_ N/A. No new metrics or alerts for backup/restore.

**Integration & Compatibility**

- [x] **Compatibility Testing** -- Ensures feature works across supported platforms, versions, and configurations
  - _Details:_ Tests validate block and filesystem volume modes on OCS using the standard and WFFC test classes in Section II.3. HPP is part of the common storage inventory but lacks the snapshots required by this DataMover path. Backward compatibility is maintained by preserving existing test parameterization unchanged.

- [ ] **Upgrade Testing** -- Validates upgrade paths from previous versions, data migration, and configuration preservation
  - _Details:_ N/A. The OCP upgrade path was evaluated; this task adds test coverage for existing backup/restore behavior without changing product upgrade behavior.

- [x] **Dependencies** -- Blocked by deliverables from other components/products
  - _Details:_ Depends on OADP being installable and functional on OCP 4.23 / CNV v5.0.0. CNV-44308 records a testing block on main on 2025-08-27. Current target-version compatibility has not been demonstrated; complete and document the unchecked smoke-check entry criterion before execution.

- [x] **Cross Integrations** -- Does the feature affect other features or require testing by other teams?
  - _Details:_ Validate DataMover and WFFC compatibility for the OCS configuration in Section II.3 with the OADP/Velero team and Storage Ecosystem. Broader provider coverage requires another snapshot-capable WFFC class and is outside this plan.

**Infrastructure**

- [ ] **Cloud Testing** -- Does the feature require multi-cloud platform testing?
  - _Details:_ A dedicated multi-cloud matrix is not required for this test-debt task. Use RHOS PSI or AWS as specified in Section II.3 and record the platform for each result; execute P2 only where the worker and storage zone prerequisites are met.

#### **3. Test Environment**

- **Cluster Topology:** Multi-node (minimum 2 worker nodes). The P2 topology scenario additionally requires workers across at least 2 zones and matching zone-aware storage.
- **OCP & OpenShift Virtualization Version(s):** OCP 4.23 / CNV v5.0.0
- **CPU Virtualization:** Standard (Intel VT-x / AMD-V)
- **Compute Resources:** Default (2 worker nodes with sufficient memory for RHEL VMs)
- **Special Hardware:** None
- **Storage:** Use the following common OCS/ODF and HPP classes, plus the explicitly created OCS WFFC test class. All selected snapshot classes must use the same driver as their storage class.

  | Storage provider | StorageClass | Binding mode | Volume modes | Provisioner | VolumeSnapshotClass | Use in this plan |
  |:-----------------|:-------------|:-------------|:-------------|:------------|:--------------------|:-----------------|
  | OCS/ODF Ceph RBD | `ocs-storagecluster-ceph-rbd-virtualization` | Immediate | Block, Filesystem | `openshift-storage.rbd.csi.ceph.com` | `ocs-storagecluster-rbdplugin-snapclass` | Stopped-VM backup/restore and failure-path scenarios |
  | OCS/ODF Ceph RBD, test class | `ocs-storagecluster-ceph-rbd-virtualization-wffc` | WaitForFirstConsumer | Block, Filesystem | `openshift-storage.rbd.csi.ceph.com` | `ocs-storagecluster-rbdplugin-snapclass` | Running- and stopped-VM WFFC backup/restore; P2 topology validation requires zone-aware storage |
  | HPP | `hostpath-csi-basic`, `hostpath-csi-pvc-block` | WaitForFirstConsumer | Filesystem | `kubevirt.io.hostpath-provisioner` | None — snapshots unsupported | Common cluster storage; cannot run this snapshot-based DataMover path |

  _Storage sources:_ The [test-suite storage matrix](https://github.com/RedHatQE/openshift-virtualization-tests/blob/main/tests/global_config.py) and [HPP capabilities](https://github.com/RedHatQE/openshift-virtualization-tests/blob/main/utilities/constants/storage.py) define the common classes and supported modes. The `pvc-block` HPP name describes its backing storage pool; the VM-facing volume mode is Filesystem. The OCS snapshot-class mapping is documented in the [Red Hat storage guide](https://docs.redhat.com/en/documentation/openshift_container_platform/4.16/html/virtualization/storage).

- **Network:** Standard cluster networking (OVN-Kubernetes)
- **Required Operators:** OpenShift Virtualization Operator, OADP Operator (with Velero and DataMover components), OpenShift Data Foundation Operator for OCS storage
- **Platform:** RHOS PSI (OpenStack) or AWS, with ODF installed and both listed OCS classes available. Record the platform, cluster, and region used for each result. For P2, validate multiple worker zones and matching storage topology on the chosen platform; the platform name alone does not establish that prerequisite.
- **Special Configurations:** Create `ocs-storagecluster-ceph-rbd-virtualization-wffc` from the standard OCS virtualization class, preserving its provisioner and storage parameters and selecting WaitForFirstConsumer binding. This is a test-created class, not an ODF default. Keep the standard class unchanged. Configure OADP to use `ocs-storagecluster-rbdplugin-snapclass` for the OCS driver and verify snapshot creation and restore. For the P2 scenario, provide at least two worker nodes in different zones and zone-aware storage placement consistent with the selected worker zones. Record the installed OADP/Velero/DataMover versions and Storage Ecosystem approval before execution.

#### **3.1. Testing Tools & Frameworks**

- **Test Framework:** N/A -- existing standard pytest framework
- **CI/CD:** N/A -- existing standard CI lane
- **Other Tools:** None

#### **4. Entry Criteria**

The following conditions must be met before testing can begin:

- [ ] Requirements and design documents are **approved and merged**
- [ ] Test environment can be **set up and configured** (see Section II.3 - Test Environment)
- [ ] OADP operator installs successfully via OLM on OCP 4.23 / CNV v5.0.0, and a sample VM backup and restore completes successfully as a smoke check; record the date, cluster, and installed OADP/Velero/DataMover versions before marking complete
- [x] The common storage matrix includes snapshot support through `ocs-storagecluster-ceph-rbd-virtualization`
- [ ] `ocs-storagecluster-rbdplugin-snapclass` has been validated with the installed OADP/Velero/DataMover versions for both volume modes
- [ ] For WFFC tests: `ocs-storagecluster-ceph-rbd-virtualization-wffc` is configured and supports successful snapshot-based backup and restore
- [ ] For the P2 topology scenario: the OCS storage topology has been confirmed against at least two worker zones
- [ ] QE Architect/PM has decided the authorization-test scope described in Sections I.1 and II.2

#### **5. Risks**

**Timeline/Schedule**

- **Risk:** OADP compatibility with OCP 4.23 / CNV v5.0.0 is unverified and could block test development and validation; CNV-44308 records a historical OADP testing block on 2025-08-27.
  - **Mitigation:** Monitor OADP operator releases and validate compatibility before sprint commitment. Use a staging branch for test development while awaiting OADP fix.
  - *Estimated impact on schedule:* 1-2 sprints delay if target-version validation reveals an OADP blocker
  - *Sign-off:* [Name/Date]

**Test Coverage**

- **Risk:** WFFC StorageClass behavior may vary between storage providers, reducing coverage confidence on non-default storage backends
  - **Mitigation:** Execute the OCS class matrix in Section II.3 and record the class and volume mode with each result. Broader provider coverage requires a snapshot-capable WFFC class; the common HPP classes cannot supply that combination.
  - *Areas with reduced coverage:* WFFC DataMover backup/restore on providers other than OCS; HPP has no snapshot support
  - *Sign-off:* [Name/Date]

**Test Environment**

- **Risk:** None -- this plan uses the existing OCS snapshot backend; the WFFC test class and P2 storage topology are checked as entry criteria.
  - **Mitigation:** Configure the OCS WFFC test class and validate the snapshot and topology entry criteria before scheduling execution. HPP availability alone does not establish readiness for this DataMover path; report an unmet prerequisite as blocked coverage.

**Untestable Aspects**

- **Risk:** None -- all identified scenarios (stopped VM backup/restore, WFFC binding, topology zone verification) are reproducible with existing cluster infrastructure and require no production-only conditions.
  - **Mitigation:** All identified scenarios are testable with the OCS snapshot class, the configured WFFC class, and the worker topology listed in Section II.3.

**Resource Constraints**

- **Risk:** The earlier PR for this same test coverage (RedHatQE/openshift-virtualization-tests#162) was closed without merging when OADP testing on main was blocked. Its implementation must be checked against the current test code and updated before it can be reused.
  - **Mitigation:** Compare PR #162's changes with the current test utilities and reuse the applicable parts. The original change was small (~35 additions), so this should require less rework than starting from scratch.
  - *Current capacity gaps:* None identified
  - *Sign-off:* [Name/Date]

**Dependencies**

- **Risk:** OADP operator version compatibility with the target CNV/OCP version may introduce API changes or behavioral differences
  - **Mitigation:** Pin OADP operator version in test prerequisites. Validate operator compatibility during environment setup phase.
  - *Dependent teams or components:* OADP/Velero team (Red Hat)
  - *Sign-off:* [Name/Date]

---

### **III. Test Scenarios & Traceability**

All scenarios use CNV-44308 as the QE tracking ID for existing behavior. The local coverage requirement labels refer to Section I.1 and distinguish the outcomes covered; they do not claim separate product requirements.

- **[CNV-44308](https://redhat.atlassian.net/browse/CNV-44308)** -- As a cluster admin, I want to back up and restore a stopped VM with a block volume mode DataVolume via Velero DataMover, so that its specification, DataVolume metadata, and data survive a disaster recovery event
  - _Coverage requirements:_ R1, R2
  - _Test Scenario:_ [Tier 2] Verify backup and restore of a stopped VM with block volume mode DataVolume using Velero DataMover; confirm the restored VM's resource configuration and DataVolume storage attributes (size, StorageClass, volume mode) match the original, the VM is restored powered off (not auto-started) and can then be started, and data is intact
  - _Priority:_ P0

- **[CNV-44308](https://redhat.atlassian.net/browse/CNV-44308)** -- As a cluster admin, I want to back up and restore a stopped VM with a filesystem volume mode DataVolume via Velero DataMover, so that its specification, DataVolume metadata, and data survive a disaster recovery event
  - _Coverage requirements:_ R1, R2
  - _Test Scenario:_ [Tier 2] Verify backup and restore of a stopped VM with filesystem volume mode DataVolume using Velero DataMover; confirm the restored VM's resource configuration and DataVolume storage attributes (size, StorageClass, volume mode) match the original, the VM is restored powered off (not auto-started) and can then be started, and data is intact
  - _Priority:_ P0

- **[CNV-44308](https://redhat.atlassian.net/browse/CNV-44308)** -- As a cluster admin, I want a Velero backup of a stopped VM to fail with a clear, actionable error when OADP/DataMover is unavailable, so that I'm not left with a silent failure or orphaned backup resources
  - _Coverage requirements:_ R5
  - _Test Scenario:_ [Tier 2] Verify that a Velero backup of a stopped VM, with either block or filesystem volume mode DataVolume, ends in a non-successful phase (PartiallyFailed or Failed) with a failure condition identifying the unavailable OADP/DataMover dependency, and that the failed backup leaves no leftover backup artifacts behind
  - _Priority:_ P0

- **[CNV-44308](https://redhat.atlassian.net/browse/CNV-44308)** -- As a cluster admin, I want restoring a stopped VM from a backup with a missing or corrupted DataVolume snapshot to fail clearly, so that I don't end up with a VM that has unbootable or missing storage or incomplete restored resources
  - _Coverage requirements:_ R6
  - _Test Scenario:_ [Tier 2] Verify that restoring a stopped VM from a backup with a missing or corrupted DataVolume snapshot ends in a non-successful Restore phase (PartiallyFailed or Failed) with a failure condition referencing the missing or invalid snapshot, for both block and filesystem volume modes, and leaves no partially created VM, DataVolume, or PVC behind
  - _Priority:_ P0

- **[CNV-44308](https://redhat.atlassian.net/browse/CNV-44308)** -- As a cluster admin, I want to back up and restore a running VM with a WFFC StorageClass DataVolume via Velero DataMover, so that data integrity is preserved for workloads using WaitForFirstConsumer storage binding
  - _Coverage requirements:_ R3, R4
  - _Test Scenario:_ [Tier 2] Verify backup and restore of a running WFFC VM configured for automatic startup, in both block and filesystem modes; preserve its saved startup policy and require the restored VM to start automatically without an explicit start request. Confirm restore completion, bound storage using the original WFFC class, and readable pre-backup data; a manual start cannot satisfy this scenario.
  - _Priority:_ P1

- **[CNV-44308](https://redhat.atlassian.net/browse/CNV-44308)** -- As a cluster admin, I want to back up and restore a stopped VM with a WFFC StorageClass DataVolume via Velero DataMover, so that the restored VM starts successfully with correct storage binding
  - _Coverage requirements:_ R3, R4
  - _Test Scenario:_ [Tier 2] Verify backup and restore of a stopped WFFC VM in both block and filesystem modes; first confirm the restored VM is powered off as soon as it is available, then explicitly request startup without waiting for a Pending volume to bind or for restore completion. After startup is requested, confirm restore completion, bound storage using the original WFFC class, a running VM, and readable pre-backup data.
  - _Priority:_ P1

- **[CNV-44308](https://redhat.atlassian.net/browse/CNV-44308)** -- As a cluster admin, I want data written to a VM before backup to be readable after restore, so that I can trust Velero backups for all four stopped-VM and WFFC configuration groups
  - _Coverage requirements:_ R2, R4
  - _Test Scenario:_ [Tier 2] Verify pre-backup data is readable after restore in all four configuration groups: stopped VM with block storage, stopped VM with filesystem storage, running VM with WFFC storage, and stopped VM with WFFC storage. Exercise both block and filesystem modes in each WFFC group, with the automatic or explicit startup expected for that source VM.
  - _Priority:_ P1

- **[CNV-44308](https://redhat.atlassian.net/browse/CNV-44308)** -- As a cluster admin, I want a restored stopped VM with a WFFC DataVolume to start with its storage bound in the same zone as the node where it is scheduled, so that zone-local data access is preserved after restore
  - _Coverage requirements:_ R4
  - _Test Scenario:_ [Tier 2] Verify that a restored stopped VM with a WFFC DataVolume starts successfully and its WFFC PV binds in a zone consistent with the node where the VM is scheduled (the bound PV's zone label matches the scheduling node's zone), demonstrating zone-local storage after restore
  - _Priority:_ P2

---

### **IV. Sign-off and Approval**

This Software Test Plan requires approval from the following stakeholders:

Required approval roles are QE Lead, PM, and Dev Lead. The QE Lead and Dev Lead identities must be confirmed before approval; a listed reviewer is not evidence of approval.

- **Reviewers:**
  - QE Architect (OCP-V): Ruth Netser (`@rnetser`)
  - QE Members (OCP-V): Jenia Peimer (`@jpeimer`), Emanuele Prella (`@ema-aka-young`), Jose Manuel Castano (`@joscasta`)

* **Approvers:**
  - QE Architect (OCP-V): Ruth Netser (`@rnetser`)
  - PM: Peter Lauterbach (`@pelauter`)
