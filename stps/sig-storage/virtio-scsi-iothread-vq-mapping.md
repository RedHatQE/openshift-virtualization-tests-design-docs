# Openshift-virtualization-tests Test plan

## **IOThread Virtqueue Mapping for virtio-scsi - Quality Engineering Plan**

### **Metadata & Tracking**

- **Enhancement(s):** [VEP #343: IOThread Virtqueue Mapping for virtio-scsi](https://github.com/kubevirt/enhancements/pull/343)
- **Feature Tracking:** [CNV-86526](https://redhat.atlassian.net/browse/CNV-86526)
- **Epic Tracking:** [CNV-86526](https://redhat.atlassian.net/browse/CNV-86526)
- **Feature Maturity:**

  - DP: v1.10
  - TP: N/A
  - GA: N/A
- **QE Owner(s):** Jose Manuel Castano (joscasta@redhat.com)
- **Owning SIG:** sig-storage
- **Participating SIGs:** sig-storage
- **Status:** Draft — QE kickoff pending; do not approve until kickoff is recorded

**Document Conventions (if applicable):**

| Term | Definition |
|:-----|:-----------|
| **IOThread** | A dedicated host thread used to process disk I/O outside the main QEMU thread, reducing CPU contention |
| **Virtqueue** | A queue used by virtio devices to exchange data between the guest and the host |
| **IOThreadsPolicy** | A VM-level setting that controls how I/O threads are allocated to virtio-blk disks and to the virtio-scsi controller's virtqueues (shared, auto, or supplementalPool) |

### **Feature Overview**

This STP covers the **Dev Preview (v1.10)** phase of IOThread virtqueue mapping for virtio-scsi.

Virtual machines that use multiple virtio-scsi disks can experience reduced I/O throughput under heavy workloads because the SCSI controller processes all disk I/O on a single thread. This feature allows the SCSI controller to distribute I/O processing across multiple dedicated threads, enabling parallel disk operations and reducing CPU contention on the host. Additionally, the existing `auto` policy is modified so that each disk — regardless of bus type — is allocated the full auto thread pool instead of a single round-robin thread.

Users opt in by setting an I/O thread policy on the VM specification and enabling the corresponding feature gate on the cluster. Three policies are available: a shared mode where all virtio-blk disks and the SCSI controller's virtqueues share one thread, an automatic mode that scales threads with the number of virtual CPUs, and a supplemental pool mode suited for workloads that frequently hotplug disks. When the feature gate is disabled, running VMs remain unchanged until restart, and new or restarted VMs use the existing single-thread behavior; the `auto` policy also reverts to assigning a single round-robin thread.

The primary benefit is improved I/O throughput for storage-intensive workloads such as databases or analytics pipelines running on VMs with multiple virtio-scsi disks.

---

### **I. Motivation and Requirements Review (QE Review Guidelines)**

#### **1. Requirement & User Story Review Checklist**

- [x] **Review Requirements**
  - *List the key D/S requirements reviewed:*
    - The existing IOThreadsPolicy API (shared, auto, supplementalPool) must be used to allocate additional I/O threads to the virtio-scsi controller without changes to the API itself
    - The existing `auto` policy must be modified so that each disk is allocated the full auto thread pool instead of a single round-robin thread, aligning behavior across virtio-blk and virtio-scsi bus types
    - Feature must be gated behind a feature gate; disabled by default
    - Thread count allocated to disks must not exceed the number of virtqueues (equal to vCPU count) for both virtio-blk and virtio-scsi

- [x] **Understand Value and Customer Use Cases**
  - *Describe the feature's value to customers:* Customers running database or storage-intensive workloads on VMs with multiple virtio-scsi disks can achieve higher I/O throughput by distributing I/O processing across multiple host threads, eliminating the single-thread bottleneck on the SCSI controller.
  - *List the customer use cases identified:*
    - As a user, I want to dedicate multiple I/O threads for my virtio-scsi disks so that I can gain a performance increase during heavy I/O operations
    - As a user, I want VMs using the auto policy to benefit from per-queue IOThread assignment regardless of bus type
    - As a cluster admin, I want to use the supplementalPool policy with hotplug-heavy workloads so that the SCSI controller has a sufficient thread pool for dynamically added disks

- [x] **Testability**
  - *Note any requirements that are unclear or untestable:* None

- [x] **Acceptance Criteria**
  - *List the acceptance criteria:*
    - When the feature gate is enabled and IOThreadsPolicy is set, the virtio-scsi controller allocates I/O threads according to the selected policy
    - When the feature gate is disabled, running VMs retain their current I/O thread allocation until the next restart; after restart, the virtio-scsi controller uses the existing single-thread behavior regardless of IOThreadsPolicy, and the `auto` policy reverts to assigning a single round-robin thread to virtio-blk disks
    - With the shared policy, the SCSI controller maps all its virtqueues to a single shared I/O thread
    - With the auto policy, each virtio-blk disk and the SCSI controller's virtqueues are allocated the full pool of non-dedicated I/O threads, up to a maximum of one thread per virtqueue (one virtqueue per vCPU)
    - With the supplementalPool policy, the SCSI controller maps its virtqueues to I/O threads drawn from a supplemental pool, separate from the threads used for per-disk virtio-blk mappings
    - Hotplugging virtio-scsi disks into a running VM with IOThreadsPolicy set uses the thread pool established at VM startup; a continuous fio writer on existing disks must complete with no I/O errors
    - Live migration of a VM with IOThreadsPolicy set must preserve the policy behavior on the destination node; a continuous fio writer on all disks must complete with no I/O errors
    - VMs with mixed virtio-blk and virtio-scsi disks allocate I/O threads correctly to both device types
    - On environments with libvirt < 11.2.0 or QEMU < 10.0, creating a VM with IOThreadsPolicy and the feature gate enabled must be rejected with a validation error indicating the unsupported version
  - *Note any gaps or missing criteria:* None

- [x] **Non-Functional Requirements (NFRs)**
  - *List applicable NFRs and their targets:*
    - Performance: with 4 virtio-scsi disks under concurrent fio random-read workloads, aggregate IOPS with IOThreadsPolicy auto must be at least 20% higher than the single-thread baseline (feature gate disabled, same VM configuration). The baseline and target runs must each complete 3 iterations on the same hardware; the result passes only if the mean improvement meets the threshold and no individual iteration falls below 10%
    - Monitoring: no new metrics or alerts are introduced for IOThread allocation; existing VM metrics remain sufficient for observability
    - Documentation: user-facing documentation must describe the feature gate and policy behavior for virtio-scsi
  - *Note any NFRs not covered and why:*
    - Security: no new RBAC or authentication changes; existing access controls apply
    - Scalability: no new cluster-level scale requirements; thread allocation is per-VM
    - UI: no UI changes introduced; the feature is configured entirely through the VM spec YAML and has no console integration

#### **2. Known Limitations**

- **SCSI controller maps I/O threads to virtqueues, not to individual disks**
  - Unlike virtio-blk, where each disk can get a dedicated thread, the SCSI controller distributes threads across virtqueues. Users cannot assign a specific thread to a specific disk.
  - *Sign-off:* [Name/Date]

- **Hotplug with auto policy is limited by the thread pool size set at VM startup**
  - The SCSI controller's thread pool is initialized when the VM starts and cannot be modified at runtime. If many virtio-scsi disks are hotplugged later, the controller may have fewer threads than optimal. Users needing heavy hotplug should use the supplementalPool policy instead.
  - *Sign-off:* [Name/Date]

#### **3. Technology and Design Review**

- [ ] **Developer Handoff/QE Kickoff**
  - *Participants:* TBD
  - *Date:* TBD
  - *Key takeaways and concerns:* TBD — kickoff meeting with dev team to be scheduled before test execution begins
  - *Decisions:* TBD
  - *Sign-off:* TBD — must be recorded before STP can move from Draft to Approved

- [x] **Technology Challenges**
  - *List identified challenges:*
    - Requires libvirt 11.2.0+ and QEMU 10.0+ for virtio-scsi IOThread virtqueue mapping support
    - Verifying correct thread-to-virtqueue mapping requires inspecting domain XML or guest-visible I/O distribution
  - *Impact on testing approach:* Tests must validate on environments with the required libvirt/QEMU versions. On environments that do not meet the minimum versions (libvirt < 11.2.0 or QEMU < 10.0), the VM must be rejected at creation with a clear validation error indicating the unsupported version; silent degradation to single-thread behavior is not acceptable. The target OCP release ships libvirt 11.2.0+ and QEMU 10.0+; this rejection path applies only to clusters running older or mixed-version infrastructure

- [x] **API Extensions**
  - *List new or modified APIs:* No new user-facing APIs; the existing IOThreadsPolicy field in the VM spec is reused to control I/O thread allocation for the virtio-scsi controller's virtqueues. The `auto` policy behavior is modified: each virtio-blk disk and the SCSI controller's virtqueues now receive the full auto thread pool instead of a single round-robin thread.
  - *Testing impact:* Tests must verify that existing IOThreadsPolicy values (shared, auto, supplementalPool) produce correct virtqueue-level mapping for the virtio-scsi controller, and that the modified `auto` policy allocates thread pools to virtio-blk disks

- [x] **Test Environment Needs**
  - *See environment requirements in Section II.3 and testing tools in Section II.3.1*

- [x] **Topology Considerations**
  - *Describe topology requirements:* Standard cluster topology; no multi-cluster or special network topology requirements
  - *Impact on test design:* Live migration tests require at least two schedulable worker nodes

### **II. Software Test Plan (STP)**

#### **1. Scope of Testing**

**Testing Goals**

*Functional*

- **[P0]** Verify that each IOThreadsPolicy (shared, auto, supplementalPool) produces predictable, policy-consistent I/O behavior for VMs with virtio-scsi disks when the feature gate is enabled
- **[P1]** Verify that VM creation is rejected with a version-unsupported validation error when libvirt < 11.2.0 or QEMU < 10.0
- **[P0]** Verify that the `auto` policy allocates the full auto thread pool to each disk regardless of bus type (virtio-blk and virtio-scsi)
- **[P0]** Verify that VMs with mixed virtio-blk and virtio-scsi disks deliver correct I/O behavior for both device types under each policy
- **[P1]** Verify that hotplugging a virtio-scsi disk into a running VM with IOThreadsPolicy set uses the existing thread pool and that a continuous fio writer on existing disks completes with no I/O errors
- **[P1]** Verify that I/O thread allocation per disk does not exceed the number of virtqueues (equal to vCPU count) for both virtio-blk and virtio-scsi, even when the policy would otherwise allocate more threads
- **[P1]** Verify that live migration of a VM with IOThreadsPolicy preserves the policy behavior on the destination node and that a continuous fio writer on all disks completes with no I/O errors

*Upgrade*

- **[P1]** Verify that after a cluster upgrade, enabling the feature gate allows existing VMs with IOThreadsPolicy to use policy-based SCSI controller allocation on next restart, and disabling the feature gate does not disrupt running VMs and reverts behavior on restart

*Regression*

- **[P1]** Verify that disabling the feature gate on a running cluster does not disrupt existing VMs or their I/O workloads, and that restarted VMs revert to single-thread SCSI controller behavior and the `auto` policy reverts to single round-robin thread assignment
- **[P2]** Verify that VMs with virtio-scsi disks achieve improved I/O throughput (at least 20% mean IOPS improvement across 3 iterations, no individual iteration below 10%) under concurrent fio random-read workloads compared to the single-thread baseline

**Out of Scope (Testing Scope Exclusions)**

- **Adding new IOThreadsPolicy values**
  - *Rationale:* This feature reuses the existing IOThreadsPolicy API; no new policy values are introduced
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
  - *Details:* Existing IOThread tests for virtio-blk must be updated to reflect the new auto policy behavior (thread pool instead of single round-robin thread); sig-storage regression suite runs on the feature cluster

- [x] **Self-Validation Testing** — Should any of the new tests be included in the self-validation test package?
  - *Details:* Yes — include a basic test that verifies a VM with IOThreadsPolicy set and virtio-scsi disks starts successfully and delivers I/O when the feature gate is enabled

**Non-Functional**

- [x] **Performance Testing** — Validates feature performance meets requirements (latency, throughput, resource usage)
  - *Details:* Measure aggregate IOPS with 4 virtio-scsi disks under concurrent fio random-read workloads using IOThreadsPolicy auto; compare against single-thread baseline (feature gate disabled, same VM). Target: at least 20% mean IOPS improvement across 3 iterations, with no individual iteration below 10%. Baseline and target runs execute on the same hardware

- [ ] **Scale Testing** — Validates feature behavior under increased load and at production-like scale
  - *Details:* Not applicable; thread allocation is per-VM and bounded by vCPU count. No cluster-level scaling behavior is introduced.

- [ ] **Security Testing** — Verifies security requirements, RBAC, authentication, authorization, and vulnerability scanning
  - *Details:* Not applicable; no new RBAC roles, security boundaries, or authentication changes are introduced. Existing VM access controls apply.

- [ ] **Usability Testing** — Validates user experience and accessibility requirements
  - *Details:* Not applicable; the feature has no UI component and is configured entirely through the VM spec YAML. Users receive feedback through VM status conditions and events if misconfigured.

- [ ] **Monitoring** — Does the feature require metrics and/or alerts?
  - *Details:* No new metrics are introduced for IOThread allocation; existing VM metrics provide sufficient observability

**Integration & Compatibility**

- [x] **Compatibility Testing** — Ensures feature works across supported platforms, versions, and configurations
  - *Details:* Verify backward compatibility: VMs created without IOThreadsPolicy must behave identically to pre-feature behavior

- [x] **Upgrade Testing** — Validates upgrade paths from previous versions, data migration, and configuration preservation
  - *Details:* Verify that enabling the feature gate after upgrade allows existing VMs to use the IOThreadsPolicy-based SCSI controller allocation on next restart; verify that disabling the feature gate does not disrupt running VMs and that restarted VMs revert to single-thread behavior with the `auto` policy reverting to single round-robin thread assignment

- [x] **Dependencies** — Blocked by deliverables from other components/products
  - *Details:* Requires libvirt 11.2.0+ and QEMU 10.0+ in the OpenShift Virtualization stack; blocked until these versions are available in the target OCP release

- [x] **Cross Integrations** — Does the feature affect other features or require testing by other teams?
  - *Details:* Live migration must preserve IOThread policy behavior on the destination node with bounded I/O interruption (no I/O errors); snapshot and backup operations on VMs with IOThreadsPolicy set should preserve the policy field

**Infrastructure**

- [ ] **Cloud Testing** — Does the feature require multi-cloud platform testing?
  - *Details:* Not applicable; virtio-scsi with IOThreads requires bare-metal or nested virtualization with hardware passthrough, which is not available on standard cloud instances

#### **3. Test Environment**

- **Cluster Topology:** 3-master/3-worker bare-metal

- **OCP & OpenShift Virtualization Version(s):** [TBD]

- **CPU Virtualization:** VT-x (Intel) or AMD-V enabled

- **Compute Resources:** Minimum per worker node: 8 vCPUs, 32GB RAM

- **Special Hardware:** N/A

- **Storage:** ocs-storagecluster-ceph-rbd-virtualization (RWX access mode, Block volume mode required for live-migration scenarios)

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
  - *Test Scenario:* [Tier 1] Verify VM (4 vCPUs, 2 virtio-scsi disks) with each IOThreadsPolicy and feature gate enabled produces the expected iothread-to-virtqueue assignment in the domain XML: shared → 1 iothread mapped to all SCSI virtqueues; auto → min(vCPUs, virtqueues) iothreads each mapped to SCSI virtqueues; supplementalPool → SCSI virtqueues mapped to iothreads from the supplemental pool, separate from virtio-blk iothreads
  - *Priority:* P0

- **[CNV-86526]** — As a user, I want to dedicate multiple I/O threads for my virtio-scsi disks so that I can gain a performance increase during heavy I/O operations
  - *Test Scenario:* [Tier 1] Verify that on a default cluster (feature gate never enabled), the domain XML shows the SCSI controller mapped to a single iothread regardless of the IOThreadsPolicy value set on the VM spec
  - *Priority:* P0

- **[CNV-86526]** — As a user, I want to dedicate multiple I/O threads for my virtio-scsi disks so that I can gain a performance increase during heavy I/O operations
  - *Test Scenario:* [Tier 1] Verify VM with virtio-scsi disks and feature gate explicitly disabled shows a single iothread mapped to the SCSI controller in the domain XML, regardless of IOThreadsPolicy
  - *Priority:* P0

- **[CNV-86526]** — As a user, I want to dedicate multiple I/O threads for my virtio-scsi disks so that I can gain a performance increase during heavy I/O operations
  - *Test Scenario:* [Tier 1] Verify shared IOThreadsPolicy on a VM (4 vCPUs, 2 virtio-scsi disks, 1 virtio-blk disk) produces exactly 1 iothread in the domain XML, with all SCSI controller virtqueues and all virtio-blk disks mapped to that single iothread
  - *Priority:* P0

- **[CNV-86526]** — As a user, I want to dedicate multiple I/O threads for my virtio-scsi disks so that I can gain a performance increase during heavy I/O operations
  - *Test Scenario:* [Tier 1] Verify auto IOThreadsPolicy on a VM (4 vCPUs, 2 virtio-scsi disks, 1 virtio-blk disk) shows in the domain XML that each virtio-blk disk and the SCSI controller's virtqueues are each assigned min(vCPUs, virtqueues) iothreads from the auto pool
  - *Priority:* P0

- **[CNV-86526]** — As a user, I want to dedicate multiple I/O threads for my virtio-scsi disks so that I can gain a performance increase during heavy I/O operations
  - *Test Scenario:* [Tier 1] Verify supplementalPool IOThreadsPolicy on a VM (4 vCPUs, 2 virtio-scsi disks, 1 virtio-blk disk) shows in the domain XML that SCSI controller virtqueues are mapped to iothreads from the supplemental pool and that these iothreads are disjoint from the iothreads assigned to virtio-blk disks
  - *Priority:* P0

- **[CNV-86526]** — As a user, I want VMs using the auto policy to benefit from per-queue IOThread assignment regardless of bus type
  - *Test Scenario:* [Tier 1] Verify auto IOThreadsPolicy on a VM (4 vCPUs, 2 virtio-blk disks, no virtio-scsi) shows in the domain XML that each virtio-blk disk is assigned min(vCPUs, virtqueues) iothreads from the auto pool, not a single round-robin thread
  - *Priority:* P0

- **[CNV-86526]** — As a user, I want to dedicate multiple I/O threads for my virtio-scsi disks so that I can gain a performance increase during heavy I/O operations
  - *Test Scenario:* [Tier 2] Verify VM (4 vCPUs, 2 virtio-scsi disks, 2 virtio-blk disks) with each IOThreadsPolicy shows the expected iothread-to-device assignment in the domain XML: shared → all devices share 1 iothread; auto → each device gets min(vCPUs, virtqueues) iothreads; supplementalPool → SCSI virtqueues use supplemental-pool iothreads disjoint from virtio-blk iothreads
  - *Priority:* P0

- **[CNV-86526]** — As a cluster admin, I want to use the supplementalPool policy with hotplug-heavy workloads so that the SCSI controller has a sufficient thread pool for dynamically added disks
  - *Test Scenario:* [Tier 2] Verify hotplugging a virtio-scsi disk into a running VM with IOThreadsPolicy uses the existing thread pool and a continuous fio writer on existing disks completes with no I/O errors 
  - *Priority:* P1

- **[CNV-86526]** — As a user, I want to dedicate multiple I/O threads for my virtio-scsi disks so that I can gain a performance increase during heavy I/O operations
  - *Test Scenario:* [Tier 1] Verify on a VM with 2 vCPUs and dedicatedIOThread plus a supplemental pool size of 8 that the domain XML shows iothread allocation for both virtio-blk and virtio-scsi disks clamped to 2 (the vCPU/virtqueue count), not 8
  - *Priority:* P1

- **[CNV-86526]** — As a user, I want to dedicate multiple I/O threads for my virtio-scsi disks so that I can gain a performance increase during heavy I/O operations
  - *Test Scenario:* [Tier 2] Verify live migration preserves I/O thread allocation on the SCSI controller and a continuous fio writer on all disks completes with no I/O errors
  - *Priority:* P1

- **[CNV-86526]** — As a user, I want to dedicate multiple I/O threads for my virtio-scsi disks so that I can gain a performance increase during heavy I/O operations
  - *Test Scenario:* [Tier 2] Verify disabling the feature gate does not disrupt I/O on running VMs that have IOThreadsPolicy set
  - *Priority:* P1

- **[CNV-86526]** — As a user, I want to dedicate multiple I/O threads for my virtio-scsi disks so that I can gain a performance increase during heavy I/O operations
  - *Test Scenario:* [Tier 2] Verify that a VM restarted after the feature gate is disabled reverts to single-thread SCSI controller behavior and the `auto` policy reverts to single round-robin thread assignment
  - *Priority:* P1

- **[CNV-86526]** — As a user, I want to dedicate multiple I/O threads for my virtio-scsi disks so that I can gain a performance increase during heavy I/O operations
  - *Test Scenario:* [Tier 2] Verify at least 20% mean aggregate IOPS improvement (3 iterations, no individual iteration below 10%) with 4 virtio-scsi disks under concurrent fio random-read workloads using IOThreadsPolicy auto compared to a baseline with the feature gate disabled and the same VM configuration on the same hardware
  - *Priority:* P2

- **[CNV-86526]** — As a user, I want to dedicate multiple I/O threads for my virtio-scsi disks so that I can gain a performance increase during heavy I/O operations
  - *Test Scenario:* [Tier 2] Verify that creating a VM with IOThreadsPolicy and the feature gate enabled is rejected with a validation error on environments with libvirt < 11.2.0 or QEMU < 10.0
  - *Priority:* P1

- **[CNV-86526]** — As a user, I want to dedicate multiple I/O threads for my virtio-scsi disks so that I can gain a performance increase during heavy I/O operations
  - *Test Scenario:* [Tier 2] Verify that enabling the feature gate after an upgrade allows an existing VM with IOThreadsPolicy to use the policy-based SCSI controller allocation on next restart
  - *Priority:* P1

- **[CNV-86526]** — As a user, I want to dedicate multiple I/O threads for my virtio-scsi disks so that I can gain a performance increase during heavy I/O operations
  - *Test Scenario:* [Tier 2] Verify that disabling the feature gate after an upgrade does not disrupt running VMs and that restarted VMs revert to single-thread SCSI controller behavior and the `auto` policy reverts to single round-robin thread assignment
  - *Priority:* P1

- **[CNV-86526]** — As a user, I want to dedicate multiple I/O threads for my virtio-scsi disks so that I can gain a performance increase during heavy I/O operations
  - *Test Scenario:* [Tier 2] Verify that snapshot and restore of a VM with IOThreadsPolicy set completes successfully and the restored VM spec preserves the IOThreadsPolicy field
  - *Priority:* P1

- **[CNV-86526]** — As a user, I want to dedicate multiple I/O threads for my virtio-scsi disks so that I can gain a performance increase during heavy I/O operations
  - *Test Scenario:* [Tier 2] Verify that backup and restore of a VM with IOThreadsPolicy set completes successfully and the restored VM spec preserves the IOThreadsPolicy field
  - *Priority:* P1

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
