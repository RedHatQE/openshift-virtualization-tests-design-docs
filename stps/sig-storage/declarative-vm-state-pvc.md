# Openshift-virtualization-tests Test plan

## **Clone and Storage Migration support for VMState PVC - Quality Engineering Plan**

### **Metadata & Tracking**

- **Enhancement(s):** [KubeVirt VEP #312: Declarative VMState PVC](https://github.com/kubevirt/enhancements/blob/main/veps/sig-storage/312-declarative-vmstate/vep.md)
- **Feature Tracking:** N/A — no feature-level parent is assigned in Jira.
- **Epic Tracking:** [CNV-79308](https://redhat.atlassian.net/browse/CNV-79308)
- **Feature Maturity:**
  - DP: CNV v5.1.0 ([CNV-98256](https://redhat.atlassian.net/browse/CNV-98256))
  - TP: CNV v5.2.0 (proposed)
  - GA: CNV v5.3.0 (proposed, see II.4)
- **QE Owner(s):** [Emanuele Prella](https://github.com/ema-aka-young)
- **Owning SIG:** sig-storage
- **Participating SIGs:** N/A

**Document Conventions:**

- **VMState PVC:** A persistent storage volume that holds virtual machine state such as vTPM, EFI, and change-tracking data.
- **vTPM:** Virtual Trusted Platform Module.
- **EFI:** Extensible Firmware Interface.
- **CBT:** QEMU Changed Block Tracking, which enables incremental backups of VM disks.
- **`DeclarativeVMState`:** Feature gate that allows a VM to reference an existing VMState PVC or request a new PVC through a volume claim template.
- **`IncrementalBackup`:** Feature gate that makes full and incremental VM backups available.
- **Declarative and implicit VMState:** With declarative VMState, the VM owner references or requests a PVC in the VM configuration. With implicit VMState, OpenShift Virtualization creates the PVC automatically.
- **MTC:** Migration Toolkit for Containers.
- **Source storage:** The storage class or volume used before a clone or migration operation.

### **Feature Overview**

OpenShift Virtualization will preserve captured vTPM and EFI state when users clone a virtual machine or migrate its storage. Guests depend on this state for security and boot continuity. The feature covers independent clone storage, state relocation, and continued use of the target volume, including during Windows live storage conversion. CBT history follows the same VM when its VMState PVC moves and is cleared when a different VM adopts the PVC. Feature Limitations describes what happens when a snapshot lacks captured state. The plan targets GA and marks checks also required for the CNV v5.1.0 Developer Preview with [DP].

---

### **I. Motivation and Requirements Review (QE Review Guidelines)**

QE interprets the clone and migration requirements as preserving usable guest state across both operations. A clone needs independent state storage, and a migrated VM must continue using its relocated state when source storage becomes inaccessible.

#### **1. Requirement & User Story Review Checklist**

- [x] **Review Requirements**
  - *List the key D/S requirements reviewed:*
    - [CNV-98256](https://redhat.atlassian.net/browse/CNV-98256): Clone captured VMState, adopt released VMState, move RWO VMState using a claim template, and report the active PVC. Preserve the VM's backup history when moving its storage and clear that history when a different VM adopts the PVC. See the [merged implementation](https://github.com/kubevirt/kubevirt/pull/19173) for the behavior contract.
    - [CNV-100645](https://redhat.atlassian.net/browse/CNV-100645): Clone VMs from implicit VMState sources into declarative targets once the tested build contains the fix.
    - [CNV-79312](https://redhat.atlassian.net/browse/CNV-79312): Tracks upgrade consideration. QE proposes verifying that pre-upgrade guest state remains usable on the same VM and PVC. The supported release pair still needs confirmation.
    - [CNV-83112](https://redhat.atlassian.net/browse/CNV-83112): Records the Windows split-storage failure in legacy MTC conversion. It informs the acceptance criteria for the supported live storage conversion workflow under CNV-98256.

- [x] **Understand Value and Customer Use Cases**
  - *Describe the feature's value to customers:* Customers can clone captured security/boot state or relocate persistent state without losing it or accidentally sharing it between VMs; uncaptured-state snapshots report the limitation instead of silently reusing the source.
  - *List the customer use cases identified:*
    - As a VM owner, I want to clone a VM with captured vTPM or EFI state so that the clone starts with the same trusted state.
    - As a VM owner, I want to move a VM to another storage class so that all of its volumes, including VMState PVC, move together.
    - As a cluster administrator, I want live storage conversion to move Windows guest disks and VMState to the target storage class so that the VM can continue using its saved state there.

- [x] **Testability**
  - *Note any requirements that are unclear or untestable:* The acceptance criteria require new end-to-end checks and extensions to the existing Windows conversion and CBT tests. Legacy clone, GA upgrade, and source-independence execution depend on their criteria in II.4.

- [x] **Acceptance Criteria**
  - *List the acceptance criteria:*
    - A clone with captured VMState can read the source VM's saved vTPM-protected data and EFI variables and uses a separate VMState PVC.
    - After storage migration, the VM reports the target VMState PVC as active and can read the vTPM-protected data and EFI variables saved before the move.
    - After Windows live storage conversion, all guest disks and the active VMState PVC use the target storage class.
    - During Windows live storage conversion, the VM stays running from start to completion without a stop or restart.
    - A clone from a snapshot without captured VMState reports the missing state. A target with a claim template warns and starts with fresh independent state. A target without a template is rejected.
    - The same VM can take an incremental backup from its pre-migration checkpoint after RWO VMState relocation.
    - A different VM adopting the released PVC takes a full backup of the tracked disk.
  - *Note any gaps or missing criteria:* The epic leaves failure recovery and Windows continuity thresholds unspecified. The plan uses preservation of saved guest state and uninterrupted guest runtime as observable QE criteria. VEP templating and PVC sizing workflows are outside the clone, relocation, and released-state adoption scope tracked here.

- [x] **Non-Functional Requirements (NFRs)**
  - *List applicable NFRs and their targets:*
    - Security and integrity: captured vTPM and EFI state remains usable after clone or relocation. Concurrent writers cannot share the same VMState PVC.
    - Compatibility and reliability: source adoption, clone and relocation preserve saved guest state. Failed operations preserve the original volume and state.
    - Backup integrity requires preserving CBT history during same-VM VMState migration and clearing it on adoption by a different VM.
    - Observability: users can identify the active state volume and distinguish unavailable state, exclusive-use rejection and fresh-state fallback through VM status or warning events.
    - Usability: II.2 covers API status, error, and warning feedback. The console and accessibility decision is pending in II.1.
    - Downtime: Windows live storage conversion must complete without stopping or restarting the guest.
    - Documentation: review release notes and clone/migration caveats against delivered behavior, including legacy-source, uncaptured-state, and storage-conversion boundaries. Complete the reviews tracked by [CNV-79311](https://redhat.atlassian.net/browse/CNV-79311) and [CNV-79315](https://redhat.atlassian.net/browse/CNV-79315) before feature sign-off.
  - *Note any NFRs not covered and why:*
    - Performance and scale benchmarking have no feature-specific targets. Functional migration checks respect the cluster's configured parallelism and storage capacity limits.
    - Monitoring introduces no new metrics or alerts. Functional tests cover user-visible state and failure reporting.
    - Connectivity: The guest runtime check covers continuity during Windows conversion. The feature defines no separate network interruption or throughput target.
    - Portability: The plan covers the workflows on the qualified CSI storage and OpenShift platform in II.3. The feature defines no cloud-specific requirement.

#### **2. Feature Limitations**

- **RWO VMState PVC referenced only by source cannot live-migrate without a volume claim template**
  - *Sign-off:* [Alvaro Romero](https://github.com/alromeros)/2026-11-25

- **Declarative VMState storage requires Filesystem volume mode**
  - *Sign-off:* [Alvaro Romero](https://github.com/alromeros)/2026-11-25

- **An existing implicit-state VM cannot be converted in place by adding declarative state configuration**
  - A new or recreated VM may adopt its released legacy PVC.
  - *Sign-off:* [Alvaro Romero](https://github.com/alromeros)/2026-11-25

- **Legacy implicit-state cloning is blocked until the CNV-100645 fix is included in the tested build**
  - [CNV-100645](https://redhat.atlassian.net/browse/CNV-100645) tracks cloning from an implicit source into a declarative target. Confirm that the fix in [KubeVirt PR #19814](https://github.com/kubevirt/kubevirt/pull/19814) is present in the tested build before executing those variants.
  - *Sign-off:* [Alvaro Romero](https://github.com/alromeros)/2026-11-25

- **A snapshot cannot preserve state it did not capture**
  - Restoring to a different VM is rejected without a volume claim template. With a template, the user receives a warning and the target starts with fresh, independent state rather than the source TPM/EFI state.
  - *Sign-off:* [Alvaro Romero](https://github.com/alromeros)/2026-11-25

#### **3. Technology and Design Review**

- [x] **Developer Handoff/QE Kickoff**
  - *Key takeaways and concerns:* QE reviewed the [declarative VMState design](https://github.com/kubevirt/enhancements/blob/main/veps/sig-storage/312-declarative-vmstate/vep.md) and [CNV-98256](https://redhat.atlassian.net/browse/CNV-98256). Verify that a clone has an independent copy of saved state and that a migrated VM reports and uses state on the target storage.

- [x] **Technology Challenges**
  - *List identified challenges:* Persistent vTPM and EFI state is security- and boot-sensitive, storage behavior differs across storage classes, and Windows live storage conversion must coordinate disk migration with VMState relocation.
  - *Impact on testing approach:* Compare saved guest vTPM-protected data and EFI variables to verify state preservation. Cover direct and snapshot clones from declarative and, once the fix is delivered, legacy sources. For Windows live conversion, the migration plan supplies the guest-disk destinations and the VM's volume claim template supplies the RWO VMState destination. Ordinary RWX compute migration may reuse the shared state volume.

- [x] **API Extensions**
  - *List new or modified APIs:* The declarative VMState API lets users reference an existing PVC or request one through a volume claim template, and VM status reports the active VMState volume.
  - *Testing impact:* Cover released-source adoption and missing-source reporting, target creation, active-volume reporting, and continued use of the correct volume after clone or relocation. Reuse existing feature-level contracts for Linux adoption, exclusive use, and missing-source errors.

- [x] **Test Environment Needs**
  - *See environment requirements in Section II.3 and testing tools in Section II.3.1*

- [x] **Topology Considerations**
  - *Describe topology requirements:* Use an OpenShift Virtualization cluster with two distinct supported storage classes and schedulable source and destination nodes for live migration.
  - *Impact on test design:* Clone and storage-migration scenarios can share cluster setup. Keep both storage classes available to the workers selected for Windows live conversion. Use a disposable source volume for TS-011 so the check can make that volume unavailable while keeping target storage available.

### **II. Software Test Plan (STP)**

#### **1. Scope of Testing**

**Testing Goals**

- **[P0] [DP]** Verify that Linux and Windows direct and snapshot clones with captured state use independent storage and preserve vTPM and EFI state. Exercise declarative sources on both milestones. Run the legacy-source variants at each milestone when the build meets the CNV-100645 entry criterion in II.4.
- **[P0] [DP]** Verify that native RWO relocation and Windows live storage conversion use the target storage class and preserve saved vTPM and EFI state. Verify that Windows live storage conversion keeps the guest running throughout.
- **[P1] [DP]** Verify that a failed clone leaves original state usable. A snapshot without captured state must reject the clone without a claim template or warn and initialize independent state when a template is available.
- **[P1] [DP]** Verify that failed native relocation or Windows live conversion leaves the original vTPM and EFI state usable.
- **[P1] [DP]** Verify that a VM with a source-only RWO VMState PVC reports why live migration is blocked and can migrate after the owner adds a volume claim template and restarts the VM.
- **[P1] [DP]** Verify that a VM can use relocated vTPM and EFI state when source storage is inaccessible.
- **[P1] [DP]** Verify that Windows can adopt released state and retain saved vTPM and EFI state across reboot. Run the existing Linux adoption and startup-error checks in II.2.
- **[P1]** Verify that a different VM adopting a released VMState PVC starts with fresh CBT state and takes a new full backup.
- **[P1]** Verify that the same VM retains its CBT checkpoint and can continue incremental backups after its RWO VMState PVC moves to the target storage class.
- **[P1]** Verify that the same Linux and Windows VMs can read pre-upgrade vTPM-protected data and EFI variables from their existing VMState PVCs after a supported upgrade to GA.

**Priority Levels:**

- **P0** blocks GA.
- **P1** is required for full feature coverage.
- **P2** can be deferred if the schedule is constrained.

**Out of Scope (Testing Scope Exclusions)**

- **Performance and scale benchmarking**
  - *Rationale:* QE will verify functional behavior within the lab's migration and storage limits. Jira and the design define no latency, throughput, or scale target to benchmark.
  - *Sign-off (Quality Owner or Product Manager):* Pending.

- **OpenShift web console workflows and accessibility**
  - *Rationale:* The API exposes the active-volume status and actionable rejection and fallback feedback needed for these workflows. The QE owner will ask PM or UX whether testing the console and its accessibility would add customer value and record the approach here before accepting this exclusion.
  - *Sign-off (Quality Owner or Product Manager):* Pending PM or UX input and scope approval.

- **Legacy MTC storage-conversion reproduction**
  - *Rationale:* [CNV-83112](https://redhat.atlassian.net/browse/CNV-83112) was closed as Won't Do for the legacy MTC workflow. TS-017 checks the analogous split-storage outcome using the supported Windows live storage conversion workflow.
  - *Sign-off (Quality Owner or Product Manager):* Pending.

**Test Limitations**

- **Source-storage fault injection is restricted to isolated, disposable storage**
  - Qualify a source-volume disconnect or equivalent scoped fault that leaves target storage available before running the source-independence case. Confirm the source is inaccessible and the migrated guest can still use its saved state; reference inspection alone is not a substitute.
  - *Sign-off:* [Alvaro Romero](https://github.com/alromeros)/2026-11-25

#### **2. Test Strategy**

**Functional**

- [x] **Functional Testing** — Validates that the feature works according to specified requirements and user stories
  - *Details:* Cover VM clone, native storage relocation, Windows live storage conversion, persistent-state usability, target-volume reference, and source-storage independence. Exercise direct and snapshot clones with captured state from declarative sources on Linux and Windows. Repeat with legacy sources when the build includes the fix in I.2.

- [x] **Automation Testing** — Confirms test automation plan is in place for CI and regression coverage (all tests are expected to be automated)
  - *Details:* Run the existing Tier 1 contracts listed under Regression Testing. Automate Tier 2 Linux workflows and Tier 3 Windows workflows in RedHatQE/openshift-virtualization-tests. Run the DP-tagged cases at Developer Preview and GA. Run the Linux and Windows upgrade cases for GA. Reuse Windows vTPM and BitLocker setup and extend existing migration tests with the VMState assertions in III. Partial-coverage tags identify automation to extend.

- [x] **Regression Testing** — Verifies that new changes do not break existing functionality
  - *Details:* Run these existing SIG Storage checks on the feature build.
    - [KubeVirt VMState adoption](https://github.com/kubevirt/kubevirt/blob/a9a239a1058dbdb0cd75709c6ba3a5b55d62e75b/tests/storage/vmstate.go#L321-L353) starts a second Fedora VM on released storage and reads the saved TPM secret and EFI variable.
    - [KubeVirt missing-source reporting](https://github.com/kubevirt/kubevirt/blob/a9a239a1058dbdb0cd75709c6ba3a5b55d62e75b/tests/storage/vmstate.go#L355-L376) reports the missing PVC when the VM attempts to start.
    - [KubeVirt exclusive-use reporting](https://github.com/kubevirt/kubevirt/blob/a9a239a1058dbdb0cd75709c6ba3a5b55d62e75b/tests/storage/vmstate.go#L378-L414) reports that the PVC is in use when a second VM attempts to start while the first VM holds it.
    - KubeVirt unit tests cover the source-only RWO migratability condition and the VM update that adds the template. TS-013 covers rejection and TS-014 covers successful retry. [Migratability checks](https://github.com/kubevirt/kubevirt/blob/a9a239a1058dbdb0cd75709c6ba3a5b55d62e75b/pkg/virt-handler/vm_test.go#L3032-L3065) · [VM update validation](https://github.com/kubevirt/kubevirt/blob/a9a239a1058dbdb0cd75709c6ba3a5b55d62e75b/pkg/virt-api/webhooks/validating-webhook/admitters/vms-admitter_test.go#L1800-L1808)
    - The [KubeVirt CBT ownership unit test](https://github.com/kubevirt/kubevirt/blob/a9a239a1058dbdb0cd75709c6ba3a5b55d62e75b/pkg/virt-launcher/virtwrap/manager_test.go#L5719-L5731) checks that a change of VM ownership clears the PVC's previous CBT data. TS-022 covers adoption and the backup outcome end to end.
    - The existing test verifies that a backup remains incremental after the VM moves to another node. Reuse its backup setup and assertions in TS-023 with declarative RWO VMState relocated across storage classes. [Incremental backup after live migration](https://github.com/RedHatQE/openshift-virtualization-tests/blob/7b8e0c0900f66c1d7e9415af60f1cf9126212bda/tests/storage/cbt/test_cbt.py#L389-L439)
    - [Windows vTPM storage migration](https://github.com/RedHatQE/openshift-virtualization-tests/blob/7b8e0c0900f66c1d7e9415af60f1cf9126212bda/tests/storage/storage_migration/test_storage_class_migration.py#L252-L330) checks boot time, guest-file integrity, and disk placement. Extend it with the VMState assertions in III.
    - Existing platform coverage owns the broader Windows guest-version and application matrix, storage-class provisioning, and basic PVC binding. This plan verifies VMState workflows on the selected guest images and storage classes.

- [ ] **Self-Validation Testing** — Should any of the new tests be included in the self-validation test package?
  - *Details:* No new package inclusion is proposed for the multi-operation clone/relocation workflows. Tier 1 adoption and reporting reuse existing feature checks. Curated downstream self-validation package membership is a separate selection decision.

**Non-Functional**

- [ ] **Performance Testing** — Validates feature performance meets requirements (latency, throughput, resource usage)
  - *Details:* Not applicable; no performance target is defined.

- [ ] **Scale Testing** — Validates feature behavior under increased load and at production-like scale (e.g., large number of VMs, nodes, or concurrent operations)
  - *Details:* See the proposed benchmarking exclusion in II.1. Run functional cases within the cluster's configured migration parallelism and available storage capacity.

- [x] **Security Testing** — Verifies security requirements, RBAC, authentication, authorization, and vulnerability scanning
  - *Details:* Verify captured vTPM and EFI state remains usable after clone or relocation, and that uncaptured-state fallback creates independent fresh state. Run the existing exclusive-use check listed under Regression Testing.

- [x] **Usability Testing** — Validates user-facing feedback
  - *Details:* Through the API, verify that users can identify the active target PVC, understand why an uncaptured-state clone or source-only RWO migration is rejected, and distinguish fresh-state fallback from preservation. Reuse the missing and in-use errors covered by the regression checks. The console and accessibility decision is pending in II.1.

- [ ] **Monitoring** — Does the feature require metrics and/or alerts?
  - *Details:* Not applicable; no new metric or alert requirement is defined.

**Integration & Compatibility**

- [x] **Compatibility Testing** — Ensures feature works across supported platforms, versions, and configurations
  - *Details:* Validate clone, native storage relocation, and Windows live storage conversion with distinct source and target storage classes.

- [x] **Upgrade Testing** — Validates upgrade paths from previous versions, data migration, and configuration preservation
  - *Details:* For GA, carry the same Linux and Windows VMs, PVCs, and saved guest state through the supported upgrade. This proves that the GA build can read state written by the source build. Qualify the pair in II.3 before running TS-020 and TS-021. Developer Preview covers the tagged workflows on its target build.

- [x] **Dependencies**
  - *Details:* The Windows conversion cases require a build with the storage migration plan API. Legacy-source clones require the [CNV-100645](https://redhat.atlassian.net/browse/CNV-100645) fix in the tested CNV build. Other scenarios can proceed when their entry criteria are met.

- [x] **Cross Integrations**
  - *Details:* SIG Storage covers VMState across clone, snapshot restore, native storage relocation, Windows live storage conversion, and incremental backup after adoption or relocation.

**Infrastructure**

- [ ] **Cloud Testing** — Does the feature require multi-cloud platform testing? Consider cloud-specific features.
  - *Details:* Not applicable; no cloud-specific behavior is defined. Storage-class compatibility is covered on the standard test platform.

#### **3. Test Environment**

- **Cluster Topology:** Planned three control-plane nodes and three worker nodes, with at least two schedulable workers for live migration.
- **OCP & OpenShift Virtualization Version(s):** Use CNV v5.1.0 for Developer Preview. The GA upgrade candidate is the proposed TP release, CNV v5.2.0, to the proposed GA release, CNV v5.3.0. Before scheduling, the QE owner confirms the actual CNV builds, their supported OCP versions, and the upgrade path in [CNV-79312](https://redhat.atlassian.net/browse/CNV-79312). Use a source build that supports declarative VMState.
- **CPU Virtualization:** VT-x (Intel) or AMD-V enabled
- **Compute Resources:** Minimum per worker node: 8 vCPUs, 32GB RAM
- **Special Hardware:** N/A - no special hardware needed.
- **Storage:** Plan to use ODF classes `ocs-storagecluster-ceph-rbd-virtualization` (source) and `ocs-storagecluster-ceph-rbd` (target) with the `openshift-storage.rbd.csi.ceph.com` provisioner. Qualify both classes for RWO Filesystem VMState, capacity, binding, and live relocation. Confirm that the clone source captures VMState in snapshots. If the pair cannot support both clone and relocation, qualify separate pairs and record their names and provisioners before running the affected scenarios.
- **Network:** OVN-Kubernetes, IPv4
- **Required Operators:** OpenShift Virtualization with the KubeVirt Migration Operator and its controller available for Windows live storage conversion.
- **Platform:** Planned bare-metal OpenShift cluster with ODF. Confirm the lab against the storage and migration requirements in II.4.
- **Special Configurations:** Enable `DeclarativeVMState` on the gated build. Use Fedora and Windows Server 2022 guests with persistent vTPM and EFI, reusing the guest setup in II.2. For RWO relocation, adopt a VMState PVC from the source class and set the target class in the volume claim template. Use a [KubeVirt storage migration plan](https://github.com/kubevirt/kubevirt-migration-controller/blob/main/api/migrationcontroller/v1alpha1/virtualmachinestoragemigrationplan_types.go) to map the Windows guest disks to the target class.
- **CBT Configurations:** Enable `IncrementalBackup` and VM-level CBT. Use the CBT test disk defined in Document Conventions and provision backup destination storage.

#### **3.1. Testing Tools & Frameworks**

- **Test Framework:** Standard
- **CI/CD:** N/A - no specific consideration on CI/CD.
- **Other Tools:** N/A - no specific tools involved.

#### **4. Entry Criteria**

- [x] Requirements and design documents are **approved and merged**
- [ ] The QE owner qualifies the OCP/CNV build for each test milestone, the planned storage classes, guest images, snapshot support, and Windows live conversion with declarative RWO VMState.
- [ ] For legacy-source clone variants only, confirm that the tested build for the milestone includes [CNV-100645](https://redhat.atlassian.net/browse/CNV-100645).
- [ ] For TS-011 only, the QE owner qualifies a disposable setup in which the selected fault makes the original VMState volume inaccessible while the target stays available.
- [ ] For TS-020 and TS-021, PM confirms the GA target and the QE owner records the supported source and target OCP/CNV builds in [CNV-79312](https://redhat.atlassian.net/browse/CNV-79312).

#### **5. Risks**

**Timeline/Schedule**

- **Mitigation:** No risk identified for the required Tier 2 and Tier 3 runs. See Dependencies for the legacy-clone fix.

**Test Coverage**

- **Risk:** Existing Windows vTPM migration tests can pass while VMState remains on source storage or saved guest state is lost.
  - **Mitigation:** Run TS-009 through TS-011 for native relocation. Run TS-015, TS-017, and TS-018 for Windows saved state, target placement, and uninterrupted runtime. TS-016 covers failure before handoff and verifies that the original VM can still use its saved state.
  - *Areas with reduced coverage:* Existing automation lacks VMState-specific assertions and may miss offline fallback. Execute the native and Windows conversion success and failure cases plus the Windows clone and adoption checks before sign-off.
  - *Sign-off:* [Alvaro Romero](https://github.com/alromeros)/2026-11-25

**Test Environment**

- **Risk:** Differences in storage and snapshot capabilities across the selected configurations could produce unsupported clone or migration results.
  - **Mitigation:** The QE owner qualifies snapshot capture and RWO cross-class relocation before execution. Use separate qualified storage pairs if the planned pair cannot meet both needs.
  - *Missing resources or infrastructure:* The lab, storage pairs, and guest images still require qualification as listed in II.3.
  - *Sign-off:* [Alvaro Romero](https://github.com/alromeros)/2026-11-25

- **Risk:** The GA target or a supported upgrade path may remain unconfirmed when the lab is scheduled.
  - **Mitigation:** PM confirms the GA target. The QE owner confirms the supported OCP/CNV release pair in CNV-79312 before provisioning the upgrade lab. Keep TS-020 and TS-021 open until a supported pair is available.
  - *Missing resources or infrastructure:* A qualified source and target release pair for GA.
  - *Sign-off:* [Alvaro Romero](https://github.com/alromeros)/2026-11-25

**Untestable Aspects**

- **Risk:** Source-independence evidence may remain incomplete if the isolated fault-injection capability is not qualified before execution.
  - **Mitigation:** Meet the isolation constraint in Test Limitations before this case starts; schedule a disposable source/target environment and prove that the selected fault makes source state inaccessible while target state remains usable. Keep the entry criterion open until that qualification succeeds.
  - *Alternative validation approach:* Use a scoped source-volume disconnect. If no safe scoped fault can be qualified, the source-independence case remains unexecuted and requires an explicit coverage decision before sign-off.
  - *Sign-off:* [Alvaro Romero](https://github.com/alromeros)/2026-11-25

**Resource Constraints**

- **Mitigation:** No risk identified. No capacity gap has been identified for the required Tier 3 runs.

**Dependencies**

- **Risk:** The legacy-clone fix may miss the CNV v5.1.0 build selected for validation. See the product constraint in I.2.
  - **Mitigation:** Confirm fix inclusion before legacy-source clone execution. If the fix misses the DP build, run the declarative-source cases and carry the unexecuted legacy variants forward to a build with the fix. If the fix misses GA, record the blocked variants and obtain a Quality Owner or Product Manager scope decision before GA sign-off.
  - *Dependent teams or components:* CNV-100645 delivery in the selected build
  - *Sign-off:* [Alvaro Romero](https://github.com/alromeros)/2026-11-25

---

### **III. Test Scenarios & Traceability**

- **[CNV-98256](https://redhat.atlassian.net/browse/CNV-98256)** — As a VM owner, I want to clone a VM with usable and independent vTPM and EFI state.
  - *Source and clone method for TS-001, TS-002, TS-006, and TS-008:* Run a direct clone and a clone from a snapshot with captured VMState for declarative sources. The [CNV-100645](https://redhat.atlassian.net/browse/CNV-100645) variants repeat both methods from an implicit source with a declarative target and follow the legacy-source entry criterion in II.4.
  - *Test Scenario:* **TS-001**: [Tier 2] A Linux clone boots, reads the source VM's saved vTPM-protected data, and returns the saved EFI variable value.
    - *Priority:* P0 [DP]
  - *Test Scenario:* **TS-002**: [Tier 2] The Linux clone reports an active VMState PVC distinct from the source VM's PVC.
    - *Priority:* P0 [DP]
  - *Test Scenario:* **TS-003**: [Tier 2] After a clone is rejected, the source VM can still read its saved vTPM-protected data and EFI variable.
    - *Priority:* P1 [DP]
  - *Test Scenario:* **TS-004**: [Tier 2] Cloning a snapshot without captured VMState and without a target claim template fails. The restore reports that the snapshot lacks VMState and the target has no template.
    - *Priority:* P1 [DP]
  - *Test Scenario:* **TS-005**: [Tier 2] For a snapshot without captured VMState, the restore warns that the target will start with fresh state. The target boots with a separate PVC from its claim template, and fresh vTPM and EFI state is confirmed by the absence of the original guest test values.
    - *Priority:* P1 [DP]
  - *Test Scenario:* **TS-006**: [Tier 3] The Windows clone boots, unlocks its BitLocker volume with saved vTPM state, and returns the saved EFI variable value.
    - *Priority:* P0 [DP]
  - *Test Scenario:* **TS-007**: [Tier 3] After changing test vTPM-protected data and an EFI variable in the Windows clone, the source VM still returns the original test values.
    - *Priority:* P1 [DP]
  - *Test Scenario:* **TS-008**: [Tier 3] The Windows clone reports an active VMState PVC distinct from the source VM's PVC.
    - *Priority:* P0 [DP]

- **[CNV-98256](https://redhat.atlassian.net/browse/CNV-98256)** — As a VM owner, I want to relocate RWO VMState and keep using saved state on the target.
  - *Test Scenario:* **TS-009**: [Tier 2] [PARTIAL_COVERAGE] After native RWO relocation completes, the guest reads the vTPM-protected data and EFI variable saved before the move.
    - *Priority:* P0 [DP]
  - *Test Scenario:* **TS-010**: [Tier 2] [PARTIAL_COVERAGE] After native RWO relocation completes, VM status identifies a new active VMState PVC on the target StorageClass.
    - *Priority:* P0 [DP]
  - *Test Scenario:* **TS-011**: [Tier 2] After native relocation, the guest can still read its saved vTPM-protected data and EFI variable while the original VMState volume is verified inaccessible and target storage stays available.
    - *Priority:* P1 [DP]
  - *Test Scenario:* **TS-012**: [Tier 2] If native relocation fails before the target becomes active, the VM still uses the original PVC and reads its saved vTPM-protected data and EFI variable.
    - *Priority:* P1 [DP]
  - *Test Scenario:* **TS-013**: [Tier 2] A live migration request for a VM using a source-only RWO VMState PVC is blocked. VM status explains that a claim template is required to provision the destination.
    - *Priority:* P1 [DP]
  - *Test Scenario:* **TS-014**: [Tier 2] After adding a claim template and restarting the VM from TS-013, the retried live migration completes and the VM reports an active PVC on the target StorageClass.
    - *Priority:* P1 [DP]

- **[CNV-98256](https://redhat.atlassian.net/browse/CNV-98256)** — As a cluster administrator, I want live storage conversion to move a running Windows VM's guest disks and VMState to target storage.
  - *Coverage note:* [CNV-83112](https://redhat.atlassian.net/browse/CNV-83112) documents the analogous split-storage failure in legacy MTC. TS-017 checks the active storage for the supported live conversion workflow.
  - *Test Scenario:* **TS-015**: [Tier 3] After live storage conversion completes, Windows can still read the vTPM-protected data and EFI variable saved before conversion.
    - *Priority:* P0 [DP]
  - *Test Scenario:* **TS-016**: [Tier 3] If live storage conversion fails before the target VMState PVC becomes active, Windows still uses the original VMState PVC and can read its saved vTPM-protected data and EFI variable.
    - *Priority:* P1 [DP]
  - *Test Scenario:* **TS-017**: [Tier 3] After live storage conversion completes, all Windows guest disk PVCs and the VMState PVC named as active in VM status use the target StorageClass.
    - *Priority:* P0 [DP]
  - *Test Scenario:* **TS-018**: [Tier 3] Observe the Windows guest's running state throughout live storage conversion. It stays running from start to completion, and the guest boot time is unchanged after completion.
    - *Priority:* P0 [DP]

- **[CNV-98256](https://redhat.atlassian.net/browse/CNV-98256)** — As a VM owner, I want to keep using saved vTPM and EFI state when a Windows VM adopts released state storage.
  - *Test Scenario:* **TS-019**: [Tier 3] A Windows VM adopting a released VMState PVC can read the previous VM's saved vTPM-protected data and EFI variable after reboot.
    - *Priority:* P1 [DP]

- **[CNV-79312](https://redhat.atlassian.net/browse/CNV-79312)** — As a cluster administrator, I want to keep using VMs' saved vTPM and EFI state after a supported upgrade.
  - *Coverage note:* These QE-derived scenarios retain each VM and its VMState PVC across the qualified upgrade pair in II.3.
  - *Test Scenario:* **TS-020**: [Tier 2] After the upgrade, the same Linux VM can read the vTPM-protected data and EFI variable saved to its VMState PVC before upgrade.
    - *Priority:* P1
  - *Test Scenario:* **TS-021**: [Tier 3] After the upgrade, the same Windows VM can read the vTPM-protected data and EFI variable saved to its VMState PVC before upgrade.
    - *Priority:* P1

- **[CNV-98256](https://redhat.atlassian.net/browse/CNV-98256)** — As a backup administrator, I want backup history to follow the same VM after storage relocation and reset when a different VM adopts the storage.
  - *Coverage notes:* Qualify the CBT test disk and establish a backup checkpoint before each operation. Retain the tracked guest disk PVC and volume name.
  - *Test Scenario:* **TS-022**: [Tier 2] After a different VM adopts the released VMState PVC, the old VM's checkpoint is cleared and the adopter's first completed backup reports a full backup for the tracked disk.
    - *Priority:* P1
  - *Test Scenario:* **TS-023**: [Tier 2] [PARTIAL_COVERAGE] After RWO relocation, the same VM uses the target VMState PVC and the next completed backup reports an incremental backup for the tracked disk from its pre-migration checkpoint.
    - *Priority:* P1

---

### **IV. Sign-off and Approval**

This plan requires sign-off from at least one person per function.

- Feature Owner: [Alvaro Romero](https://github.com/alromeros)
- Quality Owner: [Dalia Frank](https://github.com/dalia-frank), [Jenia Peimer](https://github.com/jpeimer), [Ruth Netser](https://github.com/rnetser)
- Product Manager: [Peter Lauterbach](https://github.com/peterclauterbach)
