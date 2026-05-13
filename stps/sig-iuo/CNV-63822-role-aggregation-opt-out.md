# Openshift-virtualization-tests Test plan

## **Role Aggregation Opt-Out - Quality Engineering Plan**

### **Metadata & Tracking**

- **Enhancement(s):** [Kubevirt VEP](https://github.com/kubevirt/enhancements/issues/160)
- **Feature Tracking:** [CNV-50792](https://issues.redhat.com/browse/CNV-50792)
- **Epic Tracking:** [CNV-63822](https://issues.redhat.com/browse/CNV-63822)
- **Feature Maturity:**
  - DP: 4.22
  - TP: 4.23/5.0
  - GA: 5.1
- **QE Owner(s):** Ramon Lobillo (@rlobillo), Alex Barker (@albarker-rh)
- **Owning SIG:** sig-iuo (Install, Upgrade, Operators)
- **Participating SIGs:** sig-ui

**Document Conventions (if applicable):** N/A — no feature-specific terms required.

### **Feature Overview**

By default, all project administrators, editors, and viewers automatically receive access to
OpenShift Virtualization resources. Role Aggregation Opt-Out allows cluster administrators to
disable this automatic access and instead grant virtualization permissions explicitly per user
and namespace, enabling fine-grained control in multi-tenant environments.
This STP covers testing for the Tech Preview phase (4.23/5.0).

---

### **I. Motivation and Requirements Review (QE Review Guidelines)**

This section documents the mandatory QE review process. The goal is to understand the feature's value,
technology, and testability before formal test planning.

#### **1. Requirement & User Story Review Checklist**

- [x] **Review Requirements**
  - *List the key D/S requirements reviewed:* Cluster admins can limit the access to virtualization components

- [x] **Understand Value and Customer Use Cases**
  - *Describe the feature's value to customers:* Enables tenant isolation by requiring
  explicit virtualization access grants instead of automatic role aggregation.
  - *List the customer use cases identified:*
    - As a cluster administrator, I want to disable automatic virtualization access
      so that only explicitly authorized users can use and interact with virtualization resources

- [x] **Testability**
  - *Note any requirements that are unclear or untestable:* All requirements are testable
    through standard API and RBAC validation.

- [x] **Acceptance Criteria**
  - *List the acceptance criteria:*
    - A cluster administrator can control the role aggregation strategy and any change to the setting takes effect on the virtualization deployment
    - When role aggregation is disabled, users with project admin, edit, or view roles in a namespace are forbidden from performing actions on virtualization resources
    - When role aggregation is enabled after being disabled, automatic access is restored for users who were previously blocked
  - *Note any gaps or missing criteria:* None. Defined in CNV-63822 epic.

- [x] **Non-Functional Requirements (NFRs)**
  - *List applicable NFRs and their targets:*
    - Security: RBAC hardening — users blocked without explicit grant
    - Backward Compatibility: default unchanged
    - UI: console changes tracked under CNV-80935
    - Docs: upstream docs available; downstream docs planned for 4.22
  - *Note any NFRs not covered and why:*
    - Performance: N/A — negligible RBAC overhead
    - Monitoring: N/A — no new metrics/alerts, uses standard Kubernetes RBAC
    - Scalability: N/A — scales with Kubernetes natively
    - Observability: N/A — standard audit logging covers RBAC decisions

#### **2. Known Limitations**

The limitations are documented to ensure alignment between development, QA, and product teams.
The following are confirmed product constraints accepted before testing begins.

None — reviewed and confirmed with Ronen Sde-Or (2026-05-13) that no feature limitations apply for
this release.

#### **3. Technology and Design Review**

- [x] **Developer Handoff/QE Kickoff**
  - *Key takeaways and concerns:* We agreed on the testing strategy and configuration requirements.

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
  - *Describe topology requirements:* Feature is cluster-scoped and topology-independent.
  - *Impact on test design:* Works on all topologies (standard, SNO, compact).

### **II. Software Test Plan (STP)**

This STP serves as the **overall roadmap for testing**, detailing the scope, approach, resources,
and schedule.

#### **1. Scope of Testing**

**Testing Goals**

- **[P0]** Verify a cluster administrator can disable role aggregation and the setting is applied to the virtualization deployment
- **[P0]** Verify a cluster administrator can switch the aggregation mode and the change propagates to the virtualization deployment
- **[P0]** Verify that removing the aggregation configuration resets the virtualization deployment to its original unconfigured state
- **[P0]** Verify that when role aggregation is disabled, an unprivileged user with a project admin role cannot perform virtualization admin actions (receives Forbidden error)
- **[P0]** Verify that when role aggregation is disabled, an unprivileged user with an edit role cannot perform virtualization edit actions (receives Forbidden error)
- **[P0]** Verify that when role aggregation is disabled, an unprivileged user with a view role cannot perform virtualization view actions (receives Forbidden error)
- **[P0]** Verify that enabling role aggregation after it was disabled restores automatic access for users who were previously blocked

**Regression Goals**

- **[P0]** Verify existing RBAC and migration functionality is not broken by the new feature — tier 2 regression suites run on the feature cluster, including migration rights tests

**Out of Scope (Testing Scope Exclusions)**

The following items are explicitly Out of Scope for this test cycle and represent intentional
exclusions. No verification activities will be performed for these items, and any related issues
found will not be classified as defects for this release.

- **Testing OpenShift RBAC infrastructure itself**
  - *Rationale:* Core RBAC evaluation is the responsibility of the OCP platform team; no duplication of their test effort
  - *PM/Lead Agreement:* Ronen Sde-Or / 2026-05-13

- **Testing all individual permission rules within virtualization roles**
  - *Rationale:* Individual role rules are not affected by this feature; this feature controls whether roles are aggregated, not the content of the roles themselves
  - *PM/Lead Agreement:* Ronen Sde-Or / 2026-05-13

- **External IdP compatibility (LDAP, Active Directory)**
  - *Rationale:* RBAC logic is IdP-agnostic; HTPasswd testing validates the core permission logic
  - *PM/Lead Agreement:* Ronen Sde-Or / 2026-05-13

- **Multi-tenant cluster scale testing (100+ users)**
  - *Rationale:* RBAC evaluation overhead is negligible; functional correctness at smaller scale is sufficient
  - *PM/Lead Agreement:* Ronen Sde-Or / 2026-05-13

**Test Limitations**

None — reviewed and confirmed that no test limitations apply for this release.
*Sign-off:* Ronen Sde-Or / 2026-05-13

#### **2. Test Strategy**

**Functional**

- [x] **Functional Testing** — Validates that the feature works according to specified requirements and user stories
  - *Details:* Core focus: verify role aggregation configuration, RBAC enforcement, and default behavior preservation.

- [x] **Automation Testing** — Confirms test automation plan is in place for CI and regression coverage (all tests are expected to be automated)
  - *Details:* All tier 1 and tier 2 tests automated; tier 1 validates configuration, tier 2 validates end-to-end user workflows.

- [x] **Regression Testing** — Verifies that new changes do not break existing functionality
  - *Details:* Migrate role aggregation is already covered by existing tier 2 regression tests.

**Non-Functional**

- [ ] **Performance Testing** — Validates feature performance meets requirements (latency, throughput, resource usage)
  - *Details:* N/A — feature adds no performance-sensitive operations; RBAC evaluation overhead is negligible.

- [ ] **Scale Testing** — Validates feature behavior under increased load and at production-like scale (e.g., large number of VMs, nodes, or concurrent operations)
  - *Details:* N/A — Kubernetes RBAC scales natively; feature does not introduce new scalability concerns.

- [x] **Security Testing** — Verifies security requirements, RBAC, authentication, authorization, and vulnerability scanning
  - *Details:* Feature is a security enhancement; tests verify users are correctly blocked when role aggregation is disabled for all 3 role levels.

- [ ] **Usability Testing** — Validates user experience and accessibility requirements
  - *Details:* UI changes tracked under [CNV-80935](https://issues.redhat.com/browse/CNV-80935); UI team (sig-ui) owns console testing for role aggregation configuration.

- [ ] **Monitoring** — Does the feature require metrics and/or alerts?
  - *Details:* No new metrics or alerts required; feature uses standard Kubernetes RBAC.

**Integration & Compatibility**

- [x] **Compatibility Testing** — Ensures feature works across supported platforms, versions, and configurations
  - *Details:* Default behavior unchanged; backward compatibility with previous API versions maintained.

- [x] **Upgrade Testing** — Validates upgrade paths from previous versions, data migration, and configuration preservation
  - *Details:* Verify default behavior preserved across z-stream upgrades; verify role aggregation configuration persists after upgrade.

- [ ] **Dependencies** — Blocked by deliverables from other components/products. Identify what we need from other teams before we can test.
  - *Details:* No blocking dependencies; upstream and downstream implementations are complete.

- [x] **Cross Integrations** — Does the feature affect other features or require testing by other teams? Identify the impact we cause.
  - *Details:* UI team (sig-ui) has implemented and tested console changes ([CNV-80935](https://issues.redhat.com/browse/CNV-80935) — done).

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

- [x] Requirements and design documents are **approved and merged**
- [x] Test environment can be **set up and configured** (see Section II.3 - Test Environment)
- [x] Upstream implementation **merged** (role aggregation opt-out support)
- [x] Downstream implementation **complete** (configuration field available in cluster settings)
- [x] Developer Handoff/QE Kickoff meeting completed

#### **5. Risks**

**Timeline/Schedule**

- **Risk:** N/A
  - **Mitigation:** Feature implementation is complete upstream and downstream; no schedule risk.

**Test Coverage**

- **Risk:** Cannot exhaustively test all RBAC role combinations and permission permutations.
  - **Mitigation:** Focus on the 3 critical role levels (admin, edit, view) covering acceptance criteria; individual permission rules within roles are unaffected by this feature.
  - *Areas with reduced coverage:* Individual permission rules within each virtualization role; only role-level access is validated.
  - *Sign-off:* Ronen Sde-Or / 2026-05-13

**Test Environment**

- **Risk:** N/A
  - **Mitigation:** Standard OCP cluster with HTPasswd IdP is sufficient; no special hardware or infrastructure required.

**Untestable Aspects**

- **Risk:** Cannot test with production identity providers (LDAP, Active Directory, OAuth) in the lab.
  - **Mitigation:** RBAC logic is IdP-agnostic; HTPasswd validation covers the enforcement path regardless of IdP.
  - *Alternative validation approach:* Functional validation with HTPasswd covers the RBAC enforcement path regardless of IdP.
  - *Sign-off:* Ronen Sde-Or / 2026-05-13

**Resource Constraints**

- **Risk:** N/A
  - **Mitigation:** Feature testing scope is manageable with assigned QE resources; no staffing or capacity constraints.

**Dependencies**

- **Risk:** N/A
  - **Mitigation:** UI changes ([CNV-80935](https://issues.redhat.com/browse/CNV-80935)) are complete; no remaining external dependencies.


---

### **III. Test Scenarios & Traceability**

- **[CNV-63822]** — As a cluster admin, I want to control the role aggregation strategy for virtualization resources
  - *Test Scenario:* [Tier 1] Verify that disabling role aggregation applies the setting to the virtualization deployment
  - *Priority:* P0

  - *Test Scenario:* [Tier 1] Verify that changing the aggregation mode propagates the updated setting to the virtualization deployment
  - *Priority:* P0

  - *Test Scenario:* [Tier 1] Verify that removing the aggregation configuration resets the virtualization deployment to its original state
  - *Priority:* P0

- **[CNV-63822]** — As a cluster admin, I want to disable role aggregation so unprivileged users cannot access virtualization resources
  - *Test Scenario:* [Tier 2] Verify an unprivileged user with project admin role cannot perform virtualization admin actions when role aggregation is disabled (receives Forbidden error)
  - *Priority:* P0

  - *Test Scenario:* [Tier 2] Verify an unprivileged user with edit role cannot perform virtualization edit actions when role aggregation is disabled (receives Forbidden error)
  - *Priority:* P0

  - *Test Scenario:* [Tier 2] Verify an unprivileged user with view role cannot perform virtualization view actions when role aggregation is disabled (receives Forbidden error)
  - *Priority:* P0

- **[CNV-63822]** — As a cluster admin, I want to re-enable role aggregation to restore default behavior
  - *Test Scenario:* [Tier 2] Verify that re-enabling role aggregation restores automatic access for previously blocked users
  - *Priority:* P0

---

### **IV. Sign-off and Approval**

This Software Test Plan requires approval from the following stakeholders:

* **Reviewers:**
  - QE Lead / @rnester
  - sig-iuo representative / @orenc1 @hmeir @OhadRevah @rlobillo
  - sig-ui representative / @upalatucci

* **Approvers:**
  - QE Lead / @rnetser
  - sig-iuo representative / @hmeir
  - QE Manager / @kmajcher-rh
  - Product Manager / Ronen Sde-Or @ronensdeor
