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

**Document Conventions:**
- **HCO**: HyperConverged Cluster Operator
- **RBAC**: Role-Based Access Control
- **CNV**: Container-native Virtualization (OpenShift Virtualization)

### **Feature Overview**

This feature allows cluster administrators to opt-out of automatic role aggregation for kubevirt-related permissions. When enabled, users will NOT automatically receive kubevirt.io ClusterRoles (admin, edit, view, migrate) and must be explicitly granted these permissions through RoleBindings. This enhances security by implementing the principle of least privilege for VM management operations.

Related enhancement proposals:
- Upstream design: [CNV-63824](https://issues.redhat.com/browse/CNV-63824) (in progress)

---

### **I. Motivation and Requirements Review (QE Review Guidelines)**

This section documents the mandatory QE review process. The goal is to understand the feature's value, technology, and testability prior to formal test planning.

#### **1. Requirement & User Story Review Checklist**

<!-- **How to complete this checklist:**
1. **Done column**: Mark [x] when the check is complete
2. **Details/Notes column**: Summary of the topic (e.g., list key requirements, describe customer value, note acceptance criteria)
3. **Comments column**: Document any concerns, gaps, or follow-up items needed -->

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

#### **2. Technology and Design Review**

<!-- **How to complete this checklist:**
1. **Done column**: Mark [x] when the review is complete
2. **Details/Notes column**: Summary of the item (e.g., list technology challenges, special environment needs, significant API changes)
3. **Comments column**: Note any blockers, risks, or items requiring follow-up -->

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

<!-- Briefly describe what will be tested. The scope must **cover functional and non-functional requirements**.
Must ensure user stories are included and aligned to downstream user stories from Section I. -->

This test plan covers the role aggregation opt-out feature, which allows cluster administrators to disable automatic assignment of kubevirt-related roles to users.

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

- **[P0]** Achieve 100% coverage of acceptance criteria defined in CNV-63822
- **[P0]** Validate all kubevirt.io ClusterRoles (admin, edit, view, migrate) work correctly with opt-out
- **[P0]** Verify backward compatibility - default behavior unchanged when opt-out is not configured
- **[P1]** Automate 100% of functional test scenarios in openshift-virtualization-tests repository
- **[P1]** Create reusable test infrastructure for RBAC testing (fixtures, utilities)

**Out of Scope (Testing Scope Exclusions)**

<!-- Explicitly document what is **out of scope** for testing.
**Critical:** All out-of-scope items require explicit stakeholder agreement to prevent "I assumed you were testing
that" issues; each out-of-scope item must have PM/Lead sign-off.

- Items without stakeholder agreement are considered **risks** and must be escalated
- Review the items during Developer Handoff/QE Kickoff meeting

**Note:** Replace example rows with your actual out-of-scope items. -->

| Out-of-Scope Item                                                 | Rationale                                                                     | PM/ Lead Agreement |
|:------------------------------------------------------------------|:------------------------------------------------------------------------------|:-------------------|
| Testing OpenShift RBAC infrastructure itself                      | Core RBAC functionality is OCP's responsibility, not CNV-specific             | [ ] Name/Date      |
| Performance impact testing of RBAC checks                         | RBAC overhead is negligible and not a concern for this feature                | [ ] Name/Date      |
| Testing on ARM64 or s390x architectures                           | RBAC is architecture-independent, x86_64 coverage is sufficient               | [ ] Name/Date      |
| UI testing for role aggregation configuration                     | Feature is configured via HCO CR (YAML), no UI component exists               | [ ] Name/Date      |
| Testing with external identity providers (LDAP, Active Directory) | Feature testing uses HTPasswd; external IdP testing is infrastructure concern | [ ] Name/Date      |

**Detailed Test Scope**

**In Scope:**
- **Full Regression Testing**:
  - Run complete openshift-virtualization-tests suite with opt-out enabled
  - Verify CNV functionality unaffected by RBAC changes
  - Confirm cluster-admin retains all permissions

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
  - Test permission boundaries for each ClusterRole (admin, edit, view, migrate)

- **Upgrade Testing**:
  - Verify opt-out configuration preserved across CNV z-stream upgrades (4.21.0 → 4.21.1)
  - Validate RBAC behavior unchanged post-upgrade
  - Test both scenarios: with opt-out enabled and disabled

- **HCO Reconciliation**:
  - Verify HCO reconciles correctly when opt-out is configured
  - Validate dependent operators (KubeVirt) reflect changes

**Non-Functional Requirements**:
- **Security**: Core security feature (RBAC hardening) - tested through functional scenarios
- **Backward Compatibility**: Default behavior must remain unchanged
- **Documentation**: Validated through docs review (CNV-63829)

#### **2. Test Strategy**

<!-- The following test strategy considerations must be reviewed and addressed. Mark "Y" if applicable,
"N/A" if not applicable (with justification in Comments). Empty cells indicate incomplete review. -->

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

#### **3. Test Environment**

<!-- **Note:** "N/A" means explicitly not applicable. Cannot leave empty cells. -->

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

#### **3.1. Testing Tools & Frameworks**

<!-- Document any **new or additional** testing tools, frameworks, or infrastructure required specifically
for this feature. **Note:** Only list tools that are **new** or **different** from standard testing infrastructure.
Leave empty if using standard tools. -->

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

#### **4. Entry Criteria**

The following conditions must be met before testing can begin:

- [ ] Requirements and design documents are **approved and merged**
- [ ] **BLOCKER**: Upstream design (CNV-63824) is approved and merged
- [ ] **BLOCKER**: HCO CR field name and structure defined in design
- [ ] **BLOCKER**: Development implementation complete (code merged to KubeVirt/HCO)
- [ ] Test environment can be **set up and configured** (see Section II.3 - Test Environment)
- [ ] HTPasswd identity provider configured with unprivileged user
- [ ] Developer Handoff/QE Kickoff meeting completed

#### **5. Risks**

<!-- Document specific risks for this feature. If a risk category is not applicable, mark as "N/A" with
justification in mitigation strategy.

**Note:** Empty "Specific Risk" cells mean this must be filled. "N/A" means explicitly not applicable
with justification. -->

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

#### **6. Known Limitations**

<!-- Document any known limitations, constraints, or trade-offs in the feature implementation or testing approach. -->

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

<!-- This section links requirements to test coverage, enabling reviewers to verify all requirements are
tested. -->

<!-- **Requirement ID:**
- Use Jira issue key (e.g., CNV-12345)
- Each row should trace back to a specific testable requirement in Jira

**Requirement Summary:** Brief description from the Jira issue (user story format preferred) -->

| Requirement ID       | Requirement Summary                                  | Test Scenario(s)                              | Tier  | Priority |
|:---------------------|:-----------------------------------------------------|:----------------------------------------------|:------|:---------|
| CNV-63822 (Epic)     | Opt-out of role aggregation                          | Multiple scenarios below                      | N/A   | P0       |
| Full Regression      | CNV functionality unaffected by opt-out              | See Full Regression details below             | tier2 | P0       |
| Acceptance 1         | Set opt-out in HCO CR                                | See Acceptance 1 details below                | tier2 | P0       |
| Acceptance 2         | User cannot interact without roles                   | See Acceptance 2 details below                | tier2 | P0       |
| Acceptance 3         | Explicit RoleBinding grants access                   | See Acceptance 3 details below                | tier2 | P0       |
| Default Behavior     | Role aggregation enabled by default                  | See Default Behavior details below            | tier2 | P0       |
| Role Testing         | Different ClusterRoles work correctly                | See Role Testing details below                | tier2 | P1       |
| Multi-Namespace      | RBAC enforced per-namespace                          | See Multi-Namespace details below             | tier2 | P1       |
| Upgrade Testing      | Configuration preserved across upgrades              | See Upgrade Testing details below             | tier2 | P0       |

**Test Scenario Details:**

**Summary of New Tests Based on Existing Patterns:**

The opt-out feature tests follow the **exact same pattern** as existing RBAC tests in `test_migration_rights.py`:

| ClusterRole | Negative Test (without RoleBinding) | Positive Test (with RoleBinding) | Reference |
|:------------|:------------------------------------|:---------------------------------|:----------|
| **kubevirt.io:migrate** | ✅ Already exists (CNV-11968) | ✅ Already exists (CNV-11967) | `test_migration_rights.py` |
| **kubevirt.io:admin** | ➕ NEW: Cannot create VM | ➕ NEW: Can create VM with RoleBinding | Pattern: CNV-11968 |
| **kubevirt.io:edit** | ➕ NEW: Cannot start/stop VM | ➕ NEW: Can start/stop with RoleBinding | Pattern: CNV-11968 |
| **kubevirt.io:view** | ➕ NEW: Cannot view VMs | ➕ NEW: Can view with RoleBinding | Pattern: CNV-11968 |

**Code references:**
- Fixture pattern: `test_migration_rights.py:18-29` (unprivileged_user_migrate_rolebinding)
- Negative test pattern: `test_migration_rights.py:46-50` (CNV-11968)
- Positive test pattern: `test_migration_rights.py:53-57` (CNV-11967)
- Utilities: `utilities/virt.py` (VirtualMachineForTests, running_vm, migrate_vm_and_verify)
- Constants: `utilities/constants.py` (UNPRIVILEGED_USER)

**Implementation Steps for New Tests:**

1. **Create test file:** `tests/virt/cluster/rbac_hardening/test_role_aggregation_opt_out.py`

2. **Create opt-out fixture** (setup/teardown for HCO CR):
   ```python
   @pytest.fixture(scope="module")
   def role_aggregation_opt_out_enabled(admin_client, hyperconverged_resource_scope_module):
       """Enable opt-out (disable role aggregation) - restores default on teardown"""
       with ResourceEditorValidateHCOReconcile(
           patches={
               hyperconverged_resource_scope_module: {
                   "spec": {
                       "roleAggregation": {"enabled": false}  # ← Field TBD from CNV-63824
                   }
               }
           },
           wait_for_reconcile_post_update=True,
           admin_client=admin_client,
       ):
           yield  # ← Tests run here with opt-out ENABLED
       # ← Teardown: ResourceEditorValidateHCOReconcile restores original config
   ```
   - Reference: `utilities/hco.py` → ResourceEditorValidateHCOReconcile
   - Context manager automatically reverts changes on exit (teardown)

3. **Copy RoleBinding fixture pattern** from `test_migration_rights.py:18-29`, adapt for each role:
   - `unprivileged_user_admin_rolebinding` → role_ref_name="kubevirt.io:admin"
   - `unprivileged_user_edit_rolebinding` → role_ref_name="kubevirt.io:edit"
   - `unprivileged_user_view_rolebinding` → role_ref_name="kubevirt.io:view"

4. **Create negative tests** (without RoleBinding):
   - All tests use `role_aggregation_opt_out_enabled` fixture
   - `test_unprivileged_cannot_create_vm()` → admin role
   - `test_unprivileged_cannot_start_stop_vm()` → edit role
   - `test_unprivileged_cannot_view_vm()` → view role

5. **Create positive tests** (with RoleBinding):
   - All tests use `role_aggregation_opt_out_enabled` fixture
   - `test_unprivileged_can_create_vm_with_admin_binding()` → uses unprivileged_user_admin_rolebinding
   - `test_unprivileged_can_start_stop_with_edit_binding()` → uses unprivileged_user_edit_rolebinding
   - `test_unprivileged_can_view_with_view_binding()` → uses unprivileged_user_view_rolebinding

6. **Mark tests appropriately:**
   - `@pytest.mark.polarion("CNV-XXXXX")` (get IDs from Polarion)
   - `@pytest.mark.tier2` (for P0/P1 tests)
   - `@pytest.mark.gating` (for P0 acceptance criteria)

---

**Full Regression: CNV functionality unaffected by opt-out**
1. Fresh install CNV with opt-out ENABLED from day 1 (role aggregation DISABLED)
2. Execute complete openshift-virtualization-tests regression suite
3. Verify 0 test failures related to opt-out configuration
4. Confirm:
   - All CNV operators deploy successfully
   - cluster-admin can perform all VM operations
   - Service accounts have necessary permissions
   - VM lifecycle operations work (create, start, stop, migrate, delete)
   - All CNV features functional (hotplug, storage, network, etc.)

**CI Integration Question:**
- **OPEN**: How to integrate this into CI? Run full regression on cluster with opt-out enabled?
- **To be answered by**: QE Lead
- **Options to consider**:
  - Dedicated CI lane with opt-out enabled from installation
  - Periodic job (nightly/weekly) running full suite with opt-out
  - Add to existing lanes as environment variant

**Acceptance 1: Set opt-out in HCO CR**
1. Enable opt-out via HCO CR patch
2. Verify HCO reconciles successfully
3. Verify KubeVirt CR reflects change

**Acceptance 2: Unprivileged user cannot interact with kubevirt resources**

**Pattern reference:** `tests/virt/cluster/migration_and_maintenance/rbac_hardening/test_migration_rights.py`

Test that with opt-out ENABLED (role aggregation DISABLED), unprivileged users without explicit RoleBindings receive ForbiddenError:

1. **Test: Unprivileged user cannot create VM (negative test)**
   - Setup: opt-out enabled, unprivileged_client without RoleBindings
   - Action: `VirtualMachineForTests(client=unprivileged_client, ...)`
   - Expected: `pytest.raises(ForbiddenError)` ← Similar to CNV-11968 pattern
   - Verifies: kubevirt.io:admin NOT auto-aggregated

2. **Test: Unprivileged user cannot start/stop VM (negative test)**
   - Setup: VM created by admin, unprivileged_client without RoleBindings
   - Action: `vm.start()`, `vm.stop()` with unprivileged_client
   - Expected: `pytest.raises(ForbiddenError)`
   - Verifies: kubevirt.io:edit NOT auto-aggregated

3. **Test: Unprivileged user cannot view VMs (negative test)**
   - Setup: VM exists in namespace, unprivileged_client without RoleBindings
   - Action: `VirtualMachine.get(client=unprivileged_client, ...)`
   - Expected: `pytest.raises(ForbiddenError)` or empty list
   - Verifies: kubevirt.io:view NOT auto-aggregated

4. **Test: Unprivileged user cannot migrate VM (negative test)**
   - Already covered by existing CNV-11968
   - Verifies: kubevirt.io:migrate behavior unchanged

**Acceptance 3: Explicit RoleBinding grants access**

**Pattern reference:** `tests/virt/cluster/migration_and_maintenance/rbac_hardening/test_migration_rights.py` (CNV-11967)

Test that with opt-out ENABLED, explicit RoleBindings restore functionality:

1. **Test: kubevirt.io:admin RoleBinding allows VM creation**
   ```python
   # Fixture pattern from test_migration_rights.py:18-29
   @pytest.fixture()
   def unprivileged_user_admin_rolebinding(admin_client, namespace):
       with RoleBinding(
           name="role-bind-kubevirt-admin",
           namespace=namespace.name,
           subjects_kind="User",
           subjects_name=UNPRIVILEGED_USER,
           role_ref_kind=ClusterRole.kind,
           role_ref_name="kubevirt.io:admin",
       ) as role_binding:
           yield role_binding

   # Test
   def test_unprivileged_user_can_create_vm_with_admin_rolebinding(
       unprivileged_client,
       unprivileged_user_admin_rolebinding
   ):
       with VirtualMachineForTests(client=unprivileged_client, ...) as vm:
           running_vm(vm=vm)  # Should succeed
   ```

2. **Test: kubevirt.io:edit RoleBinding allows start/stop operations**
   - Similar fixture pattern for kubevirt.io:edit
   - Verify unprivileged user CAN start/stop existing VM
   - Reference: `utilities/virt.py` → `running_vm()`, `vm.stop()`

3. **Test: kubevirt.io:view RoleBinding allows read-only access**
   - Similar fixture pattern for kubevirt.io:view
   - Verify unprivileged user CAN list/get VMs
   - Verify unprivileged user CANNOT modify VMs (still ForbiddenError)

4. **Test: kubevirt.io:migrate RoleBinding allows migration**
   - Already covered by existing CNV-11967
   - Verifies: Explicit RoleBinding works as before

**Default Behavior: Role aggregation enabled by default**
1. With opt-out disabled (default), namespace admin creates VM → succeeds
2. Verify backward compatibility

**Role Testing: Different kubevirt ClusterRoles work correctly**

**Note:** This extends Acceptance 2 & 3 to test role boundaries and permission matrices.

Test permission boundaries for each ClusterRole:

1. **kubevirt.io:admin - Full VM management**
   - CAN: create, delete, start, stop, restart, migrate VMs
   - CAN: hotplug resources, access console
   - Reference operations: All from `utilities/virt.py`

2. **kubevirt.io:edit - VM lifecycle without admin ops**
   - CAN: start, stop, restart VMs
   - CAN: hotplug resources, access console
   - CANNOT: create or delete VMs (should be ForbiddenError)
   - Verify edit < admin permissions

3. **kubevirt.io:view - Read-only access**
   - CAN: list VMs, get VM details
   - CANNOT: Any modification operations (ForbiddenError)
   - Verify view is strictly read-only

4. **kubevirt.io:migrate - Migration-only permissions**
   - CAN: migrate VMs only
   - CANNOT: create, delete, start, stop VMs
   - Already tested in CNV-11967/CNV-11968
   - Verify migrate is isolated permission

**Multi-Namespace: RBAC enforced per-namespace**
1. User with RoleBinding in namespace A can access VMs in A
2. Same user cannot access VMs in namespace B (no RoleBinding)
3. Add RoleBinding to namespace B → access granted

**Upgrade Testing: Configuration preserved across upgrades**

**Pattern reference:** `tests/install_upgrade_operators/product_upgrade/conftest.py` (before_upgrade fixtures)

Test that opt-out configuration is preserved across CNV z-stream upgrades (e.g., 4.21.0 → 4.21.1):

**Setup (before upgrade):**
1. Enable opt-out in HCO CR (role aggregation DISABLED)
2. Capture HCO configuration before upgrade:
   ```python
   @pytest.fixture(scope="session")
   def hco_role_aggregation_config_before_upgrade(hyperconverged_resource_scope_session):
       """Capture opt-out configuration before upgrade"""
       return hyperconverged_resource_scope_session.instance.to_dict()["spec"].get(
           "roleAggregation", {"enabled": True}  # Default if not present
       )
   ```

**During upgrade:**

3. Perform CNV z-stream upgrade (4.21.0 → 4.21.1) using existing upgrade fixtures: `upgraded_cnv`, `approved_cnv_upgrade_install_plan` (Reference: `test_upgrade.py:47-85` - CNV-2991)

**Post-upgrade verification:**
4. **Test: Opt-out configuration preserved**
   ```python
   @pytest.mark.post_upgrade
   @pytest.mark.polarion("CNV-XXXXX")
   def test_role_aggregation_opt_out_preserved_after_upgrade(
       hyperconverged_resource_scope_session,
       hco_role_aggregation_config_before_upgrade,
   ):
       """Verify opt-out config unchanged after upgrade"""
       current_config = hyperconverged_resource_scope_session.instance.to_dict()["spec"].get(
           "roleAggregation", {"enabled": True}
       )
       assert current_config == hco_role_aggregation_config_before_upgrade, (
           f"Role aggregation config changed after upgrade: "
           f"before={hco_role_aggregation_config_before_upgrade}, after={current_config}"
       )
   ```

5. **Test: RBAC behavior unchanged post-upgrade**
   - Rerun Acceptance 2 tests (negative tests without RoleBinding)
   - Verify unprivileged users still receive ForbiddenError
   - Confirms opt-out functionality still works, not just config preserved

**Test scenarios:**
- **Z-stream upgrade with opt-out ENABLED** (4.21.0 → 4.21.1):
  - Config preserved: `roleAggregation.enabled: false`
  - RBAC behavior: Users still need explicit RoleBindings

- **Z-stream upgrade with opt-out DISABLED** (default):
  - Config preserved: `roleAggregation.enabled: true` (or field absent)
  - RBAC behavior: Users still get automatic role aggregation

**Notes:**
- Polarion IDs pending test plan creation in Polarion (CNV-63827)
- All P0 scenarios must be automated and part of CI
- P1 scenarios should be automated but may run in extended test suites

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
