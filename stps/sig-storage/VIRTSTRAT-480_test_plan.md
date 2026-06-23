# Openshift-virtualization-tests Test plan

## **VM File-Level Restore for Data Protection Partners - Quality Engineering Plan**

### **Metadata & Tracking**

- **Enhancement(s):** [VEP #169: File-Level Restore](https://github.com/kubevirt/enhancements/pull/170)
- **Feature Tracking:** [VIRTSTRAT-480](https://redhat.atlassian.net/browse/VIRTSTRAT-480) - support single file restore for data protection partners
- **Epic Tracking:** [CNV-73895](https://redhat.atlassian.net/browse/CNV-73895) - Dev Preview: File-Level Restore
- **Feature Maturity:**

  - DP: 4.23
  - TP: TBD ([CNV-89069](https://redhat.atlassian.net/browse/CNV-89069))
  - GA: TBD ([CNV-89094](https://redhat.atlassian.net/browse/CNV-89094))
- **QE Owner(s):** TBD
- **Owning SIG:** sig-storage (Storage Ecosystem)
- **Participating SIGs:** N/A

**Document Conventions (if applicable):** N/A

### **Feature Overview**

VM File-Level Restore is a new capability delivered through a standalone Kubernetes operator (`vm-file-restore-operator`) in the kubevirt organization. It enables data protection partners and cluster administrators to restore individual files from VolumeSnapshots or PVCs to running KubeVirt VMs without requiring a full VM restart. The operator uses KubeVirt hotplug technology to attach snapshot volumes to the target VM, then employs SSH-based helper scripts to copy files from the snapshot back to the VM's disk. Two restore modes are supported: automatic mode (operator handles the full restore lifecycle via rsync) and manual mode (operator hotplugs the volume and the user copies files manually). The feature introduces a new `VirtualMachineFileRestore` CRD (`filerestore.kubevirt.io/v1alpha1`) with a 9-phase state machine and supports both Linux (ext3/ext4, XFS) and Windows (NTFS, BitLocker) guest operating systems. This STP covers the Dev Preview scope targeting CNV 4.23.

---

### **I. Motivation and Requirements Review (QE Review Guidelines)**

This section documents the mandatory QE review process. The goal is to understand the feature's value,
technology, and testability before formal test planning.

#### **1. Requirement & User Story Review Checklist**

- [x] **Review Requirements**
  - *List the key D/S requirements reviewed:*
    - [CNV-88322](https://redhat.atlassian.net/browse/CNV-88322) - VM File Restore Controller basic functionality: CRD definition, 9-phase state machine, hotplug-based volume attachment, SSH-based file copy, cleanup on CR deletion
    - [CNV-88323](https://redhat.atlassian.net/browse/CNV-88323) - Linux guest file restore helper: ext3/ext4 and XFS filesystem support, UUID collision handling with `norecovery,nouuid` mount options, rsync-based file copy
    - [CNV-88324](https://redhat.atlassian.net/browse/CNV-88324) - Windows guest file restore helper: NTFS support, BitLocker volume unlock with recovery password, disk offline during cleanup
    - [CNV-88321](https://redhat.atlassian.net/browse/CNV-88321) - HCO-compliant operator managing the file restore controller
    - [CNV-90086](https://redhat.atlassian.net/browse/CNV-90086) - Set source volume mode from snapcontent.sourceVolumeMode for DataVolume creation

- [x] **Understand Value and Customer Use Cases**
  - *Describe the feature's value to customers:* Data protection partners currently must restore an entire VM to recover a small set of files, which is time-consuming and resource-intensive. File-Level Restore allows selective file/directory recovery from backups without VM downtime, matching the capability already available on vSphere. This enables backup vendors to offer granular restore services on OpenShift Virtualization.
  - *List the customer use cases identified:*
    - Restore accidentally deleted files from a point-in-time snapshot to a running VM
    - Data protection partner integration for granular restore workflows
    - Manual browsing of backup volumes mounted to a running VM for selective file recovery

- [x] **Testability**
  - *Note any requirements that are unclear or untestable:*
    - Remote source restore (S3/rclone) is defined in the CRD but returns "not yet supported" -- not testable in Dev Preview
    - SSH over VSOCK is not yet implemented; testing limited to SSH over TCP (port 22)
    - LUKS encryption is mentioned in Jira acceptance criteria but not implemented in current Linux guest helper

- [x] **Acceptance Criteria**
  - *List the acceptance criteria:*
    - VirtualMachineFileRestore CR triggers automatic file restore from VolumeSnapshot to running VM
    - Manual mode mounts backup volume at specified path for user-driven file copy
    - Guest OS (Linux/Windows) is auto-detected and appropriate helper scripts are used
    - XFS filesystems are handled with UUID collision avoidance (norecovery,nouuid mount options)
    - Windows BitLocker volumes are unlocked using recovery password before mounting
    - Concurrent restore of the same VM is rejected with clear error
    - Cleanup runs on CR deletion: SSH cleanup command, volume unplug, DataVolume deletion, finalizer removal
    - PVC source is hotplugged directly without creating a DataVolume
    - DataVolume inherits StorageProfile from VolumeSnapshot StorageClass
  - *Note any gaps or missing criteria:*
    - LUKS encryption is mentioned in Jira acceptance criteria but not implemented in current Linux guest helper
    - No explicit performance criteria defined (e.g., maximum restore time for a given file size)

- [x] **Non-Functional Requirements (NFRs)**
  - *List applicable NFRs and their targets:*
    - **Security:** SSH key command restriction prevents arbitrary command execution via filerestore user; shell injection prevention in SSH argument parsing (fixed in PR #11)
    - **Security:** Dedicated filerestore user with ED25519 keypair and command-restricted authorized_keys
    - **Usability:** Clear status conditions on the VirtualMachineFileRestore CR reporting phase transitions and errors
  - *Note any NFRs not covered and why:*
    - **Performance:** No explicit performance targets defined for Dev Preview
    - **Scalability:** Not applicable for Dev Preview scope
    - **Monitoring:** No metrics or alerts defined for Dev Preview

#### **2. Known Limitations**

The limitations are documented to ensure alignment between development, QA, and product teams.
The following are confirmed product constraints accepted before testing begins.

- SSH over VSOCK is not implemented; SSH connectivity requires TCP port 22 access to the guest
- LUKS encryption support is not implemented in the current Linux guest helper despite being mentioned in acceptance criteria
- Remote source restore (S3/rclone) is defined in the CRD but the controller returns "not yet supported"
- Backup file browsing is explicitly out of scope per R&D epic [CNV-67673](https://redhat.atlassian.net/browse/CNV-67673)
- Parallel file restores targeting the same VM are not supported; concurrent restore is rejected
- HCO integration for deployment and packaging is not in scope; the operator is standalone

#### **3. Technology and Design Review**

- [ ] **Developer Handoff/QE Kickoff**
  - *Key takeaways and concerns:* TBD -- handoff meeting to be scheduled with development team

- [x] **Technology Challenges**
  - *List identified challenges:*
    - SSH connectivity to guest VMs requires SSH daemon enabled and accessible on port 22
    - rsync and required binaries must be present in the guest OS image
    - XFS UUID collision when mounting snapshot of the boot disk requires special mount options (norecovery,nouuid)
    - Windows BitLocker unlock requires recovery password availability
    - Hard-coded timeouts in the operator may need adjustment for different environments and storage backends
    - Command injection prevention in SSH argument parsing (security fix in PR #11)
  - *Impact on testing approach:* Tests must use VM images with SSH enabled and rsync installed. XFS-specific tests need VMs with XFS-formatted boot disks. Windows tests require BitLocker-configured guests with known recovery passwords. Test timeouts must account for operator retry behavior.

- [x] **API Extensions**
  - *List new or modified APIs:*
    - New CRD: `VirtualMachineFileRestore` (filerestore.kubevirt.io/v1alpha1), namespace-scoped, shortNames: vmfr/vmfrestore
    - 9-phase status: New, Init, Hotplugging, WaitingForAttachment, SSHConnecting, Restoring, Cleanup, Succeeded (with VolumeReady for manual mode, Failed for errors)
  - *Testing impact:* All phase transitions must be validated. CR lifecycle (create, status watch, delete with finalizer cleanup) must be tested. No existing APIs are modified.

- [ ] **Test Environment Needs**
  - *See environment requirements in Section II.3 and testing tools in Section II.3.1*

- [x] **Topology Considerations**
  - *Describe topology requirements:* Standard multi-node cluster topology. No multi-cluster or special network topology requirements.
  - *Impact on test design:* VM scheduling and hotplug operations require worker nodes with available storage. No topology-specific test design needed.

### **II. Software Test Plan (STP)**

This STP serves as the **overall roadmap for testing**, detailing the scope, approach, resources, and schedule.

#### **1. Scope of Testing**

Testing covers the VirtualMachineFileRestore CRD and its controller lifecycle, including automatic and manual restore modes, PVC and VolumeSnapshot sources, guest OS detection and platform-specific helper scripts (Linux and Windows), SSH keypair management, concurrent restore rejection, volume hotplug coexistence, and cleanup behavior. Testing spans both functional validation (Tier 1, Go/Ginkgo) and end-to-end workflows (Tier 2, Python/pytest) to ensure the operator integrates correctly with KubeVirt hotplug, CDI DataVolumes, CSI VolumeSnapshots, and guest SSH connectivity.

**Testing Goals**

- **[P0]** Validate the complete automatic file restore lifecycle: VolumeSnapshot source, hotplug, SSH connection, file copy via rsync, cleanup, and CR status transitions through all 9 phases
- **[P0]** Validate manual restore mode: hotplug, VolumeReady phase, read-only backup volume accessibility, cleanup on CR deletion
- **[P0]** Validate PVC-based restore source (direct hotplug without DataVolume creation)
- **[P1]** Validate guest OS auto-detection (Linux/Windows) and correct helper script selection
- **[P1]** Validate concurrent restore rejection with clear error reporting
- **[P1]** Validate XFS UUID collision handling with norecovery,nouuid mount options
- **[P1]** Validate cleanup behavior: temporary resources are removed and restore operation completes cleanly on CR deletion
- **[P1]** Validate volume hotplug coexistence with existing hotplugged disks
- **[P1]** Validate DataVolume StorageProfile inheritance from VolumeSnapshot StorageClass
- **[P1]** Validate standard KubeVirt hotplug is not affected when file-restore-operator is installed
- **[P2]** Validate SSH connection timeout and retry behavior
- **[P2]** Validate volume attachment timeout and Failed state transition
- **[P2]** Validate cross-namespace PVC rejection
- **[P2]** Validate Windows BitLocker volume unlock workflow
- **[P2]** Validate SSH key command restriction security (prevent arbitrary command execution)
- **[P2]** Validate operator SSH keypair lifecycle and recovery from incomplete state

**Out of Scope (Testing Scope Exclusions)**

The following items are explicitly Out of Scope for this test cycle and represent intentional exclusions.
No verification activities will be performed for these items, and any related issues found will not be classified as defects for this release.

- Remote source restore (S3/rclone) -- not yet supported (see Known Limitations I.2)
- SSH over VSOCK -- not yet implemented (see Known Limitations I.2)
- LUKS encryption support -- not implemented in current helper (see Known Limitations I.2)
- Backup file browsing -- explicitly out of scope per R&D epic [CNV-67673](https://redhat.atlassian.net/browse/CNV-67673)
- HCO integration and lifecycle management -- operator is standalone for Dev Preview
- Performance benchmarking -- no performance targets defined for Dev Preview
- Scale testing with large numbers of concurrent restores across different VMs
- Multi-cluster or federated restore scenarios

**Test Limitations**

- Windows guest testing with BitLocker requires guest images with BitLocker configured and known recovery passwords; availability of such images in CI may be limited
- Guest images must have SSH enabled and rsync installed; standard CI images may need customization
- Hard-coded operator timeouts may cause test flakiness in resource-constrained CI environments
- XFS-specific tests require VMs with XFS-formatted boot disks, which may not be the default in all CI environments

#### **2. Test Strategy**

**Functional**

- [x] **Functional Testing** -- Validates that the feature works according to specified requirements and user stories
  - *Details:* Core functional coverage across automatic restore, manual restore, PVC source, VolumeSnapshot source, guest OS detection, concurrent restore rejection, cleanup lifecycle, and cross-platform (Linux/Windows) helper script behavior. 10 Tier 1 scenarios cover controller and helper behavior; 6 Tier 2 scenarios cover error handling, security, and Windows integration.

- [x] **Automation Testing** -- Confirms test automation plan is in place for CI and regression coverage (all tests are expected to be automated)
  - *Details:* All Tier 1 tests implemented in Go/Ginkgo within the vm-file-restore-operator repository. Tier 2 tests implemented in Python/pytest in the CNV downstream test repository. Upstream e2e tests already exist in the operator repo for automatic and manual modes. Existing e2e framework from PR #15 provides helper functions for VM creation, snapshot creation, VMFR CR management, and SSH command execution.

- [x] **Regression Testing** -- Verifies that new changes do not break existing functionality
  - *Details:* File-restore-operator consumes KubeVirt hotplug, CDI DataVolume, and CSI VolumeSnapshot APIs. Regression coverage ensures standard hotplug operations, snapshot creation/restore, and VM lifecycle are not affected by the operator's RBAC roles or volume patching behavior. Dedicated scenario validates standard hotplug non-interference.

**Non-Functional**

- [ ] **Performance Testing** -- Validates feature performance meets requirements (latency, throughput, resource usage)
  - *Details:* N/A for Dev Preview. No explicit performance targets defined.

- [ ] **Scale Testing** -- Validates feature behavior under increased load and at production-like scale
  - *Details:* N/A for Dev Preview. Single-VM restore only; concurrent restore of the same VM is explicitly rejected.

- [x] **Security Testing** -- Verifies security requirements, RBAC, authentication, authorization, and vulnerability scanning
  - *Details:* Validate SSH key command restriction to prevent arbitrary command execution via the filerestore user. Validate SSH_ORIGINAL_COMMAND validation rejects non-filerestore commands. Validate command injection prevention in SSH argument parsing (addressed in PR #11).

- [x] **Usability Testing** -- Validates user experience and accessibility requirements
  - *Details:* No UI component. Validate that VirtualMachineFileRestore CR status conditions provide clear feedback about operation phase, errors, and completion. Validate that error messages for rejected operations (concurrent restore, cross-namespace PVC) are descriptive and actionable.

- [ ] **Monitoring** -- Does the feature require metrics and/or alerts?
  - *Details:* N/A for Dev Preview. No metrics or alerts defined.

**Integration & Compatibility**

- [x] **Compatibility Testing** -- Ensures feature works across supported platforms, versions, and configurations
  - *Details:* New CRD (v1alpha1) with no backward compatibility concerns. Validate compatibility with OCP 4.22+ and CNV 4.23. Validate compatibility with multiple storage backends that support CSI VolumeSnapshots.

- [ ] **Upgrade Testing** -- Validates upgrade paths from previous versions, data migration, and configuration preservation
  - *Details:* N/A for Dev Preview. No previous version exists.

- [x] **Dependencies** -- Blocked by deliverables from other components/products. Identify what we need from other teams before we can test.
  - *Details:* DeclarativeHotplugVolumes feature gate must remain enabled in KubeVirt (KubeVirt team). Downstream container images and operator packaging require completion of [CNV-89642](https://redhat.atlassian.net/browse/CNV-89642) (Release Engineering). All required platform APIs (hotplug, CDI, CSI VolumeSnapshot) are available in CNV 4.22+.

- [x] **Cross Integrations** -- Does the feature affect other features or require testing by other teams? Identify the impact we cause.
  - *Details:* The operator adds RBAC roles for VM spec patching (hotplug) which could theoretically interact with other controllers that patch VM specs. Regression test validates standard hotplug is unaffected. 5 impacted integration features identified: Hot-plug (Disk), Storage (CDI DataVolume), Snapshots, VM Lifecycle, and Networking (SSH IP discovery).

**Infrastructure**

- [ ] **Cloud Testing** -- Does the feature require multi-cloud platform testing? Consider cloud-specific features.
  - *Details:* N/A. Feature is platform-agnostic; requires only CSI VolumeSnapshot support from the storage provider.

#### **3. Test Environment**

- **Cluster Topology:** Multi-node (minimum 2 worker nodes)

- **OCP & OpenShift Virtualization Version(s):** OCP 4.22+ / CNV 4.23 (Dev Preview)

- **CPU Virtualization:** Standard (no specific CPU requirements)

- **Compute Resources:** Default (2+ worker nodes with sufficient resources for VM workloads)

- **Special Hardware:** None

- **Storage:** CSI-compatible StorageClass with VolumeSnapshot support (e.g., ocs-storagecluster-ceph-rbd)

- **Network:** Standard OVN-Kubernetes; SSH access (TCP port 22) to guest VMs required

- **Required Operators:** OpenShift Virtualization (openshift-cnv), vm-file-restore-operator (standalone deployment)

- **Platform:** Any supported OCP platform (bare-metal, AWS, Azure, GCP)

- **Special Configurations:** Guest VM images with SSH enabled and rsync installed; for Windows tests: Windows guest with BitLocker configured

#### **3.1. Testing Tools & Frameworks**

- **Test Framework:** Standard (openshift-python-wrapper for Tier 2)

- **CI/CD:** Standard CNV CI lanes; upstream operator CI (kubevirtci-based e2e in vm-file-restore-operator repo)

- **Other Tools:** None

#### **4. Entry Criteria**

The following conditions must be met before testing can begin:

- [ ] Requirements and design documents are **approved and merged**
- [ ] Test environment can be **set up and configured** (see Section II.3 - Test Environment)
- [ ] VEP #169 is merged and upstream implementation is available
- [ ] vm-file-restore-operator is deployable on the target cluster
- [ ] Guest VM images with SSH enabled and rsync installed are available in CI

#### **5. Risks**

**Timeline/Schedule**

- **Risk:** Feature is Dev Preview for CNV 4.23; development may still be in progress during test development (CNV-88322 and CNV-88321 are In Progress, CNV-88323 and CNV-88324 are New)
  - **Mitigation:** Align test development with story completion milestones; prioritize P1 scenarios first. Begin test development using upstream operator deployment while stories are finalized.
  - *Estimated impact on schedule:* 1-2 sprint delay possible if key stories (CNV-88322, CNV-88323) are not code-complete on time
  - *Sign-off:* TBD

**Test Coverage**

- **Risk:** Windows BitLocker testing (CNV-88324) requires specialized guest images that may not be readily available in CI
  - **Mitigation:** Prioritize Linux guest testing. Windows BitLocker scenario is classified as P2; can be deferred if Windows environment is unavailable.
  - *Areas with reduced coverage:* Windows guest file restore helper (CNV-88324)
  - *Sign-off:* TBD

**Test Environment**

- **Risk:** Custom VM images with SSH and rsync pre-installed may not be available in all CI lanes at the time testing begins, potentially requiring image build work before test execution
  - **Mitigation:** Use Fedora-based images with cloud-init to install required packages; maintain a verified image list for CI. Begin image preparation early in the test development cycle.
  - *Missing resources or infrastructure:* Verified CI images with SSH and rsync
  - *Sign-off:* TBD

**Untestable Aspects**

- **Risk:** Remote source restore (S3/rclone) is defined in the CRD but not implemented; cannot validate API contract correctness
  - **Mitigation:** Verify the controller returns a clear "not yet supported" error when RemoteSource is specified
  - *Alternative validation approach:* Negative test validating error message for unsupported source type
  - *Sign-off:* TBD

**Resource Constraints**

- **Risk:** N/A
  - **Mitigation:** N/A
  - *Current capacity gaps:* N/A
  - *Sign-off:* N/A

**Dependencies**

- **Risk:** VolumeSnapshotClass configuration varies across CI environments; test setup may need environment-specific StorageClass selection logic
  - **Mitigation:** Ensure CI clusters use OCS/Ceph-RBD or equivalent storage with VolumeSnapshot support; implement StorageClass discovery in test setup to select snapshot-capable storage dynamically
  - *Dependent teams or components:* Storage team (CSI driver), CDI team (DataVolume provisioning)
  - *Sign-off:* TBD

**Other**

- **Risk:** Hard-coded timeouts in the operator (SSH connection, volume attachment) may cause test flakiness in resource-constrained CI environments
  - **Mitigation:** Use generous test-level timeouts that account for operator retry behavior; report flaky tests for operator timeout tuning
  - *Sign-off:* TBD

---

### **III. Test Scenarios & Traceability**

#### Tier 1 -- Functional Tests (Go/Ginkgo)

- **[CNV-88322](https://redhat.atlassian.net/browse/CNV-88322)** -- As a VM admin, restore specific files from a backup snapshot to a running VM using automatic or manual mode
  - Automatic file restore from VolumeSnapshot: Create Fedora VM with test data, snapshot boot disk, delete test data, create VMFR CR with sourcePath, verify data restored with correct ownership and permissions. **P0**
  - Manual restore mode: Create VMFR CR without sourcePath (manual mode), verify transitions to VolumeReady, backup volume mounted read-only at mount path, files accessible, CR deletion triggers cleanup. **P0**
  - PVC-based restore source (no snapshot): Create PVC with backup data, create VMFR referencing PVC source, verify PVC hotplugged directly (no DataVolume creation), files restored, PVC unplugged on cleanup. **P0**
  - Volume hotplug coexistence: While VM has existing hotplugged data disk, create VMFR for same VM, verify restore volume added correctly alongside existing hotplugged volume, cleanup only removes restore volume. **P1**
  - Concurrent restore rejection: Create VMFR, wait for active phase, create second VMFR targeting same VM, verify second VMFR fails with error about restore in progress. **P1**
  - Guest OS auto-detection: Create VMs with different OS detection signals (annotation, GuestOSInfo, default), verify correct OS type returned and correct mount paths/helper scripts used. **P1**
  - Cleanup on CR deletion: Start restore, wait for Restoring phase, delete CR, verify finalizer cleanup runs SSH cleanup command, unplugs volume, deletes DataVolume, removes finalizer. **P1**
  - Standard hotplug non-interference: Run standard KubeVirt hotplug add/remove on VM with file-restore-operator installed, verify standard hotplug unaffected by operator's RBAC or volume patching. **P1**

- **[CNV-90086](https://redhat.atlassian.net/browse/CNV-90086)** -- As a VM admin, rely on correct volume mode inheritance when restoring from VolumeSnapshots with non-default storage profiles
  - DataVolume StorageProfile inheritance: Create VolumeSnapshot of PVC with specific StorageClass, create VMFR, verify DataVolume created with StorageSpec (not explicit size/volumeMode), inherits from StorageProfile. **P1**

- **[CNV-88323](https://redhat.atlassian.net/browse/CNV-88323)** -- As a Linux VM user, restore files from ext3/ext4 or XFS backup volumes including those with UUID collisions
  - Linux XFS UUID collision handling: Create VM with XFS boot disk, snapshot, restore files, verify guest helper uses ro,norecovery,nouuid mount options for XFS. **P1**

#### Tier 2 -- End-to-End Tests (Python/pytest)

- **[CNV-88322](https://redhat.atlassian.net/browse/CNV-88322)** -- As a VM admin, restore specific files from a backup snapshot to a running VM using automatic or manual mode
  - SSH connection retry and timeout: Create VMFR targeting VM where SSH not yet available, verify operator retries with exponential backoff, eventually times out, transitions to Failed with error message. **P2**
  - Volume attachment timeout: Create VMFR with snapshot resulting in slow DataVolume provisioning, verify operator times out after max retries and transitions to Failed. **P2**
  - Cross-namespace PVC rejection: Create VMFR where PVC source namespace differs from VM namespace, verify rejection with clear error message. **P2**
  - SSH key command restriction: Attempt arbitrary commands via filerestore SSH user, verify command= restriction and SSH_ORIGINAL_COMMAND validation reject non-filerestore commands. **P2**
  - Operator SSH keypair provisioning: Verify EnsureSSHKeypair creates Secret and ConfigMap on startup, handles orphaned resources (Secret without ConfigMap), retries on transient failures. **P2**

- **[CNV-88324](https://redhat.atlassian.net/browse/CNV-88324)** -- As a Windows VM user, restore files from NTFS backup volumes including BitLocker-encrypted disks
  - Windows BitLocker volume unlock: On Windows VM with BitLocker, verify helper unlocks volume using recovery password before mounting and properly sets disk offline during cleanup. **P2**

---

### **IV. Sign-off and Approval**

This Software Test Plan requires approval from the following stakeholders:

* **Reviewers:**
  - [TBD / @tbd]
  - [TBD / @tbd]
* **Approvers:**
  - [TBD / @tbd]
  - [TBD / @tbd]
