# Openshift-virtualization-tests Test plan

## **Live Update NetworkAttachmentDefinition Reference (Hotpluggable NAD Ref) - Quality Engineering Plan**

### **Metadata & Tracking**

| Field                  | Details                                                                                                                            |
|:-----------------------|:-----------------------------------------------------------------------------------------------------------------------------------|
| **Enhancement(s)**     | [VEP #140: Live Update NAD Reference](https://github.com/kubevirt/enhancements/blob/main/veps/sig-network/hotpluggable-nad-ref.md) |
| **Feature in Jira**    | https://issues.redhat.com/browse/VIRTSTRAT-560                                                                                         |
| **Jira Tracking**      | https://issues.redhat.com/browse/CNV-72329                                                                                         |
| **QE Owner(s)**        | Yoss Segev (ysegev@redhat.com)                                                                                                     |
| **Owning SIG**         | sig-network                                                                                                                        |
| **Participating SIGs** | sig-network                                                                                                                        |

**Document Conventions:**
- **NAD** = NetworkAttachmentDefinition (Multus secondary network)
- **VEP** = KubeVirt Enhancement Proposal
- **DNC** = Dynamic Networks Controller (Multus dynamic networks controller)

### **Feature Overview**

This feature enables VM owners to change the NetworkAttachmentDefinition reference (`networkName`) of a secondary network on a **running** VM without rebooting. When the user updates `spec.networks[].multus.networkName` in the VM spec, the VM will be reconnected to the new network (e.g., a different VLAN) without requiring a restart.\
Supported scenario in scope is **bridge binding** on live-migratable VMs.

### **I. Motivation and Requirements Review (QE Review Guidelines)**

#### **1. Requirement & User Story Review Checklist**

| Check                                  | Done | Details/Notes                                                                                                                                                    | Comments |
|:---------------------------------------|:-----|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------|:---------|
| **Review Requirements**                | [x]  | VEP #140: Change bridge binding NAD reference on running VM; no RestartRequired when only networkName (i.e. the NAD reference) changes.                          |          |
| **Understand Value**                   | [x]  | VM owners can re-assign new networks (e.g. a different VLAN) to VMs without reboot, avoiding workload impact and preserving guest interface identity (e.g. MAC). |          |
| **Customer Use Cases**                 | [x]  | As a VM owner, I should be able to re-assign VMs to a new VLAN ID without having to reboot my VMs.                                                               |          |
| **Testability**                        | [x]  | Core flow is testable (see III. Test Scenarios & Traceability).                                                                                                  |          |
| **Acceptance Criteria**                | [x]  | Change NAD reference on a VM and verify VM is connected to the new network and has connectivity (per VEP Functional Testing Approach).                           |          |
| **Non-Functional Requirements (NFRs)** | [x]  | No new NFRs called out. Documentation and E2E coverage required.                                                                                     |          |

#### **2. Technology and Design Review**

| Check                            | Done | Details/Notes                                                                                                       | Comments |
|:---------------------------------|:-----|:--------------------------------------------------------------------------------------------------------------------|:---------|
| **Developer Handoff/QE Kickoff** | [x]  | Meeting where Dev introduced QE through NAD change in VM, migration condition handling, and compatibility with DNC. |          |
| **Technology Challenges**        | [x]  | If live-migration is not possible (e.g. single-node clusters are not suitbale).                                     |          |
| **Test Environment Needs**       | [x]  | Cluster nodes with secondary interfaces (for multus secondary networks), NMState operator.                          |          |
| **API Extensions**               | [x]  | No new API; existing VM/VMI spec; only behavior change when feature is enabled and networkName is updated.          |          |
| **Topology Considerations**      | [x]  | No known limitations when considering different topologies                                                          |          |

---

### **II. Software Test Plan (STP)**

#### **1. Scope of Testing**

**Testing Goals:**
- **[P0]** Change NAD reference on a running VM (bridge binding) and verify the VM is connected to the new network and has connectivity (E2E).
- **[P1]** Change several NADs on same VM, and verify there is E2E connectivity over all the new networks.
- **[P2]** Verify user-initiated migration (i.e. not the migration that is done to complete the NAD swap) is successful after completing NAD swap.

**Out of Scope (Testing Scope Exclusions)**

| Out-of-Scope Item                                       | Rationale (per VEP Non-Goals / design)                      | PM/ Lead Agreement       |
|:--------------------------------------------------------|:------------------------------------------------------------|:-------------------------|


#### **2. Test Strategy**

| Item                           | Description                                                                                                                                                  | Applicable (Y/N or N/A) | Comments                                                                                                                                              |
|:-------------------------------|:-------------------------------------------------------------------------------------------------------------------------------------------------------------|:------------------------|:------------------------------------------------------------------------------------------------------------------------------------------------------|
| Functional Testing             | Validates that the feature works according to specified requirements and user stories                                                                        | Y                       | Core: NAD ref update → (migration in background) → new network connectivity                                                                           |
| Automation Testing             | Ensures test cases are automated for continuous integration and regression coverage                                                                          | Y                       | E2E scenarios must be automated for GA                                                                                                                |
| Performance Testing            | Validates feature performance meets requirements (latency, throughput, resource usage)                                                                       | N                       | Uses existing migration performance; no new SLA in VEP; latency cannot be measured, for example if NAD is changed from disabled network               |
| Security Testing               | Verifies security requirements, RBAC, authentication, authorization, and vulnerability scanning                                                              | N                       | No new security surface; existing VM/NAD RBAC                                                                                                         |
| Usability Testing              | Validates user experience, UI/UX consistency, and accessibility requirements                                                                                 | Y                       | UI should eventually support the feature (like in interface hot-plug), tracked in CNV-82742                                                           |
| Compatibility Testing          | Ensures feature works across supported platforms, versions, and configurations                                                                               | Y                       | Should be supported on all clusters with secondary interface on nodes                                                                                 |
| Regression Testing             | Verifies that new changes do not break existing functionality                                                                                                | Y                       | Connectivity post NAD-change; user-initiated migration post NAD-change.                                                                               |
| Upgrade Testing                | Validates upgrade paths from previous versions, data migration, and configuration preservation                                                               | N                       | Expected to function on upgraded clusters after feature-gate enablement                                                                               |
| Backward Compatibility Testing | Ensures feature maintains compatibility with previous API versions and configurations                                                                        | Y                       | Verify the existing interface hot-plug feature is not affected                                                                                        |
| Dependencies                   | Dependent on deliverables from other components/products?                                                                                                    | Y                       | KubeVirt virt-controller; Multus (just existing functionality, no new requirement); optional DNC                                                      |
| Cross Integrations             | Does the feature affect other features/require testing by other components?                                                                                   | N                       | Bridge binding in VMs is tested by the network SIG, hence changes in bridge binding are also under the network sig testing domain.                    |
| Monitoring                     | Does the feature require metrics and/or alerts?                                                                                                                | N                       | VEP does not introduce new metrics/alerts                                                                                                             |
| Cloud Testing                  | Does the feature require multi-cloud platform testing?                                                                                                        | N/A                     | The fixture involves secondary node interfaces, which are currently not supported on cloud clusters.                                                  |


#### **3. Test Environment**

| Environment Component                         | Configuration           | Specification Examples                                                                                                                                                                                 |
|:----------------------------------------------|:------------------------|:-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Cluster Topology**                          | Multi nodes; multi NICs | Sufficient for live migration (e.g., multi-worker); multi NIC support                                                                                                                                  |
| **OCP & OpenShift Virtualization Version(s)** | 4.22                    | Version where feature can be enabled (e.g., aligned with KubeVirt v1.8+)                                                                                                                          |
| **CPU Virtualization**                        | Required                | Nodes with virtualization enabled for VMs and live migration                                                                                                                                           |
| **Compute Resources**                         | Standard                | Enough for VM + migration target node                                                                                                                                                                  |
| **Special Hardware**                          | Not required            | Standard secondary NICs; secondary networks via bridge NADs                                                                                                                                            |
| **Storage**                                   | Standard                | Sufficient for migration                                                                                                                                                                               |
| **Network**                                   | Secondary networks      | At least two NADs (e.g., different VLANs/bridges) for bridge binding; Multus configured. To reduce resource dependency, it might be worth considering referring to the same node bridge in the 2 NADs. |
| **Required Operators**                        | Standard                | OpenShift Virtualization; Multus; NMState                                                                                                                                                              |
| **Platform**                                  | Standard                | Agnostic                                                                                                                                                                                               |
| **Special Configurations**                    | Feature gate            | None required                                                                                                                                                                                          |


#### **3.1. Testing Tools & Frameworks**

| Category           | Tools/Frameworks                                                                         |
|:-------------------|:-----------------------------------------------------------------------------------------|
| **Test Framework** | Existing OpenShift Virtualization E2E test suite                                         |
| **CI/CD**          | sig-network lanes; tests tagged for multi-NIC + no SNO (where migration is not possible) |
| **Other Tools**    | N/A                                                                                      |


#### **4. Entry Criteria**

The following conditions must be met before testing can begin:

- [X] VEP/design is **approved and merged** upstream; feature available in target OCP/OpenShift Virtualization version.
- [ ] Test environment can be **set up and configured** (see Section II.3 - Test Environment).
- [ ] The feature was either enabled on day-0, or can be enabled in the test environment.


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
- **Migrating between CNI types:** Explicit non-goal
- **Changing network binding/plugin:** Explicit non-goal
- **Seamless network connectivity until action is completed:** Not guaranteed by design
- **Changing NAD reference on non-migratable VMs:** Explicitly not supported
- **No limitation of migration retries because of missing Network Attachment Definition:** Explicit non-goal


---

### **III. Test Scenarios & Traceability**

| Requirement ID | Requirement Summary                                                                                                                                                            | Test Scenario(s)                                                                                                                                                                                                          | Tier   | Priority |
|:---------------|:-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:-------|:---------|
| TC-0           | As a VM owner, I want to be able to connect an exisitng interface to a different network while preserving connectivity.                                                        | Change NAD reference on running VM (bridge); VM on new network and has connectivity                                                                                                                         | Tier 2 | P0       |
| TC-1           | As a VM owner where net newtork should be configured for existing secondary interface, I want to make sure that guest interface identity preserved during NAD reference change | Change networkName → verify MAC address and interface name remain unchanged                                                                                                                                               | Tier 1 | P2       |
| TC-2           | As a VM owner, I want to be able to successfuly migrate my VM after NAD swap                                                                                                   | Change networkName → user initiated migration -> successful connectivity post-migration                                                                                                                                   | Tier 2 | P1       |
| TC-3           | As a VM owner, I want to be able to change NAD refs of more than one network on a single VM                                                                                    | Change networkName on running VM for several networks → wait for migration → verify VM attached to new NAD and connectivity in all networks                                                                               | Tier 2 | P1       |
| TC-4           | As cluster admin, I want to change NAD ref in a VM in one namespace to a NAD on a different namespace                                                                          | Create NAD in default namespace, and VM in different namespace → Change networkName on running VM (to the NAD in default namespace) → wait for migration → verify VM attached to new NAD + connectivity                   | Tier 2 | P1       |

---

### **IV. Sign-off and Approval**

This Software Test Plan requires approval from the following stakeholders:

* **Reviewers:**
  - Leading Dev: Ananya Banerjee
  - QE tech-lead: Ruth Netser
  - QE Members: Anat Wax
* **Approvers:**
  - QE tech-lead: Ruth Netser
  - Product Manager/Owner: Ronen Sde-Or, Petr Horacek
  - Development Lead: Ananya Banerjee
