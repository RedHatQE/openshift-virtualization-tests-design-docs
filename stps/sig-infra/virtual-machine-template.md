# OpenShift Virtualization Tests – Test Plan

## **Native Support For VirtualMachine Templates – Quality Engineering Plan**

### **Metadata & Tracking**

| Field                  | Details                                                                                                                                 |
|:-----------------------|:----------------------------------------------------------------------------------------------------------------------------------------|
| **Enhancement(s)**     | [VEP #76: Native Support For VirtualMachine Templates](https://github.com/kubevirt/enhancements/blob/main/veps/sig-compute/76-vmtemplates/vmtemplate-proposal.md) |
| **Jira Tracking**      | https://issues.redhat.com/browse/CNV-73392                                                                                             |
| **QE Owner(s)**        | Roni Kishner                                                                                                                             |
| **Owning SIG**         | sig-infra                                                                                                                               |
| **Participating SIGs** |sig-compute                                                                                                                  |
| **Current Status**     | Draft                                                                                                                                   |

**Document Conventions:**
- **VMT / VMTemplate** – VirtualMachineTemplate (CRD in `template.kubevirt.io`)
- **VMTR** – VirtualMachineTemplateRequest (CRD for creating a template from an existing VM)
- **VEP** – KubeVirt Enhancement Proposal
- **CDI** – Containerized Data Importer
- **OVA/OVF** – Open Virtualization Appliance / Open Virtualization Format (import/export, later phase)

---

### **Feature Overview**

KubeVirt currently lacks native, in-cluster templating for VirtualMachines.
This enhancement introduces **VirtualMachineTemplate** (and related APIs) so users can create, share, and manage VM blueprints inside the cluster—supporting both **golden-image-based** templates and **templates created from existing VMs**.
It provides a `/process` subresource for server-side template processing, a `/create` subresource for creating VMs from templates, and **virtctl** commands (`template process`, `template convert`, `template create`).
A **VirtualMachineTemplateRequest** CRD orchestrates capturing an existing VM (via snapshot/clone) into a new template.
Testing must cover CRD lifecycle, parameter substitution, cross-namespace usage, RBAC, and integration with OpenShift Virtualization and common-templates.

---

### **I. Motivation and Requirements Review (QE Review Guidelines)**

#### **1. Requirement & User Story Review Checklist**

| Check                                  | Done | Details/Notes                                                                                                                                                                                                                                                                                                                                                                | Comments |
|:---------------------------------------|:-----|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:---------|
| **Review Requirements**                | [ ]  | Native golden-image and existing-VM templating, cross-namespace creation, RBAC for template/VM creation, optional import/export (OVA/OVF).                                                                                                                                                                                                                                   |          |
| **Understand Value**                   | [ ]  | Enables rapid, consistent VM deployment from in-cluster templates; reduces scripting and external tooling; aligns with traditional virtualization workflows for RH/OCP customers.                                                                                                                                                                                            |          |
| **Customer Use Cases**                 | [ ]  | VM owner: create VM from golden-image template; create VM from template from existing VM; create VM from template in another namespace.<br/>Template owner: import/export cluster-wide templates.<br/>Cluster admin: RBAC to restrict VM creation to approved templates.                                                                                                     |          |
| **Testability**                        | [ ]  | The use cases are testable through existing coverage of dependent features.                                                                                                                                                                                                                                                                                                  |          |
| **Acceptance Criteria**                | [ ]  | VM owner can create a VM from a native in-cluster template.<br/>VM owner can share native in-cluster templates between namespaces they control.<br/>Deployment of virt-template (Template FeatureGate) is automated in CNV 4.22.<br/>VirtualMachineTemplate (template.kubevirt.io) coexists with the existing OpenShift Template resource without conflicts (Console / CLI). |          |
| **Non-Functional Requirements (NFRs)** | [ ]  | Performance, Scalability, Monitoring, Docs.                                                                                                                                                                                                                                                                                                                                  |          |

#### **2. Technology and Design Review**

| Check                             | Done | Details/Notes                                                                                                  | Comments |
|:----------------------------------|:-----|:---------------------------------------------------------------------------------------------------------------|:---------|
| **Developer Handoff/QE Kickoff**  | [ ]  | Conducted meetings to align on testing strategy                                                                |          |
| **Technology Challenges**         | [ ]  | virt-template developed in separate repo, deployed by virt-operator.                                           |          |
| **Test Environment Needs**        | [ ]  | Cluster with OpenShift Virtualization, virt-template feature gate enabled                                      |          |
| **API Extensions**                | [ ]  | New APIGroup `template.kubevirt.io` (v1alpha1); VirtualMachineTemplate and VirtualMachineTemplateRequest CRDs; |          |
| **Topology Considerations**       | [ ]  | Changes are limited to test coverage updates; no architectural or multi-cluster topology impact.               |          |

---

### **II. Software Test Plan (STP)**

#### **1. Scope of Testing**

**In scope:**<br/>
- Functional validation of VirtualMachineTemplate and VirtualMachineTemplateRequest: parameter substitution, `/process` and `/create` subresource behavior, virtctl `template process`, `template convert`, and `template create`.<br/>
- Creation of VMs from golden-image and from existing-VM templates.<br/>
- Cross-namespace template usage.<br/>
- RBAC for template and VM creation.<br/>
- Integration with instance types/preferences.<br/>
- Deployment of virt-template by virt-operator when Template FeatureGate is enabled.

**Testing Goals**

- **[P0]** Verify virt-operator deploys virt-template when Template FeatureGate is enabled.
- **[P0]** Verify VirtualMachineTemplate CRD: create, update, delete; parameter definition and substitution (e.g. `${NAME}`, `${DATA_SOURCE_NAME}`); `process` subresource returns valid VirtualMachine manifest.
- **[P0]** Verify VirtualMachineTemplateRequest: create from existing VM; controller creates VMSnapshot, clones to DataVolumes in target namespace, creates VirtualMachineTemplate; status reflects completion/failure.
- **[P0]** Verify VM creation from template: via `/create` subresource and via `virtctl template process ... | kubectl create -f -`; VM starts and is usable where applicable.
- **[P0]** Verify golden-image template flow: VirtualMachineTemplate referencing DataSource (with namespace); process/create yields VM with correct storage and boot.
- **[P0]** Verify RBAC: cluster admin can restrict users to create VMs only from approved templates; template owner and VM owner permissions as per VEP.
- **[P1]** Verify virtctl `template convert`: existing OpenShift Template (with VM object) converts to VirtualMachineTemplate; parameters preserved.
- **[P1]** Verify virtctl `template create`: generates VirtualMachineTemplateRequest from existing VM; async flow completes and template is ready for process/create.
- **[P2]** Verify cross-namespace: template in namespace A, VM creation in namespace B.
- **[P2]** Verify compatibility with common-templates-style templates.
- **[P2]** Verify admission-time validation for VirtualMachineTemplate (v1.8.0): when all required parameters have defaults, create/update is rejected if rendering the template would produce an invalid `VirtualMachine` (structural issues that would always block a valid VM).

**Out of Scope (Testing Scope Exclusions)**

| Out-of-Scope Item                                                      | Rationale                                                            | PM/Lead Agreement |
|:-----------------------------------------------------------------------|:---------------------------------------------------------------------|:------------------|
| OVA/OVF import/export                                                  | Deferred to v1beta1 / v1.9.0; not part of v1alpha1 scope.            | [ ] Name/Date |
| Guest sealing / sensitive data removal                                 | Explicitly out of scope for v1alpha1, defined as user responsibility. | [ ] Name/Date |
| Performance/scale benchmarks                                           | can be P2 and tested later.                                          | [ ] Name/Date |
| UI testing                                                             | Not required at Tech Preview stage.                                 | [ ] Name/Date |

#### **2. Test Strategy**

| Item                           | Description                                                                                                                                                 | Applicable (Y/N or N/A) | Comments |
|:-------------------------------|:------------------------------------------------------------------------------------------------------------------------------------------------------------|:------------------------|:---------|
| Functional Testing             | Validates that the feature works according to specified requirements and user stories                                                                       | Y                       | Core CRDs, subresources, virtctl, RBAC. |
| Automation Testing             | Ensures test cases are automated for continuous integration and regression coverage                                                                         | Y                       | Required for GA per STP guide. |
| Performance Testing            | Validates feature performance meets requirements (latency, throughput, resource usage)                                                                      | N/A or P2               | Only if NFRs specify; otherwise defer. |
| Security Testing               | Verifies security requirements, RBAC, authentication, authorization                                                                                         | Y                       | RBAC for template/VM creation; admission for VMTR. |
| Usability Testing              | Validates user experience, UI/UX; feature may be consumed via UI (e.g. console)                                                                             | Y                       | Align with downstream console/UI requirements. |
| Compatibility Testing          | Ensures feature works across supported OCP/OpenShift Virtualization versions and configurations                                                             | Y                       | Version matrix as per release. |
| Regression Testing             | Verifies that new changes do not break existing VM and storage workflows                                                                                    | Y                       | Snapshot, clone, DataVolume, VM lifecycle. |
| Upgrade Testing                | Validates upgrade with Template FeatureGate and existing templates/VMTRs                                                                                    | Y                       | Data preservation and API compatibility. |
| Backward Compatibility Testing | Ensures compatibility with existing OpenShift Template-based flows if convert path is supported                                                             | Y                       | `virtctl template convert` and process. |
| Dependencies                   | CDI (DataVolume, DataSource, snapshot/clone), KubeVirt (VM, VMSnapshot), virt-operator                                                                      | Y                       | Document which team owns which tests. |
| Cross Integrations             | common-templates, console                                                                                                                                   | Y                       | Identify ownership (sig-infra vs sig-compute). |
| Monitoring                     | Metrics/alerts for virt-template controller and API                                                                                                         | N/A                     | Per VEP; confirm with Dev. |
| Cloud Testing                  | Multi-cloud platform testing                                                                                                                                | N/A                     | Same as rest of OpenShift Virtualization unless feature-specific. |

#### **3. Test Environment**

| Environment Component                         | Configuration | Specification Examples                                         |
|:----------------------------------------------|:--------------|:---------------------------------------------------------------|
| **Cluster Topology**                          | Standard      | Agnostic.                                                      |
| **OCP & OpenShift Virtualization Version(s)** | Required      | OCP 4.22 (and up) with OpenShift Virtualization 4.22 (and up). |
| **CPU Virtualization**                        | N/A           |                                                                |
| **Compute Resources**                         | Required      | Sufficient for Windows VM and snapshot/clone operations.       |
| **Special Hardware**                          | N/A           |                                                                |
| **Storage**                                   | Required      | StorageClass supporting  DataVolumes and snapshot clones.      |
| **Network**                                   | Standard      | Agnostic.                                                      |
| **Required Operators**                        | Yes           | virt-operator.                                                 |
| **Platform**                                  | N/A           |                                                                |
| **Special Configurations**                    | N/A           |                                                                |

#### **3.1. Testing Tools & Frameworks**

| Category           | Tools/Frameworks |
|:-------------------|:-----------------|
| **Test Framework** | Existing OpenShift Virtualization test framework (e.g. ginkgo); virt-template repo may have its own functional tests per VEP. |
| **CI/CD**          | Dedicated or shared lanes for template tests; virt-operator deployment test in core KubeVirt. |
| **Other Tools**    | kubectl, virtctl; optional golden image/DataSource setup for golden-image template tests. |

#### **4. Entry Criteria**

The following conditions must be met before testing can begin:

- [ ] Requirements and design documents are **approved and merged** (VEP #76 and any downstream OCP enhancement).
- [ ] Test environment can be **set up and configured** (see Section II.3 – Test Environment), including Template FeatureGate and virt-template deployment.
- [ ] VirtualMachineTemplate and VirtualMachineTemplateRequest CRDs and APIs are available in the test cluster.
- [ ] Developer Handoff / QE Kickoff completed and untestable aspects agreed.

#### **5. Risks**

| Risk Category        | Specific Risk for This Feature                                                                 | Mitigation Strategy                                                                 | Status |
|:---------------------|:-----------------------------------------------------------------------------------------------|:-------------------------------------------------------------------------------------|:-------|
| Timeline/Schedule    | Feature spans virt-template repo and virt-operator integration; test automation must be merged for GA. | Prioritize P0/P1 scenarios; automate in parallel with feature maturity; align with release milestones. | [ ]    |
| Test Coverage        | Import/export and sealing are out of scope; cross-namespace limited by CDI/KEP.                | Document limitations; test in-scope flows thoroughly; trace requirements to scenarios. | [ ]    |
| Test Environment     | Snapshot/clone and storage may have environment-specific behavior.                            | Use supported storage backends; document any restrictions.                           | [ ]    |
| Untestable Aspects   | Guest sealing, OVA/OVF, production-scale template count (unless NFR).                          | Explicit stakeholder agreement; document in Out of Scope and Limitations.            | [ ]    |
| Resource Constraints | Single QE or shared ownership across sig-infra/sig-compute.                                    | Clear ownership and handoff; reuse virt-template repo tests where possible.          | [ ]    |
| Dependencies         | CDI snapshot/clone, KubeVirt VMSnapshot; virt-operator and FeatureGate.                        | Coordinate with CDI/KubeVirt QE; define interface tests and ownership.               | [ ]    |
| Other                | common-templates migration (preview branch) may lag or diverge.                               | Define compatibility scope and fallback to manual template YAML tests.               | [ ]    |

#### **6. Known Limitations**

- v1alpha1 does **not** remove sensitive information (SSH host keys, machine-id, user data) from VMs before templating; users must do that before creating a template from an existing VM.
- Cross-namespace template-to-VM creation relies on current CDI workaround (e.g. SourceRef to DataSource in another namespace); subject to future KEP-3294/KEP-3766 behavior.
- OVA/OVF import/export is not in v1alpha1; no automated tests for import/export until that phase.
- Real-time guest quiescing and application-level sealing during template creation are out of scope for initial implementation.
- Per [VEP #76](https://github.com/kubevirt/enhancements/blob/main/veps/sig-compute/76-vmtemplates/vmtemplate-proposal.md), extended `VirtualMachineTemplate` status maintained by watching PVCs, `VolumeSnapshots`, `DataSources`, and similar resources was dropped (cost and complexity at scale). Validation is instead performed at admission time when all required parameters have defaults: the admitter renders the `VirtualMachine` and rejects create/update if the result would be invalid.

---

### **III. Test Scenarios & Traceability**

| Requirement ID    | Requirement Summary (from VEP #76 / Jira) | Test Scenario(s) | Tier | Priority |
|:------------------|:------------------------------------------|:-----------------|:-----|:---------|
| VEP76-Golden      | VM owner creates templated VM referencing a golden image | Create VirtualMachineTemplate with DataSource ref; process with parameters; create VM; verify VM boots and uses correct disk. | T1   | P0       |
| VEP76-FromVM      | VM owner creates templated VM from an existing VM | Create VirtualMachineTemplateRequest for existing VM; wait for Ready; process template and create VM in same or different namespace; verify VM. | T1   | P0       |
| VEP76-CrossNS     | VM owner creates VM from template in another namespace | Template in namespace A; process/create VM in namespace B (within CDI constraints); verify VM and storage. | T1   | P2       |
| VEP76-ProcessAPI  | Server-side template processing | Call /process subresource with parameters; verify output is valid VirtualMachine YAML. | T1   | P0       |
| VEP76-CreateAPI   | Server-side VM creation from template | Call /create subresource; verify VM is created and respects RBAC. | T1   | P0       |
| VEP76-RBAC        | Cluster admin restricts users to create VMs only from approved templates | As non-admin, create VM from allowed template (success) and from disallowed template (reject); verify RBAC model. | T1   | P0       |
| VEP76-VirtctlProcess | virtctl template process | `virtctl template process <name> -p KEY=VAL` (cluster and file); output piped to kubectl create; VM created and runs. | T1   | P0       |
| VEP76-VirtctlConvert | virtctl template convert | Convert OpenShift Template (with VM) to VirtualMachineTemplate; verify parameters and VM spec preserved. | T1   | P1       |
| VEP76-VirtctlCreate  | virtctl template create | virtctl template create from existing VM; VMTR created; controller creates template; process and create VM. | T1   | P1       |
| VEP76-VirtOperator | virt-operator deploys virt-template when Template FeatureGate enabled | Enable gate; verify virt-template API and controller deploy; basic API list/create. | T1   | P0       |
| VEP76-InstanceTypes | Templates use instance types and preferences | Template with instancetype/preference params; process and create VM; verify sizing and preference applied. | T1   | P1       |
| VEP76-Upgrade     | Upgrade with templates and VMTRs present | Pre-create templates/VMTRs; upgrade cluster; verify templates still process and VMs can be created. | T2   | P1       |
| VEP76-Admission   | Admission-time validation (v1.8.0) | With all required parameters defaulted, submit `VirtualMachineTemplate` create/update that would render an invalid `VirtualMachine`; expect admission rejection. Valid templates still accepted. | T2   | P2       |

*Requirement IDs should be replaced or extended with Jira keys when available.*

---

### **IV. Sign-off and Approval**

This Software Test Plan requires approval from the following stakeholders:

- **Reviewers:**
  - TBD
- **Approvers:**
  - TBD

**Sign-off checklist (before GA):**
- [ ] Tier 1 / Tier 2 tests defined and traceability matrix updated.
- [ ] **Test automation merged** (mandatory for GA).
- [ ] Tests running in release checklist / CI jobs.
- [ ] Documentation reviewed (virtctl, API, user-facing docs).
- [ ] Feature sign-off by QE.
