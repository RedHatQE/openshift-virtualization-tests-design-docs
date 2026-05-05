# Openshift-virtualization-tests Test plan

## **Dual-Stream RHCOS Support (RHCOS9.8 + RHCOS10.2 Worker Nodes) — Quality Engineering Plan**

### **Metadata & Tracking**

- **Enhancement(s):** https://redhat.atlassian.net/browse/VIRTSTRAT-83
- **Feature Tracking:** No separate VEP/HLD; tracked via VIRTSTRAT-83
- **Epic Tracking:** https://redhat.atlassian.net/browse/CNV-49964
- **QE Owner(s):** Akriti Gupta
- **Readiness Tracking:** [RHCOS 10 Readiness Tracking](https://docs.google.com/spreadsheets/d/1mD1mVkiIqrdyaDIqB0fhRgmywWp4sI9OEy0IVBD6pDc/edit?gid=0#gid=0)
- **Owning SIG:** sig-virt
- **Participating SIGs:** sig-virt, sig-network, sig-storage, sig-iuo, sig-infra

- **Target Release(s):**
  - DP: N/A
  - TP: v4.22 — RHCOS 10.2 worker node support is Tech Preview
  - GA: v5.0 — RHCOS 10.2 support GA

> **This is a Parent STP.** It defines the overall dual-stream RHCOS testing strategy and cross-cutting
> requirements. Each participating SIG is expected to create a child STP that extends this document with
> SIG-specific test scenarios. Child STPs should reference this parent STP and must not duplicate content
> defined here.

**Document Conventions:**

- **RHCOS9.8:** Red Hat CoreOS 9.8 worker nodes (GA, default for OCP 4.22).
- **RHCOS10.2:** Red Hat CoreOS 10.2 worker nodes (Tech Preview in 4.22, GA in 5.0).
- **Dual-stream cluster:** An OCP cluster running both RHCOS9.8 and RHCOS10.2 worker nodes simultaneously.

### **Feature Overview**

Starting with OCP 4.22, OpenShift Virtualization supports dual-stream clusters running both RHCOS 9.8 and RHCOS 10.2 worker nodes.
This enables customers to gradually migrate their worker nodes to RHCOS 10 while maintaining VM workload availability through live migration across node types.
RHCOS 9.8 remains the default for OCP 4.22.

---

### **I. Motivation and Requirements Review (QE Review Guidelines)**

#### **1. Requirement & User Story Review Checklist**

- [x] **Review Requirements**
  - *Key requirements reviewed:*
    - CNV 4.22: RHCOS9.8 is GA/default; RHCOS10.2 is Tech Preview.
    - OCPSTRAT-1150: Support dual-stream clusters to
      allow customers to run mixed hardware. VM live migration must succeed across
      RHCOS9.8 ↔ RHCOS10.2 worker nodes.

- [x] **Understand Value and Customer Use Cases**
  - *Feature value to customers:* Customers can run mixed hardware in the same cluster — newer
    hardware that requires RHEL 10 and older hardware that only supports RHEL 9.
  - *Customer use cases:*
    - As a cluster administrator, I want to add RHCOS10.2 worker nodes to my existing
      cluster.
    - As a VM operator, I want to live-migrate VMs from RHCOS9.8 worker nodes to RHCOS10.2 worker
      nodes.
    - As a platform team, I want to validate that CNV behaves correctly on both RHCOS9.8 and RHCOS10.2
      nodes.

- [x] **Acceptance Criteria**
  - *Acceptance criteria:*
    - All CNV features available on RHCOS 9.8 clusters work identically on RHCOS 10.2 clusters.
    - All CNV features work identically on dual-stream clusters.
    - A VM running on an RHCOS9.8 worker node can be live-migrated to an RHCOS10.2 worker node and
      back without disruption.
    - A VM running on an RHCOS10.2 worker node can be live-migrated to an RHCOS9.8 worker node and
      back without disruption.
    - CNV components deploy and report ready status on RHCOS 10.2 worker nodes with the same
      behavior as on RHCOS 9.8 nodes.

- [x] **Non-Functional Requirements (NFRs)**
  - *Applicable NFRs:*
    - **Performance:** N/A — no new workloads introduced; existing Tier 1/2/3 results serve as the baseline.
    - **Security:** Required — all testing must be performed with FIPS enabled (see Test Environment, Section II.3).
    - **Monitoring/Observability:** N/A — no new alerts or metrics introduced; existing CNV monitoring applies unchanged.
    - **Scalability:** N/A — no new scale requirements; existing cluster-level live migration parallelism limits apply.
    - **UI:** N/A — no UI code changes introduced; UI testing adds no customer value for this feature.
    - **Documentation:** Release notes must document RHCOS10.2 Tech Preview status in 4.22 and GA status timeline.
    - **Compatibility:** N/A — validated via Tier 1/2/3 runs on both RHCOS9.8 and RHCOS10.2.


#### **2. Technology and Design Review**

- [x] **Developer Handoff/QE Kickoff**
  - *Key takeaways and concerns:*
    - The dual-stream support approach was reviewed and signed off by PM, Engineering, Platform,
      and Product Operations per the [recommendation document](https://docs.google.com/document/d/1MMNmUbhGPymnJDrbqbcq_KGi_FN9jxTvAdnzed1cwWw/edit?tab=t.0#heading=h.54747tl9m7p8).
    - CNV component teams must update their STPs for dual-stream scenarios.

- [x] **Technology Challenges**
  - *Identified challenges:*
    - **CNV compatibility on RHCOS 10.2:** RHCOS 10.2 is a new platform configuration that may
      surface unexpected failures. Tier 1, Tier 2, and Tier 3 testing is the primary mechanism for
      finding these issues.
    - **Dual-stream cluster provisioning:** Clusters with mixed RHCOS9.8 and RHCOS10.2 worker
      nodes require specific provisioning tooling. DevOps QE to provide this capability.

  - *Impact on testing approach:*
    - Tier 1, Tier 2, and Tier 3 testing on an RHCOS10.2-only cluster is mandatory for all component
      teams — this is the primary testing vehicle.
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
    - FOR RHCOS 10.2:
      - Either high-availability (HA) or a compact cluster
      - Requires both control plane and worker nodes to be on RHCOS 10.2
    - For OCPSTRAT-1150:
      - Dual-stream testing requires only a high-availability (HA)
        cluster — at least 1 worker running RHCOS10.2 alongside RHCOS9.8 workers
        within the same OCP cluster.

---

#### **3. Known Limitations**

- **CNV on RHCOS 10.2 worker nodes uses the same software stack as on RHCOS 9.8
  through OCP 5.2.** A fully RHCOS 10-native CNV stack is planned for OCP 5.3
  and is out of scope for this STP.
  - *Sign-off:* Martin Tessun / 2026-05-13

---

### **II. Software Test Plan (STP)**

#### **1. Scope of Testing**

**Testing Goals**

- **[P0]** As a cluster admin, I can run all supported VM workloads on an RHCOS 10.2-only cluster
  with the same behavior as on RHCOS 9.8.
- **[P1]** As a cluster admin, I can operate a dual-stream cluster (RHCOS 9.8 + RHCOS 10.2 worker
  nodes) and all supported VM workloads function correctly on both node types.
- **[P1]** As a VM operator, I can live-migrate a VM from an RHCOS 9.8 worker node to an RHCOS 10.2
  worker node and back without disruption, and vice versa.
- **[P1]** As a cluster admin, CNV components deploy and report ready on RHCOS 10.2 worker nodes
  with the same behavior as on RHCOS 9.8 nodes.
**Out of Scope (Testing Scope Exclusions)**

- **Fully RHCOS 10-native CNV stack**
  - *Rationale:* A fully RHCOS 10-native CNV stack is planned for OCP 5.3 and is a separate
    testing effort. This STP covers only dual-stream support through OCP 5.2.
  - *PM/Lead Agreement:* Martin Tessun / 2026-05-13


**Test Limitations**

- **Dual-stream cluster provisioning depends on QE DevOps tooling.** The ability to deploy
  a cluster with mixed RHCOS9.8 and RHCOS10.2 worker nodes relies on tooling provided by the
  QE DevOps team. If this tooling is unavailable or unstable, the dual-stream migration
  scenarios cannot be executed.
  - *Sign-off:* Martin Tessun / 2026-05-13


#### **2. Test Strategy**

**Functional**

- [x] **Functional Testing**
  - Validates that the full CNV feature set operates correctly on RHCOS10.2-only clusters
  - *Details:* The primary mechanism is running existing Tier1, Tier 2 and Tier 3 test suites and triaging failures.
  - All other SIGs (sig-network, sig-storage, sig-iuo, sig-infra) must document
    their Tier1, Tier 2 and Tier 3 Test results and bugs in their own Jira Stories.
  - For OCPSTRAT-1150: Validates that the full CNV feature set operates correctly on dual-stream clusters, with el9.8 userspace.
    - VM live migration must succeed across RHCOS9.8 ↔ RHCOS10.2 worker nodes.
      - Successful LiveMigration of VM from RHCOS9.8 to RHCOS10.2 worker node and backto RHCOS9.8
          i.e VM created first on RHCOS9.8 Worker Node
      - Successful LiveMigration of VM from RHCOS10.2 to RHCOS9.8 worker node and backto RHCOS10.2
          i.e VM created first on RHCOS10.2 Worker Node

- [ ] **Automation Testing**
  - For RHCOS 10.2: No new automation tests needed — existing Tier 1, Tier 2 and Tier 3 suites
    are run as-is.
  - For OCPSTRAT-1150 (dual-stream live migration): Manual ad-hoc runs for 4.22 Tech Preview;
    node-affinity-based automation in Tier 2 by 5.0 GA.

- [x] **Regression Testing** — sig-virt and all participating SIGs must run Tier1, Tier 2 and Tier 3
  regression
  - On RHCOS10.2-only cluster.
    - *Details:* The strategy relies on running existing Tier 1, Tier 2 and Tier 3 test suites against RHCOS 10.2
  - For OCPSTRAT-1150: See Automation Testing above for the decision and rationale.

**Non-Functional**

- [x] **Performance Testing** — N/A

- [x] **Scale Testing** — N/A

- [x] **Security Testing** — N/A

- [x] **Usability Testing** — N/A

- [x] **Monitoring** — N/A

**Integration & Compatibility**

- [x] **Compatibility Testing** — CNV must remain compatible with both RHCOS9.8 and RHCOS10.2
  across the supported version range (4.22 through 5.2).
  - *Details:* Compatibility is validated through Tier 1, Tier 2 and Tier 3 runs on both RHCOS9.8 and RHCOS10.2
    clusters. Component teams validate their specific feature areas in child STPs.

- [x] **Upgrade Testing** — Out of scope for this 4.22 STP.
  - *Details:* Upgrade testing (4.22 → 5.0, EUS-to-EUS, etc.) will be covered in the 5.0 .
    Not planned as part of 4.22 testing.

- [x] **Dependencies** — Testing is blocked on specific deliverables from other teams.
  - *Details:* QE DevOps team must provide a stable dual-stream cluster provisioning option
      (RHCOS9.8 + RHCOS10.2 workers in the same cluster).

- [x] **Cross Integrations** — Other SIGs must create a child STP extending this one to cover adhoc testing for OCPSTRAT-1150.
  - *Details:* sig-network, sig-storage, sig-iuo, and sig-infra must each create child STPs
    specifying their Tier 1, Tier 2 and Tier 3 test coverage on RHCOS10.2 nodes and dual-stream
    clusters. Each SIG is responsible for triaging failures in their area and filing bugs
    with clear RHCOS-version attribution.

**Infrastructure**

- [x] **Cloud Testing**
  — For 4.22 Tech Preview we must test with FIPS enabled.
  - Use cloud setup if it supports FIPS enabled

#### **3. Test Environment**

- **FIPS:** enabled

- **Cluster Topology:**
  - **Dual-stream testing:** High-availability (HA) bare-metal cluster required —
    3-control-plane / 3-worker minimum, with at least 1 worker running RHCOS10.2 alongside
    RHCOS9.8 workers. SNO or compact clusters are not supported for dual-stream testing.
  - **RHCOS10.2-only testing:** Standard 3-control-plane / 3-worker bare-metal cluster with all
    workers on RHCOS10.2.

- **OCP & OpenShift Virtualization Version(s):** OCP 4.22 with CNV 4.22

- **CPU Virtualization:** Standard (VT-x / AMD-V enabled)

- **Compute Resources:** Standard

- **Special Hardware:** N/A

- **Storage:** ocs-storagecluster-ceph-rbd-virtualization

- **Network:** Standard

- **Required Operators:** Standard.

- **Platform:** Bare metal (dual-stream cluster provisioned by DevOps QE tooling).

- **Special Configurations:** Dual-stream cluster. DevOps QE
  provides tooling to deploy this configuration.

#### **3.1. Testing Tools & Frameworks**

- **Test Framework:**
  - Standard (openshift-virtualization-tests) for RHCOS 10.2
  - For OCPSTRAT-1150 (dual-stream): See Automation Testing in Section II.2 for the decision and rationale.

- **CI/CD:** Two cluster configurations are required, both available from CNV 4.22:
  - **RHCOS10.2-only cluster:** Existing Tier 1, Tier 2 and Tier 3 jobs run by all component teams.
  - **Dual-stream cluster :** Manual ad-hoc live migration runs by component teams.

- **Other Tools:** N/A

#### **4. Entry Criteria**

The following conditions must be met before testing can begin:

- [x] Requirements and design documents are **approved and merged**
  (recommendation doc sign-offs from PM, Engineering, Platform, Product Ops confirmed)
- [x] Test environment can be **set up and configured** (dual-stream cluster available via
  QE DevOps tooling)
- [x] **CNV 4.22 builds based on RHCOS 9.8 are available and validated**
- [x] QE DevOps dual-stream cluster provisioning is validated and available

#### **5. Risks**

**Timeline/Schedule**

- **Risk:** None identified.
  - **Mitigation:** N/A
  - *Estimated impact on schedule:* N/A

**Test Coverage**

- **Risk:** None identified.
  - **Mitigation:** All intentional coverage exclusions are documented in Out of Scope (Section II.1).
    Each participating SIG covers their own feature area via child STPs.
  - *Areas with reduced coverage:* N/A

**Test Environment**

- **Risk:**
  - HA resource shortage.
  - RDU2 to RDU3 migration, bare metal cluster outages.
  - Deploying RHCOS 10.2 and Dual-Stream cluster on cloud fails (PSI, IBM-BM or other clouds with FIPS fails).
  - QE DevOps dual-stream cluster provisioning tooling may be unavailable or unstable, blocking
    Tier 1, Tier 2 and Tier 3 runs.
  - **Mitigation:**
    - Use bare metal cluster with FIPS enabled.
    - Engage QE DevOps team early to confirm dual-stream cluster availability timeline. Identify a
      fallback of manually provisioning a mixed-node cluster if tooling is delayed. Track
      provisioning readiness as an entry criterion.
  - *Missing or unavailable environments:* Dual-stream cluster if QE DevOps tooling is not ready.
  - *Sign-off:* Martin Tessun / 2026-05-13

**Untestable Aspects**

- **Risk:** None identified.
  - **Mitigation:** N/A
  - *Reason untestable and mitigation approach:* N/A

**Resource Constraints**

- **Risk:** Manual ad-hoc testing for dual-stream live migration scenarios (OCPSTRAT-1150) requires
  component team bandwidth through OCP 5.2, until Tier 2 automation (Option 3) is completed.
  - **Mitigation:** Each participating SIG allocates time for ad-hoc runs in their test cycle.
    Tier 2 automation will be added progressively. See Automation Testing in Section II.2 for the
    full options analysis and decision rationale.
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


- **[CNV-81251](https://redhat.atlassian.net/browse/CNV-81251)** — As a VM operator, I want to live-migrate VMs between RHCOS9.8 and
  RHCOS10.2 worker nodes within the same cluster so my workloads remain available during
  node maintenance.
  - *Test Scenario:* [Tier 2] **Scenario 1** — VM created on an RHCOS9.8 worker node is live-migrated
    to an RHCOS10.2 worker node without disruption; then migrate back to RHCOS9.8 without disruption.
  - *Priority:* P1

- **[CNV-81251](https://redhat.atlassian.net/browse/CNV-81251)** — As a VM operator, I want to live-migrate VMs between RHCOS9.8 and
  RHCOS10.2 worker nodes within the same cluster so my workloads remain available during
  node maintenance.
  - *Test Scenario:* [Tier 2] **Scenario 2** — VM created on an RHCOS10.2 worker node is live-migrated
    to an RHCOS9.8 worker node without disruption; then migrate back to RHCOS10.2 without disruption.
  - *Priority:* P1

---

### **IV. Sign-off and Approval**

This Software Test Plan requires approval from the following stakeholders:

- **Reviewers:**
  - QE Members (sig-iuo): @OhadRevah
  - QE Members (sig-network): @azhivovk
  - QE Members (sig-storage): @jpeimer @kshvaika
  - QE Members (sig-virt): @dshchedr @vsibirsk @SamAlber
  - QE Members (sig-infra): @geetikakay @RoniKishner
- **Approvers:**
  - QE Architect: [Ruth Netser](@rnetser)
  - Principal Developer (sig-virt): Luboslav Pivarc @xpivarc
  - Product Manager: [Martin Tessun] @mtessun
