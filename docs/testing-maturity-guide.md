# Testing by Feature Maturity

OpenShift Virtualization ships features as Dev Preview (DP), Tech Preview (TP) or General
Availability (GA). Each phase makes a different promise to the customer, so each owes a different
minimum of testing. This page lists what must be covered at each phase — nothing about where tests
run or what they cost ([Testing Tiers](./testing-tiers.md)) or how to plan them
([STP Guide](./stp-guide.md)).

Three rules apply throughout:

1. **Coverage is earned per phase, never carried over.** A DP test that passed on a DP build proves
   nothing about TP or GA: the code, the default state and the promise all differ. Each phase runs
   its applicable items on the build that ships in it, at that phase's bar.
2. **A higher phase raises the bar and drops what no longer applies.** A lower phase's ceiling is
   superseded, never inherited: DP's "one walkthrough is enough" and its single reference configuration
   become, at TP, the documented scope and every claimed configuration. Preview-only items drop out
   as well — the TP preview support disclaimer, and any disabled-by-default or turn-off check where
   the feature is always on at GA.
3. **Preview deferrals do not carry silently into GA.** At DP or TP, an obligation in this list may
   be deferred only if recorded in the STP under the matching constraint category (`Out of Scope` for
   a deliberate QE exclusion, `Test Limitations` for an environment or lab constraint) with Quality
   Owner or Product Manager sign-off. At GA, every documented claim and in-scope obligation must be
   explicitly resolved: covered by testing; or, if unsupported by the product, withdrawn or qualified
   in the product docs and release notes and recorded as a signed-off `Feature Limitation`; or, if
   supported by the product but deliberately excluded or blocked by an environment constraint,
   recorded as a signed-off `Out of Scope` or `Test Limitation` entry (never left undocumented).

A phase the feature never ships in — `DP: N/A` or `TP: N/A` in Feature Maturity — is not an escape
from these lists. The feature enters at the phase it names and owes every applicable item of that
phase and of the earlier phases it skipped (read at the entry phase's bar, with lower-phase
ceilings superseded and preview-only or phase-transition items — such as "upgrade from the previous
preview phase" when no preview shipped — omitted).

## Dev Preview

The promise: *this exists, you may evaluate it, and it will not hurt you.*

- The evaluation path in the enablement documentation works end to end, as written, on the single
  reference configuration and platform named in the feature documentation or release notes. One
  walkthrough is enough.
- **Harmless when off.** Where the feature ships disabled by default, on a fresh install and on an
  upgrade in that default disabled state: no unexpected objects, no error events, no abnormal error
  log volume, and no change to existing VM lifecycle behaviour.
- One adjacent supported workflow — VM lifecycle, migration or snapshot — is unaffected with the
  feature on: the same named scenario, run with the feature off and on.
- One negative case per distinct user-visible error in the evaluation flow, asserting what the user
  sees (error message, event or status condition), not merely that an error occurred. This is the DP
  subset of the negative path each P0 goal owes.
- The web console is checked: either the documented console flow succeeds end to end, or the
  inspected console views are named in the test record and confirmed to expose no broken or stray UI
  elements.
- Where the feature ships disabled by default, while off it adds no unexpected workloads,
  permissions or stored data of its own and does not reject or alter unrelated cluster requests — or
  each exception is named and signed off by the Feature Owner and Quality Owner (with Product
  Security input where applicable).

Not owed at DP: upgrade with the feature enabled, compatibility, turn-off, observability,
performance, scale, soak and data integrity, support handoff, and the full security matrix. **A claim
in the feature documentation, release notes or demo makes any of them owed** — the claim creates the
obligation, not the phase.

## Tech Preview

The promise: *this is documented, you may use it, support can act on it.*

Every applicable DP item is re-run on the TP build at the TP bar (with DP's single-walkthrough and
single-reference ceilings superseded). In addition, TP owes:

- Every documented behaviour in scope has a test (unless explicitly deferred per Rule 3), and every
  new test traces to a requirement in Section III of the STP.
- Enablement is enforced (or the feature is always present, signed off by the Quality Owner or
  Product Manager), and enable and disable both work. Where disabling is not supported, the rebuild
  path is covered instead and the feature documentation and release notes say so.
- Every documented error mode, including retry and idempotency after a transient failure, with
  messages the user can act on at their level of access.
- Upgrade from the previous release: where the feature already shipped in that release, verify the
  upgrade with the feature previously enabled and (where disabling is supported) previously disabled;
  where the feature did not yet exist in the source release, verify the upgrade succeeds and the
  feature works afterward.
- Where disabling is supported, turn-off after real use: existing objects and VMs stay usable, or
  fail with a documented, tested message.
- The named SIG regression suites run with the feature enabled and pass with no new failures
  compared to the same suites run without the feature.
- Every claimed configuration and platform: storage class families, volume modes, binding types and
  CNIs, architectures, bare metal and cloud, cluster topology, and each claimed disconnected,
  proxied or FIPS variant. Unclaimed configurations are recorded in the STP as `Feature Limitations`
  (when unsupported by the product), `Out of Scope` (when supported and deliberately excluded by QE),
  or `Test Limitations` (when supported but blocked by an environment or lab constraint), with sign-off.
- User-visible events and VM status conditions exist for success and failure, and support can
  diagnose a failure from must-gather and VM status conditions without developer logs.
- Security: authorization for each documented role, isolation proven (namespace, resource, and
  failure isolation), and no secret or other tenant's data in events, logs or must-gather data.
- Scale realism at the default magnitude stated in the STP's NFRs or the feature documentation, with
  that magnitude recorded; operations complete within the agreed bounds without degrading existing
  workloads.
- Every documented UI path, including the error states a user can reach.
- The documented procedure executed as written, from a clean environment, by someone who did not
  write it.
- Known limitations published in both the STP (`Feature Limitations`) and the release notes,
  including the preview support scope (limited support, may change or be withdrawn) and the upgrade
  and migration position.
- Performance sanity: the primary operation measured and recorded on a defined cluster shape, so GA
  has a baseline.
- Where a previous TP release shipped, objects created on that previous TP build still work on this
  one, with no forced migration.

## General Availability

The promise: *it keeps working — across upgrades, at documented limits, under attack, and after
months of use.*

Every applicable TP item is re-run on the GA build at the GA bar; preview-only items (the TP preview
support disclaimer, and disabled-by-default or turn-off checks where the feature is always on at GA)
do not carry into GA. In addition, GA owes:

- Feature complete against the design. Any product gap that would contradict GA support is fixed, or
  omitted/qualified in the product docs and release notes and recorded as a signed-off `Feature
  Limitation`.
- Upgrade from every supported OpenShift / OpenShift Virtualization path — previous minor release,
  Extended Update Support (EUS) where applicable, and from the preview phase (when a preview
  shipped): for source releases where the feature already shipped, verify the upgrade with the
  feature's objects already created and in use before the upgrade; for source releases where the
  feature did not yet exist, verify the upgrade succeeds and the feature works afterward. Plus the
  supported disable path and the state customers are left in; if GA means always on, the consequence
  is tested and must not block minor upgrades.
- Compatibility: objects from the previous preview phase (when one shipped) remain readable and
  operable, and (on releases after the first GA) objects from the previous GA release survive later
  GA upgrades. Lost or unreadable objects are never accepted — they block.
- The full configuration and platform matrix at the claimed support scope, including the
  combinations the documentation promises, not just each axis alone.
- Performance with numeric thresholds agreed with the Feature Owner, Quality Owner and Product
  Manager, measured on a defined cluster shape against a recorded baseline (from the TP run or from
  a baseline run on the same cluster shape without the feature).
- Scale at the target in the STP's NFRs or the feature documentation — the documented maximum — plus
  the platform constraint the feature depends on, and behaviour at that limit; operations complete
  within the agreed bounds without degrading existing workloads.
- The security matrix as outcomes: each documented role's access, no cross-tenant path, no secret in
  events or must-gather data, authenticated auxiliary endpoints — and for every bypass mechanism
  identified in the security review, one run that attempts it and expects rejection.
- Reliability: soak or repeated cycles, disruption (node drain, reboot, control-plane), and data
  integrity verified **inside the guest**, not only in object state.
- The alerts the documentation promises fire in a real failure and point to a documented
  remediation.
- Documentation and release notes match the supported scope: every unsupported product gap is
  recorded as a signed-off `Feature Limitation` and omitted or qualified in the docs and release
  notes.
- Support handoff: the documented known issues, error messages, must-gather diagnostics and
  remediation steps are verified against the failure behaviour observed in testing.
- Automation: GA functional and regression coverage is automated and running in the release
  checklist CI jobs (see [STP Guide](./stp-guide.md)).
- The full negative and error matrix, with the message a user of each role actually sees.

## Using this list when writing an STP

An STP always targets GA; optional phase tags mark goals and scenarios that must also pass at an
intermediate phase. This page says what each phase owes — the STP says how it is covered
([STP Guide](./stp-guide.md), [STP Template](../stps/stp-template/stp.md)):

- **Feature Maturity** names the phases and their target versions. `N/A` in a phase means the
  feature does not ship in it; the entry phase still owes every applicable item of the skipped
  phases (except phase-transition items).
- **Testing Goals (II.1)** carries each new functional and non-functional goal not already covered
  by an existing regression suite. Goals required for GA keep their untagged priority (`[P0]`,
  `[P1]`, `[P2]`); optional phase tags (`[P0][DP]`, `[P0][TP]`) mark goals that must also pass at an
  intermediate phase, using the phase names from Feature Maturity.
- **Test Strategy (II.2)** states which testing types apply, how goals are executed (automated vs
  manual), and which *existing* suites (such as named SIG regression suites or coverage owned by
  another team) satisfy regression obligations.
- **Test Scenarios & Traceability (Section III)** maps every non-regression Testing Goal (including
  manual walkthroughs) to concrete scenarios with Jira requirement IDs, Tier (`1`, `2`, or `3` — see
  [Testing Tiers](./testing-tiers.md)), and priority (with optional phase tag, e.g. `P0 [TP]`).
- **Feature Limitations (I.2), Out of Scope (II.1) and Test Limitations (II.1)** keep the three
  constraint categories separate: `Feature Limitations` for unsupported product gaps (which must
  also be omitted or qualified in docs and release notes), `Out of Scope` for deliberate QE
  exclusions, and `Test Limitations` for constraints imposed on QE — each with its required
  sign-off.
