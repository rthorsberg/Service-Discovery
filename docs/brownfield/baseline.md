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

### CFS / cross-device discovery

- `netinfra/router`
- `netinfra/backbone-link`
- `l3vpn/vpn`

## Known brownfield constraints

- Full validation requires **NSO**, **Juniper Junos NED 4.16.x**, and **resource-manager 4.2.8**.
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
