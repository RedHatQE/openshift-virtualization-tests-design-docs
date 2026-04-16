# Software Test plan

## **Allow Workload Disruption Migration - Quality Engineering Plan**

### **Metadata & Tracking**

| Field                  | Details                                          |
|:-----------------------|:-------------------------------------------------|
| **Enhancement(s)**     | [kubevirt/kubevirt#11833](https://github.com/kubevirt/kubevirt/pull/11833) |
| **Feature in Jira**    | https://redhat.atlassian.net/browse/VIRTSTRAT-244                                             |
| **Jira Tracking**      | https://redhat.atlassian.net/browse/CNV-54933                                             |
| **QE Owner(s)**        | Samuel Alberstein (@SamAlber)                    |
| **Owning SIG**         | sig-virt                                         |
| **Participating SIGs** | sig-virt                                         |
| **Current Status**     | Draft                                            |

**Document Conventions:**
- AWD: Allow Workload Disruption — a MigrationPolicy flag that permits the migration engine to stun/pause a VM to complete migration when precopy alone cannot converge.
- PostCopy: Migration mode where remaining memory pages are fetched on-demand from the source after the VM starts on the target node.
- Paused: Migration mode where the VM is stunned (paused) to allow the final dirty pages to transfer, then resumed on the target node.

### **Feature Overview**

When a VM is live-migrated, the migration may fail to converge if the guest dirties memory faster than the
migration bandwidth can transfer it. With the Allow Workload Disruption (AWD) migration policy, the platform
is permitted to use disruptive migration modes (PostCopy or Paused) to guarantee the migration completes.
This is critical for operations that require migration — such as node drain and CPU/memory hotplug — where
a failed migration would block the operation entirely. When PostCopy is allowed, the migration switches to
PostCopy mode; otherwise, the VM is stunned, migrated in Paused mode, and resumed on the target node.

---

### **I. Motivation and Requirements Review (QE Review Guidelines)**

#### **1. Requirement & User Story Review Checklist**

| Check                                  | Done | Details/Notes                                                                                                                                                                                                                                                                                | Comments |
|:---------------------------------------|:-----|:---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:---------|
| **Review Requirements**                | [x]  | AWD migration policy enables disruptive migration modes when precopy cannot converge within the configured completion timeout. When PostCopy is allowed, the migration switches to PostCopy mode. Otherwise, the VM is stunned, migrated in Paused mode, and resumed on the target node. |          |
| **Understand Value**                   | [x]  | Customers running latency-sensitive or memory-intensive workloads need guaranteed migration completion for maintenance operations (node drain, hotplug) without losing in-guest processes.                                                                                                    |          |
| **Customer Use Cases**                 | [x]  | 1. Admin drains a node for maintenance; VMs with AWD policy migrate using PostCopy or Paused mode and resume without process loss.<br>2. Admin hotplugs CPU/memory to a running VM; the resulting migration uses AWD mode and the guest reflects the new resources without process loss.      |          |
| **Testability**                        | [x]  | Testable by configuring an AWD migration policy with a tight completion timeout and capped bandwidth, then verifying the migration mode and guest process PID after migration.                                                                                                                 |          |
| **Acceptance Criteria**                | [x]  | 1. Migration completes in the expected mode (PostCopy or Paused) under AWD policy.<br>2. Guest background process PID is preserved after migration.<br>3. Hotplugged CPU/memory is reflected in the guest OS after AWD migration.<br>4. Both RHEL and Windows guests are supported.          |          |
| **Non-Functional Requirements (NFRs)** | [x]  | No UI component. No new metrics or alerts. No performance targets defined. Security (RBAC) covered by core KubeVirt tests. Documentation covered by KubeVirt user-guide.                                                                                                                     |          |

#### **2. Known Limitations**

- s390x does not support maxGuest memory, so memory hotplug is not available on this architecture.

#### **3. Technology and Design Review**

| Check                            | Done | Details/Notes                                                                                                                                                   | Comments |
|:---------------------------------|:-----|:----------------------------------------------------------------------------------------------------------------------------------------------------------------|:---------|
| **Developer Handoff/QE Kickoff** | [x]  | Feature reviewed through KubeVirt enhancement and design discussions.                                                                                           |          |
| **Technology Challenges**        | [x]  | Triggering Paused mode reliably requires tuning bandwidth, completion timeout, and guest disk load to ensure precopy does not converge before the timeout.       |          |
| **Test Environment Needs**       | [x]  | Standard OCP-V bare metal deployment with RWX default storage class. Windows tests require special infrastructure and high-resource nodes.                      |          |
| **API Extensions**               | [x]  | MigrationPolicy fields: `allowWorkloadDisruption`, `allowPostCopy`, `bandwidthPerMigration`, `completionTimeoutPerGiB`. VMI status field: `migrationState.mode` |          |
| **Topology Considerations**      | [x]  | Requires at least 2 worker nodes for migration. Windows VMs require nodes with special_infra and high_resource_vm capacity.                                     |          |

---

### **II. Software Test Plan (STP)**

#### **1. Scope of Testing**

Tests validate that allow-workload-disruption (AWD) migration completes in the expected mode (PostCopy or Paused) across different migration triggers (explicit migration, node drain, CPU/memory hotplug) and guest operating systems (RHEL, Windows). Guest process preservation is verified after each migration.

**Testing Goals**

- **[P0]** AWD Migration Mode (RHEL): Verify explicit migration completes in PostCopy and Paused modes with process preservation.
- **[P0]** AWD Migration Mode (Windows): Verify explicit migration completes in PostCopy and Paused modes with process preservation.
- **[P0]** AWD Node Drain (RHEL): Verify node drain triggers AWD migration in the expected mode with process preservation.
- **[P1]** AWD CPU Hotplug (RHEL): Verify CPU hotplug triggers AWD migration and guest reports new CPU count with process preservation.
- **[P1]** AWD CPU Hotplug (Windows): Verify CPU hotplug triggers AWD migration and guest reports new CPU count with process preservation.
- **[P1]** AWD Memory Hotplug (RHEL): Verify memory hotplug triggers AWD migration and guest reports new memory amount with process preservation.

**Out of Scope (Testing Scope Exclusions)**

| Out-of-Scope Item             | Rationale                                                                                                       | PM/ Lead Agreement |
|:------------------------------|:----------------------------------------------------------------------------------------------------------------|:------------------|
| Windows node drain            | Windows AWD node drain is not currently covered; only migration mode and CPU hotplug are tested for Windows.     | TODO              |
| Windows memory hotplug        | Windows memory hotplug with AWD is not currently covered.                                                        | TODO              |
| s390x memory hotplug          | s390x does not support maxGuest memory, so memory hotplug cannot be tested on this architecture.                 | TODO              |
| Performance / scale testing   | Not in scope for functional AWD validation.                                                                      | TODO              |

**Test Limitations**

- Triggering Paused mode reliably requires tuning bandwidth, completion timeout, and guest disk load (1GiB allocated file on RHEL) to prevent precopy from converging too quickly, which would skip the Paused phase entirely.

#### **2. Test Strategy**

| Item                           | Description                                                                                                                                                  | Applicable (Y/N or N/A) | Comments                                                                                                                  |
|:-------------------------------|:-------------------------------------------------------------------------------------------------------------------------------------------------------------|:------------------------|:--------------------------------------------------------------------------------------------------------------------------|
| Functional Testing             | Validates that the feature works according to specified requirements and user stories                                                                        | Y                       |                                                                                                                           |
| Automation Testing             | Ensures test cases are automated for continuous integration and regression coverage                                                                          | Y                       |                                                                                                                           |
| Performance Testing            | Validates feature performance meets requirements (latency, throughput, resource usage)                                                                       | N                       | Not in scope for functional AWD validation                                                                                |
| Security Testing               | Verifies security requirements, RBAC, authentication, authorization, and vulnerability scanning                                                              | N/A                     | MigrationPolicy RBAC is covered by core KubeVirt tests                                                                   |
| Usability Testing              | Validates user experience, UI/UX consistency, and accessibility requirements. Does the feature require UI? If so, ensure the UI aligns with the requirements | N/A                     | No UI component; migration mode is reported via standard VMI status fields                                                |
| Compatibility Testing          | Ensures feature works across supported platforms, versions, and configurations                                                                               | Y                       | Parametrized across RHEL and Windows guest OSes                                                                           |
| Regression Testing             | Verifies that new changes do not break existing functionality                                                                                                | Y                       | Tests validate both migration mode and hotplug functionality                                                              |
| Upgrade Testing                | Validates upgrade paths from previous versions, data migration, and configuration preservation                                                               | N                       | Upgrade path evaluated; no AWD-specific upgrade concerns identified. Not in scope for this cycle.                         |
| Backward Compatibility Testing | Ensures feature maintains compatibility with previous API versions and configurations                                                                        | N/A                     | No known API changes affecting backward compatibility                                                                     |
| Dependencies                   | Dependent on deliverables from other components/products? Identify what is tested by which team.                                                             | Y                       | Core AWD functionality is implemented in KubeVirt                                                                         |
| Cross Integrations             | Does the feature affect other features/require testing by other components? Identify what is tested by which team.                                           | Y                       | AWD interacts with hotplug and node drain (sig-virt); tests cover migration triggered by both                             |
| Monitoring                     | Does the feature require metrics and/or alerts?                                                                                                              | N/A                     | No specific metrics required for AWD                                                                                      |
| Cloud Testing                  | Does the feature require multi-cloud platform testing? Consider cloud-specific features.                                                                     | N/A                     | Bare metal with RWX storage is required                                                                                   |

#### **3. Test Environment**

| Environment Component                         | Configuration                      | Specification Examples                                                                                         |
|:----------------------------------------------|:-----------------------------------|:---------------------------------------------------------------------------------------------------------------|
| **Cluster Topology**                          | Bare Metal                         | Multi-worker OCP cluster (minimum 2 workers for migration, additional for Windows special_infra)               |
| **OCP & OpenShift Virtualization Version(s)** | OCP 4.17+                          | Feature available from OCP-V 4.17 onward                                                                       |
| **CPU Virtualization**                        | VT-x / AMD-V                      | Required for VM execution                                                                                      |
| **Compute Resources**                         | Standard + high-resource nodes     | Standard workers for RHEL; high-resource workers (special_infra) for Windows VMs                               |
| **Special Hardware**                          | N/A                                | Agnostic                                                                                                       |
| **Storage**                                   | RWX default storage class          | Required for live migration (e.g., ocs-storagecluster-ceph-rbd-virtualization)                                 |
| **Network**                                   | OVN-Kubernetes                     | Standard cluster networking                                                                                    |
| **Required Operators**                        | OpenShift Virtualization           |                                                                                                                |
| **Platform**                                  | Bare Metal                         |                                                                                                                |
| **Special Configurations**                    | N/A                                |                                                                                                                |

#### **3.1. Testing Tools & Frameworks**

| Category           | Tools/Frameworks                                  |
|:-------------------|:--------------------------------------------------|
| **Test Framework** | -                                                  |
| **CI/CD**          | -                                                  |
| **Other Tools**    | -                                                  |

#### **4. Entry Criteria**

The following conditions must be met before testing can begin:

- [x] Requirements and design documents are **approved and merged**
- [x] Test environment can be **set up and configured** (see Section II.3 - Test Environment)
- [x] AWD migration policy fields are available and functional in the target OCP-V version

#### **5. Risks**

| Risk Category        | Specific Risk for This Feature                                                                                                                 | Mitigation Strategy                                                                                                                | Status |
|:---------------------|:-----------------------------------------------------------------------------------------------------------------------------------------------|:-----------------------------------------------------------------------------------------------------------------------------------|:-------|
| Timeline/Schedule    | N/A                                                                                                                                            | -                                                                                                                                  | [x]    |
| Test Coverage        | Paused mode may not reliably trigger if precopy converges too quickly on fast storage                                                          | Added 1GiB guest disk allocation for RHEL VMs and tuned completionTimeoutPerGiB to ensure precopy does not converge in phase 1     | [x]    |
| Test Environment     | Windows tests require special_infra and high_resource_vm nodes which may not be available in all CI environments                               | Tests are marked with `special_infra` and `high_resource_vm` markers to skip when infrastructure is unavailable                    | [x]    |
| Untestable Aspects   | Exact timing of PostCopy/Paused mode transition depends on cluster load, storage speed, and network conditions                                 | Tests verify the final migration mode reported in VMI status rather than transition timing                                         | [x]    |
| Resource Constraints | N/A                                                                                                                                            | -                                                                                                                                  | [x]    |
| Dependencies         | AWD behavior depends on KubeVirt migration engine implementation; changes in convergence logic could affect mode selection                      | Monitor KubeVirt upstream changes to migration convergence and completionTimeout behavior                                          | [x]    |

---

### **III. Test Scenarios & Traceability**

| Requirement ID      | Requirement Summary                                                                                                                       | Test Scenario(s)                                                                                                                             | Tier   | Priority |
|:---------------------|:------------------------------------------------------------------------------------------------------------------------------------------|:---------------------------------------------------------------------------------------------------------------------------------------------|:-------|:---------|
| CNV-15225            | As an admin, I want AWD migration to complete in the expected mode (PostCopy/Paused) on RHEL VMs.                                         | Migrate RHEL VM with AWD policy; verify migration mode is PostCopy or Paused and background process PID is preserved.                        | Tier 1 | P0       |
| CNV-15245            | As an admin, I want node drain to trigger AWD migration in the expected mode on RHEL VMs.                                                 | Drain the node hosting a RHEL VM with AWD policy; verify migration mode and background process PID after drain completes.                    | Tier 2 | P0       |
| CNV-15234            | As an admin, I want CPU hotplug to trigger AWD migration and reflect the new CPU count in the RHEL guest.                                 | Hotplug CPU sockets on RHEL VM with AWD policy; verify migration mode, guest CPU count, and background process PID.                          | Tier 2 | P1       |
| CNV-15235            | As an admin, I want memory hotplug to trigger AWD migration and reflect the new memory amount in the RHEL guest.                          | Hotplug memory on RHEL VM with AWD policy; verify migration mode, guest memory amount, and background process PID.                           | Tier 2 | P1       |
| CNV-15246            | As an admin, I want AWD migration to complete in the expected mode (PostCopy/Paused) on Windows VMs.                                      | Migrate Windows VM with AWD policy; verify migration mode is PostCopy or Paused and background process PID is preserved.                     | Tier 1 | P0       |
| CNV-15247            | As an admin, I want CPU hotplug to trigger AWD migration and reflect the new CPU count in the Windows guest.                              | Hotplug CPU sockets on Windows VM with AWD policy; verify migration mode, guest CPU count, and background process PID.                       | Tier 2 | P1       |

---

### **IV. Sign-off and Approval**

This Software Test Plan requires approval from the following stakeholders:

* **Reviewers:**
  - QE Architect (OCP-V): [Ruth Netser](@rnetser)
  - QE Members (OCP-V): [Kedar Bidarkar](@kbidarkar), [Akriti Gupta](@akri3i), [Samuel Alberstein](@SamAlber)
* **Approvers:**
  - QE Architect (OCP-V): [Ruth Netser](@rnetser)
  - Principal QE (OCP-V): [Den Shchedrivyi](@dshchedr), [Vasiliy Sibirskiy](@vsibirsk)
  - Product Manager/Owner: [Ronen Sde-Or](rsdeor@redhat.com)
  - Principal Developer (OCP-V): [Edward Haas](@EdDev)
