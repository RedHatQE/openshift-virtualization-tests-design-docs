# Openshift-virtualization-tests Test plan

## **Clone and Storage Migration support for VMState PVC - Quality Engineering Plan**

### **Metadata & Tracking**

- **Enhancement(s):** [KubeVirt VEP #312: Declarative VMState PVC](https://github.com/kubevirt/enhancements/blob/main/veps/sig-storage/312-declarative-vmstate/vep.md)
- **Feature Tracking:** N/A — no feature-level parent is assigned in Jira.
- **Epic Tracking:** [CNV-79308](https://redhat.atlassian.net/browse/CNV-79308)
- **Feature Maturity:**
  - DP: CNV v5.1.0
  - TP: CNV v5.2.0 [confirm]
  - GA: CNV v5.3.0 [confirm]
- **QE Owner(s):** [Emanuele Prella](https://github.com/ema-aka-young)
- **Owning SIG:** sig-storage
- **Participating SIGs:** N/A

**Document Conventions:**

- **VMState PVC:** A persistent storage volume that holds virtual machine state such as vTPM, EFI, and change-tracking data.
- **vTPM:** Virtual Trusted Platform Module.
- **EFI:** Extensible Firmware Interface.
- **CBT:** QEMU Changed Block Tracking, which enables incremental backups of VM disks.
- **CBT test disk:** A persistent guest disk on a dedicated PVC that supports online incremental backup. Keep the disk PVC and its VM volume name unchanged when moving VMState or attaching the disk to the adopter.
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
    - A clone from a declarative-source snapshot without captured VMState reports the missing state. With a claim template inherited from the snapshot, the clone warns and starts with fresh independent state. Without an inherited template, the clone is rejected.
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
  - For a declarative-source snapshot, restoring to a different VM without an inherited volume claim template is rejected. With an inherited template, the user receives a warning and the target starts with fresh, independent state.
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
- **[P1] [DP]** Verify that a failed clone leaves original state usable. For a declarative-source snapshot without captured state, verify rejection without an inherited claim template and a warning with fresh, independent state when the clone inherits a template.
- **[P1] [DP]** Verify that failed native relocation or Windows live conversion leaves the original vTPM and EFI state usable.
- **[P1] [DP]** Verify that a VM with a source-only RWO VMState PVC reports why live migration is blocked and can migrate after the owner adds a volume claim template and restarts the VM.
- **[P1] [DP]** Verify that a VM can start from the relocated VMState PVC and use saved vTPM and EFI state while the original PVC is inaccessible.
- **[P1] [DP]** Verify that Windows can adopt released state and retain saved vTPM and EFI state across reboot. Run the existing Linux adoption and startup-error checks in II.2.
- **[P1]** Verify that a different VM adopting a released VMState PVC starts its own backup chain with a full backup. The ownership regression in II.2 verifies that adoption clears the previous VM's CBT data.
- **[P1]** Verify that the same VM retains its CBT checkpoint and can continue incremental backups after its RWO VMState PVC moves to the target storage class.
- **[P1]** Verify that Linux and Windows still use their previously relocated VMState PVCs and can read saved vTPM and EFI state after a supported upgrade to GA.
- **[P2]** Verify that changing vTPM and EFI test values in a Windows clone leaves the source VM's saved values intact.

**Priority Levels:**

- **P0** blocks GA.
- **P1** is required for full feature coverage.
- **P2** can be deferred if the schedule is constrained.

**Out of Scope (Testing Scope Exclusions)**

- **Performance and scale benchmarking**
  - *Rationale:* QE will verify functional behavior within the lab's migration and storage limits. Jira and the design define no latency, throughput, or scale target to benchmark.
  - *Sign-off (Quality Owner or Product Manager):* [Name/Date]

- **OpenShift web console workflows and accessibility**
  - *Rationale:* The API exposes the active-volume status and actionable rejection and fallback feedback needed for these workflows. The QE owner will ask PM or UX whether testing the console and its accessibility would add customer value and record the approach here before accepting this exclusion.
  - *Sign-off (Quality Owner or Product Manager):* [Name/Date]

- **Legacy MTC storage-conversion reproduction**
  - *Rationale:* [CNV-83112](https://redhat.atlassian.net/browse/CNV-83112) was closed as Won't Do for the legacy MTC workflow. TS-017 checks the analogous split-storage outcome using the supported Windows live storage conversion workflow.
  - *Sign-off (Quality Owner or Product Manager):* [Name/Date]

**Test Limitations**

- **Source-storage fault injection is restricted to isolated, disposable storage**
  - Qualify a source-volume disconnect or equivalent scoped fault that leaves target storage available through a VM stop and start. Confirm the source is inaccessible and the fresh guest instance can use its saved state from the target.
  - *Sign-off:* [Alvaro Romero](https://github.com/alromeros)/2026-11-25

#### **2. Test Strategy**

**Functional**

- [x] **Functional Testing** — Validates that the feature works according to specified requirements and user stories
  - *Details:* Cover VM clone, native storage relocation, Windows live storage conversion, persistent-state usability, target-volume reference, and source-storage independence. Exercise direct and snapshot clones with captured state from declarative sources on Linux and Windows. Repeat with legacy sources when the build includes the fix in I.2.

- [x] **Automation Testing** — Confirms test automation plan is in place for CI and regression coverage (all tests are expected to be automated)
  - *Details:* Run the existing Tier 1 contracts listed under Regression Testing. Automate Tier 2 Linux workflows and Tier 3 Windows workflows in RedHatQE/openshift-virtualization-tests. Run the DP-tagged cases at Developer Preview and GA. Run the Linux and Windows upgrade cases for GA. Partial-coverage tags identify existing assertions to reuse in the feature-specific cases in III.

- [x] **Regression Testing** — Verifies that new changes do not break existing functionality
  - *Details:* Run these existing SIG Storage checks on the feature build.
    - [KubeVirt VMState adoption](https://github.com/kubevirt/kubevirt/blob/a9a239a1058dbdb0cd75709c6ba3a5b55d62e75b/tests/storage/vmstate.go#L321-L353) starts a second Fedora VM on released storage and reads the saved TPM secret and EFI variable.
    - [KubeVirt missing-source reporting](https://github.com/kubevirt/kubevirt/blob/a9a239a1058dbdb0cd75709c6ba3a5b55d62e75b/tests/storage/vmstate.go#L355-L376) reports the missing PVC when the VM attempts to start.
    - [KubeVirt exclusive-use reporting](https://github.com/kubevirt/kubevirt/blob/a9a239a1058dbdb0cd75709c6ba3a5b55d62e75b/tests/storage/vmstate.go#L378-L414) reports that the PVC is in use when a second VM attempts to start while the first VM holds it.
    - [KubeVirt restore to a new Fedora VM](https://github.com/kubevirt/kubevirt/blob/a9a239a1058dbdb0cd75709c6ba3a5b55d62e75b/tests/storage/vmstate.go#L525-L597) checks saved state and a distinct PVC. TS-001 and TS-002 cover both clone entry points and check the clone's active PVC.
    - [KubeVirt RWO VMState migration](https://github.com/kubevirt/kubevirt/blob/a9a239a1058dbdb0cd75709c6ba3a5b55d62e75b/tests/vm_state_test.go#L134-L188) checks saved TPM and EFI values across migration and restart. TS-009 reuses those assertions for declarative RWO relocation across storage classes. TS-010 checks the new active target PVC.
    - KubeVirt unit tests cover the source-only RWO migratability condition and the VM update that adds the template. TS-013 covers rejection and TS-014 covers successful retry. [Migratability checks](https://github.com/kubevirt/kubevirt/blob/a9a239a1058dbdb0cd75709c6ba3a5b55d62e75b/pkg/virt-handler/vm_test.go#L3032-L3065) · [VM update validation](https://github.com/kubevirt/kubevirt/blob/a9a239a1058dbdb0cd75709c6ba3a5b55d62e75b/pkg/virt-api/webhooks/validating-webhook/admitters/vms-admitter_test.go#L1800-L1808)
    - The [KubeVirt CBT ownership unit test](https://github.com/kubevirt/kubevirt/blob/a9a239a1058dbdb0cd75709c6ba3a5b55d62e75b/pkg/virt-launcher/virtwrap/manager_test.go#L5719-L5731) verifies that a change of VM ownership clears the PVC's previous CBT data. TS-022 verifies that the adopter starts a new backup chain with a full backup.
    - The existing test verifies that a backup remains incremental after the VM moves to another node. Reuse its backup setup and assertions in TS-023 with declarative RWO VMState relocated across storage classes. [Incremental backup after live migration](https://github.com/RedHatQE/openshift-virtualization-tests/blob/7b8e0c0900f66c1d7e9415af60f1cf9126212bda/tests/storage/cbt/test_cbt.py#L389-L439)
    - [Windows vTPM storage migration](https://github.com/RedHatQE/openshift-virtualization-tests/blob/7b8e0c0900f66c1d7e9415af60f1cf9126212bda/tests/storage/storage_migration/test_storage_class_migration.py#L252-L330) checks boot time, guest-file integrity, and disk placement. TS-017 adds active VMState placement. TS-018 verifies continuous guest runtime during declarative RWO VMState conversion.
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
  - *Details:* For GA, relocate VMState on the source build, then retain the same VMs and target PVCs across the supported upgrade. TS-020 and TS-021 verify that the GA build keeps the relocated PVC active and reads its saved guest state. Qualify the builds and workflows in II.3 before execution.

- [x] **Dependencies**
  - *Details:* Legacy-source clones require the [CNV-100645](https://redhat.atlassian.net/browse/CNV-100645) fix in the tested CNV build. Other scenarios can proceed when their entry criteria are met.

- [x] **Cross Integrations**
  - *Details:* SIG Storage covers VMState across clone, snapshot restore, native storage relocation, and Windows live storage conversion. Backup coverage includes a full backup after adoption and incremental backup after relocation.

**Infrastructure**

- [ ] **Cloud Testing** — Does the feature require multi-cloud platform testing? Consider cloud-specific features.
  - *Details:* Not applicable; no cloud-specific behavior is defined. Storage-class compatibility is covered on the standard test platform.

#### **3. Test Environment**

- **Cluster Topology:** Planned three control-plane nodes and three worker nodes, with at least two schedulable workers for live migration.
- **OCP & OpenShift Virtualization Version(s):** Use CNV v5.1.0 for Developer Preview. The GA upgrade candidate is the proposed TP release, CNV v5.2.0, to the proposed GA release, CNV v5.3.0. Before scheduling, the QE owner confirms the actual CNV builds, their supported OCP versions, and the upgrade path in [CNV-79312](https://redhat.atlassian.net/browse/CNV-79312). Use a source build that supports declarative VMState.
- **CPU Virtualization:** VT-x (Intel) or AMD-V enabled
- **Compute Resources:** Minimum per worker node: 8 vCPUs, 32GB RAM
- **Special Hardware:** N/A - no special hardware needed.
- **Storage:** Plan to use ODF classes `ocs-storagecluster-ceph-rbd-virtualization` (source) and `ocs-storagecluster-ceph-rbd` (target) with the `openshift-storage.rbd.csi.ceph.com` provisioner. Qualify both classes for RWO Filesystem VMState, capacity, binding, and live relocation. Confirm that captured-state clone snapshots include VMState. For TS-004 and TS-005, qualify a separate source VMState storage class without snapshot support and confirm that the snapshot is ready with all guest disk PVCs captured and VMState omitted. If the planned pair cannot support both captured-state cloning and relocation, qualify separate pairs and record their names and provisioners before running the affected scenarios.
- **Network:** OVN-Kubernetes, IPv4
- **Required Operators:** For Windows live storage conversion, use an OpenShift Virtualization build with the KubeVirt Migration Operator, its controller, and the storage migration plan API.
- **Platform:** Planned bare-metal OpenShift cluster with ODF. Confirm the lab against the storage and migration requirements in II.4.
- **Special Configurations:** Enable `DeclarativeVMState` on the gated build. Use Fedora and Windows Server 2022 guests with persistent vTPM and EFI, reusing the guest setup in II.2. For RWO relocation, adopt a VMState PVC from the source class and set the target class in the volume claim template. Use a [KubeVirt storage migration plan](https://github.com/kubevirt/kubevirt-migration-controller/blob/main/api/migrationcontroller/v1alpha1/virtualmachinestoragemigrationplan_types.go) to map the Windows guest disks to the target class. Enable BitLocker in the Windows guest for TS-006 and TS-021. [Existing Tier 3 BitLocker setup](https://github.com/RedHatQE/openshift-virtualization-tests/blob/73ff32cd33af8d45f19b46d9cfbcf22d19ef2f0d/tests/virt/node/general/test_windows_vtpm_bitlocker.py#L48-L85)
- **CBT Configurations:** Enable `IncrementalBackup` and VM-level CBT on both source and adopter. Qualify the CBT test disk with a successful incremental backup before the VMState operation. Provision backup destination storage.

#### **3.1. Testing Tools & Frameworks**

- **Test Framework:** Standard
- **CI/CD:** N/A - no specific consideration on CI/CD.
- **Other Tools:** N/A - no specific tools involved.

#### **4. Entry Criteria**

- [x] Requirements and design documents are **approved and merged**
- [ ] The QE owner qualifies the OCP/CNV build for each test milestone, the planned storage classes, guest images, snapshot support, and Windows live conversion with declarative RWO VMState.
- [ ] For legacy-source clone variants only, confirm that the tested build for the milestone includes [CNV-100645](https://redhat.atlassian.net/browse/CNV-100645).
- [ ] For TS-011 only, the QE owner qualifies a disposable setup that keeps the original VMState volume inaccessible and target storage available through a VM stop and start.
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
  - *Shared setup* — For TS-001, TS-002, TS-006, and TS-008, clone declarative sources directly and from snapshots with captured VMState. Repeat both methods from implicit sources to declarative targets when the build includes [CNV-100645](https://redhat.atlassian.net/browse/CNV-100645). TS-003–TS-005 use ready declarative-source snapshots with all guest disk PVCs captured and VMState omitted.
  - *Test Scenario:* **TS-001**: [Tier 2] [PARTIAL_COVERAGE] Verify Linux clones retain saved vTPM and EFI state
    - *Priority:* P0 [DP]
    - *Check* — The booted clone reads the source's saved vTPM-protected data and EFI variable.
  - *Test Scenario:* **TS-002**: [Tier 2] [PARTIAL_COVERAGE] Verify Linux clones report a distinct active VMState PVC
    - *Priority:* P0 [DP]
  - *Test Scenario:* **TS-003**: [Tier 2] Verify rejected Linux clone leaves source VMState usable
    - *Priority:* P1 [DP]
    - *Check* — After the TS-004 rejection, the source still reads its original vTPM and EFI values.
  - *Test Scenario:* **TS-004**: [Tier 2] Verify clone restore rejects uncaptured VMState without a template
    - *Priority:* P1 [DP]
    - *Check* — The restore reports missing VMState and no inherited claim template.
  - *Test Scenario:* **TS-005**: [Tier 2] Verify clone warns and starts fresh when VMState is uncaptured
    - *Priority:* P1 [DP]
    - *Check* — The restore warns about fresh state. The clone boots with a separate PVC from the inherited template and lacks the source's saved vTPM and EFI test values.
  - *Test Scenario:* **TS-006**: [Tier 3] Verify Windows clones unlock BitLocker and retain EFI variables
    - *Priority:* P0 [DP]
    - *Check* — The clone unlocks BitLocker automatically without recovery and reads the saved EFI variable.
  - *Test Scenario:* **TS-007**: [Tier 3] Verify Windows clone writes leave source VMState intact
    - *Priority:* P2
    - *Check* — Changes to the clone's vTPM-protected data and EFI variable leave the source values intact.
  - *Test Scenario:* **TS-008**: [Tier 3] Verify Windows clones report a distinct active VMState PVC
    - *Priority:* P0 [DP]

- **[CNV-98256](https://redhat.atlassian.net/browse/CNV-98256)** — As a VM owner, I want to relocate RWO VMState and keep using saved state on the target.
  - *Shared setup* — Use a declarative RWO source with a claim template for the target storage class. TS-013 starts without the template.
  - *Test Scenario:* **TS-009**: [Tier 2] [PARTIAL_COVERAGE] Verify RWO VMState relocation preserves vTPM and EFI state
    - *Priority:* P0 [DP]
    - *Check* — The guest reads its pre-move vTPM and EFI values.
  - *Test Scenario:* **TS-010**: [Tier 2] Verify native RWO relocation reports the active target VMState PVC
    - *Priority:* P0 [DP]
    - *Check* — VM status names a new active PVC on the target class.
  - *Test Scenario:* **TS-011**: [Tier 2] Verify fresh VM start with the original VMState PVC inaccessible
    - *Priority:* P1 [DP]
    - *Check* — Stop and start the VM while the original PVC remains inaccessible. The new instance uses the same target PVC and reads the pre-migration values.
  - *Test Scenario:* **TS-012**: [Tier 2] Verify failed native relocation leaves source VMState usable
    - *Priority:* P1 [DP]
    - *Check* — Failure before the target becomes active leaves the original PVC active and the saved vTPM and EFI values readable.
  - *Test Scenario:* **TS-013**: [Tier 2] Verify live migration of source-only RWO VMState is rejected
    - *Priority:* P1 [DP]
    - *Check* — The request is rejected and VM status reports `LiveMigratable=False` with reason `VirtualMachineStateNotLiveMigratable` and a message requiring a claim template.
  - *Test Scenario:* **TS-014**: [Tier 2] Verify adding a VMState claim template enables live migration
    - *Priority:* P1 [DP]
    - *Check* — After adding the template and restarting the TS-013 VM, live migration succeeds and VM status reports the active VMState PVC on the target class.

- **[CNV-98256](https://redhat.atlassian.net/browse/CNV-98256)** — As a cluster administrator, I want live storage conversion to move a running Windows VM's guest disks and VMState to target storage.
  - *Shared setup* — Use declarative RWO VMState with the claim template and storage migration plan in II.3.
  - *Test Scenario:* **TS-015**: [Tier 3] Verify Windows live conversion preserves vTPM and EFI state
    - *Priority:* P0 [DP]
    - *Check* — Windows reads the vTPM-protected data and EFI variable saved before conversion.
  - *Test Scenario:* **TS-016**: [Tier 3] Verify failed Windows live conversion preserves original VMState
    - *Priority:* P1 [DP]
    - *Check* — If conversion fails before the target VMState PVC becomes active, the original PVC stays active and Windows can read both saved values.
  - *Test Scenario:* **TS-017**: [Tier 3] [PARTIAL_COVERAGE] Verify Windows live conversion moves guest disks and VMState
    - *Priority:* P0 [DP]
    - *Check* — All guest disk PVCs and the active VMState PVC in VM status use the target class. [CNV-83112 split-storage symptom](https://redhat.atlassian.net/browse/CNV-83112)
  - *Test Scenario:* **TS-018**: [Tier 3] [PARTIAL_COVERAGE] Verify Windows stays running throughout live storage conversion
    - *Priority:* P0 [DP]
    - *Check* — The guest never stops or restarts during conversion, and its boot time is unchanged.

- **[CNV-98256](https://redhat.atlassian.net/browse/CNV-98256)** — As a VM owner, I want to keep using saved vTPM and EFI state when a Windows VM adopts released state storage.
  - *Test Scenario:* **TS-019**: [Tier 3] Verify Windows reads adopted vTPM and EFI state after reboot
    - *Priority:* P1 [DP]
    - *Check* — After reboot, the adopter reads the previous VM's vTPM-protected data and EFI variable from the released PVC.

- **[CNV-79312](https://redhat.atlassian.net/browse/CNV-79312)** — As a cluster administrator, I want to keep using VMs' saved vTPM and EFI state after a supported upgrade.
  - *Shared setup* — For these QE-derived checks, relocate VMState on the qualified source release via native Linux migration or Windows live conversion.
  - *Shared check* — After upgrade, each VM reports the same relocated PVC as active and reads its saved EFI variable.
  - *Test Scenario:* **TS-020**: [Tier 2] Verify Linux retains relocated VMState across upgrade
    - *Priority:* P1
    - *Check* — Linux reads the TPM-protected secret saved before upgrade.
  - *Test Scenario:* **TS-021**: [Tier 3] Verify upgraded Windows unlocks BitLocker using relocated VMState
    - *Priority:* P1
    - *Check* — Windows unlocks the original BitLocker volume using the saved vTPM state.

- **[CNV-98256](https://redhat.atlassian.net/browse/CNV-98256)** — As a backup administrator, I want to continue the same VM's backup chain after storage relocation and start a new chain when a different VM adopts the storage.
  - *Shared setup* — Record the original VM's checkpoint on the CBT test disk before each operation.
  - *Test Scenario:* **TS-022**: [Tier 2] Verify VMState adoption starts a new full backup chain
    - *Priority:* P1
    - *Check* — A different VM adopts the released PVC. On its own tracker, the first completed backup reports Full for the same disk and records a new checkpoint.
  - *Test Scenario:* **TS-023**: [Tier 2] [PARTIAL_COVERAGE] Verify incremental backups continue after same-VM VMState relocation
    - *Priority:* P1
    - *Check* — The same VM reports a new active PVC on the target class. Its next backup uses the original tracker and recorded checkpoint and reports Incremental for the tracked disk.

---

### **IV. Sign-off and Approval**

This plan requires sign-off from at least one person per function.

- Feature Owner: [Alvaro Romero](https://github.com/alromeros)
- Quality Owner: [Dalia Frank](https://github.com/dalia-frank), [Jenia Peimer](https://github.com/jpeimer), [Ruth Netser](https://github.com/rnetser)
- Product Manager: [Peter Lauterbach](https://github.com/peterclauterbach)
