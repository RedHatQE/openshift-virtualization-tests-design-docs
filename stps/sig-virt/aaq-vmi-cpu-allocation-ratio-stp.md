# Openshift-virtualization-tests Test plan

## **Adding Support for vmiCPUAllocationRatio in AAQ VirtualResources Config**

### **Metadata & Tracking**

- **Enhancement(s):** TBD
- **Feature Tracking:** TBD
- **Epic Tracking:** https://redhat.atlassian.net/browse/CNV-73947
- **QE Owner(s):** Akriti Gupta (akritigupta@redhat.com)
- **Owning SIG:** sig-virt
- **Participating SIGs:** sig-virt

**Document Conventions:**

- **AAQ:** Application Aware Quota — a KubeVirt component that enforces resource quotas for VM workloads
- **ARQ:** ApplicationAwareResourceQuota — the CRD used to define per-namespace quotas in AAQ
- **HCO:** HyperConverged Cluster Operator

### **Feature Overview**

The `vmiCPUAllocationRatio` field in HCO's `spec.deployment.virtualization` controls how VM CPU counts are
translated into Kubernetes CPU resource requests. The VM CPU count is derived from
`spec.domain.cpu.cores × spec.domain.cpu.sockets × spec.domain.cpu.threads`; with the ratio applied, the
effective CPU usage = VM CPU count ÷ ratio.

When `vmiCalcConfigName: GuestEffectiveResources` is set in HCO, AAQ tracks quota usage directly from the
VM guest spec — not from the virt-launcher pod's resource requests. This means:

- **CPU quota:** `spec.domain.cpu` (total) ÷ `vmiCPUAllocationRatio` — the ratio is applied, so a VM with
  10 CPUs and ratio 1:10 consumes only 1 CPU unit of quota.
- **Memory quota:** `spec.domain.memory.guest` — memory overhead added by KubeVirt (e.g., QEMU overhead,
  virtio devices) is not counted against the quota.

This is in contrast to `VmiPodUsage`, which tracks the virt-launcher pod's actual `resources.requests`,
and would therefore include memory overhead and require users to explicitly configure both
`spec.domain.memory.guest` and `spec.resources.requests.memory`.

**Why AAQ is required for live migration:**

When a VM migrates, KubeVirt creates a second virt-launcher pod on the destination node while the source
pod is still running. Without AAQ, this would immediately exhaust the namespace `ResourceQuota` and cause
the migration to fail. AAQ solves this through **dynamic quota management**: it is aware of the migration
lifecycle and uses its scheduling gate mechanism to temporarily allow the migration pod to schedule, holding
back other new VMs in the namespace if needed. Once migration completes and the source pod is deleted, quota
returns to normal. This means the quota only needs to cover steady-state resources (`memory.guest` per
running VM) — no extra headroom for migration needs to be pre-allocated.

Without this feature, ARQ with `GuestEffectiveResources` would count raw VM CPU counts against the quota
rather than the ratio-adjusted units, causing VMs to be incorrectly gated on CPU-overcommitted clusters.

---

### **I. Motivation and Requirements Review (QE Review Guidelines)**

This section documents the mandatory QE review process. The goal is to understand the feature's value,
technology, and testability before formal test planning.

#### **1. Requirement & User Story Review Checklist**

- [x] **Review Requirements**
  - *List the key D/S requirements reviewed:* When `vmiCalcConfigName: GuestEffectiveResources` and
    `vmiCPUAllocationRatio: N` are set in HCO, ARQ `status.used.requests.cpu` must reflect
    `(cores × sockets × threads) ÷ ratio`, not the raw CPU count
    (e.g., 10 CPUs with ratio 1:10 → quota usage of 1)
  - *Pre-existing behaviour to verify has not regressed:* `GuestEffectiveResources` tracks
    `spec.domain.memory.guest` for memory quota — memory overhead and migration overhead are not counted;
    this is unchanged by this feature but must still pass

- [x] **Understand Value and Customer Use Cases**
  - *Describe the feature's value to customers:* Customers running CPU-overcommitted clusters need AAQ to
    honour the same ratio used by KubeVirt so quota is enforced accurately
  - *List the customer use cases identified:* Admin sets ratio 1:10 in HCO; a VM with 10 CPU sockets
    should consume only 1 CPU unit of quota, enabling higher VM density under a fixed quota; the admin
    configures only `spec.domain.cpu.sockets` and `spec.domain.memory.guest`.

- [x] **Testability**
  - *Note any requirements that are unclear or untestable:* None — testable by inspecting ARQ `status.used`
    fields and virt-launcher pod resource requests after VM creation

- [x] **Acceptance Criteria**
  - *List the acceptance criteria:*
    - ARQ `status.used.requests.cpu` equals `(cores × sockets × threads) ÷ ratio`
    - Second VM is gated when quota is exhausted; quota increase unblocks it automatically
  - *Regression criteria:* ARQ `status.used.requests.memory` continues to equal `spec.domain.memory.guest`
    with no overhead counted.
  - *Note any gaps or missing criteria:* None

- [x] **Non-Functional Requirements (NFRs)**
  - *List applicable NFRs and their targets:* No new metrics/alerts required; existing AAQ and KubeVirt
    monitoring is sufficient
  - *Note any NFRs not covered and why:* None

#### **2. Known Limitations**

The limitations are documented to ensure alignment between development, QA, and product teams.
The following are confirmed product constraints accepted before testing begins.

- **Only `GuestEffectiveResources` calc mode is in scope** — Other `vmiCalcConfigName` values are not
  affected by this change and are not tested here.

#### **3. Technology and Design Review**

- [x] **Developer Handoff/QE Kickoff**
  - *Key takeaways and concerns:* Dev suggested the following must be tested:
    - Changing the counting configuration in HCO to `GuestEffectiveResources` works correctly
      (HCO must support setting `vmiCalcConfigName: GuestEffectiveResources` — a bug was found and
      fixed in https://redhat.atlassian.net/browse/CNV-83233 /
      https://github.com/kubevirt/hyperconverged-cluster-operator/pull/4093)
    - When `vmiCPUAllocationRatio` is set, it is taken into account by AAQ: a VMI with 10 CPUs and
      ratio 1:10 should count as only 1 CPU in the quota
    - Memory overhead (and migration overhead) must continue to be ignored for `requests.memory` in
      the quota — i.e., quota tracks `memory.guest`, not the pod's actual memory request

- [x] **Technology Challenges**
  - *List identified challenges:* AAQ scheduling gates are asynchronous; test must poll ARQ status and pod
    conditions rather than asserting immediately after VM creation
  - *Impact on testing approach:* Use sufficiently long timeouts and event-driven polling; align with
    existing AAQ test patterns

- [x] **API Extensions**
  - *List new or modified APIs:* HCO `spec.deployment.applicationAwareConfig.vmiCalcConfigName` (existing field);
    HCO `spec.deployment.virtualization.vmiCPUAllocationRatio` (existing field); no new CRD fields
  - *Testing impact:* No new test infrastructure required; existing HCO patching patterns apply

- [x] **Test Environment Needs**
  - *See environment requirements in Section II.3 and testing tools in Section II.3.1*

- [x] **Topology Considerations**
  - *Describe topology requirements:* Live migration test requires ≥ 2 schedulable worker nodes
  - *Impact on test design:* Minimum 3-master/3-worker cluster required

### **II. Software Test Plan (STP)**

This STP serves as the **overall roadmap for testing**, detailing the scope, approach, resources, and schedule.

#### **1. Scope of Testing**

Verify that when HCO is configured with `vmiCalcConfigName: GuestEffectiveResources` and
`vmiCPUAllocationRatio: 10`, the AAQ controller correctly applies the ratio to ARQ quota accounting for
VMI CPU and memory resources, live migration continues to work, and quota exhaustion gates further VM
scheduling until quota is raised.

**Testing Goals**

- **[P0]** Verify ARQ `status.used.requests.cpu` equals `(cores × sockets × threads) ÷ vmiCPUAllocationRatio`
  (not raw CPU count) when a VM is running.
- **[P0]** Verify ARQ `status.used.requests.memory` equals `spec.domain.memory.guest`.
- **[P0]** Verify VM live migration succeeds with the ratio configuration active
- **[P0]** Verify a second VM is scheduling-gated (`SchedulingGated`) when ARQ quota is exhausted
- **[P0]** Verify the gated VM starts automatically after ARQ quota is increased to accommodate it

**Out of Scope (Testing Scope Exclusions)**

The following items are explicitly Out of Scope for this test cycle and represent intentional exclusions.
No verification activities will be performed for these items, and any related issues found will not be
classified as defects for this release.

- **Other `vmiCalcConfigName` modes (e.g., `VmiPodUsage`)**
  - *Rationale:* This change specifically targets `GuestEffectiveResources`; other modes are unchanged
  - *PM/Lead Agreement:* [ ] Name/Date

- **Multiple ratio values (e.g., 1:1, 1:4)**
  - *Rationale:* Ratio of 10 is representative; the ratio application is a single arithmetic operation
  - *PM/Lead Agreement:* [ ] Name/Date

- **Upgrade testing**
  - *Rationale:* Out of scope for this release
  - *PM/Lead Agreement:* [ ] Name/Date

- **Windows guest OS**
  - *Rationale:* Fedora-based guests are sufficient
  - *PM/Lead Agreement:* [ ] Name/Date

**Test Limitations**

- None — reviewed and confirmed that no test limitations apply for this release.

---

#### **2. Test Strategy**

**Functional**

- [x] **Functional Testing** — Validates ARQ quota accounting with `vmiCPUAllocationRatio`, scheduling
  gating, and quota expansion

- [x] **Automation Testing** — All test scenarios to be automated in the `openshift-virtualization-tests`
  repository

- [x] **Regression Testing** — Existing AAQ tests must continue to pass after this change

**Non-Functional**

- [ ] **Performance Testing** — N/A; no performance requirements defined for this feature
- [ ] **Scale Testing** — N/A; quota accounting logic is per-namespace and does not require scale validation
- [ ] **Security Testing** — N/A; no new RBAC or auth changes introduced
- [x] **Usability Testing** — Validate VM `status` conditions surface clear messaging when a VM is
  scheduling-gated
  - *Details:* Verify VM condition shows `Reason: SchedulingGated` and
    `Message: Scheduling is blocked due to non-empty scheduling gates`
- [ ] **Monitoring** — N/A; no new metrics or alerts required

**Integration & Compatibility**

- [x] **Compatibility Testing** — N/A
- [ ] **Upgrade Testing** — Out of scope for this release
- [x] **Dependencies** — AAQ must be enabled in HCO before tests run; KubeVirt must pick up
  `cpuAllocationRatio` from HCO config
  - *Details:* Test setup verifies `aaq-controller` and `aaq-server` pods are Running and KubeVirt CR
    reflects the ratio before tests proceed
- [ ] **Cross Integrations** — N/A; change is self-contained within AAQ and HCO config propagation

**Infrastructure**

- [ ] **Cloud Testing** — N/A; feature is not cloud-specific;

---

#### **3. Test Environment**

- **Cluster Topology:** 3-master/3-worker bare-metal (live migration requires ≥ 2 schedulable workers)
- **OCP & OpenShift Virtualization Version(s):** OCP 4.22 / OpenShift Virtualization 4.22
- **CPU Virtualization:** N/A
- **Compute Resources:** N/A
- **Special Hardware:** N/A
- **Storage:** ocs-storagecluster-ceph-rbd-virtualization
- **Network:** OVN-Kubernetes, IPv4
- **Required Operators:** AAQ enabled via HCO (`spec.deployment.applicationAwareConfig.enable: true`)
- **Platform:** Bare metal
- **Special Configurations:** HCO configured with
  `spec.deployment.applicationAwareConfig.vmiCalcConfigName: GuestEffectiveResources` and
  `spec.deployment.virtualization.vmiCPUAllocationRatio: 10`; test namespace labelled
  `application-aware-quota/enable-gating=`


#### **3.1. Testing Tools & Frameworks**

- **Test Framework:**  pytest, openshift-virtualization-tests framework
- **CI/CD:** N/A — standard
- **Other Tools:** N/A

---

#### **4. Entry Criteria**

The following conditions must be met before testing can begin:

- [ ] Requirements and design documents are approved and merged
- [ ] Test environment can be set up and configured (see Section II.3)
- [ ] HCO `spec.deployment.virtualization.vmiCPUAllocationRatio` propagation to KubeVirt CR is confirmed
  working
- [ ] AAQ controller handles the ratio in `VirtualResources` quota calculation
- [ ] `aaq-controller` and `aaq-server` pods are Running in the test cluster

---

#### **5. Risks**

**Timeline/Schedule**

- **Risk:** N/A
  - **Mitigation:** N/A
  - *Estimated impact on schedule:* N/A
  - *Sign-off:* N/A

**Test Coverage**

- **Risk:** Async nature of AAQ scheduling gates may cause flaky tests if polling intervals are too short
  - **Mitigation:** Use sufficiently long timeouts and event-driven polling; align with existing AAQ
    test patterns
  - *Areas with reduced coverage:* None
  - *Sign-off:* TBD

**Test Environment**

- **Risk:** N/A
  - **Mitigation:** N/A
  - *Missing resources or infrastructure:* N/A
  - *Sign-off:* N/A

**Untestable Aspects**

- **Risk:** N/A — all acceptance criteria are directly observable via Kubernetes API
  - **Mitigation:** N/A
  - *Alternative validation approach:* N/A
  - *Sign-off:* N/A

**Resource Constraints**

- **Risk:** N/A
  - **Mitigation:** N/A
  - *Current capacity gaps:* N/A
  - *Sign-off:* N/A


---

### **III. Test Scenarios & Traceability**

- **[CNV-75339](https://redhat.atlassian.net/browse/CNV-75339)** — As a cluster admin, I want ARQ to
  account for `vmiCPUAllocationRatio` so that quota is consumed proportionally to the ratio, not the
  raw CPU count

  - *Test Scenario 1 — CPU and memory quota reflects vmiCPUAllocationRatio:* [Tier 2]
  - *Priority:* P0

- **[CNV-75339](https://redhat.atlassian.net/browse/CNV-75339)** — As a cluster admin, I want VM live
  migration to succeed when `vmiCPUAllocationRatio` is active in AAQ config

  - *Test Scenario 2 — VM live migration succeeds:* [Tier 2]
  - *Priority:* P0

- **[CNV-75339](https://redhat.atlassian.net/browse/CNV-75339)** — As a cluster admin, I want AAQ to
  gate a second VM when quota is exhausted, and automatically ungate it when quota is increased

  - *Test Scenario 3 — Second VM gated when quota exhausted; unblocked after quota increase:* [Tier 2]
  - *Priority:* P0

---

### **IV. Sign-off and Approval**

This Software Test Plan requires approval from the following stakeholders:

* **Reviewers:**
  - dshchedr
  - vsibirsk
  - rnetser
  - kbidarkar
  - SiboWang1997
  - jerry7z
  - SamAlber
* **Approvers:**
  - dshchedr
  - vsibirsk
  - rnetser
