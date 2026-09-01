# Openshift-virtualization-tests Test plan

## **MIG vGPU - Quality Engineering Plan**

### **Metadata & Tracking**

- **Enhancement(s):** N/A — no VEP/enhancement proposal; feature tracked via
  [VIRTSTRAT-166](https://redhat.atlassian.net/browse/VIRTSTRAT-166)
- **Feature Tracking:** [VIRTSTRAT-166](https://redhat.atlassian.net/browse/VIRTSTRAT-166)
- **Epic Tracking:** [CNV-13713](https://redhat.atlassian.net/browse/CNV-13713)
- **Feature Maturity:**
  - DP: N/A
  - TP: N/A
  - GA: v4.21.0
- **QE Owner(s):** Akriti Gupta
- **Owning SIG:** sig-virt
- **Participating SIGs:** sig-virt

**Document Conventions:**

- **MIG** — Multi-Instance GPU: NVIDIA technology that partitions a single physical GPU into multiple isolated instances
- **vGPU** — Virtual GPU: GPU virtualization that allows multiple VMs to share a physical GPU
- **MIG vGPU** — A vGPU slice backed by a MIG instance, combining MIG isolation with GPU virtualization

### **Feature Overview**

Enable support for MIG-backed NVIDIA vGPUs within OpenShift Virtualization, allowing users to allocate
GPU resources more efficiently by leveraging NVIDIA's Multi-Instance GPU (MIG) technology.
Customers can run multiple VMs sharing the same physical GPU while NVIDIA's MIG technology provides
hardware-level isolation between workloads.

---

### **I. Motivation and Requirements Review (QE Review Guidelines)**

This section documents the mandatory QE review process. The goal is to understand the feature's value,
technology, and testability before formal test planning.

#### **1. Requirement & User Story Review Checklist**

- [x] **Review Requirements**
  - *List the key D/S requirements reviewed:*
    - GPU nodes advertise the configured MIG vGPU resources after MIG setup
    - The guest OS can detect the assigned GPU device
    - VMs with MIG vGPU devices can be created and reach Running state
    - Multiple VMs can share a single physical GPU concurrently using MIG slices

- [x] **Understand Value and Customer Use Cases**
  - *Describe the feature's value to customers:* Customers running AI/ML and HPC workloads require
    dedicated, isolated GPU resources per VM. MIG vGPU provides hardware-level isolation, allowing safe multi-tenancy on GPU hardware while maximizing utilization.
  - *List the customer use cases identified:*
    - As a cluster administrator, I want to configure MIG vGPU devices on my GPU nodes so that multiple
      VMs can share a single physical GPU with hardware-level isolation
    - As a VM user, I want to request a MIG vGPU device for my VM so that I can run GPU-accelerated
      workloads.

- [x] **Testability**
  - *Note any requirements that are unclear or untestable:* None identified; all acceptance criteria
    are observable via node resource availability and guest-visible GPU presence.

- [x] **Acceptance Criteria**
  - *List the acceptance criteria:*
    - GPU node advertises the configured MIG vGPU resources after setup
    - A VM requesting a MIG vGPU device reaches Running state and the guest detects the GPU
    - Two VMs sharing the same physical GPU via MIG slices are both operational concurrently
    - A VM requesting a MIG vGPU when no capacity remains stays Pending/unschedulable and exposes
      observable scheduling feedback (events or messages)
  - *Note any gaps or missing criteria:* None

- [x] **Non-Functional Requirements (NFRs)**
  - *List applicable NFRs and their targets:*
    - **Reliability:** GPU device must be visible inside the VM after successful MIG vGPU assignment
    - **Documentation:** MIG vGPU setup and VM configuration documented —
      [CNV-75353](https://redhat.atlassian.net/browse/CNV-75353)
  - *Note any NFRs not covered and why:*
    - **Performance:** N/A
    - **Monitoring:** No new metrics or alerts introduced by this feature in this cycle
    - **UI:** N/A for graphical console — no KubeVirt UI changes; MIG device exposure is owned by
      the NVIDIA GPU Operator. Customer-facing usability for VM status and event feedback is covered
      in Section II.2 (Usability Testing).
      *PM/Lead Agreement:* Martin Tessun 11/25
    - **Scalability:** No new CNV scale requirements. Two-VM concurrent scenario is functional coverage only; no dedicated scale
    testing.

    - **Security:** N/A — hardware-level isolation is enforced by NVIDIA GPU firmware; device
      exposure is provided by the NVIDIA GPU Operator. OpenShift Virtualization adds no isolation
      mechanism here; QE validates VM consumption of advertised MIG vGPU devices only.

#### **2. Known Limitations**

- **MIG vGPU is only supported on NVIDIA GPUs with MIG capability (e.g., A100, A30, H100)**
  - *Sign-off:* Martin Tessun 11/25


#### **3. Technology and Design Review**

- [x] **Developer Handoff/QE Kickoff**
  - *Key takeaways and concerns:*
    - MIG mode must be enabled on the GPU node before any MIG vGPU devices can be created
    - The NVIDIA GPU Operator handles MIG profile configuration
    - VM request MIG vGPU devices using standard GPU device resource requests
    - Node scheduling respects MIG vGPU resource availability

- [x] **Technology Challenges**
  - *List identified challenges:*
    - Requires NVIDIA MIG-capable GPU hardware in the test cluster (A30, A100, or H100)
    - MIG profile configuration and GPU Operator setup must be completed before tests run
  - *Impact on testing approach:* Tests can only execute on nodes with supported GPU hardware;
    standard CI nodes cannot run these tests.

- [x] **API Extensions**
  - *List new or modified APIs:* No new APIs
  - *Testing impact:* N/A

- [x] **Test Environment Needs**
  - *See environment requirements in Section II.3 and testing tools in Section II.3.1*

- [x] **Topology Considerations**
  - *Describe topology requirements:* At least one worker node with an NVIDIA A30 GPU and the
    NVIDIA GPU Operator installed and configured for MIG mode
  - *Impact on test design:* Tests must use node selectors or node affinity rules targeting
    the GPU-equipped node

### **II. Software Test Plan (STP)**

This STP serves as the **overall roadmap for testing**, detailing the scope, approach, resources, and schedule.

#### **1. Scope of Testing**

**Testing Goals**

- **[P0]** As a cluster admin, I can see MIG vGPU devices advertised in node capacity after MIG configuration
- **[P0]** As a VM operator, I can create a VM with a MIG vGPU device, the VM reaches Running state,
  and the GPU device is visible inside the VM
- **[P1]** As a cluster admin, I can run two VMs concurrently, each using one MIG vGPU slice from the
  same physical GPU.
- **[P1]** As a VM operator, when I request a MIG vGPU slice and no capacity remains, the VM does not
  start and I can observe why (Pending/scheduling state and related events or messages).

**Out of Scope (Testing Scope Exclusions)**

- **Legacy GPUs without MIG support**
  - *Rationale:* Only Ampere and Hopper generation GPUs that support MIG are targeted; testing on
    non-MIG GPUs provides no value for this feature
  - *PM/Lead Agreement:* Martin Tessun 11/25

- **Custom MIG topologies beyond standard configurations**
  - *Rationale:* Standard MIG slicing profiles recognized by the NVIDIA GPU Operator are assumed;
    custom or non-standard MIG topologies are not tested
  - *PM/Lead Agreement:* Martin Tessun 11/25

- **Non-RHEL guest OS validation**
  - *Rationale:* This cycle validates MIG vGPU with RHEL guests only. Other guests need NVIDIA
    drivers maintained and shipped by NVIDIA to work properly, so RHEL testing is sufficient for
    OpenShift Virtualization verification.
  - *PM/Lead Agreement:* Martin Tessun 11/25

- **GPU performance benchmarking inside VMs**
  - *Rationale:* NVIDIA owns GPU performance validation for their drivers and hardware. OpenShift
    Virtualization is not in that cycle; this STP covers functional GPU visibility and basic
    operation only.
  - *PM/Lead Agreement:* Martin Tessun 07/29

- **MIG profile configuration and GPU Operator installation**
  - *Rationale:* Infrastructure pre-configuration is handled by DevOps outside test scope; tests
    assume a correctly configured GPU node
  - *PM/Lead Agreement:* Martin Tessun 11/25

**Test Limitations**

- **Testing is limited to the NVIDIA A30 GPU — other supported MIG-capable GPUs (e.g., A100,
  H100/H200) are not available in the test environment**
  - *Sign-off:* Martin Tessun 11/25

- **Only one GPU node is available — tests cannot validate multi-GPU-node scenarios**
  - *Sign-off:* Martin Tessun 11/25

- **Windows guest OS cannot be validated** — MIG vGPU for Windows is only supported on RTX Pro
  6000 hardware; the available test hardware (NVIDIA A30) does not support Windows MIG vGPU
  - *Sign-off:* Martin Tessun 11/25

#### **2. Test Strategy**

**Functional**

- [x] **Functional Testing** — Validates that the feature works according to specified requirements
  - *Details:* Functional tests cover node resource advertisement, VM creation with MIG vGPU,
    in-VM GPU visibility, concurrent multi-VM execution on a shared GPU, and negative coverage
    when a VM requests a MIG vGPU with no remaining capacity.

- [x] **Automation Testing** — Confirms test automation plan is in place for CI and regression coverage
  - *Details:* All test scenarios will be automated using openshift-virtualization-tests framework

- [x] **Regression Testing** — Verifies that new changes do not break existing functionality
  - *Details:* Existing GPU passthrough and vGPU tests will be included in regression scope to
    ensure MIG vGPU changes do not break non-MIG GPU workflows.

- [ ] **Self-Validation Testing**
  - *Details:* N/A. MIG vGPU tests require specialized GPU hardware not available in self-validation
    environments.

**Non-Functional**

- [ ] **Performance Testing**
  - *Details:* N/A. No CNV performance code changes; GPU performance is hardware-defined.

- [ ] **Scale Testing**
  - *Details:* N/A. Two-VM concurrent scenario is functional coverage only; no dedicated scale
    testing.

- [ ] **Security Testing**
  - *Details:* Out of scope. Isolation is enforced by NVIDIA GPU firmware and device exposure is
    provided by the NVIDIA GPU Operator; OpenShift Virtualization adds no isolation mechanism.
    QE validates VM consumption of advertised MIG vGPU devices only.

- [x] **Usability Testing** — Validate that VM status and events provide clear feedback when a
  MIG vGPU device is successfully assigned.

- [ ] **Monitoring**
  - *Details:* N/A. No new metrics or alerts introduced by this feature.

**Integration & Compatibility**

- [x] **Compatibility Testing** — Tests run on the target OCP + OpenShift Virtualization version
  with NVIDIA GPU Operator.

- [ ] **Upgrade Testing**
  - *Details:* N/A. No upgrade testing is required.

- [x] **Dependencies** — Requires NVIDIA GPU Operator installed and MIG mode enabled. Cluster
  configuration tracked in [CNV-67712](https://redhat.atlassian.net/browse/CNV-67712) is complete;
  the cluster deploy job enables MIG vGPU configuration automatically.

- [ ] **Cross Integrations**
  - *Details:* N/A. MIG vGPU is self-contained; no other features share this code path.

**Infrastructure**

- [ ] **Cloud Testing**
  - *Details:* N/A. Feature requires bare-metal nodes with NVIDIA GPU hardware.

#### **3. Test Environment**

- **Cluster Topology:** 3-control-plane/3-worker bare-metal (at least one worker node with NVIDIA A30 GPU)

- **OCP & OpenShift Virtualization Version(s):** OCP 4.21 with OpenShift Virtualization 4.21

- **CPU Virtualization:** VT-x (Intel) or AMD-V enabled

- **Compute Resources:** GPU node requires an NVIDIA A30 GPU with MIG capability

- **Special Hardware:** NVIDIA A30 GPU on at least one worker node

- **Storage:** ocs-storagecluster-ceph-rbd-virtualization

- **Network:** OVN-Kubernetes, IPv4

- **Required Operators:** NVIDIA GPU Operator (with MIG mode and vGPU manager configured)

- **Platform:** Bare metal

- **Special Configurations:** GPU node must have MIG mode enabled and appropriate MIG profiles
  configured prior to test execution

#### **3.1. Testing Tools & Frameworks**

- **Test Framework:** Standard

- **CI/CD:** N/A

- **Other Tools:** N/A

#### **3.2. DevOps & Cluster Provisioning**

MIG vGPU configuration is enabled as part of the cluster deployment pipeline.
This work was completed under [CNV-67712](https://redhat.atlassian.net/browse/CNV-67712).

- **Cluster Deploy Job:** The cluster deploy job enables MIG vGPU configuration on nodes equipped
  with the NVIDIA A30 GPU. This includes:
  - Enabling MIG mode on the GPU node during cluster provisioning
  - Applying the appropriate MIG partition profile (e.g., `1g.6gb`) via the NVIDIA GPU Operator

- **Reference:** [CNV-67712 — Enable MIG vGPU configuration via the cluster deploy job](https://redhat.atlassian.net/browse/CNV-67712)

#### **4. Entry Criteria**

The following conditions must be met before testing can begin:

- [x] Requirements and design documents are **approved and merged**
- [x] Test environment can be **set up and configured** (see Section II.3 - Test Environment)
- [x] NVIDIA GPU Operator is installed and MIG mode is enabled on the target GPU node
- [x] [CNV-67712](https://redhat.atlassian.net/browse/CNV-67712) is resolved — cluster deploy job
  enables MIG vGPU configuration automatically

#### **5. Risks**

**Timeline/Schedule**

- **Risk:** No schedule risk identified
  - **Mitigation:** Feature scope is well-defined and limited to basic MIG vGPU functionality

**Test Coverage**

- **Risk:** Coverage limited to single GPU model (A30) — other MIG-capable GPUs not validated
  - **Mitigation:** A30 is representative of MIG functionality; additional GPU models can be
    validated in future cycles when hardware becomes available
  - *Areas with reduced coverage:* A100, H100/H200 GPU models
  - *Sign-off:* Martin Tessun 11/25

**Test Environment**

- **Risk:** Only one NVIDIA A30 GPU node exists in a single cluster; if the node or cluster is
  unavailable (e.g., hardware failure, cluster maintenance), all MIG vGPU testing is blocked
  with no fallback environment
  - **Mitigation:** None — no alternative GPU hardware or cluster is available; testing is fully
    dependent on this single node's availability
  - *Missing resources or infrastructure:* Redundant GPU node or secondary GPU cluster
  - *Sign-off:* Martin Tessun 11/25

**Resource Constraints**

- **Risk:** Only one node in the cluster supports A30 hardware; if the node is unavailable,
  all MIG vGPU testing is blocked
  - **Mitigation:** None — no alternative A30 hardware available
  - *Current capacity gaps:* Single A30 node, no redundancy
  - *Sign-off:* Martin Tessun 11/25

**Untestable Aspects**

- **Risk:** No untestable aspects — all functional requirements are observable via node resource
  availability and guest-visible GPU presence
  - **Mitigation:** N/A

**Dependencies**

- **Risk:** No dependency risk — CNV-67712 (cluster provisioning with MIG vGPU) is resolved
  - **Mitigation:** N/A

---

### **III. Test Scenarios & Traceability**

- **[CNV-38740](https://redhat.atlassian.net/browse/CNV-38740)** — As a cluster administrator,
  I want to see MIG vGPU resources available on GPU nodes after MIG configuration
  - *Test Scenario:* [Tier 2] Verify GPU node advertises MIG vGPU resources after MIG setup
  - *Priority:* P0

- **[CNV-38740](https://redhat.atlassian.net/browse/CNV-38740)** — As a VM user, I want to create
  a VM with a MIG vGPU device so my workload can use GPU acceleration
  - *Test Scenario:* [Tier 2] Verify a VM requesting a MIG vGPU device reaches Running state
    and the guest detects the GPU
  - *Priority:* P0

- **[CNV-38740](https://redhat.atlassian.net/browse/CNV-38740)** — As a cluster administrator,
  I want multiple VMs to share a single physical GPU using MIG slices
  - *Test Scenario:* [Tier 2] Verify two VMs sharing the same GPU via MIG slices run concurrently
  - *Priority:* P1

- **[CNV-38740](https://redhat.atlassian.net/browse/CNV-38740)** — As a VM operator, when no MIG
  vGPU capacity remains, I want clear feedback that my VM cannot be scheduled
  - *Test Scenario:* [Tier 2] With all MIG vGPU slices consumed, create another VM requesting a
    MIG vGPU device; verify the VM remains Pending/unschedulable and capture the scheduling
    events or messages shown to the user (file an RFE if feedback is unclear)
  - *Priority:* P1

---

### **IV. Sign-off and Approval**

This Software Test Plan requires approval from the following stakeholders:

* **Reviewers:**
  - QE Member: dshchedr / @dshchedr
  - QE Member: vsibirsk / @vsibirsk
  - QE Architect: Ruth Netser / @rnetser
  - QE Member: SamAlber / @SamAlber
* **Approvers:**
  - QE Member: dshchedr / @dshchedr
  - QE Member: vsibirsk / @vsibirsk
  - QE Architect: Ruth Netser / @rnetser
  - Product Manager: Martin Tessun / @mtessun
  - Dev Lead: Lee Yarwood / @lyarwood
