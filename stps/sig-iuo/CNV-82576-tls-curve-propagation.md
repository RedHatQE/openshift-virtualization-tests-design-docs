# Openshift-virtualization-tests Test plan

## **Centralized TLS Configuration & TLS Curve (Group) Propagation in OpenShift Virtualization - Quality Engineering Plan**

### **Metadata & Tracking**

- **Enhancement(s):** [openshift/api#2583 — TLS Groups (curves) in TLSSecurityProfile](https://github.com/openshift/api/pull/2583)
- **Feature Tracking:**
  - [CNV-82576 — Support TLS Groups (Curves) field in HCO for OCP 5.1 (phase 2)](https://redhat.atlassian.net/browse/CNV-82576)
  - [CNV-74453 — Centralized & enforced TLS configuration throughout OpenShift (phase 1, 4.22 must-have)](https://redhat.atlassian.net/browse/CNV-74453)
- **Epic Tracking:**
  - Primary: [CNV-82576](https://redhat.atlassian.net/browse/CNV-82576) (CNV v5.1.0, In Progress)
  - Predecessor: [CNV-74453](https://redhat.atlassian.net/browse/CNV-74453) (CNV v4.22.0, Closed)
  - QE tasks: [CNV-96294](https://redhat.atlassian.net/browse/CNV-96294) (phase 2, Testing — automation in
    [PR #6653](https://github.com/RedHatQE/openshift-virtualization-tests/pull/6653)) and
    [CNV-81812](https://redhat.atlassian.net/browse/CNV-81812) / [CNV-81756](https://redhat.atlassian.net/browse/CNV-81756)
    (phase 1, Closed — automation merged in
    [PR #4162](https://github.com/RedHatQE/openshift-virtualization-tests/pull/4162))
- **Feature Maturity:**
  - DP: N/A
  - TP: N/A
  - GA: 5.1
- **QE Owner(s):** Ohad Revah
- **Owning SIG:** sig-iuo
- **Participating SIGs:** sig-virt (virt-api and component endpoints), sig-network (apiserver-proxy), sig-observability (metrics exporter, observability controller)

**Document Conventions (if applicable):**
- **TLS profile** — the cluster-level `TLSSecurityProfile` set on the APIServer CR (one of the three knobs customers may adjust; APIServer is the default source for CNV components).
- **Groups / curves** — the TLS key-exchange group list (e.g. `X25519MLKEM768`, `X25519`, `secp256r1`) carried by the new `Groups` field in `TLSSecurityProfile`.
- **PQC** — Post-Quantum Cryptography; hybrid key-exchange groups such as `X25519MLKEM768` (ML-KEM).
- **CNV services** — the services deployed in the `openshift-cnv` namespace that expose a clusterIP endpoint.

### **Feature Overview**

OpenShift Virtualization must not hardcode its TLS configuration: every CNV component
(operator, operands and webhooks) inherits its TLS settings — protocols, ciphers and, from
5.1, key-exchange groups (curves) — from the cluster's centrally managed TLS security
profile, so a customer can opt into Post-Quantum-Cryptography-ready settings across the
whole platform by adjusting at most three documented knobs (APIServer, Kubelet, Ingress).

This plan covers both phases of that effort as one feature:

- **Phase 1 (4.22, CNV-74453, Closed):** CNV components fetch and apply the TLS policy from
  the central configuration source instead of managing it locally; hardcoded TLS settings
  were removed; service endpoints are compliant with the global TLS policy and
  PQC-ready (TLS 1.3, hybrid key exchange) where the runtime supports it.
- **Phase 2 (5.1, CNV-82576, In Progress):** HCO adopts the new `Groups` field of
  `TLSSecurityProfile` (v1beta1 and v1 of the HyperConverged API), propagates the curve
  list to every managed component CR (KubeVirt, CDI, SSP, NetworkAddonsConfig, AAQ,
  MigController), and applies it to its own pods, the console plugin (nginx), the
  apiserver-proxy, the observability controller, the network-resources-injector, autopilot
  and the metrics exporter.

Phase-1 automation is merged and running (`tests/install_upgrade_operators/crypto_policy/`);
phase-2 automation (curve propagation, negative curve rejection) is implemented in open
PR #6653 and tracked by CNV-96294. This STP covers the combined scope so the whole
feature — profile enforcement and curve propagation — is traceable in one place.

---

### **I. Motivation and Requirements Review (QE Review Guidelines)**

This section documents the mandatory QE review process. The goal is to understand the feature's value,
technology, and testability before formal test planning.

*This section records the quality interpretation of the feature. Its purpose is to expose misunderstandings
before testing starts, so reviewers should check it against their own understanding of the feature.*

#### **1. Requirement & User Story Review Checklist**

- [x] **Review Requirements**
  - *List the key D/S requirements reviewed:*
    - **[CNV-74453]** All local/hardcoded TLS configurations (protocols, ciphers, curves) are removed from CNV components; components fetch and apply the TLS policy from the central configuration source (APIServer by default); endpoints remain compliant with the global TLS policy and are PQC-ready (TLS 1.3+).
    - **[CNV-84874]** The `Groups` field is exposed in the HyperConverged CR (v1beta1 and v1), via the openshift/api bump.
    - **[CNV-84875] / [CNV-84876] / [CNV-84877] / [CNV-84878] / [CNV-84879] / [CNV-85522]** The curves configuration is populated in the KubeVirt, CDI, MigController, SSP, NetworkAddonsConfig and AAQ CRs.
    - **[CNV-84880]** TLS curves are set on the HCO operator and webhook pods (Prometheus and webhook endpoints).
    - **[CNV-84881]** TLS curves are set in the kubevirt console plugin pod (translated to the nginx format).
    - **[CNV-84882] / [CNV-84883]** The apiserver-proxy exposes a new command parameter for curves and its pods are configured from it.
    - **[CNV-96614] / [CNV-96615]** The observability controller takes a curves parameter and its pods use it.
    - **[CNV-97803]** Selected TLS groups are passed down to the network-resources-injector.
    - **[CNV-98974] / [CNV-98975]** TLS curve IDs are supported in autopilot and the metrics exporter (from the APIServer CR).
    - **[CNV-96294]** QE automation: the PQC audit must verify that endpoints can use *all* newly added curves (not just one), and the propagation test must verify that curves — not only the profile — are propagated and negotiable on the services.

- [x] **Understand Value and Customer Use Cases**
  - *Describe the feature's value to customers:*
    - Security policy compliance: customers (and compliance scanners) expect every platform
      component to honor the cluster TLS policy; a component with its own hardcoded TLS
      settings silently violates custom profiles.
    - PQC readiness: PQC-resilient algorithms are available only in TLS 1.3+; customers
      preparing for post-quantum migration need the whole platform — CNV included — to
      negotiate hybrid key-exchange groups once they opt in.
  - *List the customer use cases identified:*
    - A security team disables algorithms their policy considers unsafe and applies a custom
      TLS profile cluster-wide; CNV endpoints must follow it (phase 1) and must negotiate
      exactly the configured key-exchange groups (phase 2).
    - A customer opts into PQC hybrid groups (e.g. `X25519MLKEM768`) via the APIServer
      profile; every CNV service endpoint must negotiate them where the runtime supports it,
      and must not offer groups the profile omits.

- [x] **Testability**
  - *Note any requirements that are unclear or untestable:* None. All requirements map to
    observable endpoint behavior (negotiated TLS version, cipher, and key-exchange group),
    CR fields, or pod configuration that can be probed from a worker node with `openssl s_client`.

- [x] **Acceptance Criteria**
  - *List the acceptance criteria:*
    - Every CNV service endpoint complies with the cluster TLS profile (version + cipher suites).
    - Every curve configured in the profile is negotiated by the CNV services that support it.
    - Curves omitted from the profile are not negotiated (rejected at handshake).
    - No hardcoded TLS configuration remains in CNV components.
    - Services remain functional and reachable after a profile change is propagated.
    - QE automation for the above is merged and running in CI for GA.
  - *Note any gaps or missing criteria:* None.

- [x] **Non-Functional Requirements (NFRs)**
  - *List applicable NFRs and their targets:*
    - Security: TLS settings strictly inherited from the central profile (no Go/nginx defaults);
      FIPS-mode clusters keep their restrictions (PQC groups limited under FIPS).
    - Stability: profile propagation must not crash-loop operands (see CNV-97259, where an
      unsupported curve in the nginx config took the console plugin down).
    - Monitoring: metrics endpoints of new components (observability controller, metrics
      exporter) serve over TLS consistent with the profile.
  - *Note any NFRs not covered and why:* Performance — TLS handshake cost with hybrid groups
    is an OpenSSL/platform concern, not a CNV feature requirement; no CNV-specific target exists.

#### **2. Feature Limitations**

- **FIPS-enabled clusters restrict PQC hybrid groups (e.g. `X25519MLKEM768`) for now.**
  - *Sign-off:* [Name/Date — confirms awareness and acceptance of this limitation]
- **A component's runtime (Go version, OpenSSL provider, nginx build) may not support every configured group; unsupported groups are skipped or rejected by that component rather than fatal.**
  - *Sign-off:* [Name/Date — confirms awareness and acceptance of this limitation]

#### **3. Technology and Design Review**

- [x] **Developer Handoff/QE Kickoff**
  - *Key takeaways and concerns:*
    - Design doc: [HCO TLS curves technical implementation](https://docs.google.com/document/d/1NoHP2nZdg-xUkcB2y2BtI8469-iicdSG7xJwRad4kF0/edit?tab=t.0).
    - Curves flow: APIServer CR `TLSSecurityProfile.Groups` → HCO (new TLS reconcile controller,
      split out in CNV-74931) → component CRs and pod command lines / nginx config.
    - Phase-1 audit already found and fixed three blockers (CNV-82450 apiserver-proxy
      CurvePreferences, CNV-83219 migration-prometheus plaintext, CNV-85544 HPP CSI metrics),
      which validates the probing approach.
    - Concern: nginx-based components (console plugin) translate group names to nginx format;
      an unsupported name is fatal to nginx (CNV-97259), so the propagation must filter or
      sanitize curves the runtime cannot serve.
- [x] **Technology Challenges**
  - *List identified challenges:*
    - Probing must run from a worker node: `openssl s_client -groups ...` requires OpenSSL
      3.5+ on the node for ML-KEM hybrid groups.
    - Expected outcomes differ per service (FIPS mode, component runtime); the automation
      computes per-service expectations and xfail-gates components with open propagation Jiras.
  - *Impact on testing approach:* tests use per-service subtests with per-service expected
    negotiation results instead of one blanket assertion.
- [x] **API Extensions**
  - *List new or modified APIs:* `TLSSecurityProfile.Groups` (openshift/api), exposed in
    HyperConverged CR v1beta1 and v1; new `apiserver-proxy` and observability controller
    command-line parameters.
  - *Testing impact:* API-level validation of the `Groups` field, plus propagation
    verification through to endpoint behavior.
- [x] **Test Environment Needs**
  - *See environment requirements in Section II.3 and testing tools in Section II.3.1*
- [x] **Topology Considerations**
  - *Describe topology requirements:* Standard 3-master/3-worker cluster; worker nodes must
    run an OpenSSL that supports the probed groups. Non-FIPS for PQC scenarios.
  - *Impact on test design:* curve probes execute on worker nodes (`worker_exec` fixture);
    console-plugin reachability requires a temporary NetworkPolicy.

### **II. Software Test Plan (STP)**

This STP serves as the **overall roadmap for testing**, detailing the scope, approach, resources, and schedule.

#### **1. Scope of Testing**

**Testing Goals**

**Priority Levels:**
- **P0**: Blocks GA - must be complete before release
- **P1**: High priority - required for full feature coverage
- **P2**: Nice-to-have - can be deferred if timeline constraints exist

- **[P0]** Verify every CNV service endpoint negotiates the key-exchange groups configured in the cluster TLS profile that its runtime supports — including all newly added PQC hybrid groups — and that omitted groups are rejected (CNV-96294; PR #6653)
- **[P0]** Verify a custom TLS profile set on the APIServer CR (curves + version + ciphers) propagates to all CNV services and that the services remain reachable and communicating with the new profile (CNV-82576; extends the phase-1 propagation test to curves)
- **[P0]** Verify all CNV service endpoints are TLS-compliant with the cluster TLS profile and PQC-capable by default (phase 1, CNV-74453; regression — merged automation)
- **[P1]** Verify the `Groups` field is exposed in the HyperConverged CR and propagated into each managed component CR (KubeVirt, CDI, SSP, NetworkAddonsConfig, AAQ, MigController) and to HCO's own pods, the console plugin, the apiserver-proxy, the observability controller, the network-resources-injector, autopilot and the metrics exporter (CNV-84874…CNV-98975)
- **[P1]** Verify default (no custom profile) crypto policy compliance per resource type and connectivity (phase 1; regression — merged automation)
- **[P2]** Verify behavior on a cluster upgraded from 4.22 to 5.1: an existing custom profile without `Groups` keeps working, and adding `Groups` propagates after upgrade (CNV-82580 upgrade consideration)

**Negative paths:** the omitted-curve rejection goal above is the P0 negative path
(a curve deliberately left out of the profile must not be negotiable); phase 1 additionally
keeps the merged negative coverage for classical fallback and PQC-only handshake
rejection (`test_cnv_services_pqc_key_exchange` subtests).

**Out of Scope (Testing Scope Exclusions)**

The following items are explicitly Out of Scope for this test cycle and represent intentional exclusions.
No verification activities will be performed for these items, and any related issues found will not be classified as defects for this release.

- **OpenShift core (non-CNV) service endpoints** (router, apiserver itself, ingress)
  - *Rationale:* Owned and verified by the OCP platform teams under the same initiative; CNV QE verifies only components deployed by CNV.
  - *Sign-off (Quality Owner or Product Manager):* [Name/Date]
- **Kubelet and Ingress profile knobs as curve sources for CNV**
  - *Rationale:* CNV components take their TLS configuration from the APIServer profile; the Kubelet/Ingress knobs are not CNV sources.
  - *Sign-off (Quality Owner or Product Manager):* [Name/Date]
- **TLS handshake performance with hybrid groups**
  - *Rationale:* No CNV-specific performance requirement; platform-level concern.
  - *Sign-off (Quality Owner or Product Manager):* [Name/Date]

**Test Limitations**

None beyond the constraints recorded in one home each: the FIPS/PQC restriction is a
Feature Limitation (Section I.2) with its untestable-aspect risk in Section II.5, and the
worker-node OpenSSL 3.5+ requirement is a Test Environment entry (Section II.3) with its
fleet-uncertainty risk in Section II.5.

#### **2. Test Strategy**

**Functional**

- [x] **Functional Testing** — Validates that the feature works according to specified requirements and user stories
  - *Details:* Profile and curve propagation verified end-to-end: set the profile on the
    APIServer CR, wait for propagation, probe every CNV service endpoint from a worker node
    (`openssl s_client`) and assert the negotiated version, cipher and key-exchange group,
    including per-service expected outcomes and negative (omitted-curve) rejection.
- [x] **Automation Testing** — Confirms test automation plan is in place for CI and regression coverage (all tests are expected to be automated)
  - *Details:* All scenarios are automated in `tests/install_upgrade_operators/crypto_policy/`.
    Phase-1 automation is merged (PR #4162: `test_pqc_tls_audit.py`,
    `test_tls_profile_propagation.py`, `test_hco_crypto_policy_propagation.py`,
    `test_crypto_policy_default.py`). Phase-2 automation (curve propagation, negative
    curve rejection) is in PR #6653 and must be merged for GA (CNV-96294).
- [x] **Regression Testing** — Verifies that new changes do not break existing functionality
  - *Details:* The merged phase-1 suite covers: PQC key exchange on every CNV service
    (`test_cnv_services_pqc_key_exchange`), Modern profile propagation
    (`test_modern_profile_propagates_to_cnv_services`), HCO crypto policy setting
    (`test_set_hco_crypto_policy`), and default crypto policy per resource
    (`test_default_crypto_policy`, `test_default_crypto_policy_check_connectivity`).
    Phase-2 curve scenarios extend the same fixtures and probing utilities
    (`conftest.py`, `utils.py`, `constants.py`) and run in the same post-upgrade lane.
- [x] **Self-Validation Testing** — Should any of the new tests be included in the self-validation test package?
  - *Details:* No. The scenarios require a non-default TLS profile applied cluster-wide and
    worker-node probing, which conflicts with the self-validation package's fast,
    non-invasive health-check profile.

**Non-Functional**

- [ ] **Performance Testing** — Validates feature performance meets requirements (latency, throughput, resource usage)
  - *Details:* N/A — no CNV-specific performance requirement for TLS negotiation.
- [ ] **Scale Testing** — Validates feature behavior under increased load and at production-like scale
  - *Details:* N/A — the number of CNV service endpoints does not scale with workload; the suite already iterates over all of them.
- [x] **Security Testing** — Verifies security requirements, RBAC, authentication, authorization, and vulnerability scanning
  - *Details:* The feature *is* security testing: centralized TLS enforcement, PQC
    readiness, and rejection of non-configured groups. A tls-scanner-based compliance
    check of all `openshift-cnv` endpoints was set up in phase 1 (CNV-81756).
- [ ] **Usability Testing** — Validates user experience and accessibility requirements
  - *Details:* N/A — no UI or CLI surface changes; the `Groups` field is a CR field consumed by the operator.
- [x] **Monitoring** — Does the feature require metrics and/or alerts?
  - *Details:* The observability controller and metrics exporter receive the TLS curve IDs
    (CNV-96614/CNV-96615, CNV-98974/CNV-98975); their metrics endpoints are among the
    probed services, so curve propagation to them is verified by the same scenarios.

**Integration & Compatibility**

- [x] **Compatibility Testing** — Ensures feature works across supported platforms, versions, and configurations
  - *Details:* HyperConverged API v1beta1 and v1 both expose `Groups`; existing custom
    profiles without `Groups` must keep working (backward compatibility, covered by the
    upgrade goal). FIPS and s390x variants are marked in the suite (`sno`, `s390x` marks).
- [x] **Upgrade Testing** — Validates upgrade paths from previous versions, data migration, and configuration preservation
  - *Details:* Post-upgrade lane (`post_upgrade` mark): the profile/curve scenarios run
    against an upgraded cluster; the P2 upgrade goal covers 4.22 → 5.1 with a pre-existing
    custom profile.
- [x] **Dependencies** — Blocked by deliverables from other components/products. Identify what we need from other teams before we can test.
  - *Details:* openshift/api#2583 (merged) and the openshift/api bump in HCO (CNV-84874)
    are prerequisites for the `Groups` field; per-component propagation stories
    (CNV-84875…CNV-98975) gate the per-service expectations — components with open Jiras
    are xfail-gated in the automation until they land.
- [x] **Cross Integrations** — Does the feature affect other features or require testing by other teams? Identify the impact we cause.
  - *Details:* A cluster-wide TLS profile change affects every CNV lane's pre-suite sanity
    (an operand crash-looping on an unsupported curve aborts whole suites — CNV-97259).
    The console plugin (nginx) and UI lanes are most sensitive; coordination with sig-virt
    and the console/UI teams is needed for profile-change windows.

**Infrastructure**

- [ ] **Cloud Testing** — Does the feature require multi-cloud platform testing? Consider cloud-specific features.
  - *Details:* N/A — TLS configuration is platform-agnostic; bare-metal coverage suffices.

#### **3. Test Environment**

- **Cluster Topology:** 3-master/3-worker bare-metal

- **OCP & OpenShift Virtualization Version(s):** OCP 4.22 with OpenShift Virtualization 4.22 (phase 1, regression); OCP 5.1 with OpenShift Virtualization 5.1 (phase 2)

- **CPU Virtualization:** VT-x (Intel) or AMD-V enabled

- **Compute Resources:** Minimum per worker node: 8 vCPUs, 32GB RAM

- **Special Hardware:** N/A

- **Storage:** ocs-storagecluster-ceph-rbd-virtualization

- **Network:** OVN-Kubernetes, IPv4

- **Required Operators:** N/A

- **Platform:** Bare metal

- **Special Configurations:** Non-FIPS (PQC scenarios); AAQ enabled; OpenSSL 3.5+ on worker nodes for ML-KEM group probes

#### **3.1. Testing Tools & Frameworks**

- **Test Framework:** Standard (pytest, `tests/install_upgrade_operators/crypto_policy/`); probing utilities compose `openssl s_client` commands on worker nodes and parse `Peer Temp Key` / negotiated group output

- **CI/CD:** Post-upgrade lane (existing `post_upgrade` gating lane)

- **Other Tools:** tls-scanner compliance check against `openshift-cnv` endpoints (set up in phase 1, CNV-81756)

#### **4. Entry Criteria**

The following conditions must be met before testing can begin:

- [x] Requirements and design documents are **approved and merged** (openshift/api#2583 merged; HCO design doc reviewed)
- [x] Test environment can be **set up and configured** (see Section II.3 - Test Environment)
- [ ] Phase-2 component propagation stories landed in a testable build (CNV-84875, CNV-84876, CNV-84877, CNV-85522 still open/Testing at the time of writing; components with open Jiras stay xfail-gated)

#### **5. Risks**

**Timeline/Schedule**

- **Risk:** Per-component propagation stories (CDI, MigController, AAQ, KubeVirt) may land late in the 5.1 cycle, leaving curve-propagation coverage xfail-gated at Code Freeze.
  - **Mitigation:** Per-service subtests with xfail gates keyed to open Jiras; flip expectations as stories land; track remaining xfail count weekly.
  - *Estimated impact on schedule:* Low — automation is written; only expectations flip.
  - *Sign-off:* [Name/Date]

**Test Coverage**

- **Risk:** A component's runtime may silently strip unsupported groups rather than reject them, making the negative (omitted-curve) assertion per-service unpredictable.
  - **Mitigation:** Per-service expected-outcome computation in the automation (FIPS mode and component runtime taken into account), as already implemented in `curve_propagation_expectations`.
  - *Areas with reduced coverage:* Components whose runtime cannot express group rejection.
  - *Sign-off:* [Name/Date]

**Test Environment**

- **Risk:** Worker-node OpenSSL older than 3.5 cannot probe ML-KEM hybrid groups, silently reducing PQC coverage.
  - **Mitigation:** `verified_node_curve_propagation_support` fixture detects node capability up front and skips/xfails with an explicit reason.
  - *Missing resources or infrastructure:* None expected on the current bare-metal fleet.
  - *Sign-off:* [Name/Date]

**Untestable Aspects**

- **Risk:** FIPS-mode PQC behavior cannot be exercised while FIPS restricts hybrid groups.
  - **Mitigation:** Document as a feature limitation; cover the non-FIPS path and revisit when FIPS policy allows ML-KEM.
  - *Alternative validation approach:* Platform-level crypto policy testing by the OCP security team.
  - *Sign-off:* [Name/Date]

**Resource Constraints**

- **Risk:** Single QE owner (Ohad Revah) for both the phase-2 automation and the per-component expectation upkeep.
  - **Mitigation:** xfail gates keep the suite green without manual patching; component owners flip their own expectations when their story lands.
  - *Current capacity gaps:* None blocking.
  - *Sign-off:* [Name/Date]

**Dependencies**

- **Risk:** An unsupported curve reaching an nginx-based component (console plugin) can crash-loop the pod and abort entire gating suites (CNV-97259 precedent), amplifying a single propagation bug into fleet-wide CI noise.
  - **Mitigation:** Curve sanitization/filtering was fixed in the component (CNV-97259 Verified); the propagation test applies profiles with a curated curve set and probes console-plugin reachability as part of its subtests.
  - *Dependent teams or components:* HCO (curve translation), console plugin.
  - *Sign-off:* [Name/Date]

**Other**

- **Risk:** None beyond the categories above.
  - **Mitigation:** N/A.
  - *Sign-off:* [Name/Date]

---

### **III. Test Scenarios & Traceability**

- **[CNV-81812]** — As a cluster admin, I need every CNV service endpoint to negotiate PQC hybrid key-exchange groups (TLS 1.3) where the runtime supports it, with classical fallback and PQC-only handshake rejection verified
  - *Test Scenario:* [Tier 3] Verify PQC hybrid group key exchange, classical fallback, and PQC-only rejection per CNV service endpoint — extended to assert **all** newly added curves per endpoint (CNV-96294 extension) `[EXISTING_COVERAGE]`
  - *Priority:* P0
  - *covered_by:* `tests/install_upgrade_operators/crypto_policy/test_pqc_tls_audit.py::test_cnv_services_pqc_key_exchange` (merged, PR #4162); the all-curves extension lands with PR #6653 (CNV-96294)

- **[CNV-74453]** — As a security-conscious customer, I need CNV components to inherit their TLS configuration from the central APIServer profile so my custom TLS policy is honored platform-wide
  - *Test Scenario:* [Tier 3] Apply a Modern TLS profile on the APIServer CR and verify it propagates to all CNV services: TLS 1.3 enforced, TLS 1.2 blocked, services remain reachable and communicating `[EXISTING_COVERAGE]`
  - *Priority:* P0
  - *covered_by:* `tests/install_upgrade_operators/crypto_policy/test_tls_profile_propagation.py::test_modern_profile_propagates_to_cnv_services` (merged, PR #4162)

- **[CNV-74453]** — As a cluster admin, I need the HCO-set crypto policy to reach the components it manages
  - *Test Scenario:* [Tier 3] Set the HCO crypto policy and verify propagation to managed components `[EXISTING_COVERAGE]`
  - *Priority:* P1
  - *covered_by:* `tests/install_upgrade_operators/crypto_policy/test_hco_crypto_policy_propagation.py::test_set_hco_crypto_policy` (merged, PR #4162)

- **[CNV-74453]** — As a cluster admin, I need the default (unconfigured) crypto policy to leave CNV resources compliant and connected
  - *Test Scenario:* [Tier 1] Verify default crypto policy settings per resource type and endpoint connectivity `[EXISTING_COVERAGE]`
  - *Priority:* P1
  - *covered_by:* `tests/install_upgrade_operators/crypto_policy/test_crypto_policy_default.py::test_default_crypto_policy` and `::test_default_crypto_policy_check_connectivity` (merged, PR #4162)

- **[CNV-96294]** — As a customer opting into specific key-exchange groups, I need every curve configured in my custom TLS profile to be negotiated by the CNV services
  - *Test Scenario:* [Tier 3] Apply a Custom TLS profile with a curated curve set (including a non-default post-quantum hybrid) and verify each configured curve is negotiated per CNV service, with per-service expectations and xfail gates for open propagation Jiras `[NEW — implemented in PR #6653, not yet merged]`
  - *Priority:* P0

- **[CNV-96294]** — As a customer opting into specific key-exchange groups, I need curves I deliberately omitted from my profile to be rejected by the CNV services (negative path)
  - *Test Scenario:* [Tier 3] Verify a curve deliberately omitted from the Custom profile (plus curves stripped by FIPS mode or component runtime) is not negotiated by any CNV service `[NEW — implemented in PR #6653, not yet merged]`
  - *Priority:* P0

- **[CNV-84874]** — As a CNV admin, I need the `Groups` field exposed in the HyperConverged CR (v1beta1 and v1) so I can configure TLS curves
  - *Test Scenario:* [Tier 1] Verify the `Groups` field is settable in the HyperConverged CR in both API versions and is accepted by the validating webhook `[NEW]`
  - *Priority:* P1

- **[CNV-82576]** — As a CNV admin, I need HCO to ignore the APIServer's `TLSAdherence` field when its value is known (current behavior already matches `StrictAllComponents`) and to reject or flag an unknown value
  - *Test Scenario:* [Tier 1] Verify a known `TLSAdherence` value changes nothing in CNV component TLS behavior, and an unknown value is rejected by validation rather than silently accepted `[NEW]`
  - *Priority:* P2

- **[CNV-84875]** — As a CNV admin, I need the curves configuration populated in the KubeVirt CR
  - *Test Scenario:* [Tier 3] Verify a configured curve set appears in the KubeVirt CR and virt-api/virt-handler endpoints negotiate the configured curves `[NEW — per-service expectations in PR #6653; story in Testing]`
  - *Priority:* P1

- **[CNV-84876]** — As a CNV admin, I need the curves configuration populated in the CDI CR
  - *Test Scenario:* [Tier 3] Verify a configured curve set appears in the CDI CR and cdi-api endpoints negotiate the configured curves `[NEW — per-service expectations in PR #6653]`
  - *Priority:* P1

- **[CNV-84877]** — As a CNV admin, I need the curves configuration populated in the MigController CR
  - *Test Scenario:* [Tier 3] Verify a configured curve set appears in the MigController CR and its service endpoints negotiate the configured curves `[NEW — per-service expectations in PR #6653; story in Testing]`
  - *Priority:* P1

- **[CNV-84878]** — As a CNV admin, I need the curves configuration populated in the SSP CR
  - *Test Scenario:* [Tier 3] Verify a configured curve set appears in the SSP CR and ssp-operator-service/metrics endpoints negotiate the configured curves `[NEW — per-service expectations in PR #6653]`
  - *Priority:* P1

- **[CNV-84879]** — As a CNV admin, I need the curves configuration populated in the NetworkAddonsConfig CR
  - *Test Scenario:* [Tier 3] Verify a configured curve set appears in the NetworkAddonsConfig CR and kubemacpool-service endpoints negotiate the configured curves `[NEW — per-service expectations in PR #6653]`
  - *Priority:* P1

- **[CNV-85522]** — As a CNV admin, I need the curves configuration populated in the AAQ CR
  - *Test Scenario:* [Tier 3] Verify a configured curve set appears in the AAQ CR and AAQ service endpoints negotiate the configured curves `[NEW — per-service expectations in PR #6653; story in Testing]`
  - *Priority:* P1

- **[CNV-84880]** — As a CNV admin, I need the TLS curves set on the HCO operator and webhook pods (Prometheus and webhook endpoints)
  - *Test Scenario:* [Tier 3] Verify the HCO operator Prometheus, HCO webhook Prometheus, and HCO webhook endpoints negotiate the configured curves `[NEW — per-service expectations in PR #6653]`
  - *Priority:* P1

- **[CNV-84881]** — As a CNV admin, I need the TLS curves set in the kubevirt console plugin pod (nginx format translation)
  - *Test Scenario:* [Tier 3] Verify the console-plugin endpoint negotiates the configured curves (and remains up — no crash-loop on unsupported names, CNV-97259) `[NEW — per-service expectations in PR #6653]`
  - *Priority:* P1

- **[CNV-84882] / [CNV-84883]** — As a CNV admin, I need the apiserver-proxy to expose a curves command parameter and its pods configured from it
  - *Test Scenario:* [Tier 3] Verify kubevirt-apiserver-proxy endpoints negotiate the configured curves (regression of the phase-1 CurvePreferences fix, CNV-82450) `[NEW — per-service expectations in PR #6653]`
  - *Priority:* P1

- **[CNV-96614] / [CNV-96615]** — As a CNV admin, I need the observability controller to receive and apply the TLS curves
  - *Test Scenario:* [Tier 3] Verify observability controller service endpoints negotiate the configured curves `[NEW — per-service expectations in PR #6653]`
  - *Priority:* P1

- **[CNV-97803]** — As a CNV admin, I need the selected TLS groups passed down to the network-resources-injector
  - *Test Scenario:* [Tier 3] Verify network-resources-injector endpoints negotiate the configured curves `[NEW — per-service expectations in PR #6653]`
  - *Priority:* P1

- **[CNV-98974] / [CNV-98975]** — As a CNV admin, I need TLS curve IDs supported in autopilot and the metrics exporter
  - *Test Scenario:* [Tier 3] Verify autopilot and metrics-exporter endpoints negotiate the configured curves `[NEW — per-service expectations in PR #6653]`
  - *Priority:* P1

- **[CNV-82580]** — As a customer upgrading from 4.22, I need my existing custom TLS profile (without `Groups`) to keep working, and adding `Groups` after upgrade to propagate
  - *Test Scenario:* [Tier 3] On a cluster upgraded 4.22 → 5.1 with a pre-existing custom profile, verify service behavior is unchanged; then set `Groups` and verify propagation `[NEW]`
  - *Priority:* P2

---

### **IV. Sign-off and Approval**

This Software Test Plan requires sign-off from at least one person per function:

- Feature Owner: Nahshon Unna Tsameret / @nunnatsa
- Quality Owner: Ohad Revah / @OhadRevah
- Product Manager: Jean-Philippe Jung
