# Openshift-virtualization-tests Test plan

## **mDev-based vGPU Live Migration - Quality Engineering Plan**

### **Metadata & Tracking**

- **Enhancement(s):** [RHEL-13008](https://redhat.atlassian.net/browse/RHEL-13008)
- **Feature Tracking:** [VIRTSTRAT-589](https://redhat.atlassian.net/browse/VIRTSTRAT-589)
- **Epic Tracking:** [CNV-88979](https://redhat.atlassian.net/browse/CNV-88979)
- **Feature Maturity:**
  - DP: v5.0.0
  - TP: v5.2.0
  - GA: TBD
- **QE Owner(s):** Akriti Gupta (@akri3i)
- **Owning SIG:** sig-virt
- **Participating SIGs:** sig-virt

**Document Conventions:**

- **mdev** — Mediated device: the vGPU device type covered by this STP
- **AWD (Allow Workload Disruption)** — Existing migration policy that permits the platform to use PostCopy
  or Paused mode when standard live migration cannot converge on its own
- **vGPU** — Virtual GPU: GPU virtualization that allows a VM to consume a virtualized slice of a physical GPU

### **Feature Overview**

This feature enables live migration of VMs with a single NVIDIA mdev-based vGPU device attached, allowing
GPU-accelerated workloads to move between compatible nodes without shutting down the VM. It matters to
cluster operators who need to perform GPU node maintenance and hardware lifecycle operations without
disrupting GPU-accelerated workloads and to customers migrating
virtual desktop and AI/ML workloads.

This STP targets the **Tech Preview phase** ([CNV-88979](https://redhat.atlassian.net/browse/CNV-88979))

---

### **I. Motivation and Requirements Review (QE Review Guidelines)**

This section documents the mandatory QE review process. The goal is to understand the feature's value,
technology, and testability before formal test planning.

#### **1. Requirement & User Story Review Checklist**

- [x] **Review Requirements**
  - *List the key D/S requirements reviewed:*
    - A VM with a single mdev-based NVIDIA vGPU device can be live migrated between two nodes with
      compatible GPU hardware (same GPU type on source and target).
    - Migration completes without guest kernel crash, and the vGPU device reinitializes correctly on the
      target node after migration.
    - Migration failure scenarios (e.g., no compatible/available vGPU capacity on any target) are handled
      gracefully.
    - Because vGPU workloads maintain a persistent dirty-memory rate even when idle, vGPU migrations
      require the Allow Workload Disruption (AWD) migration policy to converge; PostCopy mode is silently
      suppressed for VFIO devices (including vGPU), so AWD convergence for vGPU migrations happens via
      Paused mode only (see [workload-disruption-migration.md](./workload-disruption-migration.md)).

- [x] **Understand Value and Customer Use Cases**
  - *Describe the feature's value to customers:* Cluster operators need to perform GPU node maintenance without shutting down GPU-accelerated workloads.

  - *List the customer use cases identified:*
    - As a cluster operator, I want to drain and perform maintenance on a GPU node without shutting down
      VMs that have a vGPU attached.
    - As an AI/ML platform team, I want to move a GPU-accelerated VM to another node while the workload
      keeps running, to maintain SLA compliance during infrastructure lifecycle events.
    - As a VM owner migrating from VMware, I want vGPU live migration to behave similarly to what I had on
      VMware, so I do not need to redesign my maintenance workflows.

- [x] **Testability**
  - *Note any requirements that are unclear or untestable:* None — all acceptance criteria are observable
    via VM/guest state and migration status.

- [x] **Acceptance Criteria**
  - *List the acceptance criteria:*
    - A VM with a single mdev-based vGPU live migrates between two compatible nodes, reaches Running state
      on the target, and the guest remains healthy throughout (no kernel crash during or after migration).
    - The vGPU device reinitializes correctly inside the guest post-migration.
    - A guest process/workload running before migration continues running (same PID, no restart) after
      migration completes.
    - When migration cannot succeed at all (e.g., no compatible/available vGPU capacity on any target
      node), the migration fails gracefully and the source VM remains Running and unaffected.
  - *Note any gaps or missing criteria:* None

- [x] **Non-Functional Requirements (NFRs)**
  - *List applicable NFRs and their targets:*
    - **Reliability:** vGPU device must be visible inside the guest after migration.
    - **Performance:** N/A — CNV QE performs functional testing only; performance benchmarking is out of
      scope for this STP (tracked separately in [CNV-81224](https://redhat.atlassian.net/browse/CNV-81224)).
    - **Documentation:** tracked for TP [CNV-71638](https://redhat.atlassian.net/browse/CNV-71638).
  - *Note any NFRs not covered and why:*
    - **Monitoring:** N/A — no new metrics or alerts introduced by this feature this cycle.
    - **Scalability:** No new scale requirements introduced by this feature.
    - **Security:** N/A — no new security surface; migration uses the existing RBAC/migration policy
      permission model.
    - **UI:** No UI component is introduced. Usability coverage for this cycle is limited to migration
      status/event feedback (see Section II.2 Usability Testing).
      *PM/UX Agreement:* [Name/Date — pending confirmation that no dedicated UI testing is required]

#### **2. Known Limitations**

The limitations are documented to ensure alignment between development, QA, and product teams.
The following are confirmed product constraints accepted before testing begins.

- **Only a single vGPU per VM is supported for live migration.** The VM must request exactly one NVIDIA
  vGPU exposed as a mediated device (mdev). PCI GPU passthrough is not migratable at all, SR-IOV vGPUs are
  not supported by this feature, and VMs with multiple vGPUs are not supported (multi-vGPU migration is
  planned for Beta) (source: [upstream docs](https://kubevirt.io/user-guide/compute/live_migration/#live-migration-with-nvidia-vgpus)).
  - *Sign-off:* [Name/Date]

- **Migration is only supported between same-GPU-type nodes; cross-vendor and cross-architecture vGPU
  migration are not supported.**
  - *Sign-off:* [Name/Date]

- **Guest OS and guest-side constraints.** The guest must run a supported version of Windows or Linux
  with NVIDIA guest drivers compatible with the host Virtual GPU Manager. Migration fails if the guest has
  CUDA unified memory, a GPU debugger, or a GPU profiler enabled (NVIDIA vendor requirement).
  - *Sign-off:* [Name/Date]

- **Post-copy migration is not available for vGPU-attached VMs (VFIO limitation).** Migrations that
  cannot converge via standard pre-copy require the Allow Workload Disruption (AWD) policy and converge
  only via Paused mode.
  - *Sign-off:* [Name/Date]

- **Reported "remaining bytes" migration statistics do not include VFIO/vGPU device state; progress and
  ETA reporting for vGPU migrations is inaccurate until upstream QEMU/libvirt changes land.**
  - *Sign-off:* [Name/Date]

- **vGPU live migration is gated behind a dedicated feature gate and is not enabled by
  default; it must be explicitly enabled at the cluster level before any vGPU VM can migrate.**
  - *Sign-off:* [Name/Date]

- **mdev-based vGPU (and its live migration) applies to pre-Ampere NVIDIA GPU hardware. Ampere-generation
  and newer GPUs use SR-IOV-based vGPU, which has separate live migration enablement tracked under
  [CNV-75316](https://redhat.atlassian.net/browse/CNV-75316) and is not covered by this STP.**
  - *Sign-off:* [Name/Date]


#### **3. Technology and Design Review**

- [ ] **Developer Handoff/QE Kickoff**
  - *Key takeaways and concerns:*
    - PostCopy is not available for VFIO/vGPU devices — AWD-driven vGPU migrations always target Paused
      mode, never PostCopy.

- [x] **Technology Challenges**
  - *List identified challenges:*
    - Requires NVIDIA mdev-capable GPU hardware (pre-Ampere for RHCOS10 nodes) on at least two worker
      nodes with the NVIDIA GPU Operator configured for mdev vGPU.
    - Feature is alpha upstream; the AWD migration policy must be configured to reliably trigger Paused
      mode for most vGPU migration scenarios.
  - *Impact on testing approach:* Tests can only execute on nodes with mdev-capable NVIDIA GPU hardware;
    standard CI nodes cannot run these tests. Test design must explicitly configure AWD migration policy
    rather than relying on default pre-copy behavior.

- [x] **API Extensions**
  - *List new or modified APIs:* A new cluster-level feature gate (Alpha) must be explicitly enabled
    before any vGPU VM is permitted to migrate. VMs continue to request a vGPU device the same way as
    existing mdev vGPU workflows, no change to VM-facing device request APIs. Live migration behavior for
    vGPU-attached VMs changes from "migration blocked" to "migration supported under AWD" once the feature
    gate is enabled.
  - *Testing impact:* Existing vGPU VM creation tests are unaffected. New coverage is required for:
    (1) feature-gate-disabled behavior (migration remains blocked), (2) feature-gate-enabled migration
    behavior, and (3) migration-specific scenarios (see Testing Goals and Section III).

- [x] **Test Environment Needs**
  - *See environment requirements in Section II.3 and testing tools in Section II.3.1*

- [x] **Topology Considerations**
  - *Describe topology requirements:* At least two worker nodes with the same NVIDIA mdev-capable GPU
    model (e.g., pre-Ampere, Tesla T4), running RHCOS10.x, with the NVIDIA GPU Operator installed and configured
    for mdev vGPU.
  - *Impact on test design:* Tests must use node selectors/affinity to place the VM on a source GPU node
    and target a compatible destination GPU node for migration.

### **II. Software Test Plan (STP)**

This STP serves as the **overall roadmap for testing**, detailing the scope, approach, resources, and schedule.

#### **1. Scope of Testing**

This STP covers Tech Preview functional validation of mdev-based single vGPU live migration: successful
migration, guest-visible GPU functionality and process preservation post-migration, AWD-driven convergence,
and graceful failure handling. CNV QE performs functional testing only; performance benchmarking is owned
separately and tracked in [CNV-81224](https://redhat.atlassian.net/browse/CNV-81224) (see Out of Scope).

**Testing Goals**

- **[P0]** Verify vGPU VM migration remains blocked while the vGPU live migration feature gate is disabled,
  and becomes permitted once the feature gate is enabled at the cluster level.
- **[P0]** Verify a VM with a single mdev-based NVIDIA vGPU live migrates between two compatible GPU nodes,
  reaches Running state on the target, and the vGPU device is visible in the guest post-migration.
- **[P0]** Verify a guest process/workload running before migration continues running (same PID, no restart)
  after a vGPU VM migration completes.
- **[P0] [Negative]** Verify a vGPU VM migration fails gracefully when no compatible/available vGPU capacity
  exists on any target node: the source VM remains Running and unaffected, and the failure is observable via
  VM/migration status.
**Out of Scope (Testing Scope Exclusions)**

The following items are explicitly Out of Scope for this test cycle and represent intentional exclusions.
No verification activities will be performed for these items, and any related issues found will not be
classified as defects for this release.

- **Multi-vGPU-per-VM live migration**
  - *Rationale:* Not supported by the feature this cycle; only single-vGPU-per-VM migration is implemented
    upstream.
  - *PM/Lead Agreement:* [Name/Date]

- **Cross-architecture and cross-vendor vGPU migration**
  - *Rationale:* Excluded from feature scope; only same-GPU-type, same-architecture node-to-node migration
    is supported upstream.
  - *PM/Lead Agreement:* [Name/Date]

- **SR-IOV-based vGPU live migration**
  - *Rationale:* Tracked as a separate feature/epic ([CNV-75316](https://redhat.atlassian.net/browse/CNV-75316))
    targeting Ampere-generation and newer GPU hardware on RHCOS10.x, with a different underlying migration
    mechanism.
  - *PM/Lead Agreement:* [Name/Date]

- **Node-drain-triggered vGPU migration**
  - *Rationale:* Node drain exercises the same AWD migration code path already covered by explicit
    migration scenarios in this STP; no unique coverage is added by testing it separately this cycle.
  - *PM/Lead Agreement:* [Name/Date]

- **Concurrent/scale vGPU migrations (multiple VMs migrating simultaneously)**
  - *Rationale:* Tech Preview scope is single-VM functional validation; scale considerations are deferred
    until the feature approaches GA readiness.
  - *PM/Lead Agreement:* [Name/Date]

- **Performance/downtime benchmarking and hypervisor tuning (multifd, compression, RDMA)**
  - *Rationale:* CNV QE performs functional testing only. Performance optimization work is owned by a
    separate team and tracked in [CNV-81224](https://redhat.atlassian.net/browse/CNV-81224).
  - *PM/Lead Agreement:* [Name/Date]

**Test Limitations**

- **The upstream implementation is still Alpha state (only basic unit tests exist upstream); full E2E
  automated coverage is a Tech-Preview-cycle target. Automation for this STP is limited by what is
  feasible against the current alpha implementation.**
  - *Sign-off:* [Name/Date]

- **Testing is limited to the pre-Ampere NVIDIA Tesla T4 GPU — the only mdev-capable GPU model available for RHCOS 10 nodes ; other supported vGPU-capable NVIDIA GPUs are not validated.**
  - *Sign-off:* [Name/Date]

#### **2. Test Strategy**

**Functional**

- [x] **Functional Testing** — Validates that the feature works according to specified requirements and user stories
  - *Details:* Covers feature-gate enforcement, successful single-vGPU migration with guest-visible GPU
    functionality, process preservation post-migration, and graceful handling of migration failure
    (see Testing Goals).

- [ ] **Automation Testing** — Confirms test automation plan is in place for CI and regression coverage
  - *Details:* Getting started this cycle per Tech Preview entry criteria
    ([CNV-88979](https://redhat.atlassian.net/browse/CNV-88979)). Validation this cycle remains largely
    manual/exploratory due to the alpha state of the upstream implementation; automation coverage in the
    openshift-virtualization-tests framework will expand as the feature matures.

- [ ] **Regression Testing** — Verifies that new changes do not break existing functionality
  - *Details:* N/A this cycle — the feature is new with no prior migration behavior to
    regress against. Existing non-migration mdev vGPU VM creation/consumption tests
    are unaffected by this feature and are not re-run here.

- [ ] **Self-Validation Testing**
  - *Details:* N/A — requires specialized mdev-capable GPU hardware not available in self-validation
    environments.

**Non-Functional**

- [ ] **Performance Testing**
  - *Details:* N/A — CNV QE performs functional testing only. Performance benchmarking (migration
    time/downtime, hypervisor tuning) is owned by a separate team and tracked in
    [CNV-81224](https://redhat.atlassian.net/browse/CNV-81224) (see Out of Scope).

- [ ] **Scale Testing**
  - *Details:* N/A this cycle — see Out of Scope (concurrent/scale vGPU migrations).

- [ ] **Security Testing**
  - *Details:* N/A — no new security surface; migration uses the existing RBAC/migration policy
    permission model.

- [x] **Usability Testing** — Validate that VM/migration status and events provide clear feedback when a
  vGPU VM migration succeeds or fails.
  - *Details:* No UI component is introduced; usability coverage is limited to status/event clarity for
    the negative/failure-path Testing Goals.

- [ ] **Monitoring**
  - *Details:* N/A — no new metrics or alerts introduced by this feature this cycle.

**Integration & Compatibility**

- [x] **Compatibility Testing** — Ensures feature works across supported platforms, versions, and configurations
  - *Details:* Tests run on the target OCP/OpenShift Virtualization Tech Preview version with RHCOS10.x
    worker nodes and the NVIDIA GPU Operator configured for mdev vGPU. Limited to the single available
    GPU model (pre-Ampere NVIDIA Tesla T4; see Test Limitations).

- [ ] **Upgrade Testing**
  - *Details:* N/A this cycle — the feature is new; there is no prior version to upgrade from within
    this migration capability. Upgrade path will be evaluated at GA.

- [x] **Dependencies** — Blocked by deliverables from other components/products.
  - *Details:* Depends on: (1) the NVIDIA GPU Operator/vGPU Manager driver stack, and (2) the upstream
    KubeVirt mdev live migration alpha implementation
    ([kubevirt/kubevirt#16675](https://github.com/kubevirt/kubevirt/pull/16675)).

- [x] **Cross Integrations** — Does the feature affect other features or require testing by other teams?
  - *Details:* Interacts with Allow Workload Disruption
    (see [workload-disruption-migration.md](./workload-disruption-migration.md)); most vGPU migrations
    require it to converge.

**Infrastructure**

- [ ] **Cloud Testing**
  - *Details:* N/A — feature requires bare-metal nodes with NVIDIA mdev-capable GPU hardware.

#### **3. Test Environment**

- **Cluster Topology:** Bare-metal, minimum 2 worker nodes with NVIDIA mdev-capable GPU hardware
  (same GPU model on both nodes), plus standard control plane

- **OCP & OpenShift Virtualization Version(s):** OCP/OpenShift Virtualization 5.2 (Tech Preview target;
  upstream implementation is Alpha as of KubeVirt v1.9)

- **CPU Virtualization:** VT-x (Intel) or AMD-V enabled

- **Compute Resources:** Standard for control plane; GPU nodes sized per NVIDIA Tesla T4 requirements

- **Special Hardware:** NVIDIA Tesla T4 GPU (pre-Ampere, mdev-capable) on at least 2 worker nodes — same
  GPU model required on source and target nodes (migration between same-GPU-type nodes only)

- **Storage:** ocs-storagecluster-ceph-rbd-virtualization

- **Network:** OVN-Kubernetes, IPv4

- **Required Operators:** NVIDIA GPU Operator (vGPU Manager configured for mdev mode)

- **Platform:** Bare metal

- **Special Configurations:** Worker nodes hosting the vGPU must run RHCOS10.x (mdev vGPU is supported
  on RHCOS10.x for pre-Ampere GPU hardware); the vGPU live migration feature gate (Alpha) must be
  enabled at the cluster level; Allow Workload Disruption migration policy must be configured to allow
  vGPU Live migrations

#### **3.1. Testing Tools & Frameworks**

- **Test Framework:** Standard (openshift-virtualization-tests)

- **CI/CD:** N/A — no dedicated lane exists yet

- **Other Tools:** N/A

#### **4. Entry Criteria**

The following conditions must be met before testing can begin:

- [ ] Requirements and design documents are **approved and merged** — pending upstream Beta-readiness
  design decisions (accurate VFIO remaining-bytes reporting); alpha implementation is merged
- [ ] Test environment can be **set up and configured** (see Section II.3)
- [ ] NVIDIA GPU Operator is installed and mdev vGPU mode is configured on the target GPU nodes
- [ ] The vGPU live migration feature gate (Alpha) is available and can be enabled in the target
  OpenShift Virtualization version
- [ ] Allow Workload Disruption migration policy is available and configurable in the target
  OCP/OpenShift Virtualization version

#### **5. Risks**

**Timeline/Schedule**

- **Risk:** The feature is still alpha upstream with unresolved gaps. These gaps may not close before
  the CNV v5.2.0 Tech Preview target.
  - **Mitigation:** This STP's scope is scoped to what is testable against the current alpha
    implementation; re-scope if upstream gaps change materially before v5.2.0.
  - *Estimated impact on schedule:* Tech Preview test execution may be compressed if upstream gaps close
    late in the cycle.
  - *Sign-off:* [Name/Date]

**Test Coverage**

- **Risk:** No E2E/automated coverage exists upstream yet — only unit tests. This STP's scenarios are
  largely manual/exploratory pending automation.
  - **Mitigation:** Prioritize manual validation of P0 scenarios; expand automation coverage as
    the Tech Preview cycle progresses.
  - *Areas with reduced coverage:* Scale/concurrent migration, SR-IOV vGPU migration
    (separate epic).
  - *Sign-off:* [Name/Date]

**Test Environment**

- **Risk:** This feature requires specific bare-metal hardware (worker nodes with a pre-Ampere
  mdev-capable NVIDIA GPU); bare-metal capacity with this GPU hardware has lower availability.
  - **Mitigation:** Coordinate with DevOps QE for cluster scheduling and availability of this hardware.
  - *Missing or unavailable environments:* Additional bare-metal nodes with pre-Ampere mdev-capable
    NVIDIA GPU hardware.
  - *Sign-off:* [Name/Date]

**Untestable Aspects**

- **Risk:** No risk identified — all acceptance criteria in scope for this cycle are observable via
  VM/guest state and migration status.
  - **Mitigation:** N/A

**Resource Constraints**

- **Risk:** None identified.
  - **Mitigation:** N/A

**Dependencies**

- **Risk:** This STP depends on the upstream KubeVirt mdev live migration implementation maturing past
  alpha (accurate VFIO remaining-bytes reporting in QEMU 11.1+/libvirt) and on the NVIDIA GPU
  Operator/driver stack; slippage in either blocks further test scope expansion.
  - **Mitigation:** Track upstream KubeVirt/QEMU/libvirt changes; re-scope this STP once dependencies land.
  - *Third-party services or blockers:* NVIDIA GPU Operator/driver stack; upstream QEMU/libvirt VFIO
    migration state reporting.
  - *Sign-off:* [Name/Date]

---

### **III. Test Scenarios & Traceability**

- **[CNV-36585](https://redhat.atlassian.net/browse/CNV-36585)** — As a cluster operator, I want vGPU VM
  migration to remain blocked until I explicitly opt in, since this is an Alpha feature.
  - *Test Scenario:* [Tier 2] With the vGPU live migration feature gate disabled, attempt to migrate a VM
    with a mdev-based vGPU; verify the migration is rejected/blocked. Enable the feature gate and verify
    the same migration now proceeds and succeeds.
  - *Priority:* P0

- **[CNV-36585](https://redhat.atlassian.net/browse/CNV-36585)** — As a cluster operator, I want to live
  migrate a VM with a single mdev-based vGPU between compatible nodes so I can perform GPU node maintenance
  without shutting down the workload.
  - *Test Scenario:* [Tier 2] Start a guest workload/process on a VM with a single mdev-based vGPU; migrate
    the VM from one compatible GPU node to another. Verify the VM reaches Running state on the target, the
    vGPU device is visible inside the guest post-migration, and the same guest process (PID) continues
    running without restart after migration completes.
  - *Priority:* P0

- **[CNV-36585](https://redhat.atlassian.net/browse/CNV-36585)** — As a cluster operator, when no compatible
  vGPU capacity is available on any target node, I want the migration to fail without impacting my running VM.
  - *Test Scenario:* [Tier 2] With all mdev vGPU capacity on candidate target nodes already consumed,
    initiate migration of a vGPU VM; verify the migration fails, the source VM remains Running and
    unaffected, and the failure is observable via VM/migration status or events.
  - *Priority:* P0

---

### **IV. Sign-off and Approval**

This Software Test Plan requires approval from the following stakeholders:

* **Reviewers:**
  - QE Owner: Akriti Gupta (@akri3i)
  - QE Member: dshchedr / @dshchedr
  - QE Member: vsibirsk / @vsibirsk
  - QE Member: SamAlber / @SamAlber
  - QE Architect: Ruth Netser / @rnetser
* **Approvers:**
  - QE Member: dshchedr / @dshchedr
  - QE Member: vsibirsk / @vsibirsk
  - QE Architect: Ruth Netser / @rnetser
  - Product Manager: Sudhakar Molli / @smolli-byte, Martin Tessun / @mtessun
  - Dev Lead: Barak Mordehai / @Barakmor1
