# End-to-end walkthrough

How to build, run, and validate the tutorial, and what each make target does.
For the narrative per device, see the `README-sections/` parts linked from the
[README](../../README.md#tutorial).

## Prerequisites

| Item | Version / location | Enforced by |
| --- | --- | --- |
| Cisco NSO (local install) | 6.3 or later (`multi-service-action` and `leftover-config` declare `ncs-min-version` 6.3; the other packages declare 6.2) | `Makefile` fails if `NCS_DIR` is unset |
| Juniper Junos NETCONF NED | `packages/juniper-junos-nc-4.16` (README names 4.16.2) | `Makefile` fails if the directory is missing |
| Resource Manager | `packages/resource-manager` (README names 4.2.8) | `Makefile` fails if the directory is missing |
| Python 3.9+ in the NSO Python VM | `asyncio.to_thread` in `multi-service-action` | runtime |
| `pylint` (and optionally `mypy`) | for `packages/maagic-copy/src` | `make build` fails without `pylint` unless `SKIP_LINT=true` |
| GNU `sed` (`gsed` on macOS) | `packages/netinfra/src/pre-compile.mk` | `make` error |
| `patch`, `diff`, `git` | patch sets and coverage diffs | — |

The NED and Resource Manager are licensed and git-ignored (`.gitignore`).

## Build and run

```bash
source <nso-install>/ncsrc
make build start
```

`make build` runs these steps in order:

1. `make_packages`: `make -C packages/<pkg>/src all` for every package, plus
   `patches/leftover-config/src`. YANG is compiled with `ncsc --fail-on-warnings`.
2. `ncs-setup --dest ncs-run`, then `mkdir config`. **The `ncs.conf` used at
   runtime is the one `ncs-setup` generates in `ncs-run/`.** The root
   [`ncs.conf`](../../ncs.conf) is not referenced by any make target. It is a
   reference copy (CLI on SSH 2024, NETCONF 2022, WebUI 8080, `hide-group debug`,
   trace-level developer log, rollbacks in `./logs`) that you can copy over
   `ncs-run/ncs.conf` manually if you need those settings.
3. `link_packages`: symlink each `packages/*` into `ncs-run/packages/`.
4. `setup_netsim`: create six Junos netsims (CR-1..3, ER-1..3) and write
   `netsim_init.xml` (device definitions for NSO).

`make start` starts the netsims, then NSO from `ncs-run/`.

Other root targets: `stop`, `clean`, `reset` (stop, then recreate `ncs-run`
and netsims without rebuilding packages), `rebuild` (rebuilds `respl3vpn`,
`netinfra`, `netinfra-rfs` only, then `packages reload`), `cli`, `clean_cdb`.
Helpers used by `tutorial.mk`: `runcmdJ CMD=...` (pipes `unhide debug` +
command into `ncs_cli --stop-on-error -u admin`), `loadconf FILE=...`
(`load merge` + commit), `netsim-load-xml-conf NETSIM=... FILE=...`.

## Tutorial step map

All targets are in [`tutorial.mk`](../../tutorial.mk). "Coverage check"
means: sync-from, save original, find-services, delete-config, re-deploy
no-networking, save new, diff, sync-from.

| Steps | Target(s) | What happens | Expected outcome |
| --- | --- | --- | --- |
| 1 | `tutorial-sd-1-start` | Load NACM/Python-VM logging (`nso-config/init.xml`) and resource pools; load each fixture into its netsim. | Netsims hold brownfield config. |
| 2 | `tutorial-sd-2-onboard-devices` | Load `netsim_init.xml`, `devices sync-from`. | NSO CDB mirrors devices. |
| 3 | `tutorial-sd-3-create-nodes` | Load `nso-config/config-nodes.xml`. | Empty `/nodes/router{X}` entries with `netsim true`. |
| 4–11 | `tutorial-sd-4` … `tutorial-sd-11` | CR-1 coverage check, one step at a time (5 is the dry-run). | No diff. |
| 12 | `tutorial-sd-12-conf-diff-check-cr-2` | CR-2 coverage check. | `eth3` missing: unit description says `Lonk to`. |
| 13 | `tutorial-sd-13-correct-interface-description` | Fix the description through NSO. | Harmless correction applied to the device. |
| 14 | `tutorial-sd-14-conf-diff-check-cr-2` | Re-check. | `class-of-service` still uncovered. |
| 15 | `tutorial-sd-15-load-leftover-serivce` | Link `patches/leftover-config` and run `make rebuild`. | `leftover-config` package loaded. |
| 16 | `tutorial-sd-16-conf-diff-check-cr-2` | Re-check, also creating and re-deploying `leftover-config CR-2`. | No meaningful diff. |
| 17 | `tutorial-sd-17-conf-diff-check-cr-3` | CR-3 coverage check. | No diff. |
| 18 | `tutorial-sd-18-conf-diff-check-er-1` | ER-1 coverage check. | `eth3 mtu 1600` missing. |
| 19–21 | `tutorial-sd-19-jump-to-vpn-v2`, `-20-git-diff-services`, `-21-rebuild` | Apply v2, inspect the diff, rebuild. | MTU modelled at RFS and CFS. |
| 22 | `tutorial-sd-22-find-services-er-1` | Re-check ER-1. | Only `+ mtu 1500` on `eth4` (v2 default), accepted for cleanup. The `eth4` service already existed from step 18 and its input did not change, so find-services does not re-run it; the default only appears after `re-deploy no-networking`. |
| 23–24 | `tutorial-sd-23-…-er-2`, `tutorial-sd-24-…-er-3` | ER-2 and ER-3 coverage checks with v2. | Reported as "no diff". Static analysis indicates that here the `eth4` vrf-interface services are created for the first time, so the find-services commit pushes `mtu 1500` to the device. The original is saved after find-services, which hides that push from the diff. |
| 25–26 | `tutorial-sd-25/26-find-services-netinfra[-dry-run]` | CFS discovery of routers and backbone links. | `/netinfra/router`, `/netinfra/backbone-link`, and (indirectly) `/infra-internal/ibgp-fullmesh`. |
| 27–28 | `tutorial-sd-27/28-find-services-l3vpn[-dry-run]` | CFS discovery of L3VPNs. | `/l3vpn/vpn{123}` and `{456}`. |
| 29 | `tutorial-sd-29-oob-ebgp-customer` | Add an eBGP neighbor to ER-3 VRF `10456` (`nso-config/config-oob-vrf-ebgp-customer.xml`). | Simulated out-of-band change. |
| 30 | `tutorial-sd-30-find-services-er-3` | Re-check ER-3. | eBGP neighbor uncovered: no service type exists. |
| 31 | `tutorial-sd-31-apply-version-3-and-rebuild` | Apply v3 and rebuild. | New `ebgp-neighbor` / `vrf-ebgp-customer` services. |
| 32 | `tutorial-sd-32-find-services-er-3` | Re-check ER-3. | eBGP neighbor covered. |
| 33–34 | `tutorial-sd-33/34-find-services-l3vpn[-dry-run]` | CFS discovery again. | `/l3vpn/vrf-ebgp-customer{2.1.3.2}`. Step 34 also re-runs the ER-3 diff from step 32. |

Things to know when running the steps (see
[limitations](limitations.md#procedure-and-tooling-caveats) for details):

- Step 4 saves the original config **before** find-services. From step 14 on,
  the original is saved **after** find-services, so any change find-services
  pushes to the device is hidden from the diff.
- Step 24 runs find-services before `sync-from`.
- Step 29 commits through NSO rather than directly on the device, so it
  simulates an out-of-band change from NSO's own CLI.
- To start over, `make -C patches restore-patches` reverts v2/v3. The
  leftover-config symlink is removed by `make clean` or `make reset`.

## Codespaces and devcontainer

[`.devcontainer/devcontainer.json`](../../.devcontainer/devcontainer.json)
uses `mcr.microsoft.com/devcontainers/python:1-3.12-bookworm`, runs
`python3 scripts/validate_brownfield_assets.py` on create, sets
`BROWNFIELD_REPO_ROOT`, and installs Copilot, GitHub Actions, Python, and
Markdown extensions. It does **not** contain NSO, the NED, or Resource
Manager. Use it for docs, specs, code review, and static validation, and run
the tutorial on a machine with a licensed NSO install. See
[`docs/codespaces.md`](../codespaces.md).

## CI and guardrails

| Workflow | Trigger | Runner | What it does |
| --- | --- | --- | --- |
| [`brownfield-assets.yml`](../../.github/workflows/brownfield-assets.yml) | every PR; push to `main`, `master`, `copilot/**` | `ubuntu-latest`, Python 3.12 | `python3 scripts/validate_brownfield_assets.py` |
| [`nso-brownfield-validation.yml`](../../.github/workflows/nso-brownfield-validation.yml) | manual (`workflow_dispatch`) | self-hosted `[self-hosted, linux, nso]` | Checks `NCS_DIR`, NED and RM directories; `make build start`, steps 1–3, then one chosen target (`tutorial-sd-10`, `-16` or `-22`); always `make stop`. |

`scripts/validate_brownfield_assets.py` reads
[`brownfield/fixtures/manifest.json`](../../brownfield/fixtures/manifest.json)
and checks that:

- every `required_paths` entry exists, with no duplicates;
- every fixture has a unique name, a role of `core` or `edge`, at least one
  `serviceFamilies` entry, and an existing `.xml` path that parses;
- every spec file exists and contains its `requiredHeadings`.

It does **not** compile YANG, run NSO, or compare fixtures with discovered
services. The self-hosted workflow runs the tutorial targets but does not fail
on diffs, because `diff ... || true` in `tutorial.mk` swallows them (except in
step 10).

Supporting process assets: `specs/` (numbered slice specs and templates),
`.github/pull_request_template.md`, `.github/copilot-instructions.md`,
`docs/brownfield/`, `docs/ai/`.
