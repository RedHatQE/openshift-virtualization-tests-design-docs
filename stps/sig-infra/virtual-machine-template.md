# OpenShift Virtualization Tests – Test Plan

## **Native Support for VM Templates – Quality Engineering Plan**

### **Metadata & Tracking**

- **Enhancement(s):**
  - [VEP #76: Native support for VM templates](https://github.com/kubevirt/enhancements/issues/76)
    — [merged proposal](https://github.com/kubevirt/enhancements/blob/main/veps/sig-compute/76-vmtemplates/vmtemplate-proposal.md)
  - [VEP #256: OCI artifact export for VMs and VM templates](https://github.com/kubevirt/enhancements/issues/256)
- **Feature Tracking:** [VIRTSTRAT-529](https://redhat.atlassian.net/browse/VIRTSTRAT-529)
- **Epic Tracking:** [CNV-73392](https://issues.redhat.com/browse/CNV-73392)
- **Feature Maturity:**
  - DP: 4.21 - Deployed by manual installation
  - TP: 4.22 - Deployed by enabling a feature gate
  - GA: 5.0 - Deployed by default
- **QE Owner(s):** Roni Kishner (rkishner@redhat.com)
- **Owning SIG:** sig-infra

**Document Conventions:**
- **Native VM template** – In-cluster reusable definition used to create new VMs with consistent shape and parameters.
- **Template-from-VM** – Workflow where an administrator or VM owner captures an existing VM as a reusable template.
- **OCI artifact export** – Packaging VMs and VM templates as OCI layouts for offline transfer or registry distribution ([VEP #256](https://github.com/kubevirt/enhancements/issues/256))

---

### **Feature Overview**

Cluster administrators and VM owners get reusable **native VM templates**: save a VM design as a template, adjust parameters, and create matching VMs from the command line or automation the same way they manage other cluster resources.
Templates can be authored from manifests or captured from an existing VM.

---

### **I. Motivation and Requirements**

#### **1. Requirement & User Story**

- [x] **Review Requirements**
  - convert an existing VM manifest into a reusable template, create new VMs from templates, and control who may create or use templates and VMs.

- [x] **Understand Value**
  - Enables rapid, consistent VM deployment from in-cluster templates.
  - Allows templates to capture in-cluster and cluster-dependent resources, while instancetypes and preferences remain cluster-agnostic.
  - Reduces scripting and external tooling.
  - Aligns with traditional virtualization workflows for RH/OCP customers.

- [x] **Customer Use Cases**
  - **VM owner**
    - Create and share reusable templates from manifests or from an existing VM containing cluster-dependent resources.
    - Create VMs from templates and boot sources.
    - Use cross-namespace flows.
  - **Cluster admin**
    - Control who can view, add, and edit specific templates.
    - Control who can create VMs from approved templates.

- [x] **Testability**
  - The feature ships behind the KubeVirt **Template** feature gate. Enable the gate on tests.
  - A later OpenShift Virtualization / KubeVirt version is expected to include VM templates in the default deployment without the gate.

- [x] **Acceptance Criteria**
  - A cluster administrator can enable the templates feature gate so that VM templates are available on the cluster (v4.22.0).
  - A cluster administrator can disable the templates feature gate so that VM templates are not available on the cluster (v5.0.0)
  - A cluster user can create a VM from a native in-cluster template.
  - A cluster user can share the content of the templates between namespaces they control, so that a VM from namespace `A` is created on namespace `B`.
  - A cluster administrator can use namespace permissions so only intended users can manage VM templates or create VMs from them, and can restrict users so they may create VMs only from templates.
  - A cluster user can still create VMs from OpenShift Templates in the web console, VM templates are available alongside those options and do not remove or replace them.

- [x] **Non-Functional Requirements (NFRs)**
  - **Security:** Verify VM creation flows through templates do not by-pass namespace restriction.
  - *Note any NFRs not covered and why:*
    - UI: updated templates display is validated by the [UI team](https://redhat.atlassian.net/browse/CNV-67254).
    - Documentation quality are not covered in this STP and are addressed in dedicated docs channels.

#### **2. Known Limitations**

- **Templates expand instance types / preferences profiles into explicit fields**
  - When a template references an instance type or preference, the saved template copies the resulting CPU, memory, and guest settings into the template instead of keeping a link to the shared object. Later changes to that instance type or preference do not apply to VMs created from the template.
  - *Sign-off:* Ronen Sde-Or (ronen@redhat.com) / 01-06-2026

- **Template-from-VM does not preserve backing storage**
  - Capturing a template from an existing VM does not carry over backing storage details, so customers cannot rely on that path to preserve persistent vTPM or EFI settings from the source VM in the template today. [Tracked Jira](https://redhat.atlassian.net/browse/CNV-79308)
  - *Sign-off:* Ronen Sde-Or (ronen@redhat.com) / 01-06-2026

- **Template-from-VM anonymization is definition-only**
  - The product strips obvious unique identifiers (UUID, serial, MAC) from the captured definition only.
    Guest identity and secrets on disk can still carry into new VMs, so customers must prepare guests and disks before reuse to avoid conflicts, leakage, or compliance issues.
  - *Sign-off:* Ronen Sde-Or (ronen@redhat.com) / 01-06-2026

#### **3. Technology and Design Review**

- [x] **Developer Handoff/QE Kickoff**
  - *Key takeaways and concerns:*
    - During the Alpha stage the testing will be done using the virt-operator repository tests
    - Starting from Tech Preview openshift-virtualization-tests repository will be adding tests, with focus on feature gate/deployment while upgrading

- [x] **API Extensions**
  - *List new or modified APIs:*
    - New CRD - **VirtualMachineTemplate** and **VirtualMachineTemplateRequest**: manage templates, render a VM spec, create a VM from a template.
    - New CLI sub-command — **`virtctl template`**: `process`, `convert`, `create` (CNV 4.22.0+).

---

### **II. Software Test Plan (STP)**

#### **1. Scope of Testing**

**Testing Goals**

- **[P0]** As a VM owner, I can create a runnable VM from a template backed by a boot source, with correct CPU, memory, disk, and boot configuration — using both declarative and CLI-driven flows.
- **[P0]** As a VM owner, I can capture a template from an existing VM and see clear success or failure; on success the template is reusable in the expected namespace.
- **[P0]** As a cluster admin, I can restrict which users may create or capture templates and which may create VMs from them.
- **[P1]** As a template owner, I can convert an OpenShift Template that contains a VM into a native VM template without losing customer-facing parameters.
- **[P1]** As a VM owner, templates honor sizing profiles and preferences so created VMs pick up the chosen shapes and defaults.
- **[P1]** As a Windows VM owner, I can build a Windows-oriented template and create a guest that boots with expected disks, network, and Windows-specific settings.
- **[P1]** As a cluster admin, templates and vm template requests survive cluster upgrade and remain usable afterward.
- **[P2]** As a VM owner, I can use a template from another namespace to create a VM where cross-namespace creation is supported.
- **[P2]** As a cluster admin, when I disable and re-enable the Template capability, workflows are blocked while disabled and recover predictably after re-enable, which could lead to data loss of existing CustomResources.

**Out of Scope (Testing Scope Exclusions)**

- **Performance/scale testing**
  - *Rationale:* No NFR targets defined for 5.0.0; can be added as P3 [in 5.0.1](https://redhat.atlassian.net/browse/CNV-86058).
  - *Sign-off:* [Dominik Holler / 1.5.2026]

- **Monitoring** — Does the feature require metrics and/or alerts?
  - N/A for 5.0.0.
  - *Sign-off:* [Dominik Holler / 1.5.2026]

**Test Limitations**

- **OCI artifact export (VM and VM template packaging)**
  - *Rationale:* Portable export uses the OCI artifact format defined in VEP #256 (merged in [kubevirt/enhancements PR #257](https://github.com/kubevirt/enhancements/pull/257)), delivery is gated and follows the OpenShift Virtualization roadmap—deferred beyond this feature's Tech Preview scope.
  - *Sign-off:* [Dominik Holler / 1.5.2026]

#### **2. Test Strategy**

**Functional**

- [x] **Automation Testing** — Confirms test automation plan is in place for CI and regression coverage (all tests are expected to be automated)
  - Tech Preview: automated suites run against a full OpenShift Virtualization cluster.
  - Tech Preview: coverage for Template capability enabled, disabled, and toggled.
  - GA: upgrade-focused coverage at the agreed tier.

**Non-Functional**

- [ ] **Performance/Scale Testing** — Validates feature performance meets requirements (latency, throughput, resource usage)
  - Out of scope for 5.0.0 (see Section II.1 Out of Scope).

- [x] **Security Testing** — Verifies security requirements, RBAC, authentication, authorization, and vulnerability scanning
  - RBAC for who may define templates and who may create VMs from them.
  - Cluster validation when customers request template-from-VM capture (who may start a capture and what is rejected).

**Integration & Compatibility**

- [x] **Compatibility Testing** — Ensures feature works across supported platforms, versions, and configurations
  - coexistence with existing OpenShift Template-based flows.

- [x] **Upgrade Testing** — Validates upgrade paths from previous versions, data migration, and configuration preservation
  - Upgrade with the Template capability enabled and existing templates plus vm template requests on the cluster.
  - Verify customer data is preserved and supported workflows still behave as documented after upgrade.

- [x] **Dependencies** — Blocked by deliverables from other components/products. Identify what we need from other teams before we can test.
  - N/A for 5.0.0.

- [x] **Cross Integrations** — Does the feature affect other features or require testing by other teams? Identify the impact we cause.
  - Affects common-templates under the UI team.

**Infrastructure**

- [x] **Cloud Testing** — Does the feature require multi-cloud platform testing? Consider cloud-specific features.
  - *Details:* N/A — same as the rest of OpenShift Virtualization.

#### **3. Test Environment**

- **Cluster Topology:** Standard — Agnostic.

- **OCP & OpenShift Virtualization Version(s):** OCP 4.22 (and up) with OpenShift Virtualization 4.22 (and up).

- **CPU Virtualization:** N/A

- **Compute Resources:** Sufficient for VM creation and snapshot/clone operations.

- **Special Hardware:** N/A

- **Storage:** Storage type should support snapshot / cloning.

- **Network:** N/A

- **Required Operators:** OpenShift Virtualization installed through the supported operator path, with the Template customer capability enabled on the deployment.

- **Platform:** N/A

- **Special Configurations:** Template capability gate turned on for the OpenShift Virtualization instance under test.

#### **3.1. Testing Tools & Frameworks**

- **Test Framework:** OpenShift-Virtualization-tests repo for tier 2 and tier 3 (very long tests), while virt-template repo for tier 1.

- **CI/CD:** Dedicated lanes for virt-template tests.

#### **4. Entry Criteria**

The following conditions must be met before testing can begin:

- [x] Requirements and design documents are **approved and merged**.
- [x] Test environment can be **set up and configured**, including the Template capability gate and healthy template component rollout.
- [x] Native VM template and template-from-VM capture workflows are available on the test cluster through supported interfaces.
- [x] Developer Handoff / QE Kickoff completed and untestable aspects agreed.
- [x] `virtctl template` commands (`process`, `convert`, `create`) for template processing, legacy conversion, and template-from-VM capture are available in the test build.

#### **5. Risks**

**Test Environment**

- **Risk:** Snapshot-enabled storage class behavior has not been validated yet for this feature, so test results may vary once snapshot-backed environments are exercised.
  - **Mitigation:** Add dedicated validation on a snapshot-capable storage class early in execution and expand coverage to include create/update/restore template flows to uncover storage-specific failures.
  - *Missing resources or infrastructure:* Confirmed snapshot storage class test coverage and known-issue baseline for snapshot-backed clusters.
  - *Sign-off:* Roni Kishner / 01-06-2026

---

### **III. Test Scenarios & Traceability**

- **[CNV-73392]** — As a VM owner, I want to create a VM from an available boot source using a template
  - *Test Scenario:* [Tier 1] Validate the end-to-end flow for creating a runnable VM from a template backed by an available namespaced boot source.
  - *Priority:* P0

- **[CNV-73392]** — As a VM owner, I want to capture a reusable template from an existing VM I am allowed to manage
  - *Test Scenario:* [Tier 1] Validate the template-from-VM capture flow and downstream reuse of the captured template to create a VM in an allowed namespace.
  - *Priority:* P0

- **[CNV-73392]** — As a VM owner, I want the cluster to expand a template with my parameters into a runnable VM definition
  - *Test Scenario:* [Tier 1] Validate the server-side template processing flow that renders user parameters into a runnable VM definition.
  - *Priority:* P0

- **[CNV-73392]** — As a VM owner, I want to create a VM directly from a template in one step where the product supports it
  - *Test Scenario:* [Tier 1] Validate the supported single-step create-from-template flow, including expected namespace placement and access behavior.
  - *Priority:* P0

- **[CNV-73392]** — As a cluster admin, I want to restrict users to create VMs only from approved templates
  - *Test Scenario:* [Tier 1] Validate RBAC enforcement for allowed versus disallowed template usage when creating VMs.
  - *Priority:* P0

- **[CNV-73392]** — As a VM owner, I want to render a template to a VM definition from the CLI and create the workload with standard tooling
  - *Test Scenario:* [Tier 1] Validate the `virtctl template process` render-and-create flow for both cluster templates and local template files.
  - *Priority:* P0

- **[CNV-73392]** — As a template owner, I want to migrate an OpenShift Template that contains a VM into a native VM template without losing customer-facing parameters
  - *Test Scenario:* [Tier 1] Validate `virtctl template convert` from legacy OpenShift Template format to native VM template format with preservation of customer-facing parameters.
  - *Priority:* P1

- **[CNV-73392]** — As a VM owner or admin, I want to start template-from-VM capture from the CLI and end with a template I can reuse
  - *Test Scenario:* [Tier 1] Validate the `virtctl template create` template-from-VM capture flow through to successful reuse of the resulting template.
  - *Priority:* P1

- **[CNV-73392]** — As a VM owner, I want templates to honor sizing profiles, preferences, and supporting configuration I reference
  - *Test Scenario:* [Tier 1] Validate that VM templates consistently apply referenced sizing profiles, preferences, and supporting configuration in the resulting VM.
  - *Priority:* P1

- **[CNV-73392]** — As a VM owner, I want a Windows-oriented template to produce a runnable Windows guest with the expected disks, network, and guest settings
  - *Test Scenario:* [Tier 1] Validate the Windows-focused template flow that results in a runnable guest with expected Windows-specific configuration.
  - *Priority:* P1

- **[CNV-73392]** — As a VM owner, I want to create a VM from a template that lives in another namespace when cross-namespace use is supported
  - *Test Scenario:* [Tier 1] Validate supported cross-namespace template consumption flow for creating VMs in a target namespace.
  - *Priority:* P2

- **[CNV-73392]** — As a cluster admin, I want templates and vm template requests to survive cluster upgrades
  - *Test Scenario:* [Tier 2] Validate upgrade continuity for existing templates and vm template requests, including post-upgrade template usability.
  - *Priority:* P1

- **[CNV-73392]** — As a template author, I want the cluster to reject templates that would always produce an invalid VM when defaults fill required parameters (OpenShift Virtualization 4.22)
  - *Test Scenario:* [Tier 2] Validate admission behavior for invalid-by-default templates and acceptance behavior for valid templates under defaulted parameters.
  - *Priority:* P2

- **[CNV-73392]** — As a cluster admin, I want template workflows unavailable when the Template capability is disabled
  - *Test Scenario:* [Tier 2] Validate capability-disable behavior that blocks new template workflows while preserving expected handling of existing objects.
  - *Priority:* P2

- **[CNV-73392]** — As a cluster admin, I want template workflows to recover after I re-enable the Template capability
  - *Test Scenario:* [Tier 2] Validate disable-to-reenable recovery flow for template workflows and predictable handling of existing template-related objects.
  - *Priority:* P2


---

### **IV. Sign-off and Approval**

This Software Test Plan requires approval from the following stakeholders:

- **Reviewers:**
  - QE Members: [Geetika Kapoor](@geetikakay), [Michal Jankowski](@mijankow)
  - Team lead: [Dominik Holler](@dominikholler)
- **Approvers:**
  - Dev Lead: [Felix Matouschek] (@0xFelix)
  - Product Manager/Owner: Ronen Sde-Or (ronen@redhat.com)
  - QE Architect (OCP-V): [Ruth Netser](@rnetser)

**Sign-off checklist (before GA):**

- [x] Tier 1 / Tier 2 tests defined and traceability matrix updated.
- [ ] **Test automation merged** (mandatory for GA).
- [ ] Tests running in release checklist / CI jobs.
- [ ] Documentation reviewed (CLI, automation surfaces, and end-user guides).
- [ ] Feature sign-off by QE.
