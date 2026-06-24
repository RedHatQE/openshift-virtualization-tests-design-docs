# Openshift-virtualization-tests Test plan

## **File-Level Restore for Data Protection Partners - Quality Engineering Plan**

### **Metadata & Tracking**

- **Enhancement(s):** [VEP #169: File-Level Restore](https://github.com/kubevirt/enhancements/pull/170)
- **Feature Tracking:** [VIRTSTRAT-480](https://issues.redhat.com/browse/VIRTSTRAT-480)
- **Epic Tracking:**
  - [CNV-67673](https://issues.redhat.com/browse/CNV-67673) R&D: Guest-Assisted File-Level Restore (Closed)
  - [CNV-73895](https://issues.redhat.com/browse/CNV-73895) Dev Preview: File-Level Restore (In Progress)
  - [CNV-89069](https://issues.redhat.com/browse/CNV-89069) TP: File Level Restore (New)
  - [CNV-89094](https://issues.redhat.com/browse/CNV-89094) GA: File Level Restore (New)
  - [CNV-89229](https://issues.redhat.com/browse/CNV-89229) File-Level Restore: API extensions and support encryption (New)
- **Feature Maturity:**
  - DP: 5.0
  - TP: TBD
  - GA: TBD
- **QE Owner(s):** TBD
- **Owning SIG:** sig-storage
- **Participating SIGs:** sig-compute (KubeVirt API, hotplug), sig-network (SSH connectivity)
- **Child STPs:** N/A

### **Feature Overview**

File-Level Restore enables VM administrators and data protection partners to restore specific files or directories from a volume snapshot or backup PVC into a running KubeVirt VM, without requiring a full volume or VM restore. This feature introduces a new Kubernetes operator (vm-file-restore-operator) with a declarative CRD (`VirtualMachineFileRestore`) that manages the entire restore lifecycle through a 9-phase state machine. The operator uses volume hot-plugging to attach backup data and SSH-based guest helpers to execute restore operations inside the VM, supporting both Linux (rsync) and Windows (robocopy) guests. Two restore modes are available: automatic mode (specify files, operator copies and cleans up) and manual mode (operator mounts volume, user browses and copies interactively). The feature is currently in Dev Preview phase (CNV-73895), targeting OpenShift Virtualization 5.0. This STP covers the Dev Preview scope including core functional testing, cross-platform guest support, and security validation.

---

### **I. Motivation and Requirements Review (QE Review Guidelines)**

This section documents the mandatory QE review process. The goal is to understand the feature's value,
technology, and testability before formal test planning.

#### **1. Requirement & User Story Review Checklist**

- [ ] **Review Requirements**
  - *List the key D/S requirements reviewed:*
    - Users can partially restore VM data by selecting specific files or directories from a backup, eliminating the need to restore an entire VM
    - Data protection partners can trigger file-level restore through a declarative KubeVirt API (VirtualMachineFileRestore CRD), providing parity with traditional virtualization platform file-level restore capabilities
    - The restore operator supports both PVC and VolumeSnapshot as data sources, with automatic DataVolume provisioning for snapshot sources
    - Automatic restore mode copies files from source to target location and cleans up temporary resources upon completion
    - Manual restore mode mounts the backup volume read-only for interactive file browsing and user-directed copy operations
    - Linux and Windows guest OS support with auto-detection via VM annotation, QEMU guest agent, or default fallback
    - Security model uses command-restricted SSH keys with a dedicated filerestore user and limited sudo permissions

- [ ] **Understand Value and Customer Use Cases**
  - *Describe the feature's value to customers:* Customers currently must restore an entire VM from backup to retrieve even a single file, which is time-consuming and resource-intensive. File-level restore allows surgical recovery of specific files or directories from volume snapshots or backup PVCs, reducing downtime and storage overhead. This brings KubeVirt to parity with traditional virtualization platform file-level restore capabilities that data protection partners already offer.
  - *List the customer use cases identified:*
    - A VM admin accidentally deletes critical configuration files and needs to restore them from the latest snapshot without downtime
    - A backup vendor integrates file-level restore into their product to offer customers granular recovery from OpenShift Virtualization backups
    - A VM user needs to recover specific application data files from a backup PVC maintained by a data protection partner
    - A VM admin restores files from an encrypted volume (LUKS on Linux, BitLocker on Windows) without exposing the entire backup

- [ ] **Testability**
  - *Note any requirements that are unclear or untestable:*
    - LUKS encrypted volume restore on Linux is mentioned in user stories (CNV-67673) but the current guest helper (filerestore.sh) does not contain explicit LUKS/cryptsetup handling. Testing this scenario requires clarification on whether the guest OS is expected to auto-mount LUKS volumes or whether explicit support will be added.
    - Remote backup source (S3/rclone) is defined in the CRD but currently returns "not supported" error. This is explicitly out of scope for Dev Preview.
    - The Jira requirements table in VIRTSTRAT-480 is empty. Requirements are distributed across child epic descriptions and user stories.

- [ ] **Acceptance Criteria**
  - *List the acceptance criteria:*
    - VirtualMachineFileRestore CR with PVC source restores specified files to target path on a running Linux VM and transitions to Succeeded phase
    - VirtualMachineFileRestore CR with VolumeSnapshot source provisions a temporary DataVolume, restores specified files, cleans up the DataVolume, and transitions to Succeeded phase
    - Manual restore mode (no sourcePath) transitions to VolumeReady with the backup volume mounted read-only at the expected guest path, and cleans up on CR deletion
    - Invalid CR configurations (no source, multiple sources, nonexistent VM, nonexistent PVC, VM not running) are rejected during Init phase with descriptive error messages
    - Temporary resources (hotplugged volumes, DataVolumes) are cleaned up after restore completion, failure, or CR deletion via finalizer
    - Guest OS is correctly auto-detected for Linux and Windows VMs
  - *Note any gaps or missing criteria:*
    - No formal acceptance criteria defined in VIRTSTRAT-480 Jira; the above criteria are derived from user stories in child epics and code analysis
    - No acceptance criteria for performance targets (e.g., restore throughput, timeout thresholds)
    - No acceptance criteria for concurrent restore behavior beyond "reject second restore on same VM"

- [ ] **Non-Functional Requirements (NFRs)**
  - *List applicable NFRs and their targets:*
    - **Security:** SSH connections use ED25519 key authentication with command-restricted authorized_keys; dedicated filerestore user with limited sudo; volumes mounted read-only
    - **Reliability:** Finalizer ensures cleanup on CR deletion; transient error retry with exponential backoff; best-effort cleanup on failure
    - **Monitoring:** Operator exposes controller-runtime reconciliation metrics via TLS-protected metrics endpoint on port 8443
  - *Note any NFRs not covered and why:*
    - **Performance:** No defined targets for restore throughput or maximum file count; not specified in requirements
    - **Scale:** No defined targets for concurrent restore operations across VMs; Dev Preview does not target scale validation
    - **Usability:** No UI component; CLI interaction via kubectl/oc only

#### **2. Known Limitations**

- Backup file browsing is not supported (manual mode provides mount-based access, not a browsing interface)
- Parallel file restores on the same VM are not supported; concurrent restore requests are explicitly rejected
- Remote backup source (S3/rclone) is not yet implemented; the CRD field exists but returns "not supported" error
- Guest helper scripts must be pre-installed on the VM before restore operations can be performed
- SSH connectivity to the VM is required; VMs without SSH access or network connectivity cannot use file-level restore
- IPv6-only environments may have connectivity issues as the IP resolution code does not distinguish between IPv4 and IPv6
- LUKS encrypted volume support on Linux may not work without explicit guest OS configuration for auto-mounting encrypted volumes
- Guest helper setup scripts download from GitHub; air-gapped environments require manual helper script installation

#### **3. Technology and Design Review**

- [ ] **Developer Handoff/QE Kickoff**
  - *Key takeaways and concerns:*
    - The feature introduces a new standalone operator (vm-file-restore-operator) separate from the main KubeVirt codebase
    - The operator uses a 9-phase state machine (New, Init, Hotplugging, WaitingForAttachment, SSHConnecting, Restoring, Cleanup, Succeeded, Failed) plus VolumeReady for manual mode
    - VEP #169 (kubevirt/enhancements#170) documents the upstream design, merged April 2026
    - The operator requires the DeclarativeHotplugVolumes feature gate to be enabled in KubeVirt
    - Two categories of scripts run inside the VM: setup scripts (run once) and restore helper scripts (run per-restore)

- [ ] **Technology Challenges**
  - *List identified challenges:*
    - SSH connectivity from operator pod to VM guest requires network reachability and correctly configured guest SSH
    - Volume hotplug behavior varies by storage provider and CSI driver
    - XFS snapshots require specific mount options (norecovery, nouuid) to avoid UUID collision; this was a bug fixed in PR #11
    - Root disk snapshots can contain partition tables requiring partition detection logic
    - Windows guest helper uses PowerShell and batch polyglot scripting with disk serial number matching
    - PR #11 fixed a command injection vulnerability in SSH argument parsing (eval replaced with read -ra)
    - PR #14 fixed trailing slash normalization to prevent restore failures
  - *Impact on testing approach:* Tests must validate filesystem-specific mount options, partition handling, cross-platform guest helpers, and error recovery for each failure mode. E2E tests require actual VMs with configured SSH and installed guest helpers.

- [ ] **API Extensions**
  - *List new or modified APIs:*
    - New CRD: `VirtualMachineFileRestore` (filerestore.kubevirt.io/v1alpha1)
    - Fields: spec.target (VM reference), spec.source (PVC/Snapshot/Remote union), spec.sourcePath, spec.sourcePartition, spec.targetPath
    - Status: phase (RestorePhase enum), conditions, mountPath, dataVolumeName
    - RBAC: New ClusterRoles for admin/editor/viewer of VirtualMachineFileRestore resources
  - *Testing impact:* All CRD fields and status transitions require test coverage. RBAC roles need permission verification. The API is new (no existing tests to update), so full coverage must be built from scratch.

- [ ] **Test Environment Needs**
  - *See environment requirements in Section II.3 and testing tools in Section II.3.1*

- [ ] **Topology Considerations**
  - *Describe topology requirements:* Standard multi-node OCP cluster with KubeVirt and CDI deployed. The operator runs in its own namespace. SSH connectivity from operator pod to VM guest must be routed through the cluster network (pod network or secondary network).
  - *Impact on test design:* Tests should validate network connectivity paths including default interface, secondary interfaces, and pod IP fallback. Multi-node testing ensures hotplug volume attachment works across nodes.

### **II. Software Test Plan (STP)**

This STP serves as the **overall roadmap for testing**, detailing the scope, approach, resources, and schedule.

#### **1. Scope of Testing**

This STP covers the Dev Preview phase of the File-Level Restore feature for OpenShift Virtualization 5.0. Testing encompasses the VirtualMachineFileRestore CRD lifecycle, automatic and manual restore modes, PVC and VolumeSnapshot data sources, Linux and Windows guest helper scripts, volume hotplug operations, SSH-based guest command execution, guest OS auto-detection, error handling and retry logic, cleanup and finalizer management, concurrent restore prevention, security (RBAC, SSH command restriction), and integration with KubeVirt, CDI, and CSI VolumeSnapshot APIs.

**Testing Goals**

- **[P0]** Validate automatic file restore from PVC source completes successfully on a Linux VM with correct file content, ownership, and permissions restored
- **[P0]** Validate automatic file restore from VolumeSnapshot source provisions DataVolume, restores files, and cleans up temporary resources
- **[P0]** Validate manual restore mode mounts backup volume read-only and transitions to VolumeReady, with cleanup on CR deletion
- **[P0]** Validate invalid CR configurations are rejected during Init phase with descriptive error messages and appropriate status conditions
- **[P1]** Validate file restore works on Windows VMs using the Windows guest helper (robocopy, NTFS)
- **[P1]** Validate guest OS auto-detection correctly identifies Linux and Windows VMs through annotation, guest agent, and fallback strategies
- **[P1]** Validate volume hotplug creates correct SCSI disk configuration and cleanup removes all temporary resources
- **[P1]** Validate SSH connectivity, key management, and command-restricted access prevent unauthorized guest execution
- **[P1]** Validate concurrent restore on the same VM is rejected with clear error messaging
- **[P1]** Validate retry logic for attachment timeout (5 min) and SSH timeout (2 min) with exponential backoff
- **[P1]** Validate cleanup finalizer triggers resource cleanup when CR is deleted during any active phase
- **[P1]** Validate file restore works with ext4 and XFS filesystems using correct mount options
- **[P1]** Validate restore status progresses through phases and reports clear final outcome (Succeeded/Failed)
- **[P2]** Validate file restore from BitLocker-encrypted volumes on Windows VMs
- **[P2]** Validate LUKS-encrypted volume handling on Linux VMs (contingent on implementation)
- **[P2]** Validate restore from volumes with partition tables (root disk snapshots)
- **[P2]** Validate operator metrics endpoint serves reconciliation metrics with TLS authentication

**Out of Scope (Testing Scope Exclusions)**

- Remote backup source restore (S3/rclone): Not implemented in Dev Preview; CRD field exists but returns "not supported" error
- Backup file browsing: Explicitly excluded from feature requirements; manual mode provides mount-based access only
- Parallel file restores on the same VM: Explicitly not supported per feature non-requirements
- HCO integration testing: HCO-compliant operator deployment is a delivery concern; HCO integration will be tested in TP/GA phases
- Operator lifecycle management (leader election, health probes): Generic Kubernetes operator patterns tested by controller-runtime; not KubeVirt-specific
- Air-gapped environment testing: Guest helper setup scripts download from GitHub; air-gapped support requires separate delivery mechanism
- Performance benchmarking: No performance targets defined for Dev Preview; performance testing deferred to TP/GA phases

**Test Limitations**

- Windows VM testing requires Windows guest images with OpenSSH server configured and guest helper scripts pre-installed; availability of licensed Windows images may constrain test execution
- BitLocker testing requires BitLocker-enabled Windows volumes with recovery password; limited by Windows licensing and image preparation
- LUKS testing is contingent on explicit LUKS support being implemented in the Linux guest helper script; current implementation may not handle LUKS volumes
- E2E tests require actual VolumeSnapshot-capable CSI drivers; not all test environments provide snapshot support
- SSH connectivity testing depends on cluster network allowing operator-to-VM communication; restrictive NetworkPolicies may block SSH traffic

#### **2. Test Strategy**

**Functional**

- [x] **Functional Testing** -- Validates that the feature works according to specified requirements and user stories
  - *Details:* Core functional testing covers the VirtualMachineFileRestore CRD lifecycle for both restore modes (automatic and manual) with both data source types (PVC and VolumeSnapshot). Tests validate the 9-phase state machine transitions, guest helper execution on Linux and Windows guests, volume hotplug/unplug operations, error handling at each phase, and cleanup on completion or failure.

- [x] **Automation Testing** -- Confirms test automation plan is in place for CI and regression coverage (all tests are expected to be automated)
  - *Details:* Tier 1 functional tests in Go/Ginkgo for CRD validation, guest OS detection, RBAC, metrics, and hotplug idempotency checks. Tier 2 E2E tests in Python/pytest for complete restore workflows (automatic, manual), guest helper execution, cleanup verification, status progression, multi-filesystem support, and encryption scenarios. Upstream e2e tests (PR #15) provide a foundation; downstream tests will extend coverage with Polarion integration.

- [x] **Regression Testing** -- Verifies that new changes do not break existing functionality
  - *Details:* The vm-file-restore-operator is a new standalone operator with no existing regression surface. Regression testing focuses on ensuring the operator does not interfere with existing KubeVirt volume operations (non-restore hotplug, VM lifecycle, snapshot creation). Integration regression covers CDI DataVolume provisioning and VolumeSnapshot consumption.

**Non-Functional**

- [ ] **Performance Testing** -- Validates feature performance meets requirements (latency, throughput, resource usage)
  - *Details:* N/A for Dev Preview. No performance targets defined. Performance testing planned for TP/GA phases.

- [ ] **Scale Testing** -- Validates feature behavior under increased load and at production-like scale
  - *Details:* N/A for Dev Preview. Scale testing (multiple concurrent restores across different VMs) planned for TP/GA phases.

- [x] **Security Testing** -- Verifies security requirements, RBAC, authentication, authorization, and vulnerability scanning
  - *Details:* Validate RBAC ClusterRoles (admin/editor/viewer) enforce correct permissions on VirtualMachineFileRestore resources. Verify SSH command restriction prevents arbitrary command execution on guest VMs. Verify dedicated filerestore user has limited sudo permissions. Verify volumes are mounted read-only. Verify SSH keypair Secret is not accessible outside the operator namespace.

- [x] **Usability Testing** -- Validates user experience and accessibility requirements
  - *Details:* No UI component. Validate CLI interaction via kubectl/oc for creating, monitoring, and deleting VirtualMachineFileRestore CRs. Verify status conditions provide clear feedback about restore progress and outcome. Verify Kubernetes events are recorded for each phase transition. Verify error messages are descriptive and actionable.

- [x] **Monitoring** -- Does the feature require metrics and/or alerts?
  - *Details:* The operator exposes controller-runtime reconciliation metrics (controller_runtime_reconcile_total) via TLS-protected metrics endpoint on port 8443. Validate metrics are accessible with proper authentication. No custom alerts defined for Dev Preview.

**Integration & Compatibility**

- [x] **Compatibility Testing** -- Ensures feature works across supported platforms, versions, and configurations
  - *Details:* This is a new CRD (v1alpha1) with no backward compatibility concerns. Forward compatibility consideration: the API is alpha and may change in TP/GA. Test with supported storage providers that offer VolumeSnapshot capability.

- [ ] **Upgrade Testing** -- Validates upgrade paths from previous versions, data migration, and configuration preservation
  - *Details:* N/A for Dev Preview. Upgrade testing will be required for TP and GA phases to validate CRD schema migration and in-flight restore handling during operator upgrade.

- [x] **Dependencies** -- Blocked by deliverables from other components/products
  - *Details:*
    - KubeVirt with DeclarativeHotplugVolumes feature gate enabled (required for volume hotplug)
    - CDI (Containerized Data Importer) for DataVolume provisioning from VolumeSnapshots

- [x] **Cross Integrations** -- Does the feature affect other features or require testing by other teams?
  - *Details:* The operator consumes KubeVirt volume hotplug API; changes to hotplug behavior could impact file-level restore. The operator creates CDI DataVolumes; changes to CDI DataVolume lifecycle could impact snapshot-based restores. OADP team may leverage this operator for their file-level restore offerings.

**Infrastructure**

- [ ] **Cloud Testing** -- Does the feature require multi-cloud platform testing?
  - *Details:* N/A for Dev Preview. Cloud testing (AWS, Azure, GCP) planned for TP/GA to validate cloud-specific storage provider compatibility with VolumeSnapshot sources.

#### **3. Test Environment**

- **Cluster Topology:** Multi-node (minimum 2 worker nodes)

- **OCP & OpenShift Virtualization Version(s):** OCP 5.0 / OpenShift Virtualization 5.0

- **CPU Virtualization:** Standard (no specific CPU requirements)

- **Compute Resources:** Minimum 2 worker nodes with 8 vCPUs and 16 GB RAM each (to support VM creation and volume operations)

- **Special Hardware:** None

- **Storage:** CSI-provisioned storage with VolumeSnapshot support (e.g., ocs-storagecluster-ceph-rbd). Block storage mode required for VM disk snapshots. At least one StorageClass supporting both ReadWriteOnce access mode and VolumeSnapshot.

- **Network:** OVN-Kubernetes CNI. SSH connectivity from operator pod to VM guests on port 22. No secondary network requirements for Dev Preview.

- **Required Operators:**
  - OpenShift Virtualization (kubevirt-hyperconverged) with DeclarativeHotplugVolumes feature gate enabled
  - HyperConverged Cluster Operator (hco-operator)
  - CDI (Containerized Data Importer)
  - vm-file-restore-operator (the operator under test)

- **Platform:** Bare-metal or cloud (any platform supporting nested virtualization)

- **Special Configurations:** KubeVirt feature gate `DeclarativeHotplugVolumes` must be enabled in the KubeVirt CR; QEMU guest agent installed in VMs for guest OS detection fallback

#### **3.1. Testing Tools & Frameworks**

- **Test Framework:**
  - Guest helper script tests: BATS (Linux), Pester (Windows)

- **CI/CD:** Standard CI lane with kubevirtci for ephemeral test clusters (cluster-up/cluster-down scripts provided in the operator repo)

- **Other Tools:**
  - virtctl for SSH access to VMs during manual testing
  - kubectl/oc for CR management and status monitoring

#### **4. Entry Criteria**

The following conditions must be met before testing can begin:

- [ ] Requirements and design documents are **approved and merged**
- [ ] Test environment can be **set up and configured** (see Section II.3 - Test Environment)
- [ ] VEP #169 (kubevirt/enhancements#170) is merged and accepted by upstream community
- [ ] VM File Restore Controller basic functionality (CNV-88322) is code-complete and merged
- [ ] Linux guest file restore helper (CNV-88323) is implemented and available
- [ ] DeclarativeHotplugVolumes feature gate is enabled and functional in the target KubeVirt version
- [ ] CDI is deployed and functional for DataVolume provisioning from VolumeSnapshots
- [ ] Guest helper setup scripts are available for Linux VM preparation
- [ ] Downstream container images for vm-file-restore-operator are built and available (CNV-88325)

#### **5. Risks**

**Timeline/Schedule**

- **Risk:** Dev Preview implementation is still in progress (CNV-73895 status: In Progress). Multiple stories are in "New" status (CNV-88323 Linux helper, CNV-88324 Windows helper), which may delay test readiness.
  - **Mitigation:** Begin test development against the current operator implementation (PR #2 merged). Prioritize PVC-source automatic restore tests that exercise the core state machine. Windows tests can be deferred if Windows helper is delayed.
  - *Estimated impact on schedule:* 2-3 sprint delay possible if guest helpers are not available
  - *Sign-off:* TBD

**Test Coverage**

- **Risk:** Unit test coverage for the operator is at 19.7% (identified in PR review). Key areas like phase handlers have limited unit test coverage, increasing the burden on E2E tests to catch regressions.
  - **Mitigation:** Prioritize E2E tests for critical paths (automatic restore, manual restore, cleanup). Advocate for upstream unit test improvements via CNV-90681 (Implement Automation).
  - *Areas with reduced coverage:* Phase handler unit tests, DataVolume provisioning edge cases, error classification logic
  - *Sign-off:* TBD

**Test Environment**

- **Risk:** E2E tests require VolumeSnapshot-capable CSI drivers. Not all test environments provide snapshot support, and snapshot behavior varies by storage provider.
  - **Mitigation:** Use kubevirtci with ocs-storagecluster-ceph-rbd for consistent snapshot support. Document minimum storage provider requirements. Fall back to PVC-source-only testing if snapshots are unavailable.
  - *Missing resources or infrastructure:* Snapshot-capable storage in all CI lanes
  - *Sign-off:* TBD

**Untestable Aspects**

- **Risk:** SSH connectivity from operator to VM depends on cluster network topology. In some network configurations (strict NetworkPolicies, certain CNI plugins), SSH may be blocked, making restore operations untestable.
  - **Mitigation:** Document network requirements. Use kubevirtci which provides a known-good network configuration. Add network connectivity pre-checks to test setup.
  - *Alternative validation approach:* Unit tests with mocked SSH connections for controller logic; E2E tests in controlled kubevirtci environment for actual SSH validation
  - *Sign-off:* TBD

**Resource Constraints**

- **Risk:** Windows VM testing requires licensed Windows guest images with OpenSSH configured and guest helper scripts installed. Image preparation and licensing may be constrained.
  - **Mitigation:** Use community Windows images where available. Prepare a Windows golden image with pre-installed guest helpers. Defer BitLocker testing to TP/GA if Windows images are unavailable.
  - *Current capacity gaps:* Windows guest image availability with OpenSSH and PowerShell
  - *Sign-off:* TBD

**Dependencies**

- **Risk:** The operator depends on the DeclarativeHotplugVolumes KubeVirt feature gate. If this feature gate is renamed, deprecated, or its behavior changes, the operator may break without code changes.
  - **Mitigation:** Track KubeVirt release notes for feature gate changes. Add a pre-test validation step that confirms the feature gate is enabled and functional.
  - *Dependent teams or components:* KubeVirt platform virt team (volume hotplug API), CDI team (DataVolume provisioning), Storage team (CSI VolumeSnapshot)
  - *Sign-off:* TBD

**Other**

- **Risk:** PR review insights identified several code quality concerns: StorageClass lookup silently suppresses errors (incorrect snapshot class selection possible); runSSHCommand has no timeout (e2e tests could hang); temporary token files are never deleted (resource leak); mixed external-snapshotter v4/v6 client usage may cause deserialization issues.
  - **Mitigation:** Include specific test scenarios that exercise these edge cases. Report identified concerns to the development team for remediation before TP phase.
  - *Sign-off:* TBD

---

### **III. Test Scenarios & Traceability**

- **[CNV-73895]** -- As a backup vendor, I want to trigger file-level restore from a backup PVC so that I can offer file-level restore capability to my customers
  - Verify automatic file restore from PVC source completes on a Linux VM: create a running Fedora VM with guest helper installed, create a PVC with test files, create VirtualMachineFileRestore CR with PVC source and sourcePath, verify phase transitions through Init/Hotplugging/WaitingForAttachment/SSHConnecting/Restoring/Cleanup/Succeeded, verify restored files match original content, ownership, and permissions -- **End-to-End, P0**
  - Verify automatic file restore from VolumeSnapshot source completes on a Linux VM: create a running VM with test files, create VolumeSnapshot of boot disk, delete test files, create VirtualMachineFileRestore CR with snapshot source and sourcePath, verify DataVolume is provisioned from snapshot, verify files are restored correctly, verify DataVolume and temporary PVC are cleaned up after completion -- **End-to-End, P0**
  - Verify restore from PVC source with custom targetPath restores files to the specified directory instead of the default location -- **End-to-End, P1**

- **[CNV-73895]** -- As a VM admin/user, I want to restore specific files from a volume snapshot into my running VM using manual mode so that I can browse and selectively copy files
  - Verify manual restore mode (no sourcePath): create VirtualMachineFileRestore CR without sourcePath, verify phase transitions to VolumeReady, verify backup volume is mounted read-only at expected guest path (/backup on Linux, C:\backup on Windows), verify files are accessible from the mounted volume, delete the CR and verify volume is unmounted, unplugged, and temporary resources are removed -- **End-to-End, P0**

- **[CNV-73895]** -- As a VM admin, I want invalid restore configurations to be rejected with clear error messages so that I can fix my request
  - Verify CR with no source (neither PVC nor Snapshot) is rejected during Init phase with descriptive error and Failed status -- **Functional, P0**
  - Verify CR with both PVC and Snapshot sources simultaneously is rejected during Init phase -- **Functional, P1**
  - Verify CR referencing a nonexistent target VM fails with clear error message -- **Functional, P1**
  - Verify CR referencing a nonexistent PVC source fails with clear error message -- **Functional, P1**
  - Verify CR referencing a nonexistent VolumeSnapshot fails with clear error message -- **Functional, P1**
  - Verify CR targeting a VM that is not running (stopped or paused) fails with clear error message -- **Functional, P1**
  - Verify CR referencing a cross-namespace PVC (PVC in different namespace than CR) is rejected with explicit cross-namespace error -- **Functional, P1**

- **[CNV-73895]** -- As a VM admin, I want the file restore operator to correctly detect my VM's guest OS so that the appropriate helper script is used
  - Verify guest OS detection via vm.kubevirt.io/os annotation set to "windows" selects the Windows helper script path and mount path -- **Functional, P1**
  - Verify guest OS detection via vm.kubevirt.io/os annotation set to "linux" selects the Linux helper script path and mount path -- **Functional, P1**
  - Verify guest OS detection via QEMU guest agent GuestOSInfo.Name when annotation is absent -- **Functional, P1**
  - Verify guest OS detection defaults to Linux when both annotation and guest agent info are absent -- **Functional, P1**

- **[CNV-73895]** -- As a VM admin, I want the restore operation to clean up temporary resources after completion or failure so that no orphaned volumes or PVCs remain on my cluster
  - Verify successful restore cleans up hotplugged volume, disk, and DataVolume (for snapshot sources) from VM spec -- **End-to-End, P1**
  - Verify failed restore performs best-effort cleanup of hotplugged volumes and DataVolumes -- **End-to-End, P1**
  - Verify cleanup finalizer triggers resource cleanup when CR is deleted during Hotplugging phase -- **Functional, P1**
  - Verify cleanup finalizer triggers resource cleanup when CR is deleted during WaitingForAttachment phase -- **Functional, P1**
  - Verify cleanup finalizer triggers resource cleanup when CR is deleted during SSHConnecting phase -- **Functional, P1**
  - Verify cleanup finalizer triggers resource cleanup when CR is deleted during VolumeReady phase (manual mode) -- **Functional, P1**
  - Verify volume detachment is confirmed before completing cleanup phase (volume removed from VMI status) -- **Functional, P2**

- **[CNV-73895]** -- As a VM admin, I want the restore operation to recover gracefully from transient errors so that temporary infrastructure issues do not cause permanent failure
  - Verify transient errors during DataVolume provisioning (snapshot source) trigger retry with requeue instead of immediate failure -- **Functional, P1**
  - Verify attachment timeout after 60 retries (5 minutes) transitions to Failed with descriptive error -- **Functional, P1**
  - Verify SSH connection timeout after 24 retries (2 minutes) transitions to Failed with descriptive error -- **Functional, P1**
  - Verify exponential backoff increases delay every 5 retries, capped at 30 seconds -- **Functional, P2**
  - Verify rate limiting prevents rapid reconciliation (minimum 5 seconds between attachment/SSH checks) -- **Functional, P2**

- **[CNV-73895]** -- As a VM admin, I want concurrent restore operations on the same VM to be prevented so that multiple restores do not interfere with each other
  - Verify creating a second VirtualMachineFileRestore CR for a VM with an active restore in progress is rejected with concurrent restore error -- **Functional, P1**

- **[CNV-73895]** -- As a VM admin, I want secure SSH access between the operator and my VM so that restore operations do not expose credentials or allow unauthorized access
  - Verify SSH key pair (ED25519) is generated at operator startup and stored in Secret (private key) and ConfigMap (public key) -- **Functional, P1**
  - Verify SSH connection uses the filerestore user with key-based authentication (no password) -- **End-to-End, P1**
  - Verify SSH command restriction in authorized_keys prevents execution of commands other than the helper script -- **End-to-End, P1**
  - Verify SSH keypair regeneration when Secret exists but ConfigMap is missing (orphan cleanup) -- **Functional, P2**
  - Verify SSH keypair regeneration when ConfigMap exists but Secret is missing (orphan cleanup) -- **Functional, P2**

- **[CNV-73895]** -- As a VM admin, I want to track the progress and outcome of my restore operation through clear status reporting
  - Verify status.phase progresses through New, Init, Hotplugging, WaitingForAttachment, SSHConnecting, Restoring, Cleanup, Succeeded for a successful automatic restore -- **End-to-End, P1**
  - Verify status.phase shows VolumeReady for manual mode after Restoring phase -- **End-to-End, P1**
  - Verify status.conditions include RestoreCompleted condition with appropriate message on success and failure -- **Functional, P1**
  - Verify Kubernetes events are recorded for each phase transition -- **Functional, P2**
  - Verify status.errorMessage contains descriptive error text on failure -- **Functional, P1**
  - Verify startTime is set on first transition from New, and completionTime is set on Succeeded or Failed -- **Functional, P2**

- **[CNV-73895]** -- As a VM admin, I want volume hotplug operations to correctly configure SCSI disks on my VM
  - Verify volume hotplug attaches backup disk with SCSI bus configuration and serial number matching CR name -- **Functional, P1**
  - Verify hotplug is idempotent (calling twice does not create duplicate volumes or disks) -- **Functional, P1**
  - Verify volume unplug removes the backup disk and volume from VM spec -- **Functional, P1**
  - Verify DataVolume is deleted during unplug for snapshot sources, but original PVC is preserved for PVC sources -- **Functional, P1**

- **[CNV-73895]** -- As a VM admin, I want network IP resolution to find the correct VM IP address for SSH connectivity
  - Verify VM IP address is resolved from the default network interface -- **End-to-End, P1**
  - Verify VM IP address falls back to first available interface when default has no IP -- **End-to-End, P2**
  - Verify VM IP address falls back to pod IP when no VM interface has an IP -- **End-to-End, P2**

- **[CNV-73895]** -- As a VM admin, I want file restore to work on Linux VMs with different filesystem types
  - Verify file restore from ext4 filesystem volume mounts with correct options (noload, read-only) -- **End-to-End, P1**
  - Verify file restore from XFS filesystem volume mounts with correct options (norecovery, nouuid, read-only) -- **End-to-End, P1**
  - Verify file restore detects backup disk by SCSI serial number using lsblk on Linux guest -- **End-to-End, P1**
  - Verify file restore handles partitioned backup volumes (root disk snapshots) by finding the correct partition with a filesystem -- **End-to-End, P2**

- **[CNV-88324]** -- As a VM admin, I want file restore to work on Windows VMs
  - Verify file restore on Windows VM: detect offline disk by serial number, bring online, assign drive letter, restore files via robocopy, clean up -- **End-to-End, P1**
  - Verify Windows guest helper creates NTFS junction point for mount path and removes it during cleanup -- **End-to-End, P1**

- **[CNV-73895]** -- As a VM admin, I want restore to handle edge cases gracefully
  - Verify restore handles VM deletion during active restore (WaitingForAttachment or SSHConnecting phase) with graceful cleanup -- **Functional, P2**
  - Verify restore with sourcePath pointing to a nonexistent path on the backup volume fails with descriptive error from guest helper -- **End-to-End, P2**
  - Verify restore file count output parsing handles different helper output formats -- **Functional, P2**

- **[CNV-73895]** -- As a VM admin, I want to restore files from a specific disk partition
  - Verify VirtualMachineFileRestore CR with sourcePartition specified selects the correct partition on the backup volume -- **End-to-End, P1**

- **[CNV-89229]** -- As a Windows VM user, I want to restore files from a BitLocker-encrypted filesystem
  - Verify file restore from BitLocker-encrypted volume on Windows guest: helper detects BitLocker, unlocks with recovery password from lockfile.txt, restores files, re-locks on cleanup -- **End-to-End, P2**

- **[CNV-89229]** -- As a Linux VM user, I want to restore files from a LUKS-encrypted volume
  - Verify file restore from LUKS-encrypted volume on Linux guest (contingent on explicit LUKS support in filerestore.sh) -- **End-to-End, P2**

- **[CNV-73895]** -- As a VM admin, I want the operator to expose metrics for monitoring restore operations
  - Verify metrics service is available at port 8443 with TLS protection -- **Functional, P2**
  - Verify controller_runtime_reconcile_total metric reflects restore operation reconciliation counts -- **Functional, P2**

- **[CNV-73895]** -- As a VM admin, I want RBAC to control who can perform restore operations
  - Verify admin ClusterRole grants full CRUD access to VirtualMachineFileRestore resources -- **Functional, P1**
  - Verify viewer ClusterRole grants read-only access to VirtualMachineFileRestore resources -- **Functional, P1**
  - Verify users without any VirtualMachineFileRestore ClusterRole cannot create or view restore CRs -- **Functional, P1**

- **[CNV-73895]** -- As a backup vendor, I want the restore API to handle remote sources appropriately
  - Verify VirtualMachineFileRestore CR with remote source returns explicit "not yet supported" error during Init phase -- **Functional, P2**

---

### **IV. Sign-off and Approval**

This Software Test Plan requires approval from the following stakeholders:

* **Reviewers:**
  - [TBD / @tbd]
  - [TBD / @tbd]
* **Approvers:**
  - [TBD / @tbd]
  - [TBD / @tbd]
