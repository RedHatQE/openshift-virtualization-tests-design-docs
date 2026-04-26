# OpenShift Virtualization Tests – Test Plan

## **Native Support For VirtualMachine Templates – Quality Engineering Plan**

### **Metadata & Tracking**

- **Enhancement(s):** [VEP #76: Native Support For VirtualMachine Templates](https://github.com/kubevirt/enhancements/blob/main/veps/sig-compute/76-vmtemplates/vmtemplate-proposal.md)
- **Feature Tracking:** https://issues.redhat.com/browse/CNV-73392
- **Epic Tracking:** [CNV-73392](https://issues.redhat.com/browse/CNV-73392)
- **QE Owner(s):** Roni Kishner
- **Owning SIG:** sig-infra
- **Participating SIGs:** sig-compute

**Document Conventions:**
- **VMT / VMTemplate** – VirtualMachineTemplate (CRD in `template.kubevirt.io`)
- **VMTR** – VirtualMachineTemplateRequest (CRD for creating a template from an existing VM)
- **VEP** – KubeVirt Enhancement Proposal
- **OVA/OVF** – Open Virtualization Appliance / Open Virtualization Format (import/export, v1beta1; target CNV 4.23.0)

---

### **Feature Overview**

This enhancement adds native in-cluster VM templating to KubeVirt, enabling users to create, share, and manage VM blueprints directly within the cluster.
Users can define reusable templates from golden images or from existing VMs, then deploy new VMs from those templates with customizable parameters—via CLI or server-side API.
A dedicated CLI command (`virtctl template`) supports template processing, conversion from existing OpenShift Templates, and template creation from running VMs.
The feature targets alpha in CNV 4.22.0, when it will be deployed by the cluster operator under a feature gate.
Testing must cover template lifecycle, parameter substitution, cross-namespace usage, RBAC, operator deployment, CLI integration, and upgrade behavior.

---

### **I. Motivation and Requirements**

#### **1. Requirement & User Story**

- [ ] **Review Requirements**
  - Native golden-image and existing-VM templating, cross-namespace creation, RBAC for template/VM creation, optional import/export (OVA/OVF).

- [ ] **Understand Value**
  - Enables rapid, consistent VM deployment from in-cluster templates; reduces scripting and external tooling; aligns with traditional virtualization workflows for RH/OCP customers.

- [ ] **Customer Use Cases**
  - VM owner: create VM from golden-image template; create VM from template from existing VM; create VM from template in another namespace.
  - Template owner: import/export cluster-wide templates.
  - Cluster admin: RBAC to restrict VM creation to approved templates.

- [ ] **Testability**
  - The feature ships behind the KubeVirt **Template** feature gate. Enable the gate on tests.
  - A later OpenShift Virtualization / KubeVirt version is expected to include VM templates in the default deployment without the gate.

- [ ] **Acceptance Criteria**
  - VM owner can create a VM from a native in-cluster template.
  - VM owner can share native in-cluster templates between namespaces they control.
  - Deployment of virt-template (Template FeatureGate) is automated in CNV 4.22.
  - VirtualMachineTemplate (template.kubevirt.io) coexists with the existing OpenShift Template resource without conflicts (Console / CLI).

- [ ] **Non-Functional Requirements (NFRs)**
  - Performance, Scalability, Monitoring.

#### **2. Known Limitations**

The limitations are documented to ensure alignment between development, QA, and product teams.
The following are confirmed product constraints accepted before testing begins.

- **v1alpha1 does not remove sensitive data (SSH host keys, machine-ID, user data) from VMs before templating**
  - Users must manually remove sensitive information from a VM before creating a template from it.
  - *Sign-off:* TBD

- **Cross-namespace template-to-VM creation relies on a CDI workaround**
  - Uses a namespaced `SourceRef` reference to a golden image in another namespace; subject to future upstream Kubernetes behavior changes.
  - *Sign-off:* Felix Matouschek

- **Exported VirtualMachineTemplates are flattened**
  - A VirtualMachineTemplates including instanceTypes/Preferences will be flattened to include the instanceType/Preferences fields directly.
  - *Sign-off:* Felix Matouschek

#### **3. Technology and Design Review**

- [x] **Developer Handoff/QE Kickoff**
  - *Key takeaways and concerns:* Conducted meetings to align on testing strategy.

- [x] **Technology Challenges**
  - *List identified challenges:*
    - The feature is developed in a separate repository.
    - The feature is deployed by the cluster operator via a feature gate in 4.22.0, and plans to be deployed by default on 4.23.0+.
  - *Impact on testing approach:* All `virtctl template` and API tests run on **CNV 4.22.0+** clusters with the feature gate active.

- [x] **API Extensions**
  - *List new or modified APIs:*
    - New `template.kubevirt.io/v1alpha1` API group: VirtualMachineTemplate and VirtualMachineTemplateRequest resources.
    - New `/process` subresource (server-side template rendering) and `/create` subresource (server-side VM creation) on VirtualMachineTemplate.
    - New `virtctl template` commands: `process`, `convert`, `create` (available in `virtctl` in CNV 4.22.0).
    - New `Template` feature gate in the KubeVirt cluster operator CRD.
  - *Testing impact:*
    - New tests required for all new resource types, subresources, and CLI commands.
    - Tests involving CRD's and featureGates could be impacted.

- [x] **Test Environment Needs**
  - *See environment requirements in Section II.3 and testing tools in Section II.3.1*

- [x] **Topology Considerations**
  - *Describe topology requirements:* Standard cluster topology is sufficient; no multi-cluster or special network topology required.
  - *Impact on test design:* No architectural impact. Cross-namespace tests require two namespaces on a single cluster.

---

### **II. Software Test Plan (STP)**

This STP serves as the **overall roadmap for testing**, detailing the scope, approach, resources, and schedule.

#### **1. Scope of Testing**

**In scope:**
- Functional validation of VirtualMachineTemplate and VirtualMachineTemplateRequest: parameter substitution, `/process` and `/create` subresource behavior, `virtctl template process`, `template convert`, and `template create`.
- Creation of VMs from golden-image and from existing-VM templates.
- Cross-namespace template usage.
- RBAC for template and VM creation.
- Integration with instance types/preferences.
- Deployment of the feature by the cluster operator when the Template feature gate is enabled (CNV 4.22.0).
- Import of template CLI commands into `virtctl` (CNV 4.22.0).
- Admission-time validation of VirtualMachineTemplates (CNV 4.22.0).

**Testing Goals**

- **[P0]** Verify the cluster operator deploys the template feature when the Template feature gate is enabled.
- **[P0]** Verify VirtualMachineTemplate lifecycle: create, update, delete; parameter definition and substitution (e.g. `${NAME}`, `${DATA_SOURCE_NAME}`); the process subresource returns a valid VirtualMachine manifest.
- **[P0]** Verify VirtualMachineTemplateRequest: create from existing VM; the controller creates a VM snapshot, clones storage to the target namespace, and creates a VirtualMachineTemplate; status reflects completion or failure.
- **[P0]** Verify VM creation from template via the create subresource and via `virtctl template process ... | kubectl create -f -`; VM starts and is usable.
- **[P0]** Verify golden-image template flow: VirtualMachineTemplate referencing a data source with namespace; process/create yields a VM with correct storage and boot.
- **[P0]** Verify RBAC: cluster admin can restrict users to create VMs only from approved templates; template owner and VM owner permissions as per VEP.
- **[P1]** Verify `virtctl template convert`: existing OpenShift Template (with VM object) converts to VirtualMachineTemplate; parameters are preserved.
- **[P1]** Verify `virtctl template create`: generates a VirtualMachineTemplateRequest from existing VM; async flow completes and template is ready for process/create.
- **[P1]** Verify `virtctl template` commands (CNV 4.22.0+): `process`, `convert`, and `create` behave correctly and match the feature specification.
- **[P2]** Verify cross-namespace: template in namespace A, VM creation in namespace B.
- **[P2]** Verify compatibility with common-templates-style templates.
- **[P2]** Verify admission-time validation (CNV 4.22.0): when all required parameters have defaults, submitting a VirtualMachineTemplate that would render an invalid VM is rejected; valid templates are still accepted.

**Out of Scope (Testing Scope Exclusions)**

The following items are explicitly Out of Scope for this test cycle and represent intentional exclusions.
No verification activities will be performed for these items, and any related issues found will not be classified as defects for this release.

- **OVA/OVF import/export**
  - *Rationale:* Deferred to v1beta1 (CNV 4.23.0); not part of v1alpha1 scope.
  - *PM/Lead Agreement:* [Dominik Holler]

- **Guest sealing / sensitive data removal**
  - *Rationale:* Explicitly out of scope for v1alpha1; defined as user responsibility before creating a template.
  - *PM/Lead Agreement:* [Dominik Holler]

- **Performance/scale benchmarks**
  - *Rationale:* No NFR targets defined for this release; can be added as P3 in a later cycle.
  - *PM/Lead Agreement:* [Dominik Holler]

- **UI testing**
  - *Rationale:* Not required at Tech Preview / Alpha stage.
  - *PM/Lead Agreement:* [Dominik Holler]

**Test Limitations**

- **None — reviewed and confirmed that no test limitations apply for this release.**


#### **2. Test Strategy**

**Functional**

- [x] **Functional Testing** — Validates that the feature works according to specified requirements and user stories
  - *Details:* Core template resources, subresources, `virtctl` commands, RBAC.

- [x] **Automation Testing** — Confirms test automation plan is in place for CI and regression coverage (all tests are expected to be automated)
  - *Details:* Required for GA per STP guide.

- [x] **Regression Testing** — Verifies that new changes do not break existing functionality
  - Smoke tests should pass without impact.

**Non-Functional**

- [ ] **Performance Testing** — Validates feature performance meets requirements (latency, throughput, resource usage)
  - N/A for this release.

- [ ] **Scale Testing** — Validates feature behavior under increased load and at production-like scale
  - N/A for this release.

- [x] **Security Testing** — Verifies security requirements, RBAC, authentication, authorization, and vulnerability scanning
  - RBAC for template and VM creation.
  - admission policy for VirtualMachineTemplateRequest.

- [x] **Usability Testing** — Validates user experience and accessibility requirements
  - Validate `virtctl` command output and status conditions.
  - align with downstream console/UI requirements where applicable.

- [ ] **Monitoring** — Does the feature require metrics and/or alerts?
  - N/A for this release.

**Integration & Compatibility**

- [x] **Compatibility Testing** — Ensures feature works across supported platforms, versions, and configurations
  - coexistence with existing OpenShift Template-based flows.

- [x] **Upgrade Testing** — Validates upgrade paths from previous versions, data migration, and configuration preservation
  - Upgrade with Template feature gate and existing templates/VMTRs present.
  - verify data preservation and API compatibility.

- [ ] **Dependencies** — Blocked by deliverables from other components/products. Identify what we need from other teams before we can test.
  - N/A for this release.

- [x] **Cross Integrations** — Does the feature affect other features or require testing by other teams? Identify the impact we cause.
  - Affects common-templates under sig-virt.

**Infrastructure**

- [ ] **Cloud Testing** — Does the feature require multi-cloud platform testing? Consider cloud-specific features.
  - *Details:* N/A — same as the rest of OpenShift Virtualization.

#### **3. Test Environment**

- **Cluster Topology:** Standard — Agnostic.

- **OCP & OpenShift Virtualization Version(s):** OCP 4.22 (and up) with OpenShift Virtualization 4.22 (and up).

- **CPU Virtualization:** N/A

- **Compute Resources:** Sufficient for VM creation and snapshot/clone operations.

- **Special Hardware:** N/A

- **Storage:** StorageClass supporting data volumes and snapshot clones.

- **Network:** N/A

- **Required Operators:** virt-operator (with Template feature gate enabled).

- **Platform:** N/A

- **Special Configurations:** Template feature gate must be enabled in the KubeVirt CR.

#### **3.1. Testing Tools & Frameworks**


- **Test Framework:** OpenShift-Virtualization-tests repo for tier 2 and 3, while virt-template repo for tier 1.

- **CI/CD:** Dedicated lanes for virt-template tests.

#### **4. Entry Criteria**

The following conditions must be met before testing can begin:

- [x] Requirements and design documents are **approved and merged** (VEP #76 and any downstream OCP enhancement).
- [ ] Test environment can be **set up and configured**, including Template feature gate and feature deployment.
- [ ] VirtualMachineTemplate and VirtualMachineTemplateRequest APIs are available in the test cluster.
- [ ] Developer Handoff / QE Kickoff completed and untestable aspects agreed.
- [ ] `virtctl template` commands available.

#### **5. Risks**


**Timeline/Schedule**

- **Risk:** Feature spans a separate repository and cluster operator integration, test automation must be merged for GA.
  - **Mitigation:** Prioritize P0/P1 scenarios, automate in parallel with feature maturity.
  - *Estimated impact on schedule:* Minor delay if cluster operator integration is late.
  - *Sign-off:* Roni Kishner

**Test Coverage**

- **Risk:** Import/export and guest sealing are out of scope, cross-namespace testing is constrained by current CDI behavior.
  - **Mitigation:** Document limitations, test all in-scope flows thoroughly and trace all requirements to scenarios.
  - *Areas with reduced coverage:* OVA/OVF.
  - *Sign-off:* [Name/Date]

**Test Environment**

- **Risk:** Snapshot/clone and storage behavior may vary across storage backends.
  - **Mitigation:** Use supported storage backends; document any environment-specific restrictions.
  - *Missing resources or infrastructure:* None known at this stage.
  - *Sign-off:* [Name/Date]

---

### **III. Test Scenarios & Traceability**

<!-- This section links D/S requirements to test coverage, enabling reviewers to verify all requirements are tested.
**What goes here:** New test scenarios specific to this feature. Each scenario should trace to a D/S Jira requirement.
**What does NOT go here:** Regression tests (covered in Test Strategy). -->

- **[VEP76-VirtOperator]** — As a cluster admin, I want the cluster operator to deploy the template feature when the Template feature gate is enabled
  - *Test Scenario:* [Tier 1] Enable Template feature gate; verify the feature API and controller are deployed; basic resource list/create succeeds.
  - *Priority:* P0

- **[VEP76-Golden]** — As a VM owner, I want to create a VM from a golden-image template
  - *Test Scenario:* [Tier 1] Create VirtualMachineTemplate referencing a data source; process with parameters; create VM; verify VM boots and uses the correct disk.
  - *Priority:* P0

- **[VEP76-FromVM]** — As a VM owner, I want to create a template from an existing VM I have access to
  - *Test Scenario:* [Tier 1] Create VirtualMachineTemplateRequest for an existing VM; wait for Ready status; process the resulting template and create a VM in the same or a different namespace; verify the VM.
  - *Priority:* P0

- **[VEP76-ProcessAPI]** — As a user, I want server-side template processing via the process subresource
  - *Test Scenario:* [Tier 1] Call the `/process` subresource with parameters; verify the output is a valid VirtualMachine manifest.
  - *Priority:* P0

- **[VEP76-CreateAPI]** — As a user, I want to create a VM server-side from a template via the create subresource
  - *Test Scenario:* [Tier 1] Call the `/create` subresource; verify the VM is created and RBAC is respected.
  - *Priority:* P0

- **[VEP76-RBAC]** — As a cluster admin, I want to restrict users to create VMs only from approved templates
  - *Test Scenario:* [Tier 1] As a non-admin, create a VM from an allowed template (expect success) and from a disallowed template (expect rejection); verify the RBAC model matches the VEP.
  - *Priority:* P0

- **[VEP76-VirtctlProcess]** — As a user, I want to process a VirtualMachineTemplate via `virtctl template process`
  - *Test Scenario:* [Tier 1] Run `virtctl template process <name> -p KEY=VAL` against a cluster resource and a local file; pipe output to `kubectl create`; verify the VM is created and running.
  - *Priority:* P0

- **[VEP76-VirtctlConvert]** — As a template owner, I want to convert an OpenShift Template to a VirtualMachineTemplate via `virtctl template convert`
  - *Test Scenario:* [Tier 1] Convert an OpenShift Template containing a VM object; verify parameters and VM spec are preserved in the resulting VirtualMachineTemplate.
  - *Priority:* P1

- **[VEP76-VirtctlCreate]** — As a template owner, I want to create a VirtualMachineTemplateRequest from an existing VM via `virtctl template create`
  - *Test Scenario:* [Tier 1] Run `virtctl template create` from an existing VM; verify the VirtualMachineTemplateRequest is created; wait for the controller to complete; process the template and create a VM.
  - *Priority:* P1

- **[VEP76-VirtctlImport]** — As a user, I want `virtctl` (CNV 4.22.0+) to expose `template process`, `template convert`, and `template create` for VM templates
  - *Test Scenario:* [Tier 1] On a CNV 4.22.0 cluster, verify `virtctl template process`, `template convert`, and `template create` succeed and match expected results for the template feature.
  - *Priority:* P1

- **[VEP76-InstanceTypes]** — As a VM owner, I want templates to support instance types and preferences
  - *Test Scenario:* [Tier 1] Create a VirtualMachineTemplate with instance type and preference parameters; process and create a VM; verify sizing and preference are applied correctly.
  - *Priority:* P1

- **[VEP76-WindowsTemplate]** — As a VM owner, I want to run a Windows guest from a dedicated Windows VirtualMachineTemplate
  - *Test Scenario:* [Tier 1] Use a VirtualMachineTemplate built for Windows (dedicated image, parameters, and guest settings); process and create a VM; verify the Windows guest boots, disks and network are as defined, and the template’s Windows-specific values are applied.
  - *Priority:* P1

- **[VEP76-CrossNS]** — As a VM owner, I want to create a VM from a template stored in a different namespace
  - *Test Scenario:* [Tier 1] Template in namespace A; process and create VM in namespace B (within current CDI constraints); verify VM and storage.
  - *Priority:* P2

- **[VEP76-CommonTemplates]** — As a user, I want compatibility with common-templates-style templates
  - *Test Scenario:* [Tier 1] Verify that templates from the common-templates preview branch can be processed and used to create VMs.
  - *Priority:* P2

- **[VEP76-Upgrade]** — As a cluster admin, I want templates and template requests to be preserved across cluster upgrades
  - *Test Scenario:* [Tier 2] Pre-create VirtualMachineTemplates and VirtualMachineTemplateRequests; upgrade the cluster; verify templates still process and VMs can still be created from them.
  - *Priority:* P1

- **[VEP76-Admission]** — As a user, I expect admission-time validation to reject fundamentally broken templates (CNV 4.22.0)
  - *Test Scenario:* [Tier 2] With all required parameters defaulted, submit a VirtualMachineTemplate create/update that would render an invalid VirtualMachine; expect admission rejection. Confirm that valid templates are still accepted.
  - *Priority:* P2

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
