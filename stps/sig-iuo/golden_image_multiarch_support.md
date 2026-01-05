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

---

##### **Background**

**What are Golden Images?**

Golden images are pre-configured OS boot disk images used to create virtual machines (VMs) in OpenShift Virtualization. They serve as ready-to-use templates that are automatically available and kept up-to-date, eliminating the need for users to manually configure OS images for each VM.

The original golden images design (documented in the [kubevirt/community repository](https://github.com/kubevirt/community/blob/69d061862e0839608932d225a728a7a6e7a89f29/design-proposals/golden-image-delivery-and-update-pipeline.md)) was built for **homogeneous clusters** where all nodes share the same CPU architecture.

**The Problem: Heterogeneous Clusters**

Modern Kubernetes clusters increasingly run nodes with different CPU architectures (e.g., `amd64`, `arm64`, `s390x`). The current golden images implementation does not support this:

1. **Wrong architecture image selection**: When the CDI-importer pulls a multi-architecture image, it selects the image variant matching the *importer pod's node architecture*, not the target VM's architecture. For example, if the importer runs on an `arm64` node but the VM will run on `amd64`, the wrong image is imported and the VM fails to boot.

2. **No custom multi-arch support**: Cluster administrators cannot define custom golden images that work across multiple architectures.

---

##### **Motivation**

This feature enables OpenShift Virtualization to properly manage golden images in heterogeneous clusters by:

- Tracking which CPU architectures exist in the cluster
- Creating architecture-specific `DataSource` resources for each golden image
- Ensuring VMs boot from images matching their target architecture
- Maintaining backward compatibility with existing tooling and scripts

---

##### **User Stories**

| ID   | User Story                                                                                                                                                          |
|:-----|:--------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| US-1 | As a **VM creator**, I want to create virtual machines with specific CPU architectures to run architecture-specific applications.                                   |
| US-2 | As a **cluster administrator**, I want to define custom golden images with multi-architecture support, so VM creators can deploy VMs on any supported architecture. |
| US-3 | As a **VM creator**, I want my existing tools and scripts to continue working without modification after this feature is enabled.                                   |

---

#### **2. Technology and Design Review**

| Check                            | Done | Details/Notes                                                                     | Comments                 |
|:---------------------------------|:-----|:----------------------------------------------------------------------------------|:-------------------------|
| **Developer Handoff/QE Kickoff** | [V]  | Met with Nahshon from HCO team.                                                   |                          |
| **Technology Challenges**        | [V]  | CDI-importer picking the correct image arch, custom templates arch specific       |                          |
| **Test Environment Needs**       | [V]  | HA cluster for simple functionality testing, MultiArch cluster for full coverage. | Jenkins deploy job exist |
| **API Extensions**               | [V]  | HCO `status.nodeInfo`, `status.dataImportCronTemplates` with new fields           |                          |
| **Topology Considerations**      | [V]  | ARM64 and S390X VMs are supported since CNV-4.19                                  |                          |

#### **HCO Operator Changes**

📖 **Feature Documentation:** [Golden Images in Heterogeneous Clusters](https://docs.redhat.com/en/documentation/openshift_container_platform/4.20/html/virtualization/advanced-vm-creation#virt-golden-image-heterogeneous-clusters)
The HyperConverged Cluster Operator (HCO) is highly affected by this feature. The following changes are introduced:

##### **New Feature Gate**

| Item              | Details                                                                    |
|:------------------|:---------------------------------------------------------------------------|
| **Feature Gate**  | `enableMultiArchBootImageImport`                                           |
| **Default Value** | `false` (disabled)                                                         |
| **Purpose**       | Enables heterogeneous cluster support for golden images when set to `true` |

##### **New Status Fields**

HCO `status` is extended with a `nodeInfo` field that tracks cluster node architectures. for example:

```yaml
status:
  nodeInfo:
    controlPlaneArchitectures:
      - amd64
    workloadsArchitectures:
      - amd64
      - arm64
```

| Field                       | Description                                              |
|:----------------------------|:---------------------------------------------------------|
| `controlPlaneArchitectures` | List of CPU architectures present on control-plane nodes |
| `workloadsArchitectures`    | List of CPU architectures present on workload nodes      |

##### **DataImportCronTemplates Enhancements**

Each `DataImportCronTemplate` in the HCO status is enhanced with:

| Field/Annotation                     | Description                                                                                             |
|:-------------------------------------|:--------------------------------------------------------------------------------------------------------|
| `ssp.kubevirt.io/dict.architectures` | Annotation listing architectures supported by the image (filtered to cluster's available architectures) |
| `originalSupportedArchitectures`     | Status field showing original architectures from the image manifest                                     |
| `conditions`                         | Status conditions for issues (e.g., `UnsupportedArchitectures`)                                         |

Example status with an unsupported architecture:

```yaml
status:
  dataImportCronTemplates:
    - metadata:
        name: centos-stream10-image-cron
        annotations:
          ssp.kubevirt.io/dict.architectures: "amd64"
      status:
        originalSupportedArchitectures: "amd64,arm64,s390x"
        conditions:
          - type: Deployed
            status: "False"
            reason: UnsupportedArchitectures
            message: "DataImportCronTemplate has no supported architectures for the current cluster"
```

##### **Node Architecture Tracking**

| Behavior                    | Description                                                                                    |
|:----------------------------|:-----------------------------------------------------------------------------------------------|
| **Workload Node Detection** | By default, nodes labeled with `node-role.kubernetes.io/worker`                                |
| **Custom Node Placement**   | If `spec.workloads.nodePlacement` is set, HCO uses it to determine workload nodes              |
| **Control-Plane Detection** | Nodes labeled with `node-role.kubernetes.io/control-plane` or `node-role.kubernetes.io/master` |
| **Dynamic Updates**         | Architecture lists are updated automatically as nodes are added/removed                        |

##### **Architecture Filtering**

When the feature gate is enabled, HCO:

1. Reads the `ssp.kubevirt.io/dict.architectures` annotation from each predefined `DataImportCronTemplate`
2. Filters out architectures not present in the cluster's workload nodes
3. Propagates the filtered list to the SSP CR for `DataImportCron` and `DataSource` creation

##### **Monitoring & Alerts**

New alerts are introduced to help administrators manage golden images in heterogeneous clusters:

| Alert                                                                                                                              | Description                                                                                                                                                                                                                                       |
|:-----------------------------------------------------------------------------------------------------------------------------------|:--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| [`HCOMultiArchGoldenImagesDisabled`](https://kubevirt.io/monitoring/runbooks/HCOMultiArchGoldenImagesDisabled.html)                | Fires when the cluster has workload nodes with different CPU architectures but `enableMultiArchBootImageImport` is disabled. Without this feature gate, golden images may be imported with the wrong architecture, causing VMs to fail to start.  |
| [`HCOGoldenImageWithNoArchitectureAnnotation`](https://kubevirt.io/monitoring/runbooks/HCOGoldenImageWithNoArchitectureAnnotation) | Fires when a custom `DataImportCronTemplate` is missing the `ssp.kubevirt.io/dict.architectures` annotation (only when FG is enabled). Without this annotation, the golden image has no defined architecture and VMs may fail to start.           |
| [`HCOGoldenImageWithNoSupportedArchitecture`](https://kubevirt.io/monitoring/runbooks/HCOGoldenImageWithNoSupportedArchitecture)   | Fires when a `DataImportCronTemplate`'s `ssp.kubevirt.io/dict.architectures` annotation doesn't include any architecture supported by the cluster (only when FG is enabled). The golden image won't be created since no cluster nodes can use it. |

**Examples:**
- **`HCOMultiArchGoldenImagesDisabled`**: A cluster with both `amd64` and `arm64` worker nodes triggers this alert if the feature gate is disabled, warning that VMs may boot from incompatible images.
- **`HCOGoldenImageWithNoArchitectureAnnotation`**: A custom DICT `my-custom-image` defined in `spec.dataImportCronTemplates` without the `ssp.kubevirt.io/dict.architectures` annotation triggers this alert.
- **`HCOGoldenImageWithNoSupportedArchitecture`**: A DICT annotated with `ssp.kubevirt.io/dict.architectures: s390x` on a cluster with only `amd64` and `arm64` workers triggers this alert, and the DICT status shows `reason: UnsupportedArchitectures`.

---


### **II. Software Test Plan (STP)**

This STP serves as the **overall roadmap for testing**, detailing the scope, approach, resources, and schedule.

**Document Conventions:**

| Term                  | Definition                                                                                                                 |
|:----------------------|:---------------------------------------------------------------------------------------------------------------------------|
| **MultiArch cluster** | Heterogeneous cluster with 3 amd64 control-plane nodes, 2 amd64 worker nodes, and 1-2 arm64 worker nodes                   |
| **HA cluster**        | Homogeneous cluster with 3 control-plane nodes and 3 amd64 worker nodes                                                    |
| **FG**                | `enableMultiArchBootImageImport` feature gate in HCO CR (see Section I.5.1)                                                |
| **Related resources** | Golden image associated resources: `DataImportCron`, `DataSource`, `DataVolume`, `VolumeSnapshot`                          |
| **nodeInfo**          | HCO status field tracking cluster architectures (`status.nodeInfo`)                                                        |

#### **1. Scope of Testing**

This test plan covers scenarios related to HCO, and monitoring:

* HCO node architecture tracking nodeInfo.
* FG activation and propagation to CNV components.
* DataImportCronTemplates architecture annotations and filtering.
* New alerts & metrics validation.

**In Scope:**
##### Functional Testing
* HCO monitors the cluster's nodes architectures correctly.
* HCO dataImportCronTemplates annotations listing the correct architectures and propagates to SSP.
* Correct resources created and ready to use for common golden images per arch.
* Correct resources created and ready to use for custom golden images per arch.

##### Alerts Testing
* `HCOMultiArchGoldenImagesDisabled` fires on heterogeneous cluster with FG disabled.
* `HCOGoldenImageWithNoArchitectureAnnotation` fires when custom DICT missing architecture annotation.
* `HCOGoldenImageWithNoSupportedArchitecture` fires when DICT has no cluster-supported architecture.

##### Non-Functional Testing
**Regression Testing**
* spec.workloads.nodePlacement should determine the workload nodes architecture.
* spec.workloads.nodePlacement of not existing arch.

**Backward Compatibility Testing**
* Legacy Datasource points to the arch specific Datasource

**Upgrade testing**
* Verify that resources names preserved as expected after upgrade.


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
| **Dependencies**       | Dependent on deliverables from other components/products? Identify what is tested by which team.                   |                         |                                |
| **Monitoring**         | Does the feature require metrics and/or alerts?                                                                    | Y                       | Three new alerts added         |
| **Cross Integrations** | Does the feature affect other features/require testing by other components? Identify what is tested by which team. | Y                       | SSP, storage, virt, upgrade    |
| **UI**                 | Does the feature require UI? If so, ensure the UI aligns with the requirements.                                    | Y                       |                                |

##### **C. Dependencies/Cross Integration**

This is a cross-team feature for CNV. Testing responsibilities are divided as follows:

| Team        | Testing Responsibility                                                                                       |
|:------------|:-------------------------------------------------------------------------------------------------------------|
| **IUO**     | HCO node architecture tracking (`status.nodeInfo`), FG activation/propagation, new metrics & alerts, upgrade |
| **SSP**     | Templates creation & utilization, new SSP API (`enableMultipleArchitectures`, `cluster` fields)              |
| **Storage** | CDI-importer architecture selection, legacy `DataSource` backward compatibility, new CDI `platform` API      |
| **Virt**    | VM scheduling to correct architecture nodes, VM migration between same-arch nodes, upgrade                   |

#### **5. Test Environment**

**Note:** "N/A" means explicitly not applicable. Cannot leave empty cells.

| Environment Component                         | Configuration            | Comments                                                       |
|:----------------------------------------------|:-------------------------|:---------------------------------------------------------------|
| **Cluster Topology**                          | MultiArch cluster        | 3 control-plane and 3-4 worker nodes                           |
| **OCP & OpenShift Virtualization Version(s)** | OCP 4.21, CNV-4.21       | OCP 4.21 and OpenShift Virtualization 4.21                     |
| **CPU Virtualization**                        | Multi-arch cluster       | 3 amd64 control-plane, 2 amd64 workers, and 1-2 arm64 workers  |
| **Compute Resources**                         | N/A                      | No special compute requirements                                |
| **Special Hardware**                          | N/A                      | No special hardware required                                   |
| **Storage**                                   | io2-csi storage class    | AWS EBS io2 CSI driver                                         |
| **Network**                                   | OVN-Kubernetes (default) | No special network requirements                                |
| **Required Operators**                        | HCO, SSP, CDI            | Standard OpenShift Virtualization operators                    |
| **Platform**                                  | AWS                      | ARM64 workers available on AWS                                 |
| **Special Configurations**                    | N/A                      | No special configurations required                             |

#### **5.5. Testing Tools & Frameworks**

Document any **new or additional** testing tools, frameworks, or infrastructure required specifically for this feature.

**Note:** Only list tools that are **new** or **different** from standard testing infrastructure. Leave empty if using standard tools.

| Category           | Tools/Frameworks              |
|:-------------------|:------------------------------|
| **Test Framework** | MultiArch cluster, HA cluster |
| **CI/CD**          | Jenkins pipeline              |
| **Other Tools**    | N/A                           |

#### **6. Entry Criteria**

The following conditions must be met before testing can begin:

- [X] VEP [dic-on-heterogeneous-cluster](https://github.com/kubevirt/enhancements/tree/main/veps/sig-storage/dic-on-heterogeneous-cluster) is **approved and merged**
- [x] Test environment (MultiArch cluster) can be **set up and configured**
- [ ] Multi-CPU architecture support enabled in openshift-virtualization repo

#### **7. Risks and Limitations**

Document specific risks and limitations for this feature. If a risk category is not applicable, mark as "N/A" with justification in mitigation strategy.

**Note:** Empty "Specific Risk" cells mean this must be filled. "N/A" means explicitly not applicable with justification.

| Risk Category                      | Specific Risk for This Feature                                                  | Mitigation Strategy                                                 | Status |
|:-----------------------------------|:--------------------------------------------------------------------------------|:--------------------------------------------------------------------|:-------|
| Timeline/Schedule                  | Code-Freeze in 2 weeks                                                          | Prioritize HCO-specific testing this week                           | [ ]    |
| Test Coverage                      | Cannot perform automation testing until virt team enable multi-cpu architecture | Coordinate with virt team on timeline; prepare test code in advance | [ ]    |
| Test Environment                   | Cannot test upgrade well until additional ARM64 worker added by DevOps          | Manual testing as fallback                                          | [ ]    |
| Untestable Aspects                 | N/A                                                                             | N/A                                                                 | [x]    |
| Resource Constraints               | Feature spans multiple CNV teams (IUO, SSP, Storage, Virt)                      | Focus automation on HCO-specific paths; coordinate with other teams | [ ]    |
| Dependencies                       | SSP, Storage, and Virt teams must complete their implementations                | Regular sync meetings; track dependencies in Jira                   | [ ]    |
| Blocker Bug for legacy DataSources | CNV-75762                                                                       | Already fixed; Storage QE to verify                                 | [ ]    |

#### **8. Known Limitations**

| Limitation                            | Description                                                                            | Impact                                       |
|:--------------------------------------|:---------------------------------------------------------------------------------------|:---------------------------------------------|
| Existing VMs not updated              | VMs already running will not automatically use new architecture-specific resources     | Users must recreate VMs to use new resources |
| Platform variant format not supported | Format like `linux/arm64/v8` is not supported in this phase                            | Future enhancement if needed                 |
| Manual annotation in HCO image build  | `ssp.kubevirt.io/dict.architectures` annotation is set manually during HCO image build | May be automated in future phases            |
| Architecture validation not performed | Custom golden image architectures are not validated by the system                      | Users responsible for correct configuration  |

---

### **III. Test Scenarios & Traceability**

This section links requirements to test coverage, enabling reviewers to verify all requirements are tested.

| Requirement ID | User Story | Test Scenario                                                                                           | Test Type(s)           | Priority |
|:---------------|:-----------|:--------------------------------------------------------------------------------------------------------|:-----------------------|:---------|
|                | US-1       | Enable FG and verify feature activates                                                                  | Functional             | P0       |
|                | US-1       | Verify `status.nodeInfo.workloadsArchitectures` lists correct architectures                             | Functional             | P0       |
|                | US-1       | Verify `status.nodeInfo.controlPlaneArchitectures` lists correct architectures                          | Functional             | P0       |
|                | US-1, US-2 | Verify `ssp.kubevirt.io/dict.architectures` annotation is set on DataImportCronTemplates                | Functional             | P0       |
|                | US-1       | Verify unsupported architectures are filtered from annotations and presented in status                  | Functional             | P1       |
|                | US-2       | Verify custom golden images get correct architecture annotations                                        | Functional             | P1       |
|                | US-1       | Verify `spec.workloads.nodePlacement` overrides workload node detection                                 | Regression             | P1       |
|                | US-1       | Verify behavior with `nodePlacement` specifying non-existing architecture                               | Regression             | P1       |
|                | US-3       | Verify legacy `DataSource` points to architecture-specific `DataSource`                                 | Backward Compatibility | P1       |
|                | US-3       | Verify resource names preserved after upgrade                                                           | Upgrade                | P1       |
|                | US-1       | Verify `HCOMultiArchGoldenImagesDisabled` alert fires on heterogeneous cluster with FG disabled         | Functional             | P2       |
|                | US-2       | Verify `HCOGoldenImageWithNoArchitectureAnnotation` alert fires when custom DICT missing annotation     | Functional             | P2       |
|                | US-2       | Verify `HCOGoldenImageWithNoSupportedArchitecture` alert fires when DICT has no cluster-supported arch  | Functional             | P2       |

---

### **IV. Sign-off and Approval**

This Software Test Plan requires approval from the following stakeholders:

* **Reviewers:**
  - [Name / @github-username]
  - [Name / @github-username]
* **Approvers:**
  - [Name / @github-username]
  - [Name / @github-username]
