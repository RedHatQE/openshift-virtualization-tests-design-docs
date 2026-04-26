# Openshift-virtualization-tests Test plan

## **Dual-Stream RHCOS Support (RHCOS9.8 + RHCOS10.2 Worker Nodes) — Quality Engineering Plan**

### **Metadata & Tracking**

- **Enhancement(s):** https://redhat.atlassian.net/browse/VIRTSTRAT-83
- **Epic Tracking:** https://redhat.atlassian.net/browse/CNV-49964
  <!-- Tasks must be created to block the feature -->
- **QE Owner(s):** Akriti Gupta
- **Readiness Tracking:** [RHCOS 10 Readiness Tracking](https://docs.google.com/spreadsheets/d/1mD1mVkiIqrdyaDIqB0fhRgmywWp4sI9OEy0IVBD6pDc/edit?gid=0#gid=0)
- **Owning SIG:** sig-virt
- **Participating SIGs:** sig-virt, sig-network, sig-storage, sig-iuo, sig-infra

> **This is a Parent STP.** It defines the overall dual-stream RHCOS testing strategy and cross-cutting
> requirements. Each participating SIG is expected to create a child STP that extends this document with
> SIG-specific test scenarios. Child STPs should reference this parent STP and must not duplicate content
> defined here.

**Document Conventions:**

- **RHCOS9.8:** Red Hat CoreOS 9.8 based control plane + worker nodes (el9 kernel / kernelspace).
- **RHCOS10.2:** Red Hat CoreOS 10.2 based control plane + worker nodes (el10 kernel / kernelspace).
- **el9 userspace:** CNV component images (e.g., virt-launcher, virt-controller) built
  on RHEL 9.8. This is the userspace shipped for OCP 4.22 through 5.2.
- **el10 userspace:** CNV component images built on RHEL 10.x. Supported from OCP 5.3.
- **Dual-stream cluster:** OCP containing a mix of RHCOS9.8 and RHCOS10.2 control plane + worker nodes in
  a single release and cluster.
- **ks:** kernelspace (RHCOS control plane + worker node OS).
- **us:** userspace (CNV component image OS).

### **Feature Overview**

The decided approach for OCP Virtualization (CNV) is **Switch userland mid-lifecycle while dual kernel
is supported (virt9 userland on el9 and el10 kernels)**, as outlined in the related documents.
- This strategy, reviewed and signed off by PM, Engineering, Platform (RHEL Virt), and Product Operations.

The primary goal for CNV 4.22 is to run Tier 1, Tier 2 and Tier 3 test suites against
RHCOS10.2-only cluster and a dual-stream cluster (RHCOS9.8 + RHCOS10.2), generate test results, triage
and file bugs.

Transition to RHEL10:
- Note: During RHEL8 to RHEL9 OCP transition, both Userspace and KernelSpace moved at the same time to RHEL9.
- This is not the case with RHEL10.
- We are not moving to RHEL10  at the same time for both Userspace and Kernelspace in OCP 5.0.
  - First is only RHCOS10 ( Kernelspace/Controlplane+Worker Nodes) supported from 5.0.
    - In October 2026
  - RHEL10 supported ( in userspace/ CNV Images ) only from 5.3 ( Testing to start from 5.2 - Once CNV CI Release builds it. )
    - In October 2027, only after a gap of 1 year.

**Timeline note:**
- RHCOS 10 supported in 5.0 - October 2026.
- RHCOS9.x support in CNV continues through OCP 5.2 (EoL May 2032).
- CNV Images based on 10.4 in 5.3 - October 2027

---

### **I. Motivation and Requirements Review (QE Review Guidelines)**

#### **1. Requirement & User Story Review Checklist**

- [x] **Review Requirements**
  - *Key D/S requirements reviewed:*
    - CNV 4.22: RHCOS9.8 is GA/default.
    - RHCOS10.2 is Tech Preview.
    - CNV images are el9.8-based for both node types.
    - All CNV 4.22.0 release checklist testing must happen with RHCOS9.8.
    - CNV component teams must do in-depth testing with RHCOS10.2 in 4.22 by running Tier1, Tier 2 and Tier 3 jobs,
      triaging failures and filing bugs for CNV, OCP, RHEL.
    - OCPSTRAT-1150: [Tech Preview] Support two major versions of RHCOS in a single OCP release and cluster.
      - Note: Component teams to discuss internally within their teams about various scenarios
      - VM live migration must succeed across RHCOS9.8 ↔ RHCOS10.2 worker nodes.
        - Successful LiveMigration of VM ( el9.8 userspace) from RHCOS9.8 to RHCOS10.2 backto RHCOS9.8
          i.e VM created first on RHCOS9.8 Worker Node
        - Successful LiveMigration of VM ( el9.8 userspace) from RHCOS10.2 to RHCOS9.8 backto RHCOS10.2
          i.e VM created first on RHCOS10.2 Worker Node

- [x] **Understand Value and Customer Use Cases**
  - *Feature value to customers:* Customers can move their existing RHCOS 9 worker nodes to RHCOS 10
    incrementally as part of the OCP 5.x minor upgrades, ensuring workload compatibility during the transition.
  - *Customer use cases:*
    - As a cluster administrator, I want to add RHCOS10.2 worker nodes to my existing
      cluster.
    - As a VM operator, I want to live-migrate VMs from RHCOS9.8 worker nodes to RHCOS10.2 worker
      nodes.
    - As a platform team, I want to validate that CNV behaves correctly on both RHCOS9.8 and RHCOS10.2
      nodes.

- [x] **Acceptance Criteria**
  - *Acceptance criteria:*
    - Tier 1, Tier 2 and Tier 3 test suites run successfully against an RHCOS10.2-only cluster and a dual-stream
      cluster for every component team; failures are triaged and bugs filed with RHCOS-version
      attribution.
    - **RHCOS10.2 test failures are not a blocker for CNV 4.22**
      - RHCOS10.2 is Tech Preview in 4.22.
      - All testing should happen with FIPS enabled
      - However, unresolved bugs **will block component readiness for CNV 5.0 GA**.
    - CNV components run and report healthy status on both RHCOS9.8 and RHCOS10.2 worker nodes.
    - For OCPSTRAT-1150:
      - All testing should happen with FIPS enabled
      - A VM running on an RHCOS9.8 worker node can be live-migrated to an RHCOS10.2 worker node and back.
      - A VM running on an RHCOS10.2 worker node can be live-migrated to an RHCOS9.8 worker node and back.

- [x] **Non-Functional Requirements (NFRs)**
  - *Applicable NFRs:*
    - **Performance:** N/A
    - **Security:** N/A
    - **Monitoring/Observability:** N/A
    - **Scalability:** N/A
    - **UI:** N/A
    - **Documentation:** Release notes must document RHCOS10.2 Tech Preview status in 4.22, GA
      status timeline.
    - **Compatibility:** N/A


#### **2. Technology and Design Review**

- [x] **Developer Handoff/QE Kickoff**
  - *Key takeaways and concerns:*
    - The adopted approach (el9 userspace on both RHCOS 9.8 and RHCOS 10.2) was reviewed and signed off
      by PM, Engineering, Platform (RHEL Virt), and Product Operations per the [recommendation
      document](https://docs.google.com/document/d/1MMNmUbhGPymnJDrbqbcq_KGi_FN9jxTvAdnzed1cwWw/edit?tab=t.0#heading=h.54747tl9m7p8). QE must align test strategy to this confirmed approach.
    - CNV component teams are rquested to discuss dual-stream(mixed cluster) scenarios during Epic grooming and
      update their own STPs accordingly (this parent STP provides the framework).
    - Testing with RHCOS10.2 can only start after CNV 4.22 builds move to using el9.8 base images.
      We are good to start even with CNV images based on el9.8 beta.
    - Most bugs found during 4.22 RHCOS10.2 Tech Preview testing must be resolved before 5.0 GA.

- [x] **Technology Challenges**
  - *Identified challenges:*
    - **CNV compatibility on RHCOS 10.2 :** Running el9.8-based CNV images on a RHCOS 10.2
      is a new configuration that may surface unexpected failures. Running Tier1, Tier 2, Tier 3 and ad-hoc testing[TBD]
      is the primary mechanism for finding these issues.
    - **Dual-stream cluster provisioning:** Clusters with mixed RHCOS9.8 and RHCOS10.2 worker
      nodes require specific provisioning tooling. DevOps QE to provide this capability.
    - **Bug triage complexity:** Failures found on RHCOS10.2 must be clearly attributed to the
      RHCOS 10.2 vs. pre-existing issues. This requires reproduction steps on both RHCOS9.8 and RHCOS10.2 to isolate root cause.

  - *Impact on testing approach:*
    - Tier1, Tier 2, Tier 3 and ad-hoc testing[TBD] on an RHCOS10.2-only cluster and on a dual-stream cluster are both mandatory for
      all component teams — this is the primary testing vehicle.
    - Live migration across RHCOS versions must be tested explicitly.
    - Bug filing must tag RHCOS version and CNV build version for clear bug reproduction.
    - Entry criteria must include confirmation of el9.8-based CNV builds.

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

### **II. Software Test Plan (STP)**

#### **1. Scope of Testing**

**Testing Goals**

<!-- Ordered P0 → P1 → P2 -->

- **[P0]** Run Tier1, Tier 2 and Tier 3 test suites against an RHCOS10.2-only worker-node cluster; triage all
  failures to identify regressions introduced by the el10 kernel. Required for sig-virt and
  all other participating SIGs (via child STPs).
- **[P1]** Run Tier 1, Tier 2 and Tier 3 test suites against a dual-stream cluster (RHCOS9.8 + RHCOS10.2
  workers); triage failures to distinguish cross-kernel issues from pre-existing bugs.
  Required for sig-virt and all other participating SIGs (via child STPs).
- **[P1]** For OCPSTRAT-1150:
  - Note: Component teams to discuss internally within their teams about various scenarios
  - VM live migration must succeed across RHCOS9.8 ↔ RHCOS10.2 worker nodes.
    - Successful LiveMigration of VM ( el9.8 userspace) from RHCOS9.8 to RHCOS10.2 backto RHCOS9.8
          i.e VM created first on RHCOS9.8 Worker Node
    - Successful LiveMigration of VM ( el9.8 userspace) from RHCOS10.2 to RHCOS9.8 backto RHCOS10.2
          i.e VM created first on RHCOS10.2 Worker Node
- **[P1]** File and track all RHCOS10.2 failures found during 4.22 testing. Per-SIG readiness status is
  tracked in the [RHCOS 10 Readiness Tracking](https://docs.google.com/spreadsheets/d/1mD1mVkiIqrdyaDIqB0fhRgmywWp4sI9OEy0IVBD6pDc/edit?gid=0#gid=0) spreadsheet.

**Release Readiness Note:**

RHCOS10.2 test failures are **not a blocker for OCP 4.22** (as Tech Preview). They **will block
readiness for CNV 5.0** — for 4.22, all e2e and functional tests must run on RHCOS9.8 by
default for release checklist.

**Out of Scope (Testing Scope Exclusions)**

- **el10.x userspace (CNV component images based on RHEL 10.x)**
  - *Rationale:* CNV userspace stays on el9.8 through OCP 5.2 per the approved [recommendation
      document](https://docs.google.com/document/d/1MMNmUbhGPymnJDrbqbcq_KGi_FN9jxTvAdnzed1cwWw/edit?tab=t.0#heading=h.54747tl9m7p8).
    el10.x userspace testing is a separate effort targeting 5.3. It is explicitly not in scope of this STP.
  - *PM/Lead Agreement:* [Name/Date]


**Test Limitations**

- **Dual-stream cluster provisioning depends on QE DevOps tooling.** The ability to deploy
  a cluster with mixed RHCOS9.8 and RHCOS10.2 worker nodes relies on tooling provided by the
  QE DevOps team. If this tooling is unavailable or unstable, the dual-stream migration
  scenarios cannot be executed.
  - *Sign-off:* [Name/Date]


#### **2. Test Strategy**

**Functional**

- [x] **Functional Testing**
  - Validates that the full CNV feature set operates correctly on RHCOS10.2-only clusters
  - *Details:* The primary mechanism is running existing Tier1, Tier 2 and Tier 3 test suites and triaging failures.
  - All other SIGs (sig-network, sig-storage, sig-iuo, sig-infra) must document
    their Tier1, Tier 2 and Tier 3 Test results and bugs in their own Jira Stories.
  - For OCPSTRAT-1150: Validates that the full CNV feature set operates correctly on dual-stream clusters, with el9.8 userspace.
    - Note: Component teams to discuss internally within their teams about various scenarios
    - VM live migration must succeed across RHCOS9.8 ↔ RHCOS10.2 worker nodes.
      - Successful LiveMigration of VM ( el9.8 userspace) from RHCOS9.8 to RHCOS10.2 backto RHCOS9.8
          i.e VM created first on RHCOS9.8 Worker Node
      - Successful LiveMigration of VM ( el9.8 userspace) from RHCOS10.2 to RHCOS9.8 backto RHCOS10.2
          i.e VM created first on RHCOS10.2 Worker Node

- [ ] **Automation Testing**
  - For RHCOS 10.2 , no new automation tests are needed
  - *Details:* The strategy relies on running existing Tier 1, Tier 2 and Tier 3 test suites against RHCOS 10.2
  - For OCPSTRAT-1150:
    - Option 0: Only have mixed clusters and run Tier 1, Tier 2 and Tier 3, neither ad-hoc scenarios nor RHCOS 9.8 and RHCOS 10.2 only clusters
    - Option 1: Manually run adhoc scenarios, by component teams after discussions within the team for scenarios.
    - Option 2: Run all the existing LM tests using a marker periodically on the cluster ( No T2 repo changes )
    - Option 3: Add support in Tier2 repo for a VM provisioning to a specific node using affinity and migrate to specific nodes to simulate the 2 LM adhoc scenarios, only for the purpose of catching any bugs.
    - Option 4: Start with Option 1 or 2 and then complete Option 3 eventually, as we need to support till 2032.
    - **sig-virt decision:** As per team discussions, sig-virt will go with Option 4.

- [x] **Regression Testing** — sig-virt and all participating SIGs must run Tier1, Tier 2 and Tier 3
  regression
  - On RHCOS10.2-only cluster.
    - *Details:* The strategy relies on running existing Tier 1, Tier 2 and Tier 3 test suites against RHCOS 10.2
  - For OCPSTRAT-1150:
    - Option 0: Only have mixed clusters and run Tier 1, Tier 2 and Tier 3, neither ad-hoc scenarios nor RHCOS 9.8 and RHCOS 10.2 only clusters
    - Option 1: Manually run adhoc scenarios, by component teams after discussions within the team for scenarios.
    - Option 2: Run all the existing LM tests using a marker periodically on the cluster ( No T2 repo changes )
    - Option 3: Add support in Tier2 repo for a VM provisioning to a specific node using affinity and migrate to specific nodes to simulate the 2 LM adhoc scenarios, only for the purpose of catching any bugs.
    - Option 4: Start with Option 1 or 2 and then complete Option 3 eventually, as we need to support till 2032.
    - **sig-virt decision:** As per team discussions, sig-virt will go with Option 4.

**Non-Functional**

- [x] **Performance Testing** — N/A

- [ ] **Scale Testing** — N/A

- [x] **Security Testing** — N/A

- [ ] **Usability Testing** — N/A

- [x] **Monitoring** — N/A

**Integration & Compatibility**

- [x] **Compatibility Testing** — CNV must remain compatible with both RHCOS9.8 and RHCOS10.2
  across the supported version range (4.22 through 5.2).
  - *Details:* Compatibility is validated through Tier 1, Tier 2 and Tier 3 runs on both RHCOS9.8 and RHCOS10.2
    clusters. Component teams validate their specific feature areas in child STPs.

- [ ] **Upgrade Testing** — Out of scope for this 4.22 STP.
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

- [ ] **Cloud Testing**
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

- **OCP & OpenShift Virtualization Version(s):** OCP 4.22 with CNV 4.22 (el9.8-based builds),
  RHCOS10.2 as Tech Preview.

- **CPU Virtualization:** Standard (VT-x / AMD-V enabled)

- **Compute Resources:** Standard

- **Special Hardware:** N/A

- **Storage:** Standard

- **Network:** Standard

- **Required Operators:** Standard.

- **Platform:** Bare metal (dual-stream cluster provisioned by DevOps QE tooling).

- **Special Configurations:** Mixed RHCOS9.8 + RHCOS10.2 worker node cluster (dual-stream). DevOps QE
  provides tooling to deploy this configuration.

#### **3.1. Testing Tools & Frameworks**

- **Test Framework:**
  - Standard (openshift-virtualization-tests, pytest) for RHCOS 10.2
  - Dual-Stream For OCPSTRAT-1150:
    - Option 0: Only have mixed clusters and run Tier 1, Tier 2 and Tier 3, neither ad-hoc scenarios nor RHCOS 9.8 and RHCOS 10.2 only clusters
    - Option 1: Manually run adhoc scenarios, by component teams after discussions within the team for scenarios.
    - Option 2: Run all the existing LM tests using a marker periodically on the cluster ( No T2 repo changes )
    - Option 3: Add support in Tier2 repo for a VM provisioning to a specific node using affinity and migrate to specific nodes to simulate the 2 LM adhoc scenarios, only for the purpose of catching any bugs.
    - Option 4: Start with Option 1 or 2 and then complete Option 3 eventually, as we need to support till 2032.
    - **sig-virt decision:** As per team discussions, sig-virt will go with Option 4.

- **CI/CD:** Two cluster configurations are required, both available from CNV 4.22:
  - **RHCOS10.2-only cluster:** Existing Tier 1, Tier 2 and Tier 3 jobs run by all component teams.
  - **Dual-stream cluster (RHCOS9.8 + RHCOS10.2):**As per team discussions, sig-virt will go with Option 4.

- **Other Tools:** N/A

#### **4. Entry Criteria**

The following conditions must be met before testing can begin:

- [ ] Requirements and design documents are **approved and merged**
  (recommendation doc sign-offs from PM, Engineering, Platform, Product Ops confirmed)
- [ ] Test environment can be **set up and configured** (dual-stream cluster available via
  QE DevOps tooling)
- [x] **CNV 4.22 builds are confirmed to use el9.8 as the userspace base**
- [ ] RHCOS10.2 worker node images are available and stable in the target OCP release build
- [ ] QE DevOps dual-stream cluster provisioning is validated and available
- [ ] Component SIG teams have been briefed and are preparing child STPs

#### **5. Risks**

**Timeline/Schedule**

- **Risk:** N/A

**Test Environment**

- **Risk:**
  - HA resource shortage
  - RDU2 to RDU3 migration, bare metsl cluster outrages
  - Deploying RHCOS 10.2 and Dual-Stream cluster on cloud fails (PSI, IBM-BM or other clouds with FIPS fails).
  - QE DevOps dual-stream cluster provisioning tooling may be unavailable or
  unstable, blocking Tier 1, Tier 2 and Tier 3 runs.
  - **Mitigation:**
    - use bare metal cluster with FIPS enabled.
    - Engage QE DevOps team early to confirm dual-stream cluster availability
    timeline. Identify a fallback of manually provisioning a mixed-node cluster if tooling
    is delayed. Track provisioning readiness as an entry criterion.
  - *Missing resources or infrastructure:* Dual-stream cluster if QE DevOps tooling is
    not ready.
  - *Sign-off:* [Name/Date]

**Resource Constraints**

- **Risk:**
  - Dual-Stream For OCPSTRAT-1150:
    - Option 0: Only have mixed clusters and run Tier 1, Tier 2 and Tier 3, neither ad-hoc scenarios nor RHCOS 9.8 and RHCOS 10.2 only clusters
    - Option 1: Manually run adhoc scenarios, by component teams after discussions within the team for scenarios.
    - Option 2: Run all the existing LM tests using a marker periodically on the cluster ( No T2 repo changes )
    - Option 3: Add support in Tier2 repo for a VM provisioning to a specific node using affinity and migrate to specific nodes to simulate the 2 LM adhoc scenarios, only for the purpose of catching any bugs.
    - Option 4: Start with Option 1 or 2 and then complete Option 3 eventually, as we need to support till 2032.
    - Pros:
      - For Option 1: Manual work, no automation changes needed.
      - For Option 2: We run LM tests periodically, but no automation changes are needed.
      - For Option 3: Cover the adhoc scenarios for mixed clusters.
      - For Option 4: Option 3, but with time.
    - Cons:
      - For Option 1: Manual task till 5.2, EoL is 2032
      - For Option 2: Might not always catch bugs, even if running jobs multiple times on the mixed cluster, without any modifications.
      - For Option 3: Might need to update lots of automation with low ROI ( 5.0 to 5.2 only) and then revert changes in 5.3.
      - For Option 4: Manual work, initially.

**Other**

- **Risk:** N/A

---

### **III. Test Scenarios & Traceability**


- **[CNV-81251](https://redhat.atlassian.net/browse/CNV-81251)** — As a VM operator, I want to live-migrate VMs between RHCOS9.8 and
  RHCOS10.2 worker nodes within the same cluster so my workloads remain available during
  node maintenance.
  - *Test Scenario:* [Tier 2 and Tier 3] **Scenario 1** — VM (el9.8 userspace) created on an RHCOS9.8
    worker node is live-migrated to an RHCOS10.2 worker node; verify the VM remains running;
    then migrate back to RHCOS9.8 and verify the same.
  - *Priority:* P1

- **[CNV-81251](https://redhat.atlassian.net/browse/CNV-81251)** — As a VM operator, I want to live-migrate VMs between RHCOS9.8 and
  RHCOS10.2 worker nodes within the same cluster so my workloads remain available during
  node maintenance.
  - *Test Scenario:* [Tier 2 and Tier 3] **Scenario 2** — VM (el9.8 userspace) created on an RHCOS10.2
    worker node is live-migrated to an RHCOS9.8 worker node; verify the VM remains running; then
    migrate back to RHCOS10.2 and verify the same.
  - *Priority:* P1

---

### **IV. Sign-off and Approval**

This Software Test Plan requires approval from the following stakeholders:

- **Reviewers:**
  - QE Members (sig-iuo): @hmeir @OhadRevah @rlobillo @albarker-rh
  - Dev Members (sig-iuo): @orenc1
  - QE Members (sig-network): @yossisegev @Anatw @EdDev @servolkov @azhivovk
  - Dev Members (sig-network):
  - QE Members (sig-storage): @duyanyan @jpeimer @josemacassan @kgoldbla @dalia-frank @Ahmad-Hafe @kshvaika @ema-aka-young @acinko-rh
  - Dev Members (sig-storage):
  - QE Members (sig-virt): @dshchedr @vsibirsk @SamAlber
  - Dev Members (sig-virt):
  - QE Members (sig-infra): @geetikakay @RoniKishner
  - Dev Members (sig-infra):
- **Approvers:**
  - QE Architect: [Ruth Netser](@rnetser)
  - Principal Developer (sig-virt): Luboslav Pivarc @xpivarc
  - Product Manager: [Martin Tessun] @mtessun
