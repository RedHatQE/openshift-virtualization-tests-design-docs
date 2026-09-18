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
| **Pull mode** | Backup mode where the hypervisor exposes an NBD export and the client pulls backup data. Scratch space on a PVC is used during the backup. |

### **Feature Overview**

CBT (Changed Block Tracking) enables storage-agnostic incremental backup of VMs, saving only changed blocks since the last backup. The main consumers are backup vendors and cluster admins. Backups can run in push mode, where the user provides a PVC to store backup data, or in pull mode, where the user provides a PVC for scratch space and backup data is exposed via an export endpoint that external backup tools can connect to and pull data from.


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

- **[P0]** As a cluster admin, I want to enable changed-block tracking on a VM so that incremental backups are available.
- **[P0]** As a cluster admin, I want to perform a full backup in push mode and validate its integrity.
- **[P0]** As a cluster admin, I want to perform incremental backups that save only changed blocks since the last backup.
- **[P0]** As a cluster admin, I want CBT functionality to be available when the feature gate is enabled.
- **[P1]** As a cluster admin, I want to perform full and incremental backups with Windows VMs.
- **[P1]** As a backup admin, I want to force a full backup even after previous backups.
- **[P1]** As a cluster admin, I want to receive an error when backup storage is full or insufficient so that no partial backup is created.
- **[P1]** As a cluster admin, I want to perform backups on different storage types.
- **[P1]** As a backup vendor, I want to perform backups in pull mode so that I can control where backup data is stored.
- **[P1]** As a cluster admin, I want pull-mode backups to be secure.
- **[P1]** As a cluster admin, I want to run concurrent backups on different VMs without errors or corruption.
- **[P2]** As a cluster admin, I want backups to recover correctly after VM restart or failures.
- **[P2]** As a cluster admin, I want to back up hotplugged disks so that all VM storage is protected.
- **[P2]** As a cluster admin, I want to perform incremental backups after migration to minimize backup storage and time.
- **[P2]** As a cluster admin, I want migration to preserve backup checkpoints.
- **[P2]** As a cluster admin, I want backup and migration operations to be mutually exclusive to ensure data integrity.

**Out of Scope (Testing Scope Exclusions)**

| Out-of-Scope Item                                                    | Rationale              | PM/ Lead Agreement |
|:---------------------------------------------------------------------|:-----------------------|:-------------------|
| Performance/benchmarking of backup duration or throughput            | This is not a functional requirement for this STP and can be tracked as a separate effort.   | [x] Peter Lauterbach / May 7, 2026 |

#### **2. Test Strategy**

| Item                           | Description                                                                                                                                                  | Applicable (Y/N or N/A) | Comments |
|:-------------------------------|:-------------------------------------------------------------------------------------------------------------------------------------------------------------|:------------------------|:---------|
| Functional Testing             | Validates that the feature works according to specified requirements and user stories                                                                        | Y                       | Core functional scope aligns with Testing Goals (Section II.1) and scenario traceability (Section III). |
| Automation Testing             | Ensures test cases are automated for continuous integration and regression coverage                                                                          | Y                       | Test cases are expected to be automated for CI and regression coverage. |
| Performance Testing            | Validates feature performance meets requirements (latency, throughput, resource usage)                                                                       | N/A                     | No performance testing is currently planned. It may be added to scope later. |
| Security Testing               | Verifies security requirements, RBAC, authentication, authorization, and vulnerability scanning                                                              | Y                       | Pull-mode backup internal tunnel security (virt-exportserver to virt-launcher transport requires client certificates). |
| Usability Testing              | Validates user experience, UI/UX consistency, and accessibility requirements. Does the feature require UI? If so, ensure the UI aligns with the requirements | N/A                     | No end-user UI, feature is API/CR driven (backup vendors, cluster admins). |
| Compatibility Testing          | Ensures feature works across supported platforms, versions, and configurations                                                                               | Y                       | CBT is storage-agnostic. OCP 4.22 with HCO feature gate for CBT enabled. Windows VM. |
| Regression Testing             | Verifies that new changes do not break existing functionality                                                                                               | Y                       | Ensure CBT/backup changes do not break existing backup and VM flows. |
| Upgrade Testing                | Validates upgrade paths from previous versions, data migration, and configuration preservation                                                               | N/A                     | Planned for follow-up, not in scope for initial CBT GA. |
| Backward Compatibility Testing | Ensures feature maintains compatibility with previous API versions and configurations                                                                        | Y                       | Backup CR/API compatibility as applicable. |
| Dependencies                   | Dependent on deliverables from other components/products? Identify what is tested by which team.                                                             | Y                       | OpenShift and CNV (OpenShift Virtualization). Libvirt (CBT/backup, qcow2 overlay migration). **VMExport** exposes pull-mode backup NBD endpoints (HTTP shim, see Feature Overview). OCP 4.22. HCO feature gate for CBT enabled. Backup vendor integration out of scope. |
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
| Dependencies         | Feature code and API still in progress. Libvirt includes fixes for **qcow2 overlay migration** with **RWO** backend (bitmap behavior) for consistent CBT/backup functionality. | Track dev deliverables. OCP 4.22. Ensure libvirt RPMs include qcow2 overlay migration bitmap fixes. | [x]    |
| Other                | T1 tests quarantined downstream. Current flakes (as of this STP) align with [CNV-78846](https://redhat.atlassian.net/browse/CNV-78846): faulty **disk source resolution in KubeVirt** ([kubevirt/kubevirt#17297](https://github.com/kubevirt/kubevirt/issues/17297)), mostly **not** a Libvirt/QEMU regression.   | T1: debug and re-enable against CNV-78846 and KubeVirt upstream. | [x]    |

#### **6. Known Limitations**

The limitations are documented to ensure alignment between development, QA, and product teams.
The following are confirmed product constraints accepted before testing begins.

| Known Limitation                                                    | Rationale/Details              | PM/ Lead Agreement |
|:--------------------------------------------------------------------|:-------------------------------|:-------------------|
| Restore as a feature is not supported                               | There is no restore API, restore workflows, or restore UX. Restore is used only to validate that backup was done properly (backup integrity), not as a product feature. | [x] Peter Lauterbach / May 7, 2026 |
| Offline backup is not supported                                     | Only online backup is supported in initial implementation per VEP.   | [x] Peter Lauterbach / May 7, 2026 |

---

### **III. Test Scenarios & Traceability**

Scenarios below trace to Jira epic [CNV-61530](https://issues.redhat.com/browse/CNV-61530). Per repo convention, the epic key appears once in **Requirement ID**, and following rows leave that cell empty. Aligned with Testing Goals (Section II.1).

| Requirement ID   | Requirement Summary | Test Scenario(s) | Tier | Priority |
|:-----------------|:--------------------|:------------------|:-----|:---------|
| CNV-61530 (epic) | As a cluster admin, I want to enable changed-block tracking on a VM so that incremental backups are available | Enable CBT on a VM, confirm status reflects the change. Disable CBT, confirm status updates and backup behavior adjusts. | T1 | P0 |
|                  | As a cluster admin, I want to perform a full backup in push mode and validate its integrity | Run a full backup in push mode to a PVC. Validate backup integrity. | T1 | P0 |
|                  | As a cluster admin, I want to perform incremental backups that save only changed blocks since the last backup | Create a backup tracker, run a full backup then an incremental backup. Confirm only changed blocks are saved. | T1 | P0 |
|                  | As a cluster admin, I want CBT functionality to be available when the feature gate is enabled | Perform CBT operations on OCP 4.22 with the HCO feature gate for CBT enabled. Confirm functionality works as expected. | T2 | P0 |
|                  | As a cluster admin, I want to perform full and incremental backups with Windows VMs | Run a full backup followed by an incremental backup for a Windows VM. Validate backup and integrity. | T3 | P1 |
|                  | As a backup admin, I want to force a full backup even after previous backups | With an existing tracker and checkpoint, trigger a forced full backup. Confirm a full backup is produced. | T1 | P1 |
|                  | As a cluster admin, I want to receive an error when backup storage is full or insufficient so that no partial backup is created | Use a full or too-small backup PVC. Confirm an error is returned and no partial backup exists. | T1 | P1 |
|                  | As a cluster admin, I want to perform backups on different storage types | Run backups with different StorageClasses (RWO/RWX, block/filesystem). Confirm successful completion. | T1 | P1 |
|                  | As a backup vendor, I want to perform backups in pull mode so that I can control where backup data is stored | Run a backup in pull mode with a scratch PVC. Confirm the backup completes and integrity can be validated by pulling data from the exposed endpoint. | T2 | P1 |
|                  | As a cluster admin, I want pull-mode backups to be secure | Confirm that the internal transport requires client certificates. Attempt HTTP CONNECT without a certificate and verify it fails. Only authenticated connections should succeed. | T1 | P1 |
|                  | As a cluster admin, I want to run concurrent backups on different VMs without errors or corruption | Run 5-10 simultaneous backups on different VMs (mix of full and incremental). Confirm all complete successfully without errors or corruption. | T2 | P1 |
|                  | As a cluster admin, I want backups to recover correctly after VM restart or failures | After VM restart, confirm checkpoints are redefined. After a crash or corrupted bitmap, confirm a full backup fallback occurs. Verify checkpoint behavior after migration with RWO and RWX backend PVCs. | T2 | P2 |
|                  | As a cluster admin, I want to back up hotplugged disks so that all VM storage is protected | Hotplug one or more disks to a running VM with CBT enabled. Run a full backup then an incremental backup. Confirm hotplugged disks are included and incremental behavior is correct. | T2 | P2 |
|                  | As a cluster admin, I want to perform incremental backups after migration to minimize backup storage and time | Migrate a VM. After migration completes, run an incremental backup. Confirm the incremental backup succeeds and captures post-migration changes with both RWO and RWX backend PVCs. | T2 | P2 |
|                  | As a cluster admin, I want migration to preserve backup checkpoints | Perform migration with VM disks on RWO backend PVC, and with RWX. Confirm bitmap behavior and proper bitmap preservation for both access modes. | T2 | P2 |
|                  | As a cluster admin, I want backup and migration operations to be mutually exclusive to ensure data integrity | Start a backup and attempt migration (or vice versa). Confirm they are mutually exclusive. | T1 | P2 |

---

### **IV. Sign-off and Approval**

This Software Test Plan requires approval from the following stakeholders:

* **Reviewers:**
  - Development Representative (OCP-V): [Adi Aloni](@Acedus), [Alvaro Romero](@alromeros)
  - QE Members (OCP-V): [Emanuele Prella](@ema-aka-young), [Kateryna Shvaika](@kshvaika), [Jose Manuel Castano](@josemacassan), [Ahmad Hafe](@Ahmad-Hafe), [Jenia Peimer](@jpeimer)
* **Approvers:**
  - QE Architect (OCP-V): [Ruth Netser](@rnetser)
  - QE Member (OCP-V): [Jenia Peimer](@jpeimer)
