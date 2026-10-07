# Openshift-virtualization-tests Test plan

## **[Dual-Stream RHCOS Support — Infrastructure Scope] - Quality Engineering Plan**

### **Metadata & Tracking**

- **Enhancement(s):** https://issues.redhat.com/browse/CNV-85277 - No separate VEP or HLD for this child scope; design context is owned by the [parent STP](./stp.md) 
- **Feature Tracking:** [VIRTSTRAT-83](https://issues.redhat.com/browse/VIRTSTRAT-83)
- **Epic Tracking:** [CNV-85277](https://issues.redhat.com/browse/CNV-85277) (sig-infra QE epic: [CNV-86242](https://issues.redhat.com/browse/CNV-86242))
- **Parent STP:** [Dual-Stream RHCOS Support (parent)](./stp.md)
- **QE Owner(s):** Michal Jankowski (@mijankow)
- **SIG:** sig-infra

**Document Conventions (if applicable):**

- RHCOS = Red Hat CoreOS, the immutable container-optimized OS used for OpenShift worker nodes.
- dual-stream cluster = a cluster running both RHCOS 9 and RHCOS 10 worker nodes simultaneously.

### **Feature Overview**

This child STP covers the **sig-infra** slice of dual-stream RHCOS support for **CNV 5.0 GA**: Windows guest operation on dual-stream clusters, RHEL guest create/start/delete on dual-stream clusters, and RHEL live migration across RHCOS 9 and RHCOS 10 workers on dual-stream clusters.

Feature-wide overview, maturity (DP/TP/GA), and cross-SIG requirements are defined in the [parent STP](./stp.md). New testing goals in this child STP target CNV 5.0 GA dual-stream and RHCOS 9-only regression selections. RHCOS 10-only is **not** omitted: for CNV 4.23 it is covered by dedicated RHCOS 10-only infrastructure testing; from CNV 5.0, RHCOS 10 is the default worker configuration and is covered by standard infrastructure regression (see Existing coverage and Regression Testing).

---

### **I. Motivation and Requirements Review (QE Review Guidelines)**

#### **1. Requirement & User Story Review Checklist**

- [x] **Review Requirements**
  - *SIG-specific requirements:*
    - Windows VMs can be created, started, and used (guest connectivity) on a dual-stream cluster
    - RHEL VMs can be created, started, and deleted on a dual-stream cluster
    - RHEL VMs can be live-migrated between RHCOS 9 and RHCOS 10 workers on a dual-stream cluster in both directions, and remain usable after migration
  - *Parent-owned requirements:* All other dual-stream feature requirements are defined in the [parent STP](./stp.md)

- [x] **Acceptance Criteria**
  - On a dual-stream cluster, an administrator can create and start a Windows VM and connect to the guest successfully
  - On a dual-stream cluster, an administrator can create and start a RHEL VM and connect to the guest successfully
  - On a dual-stream cluster, an operator can live-migrate a RHEL VM from an RHCOS 9 worker to an RHCOS 10 worker; after migration the VM stays up and the guest remains reachable
  - On a dual-stream cluster, an operator can live-migrate a RHEL VM from an RHCOS 10 worker to an RHCOS 9 worker; after migration the VM stays up and the guest remains reachable
  - On a dual-stream cluster, an administrator can delete a RHEL VM after successful operation

- [x] **Testability**
  - *Note any SIG-specific requirements that are unclear or untestable:* All sig-infra requirements above are testable through existing infrastructure guest-OS automation and dedicated CNV 5.0 CI lanes (see Section II.3.1). Continuous in-migration guest reachability (proving no interruption during the migration window) is **not** covered by the current automation and is not claimed below.

- [x] **Non-Functional Requirements (NFRs)**
  - *SIG-specific NFRs:* None — no new NFRs introduced in the sig-infra scope
  - *NFRs not covered and why:* Monitoring, Observability, UI, Documentation, Performance, Security, and Scalability for the dual-stream feature are owned by the [parent STP](./stp.md)

#### **2. Known Limitations**

None — no user-facing product limitations specific to sig-infra beyond those in the [parent STP](./stp.md). Reviewed with Ronen Sde-Or, 09/2026.

#### **3. Technology and Design Review**

- [ ] **Developer Handoff/QE Kickoff**
  - *Key takeaways and concerns:* Pending — no separate sig-infra kickoff meeting recorded; scope aligned asynchronously via parent STP and CNV-85277 / CNV-86242. Checklist remains open until a dated handoff is captured.

- [x] **Technology Challenges**
  - *List identified challenges:* Mixed RHCOS 9 and RHCOS 10 worker kernels may affect Windows guest operation or RHEL live migration differently per node type
  - *Impact on testing approach:* Validate Windows and RHEL guest workflows on dual-stream clusters and bidirectional RHEL live migration between RHCOS versions

- [x] **API Extensions**
  - *List new or modified user-facing APIs:* N/A — see parent STP
  - *Testing impact:* N/A

- [x] **Test Environment Needs**
  - *See environment requirements in Section II.3 and testing tools in Section II.3.1*

- [x] **Topology Considerations**
  - *Describe topology requirements:* Dual-stream cluster with at least one RHCOS 9 and one RHCOS 10 worker for migration and dual-stream guest scenarios; RHCOS 9-only cluster for infrastructure regression selections (see Section II.2)
  - *Impact on test design:* Live migration scenarios run on dual-stream clusters only

### **II. Software Test Plan (STP)**

#### **1. Scope of Testing**

**Testing Goals**

- **[P0]** As a cluster admin, I can create and start a Windows VM on a CNV 5.0 dual-stream cluster and connect to the guest
- **[P0]** As a VM operator, I can live-migrate a RHEL VM between RHCOS 9 and RHCOS 10 workers on a CNV 5.0 dual-stream cluster in both directions; after migration the VM stays up and the guest remains reachable
- **[P1]** As a cluster admin, I can create, start, and delete a RHEL VM on a CNV 5.0 dual-stream cluster
- **P0 failure-path coverage:** Negative / injected failure scenarios for the P0 goals above are not tested in this child STP (see Out of Scope)

**Out of Scope (Testing Scope Exclusions)**

- **Non-RHCOS worker node variants and mixed control-plane configurations**
  - *Rationale:* This feature targets RHCOS worker nodes only; control plane and non-RHCOS worker variants are out of scope
  - *PM/Lead Agreement:* Ronen Sde-Or, 09/2026

- **P0 failure-path scenarios on dedicated CNV 5.0 infra lanes**
  - *Rationale:* Dedicated infra lanes validate successful Windows/RHEL guest operation and successful RHEL live migration only; deliberate failure injection is not part of the lane selection
  - *PM/Lead Agreement:* Ruth Netser, 09/2026

- **Continuous guest reachability during the live-migration window**
  - *Rationale:* Current automation verifies post-migration usability (VM up, guest reachable after migration), not uninterrupted reachability throughout the migration. Claiming in-migration continuity without that evidence is out of scope for this child STP
  - *PM/Lead Agreement:* Ruth Netser, 09/2026

**Existing coverage (not Out of Scope)**

- **RHEL guest testing on RHCOS 9-only clusters** is already covered by gating infrastructure regression. This child STP does not restate it as a new testing goal; RHCOS 9-only regression selections for infrastructure are documented under Regression Testing (Section II.2).

- **RHCOS 10-only infrastructure coverage** is not omitted by sig-infra. For CNV 4.23 it is covered by dedicated RHCOS 10-only infrastructure testing. From CNV 5.0, RHCOS 10 is the default worker OS, so coverage continues via standard infrastructure regression on that default configuration (no separate RHCOS 10-only feature goals in this child STP).

**Test Limitations**

- **Testing is limited to RHCOS-based worker nodes.** Control plane and infrastructure nodes are not exercised — VMs are not scheduled or migrated on those nodes. Full infrastructure gating is not run on every topology; targeted guest-OS selections and dedicated CI lanes cover the sig-infra scope (see Section II.2).
  - *Sign-off:* Roni Kishner (@RoniKishner), 09/2026

#### **2. Test Strategy**

**Functional**

- [x] **Functional Testing**
  - *Details:* Validate Windows guest create/start/connectivity and RHEL create/start/delete on dual-stream clusters; validate bidirectional RHEL live migration between RHCOS 9 and RHCOS 10 workers with post-migration guest reachability. P0 failure-path and in-migration continuity claims are excluded per Out of Scope (Section II.1).

- [x] **Automation Testing**
  - *Details:* Scenarios run via existing infrastructure guest-OS automation in dedicated CNV 5.0 CI lanes (see Section II.3.1). No new STD required for this child scope.

- [x] **Regression Testing**
  - *Details:* On CNV 5.0 RHCOS 9-only: infrastructure guest-OS regression with Windows coverage included; RHEL migration deselected (migration is dual-stream only). On CNV 5.0 dual-stream: Windows guest coverage plus RHEL create/start/migration/delete selections. RHEL guest coverage on RHCOS 9-only remains existing gating regression (see Existing coverage above). RHCOS 10-only: dedicated infrastructure testing for CNV 4.23; from CNV 5.0 covered by standard infrastructure regression on the default RHCOS 10 worker configuration.

- [ ] **Self-Validation Testing**
  - *Details:* Not in sig-infra child scope — see [parent STP § II.2](./stp.md#2-test-strategy)

**Non-Functional**

- [ ] **Performance Testing**
  - *Details:* Not in sig-infra child scope — see [parent STP § II.2](./stp.md#2-test-strategy)

- [ ] **Scale Testing**
  - *Details:* Not in sig-infra child scope — see [parent STP § II.2](./stp.md#2-test-strategy)

- [ ] **Security Testing**
  - *Details:* Not in sig-infra child scope — see [parent STP § II.2](./stp.md#2-test-strategy)

- [ ] **Usability Testing**
  - *Details:* Not in sig-infra child scope — no UI changes; see [parent STP § II.2](./stp.md#2-test-strategy)

- [ ] **Monitoring**
  - *Details:* Not in sig-infra child scope — no new metrics or alerts; see [parent STP § II.2](./stp.md#2-test-strategy)

**Integration & Compatibility**

- [ ] **Compatibility Testing**
  - *Details:* Cross-version and platform compatibility for the dual-stream feature is owned by the [parent STP](./stp.md#2-test-strategy). Bidirectional RHEL migration scenarios for sig-infra remain under Functional Testing above.

- [ ] **Upgrade Testing**
  - *Details:* Not in sig-infra child scope — see [parent STP § II.2](./stp.md#2-test-strategy)

- [x] **Dependencies**
  - *Details:* Dedicated CNV 5.0 infrastructure CI lanes are provisioned and available ([CNV-92281](https://issues.redhat.com/browse/CNV-92281) — Closed / Done): `test-pytest-cnv-5.0-infrastructure-rhcos9`, `test-pytest-cnv-5.0-infrastructure-dualstream`.

- [ ] **Cross Integrations**
  - *Details:* Not in sig-infra child scope — see [parent STP § II.2](./stp.md#2-test-strategy)

**Infrastructure**

- [ ] **Cloud Testing**
  - *Details:* Not applicable; this feature targets bare-metal RHCOS nodes only

#### **3. Test Environment**

Covered by the [parent STP](./stp.md). Infrastructure-specific requirements:

- **FIPS:** enabled (see parent STP, Section II.3)

- **Cluster Topology:**
  - **Dual-stream testing (CNV 5.0):** High-availability (HA) bare-metal cluster — 3-control-plane / 3-worker minimum, with at least one RHCOS 9 and one RHCOS 10 worker node. SNO or compact clusters are not supported.
  - **RHCOS 9-only testing (CNV 5.0):** Standard 3-control-plane / 3-worker bare-metal cluster with all workers on RHCOS 9 (regression selections only).

- **OCP & OpenShift Virtualization Version(s):** OCP 5.0 with CNV 5.0

- **CPU Virtualization:** VT-x (Intel) or AMD-V enabled

- **Compute Resources:** Minimum per worker node: 8 vCPUs, 32GB RAM

- **Special Hardware:** N/A

- **Storage:** ocs-storagecluster-ceph-rbd-virtualization — RWX shared storage with Block volume mode required for live migration scenarios

- **Network:** Standard — no special network configuration needed beyond the standard test environment

- **Required Operators:** OpenShift Virtualization; OpenShift Data Foundation (provides `ocs-storagecluster-ceph-rbd-virtualization`)

- **Platform:** Bare metal. Dual-stream and single-stream clusters provisioned by QE DevOps tooling.

- **Special Configurations:** Worker nodes labeled by RHCOS version for VM scheduling and migration targeting; FIPS enabled per parent STP.

#### **3.1. Testing Tools & Frameworks**

- **Test Framework:** Standard. Dual-stream migration scenarios require identifying workers by RHCOS version and targeting migration between RHCOS 9 and RHCOS 10.

- **CI/CD:** Dedicated CNV 5.0 infrastructure lanes for this child STP’s RHCOS 9-only and dual-stream goals ([CNV-92281](https://issues.redhat.com/browse/CNV-92281) — Closed / Done). CNV 4.23 RHCOS 10-only and CNV 5.0 default RHCOS 10 regression use existing infrastructure CI coverage (lane definitions live with QE DevOps / CI configuration, not in this STP).

- **Other Tools:** N/A

#### **4. Entry Criteria**

The following conditions must be met before testing can begin:

- [x] Parent STP requirements and design are available for reference
- [x] Test environment can be set up and configured (see Section II.3)
- [x] Both dedicated CNV 5.0 CI lanes are provisioned and operational ([CNV-92281](https://issues.redhat.com/browse/CNV-92281))
- [x] Infrastructure guest-OS automation is available in openshift-virtualization-tests

#### **5. Risks**

**Timeline/Schedule**

- **Risk:** None identified.
  - **Mitigation:** sig-infra coverage uses existing guest-OS automation and already-provisioned CNV 5.0 CI lanes; no schedule risk specific to this child STP.

**Test Coverage**

- **Risk:** Mixed RHCOS 9 and RHCOS 10 kernels may affect Windows guest operation or RHEL live migration differently per node type.
  - **Mitigation:** Run Windows and RHEL dual-stream scenarios via dedicated CI lanes; investigate failures per guest OS and node type.
  - *Areas with reduced coverage:* Full gating infrastructure suite is not run on every topology — only the guest-OS selections described in Section II.2.
  - *Sign-off:* Roni Kishner (@RoniKishner), 09/2026

**Test Environment**

- **Risk:** None identified.
  - **Mitigation:** Dual-stream and RHCOS 9-only environments are available via dedicated CNV 5.0 infrastructure CI lanes ([CNV-92281](https://issues.redhat.com/browse/CNV-92281)).

**Untestable Aspects**

- **Risk:** None identified.
  - **Mitigation:** All SIG-owned goals in this child STP are testable through existing infrastructure guest-OS automation; in-migration continuity is intentionally Out of Scope (Section II.1), not untestable by constraint.

**Resource Constraints**

- **Risk:** None identified.
  - **Mitigation:** No additional QE headcount or special hardware beyond the standard dual-stream / RHCOS 9-only bare-metal lanes already in use.

**Dependencies**

- **Risk:** Dedicated CI lanes depend on QE DevOps maintenance after provisioning.
  - **Mitigation:** Lanes already delivered under [CNV-92281](https://issues.redhat.com/browse/CNV-92281); track ongoing lane health with QE DevOps.
  - *Third-party services or blockers:* QE DevOps team
  - *Sign-off:* Geetika Kapoor (@geetikakay), 09/2026

---

### **III. Test Scenarios & Traceability**

Scenarios below are feature outcomes owned by sig-infra. They map to **existing** infrastructure guest-OS automation (no new STD). Implementation details live in the test repository and CI lane definitions (Section II.3.1).

- **[CNV-85277]** — As a cluster admin, I want a Windows VM to run correctly on a CNV 5.0 dual-stream cluster.
  - *Test Scenario:* [Tier 3] Create and start a Windows VM on a dual-stream cluster; confirm guest connectivity (console or remote access succeeds).
  - *Priority:* P0

- **[CNV-85277]** — As a VM operator, I want to live-migrate a RHEL VM from an RHCOS 9 worker to an RHCOS 10 worker on a CNV 5.0 dual-stream cluster.
  - *Test Scenario:* [Tier 2] Live-migrate RHEL VM RHCOS 9 → RHCOS 10; after migration the VM stays up and the guest remains reachable.
  - *Priority:* P0

- **[CNV-85277]** — As a VM operator, I want to live-migrate a RHEL VM from an RHCOS 10 worker to an RHCOS 9 worker on a CNV 5.0 dual-stream cluster.
  - *Test Scenario:* [Tier 2] Live-migrate RHEL VM RHCOS 10 → RHCOS 9; after migration the VM stays up and the guest remains reachable.
  - *Priority:* P0

- **[CNV-85277]** — As a cluster admin, I want to create and start a RHEL VM on a CNV 5.0 dual-stream cluster.
  - *Test Scenario:* [Tier 2] Create and start a RHEL VM on a dual-stream cluster; confirm guest connectivity succeeds.
  - *Priority:* P1

- **[CNV-85277]** — As a cluster admin, I want to delete a RHEL VM on a CNV 5.0 dual-stream cluster after successful operation.
  - *Test Scenario:* [Tier 2] Delete a RHEL VM on a dual-stream cluster after successful operation; deletion completes successfully.
  - *Priority:* P1

---

### **IV. Sign-off and Approval**

This Software Test Plan requires approval from the following stakeholders:

* **Reviewers:**
  - QE Member (sig-infra): Geetika Kapoor (@geetikakay), Roni Kishner (@RoniKishner)
  - QE Architect: Ruth Netser (@rnetser)
* **Approvers:**
  - QE Lead (sig-infra): Geetika Kapoor (@geetikakay)
  - QE Architect: Ruth Netser (@rnetser)
  - Dev Lead: Luboslav Pivarc (@xpivarc)
  - Product Manager: Martin Tessun (@mtessun)
