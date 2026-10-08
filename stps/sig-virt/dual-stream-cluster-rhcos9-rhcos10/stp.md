# Openshift-virtualization-tests Test plan

## **Dual-Stream RHCOS Support (RHCOS9.x + RHCOS10.x Worker Nodes) — Quality Engineering Plan**

### **Metadata & Tracking**

- **Enhancement(s):** https://issues.redhat.com/browse/VIRTSTRAT-83
- **Feature Tracking:** No separate VEP/HLD; tracked via VIRTSTRAT-83
- **Epic Tracking:** https://issues.redhat.com/browse/CNV-84749
- **QE Owner(s):** Akriti Gupta (@akri3i)
- **Readiness Tracking:** [RHCOS 10 Readiness Tracking](https://docs.google.com/spreadsheets/d/1mD1mVkiIqrdyaDIqB0fhRgmywWp4sI9OEy0IVBD6pDc/edit?gid=0#gid=0)
- **Owning SIG:** sig-virt
- **Participating SIGs:** sig-virt, sig-network, sig-storage, sig-iuo, sig-infra
- **Child STPs:**
  - [sig-network](./network.md) — QE Owner: Asia Khromov (@azhivovk)
  - [sig-storage](./storage.md) — QE Owner: Kate Shvaika (@kshvaika)
  - sig-iuo — QE Owner: Ohad Revah (@OhadRevah) — child STP: [PR #108](https://github.com/RedHatQE/openshift-virtualization-tests-design-docs/pull/108) (not yet merged)
  - [sig-infra](./infra.md) — QE Owner: Michal Jankowski (@mijankow); tracked in [CNV-86242](https://issues.redhat.com/browse/CNV-86242)
  - sig-virt — covered by this parent STP (no separate child STP)

- **Target Release(s):**
  - DP: N/A
  - TP: v4.22 — RHCOS 10.x worker node support is Tech Preview
  - GA: v5.0 — RHCOS 10.x support GA

> **This is a Parent STP.** It defines the overall dual-stream RHCOS testing strategy and cross-cutting
> requirements. Each participating SIG is expected to create a child STP that extends this document with
> SIG-specific test scenarios. Child STPs should reference this parent STP and must not duplicate content
> defined here.

**Document Conventions:**

- **RHCOS9.x:** Red Hat CoreOS 9.x worker nodes (supported alongside RHCOS 10.x through CNV 5.2).
- **RHCOS10.x:** Red Hat CoreOS 10.x worker nodes (Tech Preview in 4.22, GA and default from 5.0).
- **Dual-stream cluster:** An OCP cluster running both RHCOS9.x and RHCOS10.x worker nodes simultaneously.

### **Feature Overview**

OpenShift Virtualization supports dual-stream clusters running both RHCOS 9.x and RHCOS 10.x
worker nodes in the same cluster. Customers can keep mixed worker OS versions and move VM
workloads between node types with live migration while gradually adopting RHCOS 10.

This STP validates 5.0; the feature is supported through 5.2.
RHCOS 10.x is the default worker OS in 5.0. Tech Preview dual-stream support began in 4.22.

---

### **I. Motivation and Requirements Review (QE Review Guidelines)**

#### **1. Requirement & User Story Review Checklist**

- [x] **Review Requirements**
  - *Key requirements reviewed:*
    - CNV 4.22 / 4.23 (Tech Preview): RHCOS9.x is GA/default; RHCOS10.x is Tech Preview.
      Covered by the earlier 4.22-era STP work — **out of scope for this STP**.
    - CNV 5.0: RHCOS10.x is GA/default; RHCOS9.x remains supported for dual-stream and
      RHCOS 9.x-only clusters through CNV 5.2.
    - OCPSTRAT-1150: Support dual-stream clusters to
      allow customers to run mixed hardware. VM live migration must succeed across
      RHCOS9.x ↔ RHCOS10.x worker nodes.

- [x] **Understand Value and Customer Use Cases**
  - *Feature value to customers:* Customers can run mixed hardware in the same cluster — newer
    hardware that requires RHEL 10 and older hardware that only supports RHEL 9.
  - *Customer use cases:*
    - As a cluster administrator, I want to add RHCOS10.x worker nodes to my existing
      cluster.
    - As a VM operator, I want to live-migrate VMs from RHCOS9.x worker nodes to RHCOS10.x worker
      nodes.
    - As a platform team, I want to validate that CNV behaves correctly on both RHCOS9.x and RHCOS10.x
      nodes.

- [x] **Acceptance Criteria**
  - *Acceptance criteria:*
    - CNV features on dual-stream clusters behave as on single-OS clusters — validated by existing
      Tier 1/2/3 suites; SIG-specific coverage documented in child STPs.
    - A VM on an RHCOS9.x worker can be live-migrated to an RHCOS10.x worker and back:
      VM remains in Running phase throughout migration, a guest workload started before
      migration continues running after migration without restart, and the VM is accessible
      on the target node — validated by CNV-81251 scenarios in Section III.
    - A VM on an RHCOS10.x worker can be live-migrated to an RHCOS9.x worker and back:
      VM remains in Running phase throughout migration, a guest workload started before
      migration continues running after migration without restart, and the VM is accessible
      on the target node — validated by CNV-81251 scenarios in Section III.
    - Single-stream RHCOS 9.x-only coverage (supported through CNV 5.2) is provided by existing
      Tier 1/2/3 regression suites from participating SIGs (see Testing Goals / Regression
      Testing) — not by new Section III scenarios.

- [x] **Non-Functional Requirements (NFRs)**
  - *Applicable NFRs:*
    - **Performance:** N/A — no new workloads introduced; existing Tier 1/2/3 results serve as the baseline.
    - **Security:** Required — all testing must be performed with FIPS enabled (see Test Environment, Section II.3).
    - **Monitoring/Observability:** N/A — no new alerts or metrics introduced; existing CNV monitoring applies unchanged.
    - **Scalability:** N/A — no new scale requirements; existing cluster-level live migration parallelism limits apply.
    - **UI:** N/A — no UI code changes introduced; UI testing adds no customer value for this feature.
    - **Documentation:** Release notes must document RHCOS10.x Tech Preview status in 4.22 and GA status timeline.
    - **Compatibility:** Required — CNV must remain compatible with RHCOS 9.x, RHCOS 10.x, and
      dual-stream clusters. Validated via existing Tier 1/2/3 suites on both node types, plus
      dual-stream live migration scenarios in Section III. SIG-specific coverage is in child STPs.


#### **2. Technology and Design Review**

- [x] **Developer Handoff/QE Kickoff**
  - *Key takeaways and concerns:*
    - The dual-stream support approach was reviewed and signed off by PM, Engineering, Platform,
      and Product Operations per the [recommendation document](https://docs.google.com/document/d/1MMNmUbhGPymnJDrbqbcq_KGi_FN9jxTvAdnzed1cwWw/edit?tab=t.0#heading=h.54747tl9m7p8).
    - CNV component teams must update their STPs for dual-stream scenarios.

- [x] **Technology Challenges**
  - *Identified challenges:*
    - **CNV compatibility on RHCOS 10.x:** RHCOS 10.x is a new platform configuration that may
      surface unexpected failures. Tier 1, Tier 2, and Tier 3 testing is the primary mechanism for
      finding these issues.
    - **Dual-stream cluster provisioning:** Clusters with mixed RHCOS9.x and RHCOS10.x worker
      nodes require specific provisioning tooling. QE DevOps has provided this capability
      and it is validated and available for test use.

  - *Impact on testing approach:*
    - Tier 1, Tier 2, and Tier 3 testing on an RHCOS10.x-only cluster is default in CNV-5.0.
    - Since RHCOS9.x is still supported in 5.0, testing should also cover RHCOS9.x-only clusters;
      component teams decide which tests to run.
    - Each participating SIG decides which tests to run on dual-stream clusters based on their
      feature area requirements.
    - Live migration across RHCOS versions must be tested explicitly.

- [x] **API Extensions**
  - *New or modified user-facing APIs:* No Upstream or Downstream changes in CNV.
  - *Testing impact:* No new API tests required.

- [x] **Test Environment Needs**
  - *See Section II.3 for environment requirements.*

- [x] **Topology Considerations**
  - *Topology requirements:*
    - FOR RHCOS 10.x:
      - Either high-availability (HA) or a compact cluster
      - Requires both control plane and worker nodes to be on RHCOS 10.x
    - FOR RHCOS 9.x:
      - Either high-availability (HA) or a compact cluster
      - Requires both control plane and worker nodes to be on RHCOS 9.x
    - For OCPSTRAT-1150:
      - Dual-stream testing requires a high-availability (HA) bare-metal
        cluster — at least 1 worker running RHCOS10.x alongside RHCOS9.x workers
        within the same OCP cluster.
---

#### **3. Known Limitations**

- **CNV on RHCOS 10.x worker nodes uses the same software stack as on RHCOS 9.x
  through CNV 5.2.** A fully RHCOS 10-native CNV stack is planned for OCP 5.3
  (testing decision and sign-off in Out of Scope, Section II.1).

---

### **II. Software Test Plan (STP)**

#### **1. Scope of Testing**

**Testing Goals**

- **[P1] [Regression]** On an RHCOS 9.x-only cluster (supported through CNV 5.2), existing
  Tier 1/2/3 suites from sig-virt, sig-network, sig-storage, sig-iuo, and sig-infra run as
  decided by each SIG. No new single-stream tests; coverage is regression.
- **[P1]** As a cluster admin, I can operate a dual-stream cluster (RHCOS 9.x + RHCOS 10.x worker
  nodes) and all supported VM workloads function correctly on both node types.
- **[P1]** As a VM operator, I can live-migrate a VM from an RHCOS 9.x worker node to an RHCOS 10.x
  worker node and back (and vice versa): the VM remains in Running phase throughout migration,
  a guest workload started before migration continues running after migration without restart,
  and the VM is accessible on the target node.


**Out of Scope (Testing Scope Exclusions)**

- **Fully RHCOS 10-native CNV stack**
  - *Rationale:* A fully RHCOS 10-native CNV stack is planned for OCP 5.3 and is a separate
    testing effort. This STP covers only dual-stream support through OCP 5.2.
  - *PM/Lead Agreement:* Martin Tessun / 2026-05-13

- **Upgrade testing**
  - *Rationale:* This STP validates CNV 5.0. Upgrade testing is relevant only
    from 5.1.0.
  - *PM/Lead Agreement:* Martin Tessun / 2026-05-13


**Test Limitations**

- None — dual-stream cluster provisioning tooling from QE DevOps is validated and available
  (see Dependencies in Section II.2 and Entry Criteria in Section II.4).
  - *Sign-off:* Martin Tessun / 2026-05-13


#### **2. Test Strategy**

**Functional**

- [x] **Functional Testing**
  - For OCPSTRAT-1150: Validates that the full CNV feature set operates correctly on dual-stream clusters.
    - VM live migration must succeed across RHCOS9.x ↔ RHCOS10.x worker nodes.
      - Successful live migration of a VM from an RHCOS9.x worker node to an RHCOS10.x worker
        node and back to RHCOS9.x — that is, the VM is created first on an RHCOS9.x worker node
      - Successful live migration of a VM from an RHCOS10.x worker node to an RHCOS9.x worker
        node and back to RHCOS10.x — that is, the VM is created first on an RHCOS10.x worker node
  - Single-stream RHCOS 9.x-only coverage is **regression** for this STP (see Regression
    Testing and Testing Goals).

- [x] **Automation Testing**
  - For RHCOS 9.x single-stream regression: No new automation — existing Tier 1, Tier 2,
    and Tier 3 suites are run as-is as decided by each SIG.
  - For OCPSTRAT-1150 (dual-stream live migration): Automation is **done** for sig-virt
    (CNV-81251 scenarios in this parent STP), sig-network, and sig-infra. sig-storage and
    sig-iuo automation is **not done**; sig-storage tracks remaining work in
    [storage.md](./storage.md), and sig-iuo tracks remaining work in
    [PR #108](https://github.com/RedHatQE/openshift-virtualization-tests-design-docs/pull/108).

- [x] **Regression Testing** — RHCOS 9.x-only single-stream coverage for this STP.
  - *SIG suites:* sig-virt, sig-network, sig-storage, sig-iuo, and sig-infra each run their
    existing Tier 1, Tier 2, and Tier 3 suites on RHCOS 9.x-only as decided by each SIG.
    Each SIG documents results/bugs in their own Jira stories / child STPs.
  - On RHCOS9.x-only cluster (supported through CNV 5.2):
    - *Details:* Run existing Tier 1, Tier 2, and Tier 3 test suites against RHCOS 9.x
      as decided by each participating SIG.
  - On RHCOS10.x-only cluster: RHCOS 10.x is the CNV 5.0 default; existing Tier 1/2/3 suites
    already run there as standard product CI. Not a Testing Goal of this STP.
  - For OCPSTRAT-1150: see Automation Testing above.
  - Regression coverage is **not** listed in Section III.
- [ ] **Self-Validation Testing**
  - *Details:* N/A. RHCOS 10.x-only and dual-stream scenarios require specialized cluster
    configurations not available in self-validation environments.

**Non-Functional**

- [x] **Performance Testing** — N/A

- [x] **Scale Testing** — N/A

- [x] **Security Testing** — N/A

- [x] **Usability Testing** — N/A

- [x] **Monitoring** — N/A

**Integration & Compatibility**

- [x] **Compatibility Testing** — CNV must remain compatible with both RHCOS9.x and RHCOS10.x.
  - *Details:* Compatibility is validated through Tier 1, Tier 2, and Tier 3 runs on both RHCOS9.x
    and RHCOS10.x clusters for OCP/CNV 5.0. This STP validates 5.0; the feature is supported
    through 5.2. 4.22/4.23 Tech Preview coverage is handled by the earlier 4.22-era STP.
    Component teams validate their specific feature areas in child STPs.

- [ ] **Upgrade Testing** — Out of scope for this STP.
  - *Details:* Relevant only from 5.1.0.
  - *PM/Lead Agreement:* Martin Tessun / 2026-05-13

- [x] **Dependencies** — Resolved.
  - *Details:* QE DevOps team has provided dual-stream cluster provisioning
      (RHCOS9.x + RHCOS10.x workers in the same cluster).

- [x] **Cross Integrations** — Other SIGs must create a child STP extending this one to cover testing for OCPSTRAT-1150.
  - *Details:* sig-network, sig-storage, sig-iuo, and sig-infra must each create child STPs
    specifying their Tier 1, Tier 2 and Tier 3 test coverage on RHCOS10.x nodes and dual-stream
    clusters.

**Infrastructure**

- [ ] **Cloud Testing**
  - *Details:* N/A. Dual-stream testing requires an HA bare-metal cluster.

#### **3. Test Environment**

- **FIPS:** enabled

- **Cluster Topology:**
  - **Dual-stream testing:** High-availability (HA) bare-metal cluster required —
    3-control-plane / 3-worker minimum, with at least 1 worker running RHCOS10.x alongside
    RHCOS9.x workers. SNO or compact clusters are not supported for dual-stream testing.
  - **RHCOS10.x-only testing:** Standard 3-control-plane / 3-worker bare-metal cluster with all
    workers on RHCOS10.x.
  - **RHCOS9.x-only testing:** Standard 3-control-plane / 3-worker bare-metal cluster with all
    workers on RHCOS9.x (supports P1 single-stream regression goal).

- **OCP & OpenShift Virtualization Version(s):** OCP 5.0 with CNV 5.0. This STP validates 5.0;
  the feature is supported through 5.2. 4.22/4.23 Tech Preview is covered by the earlier
  4.22-era STP.

- **CPU Virtualization:** Standard (VT-x / AMD-V enabled)

- **Compute Resources:** Standard

- **Special Hardware:** N/A

- **Storage:** ocs-storagecluster-ceph-rbd-virtualization

- **Network:** Standard

- **Required Operators:** Standard.

- **Platform:** Bare metal. Dual-stream cluster provisioned by QE DevOps tooling.

- **Special Configurations:** Dual-stream cluster with FIPS enabled. QE DevOps dual-stream
  provisioning tooling is validated and available to deploy this configuration.

#### **3.1. Testing Tools & Frameworks**

- **Test Framework:**
  - Standard (openshift-virtualization-tests) for RHCOS 10.x
  - For OCPSTRAT-1150 (dual-stream): see Automation Testing in Section II.2.
- **CI/CD:** Two cluster configurations are required, both available from CNV 4.22:
  - **RHCOS10.x-only cluster:** Existing Tier 1, Tier 2 and Tier 3 jobs run by all component teams.
  - **Dual-stream cluster:** See Automation Testing (Section II.2) for per-SIG automation status.

- **Other Tools:** N/A

#### **4. Entry Criteria**

The following conditions must be met before testing can begin:

- [x] Requirements and design documents are **approved and merged**
  (recommendation doc sign-offs from PM, Engineering, Platform, Product Ops confirmed)
- [x] Test environment can be **set up and configured** (dual-stream cluster available via
  QE DevOps tooling)
- [x] QE DevOps dual-stream cluster provisioning is validated and available
- [x] CNV 5.0 defaults to RHCOS 10.x worker nodes

#### **5. Risks**

**Timeline/Schedule**

- **Risk:** None identified.
  - **Mitigation:** N/A
  - *Estimated impact on schedule:* N/A

**Test Coverage**

- **Risk:** sig-storage and sig-iuo dual-stream automation is not done. Remaining
  coverage depends on those SIGs landing automation tracked in their child STPs
  (see Automation Testing, Section II.2). Target: CNV 5.0 GA.
  - **Mitigation:** See Automation Testing (Section II.2) for tracking links.
  - *Areas with reduced coverage:* Dual-stream automation for sig-storage and sig-iuo
    until those child STPs record the work as done.
  - *Sign-off:* Martin Tessun / 2026-05-13

**Test Environment**

- **Risk:**
  - HA resource shortage.
  - **Mitigation:**
    - Use QE DevOps dual-stream HA bare-metal provisioning and coordinate cluster
      capacity for dual-stream runs.
  - *Missing or unavailable environments:* HA bare-metal capacity.
  - *Sign-off:* Martin Tessun / 2026-05-13

**Untestable Aspects**

- **Risk:** None identified.
  - **Mitigation:** N/A
  - *Reason untestable and mitigation approach:* N/A

**Resource Constraints**

- **Risk:** None identified.
  - **Mitigation:** N/A — sig-virt dual-stream automation is done; other SIGs track any
    pending automation in their child STPs (see Automation Testing).
  - *Missing resources or infrastructure:* N/A
  - *Sign-off:* Martin Tessun / 2026-05-13

**Dependencies**

- **Risk:** None identified.
  - **Mitigation:** N/A
  - *Third-party services or blockers:* N/A

**Other**

- **Risk:** None identified.
  - **Mitigation:** N/A

---

### **III. Test Scenarios & Traceability**


- **[CNV-81251](https://issues.redhat.com/browse/CNV-81251)** — As a VM operator, I want to live-migrate VMs between RHCOS9.x and
  RHCOS10.x worker nodes within the same cluster so my workloads remain available during
  node maintenance.
  - *Test Scenario:* [Tier 2] **Scenario 1** — A VM created on an RHCOS9.x worker node
    is live-migrated to an RHCOS10.x worker node, then back to RHCOS9.x. For each migration:
    the VM remains in Running phase throughout migration, a guest workload started before
    migration continues running after migration without restart, and the VM is accessible
    on the target node.
  - *Guest OS:* RHEL, Windows
  - *Priority:* P1

- **[CNV-81251](https://issues.redhat.com/browse/CNV-81251)** — As a VM operator, I want to live-migrate VMs between RHCOS9.x and
  RHCOS10.x worker nodes within the same cluster so my workloads remain available during
  node maintenance.
  - *Test Scenario:* [Tier 2] **Scenario 2** — A VM created on an RHCOS10.x worker node
    is live-migrated to an RHCOS9.x worker node, then back to RHCOS10.x. For each migration:
    the VM remains in Running phase throughout migration, a guest workload started before
    migration continues running after migration without restart, and the VM is accessible
    on the target node.
  - *Guest OS:* RHEL, Windows
  - *Priority:* P1

---

### **IV. Sign-off and Approval**

This Software Test Plan requires approval from the following stakeholders:

- **Reviewers:**
  - QE Members (sig-iuo): Ohad Revah (@OhadRevah)
  - QE Members (sig-network): Asia Zhivov Khromov (@azhivovk)
  - QE Members (sig-storage): Jenia Peimer (@jpeimer), Kate Shvaika (@kshvaika)
  - QE Members (sig-virt): Denys Shchedrivyi (@dshchedr), Vasiliy Sibirskiy (@vsibirsk),
    Samuel Alberstein (@SamAlber)
  - QE Members (sig-infra): Geetika Kapoor (@geetikakay), Roni Kishner (@RoniKishner)
- **Approvers:**
  - QE Architect: Ruth Netser (@rnetser)
  - Principal Developer (sig-virt): Luboslav Pivarc (@xpivarc)
  - Product Manager: Martin Tessun (@mtessun)
