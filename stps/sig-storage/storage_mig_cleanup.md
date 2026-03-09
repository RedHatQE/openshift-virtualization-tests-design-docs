# Openshift-virtualization-tests Test plan

## Storage migration cleanup - Quality Engineering Plan

### **Metadata & Tracking**

| Field                  | Details                                                 |
|:-----------------------|:--------------------------------------------------------|
| **Enhancement(s)**     | N/A                                                     |
| **Feature in Jira**    | [CNV-73509](https://issues.redhat.com/browse/CNV-73509) |
| **Jira Tracking**      | [CNV-81263](https://issues.redhat.com/browse/CNV-81263) |
| **QE Owner(s)**        | Yan Du                                                  |
| **Owning SIG**         | sig-storage                                             |
| **Participating SIGs** | sig-storage                                             |
| **Current Status**     | draft                                                   |

**Document Conventions (if applicable):** [Define acronyms or terms specific to this document]

### **Feature Overview**

<!-- Provide a brief (2-4 sentences) description of the feature being tested.
Include: what it does, why it matters to customers, and key technical components. -->

The storage migration cleanup feature allows the system to optionally decommission migration plans and legacy PVCs upon successful completion.

<!-- [Template Note: Remove this section if not applicable]
- [KubeVirt Enhancements](https://github.com/kubevirt/enhancements/tree/main/veps)
- [OCP Enhancements](https://github.com/openshift/enhancements/tree/master/enhancements) -->

---

### **I. Motivation and Requirements Review (QE Review Guidelines)**


#### **1. Requirement & User Story Review Checklist**

<!-- **How to complete this checklist:**
1. **Done column**: Mark [x] when the check is complete
2. **Details/Notes column**: Summary of the topic (e.g., list key requirements, describe customer value, note acceptance criteria)
3. **Comments column**: Document any concerns, gaps, or follow-up items needed -->

| Check                                  | Done | Details/Notes                                                                                                                                                                           | Comments |
|:---------------------------------------|:-----|:----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:---------|
| **Review Requirements**                | [x]  | Reviewed the relevant requirements.                                                                                                                                                     |          |
| **Understand Value**                   | [x]  | Confirmed clear user stories and understood.  <br/>Understand the difference between U/S and D/S requirements<br/> **What is the value of the feature for RH customers**.               |          |
| **Customer Use Cases**                 | []   | Ensured requirements contain relevant **customer use cases**.                                                                                                                           |          |
| **Testability**                        | []   | Confirmed requirements are **testable and unambiguous**.                                                                                                                                |          |
| **Acceptance Criteria**                | []   | Ensured acceptance criteria are **defined clearly** (clear user stories; D/S requirements clearly defined in Jira).                                                                     |          |
| **Non-Functional Requirements (NFRs)** | []   | Confirmed coverage for NFRs, including Performance, Security, Usability, Downtime, Connectivity, Monitoring (alerts/metrics), Scalability, Portability (e.g., cloud support), and Docs. |          |

#### **2. Technology and Design Review**

<!-- **How to complete this checklist:**
1. **Done column**: Mark [x] when the review is complete
2. **Details/Notes column**: Summary of the item (e.g., list technology challenges, special environment needs, significant API changes)
3. **Comments column**: Note any blockers, risks, or items requiring follow-up -->

| Check                            | Done | Details/Notes                                                                                                                                           | Comments |
|:---------------------------------|:-----|:--------------------------------------------------------------------------------------------------------------------------------------------------------|:---------|
| **Developer Handoff/QE Kickoff** | [x]  | A meeting where Dev/Arch walked QE through the design, architecture, and implementation details. **Critical for identifying untestable aspects early.** |          |
| **Technology Challenges**        | [x]  | Identified potential testing challenges related to the underlying technology.                                                                           |          |
| **Test Environment Needs**       | []   | Determined necessary **test environment setups and tools**.                                                                                             |          |
| **API Extensions**               | []   | Reviewed new or modified APIs and their impact on testing.                                                                                              |          |
| **Topology Considerations**      | []   | Evaluated multi-cluster, network topology, and architectural impacts.                                                                                   |          |


### **II. Software Test Plan (STP)**


#### **1. Scope of Testing**

<!-- Briefly describe what will be tested. The scope must **cover functional and non-functional requirements**.
Must ensure user stories are included and aligned to downstream user stories from Section I. -->

**Testing Goals**

<!-- Define specific, measurable testing objectives for this feature using **SMART criteria**
(Specific, Measurable, Achievable, Relevant, Time-bound).
Each goal should tie back to requirements from Section I and be independently verifiable.

**How to Define Good Testing Goals:**
- **Specific**: Clearly state what will be tested (not "test the feature" but "validate VM live migration
  with SR-IOV networks")
- **Measurable**: Define quantifiable success criteria (e.g., "95% of VM migrations complete within xxx seconds")
- **Achievable**: Realistic given resources and timeline
- **Relevant**: Directly supports feature acceptance criteria and user stories
- **Verifiable**: Can be objectively confirmed as complete

**Priority Levels:**
- **P0**: Blocking GA - must be complete before release
- **P1**: High priority - required for full feature coverage
- **P2**: Nice-to-have - can be deferred if timeline constraints exist -->

<!-- **Example - Functional Goals**:
- **[P0]** Verify VM live migration completes successfully with new network binding plugin across
  OVN-Kubernetes and secondary networks
- **[P1]** Validate hotplug/hotunplug operations work with new storage class without VM restart
- **[P0]** Confirm RBAC permissions model correctly restricts non-admin users from accessing
  cluster-wide configuration API
- **[P2]** Validate new metrics with real-time VM performance data (CPU, memory, network, disk I/O)

**Example - Quality Goals**:
- **[P0]** Verify VM live migration completes in <30 seconds for VMs with <8GB memory
  (performance baseline from VEP-XXXX)
- **[P1]** Confirm feature operates correctly in disconnected/air-gapped environments with local
  image registry
- **[P0]** Validate zero data loss during live migration under network latency up to 100ms

**Example - Integration Goals**:
- **[P0]** Verify backward compatibility: upgrade from OCP 4.19 to 4.20 preserves existing VM
  configurations without manual intervention
- **[P0]** Confirm interoperability with OpenShift Service Mesh when VMs use Istio sidecar injection
- **[P1]** Test integration with OpenShift monitoring stack: metrics appear in Prometheus,
  alerts fire correctly in Alertmanager -->

- **[P0]** Verify source DataVolume/PVC will be remained after a migration completed when set retentionPolicy to keepSource
- **[P0]** Verify source DataVolume/PVC will be cleaned up after a migration completed when set retentionPolicy to deleteSource
- **[P1]** Verify RetentionPolicy is not set, default behavior is keepSource
- **[P2]** Verify the source DataVolume/PVC behavior when migration is failed

**Out of Scope (Testing Scope Exclusions)**

<!-- Explicitly document what is **out of scope** for testing.
**Critical:** All out-of-scope items require explicit stakeholder agreement to prevent "I assumed you were testing
that" issues; each out-of-scope item must have PM/Lead sign-off.

- Items without stakeholder agreement are considered **risks** and must be escalated
- Review the items during Developer Handoff/QE Kickoff meeting

**Note:** Replace example rows with your actual out-of-scope items. -->

| Out-of-Scope Item             | Rationale               | PM/ Lead Agreement |
|:------------------------------|:------------------------|:-------------------|
| Other storage migration tests | covered in 4.21 already | [ ] Name/Date      |
| Storage migration UI tests    | covered in UI team      | [ ] Name/Date      |

#### **2. Test Strategy**

<!-- The following test strategy considerations must be reviewed and addressed. Mark "Y" if applicable,
"N/A" if not applicable (with justification in Comments). Empty cells indicate incomplete review. -->

| Item                           | Description                                                                                                                                                  | Applicable (Y/N or N/A) | Comments                                                                                       |
|:-------------------------------|:-------------------------------------------------------------------------------------------------------------------------------------------------------------|:------------------------|:-----------------------------------------------------------------------------------------------|
| Functional Testing             | Validates that the feature works according to specified requirements and user stories                                                                        | Y                       | Functional testing with retentionPolicy field defined in spec                                  |
| Automation Testing             | Ensures test cases are automated for continuous integration and regression coverage                                                                          | Y                       | Ensures test cases are automated, might be added to the existing storage class migration tests |
| Performance Testing            | Validates feature performance meets requirements (latency, throughput, resource usage)                                                                       | N                       | No performance testing currently                                                               |
| Security Testing               | Verifies security requirements, RBAC, authentication, authorization, and vulnerability scanning                                                              | N                       | Not security relevant                                                                          |
| Usability Testing              | Validates user experience, UI/UX consistency, and accessibility requirements. Does the feature require UI? If so, ensure the UI aligns with the requirements | N                       | will be covered by UI team                                                                     |
| Compatibility Testing          | Ensures feature works across supported platforms, versions, and configurations                                                                               | N                       | No compatibility testing currently                                                             |
| Regression Testing             | Verifies that new changes do not break existing functionality                                                                                                | N                       | Ensure storage migration functionality will be affected by new implemented cleanup code        |
| Upgrade Testing                | Validates upgrade paths from previous versions, data migration, and configuration preservation                                                               | N                       | Not Upgrade relevant                                                                           |
| Backward Compatibility Testing | Ensures feature maintains compatibility with previous API versions and configurations                                                                        | N                       | No Compatibility testing currently                                                             |
| Dependencies                   | Dependent on deliverables from other components/products? Identify what is tested by which team.                                                             | N                       | No Dependencies                                                                                             |
| Cross Integrations             | Does the feature affect other features/require testing by other components? Identify what is tested by which team.                                           | N                       | Will not affect other components                                                               |
| Monitoring                     | Does the feature require metrics and/or alerts?                                                                                                              | N                       | No Monitoring testing currently                                                                |
| Cloud Testing                  | Does the feature require multi-cloud platform testing? Consider cloud-specific features.                                                                     | N                       | Not multi-cloud platform testing relevant                                                      |

#### **3. Test Environment**

<!-- **Note:** "N/A" means explicitly not applicable. Cannot leave empty cells. -->

| Environment Component                         | Configuration | Specification Examples                      |
|:----------------------------------------------|:--------------|:--------------------------------------------|
| **Cluster Topology**                          |               | No specific Cluster Topology required       |
| **OCP & OpenShift Virtualization Version(s)** |               | OCP 4.22 with OpenShift Virtualization 4.22 |
| **CPU Virtualization**                        |               | Standard                                    |
| **Compute Resources**                         |               | Standard                                    |
| **Special Hardware**                          |               | N/A                                         |
| **Storage**                                   |               | Standard                                    |
| **Network**                                   |               | Default network                             |
| **Required Operators**                        |               | migration controller                        |
| **Platform**                                  |               | PSI                                         |
| **Special Configurations**                    |               | N/A                                         |

#### **3.1. Testing Tools & Frameworks**

<!-- Document any **new or additional** testing tools, frameworks, or infrastructure required specifically
for this feature. **Note:** Only list tools that are **new** or **different** from standard testing infrastructure.
Leave empty if using standard tools. -->

| Category           | Tools/Frameworks |
|:-------------------|:-----------------|
| **Test Framework** |                  |
| **CI/CD**          |                  |
| **Other Tools**    |                  |

#### **4. Entry Criteria**

The following conditions must be met before testing can begin:

- [ ] Requirements and design documents are **approved and merged**
- [ ] Test environment can be **set up and configured** (see Section II.3 - Test Environment)


#### **5. Risks**

<!-- Document specific risks for this feature. If a risk category is not applicable, mark as "N/A" with
justification in mitigation strategy.

**Note:** Empty "Specific Risk" cells mean this must be filled. "N/A" means explicitly not applicable
with justification. -->

| Risk Category        | Specific Risk for This Feature | Mitigation Strategy | Status |
|:---------------------|:-------------------------------|:--------------------|:-------|
| Timeline/Schedule    | N/A                            |                     | [ ]    |
| Test Coverage        | N/A                            |                     | [ ]    |
| Test Environment     | N/A                            |                     | [ ]    |
| Untestable Aspects   | N/A                            |                     | [ ]    |
| Resource Constraints | N/A                            |                     | [ ]    |
| Dependencies         | N/A                            |                     | [ ]    |
| Other                | N/A                            |                     | [ ]    |

#### **6. Known Limitations**

<!-- Document any known limitations, constraints, or trade-offs in the feature implementation or testing approach.

**Examples:**
- Feature does not support IPv6 (only IPv4)
- No support for ARM64 architecture in this release -->


---

### **III. Test Scenarios & Traceability**

<!-- This section links requirements to test coverage, enabling reviewers to verify all requirements are
tested. -->

<!-- **Requirement ID:**
- Use Jira issue key (e.g., CNV-12345)
- Each row should trace back to a specific testable requirement in Jira

**Requirement Summary:** Brief description from the Jira issue (user story format preferred) -->

| Requirement ID | Requirement Summary                                | Test Scenario(s)                                                  | Tier   | Priority |
|:---------------|:---------------------------------------------------|:------------------------------------------------------------------|:-------|:---------|
| TBD            | retentionPolicy: keepSource                        | Verify source DV/PVC will be remained after migration completed   | Tier 2 | P0       |
| TBD            | retentionPolicy: deleteSource                      | Verify source DV/PVC will be cleaned up after migtation completed | Tier 2 | P0       |
| TBD            | retentionPolicy: None                              | Verify default behavior when retentionPolicy is not set           | Tier 2 | P1       |
| TBD            | Migration failed with retentionPolicy keepSource   | Verify source DV/PVC will be remained after migration failed      | Tier 2 | P2       |
| TBD            | Migration failed with retentionPolicy deleteSource | Verify source DV/PVC will be cleaned up after migration failed    | Tier 2 | P2       |


---

### **IV. Sign-off and Approval**

This Software Test Plan requires approval from the following stakeholders:

* **Reviewers:**
  - [Name / @github-username]
  - [Name / @github-username]
* **Approvers:**
  - [Name / @github-username]
  - [Name / @github-username]

