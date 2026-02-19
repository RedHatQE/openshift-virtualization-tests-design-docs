# Openshift-virtualization-tests Test plan

## **Live Update NetworkAttachmentDefinition Reference (Hotpluggable NAD Ref) - Quality Engineering Plan**

### **Metadata & Tracking**

| Field                  | Details                                                                                                                            |
|:-----------------------|:-----------------------------------------------------------------------------------------------------------------------------------|
| **Enhancement(s)**     | [VEP #140: Live Update NAD Reference](https://github.com/kubevirt/enhancements/blob/main/veps/sig-network/hotpluggable-nad-ref.md) |
| **Feature in Jira**    | https://issues.redhat.com/browse/CNV-72329                                                                                         |
| **Jira Tracking**      | https://issues.redhat.com/browse/CNV-75778                                                                                         |
| **QE Owner(s)**        | Yoss Segev (ysegev@redhat.com)                                                                                                     |
| **Owning SIG**         | sig-network                                                                                                                        |
| **Participating SIGs** | sig-network                                                                                                                        |
| **Current Status**     | Draft                                                                                                                              |

**Document Conventions:**
- **NAD** = NetworkAttachmentDefinition (Multus secondary network)
- **VEP** = KubeVirt Enhancement Proposal
- **DNC** = Dynamic Networks Controller (Multus dynamic networks controller)

### **Feature Overview**

This feature enables VM owners to change the NetworkAttachmentDefinition reference (`networkName`) of a secondary network on a **running** VM without rebooting. When the user updates `spec.networks[].multus.networkName` in the VM spec, the system triggers a Live Migration, so the VM’s new pod will now be plumbed to the new network (e.g., a different VLAN). Today, changing the NAD reference requires a VM restart. The enhancement uses the existing migration path: no reboot, and guest interface properties (e.g., MAC) stay the same. A new feature gate **LiveUpdateNADRef** controls the behavior. Supported scenario in scope is **bridge binding** on live-migratable VMs.

### **I. Motivation and Requirements Review (QE Review Guidelines)**

#### **1. Requirement & User Story Review Checklist**

| Check                                  | Done | Details/Notes                                                                                                                                                                                                                                            | Comments |
|:---------------------------------------|:-----|:---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:---------|
| **Review Requirements**                | [x]  | VEP #140: Change bridge binding NAD reference on running VM; no RestartRequired when only networkName (i.e. the NAD reference) changes; migration triggered when networkName changes.                                                      |          |
| **Understand Value**                   | [x]  | VM owners can re-assign new networks (e.g. a different VLAN) to VMs without reboot, avoiding workload impact and preserving guest interface identity (e.g. MAC).                                                                                         |          |
| **Customer Use Cases**                 | [x]  | As a VM owner, I should be able to re-assign VMs to a new VLAN ID without having to reboot my VMs.                                                                                                                                                       |          |
| **Testability**                        | [x]  | Core flow is testable: Update networkName on VM → wait for completion (mostly for the migration in the background) → verify VM is connected to the new network and has connectivity. Non-goals (e.g., non-migratable VMs, CNI type change) are explicit. |          |
| **Acceptance Criteria**                | [x]  | Change NAD reference on a VM and verify VM is connected to the new network and has connectivity (per VEP Functional Testing Approach).                                                                                                                   |          |
| **Non-Functional Requirements (NFRs)** | [x]  | Scalability/update/rollback per VEP rely on existing KubeVirt capabilities; no new NFRs called out. Documentation and E2E coverage required for Beta/GA.                                                                                                 |          |

#### **2. Technology and Design Review**

| Check                            | Done | Details/Notes                                                                                                                             | Comments |
|:---------------------------------|:-----|:------------------------------------------------------------------------------------------------------------------------------------------|:---------|
| **Developer Handoff/QE Kickoff** | [x]  | Meeting where Dev introduced QE through NAD change in VM, migration condition handling, and DNC compatibility (Option 1 vs 2).            |          |
| **Technology Challenges**        | [x]  | Requires live-migratable VM and bridge binding; multus secondary networks.                                                                |          |
| **Test Environment Needs**       | [x]  | Cluster nodes with secondary interfaces, bridge binding, live migration enabled, NMState operator; LiveUpdateNADRef feature-gate enabled. |          |
| **API Extensions**               | [x]  | No new API; existing VM/VMI spec; only behavior change when networkName is updated and LiveUpdateNADRef gate is enabled.                  |          |
| **Topology Considerations**      | [x]  | In-cluster migration; no multi-cluster or new topology; No dependency on DNC changes (all implementation changes are in Kubevirt).        |          |

---

### **II. Software Test Plan (STP)**

#### **1. Scope of Testing**

**In scope:**
- Updating `spec.networks[].multus.networkName` on a running VM that uses **bridge binding** and is **live-migratable**.
- Verifying that post-migration VM has the bridged interface attached to the **new** NAD and has connectivity on the new network (migration is happening in the background, and is not part of the user's required actions).
- Verifying that guest interface identity (e.g. MAC) is preserved where applicable.
- Feature gate **LiveUpdateNADRef** enabled/disabled behavior.

**Testing Goals:**
- **[P0]** Change NAD reference on a running VM (bridge binding) and verify the VM is connected to the new network and has connectivity (E2E).
- **[P1]** Regression: existing secondary network and migration flows unchanged when not using this feature, including interface hot-plug.
- **[P2]** Verify behavior when LiveUpdateNADRef feature-gate is disabled (e.g. attempting to change NAD reference produces failure/error).

**Out of Scope (Testing Scope Exclusions)**

| Out-of-Scope Item                                       | Rationale (per VEP Non-Goals / design)                      | PM/ Lead Agreement |
|:--------------------------------------------------------|:------------------------------------------------------------|:-------------------|
| Migrating between CNI types                             | Explicit non-goal in VEP                                    | [ ]                |
| Changing network binding/plugin                         | Explicit non-goal                                           | [ ]                |
| Seamless network connectivity until action is completed | Not guaranteed by design                                    | [ ]                |
| Changing NAD reference on non-migratable VMs            | Not supported                                               | [ ]                |
| Changing guest network configuration    | Not in scope; guest may need separate reconfig              | [ ]                |
| Limiting migration retries because of missing Network Attachment Definition        | Explicit non-goal in VEP                       | [ ]                |


#### **2. Test Strategy**

| Item                           | Description                                                                                                                                                  | Applicable (Y/N or N/A) | Comments                                                                                                                                |
|:-------------------------------|:-------------------------------------------------------------------------------------------------------------------------------------------------------------|:------------------------|:----------------------------------------------------------------------------------------------------------------------------------------|
| Functional Testing             | Validates that the feature works according to specified requirements and user stories                                                                        | Y                       | Core: NAD ref update → (migration in background) → new network connectivity                                                             |
| Automation Testing             | Ensures test cases are automated for continuous integration and regression coverage                                                                          | Y                       | E2E scenarios must be automated for GA                                                                                                  |
| Performance Testing            | Validates feature performance meets requirements (latency, throughput, resource usage)                                                                       | N                       | Uses existing migration performance; no new SLA in VEP; latency cannot be measured, for example if NAD is changed from disabled network |
| Security Testing               | Verifies security requirements, RBAC, authentication, authorization, and vulnerability scanning                                                              | N                       | No new security surface; existing VM/NAD RBAC                                                                                           |
| Usability Testing              | Validates user experience, UI/UX consistency, and accessibility requirements                                                                                 | Y                       | UI should eventually support the feature (like in interface hot-plug)                                                                   |
| Compatibility Testing          | Ensures feature works across supported platforms, versions, and configurations                                                                               | Y                       | Should be supported on all clusters with secondary interface on nodes                                                                   |
| Regression Testing             | Verifies that new changes do not break existing functionality                                                                                                | Y                       | Connectivity post NAD-change                                                                                                            |
| Upgrade Testing                | Validates upgrade paths from previous versions, data migration, and configuration preservation                                                               | Y                       | Expected to function on upgraded clusters after feature-gate enablement                                                                 |
| Backward Compatibility Testing | Ensures feature maintains compatibility with previous API versions and configurations                                                                        | Y                       | Verify the existing interface hot-plug feature is not affected                                                                          |
| Dependencies                   | Dependent on deliverables from other components/products?                                                                                                    | Y                       | KubeVirt virt-controller; Multus (just exisiting functionality, no new reqiurement); optional DNC                                       |
| Cross Integrations             | Does the feature affect other features/require testing by other components?                                                                                   | N                       | Bridge binding in VMs is tested byt network SIG, hance changes in bridge binding are also under the network sig testing domain.         |
| Monitoring                     | Does the feature require metrics and/or alerts?                                                                                                                | N                       | VEP does not introduce new metrics/alerts                                                                                               |
| Cloud Testing                  | Does the feature require multi-cloud platform testing?                                                                                                        | N/A                     | Same as existing migration/secondary network requirements; secondary node interfaces are currently not supported on cloud clusters.     |


#### **3. Test Environment**

| Environment Component                         | Configuration           | Specification Examples                                                                                                                                                                                 |
|:----------------------------------------------|:------------------------|:-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Cluster Topology**                          | Standard                | Sufficient for live migration (e.g., multi-worker); multi NIC support                                                                                                                                  |
| **OCP & OpenShift Virtualization Version(s)** | 4.22                    | Version where LiveUpdateNADRef is available (e.g., aligned with KubeVirt v1.8+ Beta)                                                                                                                   |
| **CPU Virtualization**                        | Required                | Nodes with virtualization enabled for VMs and live migration                                                                                                                                           |
| **Compute Resources**                         | Standard                | Enough for VM + migration target node                                                                                                                                                                  |
| **Special Hardware**                          | Not required            | Standard secondary NICs; secondary networks via bridge NADs                                                                                                                                            |
| **Storage**                                   | Standard                | Sufficient for migration                                                                                                                                                                               |
| **Network**                                   | Secondary networks      | At least two NADs (e.g., different VLANs/bridges) for bridge binding; Multus configured. To reduce resource dependency, it might be worth considering referring to the same node bridge in the 2 NADs. |
| **Required Operators**                        | Standard                | OpenShift Virtualization; Multus; NMState                                                                                                                                                              |
| **Platform**                                  | Multi nodes; multi NICs | Per existing migration and secondary network support                                                                                                                                                   |
| **Special Configurations**                    | Feature gate            | LiveUpdateNADRef enabled for positive tests                                                                                                                                                            |


#### **3.1. Testing Tools & Frameworks**

| Category           | Tools/Frameworks                                                                         |
|:-------------------|:-----------------------------------------------------------------------------------------|
| **Test Framework** | Existing OpenShift Virtualization E2E test suite                                         |
| **CI/CD**          | sig-network lanes; tests tagged for multi-NIC + no SNO (where migration is not possible) |
| **Other Tools**    | N/A                                                                                      |


#### **4. Entry Criteria**

The following conditions must be met before testing can begin:

- [ ] VEP/design is **approved and merged** upstream; feature available in target OCP/OpenShift Virtualization version.
- [ ] Test environment can be **set up and configured** (see Section II.3 - Test Environment).
- [ ] Feature gate **LiveUpdateNADRef** is configurable in the test environment, or set on day-0


#### **5. Risks**

| Risk Category        | Specific Risk for This Feature                                                                                          | Mitigation Strategy                                                | Status |
|:---------------------|:------------------------------------------------------------------------------------------------------------------------|:-------------------------------------------------------------------|:-------|
| Timeline/Schedule    | Dependency on KubeVirt implementation and gate availability in OCP build                                                | Align with Dev on milestone; automate core scenario early          | [ ]    |
| Test Coverage        | The migration is not reflected to the user, hence following the process and verifying its completion is challenging.    | Might follow `MigrationRequired` condition in VMI                  | [ ]    |
| Test Environment     | No real risk, the environment requirements as specified in "Test Environment" section are standard in most CI clusters. |                                                                    | [ ]    |
| Untestable Aspects   | N/A                                                                                                                     |      | [ ]    |
| Resource Constraints | N/A                                                                                                                     |                                                                   | [ ]    |
| Dependencies         | See "Test Environment"                                                                                                                    |  | [ ]    |


#### **6. Known Limitations**

- **Non-migratable VMs:** Changing NAD reference on non-migratable VMs is out of scope; RestartRequired or no migration expected.
- **Binding support:** Any supported **bridge binding** only.
- **Guest network config:** Feature does not change guest-side configuration; guest may need separate reconfiguration for new network (e.g., IP).
- **Single-node clusters (SNO):** Cannot be supported because migration is not possible.


---

### **III. Test Scenarios & Traceability**

| Requirement ID   | Requirement Summary                                                                 | Test Scenario(s)                                                                           | Tier   | Priority |
|:-----------------|:------------------------------------------------------------------------------------|:-------------------------------------------------------------------------------------------|:-------|:---------|
| VEP-140 (Goal)   | Change NAD reference on running VM (bridge) via migration; VM on new network and has connectivity | Change networkName on running VM → wait for migration → verify VM attached to new NAD and connectivity | Tier 2 | P0       |
| VEP-140 (Design) | Migration triggered and completes after networkName update                          | Update networkName → verify migration requested and completes                              | Tier 1 | P0       |
| VEP-140 (Design) | RestartRequired not set when only networkName changes                               | Update only networkName → assert RestartRequired not added                                 | Tier 1 | P1       |
| VEP-140 (NFR)    | No regression in secondary network and migration                                    | Existing secondary network and migration tests pass                                         | Tier 2 | P1       |
| VEP-140 (Goal)   | Guest interface identity preserved during NAD reference change                      | Change networkName → verify MAC address and interface name remain unchanged after migration | Tier 2 | P2       |

---

### **IV. Sign-off and Approval**

This Software Test Plan requires approval from the following stakeholders:

* **Reviewers:**
  - Leading Dev: Ananya Banerjee
  - QE tech-lead: Ruth Netser
  - QE Members: Asia Khromov, Anat Wax, Sergei Volkov
* **Approvers:**
  - QE tech-lead: Ruth Netser
  - Product Manager/Owner: Ronen Sde-Or, Petr Horacek
  - Development Lead: Ananya Banerjee
