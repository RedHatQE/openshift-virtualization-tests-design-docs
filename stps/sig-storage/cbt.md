# Openshift-virtualization-tests Test plan

## **CBT - Quality Engineering Plan**

### **Metadata & Tracking**

| Field                  | Details                                                                |
|:-----------------------|:-----------------------------------------------------------------------|
| **Enhancement(s)**     | [VEP #25: Storage agnostic incremental backup using qemu (CBT)](https://github.com/kubevirt/enhancements/blob/main/veps/sig-storage/incremental-backup.md) |
| **Feature in Jira**    | [CNV-61530](https://issues.redhat.com/browse/CNV-61530)               |
| **Jira Tracking**      | [CNV-61552](https://redhat.atlassian.net/browse/CNV-61552) |
| **QE Owner(s)**        | Dalia Frank                                                            |
| **Owning SIG**         | sig-storage                                                            |
| **Participating SIGs** | sig-storage                                                            |
| **Current Status**     | Draft                                                                  |

**Document Conventions:**

| Term        | Definition |
|:------------|:-----------|
| **CBT**     | Changed Block Tracking |
| **Push mode** | Backup mode where the hypervisor writes backup data to a user-provided PVC. |
| **Pull mode** | Backup mode where the hypervisor exposes an NBD export and the client pulls backup data. Scratch space on a PVC is used during the backup. In KubeVirt, access is exposed through the **VMExport API**, which adds an HTTP shim layer over the underlying export path. |

### **Feature Overview**

CBT (Changed Block Tracking) enables storage-agnostic incremental backup of VMs using QEMU, saving only changed blocks since the last backup. The main consumers are backup vendors and cluster admins. Backups can run in push mode, where the user provides a filesystem-based PVC to store backup data, or in pull mode, where the user provides a PVC for scratch space and libvirt exposes an NBD export so external components can pull backup data or query the dirty bitmap. In KubeVirt, pull-mode access to that NBD export is further abstracted through an HTTP shim layer using the **VMExport API**.


---

### **I. Motivation and Requirements Review (QE Review Guidelines)**

**Motivation:** Current backup options rely on CSI storage and create a full snapshot with each backup, leading to longer backup times, higher storage use (in-cluster and off-site), and large data transfers when copying off-site. Leveraging QEMU's incremental backup with CBT saves only changes since the last backup, reducing backup time, storage usage, and off-site copy size.

#### **1. Requirement & User Story Review Checklist**

| Check                                  | Done | Details/Notes                                                                                                                                                                           | Comments |
|:---------------------------------------|:-----|:----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:---------|
| **Review Requirements**                | [x]  | Reviewed the relevant requirements.                                                                                                                                                     |          |
| **Understand Value**                   | [x]  | Confirmed clear user stories and understood.  <br/>Understand the difference between U/S and D/S requirements<br/> **What is the value of the feature for RH customers**.               |          |
| **Customer Use Cases**                 | [x]  | Ensured requirements contain relevant **customer use cases**.                                                                                                                           |          |
| **Testability**                        | [x]  | Confirmed requirements are **testable and unambiguous**.                                                                                                                                |          |
| **Acceptance Criteria**                | [x]  | Ensured acceptance criteria are **defined clearly** (clear user stories, D/S requirements clearly defined in Jira).                                                                     |          |
| **Non-Functional Requirements (NFRs)** | [x]  | Confirmed coverage for NFRs, including Performance, Security, Usability, Downtime, Connectivity, Monitoring (alerts/metrics), Scalability, Portability (e.g., cloud support), and Docs. |          |

#### **2. Technology and Design Review**

| Check                            | Done | Details/Notes                                                                                                                                           | Comments |
|:---------------------------------|:-----|:--------------------------------------------------------------------------------------------------------------------------------------------------------|:---------|
| **Developer Handoff/QE Kickoff** | [x]  | A meeting where Dev/Arch walked QE through the design, architecture, and implementation details. **Critical for identifying untestable aspects early.** |          |
| **Technology Challenges**        | [x]  | Identified potential testing challenges related to the underlying technology.                                                                           |          |
| **Test Environment Needs**       | [x]  | Determined necessary **test environment setups and tools**.                                                                                             |          |
| **API Extensions**               | [x]  | Reviewed new or modified APIs and their impact on testing.                                                                                              |          |
| **Topology Considerations**      | [x]  | Evaluated multi-cluster, network topology, and architectural impacts.                                                                                  |          |


### **II. Software Test Plan (STP)**

#### **1. Scope of Testing**

**Testing Goals**

- **[P0]** Verify CBT enable/disable and VM/VMI status.
- **[P0]** Verify push-mode full backup completes and backup integrity can be validated.
- **[P0]** Verify incremental backup with VirtualMachineBackupTracker (full then incremental).
- **[P0]** Verify CBT on OCP 4.22 with HCO feature gate for CBT enabled.
- **[P1]** Verify full and incremental backup with Windows VM.
- **[P1]** Verify ForceFullBackup when tracker has checkpoint.
- **[P1]** Verify behavior when backup PVC is full or insufficient (error returned, no partial backup).
- **[P1]** Verify backup on different StorageClasses with different capabilities (RWO/RWX, block/filesystem).
- **[P1]** Verify pull-mode backup.
- **[P2]** Verify checkpoint redefinition after VM restart. Full backup fallback after crash/corrupted bitmap.
- **[P2]** Verify backup with hotplugged disks.
- **[P2]** Verify incremental backup after migration.
- **[P2]** Verify qcow2 overlay migration with RWO and RWX backend PVCs (bitmap behavior, known libvirt limitation for qcow2 overlay migration with RWO that affects CBT/backup generally).
- **[P2]** Verify migration and backup are mutually exclusive.

**Out of Scope (Testing Scope Exclusions)**

| Out-of-Scope Item                                                    | Rationale              | PM/ Lead Agreement |
|:---------------------------------------------------------------------|:-----------------------|:-------------------|
| Restore as a feature (restore API, restore workflows, restore UX)   | Restore is used only to validate that backup was done properly (backup integrity). We do not test restore as a product feature. | [ ] Name/Date      |
| Offline backup                                                      | Only online backup is supported in initial implementation per VEP.   | [ ] Name/Date      |
| Performance/benchmarking of backup duration or throughput            | This is not a functional requirement for this STP and can be tracked as a separate effort.   | [ ] Name/Date      |

#### **2. Test Strategy**

| Item                           | Description                                                                                                                                                  | Applicable (Y/N or N/A) | Comments |
|:-------------------------------|:-------------------------------------------------------------------------------------------------------------------------------------------------------------|:------------------------|:---------|
| Functional Testing             | Validates that the feature works according to specified requirements and user stories                                                                        | Y                       | Core functional scope aligns with Testing Goals (Section II.1) and scenario traceability (Section III). |
| Automation Testing             | Ensures test cases are automated for continuous integration and regression coverage                                                                          | Y                       | Test cases are expected to be automated for CI and regression coverage. |
| Performance Testing            | Validates feature performance meets requirements (latency, throughput, resource usage)                                                                       | N/A                     | No performance testing is currently planned. It may be added to scope later. |
| Security Testing               | Verifies security requirements, RBAC, authentication, authorization, and vulnerability scanning                                                              | N                       | Not planned as part of scope of testing.                 |
| Usability Testing              | Validates user experience, UI/UX consistency, and accessibility requirements. Does the feature require UI? If so, ensure the UI aligns with the requirements | N/A                     | No end-user UI, feature is API/CR driven (backup vendors, cluster admins). |
| Compatibility Testing          | Ensures feature works across supported platforms, versions, and configurations                                                                               | Y                       | CBT is storage-agnostic. OCP 4.22 with HCO feature gate for CBT enabled. Windows VM. |
| Regression Testing             | Verifies that new changes do not break existing functionality                                                                                               | Y                       | Ensure CBT/backup changes do not break existing backup and VM flows. |
| Upgrade Testing                | Validates upgrade paths from previous versions, data migration, and configuration preservation                                                               | N/A                     | Planned for follow-up, not in scope for initial CBT GA. |
| Backward Compatibility Testing | Ensures feature maintains compatibility with previous API versions and configurations                                                                        | Y                       | Backup CR/API compatibility as applicable. |
| Dependencies                   | Dependent on deliverables from other components/products? Identify what is tested by which team.                                                             | Y                       | OpenShift and CNV (OpenShift Virtualization). Libvirt (CBT/backup, qcow2 overlay migration, see Known Limitations). **VMExport** exposes pull-mode backup NBD endpoints (HTTP shim, see Feature Overview). OCP 4.22. HCO feature gate for CBT enabled. Backup vendor integration out of scope. |
| Cross Integrations             | Does the feature affect other features/require testing by other components? Identify what is tested by which team.                                           | Y                       | Migration and backup mutually exclusive. VMSnapshot interaction per VEP. Pull-mode backup relies on **VMExport** to expose the resulting NBD export path. |
| Monitoring                     | Does the feature require metrics and/or alerts?                                                                                                              | N/A                     | No specific metrics/alerts in scope for this STP. |
| Cloud Testing                  | Does the feature require multi-cloud platform testing? Consider cloud-specific features.                                                                     | N/A                     | Standard OCP platforms, no cloud-specific CBT requirements in scope. |

#### **3. Test Environment**

| Environment Component                         | Configuration | Specification Examples                                                                        |
|:----------------------------------------------|:--------------|:----------------------------------------------------------------------------------------------|
| **Cluster Topology**                          |               | Standard.                                                                                     |
| **OCP & OpenShift Virtualization Version(s)** |               | OCP 4.22 with OpenShift Virtualization (CNV). HCO feature gate for CBT enabled. Ensure libvirt RPMs delivered with 4.22 include relevant CBT features and bug fixes. |
| **CPU Virtualization**                        |               | Standard.                                                                                     |
| **Compute Resources**                         |               | Standard.                                                                                     |
| **Special Hardware**                          |               | Standard.                                                                                     |
| **Storage**                                   |               | Standard. CBT is storage-agnostic. Any StorageClass for VMs and PVCs, sufficient capacity for backup PVCs. |
| **Network**                                   |               | Standard.                                                                                     |
| **Required Operators**                        |               | Standard. OpenShift Virtualization (CNV).                                                     |
| **Platform**                                  |               | Standard.                                                                                     |
| **Special Configurations**                    |               | HCO feature gate for CBT enabled.                                                             |

#### **3.1. Testing Tools & Frameworks**

| Category           | Tools/Frameworks                                                  |
|:-------------------|:------------------------------------------------------------------|
| **Test Framework** |                  |
| **CI/CD**          |                  |
| **Other Tools**    |                  |

#### **4. Entry Criteria**

The following conditions must be met before testing can begin:

- [x] Requirements and design documents are **approved and merged**
- [x] Test environment can be **set up and configured** (see Section II.3 - Test Environment)
- [x] HCO feature gate for CBT enabled

#### **5. Risks**

| Risk Category        | Specific Risk for This Feature                                                                                 | Mitigation Strategy                                                                            | Status |
|:---------------------|:---------------------------------------------------------------------------------------------------------------|:-----------------------------------------------------------------------------------------------|:-------|
| Timeline/Schedule    | Feature code still under development. Testing may be blocked or delayed until implementation stabilizes.       | Start with basic testing (push backup). Prioritize P0 goals. Align with dev milestones. Debug quarantined tests in parallel. | [x]    |
| Test Coverage        | Tier 1 tests run upstream but are quarantined downstream (failing, need debug). Coverage gap until re-enabled. Downstream flakes are tracked in [CNV-78846](https://redhat.atlassian.net/browse/CNV-78846) (faulty disk source resolution in KubeVirt, see [kubevirt/kubevirt#17297](https://github.com/kubevirt/kubevirt/issues/17297)). | Run and maintain tests upstream. Debug downstream failures against CNV-78846 and upstream KubeVirt. Re-enable when stable.             | [x]    |
| Test Environment     | OCP 4.22. HCO feature gate for CBT enabled.                                                                     | Standard CNV test environment.                          | [x]    |
| Untestable Aspects   | None identified.                                                                                               | N/A                                                                                            | [x]    |
| Resource Constraints | Limited QE capacity, feature spans multiple areas (CBT, backup).                                                | Focus on P0 and P1. Automate where possible.                                                   | [x]    |
| Dependencies         | Feature code and API still in progress. Libvirt/QEMU bug requires fix for consistent backup overall and for **qcow2 overlay migration** with **RWO** backend (bitmap behavior). This is a **general CBT/backup** limitation for that storage layout. It is not specific to push vs pull backup mode. | Track dev deliverables. OCP 4.22. Blocked on libvirt/QEMU fix for incremental-after-overlay-migration coverage with RWO. Use RWX or defer scenario until fix. | [x]    |
| Other                | T1 tests quarantined downstream. Current flakes (as of this STP) align with [CNV-78846](https://redhat.atlassian.net/browse/CNV-78846): faulty **disk source resolution in KubeVirt** ([kubevirt/kubevirt#17297](https://github.com/kubevirt/kubevirt/issues/17297)), mostly **not** a Libvirt/QEMU regression. Separately, incremental backup after **qcow2 overlay migration** with **RWO** (bitmap migration) is a **general CBT/backup** risk tracked under libvirt fixes and Known Limitations.   | T1: debug and re-enable against CNV-78846 and KubeVirt upstream. For overlay migration with RWO, use RWX or defer until libvirt fix. Track upstream fixes for both tracks. | [x]    |

#### **6. Known Limitations**

- Testing can start with current scope (e.g. upstream, P0/P1 focus). Not all tests are active yet: Tier 1 tests are quarantined downstream until failures are debugged. Downstream instability is tracked in [CNV-78846](https://redhat.atlassian.net/browse/CNV-78846) and tied to faulty **disk source resolution in KubeVirt** ([kubevirt/kubevirt#17297](https://github.com/kubevirt/kubevirt/issues/17297)), which is **for the most part unrelated** to a Libvirt/QEMU regression.
- Feature code and API are still under development. Testing will start on OCP 4.22 with HCO feature gate for CBT enabled.
- Libvirt/QEMU / libvirt bug (fix pending): **qcow2 overlay migration** with **RWO** backend PVC does not migrate bitmaps as expected. That affects **incremental backup after migration** and related **CBT/backup** behavior for that disk layout. Root cause is overlay migration and bitmap handling with RWO, independent of push vs pull backup mode. Use RWX (or another supported access mode) for overlay migration until fixed. See incremental backup after migration and overlay migration with RWO and RWX backend PVCs in Section III.

---

### **III. Test Scenarios & Traceability**

Scenarios below trace to Jira epic [CNV-61530](https://issues.redhat.com/browse/CNV-61530). Per repo convention, the epic key appears once in **Requirement ID**, and following rows leave that cell empty. Aligned with Testing Goals (Section II.1).

| Requirement ID   | Requirement Summary | Test Scenario(s) | Tier | Priority |
|:-----------------|:--------------------|:------------------|:-----|:---------|
| CNV-61530 (epic) | CBT enable/disable and VM/VMI status | Enable CBT on VM, verify VM/VMI status. Disable CBT, verify behavior and status. | T1 | P0 |
|                  | Push-mode full backup and integrity | Run full backup in push mode to user PVC. Validate backup integrity (e.g. restore verification). | T1 | P0 |
|                  | Incremental backup with VirtualMachineBackupTracker | Create backup tracker, run full backup then incremental backup. Verify only changed blocks. | T1 | P0 |
|                  | Full and incremental backup with Windows VM | Run full then incremental backup for Windows VM. Validate backup and integrity. | T3 | P1 |
|                  | CBT on OCP 4.22 with HCO feature gate | Verify CBT flows on OCP 4.22 with HCO feature gate for CBT enabled. | T2 | P0 |
|                  | ForceFullBackup when tracker has checkpoint | With existing tracker/checkpoint, trigger ForceFullBackup. Verify full backup is produced. | T1 | P1 |
|                  | Backup when PVC is full or insufficient | Use full or too-small backup PVC. Verify error returned and no partial backup. | T1 | P1 |
|                  | Backup on different StorageClasses | Run backup with RWO/RWX and block/filesystem StorageClasses. Verify success and behavior. | T1 | P1 |
|                  | Pull-mode backup | Run backup in pull mode with scratch PVC. Verify completion and integrity using the **VMExport API** (HTTP shim to the underlying NBD export). (Merged for 4.22.) | T2 | P1 |
|                  | Checkpoint redefinition after VM restart, full backup fallback | After VM restart, verify checkpoint redefinition. After crash/corrupted bitmap, verify full backup fallback. Checkpoint behavior after **qcow2 overlay migration** with **RWO** backend requires libvirt fix (tested locally with patch). | T2 | P2 |
|                  | Backup with hotplugged disks | Hotplug one or more disks to a running VM with CBT enabled. Run full then incremental backup. Verify hotplugged disks are included in backup scope and incremental behavior is correct. | T2 | P2 |
|                  | Incremental backup after migration | Migrate the VM (live or cold per test design). After migration completes, run incremental backup against the prior checkpoint/tracker state. Verify incremental backup succeeds and captures post-migration changes. With **RWO** and **qcow2 overlay migration**, align with Known Limitations (bitmap migration bug, prefer RWX until fixed—a **general CBT/backup** constraint for that layout). | T2 | P2 |
|                  | Overlay migration with RWO and RWX backend PVCs | Run **qcow2 overlay migration** with VM disk on RWO backend PVC, and with RWX. Verify bitmap behavior, and document RWO limitation (libvirt bug on overlay migration and bitmaps with **general CBT/backup** impact). | T2 | P2 |
|                  | Migration and backup mutually exclusive | Start backup, attempt migration (or vice versa). Verify they are mutually exclusive. | T1 | P2 |

---

### **IV. Sign-off and Approval**

This Software Test Plan requires approval from the following stakeholders:

* **Reviewers:**
  - [Name / @github-username]
  - [Name / @github-username]
* **Approvers:**
  - [Name / @github-username]
  - [Name / @github-username]
