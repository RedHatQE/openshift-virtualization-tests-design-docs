# Openshift-virtualization-tests Test plan

## **Clone and Storage Migration support for VMState PVC - Quality Engineering Plan**

### **Metadata & Tracking**

- **Enhancement(s):** [KubeVirt VEP #312](https://github.com/kubevirt/enhancements/issues/312), [CNV-85157](https://redhat.atlassian.net/browse/CNV-85157)
- **Feature Tracking:** N/A — no feature-level parent is assigned in Jira.
- **Epic Tracking:** [CNV-79308](https://redhat.atlassian.net/browse/CNV-79308)
- **Feature Maturity:**
  - DP: CNV v5.1.0
  - TP: CNV v5.2.0
  - GA: CNV v5.3.0
- **QE Owner(s):** [Emanuele Prella](@ema-aka-young)
- **Owning SIG:** sig-storage
- **Participating SIGs:** N/A

**Document Conventions (if applicable):**

- **VMState PVC:** A persistent storage volume that holds virtual machine state such as vTPM, EFI, and change-tracking data.
- **vTPM:** Virtual Trusted Platform Module.
- **EFI:** Extensible Firmware Interface.
- **MTC:** Migration Toolkit for Containers.
- **Source storage:** The storage class or volume used before a clone or migration operation.

### **Feature Overview**

OpenShift Virtualization will preserve captured vTPM and EFI state when users clone a virtual machine or migrate its storage. This matters because security and boot state can be required for guest continuity, and losing or sharing that state can make a cloned or migrated VM unusable. The feature covers independent clone storage, state relocation, and continued use of the target volume, including during Windows live storage conversion. Snapshot-based clones with uncaptured state follow the rejection or warning and fresh-state behavior in Known Limitations. This plan targets the proposed CNV v5.1.0 Developer Preview.

---

### **I. Motivation and Requirements Review (QE Review Guidelines)**

#### **1. Requirement & User Story Review Checklist**

- [x] **Review Requirements**
  - *List the key D/S requirements reviewed:*
    - VM clones work with VMState PVC.
    - Migrate storage of VMState PVC is supported.
    - Captured vTPM and EFI state must remain usable after clone or migration; uncaptured snapshot state follows the documented fallback boundary.
    - Migrated VMs must not retain a dependency on source storage.

- [x] **Understand Value and Customer Use Cases**
  - *Describe the feature's value to customers:* Customers can clone captured security/boot state or relocate persistent state without losing it or accidentally sharing it between VMs; uncaptured-state snapshots report the limitation instead of silently reusing the source.
  - *List the customer use cases identified:*
    - As a VM owner, I want to clone a VM with captured vTPM or EFI state so that the clone starts with the same trusted state.
    - As a VM owner, I want to move a VM to another storage class so that all of its volumes, including VMState PVC, move together.
    - As a cluster administrator, I want live storage conversion to move Windows guest disks and VMState to the target storage class so that the VM can continue using its saved state there.

- [x] **Testability**
  - *Note any requirements that are unclear or untestable:* The two acceptance criteria are testable. The epic does not state a performance, scale, monitoring, or UI requirement.

- [x] **Acceptance Criteria**
  - *List the acceptance criteria:*
    - A clone with captured VMState can read the source VM's saved vTPM-protected data and EFI variables and uses a separate VMState PVC.
    - After storage migration, the VM uses a VMState PVC on the target storage class and reports it as the active state volume.
  - *Note any gaps or missing criteria:* The epic does not define expected behavior for clone or migration failure or concurrent use of the same VMState PVC. The linked implementation and bug reports inform those checks.

- [x] **Non-Functional Requirements (NFRs)**
  - *List applicable NFRs and their targets:*
    - Security and integrity: captured vTPM and EFI state remains usable after clone or relocation; concurrent writers cannot share the same VMState PVC.
    - Compatibility and reliability: source adoption, clone and relocation preserve saved guest state. Failed operations preserve the original volume and state.
    - Observability: users can identify the active state volume and distinguish unavailable state, exclusive-use rejection and fresh-state fallback through VM status or warning events.
    - Documentation: review release notes and existing clone/migration caveats against delivered behavior, including legacy-source, uncaptured-state, and storage-conversion boundaries. Complete the review tracked by CNV-79311 and CNV-79315 before final sign-off.
  - *Note any NFRs not covered and why:*
    - Performance and scale benchmarking have no feature-specific targets. Functional migration checks respect the cluster's configured parallelism and storage capacity limits.
    - Monitoring introduces no new metrics or alerts; user-visible state and failure reporting is checked functionally.
    - OpenShift web console workflows and accessibility are proposed exclusions in II.1. Functional checks cover API status and errors.

#### **2. Known Limitations**

- **RWO VMState PVC referenced only by source cannot live-migrate without a volume claim template**
  - *Sign-off:* [Name/Date]

- **Declarative VMState storage requires Filesystem volume mode**
  - *Sign-off:* [Name/Date]

- **An existing implicit-state VM cannot be converted in place by adding declarative state configuration**
  - A new or recreated VM may adopt its released legacy PVC.
  - *Sign-off:* [Name/Date]

- **Legacy implicit-state cloning is blocked until the CNV-100645 fix is included in the tested build**
  - [CNV-100645](https://redhat.atlassian.net/browse/CNV-100645) tracks the implicit-source to declarative-target clone failure. [KubeVirt PR #19814](https://github.com/kubevirt/kubevirt/pull/19814) was open and unmerged in the retained November 17 review evidence; inclusion must be checked before execution.
  - *Sign-off:* [Name/Date]

- **A snapshot cannot preserve state it did not capture**
  - Restoring to a different VM is rejected without a volume claim template. With a template, the user receives a warning and the target starts with fresh, independent state rather than the source TPM/EFI state.
  - *Sign-off:* [Name/Date]

#### **3. Technology and Design Review**

- [x] **Developer Handoff/QE Kickoff**
  - *Key takeaways and concerns:* QE reviewed the declarative VMState design in CNV-85157 and the implementation story CNV-98256 during design and implementation. The main concern is proving that state is copied, not shared, and that the VM is repointed to the target volume after migration.

- [x] **Technology Challenges**
  - *List identified challenges:* Persistent vTPM and EFI state is security- and boot-sensitive, storage behavior differs across storage classes, and Windows live storage conversion must coordinate disk migration with VMState relocation.
  - *Impact on testing approach:* Compare saved guest vTPM-protected data and EFI variables to verify state preservation. Cover direct and snapshot clones from declarative and, once the fix is delivered, legacy sources. For Windows live conversion, the migration plan supplies the guest-disk destinations and the VM's volume claim template supplies the RWO VMState destination. Ordinary RWX compute migration may reuse the shared state volume.

- [x] **API Extensions**
  - *List new or modified APIs:* The declarative VMState API lets users reference an existing PVC or request one through a volume claim template, and VM status reports the active VMState volume.
  - *Testing impact:* Cover released-source adoption and missing-source reporting, target creation, active-volume reporting, and continued use of the correct volume after clone or relocation. Reuse existing feature-level contracts for Linux adoption, exclusive use, and missing-source errors.

- [x] **Test Environment Needs**
  - *See environment requirements in Section II.3 and testing tools in Section II.3.1*

- [x] **Topology Considerations**
  - *Describe topology requirements:* Use an OpenShift Virtualization cluster with two distinct supported storage classes and schedulable source and destination nodes for live migration.
  - *Impact on test design:* Clone and storage-migration scenarios can share cluster setup. Windows live conversion uses the KubeVirt Migration Controller and the Windows guest in Section II.3. Its Tier 3 cases are required coverage.

### **II. Software Test Plan (STP)**

#### **1. Scope of Testing**

**Testing Goals**

- **[P0]** As a VM owner, verify that Linux and Windows direct and snapshot clones with captured state preserve vTPM/EFI state on independent storage for declarative and supported legacy sources.
- **[P0]** As a VM owner, verify that RWO state relocation and Windows live storage conversion use the target storage class and preserve saved vTPM and EFI state.
- **[P1]** As a VM owner, verify that a migrated VM has no dependency on source storage.
- **[P1]** As a VM owner, verify that failed clone or migration operations preserve original state and that uncaptured-state clones reject or warn and initialize independent fresh state according to template availability.
- **[P1]** As a VM owner, verify that Linux and Windows can adopt released state with saved guest state and that unavailable or concurrently used state produces an actionable startup error.

**Out of Scope (Testing Scope Exclusions)**

- **Performance and scale benchmarking**
  - *Rationale:* Jira and the design evidence define no latency, throughput, or scale target for this feature.
  - *PM/Lead Agreement:* [Name/Date]

- **Broad Windows guest coverage**
  - *Rationale:* Windows VMState cloning, clone isolation, adoption and storage conversion are included in this plan. Existing platform coverage owns the broader Windows version and application matrix.
  - *PM/Lead Agreement:* [Name/Date]

- **Platform storage-class functionality**
  - *Rationale:* OpenShift storage-class provisioning and basic PVC binding are platform capabilities; this plan tests virtualization behavior when using those classes.
  - *PM/Lead Agreement:* [Name/Date]

- **OpenShift web console workflows and accessibility**
  - *Rationale:* The plan validates the scoped VMState workflows through the API, including active-volume status, rejection errors and warnings for uncaptured state.
  - *PM/Lead Agreement:* [Name/Date]

- **Legacy MTC storage-conversion reproduction**
  - *Rationale:* [CNV-83112](https://redhat.atlassian.net/browse/CNV-83112) was closed as Won't Do. TS-011 covers the reported split-storage failure through KubeVirt live storage conversion.
  - *PM/Lead Agreement:* [Name/Date]

**Test Limitations**

- **Source-storage fault injection is restricted to isolated, disposable storage**
  - Qualify a source-volume disconnect or equivalent scoped fault that leaves target storage available before running the source-independence case. Confirm the source is inaccessible and the migrated guest can still use its saved state; reference inspection alone is not a substitute.
  - *Sign-off:* [Name/Date]

#### **2. Test Strategy**

**Functional**

- [x] **Functional Testing** — Validates that the feature works according to specified requirements and user stories
  - *Details:* Cover VM clone, native storage relocation, Windows live storage conversion, persistent-state usability, target-volume reference, and source-storage independence.

- [x] **Automation Testing** — Confirms test automation plan is in place for CI and regression coverage (all tests are expected to be automated)
  - *Details:* Reuse Tier 1 Go/Ginkgo feature contracts in kubevirt/kubevirt for Linux adoption, exclusive use, and missing-source reporting. Automate Tier 2 Linux workflows and Tier 3 Windows workflows in RedHatQE/openshift-virtualization-tests. Execute all Tier 3 clone, isolation, live conversion success and failure, and adoption cases before final sign-off. Reuse Windows vTPM/BitLocker setup where applicable and extend existing migration tests with the missing VMState assertions. Partial-coverage tags identify existing automation to extend. All new scenarios are intended for automation.

- [x] **Regression Testing** — Verifies that new changes do not break existing functionality
  - *Details:* Extend the existing Windows vTPM storage-migration coverage with VMState PVC placement, active reference, and saved vTPM and EFI assertions. Retain existing boot-time, data-integrity, and disk storage-class checks.

- [ ] **Self-Validation Testing** — Should any of the new tests be included in the self-validation test package?
  - *Details:* No new package inclusion is proposed for the multi-operation clone/relocation workflows. Tier 1 adoption and reporting reuse existing feature checks. Curated downstream self-validation package membership is a separate selection decision.

**Non-Functional**

- [ ] **Performance Testing** — Validates feature performance meets requirements (latency, throughput, resource usage)
  - *Details:* Not applicable; no performance target is defined.

- [ ] **Scale Testing** — Validates feature behavior under increased load and at production-like scale (e.g., large number of VMs, nodes, or concurrent operations)
  - *Details:* No new scale benchmark is specified; see II.1's benchmarking exclusion. Functional execution must respect the installed cluster's migration parallelism and available storage capacity; no new concurrency limit is invented.

- [x] **Security Testing** — Verifies security requirements, RBAC, authentication, authorization, and vulnerability scanning
  - *Details:* Verify captured vTPM and EFI state remains usable after clone or relocation, uncaptured-state fallback creates independent fresh state, and concurrent VM use of the same VMState PVC is rejected.

- [ ] **Usability Testing** — Validates user experience and accessibility requirements
  - *Details:* See II.1 for the proposed OpenShift web console exclusion. Functional tests verify active-volume status, missing and in-use errors, and warnings for uncaptured state through the API.

- [ ] **Monitoring** — Does the feature require metrics and/or alerts?
  - *Details:* Not applicable; no new metric or alert requirement is defined.

**Integration & Compatibility**

- [x] **Compatibility Testing** — Ensures feature works across supported platforms, versions, and configurations
  - *Details:* Validate clone, native storage relocation, and Windows live storage conversion with distinct source and target storage classes.

- [ ] **Upgrade Testing** — Validates upgrade paths from previous versions, data migration, and configuration preservation
  - *Details:* Deferred for Developer Preview. Consider Linux and Windows VMState preservation, clone, and relocation after upgrade in Technology Preview or a later phase once a supported upgrade path is defined.

- [ ] **Dependencies** — Blocked by deliverables from other components/products. Identify what we need from other teams before we can test.
  - *Details:* Not applicable; no additional team delivery is required for the planned scenarios.

- [x] **Cross Integrations** — Does the feature affect other features or require testing by other teams? Identify the impact we cause.
  - *Details:* Cover VMState across clone, snapshot restore, native storage relocation, and Windows live storage conversion using the KubeVirt Migration Controller.

**Infrastructure**

- [ ] **Cloud Testing** — Does the feature require multi-cloud platform testing? Consider cloud-specific features.
  - *Details:* Not applicable; no cloud-specific behavior is defined. Storage-class compatibility is covered on the standard test platform.

#### **3. Test Environment**

- **Cluster Topology:** Planned three control-plane nodes and three worker nodes, with at least two schedulable workers for live migration.
- **OCP & OpenShift Virtualization Version(s):** Target CNV v5.1.0 from Jira. Qualify the exact CNV build and supported OCP release before execution.
- **CPU Virtualization:** VT-x (Intel) or AMD-V enabled
- **Compute Resources:** Minimum per worker node: 8 vCPUs, 32GB RAM
- **Special Hardware:** N/A - no special hardware needed.
- **Storage:** Two distinct supported source/target StorageClasses; concrete names and provisioners are not selected. Qualify Filesystem mode, required RWO access, capacity/binding behavior and VMState snapshot capability for direct/snapshot clones; verify any RWX coverage separately from actual storage-class relocation. ODF is a candidate, not a qualified selection.
- **Network:** OVN-Kubernetes, IPv4
- **Required Operators:** OpenShift Virtualization with the KubeVirt Migration Operator and its controller available for Windows live storage conversion.
- **Platform:** Bare metal or virtualized. Qualify the selected cluster for the planned storage and migration workflows.
- **Special Configurations:** Enable DeclarativeVMState and use Linux and Windows guests with persistent vTPM and EFI. For RWO relocation, adopt a VMState PVC from the source class and set the target class in the volume claim template. Use a [KubeVirt migration plan](https://github.com/kubevirt/kubevirt-migration-controller/blob/main/api/migrationcontroller/v1alpha1/virtualmachinestoragemigrationplan_types.go) for Windows guest disks.

#### **3.1. Testing Tools & Frameworks**

- **Test Framework:** Standard
- **CI/CD:** N/A - no specific consideration on CI/CD.
- **Other Tools:** N/A - no specific tools involved.

#### **4. Entry Criteria**

- [x] Requirements and design documents are **approved and merged**
- [ ] Qualify and configure the test environment in II.3, including Windows live conversion with declarative RWO VMState.
- [ ] Verify the build includes the CNV-100645 fix before running legacy clone cases.
- [ ] Qualify the isolated source-storage fault before running the source-independence case.

#### **5. Risks**

**Timeline/Schedule**

- **Mitigation:** No risk identified — execute all scoped Tier 2 and Tier 3 cases before final sign-off; Tier 3 execution has no identified separate schedule limitation.

**Test Coverage**

- **Risk:** Existing Windows vTPM migration tests can pass while VMState remains on source storage or saved guest state is lost.
  - **Mitigation:** Verify placement and active reference in TS-008, TS-009 and TS-011. Compare saved vTPM and EFI state after relocation and during failure recovery. Prove source independence in TS-010 using the qualified isolated fault.
  - *Areas with reduced coverage:* Existing automation lacks VMState-specific assertions. Add and execute native and Windows live conversion success and failure checks, including TS-011 and TS-014, and the Windows clone and adoption checks before final sign-off.
  - *Sign-off:* [Name/Date]

**Test Environment**

- **Risk:** Differences in storage and snapshot capabilities across the selected configurations could produce unsupported clone or migration results.
  - **Mitigation:** Qualify the source/target storage capabilities and guest images listed in II.3 before executing the planned Tier 2 and Tier 3 cases.
  - *Missing resources or infrastructure:* No Tier 3 capacity shortage has been identified; concrete environment selections still require qualification as listed in II.3.
  - *Sign-off:* [Name/Date]

**Untestable Aspects**

- **Risk:** Source-independence evidence may remain incomplete if the isolated fault-injection capability is not qualified before execution.
  - **Mitigation:** Meet the isolation constraint in Test Limitations before this case starts; schedule a disposable source/target environment and prove that the selected fault makes source state inaccessible while target state remains usable. Keep the entry criterion open until that qualification succeeds.
  - *Alternative validation approach:* Use a scoped source-volume disconnect. If no safe scoped fault can be qualified, the source-independence case remains unexecuted and requires an explicit coverage decision before sign-off.
  - *Sign-off:* [Name/Date]

**Resource Constraints**

- **Mitigation:** No risk identified — the planned Tier 3 coverage has no identified resource constraint. Execute the Windows live conversion success and failure scenarios before final sign-off.

**Dependencies**

- **Risk:** A selected build may finish Windows disk conversion without moving VMState if the operation falls back to offline disk migration or the state volume configuration differs from the live RWO path.
  - **Mitigation:** In TS-011, observe the VM stay running from the start of live conversion through completion and confirm the Windows guest boot time is unchanged. Verify that the guest disks and VMState are on the target class, VM status shows the active target state volume, and saved vTPM and EFI state remains usable. Fail TS-011 if conversion completes with VMState still active on source storage. In TS-014, exercise failure before handoff and verify that the original VM can use its saved state.
  - *Dependent teams or components:* KubeVirt Migration Controller and OpenShift Virtualization live migration
  - *Sign-off:* [Name/Date]

- **Risk:** The legacy-clone fix may not be present in the selected CNV v5.1.0 build in time for validation; see Known Limitations for the current product constraint.
  - **Mitigation:** Check the CNV-100645 fix inclusion before legacy-source clone execution. Keep its build entry criterion open until delivered; if delivery misses execution approval, agree a documented scope/priority change with PM/Lead rather than count the variant as covered.
  - *Dependent teams or components:* CNV-100645 delivery in the selected build
  - *Sign-off:* [Name/Date]

---

### **III. Test Scenarios & Traceability**

- **[REQ-CNV-79308-01]** — As a VM owner, I want VM clones to work with VMState PVC.
  - *Test Scenario:* **TS-001**: [Tier 2] Verify Linux clone preserves vTPM security and EFI state
    - *Priority:* P0
  - *Test Scenario:* **TS-002**: [Tier 2] Verify clone uses a separate VMState PVC
    - *Priority:* P0
  - *Test Scenario:* **TS-003**: [Tier 2] Verify source vTPM and EFI remain usable after clone failure
    - *Priority:* P1
  - *Test Scenario:* **TS-004**: [Tier 2] Verify uncaptured-state clone rejects without a template
    - *Priority:* P1
  - *Test Scenario:* **TS-005**: [Tier 2] Verify uncaptured-state clone warns and initializes independent fresh state
    - *Priority:* P1
  - *Test Scenario:* **TS-006**: [Tier 3] Verify Windows clones preserve saved vTPM and EFI state
    - *Priority:* P0
  - *Test Scenario:* **TS-007**: [Tier 3] Verify Windows clone changes leave source vTPM and EFI unchanged
    - *Priority:* P1

- **[REQ-CNV-79308-02]** — As a VM owner, I want to migrate storage of VMState PVC.
  - *Test Scenario:* **TS-008**: [Tier 2] [PARTIAL_COVERAGE] Verify RWO VMState reaches target storage with saved vTPM and EFI
    - *Priority:* P0
  - *Test Scenario:* **TS-009**: [Tier 2] [PARTIAL_COVERAGE] Verify VM references migrated VMState PVC
    - *Priority:* P0
  - *Test Scenario:* **TS-010**: [Tier 2] Verify relocated vTPM and EFI remain usable with source storage inaccessible
    - *Priority:* P1
  - *Test Scenario:* **TS-011**: [Tier 3] Verify Windows live conversion preserves vTPM and EFI without stopping or restarting the VM
    - *Priority:* P0
  - *Test Scenario:* **TS-012**: [Tier 1] [EXISTING_COVERAGE] Verify concurrent startup reports VMState PVC in-use rejection
    - *Priority:* P1
  - *Test Scenario:* **TS-013**: [Tier 2] Verify failed migration keeps original vTPM and EFI usable
    - *Priority:* P1
  - *Test Scenario:* **TS-014**: [Tier 3] Verify failed Windows conversion keeps original vTPM and EFI usable
    - *Priority:* P1

- **[REQ-CNV-79308-04]** — As a VM owner, I want to reuse released VMState PVC data and identify unavailable state.
  - *Test Scenario:* **TS-019**: [Tier 1] [EXISTING_COVERAGE] Verify Linux VMState adoption preserves saved vTPM and EFI
    - *Priority:* P1
  - *Test Scenario:* **TS-020**: [Tier 1] [EXISTING_COVERAGE] Verify missing VMState prevents startup with an error
    - *Priority:* P1
  - *Test Scenario:* **TS-021**: [Tier 3] Verify adopted Windows preserves vTPM and EFI across reboot
    - *Priority:* P1

---

### **IV. Sign-off and Approval**

This Software Test Plan requires approval from the following stakeholders:

- **Reviewers:**
  - QE: [Dalia Frank](@dalia-frank), [Kateryna Shvaika](@kshvaika), [Jose Manuel Castano](@josemacassan), [Ahmad Hafe](@Ahmad-Hafe), [Jenia Peimer](@jpeimer), [Adam Cinko](@acinko-rh)
  - Development: [Alvaro Romero](@alromeros), [Adi Aloni](@Acedus), [Adam Litke](@aglitke)
  - QE Architect: [Ruth Netser](@rnetser)
- **Approvers:**
  - QE Lead: [Name / @github-handle]
  - Dev Lead: [Name / @github-handle]
  - Product Manager: [Peter Lauterbach](@peterclauterbach)
