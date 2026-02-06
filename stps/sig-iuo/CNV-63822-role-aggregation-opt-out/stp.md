# Openshift-virtualization-tests Test plan

## **Role Aggregation Opt-Out - Quality Engineering Plan**

### **Metadata & Tracking**

| Field                  | Details                                                 |
|:-----------------------|:--------------------------------------------------------|
| **Enhancement(s)**     | KubeVirt PR #16350 (pending merge)                      |
| **Feature in Jira**    | [CNV-63822](https://issues.redhat.com/browse/CNV-63822) |
| **Jira Tracking**      | [CNV-63822](https://issues.redhat.com/browse/CNV-63822) |
| **QE Owner(s)**        | Ramon Lobillo (@rlobillo)                               |
| **Owning SIG**         | sig-iuo (Install, Upgrade, Operators)                   |
| **Participating SIGs** | TBD                                                     |
| **Current Status**     | Draft - Waiting for upstream merge                      |

---

### **I. Motivation and Requirements Review (QE Review Guidelines)**

#### **1. Requirement & User Story Review Checklist**

| Check                                  | Done | Details/Notes                                                                   | Comments                                              |
|:---------------------------------------|:-----|:--------------------------------------------------------------------------------|:------------------------------------------------------|
| **Review Requirements**                | [x]  | Admins can disable automatic kubevirt.io role aggregation via config             | Per CNV-63822 epic acceptance criteria               |
| **Understand Value**                   | [x]  | Enables strict RBAC: users must explicitly get kubevirt.io permissions           | Required for regulated/multi-tenant environments      |
| **Customer Use Cases**                 | [x]  | Regulated environments, multi-tenant clusters, security-hardened deployments     | Aligns with enterprise RBAC requirements              |
| **Testability**                        | [ ]  | Blocked until KubeVirt PR #16350 merges; need to confirm field name and API     | Cannot implement tests without actual implementation  |
| **Acceptance Criteria**                | [x]  | (1) Config disables aggregation, (2) Users blocked without RoleBinding, (3) RoleBinding grants access | Clearly defined in CNV-63822                         |
| **Non-Functional Requirements (NFRs)** | [x]  | Security (RBAC hardening), Backward Compatibility (default unchanged)            | Upgrade and docs coverage required                    |

#### **2. Technology and Design Review**

| Check                            | Done | Details/Notes                                                                   | Comments                                              |
|:---------------------------------|:-----|:--------------------------------------------------------------------------------|:------------------------------------------------------|
| **Developer Handoff/QE Kickoff** | [ ]  | Pending KubeVirt PR #16350 merge; will schedule once API is confirmed           | Need exact config field name and allowed values       |
| **Technology Challenges**        | [x]  | RBAC testing requires unprivileged user (HTPasswd IdP already supported)        | Using existing test infrastructure                    |
| **Test Environment Needs**       | [x]  | Standard OCP + CNV cluster with HTPasswd IdP for unprivileged user testing      | No special hardware required                          |
| **API Extensions**               | [ ]  | KubeVirt spec field TBD; likely under spec.configuration per PR #16350          | Cannot finalize until upstream merged                 |
| **Topology Considerations**      | [x]  | Feature is cluster-scoped (KubeVirt CR level), topology-independent             | Works on all topologies (standard, SNO, compact)      |

[Kubevirt VEP](https://github.com/kubevirt/enhancements/issues/160)


### **II. Software Test Plan (STP)**

#### **1. Scope of Testing**

**In Scope:**
- Verify role aggregation can be disabled via KubeVirt config
- Unprivileged users cannot access kubevirt resources without explicit RoleBinding (when disabled):
- Explicit RoleBindings (admin, edit, view) grant access correctly
  - admin = create/delete/modify VM/VMI
  - edit = modify VM/VMIs but cannot create/delete
  - view = Only read VM/VMIs
- Default behavior (role aggregation enabled) remains unchanged
- Configuration preserved across CNV z-stream upgrades
- Backward compatibility validation

**Out of Scope:**
- Testing OpenShift RBAC infrastructure itself (OCP responsibility)
- Performance impact of RBAC enforcement
- ARM64/s390x architectures (RBAC is architecture-independent)
- External IdP testing beyond HTPasswd (feature is IdP-agnostic)

#### **2. Testing Goals**

- [ ] Manual functional test scenarios
- [ ] Automate functional test scenarios for CI integration
- [ ] Verify backward compatibility
- [ ] Verify configuration remains between upgrades

#### **3. Non-Goals (Testing Scope Exclusions)**

| Non-Goal                                                  | Rationale                                                                     | PM/ Lead Agreement |
|:----------------------------------------------------------|:------------------------------------------------------------------------------|:-------------------|
| Full regression with opt-out enabled from fresh install   | Deferred to post-GA manual testing if time-constrained                        | [ ] TBD            |
| External IdP compatibility (LDAP, Active Directory)       | RBAC is IdP-agnostic; HTPasswd testing validates core logic                   | [ ] TBD            |
| Multi-tenant cluster scale testing (100+ users)           | RBAC overhead negligible; functional correctness sufficient at smaller scale  | [ ] TBD            |
| Testing kubevirt.io:migrate role aggregation              | kubevirt.io:migrate has no aggregate labels (not a Kubernetes base role); already requires explicit RoleBinding regardless of strategy | [ ] TBD            |

#### **4. Test Strategy**

##### **A. Types of Testing**

| Item (Testing Type)            | Applicable (Y/N or N/A) | Comments |
|:-------------------------------|:------------------------|:---------|
| Functional Testing             | Y                       | Core focus: verify RBAC opt-out behavior |
| Automation Testing             | Y                       | All tests automated in openshift-virtualization-tests |
| Performance Testing            | N/A                     | RBAC checks have negligible impact |
| Security Testing               | Y                       | Feature IS a security enhancement; tested via functional scenarios |
| Usability Testing              | N/A                     | Configuration via YAML, no UI component |
| Compatibility Testing          | Y                       | Backward compatibility with default behavior |
| Regression Testing             | Y                       | Ensure existing CNV functionality unaffected |
| Upgrade Testing                | Y                       | Verify config preserved across z-stream upgrades |
| Backward Compatibility Testing | Y                       | Default state (opt-out disabled) unchanged |

##### **B. Potential Areas to Consider**

| Item                   | Description                                                                 | Applicable (Y/N or N/A) | Comment |
|:-----------------------|:----------------------------------------------------------------------------|:------------------------|:--------|
| **Dependencies**       | Depends on KubeVirt PR #16350 (upstream) and HCO integration (downstream)   | Y                       | Blocker until upstream merged |
| **Monitoring**         | Feature doesn't require metrics/alerts                                      | N/A                     | RBAC enforcement is transparent |
| **Cross Integrations** | All kubevirt features requiring VM interaction affected by RBAC changes     | Y                       | Verify cluster-admin retains all permissions |
| **UI**                 | Configuration via HCO/KubeVirt CR YAML only                                 | N/A                     | No UI component |

#### **5. Test Environment**

| Environment Component                         | Configuration                  | Specification Examples                                             |
|:----------------------------------------------|:-------------------------------|:-------------------------------------------------------------------|
| **Cluster Topology**                          | Standard or SNO                | Feature works on all topologies; multi-node preferred              |
| **OCP & OpenShift Virtualization Version(s)** | OCP 4.21+ with CNV 4.22        | Target version where feature introduced                            |
| **CPU Virtualization**                        | N/A                            | Not relevant for RBAC testing                                      |
| **Compute Resources**                         | Standard cluster resources     | Minimum per worker: 4 vCPUs, 16GB RAM                              |
| **Special Hardware**                          | N/A                            | No special hardware required                                       |
| **Storage**                                   | Any RWX storage class          | ocs-storagecluster-ceph-rbd-virtualization                         |
| **Network**                                   | Default (OVN-Kubernetes)       | No special network requirements                                    |
| **Required Operators**                        | OpenShift Virtualization       | Standard CNV installation                                          |
| **Platform**                                  | Any supported platform         | Prefer AWS or bare-metal for CI integration                        |
| **Special Configurations**                    | HTPasswd identity provider     | REQUIRED: Must have HTPasswd IdP with unprivileged user            |

#### **5.5. Testing Tools & Frameworks**

| Category           | Tools/Frameworks                                       |
|:-------------------|:-------------------------------------------------------|
| **Test Framework** | ginkgo for tier1 tests inside kubevirt repo            |
|                    | pytest with openshift-virtualization-tests for tier2 tests    |
| **CI/CD**          | Standard Jenkins CI lanes, no special pipeline needed  |
| **Other Tools**    | Existing unprivileged_client fixture and RBAC utilities |

#### **6. Entry Criteria**

- [ ] KubeVirt PR #16350 **merged** (upstream blocking dependency)
- [ ] HCO downstream implementation **complete** (field integrated into HCO CR)
- [ ] Requirements and design documents approved
- [ ] Test environment configured with HTPasswd IdP
- [ ] Developer Handoff/QE Kickoff meeting completed

#### **7. Risks and Limitations**

| Risk Category        | Specific Risk for This Feature                          | Mitigation Strategy                                     | Status     |
|:---------------------|:--------------------------------------------------------|:--------------------------------------------------------|:-----------|
| Timeline/Schedule    | KubeVirt PR #16350 not yet merged; blocks test implementation | Monitor PR status weekly; prepare test infrastructure in parallel | [x] Active |
| Test Coverage        | Cannot exhaustively test all RBAC role combinations     | Test critical paths (all 4 roles); focus on acceptance criteria | [ ]        |
| Test Environment     | Requires HTPasswd IdP setup; not all CI lanes support it | Use existing infrastructure; verify CI environment available | [ ]        |
| Dependencies         | Blocking: PR #16350 merge. Soft: HCO downstream implementation | Track upstream progress; coordinate with HCO team       | [x] Active |
| Untestable Aspects   | Limited to HTPasswd; cannot test LDAP/AD/OAuth         | RBAC logic is IdP-agnostic; HTPasswd validation sufficient | [ ]        |

#### **8. Known Limitations**

- Feature implementation pending KubeVirt PR #16350 merge (no implementation to test yet)
- Testing scope limited to HTPasswd identity provider
- Upgrade testing from CNV <4.21 only tests "feature not available" → "feature available" scenario
- Cannot test production-scale multi-tenant environments (functional correctness sufficient at smaller scale)

---

### **III. Test Scenarios & Traceability**

| Requirement ID           | Requirement Summary                                  | Test Scenario(s)                                                        | Test Type(s)     | Priority |
|:-------------------------|:-----------------------------------------------------|:------------------------------------------------------------------------|:-----------------|:---------|
| KubeVirt PR #16350       | `RoleAggregationStrategy config should keep aggregate labels when RoleAggregationStrategy is nil`                       || tier1 automation | P0       |
| KubeVirt PR #16350       | `RoleAggregationStrategy configuration should keep aggregate labels when RoleAggregationStrategy is AggregateToDefault`        || tier1 automation | P0       |
| KubeVirt PR #16350       | `RoleAggregationStrategy configuration should create ClusterRole without aggregate labels when RoleAggregationStrategy is Manual` ||  tier1 auto   | P0       |
| KubeVirt PR #16350       | `RoleAggregationStrategy configuration should remove aggregate labels from existing ClusterRole when strategy changes to Manual`  ||  tier1 auto   | P0       |
| CNV-63822 (Acceptance 1) | Feature can be enabled via config                | Set `spec.roleAggregation.enabled: False` in HCO CR; verify config persists | tier2 automation | P0       |
| CNV-63822 (Acceptance 2) | Unprivileged user blocked without RoleBinding    | Verify ForbiddenError when unprivileged user lacks binding                  | tier2 automation | P0       |
| CNV-63822 (Acceptance 3) | Explicit RoleBinding grants access               | Verify new user gains access after RoleBinding created                      | tier2 automation | P0       |
| CNV-63822 (Acceptance 4) | Feature can be disabled via config               | Verify new user gains access after feature disabling                        | tier2 automation | P0       |
| Default Behavior         | Role aggregation enabled by default (Back. Comp.)| Verify default config enables automatic role aggregation                    | Regression       | P0       |
| Y Upgrade Testing        | Config preserved on Y upgrades (4.21.z → 4.22.0) | Test upgrade path preserves configuration and RBAC behavior                 | Regression       | P0       |
| Role Testing             | All 3 kubevirt.io roles work correctly           | Test admin/edit/view roles independently                                    | tier2 - manual   | P1       |
| Multi-Namespace          | RBAC enforced per-namespace                      | User with RoleBinding in NS-A cannot access NS-B                            | tier2 - manual   | P1       |
| Upgrade Testing          | Config preserved across z-stream upgrades        | Test upgrade path preserves configuration and RBAC behavior [BLOCKED]       | manual           | P1       |


**Note:** tier2 automation tests can be inspired on *migrate* clusterRole tests: [test_migration_rights.py](https://github.com/RedHatQE/openshift-virtualization-tests/blob/main/tests/virt/cluster/migration_and_maintenance/rbac_hardening/test_migration_rights.py)

---

### **IV. Sign-off and Approval**

This Software Test Plan requires approval from the following stakeholders:

* **Reviewers:**
  - [QE Lead / @rnester]
  - [sig-iuo representative / @orenc1 @hmeir @OhadRevah albarker-rh]

* **Approvers:**
  - [QE Manager / @kmajcher-rh @fabiand]
  - [Product Manager / TBD]

**Review Status:**
- [X] Draft complete
- [ ] QE team reviewed
- [ ] Dev/Arch reviewed (pending KubeVirt PR #16350 merge)
- [ ] PM approved
- [ ] Ready for implementation
