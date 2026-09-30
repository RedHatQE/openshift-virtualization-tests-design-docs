# Openshift-virtualization-tests Test plan

## **CBT: Offline VM Support - Quality Engineering Plan**

### **Metadata & Tracking**

- **Enhancement(s):** [VEP 401: Offline Incremental Backup](https://github.com/kubevirt/enhancements/blob/main/veps/sig-storage/25-incremental-backup/401-offline-incremental-backup/offline-incremental-backup.md) ([merged PR #402](https://github.com/kubevirt/enhancements/pull/402)); [CNV-92883](https://redhat.atlassian.net/browse/CNV-92883) (downstream tracking); extends [VEP #25 CBT](https://github.com/kubevirt/enhancements/blob/main/veps/sig-storage/incremental-backup.md)
- **Feature Tracking:** [CNV-96511](https://redhat.atlassian.net/browse/CNV-96511)
- **Epic Tracking:** [VIRTSTRAT-481](https://redhat.atlassian.net/browse/VIRTSTRAT-481) (storage agnostic incremental backup)
- **Feature Maturity:**
  - DP: CNV 5.1.0
  - TP: N/A
  - GA: N/A
- **QE Owner(s):** Emanuele Prella (eprella@redhat.com)
- **Owning SIG:** sig-storage
- **Participating SIGs:** sig-storage
- **Related STP:** This plan extends the [CBT STP](./cbt.md) with offline VM backup scenarios.

**Document Conventions (if applicable):**

- **Offline backup:** A backup of a stopped VM that reports offline mode to the backup provider.
- **Push mode:** Backup mode where the hypervisor writes backup data to a user-provided PVC.
- **Pull mode:** Backup mode where the hypervisor exposes an NBD export and the client pulls backup data. Scratch space on a PVC is used during the backup.

### **Feature Overview**

Changed Block Tracking (CBT) incremental backup previously supported only running virtual machines. This enhancement extends the existing backup API so backup providers can perform consistent full and incremental backups of stopped (offline) VMs, enabling complete protection regardless of VM power state. Offline mode is selected automatically when the source VM is stopped. This plan validates offline backup behavior, exported disk coverage, and checkpoint continuity while retaining the existing running-VM backup scope in the parent CBT plan. Restore is not a CNV product capability.

---

### **I. Motivation and Requirements Review (QE Review Guidelines)**

This section documents the mandatory QE review process. The goal is to understand the feature's value,
technology, and testability before formal test planning.

#### **1. Requirement & User Story Review Checklist**

- [x] **Review Requirements**
  - *List the key D/S requirements reviewed:*
    - VEP-401 merged upstream ([PR #402](https://github.com/kubevirt/enhancements/pull/402)) — offline incremental backup for stopped VMs
    - Incremental backup of stopped/offline VMs via the CNV backup API (CNV v5.1, feature gate)
    - Automated e2e tests for offline VM backup and restore validation (CNV-96537)
    - STP updated to include offline VM backup scenarios (CNV-96538)
    - Same backup API as online CBT ([VEP #25](https://github.com/kubevirt/enhancements/blob/main/veps/sig-storage/incremental-backup.md)); backup status exposes offline mode

- [x] **Understand Value and Customer Use Cases**
  - *Describe the feature's value to customers:* Backup vendors can protect stopped VMs during maintenance windows without full copies; cluster admins reduce nightly backup time and storage for powered-off workloads.
  - *List the customer use cases identified:*
    - As a backup provider, I want to perform incremental backups of offline (stopped) VMs so that I can offer complete protection regardless of VM power state.
    - As a cluster admin, I want incremental backups of stopped VMs so that I reduce backup time and storage consumption.
    - As a backup provider, I want to use the same backup API for both online and offline incremental backups.

- [x] **Testability**
  - *Note any requirements that are unclear or untestable:*
    - Partner validation ("at least one certified backup partner confirms workflows") is a manual/partner activity, not automatable QE scope — documented as Out of Scope.

- [x] **Acceptance Criteria**
  - *List the acceptance criteria:*
    - A backup provider can create incremental backups of stopped VMs through the CNV backup API when the offline backup feature gate is enabled.
    - Automated e2e coverage validates offline VM backup and backup-integrity workflows (CNV-96537).
    - At least one Red Hat certified backup partner confirms its offline backup workflow; this manual partner confirmation is constrained by the available QE environment.
  - *Note any gaps or missing criteria:* VEP merge, the STP update, release note, and downstream documentation are tracked delivery criteria (CNV-92883, CNV-96538, CNV-96539, and CNV-96540), not functional scenarios.

- [x] **Non-Functional Requirements (NFRs)**
  - *List applicable NFRs and their targets:*
    - Security: Pull-mode offline backup transport uses the same certificate-based security model as online CBT pull mode
    - Documentation: Downstream docs updated for offline backup API usage and feature gate (verified by docs team, not duplicated in QE functional scope)
    - Compatibility: QCOW2 disk format required for offline CBT (RAW unsupported per VEP non-goals); storage-agnostic for supported formats
    - Backward Compatibility: Online CBT checkpoints compatible with offline CBT; upgrade enables feature gate; rollback fails in-progress offline backups without blocking VM operations
  - *Note any NFRs not covered and why:*
    - Performance: N/A — no performance targets defined for offline backup in the epic or VEP
    - Monitoring: N/A — no new metrics or alerts specified
    - Scalability: N/A for new scale dimensions — offline backup uses the same CBT mechanism; existing cluster-level backup parallelism limits apply
    - Usability: N/A — no CNV UI changes; backup provider UX is vendor-owned (explicit non-requirement)
    - UI: No CNV console changes — per epic non-requirement; QE validates API behavior only

#### **2. Known Limitations**

The limitations are documented to ensure alignment between development, QA, and product teams.
The following are confirmed product constraints accepted before testing begins.

- **Only one offline incremental backup between VM starts**
  - VEP-401 known limitation — A second incremental while still stopped is rejected; a full backup can proceed.
  - *Sign-off:* [Placeholder] / [Date placeholder]

- **RAW disk format is not supported for offline CBT**
  - VEP-401 non-goal — Offline change tracking requires QCOW2 disk overlays.
  - *Sign-off:* [Placeholder] / [Date placeholder]

- **Automatic VM stop/start orchestration is not supported**
  - VEP-401 non-goal - Offline backup does not automatically stop or start the source VM.
  - *Sign-off:* [Placeholder] / [Date placeholder]

- **Pull-mode trust boundary: deleting a completed backup request advances the checkpoint even if the provider did not retrieve all data**
  - VEP-401 known limitation — external backup chain gap not detected by the platform
  - *Sign-off:* [Placeholder] / [Date placeholder]

- **Node affinity window**
  - VEP 401 known limitation - Until backup volume mounts are released, a VM can be restricted to the export node; immediate placement on a different node is not promised.
  - *Sign-off:* [Placeholder] / [Date placeholder] 

- **Restore as a product feature is not supported**
  - Inherited from parent CBT STP — Restore used only for backup integrity validation
  - *Sign-off:* [Placeholder] / [Date placeholder]

#### **3. Technology and Design Review**

- [ ] **Developer Handoff/QE Kickoff**
  - *Key takeaways and concerns:* 
    - Not yet held. Design context is available from merged VEP 401 ([PR #402](https://github.com/kubevirt/enhancements/pull/402)); a dedicated QE kickoff with storage/CBT dev is pending before P0 test execution. Kickoff must confirm CNV v5.1 offline backup feature gate name, build availability, and test environment prerequisites.

- [x] **Technology Challenges**
  - *List identified challenges:*
    - Online-to-offline checkpoint continuity (online backup, VM shutdown, offline incremental)
    - VM start prevention while backup is progressing; different completion semantics for push vs pull mode
    - Bitmap validation failures and per-disk fallback to full backup
    - Hotplugged disks without prior checkpoints (full backup for new disk, incremental for others)
    - Stale VM runtime pods blocking backup requests
    - Export pod crash during bitmap creation and recovery on restart
    - VM deletion during backup (backup must fail cleanly)
  - *Impact on testing approach:* Scenarios derived from VEP 401 functional testing approach; prioritize online→offline transition and start-gating as P0; validate push vs pull completion paths separately

- [x] **API Extensions**
  - *List new or modified APIs:* No new CRs — he existing backup API accepts stopped VMs and reports offline operation.
  - *Testing impact:* Extend existing backup API tests with stopped-VM fixtures; verify offline status on backup resources; feature gate enablement is a prerequisite

- [x] **Test Environment Needs**
  - *See environment requirements in Section II.3 and testing tools in Section II.3.1*

- [x] **Topology Considerations**
  - *Describe topology requirements:* Standard single-cluster topology; QCOW2 VM disks required for offline CBT scenarios
  - *Impact on test design:* No multi-cluster requirements; tests run on standard CNV CI clusters with both CBT and offline backup feature gates enabled

### **II. Software Test Plan (STP)**

This STP serves as the **overall roadmap for testing**, detailing the scope, approach, resources,
and schedule.

#### **1. Scope of Testing**

**Testing Goals**

- **[P0] G01 — Offline availability:** As a cluster admin, verify that offline backup is available in push and pull modes when the offline backup feature gate is enabled, and that offline requests are rejected when the gate is disabled.
- **[P0] G02 — Full push backup:** As a backup provider, complete a full backup of a stopped Linux VM in push mode and verify the expected full-mode disk artifacts and offline status.
- **[P0] G03 — Full pull backup:** As a backup provider, complete a full backup of a stopped Linux VM in pull mode only after all disk data has been retrieved and the request has been finalized, verifying the expected full-mode exports, offline status, and completion boundary.
- **[P0] G04 — Incremental push backup:** As a backup provider, complete an incremental push backup of a continuously stopped Linux VM and verify that each disk contains only blocks changed since the selected prior checkpoint.
- **[P0] G05 — Incremental pull backup:** As a backup provider, complete an incremental pull backup of a continuously stopped Linux VM only after full retrieval and finalization, verifying changed-only exports for each disk and documenting the incomplete-pull acknowledgement boundary.
- **[P0] G06 — Linux recovery integrity:** As a backup provider, validate that Linux data recovered from offline push and pull backups matches the source data through the existing recovery workflow; backup completion alone is insufficient evidence of integrity.
- **[P0] G07 — Windows recovery integrity:** As a backup provider, validate that Windows data recovered from offline push and pull backups matches the source data through the existing recovery workflow; backup completion alone is insufficient evidence of integrity.
- **[P0] G08 — Online-to-offline continuity:** As a backup provider, use an online CBT checkpoint, stop the VM, and complete offline incremental push and pull backups that capture only changes after the checkpoint while preserving the usable backup chain.
- **[P0] G09 — Start gating:** As a cluster admin, verify that a VM cannot start during an active offline push or pull backup and can start only after the appropriate completion, deletion, or cleanup action.
- **[P0] G10 — Multi-step chain:** As a backup provider, complete full → incremental → incremental chains on a stopped Linux VM in both push and pull modes and verify the dirty extents at every step.
- **[P0] G11 — Checkpoint continuity across restart:** As a backup provider, verify that offline checkpoints remain usable across VM restart and support a subsequent incremental backup without missing backed-up data.
- **[P1] G12 — Interruption and recovery safety:** As a backup provider, interrupt an active offline push or pull transfer or preparation and verify explicit failure, no advancement of recoverable history, preservation of valid tracking, and a successful later backup.
- **[P1] G13 — Deletion handling:** As a cluster admin, delete the source VM during an active push or pull backup and verify that the backup fails while VM deletion completes.
- **[P1] G14 — Same-source conflicts:** As a cluster admin, reject overlapping push and pull requests for the same stopped VM while an offline backup is active.
- **[P1] G15 — Offline forced-full behavior:** As a backup provider, reject unchanged repeat offline incremental push and pull requests while allowing an explicitly forced full offline backup to proceed for the stopped VM.
- **[P1] G16 — Offline full fallback:** As a backup provider, for a stopped VM, use a full push or pull backup for a disk with missing or inconsistent tracking history while retaining incremental treatment for eligible disks.
- **[P1] G17 — Offline hotplugged disks:** As a cluster admin, after a disk is added to a VM and the VM is stopped, back up the new disk fully while backing up existing disks incrementally in both push and pull modes.
- **[P1] G18 — Active-source rejection:** As a cluster admin, reject push and pull requests when residual runtime activity prevents the source VM from being fully stopped.
- **[P1] G19 — Per-disk degradation:** As a backup provider, distinguish a disk that becomes unavailable during backup from healthy output in push and pull mode without reporting complete-guest success when a required disk is unavailable.
- **[P1] G20 — Rollback safety:** As a cluster admin, fail an active offline push or pull backup safely during supported rollback and verify that the VM is not permanently blocked and later operations remain possible.
- **[P1] G21 — Offline pull authorization:** As a cluster admin, allow authorized offline pull reads and reject invalid or unauthenticated export credentials.
- **[P1] G22 — Offline storage compatibility:** As a cluster admin, complete offline push and pull backups for QCOW2 disks on the supported block and filesystem storage classes required by the offline path.
- **[P1] G23 — Manual partner validation:** As a backup provider, obtain manual confirmation from one certified partner that an offline backup through the CBT API succeeds at the selected backup point before epic acceptance. This is external evidence, not an automated QE scenario; restore evidence remains dependent on provider-owned tooling.
- **[P2] G24 — Concurrent offline backups:** As a cluster admin, complete concurrent push and pull offline backups on five stopped VMs without errors or corruption, subject to existing CBT cluster-level parallelism limits.
- **[P2] G25 — Unsupported disk format:** As a cluster admin, reject offline push and pull backup for VMs using RAW disks while retaining support for the required QCOW2 format.
- **[P2] G26 — Pull expiry:** As a backup provider, allow a pull request to expire and verify explicit failure without advancing the prior checkpoint or losing prior history.
- **[P2] G27 — Migration continuity:** As a cluster admin, start with an existing online CBT checkpoint, complete live migration while the VM is running, stop the VM, and verify that the retained checkpoint supports an offline incremental backup.
- **[P2] G28 — Upgrade continuity:** As a cluster admin, preserve recoverability across a supported upgrade and complete offline incremental push and pull backups from online CBT checkpoints that already exist.

**Out of Scope (Testing Scope Exclusions)**

The following items are explicitly Out of Scope for this test cycle and represent intentional
exclusions. No verification activities will be performed for these items, and any related issues
found will not be classified as defects for this release.

- **Running VM backup scenarios**
  - *Rationale:* Explicitly listed as a non-requirement on CNV-96511; covered by the existing CBT STP and CNV-67413
  - *PM/Lead Agreement:* [Placeholder] / [Date placeholder]

- **Backup provider UI and vendor integration workflows**
  - *Rationale:* UX is owned by backup providers; QE validates the CNV backup API only
  - *PM/Lead Agreement:* [Placeholder] / [Date placeholder]

- **Certified backup partner validation**
  - *Rationale:* Acceptance criterion requires partner confirmation — manual/partner activity outside automated QE scope
  - *PM/Lead Agreement:* [Placeholder] / [Date placeholder]

- **Performance and throughput benchmarking of offline backup**
  - *Rationale:* No performance requirements defined; consistent with parent CBT STP deferral
  - *PM/Lead Agreement:* [Placeholder] / [Date placeholder]

- **External backup chain completeness after incomplete pull**
  - *Rationale:* VEP 401 documents pull-mode trust boundary — vendor responsibility; on-disk state remains intact but external chain gaps are not platform-detectable
  - *PM/Lead Agreement:* [Placeholder] / [Date placeholder]

**Test Limitations**

- **CNV v5.1 downstream implementation not yet in test builds (CNV-96536)**
  - *Sign-off:* [Placeholder] / [Date placeholder] — upstream VEP merged; functional CNV testing blocked until downstream feature gate and API land in v5.1 builds

- **Certified partner environments unavailable in QE lab**
  - *Sign-off:* [Placeholder] / [Date placeholder] — partner-specific integration validated externally, not in CNV CI

#### **2. Test Strategy**

**Functional**

- [x] **Functional Testing** — Validates that the feature works according to specified requirements and user stories
  - *Details:* Scenarios cover online→offline transition, start gating, push/pull completion semantics, checkpoint chains, known limitations, and negative paths including VM deletion, residual runtime state, and concurrent requests.

- [x] **Automation Testing** — Confirms test automation plan is in place for CI and regression coverage (all tests are expected to be automated)
  - *Details:* New e2e tests tracked under CNV-96537; automated in CNV test suite following existing CBT test patterns and VEP 401 test matrix.

- [x] **Regression Testing** — Verifies that new changes do not break existing functionality
  - *Details:* Run the existing sig-storage CBT push-mode, pull-mode, checkpoint, and VM-start-gating regression scenarios on the feature cluster; offline changes must not regress the online backup behavior covered by the parent CBT STP.

- [ ] **Self-Validation Testing** — Should any of the new tests be included in the self-validation test package?
  - *Details:* Pending QE kickoff. Assess whether the stopped-VM push-mode full and incremental backup scenarios should be added to the self-validation package once CNV-96537 automation is available.

**Non-Functional**

- [ ] **Performance Testing** — Validates feature performance meets requirements (latency, throughput, resource usage)
  - *Details:* N/A — no performance targets defined for offline backup in this release.

- [x] **Scale Testing** — Validates feature behavior under increased load and at production-like scale
  - *Details:* Validate five concurrent offline backups as a bounded regression-scale scenario. This does not establish a new platform scale limit; existing CBT cluster-level parallelism limits still apply.

- [x] **Security Testing** — Verifies security requirements, RBAC, authentication, authorization, and vulnerability scanning
  - *Details:* Pull-mode offline backup inherits certificate-based transport security from existing CBT pull mode; Section III includes unauthenticated connection rejection for offline pull mode.

- [ ] **Usability Testing** — Validates user experience and accessibility requirements
  - *Details:* N/A — no CNV UI changes; backup provider UX is vendor-owned (epic non-requirement).

- [ ] **Monitoring** — Does the feature require metrics and/or alerts?
  - *Details:* N/A — no new metrics or alerts specified for offline backup.

**Integration & Compatibility**

- [x] **Compatibility Testing** — Ensures feature works across supported platforms, versions, and configurations
  - *Details:* QCOW2 VM disks required; validate RWO block and filesystem storage classes. Online CBT checkpoints must remain compatible with offline incremental backups.

- [x] **Upgrade Testing** — Validates upgrade paths from previous versions, data migration, and configuration preservation
  - *Details:* Section III validates offline incremental backup after upgrade with existing online CBT checkpoints; verify in-progress offline backup fails cleanly on rollback without blocking VM operations (per VEP 401 upgrade/rollback section).

- [x] **Dependencies** — Blocked by deliverables from other components/products
  - *Details:* Upstream VEP 401 is merged; functional testing is blocked on CNV-96536 delivering the CNV-side feature gate and API in v5.1.

- [x] **Cross Integrations** — Does the feature affect other features or require testing by other teams?
  - *Details:* Extends existing CBT backup flows; must not break online backup (parent STP). VM start gating during offline backup uses the same pattern as migration gating. Hotplug disk scenarios intersect with storage hotplug coverage.

**Infrastructure**

- [ ] **Cloud Testing** — Does the feature require multi-cloud platform testing?
  - *Details:* N/A — standard OCP platforms; CBT is storage-agnostic with no cloud-specific offline backup requirements.

#### **3. Test Environment**

- **Cluster Topology:** Standard (3-master/3-worker or equivalent CI topology)

- **OCP & OpenShift Virtualization Version(s):** OCP aligned with CNV v5.1.0 (CNV v5.1.0)

- **CPU Virtualization:** Standard

- **Compute Resources:** Standard

- **Special Hardware:** N/A

- **Storage:** QCOW2 VM disks on standard StorageClasses (RWO primary; RWX where pull-mode scratch requires it)

- **Network:** Standard (OVN-Kubernetes)

- **Required Operators:** OpenShift Virtualization (CNV)

- **Platform:** Standard (bare metal or virtualized — no platform-specific offline backup behavior)

- **Special Configurations:** CBT feature gate enabled; offline incremental backup feature gate enabled; VM disks must use QCOW2 format for offline CBT scenarios

#### **3.1. Testing Tools & Frameworks**

- **Test Framework:** Standard

- **CI/CD:** Standard CNV test lanes

- **Other Tools:** N/A

#### **4. Entry Criteria**

The following conditions must be met before testing can begin:

- [x] Requirements and design documents are **approved and merged** (VEP 401 merged via [PR #402](https://github.com/kubevirt/enhancements/pull/402))
- [x] Test environment can be **set up and configured** (see Section II.3 - Test Environment)
- [ ] Offline VM backup feature gate available in CNV v5.1 test builds
- [ ] CNV-side offline backup API implementation available (CNV-96536)
- [ ] Developer Handoff/QE Kickoff meeting completed

#### **5. Risks**

**Timeline/Schedule**

- **Risk:** CNV v5.1 downstream implementation (CNV-96536) may delay test-ready builds despite upstream VEP merge.
  - **Mitigation:** Upstream VEP merged — focus on CNV integration timeline; prioritize P0 scenarios; align test development with CNV-96537.
  - *Estimated impact on schedule:* 2–4 weeks if CNV-side feature gate slips past v5.1 code freeze
  - *Sign-off:* [Placeholder] / [Date placeholder]

**Test Coverage**

- **Risk:** Pull-mode trust boundary and external backup chain gaps cannot be fully validated in automated QE.
  - **Mitigation:** Document as Out of Scope; validate on-disk checkpoint behavior and CR deletion semantics only.
  - *Areas with reduced coverage:* Vendor external backup chain completeness; node affinity scheduling window characterization
  - *Sign-off:* [Placeholder] / [Date placeholder]

**Test Environment**

- **Mitigation:** No separate environment risk is identified beyond the unavailable CNV v5.1 build recorded in Test Limitations. When the build is available, use the Section II.3 configuration with both feature gates enabled.

**Untestable Aspects**

- **Risk:** Certified backup partner workflow validation cannot be reproduced in QE automation.
  - **Mitigation:** Document as Out of Scope; partner validation tracked as separate acceptance criterion with manual sign-off.
  - *Reason untestable and mitigation approach:* Partner environments and vendor-specific workflows are external to CNV CI
  - *Sign-off:* [Placeholder] / [Date placeholder]

**Resource Constraints**

- **Risk:** QE capacity shared with parent CBT GA work and multiple CNV-96511 child stories.
  - **Mitigation:** Focus on P0 goals first (VEP functional testing approach); automate via CNV-96537; defer P2 scenarios if timeline compresses.
  - *Missing resources or infrastructure:* QE capacity for parallel P1/P2 implementation and execution while parent CBT GA work is active
  - *Sign-off:* [Placeholder] / [Date placeholder]

**Dependencies**

- **Mitigation:** No separate dependency risk is identified.

---

### **III. Test Scenarios & Traceability**

Scenarios aligned with VEP 401 functional testing approach and CNV-96511 acceptance criteria.

| Requirement ID | Requirement Summary | Test Scenario(s) | Tier | Priority |
|:---------------|:--------------------|:-----------------|:-----|:---------|
| CNV-96511 | As a backup provider, I want to perform incremental backups of offline (stopped) VMs so that I can offer complete protection regardless of VM power state | Perform a full backup of a stopped VM in push mode; confirm backup completion and offline-mode status | 1 | P0 |
| | | Run a full push backup, modify disk data while the VM is stopped, then run an incremental push backup; confirm only changed blocks are saved | 1 | P0 |
| | | Request an incremental push backup on a stopped VM with no prior checkpoint; confirm a full backup is performed | 1 | P0 |
| | | Request an incremental pull backup on a stopped VM with no prior checkpoint; confirm a full backup is available for export | 1 | P0 |
| | | With the offline backup feature gate enabled, confirm a push backup succeeds; with the gate disabled, confirm a push backup is rejected | 1 | P0 |
| | | With the offline backup feature gate enabled, confirm a pull backup becomes ready for export; with the gate disabled, confirm a pull backup is rejected | 1 | P0 |
| | | Perform a push-mode offline backup; confirm it completes only after backup export finishes successfully | 1 | P1 |
| | | Delete a push-mode backup request while it is in progress; confirm the backup fails and the checkpoint is not advanced | 1 | P1 |
| | | Delete the source VM during a push offline backup; confirm the backup fails and VM deletion proceeds | 1 | P1 |
| | | Delete the source VM during a pull offline backup; confirm the backup fails and VM deletion proceeds | 1 | P1 |
| | | Start two push offline backup requests for the same stopped VM concurrently; confirm the second request is rejected immediately | 1 | P1 |
| | | Start two pull offline backup requests for the same stopped VM concurrently; confirm the second request is rejected immediately | 1 | P1 |
| | | After a successful push offline incremental backup with no disk changes, request a second incremental backup; confirm the request is rejected | 1 | P1 |
| | | After a successful pull offline incremental backup with no disk changes, request a second incremental backup; confirm the request is rejected | 1 | P1 |
| | | After a push offline incremental backup, request a full (non-incremental) push backup while the VM remains stopped; confirm it succeeds | 1 | P1 |
| | | After a pull offline incremental backup, request a full (non-incremental) pull backup while the VM remains stopped; confirm it becomes ready for export | 1 | P1 |
| | | Attempt a push offline backup while residual source-VM runtime state prevents the VM from being fully stopped; confirm the request fails without creating a backup artifact | 1 | P1 |
| | | Attempt a pull offline backup while residual source-VM runtime state prevents the VM from being fully stopped; confirm the request fails without creating a backup artifact | 1 | P1 |
| | | Simulate inconsistent change tracking on one disk for a push backup; confirm that disk falls back to full backup while other disks proceed incrementally | 1 | P1 |
| | | Simulate inconsistent change tracking on one disk for a pull backup; confirm that disk falls back to full backup while other disks proceed incrementally | 1 | P1 |
| | | Run push offline VM backups on QCOW2 disks using RWO block and filesystem StorageClasses; confirm successful completion for each storage class | 1 | P1 |
| | | Run pull offline VM backups on QCOW2 disks using RWO block and filesystem StorageClasses; confirm each backup becomes ready for export | 1 | P1 |
| | | Attempt an unauthenticated connection to the offline pull-mode export endpoint; confirm the connection is rejected | 1 | P1 |
| | | Attempt a push offline backup on a VM with RAW disk format; confirm the request is rejected | 1 | P2 |
| | | Attempt a pull offline backup on a VM with RAW disk format; confirm the request is rejected | 1 | P2 |
| | | Run an online incremental backup, stop the VM, then run an offline incremental push backup; confirm only changes written after shutdown are captured and the VM starts successfully afterward | 2 | P0 |
| | | Run an online incremental backup, stop the VM, then run an offline incremental pull backup; confirm only changes written after shutdown are captured and the VM starts successfully afterward | 2 | P0 |
| | | Attempt to start the VM while a push backup is progressing; confirm start is blocked until the push backup completes, then confirm the VM starts successfully | 2 | P0 |
| | | Attempt to start the VM while a pull backup is progressing; confirm start is blocked until the backup request is deleted, then confirm the VM starts successfully | 2 | P0 |
| | | Run a full → incremental → incremental push-backup chain on a stopped VM; confirm the second incremental captures only changes since the first incremental | 2 | P0 |
| | | Run a full → incremental → incremental pull-backup chain on a stopped VM; confirm the second incremental captures only changes since the first incremental | 2 | P0 |
| | | After offline push backups, start the VM; confirm checkpoints are redefined at boot and a subsequent push incremental backup preserves the chain | 2 | P0 |
| | | After offline pull backups, start the VM; confirm checkpoints are redefined at boot and a subsequent pull incremental backup preserves the chain | 2 | P0 |
| | | After a successful stopped-VM push backup, run the restore-validation workflow; confirm recovered data matches the source data | 2 | P0 |
| | | After a successful stopped-VM pull backup, run the restore-validation workflow; confirm recovered data matches the source data | 2 | P0 |
| | | Interrupt an in-progress offline push backup; confirm it fails, the previous checkpoint remains usable, and a later backup can be requested | 2 | P0 |
| | | Perform a full backup of a stopped VM in pull mode; retrieve the backup data while the request is progressing, delete the request, and confirm completion is reported only after deletion | 2 | P1 |
| | | Perform a full backup followed by an incremental backup of a stopped VM in pull mode; confirm the incremental backup contains only blocks changed since the full backup | 2 | P1 |
| | | Hotplug a new disk while the VM is running, stop the VM, then run a push offline backup; confirm the new disk is fully backed up and existing disks are incrementally backed up | 2 | P1 |
| | | Hotplug a new disk while the VM is running, stop the VM, then run a pull offline backup; confirm the new disk is fully available for export and existing disks are incrementally available | 2 | P1 |
| | | After cluster upgrade to CNV v5.1 with offline backup gate enabled, run a push offline incremental backup on a stopped VM that has existing online CBT checkpoints; confirm the backup succeeds | 2 | P1 |
| | | After cluster upgrade to CNV v5.1 with offline backup gate enabled, run a pull offline incremental backup on a stopped VM that has existing online CBT checkpoints; confirm the backup becomes ready for export | 2 | P1 |
| | | Roll back during an in-progress push offline backup; confirm the backup fails, the VM remains manageable, and a subsequent backup can be requested | 2 | P1 |
| | | Roll back during an in-progress pull offline backup; confirm the backup fails, the VM remains manageable, and a subsequent backup can be requested | 2 | P1 |
| | | Interrupt push offline-backup preparation, allow the backup service to recover, and confirm valid change tracking is preserved while inconsistent tracking is recreated | 2 | P2 |
| | | Interrupt pull offline-backup preparation, allow the backup service to recover, and confirm valid change tracking is preserved while inconsistent tracking is recreated | 2 | P2 |
| | | Perform a full push backup, change guest data, then perform an incremental push backup on a stopped Windows VM; confirm the incremental backup contains only the changed blocks | 3 | P1 |
| | | Perform a full pull backup, change guest data, then perform an incremental pull backup on a stopped Windows VM; confirm the incremental backup contains only the changed blocks | 3 | P1 |
| | | Run concurrent push offline VM backups on 5 different stopped VMs; confirm all complete without errors or corruption | 3 | P2 |
| | | Run concurrent pull offline VM backups on 5 different stopped VMs; confirm all become ready for export without errors or corruption | 3 | P2 |
| | | In pull mode, allow backup TTL to expire; confirm backup fails and checkpoint is not advanced | 3 | P2 |

---

### **IV. Sign-off and Approval**

This Software Test Plan requires approval from the following stakeholders:

* **Reviewers:**
  - Development Representative (OCP-V): [Adi Aloni](@Acedus), [Alvaro Romero](@alromeros)
  - QE Members (OCP-V): [Dalia Frank](@dafrank), [Kateryna Shvaika](@kshvaika), [Jose Manuel Castano](@josemacassan), [Ahmad Hafe](@Ahmad-Hafe), [Jenia Peimer](@jpeimer)
* **Approvers:**
  - QE Architect (OCP-V): [Ruth Netser](@rnetser)
  - QE Member (OCP-V): [Jenia Peimer](@jpeimer)
