# Openshift-virtualization-tests Test plan

## Golden Images Support For Heterogeneous Clusters - Quality Engineering Plan**

### **Metadata & Tracking**

| Field                  | Details                                                                                                                          |
|:-----------------------|:---------------------------------------------------------------------------------------------------------------------------------|
| **Enhancement(s)**     | [dic-on-heterogeneous-cluster](https://github.com/kubevirt/enhancements/tree/main/veps/sig-storage/dic-on-heterogeneous-cluster) |
| **Feature in Jira**    | [VIRTSTRAT-494](https://issues.redhat.com/browse/VIRTSTRAT-494)                                                                  |
| **Jira Tracking**      | [CNV-67900](https://issues.redhat.com/browse/CNV-67900)                                                                          |
| **QE Owner(s)**        | Harel Meir                                                                                                                       |
| **Owning SIG**         | sig-iuo                                                                                                                          |
| **Participating SIGs** | sig-infra, sig-storage, sig-virt                                                                                                 |
| **Current Status**     | Draft                                                                                                                            |

---

### **I. Motivation and Requirements Review (QE Review Guidelines)**
This section documents the mandatory QE review process. The goal is to understand the feature's value, technology, and testability prior to formal test planning.

#### **1. Requirement & User Story Review Checklist**

| Check                                  | Done | Details/Notes                                                                                                                                                                           | Comments |
|:---------------------------------------|:-----|:----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:---------|
| **Review Requirements**                | [V]  | Reviewed the relevant requirements.                                                                                                                                                     |          |
| **Understand Value**                   | [V]  | Confirmed clear user stories and understood.  <br/>Understand the difference between U/S and D/S requirements<br/> **What is the value of the feature for RH customers**.               |          |
| **Customer Use Cases**                 | [V]  | Ensured requirements contain relevant **customer use cases**.                                                                                                                           |          |
| **Testability**                        | [V]  | Confirmed requirements are **testable and unambiguous**.                                                                                                                                |          |
| **Acceptance Criteria**                | [v]  | Ensured acceptance criteria are **defined clearly** (clear user stories; D/S requirements clearly defined in Jira).                                                                     |          |
| **Non-Functional Requirements (NFRs)** | [V]  | Confirmed coverage for NFRs, including Performance, Security, Usability, Downtime, Connectivity, Monitoring (alerts/metrics), Scalability, Portability (e.g., cloud support), and Docs. |          |

#### Overview

Golden images are commonly used OS boot disk images that are used to create virtual machines (VMs) in a Kubernetes
cluster. Their purpose is to ensure these images are automatically available and kept up-to-date. The original design of
the golden images is documented in the [kubevirt/community repository](https://github.com/kubevirt/community/blob/69d061862e0839608932d225a728a7a6e7a89f29/design-proposals/golden-image-delivery-and-update-pipeline.md).

The initial design assumed homogeneous clusters, where all nodes in the cluster share the same architecture. However, as
there is a need to support heterogeneous clusters, where nodes may have different architectures (e.g., `arm64`, `amd64`,
`s390x`), this assumption does not apply anymore, and some changes are required to support this use-case.

#### Motivation

The high level flow of the golden images is as follows:

1. The HyperConverged Cluster Operator (HCO) image, includes predefined DataImportCronTemplate files. HCO generates
   a list of `DataImportCronTemplate` objects in the `SSP` CR, based on these files.
2. SSP creates `DataImportCron` CRs from the `DataImportCronTemplate` objects in the `SSP` CR.
3. Either SSP or CDI create a `DataSource` CRs based on the `DataImportCron` CRs.
   The CDI monitors the `DataImportCron` CRs, and ensures the corresponding `DataSource` CRs are updated as needed.
4. CDI checks the image URL or the ImageStream periodically (according to the cron expression in the
   `DataImportCron` CR), and if the image is updated, it creates a new `VolumeSnapshot` (or a `PVC`), imports the
   latest version of the requested image into this new `VolumeSnapshot`/`PVC`, and modifies the `DataSource` CR to point
   to the latest `VolumeSnapshot`/`PVC`.
   
   To perform the actual import, CDI creates a `DataVolume` CR, from the `spec.template` field in the `DataImportCron`
   CR.
5. When creating a VM, users set the VM's `spec.dataVolumeTemplate` field, to point to the desired `DataSource` CR.
   CDI creates a new `PVC`, and clones the `VolumeSnapshot`/`PVC` that is referenced by the `DataSource`,
   into this `PVC`.

Cluster administrators can create custom golden images, by adding `DataImportCronTemplate` objects to the
`HyperConverged` CR. The HCO adds these custom templates to the `SSP` custom resource, initiating the same workflow.

**Technology Challenges**  
The current design assumes homogeneous clusters, where all nodes in the cluster share the same architecture. However,
heterogeneous clusters with nodes of different architectures (e.g., `arm64`, `amd64`, `s390x`) introduce challenges:

* CDI-importer may pick wrong arch image to pull:
The predefined `DataImportCronTemplate` already configured with multi-architecture images (image manifests pointing to
multiple architecture-specific images). However, when the cdi-importer pulls an image, it selects one suitable for the
node's architecture, which may not match the architecture of the VM being created. For example, pulling an `arm64`
image for a VM running on an `amd64` node will cause the VM to fail.

* Custom templates arch specific
Users may need to create VMs with specific architectures to run architecture-specific applications. For that, they
will want to create a custom golden image with a specific architecture, and use it to create VMs with the same
architecture. This use-case is not supported by the current design.

##### HCO part

#### User stories

1. As a VM creator, I want to create virtual machines with specific architectures to run architecture-specific applications.
2. As a cluster administrator, I want to define custom golden images with multi-architecture support, enabling VM  creators to deploy VMs with the desired architecture.
3. As a VM creator, I want my existing tools and script will continue to work as before, without any changes.


#### **2. Technology and Design Review**

| Check                            | Done | Details/Notes                                                                     | Comments                 |
|:---------------------------------|:-----|:----------------------------------------------------------------------------------|:-------------------------|
| **Developer Handoff/QE Kickoff** | [V]  | Met with Nahshon from HCO team.                                                   |                          |
| **Technology Challenges**        | [V]  | CDI-importer picking the correct image arch, custom templates arch specific       |                          |
| **Test Environment Needs**       | [V]  | HA cluster for simple functionality testing, MultiArch cluster for full coverage. | Jenkins deploy job exist |
| **API Extensions**               | [V]  | HCO nodeInfo, dataImportCronTemplates                                             |                          |
| **Topology Considerations**      | [V]  | ARM64 and S390X vms are supported since cnv-4.19                                  |                          |




### **II. Software Test Plan (STP)**

This STP serves as the **overall roadmap for testing**, detailing the scope, approach, resources, and schedule.

#### **1. Scope of Testing**

This testplan covers FG activation, propagation to other components and new alerts & metrics tested.

**Document Conventions (if applicable):**  
- **MultiArch cluster** - heterogeneous cluster with 3 amd64 control-plane nodes, 2 amd64 worker nodes, and 1/2 arm64 worker nodes.
- **HA cluster** - homogenous cluster with 3 control-plane and 3 amd64 worker node.
- **Archs** - architectures.
- **Related resources** - golden images accosiated DataImportCron,DataSource,DV/VMsnapshot CRs.
- **FG** - enableMultiArchBootImageImport FeatureGate in HCO CR enabling this feature.

**In Scope:**
##### Functional Testing
- HCO monitors the cluster's nodes architectures correctly.
- HCO dataImportCronTemplates annotations listing the correct architectures and propagates to SSP.
- Correct resources created and ready to use for common golden images per arch.
- Correct resources created and ready to use for custom golden images per arch.

##### Non-Functional Testing  
**Regression Testing**
- spec.workloads.nodePlacement should determine the workload nodes architecture.
- spec.workloads.nodePlacement of not existing arch.

**Backward Compatibility Testing**
- Legacy Datasource points to the arch specific Datasource

**Upgrade testing**
- Verify that resources names preserved as expected after upgrade.


#### **2. Testing Goals**

Define specific, measurable testing objectives for this feature, such as:

- [ ] Achieve 100% feature coverage for core functionality.
- [x] Validate feature enablement until related resources created as expected.
- [x] Verify backward compatibility with legacy dataSources.
- [x] Verify NodePlacement.
- [x] Verify negative scenarios.
- [x] Verify new alerts & metrics
- [x] Verify related resources names preserved as expected after upgrade.
- [ ] Automate 100% of functional tests.


#### **3. Non-Goals (Testing Scope Exclusions)**

Explicitly document what is **out of scope** for testing. **Critical:** All non-goals require explicit stakeholder agreement to prevent "I assumed you were testing that" issues.


| Non-Goal                         | Rationale                                                         | PM/ Lead Agreement |
|:---------------------------------|:------------------------------------------------------------------|:-------------------|
| Update existing VM               | If a VM already running, it won't use the arch-specific resources | [ ] Name/Date      |
| Performance Testing              | Feature not related to scale                                      | [ ] Name/Date      |
| Security Testing                 | Feature not security related                                      | [ ] Name/Date      |
| Usability testing                | Should be done by UI team                                         | [ ] Name/Date      |
| Compatibility                    | Should be done by Virt/SSP team(create vms from multiple archs)   | [ ] Name/Date      |
| Templates creation & utilization | Should be done by SSP team                                        | [ ] Name/Date      |
| Import & datasource new API      | Should be done by Storage team                                    | [ ] Name/Date      |


#### **4. Test Strategy**

##### **A. Types of Testing**

**Note:** Mark "Y" if applicable, "N/A" if not applicable (with justification in Comments). Empty cells indicate incomplete review.

| Item (Testing Type)            | Applicable (Y/N or N/A) | Comments                       |
|:-------------------------------|:------------------------|:-------------------------------|
| Functional Testing             | Yes                     | Defined above                  |
| Automation Testing             | Yes                     | All tests should be automated. |
| Performance Testing            | N/A                     |                                |
| Security Testing               | N/A                     |                                |
| Usability Testing              | N/A                     |                                |
| Compatibility Testing          | N/A                     |                                |
| Regression Testing             | Yes                     | Defined above                  |
| Upgrade Testing                | Yes                     | Defined above                  |
| Backward Compatibility Testing | Yes                     | Defined above                  |

##### **B. Potential Areas to Consider**

**Note:** Mark "Y" if applicable, "N/A" if not applicable (with justification in Comment). Empty cells indicate incomplete review.

| Item                   | Description                                                                                                        | Applicable (Y/N or N/A) | Comment                        |
|:-----------------------|:-------------------------------------------------------------------------------------------------------------------|:------------------------|:-------------------------------|
| **Dependencies**       | Dependent on deliverables from other components/products? Identify what is tested by which team.                   | N                       |                                |
| **Monitoring**         | Does the feature require metrics and/or alerts?                                                                    | Y                       | Two new alerts & metrics added |
| **Cross Integrations** | Does the feature affect other features/require testing by other components? Identify what is tested by which team. | Y                       | SSP, storage, virt, upgrade    |
| **UI**                 | Does the feature require UI? If so, ensure the UI aligns with the requirements.                                    | Y                       |                                |

**Dependencies**


###### Dependencies/Cross Integration
Since it's a cross-team feature for CNV, the following should be tested:
**IUO** 
- Testing HCO monitors new nodes architectures correctly.
- Testing FG activation and propagation to CNV components.
- Verifies new metrics & alerts.
- Verifies upgrade.

**SSP**
- Templates creation & utilization
- Verify new SSP API.

**Storage**
- Verify that cdi-importer doing so successfully.
- Verify Legacy datasource's backwards compatibility.
- etc

**Virt**
- Verify VMs picked correctly the appropriate node by arch.
- Verify VMs migrated to nodes with the same arch.
- Verify upgrade.
- etc

#### **5. Test Environment**

**Note:** "N/A" means explicitly not applicable. Cannot leave empty cells.

| Environment Component                         | Configuration            | Comments                                                       |
|:----------------------------------------------|:-------------------------|:---------------------------------------------------------------|
| **Cluster Topology**                          | MultiArch cluster        | 3 control-plan and 3/4 worker nodes.                           |
| **OCP & OpenShift Virtualization Version(s)** | OCP 4.21, CNV-4.21       | OCP 4.21 and openshift-virtualization 4.21.                    |
| **CPU Virtualization**                        | Multi-arch cluster       | 3 amd64 control-plane, 2 amd64 workers, and 1/2 arm64 workers. |
| **Compute Resources**                         | N/A                      |                                                                |
| **Special Hardware**                          |                          |                                                                |
| **Storage**                                   | io2-csi storage class    |                                                                |
| **Network**                                   | OVN-Kubernetes (default) | No network requirements                                        |
| **Required Operators**                        |                          |                                                                |
| **Platform**                                  | AWS                      |                                                                |
| **Special Configurations**                    |                          |                                                                |

#### **5.5. Testing Tools & Frameworks**

Document any **new or additional** testing tools, frameworks, or infrastructure required specifically for this feature.

**Note:** Only list tools that are **new** or **different** from standard testing infrastructure. Leave empty if using standard tools.

| Category           | Tools/Frameworks              |
|:-------------------|:------------------------------|
| **Test Framework** | MultiArch cluster, HA cluster |
| **CI/CD**          | Jenkins pipeline              |
| **Other Tools**    |                               |

#### **6. Entry Criteria**

The following conditions must be met before testing can begin:

- [] Requirements and design documents are **approved and merged**
- [] Test environment can be **set up and configured**
- [] multi-cpu architecture enabled in openshift-virtualization repo
- [ ] [ֿAdd feature-specific entry criteria as needed]

#### **7. Risks and Limitations**

Document specific risks and limitations for this feature. If a risk category is not applicable, mark as "N/A" with justification in mitigation strategy.

**Note:** Empty "Specific Risk" cells mean this must be filled. "N/A" means explicitly not applicable with justification.

| Risk Category                      | Specific Risk for This Feature                                                  | Mitigation Strategy                                                                            | Status |
|:-----------------------------------|:--------------------------------------------------------------------------------|:-----------------------------------------------------------------------------------------------|:-------|
| Timeline/Schedule                  | Code-Freeze in 2 weeks                                                          | prioritize this week                                                                           | [ ]    |
| Test Coverage                      | Cannot perform automation testing until virt team enable multi-cpu architecture |                                                                                                | [ ]    |
| Test Environment                   | Cannot test upgrade well until additional ARM64 worker will be added by Devops  | Try to do so manually                                                                          | [ ]    |
| Untestable Aspects                 | N/A                                                                             |                                                                                                | [ ]    |
| Resource Constraints               | Feature includes almost all CNV teams                                           | [Your mitigation, e.g., "Focus automation on critical paths, coordinate with dev for testing"] | [ ]    |
| Dependencies                       | SSP, Storage and Virt team finishing their part                                 | Sync                                                                                           | [ ]    |
| Blocker Bug for legacy DataSources | CNV-75762                                                                       | Already fixed, Storage QE need to verify                                                       | [ ]    |

#### **8. Known Limitations**

Document any known limitations, constraints, or trade-offs in the feature implementation or testing approach.

---

### **III. Test Scenarios & Traceability**

This section links requirements to test coverage, enabling reviewers to verify all requirements are tested.

| Requirement ID | Requirement Summary   | Test Scenario(s)                                                             | Test Type(s)           | Priority |
|:---------------|:----------------------|:-----------------------------------------------------------------------------|:-----------------------|:---------|
| [Jira-xxx]     | As a user...          | HCO listing supported archs correctly                                        | Functional             | P0       |
| [Jira-xxx]     | As an admin...        | HCO annotating dataImportCronTemplates with supported archs                  | Functional             | P0       |
| [Jira-xxx]     | NFR-2 (Security)      | Correct resources created and ready to use for common golden images per arch | Functional             | P1       |
| [Jira-xxx]     | As a cluster admin... | Correct resources created and ready to use for custom golden images per arch | Functional             | P1       |
| [Jira-xxx]     | As a cluster admin... | nodePlacement should determine the workload nodes architecture               | Regression             | P1       |
| [Jira-xxx]     | As a cluster admin... | nodePlacement of not existing arch                                           | Regression             | P1       |
| [Jira-xxx]     | As a cluster admin... | Legacy Datasource points to the arch specific Datasource                     | Backward Compatibility | P1       |
| [Jira-xxx]     | As a cluster admin... | related resources names preserved as expected after upgrade                  | Upgrade                | P1       |

---

### **IV. Sign-off and Approval**

This Software Test Plan requires approval from the following stakeholders:

* **Reviewers:**
  - [Name / @github-username]
  - [Name / @github-username]
* **Approvers:**
  - [Name / @github-username]
  - [Name / @github-username]
