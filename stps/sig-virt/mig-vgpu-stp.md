# Openshift-virtualization-tests Test plan

## **MIG vGPU - Quality Engineering Plan**

### **Metadata & Tracking**

- **Enhancement(s):** [Links to enhancement(s); KubeVirt, OpenShift, etc.]
- **Feature Tracking:** https://redhat.atlassian.net/browse/VIRTSTRAT-166
- **Epic Tracking:** https://redhat.atlassian.net/browse/CNV-13713
  <!-- Tasks must be created to block the feature -->
- **QE Owner(s):** [Name(s)]
- **Owning SIG:** sig-virt
- **Participating SIGs:** [List of participating SIGs]

**Document Conventions:**
- **MIG** — Multi-Instance GPU: NVIDIA technology that partitions a single physical GPU into multiple isolated instances
- **vGPU** — Virtual GPU: GPU virtualization that allows multiple VMs to share a physical GPU
- **MIG vGPU** — A vGPU slice backed by a MIG instance, combining MIG isolation with GPU virtualization
- **RHEL VM** — Red Hat Enterprise Linux Virtual Machine

### **Feature Overview**

<!-- Provide a brief (2-4 sentences) description of the feature being tested.
Include: what it does, why it matters to customers, and key technical components. -->

Enable support for MIG-backed NVIDIA vGPUs within OpenShift Virtualization, allowing users to allocate GPU resources more efficiently and securely by leveraging NVIDIA's Multi-Instance GPU (MIG) technology. This feature helps maximize GPU utilization, reduce resource fragmentation, and provide guaranteed performance for AI/ML or HPC workloads running in KubeVirt-based virtual machines on OpenShift.

---

### **I. Motivation and Requirements Review (QE Review Guidelines)**

This section documents the mandatory QE review process. The goal is to understand the feature's value,
technology, and testability before formal test planning.

#### **1. Requirement & User Story Review Checklist**

<!-- **How to complete this checklist:**
1. **Checkbox**: Mark [x] if the check is complete; if the item cannot be checked - add an explanation why in the `details` section
2. Complete the relevant, needed details for the checklist item -->

- [x] **Review Requirements**
  - *List the key D/S requirements reviewed:*
    - Nodes with supported NVIDIA GPUs must advertise MIG vGPU devices in their `Capacity` and `Allocatable` sections after MIG configuration
    - RHEL VMs must be creatable with a MIG vGPU device attached and reach Running state
    - The MIG vGPU device must be visible inside the RHEL VM via standard PCI enumeration (`lspci`)
    - Multiple RHEL VMs must be able to share the same physical GPU concurrently

- [x] **Understand Value and Customer Use Cases**
  - *Describe the feature's value to customers:* Customers running AI/ML and HPC workloads require dedicated, isolated GPU resources per VM. MIG vGPU provides hardware-level isolation with predictable performance, allowing safe multi-tenancy on expensive GPU hardware while maximizing GPU utilization and reducing resource fragmentation.

- [x] **Testability**
  - *Note any requirements that are unclear or untestable:* None identified at this time; all acceptance criteria are testable via node inspection and in-VM CLI commands.

- [x] **Acceptance Criteria**
  - *List the acceptance criteria:*
    - Node `Capacity` and `Allocatable` fields reflect the configured MIG vGPU device after setup
    - A RHEL VM with a MIG vGPU device request reaches `Running` state
    - `lspci -nnk | grep NVIDIA` inside the RHEL VM returns the expected NVIDIA device entry
    - Two RHEL VMs each assigned one MIG vGPU slice from the same GPU are both reachable and operational concurrently
  - *Note any gaps or missing criteria:* None

- [x] **Non-Functional Requirements (NFRs)**
  - *List applicable NFRs and their targets:*
    - Resource isolation: MIG vGPU instances must not impact each other's performance
    - Supportability: GPU device visibility must be consistent across VM restarts

#### **2. Known Limitations**

- **MIG vGPU is only supported on NVIDIA GPUs that support the MIG feature (e.g., A100, A30, H100); testing is limited to the NVIDIA A30 as that is the only available hardware**
  - *Sign-off:* [Name/Date]

- **Only RHEL guest OS is validated **
  - *Sign-off:* [Name/Date]

- **MIG vGPU for Windows guests is only supported on vGPUs created on RTX Pro 6000 hardware; Windows MIG vGPU is not tested in this cycle as the available hardware is the A30**
  - *Sign-off:* [Name/Date]

- **MIG vGPU configuration requires pre-configuration of the GPU node (MIG mode enabled, MIG profiles set) before VM scheduling**
  - *Sign-off:* [Name/Date]

#### **3. Technology and Design Review**

- [ ] **Developer Handoff/QE Kickoff**
  - *Key takeaways and concerns:* [Summarize key points and concerns]

- [ ] **Technology Challenges**
  - *List identified challenges:*
    - Requires NVIDIA MIG-capable GPU hardware in the test cluster
    - MIG profile configuration and GPU Operator setup must be completed before tests run
  - *Impact on testing approach:* Tests can only execute on nodes with supported GPU hardware.

- [ ] **API Extensions**
  - *List new or modified APIs:* Node resource capacity fields (`nvidia.com/mig-*` resources); VirtualMachine spec GPU device stanza
  - *Testing impact:* Tests must validate node resource advertisement and VM spec GPU device assignment.

- [ ] **Test Environment Needs**
  - *See environment requirements in Section II.3 and testing tools in Section II.3.1*

- [ ] **Topology Considerations**
  - *Describe topology requirements:* At least one worker node with an NVIDIA A30 GPU and the NVIDIA GPU Operator installed and configured for MIG mode.
  - *Impact on test design:* Tests must use node selectors or node affinity rules targeting the GPU-equipped node.

### **II. Software Test Plan (STP)**

This STP serves as the **overall roadmap for testing**, detailing the scope, approach, resources, and schedule.

#### **1. Scope of Testing**

**Testing Goals**

- **[P0]** Verify that a MIG-capable GPU node correctly advertises MIG vGPU devices in its `Capacity` and `Allocatable` node fields after MIG configuration
- **[P0]** Validate that a RHEL VM requesting a MIG vGPU device can be created and reaches `Running` state
- **[P0]** Confirm that the NVIDIA GPU device is visible inside a running RHEL VM via `lspci -nnk | grep NVIDIA`
- **[P1]** Verify that two RHEL VMs, each assigned one MIG vGPU slice from the same physical GPU, can run concurrently without conflict

**Out of Scope (Testing Scope Exclusions)**

- **Legacy GPUs without MIG support**
  - *Rationale:* Only Ampere and Hopper generation GPUs (e.g., A100, H100/H200) or later that support MIG are targeted; testing on non-MIG GPUs is not planned
  - *PM/Lead Agreement:* [Name/Date]

- **Advanced multi-tenancy beyond GPU-level isolation**
  - *Rationale:* Deep security isolation beyond MIG's hardware partitioning (e.g., vTPM integration) is not addressed in this feature
  - *PM/Lead Agreement:* [Name/Date]

- **Custom MIG topologies beyond standard configurations**
  - *Rationale:* Standard MIG slicing profiles recognized by the NVIDIA GPU Operator are assumed; custom or non-standard MIG topologies are not tested
  - *PM/Lead Agreement:* [Name/Date]

- **Windows guest OS**
  - *Rationale:* MIG vGPU for Windows is only supported on RTX Pro 6000 hardware; the available test hardware is the NVIDIA A30, which does not support Windows MIG vGPU
  - *PM/Lead Agreement:* [Name/Date]

- **GPU benchmark / performance testing inside VMs**
  - *Rationale:* No standardized GPU benchmark tooling integrated into CI; performance NFRs deferred to a future cycle
  - *PM/Lead Agreement:* [Name/Date]

- **MIG profile configuration and GPU Operator installation**
  - *Rationale:* Infrastructure pre-configuration is handled outside the test scope; tests assume a correctly configured GPU node
  - *PM/Lead Agreement:* [Name/Date]

**Test Limitations**

- **Testing is limited to the NVIDIA A30 GPU — other supported MIG-capable GPUs (e.g., A100, H100/H200) are not available in the test environment**
  - *Sign-off:* [Name/Date]

- **MIG-capable GPU hardware (e.g., NVIDIA A100) must be available in the test cluster — tests cannot run on standard CI nodes**
  - *Sign-off:* [Name/Date]

#### **2. Test Strategy**

**Functional**

- [x] **Functional Testing** — Validates that the feature works according to specified requirements and user stories
  - *Details:* Functional tests cover node resource advertisement, VM creation with MIG vGPU, in-VM GPU visibility, and concurrent multi-VM execution on a shared GPU.

- [x] **Automation Testing** — Confirms test automation plan is in place for CI and regression coverage
  - *Details:* All test scenarios will be automated using the standard openshift-virtualization-tests and integrated into the GPU-specific CI lane targeting MIG-capable nodes.

- [x] **Regression Testing** — Verifies that new changes do not break existing functionality
  - *Details:* Existing GPU passthrough and vGPU tests will be included in regression scope to ensure MIG vGPU changes do not break non-MIG GPU workflows.

**Non-Functional**

- [ ] **Performance Testing**
  - *Details:* Not applicable this cycle — GPU performance benchmarking inside VMs is out of scope (see Test Limitations).

- [ ] **Scale Testing**
  - *Details:* Not applicable this cycle — limited to a single GPU node; scale testing deferred.

- [ ] **Security Testing**
  - *Details:* N/A — no new RBAC or authentication changes introduced by this feature.

- [x] **Usability Testing**
  - *Details:* Validate that node capacity/allocatable fields are set correctly. Validate that VM status and events provide clear feedback when a MIG vGPU device is successfully assigned or fails to be allocated.

- [ ] **Monitoring**
  - *Details:* N/A — no new metrics or alerts introduced by this feature in this cycle.

**Integration & Compatibility**

- [x] **Compatibility Testing**
  - *Details:* Tests run on the target OCP + OpenShift Virtualization version with NVIDIA GPU Operator. Ensure existing non-MIG vGPU and GPU passthrough tests remain unaffected.

- [ ] **Upgrade Testing**
  - *Details:* Not in scope for this cycle.

- [x] **Dependencies**
  - *Details:* Requires NVIDIA GPU Operator to be installed and MIG mode enabled on the target node before tests execute.

- [ ] **Cross Integrations**
  - *Details:* N/A — no known cross-team integration impacts identified.

**Infrastructure**

- [ ] **Cloud Testing**
  - *Details:* N/A — feature requires bare-metal nodes with MIG supported NVIDIA GPU hardware.

#### **3. Test Environment**

- **Cluster Topology:** 3-master/3-worker bare-metal (at least one worker node with NVIDIA A30 GPU)

- **OCP & OpenShift Virtualization Version(s):** [e.g., OCP 4.21 with OpenShift Virtualization 4.21]

- **CPU Virtualization:** VT-x (Intel) or AMD-V enabled

- **Compute Resources:** GPU node requires an NVIDIA A30 GPU

- **Special Hardware:** NVIDIA A30 GPU on at least one worker node

- **Storage:** ocs-storagecluster-ceph-rbd-virtualization

- **Network:** OVN-Kubernetes, IPv4

- **Required Operators:** NVIDIA GPU Operator (with MIG mode and vGPU manager configured)

- **Platform:** Bare metal

- **Special Configurations:** GPU node must have MIG mode enabled and appropriate MIG profiles configured prior to test execution

#### **3.1. Testing Tools & Frameworks**

- **Test Framework:** openshift-virtualization-tests

- **CI/CD:** N/A

- **Other Tools:** `lspci` (available inside RHEL VM guest OS) for in-VM GPU visibility validation;

#### **3.2. DevOps & Cluster Provisioning**

MIG vGPU configuration must be enabled as part of the cluster deployment pipeline before any tests can execute. This work is tracked under [CNV-67712](https://redhat.atlassian.net/browse/CNV-67712).

- **Cluster Deploy Job:** The cluster deploy job must be extended to enable MIG vGPU configuration on nodes equipped with the NVIDIA A30 GPU. This includes:
  - Enabling MIG mode on the GPU node during cluster provisioning
  - Applying the appropriate MIG partition profile (e.g., `1g.6gb`) via the NVIDIA GPU Operator CRD

- **Tracking:** [CNV-67712 — Enable MIG vGPU configuration via the cluster deploy job](https://redhat.atlassian.net/browse/CNV-67712)

#### **4. Entry Criteria**

The following conditions must be met before testing can begin:

- [ ] Requirements and design documents are **approved and merged**
- [x] Test environment can be **set up and configured** (see Section II.3 - Test Environment)
- [x] NVIDIA GPU Operator is installed and MIG mode is enabled on the target GPU node
- [x] [CNV-67712](https://redhat.atlassian.net/browse/CNV-67712) is resolved — cluster deploy job enables MIG vGPU configuration automatically on the GPU node

#### **5. Risks**

**Timeline/Schedule**

- **Risk:** N/A
  - **Mitigation:** N/A
  - *Estimated impact on schedule:* N/A
  - *Sign-off:* N/A

**Test Coverage**

- **Risk:** N/A
  - **Mitigation:** N/A
  - *Areas with reduced coverage:* N/A
  - *Sign-off:* N/A

**Test Environment**

- **Risk:** Only one NVIDIA A30 GPU node exists in a single cluster; if the node or cluster is unavailable (e.g., hardware failure, cluster maintenance), all MIG vGPU testing is blocked with no fallback environment.
  - **Mitigation:** None — no alternative GPU hardware or cluster is available; testing is fully dependent on this single node's availability.
  - *Sign-off:* [Name/Date]

### **III. Test Scenarios & Traceability**

<!-- This section links D/S requirements to test coverage, enabling reviewers to verify all requirements are tested. -->

- **[CNV-38740](https://redhat.atlassian.net/browse/CNV-38740)** — MIG vGPU node capacity and allocatable resources are updated after MIG configuration
  - *Test Scenario:* [Tier 2] Verify node `Capacity` and `Allocatable` sections show the MIG vGPU device after MIG mode and profiles are configured on the GPU node
  - *Priority:* P0

- **[CNV-38740](https://redhat.atlassian.net/browse/CNV-38740)** — RHEL VM with MIG vGPU device reaches Running state
  - *Test Scenario:* [Tier 2] Verify a RHEL VM requesting a MIG vGPU device can be created and transitions to `Running` state
  - *Priority:* P0

- **[CNV-38740](https://redhat.atlassian.net/browse/CNV-38740)** — MIG vGPU device is visible inside a running RHEL VM
  - *Test Scenario:* [Tier 2] Verify the NVIDIA GPU device is visible inside the RHEL VM via `lspci -nnk | grep NVIDIA`
  - *Priority:* P0

- **[CNV-38740](https://redhat.atlassian.net/browse/CNV-38740)** — Two RHEL VMs with one MIG vGPU each run concurrently on the same GPU
  - *Test Scenario:* [Tier 2] Verify two RHEL VMs each assigned one MIG vGPU slice from the same A30 GPU can run in parallel without conflict
  - *Priority:* P1

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
