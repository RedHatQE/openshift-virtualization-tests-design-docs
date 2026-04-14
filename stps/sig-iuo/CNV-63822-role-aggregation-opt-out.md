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

**Document Conventions (if applicable):** N/A — no feature-specific terms required.

### **Feature Overview**

Role Aggregation Opt-Out gives cluster administrators the ability to control which users can
access OpenShift Virtualization resources on a per-namespace basis. By default, OpenShift
Virtualization grants all project administrators, editors, and viewers automatic access to
virtualization resources through role aggregation. When opt-out is enabled, this automatic
access is removed, and administrators must explicitly grant virtualization permissions to
individual users through role bindings. This feature supports multi-tenant environments where
not all users should have access to virtualization workloads, and enables fine-grained control
over resource usage across namespaces.

---

### **I. Motivation and Requirements Review (QE Review Guidelines)**

#### **1. Requirement & User Story Review Checklist**

| Check                                  | Done | Details/Notes                                                                                                                                                                    | Comments                                              |
|:---------------------------------------|:-----|:---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:------------------------------------------------------|
| **Review Requirements**                | [x]  | As a cluster-admin I want to decide which users will have access to the virtualization in the cluster. Not all project-admins should have this access but only the eligible ones | Per CNV-50792 feature request |
| **Understand Value**                   | [x]  | A cluster-admin wants to control which users has access to view/create/edit openshift virtualization resources on a given namespace                                              | Per CNV-50792 feature request |
| **Customer Use Cases**                 | [x]  | * multi-tenant clusters                                                                                                                                                          |different namespaces are used to allow different workloads and prevent unallowed usage of workload that the tenant is not eligible to us|
|                                        |      | * Resources usage control                                                                                                                                                        |cluster admin wants to get a request to allow a specific user to create VMs and Storage|
| **Testability**                        | [x]  | All requirements are testable through standard API and RBAC validation                                                                                                           | Ready to implement tests  |
| **Acceptance Criteria**                | [x]  | (1) When opt-out is enabled, a project admin in a namespace receives Forbidden when attempting virtualization actions (2) When opt-out is enabled, explicit role bindings for admin/edit/view grant the corresponding virtualization access (3) When opt-out is disabled (default), all users with project roles retain automatic access — no change from previous releases (4) Configuration changes persist without cluster restart | Defined in CNV-63822 epic |
| **Non-Functional Requirements (NFRs)** | [x]  | Security: RBAC hardening — users blocked without explicit grant. Backward Compatibility: default unchanged. UI: console changes tracked under CNV-80935. Docs: user-facing documentation required. Performance: N/A — negligible RBAC overhead. Monitoring: N/A — no new metrics/alerts, uses standard Kubernetes RBAC. Scalability: N/A — scales with Kubernetes natively. Observability: N/A — standard audit logging covers RBAC decisions | Upgrade and docs coverage required                    |

#### **2. Known Limitations**

None — reviewed and confirmed with [Name/Date — TBD] that no feature limitations apply for
this release.

#### **3. Technology and Design Review**

| Check                            | Done | Details/Notes                                                                                                                        | Comments                                         |
|:---------------------------------|:-----|:-------------------------------------------------------------------------------------------------------------------------------------|:-------------------------------------------------|
| **Developer Handoff/QE Kickoff** | [x]  | The feature is behind a KubeVirt feature-gate. When the feature is enabled in Openshift, HCO will automatically add the feature-gate |                                                  |
| **Technology Challenges**        | [x]  | N/A                                                                                                                                  |                                                  |
| **Test Environment Needs**       | [x]  | Standard OCP + CNV cluster with HTPasswd IdP for unprivileged user testing                                                           | No special hardware required                     |
| **API Extensions**               | [x]  | New cluster-level configuration field to control role aggregation behavior (default: enabled, opt-out: manual)                       | Tests must validate config changes and downstream RBAC effects |
| **Topology Considerations**      | [x]  | Feature is cluster-scoped (KubeVirt CR level), topology-independent                                                                  | Works on all topologies (standard, SNO, compact) |



### **II. Software Test Plan (STP)**

#### **1. Scope of Testing**

**Testing Goals**

- **[P0]** Verify a cluster administrator can enable role aggregation opt-out through the cluster configuration and the setting persists
- **[P0]** Verify that when opt-out is enabled, an unprivileged user with a project admin role cannot perform virtualization admin actions (receives Forbidden error)
- **[P0]** Verify that when opt-out is enabled, an unprivileged user with an edit role cannot perform virtualization edit actions (receives Forbidden error)
- **[P0]** Verify that when opt-out is enabled, an unprivileged user with a view role cannot perform virtualization view actions (receives Forbidden error)
- **[P0]** Verify that a cluster administrator can explicitly grant virtualization admin, edit, and view permissions to a user when opt-out is enabled, and the user can perform the corresponding actions
- **[P0]** Verify a cluster administrator can disable role aggregation opt-out and default automatic access is restored
- **[P0]** Verify default behavior (role aggregation enabled) remains unchanged when the feature is not configured
- **[P0]** Verify default behavior is preserved across OpenShift Virtualization z-stream upgrades
- **[P1]** Verify that toggling opt-out off after it was enabled restores automatic access for users who previously lost it
- **[P1]** Verify that removing an explicit role binding while opt-out is enabled immediately revokes the user's virtualization access

**Out of Scope:**

| Out-of-Scope Item                                         | Rationale                                                                     | PM/ Lead Agreement |
|:----------------------------------------------------------|:------------------------------------------------------------------------------|:-------------------|
| Testing OpenShift RBAC infrastructure itself              | Core RBAC evaluation is the responsibility of the OCP platform team; no duplication of their test effort | [Name/Date — TBD]  |
| Testing all individual permission rules within virtualization roles | Individual role rules are not affected by this feature; this feature controls whether roles are aggregated, not the content of the roles themselves | [Name/Date — TBD]  |
| External IdP compatibility (LDAP, Active Directory)       | RBAC logic is IdP-agnostic; HTPasswd testing validates the core permission logic | [Name/Date — TBD]  |
| Multi-tenant cluster scale testing (100+ users)           | RBAC evaluation overhead is negligible; functional correctness at smaller scale is sufficient | [Name/Date — TBD]  |

**Note:** Migrate role aggregation testing is already covered by existing tier 2 regression tests
([test_migration_rights.py](https://github.com/RedHatQE/openshift-virtualization-tests/blob/main/tests/virt/cluster/migration_and_maintenance/rbac_hardening/test_migration_rights.py))
and is therefore documented as existing coverage, not out of scope.

**Test Limitations**

None — reviewed and confirmed that no test limitations apply for this release.
*Sign-off:* [Name/Date — TBD]


#### **2. Test Strategy**

| Item               | Description                                                                                                        | Applicable (Y/N or N/A) | Comments |
|:-------------------|:-------------------------------------------------------------------------------------------------------------------|:------------------------|:---------|
| Functional Testing | Validates that the feature works according to specified requirements and user stories                               | Y                       | Core focus: verify opt-out configuration, RBAC enforcement, explicit grants, and default behavior preservation |
| Automation Testing | Ensures test cases are automated for continuous integration and regression coverage                                 | Y                       | All tier 1 and tier 2 tests automated; tier 1 validates configuration, tier 2 validates end-to-end user workflows |
| Regression Testing | Verifies that new changes do not break existing functionality                                                      | Y                       | Existing RBAC/migration tests provide regression coverage; standard sig-iuo suites run on feature cluster |
| Performance Testing | Validates feature performance meets requirements (latency, throughput, resource usage)                             | N/A                     | Feature adds no performance-sensitive operations; RBAC evaluation overhead is negligible |
| Scale Testing      | Validates feature behavior under increased load and at production-like scale                                       | N/A                     | Kubernetes RBAC scales natively; feature does not introduce new scalability concerns |
| Security Testing   | Verifies security requirements, RBAC, authentication, authorization, and vulnerability scanning                    | Y                       | Feature is a security enhancement; tests verify users are correctly blocked and explicit grants work for all 3 role levels |
| Usability Testing  | Validates user experience, UI/UX consistency, and accessibility requirements                                       | Y                       | UI changes tracked under [CNV-80935](https://issues.redhat.com/browse/CNV-80935); UI team (sig-ui) owns console testing; QE validates config workflow feedback |
| Monitoring         | Does the feature require metrics and/or alerts?                                                                    | N                       | No new metrics or alerts required; feature uses standard Kubernetes RBAC |
| Compatibility Testing | Ensures feature works across supported platforms, versions, and configurations; includes backward compatibility  | Y                       | Default behavior unchanged; backward compatibility with previous API versions maintained |
| Upgrade Testing    | Validates upgrade paths from previous versions, data migration, and configuration preservation                     | Y                       | Verify default behavior preserved across z-stream upgrades; verify opt-out config persists after upgrade |
| Dependencies       | Dependent on deliverables from other components/products? Identify what is tested by which team                    | N                       | No blocking dependencies; upstream and downstream implementations are complete |
| Cross Integrations | Does the feature affect other features/require testing by other components? Identify what is tested by which team  | Y                       | UI team (sig-ui) needs to implement and test console changes ([CNV-80935](https://issues.redhat.com/browse/CNV-80935)) |
| Cloud Testing      | Does the feature require multi-cloud platform testing? Consider cloud-specific features                            | N                       | Feature is RBAC-based and platform-independent; no cloud-specific behavior |


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
| **Test Framework** | Standard         |
| **CI/CD**          | N/A              |
| **Other Tools**    | N/A              |

#### **4. Entry Criteria**

- [X] KubeVirt PR #16350 **merged**
- [X] HCO downstream implementation **complete** (field integrated into HCO CR)
- [ ] Requirements and design documents approved
- [ ] Developer Handoff/QE Kickoff meeting completed

#### **5. Risks**

| Risk Category        | Specific Risk for This Feature                                                       | Mitigation Strategy                                                                     | Sign-off           |
|:---------------------|:-------------------------------------------------------------------------------------|:----------------------------------------------------------------------------------------|:-------------------|
| Timeline/Schedule    | N/A — feature implementation is complete (upstream and downstream)                   | N/A                                                                                     | [Name/Date — TBD]  |
| Test Coverage        | Cannot exhaustively test all RBAC role combinations and permission permutations       | Focus on the 3 critical role levels (admin, edit, view) covering acceptance criteria; individual permission rules within roles are unaffected by this feature | [Name/Date — TBD]  |
| Test Environment     | N/A — standard OCP cluster with HTPasswd IdP is sufficient; no special hardware required | N/A                                                                                  | [Name/Date — TBD]  |
| Untestable Aspects   | Cannot test with production identity providers (LDAP, Active Directory, OAuth) in the lab | RBAC logic is IdP-agnostic; HTPasswd validation covers the enforcement path regardless of IdP | [Name/Date — TBD]  |
| Resource Constraints | N/A — no staffing or capacity constraints; feature testing scope is manageable with assigned QE resources | N/A                                                                       | [Name/Date — TBD]  |
| Dependencies         | UI changes ([CNV-80935](https://issues.redhat.com/browse/CNV-80935)) are pending; console configuration interface may not be ready for testing | Track progress with UI team (sig-ui); API-level testing can proceed independently of UI | [Name/Date — TBD]  |
| Other                | N/A — no additional risks identified                                                 | N/A                                                                                     | [Name/Date — TBD]  |


---

### **III. Test Scenarios & Traceability**

| Requirement ID | Requirement Summary                                                                                        | Test Scenario(s)                                                                                                                                               | Test Type(s)     | Priority |
|:---------------|:-----------------------------------------------------------------------------------------------------------|:---------------------------------------------------------------------------------------------------------------------------------------------------------------|:-----------------|:---------|
| CNV-63822      | As a cluster admin, I want to control the role aggregation strategy for virtualization resources            | Verify default behavior is preserved when role aggregation opt-out is not configured — all users retain automatic access                                       | tier1 automation | P0       |
|                |                                                                                                            | Verify default behavior is preserved when aggregation strategy is explicitly set to the default mode                                                           | tier1 automation | P0       |
|                |                                                                                                            | Verify that when opt-out mode is enabled, virtualization roles no longer automatically grant access to users                                                   | tier1 automation | P0       |
|                |                                                                                                            | Verify that switching from default to opt-out mode removes previously aggregated access from existing roles                                                    | tier1 automation | P0       |
| CNV-63822      | As a cluster admin, I want to enable opt-out so unprivileged users cannot access virtualization resources   | Verify opt-out can be enabled via cluster configuration and the setting persists                                                                               | tier2 automation | P0       |
|                |                                                                                                            | Verify an unprivileged user with admin/edit/view role cannot perform virtualization admin/edit/view actions when opt-out is enabled (receives Forbidden error) | tier2 automation | P0       |
| CNV-63822      | As a cluster admin, I want to explicitly grant virtualization permissions to specific users                 | Verify a cluster admin can grant virtualization admin/edit/view permissions to a user in a namespace and the user can perform admin/edit/view actions          | tier2 automation | P0       |
| CNV-63822      | As a cluster admin, I want to disable opt-out to restore default behavior                                  | Verify opt-out can be disabled and default automatic access is restored for users                                                                              | tier2 automation | P0       |
|                |                                                                                                            | Verify that toggling opt-out off after it was enabled restores automatic access for users who previously lost it                                               | tier2 automation | P1       |
| CNV-63822      | As a cluster admin, I want revoking a role binding to immediately remove virtualization access              | Verify that removing an explicit role binding while opt-out is enabled immediately revokes the user's access                                                   | tier2 automation | P1       |

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
