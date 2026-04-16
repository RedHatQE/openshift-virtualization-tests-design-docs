# Openshift-virtualization-tests Test plan

## **Offline Storage Migration - Quality Engineering Plan**

### **Metadata & Tracking**

- **Enhancement(s):** https://github.com/kubevirt/kubevirt-migration-controller/pull/32
- **Feature Tracking:** [CNV-73509](https://redhat.atlassian.net/browse/CNV-73509)
- **Epic Tracking:** [CNV-73500](https://redhat.atlassian.net/browse/CNV-73500)
- **QE Owner(s):** Jose Manuel Castano (joscasta@redhat.com)
- **Owning SIG:** sig-storage
- **Participating SIGs:** sig-storage

**Document Conventions:**
None

### **Feature Overview**

This feature extends the OpenShift Virtualization migration plan to support storage migration for offline (stopped) VMs in addition to existing online (running) VM support. It enables customers to migrate storage for VMs regardless of their running state, allowing mixed migration plans containing both offline and running VMs.

---

### **I. Motivation and Requirements Review (QE Review Guidelines)**

This section documents the mandatory QE review process. The goal is to understand the feature's value,
technology, and testability before formal test planning.

#### **1. Requirement & User Story Review Checklist**

- [x] **Review Requirements**
  - *List the key D/S requirements reviewed:* Reviewed the user cases for offline VM storage migration from CNV-82430 and CNV-73500

- [x] **Understand Value and Customer Use Cases**
  - *Describe the feature's value to customers:* Customers need to perform storage migration for offline VMs without requiring them to be running, providing flexibility in storage management operations.
  - *List the customer use cases identified:* Storage migration for mixed offline VMs and running VMs in one migration plan, allowing batch migration operations regardless of VM state.

- [x] **Testability**
  - *Note any requirements that are unclear or untestable:* Requirements are testable. Downstream build with the feature code is available for testing.

- [x] **Acceptance Criteria**
  - *List the acceptance criteria:*
    - Storage migration completes successfully for offline VMs between ODF and HPP storage classes
    - Storage migration completes successfully for mixed offline VMs and running VMs
    - Storage migration completes successfully for offline VMs with hotplug disk
    - Source volume could be retained/cleaned up for an offline VM migration completed with retentionPolicy defined
    - Offline VM points to the origin volume when migration failed
    - Migration succeeded when starting a stopped VM during migration

  - *Note any gaps or missing criteria:* N/A

- [x] **Non-Functional Requirements (NFRs)**
  - *List applicable NFRs and their targets:* Documentation updates to reflect offline VM storage migration support and UI support for offline VM migrations.
  - *Note any NFRs not covered and why:* Performance, Monitoring, Observability, Security and Scalability testing are not included in this test plan

#### **2. Known Limitations**

The limitations are documented to ensure alignment between development, QA, and product teams.
The following topics will not be tested or supported.

None - reviewed and confirmed with Yan Du on Apr 7,2026.

#### **3. Technology and Design Review**

- [x] **Developer Handoff/QE Kickoff**
  - *Key takeaways and concerns:* Extend the offline VMs storage migration support

- [x] **Technology Challenges**
  - *List identified challenges:* Offline migration uses a different mechanism than online migration, requiring separate test coverage
  - *Impact on testing approach:* Test cases must verify both offline VM migration mixed scenarios with both offline and running VMs in the same migration plan.

- [x] **API Extensions**
  - *List new or modified APIs:* No new APIs - extends existing migration plan API to handle offline VMs
  - *Testing impact:* No API test updates required; functional tests will verify new behavior

- [x] **Test Environment Needs**
  - *See environment requirements in Section II.3 and testing tools in Section II.3.1*

- [x] **Topology Considerations**
  - *Describe topology requirements:* Standard 3-master/3-worker cluster sufficient
  - *Impact on test design:* No special topology requirements

### **II. Software Test Plan (STP)**

This STP serves as the **overall roadmap for testing**, detailing the scope, approach, resources, and schedule.

#### **1. Scope of Testing**

**Testing Goals**

- **[P0]** Verify offline VM storage migration completes between ODF and HPP storage classes, and the VM boots successfully after migration
- **[P0]** Verify storage migration completes for a migration plan containing both offline and running VMs
- **[P0]** Verify source volumes are retained or deleted according to retentionPolicy configuration when offline VM storage migration completes
- **[P1]** Verify offline VM storage migration completes when the VM has hotplug disks attached
- **[P2]** Verify offline VM continues pointing to the original volume when storage migration fails
- **[P2]** Verify storage migration completes when a stopped VM is started during the migration process

**Storage Class Coverage**

The following storage class migration combinations will be tested:
- **ODF** (ocs-storagecluster-ceph-rbd-virtualization) ↔ **HPP** (hostpath-provisioner)
- **ODF ↔ ODF** — Same storage class migration
- **HPP ↔ HPP** — Same storage class migration

Storage classes **not covered** in this test plan:
- Cloud provider-specific storage classes (AWS EBS, Azure Disk, GCP PD) — Out of scope for initial release

**Out of Scope (Testing Scope Exclusions)**

The following items are explicitly Out of Scope for this test cycle and represent intentional exclusions.
No verification activities will be performed for these items, and any related issues found will not be classified as defects for this release.

None

#### **2. Test Strategy**

**Functional**

- [x] **Functional Testing** — Validates that the feature works according to specified requirements and user stories
  - *Details:* Functional testing will verify offline VM storage migration and mixed offline/online VM migration scenarios

- [x] **Automation Testing** — Confirms test automation plan is in place for CI and regression coverage (all tests are expected to be automated)
  - *Details:* All test cases will be automated

- [x] **Regression Testing** — Verifies that new changes do not break existing functionality
  - *Details:* Verify that existing online VM storage migration functionality remains unaffected by the offline VM support additions

**Non-Functional**

- [ ] **Performance Testing** — Validates feature performance meets requirements (latency, throughput, resource usage)
  - *Details:* Performance testing for bulk offline migrations is tracked separately in CNV-82430 and will be covered by a separate test plan

- [ ] **Scale Testing** — Validates feature behavior under increased load and at production-like scale (e.g., large number of VMs, nodes, or concurrent operations)
  - *Details:* Not applicable

- [ ] **Security Testing** — Verifies security requirements, RBAC, authentication, authorization, and vulnerability scanning
  - *Details:* Not applicable

- [x] **Usability Testing** — Validates user experience and accessibility requirements
  - Does the feature require a UI? If so, ensure the UI aligns with the requirements (UI/UX consistency, accessibility)
  - Does the feature expose CLI commands? If so, validate usability and that needed information is available (e.g., status conditions, clear output)
  - Does the feature trigger backend operations that should be reported to the admin? If so, validate that the user receives clear feedback about the operation and its outcome (e.g., status conditions, events, or notifications indicating success or failure)
  - *Details:* UI testing will be covered in https://redhat.atlassian.net/browse/CNV-77503

- [ ] **Monitoring** — Does the feature require metrics and/or alerts?
  - *Details:* Not applicable

**Integration & Compatibility**

- [x] **Compatibility Testing** — Ensures feature works across supported platforms, versions, and configurations
  - Does the feature maintain backward compatibility with previous API versions and configurations?
  - *Details:* Feature maintains backward compatibility with existing migration API. Existing online VM migrations continue to work unchanged.

- [ ] **Upgrade Testing** — Validates upgrade paths from previous versions, data migration, and configuration preservation
  - *Details:* Not applicable

- [ ] **Dependencies** — Blocked by deliverables from other components/products. Identify what we need from other teams before we can test.
  - *Details:* No blocking dependencies

- [x] **Cross Integrations** — Does the feature affect other features or require testing by other teams? Identify the impact we cause.
  - *Details:* UI team needs to update their migration UI to support offline VM selection

**Infrastructure**

- [ ] **Cloud Testing** — Does the feature require multi-cloud platform testing? Consider cloud-specific features.
  - *Details:* Not applicable

#### **3. Test Environment**

- **Cluster Topology:** 3-master/3-worker bare-metal

- **OCP & OpenShift Virtualization Version(s):** OCP 4.22 with OpenShift Virtualization 4.22

- **CPU Virtualization:** VT-x (Intel) or AMD-V enabled

- **Compute Resources:** Minimum per worker node: 8 vCPUs, 32GB RAM

- **Special Hardware:** N/A

- **Storage:** ocs-storagecluster-ceph-rbd-virtualization, hostpath-provisioner

- **Network:** OVN-Kubernetes, IPv4

- **Required Operators:** N/A

- **Platform:** PSI

- **Special Configurations:** N/A

#### **3.1. Testing Tools & Frameworks**

- **Test Framework:** Standard

- **CI/CD:** N/A

- **Other Tools:** N/A

#### **4. Entry Criteria**

The following conditions must be met before testing can begin:

- [x] Requirements and design documents are **approved and merged**
- [x] Test environment can be **set up and configured** (see Section II.3 - Test Environment)

#### **5. Exit Criteria**

- [ ] All high-priority defects are resolved and verified
- [ ] Test coverage goals achieved
- [ ] Test automation merged (required for GA sign-off)
- [ ] All planned test cycles completed
- [ ] Test summary report approved
- [ ] Acceptance criteria met

#### **6. Risks**

**Timeline/Schedule**

- **Risk:** N/A
  - **Mitigation:** N/A
  - *Estimated impact on schedule:* None

**Test Coverage**

- **Risk:** N/A
  - **Mitigation:** All acceptance criteria are covered by planned test scenarios
  - *Areas with reduced coverage:* None

**Test Environment**

- **Risk:** N/A
  - **Mitigation:** Standard test environment is sufficient for testing this feature
  - *Missing resources or infrastructure:* None

**Untestable Aspects**

- **Risk:** N/A
  - **Mitigation:** N/A
  - *Alternative validation approach:* N/A

**Resource Constraints**

- **Risk:** N/A
  - **Mitigation:** N/A
  - *Current capacity gaps:* None

**Dependencies**

- **Risk:** N/A
  - **Mitigation:** No external dependencies
  - *Dependent teams or components:* UI team for UI updates (non-blocking)

**Other**

- **Risk:** N/A
  - **Mitigation:** No additional risks identified

> **Risks Review Sign-off:** All risk categories reviewed and confirmed N/A or addressed above — Yan Du, Apr 7,2026

---

### **III. Test Scenarios & Traceability**

- **[CNV-73500]** — As a VM owner, I want to migrate storage for offline VMs between ODF and HPP
  - *Test Scenario:* [Tier 2] Verify storage migration completes for offline VMs between ODF and HPP, and the VM boots successfully after migration
  - *Priority:* P0

- **[CNV-73500]** — As a VM owner, I want to migrate storage with mixed VM states (online and offline)
  - *Test Scenario:* [Tier 2] Verify storage migration completes for a migration plan containing both offline and running VMs
  - *Priority:* P0

- **[CNV-73500]** — As a VM owner, I want to migrate storage for offline VMs with hotplug disk
  - *Test Scenario:* [Tier 2] Verify storage migration completes successfully for offline VM with hotplug disk
  - *Priority:* P1

- **[CNV-73500]** — As a VM owner, I want to retain or delete the source volume for an offline VM
  - *Test Scenario:* [Tier 2] Verify source volume is retained or cleaned up for an offline VM when retentionPolicy is set in the Migration Plan
  - *Priority:* P0

- **[CNV-73500]** — As a VM owner, I want an offline VM to still point to the original volume when migration fails
  - *Test Scenario:* [Tier 2] Verify an offline VM still points to the original volume when migration fails
  - *Priority:* P2

- **[CNV-73500]** — As a VM owner, I want the migration to succeed when starting a stopped VM during migration
  - *Test Scenario:* [Tier 2] Verify migration succeeds when starting a stopped VM during the migration process
  - *Priority:* P2

---

### **IV. Sign-off and Approval**

This Software Test Plan requires approval from the following stakeholders:

* **Reviewers:**
  - QE Architect (OCP-V): Ruth Netser (`@rnetser`)
  - QE Members (OCP-V): Jenia Peimer (`@jpeimer`), Kate Shvaika (`@kshvaika`), Jose Manuel Castano (`@joscasta`)
* **Approvers:**
  - QE Architect (OCP-V): Ruth Netser (`@rnetser`)
  - Principal Developer: Alexander Wels (`@awels`)
