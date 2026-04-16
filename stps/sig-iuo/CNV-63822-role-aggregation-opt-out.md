# Openshift-virtualization-tests Test plan

## **Role Aggregation Opt-Out - Quality Engineering Plan**

### **Metadata & Tracking**

- **Enhancement(s):** [Kubevirt VEP](https://github.com/kubevirt/enhancements/issues/160)
- **Feature Tracking:** [CNV-50792](https://issues.redhat.com/browse/CNV-50792)
- **Epic Tracking:** [CNV-63822](https://issues.redhat.com/browse/CNV-63822)
- **QE Owner(s):** Ramon Lobillo (@rlobillo), Alex Barker (@albarker-rh)
- **Owning SIG:** sig-iuo (Install, Upgrade, Operators)
- **Participating SIGs:** sig-ui

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

This section documents the mandatory QE review process. The goal is to understand the feature's value,
technology, and testability before formal test planning.

#### **1. Requirement & User Story Review Checklist**

- [x] **Review Requirements**
  - *List the key D/S requirements reviewed:* As a cluster-admin I want to decide which users
    will have access to the virtualization in the cluster. Not all project-admins should have
    this access but only the eligible ones. Per CNV-50792 feature request.

- [x] **Understand Value and Customer Use Cases**
  - *Describe the feature's value to customers:* A cluster-admin wants to control which users
    has access to view/create/edit openshift virtualization resources on a given namespace.
    Per CNV-50792 feature request.
  - *List the customer use cases identified:*
    - As a cluster administrator managing a multi-tenant cluster, I want to prevent tenants
      from accessing virtualization workloads they are not eligible to use, so that different
      namespaces can enforce different workload entitlements
    - As a cluster administrator, I want to require users to request approval before creating
      VMs and consuming storage, so that I can control resource usage across namespaces

- [x] **Testability**
  - *Note any requirements that are unclear or untestable:* All requirements are testable
    through standard API and RBAC validation.

- [x] **Acceptance Criteria**
  - *List the acceptance criteria:*
    - When opt-out is enabled, a project admin in a namespace receives Forbidden when
      attempting virtualization actions
    - When opt-out is enabled, explicit role bindings for admin/edit/view grant the
      corresponding virtualization access
    - When opt-out is disabled (default), all users with project roles retain automatic
      access — no change from previous releases
    - Configuration changes persist without cluster restart
  - *Note any gaps or missing criteria:* None. Defined in CNV-63822 epic.

- [x] **Non-Functional Requirements (NFRs)**
  - *List applicable NFRs and their targets:*
    - Security: RBAC hardening — users blocked without explicit grant
    - Backward Compatibility: default unchanged
    - UI: console changes tracked under CNV-80935
    - Docs: user-facing documentation required
  - *Note any NFRs not covered and why:*
    - Performance: N/A — negligible RBAC overhead
    - Monitoring: N/A — no new metrics/alerts, uses standard Kubernetes RBAC
    - Scalability: N/A — scales with Kubernetes natively
    - Observability: N/A — standard audit logging covers RBAC decisions

#### **2. Known Limitations**

The limitations are documented to ensure alignment between development, QA, and product teams.
The following are confirmed product constraints accepted before testing begins.

None — reviewed and confirmed with [Name/Date — TBD] that no feature limitations apply for
this release.

#### **3. Technology and Design Review**

- [x] **Developer Handoff/QE Kickoff**
  - *Key takeaways and concerns:* The feature is behind a KubeVirt feature-gate. When the
    feature is enabled in Openshift, HCO will automatically add the feature-gate.
    Implementation details discussed, ready for testing.

- [x] **Technology Challenges**
  - *List identified challenges:* N/A
  - *Impact on testing approach:* N/A

- [x] **API Extensions**
  - *List new or modified APIs:* New cluster-level configuration field to control role
    aggregation behavior (default: enabled, opt-out: manual).
  - *Testing impact:* Tests must validate config changes and downstream RBAC effects.

- [x] **Test Environment Needs**
  - *See environment requirements in Section II.3 and testing tools in Section II.3.1*

- [x] **Topology Considerations**
  - *Describe topology requirements:* Feature is cluster-scoped (KubeVirt CR level),
    topology-independent.
  - *Impact on test design:* Works on all topologies (standard, SNO, compact).

### **II. Software Test Plan (STP)**

This STP serves as the **overall roadmap for testing**, detailing the scope, approach, resources,
and schedule.

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

**Out of Scope (Testing Scope Exclusions)**

The following items are explicitly Out of Scope for this test cycle and represent intentional
exclusions. No verification activities will be performed for these items, and any related issues
found will not be classified as defects for this release.

- **Testing OpenShift RBAC infrastructure itself**
  - *Rationale:* Core RBAC evaluation is the responsibility of the OCP platform team; no duplication of their test effort
  - *PM/Lead Agreement:* [Name/Date — TBD]

- **Testing all individual permission rules within virtualization roles**
  - *Rationale:* Individual role rules are not affected by this feature; this feature controls whether roles are aggregated, not the content of the roles themselves
  - *PM/Lead Agreement:* [Name/Date — TBD]

- **External IdP compatibility (LDAP, Active Directory)**
  - *Rationale:* RBAC logic is IdP-agnostic; HTPasswd testing validates the core permission logic
  - *PM/Lead Agreement:* [Name/Date — TBD]

- **Multi-tenant cluster scale testing (100+ users)**
  - *Rationale:* RBAC evaluation overhead is negligible; functional correctness at smaller scale is sufficient
  - *PM/Lead Agreement:* [Name/Date — TBD]

**Test Limitations**

None — reviewed and confirmed that no test limitations apply for this release.
*Sign-off:* [Name/Date — TBD]

#### **2. Test Strategy**

**Functional**

- [x] **Functional Testing** — Validates that the feature works according to specified requirements and user stories
  - *Details:* Core focus: verify opt-out configuration, RBAC enforcement, explicit grants, and default behavior preservation.

- [x] **Automation Testing** — Confirms test automation plan is in place for CI and regression coverage (all tests are expected to be automated)
  - *Details:* All tier 1 and tier 2 tests automated; tier 1 validates configuration, tier 2 validates end-to-end user workflows.

- [x] **Regression Testing** — Verifies that new changes do not break existing functionality
  - *Details:* Existing RBAC/migration tests provide regression coverage; standard sig-iuo suites run on feature cluster. Migrate role aggregation is already covered by existing tier 2 regression tests ([test_migration_rights.py](https://github.com/RedHatQE/openshift-virtualization-tests/blob/main/tests/virt/cluster/migration_and_maintenance/rbac_hardening/test_migration_rights.py)).

**Non-Functional**

- [ ] **Performance Testing** — Validates feature performance meets requirements (latency, throughput, resource usage)
  - *Details:* N/A — feature adds no performance-sensitive operations; RBAC evaluation overhead is negligible.

- [ ] **Scale Testing** — Validates feature behavior under increased load and at production-like scale (e.g., large number of VMs, nodes, or concurrent operations)
  - *Details:* N/A — Kubernetes RBAC scales natively; feature does not introduce new scalability concerns.

- [x] **Security Testing** — Verifies security requirements, RBAC, authentication, authorization, and vulnerability scanning
  - *Details:* Feature is a security enhancement; tests verify users are correctly blocked and explicit grants work for all 3 role levels.

- [x] **Usability Testing** — Validates user experience and accessibility requirements
  - *Details:* UI changes tracked under [CNV-80935](https://issues.redhat.com/browse/CNV-80935); UI team (sig-ui) owns console testing; QE validates config workflow feedback.

- [ ] **Monitoring** — Does the feature require metrics and/or alerts?
  - *Details:* No new metrics or alerts required; feature uses standard Kubernetes RBAC.

**Integration & Compatibility**

- [x] **Compatibility Testing** — Ensures feature works across supported platforms, versions, and configurations
  - *Details:* Default behavior unchanged; backward compatibility with previous API versions maintained.

- [x] **Upgrade Testing** — Validates upgrade paths from previous versions, data migration, and configuration preservation
  - *Details:* Verify default behavior preserved across z-stream upgrades; verify opt-out config persists after upgrade.

- [ ] **Dependencies** — Blocked by deliverables from other components/products. Identify what we need from other teams before we can test.
  - *Details:* No blocking dependencies; upstream and downstream implementations are complete.

- [x] **Cross Integrations** — Does the feature affect other features or require testing by other teams? Identify the impact we cause.
  - *Details:* UI team (sig-ui) needs to implement and test console changes ([CNV-80935](https://issues.redhat.com/browse/CNV-80935)).

**Infrastructure**

- [ ] **Cloud Testing** — Does the feature require multi-cloud platform testing? Consider cloud-specific features.
  - *Details:* N/A — feature is RBAC-based and platform-independent; no cloud-specific behavior.

#### **3. Test Environment**

- **Cluster Topology:** Standard or SNO — feature works on all topologies; multi-node preferred

- **OCP & OpenShift Virtualization Version(s):** OCP 4.22 with OpenShift Virtualization 4.22

- **CPU Virtualization:** N/A — not relevant for RBAC testing

- **Compute Resources:** Minimum per worker node: 4 vCPUs, 16GB RAM

- **Special Hardware:** N/A — no special hardware required

- **Storage:** Any RWX storage class (e.g., ocs-storagecluster-ceph-rbd-virtualization)

- **Network:** OVN-Kubernetes, IPv4 — no special network requirements

- **Required Operators:** OpenShift Virtualization (standard installation)

- **Platform:** Any supported platform (bare metal, AWS, Azure, GCP — no platform-specific behavior)

- **Special Configurations:** HTPasswd identity provider — REQUIRED: Must have HTPasswd IdP with unprivileged user

#### **3.1. Testing Tools & Frameworks**

- **Test Framework:** Standard

- **CI/CD:** N/A

- **Other Tools:** N/A

#### **4. Entry Criteria**

The following conditions must be met before testing can begin:

- [ ] Requirements and design documents are **approved and merged**
- [ ] Test environment can be **set up and configured** (see Section II.3 - Test Environment)
- [x] KubeVirt PR #16350 **merged** (upstream implementation)
- [x] HCO downstream implementation **complete** (field integrated into HCO CR)
- [x] Developer Handoff/QE Kickoff meeting completed

#### **5. Risks**

**Timeline/Schedule**

- **Risk:** N/A — feature implementation is complete (upstream and downstream).
  - **Mitigation:** N/A
  - *Estimated impact on schedule:* None
  - *Sign-off:* [Name/Date — TBD]

**Test Coverage**

- **Risk:** Cannot exhaustively test all RBAC role combinations and permission permutations.
  - **Mitigation:** Focus on the 3 critical role levels (admin, edit, view) covering acceptance criteria; individual permission rules within roles are unaffected by this feature.
  - *Areas with reduced coverage:* Individual permission rules within each virtualization role; only role-level access is validated.
  - *Sign-off:* [Name/Date — TBD]

**Test Environment**

- **Risk:** N/A — standard OCP cluster with HTPasswd IdP is sufficient; no special hardware required.
  - **Mitigation:** N/A
  - *Missing resources or infrastructure:* None
  - *Sign-off:* [Name/Date — TBD]

**Untestable Aspects**

- **Risk:** Cannot test with production identity providers (LDAP, Active Directory, OAuth) in the lab.
  - **Mitigation:** RBAC logic is IdP-agnostic; HTPasswd validation covers the enforcement path regardless of IdP.
  - *Alternative validation approach:* Functional validation with HTPasswd covers the RBAC enforcement path regardless of IdP.
  - *Sign-off:* [Name/Date — TBD]

**Resource Constraints**

- **Risk:** N/A — no staffing or capacity constraints; feature testing scope is manageable with assigned QE resources.
  - **Mitigation:** N/A
  - *Current capacity gaps:* None
  - *Sign-off:* [Name/Date — TBD]

**Dependencies**

- **Risk:** UI changes ([CNV-80935](https://issues.redhat.com/browse/CNV-80935)) are pending; console configuration interface may not be ready for testing.
  - **Mitigation:** Track progress with UI team (sig-ui); API-level testing can proceed independently of UI.
  - *Dependent teams or components:* sig-ui — console configuration interface for opt-out
  - *Sign-off:* [Name/Date — TBD]

**Other**

- **Risk:** N/A — no additional risks identified.
  - **Mitigation:** N/A
  - *Sign-off:* [Name/Date — TBD]

---

### **III. Test Scenarios & Traceability**

- **[CNV-63822]** — As a cluster admin, I want to control the role aggregation strategy for virtualization resources
  - *Test Scenario:* [Tier 1] Verify default behavior is preserved when role aggregation opt-out is not configured — all users retain automatic access
  - *Priority:* P0

  - *Test Scenario:* [Tier 1] Verify default behavior is preserved when aggregation strategy is explicitly set to the default mode
  - *Priority:* P0

  - *Test Scenario:* [Tier 1] Verify that when opt-out mode is enabled, virtualization roles no longer automatically grant access to users
  - *Priority:* P0

  - *Test Scenario:* [Tier 1] Verify that switching from default to opt-out mode removes previously aggregated access from existing roles
  - *Priority:* P0

- **[CNV-63822]** — As a cluster admin, I want to enable opt-out so unprivileged users cannot access virtualization resources
  - *Test Scenario:* [Tier 2] Verify opt-out can be enabled via cluster configuration and the setting persists
  - *Priority:* P0

  - *Test Scenario:* [Tier 2] Verify an unprivileged user with project admin role cannot perform virtualization admin actions when opt-out is enabled (receives Forbidden error)
  - *Priority:* P0

  - *Test Scenario:* [Tier 2] Verify an unprivileged user with edit role cannot perform virtualization edit actions when opt-out is enabled (receives Forbidden error)
  - *Priority:* P0

  - *Test Scenario:* [Tier 2] Verify an unprivileged user with view role cannot perform virtualization view actions when opt-out is enabled (receives Forbidden error)
  - *Priority:* P0

- **[CNV-63822]** — As a cluster admin, I want to explicitly grant virtualization permissions to specific users
  - *Test Scenario:* [Tier 2] Verify a cluster admin can grant virtualization admin permissions to a user in a namespace and the user can perform admin actions
  - *Priority:* P0

  - *Test Scenario:* [Tier 2] Verify a cluster admin can grant virtualization edit permissions to a user in a namespace and the user can perform edit actions
  - *Priority:* P0

  - *Test Scenario:* [Tier 2] Verify a cluster admin can grant virtualization view permissions to a user in a namespace and the user can view resources
  - *Priority:* P0

- **[CNV-63822]** — As a cluster admin, I want to disable opt-out to restore default behavior
  - *Test Scenario:* [Tier 2] Verify opt-out can be disabled and default automatic access is restored for users
  - *Priority:* P0

  - *Test Scenario:* [Tier 2] Verify that toggling opt-out off after it was enabled restores automatic access for users who previously lost it
  - *Priority:* P1

- **[CNV-63822]** — As a cluster admin, I want revoking a role binding to immediately remove virtualization access
  - *Test Scenario:* [Tier 2] Verify that removing an explicit role binding while opt-out is enabled immediately revokes the user's access
  - *Priority:* P1

---

### **IV. Sign-off and Approval**

This Software Test Plan requires approval from the following stakeholders:

* **Reviewers:**
  - QE Lead / @rnester
  - sig-iuo representative / @orenc1 @hmeir @OhadRevah @albarker-rh
  - sig-ui representative / @gouyang

* **Approvers:**
  - QE Manager / @kmajcher-rh @fabiand
  - Product Manager / Ronen Sde-Or
