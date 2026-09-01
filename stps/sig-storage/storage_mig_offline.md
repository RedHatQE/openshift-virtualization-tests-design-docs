# Openshift-virtualization-tests Test plan

## **Offline Storage Migration - Quality Engineering Plan**

### **Metadata & Tracking**

- **Enhancement(s):** [CNV-77501](https://issues.redhat.com/browse/CNV-77501) - no VEP exists for this feature
- **Feature Tracking:** [CNV-73500](https://issues.redhat.com/browse/CNV-73500)
- **Epic Tracking:** [CNV-73500](https://issues.redhat.com/browse/CNV-73500)
- **QE Owner(s):** Jose Manuel Castano (joscasta@redhat.com)
- **Owning SIG:** sig-storage
- **Participating SIGs:** sig-storage
- **Feature Maturity:**
  - DP: N/A
  - TP: v4.22
  - GA: v5.0

**Document Conventions:**
None

### **Feature Overview**

This feature enables customers to migrate storage for VMs regardless of their running state, including stopped VMs. Customers can perform batch storage migrations that include both offline and running VMs in a single operation.

---

### **I. Motivation and Requirements Review (QE Review Guidelines)**

This section documents the mandatory QE review process. The goal is to understand the feature's value,
technology, and testability before formal test planning.

#### **1. Requirement & User Story Review Checklist**

- [x] **Review Requirements**
  - *List the key D/S requirements reviewed:*
    - Support storage migration for offline (stopped) VMs between different storage classes
    - Support mixed migration plans containing both offline and running VMs
    - Support offline VM storage migration with hotplug disks attached
    - Support source volume cleanup policy configuration for offline VM migration (retain or delete source volumes after migration completes)
    - Ensure offline VMs remain pointing to original volumes when migration fails
    - Support VM start operations during ongoing storage migration — when a user starts a stopped VM during migration, the VM waits for migration to complete before becoming ready (the VM transitions to Running only after storage migration finishes)
    - Support all volume mode combinations for cross-storage migration (File-to-Block, Block-to-File, File-to-File, Block-to-Block)
    - Support cancellation of in-progress storage migration for both offline and online VMs — cancelling the migration while it is running leaves the VMs pointing to their original volumes

- [x] **Understand Value and Customer Use Cases**
  - *Describe the feature's value to customers:* Customers need to perform storage migration for offline VMs without requiring them to be running, providing flexibility in storage management operations.
  - *List the customer use cases identified:*
    - As a VM owner, I want to migrate storage for offline VMs, so that I can perform storage management operations without having to start the VMs
    - As a VM owner, I want to migrate storage with mixed VM states (online and offline) in one migration plan, so that I can perform batch migration operations regardless of VM state

- [x] **Testability**
  - *Note any requirements that are unclear or untestable:* Requirements are testable. Downstream build with the feature code is available for testing.

- [x] **Acceptance Criteria**
  - *List the acceptance criteria:*
    - As a VM owner, I want to migrate storage for offline VMs between ODF and HPP storage classes, so that:
      - Migration plan status reports "Succeeded"
      - Offline VM disk references point to the new target storage class
      - VM boots successfully after migration using the migrated storage
    - As a VM owner, I want to migrate storage with mixed offline VMs and running VMs in one migration plan, so that:
      - Migration plan status reports "Succeeded"
      - All offline VMs point to target storage class
      - All running VMs point to target storage class and remain running
    - As a VM owner, I want to migrate storage for offline VMs with hotplug disk, so that:
      - Migration plan status reports "Succeeded"
      - All disks including hotplug disks are migrated to target storage class
      - VM boots successfully with all disks accessible
    - As a VM owner, I want to retain or delete the source volume for an offline VM, so that:
      - When the cleanup policy is set to retain: source volumes exist after migration completes
      - When the cleanup policy is set to delete: source volumes are deleted after migration completes
    - As a VM owner, I want an offline VM to point to the original volume when migration fails, so that:
      - Migration plan status reports "Failed"
      - VM disk references remain unchanged and point to original storage
      - Source-volume survival when cleanup policy is delete and migration fails is covered by [storage_mig_cleanup.md](stps/sig-storage/storage_mig_cleanup.md)
    - As a VM owner, I want migration to succeed when starting a stopped VM during migration, so that:
      - Migration plan status reports "Succeeded"
      - VM remains in a pending state throughout the migration and only becomes Ready after migration completes (proves no disrupt-then-restart occurred)
      - VM start operation waits for migration to complete before the VM becomes ready
      - VM points to target storage and starts successfully after migration completes

    - As a VM owner, I want to cancel an in-progress storage migration for offline and online VMs, so that:
      - Migration plan status reports "Canceled"
      - VM disk references remain unchanged and point to the original storage
      - VM remains running throughout (online VMs)
      - Source volumes are preserved regardless of the configured cleanup policy

  - *Note any gaps or missing criteria:* N/A

- [x] **Non-Functional Requirements (NFRs)**
  - *List applicable NFRs and their targets:*
    - **Documentation:** User guide updates for offline VM storage migration support
    - **UI:** UI updates for offline VM migration selection (covered by UI team in CNV-77503)
  - *Note any NFRs not covered and why:*
    - **Performance:** Not covered - Performance testing for bulk offline migrations is tracked separately and will be addressed by a dedicated test plan
    - **Monitoring:** Not applicable - Feature does not introduce new metrics or alerts; existing migration monitoring applies
    - **Observability:** Not applicable - Feature reuses existing migration observability patterns without new requirements
    - **Security:** Not applicable - Feature does not introduce new security boundaries or authentication/authorization requirements; leverages existing migration RBAC
    - **Scalability:** Inherits existing limits - Feature reuses existing migration infrastructure with its cluster-level parallelism constraints; offline VM support introduces no additional scalability requirements

#### **2. Known Limitations**

The limitations are documented to ensure alignment between development, QA, and product teams.
The following topics will not be tested or supported.

None - reviewed and confirmed with Peter Lauterbach on Apr 28,2026.

#### **3. Technology and Design Review**

- [x] **Developer Handoff/QE Kickoff**
  - *Key takeaways and concerns:* Extend the offline VMs storage migration support

- [x] **Technology Challenges**
  - *List identified challenges:*
    - Simulating migration failures for offline VMs requires injecting failures at specific points (e.g., storage provisioning failures, clone failures) to verify rollback behavior
    - Testing VM start during migration requires precise timing control to ensure the VM start request occurs while migration is in progress
    - Testing migration cancellation requires a sufficiently large disk so the migration takes long enough to cancel while still in progress
    - Verifying volume mode conversion behavior (Block-to-File, File-to-Block) requires validation that data remains accessible after conversion
    - Testing mixed migration plans requires coordinating both offline and online migration paths simultaneously to verify they don't interfere
  - *Impact on testing approach:*
    - Test framework must support failure injection mechanisms for storage operations
    - Test cases need timing coordination to trigger VM start at specific migration stages
    - Cancellation tests require sufficiently large disks so that migration remains in progress when cancellation is initiated
    - Verification logic must include data integrity checks across volume mode conversions
    - Mixed migration scenarios require monitoring both offline and online VMs throughout the migration lifecycle

- [x] **API Extensions**
  - *List new or modified APIs:* No new APIs - extends existing migration plan API to handle offline VMs
  - *Testing impact:* No API test updates required; functional tests will verify new behavior

- [x] **Test Environment Needs**
  - *See environment requirements in Section II.3 and testing tools in Section II.3.1*

- [x] **Topology Considerations**
  - *Describe topology requirements:* Standard 3-master/3-worker cluster sufficient
  - *Impact on test design:* No special topology requirements

### **II. Software Test Plan (STP)**

This STP serves as the **overall roadmap for testing**, detailing the scope, approach, resources, and schedule.

#### **1. Scope of Testing**

**Testing Goals**

- **[P0]** Verify offline VM storage migration completes between ODF and HPP storage classes, and the VM boots successfully after migration
- **[P0]** Verify storage migration completes for a migration plan containing both offline and running VMs
- **[P0]** Verify source volumes are retained or deleted according to the source volume cleanup policy when offline VM storage migration completes
- **[P1]** Verify offline VM storage migration completes when the VM has hotplug disks attached
- **[P1]** Verify offline VM storage migration completes for same-storage class migrations (HPP to HPP) to enable node-to-node migration with local storage
- **[P2]** Verify offline VM continues pointing to the original volume when storage migration fails
- **[P2]** Verify storage migration completes when a stopped VM is started during the migration process and the VM waits for migration completion before becoming ready
- **[P2]** Verify storage migration for offline and online VMs can be cancelled while in progress with the default cleanup policy (keepSource), the VMs continue pointing to their original volumes, and source volumes are preserved

> **Failure-path priority rationale:** The migration-failure scenario is P2 rather than P0 because offline VM migration reuses the same rollback mechanism already validated by existing online VM storage migration tests. Since the VM is stopped during offline migration, a failed migration carries lower operational risk than the online case — no running workload is disrupted, and the VM remains safely pointing to its original volumes. The rollback path is covered at P2 to confirm it works for the offline case, but it does not block GA given the existing online migration failure coverage.
>
> *PM Agreement:* Peter Lauterbach/2026-06-17

**Storage Class Coverage**

The following storage classes are supported for migration testing:
- **ODF** (ocs-storagecluster-ceph-rbd-virtualization)
- **HPP** (hostpath-csi-pvc-block)

Migration combinations will be tested:
- Cross-storage class migrations (ODF ↔ HPP)
- Same-storage class migrations (HPP → HPP) for node-to-node migration scenarios with local storage

**Volume Mode Coverage**

All volume mode combinations are supported and will be tested:
- **Block ↔ Block** — Block to Block migration
- **File ↔ File** — Filesystem to Filesystem migration
- **Block ↔ File** — Block to Filesystem migration
- **File ↔ Block** — Filesystem to Block migration

**Out of Scope (Testing Scope Exclusions)**

The following items are explicitly Out of Scope for this test cycle and represent intentional exclusions.
No verification activities will be performed for these items, and any related issues found will not be classified as defects for this release.

None — reviewed and confirmed that all supported product functionality will be tested this cycle.

> **PM Sign-off:** Peter Lauterbach/2026-06-17

**Test Limitations**

None — reviewed and confirmed that no test limitations apply for this release.
- *Sign-off:* Peter Lauterbach/2026-06-17

#### **2. Test Strategy**

**Functional**

- [x] **Functional Testing** — Validates that the feature works according to specified requirements and user stories
  - *Details:* Functional testing will verify offline VM storage migration and mixed offline/online VM migration scenarios

- [x] **Automation Testing** — Confirms test automation plan is in place for CI and regression coverage (all tests are expected to be automated)
  - *Details:* All test cases will be automated

- [x] **Regression Testing** — Verifies that new changes do not break existing functionality
  - *Details:* Verify that existing online VM storage migration functionality remains unaffected by the offline VM support additions

- [ ] **Self-Validation Testing** — Should any of the new tests be included in the self-validation test package?
  - *Details:* N/A. Offline storage migration is not a core operational health-check scenario suitable for the self-validation package.

**Non-Functional**

- [ ] **Performance Testing** — Validates feature performance meets requirements (latency, throughput, resource usage)
  - *Details:* Performance testing for bulk offline migrations is tracked separately in CNV-82430 and will be covered by a separate test plan

- [ ] **Scale Testing** — Validates feature behavior under increased load and at production-like scale (e.g., large number of VMs, nodes, or concurrent operations)
  - *Details:* N/A. Scalability characteristics inherit from existing migration infrastructure; no new scalability requirements introduced by adding offline VM support.

- [ ] **Security Testing** — Verifies security requirements, RBAC, authentication, authorization, and vulnerability scanning
  - *Details:* N/A. Feature does not introduce new security boundaries or authentication/authorization requirements; leverages existing migration RBAC model.

- [x] **Usability Testing** — Validates user experience and accessibility requirements
  - Does the feature require a UI? If so, ensure the UI aligns with the requirements (UI/UX consistency, accessibility)
  - Does the feature expose CLI commands? If so, validate usability and that needed information is available (e.g., status conditions, clear output)
  - Does the feature trigger backend operations that should be reported to the admin? If so, validate that the user receives clear feedback about the operation and its outcome (e.g., status conditions, events, or notifications indicating success or failure)
  - *Details:* UI testing will be covered in https://issues.redhat.com/browse/CNV-77503

- [x] **Monitoring** — Does the feature require metrics and/or alerts?
  - *Details:* No new metrics or alerts are required. Existing migration monitoring (including migration progress reporting) applies to both online and offline VM migrations and is covered by existing regression suites.

**Integration & Compatibility**

- [x] **Compatibility Testing** — Ensures feature works across supported platforms, versions, and configurations
  - Does the feature maintain backward compatibility with previous API versions and configurations?
  - *Details:* Feature maintains backward compatibility with existing migration API. Existing online VM migrations continue to work unchanged.

- [ ] **Upgrade Testing** — Validates upgrade paths from previous versions, data migration, and configuration preservation
  - *Details:* Upgrade path was evaluated. No dedicated upgrade testing is required because this is a new additive feature (offline VM storage migration support) that does not modify existing migration behavior or introduce configuration changes requiring migration. Existing online VM migration functionality remains unchanged and backward compatible (see Compatibility Testing). Users upgrading to v4.22+ will gain offline migration capability without requiring any configuration updates or data migration.

- [ ] **Dependencies** — Blocked by deliverables from other components/products. Identify what we need from other teams before we can test.
  - *Details:* No blocking dependencies

- [x] **Cross Integrations** — Does the feature affect other features or require testing by other teams? Identify the impact we cause.
  - *Details:* UI team needs to update their migration UI to support offline VM selection

**Infrastructure**

- [x] **Cloud Testing** — Does the feature require multi-cloud platform testing? Consider cloud-specific features.
  - *Details:* Cloud storage migration uses platform default storage classes and does not require dedicated cloud-specific test scenarios. The underlying storage transfer mechanism is platform-agnostic. Testing with bare-metal storage classes (ODF and HPP) validates the migration mechanism; cloud platforms (AWS EBS, Azure Disk, GCP PD) inherit this validated behavior through the same storage migration infrastructure.

#### **3. Test Environment**

- **Cluster Topology:** 3-master/3-worker

- **OCP & OpenShift Virtualization Version(s):** OCP 4.22 with OpenShift Virtualization 4.22

- **CPU Virtualization:** VT-x (Intel) or AMD-V enabled

- **Compute Resources:** Minimum per worker node: 8 vCPUs, 32GB RAM

- **Special Hardware:** N/A

- **Storage:**
  - Bare Metal: ocs-storagecluster-ceph-rbd-virtualization, hostpath-csi-pvc-block

- **Network:** OVN-Kubernetes, IPv4

- **Required Operators:** N/A

- **Platform:** Bare Metal, AWS, Azure, GCP

- **Special Configurations:** N/A

#### **3.1. Testing Tools & Frameworks**

- **Test Framework:** Standard

- **CI/CD:** N/A

- **Other Tools:** N/A

#### **4. Entry Criteria**

The following conditions must be met before testing can begin:

- [x] Requirements and design documents are **approved and merged**
- [x] Test environment can be **set up and configured** (see Section II.3 - Test Environment)

#### **5. Risks**

**Timeline/Schedule**

- **Risk:** No scheduling or deadline risks identified
  - **Mitigation:** Standard test timeline is sufficient for planned test scenarios

**Test Coverage**

- **Risk:** No gaps in test coverage identified
  - **Mitigation:** All acceptance criteria are covered by planned test scenarios

**Test Environment**

- **Risk:** No hardware, software, or infrastructure constraints identified
  - **Mitigation:** Standard test environment is sufficient for testing this feature

**Untestable Aspects**

- **Risk:** No untestable scenarios identified
  - **Mitigation:** All scenarios can be reproduced in test environment

**Resource Constraints**

- **Risk:** No staffing, skill, or capacity limitations identified
  - **Mitigation:** Current QE team capacity is sufficient for planned test execution

**Dependencies**

- **Risk:** No blocking external dependencies identified
  - **Mitigation:** UI team updates for offline VM selection are non-blocking; API testing can proceed independently

---

### **III. Test Scenarios & Traceability**

- **[CNV-77501]** — As a VM owner, I want to migrate storage for offline VMs between ODF and HPP
  - *Test Scenario:* [Tier 2] Verify storage migration completes for offline VMs between ODF and HPP across all volume mode combinations (Block-to-Block, File-to-File, Block-to-File, File-to-Block): VM boots successfully after migration, and pre-written guest data remains readable and unchanged after each volume-mode combination
  - *Priority:* P0

- **[CNV-77501]** — As a VM owner, I want to migrate storage with mixed VM states (online and offline)
  - *Test Scenario:* [Tier 2] Verify storage migration completes for a migration plan containing both offline and running VMs: migration plan status reports "Succeeded", all offline VMs point to the target storage class, and all running VMs point to the target storage class while remaining running throughout
  - *Priority:* P0

- **[CNV-77501]** — As a VM owner, I want to retain or delete the source volume for an offline VM
  - *Test Scenario:* [Tier 2] Verify source volume handling for an offline VM matches the configured cleanup policy: source volumes exist after migration when set to retain, and source volumes are deleted after migration when set to delete
  - *Priority:* P0

- **[CNV-77501]** — As a VM owner, I want to migrate storage for offline VMs with hotplug disk
  - *Test Scenario:* [Tier 2] Verify storage migration for offline VM with hotplug disk: migration plan status reports "Succeeded", all disks including hotplug disks are migrated to the target storage class, and VM boots successfully with all disks accessible
  - *Priority:* P1

- **[CNV-77501]** — As a VM owner, I want to migrate storage for offline VMs between nodes using the same storage class (HPP)
  - *Test Scenario:* [Tier 2] Verify storage migration for offline VM from HPP to HPP storage class across different nodes: migration plan status reports "Succeeded", VM disk references point to the new volume on the target node, and VM boots successfully after migration
  - *Priority:* P1

- **[CNV-77501]** — As a VM owner, I want an offline VM to still point to the original volume when migration fails
  - *Test Scenario:* [Tier 2] Verify offline VM rollback on migration failure: migration plan status reports "Failed", and VM disk references remain unchanged pointing to the original storage
  - *Priority:* P2

- **[CNV-77501]** — As a VM owner, I want the migration to succeed when starting a stopped VM during migration
  - *Test Scenario:* [Tier 2] Verify migration succeeds when starting a stopped VM during migration: migration plan status reports "Succeeded", VM remains in a pending state throughout the migration, VM becomes ready only after migration completes, and VM points to the target storage class
  - *Priority:* P2

- **[CNV-77501]** — As a VM owner, I want to cancel an in-progress storage migration for offline and online VMs
  - *Test Scenario:* [Tier 2] Verify storage migration cancellation while the migration is actively in progress for both offline and online VMs with the default cleanup policy (keepSource): cancel the migration, verify migration plan status reports "Canceled", VM disk references remain unchanged pointing to the original storage, online VMs remain running throughout, and source volumes are preserved
  - *Priority:* P2

---

### **IV. Sign-off and Approval**

This Software Test Plan requires approval from the following stakeholders:

* **Reviewers:**
  - QE Architect (OCP-V): Ruth Netser (`@rnetser`)
  - QE Members (OCP-V): Jenia Peimer (`@jpeimer`), Kate Shvaika (`@kshvaika`), Jose Manuel Castano (`@joscasta`)
* **Approvers:**
  - QE Architect (OCP-V): Ruth Netser (`@rnetser`)
  - Dev Lead: Alexander Wels (`@awels`)
  - PM: Peter Lauterbach (`@pelauter`)
