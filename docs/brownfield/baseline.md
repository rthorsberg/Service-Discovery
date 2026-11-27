# Brownfield baseline

## Purpose

This repository is a brownfield NSO tutorial focused on discovering already-deployed network services, modeling them as NSO services, and proving coverage before any reconcile step takes ownership.

## Current architecture

- **Brownfield fixtures** live in `device-configs-brownfield`.
- **RFS discovery and regeneration** are implemented in `packages/netinfra-rfs`.
- **CFS discovery and regeneration** are implemented in `packages/netinfra` and `packages/respl3vpn`.
- **Tutorial orchestration** lives in `tutorial.mk`.
- **Tutorial explanation** lives in `README.md` and `README-sections/`.

## Brownfield invariants

These are non-negotiable unless a spec explicitly changes them:

1. **Discovery is read-safe.** Find-services actions must not mutate live network behavior.
2. **Coverage before ownership.** Reconcile should happen only after the coverage diff is empty or explicitly allowlisted.
3. **Brownfield config is the source of truth.** Regenerated config must not exceed the brownfield config unless the spec and reviewers approve it.
4. **Unsupported patterns must be visible.** If the model cannot represent a pattern, it must be surfaced as a gap, temporary leftover, or follow-up slice.
5. **Iterate in bounded slices.** Discovery improvements should target one service family or one deviation family at a time.

## Supported service families in the current tutorial

### RFS / per-device discovery

- `base-config`
- `backbone-interface`
- `ibgp-neighbor`
- `vrf`
- `vrf-interface`
- `ebgp-neighbor` (after patch set v3)
- `internet-interface` is modelled in YANG but has no callback or discovery code.

### CFS / cross-device discovery

- `netinfra/router`
- `netinfra/backbone-link`
- `infra-internal/ibgp-fullmesh` (created by `netinfra/router` for core routers, not discovered directly)
- `l3vpn/vpn`
- `l3vpn/vrf-ebgp-customer` (after patch set v3)

See [docs/framework/](../framework/README.md) for the full architecture and
package reference.

## Known brownfield constraints

- Full validation requires **NSO 6.6 or later** (6.7+ builds auto-apply `packages/*/nso-6.7.patch`), **Juniper Junos NED 4.16.x** (`juniper-junos-nc-4.16`), and **resource-manager 5.x**.
- `find-services` commits with reconcile flags and without `no-networking`; it is read-safe only when the generated config already matches the device. Always dry-run first.
- The repository currently depends on assets that cannot be assumed in GitHub-hosted CI or default Codespaces.
- The root `Makefile` enforces NSO prerequisites before running the tutorial targets.

## Known deviations and temporary handling

- **CR-2 interface description typo**: discovery depends on a textual marker and currently requires correcting a safe typo.
- **Temporary leftover coverage**: the `patches/leftover-config` package is used as a bounded escape hatch while discovery coverage matures.
- **ER-1 MTU variance**: the tutorial explicitly evolves the model to support a meaningful MTU deviation.
- **ER-3 out-of-band changes**: later tutorial steps model drift handling after onboarding.

## Target operating model after this uplift

- Baseline rules are documented and reviewed like code.
- Each brownfield change is captured as a numbered spec slice.
- Fixture inventory is tracked explicitly.
- Static checks run in hosted CI.
- Full NSO validation runs in a private or self-hosted environment with licensed assets.
