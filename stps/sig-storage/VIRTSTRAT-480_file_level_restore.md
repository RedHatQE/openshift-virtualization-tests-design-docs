# Openshift-virtualization-tests Test plan

## **File-Level Restore for Data Protection Partners - Quality Engineering Plan**

### **Metadata & Tracking**

- **Enhancement(s):** [VEP #169: File-Level Restore](https://github.com/kubevirt/enhancements/pull/170)
- **Feature Tracking:** [VIRTSTRAT-480](https://issues.redhat.com/browse/VIRTSTRAT-480) - support single file restore for data protection partners
- **Epic Tracking:**
  - [CNV-67673](https://issues.redhat.com/browse/CNV-67673) - R&D: Guest-Assisted File-Level Restore
  - [CNV-73895](https://issues.redhat.com/browse/CNV-73895) - Dev Preview: File-Level Restore
  - [CNV-89069](https://issues.redhat.com/browse/CNV-89069) - TP: File Level Restore
  - [CNV-89094](https://issues.redhat.com/browse/CNV-89094) - GA: File Level Restore
  - [CNV-89229](https://issues.redhat.com/browse/CNV-89229) - File-Level Restore: API extensions and support encryption
- **Feature Maturity:**
  - DP: CNV 5.0.0
  - TP: TBD
  - GA: TBD
- **QE Owner(s):** Emanuele Prella
- **Owning SIG:** sig-storage
- **Participating SIGs:** sig-compute (hotplug integration)
- **Child STPs:** N/A

**Document Conventions (if applicable):** N/A

### **Feature Overview**

File-Level Restore enables VM users and data protection partners to restore specific files or
directories from a backup into a running VM, without requiring a full volume or VM restore. Two
restore modes are available: automatic mode, where the user specifies the files to restore and the
system handles the entire operation including cleanup; and manual mode, where the backup is mounted
read-only for the user to browse and copy files interactively. The feature supports both Linux and
Windows guests with PVC and VolumeSnapshot backup sources. This STP covers the **Dev Preview** phase
targeting CNV 5.0.

---

### **I. Motivation and Requirements Review (QE Review Guidelines)**

This section documents the mandatory QE review process. The goal is to understand the feature's value,
technology, and testability before formal test planning.

#### **1. Requirement & User Story Review Checklist**

- [x] **Review Requirements**
  - *List the key D/S requirements reviewed:*
    - [CNV-73895] Implement file-level restore allowing users and data protection partners to restore specific files/directories from a volume snapshot or backup PVC into a running VM
    - [CNV-88322] VM File Restore Controller with automatic and manual restore modes, guest OS auto-detection
    - [CNV-88323] Linux guest file restore helper (LUKS encryption support deferred to CNV-89229)
    - [CNV-88324] Windows guest file restore helper (BitLocker encryption support deferred to CNV-89229)
    - [CNV-88321] HCO-compliant operator for deploying and managing the file restore controller
    - [CNV-90086] Source volume mode must be set from snapcontent.sourceVolumeMode to avoid CDI clone failures
    - [CNV-84209] LVM-based volume snapshot restore must handle UUID collisions

- [x] **Understand Value and Customer Use Cases**
  - *Describe the feature's value to customers:* VM users regularly need to partially restore information from a VM backup. Currently, restoring a few files requires restoring an entire VM separately, which is time-consuming and resource-intensive. File-level restore provides data protection partners the ability to offer the same capability they have on vSphere today, enabling users to find and restore only the small set of files needed.
  - *List the customer use cases identified:*
    - As a backup vendor, I want to trigger file-level restore from a backup PVC, so I can offer file-level restore capability to my customers
    - As a VM Admin/User, I want to restore specific files or directories from a VolumeSnapshot into my running VM, so I don't have to restore the entire volume or VM
    - As a Linux VM user, I want to restore files on LUKS-encrypted volumes (deferred to CNV-89229)
    - As a Windows VM user, I want to restore files on BitLocker-encrypted file systems (deferred to CNV-89229)

- [x] **Testability**
  - *Note any requirements that are unclear or untestable:*
    - The VIRTSTRAT-480 feature ticket has an empty requirements table (placeholder only). Testable requirements are derived from the child epic CNV-73895 and its implementation stories.
    - Remote storage (S3) restore source is mentioned in VEP design but deferred; no testable requirements exist for Dev Preview.

- [x] **Acceptance Criteria**
  - *List the acceptance criteria:*
    - Data protection partners can restore single files or a subset of user data into a VM
    - Users do not need to restore an entire VM to recover a small set of files
    - Backup vendor can trigger file-level restore from a backup PVC
    - VM Admin/User can restore specific files/directories from a VolumeSnapshot into a running VM without interrupting the VM's availability — the VM remains network-reachable and guest-responsive throughout the restore operation (no reboot, no pause)
    - Guest OS auto-detection correctly identifies Linux vs Windows and selects appropriate restore method
    - Automatic restore mode: user specifies files to restore, system restores them and cleans up all temporary resources
    - Manual restore mode: backup is made available read-only in the guest, user copies files interactively, cleanup occurs when the restore request is removed
  - *Note any gaps or missing criteria:*
    - No formal acceptance criteria defined on VIRTSTRAT-480 itself; criteria derived from child epics and VEP
    - No performance/latency acceptance criteria for restore operations
    - No criteria for maximum file size or number of files per restore operation
    - Encryption support (LUKS on Linux, BitLocker on Windows) deferred to CNV-89229; not an acceptance criterion for Dev Preview

- [x] **Non-Functional Requirements (NFRs)**
  - *List applicable NFRs and their targets:*
    - Security: Restore operations use authenticated, restricted guest access with dedicated user and RBAC roles (admin/editor/viewer)
    - Security: Credentials used for guest access are generated per-operation and cleaned up after completion
    - Security: Guest helper scripts prevent command injection
    - Usability: Clear error reporting through restore status and events
    - UI: No UI changes introduced; feature is API-only. Confirmed with PM that no console integration is planned for Dev Preview.
    - Monitoring/Observability: Operator exposes standard reconciliation metrics via secure endpoint. No custom alerts or feature-specific metrics defined for Dev Preview.
    - Docs: User-facing documentation for the file restore API and guest helper setup will be validated as part of Dev Preview delivery.
  - *Note any NFRs not covered and why:*
    - Performance: No latency/throughput targets defined for Dev Preview
    - Scale: No concurrent restore limits defined beyond "parallel restores of same VM not supported"
    - Portability: No cloud-specific requirements for Dev Preview; will be evaluated for TP/GA

#### **2. Known Limitations**

- **Backup file browsing is not supported; users must know the path of files to restore**
  - *Sign-off:* [TBD]

- **Parallel file restores of the same VM are not supported**
  - *Sign-off:* [TBD]

- **Remote storage (S3) source is not supported in Dev Preview; only PVC and VolumeSnapshot sources**
  - *Sign-off:* [TBD]

- **The `DeclarativeHotplugVolumes` feature gate must be enabled in KubeVirt for the operator to function**
  - *Sign-off:* [TBD]

- **Guest helper script must be pre-installed in the VM; the operator does not install it automatically**
  - *Sign-off:* [TBD]

- **SSH access must be configured on the VM with the `filerestore` user; the operator does not configure guest SSH automatically**
  - *Sign-off:* [TBD]

#### **3. Technology and Design Review**

- [x] **Developer Handoff/QE Kickoff**
  - *Key takeaways and concerns:*
    - Standalone operator (`vm-file-restore-operator`) in kubevirt org, not part of kubevirt/kubevirt core
    - VEP #169 merged on 2026-04-25 after feedback from Backup/DR Vendors
    - State machine with distinct phases: New → Init → Hotplugging → WaitingForAttachment → SSHConnecting → Restoring → Cleanup → Succeeded (with VolumeReady for manual mode, Failed for errors)
    - R&D phase (CNV-67673) is closed; PoC demonstrated; SSH over VSOCK explored but dropped in favor of SSH over network

- [x] **Technology Challenges**
  - *List identified challenges:*
    - Guest helper tool dependencies: some guest OS images may lack required file transfer utilities, requiring test VMs to be pre-configured (flagged in VEP review)
    - XFS snapshot mounting requires special options to avoid filesystem identifier collisions
    - LVM-based volume snapshots have identifier collision issues that need explicit handling
    - Storage mode mismatches between snapshot sources and cluster defaults can cause restore failures, requiring tests across different storage configurations
    - Windows guest connectivity support for guest helper execution
  - *Impact on testing approach:* Tests must cover multiple filesystem types (ext4, XFS), storage backends (Ceph, LVM), and both Linux and Windows guest OS variants. Test VMs must have guest helper scripts pre-installed.

- [x] **API Extensions**
  - *List new or modified APIs:*
    - New file restore API — users create restore requests specifying a target VM, backup source (PVC or VolumeSnapshot), and file paths. Status provides phase tracking and completion information.
  - *Testing impact:* All create, read, update, and delete operations on the file restore API must be tested. Restore phase transitions must be validated. Status must be verified for both success and failure paths.

- [x] **Test Environment Needs**
  - *See environment requirements in Section II.3 and testing tools in Section II.3.1*

- [x] **Topology Considerations**
  - *Describe topology requirements:* Multi-node cluster required for hotplug volume attachment. Cross-namespace PVC restore requires namespace-level RBAC verification.
  - *Impact on test design:* Tests must run on multi-node clusters with VolumeSnapshot support enabled. Cross-namespace tests require additional namespace setup and RBAC configuration.

### **II. Software Test Plan (STP)**

This STP serves as the **overall roadmap for testing**, detailing the scope, approach, resources, and schedule.

#### **1. Scope of Testing**

This STP covers the Dev Preview phase of the File-Level Restore feature for CNV 5.0.
Testing validates automatic and manual restore modes, Linux and Windows guest support, PVC and
VolumeSnapshot source types, error handling and status reporting, resource cleanup, and security
controls (RBAC, authenticated guest access). Integration with volume attachment, storage provisioning,
and operator lifecycle management is validated. Disk encryption support (LUKS/BitLocker) is deferred
to a future release under CNV-89229.

**Testing Goals**

- [P0] Verify a backup vendor can restore files from a backup volume into a running Linux VM with file integrity preserved (size, ownership, permissions)
- [P0] Verify a VM user can restore files from a volume snapshot into a running VM without interrupting the VM's availability
- [P0] Verify manual restore mode provides read-only access to backup contents and the system cleans up when the restore request is removed
- [P0] Verify the system correctly detects whether a VM runs Linux or Windows and selects the appropriate restore method
- [P0] Verify the system reports clear, actionable errors when a restore operation fails at any stage
- [P0] Verify temporary resources created during restore are cleaned up after the operation completes
- [P0] Verify guest connection during restore is authenticated and secure
- [P0] Verify the system rejects invalid restore requests with clear validation errors
- [P0] Verify end-to-end restore workflow from restore request creation to file verification using the file restore API
- [P1] Verify file restore on Linux VM with ext4 and XFS filesystems preserves file content and handles filesystem-specific constraints
- [P1] Verify file restore on Windows VM completes with NTFS metadata preserved
- [P1] Verify the system reports a clear, actionable error when the restore helper is not available in the VM
- [P1] Verify RBAC controls allow and deny restore operations as expected for different roles (admin, editor, viewer)
- [P1] Verify the system reports an informative error when the backup source is invalid or corrupted
- [P1] Verify the system reports an informative error when the target VM is not running or does not exist
- [P1] Verify the system reports error and avoids resource leaks when cleanup of temporary resources fails
- [P1] Verify hotplugged backup volumes are attached read-only so backup data cannot be accidentally modified
- [P1] Verify files are restored from root disk backup to their original location in a running Linux VM
- [P1] Verify sequential restore operations from the same snapshot complete with proper cleanup between each
- [P1] Verify the restore status reflects each phase of the operation so that progress can be monitored
- [P1] Verify temporary resources are cleaned up even when a restore operation fails at any stage
- [P1] Verify the file restore operator deploys and operates correctly as an HCO-managed component
- [P2] Verify cross-namespace restore from a volume in a different namespace completes with proper resource management
- [P2] Verify restore succeeds when the source volume's storage mode differs from the cluster default
- [P2] Verify restore from an LVM-based snapshot handles volume identifier collisions correctly
- [P2] Verify concurrent restore prevention rejects a second simultaneous restore to the same VM
- [P2] Verify paths with formatting variations (trailing slashes, double slashes) are handled correctly during restore on Linux (ext4, XFS) and Windows (NTFS) guests
- [P2] Verify the system handles guest connection loss during file transfer gracefully with partial completion status
- [P2] Verify operator upgrade preserves existing restore resources and their status
- [P2] Verify manual file browsing mode works on a Windows VM with NTFS backup volumes

**Out of Scope (Testing Scope Exclusions)**

The following items are explicitly Out of Scope for this test cycle and represent intentional exclusions.
No verification activities will be performed for these items, and any related issues found will not be classified as defects for this release.

- **Performance/scale testing**
  - *Rationale:* No performance targets defined for Dev Preview; will be addressed in TP/GA phases
  - *PM/Lead Agreement:* [TBD]

- **Disk encryption (LUKS/BitLocker)**
  - *Rationale:* Encryption support (LUKS for Linux, BitLocker for Windows) is tracked under CNV-89229 for a future release; not in scope for Dev Preview
  - *PM/Lead Agreement:* [TBD]

- **ARM64 architecture**
  - *Rationale:* Not in scope for initial Dev Preview validation
  - *PM/Lead Agreement:* [TBD]

- **VSOCK-based guest communication**
  - *Rationale:* Design explored but dropped in favor of SSH over network
  - *PM/Lead Agreement:* [TBD]

**Test Limitations**

- Windows VM testing requires a Windows guest image with SSH support configured; image availability may be limited
  - *Sign-off:* [TBD]

- LVM-based snapshot testing requires LVM-backed storage provisioner in the test cluster
  - *Sign-off:* [TBD]

- Guest helper script installation is a manual prerequisite; automated provisioning is not available from the operator, but instrumentation scripts will be provided to assist with installation.
  - *Sign-off:* [TBD]

#### **2. Test Strategy**

**Functional**

- [x] **Functional Testing** — Validates that the feature works according to specified requirements and user stories
  - *Details:* Comprehensive functional testing covering both automatic and manual restore modes, Linux and Windows guest support, PVC and VolumeSnapshot sources, error scenarios, and resource cleanup. Each restore phase transition is validated.

- [x] **Automation Testing** — Confirms test automation plan is in place for CI and regression coverage (all tests are expected to be automated)
  - *Details:* All Tier 1 functional tests automated in Go/Ginkgo and integrated into CI. Tier 2 end-to-end tests automated in Python/pytest for cross-component workflow validation. Tier 3 specialized tests (Windows guest, resource-intensive multi-VM concurrency) planned for automation when infrastructure is available. Upstream e2e tests already exist in the vm-file-restore-operator repository.

- [x] **Regression Testing** — Verifies that new changes do not break existing functionality
  - *Details:* Regression impact analysis identified 3 critical dependency areas: (1) volume hotplug operations, (2) volume lifecycle state management, (3) storage controller allocation. Existing hotplug, provisioning, and volume management test suites provide regression coverage for these integration points.

**Non-Functional**

- [x] **Performance Testing** — Validates feature performance meets requirements (latency, throughput, resource usage)
  - *Details:* N/A for Dev Preview. No performance targets defined. Will be addressed in TP/GA phases.

- [x] **Scale Testing** — Validates feature behavior under increased load and at production-like scale
  - *Details:* No formal scale targets for Dev Preview. Concurrent restore prevention on the same VM is tested as a functional requirement. Basic multi-VM concurrency (two VMs restoring in parallel) is validated as a Tier 3 scenario to confirm the operator handles independent parallel operations.

- [x] **Security Testing** — Verifies security requirements, RBAC, authentication, authorization, and vulnerability scanning
  - *Details:* Validate RBAC roles (admin/editor/viewer) for file restore operations. Verify guest access is restricted to authorized restore commands only.

- [x] **Usability Testing** — Validates user experience and accessibility requirements
  - *Details:* No UI required per feature specification. Validate that restore status provides clear feedback about operation progress and outcome. Verify error messages are informative when guest helper is missing or guest connection fails.

- [x] **Monitoring** — Does the feature require metrics and/or alerts?
  - *Details:* Operator exposes standard reconciliation metrics via secure endpoint. No custom alerts or feature-specific metrics defined for Dev Preview. Metrics endpoint accessibility will be validated.

**Integration & Compatibility**

- [x] **Compatibility Testing** — Ensures feature works across supported platforms, versions, and configurations
  - *Details:* Validate compatibility with KubeVirt DeclarativeHotplugVolumes feature gate. Verify file restore API backward compatibility.

- [x] **Upgrade Testing** — Validates upgrade paths from previous versions, data migration, and configuration preservation
  - *Details:* Verify operator upgrade preserves existing file restore resources and their status. First release; no prior version to upgrade from, but HCO integration upgrade path must be validated.

- [x] **Dependencies** — Blocked by deliverables from other components/products
  - *Details:* Depends on HCO team to add file restore operator as an HCO-managed component for downstream delivery (CNV-89642). HCO integration includes operator lifecycle management and certificate rotation.

- [x] **Cross Integrations** — Does the feature affect other features or require testing by other teams?
  - *Details:* File restore uses volume hotplug; changes to hotplug admission or lifecycle may affect restore. CDI storage pipeline changes (especially volume mode handling) may affect snapshot-based restore. Backup/DR Vendors will need to validate their integration with the file restore API.

**Infrastructure**

- [ ] **Cloud Testing** — Does the feature require multi-cloud platform testing?
  - *Details:* N/A for Dev Preview. Cloud-specific storage considerations will be evaluated for TP/GA.

#### **3. Test Environment**

- **Cluster Topology:** Multi-node (minimum 2 worker nodes)

- **OCP & CNV Version(s):** OCP 4.23+ / CNV 5.0+

- **CPU Virtualization:** Standard (no specific CPU requirements)

- **Compute Resources:** Default (2 worker nodes with standard VM hosting capacity)

- **Special Hardware:** N/A

- **Storage:** VolumeSnapshot-capable StorageClass required (e.g., ocs-storagecluster-ceph-rbd). LVM-backed storage for UUID collision testing. Block storage mode support required.

- **Network:** Standard OVN-Kubernetes. SSH access from operator pod to guest VMs required (port 22).

- **Required Operators:** OpenShift Virtualization (kubevirt-hyperconverged), HyperConverged Cluster Operator (hco-operator), vm-file-restore-operator (new), CDI (included with OpenShift Virtualization)

- **Platform:** Bare-metal or virtualized (no cloud-specific requirements for Dev Preview)

- **Special Configurations:** DeclarativeHotplugVolumes feature gate must be enabled in KubeVirt CR. Guest VMs must have guest helper scripts installed and SSH configured with filerestore user.

#### **3.1. Testing Tools & Frameworks**

- **Test Framework:**
  - Upstream: Go/Ginkgo e2e tests in kubevirt/vm-file-restore-operator repository using kubevirtci for cluster management.

- **CI/CD:** Standard CI lanes.

- **Other Tools:** BATS (Bash Automated Testing System) for Linux guest helper unit tests. Pester/PowerShell for Windows guest helper unit tests.

#### **4. Entry Criteria**

The following conditions must be met before testing can begin:

- [x] Requirements and design documents are **approved and merged** (VEP #169 merged 2026-04-25)
- [x] Test environment can be **set up and configured** (see Section II.3 - Test Environment)
- [x] vm-file-restore-operator is deployed and operational on test cluster
- [x] DeclarativeHotplugVolumes feature gate is enabled in KubeVirt CR
- [x] Guest helper scripts are available for installation on test VMs (Linux and Windows)
- [x] VolumeSnapshot-capable StorageClass is configured and functional
- [ ] HCO integration for downstream delivery is available (CNV-89642)

#### **5. Risks**

**Timeline/Schedule**

- **Risk:** Dev Preview implementation stories (CNV-88322, CNV-88323, CNV-88324) are still in progress; test automation (CNV-90681) has not started
  - **Mitigation:** Align test development with implementation milestones. Start test framework setup and stub generation in parallel with ongoing development.
  - *Estimated impact on schedule:* Possible delay if implementation stories extend
  - *Sign-off:* TBD

**Test Coverage**

- **Risk:** Windows guest testing may have limited coverage due to image availability and configuration complexity
  - **Mitigation:** Prioritize Linux guest testing for Dev Preview. Establish Windows test VM image with SSH pre-configured.
  - *Areas with reduced coverage:* Windows guest restore
  - *Sign-off:* TBD

**Test Environment**

- **Risk:** LVM-backed storage for UUID collision testing may not be available in standard CI environments
  - **Mitigation:** Use dedicated test environment with LVM provisioner or mock the UUID collision scenario at the operator level.
  - *Missing resources or infrastructure:* LVM storage provisioner in CI
  - *Sign-off:* TBD

**Untestable Aspects**

- **Risk:** Direct integration with third-party Backup/DR Vendors cannot be tested in CI; vendor-specific restore workflows rely on proprietary backup formats
  - **Mitigation:** Test the CRD API surface that vendors integrate with. Validate PVC-based restore path which is the vendor integration point.
  - *Alternative validation approach:* API-level testing with synthetic backup PVCs simulating vendor workflow
  - *Sign-off:* TBD

**Resource Constraints**

- **Risk:** New standalone operator requires QE ramp-up on vm-file-restore-operator codebase, CRD design, and guest helper scripts
  - **Mitigation:** QE spike (CNV-86827) already completed. Leverage upstream e2e tests as reference for downstream test development.
  - *Sign-off:* TBD

**Dependencies**

- **Risk:** Feature depends on KubeVirt DeclarativeHotplugVolumes feature gate and CDI DataVolume pipeline; changes in either could break file restore
  - **Mitigation:** Monitor KubeVirt and CDI upstream for breaking changes. Regression analysis identified 67 non-test references across 3 dependency chains. Include integration regression tests in CI.
  - *Dependent teams or components:* KubeVirt core (hotplug), CDI (DataVolume), HCO (operator lifecycle)
  - *Sign-off:* TBD

**Other**

- **Risk:** VEP review feedback from a Backup/DR Vendor indicated PVC-based restore adds an "unnecessary extra hop" compared to direct guest file API similar to a Virtualization Infrastructure Vendor Guest Operations API. This may lead to API redesign in future phases.
  - **Mitigation:** Dev Preview scope is limited to PVC/VolumeSnapshot sources. Monitor vendor feedback for TP/GA scope adjustments.
  - *Sign-off:* TBD

---

### **III. Test Scenarios & Traceability**

- **[CNV-73895]** — As a backup vendor, I want to trigger file-level restore from a backup PVC into a running VM
  - *Test Scenario:* [Tier 1] Verify files are restored to a running Linux VM from a backup volume with file integrity preserved (size, ownership, permissions)
  - *Priority:* P0

- **[CNV-73895]** — As a VM admin, I want to restore specific files and directories from a volume snapshot into a running VM without disrupting it
  - *Test Scenario:* [Tier 1] Verify files and directories are restored from a volume snapshot without interrupting VM availability (validated via continuous guest accessibility during restore)
  - *Priority:* P0

- **[CNV-88322]** — As a VM admin, I want to use manual restore mode to browse and selectively copy files from backup
  - *Test Scenario:* [Tier 1] Verify backup is made available read-only in the guest, user can copy files interactively, and cleanup occurs when the restore request is removed
  - *Priority:* P0

- **[CNV-88322]** — As a VM user, I want the system to detect my guest OS and select the appropriate restore method automatically
  - *Test Scenario:* [Tier 1] Verify the system detects Linux vs Windows guest and selects the correct restore method
  - *Priority:* P0

- **[CNV-88322]** — As a VM user, I want clear error feedback when a restore fails during volume attachment
  - *Test Scenario:* [Tier 1] Verify a clear error is reported when volume attachment fails during restore
  - *Priority:* P0

- **[CNV-88322]** — As a VM user, I want clear error feedback when a restore fails during guest connection
  - *Test Scenario:* [Tier 1] Verify a clear error is reported when guest connection cannot be established during restore
  - *Priority:* P0

- **[CNV-88322]** — As a VM user, I want clear error feedback when a restore fails during file transfer
  - *Test Scenario:* [Tier 1] Verify a clear error is reported when file transfer fails during restore
  - *Priority:* P0

- **[CNV-88322]** — As a VM admin, I want temporary resources cleaned up after a successful restore
  - *Test Scenario:* [Tier 1] Verify all temporary resources created during restore are automatically cleaned up after successful completion
  - *Priority:* P0

- **[CNV-88322]** — As a VM user, I want the guest connection during restore to be authenticated and secure
  - *Test Scenario:* [Tier 1] Verify the guest connection during restore is authenticated and credentials are cleaned up after completion
  - *Priority:* P0

- **[CNV-88322]** — As a VM user, I want the system to reject invalid restore requests with clear validation errors
  - *Test Scenario:* [Tier 1] Verify the system rejects invalid restore requests with clear error messages
  - *Priority:* P0

- **[VIRTSTRAT-480]** — As a backup vendor, I want a declarative API for file-level restore so that I can integrate it into my backup product
  - *Test Scenario:* [Tier 2] Verify end-to-end restore workflow from restore request creation to file verification using the file restore API
  - *Priority:* P0

- **[CNV-88323]** — As a Linux VM user, I want to restore files on ext4 and XFS filesystems with file integrity
  - *Test Scenario:* [Tier 1] Verify file restore on Linux VM with ext4 filesystem preserves file content, and XFS-based restore handles filesystem-specific constraints
  - *Priority:* P1

- **[CNV-88324]** — As a Windows VM user, I want to restore files from a backup volume on NTFS filesystem
  - *Test Scenario:* [Tier 3] Verify file restore on Windows VM from a backup PVC completes successfully with NTFS metadata and ACLs preserved
  - *Priority:* P1

- **[CNV-88324]** — As a Windows VM user, I want to restore files from a volume snapshot on NTFS filesystem
  - *Test Scenario:* [Tier 3] Verify file restore on Windows VM from a volume snapshot completes successfully with NTFS metadata and ACLs preserved
  - *Priority:* P1

- **[CNV-88322]** — As a VM user, I want an informative error when restore is attempted on a VM without the restore helper installed
  - *Test Scenario:* [Tier 1] Verify the system reports a clear, actionable error message when the restore helper is not found in the VM
  - *Priority:* P1

- **[CNV-88322]** — As a cluster admin, I want RBAC controls to allow and deny restore operations for different roles
  - *Test Scenario:* [Tier 1] Verify admin role can create/delete restores, editor role can create restores, viewer role can only read restores, and unauthorized users are denied
  - *Priority:* P1

- **[CNV-88322]** — As a VM user, I want a clear error when the backup source is invalid or corrupted
  - *Test Scenario:* [Tier 1] Verify the system reports an informative error when the backup volume is empty, contains corrupted data, or the specified source path does not exist
  - *Priority:* P1

- **[CNV-88322]** — As a VM user, I want a clear error when restore is attempted on a VM that is not running or does not exist
  - *Test Scenario:* [Tier 1] Verify the system reports an informative error when file restore is attempted on a stopped, migrating, or non-existent VM
  - *Priority:* P1

- **[CNV-88322]** — As a VM admin, I want the system to handle cleanup failures gracefully and avoid resource leaks
  - *Test Scenario:* [Tier 1] Verify the system reports an error and does not leave orphaned resources when cleanup of temporary volumes fails after restore
  - *Priority:* P1

- **[CNV-73895]** — As a VM admin, I want hotplugged backup volumes to be attached read-only so that backup data cannot be accidentally modified
  - *Test Scenario:* [Tier 1] Verify hotplugged volume is mounted read-only in the guest
  - *Priority:* P1

- **[CNV-73895]** — As a VM user, I want to automatically restore a deleted file from a root disk backup to its original location so that I can recover lost data without a full disk restore
  - *Test Scenario:* [Tier 2] Verify files are restored from root disk backup (VolumeSnapshot and PVC) to their original location in a running Linux VM
  - *Priority:* P1

- **[CNV-73895]** — As a VM user, I want to restore multiple files sequentially from the same data disk snapshot so that I can verify the operator cleans up between operations
  - *Test Scenario:* [Tier 2] Verify sequential restore operations from the same snapshot complete with proper cleanup between each
  - *Priority:* P1

- **[CNV-73895]** — As a VM admin, I want the restore status to clearly reflect each phase of the operation so that I can monitor progress
  - *Test Scenario:* [Tier 1] Verify restore status progresses through expected phases during a successful restore operation
  - *Priority:* P1

- **[CNV-73895]** — As a VM admin, I want temporary volumes to be cleaned up even when a restore fails so that resources are not leaked
  - *Test Scenario:* [Tier 1] Verify cleanup occurs and restore transitions to Failed status when restore encounters an error mid-operation
  - *Priority:* P1

- **[CNV-88321]** — As a cluster admin, I want the file restore operator to be managed by HCO so that it follows the standard operator lifecycle
  - *Test Scenario:* [Tier 2] Verify the operator deploys and operates correctly under HCO management with proper certificate rotation and TLS configuration
  - *Priority:* P1

- **[CNV-73895]** — As a VM admin, I want to restore files from a backup volume in a different namespace
  - *Test Scenario:* [Tier 2] Verify restore from a volume in a different namespace completes successfully with proper resource management and cleanup
  - *Priority:* P2

- **[CNV-90086]** — As a VM user, I want restore to succeed when the source volume's storage mode differs from the cluster default
  - *Test Scenario:* [Tier 2] Verify restore from a volume snapshot completes successfully when the source volume's storage mode differs from the cluster default
  - *Priority:* P2

- **[CNV-84209]** — As a VM user, I want restore from LVM-based snapshots to handle volume identifier collisions correctly
  - *Test Scenario:* [Tier 2] Verify restore from LVM-based snapshot mounts successfully despite identifier collision with the original volume
  - *Priority:* P2

- **[CNV-88322]** — As a VM user, I want the system to prevent concurrent restores to the same VM
  - *Test Scenario:* [Tier 1] Verify a second file restore request targeting the same VM is rejected with a clear error while a restore is in progress
  - *Priority:* P2

- **[VIRTSTRAT-480]** — As a backup vendor, I want to browse backup files on a Windows VM in manual mode so that I can selectively restore Windows files
  - *Test Scenario:* [Tier 3] Verify manual file browsing from backup volume works on a Windows VM with NTFS filesystem
  - *Priority:* P2

- **[CNV-88322]** — As a VM user, I want paths with formatting variations to be normalized correctly before restore
  - *Test Scenario:* [Tier 1] Verify restore handles source and target paths with trailing slashes, double slashes, or relative components correctly
  - *Priority:* P2

- **[CNV-88322]** — As a VM user, I want the system to handle guest connection loss during file transfer gracefully
  - *Test Scenario:* [Tier 2] Verify the system reports partial completion status and allows retry when the guest connection is interrupted during file transfer
  - *Priority:* P2

- **[CNV-88322]** — As a cluster admin, I want operator upgrade to preserve existing restore resources and their status
  - *Test Scenario:* [Tier 2] Verify operator upgrade preserves existing restore resources and their status without manual intervention
  - *Priority:* P2

- **[CNV-84209]** — As a VM user, I want to restore files from an LVM-based volume snapshot of the root disk so that I can recover data even when UUID collisions exist
  - *Test Scenario:* [Tier 2] Verify restore succeeds from root disk snapshot with XFS filesystem
  - *Priority:* P2

- **[CNV-73895]** — As a VM admin, I want the operator to handle rate limiting when polling for volume attachment and SSH connectivity so that the API server is not overloaded
  - *Test Scenario:* [Tier 1] Verify the operator completes restore operations without triggering API server rate-limiting or excessive retry errors
  - *Priority:* P2

- **[CNV-73895]** — As a VM user, I want to manually browse files from a root disk backup so that I can inspect and selectively restore specific files
  - *Test Scenario:* [Tier 2] Verify manual file browsing from root disk backup (VolumeSnapshot and PVC) in VolumeReady mode
  - *Priority:* P2

- **[CNV-73895]** — As a VM user, I want to restore a large file (1GB) from a data disk snapshot so that I can verify the operator handles big transfers reliably
  - *Test Scenario:* [Tier 2] Verify restore of a large file (1GB) from data disk snapshot completes successfully
  - *Priority:* P2

- **[CNV-73895]** — As a VM user, I want to restore files on two different VMs concurrently so that I can verify the operator handles parallel operations across VMs
  - *Test Scenario:* [Tier 3] Verify concurrent file restore operations on different VMs complete independently and successfully
  - *Priority:* P2

---

### **IV. Sign-off and Approval**

This Software Test Plan requires approval from the following stakeholders:

* **Reviewers:**
  - Development Representative (OCP-V): [Arnon Gilboa](@arnongilboa), [Noam Assouline](@noamasu)
  - QE Members (OCP-V): [Dalia Frank](@dafrank), [Kateryna Shvaika](@kshvaika), [Jose Manuel Castano](@josemacassan), [Ahmad Hafe](@Ahmad-Hafe), [Jenia Peimer](@jpeimer)
* **Approvers:**
  - QE Architect (OCP-V): [Ruth Netser](@rnetser)
  - QE Member (OCP-V): [Jenia Peimer](@jpeimer)
  - PM: [Peter Lauterbach](@peterclauterbach)
