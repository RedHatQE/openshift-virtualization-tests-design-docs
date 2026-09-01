# OpenShift-virtualization-tests Test plan

## **[Dual-Stream RHCOS 9.x + RHCOS 10.x — IUO Scope] - Quality Engineering Plan**

### **Metadata & Tracking**

- **Feature Tracking:** [VIRTSTRAT-83](https://redhat.atlassian.net/browse/VIRTSTRAT-83)
- **Epic Tracking:** [CNV-85268](https://redhat.atlassian.net/browse/CNV-85268)
- **IUO Story:** [CNV-85504](https://redhat.atlassian.net/browse/CNV-85504)
- **Parent STP:** [stp.md](stp.md)
- **QE Owner(s):** Ohad Revah (@OhadRevah)
- **SIG:** sig-iuo (Install, Upgrade, Operators)

### **Feature Overview**

This STP covers the IUO-specific aspects of dual-stream RHCOS support: validating that
OpenShift Virtualization deploys and functions correctly on RHCOS 10.x, diagnostic data collection works on RHCOS 10.x nodes,
node placement policies are honored in mixed-version clusters, observability metrics work
as expected, and migration metrics are accurately reported during cross-version live migration.

This STP covers testing for OCP 5.0. Automation is required for migration metrics validation on dual-stream clusters.

---

### **I. Motivation and Requirements Review (QE Review Guidelines)**

#### **1. Requirement & User Story Review Checklist**

- [x] **Review Requirements**
  - *SIG-specific requirements:*
    - OpenShift Virtualization components deploy and report ready on RHCOS 10.x worker nodes
    - Must-gather collects complete and valid data from RHCOS 10.x nodes, with no gaps compared to RHCOS 9.x
    - OpenShift Virtualization migration metrics (duration, data processed, bandwidth) are reported and populated during cross-version live migration
    - Node placement policies are respected when scheduling and migrating VMs on dual-stream clusters

- [x] **Acceptance Criteria**
  - OpenShift Virtualization components deploy and report ready on RHCOS 10.x worker nodes
  - Must-gather collects complete and valid data from RHCOS 10.x and dual-stream cluster nodes
  - Migration metrics (duration, data processed, bandwidth) are reported and populated during cross-version live migration on dual-stream clusters
  - Node placement policies are respected when scheduling and migrating VMs on dual-stream clusters

- [x] **Testability**
  - *Note any SIG-specific requirements that are unclear or untestable:* All requirements are testable
    through existing IUO test suites and new migration metrics automation on RHCOS 10.x and dual-stream clusters.

- [x] **Non-Functional Requirements (NFRs)**
  - *SIG-specific NFRs:*
    - Monitoring: OpenShift Virtualization metrics (including migration metrics) must report correctly on RHCOS 10.x nodes
  - *NFRs not covered and why:*
    - Performance: N/A — no new IUO-specific performance requirements; covered by parent STP
    - Security: N/A — no new auth or RBAC changes; FIPS requirement covered by parent STP
    - Scalability: N/A — no new scale requirements for IUO components; existing cluster-level live migration parallelism limits apply (see parent STP)
    - UI: N/A — dual-stream RHCOS support introduces no new user journeys or UI elements for IUO; existing console functionality is unchanged
    - Documentation: N/A — no IUO-specific documentation changes; release notes covered by parent STP

#### **2. Known Limitations**

None — reviewed and confirmed that no IUO-specific feature limitations apply for this release.

#### **3. Technology and Design Review**

- [x] **Developer Handoff/QE Kickoff**
  - *Key takeaways and concerns:* OpenShift Virtualization operators run the same el9.x userland on both RHCOS 9.x and
    RHCOS 10.x kernels. No operator code changes are expected, but kernel differences could surface
    unexpected behavior in must-gather log collection or metrics.

- [x] **Technology Challenges**
  - *List identified challenges:*
    - Must-gather may encounter differences in log paths or system service names between RHCOS 9.x
      and RHCOS 10.x nodes, potentially causing incomplete data collection.
  - *Impact on testing approach:* Must-gather output must be compared between RHCOS 9.x and
    RHCOS 10.x to identify any gaps.

- [x] **API Extensions**
  - *List new or modified user-facing APIs:* N/A — see parent STP
  - *Testing impact:* N/A

- [x] **Test Environment Needs**
  - *See environment requirements in Section II.3 and testing tools in Section II.3.1*

- [x] **Topology Considerations**
  - *Describe topology requirements:* Same as parent STP. Dual-stream cluster required for
    migration and node placement scenarios; RHCOS 10.x-only cluster required for IUO regression.
  - *Impact on test design:* Node placement tests require labeling nodes by RHCOS version
    and using node affinity to control VM scheduling and migration targets.

### **II. Software Test Plan (STP)**

#### **1. Scope of Testing**

**Testing Goals**

- **[P0]** OpenShift Virtualization components deploy, report ready, and function correctly on RHCOS 10.x-only and dual-stream clusters.
- **[P1]** Verify migration metrics (duration, data processed, bandwidth) are reported and populated during cross-version live migration on dual-stream clusters (RHCOS 9.x ↔ RHCOS 10.x).
- **[P1]** Verify node placement policies are respected when scheduling and migrating VMs on dual-stream clusters.

**Out of Scope (Testing Scope Exclusions)**

- **Upgrade testing**
  - *Rationale:* Relevant only from 5.1.0.
  - *PM/Lead Agreement:* Martin Tessun / 2026-05-13

**Test Limitations**

- None — dual-stream cluster provisioning tooling is available and operational.

#### **2. Test Strategy**

**Functional**

- [x] **Functional Testing** — Validates IUO-specific features on RHCOS 10.x and dual-stream clusters
  - *Details:* Run existing IUO Tier 1 and Tier 2 suites on RHCOS 10.x-only and dual-stream clusters.

- [x] **Automation Testing** — Migration metrics validation on dual-stream clusters
  - *Details:* Existing IUO Tier 1/2 suites run as-is on RHCOS 10.x cluster. New automation planned
    for migration metrics validation during cross-version live migration (RHCOS 9.x ↔ RHCOS 10.x).

- [x] **Regression Testing** — IUO regression on RHCOS 10.x and dual-stream clusters
  - *Details:* Existing IUO Tier 1 and Tier 2 regression suites run on RHCOS 10.x-only and dual-stream clusters.
    Failures triaged and bugs filed with RHCOS-version attribution.

- [ ] **Self-Validation Testing**
  - *Details:* N/A — migration metrics tests are Tier 2 scenarios requiring dual-stream clusters;
    not suitable for the self-validation health check package.

**Non-Functional**

- [ ] **Performance Testing**
  - *Details:* Covered by parent STP.

- [ ] **Scale Testing**
  - *Details:* Covered by parent STP.

- [ ] **Security Testing**
  - *Details:* Covered by parent STP. FIPS requirement applies to all testing.

- [ ] **Usability Testing**
  - *Details:* N/A — dual-stream RHCOS support introduces no new user journeys or UI elements for IUO; existing console functionality is unchanged.

- [x] **Monitoring** — Verify migration metrics on dual-stream clusters
  - *Details:* Verify migration metrics (duration, data processed, bandwidth) have values
    during cross-version live migration on dual-stream clusters (RHCOS 9.x ↔ RHCOS 10.x).

**Integration & Compatibility**

- [ ] **Compatibility Testing**
  - *Details:* Not applicable for this STP.

- [ ] **Upgrade Testing**
  - *Details:* Relevant only from 5.1.0.

- [x] **Dependencies** — Dual-stream cluster provisioning
  - *Details:* Dual-stream cluster provisioning tooling is available via QE DevOps. Dedicated CI lanes
    are operational for both RHCOS 10.x-only and dual-stream clusters.

- [ ] **Cross Integrations**
  - *Details:* Covered by parent STP.

**Infrastructure**

- [ ] **Cloud Testing**
  - *Details:* Covered by parent STP.

#### **3. Test Environment**

Covered by the parent STP. IUO-specific requirements:

- **Cluster Topology:**
  - RHCOS 10.x-only cluster: for IUO Tier 1/2 regression
  - Dual-stream cluster (RHCOS 9.x + RHCOS 10.x workers): for migration metrics,
    node placement, and must-gather dual-node scenarios

- **OCP & OpenShift Virtualization Version(s):** OCP 5.0 with CNV 5.0

- **Storage:** ocs-storagecluster-ceph-rbd-virtualization

- **Platform:** Bare metal

- **Special Configurations:** None — RHCOS 9.x worker nodes are identified by the `worker-rhcos9`
  node role label, applied automatically during cluster provisioning.

#### **3.1. Testing Tools & Frameworks**

- **Test Framework:** Standard. Tests require logic to identify nodes by RHCOS version
  for node placement and migration validation.

- **CI/CD:** Dedicated CI lanes for RHCOS 10.x and dual-stream clusters:
  - RHCOS 10.x: IUO testing and observability lanes
  - Dual-stream: IUO testing and observability lanes

- **Other Tools:** N/A

#### **4. Entry Criteria**

Covered by the parent STP. IUO-specific entry criteria:

- [x] Requirements and design documents are **approved and merged**
- [x] RHCOS 10.x-only cluster available with IUO CI lanes provisioned
- [x] Dual-stream cluster available via QE DevOps tooling (required for migration/node-placement scenarios)

#### **5. Risks**

**Test Coverage**

- **Risk:** Must-gather may encounter differences in log paths or system service names between
  RHCOS 9.x and RHCOS 10.x nodes, potentially causing incomplete diagnostic data collection.
  - **Mitigation:** Must-gather output is compared between RHCOS 9.x and RHCOS 10.x during testing
    to identify and address any gaps before GA.

Feature-wide risks are covered by the parent STP.

---

### **III. Test Scenarios & Traceability**

IUO coverage for dual-stream RHCOS is primarily provided through regression testing
(existing Tier 1/2 suites on RHCOS 10.x and dual-stream clusters). Node placement
and must-gather validation are covered by existing regression suites — no new scenarios
required. The following new test scenarios are required for migration metrics validation
on dual-stream clusters:

- **[CNV-85504]** — As a VM operator, I want migration metrics to be reported and populated when migrating from an RHCOS 9.x node to an RHCOS 10.x node.
  - *Test Scenario:* [Tier 2] Live migrate a VM from an RHCOS 9.x node to an RHCOS 10.x node and verify that migration metrics (duration, data processed, bandwidth) have values (non-zero/non-empty).
  - *Priority:* P1

- **[CNV-85504]** — As a VM operator, I want migration metrics to be reported and populated when migrating from an RHCOS 10.x node to an RHCOS 9.x node.
  - *Test Scenario:* [Tier 2] Live migrate a VM from an RHCOS 10.x node to an RHCOS 9.x node and verify that migration metrics (duration, data processed, bandwidth) have values (non-zero/non-empty).
  - *Priority:* P1

---

### **IV. Sign-off and Approval**

This Software Test Plan requires approval from the following stakeholders:

* **Reviewers:**
  - QE Architect: Ruth Netser (@rnetser)
  - sig-iuo representatives: Oren Cohen (@orenc1), Harel Meir (@hmeir), Roberto Lobillo (@rlobillo)
  - sig-virt representative: Akriti Gupta (@akri3i) (parent STP owner)
* **Approvers:**
  - QE Architect: Ruth Netser (@rnetser)
  - sig-iuo Lead: Harel Meir (@hmeir)
  - Principal Developer: Luboslav Pivarc (@xpivarc)
  - Product Manager: Martin Tessun (@mtessun)
