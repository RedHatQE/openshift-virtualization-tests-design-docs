# Openshift-virtualization-tests Test plan

## **[Dual-Stream RHCOS 9.8 + RHCOS 10.2 — IUO Scope] - Quality Engineering Plan**

### **Metadata & Tracking**

- **Feature Tracking:** [VIRTSTRAT-83](https://redhat.atlassian.net/browse/VIRTSTRAT-83)
- **Epic Tracking:** [CNV-85268](https://redhat.atlassian.net/browse/CNV-85268)
- **IUO Story:** [CNV-85504](https://redhat.atlassian.net/browse/CNV-85504)
- **Parent STP:** [stp.md](stp.md)
- **QE Owner(s):** Ohad Revah (@OhadRevah)
- **SIG:** sig-iuo (Install, Upgrade, Operators)

**Document Conventions (if applicable):**

- **RHCOS9.8:** Red Hat CoreOS 9.8 worker nodes (GA, default for OCP 4.22).
- **RHCOS10.2:** Red Hat CoreOS 10.2 worker nodes (GA in OCP 5.0).
- **Dual-stream cluster:** An OCP cluster running both RHCOS9.8 and RHCOS10.2 worker nodes simultaneously.

### **Feature Overview**

This STP covers the IUO-specific aspects of dual-stream RHCOS support: validating that
OpenShift Virtualization deploys and functions correctly on RHCOS 10.2, diagnostic data collection works on RHCOS 10.2 nodes,
node placement policies are honored in mixed-version clusters, observability metrics work
as expected, and migration metrics are accurately reported during cross-version live migration.

This STP covers testing for OCP 5.0. Automation is required for migration metrics validation on dual-stream clusters.

---

### **I. Motivation and Requirements Review (QE Review Guidelines)**

#### **1. Requirement & User Story Review Checklist**

- [x] **Review Requirements**
  - *SIG-specific requirements:*
    - OpenShift Virtualization components deploy and report ready on RHCOS 10.2 worker nodes
    - Must-gather collects complete and valid data from RHCOS 10.2 nodes, with no gaps compared to RHCOS 9.8
    - OpenShift Virtualization migration metrics (duration, data processed, bandwidth) are reported accurately during cross-version live migration
    - Node placement policies are respected when scheduling and migrating VMs on dual-stream clusters

- [x] **Acceptance Criteria**
  - All IUO Tier 1 and Tier 2 tests pass on RHCOS 10.2-only and dual-stream clusters

- [x] **Testability**
  - *Note any SIG-specific requirements that are unclear or untestable:* All requirements are testable
    through existing IUO test suites on RHCOS 10.2 and dual-stream clusters.

- [x] **Non-Functional Requirements (NFRs)**
  - *SIG-specific NFRs:*
    - Monitoring: CNV metrics (including migration metrics) must report correctly on RHCOS 10.2 nodes
  - *NFRs not covered and why:*
    - Performance: N/A — no new IUO-specific performance requirements; covered by parent STP
    - Security: N/A — no new auth or RBAC changes; FIPS requirement covered by parent STP
    - Scalability: N/A — no new scale requirements for IUO components
    - UI: N/A — dual-stream RHCOS support introduces no new user journeys or UI elements for IUO; existing console functionality is unchanged
    - Documentation: N/A — no IUO-specific documentation changes; release notes covered by parent STP

#### **2. Known Limitations**

None — reviewed and confirmed that no IUO-specific feature limitations apply for this release.

#### **3. Technology and Design Review**

- [x] **Developer Handoff/QE Kickoff**
  - *Key takeaways and concerns:* CNV operators run the same el9.8 userland on both RHCOS 9.8 and
    RHCOS 10.2 kernels. No operator code changes are expected, but kernel differences could surface
    unexpected behavior in must-gather log collection or metrics.

- [x] **Technology Challenges**
  - *List identified challenges:*
    - Must-gather may encounter differences in log paths or system service names between RHCOS 9.8
      and RHCOS 10.2 nodes, potentially causing incomplete data collection.
  - *Impact on testing approach:* Must-gather output must be compared between RHCOS 9.8 and
    RHCOS 10.2 to identify any gaps.

- [x] **API Extensions**
  - *List new or modified user-facing APIs:* N/A — see parent STP
  - *Testing impact:* N/A

- [x] **Test Environment Needs**
  - *See environment requirements in Section II.3 and testing tools in Section II.3.1*

- [x] **Topology Considerations**
  - *Describe topology requirements:* Same as parent STP. Dual-stream cluster required for
    migration and node placement scenarios; RHCOS 10.2-only cluster required for IUO regression.
  - *Impact on test design:* Node placement tests require labeling nodes by RHCOS version
    and using node affinity to control VM scheduling and migration targets.

### **II. Software Test Plan (STP)**

#### **1. Scope of Testing**

**Testing Goals**

- **[P0]** Verify all IUO Tier 1 and Tier 2 tests pass on an RHCOS 10.2-only cluster.
- **[P1]** Verify migration metrics (duration, data processed, bandwidth) are reported accurately during cross-version live migration on dual-stream clusters (RHCOS 9.8 ↔ RHCOS 10.2).
- **[P1]** Verify node placement policies (node affinity, eviction) are respected on dual-stream clusters.

**Out of Scope (Testing Scope Exclusions)**

- **Upgrade testing**
  - *Rationale:* Relevant only from 5.1.0.
  - *PM/Lead Agreement:* Martin Tessun / 2026-05-13

- **Operator installation on RHCOS 10.2 from scratch**
  - *Rationale:* Operator installation is identical regardless of RHCOS version — no IUO-specific
    code paths differ. Installation correctness is validated by the Tier 1/2 suites passing on
    the RHCOS 10.2 cluster.
  - *PM/Lead Agreement:* [Name/Date]

**Test Limitations**

- **Dual-stream cluster provisioning depends on QE DevOps tooling.** Same limitation as the parent
  STP — if tooling is unavailable or unstable, dual-stream scenarios cannot be executed.
  - *Sign-off:* Martin Tessun / 2026-05-13

#### **2. Test Strategy**

**Functional**

- [x] **Functional Testing** — Validates IUO-specific features on RHCOS 10.2 and dual-stream clusters
  - *Details:* Run existing IUO Tier 1 and Tier 2 suites on RHCOS 10.2-only cluster. For
    dual-stream: targeted manual testing of migration metrics, node placement, and must-gather.

- [x] **Automation Testing** — Migration metrics validation on dual-stream clusters
  - *Details:* Existing IUO Tier 1/2 suites run as-is on RHCOS 10.2 cluster. New automation
    for migration metrics validation during cross-version live migration (RHCOS 9.8 ↔ RHCOS 10.2).

- [x] **Regression Testing** — IUO regression on RHCOS 10.2
  - *Details:* Existing IUO Tier 1 and Tier 2 regression suites run on RHCOS 10.2-only cluster.
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

- [x] **Monitoring** — Verify CNV metrics on RHCOS 10.2
  - *Details:* Verify CNV metrics (including migration metrics: duration, data processed,
    bandwidth) are reported correctly on RHCOS 10.2 nodes and during cross-version live migration.

**Integration & Compatibility**

- [ ] **Compatibility Testing**
  - *Details:* Not applicable for this STP.

- [ ] **Upgrade Testing**
  - *Details:* Relevant only from 5.1.0.

- [x] **Dependencies** — Blocked on dual-stream cluster provisioning
  - *Details:* Same as parent STP. QE DevOps team must provide dual-stream cluster
    provisioning tooling before dual-stream scenarios can be tested.

- [ ] **Cross Integrations**
  - *Details:* Covered by parent STP.

**Infrastructure**

- [ ] **Cloud Testing**
  - *Details:* Covered by parent STP.

#### **3. Test Environment**

Covered by the parent STP. IUO-specific requirements:

- **Cluster Topology:**
  - RHCOS 10.2-only cluster: for IUO Tier 1/2 regression
  - Dual-stream cluster (RHCOS 9.8 + RHCOS 10.2 workers): for migration metrics,
    node placement, and must-gather dual-node scenarios

- **OCP & OpenShift Virtualization Version(s):** OCP 5.0 with CNV 5.0

- **Storage:** ocs-storagecluster-ceph-rbd-virtualization

- **Platform:** Bare metal

- **Special Configurations:** Nodes must be labeled by RHCOS version for node placement
  and migration targeting tests.

#### **3.1. Testing Tools & Frameworks**

- **Test Framework:** Standard. Tests require logic to identify nodes by RHCOS version
  for node placement and migration validation.

- **CI/CD:** Dedicated CI lanes for RHCOS 10.2 and dual-stream clusters:
    - RHCOS 10.2: IUO testing and observability lanes
    - Dual-stream: IUO testing and observability lanes

- **Other Tools:** N/A

#### **4. Entry Criteria**

Covered by the parent STP. IUO-specific entry criteria:

- [x] Requirements and design documents are **approved and merged**
- [x] RHCOS 10.2-only cluster available with IUO CI lanes provisioned
- [x] Dual-stream cluster available via QE DevOps tooling (required for migration/node-placement scenarios)

#### **5. Risks**

No IUO-specific risks identified. Feature-wide risks are covered by the parent STP.

---

### **III. Test Scenarios & Traceability**

IUO coverage for dual-stream RHCOS is primarily provided through regression testing
(existing Tier 1/2 suites on RHCOS 10.2 clusters). The following new test scenarios
are required for migration metrics validation on dual-stream clusters:

- **[CNV-85504]** — As a VM operator, I want migration metrics to be reported accurately when migrating from an RHCOS 9.8 node to an RHCOS 10.2 node.
  - *Test Scenario:* [Tier 2] Live migrate a VM from an RHCOS 9.8 node to an RHCOS 10.2 node and verify that migration metrics (duration, data processed, bandwidth) are reported correctly.
  - *Priority:* P1

- **[CNV-85504]** — As a VM operator, I want migration metrics to be reported accurately when migrating from an RHCOS 10.2 node to an RHCOS 9.8 node.
  - *Test Scenario:* [Tier 2] Live migrate a VM from an RHCOS 10.2 node to an RHCOS 9.8 node and verify that migration metrics (duration, data processed, bandwidth) are reported correctly.
  - *Priority:* P1

---

### **IV. Sign-off and Approval**

This Software Test Plan requires approval from the following stakeholders:

* **Reviewers:**
  - QE Architect: Ruth Netser (@rnetser)
  - sig-iuo representatives: @orenc1 @hmeir @rlobillo
  - sig-virt representative: Akriti Gupta (parent STP owner)
* **Approvers:**
  - QE Architect: Ruth Netser (@rnetser)
  - sig-iuo Lead: @hmeir
  - Product Manager: Martin Tessun (@mtessun)
