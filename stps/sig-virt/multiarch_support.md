# Openshift-virtualization-tests Test plan

## VM Creation and Live Migration on a Multi-Arch Cluster - Quality Engineering Plan

### **Metadata & Tracking**

- **Enhancement(s):** [dic-on-heterogeneous-cluster](https://github.com/kubevirt/enhancements/blob/main/veps/sig-storage/dic-on-heterogeneous-cluster/dic-on-heterogeneous-cluster.md)
- **Feature Tracking:** [VIRTSTRAT-494](https://issues.redhat.com/browse/VIRTSTRAT-494)
- **Epic Tracking:** [CNV-26818](https://issues.redhat.com/browse/CNV-26818)
- **QE Owner(s):** Akriti Gupta
- **Owning SIG:** sig-virt
- **Participating SIGs:** sig-infra, sig-storage, sig-iuo

**Document Conventions:**

| Term                       | Definition                                                                                            |
| :------------------------- | :---------------------------------------------------------------------------------------------------- |
| **VM**                     | Virtual Machine                                                                                       |
| **VMI**                    | VirtualMachineInstance                                                                                 |
| **Live Migration**         | Moving a running VM from one node to another without downtime                                         |
| **Heterogeneous cluster**  | Cluster with worker nodes of different CPU architectures (amd64 and arm64)                            |
| **Golden Image**           | Pre-configured bootable OS volume used as template for VM creation                                    |
| **FG**                     | Feature Gate (`enableMultiArchBootImageImport` in HCO CR)                                             |

### **Feature Overview**

This feature enables arm64 VM support in mixed-architecture (amd64/arm64) OpenShift Virtualization clusters. VMs must be scheduled only on nodes matching their CPU architecture, and live migration is restricted to same-architecture nodes. This child STP covers the sig-virt responsibilities assigned by the [parent STP](stps/sig-iuo/multiarch_arm_support.md): VM scheduling, live migration, upgrade validation, and regression testing on heterogeneous clusters.

---

### **I. Motivation and Requirements Review (QE Review Guidelines)**

> **Note:** This is a child STP. The full feature-wide requirements review, user stories, and technology/design review
> are documented in the [parent STP](stps/sig-iuo/multiarch_arm_support.md) ([PR #12](https://github.com/RedHatQE/openshift-virtualization-tests-design-docs/pull/12)).
> This section covers the sig-virt perspective only: VM scheduling and live migration on multi-arch clusters.

#### **1. Requirement & User Story Review Checklist**

- [x] **Review Requirements**
  - *List the key D/S requirements reviewed:* VMs must be scheduled only on nodes matching their CPU architecture; live migration restricted to same-arch nodes.

- [x] **Understand Value and Customer Use Cases**
  - *Describe the feature's value to customers:* Ensures workload uptime and hardware flexibility by enabling seamless VM creation and architecture-safe live migration across amd64 and arm64 nodes within a single managed cluster.
  - *List the customer use cases identified:* Admins consolidate heterogeneous workloads on a single cluster; developers test across amd64 and arm64 without separate infrastructure.

- [x] **Testability**
  - *Note any requirements that are unclear or untestable:* None

- [x] **Acceptance Criteria**
  - *List the acceptance criteria:* VMs are scheduled and migrated successfully on correct architecture nodes.
  - *Note any gaps or missing criteria:* None

- [x] **Non-Functional Requirements (NFRs)**
  - *List applicable NFRs and their targets:* **Regression**: Run T1+T2 tests on multiarch clusters. **Upgrade**: VMs survive upgrade with correct architecture placement preserved.
  - *Note any NFRs not covered and why:* None

#### **2. Known Limitations**

- Container Disk VM testing is limited: no defaulting of the architecture based on the containerdisk arch, so VMs won't schedule on expected architecture nodes unless manually providing `spec.template.spec.architecture` in the VM.
- Cross-architecture live migration is not supported (e.g., amd64 to arm64).

#### **3. Technology and Design Review**

- [x] **Developer Handoff/QE Kickoff**
  - *Key takeaways and concerns:* Attended cross-SIG kickoff. See [parent STP](stps/sig-iuo/multiarch_arm_support.md) for full design walkthrough details. Covered in parent STP and in team discussions.

- [x] **Technology Challenges**
  - *List identified challenges:* MultiArch cluster available only for 12 hours; need 2 arm64 + 2 amd64 worker nodes for live migration testing.
  - *Impact on testing approach:* Limited cluster availability requires efficient test execution.

- [x] **API Extensions**
  - *List new or modified APIs:* `spec.template.spec.architecture` field used to target specific architecture.
  - *Testing impact:* See [parent STP](stps/sig-iuo/multiarch_arm_support.md) for full API extensions across all SIGs.

- [x] **Test Environment Needs**
  - *See environment requirements in Section II.3 and testing tools in Section II.3.1*

- [x] **Topology Considerations**
  - *Describe topology requirements:* Heterogeneous cluster: 3 amd64 control-plane, 2 amd64 workers, 2 arm64 workers.
  - *Impact on test design:* At least 2 worker nodes per architecture required to test live migration.

### **II. Software Test Plan (STP)**

This child STP details the sig-virt scope, approach, and schedule for multiarch testing.
See the [parent STP](stps/sig-iuo/multiarch_arm_support.md) for the overall feature roadmap.

#### **1. Scope of Testing**

This child STP covers sig-virt's responsibilities within the [parent multiarch STP](stps/sig-iuo/multiarch_arm_support.md):
VM scheduling, live migration, upgrade, and regression testing on multi-arch clusters.

**Testing Goals**

*Functional Goals:*

- **[P0]** Verify VMs scheduled only on nodes matching their CPU architecture ([CNV-26818](https://issues.redhat.com/browse/CNV-26818)).
- **[P0]** Verify VM migration between same-architecture nodes works correctly.
- **[P0]** Verify VM creation using golden image DataSources on correct architecture nodes.
- **[P0]** Verify VM creation using custom Qcow2 images on correct architecture nodes.

*Upgrade Goals:*

- **[P0]** Verify arm64 and amd64 VMs are migrated to same-architecture nodes during upgrades and correct placement is preserved.

*Regression Goals:*

- **[P0]** Run Tier 1 and Tier 2 test suites on multiarch clusters with both CPU architectures.

**Out of Scope (Testing Scope Exclusions)**

- [ ] **Testing with container disk VM**
  - *Rationale:* No defaulting of the architecture based on the containerdisk arch
  - *PM/Lead Agreement:* [ ] Name/Date

- [ ] **Cross-arch live migration**
  - *Rationale:* Live migration between different architectures (e.g., amd64 to arm64) is not supported
  - *PM/Lead Agreement:* [ ] Name/Date

#### **2. Test Strategy**

**Functional**

- [x] **Functional Testing** — Validates that VMs schedule and live migrate on correct architecture nodes
  - *Details:* Verify scheduling and migration behavior across amd64 and arm64 nodes.

- [x] **Automation Testing** — Confirms test automation plan is in place for CI and regression coverage
  - *Details:* All test cases automated in `openshift-virtualization-tests` repo.

- [x] **Regression Testing** — Verifies that new changes do not break existing functionality
  - *Details:* Run T1 and T2 on multiarch clusters per regression goals.

**Non-Functional**

- [ ] **Performance Testing** — Validates feature performance meets requirements (latency, throughput, resource usage)
  - *Details:* N/A — Not scale-related.

- [ ] **Security Testing** — Verifies security requirements, RBAC, authentication, authorization, and vulnerability scanning
  - *Details:* N/A — Not security-related.

- [ ] **Usability Testing** — Validates user experience and accessibility requirements
  - *Details:* N/A — Out of scope for this test plan.

- [ ] **Monitoring** — Does the feature require metrics and/or alerts?
  - *Details:* N/A — Out of scope for this test plan.

**Integration & Compatibility**

- [ ] **Compatibility Testing** — Ensures feature works across supported platforms, versions, and configurations
  - *Details:* N/A — Out of scope for this test plan.

- [x] **Upgrade Testing** — Validates upgrade paths from previous versions, data migration, and configuration preservation
  - *Details:* Verify VMs migrate to same-arch nodes during upgrade and placement is preserved.

- [x] **Dependencies** — Blocked by deliverables from other components/products
  - *Details:* Multi-arch cluster support in openshift-virtualization-tests [PR #3755](https://github.com/RedHatQE/openshift-virtualization-tests/pull/3755).

- [x] **Cross Integrations** — Does the feature affect other features or require testing by other teams?
  - *Details:* Coordinated via [parent STP](stps/sig-iuo/multiarch_arm_support.md): sig-iuo (HCO/golden images), sig-storage (CDI imports), sig-infra (templates), sig-network (network tests).

**Infrastructure**

- [x] **Cloud Testing** — Does the feature require multi-cloud platform testing?
  - *Details:* AWS cluster required for arm64 worker nodes.

#### **3. Test Environment**

- **Cluster Topology:** MultiArch cluster — 3 control-plane and 4 worker nodes

- **OCP & OpenShift Virtualization Version(s):** OCP 4.22, CNV-4.22

- **CPU Virtualization:** Multi-arch cluster — 3 amd64 control-plane, 2 amd64 workers, and 2 arm64 workers

- **Compute Resources:** N/A — No special compute requirements

- **Special Hardware:** N/A

- **Storage:** io2-csi storage class (AWS EBS io2 CSI driver)

- **Network:** OVN-Kubernetes (default) — No special network requirements

- **Required Operators:** N/A

- **Platform:** AWS — arm64 workers available on AWS

- **Special Configurations:** N/A

#### **3.1. Testing Tools & Frameworks**

- **Test Framework:** pytest, openshift-virtualization-tests framework

- **CI/CD:** `test-pytest-cnv-4.22-virt-multiarch`

- **Other Tools:** oc CLI, virtctl

#### **4. Entry Criteria**

The following conditions must be met before testing can begin:

- [ ] Requirements and design documents are **approved and merged**
- [ ] Test environment can be **set up and configured** (see Section II.3 - Test Environment)
- [ ] Multi-CPU architecture support enabled in openshift-virtualization-tests repo ([CNV-74481](https://issues.redhat.com/browse/CNV-74481))

#### **5. Risks**

**Timeline/Schedule**

- [ ] **Risk:** Feature delivery timeline constrained by code freeze and limited multi-arch cluster availability
  - **Mitigation:** Prioritize P0 scenarios, automate in parallel

**Test Coverage**

- N/A

**Test Environment**

- N/A

**Resource Constraints**

- [ ] **Risk:** MultiArch cluster available only for 12 hours; limited number of AWS clusters available
  - **Mitigation:** Coordinated via [parent STP](stps/sig-iuo/multiarch_arm_support.md).

**Dependencies**

- [ ] **Risk:** Depends on multi-arch cluster support being enabled in openshift-virtualization-tests
  - **Mitigation:** Coordinate via [parent STP](stps/sig-iuo/multiarch_arm_support.md) and review PR when ready.

---

### **III. Test Scenarios & Traceability (sig-virt)**

This section links requirements to test coverage, enabling reviewers to verify all requirements are
tested. Only sig-virt test cases are listed here; other participating SIGs track their scenarios in the
[parent STP](stps/sig-iuo/multiarch_arm_support.md) and their own child STPs.

- **[CNV-26818](https://issues.redhat.com/browse/CNV-26818)** — VMs scheduled on matching CPU architecture nodes
  - *Test Scenario:* [Tier 2] Verify amd64 VMs schedule on amd64 nodes and arm64 VMs schedule on arm64 nodes
  - *Priority:* P0

- **[CNV-26818](https://issues.redhat.com/browse/CNV-26818)** — VM live migration between same-architecture nodes
  - *Test Scenario:* [Tier 2] Verify live migration succeeds between same-arch nodes (amd64-to-amd64, arm64-to-arm64)
  - *Priority:* P0

- **[CNV-26818](https://issues.redhat.com/browse/CNV-26818)** — VM creation with golden image DataSources on correct arch
  - *Test Scenario:* [Tier 2] Verify VMs created from arch-specific golden image DataSources run on matching architecture nodes
  - *Priority:* P0

- **[CNV-26818](https://issues.redhat.com/browse/CNV-26818)** — VM creation with custom Qcow2 images on correct arch
  - *Test Scenario:* [Tier 2] Verify VMs created from custom Qcow2 images schedule on correct architecture nodes
  - *Priority:* P0

- **[CNV-26818](https://issues.redhat.com/browse/CNV-26818)** — VMs migrate to same-arch nodes during upgrade
  - *Test Scenario:* [Tier 2] Verify arm64 and amd64 VMs are migrated to same-architecture nodes during upgrades and placement preserved
  - *Priority:* P0

- **[CNV-75737](https://issues.redhat.com/browse/CNV-75737)** — Regression: Run T1+T2 on multiarch clusters
  - *Test Scenario:* [Tier 2] Run Tier 1 and Tier 2 test suites on multiarch clusters with both CPU architectures
  - *Priority:* P0

- **[CNV-33896](https://issues.redhat.com/browse/CNV-33896)** — Conformance tests on multiarch cluster
  - *Test Scenario:* [Tier 1] Run conformance tests on multi-arch cluster (arm64 and amd64)
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
