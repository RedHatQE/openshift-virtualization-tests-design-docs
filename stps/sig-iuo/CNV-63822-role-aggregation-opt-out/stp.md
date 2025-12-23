# Openshift-virtualization-tests Test plan

## **Role Aggregation Opt-Out - Quality Engineering Plan**

### **Metadata & Tracking**

| Field                  | Details                                                 |
|:-----------------------|:--------------------------------------------------------|
| **Enhancement(s)**     | TBD - Pending upstream design (CNV-63824)               |
| **Feature in Jira**    | [CNV-63822](https://issues.redhat.com/browse/CNV-63822) |
| **Jira Tracking**      | [CNV-63822](https://issues.redhat.com/browse/CNV-63822) |
| **QE Owner(s)**        | Ramón Lobillo                                           |
| **Owning SIG**         | sig-iuo (Install, Upgrade, Operators)                   |
| **Participating SIGs** | sig-virt (affected by RBAC changes)                     |
| **Current Status**     | Draft                                                   |

---

### **I. Motivation and Requirements Review (QE Review Guidelines)**

This section documents the mandatory QE review process. The goal is to understand the feature's value, technology, and testability prior to formal test planning.

#### **1. Requirement & User Story Review Checklist**

| Check                                  | Done | Details/Notes                                                                   | Comments                                              |
|:---------------------------------------|:-----|:--------------------------------------------------------------------------------|:------------------------------------------------------|
| **Review Requirements**                | [x]  | Reviewed CNV-63822 epic and sub-tasks.                                          | Upstream design (CNV-63824) is in progress            |
| **Understand Value**                   | [x]  | See detailed user story and value proposition below                             | Critical for customers requiring strict RBAC controls |
| **Customer Use Cases**                 | [x]  | See customer use cases listed below                                             | Use cases align with enterprise security requirements |
| **Testability**                        | [ ]  | Blocked: Waiting for upstream design (CNV-63824)                                | Cannot write tests without configuration mechanism    |
| **Acceptance Criteria**                | [x]  | See acceptance criteria listed below                                            | Clearly defined in sub-task descriptions              |
| **Non-Functional Requirements (NFRs)** | [x]  | Security, Upgrade, Backward Compatibility, Docs - see details below             | Performance/Scalability not applicable for RBAC       |

**User Story and Value:**
- **User Story**: As a cluster admin, I want to disable automatic role aggregation so that users do NOT receive kubevirt-related roles by default.
- **Value**: Enhanced security through principle of least privilege - admins explicitly grant kubevirt permissions rather than automatic assignment.

**Customer Use Cases:**
1. Regulated environments requiring explicit permission grants
2. Multi-tenant clusters where VM management is restricted to specific teams
3. Security-hardened clusters with no default elevated permissions

**Acceptance Criteria:**
1. Set opt-out for role aggregation in HCO CR
2. Unprivileged user cannot interact with kubevirt resources
3. After adding explicit RoleBinding, user CAN interact with kubevirt resources

**Non-Functional Requirements:**
- **Security**: Core feature is security-focused (RBAC hardening)
- **Upgrade**: Must preserve configuration across upgrades
- **Backward Compatibility**: Default behavior unchanged
- **Monitoring**: N/A - RBAC feature
- **Docs**: Downstream docs task exists (CNV-63829)

- [KubeVirt Enhancements](https://github.com/kubevirt/enhancements/tree/main/veps)
- [OCP Enhancements](https://github.com/openshift/enhancements/tree/master/enhancements)

#### **2. Technology and Design Review**

| Check                            | Done | Details/Notes                                                                   | Comments                                              |
|:---------------------------------|:-----|:--------------------------------------------------------------------------------|:------------------------------------------------------|
| **Developer Handoff/QE Kickoff** | [ ]  | Pending: Need Dev/Arch walkthrough once upstream design complete                | Critical to understand HCO CR changes                 |
| **Technology Challenges**        | [x]  | See technology challenges listed below                                          | Challenges manageable with existing infrastructure    |
| **Test Environment Needs**       | [x]  | Standard OCP + CNV cluster with HTPasswd IdP                                    | Can use existing test infrastructure                  |
| **API Extensions**               | [x]  | HCO CR modification for role aggregation opt-out                                | Waiting for exact field name from upstream design     |
| **Topology Considerations**      | [x]  | Cluster-scoped feature, topology-independent                                    | Works on all topologies (standard, SNO, compact)      |

**Technology Challenges:**
1. Testing requires proper unprivileged user setup (already exists: `unprivileged_client` fixture)
2. Need to verify HCO reconciliation
3. Upgrade testing requires multi-version clusters

**Test Environment Details:**
- Standard OCP + OpenShift Virtualization cluster
- No special hardware requirements
- Must support HTPasswd identity provider for unprivileged users

**API Extensions:**
- HCO CR will be modified (new field for role aggregation opt-out)
- No new CRDs, no VM API changes
- Affects: ClusterRole bindings for kubevirt.io roles

**Topology:**
- Feature is cluster-scoped (HCO CR)
- No multi-cluster implications
- No network topology impact
- Works on all topologies (standard, SNO, compact)


### **II. Software Test Plan (STP)**

This STP serves as the **overall roadmap for testing**, detailing the scope, approach, resources, and schedule.

#### **1. Scope of Testing**

This test plan covers the role aggregation opt-out feature, which allows cluster administrators to disable automatic assignment of kubevirt-related roles to users.

**In Scope:**
- **Functional Testing**:
  - Verify role aggregation can be disabled via HCO CR configuration
  - Test that unprivileged users cannot interact with kubevirt resources when opt-out is enabled
  - Verify explicit RoleBinding grants work correctly with opt-out enabled
  - Validate default behavior (role aggregation enabled) remains unchanged
  - Test all kubevirt ClusterRoles: kubevirt.io:admin, kubevirt.io:edit, kubevirt.io:view, kubevirt.io:migrate

- **RBAC Hardening**:
  - Verify ForbiddenError responses when permissions are missing
  - Test VM operations: create, start, stop, delete, migrate, console access
  - Validate permissions across multiple namespaces
  - Test with different user types (namespace admin, regular user)

- **Upgrade Testing**:
  - Verify configuration preservation across CNV upgrades
  - Test upgrade with opt-out disabled → enabled
  - Test upgrade with opt-out already enabled
  - Validate behavior change during upgrade

- **Installation Testing**:
  - Fresh install with opt-out enabled
  - Fresh install with opt-out disabled (default)

- **HCO Reconciliation**:
  - Toggle configuration on live cluster
  - Verify HCO reconciles correctly after configuration change
  - Validate dependent operators (KubeVirt) reflect changes

**Non-Functional Requirements**:
- **Security**: Core security feature (RBAC hardening) - tested through functional scenarios
- **Backward Compatibility**: Default behavior must remain unchanged
- **Documentation**: Validated through docs review (CNV-63829)

**Document Conventions:**
- **HCO**: HyperConverged Cluster Operator
- **RBAC**: Role-Based Access Control
- **CNV**: Container-native Virtualization (OpenShift Virtualization)

#### **2. Testing Goals**

Define specific, measurable testing objectives for this feature, such as:

- [x] **Goal 1**: Achieve 100% coverage of acceptance criteria defined in CNV-63822
- [x] **Goal 2**: Validate all kubevirt.io ClusterRoles (admin, edit, view, migrate) work correctly with opt-out
- [x] **Goal 3**: Verify backward compatibility - default behavior unchanged when opt-out is not configured
- [x] **Goal 4**: Automate 100% of functional test scenarios in openshift-virtualization-tests repository
- [x] **Goal 5**: Create reusable test infrastructure for RBAC testing (fixtures, utilities)

#### **3. Non-Goals (Testing Scope Exclusions)**

Explicitly document what is **out of scope** for testing. **Critical:** All non-goals require explicit stakeholder agreement to prevent "I assumed you were testing that" issues.

| Non-Goal                                                          | Rationale                                                                     | PM/ Lead Agreement |
|:------------------------------------------------------------------|:------------------------------------------------------------------------------|:-------------------|
| Testing OpenShift RBAC infrastructure itself                      | Core RBAC functionality is OCP's responsibility, not CNV-specific             | [ ] Name/Date      |
| Performance impact testing of RBAC checks                         | RBAC overhead is negligible and not a concern for this feature                | [ ] Name/Date      |
| Testing on ARM64 or s390x architectures                           | RBAC is architecture-independent, x86_64 coverage is sufficient               | [ ] Name/Date      |
| UI testing for role aggregation configuration                     | Feature is configured via HCO CR (YAML), no UI component exists               | [ ] Name/Date      |
| Testing with external identity providers (LDAP, Active Directory) | Feature testing uses HTPasswd; external IdP testing is infrastructure concern | [ ] Name/Date      |

**Important Notes:**
- Non-goals without stakeholder agreement are considered **risks** and must be escalated (see Section II.7 - Risks and Limitations)
- Review non-goals during Developer Handoff/QE Kickoff meeting (see Section I.2 - Technology and Design Review)

#### **4. Test Strategy**

##### **A. Types of Testing**

The following types of testing must be reviewed and addressed.

| Item (Testing Type)            | Applicable (Y/N or N/A) | Comments                                                                         |
|:-------------------------------|:------------------------|:---------------------------------------------------------------------------------|
| Functional Testing             | Y                       | Core testing focus - verify all role aggregation scenarios                       |
| Automation Testing             | Y                       | 100% of test scenarios will be automated in openshift-virtualization-tests       |
| Performance Testing            | N/A                     | RBAC checks have negligible performance impact                                   |
| Security Testing               | Y                       | Feature IS a security enhancement - RBAC hardening testing                       |
| Usability Testing              | N/A                     | No UI component - configuration via YAML                                         |
| Compatibility Testing          | Y                       | Backward compatibility verification (default behavior unchanged)                 |
| Regression Testing             | Y                       | Ensure existing RBAC functionality not broken                                    |
| Upgrade Testing                | Y                       | Critical - verify configuration preservation across upgrades                     |
| Backward Compatibility Testing | Y                       | Verify default behavior (opt-out disabled) remains unchanged                     |

##### **B. Potential Areas to Consider**

| Item                   | Description                                         | Applicable (Y/N or N/A) | Comment                                   |
|:-----------------------|:----------------------------------------------------|:------------------------|:------------------------------------------|
| **Dependencies**       | Dependent on deliverables from other components?    | Y                       | See dependencies details below            |
| **Monitoring**         | Does the feature require metrics and/or alerts?     | N/A                     | RBAC feature - no metrics/alerts required |
| **Cross Integrations** | Does the feature affect other features/components?  | Y                       | See cross-integration details below       |
| **UI**                 | Does the feature require UI?                        | N/A                     | No UI - configuration via HCO CR YAML     |

**Dependencies:**
1. Upstream design (CNV-63824) - BLOCKER for test implementation
2. HCO implementation - Dev team
3. Documentation (CNV-63829) - Docs team

**Testing Ownership:**
- **QE tests**: HCO CR configuration, RBAC behavior
- **Dev tests**: HCO operator logic

**Cross Integrations:**
- **Affected**: All kubevirt features requiring VM interaction
- **Testing approach**: Verify RBAC doesn't break existing VM operations when roles are properly assigned
- **Coordination**: sig-virt QE should be aware of RBAC changes

#### **5. Test Environment**

| Environment Component                         | Configuration                  | Specification Examples                                            |
|:----------------------------------------------|:-------------------------------|:------------------------------------------------------------------|
| **Cluster Topology**                          | Standard multi-node or SNO     | Feature works on all topologies, prefer multi-node                |
| **OCP & OpenShift Virtualization Version(s)** | OCP 4.21+ with CNV 4.21+       | Target versions: CNV v4.21.0, CNV v4.22.0                         |
| **CPU Virtualization**                        | N/A                            | Not relevant for RBAC testing                                     |
| **Compute Resources**                         | Standard cluster resources     | Minimum per worker: 4 vCPUs, 16GB RAM                             |
| **Special Hardware**                          | N/A                            | No special hardware required                                      |
| **Storage**                                   | Any RWX storage class          | e.g., OCS, NFS - needed for VM creation tests                     |
| **Network**                                   | Default (OVN-Kubernetes)       | No special network requirements                                   |
| **Required Operators**                        | OpenShift Virtualization (HCO) | Standard CNV installation                                         |
| **Platform**                                  | Any supported platform         | Prefer AWS or bare-metal for CI integration                       |
| **Special Configurations**                    | HTPasswd identity provider     | REQUIRED: Must configure HTPasswd IdP with unprivileged user      |

#### **5.5. Testing Tools & Frameworks**

Document any **new or additional** testing tools, frameworks, or infrastructure required specifically for this feature.

| Category           | Tools/Frameworks                                                             |
|:-------------------|:-----------------------------------------------------------------------------|
| **Test Framework** | Standard: pytest with openshift-virtualization-tests infrastructure          |
| **CI/CD**          | Standard: Jenkins CI lanes, no special pipeline needed                       |
| **Other Tools**    | See existing utilities listed below - no new tools required                  |

**Existing Utilities:**
- `unprivileged_client` fixture (tests/conftest.py:385)
- `ResourceEditorValidateHCOReconcile` (utilities/hco.py)
- `test_migration_rights.py` as reference pattern
- **No new tools required**

#### **6. Entry Criteria**

The following conditions must be met before testing can begin:

- [ ] **BLOCKER**: Upstream design (CNV-63824) is approved and merged
- [ ] **BLOCKER**: HCO CR field name and structure defined in design
- [ ] **BLOCKER**: Development implementation complete (code merged to KubeVirt/HCO)
- [ ] Test environment can be **set up and configured** (see Section II.5 - Test Environment)
- [ ] HTPasswd identity provider configured with unprivileged user
- [ ] Developer Handoff/QE Kickoff meeting completed

#### **7. Risks and Limitations**

Document specific risks and limitations for this feature. If a risk category is not applicable, mark as "N/A" with justification in mitigation strategy.

| Risk Category        | Specific Risk for This Feature                          | Mitigation Strategy                                     | Status     |
|:---------------------|:--------------------------------------------------------|:--------------------------------------------------------|:-----------|
| Timeline/Schedule    | Critical: CNV-63824 not complete, CNV 4.21.0 target     | See timeline mitigation below                           | [x] Active |
| Test Coverage        | Cannot test all ClusterRole combinations exhaustively   | See coverage mitigation below                           | [ ]        |
| Test Environment     | Requires HTPasswd IdP setup                             | See environment mitigation below                        | [ ]        |
| Untestable Aspects   | Limited to HTPasswd, cannot test LDAP/AD/OAuth          | See untestable aspects mitigation below                 | [ ]        |
| Resource Constraints | 1 QE assigned, spans RBAC + HCO + upgrade               | See resource mitigation below                           | [ ]        |
| Dependencies         | Blocking: CNV-63824, Soft: CNV-63829                    | See dependencies mitigation below                       | [x] Active |
| Other                | Upgrade testing needs previous CNV version              | See upgrade mitigation below                            | [ ]        |

**Risk Details and Mitigation:**

**Timeline/Schedule:**
- **Risk**: Upstream design (CNV-63824) not yet complete. Cannot implement tests without knowing HCO CR field structure. Target: CNV 4.21.0
- **Mitigation**: (1) Monitor CNV-63824 progress weekly, (2) Begin test framework setup before design complete, (3) Have test plan ready for rapid implementation

**Test Coverage:**
- **Risk**: Cannot test all possible ClusterRole combinations exhaustively (admin, edit, view, migrate, etc.)
- **Mitigation**: (1) Test critical roles, (2) Use matrix-based testing, (3) Focus on most common user scenarios

**Test Environment:**
- **Risk**: Requires HTPasswd identity provider setup - some CI environments may not support this
- **Mitigation**: (1) Document HTPasswd setup procedure, (2) Ensure CI lanes configured, (3) Use existing `unprivileged_client` infrastructure

**Untestable Aspects:**
- **Risk**: Cannot test with all external identity providers (LDAP, AD, OAuth) - limited to HTPasswd
- **Mitigation**: HTPasswd testing validates core RBAC logic (OCP handles IdP integration). RBAC enforcement is IdP-agnostic.

**Resource Constraints:**
- **Risk**: 1 QE assigned, feature spans RBAC + HCO + upgrade testing
- **Mitigation**: (1) Leverage existing RBAC infrastructure, (2) Automate all scenarios, (3) Reuse HCO utilities

**Dependencies:**
- **Risk**: Blocking dependency: CNV-63824 must complete before test implementation. Soft dependency: CNV-63829 (docs)
- **Mitigation**: (1) Track CNV-63824 weekly, (2) Prepare infrastructure in parallel, (3) Coordinate with docs team

**Upgrade Testing:**
- **Risk**: Requires access to previous CNV version - may need special test environment setup
- **Mitigation**: (1) Use existing upgrade infrastructure, (2) Coordinate with CI team, (3) Document procedure for manual execution

#### **8. Known Limitations**

Document any known limitations, constraints, or trade-offs in the feature implementation or testing approach.

**Testing Limitations:**
- Testing limited to HTPasswd identity provider (does not cover LDAP, Active Directory, OAuth providers)
  - **Rationale**: RBAC logic is identity-provider agnostic; HTPasswd validation is sufficient
- Cannot test in production-scale multi-tenant environments (100+ users, 50+ namespaces)
  - **Rationale**: RBAC overhead is negligible; functional correctness proven with smaller scale
- Upgrade testing from CNV <4.21 will test "opt-out not available" → "opt-out available" scenario only
  - **Rationale**: Feature introduced in 4.21; no prior configuration to preserve

**Feature Limitations** (pending design confirmation):
- TBD based on upstream design (CNV-63824)

---

### **III. Test Scenarios & Traceability**

This section links requirements to test coverage, enabling reviewers to verify all requirements are tested.

| Requirement ID   | Requirement Summary                     | Test Scenario(s)                     | Test Type(s)              | Priority | Polarion ID |
|:-----------------|:----------------------------------------|:-------------------------------------|:--------------------------|:---------|:------------|
| CNV-63822 (Epic) | Opt-out of role aggregation             | Multiple scenarios below             | Functional, Security      | P0       | TBD         |
| Acceptance 1     | Set opt-out in HCO CR                   | See Acceptance 1 details below       | Functional, HCO Reconcile | P0       | CNV-XXXXX   |
| Acceptance 2     | User cannot interact without roles      | See Acceptance 2 details below       | Functional, Security      | P0       | CNV-XXXXX   |
| Acceptance 3     | Explicit RoleBinding grants access      | See Acceptance 3 details below       | Functional, RBAC          | P0       | CNV-XXXXX   |
| Default Behavior | Role aggregation enabled by default     | See Default Behavior details below   | Functional, Backward      | P0       | CNV-XXXXX   |
| Role Testing     | Different ClusterRoles work correctly   | See Role Testing details below       | Functional, RBAC          | P1       | CNV-XXXXX   |
| Multi-Namespace  | RBAC enforced per-namespace             | See Multi-Namespace details below    | Functional, Security      | P1       | CNV-XXXXX   |
| Upgrade Testing  | Configuration preserved across upgrades | See Upgrade Testing details below    | Upgrade, Backward Compat. | P0       | CNV-XXXXX   |
| Fresh Install    | Opt-out works on fresh install          | See Fresh Install details below      | Installation, Functional  | P2       | CNV-XXXXX   |
| Toggle Config    | Changing opt-out on live cluster works  | See Toggle Config details below      | Functional, HCO Reconcile | P1       | CNV-XXXXX   |
| Negative Testing | Proper error messages without perms     | See Negative Testing details below   | Functional, Security      | P2       | CNV-XXXXX   |

**Test Scenario Details:**

**Acceptance 1: Set opt-out in HCO CR**
1. Enable opt-out via HCO CR patch
2. Verify HCO reconciles successfully
3. Verify KubeVirt CR reflects change

**Acceptance 2: Unprivileged user cannot interact with kubevirt resources**
1. With opt-out enabled, unprivileged user tries to create VM → expect ForbiddenError
2. Test delete, start, stop operations → all fail
3. Test console access → fails
4. Test VM migration → fails

**Acceptance 3: Explicit RoleBinding grants access**
1. Create RoleBinding for kubevirt.io:admin role
2. Verify user CAN create/manage VMs
3. Test all VM operations succeed

**Default Behavior: Role aggregation enabled by default**
1. With opt-out disabled (default), namespace admin creates VM → succeeds
2. Verify backward compatibility

**Role Testing: Different kubevirt ClusterRoles work correctly**
1. Test kubevirt.io:admin role (full permissions)
2. Test kubevirt.io:edit role (edit, no admin)
3. Test kubevirt.io:view role (read-only)
4. Test kubevirt.io:migrate role (migrate only)

**Multi-Namespace: RBAC enforced per-namespace**
1. User with RoleBinding in namespace A can access VMs in A
2. Same user cannot access VMs in namespace B (no RoleBinding)
3. Add RoleBinding to namespace B → access granted

**Upgrade Testing: Configuration preserved across upgrades**
1. Upgrade from CNV 4.21 → 4.22 with opt-out enabled
2. Verify configuration preserved
3. Verify RBAC behavior unchanged post-upgrade

**Fresh Install: Opt-out works on fresh install**
1. Install CNV with opt-out enabled from day 1
2. Verify RBAC enforcement works immediately

**Toggle Config: Changing opt-out on live cluster works**
1. Disable opt-out on running cluster with VMs
2. Verify existing VMs unaffected
3. Enable opt-out → verify RBAC enforcement kicks in
4. Verify HCO reconciliation at each step

**Negative Testing: Proper error messages without permissions**
1. Verify ForbiddenError has clear message
2. Test API responses are correct HTTP 403
3. Validate error doesn't leak sensitive info

**Notes:**
- Polarion IDs pending test plan creation in Polarion (CNV-63827)
- All P0 scenarios must be automated and part of CI
- P1/P2 scenarios should be automated but may run in extended test suites

---

### **IV. Sign-off and Approval**

This Software Test Plan requires approval from the following stakeholders:

* **Reviewers:**
  - [QE Lead / @github-username]
  - [sig-iuo representative / @github-username]

* **Approvers:**
  - [QE Manager / @github-username]
  - [Product Manager / @github-username]

**Review Status:**
- [ ] Draft complete
- [ ] QE team reviewed
- [ ] Dev/Arch reviewed (pending CNV-63824 completion)
- [ ] PM approved
- [ ] Ready for implementation
