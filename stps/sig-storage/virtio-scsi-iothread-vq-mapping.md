# Openshift-virtualization-tests Test plan

## **IOThread Virtqueue Mapping for virtio-scsi - Quality Engineering Plan**

### **Metadata & Tracking**

- **Enhancement(s):** [VEP #342: IOThread Virtqueue Mapping for virtio-scsi](https://github.com/kubevirt/enhancements/pull/343)
- **Feature Tracking:** [CNV-86526](https://redhat.atlassian.net/browse/CNV-86526)
- **Epic Tracking:** [CNV-86526](https://redhat.atlassian.net/browse/CNV-86526)
- **Feature Maturity:**

  - DP: [TBD]
  - TP: [TBD]
  - GA: [TBD]
- **QE Owner(s):** Jose Manuel Castano (joscasta@redhat.com)
- **Owning SIG:** sig-storage
- **Participating SIGs:** sig-storage

**Document Conventions (if applicable):**

| Term | Definition |
|:-----|:-----------|
| **IOThread** | A dedicated host thread used to process disk I/O outside the main QEMU thread, reducing CPU contention |
| **Virtqueue** | A queue used by virtio devices to exchange data between the guest and the host |
| **IOThreadsPolicy** | A VM-level setting that controls how I/O threads are allocated to disks (shared, auto, or supplementalPool) |

### **Feature Overview**

VMs running multiple virtio-scsi disks with heavy I/O workloads can experience a CPU bottleneck because the SCSI controller currently uses at most a single I/O thread shared by all virtio-scsi devices. This feature extends the existing IOThreadsPolicy settings (shared, auto, supplementalPool) to also apply to the virtio-scsi controller, allowing multiple dedicated I/O threads to process the controller's virtqueues in parallel. The feature is opt-in and protected by a feature gate. When enabled, users can expect improved I/O throughput for VMs with multiple virtio-scsi disks performing concurrent I/O operations.

---

### **I. Motivation and Requirements Review (QE Review Guidelines)**

#### **1. Requirement & User Story Review Checklist**

- [ ] **Review Requirements**
  - *List the key D/S requirements reviewed:*
    - IOThreadsPolicy (shared, auto, supplementalPool) must be extended to allocate I/O threads to the virtio-scsi controller
    - Feature must be gated behind a feature gate; disabled by default
    - Existing virtio-blk IOThread behavior must remain unchanged
    - Thread count allocated to the SCSI controller must not exceed the number of virtqueues (equal to vCPU count)

- [ ] **Understand Value and Customer Use Cases**
  - *Describe the feature's value to customers:* Customers running database or storage-intensive workloads on VMs with multiple virtio-scsi disks can achieve higher I/O throughput by distributing I/O processing across multiple host threads, eliminating the single-thread bottleneck on the SCSI controller.
  - *List the customer use cases identified:*
    - As a user, I want to dedicate multiple I/O threads for my virtio-scsi disks so that I can gain a performance increase during heavy I/O operations
    - As a cluster admin, I want to use the supplementalPool policy with hotplug-heavy workloads so that the SCSI controller has a sufficient thread pool for dynamically added disks

- [ ] **Testability**
  - *Note any requirements that are unclear or untestable:* None

- [ ] **Acceptance Criteria**
  - *List the acceptance criteria:*
    - When the feature gate is enabled and IOThreadsPolicy is set, the virtio-scsi controller uses multiple I/O threads according to the selected policy
    - When the feature gate is disabled, the virtio-scsi controller uses the existing single-thread behavior regardless of IOThreadsPolicy
    - With the shared policy, the SCSI controller shares the same single I/O thread assigned to all disks
    - With the auto policy, the SCSI controller receives all non-dedicated I/O threads, and thread count does not exceed the number of virtqueues (vCPUs)
    - With the supplementalPool policy, the entire supplemental thread pool is shared with the SCSI controller
    - Hotplugging virtio-scsi disks into a running VM with IOThreadsPolicy set uses the thread pool established at VM startup
    - VMs with mixed virtio-blk and virtio-scsi disks allocate I/O threads correctly to both device types
  - *Note any gaps or missing criteria:* None

- [ ] **Non-Functional Requirements (NFRs)**
  - *List applicable NFRs and their targets:*
    - Performance: measurable I/O throughput improvement with multiple virtio-scsi disks under concurrent I/O load compared to single-thread baseline
    - Monitoring: confirm whether new metrics or alerts are introduced for IOThread allocation (TBD with dev team)
    - Documentation: user-facing documentation must describe the feature gate and policy behavior for virtio-scsi
  - *Note any NFRs not covered and why:*
    - Security: no new RBAC or authentication changes; existing access controls apply
    - Scalability: no new cluster-level scale requirements; thread allocation is per-VM
    - UI: no UI changes introduced; PM/UX to confirm whether UI testing adds customer value

#### **2. Known Limitations**

- **SCSI controller maps I/O threads to virtqueues, not to individual disks**
  - Unlike virtio-blk, where each disk can get a dedicated thread, the SCSI controller distributes threads across virtqueues. Users cannot assign a specific thread to a specific disk.
  - *Sign-off:* [Name/Date]

- **Hotplug with auto policy is limited by the thread pool size set at VM startup**
  - The SCSI controller's thread pool is initialized when the VM starts and cannot be modified at runtime. If many virtio-scsi disks are hotplugged later, the controller may have fewer threads than optimal. Users needing heavy hotplug should use the supplementalPool policy instead.
  - *Sign-off:* [Name/Date]

#### **3. Technology and Design Review**

- [ ] **Developer Handoff/QE Kickoff**
  - *Key takeaways and concerns:* [TBD — schedule meeting with dev team]

- [ ] **Technology Challenges**
  - *List identified challenges:*
    - Requires libvirt 11.2.0+ and QEMU 10.0+ for virtio-scsi IOThread virtqueue mapping support
    - Verifying correct thread-to-virtqueue mapping requires inspecting domain XML or guest-visible I/O distribution
  - *Impact on testing approach:* Tests must validate on environments with the required libvirt/QEMU versions; older versions must gracefully degrade or reject the configuration

- [ ] **API Extensions**
  - *List new or modified APIs:* No new APIs; the existing IOThreadsPolicy field is reused. The SCSI controller domain XML is extended internally to include IOThread references.
  - *Testing impact:* Tests must verify that existing IOThreadsPolicy values (shared, auto, supplementalPool) produce correct behavior for virtio-scsi disks in addition to existing virtio-blk behavior

- [ ] **Test Environment Needs**
  - *See environment requirements in Section II.3 and testing tools in Section II.3.1*

- [ ] **Topology Considerations**
  - *Describe topology requirements:* Standard cluster topology; no multi-cluster or special network topology requirements
  - *Impact on test design:* Live migration tests require at least two schedulable worker nodes

### **II. Software Test Plan (STP)**

#### **1. Scope of Testing**

**Testing Goals**

- **[P0]** Verify that when the feature gate is enabled and IOThreadsPolicy is set, a VM with virtio-scsi disks uses multiple I/O threads on the SCSI controller
- **[P0]** Verify that when the feature gate is disabled, the virtio-scsi controller falls back to single-thread behavior regardless of IOThreadsPolicy
- **[P0]** Verify that the shared IOThreadsPolicy assigns the same single I/O thread to the SCSI controller and all disks
- **[P0]** Verify that the auto IOThreadsPolicy distributes I/O threads to the SCSI controller, capped at the number of virtqueues (vCPUs)
- **[P0]** Verify that the supplementalPool IOThreadsPolicy shares the entire supplemental thread pool with the SCSI controller
- **[P0]** Verify that a VM with mixed virtio-blk and virtio-scsi disks allocates I/O threads correctly to both device types under each policy
- **[P1]** Verify that hotplugging a virtio-scsi disk into a running VM with IOThreadsPolicy set uses the existing thread pool
- **[P1]** Verify that when I/O threads exceed the number of virtqueues (vCPUs), the SCSI controller uses only as many threads as there are virtqueues
- **[P1]** Verify that live migration of a VM with multi-threaded SCSI controller preserves I/O thread allocation after migration
- **[P1]** Verify that disabling the feature gate on a running cluster does not disrupt existing VMs (rollback behavior)
- **[P2]** Verify measurable I/O throughput improvement with multiple virtio-scsi disks under concurrent I/O load compared to single-thread baseline

**Out of Scope (Testing Scope Exclusions)**

- **Changes to virtio-blk IOThread mapping**
  - *Rationale:* This feature does not modify virtio-blk behavior; existing virtio-blk tests provide coverage
  - *PM/Lead Agreement:* [Name/Date]

- **Windows guest OS testing**
  - *Rationale:* Initial validation uses Linux-based guests; Windows virtio-scsi driver compatibility is not confirmed for this phase
  - *PM/Lead Agreement:* [Name/Date]

**Test Limitations**

- **Performance benchmarking accuracy depends on consistent hardware and I/O load generation**
  - *Sign-off:* [Name/Date]

#### **2. Test Strategy**

**Functional**

- [x] **Functional Testing** — Validates that the feature works according to specified requirements and user stories
  - *Details:* Verify each IOThreadsPolicy (shared, auto, supplementalPool) with virtio-scsi disks, feature gate behavior, mixed disk types, and thread count capping

- [x] **Automation Testing** — Confirms test automation plan is in place for CI and regression coverage (all tests are expected to be automated)
  - *Details:* All Tier 1 and Tier 2 tests will be automated and integrated into CI lanes

- [x] **Regression Testing** — Verifies that new changes do not break existing functionality
  - *Details:* Existing IOThread tests for virtio-blk must continue to pass; sig-storage regression suite runs on the feature cluster

- [ ] **Self-Validation Testing** — Should any of the new tests be included in the self-validation test package?
  - *Details:* TBD — evaluate whether basic IOThreadsPolicy with virtio-scsi validation should be part of self-validation

**Non-Functional**

- [x] **Performance Testing** — Validates feature performance meets requirements (latency, throughput, resource usage)
  - *Details:* Measure I/O throughput (IOPS, bandwidth) with multiple virtio-scsi disks under concurrent fio workloads; compare multi-thread vs. single-thread baseline

- [ ] **Scale Testing** — Validates feature behavior under increased load and at production-like scale
  - *Details:* Not applicable for initial phase; thread allocation is per-VM and bounded by vCPU count

- [ ] **Security Testing** — Verifies security requirements, RBAC, authentication, authorization, and vulnerability scanning
  - *Details:* No new RBAC or security boundaries introduced; existing VM access controls apply

- [ ] **Usability Testing** — Validates user experience and accessibility requirements
  - *Details:* No UI changes; the feature is configured via VM spec YAML. Users receive feedback through VM status conditions and events if misconfigured.

- [ ] **Monitoring** — Does the feature require metrics and/or alerts?
  - *Details:* TBD — confirm with dev team whether new metrics for IOThread allocation are exposed

**Integration & Compatibility**

- [x] **Compatibility Testing** — Ensures feature works across supported platforms, versions, and configurations
  - *Details:* Verify backward compatibility: VMs created without IOThreadsPolicy must behave identically to pre-feature behavior

- [x] **Upgrade Testing** — Validates upgrade paths from previous versions, data migration, and configuration preservation
  - *Details:* Verify that enabling the feature gate after upgrade allows existing VMs to use multi-threaded SCSI controller on next restart; verify disabling the feature gate reverts to single-thread behavior

- [ ] **Dependencies** — Blocked by deliverables from other components/products
  - *Details:* Requires libvirt 11.2.0+ and QEMU 10.0+ in the OpenShift Virtualization stack; blocked until these versions are available in the target OCP release

- [ ] **Cross Integrations** — Does the feature affect other features or require testing by other teams?
  - *Details:* Live migration must preserve IOThread mapping; snapshot and backup operations on VMs with multi-threaded SCSI controllers should be unaffected

**Infrastructure**

- [ ] **Cloud Testing** — Does the feature require multi-cloud platform testing?
  - *Details:* Not applicable; virtio-scsi with IOThreads requires bare-metal or nested virtualization with hardware passthrough, which is not available on standard cloud instances

#### **3. Test Environment**

- **Cluster Topology:** 3-master/3-worker bare-metal

- **OCP & OpenShift Virtualization Version(s):** [TBD]

- **CPU Virtualization:** VT-x (Intel) or AMD-V enabled

- **Compute Resources:** Minimum per worker node: 8 vCPUs, 32GB RAM

- **Special Hardware:** N/A

- **Storage:** ocs-storagecluster-ceph-rbd-virtualization

- **Network:** OVN-Kubernetes, IPv4

- **Required Operators:** N/A

- **Platform:** Bare metal

- **Special Configurations:** N/A

#### **3.1. Testing Tools & Frameworks**

- **Test Framework:** Standard

- **CI/CD:** N/A

- **Other Tools:** fio (for I/O workload generation during performance testing)

#### **4. Entry Criteria**

The following conditions must be met before testing can begin:

- [ ] Requirements and design documents are **approved and merged**
- [ ] Feature gate is implemented and available in the target build
- [ ] Test environment has libvirt 11.2.0+ and QEMU 10.0+ available
- [ ] Test environment can be **set up and configured** (see Section II.3 - Test Environment)

#### **5. Risks**

**Timeline/Schedule**

- **Risk:** Feature depends on upstream KubeVirt v1.10 release timeline; delays in upstream graduation may push downstream testing
  - **Mitigation:** Track upstream milestone progress; begin test development against development builds before formal release
  - *Estimated impact on schedule:* Up to one sprint delay if upstream graduation slips
  - *Sign-off:* [Name/Date]

**Test Coverage**

- **Risk:** Performance testing results may vary across hardware configurations, making it difficult to establish a universal baseline
  - **Mitigation:** Define performance baselines on reference hardware; document hardware specs alongside results for reproducibility
  - *Areas with reduced coverage:* Performance benchmarks may not generalize across all supported hardware
  - *Sign-off:* [Name/Date]

**Test Environment**

- **Risk:** Required libvirt/QEMU versions may not be available in early test builds
  - **Mitigation:** Coordinate with platform team to confirm libvirt/QEMU version availability in target OCP builds; use development builds for early testing if needed
  - *Missing resources or infrastructure:* libvirt 11.2.0+ / QEMU 10.0+ in test environment
  - *Sign-off:* [Name/Date]

**Untestable Aspects**

- **Risk:** No untestable aspects identified
  - **Mitigation:** All functional requirements are testable in the target environment

**Resource Constraints**

- **Risk:** No resource constraints identified
  - **Mitigation:** Standard QE team capacity is sufficient for the test scope

**Dependencies**

- **Risk:** Feature depends on upstream KubeVirt changes and libvirt/QEMU versions shipping in the target OCP release
  - **Mitigation:** Monitor upstream PRs and coordinate with the platform team on dependency versions
  - *Dependent teams or components:* KubeVirt upstream, OpenShift platform (libvirt/QEMU packaging)
  - *Sign-off:* [Name/Date]

---

### **III. Test Scenarios & Traceability**

- **[CNV-86526]** — As a user, I want to dedicate multiple I/O threads for my virtio-scsi disks so that I can gain a performance increase during heavy I/O operations
  - *Test Scenario:* [Tier 1] Verify VM with IOThreadsPolicy and virtio-scsi disks uses multiple I/O threads on the SCSI controller when feature gate is enabled
  - *Priority:* P0

- **[CNV-86526]**
  - *Test Scenario:* [Tier 1] Verify VM with virtio-scsi disks falls back to single-thread SCSI controller when feature gate is disabled
  - *Priority:* P0

- **[CNV-86526]**
  - *Test Scenario:* [Tier 1] Verify shared IOThreadsPolicy assigns the same I/O thread to the SCSI controller and all disks
  - *Priority:* P0

- **[CNV-86526]**
  - *Test Scenario:* [Tier 1] Verify auto IOThreadsPolicy distributes I/O threads to the SCSI controller, capped at the number of vCPUs
  - *Priority:* P0

- **[CNV-86526]**
  - *Test Scenario:* [Tier 1] Verify supplementalPool IOThreadsPolicy shares the supplemental thread pool with the SCSI controller
  - *Priority:* P0

- **[CNV-86526]**
  - *Test Scenario:* [Tier 2] Verify VM with mixed virtio-blk and virtio-scsi disks allocates I/O threads correctly under each policy
  - *Priority:* P0

- **[CNV-86526]**
  - *Test Scenario:* [Tier 2] Verify hotplugging a virtio-scsi disk into a running VM with IOThreadsPolicy uses the existing thread pool
  - *Priority:* P1

- **[CNV-86526]**
  - *Test Scenario:* [Tier 1] Verify SCSI controller thread count is capped at the number of virtqueues when I/O threads exceed vCPUs
  - *Priority:* P1

- **[CNV-86526]**
  - *Test Scenario:* [Tier 2] Verify live migration preserves I/O thread allocation on the SCSI controller
  - *Priority:* P1

- **[CNV-86526]**
  - *Test Scenario:* [Tier 2] Verify disabling the feature gate does not disrupt existing running VMs
  - *Priority:* P1

- **[CNV-86526]**
  - *Test Scenario:* [Tier 3] Verify measurable I/O throughput improvement with multiple virtio-scsi disks under concurrent I/O load vs single-thread baseline
  - *Priority:* P2

---

### **IV. Sign-off and Approval**

This Software Test Plan requires approval from the following stakeholders:

* **Reviewers:**
  - QE Architect (OCP-V): Ruth Netser (@rnetser)
  - QE Members (OCP-V): Jenia Peimer (@jpeimer), Kate Shvaika (@kshvaika), Jose Manuel Castano (@joscasta)
* **Approvers:**
  - QE Lead: Ruth Netser (@rnetser)
  - Dev Lead: Danny Sanatar (@dsanatar)
  - PM: Peter Lauterbach (@pelauter)
