# Openshift-virtualization-tests Test plan

## **Storage migration cleanup - Quality Engineering Plan**

### **Metadata & Tracking**

- **Enhancement(s):** https://github.com/kubevirt/kubevirt-migration-controller/pull/28
- **Feature Tracking:** [CNV-77497](https://redhat.atlassian.net/browse/CNV-77497)
- **Epic Tracking:** [CNV-73509](https://redhat.atlassian.net/browse/CNV-73509)
- **QE Owner(s):** Jose Manuel Castano
- **Owning SIG:** sig-storage
- **Participating SIGs:** sig-storage

**Document Conventions:**
- **VirtualMachineStorageMigrationPlan**: used to migrate the disks of a single Virtual Machine within a specific namespace
- **MultiNamespaceVirtualMachineStorageMigrationPlan**: allowed user to perform storage migrations across multiple namespaces simultaneously
- **retentionPolicy**: API field that controls whether source volumes are retained (keepSource) or deleted (deleteSource) after successful migration

### **Feature Overview**

The storage migration cleanup feature allows users to optionally decommission migration plans and legacy PVCs upon successful completion

---

### **I. Motivation and Requirements Review (QE Review Guidelines)**

This section documents the mandatory QE review process. The goal is to understand the feature's value,
technology, and testability before formal test planning.

#### **1. Requirement & User Story Review Checklist**

- [x] **Review Requirements**
  - *List the key D/S requirements reviewed:* Reviewed the relevant requirements for retentionPolicy field in storage migration plans

- [x] **Understand Value and Customer Use Cases**
  - *Describe the feature's value to customers:* Confirmed clear user stories and understood the difference between U/S and D/S requirements. The value for RH customers is automated cleanup of source storage resources after successful migration, reducing manual cleanup effort and storage costs.
  - *List the customer use cases identified:* User can optionally choose to keep (keepSource) or delete (deleteSource) source DataVolumes/PVCs after a successful VM storage migration.

- [x] **Testability**
  - *Note any requirements that are unclear or untestable:* None — all requirements are testable with standard test infrastructure

- [x] **Acceptance Criteria**
  - *List the acceptance criteria:*
    - Source volumes are retained after successful migration (default behavior)
    - Source volumes are deleted after successful migration when RetentionPolicy=deleteSource (namespace level)
    - Source volumes are deleted after successful migration when RetentionPolicy=deleteSource (spec level)
    - Source volumes are deleted/retained when setting combination of namespace level and spec level retentionPolicy
    - RetentionPolicy will not clean up the volume when migration failed
  - *Note any gaps or missing criteria:* None

- [x] **Non-Functional Requirements (NFRs)**
  - *List applicable NFRs and their targets:* Documentation: User guide updates for retentionPolicy in migration plan
  - *Note any NFRs not covered and why:* None

#### **2. Known Limitations**

The limitations are documented to ensure alignment between development, QA, and product teams.
The following topics will not be tested or supported.

None — reviewed and confirmed that no feature limitations apply for this release.

#### **3. Technology and Design Review**

- [x] **Developer Handoff/QE Kickoff**
  - *Key takeaways and concerns:* Reviewed retentionPolicy implementation with development team. Feature adds optional cleanup of source PVCs/DataVolumes after successful migration. No untestable aspects identified.

- [x] **Technology Challenges**
  - *List identified challenges:* None — standard storage migration testing approach applies
  - *Impact on testing approach:* No impact

- [x] **API Extensions**
  - *List new or modified APIs:* Introduces a retentionPolicy field allowing users to keep (keepSource) or delete (deleteSource) source volumes after successful migration.
  - *Testing impact:* Requires validation of both namespace-level and spec-level retentionPolicy settings

- [x] **Test Environment Needs**
  - *See environment requirements in Section II.3 and testing tools in Section II.3.1*

- [x] **Topology Considerations**
  - *Describe topology requirements:* None
  - *Impact on test design:* None

### **II. Software Test Plan (STP)**

This STP serves as the **overall roadmap for testing**, detailing the scope, approach, resources, and schedule.

#### **1. Scope of Testing**

**Testing Goals**

- **[P0]** Verify source volumes are deleted/retained per the retentionPolicy after successful VM storage migration (online, offline, and online+offline)
  - namespace level retentionPolicy
  - spec level retentionPolicy
  - combination of namespace level and spec level retentionPolicy

- **[P1]** Verify source volumes will be retained when retentionPolicy is not set, default behavior is keepSource

- **[P2]** Verify the source DataVolume/PVC behavior when migration fails

**Out of Scope (Testing Scope Exclusions)**

The following items are explicitly Out of Scope for this test cycle and represent intentional exclusions.
No verification activities will be performed for these items, and any related issues found will not be classified as defects for this release.

None — reviewed and confirmed that all supported product functionality will be tested this cycle.

**Test Limitations**

The following limitations constrain the test approach for this feature.

None — reviewed and confirmed that no test limitations apply for this release.

#### **2. Test Strategy**

**Functional**

- [x] **Functional Testing** — Validates that the feature works according to specified requirements and user stories
  - *Details:* Functional testing with retentionPolicy field defined in spec

- [x] **Automation Testing** — Confirms test automation plan is in place for CI and regression coverage (all tests are expected to be automated)
  - *Details:* Ensures test cases are automated, might be added to the existing storage class migration tests

- [x] **Regression Testing** — Verifies that new changes do not break existing functionality
  - *Details:* Ensure storage migration functionality will not be affected by new implemented cleanup code

**Non-Functional**

- [x] **Performance Testing** — Validates feature performance meets requirements (latency, throughput, resource usage)
  - *Details:* No performance testing currently

- [x] **Scale Testing** — Validates feature behavior under increased load and at production-like scale (e.g., large number of VMs, nodes, or concurrent operations)
  - *Details:* Not applicable

- [x] **Security Testing** — Verifies security requirements, RBAC, authentication, authorization, and vulnerability scanning
  - *Details:* Not security relevant

- [x] **Usability Testing** — Validates user experience and accessibility requirements
  - *Details:* Will be covered by UI team in https://redhat.atlassian.net/browse/CNV-77404

- [x] **Monitoring** — Does the feature require metrics and/or alerts?
  - *Details:* No Monitoring testing currently

**Integration & Compatibility**

- [x] **Compatibility Testing** — Ensures feature works across supported platforms, versions, and configurations
  - Does the feature maintain backward compatibility with previous API versions and configurations?
  - *Details:* No compatibility testing currently

- [x] **Upgrade Testing** — Validates upgrade paths from previous versions, data migration, and configuration preservation
  - *Details:* Not Upgrade relevant

- [x] **Dependencies** — Blocked by deliverables from other components/products. Identify what we need from other teams before we can test.
  - *Details:* No Dependencies

- [x] **Cross Integrations** — Does the feature affect other features or require testing by other teams? Identify the impact we cause.
  - *Details:* Will not affect other components

**Infrastructure**

- [x] **Cloud Testing** — Does the feature require multi-cloud platform testing? Consider cloud-specific features.
  - *Details:* Not multi-cloud platform testing relevant

#### **3. Test Environment**

- **Cluster Topology:** Standard 3-master/3-worker

- **OCP & OpenShift Virtualization Version(s):** OCP 4.22 with OpenShift Virtualization 4.22

- **CPU Virtualization:** Standard

- **Compute Resources:** Standard

- **Special Hardware:** N/A

- **Storage:** ODF (ocs-storagecluster-ceph-rbd) and HPP (hostpath-provisioner)

- **Network:** Default network

- **Required Operators:** migration controller

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

#### **5. Risks**

**Timeline/Schedule**

- **Risk:** N/A
  - **Mitigation:** No timeline risks identified
  - *Estimated impact on schedule:* None
  - *Sign-off:* Jose Manuel Castano/2026-04-22

**Test Coverage**

- **Risk:** N/A
  - **Mitigation:** No test coverage gaps identified
  - *Areas with reduced coverage:* None
  - *Sign-off:* Jose Manuel Castano/2026-04-22

**Test Environment**

- **Risk:** N/A
  - **Mitigation:** All required test environments are available
  - *Missing resources or infrastructure:* None
  - *Sign-off:* Jose Manuel Castano/2026-04-22

**Untestable Aspects**

- **Risk:** N/A
  - **Mitigation:** All aspects of the feature are testable
  - *Alternative validation approach:* N/A
  - *Sign-off:* Jose Manuel Castano/2026-04-22

**Resource Constraints**

- **Risk:** N/A
  - **Mitigation:** No resource constraints identified
  - *Current capacity gaps:* None
  - *Sign-off:* Jose Manuel Castano/2026-04-22

**Dependencies**

- **Risk:** N/A
  - **Mitigation:** No external dependencies identified
  - *Dependent teams or components:* None
  - *Sign-off:* Jose Manuel Castano/2026-04-22

**Other**

- **Risk:** N/A
  - **Mitigation:** No other risks identified
  - *Sign-off:* Jose Manuel Castano/2026-04-22

---

### **III. Test Scenarios & Traceability**

- **[CNV-73509]** — Spec level retentionPolicy: keepSource/deleteSource in VirtualMachineStorageMigrationPlan
  - *Test Scenario:* [Tier 2] Verify source DV/PVC will be retained/cleaned up after migration completed in VirtualMachineStorageMigrationPlan
  - *Priority:* P0

- **[CNV-73509]** — Namespace level retentionPolicy: keepSource/deleteSource in MultiNamespaceVirtualMachineStorageMigrationPlan
  - *Test Scenario:* [Tier 2] Verify source DV/PVC will be retained/cleaned up after migration completed in MultiNamespaceVirtualMachineStorageMigrationPlan
  - *Priority:* P0

- **[CNV-73509]** — Spec level retentionPolicy: keepSource/deleteSource in MultiNamespaceVirtualMachineStorageMigrationPlan
  - *Test Scenario:* [Tier 2] Verify source DV/PVC will be retained/cleaned up after migration completed in MultiNamespaceVirtualMachineStorageMigrationPlan
  - *Priority:* P0

- **[CNV-73509]** — Combination of namespace level and spec level retentionPolicy: keepSource/deleteSource in MultiNamespaceVirtualMachineStorageMigrationPlan
  - *Test Scenario:* [Tier 2] Verify source DV/PVC will be retained/cleaned up after migration completed in MultiNamespaceVirtualMachineStorageMigrationPlan
  - *Priority:* P0

- **[CNV-73509]** — retentionPolicy: None
  - *Test Scenario:* [Tier 2] Verify default behavior when retentionPolicy is not set
  - *Priority:* P1

- **[CNV-73509]** — Migration failed with retentionPolicy keepSource/deleteSource
  - *Test Scenario:* [Tier 2] Verify source DV/PVC will not be cleaned up when migration failed
  - *Priority:* P2


---

### **IV. Sign-off and Approval**

This Software Test Plan requires approval from the following stakeholders:

* **Reviewers:**
  - QE Architect (OCP-V): Ruth Netser (@rnetser)
  - QE Members (OCP-V): Jenia Peimer (jpeimer@), Kate Shvaika (kshvaika@), Jose Manuel Castano(joscasta@)
* **Approvers:**
  - QE Architect (OCP-V): Ruth Netser (@rnetser)
  - Principal Developer: Alexander Wels (awels@redhat.com)
