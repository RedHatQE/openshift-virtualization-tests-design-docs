# Openshift-virtualization-tests Test plan

## **Role Aggregation Opt-Out - Quality Engineering Plan**

### **Metadata & Tracking**

| Field                  | Details                                                 |
|:-----------------------|:--------------------------------------------------------|
| **Enhancement(s)**     | [Kubevirt VEP](https://github.com/kubevirt/enhancements/issues/160) |
| **Feature in Jira**    | [CNV-50792](https://issues.redhat.com/browse/CNV-50792) |
| **Jira Tracking**      | [CNV-63822](https://issues.redhat.com/browse/CNV-63822) |
| **QE Owner(s)**        | Ramon Lobillo (@rlobillo), Alex Barker (@albarker-rh)   |
| **Owning SIG**         | sig-iuo (Install, Upgrade, Operators)                   |
| **Participating SIGs** | sig-ui                                                  |
| **Current Status**     | Draft                                                   |

---

### **I. Motivation and Requirements Review (QE Review Guidelines)**

#### **1. Requirement & User Story Review Checklist**

| Check                                  | Done | Details/Notes                                                                   | Comments                                              |
|:---------------------------------------|:-----|:--------------------------------------------------------------------------------|:------------------------------------------------------|
| **Review Requirements**                | [x]  | As a cluster-admin I want to decide which users will have access to the virtualization in the cluster. Not all project-admins should have this access but only the eligible ones            | Per CNV-50792 feature request |
| **Understand Value**                   | [x]  | A cluster-admin wants to control which users has access to view/create/edit openshift virtualization resources on a given namespace | Per CNV-50792 feature request |
| **Customer Use Cases**                 | [x]  | * multi-tenant clusters|different namespaces are used to allow different workloads and prevent unallowed usage of workload that the tenant is not eligible to us|
|                                        |      | * Resources usage control|cluster admin wants to get a request to allow a specific user to create VMs and Storage|
| **Testability**                        | [ ]  | Blocked until HCO API modification is available; need to confirm field name and API     | Cannot implement tests without actual implementation  |
| **Acceptance Criteria**                | [x]  | (1) Config disables aggregation, (2) Users blocked without RoleBinding, (3) RoleBinding grants access | Defined in CNV-63822 epic |
| **Non-Functional Requirements (NFRs)** | [x]  | Security (RBAC hardening), Backward Compatibility (default unchanged)            | Upgrade and docs coverage required                    |

#### **2. Technology and Design Review**

| Check                            | Done | Details/Notes                                                                   | Comments                                              |
|:---------------------------------|:-----|:--------------------------------------------------------------------------------|:------------------------------------------------------|
| **Developer Handoff/QE Kickoff** | [x]  |||
| **Technology Challenges**        | [x]  | N/A ||
| **Test Environment Needs**       | [x]  | Standard OCP + CNV cluster with HTPasswd IdP for unprivileged user testing      | No special hardware required                          |
| **API Extensions**               | [ ]  | hco spec field TBD;                                                             | Cannot finalize until feature is completely implemented    |
| **Topology Considerations**      | [x]  | Feature is cluster-scoped (KubeVirt CR level), topology-independent             | Works on all topologies (standard, SNO, compact)      |



### **II. Software Test Plan (STP)**

#### **1. Scope of Testing**

**Testing Goals**
- [P0] Verify opt-out role aggregation can be enabled via hyperconvergeds.hco.kubevirt.io config
- [P0] Unprivileged users cannot access kubevirt resources without explicit RoleBinding when feature is enabled
- [P0] Explicit RoleBindings (admin, edit, view) grant access correctly
- [P0] Verify opt-out role aggregation can be disabled via hyperconvergeds.hco.kubevirt.io config

**Backward compatibility Goals**

- [P0] Default behavior (role aggregation enabled) remains unchanged
- [P0] Default behaviour is preserved across CNV z-stream upgrades

**Out of Scope:**

| Out-of-Scope Item                                         | Rationale                                                                     | PM/ Lead Agreement |
|:----------------------------------------------------------|:------------------------------------------------------------------------------|:-------------------|
| Testing OpenShift RBAC infrastructure itself              | OCP responsibility                                                            | [ ] TBD            |
| Testing all rules within kubevirt.io roles                | kubevirt.io:{admin,edit,view} clusterroles contains rules that are not affected by this feature | [ ] TBD            |
| External IdP compatibility (LDAP, Active Directory)       | RBAC is IdP-agnostic; HTPasswd testing validates core logic                   | [ ] TBD            |
| Multi-tenant cluster scale testing (100+ users)           | RBAC overhead negligible; functional correctness sufficient at smaller scale  | [ ] TBD            |
| Testing kubevirt.io:migrate role aggregation              | Already covered on tier2 regression testing: [test_migration_rights.py](https://github.com/RedHatQE/openshift-virtualization-tests/blob/main/tests/virt/cluster/migration_and_maintenance/rbac_hardening/test_migration_rights.py) | [ ] TBD            |


#### **2. Test Strategy**

| Item                           | Description                                                                                                                                                  | Applicable (Y/N or N/A) | Comments |
|:-------------------------------|:-------------------------------------------------------------------------------------------------------------------------------------------------------------|:------------------------|:---------|
| Functional Testing             | Validates that the feature works according to specified requirements and user stories                                                                        | Y                       | Core focus: verify RBAC opt-out behaviour |
| Automation Testing             | Ensures test cases are automated for continuous integration and regression coverage                                                                          | Y                       |          |
| Performance Testing            | Validates feature performance meets requirements (latency, throughput, resource usage)                                                                       | N/A                     |          |
| Security Testing               | Verifies security requirements, RBAC, authentication, authorization, and vulnerability scanning                                                              | Y                       | Feature is a security enhancement |
| Usability Testing              | Validates user experience, UI/UX consistency, and accessibility requirements. Does the feature require UI? If so, ensure the UI aligns with the requirements | Y                       | [CNV-80935](https://issues.redhat.com/browse/CNV-80935) |
| Compatibility Testing          | Ensures feature works across supported platforms, versions, and configurations                                                                               | Y                       | default behaviour will not change |
| Regression Testing             | Verifies that new changes do not break existing functionality                                                                                                | Y                       |          |
| Upgrade Testing                | Validates upgrade paths from previous versions, data migration, and configuration preservation                                                               | Y                       |          |
| Backward Compatibility Testing | Ensures feature maintains compatibility with previous API versions and configurations                                                                        | Y                       |          |
| Dependencies                   | Dependent on deliverables from other components/products? Identify what is tested by which team.                                                             | N                       |          |
| Cross Integrations             | Does the feature affect other features/require testing by other components? Identify what is tested by which team.                                           | Y                       | UI       |
| Monitoring                     | Does the feature require metrics and/or alerts?                                                                                                              | N                       |          |
| Cloud Testing                  | Does the feature require multi-cloud platform testing? Consider cloud-specific features.                                                                     | N                       |          |


#### **3. Test Environment**

| Environment Component                         | Configuration                  | Specification Examples                                             |
|:----------------------------------------------|:-------------------------------|:-------------------------------------------------------------------|
| **Cluster Topology**                          | Standard or SNO                | Feature works on all topologies; multi-node preferred              |
| **OCP & OpenShift Virtualization Version(s)** | OCP 4.22 with CNV 4.22         | Target version where feature introduced                            |
| **CPU Virtualization**                        | N/A                            | Not relevant for RBAC testing                                      |
| **Compute Resources**                         | Standard cluster resources     | Minimum per worker: 4 vCPUs, 16GB RAM                              |
| **Special Hardware**                          | N/A                            | No special hardware required                                       |
| **Storage**                                   | Any RWX storage class          | ocs-storagecluster-ceph-rbd-virtualization                         |
| **Network**                                   | Default (OVN-Kubernetes)       | No special network requirements                                    |
| **Required Operators**                        | OpenShift Virtualization       | Standard CNV installation                                          |
| **Platform**                                  | Any supported platform         |                                                                    |
| **Special Configurations**                    | HTPasswd identity provider     | REQUIRED: Must have HTPasswd IdP with unprivileged user            |

#### **3.1. Testing Tools & Frameworks**

| Category           | Tools/Frameworks |
|:-------------------|:-----------------|
| **Test Framework** |                  |
| **CI/CD**          |                  |
| **Other Tools**    |                  |

#### **4. Entry Criteria**

- [X] KubeVirt PR #16350 **merged**
- [ ] HCO downstream implementation **complete** (field integrated into HCO CR)
- [ ] Requirements and design documents approved
- [ ] Developer Handoff/QE Kickoff meeting completed

#### **5. Risks**

| Risk Category        | Specific Risk for This Feature                          | Mitigation Strategy                                     | Status     |
|:---------------------|:--------------------------------------------------------|:--------------------------------------------------------|:-----------|
| IU adaptations    | The feature description mentions IU changes that are still pending to concrete | Discussion started and will be tracked with IU team | [x] Active |
| Test Coverage        | Cannot exhaustively test all RBAC role combinations     | Test critical paths (all 4 roles); focus on acceptance criteria | [ ]        |
| Dependencies         | HCO downstream implementation | Track  progress and coordinate with HCO team       | [x] Active |
| Untestable Aspects   | Limited to HTPasswd; cannot test LDAP/AD/OAuth         | RBAC logic is IdP-agnostic; HTPasswd validation sufficient | [ ]        |


#### **8. Known Limitations**

No limitations.

---

### **III. Test Scenarios & Traceability**

| Requirement ID           | Requirement Summary                                  | Test Scenario(s)                                                        | Test Type(s)     | Priority |
|:-------------------------|:-----------------------------------------------------|:------------------------------------------------------------------------|:-----------------|:---------|
| KubeVirt PR #16350       | `RoleAggregationStrategy config should keep aggregate labels when RoleAggregationStrategy is nil`                       | | tier1 automation | P0       |
| KubeVirt PR #16350       | `RoleAggregationStrategy configuration should keep aggregate labels when RoleAggregationStrategy is AggregateToDefault`        | | tier1 automation | P0       |
| KubeVirt PR #16350       | `RoleAggregationStrategy configuration should create ClusterRole without aggregate labels when RoleAggregationStrategy is Manual` | |  tier1 auto   | P0       |
| KubeVirt PR #16350       | `RoleAggregationStrategy configuration should remove aggregate labels from existing ClusterRole when strategy changes to Manual`  | |  tier1 auto   | P0       |
| CNV-63822                | As an admin, I can enable the feature via config in hyperconverged CR  | Verify config persists once enabled  | tier2 automation | P0       |
|                          | As an admin, I can enable the feature so an unprivileged user with admin role on a namespace cannot perform kubevirt.io:admin actions | Verify user gets ForbiddenError | tier2 automation | P0       |
|                          | As an admin, I can enable the feature so an unprivileged user with edit role on a namespace cannot perform kubevirt.io:edit actions  | Verify user gets ForbiddenError | tier2 automation | P0       |
|                          | As an admin, I can enable the feature so an unprivileged user with view role on a namespace cannot perform kubevirt.io:view actions | Verify user getse ForbiddenError | tier2 automation | P0       |
|                          | As an admin, I can specifically add kubevirt.io:admin permissions to an unprivileged user in a namespace when feature is enabled| Verify user can perform action | tier2 automation | P0       |
|                          | As an admin, I can specifically add kubevirt.io:edit permissions to an unprivileged user in a namespace when feature is enabled| Verify user can perform action | tier2 automation | P0       |
|                          | As an admin, I can specifically add kubevirt.io:view permissions to an unprivileged user in a namespace when feature is enabled| Verify user can perform action | tier2 automation | P0       |
|                          | As an admin, I can disable the feature via config in hyperconverged CR | Verify config persists once disabled and unprivileged user with admin role in a namespace can perform kubevirt:admin action | tier2 automation | P0       |

---

### **IV. Sign-off and Approval**

This Software Test Plan requires approval from the following stakeholders:

* **Reviewers:**
  - [QE Lead / @rnester]
  - [sig-iuo representative / @orenc1 @hmeir @OhadRevah @albarker-rh]
  - [sig-ui representative / @gouyang]

* **Approvers:**
  - [QE Manager / @kmajcher-rh @fabiand]
  - [Product Manager / Ronen Sde-Or]

**Review Status:**
- [X] Draft complete
- [ ] QE team reviewed
- [ ] Dev/Arch reviewed
- [ ] PM approved
- [ ] Ready for implementation
