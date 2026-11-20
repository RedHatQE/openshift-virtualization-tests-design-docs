# Testing by Feature Maturity

OpenShift Virtualization ships features as Dev Preview (DP), Tech Preview (TP) or General
Availability (GA). Each phase makes a different promise to the customer, so each owes a different
minimum of testing. This page lists what must be covered at each phase — nothing about where tests
run or what they cost ([Testing Tiers](./testing-tiers.md)) or how to plan them
([STP Guide](./stp-guide.md)).

Two rules apply throughout:

- **Coverage is earned per phase, never carried over.** A DP test that passed on a DP build proves
  nothing about TP or GA: the code, the default state and the promise all differ. Each phase runs its
  own list on the build that ships in it.
- **Skipping is a preview allowance, never a GA one.** At DP or TP an item may be left uncovered if
  that is declared and agreed; at GA nothing is left uncovered — it is covered, the claim it protects
  is withdrawn from the docs and release note, or the feature does not ship as GA.

## Dev Preview

The promise: *this exists, you may evaluate it, and it will not hurt you.*

- The evaluation path in the enablement text works end to end. One walkthrough is enough.
- **Harmless when off.** On a fresh install and on an upgrade, with the feature at its default
  disabled state: no new objects, no error events, no log spam, no failed reconciles, and no change to
  existing VM lifecycle behaviour.
- One adjacent supported workflow — VM lifecycle, migration or snapshot — is unaffected with the
  feature on: the same named scenario, run with the feature off and on.
- One negative case per distinct error a user can see, asserting what the user sees (event,
  condition, message), not merely that an error occurred.
- The enablement instructions work as written, on the single reference configuration and platform
  named in the release note.
- The console was checked: either the exposed flow works, or the surfaces inspected are named and
  found to expose nothing.
- While the feature is off it adds no running component, no admission behaviour, and no permission or
  data surface of its own — or each one it adds is named and accepted by Product Security.

Not owed at DP: upgrade with the feature enabled, compatibility, turn-off, observability,
performance, scale, soak and data integrity, support handoff, and the full security matrix. **A claim
in the release note or demo makes any of them owed** — the claim creates the obligation, not the
phase.

## Tech Preview

The promise: *this is documented, you may use it, support can act on it.*

Everything above, re-run on the TP build, plus:

- Every sentence of the documented scope has a test, and every test traces to a requirement.
- Enablement is enforced (or the feature is always present, signed off as such), and enable and
  disable both work. Where the switch cannot be undone, the rebuild is covered and the release note
  says so.
- Every documented error mode, including retry and idempotency after a transient failure, with
  messages the user can act on at their level of access.
- Upgrade from the previous phase release, with the feature previously enabled and previously
  disabled.
- Turn-off after real use: existing objects and VMs stay usable, or fail with a documented, tested
  message.
- The named SIG regression suites are green with the feature on.
- Every claimed configuration and platform: storage class families, volume modes, binding types and
  CNIs, architectures, bare metal and cloud, cluster topology, and each claimed disconnected, proxied
  or FIPS variant. Unclaimed ones are stated as untested.
- User-visible events and conditions exist for success and failure, and support can diagnose a
  failure from must-gather and VM conditions without developer logs.
- Security: authorization for each documented role, isolation proven (namespace, resource, and
  failure isolation), and no secret or other tenant's data in events, logs or support data.
- Scale realism at the documented default magnitude, with the magnitude recorded.
- Every documented UI path, including the error states a user can reach.
- The documented procedure executed as written, from a clean environment, by someone who did not
  write it.
- Known limitations published in both the STP and the release note, including the TP position
  (Severity 3/4 cases, may change or be withdrawn) and the upgrade and migration position.
- Performance sanity: the primary operation measured and recorded, so GA has a baseline.
- Objects created by the previous TP build still work on this one, with no forced migration.

## General Availability

The promise: *it keeps working — across upgrades, at documented limits, under attack, and after
months of use.*

Everything above, re-run on the GA build, plus:

- Feature complete against the design. Any gap that would contradict GA language is fixed or
  documented as a product limitation.
- Upgrade from every supported path — previous minor, EUS where applicable, and from the preview
  phase — and with the feature's objects already created and in use before the upgrade. Plus the
  supported disable path and the state customers are left in; if GA means always on, the consequence
  is tested and must not block minor upgrades.
- Compatibility: objects from the previous phase remain readable and operable, and objects from the
  previous GA release survive later GA upgrades. Lost or unreadable objects are never accepted — they
  block.
- The full configuration and platform matrix at the claimed support scope, including the combinations
  the documentation promises, not just each axis alone.
- Performance with numeric thresholds agreed with Development and Product Management, measured on a
  defined cluster shape against a recorded baseline.
- Scale at the documented maximum, plus the platform constraint the feature depends on, and behaviour
  at that limit.
- The security matrix as outcomes: each documented role's access, no cross-tenant path, no secret in
  events or support data, authenticated auxiliary endpoints — and for every bypass mechanism the
  security review names, one run that attempts it and expects rejection.
- Reliability: soak or repeated cycles, disruption (node drain, reboot, control-plane), and data
  integrity verified **inside the guest**, not only in object state.
- The alerts the documentation promises fire in a real failure and point to a documented remediation.
- Documentation and release note match the tested scope exactly.
- The named SIG regression suites are green, with no new failures.
- Support handoff: known issues, error catalogue, must-gather expectations, escalation path.
- The full negative and error matrix, with the message a user of each role actually sees.
