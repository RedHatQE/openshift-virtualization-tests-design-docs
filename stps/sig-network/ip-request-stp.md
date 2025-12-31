# Openshift-virtualization-tests Test plan

## **Request a specific IP for a VM in UDN through a third party integration - Quality Engineering Plan**

### **Metadata & Tracking**

| Field                   | Details                                                                    |
|:----------------------- |:---------------------------------------------------------------------------|
| **Enhancement(s)**      | [As close as possible to VEP](https://access.redhat.com/solutions/7133388) |
|                         | Also note that this feature is based on the [IP request in imported VM](https://github.com/openshift/enhancements/blob/master/enhancements/network/requesting-staticips-for-vms-being-migrated-into-primary-l2-udns-using-MTV.md). |
| **Feature in Jira**     | https://issues.redhat.com/browse/CNV-67524                                 |
| **Jira Tracking**       | https://issues.redhat.com/browse/CNV-70089                                 |
| **QE Owner(s)**         | Yoss Segev (ysegev@redhat.com)                                             |
| **Owning SIG**          | sig-network                                                                |
| **Participating SIGs**  | sig-network                                                                |
| **Current Status**      | Draft                                                                      |

---

### **I. Motivation and Requirements Review (QE Review Guidelines)**

This section documents the mandatory QE review process. The goal is to understand the feature's value, technology, and testability prior to formal test planning.

#### **1. Requirement & User Story Review Checklist**

| Check                                   | Done | Details/Notes                                                                                                                                                                           | Comments  |
|:--------------------------------------- |:-----|:----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:--------- |
| **Review Requirements**                 | [V]  | Reviewed the relevant requirements.                                                                                                                                                     |           |
| **Understand Value**                    | [V]  | Enabling VM import with desired static IP (from 3rd party integrator) expands the motivation to import to RedHat.                                                                       |           |
| **Customer Use Cases**                  | [V]  | Ensured requirements contain relevant **customer use cases**.                                                                                                                           |           |
| **Testability**                         | [V]  | Confirmed requirements are **testable and unambiguous**.                                                                                                                                |           |
|                                         |      | Test cases are similar to those of the MTV IPAM Claim feature.                                                                                                                          |           |
| **Acceptance Criteria**                 | [V]  | Clearly defined in the [epic](https://issues.redhat.com/browse/CNV-67524).                                                                                                              |           |
| **Non-Functional Requirements (NFRs)**  | [V]  | Confirmed coverage for NFRs, including Performance, Security, Usability, Downtime, Connectivity, Monitoring (alerts/metrics), Scalability, Portability (e.g., cloud support), and Docs. |           |
|                                         |      | All relevant NFRs detailed in the epic and docs.                                                                                                                                        |           |


#### **2. Technology and Design Review**

| Check                             | Done  | Details/Notes                                                                                                                                                                         | Comments                                                                                                                                            |
|:--------------------------------- |:----- |:--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:--------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Developer Handoff/QE Kickoff**  | [V]   | A meeting where Dev/Arch walked QE through the design, architecture, and implementation details. **Critical for identifying untestable aspects early.**                               |                                                                                                                                                     |
| **Technology Challenges**         | [V]   | Identified potential testing challenges related to the underlying technology.                                                                                                         |                                                                                                                                                     |
| **Test Environment Needs**        | [V]   | Determined necessary **test environment setups and tools**.                                                                                                                           |                                                                                                                                                     |
| **API Extensions**                | [V]   | Reviewed new or modified APIs and their impact on testing.                                                                                                                            |                                                                                                                                                     |
|                                   |       | The change in VirtualMachine CRD is also covered in the [MTV-IPAMClaim epic](https://issues.redhat.com/browse/CNV-61227),                                                             |                                                                                                                                                     |
|                                   |       | and can be found in the [docs](https://docs.google.com/document/d/1xvd__b5QYm60laKwwxsaYTpZqDIZg_xdN1d1rCdh6H8/edit?tab=t.0#heading=h.ig6baarsl73l) (_Example VirtualMachine Manifest_) |                                                                                                                                                     |
| **Topology Considerations**       | [V]   | Evaluated multi-cluster, network topology, and architectural impacts.                                                                                                                 | Same as in the setups that are used for the MTV IPAM claim testing.<br/>3rd party will provide UDN and annotated VM, CNV testing starts from that.  |


### **II. Software Test Plan (STP)**

This STP serves as the **overall roadmap for testing**, detailing the scope, approach, resources, and schedule.

#### **1. Scope of Testing**

As testing starts at Openshift Virtualization part, it will be similar to the testing
of the MTV-IPAMClaim feature.

**In Scope:**
- Testing of known networking flows on VMs, where specific IP is requested for primary interface over
Cluster/UserDefinedNetwork.\
The uniqueness in this feature is how the IP is assigned - using the new `network.kubevirt.io/addresses` annotation

**Document Conventions (if applicable):** None

#### **2. Testing Goals**

Define specific, measurable testing objectives for this feature, such as:

- [ ] Goal 1: Verify known networking scenarios are still valid when primary static IP is assigned via the new\
annotation.
- [ ] [Goal 2: Consider new cases to be tested, presented by this new feature.

#### **3. Non-Goals (Testing Scope Exclusions)**

Explicitly document what is **out of scope** for testing. **Critical:** All non-goals require explicit stakeholder agreement to prevent "I assumed you were testing that" issues.

**Note:** Replace example rows with your actual non-goals. Each non-goal must have PM/Lead sign-off.

| Non-Goal                                            | Rationale                                                                                                                                          | PM/ Lead Agreement  |
|:----------------------------------------------------|:---------------------------------------------------------------------------------------------------------------------------------------------------|:------------------- |
| Templating VM spec with the `addresses` annotation. | It's the responsibility of the 3rd party integrator, and not accessible by us.<br/>We cannot and will not test the integration with the 3rd party. | [ ] Name/Date       |
| Creating C/UDN with IP range.                       | Same                                                                                                                                               | [ ] Name/Date       |
| Secondary UDN interfaces.                           | Not supported                                                                                                                                      | [ ] Name/Date       |
| Annotated address out of UDN range.                 | Unsupported by OVN-k8s and behavior is unexpected.                                                                                                 | [ ] Name/Date       |


**Important Notes:**
- Non-goals without stakeholder agreement are considered **risks** and must be escalated (see Section II.7 - Risks and Limitations)
- Review non-goals during Developer Handoff/QE Kickoff meeting (see Section I.2 - Technology and Design Review)

#### **4. Test Strategy**

##### **A. Types of Testing**

The following types of testing must be reviewed and addressed.

**Note:** Mark "Y" if applicable, "N/A" if not applicable (with justification in Comments). Empty cells indicate incomplete review.

| Item (Testing Type)             | Applicable (Y/N or N/A) | Comments                                                                                                                                                         |
|:------------------------------- |:------------------------|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Functional Testing              | Y                       |                                                                                                                                                                  |
| Automation Testing              | Y                       |                                                                                                                                                                  |
| Performance Testing             | Y                       | https://issues.redhat.com/browse/CNV-75797                                                                                                                       |
| Security Testing                | N/A                     |                                                                                                                                                                  |
| Usability Testing               | N                       | The annotation is done by the 3rd-party intergrator, therefore no new UI capability to test.                                                                     |
| Compatibility Testing           |                         | This feature is implemented in kubevirt and is environment-agnostic.                                                                                             |
| Regression Testing              | Y                       | Verify this feature can work with secondary interfaces (i.e. have a VM with primary UDN with the annotated address + secondary interface, either UDN or bridged) |
| Upgrade Testing                 | Y                       | Add pre./post-upgrade tests to ensure this feature survives upgrade.                                                                                             |
| Backward Compatibility Testing  | N/A                     |                                                                                                                                                                  |

##### **C. Potential Areas to Consider**

**Note:** Mark "Y" if applicable, "N/A" if not applicable (with justification in Comment). Empty cells indicate incomplete review.

| Item                    | Description                                                                                                         | Applicable (Y/N or N/A) | Comment                                                                                                                                                                                     |
|:----------------------- |:------------------------------------------------------------------------------------------------------------------- |:------------------------|:--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Dependencies**        | Dependent on deliverables from other components/products? Identify what is tested by which team.                    |                         | Depends on OVN-k8s ability to manage requested IPs, which is already implemented. All the cases in the STP are necessarily Openshift Virtualization cases, thus tested by CNV network only. |
| **Monitoring**          | Does the feature require metrics and/or alerts?                                                                     | N                       |                                                                                                                                                                                             |
| **Cross Integrations**  | Does the feature affect other features/require testing by other components? Identify what is tested by which team.  | N                       |                                                                                                                                                                                             |
| **UI**                  | Does the feature require UI? If so, ensure the UI aligns with the requirements.                                     | N                       | No UI intergration, configuration is done in the 3rd-party.                                                                                                                                 |

#### **5. Test Environment**

**Note:** "N/A" means explicitly not applicable. Cannot leave empty cells.

| Environment Component                          | Configuration                                                                                                                                                                                              | Specification Examples                                          |
|:---------------------------------------------- |:---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |:----------------------------------------------------------------|
| **Cluster Topology**                           | No special HW requirements; none of the feature contents should limit it to specific environments                                                                                                          | [e.g., 3-master/3-worker bare-metal, SNO, Compact Cluster, HCP] |
| **OCP & OpenShift Virtualization Version(s)**  | 4.21                                                                                                                                                                                                       |                                                                 |
| **CPU Virtualization**                         | No special configuration required                                                                                                                                                                          | [e.g., Nodes with VT-x (Intel) or AMD-V (AMD) enabled in BIOS]  |
| **Compute Resources**                          | Not required                                                                                                                                                                                               | [e.g., Minimum per worker node: 8 vCPUs, 32GB RAM]              |
| **Special Hardware**                           | No special HW requirements; none of the feature contents should limit it to specific environments                                                                                                          | [e.g., Specific NICs for SR-IOV, GPU etc.]                      |
| **Storage**                                    | Not required                                                                                                                                                                                               | [e.g., Minimum 500GB per node, specific StorageClass(es)]       |
| **Network**                                    | No special node networking is pre-requisited. The feature is based on primary UDN, thus is not dependent on secondary node NICs. Can and will be tested on both IPv4/6                                     |                                                                 |
| **Required Operators**                         | CNV                                                                                                                                                                                                        |                                                                 |
| **Platform**                                   | No special configuration required                                                                                                                                                                          |                                                                 |
| **Special Configurations**                     | Not required                                                                                                                                                                                               |                                                                 |

#### **5.5. Testing Tools & Frameworks**

Document any **new or additional** testing tools, frameworks, or infrastructure required specifically for this feature.

**Note:** Only list tools that are **new** or **different** from standard testing infrastructure. Leave empty if using standard tools.

| Category            | Tools/Frameworks  |
|:------------------- |:----------------- |
| **Test Framework**  | None              |
| **CI/CD**           | None              |
| **Other Tools**     | None              |

#### **6. Entry Criteria**

The following conditions must be met before testing can begin:

- [ ] Requirements and design documents are **approved and merged**
- [ ] Test environment can be **set up and configured** (see Section II.5 - Test Environment)
- [ ] The starting point of this testing, from Openshift VIrtualization networking perspective, is by performing the 2\
actions:\
  * Create the C/UDN resource, with the desired IP range specified in it
  * Create the VM manifest with the new `addresses` annotation\
At this point we cannot integrate with the third-party IPAM providers, so we need to patch 	these inputs ourselves.

#### **7. Risks and Limitations**

Document specific risks and limitations for this feature. If a risk category is not applicable, mark as "N/A" with justification in mitigation strategy.

**Note:** Empty "Specific Risk" cells mean this must be filled. "N/A" means explicitly not applicable with justification.

| Risk Category         | Specific Risk for This Feature                                                                                         | Mitigation Strategy  | Status  |
|:--------------------- |:---------------------------------------------------------------------------------------------------------------------- |:-------------------- |:------- |
| Timeline/Schedule     |                                                                                                                        |                      | [ ]     |
| Test Coverage         | STD is yet to be composed.                                                                                             |                      | [ ]     |
| Test Environment      | No special HW requirement; any stable cluster should do.                                                               |                      | [ ]     |
| Untestable Aspects    | The third-party integration. Our testing will start with the step of creating UDN and VM with `addresses` annotation.  |                      | [ ]     |
| Resource Constraints  | None                                                                                                                   |                      | [ ]     |
| Dependencies          |                                                                                                                        |                      | [ ]     |
| Other                 |                                                                                                                        |                      | [ ]     |

#### **8. Known Limitations**

Document any known limitations, constraints, or trade-offs in the feature implementation or testing approach.

- No support for ARM64 architecture in this release
- At this point the feature is limited only to primary UDN VM interface (no secondary).
- There will be no integration with the 3rd party providers; 3rd party is responsible for providing valid UDN and annotated VM specs, which will be the starting point of the testing in CNV.


---

### **III. Test Scenarios & Traceability**

This section links requirements to test coverage, enabling reviewers to verify all requirements are tested.

| Requirement ID     | Requirement Summary                                                              | Test Scenario(s)                                            | Test Type(s)     | Priority  |
|:------------------ |:---------------------------------------------------------------------------------|:----------------------------------------------------------- |:-----------------|:--------- |
| CNV-67524 (epic)          | The requirement is covered by these following scenarios:                         |                                                             |                  |           |
|                    | See the IP address in the VMI status                                             |                                                             | Functional       |           |
|                    | See it in the guest                                                              |                                                             | Functional       |           |
|                    | Verify the address is pingable                                                   |                                                             | Functional       |           |
|                    | Verify this interface can maintain TCP connectivity - east/west and north/south. |                                                             | Functional (E2E) |           |
|                    | The feature should be applied on both IPv4/6 families                            |                                                             | Functional                 |           |                                                         |                                                             |                              |           |
|                    | Verify the assigned address and connectivity are maintained after VM reboot.     |                                                             | Functional                 |           |
|                    | Verify the assigned address and connectivity are maintained after VM migration.  |                                                             | Functional                 |           |
|                    | Verify the assigned address can be reclaimed and re-used after deleting the VM   |                                                             | Functional                 |           |
|                    | Verify no collision - try annotating 2 VMs with the same IP claim.                                                                                | Functional                                                            |                  |           |
*
* v
* v
* v

---

### **IV. Sign-off and Approval**

This Software Test Plan requires approval from the following stakeholders:

* **Reviewers:**
  - Orel Misan: Main feature developer (Openshift Virtualization network)
  - Anat Wax / Asia Zhivov Khromov / Sergei Volkov: QE team colleagues
  - Edward Haas: Principal developer (Openshift Virtualization network)
  - Ruth Netser: Openshift Virtualization tech-lead
  - Petr Horacek: Openshift Virtualization network team lead
