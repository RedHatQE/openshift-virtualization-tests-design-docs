# Openshift-virtualization-tests Test plan

## **CBT: Offline VM Support - Quality Engineering Plan**

### **Metadata & Tracking**

- **Enhancement(s):** [VEP 401: Offline Incremental Backup](https://github.com/kubevirt/enhancements/blob/main/veps/sig-storage/25-incremental-backup/401-offline-incremental-backup/offline-incremental-backup.md) ([merged PR #402](https://github.com/kubevirt/enhancements/pull/402)); [CNV-92883](https://redhat.atlassian.net/browse/CNV-92883) (downstream tracking); extends [VEP #25 CBT](https://github.com/kubevirt/enhancements/blob/main/veps/sig-storage/25-incremental-backup/vep.md)
- **Feature Tracking:** [VIRTSTRAT-481](https://redhat.atlassian.net/browse/VIRTSTRAT-481) (storage agnostic incremental backup)
- **Epic Tracking:** [CNV-96511](https://redhat.atlassian.net/browse/CNV-96511)
- **Feature Maturity:**
  - DP: N/A
  - TP: CNV 5.1.0
  - GA: CNV 5.2.0
- **QE Owner(s):** Emanuele Prella
- **Owning SIG:** sig-storage
- **Participating SIGs:** sig-storage
- **Related STP:** This plan extends the [CBT STP](cbt.md) with offline VM backup scenarios.

**Document Conventions (if applicable):**

- **Offline backup:** A backup of a stopped VM; the VEP reporting expectation requires a delivered API contract before validation.
- **Push mode:** Backup mode that writes backup files to a provider-supplied PVC.
- **Pull mode:** Backup mode that lets the provider retrieve disk data over HTTPS and finalize the backup by deleting its request.

### **Feature Overview**

QEMU Changed Block Tracking (CBT) incremental backup previously supported only running virtual machines. Offline CBT extends the existing backup API so backup providers can perform full and incremental backups of eligible stopped VMs. This plan targets GA in CNV v5.2.0 and marks checks also required at Tech Preview in CNV v5.1.0, when offline backup is enabled through an HCO feature gate. Offline mode is selected automatically when the source VM is stopped. This plan validates offline backup behavior, exported disk coverage, and prior backup history continuity while retaining the existing running-VM backup scope in the parent CBT plan. Recovered guest bootability and data checks validate backup integrity without claiming a CNV restore product API.

---

### **I. Motivation and Requirements Review (QE Review Guidelines)**

This section documents the mandatory QE review process. The goal is to understand the feature's value,
technology, and testability before formal test planning.

#### **1. Requirement & User Story Review Checklist**

- [x] **Review Requirements**
  - *List the key D/S requirements reviewed:*
    - VEP-401 merged upstream ([PR #402](https://github.com/kubevirt/enhancements/pull/402)) — offline incremental backup for stopped VMs
    - Alpha, opt-in incremental backup of stopped VMs through the CNV v5.1 backup API
    - HCO feature-gate enablement and preservation in effective KubeVirt configuration as environment prerequisites
    - Automated offline backup and recovery validation (CNV-96537); STD and automation delivery tracked by CNV-100769 and CNV-100770
    - STP updated to include offline VM backup scenarios (CNV-96538)
    - Same backup API as online CBT ([VEP #25](https://github.com/kubevirt/enhancements/blob/main/veps/sig-storage/25-incremental-backup/vep.md)); the VEP expects offline-mode reporting, pending target-build API confirmation

- [x] **Understand Value and Customer Use Cases**
  - *Describe the feature's value to customers:* Backup vendors can protect stopped VMs during maintenance windows without full copies; cluster admins reduce nightly backup time and storage for powered-off workloads.
  - *List the customer use cases identified:*
    - As a backup provider, I want to perform incremental backups of offline (stopped) VMs so that I can offer complete protection regardless of VM power state.
    - As a cluster admin, I want incremental backups of stopped VMs so that I reduce backup time and storage consumption.
    - As a backup provider, I want to use the same backup API for both online and offline incremental backups.

- [x] **Testability**
  - *Note any requirements that are unclear or untestable:*
    - HCO feature-gate configuration is an environment prerequisite. Repeated unchanged increments, residual-runtime and overlapping-request outcomes, and offline reporting require development agreement before execution (see Test Coverage risk).

- [x] **Acceptance Criteria**
  - *List the acceptance criteria:*
    - A backup provider can create incremental backups of stopped VMs through the CNV backup API when the offline backup feature gate is enabled.
    - The HCO feature gate enables offline backup and preserves the enabled setting across operator restart/configuration updates; leaving the feature gate disabled produces no offline output.
    - Automated e2e coverage reconstructs Linux and Windows backup points, verifies recovered bootability and matching guest-data checksums, and rejects incomplete recovery chains (CNV-96537).
    - External epic acceptance: [CNV-96511](https://redhat.atlassian.net/browse/CNV-96511) requires at least one certified backup partner to confirm offline workflows through the CBT API; this is outside this STP’s test coverage (II.1).
  - *Note any gaps or missing criteria:* HCO configuration is a prerequisite; operator restart/configuration-update preservation is explicitly out of scope (II.1). TS-01 retains the disabled-gate backup check. VEP merge, the STP update, release note, and documentation are tracked delivery criteria (CNV-92883, CNV-96538, CNV-96539, CNV-96540 and CNV-100450), not functional scenarios.

- [x] **Non-Functional Requirements (NFRs)**
  - *List applicable NFRs and their targets:*
    - Security: Pull-mode offline backup uses trusted TLS and token authorization; the service rejects invalid credentials and clients reject untrusted server certificates.
    - Functional API feedback: Pending/failure feedback is validated with API behavior; offline reporting awaits the delivered contract. No UI/UX change is specified.
    - Documentation: Downstream docs updated for offline backup API usage and feature gate (verified by docs team, not duplicated in QE functional scope)
    - Compatibility: QCOW2 tracking overlays are required and may use raw backing disks; RAW-only tracking is unsupported. Supported storage remains storage-agnostic.
    - Backward Compatibility: Prior online backup history remains compatible with offline CBT; rollback fails in-progress offline backups without blocking VM operations
    - Performance: Offline incremental backups are expected to complete in comparable or less time than online incremental backups. See the benchmarking scope in II.1.
    - Scalability: Verify concurrent CBT backups on a five-VM ODF fleet in all-stopped and mixed running/stopped configurations. Production-scale coverage and behavior at the cluster's backup parallelism limit are tracked in [CNV-89381](https://redhat.atlassian.net/browse/CNV-89381).
  - *Note any NFRs not covered and why:*
    - Monitoring: N/A — no new metrics or alerts specified
    - Observability: N/A — offline mode uses existing backup status and events; no new observability contract is defined
    - UI: No CNV console changes — per epic non-requirement; QE validates API behavior only

#### **2. Feature Limitations**

The limitations are documented to ensure alignment between development, QA, and product teams.
The following are confirmed product constraints accepted before testing begins.

- **Offline backup requires prior CBT initialization in CNV v5.1.0**
  - In CNV v5.1.0, offline backup requires a VM that has previously started with CBT enabled. A backup of a never-started VM fails during initialization. [CNV-100648](https://redhat.atlassian.net/browse/CNV-100648) tracks full-backup support. The planned GA check applies once that support is delivered in the GA build.
  - The same requirement applies to an otherwise eligible disk added or changed from read-only to read-write while the VM is stopped if the disk has never been initialized for CBT. The backup fails until the VM starts with CBT enabled and the disk writable. After the VM stops again, the next offline backup backs up that disk in full.
  - *Sign-off:* Alvaro Romero, 2026-11-24

- **No incremental checkpoint baseline for never-started VMs in CNV v5.1.0**
  - CNV v5.1.0 cannot create this checkpoint because the first backup fails. [CNV-100650](https://redhat.atlassian.net/browse/CNV-100650) depends on CNV-100648 and has no confirmed GA delivery. If delivered for GA, verify that the first full backup establishes a usable checkpoint and a subsequent incremental backup of the untouched VM reports zero changes in separate push and pull runs.
  - *Sign-off:* Alvaro Romero, 2026-11-24

- **Automatic VM stop/start orchestration is not supported**
  - VEP-401 non-goal - Offline backup does not automatically stop or start the source VM.
  - *Sign-off:* Alvaro Romero, 2026-11-24

- **Pull-mode trust boundary: deleting a completed backup request advances the checkpoint even if the provider did not retrieve all data**
  - VEP-401 known limitation — external backup chain gap not detected by the platform
  - *Sign-off:* Alvaro Romero, 2026-11-24

- **Node affinity window**
  - VEP 401 known limitation - Until backup volume mounts are released, a VM can be restricted to the export node; immediate placement on a different node is not promised.
  - *Sign-off:* Alvaro Romero, 2026-11-24

- **Restore as a product feature is not supported**
  - Inherited from the parent CBT STP — there is no restore API, workflow, or UX; restore may be used only as a method to validate backup integrity, not as a product capability under test
  - *Sign-off:* Alvaro Romero, 2026-11-24

#### **3. Technology and Design Review**

- [x] **Developer Handoff/QE Kickoff**
  - *Key takeaways and concerns:*
    - Initial meeting held on October 2nd, 2026 between QE and Dev.
    - Development/QE agreement is needed on mode-specific completion, HCO/build readiness, recovery evidence and the pending-versus-failed status contract.

- [x] **Technology Challenges**
  - *List identified challenges:*
    - Online-to-offline checkpoint continuity (online backup, VM shutdown, offline incremental)
    - VM start prevention while backup is progressing; different completion semantics for push vs pull mode
    - Bitmap validation failures and per-disk fallback to full backup
    - Hotplugged disks without prior checkpoints (full backup for new disk, incremental for others)
    - The VEP specifies immediate failure for residual runtime activity, while the inspected controller waits for source cleanup. Upstream API admission rejects additional requests for the same VM while a backup is active. Confirm both behaviors on the target build.
    - Bitmap consistency after an export pod crashes and restarts during bitmap creation
    - VM deletion during backup (backup must fail cleanly)
  - *Impact on testing approach:* Scenarios derived from VEP 401 functional testing approach; prioritize online→offline transition and start-gating as P0; validate push vs pull completion paths separately

- [x] **API Extensions**
  - *List new or modified APIs:* No new CRs — the existing backup API accepts stopped VMs; offline-operation reporting is specified by the VEP but is unconfirmed in the delivered API.
  - *Testing impact:* Extend existing backup API tests with stopped-VM fixtures; validate delivered offline reporting after Development confirms its representation; HCO feature-gate configuration is a prerequisite

- [x] **Test Environment Needs**
  - *See environment requirements in Section II.3 and testing tools in Section II.3.1*

- [x] **Topology Considerations**
  - *Describe topology requirements:* Standard single-cluster topology; QCOW2 tracking overlays required for offline CBT scenarios
  - *Impact on test design:* No multi-cluster requirements; tests run on standard CNV CI clusters with both CBT and offline backup feature gates enabled

### **II. Software Test Plan (STP)**

This STP serves as the **overall roadmap for testing**, detailing the scope, approach, resources,
and schedule.

#### **1. Scope of Testing**

**Testing Goals**

- **[P0] G01 — Availability controls:** As a cluster admin, verify that in CNV v5.1.0, stopped-VM backup requests remain pending without offline output when the HCO offline-backup feature gate is disabled.
- **[P0] [TP] G02 — Linux offline backup correctness:** As a backup provider, verify full and incremental push and pull backups expose the expected data of eligible stopped Linux VMs.
- **[P0] [TP] G03 — Linux recovery integrity:** As a backup provider, verify recovered Linux guests boot with checksums matching each backup point and that incomplete Linux backup chains fail recovery validation.
- **[P0] G04 — History continuity:** As a backup provider, verify prior online and offline history remains usable across VM restart, and preserve that history when backup preparation or transfer fails.
- **[P0] G05 — VM safety:** As a cluster admin, verify VM start is blocked during backup, resumes at the mode-specific completion boundary, and source deletion fails the backup without blocking deletion.
- **[P0] G12 — Unchanged increments:** As a backup provider, verify the expected result of repeating an incremental backup when no disk data has changed.
- **[P0] G13 — Extended backup integrity:** As a backup provider, verify recovered Windows guests boot with checksums matching each backup point and that incomplete Windows backup chains fail recovery validation. Verify that unavailable disks prevent successful recovery validation.
- **[P1] G06 — Recovery and conflicts:** As a backup provider, verify retries recover from interruption while overlapping requests and residual source activity cannot produce unsafe backup output. In CNV v5.1.0, verify that backups of never-started VMs fail safely.
- **[P1] G07 — Storage and transport security:** As a cluster admin, verify offline disk coverage, trusted TLS retrieval and rejection of invalid credentials or untrusted certificates.
- **[P1] G08 — Lifecycle compatibility:** As a cluster admin, verify that offline backup fails safely when a disk needs CBT initialization after a stopped-VM configuration change. Verify that after a start and stop, the affected disk is backed up in full and other eligible disks remain incremental. Verify that per-disk fallback preserves eligible incremental data and rollback leaves later VM operations available.
- **[P1] G10 — Upgrade continuity:** As a backup provider, verify that an online checkpoint created before a supported upgrade into the GA release remains usable for offline incremental backup in both modes.
- **[P1] G11 — First backup of never-started VMs:** As a backup provider, verify that a never-started VM can be backed up in both modes once CNV-100648 is delivered in the GA build.
- **[P2] G09 — Extended validation:** As a cluster admin, verify that concurrent backups of all-stopped and mixed running/stopped VM fleets preserve each VM's backup data, and that offline-created checkpoints remain usable across restart and migration.

**Priority Levels:**

- **P0** — Blocks GA.
- **P1** — Required for full feature coverage.
- **P2** — May be deferred if time is limited.

**Phase tag (optional):** Priorities refer to GA. If the same expectation must also pass at Tech Preview, use `[P0][TP]` for a goal or `P0 [TP]` on a scenario's Priority line. Use the phase names from Feature Maturity. Checks specific to an earlier release name that release in the goal or scenario.

**Out of Scope (Testing Scope Exclusions)**

The following items are explicitly Out of Scope for this test cycle and represent intentional
exclusions. No verification activities will be performed for these items, and any related issues
found will not be classified as defects for this release.

- **New running-VM-only functional scenarios**
  - *Rationale:* The parent CBT STP and CNV-67413 own existing online coverage. This plan adds offline cases and retains the online regression commitment in II.2; the exclusion does not waive regressions detected by that campaign.
  - *Sign-off (Quality Owner or Product Manager):* [Name/Date]

- **UI testing**
  - *Rationale:* The feature is API-only with no UI components.
  - *Sign-off (Quality Owner or Product Manager):* [Name/Date]

- **Execution of online-versus-offline incremental backup benchmarking**
  - *Rationale:* We'll work with the Performance & Scale team to define the comparison, agree on what counts as comparable before setting a pass criterion, and run and report the benchmark under a proposed CNV 5.1 Jira ticket.
  - *Sign-off (Quality Owner or Product Manager):* [Name/Date]

- **Certified backup partner validation**
  - *Rationale:* Partner integration and workflow validation are not covered by this STP; the epic’s external acceptance requirement remains separate.
  - *Sign-off (Quality Owner or Product Manager):* [Name/Date]

- **HCO feature-gate enablement and operator lifecycle validation**
  - *Rationale:* This plan tests offline backup behavior, including the disabled-gate check in TS-01. HCO enablement and persistence across operator restarts/configuration updates, including backup checks after those transitions, are not covered by this STP; the epic acceptance requirement remains separate.
  - *Sign-off (Quality Owner or Product Manager):* [Name/Date]

**Test Limitations**

- **A runnable CNV v5.1 build including the HCO offline-backup feature gate is not yet confirmed**
  - *Sign-off:* Alvaro Romero, 2026-11-24

#### **2. Test Strategy**

**Functional**

- [x] **Functional Testing** — Validates that the feature works according to specified requirements and user stories
  - *Details:* Extend existing CBT workflows with stopped-VM output validation. Offline chains include a full baseline and two increments, with guest writes between checkpoints; verify mode-specific completion, failure handling and startup gating. Successful pull validation retrieves the data before request deletion. Push cancellation occurs during writing and preserves prior history for retry.

- [x] **Automation Testing** — Confirms test automation plan is in place for CI and regression coverage (all tests are expected to be automated)
  - *Details:* Automate offline API and Linux/Windows recovery under CNV-96537 (design/automation: CNV-100769/100770). Recovery requires bootability and matching checkpoint checksums; incomplete chains must fail validation.

- [x] **Regression Testing** — Verifies that new changes do not break existing functionality
  - *Details:* Run the existing [CBT tests](https://github.com/RedHatQE/openshift-virtualization-tests/blob/main/tests/storage/cbt/test_cbt.py) for online full/incremental chains, multi-disk and Windows backups, concurrency and migration on the feature cluster. Current automation checks running-VM backup status and disk lists; extend these workflows for offline data validation. Retain client certificate-trust checks from the [parent CBT plan](https://github.com/RedHatQE/openshift-virtualization-tests-design-docs/blob/main/stps/sig-storage/cbt.md) as regression coverage; their execution is not established by this review.

- [ ] **Self-Validation Testing** — Should any of the new tests be included in the self-validation test package?
  - *Details:* No — multi-stage backup and recovery workflows are unsuitable for the fast product-health package.

**Non-Functional**

- [ ] **Performance Testing** — Validates feature performance meets requirements (latency, throughput, resource usage)
  - *Details:* See the benchmarking scope in II.1. Compare online and offline incremental backup durations separately for push and pull using equivalent source disks, storage, and changed data. Measure from request submission to successful backup completion for push, and from request submission through data retrieval and backup finalization for pull.

- [x] **Scale Testing** — Validates feature behavior under increased load and at production-like scale
  - *Details:* Run the scheduled five-VM concurrency check in TS-18. Track larger workloads and verify how requests beyond the cluster's active-backup capacity are handled under [CNV-89381](https://redhat.atlassian.net/browse/CNV-89381).

- [x] **Security Testing** — Verifies security requirements, RBAC, authentication, authorization, and vulnerability scanning
  - *Details:* Verify trusted offline pull retrieval over TLS; reject invalid credentials and untrusted server certificates before reading data. Retain existing CBT transport regression coverage.

- [ ] **Usability Testing** — Validates user experience and accessibility requirements
  - *Details:* N/A — Jira specifies no-ux and no CNV console changes. API pending/failure feedback remains Functional Testing.

- [ ] **Monitoring** — Does the feature require metrics and/or alerts?
  - *Details:* N/A — no new metrics or alerts specified for offline backup.

**Integration & Compatibility**

- [x] **Compatibility Testing** — Ensures feature works across supported platforms, versions, and configurations
  - *Details:* Validate Linux and Windows guests with QCOW2 tracking overlays on supported block/filesystem and CSI backends. Prior online backup history must remain compatible with offline increments.

- [x] **Upgrade Testing** — Validates upgrade paths from previous versions, data migration, and configuration preservation
  - *Details:* Validate online checkpoint continuity for offline incremental backups after a supported upgrade into the GA release.
- [x] **Dependencies** — Blocked by deliverables from other components/products
  - *Details:* VEP 401 and KubeVirt implementation PR #19294 are merged; CNV-96536 is Closed in fresh Jira. Execution still requires a compatible downstream build exposing the HCO offline-backup feature gate and offline backup API.

- [x] **Cross Integrations** — Does the feature affect other features or require testing by other teams?
  - *Details:* Extends existing CBT backup flows; must not break online backup (parent STP). VM start gating during offline backup uses the same pattern as migration gating. Hotplug disk scenarios intersect with storage hotplug coverage.

**Infrastructure**

- [ ] **Cloud Testing** — Does the feature require multi-cloud platform testing?
  - *Details:* N/A — standard OCP platforms; CBT is storage-agnostic with no cloud-specific offline backup requirements.

#### **3. Test Environment**

- **Cluster Topology:** Standard (3-master/3-worker or equivalent CI topology)

- **OCP & OpenShift Virtualization Version(s):** CNV v5.1.0 for release-specific checks, on a compatible OCP release. For GA upgrade testing, use the confirmed source and target CNV builds and the supported OCP versions for the upgrade path.

- **CPU Virtualization:** Standard

- **Compute Resources:** Standard for baseline Linux; the dedicated concurrent-backup cycle needs capacity for three Windows guests and two Linux guests plus backup workers. Final sizing follows the selected images and build

- **Special Hardware:** N/A - no special hardware needed

- **Storage:** Standard. CBT is storage-agnostic. Any StorageClass for VMs and PVCs, sufficient capacity for backup PVCs.

- **Network:** Standard (OVN-Kubernetes)

- **Required Operators:** OpenShift Virtualization (CNV)

- **Platform:** Standard (bare metal or virtualized — no platform-specific offline backup behavior)

- **Special Configurations:** Enable CBT for positive cases. For builds that require opt-in, HCO must apply and preserve the offline backup feature gate (`OfflineIncrementalBackup`). TS-01 covers disabled offline backup. Use the prior-start eligibility in Feature Limitations for fixtures that require initialized CBT. TS-26 uses a VM that has never started. QCOW2 tracking overlays may use raw backing disks

#### **3.1. Testing Tools & Frameworks**

- **Test Framework:** N/A — no non-standard framework required

- **CI/CD:** Existing CI lanes and scheduled validation cycles, selected by the scenario matrix

- **Other Tools:** N/A - no specific testing tools required

#### **4. Entry Criteria**

The following conditions must be met before testing can begin:

- [x] Requirements and design documents are **approved and merged** (VEP 401 merged via [PR #402](https://github.com/kubevirt/enhancements/pull/402))
- [x] Developer Handoff/QE Kickoff record confirmed, including date and design-phase takeaways
- [ ] Test environment can be **set up and configured** (see Section II.3 - Test Environment)

#### **5. Risks**

**Timeline/Schedule**

- **Risk:** Late confirmation of a runnable downstream/HCO build could compress the P1/P2 execution window.
  - **Mitigation:** Confirm build readiness with Storage Ecosystem and execute P0 coverage first after Entry Criteria are met.
  - *Estimated impact on schedule:* A late runnable build reduces the time for subsequent coverage before release readiness.
  - *Sign-off:* Alvaro Romero, 2026-11-24

**Test Coverage**

- **Risk:** The implementation evolved through reviews and differs from the original VEP ([PR #19294](https://github.com/kubevirt/kubevirt/pull/19294)):
  - **Unchanged increments:** VEP rejects repeats; implementation permits empty increments and advances history in both modes.
  - **Overlapping requests:** Upstream API admission rejects additional requests for the same VM while a backup is active. The offline controller serializes overlapping requests that reach it.
  - **Residual runtime activity:** VEP fails immediately; implementation waits for source cleanup.
  - **Status reporting:** VEP proposes backup `status.offline`; implementation adds VM `status.backupInProgress` for synchronization instead.
  - **Mitigation:** Confirm target-build outcomes with Development before execution; prevent unsafe output and use only delivered status fields.
  - *Areas with reduced coverage:* Repeat-incremental/conflict/runtime outcomes and offline reporting remain unresolved until the target-build decision is recorded; node-affinity characterization is limited to Feature Limitations.
  - *Sign-off:* Alvaro Romero, 2026-11-24

- **Risk:** Shareable-disk coverage depends on whether the target CNV build includes [KubeVirt PR #19708](https://github.com/kubevirt/kubevirt/pull/19708). With the change, full and incremental offline backups omit shareable disks in both modes. A backup can succeed while shared data, such as data on a Windows Server Failover Clustering (WSFC) disk, remains unprotected.
  - **Mitigation:** Confirm with Development whether the target CNV build includes the change before assessing backup coverage for shareable disks.
  - *Areas with reduced coverage:* Offline backup of shareable disks on the target build remains unverified.
  - *Sign-off:* [Name/Date]

**Test Environment**

None — no separate environment risk.

*Mitigation:* Build/HCO availability is a Test Limitation and Entry Criterion; its schedule consequence is under Timeline/Schedule.

**Untestable Aspects**

None — no in-scope requirement is omitted as untestable.

*Mitigation:* Not applicable.

**Resource Constraints**

- **Risk:** QE capacity shared with parent CBT GA work and multiple CNV-96511 child stories.
  - **Mitigation:** Prioritize P0 automation, then P1 coverage; defer P2 only if the timeline compresses.
  - *Current capacity gaps:* Parallel P1/P2 implementation and execution alongside parent CBT GA work.
  - *Sign-off:* Alvaro Romero, 2026-11-24

**Dependencies**

None — no separate dependency risk identified.

*Mitigation:* Product build dependencies are tracked in II.2 and Entry Criteria.

---

### **III. Test Scenarios & Traceability**

Offline-specific scenarios extend the parent CBT test plan. Each scenario with push and pull variants requires two independent executions, each with its own backup requests and mode-specific assertions. Coverage requires both executions to pass.

- **[CNV-96511]** — As a cluster admin, I want stopped-VM backup requests in CNV v5.1.0 to remain pending without offline output when the HCO offline-backup feature gate is disabled.
  - *Test Scenario:* [Tier 1] **TS-01:** Verify disabled offline backup remains pending without output.
  - *Priority:* P0

- **[CNV-96511]** — As a backup provider, I want Linux offline backups in both modes to capture complete disk data in the first full backup and only changed data in subsequent increments.
  - *Test Scenario:* [Tier 1] **TS-02:** Verify full and incremental Linux offline backup data.
  - **Push execution** — Verify the full and incremental images written to the target PVC.
  - **Pull execution** — Retrieve and verify the full and incremental disk data over trusted HTTPS before deleting each backup request.
  - *Priority:* P0 [TP]

- **[CNV-96537]** — As a backup provider, I want successive offline backup points in push and pull modes to recover bootable Linux guests with checksums matching guest changes between checkpoints across VM restarts, while incomplete chains fail validation
  - *Test Scenario:* [Tier 2] **TS-04:** Validate bootable Linux recovery with changed data between checkpoints.
  - *Priority:* P0 [TP]

- **[CNV-96537]** — As a backup provider, I want Windows Server 2022 offline recovery in both modes to produce bootable guests with matching data checksums and preserved persistent vTPM/EFI configuration. Verify recovery from a full baseline without prior backup history and from increments based on online and offline checkpoints. Verify that incomplete chains fail recovery validation.
  - *Test Scenario:* [Tier 3] **TS-05:** Validate Windows offline recovery and startup gating.
  - **Push execution** — Run the recovery checks using push backups and verify the Windows VM follows the push startup rules in TS-08.
  - **Pull execution** — Run the recovery checks using pull backups and verify the Windows VM follows the pull startup rules in TS-08.
  - *Priority:* P0

- **[CNV-96511]** — As a backup provider, I want Linux online history to support Linux offline increments and subsequent VM startup in push and pull modes
  - *Test Scenario:* [Tier 2] **TS-07:** Verify online checkpoints support offline increments across backup modes.
  - *Priority:* P0

- **[CNV-96511]** — As a cluster admin, I want Linux VM startup blocked while an offline backup is active and allowed when it completes according to its mode.
  - *Test Scenario:* [Tier 2] **TS-08:** Verify VM startup waits for offline backup completion.
  - **Push execution** — Attempt startup while the backup is writing and verify it stays blocked. Verify startup is allowed after writing succeeds and the backup completes.
  - **Pull execution** — Attempt startup while the backup is active and verify it stays blocked, including after successful retrieval. Verify startup is allowed after deleting the backup request.
  - *Priority:* P0

- **[CNV-96511]** — As a backup provider, I want interrupted preparation in either mode to resume the original request without corruption, and failed or cancelled pushes to preserve history, release startup and permit retry
  - *Test Scenario:* [Tier 2] **TS-10:** Validate offline preparation recovery and failed-push retry safety.
  - *Priority:* P1

- **[CNV-96511]** — As a cluster admin, I want source deletion to abort offline backups without blocking VM deletion in push and pull modes
  - *Test Scenario:* [Tier 2] **TS-11:** Verify source deletion aborts offline backups without blocking removal.
  - *Priority:* P1

- **[CNV-96511]** — As a cluster admin, I want overlapping offline backup requests rejected while the existing backup remains active
  - *Test Scenario:* [Tier 1] **TS-12:** Verify the API rejects additional requests during an active offline backup.
  - In separate push and pull runs, submit a second and third request with distinct names for the same stopped VM while the original backup is active. Verify that the API rejects both and that the original backup completes successfully. Verify that the API accepts a fresh full-backup request after successful push completion or after successful pull retrieval and deletion of the original request.
  - *Priority:* P1

- **[CNV-96511]** — As a backup provider, I want to know whether a repeat incremental backup succeeds when no disk data has changed. If the disk configuration is unchanged, I also want to take a full backup in push or pull mode without starting the VM again.
  - *Test Scenario:* [Tier 1] **TS-13:** Validate offline backup requests between VM starts.
  - For repeat incremental backups, verify the expected result confirmed with Development under Test Coverage (Section II.5).
  - *Priority:* P1

- **[CNV-96511]** — As a backup provider, I want push and pull offline backups to retain healthy increments for eligible disks, fully back up eligible new disks or eligible disks with unusable history, and report unavailable eligible disks without indicating complete coverage.
  - *Test Scenario:* [Tier 2] **TS-14:** Validate offline fallback and unavailable-disk reporting for eligible disks.
  - *Priority:* P1

- **[CNV-96511]** — As a cluster admin, I want VM shutdown to finish before an offline backup produces data.
  - *Test Scenario:* [Tier 1] **TS-15:** Verify offline backup produces no data during shutdown cleanup.
  - Submit the request after the VM stops while its launcher pod is still shutting down. Verify the behavior confirmed with Development under Test Coverage (Section II.5).
  - *Priority:* P1

- **[CNV-96511]** — As a cluster admin, I want rollback to fail active offline backups without blocking later VM operations or backup requests in push and pull modes
  - *Test Scenario:* [Tier 2] **TS-16:** Verify rollback aborts offline backups and releases VM operations.
  - *Priority:* P1

- **[CNV-96511]** — As a backup provider, I want invalid credentials rejected before offline pull data is disclosed
  - *Test Scenario:* [Tier 1] **TS-17:** Verify unauthorized clients cannot retrieve offline pull disk data.
  - *Priority:* P1

- **[CNV-96511]** — As a cluster admin, I want concurrent backups of running and stopped VMs to preserve each VM's data.
  - *Test Scenario:* [Tier 3] **TS-18:** Verify concurrent backups preserve per-VM data.
  - Use five VMs on ODF, three Windows and two Linux. Run an all-stopped variant and a mixed variant with three stopped and two running VMs. Execute each variant separately in push and pull modes. Submit all five backup requests concurrently and verify that each completes with the expected data for its source VM.
  - *Priority:* P2

- **[CNV-96511]** — As a backup provider, I want expiry to fail an offline pull without advancing history or leaving VM startup blocked
  - *Test Scenario:* [Tier 2] **TS-19:** Verify expired offline pulls preserve history and release startup.
  - *Priority:* P2

- **[CNV-96511]** — As a backup provider, I want an offline-created checkpoint in push and pull modes to survive VM startup and migration so a later stopped-VM increment remains valid
  - *Test Scenario:* [Tier 2] **TS-20:** Verify offline checkpoints survive restart, migration and shutdown.
  - *Priority:* P2

- **[CNV-96511]** — As a backup provider, I want early pull-request deletion to advance history without implying external-chain completeness
  - *Test Scenario:* [Tier 1] **TS-21:** Confirm early offline pull deletion advances history despite incomplete retrieval.
  - *Priority:* P1

- **[CNV-96537]** — As a backup provider, I want full and incremental offline Linux backup points on a supported non-default CSI backend (e.g. Trident) to recover bootable guests with matching checksums in push and pull modes, while incomplete chains fail validation
  - *Test Scenario:* [Tier 3] **TS-22:** Validate offline recovery integrity on supported non-default storage.
  - *Priority:* P2

- **[CNV-96511]** — As a backup provider, I want clients to reject untrusted offline pull certificates before reading disk data
  - *Test Scenario:* [Tier 1] **TS-23:** Verify untrusted certificates block offline pull data retrieval.
  - *Priority:* P1

- **[CNV-100648]** — As a backup provider, I want push and pull backups of never-started VMs in CNV v5.1.0 to return an error without backup output, source-data changes or blocked VM startup
  - *Test Scenario:* [Tier 1] **TS-24:** Verify never-started VM backups fail safely with clear errors.
  - *Priority:* P1

- **[CNV-96511]** — As a backup provider, I want an online CBT checkpoint created before a supported upgrade into the GA release to remain usable for an offline incremental backup afterward.
  - *Test Scenario:* [Tier 2] **TS-25:** Verify offline increments use a pre-upgrade online checkpoint.
  - Each execution uses its own pre-upgrade checkpoint. The backup remains incremental and contains only the changes since that checkpoint.
  - **Push execution** — Verify the incremental image on the target PVC.
  - **Pull execution** — Verify the incremental data available over trusted HTTPS.
  - *Priority:* P1

- **[CNV-100648]** — As a backup provider, I want a full backup of a VM that has never started to contain the expected disk data.
  - *Test Scenario:* [Tier 1] **TS-26:** Verify full offline backups of never-started VMs.
  - Applies to GA builds that include CNV-100648. Both modes produce a successful full backup with the expected disk data without starting the VM.
  - **Push execution** — Verify the full image on the target PVC.
  - **Pull execution** — Verify the full disk data available over trusted HTTPS.
  - *Priority:* P1

- **[CNV-96511]** — As a backup provider, I want offline push and pull increments to preserve the prior checkpoint if a newly eligible disk still requires CBT initialization. After a CBT-enabled start and stop, the retry backs up that disk in full and other eligible disks incrementally.
  - *Test Scenario:* [Tier 2] **TS-27:** Verify offline backup fails after adding a writable disk to a stopped VM and succeeds after a CBT-enabled start and stop.
  - *Test Scenario:* [Tier 2] **TS-28:** Verify offline backup fails after switching an untracked disk from read-only to read-write on a stopped VM and succeeds after a CBT-enabled start and stop.
  - *Priority:* P1

---

### **IV. Sign-off and Approval**

This Software Test Plan requires sign-off from at least one person per function:

- Feature Owner: [Alvaro Romero](@alromeros)
- Quality Owner: [Dalia Frank](@dalia-frank), [Ruth Netser](@rnetser)
- Product Manager: [Peter Lauterbach](@peterclauterbach)
