# Openshift-virtualization-tests Test plan

## **Clone and Storage Migration support for VMState PVC - Quality Engineering Plan**

### **Metadata & Tracking**

- **Enhancement(s):** [KubeVirt VEP #312](https://github.com/kubevirt/enhancements/issues/312), [CNV-85157](https://redhat.atlassian.net/browse/CNV-85157)
- **Feature Tracking:** N/A — no feature-level parent is assigned in Jira.
- **Epic Tracking:** [CNV-79308](https://redhat.atlassian.net/browse/CNV-79308)
- **Feature Maturity:**
  - DP: CNV v5.1.0
  - TP: CNV v5.2.0 [confirm]
  - GA: CNV v5.3.0 [confirm]
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

OpenShift Virtualization will preserve captured vTPM and EFI state when users clone a virtual machine or migrate its storage. Guests depend on this state for security and boot continuity. The feature covers independent clone storage, state relocation, and continued use of the target volume, including during Windows live storage conversion. Feature Limitations describes what happens when a snapshot lacks captured state. The plan targets GA and marks checks also required for the CNV v5.1.0 Developer Preview with [DP].

---

### **I. Motivation and Requirements Review (QE Review Guidelines)**

QE interprets the clone and migration requirements as preserving usable guest state across both operations. A clone needs independent state storage, and a migrated VM must continue using its relocated state when source storage becomes inaccessible.

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
  - *Note any requirements that are unclear or untestable:* The acceptance criteria are testable. The epic does not state a performance, scale, monitoring, or UI requirement.

- [x] **Acceptance Criteria**
  - *List the acceptance criteria:*
    - A clone with captured VMState can read the source VM's saved vTPM-protected data and EFI variables and uses a separate VMState PVC.
    - After storage migration, the VM uses a VMState PVC on the target storage class and reports it as the active state volume.
    - During Windows live storage conversion, the VM stays running from start to completion without a stop or restart.
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

#### **2. Feature Limitations**

- **RWO VMState PVC referenced only by source cannot live-migrate without a volume claim template**
  - *Sign-off:* [Name/Date]

- **Declarative VMState storage requires Filesystem volume mode**
  - *Sign-off:* [Name/Date]

- **An existing implicit-state VM cannot be converted in place by adding declarative state configuration**
  - A new or recreated VM may adopt its released legacy PVC.
  - *Sign-off:* [Name/Date]

- **Legacy implicit-state cloning is blocked until the CNV-100645 fix is included in the tested build**
  - [CNV-100645](https://redhat.atlassian.net/browse/CNV-100645) tracks cloning from an implicit source into a declarative target. [KubeVirt PR #19814](https://github.com/kubevirt/kubevirt/pull/19814) remained open on November 20, 2026. Check actual build inclusion before execution.
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

- **[P0][DP]** Verify that Linux and Windows direct and snapshot clones with captured state use independent storage and preserve vTPM and EFI state. Cover declarative sources and include legacy sources once the tested build includes the fix in I.2.
- **[P0][DP]** Verify that native RWO relocation and Windows live storage conversion use the target storage class and preserve saved vTPM and EFI state.
- **[P1][DP]** Verify that a failed clone leaves original state usable. A snapshot without captured state must reject the clone without a claim template or warn and initialize independent state when a template is available.
- **[P1][DP]** Verify that failed native relocation or Windows live conversion leaves the original vTPM and EFI state usable.
- **[P1][DP]** Verify that a VM can use relocated vTPM and EFI state when source storage is inaccessible.
- **[P1][DP]** Verify that Windows can adopt released state and retain saved vTPM and EFI state across reboot. Run the existing Linux adoption and startup-error checks in II.2.
- **[P1]** Verify that Linux and Windows VMs keep usable pre-upgrade vTPM and EFI state after upgrading along a supported path to GA.

**Priority Levels:**

- **P0** blocks GA.
- **P1** is required for full feature coverage.
- **P2** can be deferred if the schedule is constrained.

**Phase tag (optional):** [DP] marks coverage also required for Developer Preview.

**Out of Scope (Testing Scope Exclusions)**

- **Performance and scale benchmarking**
  - *Rationale:* QE will verify functional behavior within the lab's migration and storage limits. Jira and the design define no latency, throughput, or scale target to benchmark.
  - *Sign-off (Quality Owner or Product Manager):* [Name/Date]

- **OpenShift web console workflows and accessibility**
  - *Rationale:* The plan validates the scoped VMState workflows through the API, including active-volume status, rejection errors and warnings for uncaptured state.
  - *Sign-off (Quality Owner or Product Manager):* [Name/Date]

- **Legacy MTC storage-conversion reproduction**
  - *Rationale:* [CNV-83112](https://redhat.atlassian.net/browse/CNV-83112) was closed as Won't Do. TS-011 covers the reported split-storage failure through KubeVirt live storage conversion.
  - *Sign-off (Quality Owner or Product Manager):* [Name/Date]

**Test Limitations**

- **Source-storage fault injection is restricted to isolated, disposable storage**
  - Qualify a source-volume disconnect or equivalent scoped fault that leaves target storage available before running the source-independence case. Confirm the source is inaccessible and the migrated guest can still use its saved state; reference inspection alone is not a substitute.
  - *Sign-off:* [Name/Date]

#### **2. Test Strategy**

**Functional**

- [x] **Functional Testing** — Validates that the feature works according to specified requirements and user stories
  - *Details:* Cover VM clone, native storage relocation, Windows live storage conversion, persistent-state usability, target-volume reference, and source-storage independence. Exercise direct and snapshot clones with captured state from declarative sources on Linux and Windows. Repeat with legacy sources when the build includes the fix in I.2.

- [x] **Automation Testing** — Confirms test automation plan is in place for CI and regression coverage (all tests are expected to be automated)
  - *Details:* Run the existing Tier 1 contracts listed under Regression Testing. Automate Tier 2 Linux workflows and Tier 3 Windows workflows in RedHatQE/openshift-virtualization-tests. Execute the Windows clone, isolation, live conversion success and failure, and adoption cases for Developer Preview and GA. Execute the Windows upgrade case for GA. Reuse Windows vTPM/BitLocker setup and extend existing migration tests with the missing VMState assertions. Partial-coverage tags identify automation to extend.

- [x] **Regression Testing** — Verifies that new changes do not break existing functionality
  - *Details:* Run these existing SIG Storage checks on the feature build.
    - [KubeVirt VMState adoption](https://github.com/kubevirt/kubevirt/blob/a9a239a1058dbdb0cd75709c6ba3a5b55d62e75b/tests/storage/vmstate.go#L320-L355) starts a second Fedora VM on released storage and reads the saved TPM secret and EFI variable.
    - [KubeVirt missing-source reporting](https://github.com/kubevirt/kubevirt/blob/a9a239a1058dbdb0cd75709c6ba3a5b55d62e75b/tests/storage/vmstate.go#L357-L375) reports the missing PVC when the VM attempts to start.
    - [KubeVirt exclusive-use reporting](https://github.com/kubevirt/kubevirt/blob/a9a239a1058dbdb0cd75709c6ba3a5b55d62e75b/tests/storage/vmstate.go#L378-L414) reports that the PVC is in use when a second VM attempts to start while the first VM holds it.
    - [Windows vTPM storage migration](https://github.com/RedHatQE/openshift-virtualization-tests/blob/7b8e0c0900f66c1d7e9415af60f1cf9126212bda/tests/storage/storage_migration/test_storage_class_migration.py#L252-L330) checks boot time, guest-file integrity, and disk placement. Extend it with the VMState assertions in III.
    - Existing platform coverage owns the broader Windows guest-version and application matrix, storage-class provisioning, and basic PVC binding. This plan verifies VMState workflows on the selected guest images and storage classes.

- [ ] **Self-Validation Testing** — Should any of the new tests be included in the self-validation test package?
  - *Details:* No new package inclusion is proposed for the multi-operation clone/relocation workflows. Tier 1 adoption and reporting reuse existing feature checks. Curated downstream self-validation package membership is a separate selection decision.

**Non-Functional**

- [ ] **Performance Testing** — Validates feature performance meets requirements (latency, throughput, resource usage)
  - *Details:* Not applicable; no performance target is defined.

- [ ] **Scale Testing** — Validates feature behavior under increased load and at production-like scale (e.g., large number of VMs, nodes, or concurrent operations)
  - *Details:* No new scale benchmark is specified; see II.1's benchmarking exclusion. Functional execution must respect the installed cluster's migration parallelism and available storage capacity; no new concurrency limit is invented.

- [x] **Security Testing** — Verifies security requirements, RBAC, authentication, authorization, and vulnerability scanning
  - *Details:* Verify captured vTPM and EFI state remains usable after clone or relocation, and that uncaptured-state fallback creates independent fresh state. Run the existing exclusive-use check listed under Regression Testing.

- [ ] **Usability Testing** — Validates user experience and accessibility requirements
  - *Details:* See II.1 for the proposed OpenShift web console exclusion. Functional tests verify active-volume status, missing and in-use errors, and warnings for uncaptured state through the API.

- [ ] **Monitoring** — Does the feature require metrics and/or alerts?
  - *Details:* Not applicable; no new metric or alert requirement is defined.

**Integration & Compatibility**

- [x] **Compatibility Testing** — Ensures feature works across supported platforms, versions, and configurations
  - *Details:* Validate clone, native storage relocation, and Windows live storage conversion with distinct source and target storage classes.

- [x] **Upgrade Testing** — Validates upgrade paths from previous versions, data migration, and configuration preservation
  - *Details:* For the GA milestone, verify Linux and Windows VMs can use state saved before a supported upgrade. Select a supported source release that can create declarative VMState so the check covers existing PVCs and guest state across the version change. Qualify the release pair in II.3. Developer Preview covers the tagged functional workflows on its target build.

- [x] **Dependencies** — Blocked by deliverables from other components/products. Identify what we need from other teams before we can test.
  - *Details:* Legacy-source cloning depends on delivery of the KubeVirt fix tracked by CNV-100645 in the tested CNV build. The other scenarios can proceed when their entry criteria are met.

- [x] **Cross Integrations** — Does the feature affect other features or require testing by other teams? Identify the impact we cause.
  - *Details:* Cover VMState across clone, snapshot restore, native storage relocation, and Windows live storage conversion using the KubeVirt Migration Controller.

**Infrastructure**

- [ ] **Cloud Testing** — Does the feature require multi-cloud platform testing? Consider cloud-specific features.
  - *Details:* Not applicable; no cloud-specific behavior is defined. Storage-class compatibility is covered on the standard test platform.

#### **3. Test Environment**

- **Cluster Topology:** Planned three control-plane nodes and three worker nodes, with at least two schedulable workers for live migration.
- **OCP & OpenShift Virtualization Version(s):** CNV v5.1.0 is the Developer Preview target from Jira. Qualify the exact CNV build and supported OCP release for each milestone. Confirm the supported source and target release pair for the GA upgrade cases.
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
- [ ] Confirm the GA target and supported OCP/CNV upgrade pair before running the upgrade cases.

#### **5. Risks**

**Timeline/Schedule**

- **Mitigation:** No risk identified for the required Tier 2 and Tier 3 runs. See Dependencies for the legacy-clone fix.

**Test Coverage**

- **Risk:** Existing Windows vTPM migration tests can pass while VMState remains on source storage or saved guest state is lost.
  - **Mitigation:** Verify VMState placement and the active reference in TS-008 and TS-009. Compare saved vTPM and EFI state after relocation and during failure recovery. Prove source independence in TS-010 using the qualified isolated fault.

    In TS-011, observe the VM stay running through conversion and confirm the guest boot time is unchanged. Verify target placement for the guest disks and VMState, the active target state volume in VM status, and continued access to saved vTPM and EFI state. Fail the case if disk conversion completes with active VMState on source storage. TS-013 covers failure before handoff and verifies the original VM can still use its saved state.
  - *Areas with reduced coverage:* Existing automation lacks VMState-specific assertions and may miss offline fallback. Execute the native and Windows conversion success and failure cases plus the Windows clone and adoption checks before sign-off.
  - *Sign-off:* [Name/Date]

**Test Environment**

- **Risk:** Differences in storage and snapshot capabilities across the selected configurations could produce unsupported clone or migration results.
  - **Mitigation:** Qualify snapshot capture and RWO cross-class relocation before execution. Use separate qualified storage pairs for those workflows if a single pair cannot meet both needs.
  - *Missing resources or infrastructure:* The lab, storage pairs, and guest images still require qualification as listed in II.3.
  - *Sign-off:* [Name/Date]

- **Risk:** The GA target or a supported upgrade path may remain unconfirmed when the lab is scheduled.
  - **Mitigation:** Confirm the supported OCP/CNV release pair before provisioning the upgrade lab. Keep TS-015 and TS-016 open until a supported pair is available.
  - *Missing resources or infrastructure:* A qualified source and target release pair for GA.
  - *Sign-off:* [Name/Date]

**Untestable Aspects**

- **Risk:** Source-independence evidence may remain incomplete if the isolated fault-injection capability is not qualified before execution.
  - **Mitigation:** Meet the isolation constraint in Test Limitations before this case starts; schedule a disposable source/target environment and prove that the selected fault makes source state inaccessible while target state remains usable. Keep the entry criterion open until that qualification succeeds.
  - *Alternative validation approach:* Use a scoped source-volume disconnect. If no safe scoped fault can be qualified, the source-independence case remains unexecuted and requires an explicit coverage decision before sign-off.
  - *Sign-off:* [Name/Date]

**Resource Constraints**

- **Mitigation:** No risk identified. No capacity gap has been identified for the required Tier 3 runs.

**Dependencies**

- **Risk:** The legacy-clone fix may miss the CNV v5.1.0 build selected for validation. See the product constraint in I.2.
  - **Mitigation:** Confirm fix inclusion before legacy-source clone execution. If delivery misses the selected build, record the variant as unexecuted and obtain a scope or priority decision from the Quality Owner or Product Manager.
  - *Dependent teams or components:* CNV-100645 delivery in the selected build
  - *Sign-off:* [Name/Date]

---

### **III. Test Scenarios & Traceability**

- **[REQ-CNV-79308-01]** — As a VM owner, I want VM clones to work with VMState PVC.
  - *Source and clone method for TS-001, TS-002, and TS-006:*
    - Declarative VMState source — direct VM clone and clone from a snapshot that captured VMState.
    - Legacy implicit VMState source — direct VM clone and clone from a snapshot that captured VMState. Run both only when the tested build meets the CNV-100645 entry criterion in II.4.
  - *Test Scenario:* **TS-001**: [Tier 2] Verify Linux clone preserves vTPM security and EFI state
    - *Priority:* P0 [DP]
  - *Test Scenario:* **TS-002**: [Tier 2] Verify Linux clone uses a separate VMState PVC
    - *Priority:* P0 [DP]
  - *Test Scenario:* **TS-003**: [Tier 2] Verify source vTPM and EFI remain usable after clone failure
    - *Priority:* P1 [DP]
  - *Test Scenario:* **TS-004**: [Tier 2] Verify uncaptured-state clone rejects without a template
    - *Priority:* P1 [DP]
  - *Test Scenario:* **TS-005**: [Tier 2] Verify uncaptured-state clone warns and initializes independent fresh state
    - *Priority:* P1 [DP]
  - *Test Scenario:* **TS-006**: [Tier 3] Verify Windows clone preserves vTPM and EFI on a separate VMState PVC
    - *Priority:* P0 [DP]
  - *Test Scenario:* **TS-007**: [Tier 3] Verify Windows clone changes leave source vTPM and EFI unchanged
    - *Priority:* P1 [DP]

- **[REQ-CNV-79308-02]** — As a VM owner, I want to migrate storage of VMState PVC.
  - *Test Scenario:* **TS-008**: [Tier 2] [PARTIAL_COVERAGE] Verify RWO VMState reaches target storage with saved vTPM and EFI
    - *Priority:* P0 [DP]
  - *Test Scenario:* **TS-009**: [Tier 2] [PARTIAL_COVERAGE] Verify VM references migrated VMState PVC
    - *Priority:* P0 [DP]
  - *Test Scenario:* **TS-010**: [Tier 2] Verify relocated vTPM and EFI remain usable with source storage inaccessible
    - *Priority:* P1 [DP]
  - *Test Scenario:* **TS-011**: [Tier 3] Verify Windows live conversion preserves vTPM and EFI without stopping or restarting the VM
    - *Priority:* P0 [DP]
  - *Test Scenario:* **TS-012**: [Tier 2] Verify failed migration keeps original vTPM and EFI usable
    - *Priority:* P1 [DP]
  - *Test Scenario:* **TS-013**: [Tier 3] Verify failed Windows conversion keeps original vTPM and EFI usable
    - *Priority:* P1 [DP]

- **[REQ-CNV-79308-04]** — As a VM owner, I want to keep using saved vTPM and EFI state when I adopt released storage or the cluster is upgraded.
  - *Test Scenario:* **TS-014**: [Tier 3] Verify adopted Windows preserves vTPM and EFI across reboot
    - *Priority:* P1 [DP]
  - *Test Scenario:* **TS-015**: [Tier 2] Verify Linux VM reads pre-upgrade vTPM and EFI state
    - *Priority:* P1
  - *Test Scenario:* **TS-016**: [Tier 3] Verify Windows VM reads pre-upgrade vTPM and EFI state
    - *Priority:* P1

---

### **IV. Sign-off and Approval**

This plan requires sign-off from at least one person per function.

- Feature Owner: [Alvaro Romero](@alromeros)
- Quality Owner: [Dalia Frank](@dalia-frank), [Jenia Peimer](@jpeimer) ,[Ruth Netser](@rnetser)
- Product Manager: [Peter Lauterbach](@peterclauterbach)