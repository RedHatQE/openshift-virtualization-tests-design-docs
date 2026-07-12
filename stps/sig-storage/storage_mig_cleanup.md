# Openshift-virtualization-tests Test plan

## **Storage migration cleanup - Quality Engineering Plan**

### **Metadata & Tracking**

- **Enhancement(s):** [CNV-73509](https://issues.redhat.com/browse/CNV-73509)
- **Feature Tracking:** [CNV-77497](https://redhat.atlassian.net/browse/CNV-77497)
- **Epic Tracking:** [CNV-73509](https://redhat.atlassian.net/browse/CNV-73509)
- **QE Owner(s):** Jose Manuel Castano (joscasta@redhat.com)
- **Owning SIG:** sig-storage
- **Participating SIGs:** sig-storage
- **Feature Maturity:**
  - DP: N/A
  - TP: v4.22
  - GA: v5.0

**Document Conventions:**
- **Single-namespace migration**: Migration plan for moving a VM's disks within a single namespace
- **Multi-namespace migration**: Migration plan that can migrate VMs across multiple namespaces simultaneously
- **Source volume cleanup**: Policy option to either keep or delete the original storage volumes after migration completes successfully

### **Feature Overview**

The storage migration cleanup feature allows cluster administrators to automatically delete source storage volumes after successfully migrating VMs to new storage classes. Administrators can configure cleanup policies at the namespace level or per-migration plan, choosing to either retain volumes for rollback scenarios or delete them to reduce storage costs. Failed migrations always preserve source volumes to prevent data loss.

---

### **I. Motivation and Requirements Review (QE Review Guidelines)**

This section documents the mandatory QE review process. The goal is to understand the feature's value,
technology, and testability before formal test planning.

#### **1. Requirement & User Story Review Checklist**

- [x] **Review Requirements**
  - *List the key D/S requirements reviewed:*
    - Add cleanup policy option to Migration Plan API/spec to configure whether to retain or delete source DV/PVC
    - Implement DV/PVC garbage collection that removes source volumes after successful migrations based on the policy
    - Plans will always be retained (cleanup applies to DV/PVC only, not the Migration Plan object)
    - Default behavior is to retain source volumes

- [x] **Understand Value and Customer Use Cases**
  - *Describe the feature's value to customers:* Confirmed clear user stories and understood the difference between U/S and D/S requirements. The value for RH customers is automated cleanup of source storage resources after successful migration, reducing manual cleanup effort and storage costs.
  - *List the customer use cases identified:* As a cluster administrator, I want to choose whether to keep or automatically delete the original storage volumes after a successful VM migration, so that I can reduce storage costs and manual cleanup effort while maintaining flexibility for rollback scenarios.

- [x] **Testability**
  - *Note any requirements that are unclear or untestable:* None — all requirements are testable with standard test infrastructure

- [x] **Acceptance Criteria**
  - *List the acceptance criteria:*
    - Source volumes are retained after successful migration (default behavior)
    - Source volumes are automatically deleted after successful migration when cleanup policy is set to delete at the namespace level
    - Source volumes are automatically deleted after successful migration when cleanup policy is set to delete at the migration plan level
    - Source volumes are deleted or retained correctly when cleanup policies are configured at both namespace and migration plan levels
    - Source volumes are not cleaned up when migration fails, regardless of cleanup policy
  - *Note any gaps or missing criteria:* None

- [x] **Non-Functional Requirements (NFRs)**
  - *List applicable NFRs and their targets:*
    - **Documentation:** User guide updates for cleanup policy configuration in migration plans
    - **UI:** UI updates for cleanup policy selection (covered by UI team in CNV-77404)
  - *Note any NFRs not covered and why:*
    - **Monitoring:** Not applicable - feature uses existing migration monitoring, no new metrics required
    - **Observability:** Not applicable - cleanup actions are logged through standard migration events
    - **Performance:** Not applicable - cleanup is post-migration operation with no performance impact on migration itself
    - **Security:** Not applicable - feature uses existing RBAC for migration plans, no new security requirements
    - **Scalability:** Not applicable - cleanup scales with existing migration controller capabilities

#### **2. Known Limitations**

The limitations are documented to ensure alignment between development, QA, and product teams.
The following topics will not be tested or supported.

None — reviewed and confirmed with Jose Manuel Castano/2026-04-22

#### **3. Technology and Design Review**

- [x] **Developer Handoff/QE Kickoff**
  - *Key takeaways and concerns:* Reviewed cleanup policy implementation with development team. Feature adds optional cleanup of source storage volumes after successful migration. No untestable aspects identified.

- [x] **Technology Challenges**
  - *List identified challenges:* None — standard storage migration testing approach applies
  - *Impact on testing approach:* No impact

- [x] **API Extensions**
  - *List new or modified APIs:* Introduces a cleanup policy field allowing users to retain or automatically delete source volumes after successful migration.
  - *Testing impact:* Requires validation of cleanup policy settings at both namespace level and migration plan level

- [x] **Test Environment Needs**
  - *See environment requirements in Section II.3 and testing tools in Section II.3.1*

- [x] **Topology Considerations**
  - *Describe topology requirements:* None
  - *Impact on test design:* None

### **II. Software Test Plan (STP)**

This STP serves as the **overall roadmap for testing**, detailing the scope, approach, resources, and schedule.

#### **1. Scope of Testing**

**Testing Goals**

- **[P0]** Source volumes are deleted or retained according to the cleanup policy after successful VM storage migration (online, offline, and online+offline)
  - namespace-level cleanup policy
  - migration plan-level cleanup policy
  - combination of namespace-level and migration plan-level cleanup policies

- **[P1]** Source volumes are retained by default when no cleanup policy is configured

- **[P2]** Source volumes remain available when migration fails

**Out of Scope (Testing Scope Exclusions)**

The following items are explicitly Out of Scope for this test cycle and represent intentional exclusions.
No verification activities will be performed for these items, and any related issues found will not be classified as defects for this release.

- **None** — all supported product functionality will be tested this cycle.
  - *Rationale:* Feature scope is well-defined with clear boundaries; all user-facing functionality is testable
  - *PM/Lead Agreement:* Peter Lauterbach/2026-05-20

**Test Limitations**

The following limitations constrain the test approach for this feature.

- **None** — no test limitations apply for this release
  - *Sign-off:* Jose Manuel Castano/2026-04-22

#### **2. Test Strategy**

**Functional**

- [x] **Functional Testing** — Validates that the feature works according to specified requirements and user stories
  - *Details:* Functional testing with cleanup policy configured in migration plan

- [x] **Automation Testing** — Confirms test automation plan is in place for CI and regression coverage (all tests are expected to be automated)
  - *Details:* Ensures test cases are automated, might be added to the existing storage class migration tests

- [x] **Regression Testing** — Verifies that new changes do not break existing functionality
  - *Details:* Ensure storage migration functionality will not be affected by new implemented cleanup code

**Non-Functional**

- [ ] **Performance Testing** — Validates feature performance meets requirements (latency, throughput, resource usage)
  - *Details:* Not applicable — cleanup is a post-migration operation with no performance impact on migration itself; existing migration performance testing covers the critical path

- [ ] **Scale Testing** — Validates feature behavior under increased load and at production-like scale (e.g., large number of VMs, nodes, or concurrent operations)
  - *Details:* Not applicable — cleanup scales with existing migration controller capabilities; no new scale requirements introduced

- [ ] **Security Testing** — Verifies security requirements, RBAC, authentication, authorization, and vulnerability scanning
  - *Details:* Not applicable — feature uses existing RBAC for migration plans; no new security requirements or attack surface introduced

- [ ] **Usability Testing** — Validates user experience and accessibility requirements
  - *Details:* Not applicable to QE - usability testing is owned by UI team in https://redhat.atlassian.net/browse/CNV-77404

- [ ] **Monitoring** — Does the feature require metrics and/or alerts?
  - *Details:* Not applicable — cleanup actions are logged through existing migration events; no new metrics or alerts required

**Integration & Compatibility**

- [ ] **Compatibility Testing** — Ensures feature works across supported platforms, versions, and configurations
  - Does the feature maintain backward compatibility with previous API versions and configurations?
  - *Details:* Not applicable — feature is additive with optional cleanup policy; existing migrations continue to work with default behavior (retain source volumes); backward compatibility is inherent in the design

- [x] **Upgrade Testing** — Validates upgrade paths from previous versions, data migration, and configuration preservation
  - *Details:* Upgrade path evaluated - not applicable. Feature is additive with optional cleanup policy; existing migrations continue to work with default behavior (retain source volumes)

- [x] **Dependencies** — Blocked by deliverables from other components/products. Identify what we need from other teams before we can test.
  - *Details:* No Dependencies

- [x] **Cross Integrations** — Does the feature affect other features or require testing by other teams? Identify the impact we cause.
  - *Details:* Will not affect other components

**Infrastructure**

- [ ] **Cloud Testing** — Does the feature require multi-cloud platform testing? Consider cloud-specific features.
  - *Details:* Not multi-cloud platform testing relevant

#### **3. Test Environment**

- **Cluster Topology:** Standard 3-master/3-worker

- **OCP & OpenShift Virtualization Version(s):** OCP 4.22 with OpenShift Virtualization 4.22

- **CPU Virtualization:** Standard

- **Compute Resources:** Standard

- **Special Hardware:** N/A

- **Storage:** ODF (ocs-storagecluster-ceph-rbd-virtualization) and HPP (hostpath-csi-basic)

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

- **Risk:** No scheduling or deadline risks identified
  - **Mitigation:** Standard test timeline is sufficient for planned test scenarios
  - *Estimated impact on schedule:* None
  - *Sign-off:* Jose Manuel Castano, Apr 22, 2026

**Test Coverage**

- **Risk:** No gaps in test coverage identified
  - **Mitigation:** All acceptance criteria are covered by planned test scenarios
  - *Areas with reduced coverage:* None
  - *Sign-off:* Jose Manuel Castano, Apr 22, 2026

**Test Environment**

- **Risk:** No hardware, software, or infrastructure constraints identified
  - **Mitigation:** Standard test environment is sufficient for testing this feature
  - *Missing resources or infrastructure:* None
  - *Sign-off:* Jose Manuel Castano, Apr 22, 2026

**Untestable Aspects**

- **Risk:** No untestable scenarios identified
  - **Mitigation:** All scenarios can be reproduced in test environment
  - *Alternative validation approach:* N/A
  - *Sign-off:* Jose Manuel Castano, Apr 22, 2026

**Resource Constraints**

- **Risk:** No staffing, skill, or capacity limitations identified
  - **Mitigation:** Current QE team capacity is sufficient for planned test execution
  - *Current capacity gaps:* None
  - *Sign-off:* Jose Manuel Castano, Apr 22, 2026

**Dependencies**

- **Risk:** No blocking external dependencies identified
  - **Mitigation:** UI team updates (CNV-77404) are non-blocking; API testing can proceed independently
  - *Dependent teams or components:* UI team for UI updates (non-blocking)
  - *Sign-off:* Jose Manuel Castano, Apr 22, 2026

**Other**

- **Risk:** No additional risks identified
  - **Mitigation:** No additional mitigation required
  - *Sign-off:* Jose Manuel Castano, Apr 22, 2026

---

### **III. Test Scenarios & Traceability**

- **[CNV-73509]** — As a cluster administrator, I want to configure source volume cleanup policy at the plan level and namespace level, so that I can control cleanup behavior with namespace-level policy overriding plan-level policy
  - *Test Scenario:* [Tier 2] Verify source volumes are retained/cleaned up correctly per plan-level and namespace-level cleanup policies, with namespace-level overriding plan-level when both are configured
  - *Priority:* P0

- **[CNV-73509]** — As a cluster administrator, I want the system to use default cleanup behavior when no policy is specified, so that existing migrations continue to work without configuration changes
  - *Test Scenario:* [Tier 2] Verify source volumes are retained by default when no cleanup policy is configured
  - *Priority:* P1

- **[CNV-73509]** — As a cluster administrator, I want source volumes to be preserved when migration fails, so that I don't lose data even if cleanup was configured
  - *Test Scenario:* [Tier 2] Verify source volumes are not cleaned up when migration fails, regardless of cleanup policy configuration
  - *Priority:* P2


---

### **IV. Sign-off and Approval**

This Software Test Plan requires approval from the following stakeholders:

* **Reviewers:**
  - QE Architect (OCP-V): Ruth Netser (@rnetser)
  - QE Members (OCP-V): Jenia Peimer (@jpeimer), Kate Shvaika (@kshvaika), Jose Manuel Castano (@joscasta)
* **Approvers:**
  - QE Lead: Ruth Netser (@rnetser)
  - Dev Lead: Alexander Wels (@awels)
  - PM: Peter Lauterbach (@pelauter)
