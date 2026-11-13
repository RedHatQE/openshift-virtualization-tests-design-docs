# Openshift-virtualization-tests Test plan

## **CBT: Offline VM Support - Quality Engineering Plan**

### **Metadata & Tracking**

- **Enhancement(s):** [VEP 401: Offline Incremental Backup](https://github.com/kubevirt/enhancements/blob/main/veps/sig-storage/25-incremental-backup/401-offline-incremental-backup/offline-incremental-backup.md) ([merged PR #402](https://github.com/kubevirt/enhancements/pull/402)); [CNV-92883](https://redhat.atlassian.net/browse/CNV-92883) (downstream tracking); extends [VEP #25 CBT](https://github.com/kubevirt/enhancements/blob/main/veps/sig-storage/25-incremental-backup/vep.md)
- **Feature Tracking:** [VIRTSTRAT-481](https://redhat.atlassian.net/browse/VIRTSTRAT-481) (storage agnostic incremental backup)
- **Epic Tracking:** [CNV-96511](https://redhat.atlassian.net/browse/CNV-96511)
- **Feature Maturity:**
  - DP: CNV 5.1.0
  - TP: N/A
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

Changed Block Tracking (CBT) incremental backup previously supported only running virtual machines. This plan covers Alpha, opt-in offline backup in CNV v5.1.0, enabled through an HCO offline-backup feature gate, extending the existing backup API so backup providers can perform consistent full and incremental backups of eligible stopped (offline) VMs. Offline mode is selected automatically when the source VM is stopped. This plan validates offline backup behavior, exported disk coverage, and prior backup history continuity while retaining the existing running-VM backup scope in the parent CBT plan. Recovered guest bootability and data checks validate backup integrity without claiming a CNV restore product API.

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
    - Partner acceptance is externally executed and manually reviewed by QE; the lab constraint is in Test Limitations and the evidence requirement remains in scope.
    - HCO feature-gate configuration is an environment prerequisite. Repeated unchanged increments, residual-runtime and overlapping-request outcomes, and offline reporting require development agreement before execution (see Test Coverage risk).

- [x] **Acceptance Criteria**
  - *List the acceptance criteria:*
    - A backup provider can create incremental backups of stopped VMs through the CNV backup API when the offline backup feature gate is enabled.
    - The HCO feature gate enables offline backup and preserves the enabled setting across operator restart/configuration updates; leaving the feature gate disabled produces no offline output.
    - Automated e2e coverage reconstructs Linux and Windows backup points, verifies recovered bootability and matching guest-data checksums, and rejects incomplete recovery chains (CNV-96537).
    - At least one Red Hat certified backup partner records successful stopped-VM full/incremental backup and recovery evidence on CNV-96511 before release readiness; failed or incomplete evidence cannot satisfy acceptance.
  - *Note any gaps or missing criteria:* HCO enablement and preservation remain environment prerequisites (II.3/II.4); TS-01 retains disabled-gate behavior. VEP merge, the STP update, release note, and documentation are tracked delivery criteria (CNV-92883, CNV-96538, CNV-96539, CNV-96540 and CNV-100450), not functional scenarios.

- [x] **Non-Functional Requirements (NFRs)**
  - *List applicable NFRs and their targets:*
    - Security: Pull-mode offline backup uses trusted TLS and token authorization; the service rejects invalid credentials and clients reject untrusted server certificates.
    - Functional API feedback: Pending/failure feedback is validated with API behavior; offline reporting awaits the delivered contract. No UI/UX change is specified.
    - Documentation: Downstream docs updated for offline backup API usage and feature gate (verified by docs team, not duplicated in QE functional scope)
    - Compatibility: QCOW2 tracking overlays are required and may use raw backing disks; RAW-only tracking is unsupported. Supported storage remains storage-agnostic.
    - Backward Compatibility: Prior online backup history remains compatible with offline CBT; upgrade enables feature gate; rollback fails in-progress offline backups without blocking VM operations
  - *Note any NFRs not covered and why:*
    - Performance: N/A — no performance targets defined for offline backup in the epic or VEP
    - Monitoring: N/A — no new metrics or alerts specified
    - Observability: N/A — offline mode uses existing backup status and events; no new observability contract is defined
    - Scalability: N/A for new scale dimensions — offline backup uses the same CBT mechanism; existing cluster-level backup parallelism limits apply
    - UI: No CNV console changes — per epic non-requirement; QE validates API behavior only

#### **2. Known Limitations**

The limitations are documented to ensure alignment between development, QA, and product teams.
The following are confirmed product constraints accepted before testing begins.

- **Never-started VMs cannot be backed up in CNV v5.1.0**
  - Offline backup requires a VM that has previously started with CBT enabled. A never-started VM has no tracking overlay and its backup request returns an error. [CNV-100648](https://redhat.atlassian.net/browse/CNV-100648) tracks adding full-backup support for that case; the issue is New and targets CNV v5.2.0.
  - *Sign-off:* [Name/Date]

- **No incremental checkpoint baseline for never-started VMs in CNV v5.1.0**
  - [CNV-100650](https://redhat.atlassian.net/browse/CNV-100650) depends on CNV-100648 and tracks recording a checkpoint during the future first full backup of a never-started VM, so subsequent incremental backups can identify zero changes. This dependent behavior is unavailable in CNV v5.1.0; the preceding limitation prevents a successful first backup for these VMs.
  - *Sign-off:* [Name/Date]

- **Only one offline incremental backup between VM starts**
  - VEP-401 specifies rejection of a second unchanged incremental; inspected upstream tests instead expect successful empty increments. This is an unresolved target-build constraint, not an established delivered limitation. Development must settle it under Entry Criteria; a full backup remains planned.
  - *Sign-off:* [Name/Date]

- **RAW-only change tracking is unsupported**
  - VEP 401 requires QCOW2 tracking overlays. Raw backing disks beneath those overlays are allowed; backing-disk format alone does not establish a blanket request-rejection contract.
  - *Sign-off:* [Name/Date]

- **Automatic VM stop/start orchestration is not supported**
  - VEP-401 non-goal - Offline backup does not automatically stop or start the source VM.
  - *Sign-off:* [Name/Date]

- **Pull-mode trust boundary: deleting a completed backup request advances the checkpoint even if the provider did not retrieve all data**
  - VEP-401 known limitation — external backup chain gap not detected by the platform
  - *Sign-off:* [Name/Date]

- **Node affinity window**
  - VEP 401 known limitation - Until backup volume mounts are released, a VM can be restricted to the export node; immediate placement on a different node is not promised.
  - *Sign-off:* [Name/Date]

- **Restore as a product feature is not supported**
  - Inherited from the parent CBT STP — there is no restore API, workflow, or UX; restore may be used only as a method to validate backup integrity, not as a product capability under test
  - *Sign-off:* [Name/Date]

#### **3. Technology and Design Review**

- [ ] **Developer Handoff/QE Kickoff**
  - *Key takeaways and concerns:*
    - Design-phase kickoff completion/date is unconfirmed; the checkbox remains open until a human supplies the record.
    - Development/QE agreement is needed on mode-specific completion, HCO/build readiness, recovery evidence and the pending-versus-failed status contract.

- [x] **Technology Challenges**
  - *List identified challenges:*
    - Online-to-offline checkpoint continuity (online backup, VM shutdown, offline incremental)
    - VM start prevention while backup is progressing; different completion semantics for push vs pull mode
    - Bitmap validation failures and per-disk fallback to full backup
    - Hotplugged disks without prior checkpoints (full backup for new disk, incremental for others)
    - The VEP specifies immediate failure for residual runtime activity and overlapping requests, while the inspected local implementation waits; confirm the target-build contract.
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

- **[P0] G01 — Availability controls:** As a cluster admin, verify disabled offline backup requests remain pending without offline output.
- **[P0] G02 — Offline backup correctness:** As a backup provider, verify full and incremental push and pull backups expose the expected data of eligible stopped VMs, and validate repeated unchanged increments against the target-build contract agreed before execution.
- **[P0] G03 — Backup integrity:** As a backup provider, verify recovered Linux and Windows guests boot with checksums matching each backup point; incomplete chains or unavailable disks must not yield successful recovery validation.
- **[P0] G04 — History continuity:** As a backup provider, verify prior online and offline history remains usable across VM restart, and preserve that history when backup preparation or transfer fails.
- **[P0] G05 — VM safety:** As a cluster admin, verify VM start is blocked during backup, resumes at the mode-specific completion boundary, and source deletion fails the backup without blocking deletion.
- **[P1] G06 — Recovery and conflicts:** As a backup provider, verify retries recover from interruption while overlapping requests and residual source activity cannot produce unsafe backup output.
- **[P1] G07 — Storage and transport security:** As a cluster admin, verify offline disk coverage on supported storage and deny unauthorized access to offline pull data; retain CBT transport checks in the regression campaign.
- **[P1] G08 — Lifecycle compatibility:** As a cluster admin, verify hotplugged disks and per-disk fallback preserve eligible incremental data, and rollback leaves later VM operations available.
- **[P1] G11 — Partner acceptance:** As a backup provider, verify certified-partner offline backup and recovery evidence, rejecting failed or incomplete protection claims.
- **[P2] G09 — Extended validation:** As a cluster admin, verify simultaneous offline backups keep per-VM data separate and offline-created checkpoints remain usable across restart and migration, within existing backup parallelism limits.
- **[P2] G10 — Upgrade continuity:** As a cluster admin, verify CNV v5.0.0 online history remains usable after upgrade to CNV v5.1.0 for offline incremental backup.

**Out of Scope (Testing Scope Exclusions)**

The following items are explicitly Out of Scope for this test cycle and represent intentional
exclusions. No verification activities will be performed for these items, and any related issues
found will not be classified as defects for this release.

- **New running-VM-only functional scenarios**
  - *Rationale:* The parent CBT STP and CNV-67413 own existing online coverage. This plan adds offline cases and retains the online regression commitment in II.2; the exclusion does not waive regressions detected by that campaign.
  - *PM/Lead Agreement:* [Name/Date]

- **UI testing**
  - *Rationale:* The feature is API-only with no UI components. PM/Lead confirmed no UI coverage is needed based on customer value assessment.
  - *PM/Lead Agreement:* [Name/Date]

- **Performance and throughput benchmarking of offline backup**
  - *Rationale:* No performance requirements defined; consistent with parent CBT STP deferral
  - *PM/Lead Agreement:* [Name/Date]

**Test Limitations**

- **A runnable CNV v5.1 build including the HCO offline-backup feature gate is not yet confirmed**
  - *Sign-off:* [Name/Date]

- **Certified partner environments unavailable in QE lab**
  - *Sign-off:* [Name/Date]

#### **2. Test Strategy**

**Functional**

- [x] **Functional Testing** — Validates that the feature works according to specified requirements and user stories
  - *Details:* Extend existing CBT workflows with stopped-VM output validation. Offline chains include a full baseline and two increments, with guest writes between VM starts; verify mode-specific completion, failure handling and startup gating. Successful pull validation retrieves the data before request deletion. Push cancellation occurs during writing and preserves prior history for retry.

- [x] **Automation Testing** — Confirms test automation plan is in place for CI and regression coverage (all tests are expected to be automated)
  - *Details:* Automate offline API and Linux/Windows recovery under CNV-96537 (design/automation: CNV-100769/100770). Recovery requires bootability and matching checkpoint checksums; incomplete chains must fail validation. Partner execution is external and manually reviewed by QE: evidence identifies the certified partner, build, guest and supported mode, demonstrates full/incremental recovery, and rejects failed or incomplete results.

- [x] **Regression Testing** — Verifies that new changes do not break existing functionality
  - *Details:* Run the existing [CBT tests](https://github.com/RedHatQE/openshift-virtualization-tests/blob/main/tests/storage/cbt/test_cbt.py) for online full/incremental chains, multi-disk and Windows backups, concurrency and migration on the feature cluster. Current automation checks running-VM backup status and disk lists; extend these workflows for offline data validation. Retain client certificate-trust checks from the [parent CBT plan](https://github.com/RedHatQE/openshift-virtualization-tests-design-docs/blob/main/stps/sig-storage/cbt.md) as regression coverage; their execution is not established by this review.

- [ ] **Self-Validation Testing** — Should any of the new tests be included in the self-validation test package?
  - *Details:* No — multi-stage backup and recovery workflows are unsuitable for the fast product-health package.

**Non-Functional**

- [ ] **Performance Testing** — Validates feature performance meets requirements (latency, throughput, resource usage)
  - *Details:* N/A — no performance targets defined for offline backup in this release.

- [x] **Scale Testing** — Validates feature behavior under increased load and at production-like scale
  - *Details:* Validate concurrent offline backups within existing CBT parallelism limits, checking that each VM retains its own backup data.

- [x] **Security Testing** — Verifies security requirements, RBAC, authentication, authorization, and vulnerability scanning
  - *Details:* Verify invalid credentials cannot retrieve offline pull data. Trusted retrieval is exercised by the offline full/incremental cases; existing CBT TLS/client-trust checks remain in the regression campaign.

- [ ] **Usability Testing** — Validates user experience and accessibility requirements
  - *Details:* N/A — Jira specifies no-ux and no CNV console changes. API pending/failure feedback remains Functional Testing; offline reporting needs the agreed API contract in Entry Criteria.

- [ ] **Monitoring** — Does the feature require metrics and/or alerts?
  - *Details:* N/A — no new metrics or alerts specified for offline backup.

**Integration & Compatibility**

- [x] **Compatibility Testing** — Ensures feature works across supported platforms, versions, and configurations
  - *Details:* Validate Linux and Windows guests with QCOW2 tracking overlays on supported block/filesystem and CSI backends. Prior online backup history must remain compatible with offline increments.

- [x] **Upgrade Testing** — Validates upgrade paths from previous versions, data migration, and configuration preservation
  - *Details:* Section III validates CNV v5.0.0 online backup history after upgrade to CNV v5.1.0; in-progress offline backup must fail cleanly on rollback without blocking VM operations (per VEP 401 upgrade/rollback section).

- [x] **Dependencies** — Blocked by deliverables from other components/products
  - *Details:* VEP 401 and KubeVirt implementation PR #19294 are merged; CNV-96536 is Closed in fresh Jira. Execution still requires a compatible downstream build exposing the HCO offline-backup feature gate and offline backup API.

- [x] **Cross Integrations** — Does the feature affect other features or require testing by other teams?
  - *Details:* Extends existing CBT backup flows; must not break online backup (parent STP). VM start gating during offline backup uses the same pattern as migration gating. Hotplug disk scenarios intersect with storage hotplug coverage.

**Infrastructure**

- [ ] **Cloud Testing** — Does the feature require multi-cloud platform testing?
  - *Details:* N/A — standard OCP platforms; CBT is storage-agnostic with no cloud-specific offline backup requirements.

#### **3. Test Environment**

- **Cluster Topology:** Standard (3-master/3-worker or equivalent CI topology)

- **OCP & OpenShift Virtualization Version(s):** CNV v5.1.0 on the OCP release listed as compatible in the CNV v5.1 build metadata; upgrade coverage starts on CNV v5.0.0 and ends on CNV v5.1.0, using one OCP release supported by both builds

- **CPU Virtualization:** Standard

- **Compute Resources:** Standard for baseline Linux; the dedicated concurrent-backup cycle needs capacity for three Windows guests and two Linux guests plus backup workers. Final sizing follows the selected images and build

- **Special Hardware:** N/A - no special hardware needed

- **Storage:** Standard. CBT is storage-agnostic. Any StorageClass for VMs and PVCs, sufficient capacity for backup PVCs.

- **Network:** Standard (OVN-Kubernetes)

- **Required Operators:** OpenShift Virtualization (CNV)

- **Platform:** Standard (bare metal or virtualized — no platform-specific offline backup behavior)

- **Special Configurations:** HCO enablement and preservation of the offline feature gate in effective KubeVirt configuration are environment prerequisites. CBT and offline incremental backup (`OfflineIncrementalBackup`) are enabled for positive cases; TS-01 covers disabled offline backup. VM fixtures meet the prior-start eligibility in Known Limitations; QCOW2 tracking overlays may use raw backing disks

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
  - *Sign-off:* [Name/Date]

**Test Coverage**

- **Risk:** The VEP and inspected implementation disagree on repeated unchanged increments, overlapping requests, residual runtime activity and offline status reporting.
  - **Mitigation:** Obtain a Development-approved target-build decision on all four differences before executing affected cases; update candidate VEP outcomes and reporting expectations to that decision. Retain the safety expectation of no unsafe backup output; no absent API field may be invented.
  - *Areas with reduced coverage:* Repeat-incremental/conflict/runtime outcomes and offline reporting remain unresolved until the target-build decision is recorded; node-affinity characterization is limited to Known Limitations.
  - *Sign-off:* [Name/Date]

**Test Environment**

None — no separate environment risk.

*Mitigation:* Build/HCO availability is a Test Limitation and Entry Criterion; its schedule consequence is under Timeline/Schedule.

**Untestable Aspects**

None — no acceptance requirement is omitted as untestable.

*Mitigation:* The unavailable partner lab is a Test Limitation. External partner execution and QE review of recovery evidence provide validation before release readiness.

**Resource Constraints**

- **Risk:** QE capacity shared with parent CBT GA work and multiple CNV-96511 child stories.
  - **Mitigation:** Prioritize P0 automation, then P1 coverage; defer P2 only if the timeline compresses.
  - *Current capacity gaps:* Parallel P1/P2 implementation and execution alongside parent CBT GA work.
  - *Sign-off:* [Name/Date]

**Dependencies**

- **Risk:** Certified-partner evidence may arrive too late for the epic acceptance decision.
  - **Mitigation:** Arrange partner execution and require successful full/incremental backup and recovery evidence on CNV-96511 before release readiness; incomplete evidence does not satisfy acceptance.
  - *Dependent teams or components:* Certified backup partner and Storage Ecosystem QE reviewing the external workflow.
  - *Sign-off:* [Name/Date]

---

### **III. Test Scenarios & Traceability**

Offline-specific scenarios extend the parent CBT test plan.

- **[CNV-96511]** — As a cluster admin, I want the disabled HCO offline-backup feature gate to keep stopped-VM backup requests pending without offline output
  - *Test Scenario:* [Tier 1] **TS-01:** Verify disabled offline backup remains pending without output.
  - *Priority:* P0

- **[CNV-96511]** — As a backup provider, I want Linux offline push backups to write complete full images without prior history and only changed data in subsequent increments
  - *Test Scenario:* [Tier 1] **TS-02:** Verify full and incremental offline push image contents.
  - *Priority:* P0

- **[CNV-96511]** — As a backup provider, I want Linux offline pull backups to expose complete full data without prior history and only changed data in subsequent increments
  - *Test Scenario:* [Tier 1] **TS-03:** Verify full and incremental offline pull data retrieval.
  - *Priority:* P0

- **[CNV-96537]** — As a backup provider, I want successive offline backup points in push and pull modes to recover bootable Linux guests with matching data across VM restarts, while incomplete chains fail validation
  - *Test Scenario:* [Tier 2] **TS-04:** Validate bootability and checksums across Linux offline backup chains.
  - *Priority:* P0

- **[CNV-96537]** — As a backup provider, I want Windows Server 2022 offline push full baselines without history and increments from offline/online checkpoints to recover bootable guests with matching data, reject incomplete chains, and block startup until writing completes, preserving persistent vTPM/EFI configuration
  - *Test Scenario:* [Tier 3] **TS-05:** Validate Windows offline push integrity and startup gating.
  - *Priority:* P0

- **[CNV-96537]** — As a backup provider, I want Windows Server 2022 offline pull full baselines without history and increments from offline/online checkpoints to recover bootable guests with matching data, reject incomplete chains, and block startup until request deletion, preserving persistent vTPM/EFI configuration
  - *Test Scenario:* [Tier 3] **TS-06:** Validate Windows offline pull integrity and startup gating.
  - *Priority:* P0

- **[CNV-96511]** — As a backup provider, I want Linux online history to support Linux offline increments and subsequent VM startup in push and pull modes
  - *Test Scenario:* [Tier 2] **TS-07:** Verify online checkpoints support offline increments across backup modes.
  - *Priority:* P0

- **[CNV-96511]** — As a cluster admin, I want Linux VM startup blocked throughout offline push writing and allowed after successful completion
  - *Test Scenario:* [Tier 2] **TS-08:** Verify startup stays blocked during offline push, then resumes.
  - *Priority:* P0

- **[CNV-96511]** — As a cluster admin, I want Linux VM startup blocked throughout a successful offline pull and allowed after request deletion
  - *Test Scenario:* [Tier 2] **TS-09:** Verify startup stays blocked during offline pull until deletion.
  - *Priority:* P0

- **[CNV-96511]** — As a backup provider, I want interrupted preparation in either mode to resume the original request without corruption, and failed or cancelled pushes to preserve history, release startup and permit retry
  - *Test Scenario:* [Tier 2] **TS-10:** Validate offline preparation recovery and failed-push retry safety.
  - *Priority:* P1

- **[CNV-96511]** — As a cluster admin, I want source deletion to abort offline backups without blocking VM deletion in push and pull modes
  - *Test Scenario:* [Tier 2] **TS-11:** Verify source deletion aborts offline backups without blocking removal.
  - *Priority:* P1

- **[CNV-96511]** — As a cluster admin, I want overlapping offline backup requests rejected while the existing backup remains active
  - *Test Scenario:* [Tier 1] **TS-12:** Confirm overlapping requests fail while existing backups continue.
  - Candidate VEP outcome; apply the target-build decision required by Entry Criteria.
  - *Priority:* P1

- **[CNV-96511]** — As a backup provider, I want unchanged incremental requests to follow the agreed target-build contract while full backups remain available without another VM start in both modes
  - *Test Scenario:* [Tier 1] **TS-13:** Validate offline backup requests between VM starts.
  - Repeated-increment outcomes remain conditional on the target-build decision in Entry Criteria.
  - *Priority:* P1

- **[CNV-96511]** — As a backup provider, I want offline backups to retain healthy increments, fully protect new disks or disks with unusable history, and report unavailable disks without false complete-guest success in both modes
  - *Test Scenario:* [Tier 2] **TS-14:** Validate per-disk offline fallback and unavailable-disk reporting.
  - *Priority:* P1

- **[CNV-96511]** — As a cluster admin, I want residual VM activity to reject offline backup requests without producing output
  - *Test Scenario:* [Tier 1] **TS-15:** Verify residual source activity rejects requests without output.
  - Candidate VEP outcome; apply the target-build decision required by Entry Criteria.
  - *Priority:* P1

- **[CNV-96511]** — As a cluster admin, I want rollback to fail active offline backups without blocking later VM operations or backup requests in push and pull modes
  - *Test Scenario:* [Tier 2] **TS-16:** Verify rollback aborts offline backups and releases VM operations.
  - *Priority:* P1

- **[CNV-96511]** — As a backup provider, I want invalid credentials rejected before offline pull data is disclosed
  - *Test Scenario:* [Tier 1] **TS-17:** Verify unauthorized clients cannot retrieve offline pull disk data.
  - *Priority:* P1

- **[CNV-96511]** — As a cluster admin, I want five simultaneous stopped-VM backups, including three Windows guests and two Linux guests on ODF storage, to produce data matching their source backup points in push and pull modes
  - *Test Scenario:* [Tier 3] **TS-18:** Verify concurrent Windows and Linux backups preserve per-VM data.
  - *Priority:* P2

- **[CNV-96511]** — As a backup provider, I want expiry to fail an offline pull without advancing history or leaving VM startup blocked
  - *Test Scenario:* [Tier 2] **TS-19:** Verify expired offline pulls preserve history and release startup.
  - *Priority:* P2

- **[CNV-96511]** — As a backup provider, I want an offline-created checkpoint in push and pull modes to survive VM startup and migration so a later stopped-VM increment remains valid
  - *Test Scenario:* [Tier 2] **TS-20:** Verify offline checkpoints survive restart, migration and shutdown.
  - *Priority:* P2

- **[CNV-96511]** — As a cluster admin, I want CNV v5.0.0 online history to support offline increments after upgrade to CNV v5.1.0 in push and pull modes
  - *Test Scenario:* [Tier 2] **TS-21:** Verify pre-upgrade online history supports feature-gated offline increments.
  - *Priority:* P2

- **[CNV-96511]** — As a backup provider, I want certified-partner evidence of stopped-VM full/incremental recovery to demonstrate guest bootability and matching data, rejecting failed or incomplete protection claims
  - *Test Scenario:* [Tier 2] **TS-22:** Validate certified-partner recovery from stopped-VM full and incremental backups.
  - *Priority:* P1

- **[CNV-96511]** — As a backup provider, I want early pull-request deletion to advance history without implying external-chain completeness
  - *Test Scenario:* [Tier 1] **TS-23:** Confirm early offline pull deletion advances history despite incomplete retrieval.
  - *Priority:* P1

- **[CNV-96537]** — As a backup provider, I want full and incremental offline Linux backup points on a supported non-default CSI backend to recover bootable guests with matching checksums in push and pull modes, while incomplete chains fail validation
  - *Test Scenario:* [Tier 3] **TS-24:** Validate offline recovery integrity on supported non-default storage.
  - *Priority:* P1

---

### **IV. Sign-off and Approval**

This Software Test Plan requires approval from the following stakeholders:

* **Reviewers:**
  - QE: [Dalia Frank](@dafrank), [Kateryna Shvaika](@kshvaika), [Jose Manuel Castano](@josemacassan), [Ahmad Hafe](@Ahmad-Hafe), [Jenia Peimer](@jpeimer), [Adam Cinko](@acinko-rh)
  - Development: [Alvaro Romero](@alromeros), [Adi Aloni](@Acedus)
* **Approvers:**
  - QE Lead: [Ruth Netser](@rnetser)
  - Dev Lead: [Adam Litke](@aglitke)
  - Product Manager: [Peter Lauterbach](@peterclauterbach)
