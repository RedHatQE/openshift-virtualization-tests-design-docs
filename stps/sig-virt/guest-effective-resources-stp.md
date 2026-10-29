# Openshift-virtualization-tests Test plan

## **Guest-Effective Quota and Published Memory Overhead — Quality Engineering Plan**

### **Metadata & Tracking**

- **Enhancement(s):** [VEP 156, memory overhead on the virtual machine](https://github.com/kubevirt/enhancements/issues/156)
- **Feature Tracking:** [CNV-61868](https://issues.redhat.com/browse/CNV-61868)
- **Epic Tracking:**
  - [CNV-91264](https://issues.redhat.com/browse/CNV-91264) — KubeVirt publishes the memory overhead it reserved. [CNV-91281](https://issues.redhat.com/browse/CNV-91281) — CNV 5.2. Application Aware Quota uses that published value for guest-effective counting.
  - [CNV-73947](https://issues.redhat.com/browse/CNV-73947) — CNV 5.2. Quota CPU follows the CPU allocation ratio, and quota memory follows the memory overcommit percentage.
- **Feature Maturity:**
  - DP: N/A
  - TP: 5.0 — [CNV-88377](https://issues.redhat.com/browse/CNV-88377)
  - GA: 5.1 — [CNV-91264](https://issues.redhat.com/browse/CNV-91264)
- **QE Owner(s):** Ameya Keskar (@ameya-keskar)
- **Owning SIG:** sig-virt
- **Participating SIGs:** sig-virt

**Document Conventions:**

- **Published memory overhead** — the platform memory KubeVirt reserved for a virtual machine beyond the guest. It is written on the pod as `kubevirt.io/memory-overhead-bytes` and copied to `status.memory.memoryOverhead` ([kubevirt#16746](https://github.com/kubevirt/kubevirt/pull/16746)). During a migration the destination value is `status.migrationState.targetMemoryOverhead`.
- **Guest-effective counting** — the Application Aware Quota mode `GuestEffectiveResources`. It charges the virtual machine's compute container, then removes memory overhead. In this plan that overhead is the published value, not a separate estimate.
- **CPU allocation ratio** — cluster setting `vmiCPUAllocationRatio`. Default 10. The pod CPU request is the vCPU count divided by this ratio, unless the virtual machine sets its own CPU request or uses dedicated CPUs. The guest still sees every vCPU.
- **Memory overcommit percentage** — cluster setting `memoryOvercommitPercentage`. Default 100, minimum 10. Guest memory is scaled by `100 / percentage` into the pod memory request, unless the virtual machine sets its own memory request, uses hugepages, or uses dedicated CPUs. Overhead is added after that scaling.
- **Namespace quota** — `status.used` on the namespace ApplicationAwareResourceQuota.

### **Feature Overview**

Quota for a virtual machine follows the CPU and memory the guest was given, after the cluster overcommit settings, and leaves out the extra memory reserved for the virtual machine process. KubeVirt shows that reserved memory on the running virtual machine, and guest-effective counting uses that shown value. The CPU charge follows the allocation ratio while the guest still sees the full vCPU count, and the memory charge follows the overcommit percentage. A live migration does not count the virtual machine twice, and a virtual machine that does not fit the quota stays pending until the quota is raised. This plan covers that behavior on CNV 5.2, where [CNV-91281](https://issues.redhat.com/browse/CNV-91281) and [CNV-73947](https://issues.redhat.com/browse/CNV-73947) are both implemented.

---

### **I. Motivation and Requirements Review (QE Review Guidelines)**

This section documents the mandatory QE review process. The goal is to understand the feature's value,
technology, and testability before formal test planning.

#### **1. Requirement & User Story Review Checklist**

- [x] **Review Requirements**
  - *List the key D/S requirements reviewed:*
    - A running virtual machine shows the memory overhead reserved for it
    - After a live migration, the virtual machine shows the overhead reserved on the destination pod
    - With guest-effective counting, namespace quota subtracts that overhead from the memory charge
    - Quota CPU follows the CPU allocation ratio, and the guest still sees the full vCPU count
    - Quota memory follows the memory overcommit percentage
    - A live migration does not add a second quota charge for the same virtual machine
    - A virtual machine that does not fit the remaining quota stays pending, and starts after the quota is raised

- [x] **Understand Value and Customer Use Cases**
  - *Describe the feature's value to customers:* An administrator can set a CPU and memory quota on a namespace. Each virtual machine is charged the CPU and memory reserved for the guest in its pod, after the CPU allocation ratio and the memory overcommit percentage, and is not charged the extra memory reserved for the virtual machine process. A [live migration](https://github.com/kubevirt/application-aware-quota/blob/main/README.md) does not fail the quota just because two pods exist for a short time, and the virtualization overhead is not part of the charge the guest owner requested.
  - *List the customer use cases identified:*
    - As a cluster administrator, I want a running virtual machine to show the memory overhead that was reserved for it, including after a live migration.
    - As a cluster administrator, I want guest-effective quota to subtract that same overhead.
    - As a cluster administrator, I want quota CPU to follow the CPU allocation ratio, so more virtual machines fit under the same CPU quota while the guest still sees the full vCPU count.
    - As a cluster administrator, I want quota memory to follow the memory overcommit percentage.
    - As a cluster administrator, I want a virtual machine that does not fit the quota to wait, and to start after I raise the quota, without creating it again.

- [x] **Testability**
  - *Note any requirements that are unclear or untestable:* None. A running virtual machine reports its memory overhead. Namespace quota usage, the guest CPU count, and the scheduling gate can be read.

- [x] **Acceptance Criteria**
  - *List the acceptance criteria:*
    - A running virtual machine reports the memory overhead reserved for it. No feature gate is turned on for this.
    - During a live migration, the destination overhead is reported on its own. After the migration, the overhead shown on the virtual machine equals that destination value.
    - With guest-effective counting, the memory charge uses that reported overhead and does not include it.
      - The CPU charge follows the CPU allocation ratio. The guest still sees the full vCPU count.
      - The memory charge follows the memory overcommit percentage.
      - A live migration does not add a second quota charge for the same virtual machine.
  - *Note any gaps or missing criteria:* None

- [x] **Non-Functional Requirements (NFRs)**
  - *List applicable NFRs and their targets:*
    - **Usability:** when quota is inadequate, the pod stays scheduling-gated and an event explains the refusal. When the quota is raised, the gate is removed and the virtual machine starts. That is the negative scenario in [Section III](#iii-test-scenarios--traceability). There is no new screen and no new CLI.
    - **Documentation:** No downstream documentation is required for the memory overhead a virtual machine reports.
  - *Note any NFRs not covered and why:*
    - **Monitoring:** neither epic adds an alert. Quota usage and the virtual machine overhead are the values the scenarios read. No separate metrics scenario.
    - **UI:** No changes introduced.
    - **Performance:** N/A
    - **Security:** neither epic adds a permission. The scenarios use the existing administrator role.
    - **Scalability:** N/A

#### **2. Known Limitations**

- **Dedicated CPUs skip both overcommit settings.** Neither the [CPU allocation ratio](https://github.com/kubevirt/hyperconverged-cluster-operator/blob/main/docs/cluster-configuration.md) nor the memory overcommit percentage is applied. Guest-effective counting then charges the resulting pod request, with memory overhead still removed.
  - *Sign-off:* Pending

- **A request set on the virtual machine replaces the calculated one.** A CPU request set there is the CPU charge, and the CPU allocation ratio does not divide it. A memory request set there is not scaled by the memory overcommit percentage. Memory overhead is still left out of the memory charge, so that charge is the memory request set on the virtual machine.
  - *Sign-off:* Pending

- **Hugepages are not scaled by the memory overcommit percentage.** The memory request stays at the hugepage size.
  - *Sign-off:* Pending

- **`overcommitGuestOverhead` leaves the overhead off the pod memory request.** When the flag is set, overhead is not added to that request. Subtracting it again would under-count. This STP does not set the flag.
  - *Sign-off:* Pending

- **A running pod does not pick up a new overcommit value.** A [memory overcommit percentage](https://github.com/kubevirt/hyperconverged-cluster-operator/blob/main/docs/cluster-configuration.md) change applies after a power cycle or a live migration. The CPU allocation ratio is applied when the pod is created, so a running pod keeps that CPU request until the pod is replaced.
  - *Sign-off:* Pending

#### **3. Technology and Design Review**

- [x] **Developer Handoff/QE Kickoff**
  - *Key takeaways and concerns:*
    - Guest-effective counting uses the compute-container request. The memory overhead it subtracts is the value KubeVirt published. The CPU allocation ratio and the memory overcommit percentage are already applied in that request.
    - CPU is not part of that overhead. Guest-effective CPU is the compute-container CPU request. KubeVirt has already divided it by `vmiCPUAllocationRatio`.
    - CNV-91264 is labeled no-qe. The overhead on the virtual machine and the guest-effective quota that uses it are both in this plan. QE lead confirms that at sign-off.

- [x] **Technology Challenges**
  - *List identified challenges:* Quota is asynchronous. A [scheduling gate](https://github.com/kubevirt/application-aware-quota/blob/main/README.md#how-it-works) is added to the pod, and a controller removes it only after the quota has room. A virtual machine can exist before `status.used` moves. On one architecture the old estimate and the published overhead can be the same number, so a quota result by itself does not show which source was used.
  - *Impact on testing approach:* Tests wait until `status.used` settles, and until a gated pod either stays gated or starts. Memory assertions use `status.memory.memoryOverhead`. They do not copy the overhead formula into the test.

- [x] **API Extensions**
  - *List new or modified APIs:* `status.memory.memoryOverhead` and `status.migrationState.targetMemoryOverhead` on the virtual machine. Guest-effective counting, `vmiCPUAllocationRatio`, and `memoryOvercommitPercentage` already exist. No new quota object.
  - *Testing impact:* Scenarios read those two status fields and the namespace quota. They count the [compute container](https://github.com/kubevirt/application-aware-quota/blob/main/README.md#configure-aaq-operator) only. Extra containers in the pod are not part of the charge.

- [x] **Test Environment Needs**
  - *See environment requirements in [Section II.3](#3-test-environment) and testing tools in [Section II.3.1](#31-testing-tools--frameworks)*

- [x] **Topology Considerations**
  - *Describe topology requirements:* One cluster with at least two worker nodes, so one virtual machine can live-migrate. No secondary network and no extra storage class. Application Aware Quota is enabled through OpenShift Virtualization, and the test namespace has the [`application-aware-quota/enable-gating`](https://github.com/kubevirt/application-aware-quota/blob/main/README.md#configure-aaq-operator) label. That label selects the namespaces where the scheduling gate is applied.
  - *Impact on test design:* Migration scenarios check the overhead fields and the quota charge. Node placement, network type, and storage type are not part of the result.

### **II. Software Test Plan (STP)**

This STP serves as the **overall roadmap for testing**, detailing the scope, approach, resources, and schedule.

#### **1. Scope of Testing**

One suite on CNV 5.2. Guest-effective counting subtracts the published memory overhead. Quota CPU follows the CPU allocation ratio, and quota memory follows the memory overcommit percentage.

**Testing Goals**

- **[P0]** A running virtual machine reports `status.memory.memoryOverhead` equal to `kubevirt.io/memory-overhead-bytes` on its current pod. No feature gate is changed.
- **[P0]** During live migration, `status.migrationState.targetMemoryOverhead` is set. After migration, `status.memory.memoryOverhead` equals that destination value.
- **[P0]** With guest-effective counting, namespace quota memory equals the compute-container memory request minus `status.memory.memoryOverhead`.
- **[P0]** With `vmiCPUAllocationRatio` 10, a 10-vCPU virtual machine with no CPU request, no dedicated CPUs, and no supplemental IO threads adds 1 CPU to the namespace quota. The guest still reports 10 vCPUs.
- **[P0]** With `memoryOvercommitPercentage` 100, a 3072Mi guest with no memory request, no hugepages, and no dedicated CPUs adds 3072Mi to the namespace quota. The pod memory request is larger by `status.memory.memoryOverhead`.
- **[P0]** With `memoryOvercommitPercentage` 150, that same guest adds 2048Mi to the namespace quota.
- **[P0]** A same-size live migration does not add a second full CPU or memory charge. Afterwards, quota memory equals the destination compute-container memory request minus the overhead shown on the virtual machine.
- **[P0]** [NEGATIVE] With the hard limit set to one charge, a second identical virtual machine does not run and its pod stays scheduling-gated. An event reports that the quota does not allow the pod. After the hard limit is raised to two charges, the gate is removed and that same pod runs.

**Out of Scope (Testing Scope Exclusions)**

- **`overcommitGuestOverhead`**
  - *Rationale:* That flag removes overhead from the pod memory request before quota runs. It is not in the CNV-73947 acceptance criteria. See the limitation in [Section I.2](#2-known-limitations).
  - *PM/Lead Agreement:* Pending

- **Instance-type `overcommitPercent`**
  - *Rationale:* That percentage belongs to the instance type. It is not `memoryOvercommitPercentage`.
  - *PM/Lead Agreement:* Pending

- **CPU hotplug**
  - *Rationale:* Adding vCPUs to a running virtual machine is a separate operation. This cycle covers the charge at start and across a same-size migration.
  - *PM/Lead Agreement:* Pending

- **Other guest operating systems, including Windows**
  - *Rationale:* The charge is taken from the pod request and the virtual machine status, not from the guest OS.
  - *PM/Lead Agreement:* Pending

**Test Limitations**

None.

#### **2. Test Strategy**

**Functional**

- [x] **Functional Testing** — Validates that the feature works according to the specified requirements and user stories
  - *Details:* The goals in [Section II.1](#1-scope-of-testing) are the suite: overhead at start and across migration, quota memory using the published overhead, the CPU ratio, both memory percentages, a same-size migration, and the gated second virtual machine. Each goal has one scenario in [Section III](#iii-test-scenarios--traceability).

- [x] **Automation Testing** — Confirms test automation plan is in place for CI and regression coverage (all tests are expected to be automated)
  - *Details:* Automation is [CNV-75339](https://issues.redhat.com/browse/CNV-75339), run on CNV 5.2. No scenario in [Section III](#iii-test-scenarios--traceability) is manual-only.

- [x] **Regression Testing** — Verifies that new changes do not break existing functionality
  - *Details:* `DedicatedVirtualResources`, `VirtualResources`, and `VmiPodUsage` already have tests and are not repeated. Existing tests already check that `vmiCPUAllocationRatio` and `memoryOvercommitPercentage` change the pod request. Those stay. This suite adds the overhead field and the namespace quota check.

- [ ] **Self-Validation Testing** — Should any of the new tests be included in the self-validation test package?
  - *Details:* No. The scenarios change cluster overcommit settings and quota, and migration needs two workers.

**Non-Functional**

- [ ] **Performance Testing** — Validates feature performance meets requirements (latency, throughput, resource usage)
  - *Details:* No performance target on either epic.

- [ ] **Scale Testing** — Validates feature behavior under increased load and at production-like scale (e.g., large number of VMs, nodes, or concurrent operations)
  - *Details:* No scale target.

- [ ] **Security Testing** — Verifies security requirements, RBAC, authentication, authorization, and vulnerability scanning
  - *Details:* No new permission boundary. Out of Scope

- [x] **Usability Testing** — Validates user experience and accessibility requirements
  - *Details:* No new UI. The check is the gated pod and the quota event in the negative scenario, then the same pod starting after the quota is raised.

- [ ] **Monitoring** — Does the feature require metrics and/or alerts?
  - *Details:* No new alert. The scenarios read the virtual machine status and the namespace quota.

**Integration & Compatibility**

- [x] **Compatibility Testing** — Ensures feature works across supported platforms, versions, and configurations
  - *Details:* The charge does not depend on storage or network type. Dedicated CPUs, explicit requests, and hugepages are the limitations in [Section I.2](#2-known-limitations).

- [ ] **Upgrade Testing** — Validates upgrade paths from previous versions, data migration, and configuration preservation
  - *Details:* N/A

- [ ] **Dependencies** — Blocked by deliverables from other components/products. Identify what we need from other teams before we can test.
  - *Details:* Not blocked. CNV 5.2 contains [CNV-91281](https://issues.redhat.com/browse/CNV-91281) and [CNV-73947](https://issues.redhat.com/browse/CNV-73947). The memory-overhead report is already merged, so no further KubeVirt API work is required.

- [ ] **Cross Integrations** — Does the feature affect other features or require testing by other teams? Identify the impact we cause.
  - *Details:* sig-virt owns the scenarios. No other SIG has any involvement here.

**Infrastructure**

- [ ] **Cloud Testing** — Does the feature require multi-cloud platform testing? Consider cloud-specific features.
  - *Details:* N/A

#### **3. Test Environment**

- **Cluster Topology:** 3 control-plane nodes and 3 workers(High Availability cluster). Two workers are required for live migration.
- **OCP & OpenShift Virtualization Version(s):** OpenShift Virtualization 5.2, including [CNV-91281](https://issues.redhat.com/browse/CNV-91281) and [CNV-73947](https://issues.redhat.com/browse/CNV-73947).
- **CPU Virtualization:** VT-x (Intel) or AMD-V enabled
- **Compute Resources:** Minimum per worker node: 8 vCPUs, 32GB RAM
- **Special Hardware:** N/A
- **Storage:** ocs-storagecluster-ceph-rbd-virtualization
- **Network:** OVN-Kubernetes, IPv4
- **Required Operators:** Application Aware Quota, enabled from OpenShift Virtualization
- **Platform:** Bare metal or PSI
- **Special Configurations:** Test namespace labeled `application-aware-quota/enable-gating`. Counting mode `GuestEffectiveResources`. `vmiCPUAllocationRatio` and `memoryOvercommitPercentage` set per scenario. `VmiMemoryOverheadReport` is not toggled.

#### **3.1. Testing Tools & Frameworks**

- **Test Framework:** Standard (openshift-virtualization-tests)
- **CI/CD:** N/A
- **Other Tools:** N/A

#### **4. Entry Criteria**

The following conditions must be met before testing can begin:

- [x] The overhead report is merged. [kubevirt#16746](https://github.com/kubevirt/kubevirt/pull/16746) and [kubevirt#18708](https://github.com/kubevirt/kubevirt/pull/18708).
- [ ] The build under test is CNV 5.2, including [CNV-91281](https://issues.redhat.com/browse/CNV-91281) and [CNV-73947](https://issues.redhat.com/browse/CNV-73947)
- [ ] [Section III](#iii-test-scenarios--traceability) scenarios are reviewed and approved
- [x] Test environment can be **set up and configured** (see [Section II.3](#3-test-environment) - Test Environment)
- [ ] A running virtual machine shows `status.memory.memoryOverhead` with no feature-gate change
- [ ] Sign-offs in Sections I.2, II.1, and II.5 have a name and a date

#### **5. Risks**

**Timeline/Schedule**

- **Risk:** N/A. This plan runs on CNV 5.2, where [CNV-91281](https://issues.redhat.com/browse/CNV-91281) and [CNV-73947](https://issues.redhat.com/browse/CNV-73947) are both present.
  - **Mitigation:** The scenarios describe that finished behavior. An open story is not a schedule risk in this plan.

**Test Coverage**

- **Risk:** When the published overhead equals the estimate guest-effective counting used before CNV 5.2, the quota total does not show which value was subtracted. After a live migration, the memory charge follows the overhead then shown on the virtual machine, which can differ from the overhead shown before the migration.
  - **Mitigation:** Memory assertions subtract `status.memory.memoryOverhead` from the compute-container memory request. They do not treat a matching total as proof of the source, and they do not require the post-migration memory charge to equal the pre-migration number.
  - *Areas with reduced coverage:* The overhead formula is not re-derived. Releases that still estimate the overhead are out of scope.
  - *Sign-off:* Pending

**Test Environment**

- **Risk:** N/A. [Section II.3](#3-test-environment) is a standard bare-metal cluster with two workers for migration.
  - **Mitigation:** No extra hardware profile.

**Untestable Aspects**

- **Risk:** N/A. On CNV 5.2 the overhead on the virtual machine, quota usage, the guest CPU count, the scheduling gate, and the quota event are observable.
  - **Mitigation:** Nothing in [Section III](#iii-test-scenarios--traceability) depends on reading Application Aware Quota source at runtime.

**Resource Constraints**

- **Risk:** N/A. One owner automates the scenarios. No second cluster and no second SIG.
  - **Mitigation:** One virtual machine for the charge checks, two for quota exhaustion.

**Dependencies**

- **Risk:** N/A. CNV 5.2 contains [CNV-91281](https://issues.redhat.com/browse/CNV-91281) and [CNV-73947](https://issues.redhat.com/browse/CNV-73947). The memory-overhead report those checks read is already merged.
  - **Mitigation:** No further KubeVirt API change is required for this plan.

---

### **III. Test Scenarios & Traceability**

All of these run on CNV 5.2 with guest-effective counting, viz. a AAQ counting mode introduced in CNV-73947. Where a scenario reads or sets a quota, that quota is the namespace Application Aware Quota: `hard` is the limit, and `status.used` is the CPU and memory already consumed. The virtual machine does not set its own CPU or memory request, does not use dedicated CPUs, hugepages, or supplemental IO threads, and does not set `overcommitGuestOverhead`.

- **[CNV-91264](https://issues.redhat.com/browse/CNV-91264)** — As a cluster administrator, I want a running virtual machine to show the memory overhead that was reserved for it.
  - *Test Scenario:* [Tier 2] Start a virtual machine without changing feature gates. `status.memory.memoryOverhead` is set and equals `kubevirt.io/memory-overhead-bytes` on its current pod.
  - *Priority:* P0

- **[CNV-91264](https://issues.redhat.com/browse/CNV-91264)** — As a cluster administrator, I want that overhead to follow a live migration.
  - *Test Scenario:* [Tier 2] Live-migrate the virtual machine. While the migration is in progress, `status.migrationState.targetMemoryOverhead` is set. After the migration, `status.memory.memoryOverhead` equals that destination pod value.
  - *Priority:* P0

- **[CNV-91281](https://issues.redhat.com/browse/CNV-91281)** — As a cluster administrator, I want guest-effective counting to subtract the published overhead from Application Aware Quota.
  - *Test Scenario:* [Tier 2] Start a virtual machine. Application Aware Quota `status.used` memory increases by the compute-container memory request minus `status.memory.memoryOverhead`. It does not increase by the full memory request.
  - *Priority:* P0

- **[CNV-73947](https://issues.redhat.com/browse/CNV-73947)** — As a cluster administrator, I want Application Aware Quota CPU to follow the CPU allocation ratio.
  - *Test Scenario:* [Tier 2] Set `vmiCPUAllocationRatio` to 10. Start a virtual machine with 10 vCPUs. Application Aware Quota `status.used` CPU increases by 1 CPU. The guest reports 10 vCPUs.
  - *Priority:* P0

- **[CNV-73947](https://issues.redhat.com/browse/CNV-73947)** — As a cluster administrator, I want Application Aware Quota memory to stay at the guest size when the overcommit percentage does not scale it, and to exclude overhead.
  - *Test Scenario:* [Tier 2] Set `memoryOvercommitPercentage` to 100. Start a virtual machine with 3072Mi of guest memory. Application Aware Quota `status.used` memory increases by 3072Mi. The compute-container memory request minus `status.memory.memoryOverhead` is 3072Mi.
  - *Priority:* P0

- **[CNV-73947](https://issues.redhat.com/browse/CNV-73947)** — As a cluster administrator, I want Application Aware Quota memory to follow the memory overcommit percentage.
  - *Test Scenario:* [Tier 2] Set `memoryOvercommitPercentage` to 150. Start a virtual machine with 3072Mi of guest memory. Application Aware Quota `status.used` memory increases by 2048Mi.
  - *Priority:* P0

- **[CNV-73947](https://issues.redhat.com/browse/CNV-73947)** — As a cluster administrator, I want a live migration to count the virtual machine once in Application Aware Quota.
  - *Test Scenario:* [Tier 2] Record Application Aware Quota `status.used` CPU and memory. Live-migrate the virtual machine. While both pods exist, `status.used` CPU and memory do not increase by that same CPU and memory again. After the migration, `status.used` CPU equals the recorded CPU, and `status.used` memory equals the destination compute-container memory request minus `status.memory.memoryOverhead`.
  - *Priority:* P0

- **[CNV-73947](https://issues.redhat.com/browse/CNV-73947)** — As a cluster administrator, I want a virtual machine that does not fit in Application Aware Quota to wait, and to start after I raise the quota.
  - *Test Scenario:* [Tier 2] [NEGATIVE] Set Application Aware Quota `hard` CPU to 1 and `hard` memory to the memory one virtual machine consumed above, 3072Mi or 2048Mi. Start one virtual machine and wait until `status.used` shows that CPU and memory. Create a second identical virtual machine. It does not run. Its pod stays scheduling-gated, and an event says the quota does not allow the pod. Raise `hard` CPU to 2 and `hard` memory to twice that memory. The gate is removed, the same pod runs, and `status.used` shows 2 CPU and twice that memory.
  - *Priority:* P0

---

### **IV. Sign-off and Approval**

This Software Test Plan requires approval from the following stakeholders:

* **Reviewers:**
  - Development Lead: Barak Mordehai (@Barakmor1)
  - sig-virt: Akriti Gupta (@akri3i), Denys Shchedrivyi (@dshchedr), Vasiliy Sibirskiy (@vsibirsk), Samuel Alberstein (@SamAlber)
  - QE architect: Ruth Netser (@rnetser)
* **Approvers:**
  - QE Lead: Kedar Bidarkar (@kbidarkar)
  - Development Lead: Barak Mordehai (@Barakmor1)
  - Product Manager: Martin Tessun (@mtessun)
