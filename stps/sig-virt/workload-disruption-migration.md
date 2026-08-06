# Openshift-virtualization-tests Test plan

## **Allow Workload Disruption Migration - Quality Engineering Plan**

### **Metadata & Tracking**

- **Enhancement(s):** [kubevirt/kubevirt#11833](https://github.com/kubevirt/kubevirt/pull/11833) (no VEP — feature predates the KubeVirt VEP process)
- **Feature Tracking:** https://issues.redhat.com/browse/VIRTSTRAT-244
- **Epic Tracking:** https://issues.redhat.com/browse/CNV-54933
- **Feature Maturity:**
  - DP: N/A
  - TP: 4.19
  - GA: 5.0.0
- **QE Owner(s):** Samuel Alberstein (@SamAlber)
- **Owning SIG:** sig-virt
- **Participating SIGs:** sig-virt

**Document Conventions:**

- AWD: Allow Workload Disruption — a migration policy option that permits the platform to pause a VM or switch to PostCopy to complete migration when standard live migration alone cannot converge.
- PostCopy: Migration mode where, after pre-copy fails to converge, the VM switches to the target node and remaining memory is fetched on-demand from the source.
- Paused: Migration mode where the VM is briefly paused to allow the final memory transfer, then resumed on the target node.

### **Feature Overview**

AWD has been available as Tech Preview since OCP-V 4.19 and reaches GA in OCP-V 5.0.

When a VM is live-migrated, the migration may fail to complete if the guest is writing to memory faster than
the platform can transfer it (high dirty rate). With the Allow Workload Disruption (AWD) migration policy, the platform is
permitted to use potentially disruptive migration modes (PostCopy or Paused) to help the migration converge
when pre-copy cannot. This is critical for operations that require migration — such as node drain
and CPU/memory hotplug — where a non-converging migration would block the operation entirely.
This allows maintenance operations to complete and in-guest processes to be preserved after migration.
AWD is configurable at the cluster level and applies to all migrations cluster-wide once enabled by the administrator.

---

### **I. Motivation and Requirements Review (QE Review Guidelines)**

This section documents the mandatory QE review process. The goal is to understand the feature's value,
technology, and testability before formal test planning.

#### **1. Requirement & User Story Review Checklist**

- [x] **Review Requirements**
  - *List the key D/S requirements reviewed:* AWD migration policy enables potentially disruptive migration modes when standard live migration cannot converge within the configured completion timeout. When PostCopy is allowed, the VM starts on the target while remaining memory is fetched on-demand. Otherwise, the VM is briefly paused to allow the final memory transfer, then resumed on the target node.

- [x] **Understand Value and Customer Use Cases**
  - *Describe the feature's value to customers:* Customers need migration to converge for maintenance operations (node drain, hotplug) even at the cost of brief disruption, rather than having migrations fail and block the operation entirely.
  - *List the customer use cases identified:*
    1. As an admin, I want to migrate a VM with AWD policy so that migration completes in PostCopy or Paused mode when pre-copy cannot converge, without terminating running guest workloads.
    2. As an admin, I want to drain a node for maintenance so that VMs with AWD policy migrate and resume without terminating running guest workloads.
    3. As an admin, I want to hotplug CPU/memory to a running VM so that AWD migration completes and the guest reflects the new resources without terminating running guest workloads.
    4. As an admin, I want to enable AWD at the cluster level so that the policy applies to all qualifying migrations cluster-wide.

- [x] **Testability**
  - *Note any requirements that are unclear or untestable:* Testable by configuring an AWD migration policy with a tight completion timeout and capped bandwidth, then verifying the migration mode after migration.

- [x] **Acceptance Criteria**
  - *List the acceptance criteria:*
    1. When pre-copy migration does not converge, migration completes successfully in the expected mode (PostCopy for RHEL and Windows guests; Paused for RHEL guests) under AWD policy when triggered by explicit migration or supported hotplug operations.
    2. After migration completes, the same process instances that were running in the guest before migration continue running with their original PIDs — no guest reboot, application restart, or process re-launch is required.
    3. When AWD is enabled at the cluster level, a VM without an explicit AWD migration policy inherits the cluster-level setting and migrates in Paused mode when pre-copy cannot converge.

- [x] **Non-Functional Requirements (NFRs)**
  - *List applicable NFRs and their targets:*
    - Monitoring: No new metrics or alerts required; migration mode is observable via existing migration status.
    - Observability: No new observability requirements.
    - UI: No UI component; PM confirmed UI testing not needed for this feature.
    - Documentation: Currently documented upstream (KubeVirt user guide) only; downstream OpenShift Virtualization product documentation expected before GA.
    - Performance: No performance targets defined for this cycle.
    - Security: RBAC enforcement is covered by existing migration policy permission model.
    - Scalability: AWD is per-VM, but relies on live migration which is subject to platform-level parallelism limits (e.g., cluster-wide concurrent migration cap). These inherited constraints are acknowledged but not newly introduced by AWD.

#### **2. Known Limitations**

The limitations are documented to ensure alignment between development, QA, and product teams.
The following are confirmed product constraints accepted before testing begins.

- **s390x does not support memory hotplug, so memory hotplug scenarios are not applicable on this architecture.**
  - *Sign-off:* Martin Tessun / 2026-06-30

- **PostCopy mode is silently suppressed for VMs with VFIO devices (host devices, GPUs, SR-IOV interfaces); AWD falls back to Paused mode instead.**
  - *Sign-off:* Jed Lejosne / 2026-07-06

- **CPU/memory hotplug is not supported on arm64; only AWD migration is validated on this architecture.**
  - *Sign-off:* Denys Shchedrivyi / 2026-08-07

#### **3. Technology and Design Review**

- [x] **Developer Handoff/QE Kickoff**
  - *Key takeaways and concerns:*
    - PostCopy mode is silently suppressed for VMs with VFIO devices; AWD falls back to Paused mode — verified manually.
    - Triggering disruptive modes requires tuning bandwidth and completion timeout; standard pre-copy will converge if resources are sufficient.
    - Cluster-level AWD configuration propagation must be validated as a dedicated test path.
    - Windows and Linux use different guest-level mechanisms for memory hotplug, requiring separate validation for each guest OS.

- [x] **Technology Challenges**
  - *List identified challenges:* Triggering Paused mode reliably requires tuning bandwidth, completion timeout, and guest memory load to ensure standard (pre-copy) live migration does not converge before the timeout.

- [x] **API Extensions**
  - *List new or modified APIs:* New migration policy option to enable disruptive migration modes, a migration status field reporting the mode used, and a cluster-level configuration option to enable AWD for all migrations.

- [x] **Test Environment Needs**
  - *See environment requirements in Section II.3 and testing tools in Section II.3.1*

- [x] **Topology Considerations**
  - *Describe topology requirements:* Requires at least 2 worker nodes for migration. Windows VMs require dedicated high-resource nodes.

### **II. Software Test Plan (STP)**

This STP serves as the **overall roadmap for testing**, detailing the scope, approach, resources, and schedule.

#### **1. Scope of Testing**

Tests validate that allow-workload-disruption (AWD) migration completes in the expected mode (PostCopy or Paused) across different migration triggers (explicit migration, CPU/memory hotplug) and guest operating systems (RHEL, Windows). RHEL tests cover both PostCopy and Paused modes; Windows tests cover PostCopy only (see Out of Scope). AWD migration scenarios are validated on both x86_64 and arm64; CPU/memory hotplug scenarios run on x86_64 only (see Known Limitations). CPU hotplug is tested with RHEL guests only (see Out of Scope). Guest process preservation — verified by confirming the same process instance (PID) started before migration remains running after migration without restart — is checked after each migration. Additionally, cluster-level AWD configuration propagation from HCO to KubeVirt is validated as a dedicated test scenario.

**Testing Goals**

- **[P0]** AWD Migration Mode: Verify AWD migration falls back to PostCopy and Paused modes when pre-copy cannot converge, with process preservation.
- **[P0]** AWD Cluster Configuration: Verify that enabling AWD at the cluster level propagates the setting from HCO to KubeVirt.
- **[P1]** AWD CPU Hotplug: Verify CPU hotplug triggers AWD migration and guest reports new CPU count with process preservation (RHEL).
- **[P1]** AWD Memory Hotplug: Verify memory hotplug triggers AWD migration and guest reports new memory amount with process preservation (RHEL, Windows).

**Out of Scope (Testing Scope Exclusions)**

The following items are explicitly Out of Scope for this test cycle and represent intentional exclusions.
No verification activities will be performed for these items, and any related issues found will not be classified as defects for this release.

- **Node drain (all guest OSes)**
  - *Rationale:* Node drain is a cluster-level operation that evicts VMs regardless of guest OS; the AWD migration path exercised during drain is identical to explicit migration, which is already covered by the migration mode tests.
  - *PM/Lead Agreement:* Denys Shchedrivyi / 2026-06-30

- **Windows Paused mode**
  - *Rationale:* Paused mode differs from PostCopy only in how the migration engine handles non-convergence (pause-and-copy vs. post-copy page faults); this is a platform-level mechanism independent of guest OS. RHEL covers Paused mode validation; Windows adds no additional code path.
  - *PM/Lead Agreement:* Denys Shchedrivyi / 2026-06-30

- **Windows CPU hotplug (CNV-15247)**
  - *Rationale:* CPU onlining is a post-switchover ACPI event that runs identically regardless of migration mode (pre-copy, Paused, or PostCopy) — the migration mode does not affect how Windows onlines a vCPU. The general hotplug suite already validates Windows CPU hotplug with the same image, so duplicating it under AWD adds no unique coverage.
  - *PM/Lead Agreement:* Denys Shchedrivyi / 2026-06-30

**Test Limitations**

- **Triggering Paused mode reliably requires tuning bandwidth, completion timeout, and guest memory load to prevent standard live migration from converging before the timeout.**
  - *Sign-off:* Denys Shchedrivyi / 2026-06-30

#### **2. Test Strategy**

**Functional**

- [x] **Functional Testing** — Validates that the feature works according to specified requirements and user stories

- [x] **Automation Testing** — Confirms test automation plan is in place for CI and regression coverage (all tests are expected to be automated)

- [x] **Regression Testing** — Verifies that new changes do not break existing functionality
  - *Details:* Tests validate both migration mode and hotplug functionality

- [ ] **Self-Validation Testing** — Should any of the new tests be included in the self-validation test package?
  - *Details:* N/A — AWD tests require bandwidth capping and tuned completion timeouts to force non-convergence; this specialized setup is not suitable for self-validation.

**Non-Functional**

- [ ] **Performance Testing** — Validates feature performance meets requirements (latency, throughput, resource usage)
  - *Details:* Not in scope for functional AWD validation

- [ ] **Scale Testing** — Validates feature behavior under increased load and at production-like scale (e.g., large number of VMs, nodes, or concurrent operations)
  - *Details:* Scale testing is deferred; AWD is validated functionally per-VM. No scale-specific concerns identified.

- [ ] **Security Testing** — Verifies security requirements, RBAC, authentication, authorization, and vulnerability scanning
  - *Details:* N/A — Migration policy RBAC is covered by core KubeVirt tests

- [ ] **Usability Testing** — Validates user experience and accessibility requirements
  - *Details:* N/A — No UI component; migration mode is reported via standard status fields

- [ ] **Monitoring** — Does the feature require metrics and/or alerts?
  - *Details:* N/A — No specific metrics required for AWD

**Integration & Compatibility**

- [x] **Compatibility Testing** — Ensures feature works across supported platforms, versions, and configurations
  - *Details:* Parametrized across RHEL and Windows guest OSes; arm64 coverage for AWD migration scenarios (hotplug excluded on arm64)
  - *Backward compatibility:* No known API changes affecting backward compatibility

- [ ] **Upgrade Testing** — Validates upgrade paths from previous versions, data migration, and configuration preservation
  - *Details:* Upgrade path evaluated; no AWD-specific upgrade concerns identified. Not in scope for this cycle.

- [x] **Dependencies** — Blocked by deliverables from other components/products. Identify what we need from other teams before we can test.
  - *Details:* AWD depends on the core virtualization engine for mode enforcement and on the cluster-level operator for propagating configuration to the migration subsystem.

- [x] **Cross Integrations** — Does the feature affect other features or require testing by other teams? Identify the impact we cause.
  - *Details:* AWD interacts with hotplug (sig-virt); tests cover migration triggered by hotplug. Node drain is excluded (see Out of Scope). Cluster-level AWD configuration propagation is validated as a dedicated test scenario (CNV-16551) within the strict reconciliation test suite.

**Infrastructure**

- [ ] **Cloud Testing** — Does the feature require multi-cloud platform testing? Consider cloud-specific features.
  - *Details:* N/A — Bare metal with RWX storage is required

#### **3. Test Environment**

- **Cluster Topology:** Bare Metal — Multi-worker OCP cluster (minimum 2 workers for migration, additional for Windows special_infra)
- **OCP & OpenShift Virtualization Version(s):** OCP 5.0 with OpenShift Virtualization 5.0 (GA); available as TP since OpenShift Virtualization 4.19
- **CPU Virtualization:** VT-x / AMD-V (x86_64); arm64 nodes for architecture-specific scenarios
- **Compute Resources:** Standard + high-resource nodes — Standard workers for RHEL; high-resource workers (special_infra) for Windows VMs
- **Special Hardware:** N/A
- **Storage:** RWX default storage class (e.g., ocs-storagecluster-ceph-rbd-virtualization)
- **Network:** OVN-Kubernetes
- **Required Operators:** OpenShift Virtualization
- **Platform:** Bare Metal
- **Special Configurations:** N/A

#### **3.1. Testing Tools & Frameworks**

- **Test Framework:** Standard
- **CI/CD:** Tests use marker-based CI lane selection to ensure they run only in environments with the required infrastructure (bare metal, RWX storage, high-resource nodes for Windows)
- **Other Tools:** N/A

#### **4. Entry Criteria**

The following conditions must be met before testing can begin:

- [x] Requirements and design documents are **approved and merged**
- [x] Test environment can be **set up and configured** (see Section II.3 - Test Environment)
- [x] AWD migration policy fields are available and functional in the target OCP-V version

#### **5. Risks**

**Timeline/Schedule**

- **Risk:** No schedule risk identified.
  - **Category:** Schedule
  - **Mitigation:** Feature was validated in TP with no known blockers to GA test development (see Feature Maturity for versions).
  - **Sign-off:** Denys Shchedrivyi / 2026-06-30

**Test Coverage**

- **Risk:** Paused mode may not reliably trigger if standard live migration converges too quickly on fast storage
  - **Category:** Technical
  - **Mitigation:** Added guest memory pressure and tuned completion timeout to ensure migration does not converge before the disruptive mode triggers
  - **Sign-off:** Denys Shchedrivyi / 2026-06-30

**Test Environment**

- **Risk:** Windows tests require special infrastructure and high-resource nodes which may not be available in all CI environments
  - **Category:** Infrastructure
  - **Mitigation:** Tests are marked for CI lane selection so they only run in environments with the required infrastructure
  - **Sign-off:** Denys Shchedrivyi / 2026-06-30

**Untestable Aspects**

- **Risk:** Whether the platform selects PostCopy or Paused mode depends on cluster load, storage speed, and network conditions — the exact mode chosen in a given run is not fully deterministic.
  - **Category:** Technical
  - **Mitigation:** Tests force non-convergence through bandwidth capping and tight completion timeouts, then verify the migration completed in the expected disruptive mode.
  - **Sign-off:** Denys Shchedrivyi / 2026-06-30

**Resource Constraints**

- **Risk:** No resource constraints identified.
  - **Category:** Resource
  - **Mitigation:** Required infrastructure (bare metal with RWX storage, high-resource nodes for Windows) is available in existing CI environments.
  - **Sign-off:** Jed Lejosne / 2026-06-30

**Dependencies**

- **Risk:** AWD behavior depends on upstream migration engine implementation; changes in convergence logic could affect mode selection
  - **Category:** External Dependency
  - **Mitigation:** Monitor upstream changes to migration convergence behavior
  - **Sign-off:** Denys Shchedrivyi / 2026-06-30

---

### **III. Test Scenarios & Traceability**

- **[CNV-15225]** — As an admin, I want AWD migration to complete in PostCopy mode when pre-copy cannot converge (RHEL).
  - *Test Scenario:* [Tier 2] Migrate RHEL VM with AWD policy (PostCopy allowed); verify migration completes in PostCopy mode and background process (PID) is preserved.
  - *Priority:* P0

- **[CNV-15225]** — As an admin, I want AWD migration to complete in Paused mode when pre-copy cannot converge and PostCopy is not allowed (RHEL).
  - *Test Scenario:* [Tier 2] Migrate RHEL VM with AWD policy (PostCopy not allowed); verify migration completes in Paused mode and background process (PID) is preserved.
  - *Priority:* P0

- **[CNV-15246]** — As an admin, I want AWD migration to complete in PostCopy mode when pre-copy cannot converge (Windows).
  - *Test Scenario:* [Tier 2] Migrate Windows VM with AWD policy (PostCopy allowed); verify migration completes in PostCopy mode and background process is preserved.
  - *Priority:* P0

- **[CNV-15234]** — As an admin, I want CPU hotplug to trigger AWD migration and reflect the new CPU count in the guest (RHEL).
  - *Test Scenario:* [Tier 2] Hotplug CPU sockets on RHEL VM with AWD policy; verify migration completes in the expected AWD mode (PostCopy when allowed, Paused otherwise), guest reports the new CPU count, and background process (PID) is preserved.
  - *Priority:* P1

- **[CNV-15235]** — As an admin, I want memory hotplug to trigger AWD migration and reflect the new memory amount in the guest (RHEL).
  - *Test Scenario:* [Tier 2] Hotplug memory on RHEL VM with AWD policy; verify migration completes in the expected AWD mode (PostCopy when allowed, Paused otherwise), guest reports the new memory amount, and background process (PID) is preserved.
  - *Priority:* P1

- **[CNV-16312]** — As an admin, I want memory hotplug to trigger AWD migration and reflect the new memory amount in the guest (Windows).
  - *Test Scenario:* [Tier 2] Hotplug memory on Windows VM with AWD policy (PostCopy allowed); verify migration completes in PostCopy mode, guest reports the new memory amount, and background process (PID) is preserved.
  - *Priority:* P1

- **[CNV-16551]** — As an admin, I want to enable AWD at the cluster level and have the configuration propagate to the migration subsystem.
  - *Test Scenario:* [Tier 2, Gating] Enable AWD in the cluster-level migration configuration (HCO); verify the setting propagates to KubeVirt — confirming the cluster-level configuration is accepted and reconciled.
  - *Priority:* P0

---

### **IV. Sign-off and Approval**

This Software Test Plan requires approval from the following stakeholders:

* **Reviewers:**
  - QE Architect (OCP-V): [Ruth Netser](@rnetser)
  - QE Members (OCP-V): [Akriti Gupta](@akri3i), [Samuel Alberstein](@SamAlber)
  - Principal QE (OCP-V): [Denys Shchedrivyi](@dshchedr), [Vasiliy Sibirskiy](@vsibirsk)
  - Principal Developer (OCP-V): [Jed Lejosne](@jean-edouard)
  - Product Manager/Owner: [Martin Tessun](@mtessun)

* **Approvers:**
  - QE Architect (OCP-V): [Ruth Netser](@rnetser)
  - Principal QE (OCP-V): [Denys Shchedrivyi](@dshchedr), [Vasiliy Sibirskiy](@vsibirsk)
  - Principal Developer (OCP-V): [Jed Lejosne](@jean-edouard)
  - Product Manager/Owner: [Martin Tessun](@mtessun)
