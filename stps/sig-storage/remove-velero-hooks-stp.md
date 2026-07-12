# Openshift-virtualization-tests Test plan

## **Make Velero Hooks in virt-launcher Optional or Removable - Quality Engineering Plan**

### **Metadata & Tracking**

- **Enhancement(s):** [kubevirt/kubevirt#14056: Remove Velero Prehook/Posthook Annotations on virt-launcher Pod](https://github.com/kubevirt/kubevirt/issues/14056)
- **Feature Tracking:** [CNV-75370](https://redhat.atlassian.net/browse/CNV-75370)
- **Epic Tracking:** [CNV-79727](https://redhat.atlassian.net/browse/CNV-79727)
- **Feature Maturity:**
  - DP: N/A
  - TP: N/A
  - GA: 4.22
- **QE Owner(s):** [Emanuele Prella](@ema-aka-young)
- **Owning SIG:** sig-storage
- **Participating SIGs:** sig-storage

**Document Conventions:**

| Term | Definition |
| :--- | :--------- |
| Velero hooks | Pre- and post-backup annotations on virt-launcher pods that trigger filesystem freeze/unfreeze operations during Velero backups |
| Opt-out annotation | A VM or KubeVirt CR annotation that disables Velero hook injection, preventing freeze/unfreeze operations during backups |
| Cluster-wide opt-out | Setting the opt-out annotation on the KubeVirt CR to disable hooks for all VMs that do not explicitly override it |
| Per-VM opt-out | Setting the opt-out annotation on a specific VM to override the cluster-wide setting |


### **Feature Overview**

Cluster administrators can now control or disable the automatic Velero pre- and post-backup hooks that freeze and unfreeze VM filesystems during backups. Previously, these hooks ran automatically on every Velero backup, executing freeze and unfreeze operations regardless of whether those operations were needed. With this feature, administrators can opt out of hook execution per VM or cluster-wide via a simple annotation, giving them granular control over backup behavior without requiring VM restarts. This avoids unnecessary guest-agent operations and improves overall backup reliability for OpenShift Virtualization workloads.

---

### **I. Motivation and Requirements Review (QE Review Guidelines)**

**Motivation:** Velero backup hooks automatically freeze and unfreeze VM filesystems during backups, but these operations are not always needed and may be undesirable in certain environments. Customers need the ability to disable these hooks to avoid unnecessary filesystem freeze/unfreeze operations during backups.

#### **1. Requirement & User Story Review Checklist**

- [x] **Review Requirements**
  - *List the key D/S requirements reviewed:* Reviewed CNV-75370 and upstream issue kubevirt/kubevirt#14056. The feature adds an opt-out annotation to disable Velero freeze/unfreeze hooks on VMs.

- [x] **Understand Value and Customer Use Cases**
  - *Describe the feature's value to customers:* Velero backup hooks execute filesystem freeze/unfreeze operations that are not always needed and may be undesirable in certain environments. This feature gives administrators control over hook execution.
  - *List the customer use cases identified:*
    - **UC1:** As a cluster administrator, I want to disable Velero backup hooks on specific VMs so that backups succeed even when the guest agent is unavailable.
    - **UC2:** As a cluster administrator, I want to disable hooks cluster-wide so that metadata-only backups proceed without filesystem freezes.

- [x] **Testability**
  - *Note any requirements that are unclear or untestable:* Guest agent unavailability cannot be reliably simulated with standard VM images (see Test Limitations in Section II.1). All other requirements are testable. Backup hook behavior is observable through Velero backup outcomes.

- [x] **Acceptance Criteria**
  - *List the acceptance criteria:*
    - **AC1:** When the opt-out annotation is set on a VM, Velero backup operations proceed without attempting filesystem freeze/unfreeze.
    - **AC2:** When no opt-out annotation is set, Velero backup operations attempt filesystem freeze/unfreeze as before.
    - **AC3:** Setting the annotation cluster-wide disables hooks for all VMs that do not explicitly override it.
    - **AC4:** Adding or removing the annotation takes effect on running VMs without requiring a restart.
    - **AC5:** The opt-out annotation is honored when a VM is paused, confirming hooks are not injected regardless of VM state.
  - *Note any gaps or missing criteria:* UC1 (guest agent unavailability) is not directly testable — see Test Limitations in Section II.1.

- [x] **Non-Functional Requirements (NFRs)**
  - *List applicable NFRs and their targets:*
    - **Monitoring:** No new metrics or alerts — the feature is a simple annotation toggle.
    - **UI:** No UI changes. Feature is annotation-driven via CLI/API and UI testing doesn't add any customer value. See "Out of Scope (Testing Scope Exclusions) - UI testing for hook opt-out configuration". *PM LGTM:* Peter Lauterbach/16-06-2026
    - **Security:** No RBAC changes — uses existing VM/KubeVirt CR edit permissions.
    - **Performance:** No performance impact.
    - **Scalability:** Cluster-wide toggle propagates to all VMs via standard KubeVirt reconciliation. No documented scale limits.
    - **Documentation:** Upstream docs updated in PR.
  - *Note any NFRs not covered and why:* None

#### **2. Known Limitations**

- The opt-out setting only controls Velero backup hook injection; it does not affect other backup mechanisms.
  - *Sign-off:* Peter Lauterbach/16-06-2026

- Changing the cluster-wide opt-out setting triggers reconciliation of all running VMs, which may cause a brief processing spike in large environments.
  - *Sign-off:* Peter Lauterbach/16-06-2026

#### **3. Technology and Design Review**

- [x] **Developer Handoff/QE Kickoff**
  - *Key takeaways and concerns:* Reviewed upstream PR kubevirt/kubevirt#16786 (merged Feb 2026). Implementation uses an opt-out annotation rather than a new API field to avoid feature-freeze constraints.

- [x] **Technology Challenges**
  - *List identified challenges:* Tier 2 tests require OADP operator and a functional Velero installation.
  - *Impact on testing approach:* Standard OADP test infrastructure from existing data_protection test suite will be reused.

- [x] **API Extensions**
  - *List new or modified APIs:* No new API fields. The feature uses a VM/KubeVirt CR annotation to control behavior.
  - *Testing impact:* Annotation behavior validated through Velero backup outcomes.

- [x] **Test Environment Needs**
  - *See environment requirements in Section II.3 and testing tools in Section II.3.1*

- [x] **Topology Considerations**
  - *Describe topology requirements:* No special topology requirements. Standard cluster topology is sufficient.
  - *Impact on test design:* None.

### **II. Software Test Plan (STP)**

This STP serves as the overall roadmap for testing, detailing the scope, approach, resources, and schedule.


#### **1. Scope of Testing**

**Testing Goals**

- **[P0]** As a cluster administrator, I want to verify that backup hooks are present by default and that the cluster-wide opt-out dynamically adds and removes them on running VMs without requiring a restart.
- **[P0]** As a cluster administrator, I want to verify that a per-VM opt-out setting takes precedence over the cluster-wide setting.
- **[P0]** As a cluster administrator, I want to verify that the opt-out annotation is honored for a paused VM, confirming hooks are not injected regardless of VM state.
- **[P0]** As a cluster administrator, I want to verify that a full Velero backup and restore workflow completes successfully with hooks disabled.

**Out of Scope (Testing Scope Exclusions)**

- **Backup of a VM in provisioning state (no running pod)**
  - *Rationale:* When a VM is still provisioning, no backup hooks are present regardless of the opt-out setting. The opt-out annotation does not change behavior in this case — the backup outcome is the same with or without it.
  - *PM/Lead Agreement:* Peter Lauterbach/16-06-2026

- **Windows VM-specific testing of hook opt-out**
  - *Rationale:* The opt-out annotation controls whether backup hooks are injected, independent of the guest operating system. The behavior is identical for Linux and Windows VMs. Windows backup/restore is already covered by existing OADP tests.
  - *PM/Lead Agreement:* Peter Lauterbach/16-06-2026

- **UI testing for hook opt-out configuration**
  - *Rationale:* The feature is annotation-driven via CLI/API with no UI components. PM confirmed no UI coverage is needed based on customer value assessment.
  - *PM/Lead Agreement:* Peter Lauterbach/16-06-2026

**Test Limitations**

- **Guest agent unavailability scenario**
  - *Constraint:* Standard VM images (RHEL, Fedora) include a functioning guest agent by default. There is no reliable way to simulate guest agent unavailability without using non-standard images (e.g., Cirros) or fragile workarounds that do not produce meaningful behavioral differences — the backup hooks exit successfully regardless of guest agent state.
  - *Sign-off:* Emanuele Prella/28-05-2026

#### **2. Test Strategy**

**Functional**

- [x] **Functional Testing** — Validates that the feature works according to specified requirements and user stories
  - *Details:* Verify Velero backup hook opt-out behavior per VM and cluster-wide, and Velero backup outcomes with hooks disabled.

- [x] **Automation Testing** — Confirms test automation plan is in place for CI and regression coverage (all tests are expected to be automated)
  - *Details:* Tier 1 functional tests in the upstream kubevirt test suite. Tier 2 end-to-end tests in the downstream test repository covering the full VM lifecycle with opt-out toggling.

- [x] **Regression Testing** — Verifies that new changes do not break existing functionality
  - *Details:* Existing OADP/Velero backup tests must continue to pass (default hook behavior unchanged for VMs without the opt-out setting).

**Non-Functional**

- [ ] **Performance Testing** — Validates feature performance meets requirements
  - *Details:* N/A. Simple annotation toggle, no measurable performance impact.

- [ ] **Scale Testing** — Validates feature behavior under increased load
  - *Details:* N/A. Cluster-wide toggle propagates to all VMs; this behavior is covered by upstream tests.

- [ ] **Security Testing** — Verifies security requirements, RBAC, authentication, authorization
  - *Details:* N/A. No new RBAC, auth, or authorization changes. Uses existing VM/KubeVirt CR permissions.

- [ ] **Usability Testing** — Validates user experience and accessibility requirements
  - *Details:* N/A. Feature is annotation-driven via CLI/API — PM confirmed UI/usability testing adds no customer value (Peter Lauterbach/16-06-2026). See "Out of Scope (Testing Scope Exclusions) - UI testing for hook opt-out configuration"

- [ ] **Monitoring** — Does the feature require metrics and/or alerts?
  - *Details:* N/A. No new metrics or alerts introduced.

**Integration & Compatibility**

- [x] **Compatibility Testing** — Ensures feature works across supported platforms, versions, and configurations
  - *Details:* OCP 4.22 with OpenShift Virtualization 4.22. The feature is also backported to earlier releases (Kubevirt 1.6, 1.7, 1.8); testing targets 4.22 only.

- [x] **Upgrade Testing** — Validates upgrade paths from previous versions
  - *Details:* Annotation-based feature with no persistent state to migrate. Upgrade path evaluation: VMs with the annotation set before upgrade will retain it after upgrade; no data migration needed.

- [x] **Dependencies** — Blocked by deliverables from other components/products
  - *Details:* OADP operator required; available in existing test infrastructure (see Test Environment II.3 and Entry Criteria II.4).

- [ ] **Cross Integrations** — Does the feature affect other features or require testing by other teams?
  - *Details:* N/A. The backup hook opt-out only affects Velero hook annotations; no other storage settings share this code path. Existing backup workflows are unchanged when the opt-out is not set.

**Infrastructure**

- [ ] **Cloud Testing** — Does the feature require multi-cloud platform testing?
  - *Details:* N/A. No cloud-specific requirements.

#### **3. Test Environment**

- **Cluster Topology:** Standard (3-master/3-worker)
- **OCP & OpenShift Virtualization Version(s):** OCP 4.22 with OpenShift Virtualization 4.22
- **CPU Virtualization:** Standard
- **Compute Resources:** Standard
- **Special Hardware:** N/A
- **Storage:** `ocs-storagecluster-ceph-rbd-virtualization`
- **Network:** Standard
- **Required Operators:** OADP Operator
- **Platform:** PSI
- **Special Configurations:** Serial test execution required for KubeVirt CR annotation tests to avoid cluster-wide side effects

#### **3.1. Testing Tools & Frameworks**

- **Test Framework:** Standard
- **CI/CD:** N/A
- **Other Tools:** Velero CLI (for backup/restore operations in Tier 2 tests)

#### **4. Entry Criteria**

The following conditions must be met before testing can begin:

- [x] Requirements and design documents are **approved and merged**
- [x] Test environment can be **set up and configured** (see Section II.3 - Test Environment)
- [x] OADP operator installed and configured

#### **5. Risks**

- [x] **Timeline/Schedule**
  - Mitigation: No risk. Feature is already merged upstream and backported.

- [x] **Test Coverage**
  - Risk: Guest agent unavailability scenario is not directly testable — standard VM images include a functioning guest agent, and there is no reliable way to simulate its absence (see Test Limitations in Section II.1).
  - Mitigation: The opt-out mechanism controls hook injection identically regardless of guest agent state. The default behavior and opt-out scenarios exercise the same code path, providing equivalent coverage. Residual risk is low.
  - *Areas with reduced coverage:* Guest agent unavailability scenario.
  - *Sign-off:* Emanuele Prella/28-05-2026

- [x] **Test Environment**
  - Mitigation: No risk. Standard cluster with OADP operator, already available in existing test infrastructure.

- [x] **Untestable Aspects**
  - Mitigation: No additional untestable aspects beyond the guest agent unavailability scenario documented under Test Coverage above.

- [x] **Resource Constraints**
  - Mitigation: No risk. Feature scope is small and test count is manageable.

- [x] **Dependencies**
  - Risk: Feature availability in downstream builds depends on the rebase schedule. Backport PRs are merged for releases 1.6, 1.7, and 1.8, but downstream availability depends on the OCP z-stream schedule.
  - Mitigation: Track the downstream rebase status and z-stream schedule; test against available builds in the interim.
  - *Third-party services or blockers:* OCP z-stream rebase schedule for downstream builds.
  - *Sign-off:* Emanuele Prella/28-05-2026

---

### **III. Test Scenarios & Traceability**

Scenarios trace to epic [CNV-79727](https://redhat.atlassian.net/browse/CNV-79727).

- **[CNV-79727]** — As a cluster administrator, I want to verify that backup hooks are present by default and that the cluster-wide opt-out dynamically adds and removes them on running VMs without requiring a restart
  - *Test Scenario:* [Tier 1] Deploy a VM without opt-out and confirm backup hooks are active. Add the opt-out annotation to the cluster configuration. Confirm backup hooks are removed from the running VM without a restart. Remove the annotation. Confirm backup hooks are restored. (Upstream — kubevirt functional tests)
  - *Priority:* P0

- **[CNV-79727]** — As a cluster administrator, I want per-VM opt-out to take precedence over the cluster-wide setting
  - *Test Scenario:* [Tier 1] Configure the cluster to opt out of backup hooks. Deploy a VM that explicitly keeps hooks enabled. Confirm backup hooks are active on that VM despite the cluster-wide opt-out. (Upstream — kubevirt functional tests)
  - *Priority:* P0

- **[CNV-79727]** — As a cluster administrator, I want to verify that the opt-out annotation is honored for a paused VM, confirming hooks are not injected regardless of VM state
  - *Test Scenario:* [Tier 2] Deploy a VM configured to opt out of backup hooks and pause it. Run a Velero backup. Confirm no hooks were attempted and the backup completed successfully.
  - *Priority:* P0

- **[CNV-79727]** — As a cluster administrator, I want to perform a full backup and restore with hooks disabled
  - *Test Scenario:* [Tier 2] Deploy a running VM with a per-VM opt-out annotation disabling backup hooks. Run a Velero backup. Delete the VM and its namespace. Restore from backup. Confirm the VM is running. Data integrity is not verified because freeze hooks are skipped.
  - *Priority:* P0

---

### **IV. Sign-off and Approval**

This Software Test Plan requires approval from the following stakeholders:

* **Reviewers:**
  - Development Representative (OCP-V): [Alvaro Romero](@alromeros), [Noam Assouline](@noamasu)
  - QE Members (OCP-V): [Dalia Frank](@dafrank), [Kateryna Shvaika](@kshvaika), [Jose Manuel Castano](@josemacassan), [Ahmad Hafe](@Ahmad-Hafe), [Jenia Peimer](@jpeimer)
* **Approvers:**
  - QE Architect (OCP-V): [Ruth Netser](@rnetser)
  - QE Member (OCP-V): [Jenia Peimer](@jpeimer)
  - PM: [Peter Lauterbach](@peterclauterbach)
