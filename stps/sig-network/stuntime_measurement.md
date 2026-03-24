# Openshift-virtualization-tests Test plan

## **Stuntime Measurement - Quality Engineering Plan**

### **Metadata & Tracking**

| Field                  | Details                                                                |
|:-----------------------|:-----------------------------------------------------------------------|
| **Enhancement(s)**     | -                                                                      |
| **Feature in Jira**    | N/A - Not a new feature. Work is tracked under the Epic (see Jira Tracking).|
| **Jira Tracking**      | https://issues.redhat.com/browse/CNV-72773                             |
| **QE Owner(s)**        | Anat Wax (awax@redhat.com)                                                              |
| **Owning SIG**         | sig-network                                                            |
| **Participating SIGs** | sig-network                                                            |

**Document Conventions:**
- **Stuntime:** VM downtime (unreachability window) during live migration - the connectivity gap from first connectivity loss to first recovery.
- **KCS:** [Knowledge Centered Support](https://access.redhat.com/articles/7031392).

### **Feature Overview**

Customers need predictable network traffic connectivity downtime during live migration. Detecting regressions in stuntime is required.
The feature defines and measures VM stuntime during live migration and establishes a baseline with a pass/fail threshold. Testing scope is defined in Section II below.

---

### **I. Motivation and Requirements Review (QE Review Guidelines)**

#### **1. Requirement & User Story Review Checklist**

| Check                                  | Done | Details/Notes                                                                                                                                       | Comments |
|:---------------------------------------|:-----|:----------------------------------------------------------------------------------------------------------------------------------------------------|:---------|
| **Review Requirements**                | [x]  | Measure network connectivity stuntime during live migration so that these values can be shared with customers per release. |          |
| **Understand Value**                   | [x]  | Network connectivity downtime measurements and their resulting values provide users a set of expectations for VM downtime during live migration and allow comparison of OCP-V with other virtualization solutions. |          |
| **Customer Use Cases**                 | [x]  | Users performing live migrations need reference values to understand expected network connectivity downtime. Users evaluating OCP-V also need stuntime data to compare with other virtualization solutions. |          |
| **Testability**                        | [x]  | Testable by measuring the time period in which network traffic is lost. |          |
| **Acceptance Criteria**                | [x]  | Measured values are published as reference data per release; they are not a formal SLA commitment across all environments and conditions. A per-scenario threshold exists for regression detection. | These values are best-effort; actual stuntime may vary across different environments. |
| **Non-Functional Requirements (NFRs)** | [x]  | Measured stuntime will be documented in a KCS or a Red Hat blog post. |          |

#### **2. Known Limitations**

No known technical limitations. All scope exclusions are documented in the Out-of-Scope table.

#### **3. Technology and Design Review**

| Check                            | Done | Details/Notes                                                                                                                                           | Comments |
|:---------------------------------|:-----|:--------------------------------------------------------------------------------------------------------------------------------------------------------|:---------|
| **Developer Handoff/QE Kickoff** | [x]  | Conducted meetings to align on testing strategy. |          |
| **Technology Challenges**        | [x]  | Stuntime is sensitive to network workload and infrastructure, so measured values may vary across different labs and environments. A relatively stable setup environment is needed to provide as stable results as possible. |          |
| **Test Environment Needs**       | [x]  | Default OCP-V deployment on Bare Metal, with worker nodes that have multiple NICs for secondary networks. |          |
| **API Extensions**               | [x]  | No new or modified APIs.                                                                                                 |          |
| **Topology Considerations**      | [x]  | Limited to BM clusters with secondary NICs. |          |

---

### **II. Software Test Plan (STP)**

#### **1. Scope of Testing**

Tests measure network connectivity stuntime during live migration. Connectivity is measured on secondary networks (Linux bridge and OVN localnet). The test scenarios reflect different migration paths and ARP/CNI behavior during migration. Since stuntime can differ depending on who initiates traffic, both traffic initiation directions will be measured. All scenarios are measured for both IPv4 and IPv6. Measurements are taken on an idle cluster with a minimal VM setup; results reflect expected stuntime under those conditions.

**Testing Goals**

- **[P0]** VM with secondary network connected to a Linux bridge:
  - Verify stuntime stays within the per-scenario threshold for the following variants:
    - IP Family: IPv4, IPv6
    - Connectivity initiator: Client (initiator), Server (listener).
    - Migration paths (relative to the node hosting the connectivity peer):
      - Initially running on the same node.
      - Initially running on different nodes, reaching the same node.
      - Always running on different nodes.
- **[P0]** VM with secondary network connected to OVN localnet:
  - Verify stuntime stays within the per-scenario threshold for the following variants:
    - IP Family: IPv4, IPv6
    - Connectivity initiator: Client (initiator), Server (listener).
    - Migration paths (relative to the node hosting the connectivity peer):
      - Initially running on the same node.
      - Initially running on different nodes, reaching the same node.
      - Always running on different nodes.

**Out of Scope (Testing Scope Exclusions)**

| Out-of-Scope Item                                 | Rationale                                                                                      | PM/ Lead Agreement |
|:--------------------------------------------------|:----------------------------------------------------------------------------------------------|:-------------------|
| Default pod network / masquerade                  | To save capacity, stuntime coverage is limited to the vast majority of client scenarios - secondary networks. | [x] phoracek@redhat.com (03/2026) |
| Other secondary CNIs (e.g. SR-IOV, other plugins) | Stuntime coverage is limited to the vast majority of client scenarios - Linux bridge and OVN localnet. | [x] phoracek@redhat.com (03/2026) |
| Worst-case SLA guarantee | The tests assert a per-scenario threshold for regression detection, but this threshold is not a public SLA commitment. These values are best-effort; Different HW, load, and network conditions may influence stuntime. | [x] phoracek@redhat.com (03/2026) |
| General performance testing | Testing is scoped to a stable environment with no performance or scale focus. High-density stress testing and measuring stuntime under heavy cluster load are out of scope. | [x] phoracek@redhat.com (03/2026) |
| Upgrade | These tests will not be added to the upgrade CI lane. Baseline is measured on an idle cluster; the upgrade lane runs with heavier load and is out of scope for the current epic. | [x] phoracek@redhat.com (03/2026) |
| localnet over br-ex | To save team capacity, coverage focuses on the recommended configuration: dedicated NICs for VM network. | [x] phoracek@redhat.com (03/2026) |
| Cloud / virtualized environments (AWS, etc.) | Stuntime measurement is BM-only. Localnet and bridge CNI are not supported on public cloud. | [x] phoracek@redhat.com (03/2026) |


#### **2. Test Strategy**

| Item                           | Description                                                                                                                                                  | Applicable (Y/N or N/A) | Comments                                                                                  |
|:-------------------------------|:-------------------------------------------------------------------------------------------------------------------------------------------------------------|:------------------------|:------------------------------------------------------------------------------------------|
| Functional Testing             | Validates that the feature works according to specified requirements and user stories                                                                        | N                       | Stuntime measurement is a performance baseline test; there is no functional feature to validate.                                                                                           |
| Automation Testing             | Ensures test cases are automated for continuous integration and regression coverage                                                                          | Y                       |                                                                                           |
| Performance Testing            | Validates feature performance meets requirements (latency, throughput, resource usage)                                                                       | N                       | Not a performance/scale test. Performance and scale testing is explicitly out of scope (see Out-of-Scope table).                                                       |
| Security Testing               | Verifies security requirements, RBAC, authentication, authorization, and vulnerability scanning                                                              | N/A                     | Not applicable to stuntime measurement.                                                   |
| Usability Testing              | Validates user experience, UI/UX consistency, and accessibility requirements. Does the feature require UI? If so, ensure the UI aligns with the requirements | N                       | No UI planned for this feature.                                                          |
| Compatibility Testing          | Ensures feature works across supported platforms, versions, and configurations                                                                               | N                       | No new feature or configuration introduced; stuntime measurement runs on a fixed BM environment and does not require cross-configuration validation.                                                                                           |
| Regression Testing             | Verifies that new changes do not break existing functionality                                                                                                | Y                       | Regression is detected via the per-scenario threshold shared between all versions.                                                               |
| Upgrade Testing                | Validates upgrade paths from previous versions, data migration, and configuration preservation                                                               | N                       | Not added to the upgrade CI lane. Regression detection across versions is handled by the per-scenario threshold shared between all versions.                                                               |
| Backward Compatibility Testing | Ensures feature maintains compatibility with previous API versions and configurations                                                                        | N/A                    | The stuntime is a performance measurement addition, not a product feature. No APIs or configurations are introduced that users depend on.                                                                           |
| Dependencies                   | Dependent on deliverables from other components/products? Identify what is tested by which team.                                                             | N                       | Uses existing migration and secondary network topologies.                                     |
| Cross Integrations             | Does the feature affect other features/require testing by other components? Identify what is tested by which team.                                           | N                       | Tests are self-contained and do not affect other features.                                                                                           |
| Monitoring                     | Does the feature require metrics and/or alerts?                                                                                                              | N                       | Stuntime measurement does not introduce new metrics or alerts.                                                                                           |
| Cloud Testing                  | Does the feature require multi-cloud platform testing? Consider cloud-specific features.                                                                     | N/A                    | Tests run on BM; official stuntime data from BM only.                                             |

#### **3. Test Environment**

| Environment Component                         | Configuration | Specification Examples                                                                 |
|:----------------------------------------------|:--------------|:---------------------------------------------------------------------------------------|
| **Cluster Topology**                          |     Multi-node dual-stack BM cluster         |  Three workers to support all migration paths. |
| **OCP & OpenShift Virtualization Version(s)** |         v4.22     | -                                                                                      |
| **CPU Virtualization**                        |       N/A             | Agnostic                   |
| **Compute Resources**                         |        N/A       | Agnostic                                                          |
| **Special Hardware**                          |       N/A        | Agnostic                                                                                       |
| **Storage**                                   | N/A          | Agnostic                                            |
| **Network**                                   |   IPv4 + IPv6 / Multi-NIC            | -                                                                                      |
| **Required Operators**                        |          NMState     | -                                                                                      |
| **Platform**                                  |       Bare Metal        | -                                                                                      |
| **Special Configurations**                    |       N/A        | Agnostic                                                                               |

#### **3.1. Testing Tools & Frameworks**

| Category           | Tools/Frameworks                                                                                  |
|:-------------------|:--------------------------------------------------------------------------------------------------|
| **Test Framework** | - |
| **CI/CD**          | -                                                                                                 |
| **Other Tools**    | **Additional Information:** Measurement tool: `ping`. For a deeper dive into the design decisions and rationale, see [CNV-78675](https://issues.redhat.com/browse/CNV-78675). |

#### **4. Entry Criteria**

The following conditions must be met before testing can begin:

- [X] Test environment can be **set up and configured** (see Section II.3 - Test Environment)

#### **5. Risks**

| Risk Category        | Specific Risk for This Feature                                                                 | Mitigation Strategy                                                                                    | Status |
|:---------------------|:-----------------------------------------------------------------------------------------------|:-------------------------------------------------------------------------------------------------------|:-------|
| Timeline/Schedule    | N/A                                                                                            | -                                                                                                                                                                                                  | [x]    |
| Test Coverage        | Regressions in default pod network or other CNIs (e.g. SR-IOV) may go undetected.             | Coverage limited to bridge and localnet by design. Explicit out-of-scope notes. Can be extended later if requirements change.                                                                      | [x]    |
| Test Environment     | Stuntime values may vary across environments (different labs, HW, network config); even on an idle BM, results from one setup may not reflect another. | Baseline will be derived from repeated runs on a stable BM setup; the threshold defined will be based on a multiplier to absorb variance. | [x]    |
| Untestable Aspects   | Stuntime under performance and scale conditions (high cluster load, concurrent migrations) is unknown. | Results reflect idle cluster with minimal VM setup only; explicitly out of scope.                                                                                                                  | [x]    |
| Upgrade              | A regression introduced during an OCP-V upgrade may go undetected since tests do not run in the upgrade CI lane. | The per-scenario threshold is shared between all versions; if stuntime regresses post-upgrade, it will be caught when the tests run on the new version.                                            | [x]    |
| Resource Constraints | N/A                                                                                            | -                                                                                                                                                                                                  | [x]    |
| Dependencies         | N/A                                                                                            | -                                                                                                                                                                                                  | [x]    |

---

### **III. Test Scenarios & Traceability**

Scenario Variants: See **Testing Goals** (Section II.1) for details.

| Requirement ID | Requirement Summary | Test Scenario(s) | Tier | Priority |
|:---------------|:--------------------|:-----------------|:-----|:---------|
| CNV-72773 | Measure VM stuntime over Linux bridge | Verify stuntime during live migration over Linux bridge within the per-scenario threshold | Tier 2 | P0 |
| CNV-72773 | Measure VM stuntime over OVN localnet | Verify stuntime during live migration over OVN localnet within the per-scenario threshold | Tier 2 | P0 |

---

### **IV. Sign-off and Approval**

This Software Test Plan requires approval from the following stakeholders:

* **Reviewers:**
  - QE Architect (OCP-V): Ruth Netser (@rnetser)
  - QE Members (OCP-V): Yossi Segev (@yossisegev), Asia Zhivov Khromov (@azhivovk), Sergei Volkov (@servolkov)
* **Approvers:**
  - QE Architect (OCP-V): Ruth Netser (@rnetser)
  - Product Manager/Owner: Ronen Sde-Or (ronen@redhat.com), Petr Horacek (@phoracek)
  - Principal Developer: Edward Haas (@EdDev)
