# Openshift-virtualization-tests Test plan

## **[Dual-Stream RHCOS 9.8 + RHCOS 10.2 — IUO Scope] - Quality Engineering Plan**

### **Metadata & Tracking**

- **Feature Tracking:** [VIRTSTRAT-83](https://redhat.atlassian.net/browse/VIRTSTRAT-83)
- **Epic Tracking:** [CNV-49964](https://redhat.atlassian.net/browse/CNV-49964)
- **IUO Story:** [CNV-85504](https://redhat.atlassian.net/browse/CNV-85504)
- **Parent STP:** [stp.md](stp.md)
- **QE Owner(s):** Ohad Revah (@OhadRevah)
- **SIG:** sig-iuo (Install, Upgrade, Operators)

**Document Conventions (if applicable):**

- **RHCOS9.8:** Red Hat CoreOS 9.8 worker nodes (GA, default for OCP 4.22).
- **RHCOS10.2:** Red Hat CoreOS 10.2 worker nodes (Tech Preview in 4.22, GA in 5.0).
- **Dual-stream cluster:** An OCP cluster running both RHCOS9.8 and RHCOS10.2 worker nodes simultaneously.
- **Golden images:** Pre-configured VM boot sources managed by the SSP operator via DataImportCrons.

### **Feature Overview**

This STP covers the IUO-specific aspects of dual-stream RHCOS support: validating that
OpenShift Virtualization deploys and functions correctly on RHCOS 10.2, golden images are available and bootable, diagnostic data collection works on RHCOS 10.2 nodes,
node placement policies are honored in mixed-version clusters, observability metrics work
as expected, and migration metrics are accurately reported during cross-version live migration.

This STP covers testing for the Tech Preview phase. Automation is required only at GA.

---

### **I. Motivation and Requirements Review (QE Review Guidelines)**

#### **1. Requirement & User Story Review Checklist**

- [x] **Review Requirements**
  - *SIG-specific requirements:*
    - OpenShift Virtualization components deploy and report ready on RHCOS 10.2 worker nodes
    - Golden images are available and functional on RHCOS 10.2
    - Must-gather collects complete and valid data from RHCOS 10.2 nodes
    - CNV migration metrics are reported accurately during cross-version live migration
    - Node placement policies are respected when scheduling and migrating VMs on dual-stream clusters

- [x] **Acceptance Criteria**
  - All IUO Tier 1 and Tier 2 tests pass on an RHCOS 10.2-only cluster
  - Must-gather produces complete output from RHCOS 10.2 nodes, with no missing data compared to RHCOS 9.8
  - Golden images are available and VMs can boot from them on RHCOS 10.2
  - Migration metrics (duration, data processed, bandwidth) are accurate when migrating between RHCOS 9.8 and RHCOS 10.2 nodes
  - Node affinity rules are enforced correctly on dual-stream clusters

- [x] **Testability**
  - *Note any SIG-specific requirements that are unclear or untestable:* All requirements are testable
    through existing IUO test suites and targeted manual validation on RHCOS 10.2 and dual-stream clusters.

- [x] **Non-Functional Requirements (NFRs)**
  - *SIG-specific NFRs:*
    - Monitoring: CNV metrics (including migration metrics) must report correctly on RHCOS 10.2 nodes
  - *NFRs not covered and why:*
    - Performance: N/A — no new IUO-specific performance requirements; covered by parent STP
    - Security: N/A — no new auth or RBAC changes; FIPS requirement covered by parent STP
    - Scalability: N/A — no new scale requirements for IUO components
    - Observability: N/A — no new IUO-specific observability requirements; existing CNV monitoring applies unchanged
    - UI: N/A — dual-stream RHCOS support introduces no new user journeys or UI elements for IUO; existing console functionality is unchanged
    - Documentation: N/A — no IUO-specific documentation changes; release notes covered by parent STP

#### **2. Known Limitations**

None — reviewed and confirmed that no IUO-specific feature limitations apply for this release.

#### **3. Technology and Design Review**

- [x] **Developer Handoff/QE Kickoff**
  - *Key takeaways and concerns:* CNV operators run the same el9.8 userland on both RHCOS 9.8 and
    RHCOS 10.2 kernels. No operator code changes are expected, but kernel differences could surface
    unexpected behavior in must-gather log collection or golden image provisioning as well as metrics.

- [x] **Technology Challenges**
  - *List identified challenges:*
    - Must-gather may encounter differences in log paths or system service names between RHCOS 9.8
      and RHCOS 10.2 nodes, potentially causing incomplete data collection.
    - Golden image provisioning (DataImportCrons) depends on storage and CDI behavior that may
      differ with the RHCOS 10.2 kernel.
  - *Impact on testing approach:* Must-gather output must be compared between RHCOS 9.8 and
    RHCOS 10.2 to identify any gaps. Golden image tests must verify the full lifecycle
    (import, boot, connectivity).

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

- **[P0]** As a cluster admin, I want all IUO Tier 1 and Tier 2 tests to pass on an RHCOS 10.2-only
  cluster so that I know OpenShift Virtualization functions correctly on the new platform.
- **[P0]** As a cluster admin, I want must-gather to collect complete data from RHCOS 10.2 nodes so
  that support cases can be investigated without missing information.
- **[P1]** As a cluster admin, I want golden images to be available and functional on an
  RHCOS 10.2 cluster so that I can create VMs from pre-configured templates.
- **[P1]** As a VM operator, I want migration metrics (duration, data processed, bandwidth) to be
  reported accurately when migrating between RHCOS 9.8 and RHCOS 10.2 nodes so that I can monitor
  migration health.
- **[P1]** As a cluster admin, I want node placement policies (node affinity, eviction) to be
  respected when scheduling and migrating VMs on a dual-stream cluster so that workloads land on
  the correct node type.
- **[P1]** As a cluster admin, I want must-gather on a dual-stream cluster to collect data from both
  RHCOS 9.8 and RHCOS 10.2 nodes so that I have a complete diagnostic picture.

**Out of Scope (Testing Scope Exclusions)**

- **Upgrade testing (4.22 to 5.0)**
  - *Rationale:* Upgrade testing will be covered in the 5.0 STP per parent STP decision.
    Not planned as part of 4.22 testing.
  - *PM/Lead Agreement:* Martin Tessun / 2026-05-13

- **Operator installation on RHCOS 10.2 from scratch**
  - *Rationale:* Operator installation is identical regardless of RHCOS version — no IUO-specific
    code paths differ. Installation correctness is validated by the Tier 1/2 suites passing on
    the RHCOS 10.2 cluster.
  - *PM/Lead Agreement:* [Name/Date]

**Test Limitations**

- **No automation requirement for Tech Preview.** Testing is manual/ad-hoc for the TP phase (4.22).
  Automation will be implemented for GA (5.0).
  - *Sign-off:* [Name/Date]

- **Dual-stream cluster provisioning depends on QE DevOps tooling.** Same limitation as the parent
  STP — if tooling is unavailable or unstable, dual-stream scenarios cannot be executed.
  - *Sign-off:* Martin Tessun / 2026-05-13

#### **2. Test Strategy**

**Functional**

- [x] **Functional Testing** — Validates IUO-specific features on RHCOS 10.2 and dual-stream clusters
  - *Details:* Run existing IUO Tier 1 and Tier 2 suites on RHCOS 10.2-only cluster. For
    dual-stream: targeted manual testing of migration metrics, node placement, and must-gather.

- [ ] **Automation Testing** — No new automation for TP phase
  - *Details:* Existing IUO Tier 1/2 suites run as-is on RHCOS 10.2 cluster. New dual-stream
    test automation planned for GA (5.0).

- [x] **Regression Testing** — IUO regression on RHCOS 10.2
  - *Details:* Existing IUO Tier 1 and Tier 2 regression suites run on RHCOS 10.2-only cluster.
    Failures triaged and bugs filed with RHCOS-version attribution.

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
  - *Details:* Out of scope for 4.22; covered in 5.0 STP per parent STP decision.

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

- **OCP & OpenShift Virtualization Version(s):** OCP 4.22 with CNV 4.22

- **Storage:** ocs-storagecluster-ceph-rbd-virtualization

- **Platform:** Bare metal

- **Special Configurations:** Nodes must be labeled by RHCOS version for node placement
  and migration targeting tests.

#### **3.1. Testing Tools & Frameworks**

- **Test Framework:** Standard. Tests require logic to identify nodes by RHCOS version
  for node placement and migration validation.

- **CI/CD:** Existing IUO Tier 1/2 CI lanes run on RHCOS 10.2-only cluster.
  Dual-stream scenarios are manual/ad-hoc for TP.

- **Other Tools:** N/A

#### **4. Entry Criteria**

Covered by the parent STP. IUO-specific entry criteria:

- [x] Requirements and design documents are **approved and merged**
- [x] RHCOS 10.2-only cluster available with IUO CI lanes provisioned
- [ ] Dual-stream cluster available via QE DevOps tooling (required for migration/node-placement scenarios)

#### **5. Risks**

**Test Coverage**

- **Risk:** Golden image behavior differences between RHCOS 9.8 and RHCOS 10.2 kernels could
  surface unexpected issues in DataImportCron or CDI that are not covered by existing test suites.
  - **Mitigation:** Run full golden image lifecycle tests (import, boot, connectivity) on
    RHCOS 10.2 and compare results with RHCOS 9.8 baseline. File bugs with RHCOS-version attribution.
  - *Areas with reduced coverage:* Golden image edge cases (non-standard image formats,
    large images) are not explicitly tested on RHCOS 10.2.

**Test Environment**

- **Risk:** Dual-stream cluster provisioning tooling may be unavailable or unstable, blocking
  migration metrics and node placement testing.
  - **Mitigation:** Same as parent STP — engage QE DevOps early; fallback to manual
    mixed-node cluster provisioning if tooling is delayed.
  - *Missing or unavailable environments:* Dual-stream cluster if QE DevOps tooling is not ready.
  - *Sign-off:* Martin Tessun / 2026-05-13

**Resource Constraints**

- **Risk:** Manual ad-hoc testing for TP phase increases IUO team effort for dual-stream scenarios
  compared to automated regression.
  - **Mitigation:** Focus manual testing on P0 and P1 goals. Prioritize must-gather and
    golden images as highest-value manual checks. Automation planned for GA.
  - *Current capacity gaps:* None — manageable within assigned QE resources for TP scope.

---

### **III. Test Scenarios & Traceability**

- **[CNV-85504](https://redhat.atlassian.net/browse/CNV-85504)** — As a cluster admin, I want
  OpenShift Virtualization to function correctly on RHCOS 10.2 so that I can run virtualization
  workloads on the new platform.
  - *Test Scenario:* [Tier 1] Verify OpenShift Virtualization components deploy, report ready,
    and operate correctly on an RHCOS 10.2-only cluster, including operator health, VM lifecycle,
    and workload scheduling.
  - *Priority:* P0

- **[CNV-85504](https://redhat.atlassian.net/browse/CNV-85504)** — As a cluster admin, I want
  must-gather to collect complete diagnostic data from RHCOS 10.2 nodes so that support cases are
  not blocked by missing information.
  - *Test Scenario:* [Tier 1] Run must-gather on RHCOS 10.2 cluster and verify output includes all
    expected sections (operator logs, VM state, node info) with no gaps compared to RHCOS 9.8.
  - *Priority:* P0

- **[CNV-85504](https://redhat.atlassian.net/browse/CNV-85504)** — As a cluster admin, I want
  golden images to be available on RHCOS 10.2 so that I can create VMs from pre-configured templates.
  - *Test Scenario:* [Tier 1] Verify golden images are created and updated on RHCOS 10.2
    cluster. Boot a VM from a golden image and verify it reaches a running state with network
    connectivity.
  - *Priority:* P1

- **[CNV-85504](https://redhat.atlassian.net/browse/CNV-85504)** — As a VM operator, I want
  migration metrics to be accurate during cross-version live migration so that I can monitor
  migration health on a dual-stream cluster.
  - *Test Scenario:* [Tier 2] Live migrate a VM from an RHCOS 9.8 node to an RHCOS 10.2 node and
    back. Verify migration metrics (duration, data processed, bandwidth) are reported correctly
    and match observed behavior.
  - *Priority:* P1

- **[CNV-85504](https://redhat.atlassian.net/browse/CNV-85504)** — As a cluster admin, I want
  node placement policies to be respected on a dual-stream cluster so that VMs are scheduled on
  the correct node type.
  - *Test Scenario:* [Tier 2] Configure node affinity rules targeting RHCOS 10.2 nodes. Create a VM
    and verify it is scheduled on an RHCOS 10.2 node. Trigger a live migration and verify the VM
    lands on a node matching the placement policy.
  - *Priority:* P1

- **[CNV-85504](https://redhat.atlassian.net/browse/CNV-85504)** — As a cluster admin, I want
  must-gather on a dual-stream cluster to capture data from both node types so that I have a
  complete diagnostic picture.
  - *Test Scenario:* [Tier 2] Run must-gather on a dual-stream cluster and verify output includes
    data from both RHCOS 9.8 and RHCOS 10.2 nodes. Compare against single-version output to
    confirm no gaps.
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
