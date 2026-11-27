# Known limitations and assumptions

These come from the tutorial's stated scope (README "Assumptions") and from
static review of the code. Items marked *static analysis* have not been
confirmed on a running NSO.

## Stated assumptions (by design)

| Assumption | Where it shows in the code |
| --- | --- |
| Discovery runs on a separate NSO, not production. | Discovery commits and coverage checks modify the NSO CDB and can push config (see below). |
| Each service instance touches **one device**. | Every RFS lives under `/nodes/router{X}` and templates target `{$DEVICE}` or `{../name}`. Cross-device intent exists only in the CFS layer. |
| **One device type and version.** | Discovery reads only `junos:configuration`; templates are Junos XML only; netsims are all `juniper-junos-nc-4.16`. |
| The NED fully supports the services. | Coverage diffs are only meaningful if every configured node round-trips through the NED model. |
| Focus is discovery, not onboarding. | No production `re-deploy reconcile` or rollout procedure is included. |

## Discovery safety

- **find-services is not strictly read-only.** Each `find-services` action
  commits its transaction with `reconcile keep-non-service-config` (or
  `discard-non-service-config`). It does not use `no-networking`. Any config
  the new services generate that is not already on the device is pushed. The
  dry-run (step 5, 25, 27, 33) is the only preview.
  `discard-non-service-config` additionally removes device config that the
  service does not produce.
- **Original saved after find-services (steps 14 onward).** This masks any
  device change made by find-services. *Static analysis:* with v2 applied,
  newly created `vrf-interface` instances without an explicit MTU write
  `mtu 1500`, so ER-2 and ER-3 `eth4` most likely receive `mtu 1500` during
  steps 23 and 24, and the diff reports nothing.
- **Step 24** runs find-services before `sync-from`.
- **Step 29** is applied through NSO (`load merge` + commit), not directly on
  the device.

## Discovery heuristics are marker-based

- Backbone interfaces are found only through the unit 0 description
  `Link to <device> [<if>]`. A typo (CR-2 `Lonk to`) hides the whole service.
- VRF interfaces require the exact interface description
  `Customer Access Interface` and the unit description
  `Customer VRF <vrf> <dev> [<if>]`.
- Role comes from the hostname prefix (`CR` → core, `ER` → edge). Other
  prefixes make base-config discovery fail. `peering` exists in the model but
  is never discovered.
- Router `id` is the last hextet of the IPv6 loopback, parsed as a decimal
  `uint32`. Hex hextets such as `::a` fail.
- VRFs are recognised only when the RD suffix equals the route-target suffix.
  The RD prefix must be `123.123.123.123` (hard-coded `router-id` in
  `vrf.py`) or the regenerated config differs.
- iBGP groups are matched by the `IPV[46]-` prefix. A matching group with
  neighbors but an unknown suffix (for example `IPV4-CUSTOMER` with peers)
  sets `type` to `''`, which fails the whole action.
- Only unit 0, single IPv4/IPv6 address per unit, and IPv4-only VRF
  interfaces are handled. IPv6 on VRF interfaces is modelled at CFS/RFS but
  never discovered.
- v3 `ebgp-neighbor` discovery matches only `IPV4-VPN-CUSTOMER` and does not
  read `peer-as`, `description` or `as-override`; the template hard-codes
  `peer-as 64513`. A neighbor with a different peer AS would be discovered
  and then *normalised* to 64513.

## Model and code gaps

- `internet-interface` has YANG and a `find-services` enum value but no
  callback, template, or discovery code.
- `respl3vpn` `find-services` checks `service_type == 'l3vpn'` while the
  enum value is `vpn`, so `service-type vpn` discovers nothing; only `all`
  works.
- `netinfra-rfs` `find-services` has no `ebgp-neighbor` enum value in v3, so
  eBGP discovery runs only with `all`.
- `netinfra/router` ignores `custom/ipv6-address` and derives the IPv6 loopback
  as `2001:db8::{id}`. The `ipv6-loopback` pool is defined but unused.
- `backbone-link` sets iBGP types only for core–core and core–edge pairs.
  Edge–edge or peering links leave `vars/*-ibgp-type` unset.
- v2 CFS MTU logic: when a VPN's most common MTU is 1600, endpoints that share
  it have `endpoint/mtu` cleared and read back as the default 1500. In
  `cb_create` that 1500 overrides the VPN-level 1600, so those endpoints
  regenerate with the RFS default of 1500 (*static analysis*).
- `find_l3vpn` creates a `vpn` for every RFS `vrf`, and never sets `name` or
  `ipv6-prefix`.
- Hard-coded values: ASN `64999`, VRF ID offset `10000`, router-id
  `123.123.123.123`, IS-IS area `49.0001`, IS-IS metric 1337, backbone MTU
  2000, user `admin` in `multi-service-action` and `self-test`.
- `base-config.xml` references `feature-flags/telemetry` and
  `vars/isis-key-junos`, which are not in the model, and uses an unbraced
  `when="/vars/ibgp-auth-key-junos"` (evaluated as a non-empty literal). All
  are currently harmless because the values are empty.
- `rfs-backbone-interface.xml` has dead `not($CR)` branches that reference a
  non-existent `vars/mtu`.
- `multi-service-action` assumes every child list or presence container of
  `/nodes/router{X}` is a service. A presence container that does not exist
  (for example a router without `base-config`) is still invoked.
- `leftover-config` is hard-wired to CR-2.

## Procedure and tooling caveats

- The root `ncs.conf` is not used; `ncs-setup` generates `ncs-run/ncs.conf`.
- `make rebuild` rebuilds only `respl3vpn`, `netinfra` and `netinfra-rfs`.
  Changes to `multi-service-action`, `maagic-copy` or `leftover-config` need
  `make build` (or a manual `make -C ... all`) followed by a packages reload.
- `make build` requires `pylint` because `packages/maagic-copy/src/Makefile`
  lints on `all`. `src/.pylintrc` uses options removed in modern pylint
  (`files-output`, `no-space-check`, `bad-functions`), which recent versions
  may reject. Set `SKIP_LINT=true` to bypass.
- `patches/v3` must be applied after `patches/v2`.
- Coverage diffs are line-based `diff -u` on XML, so ordering or formatting
  noise is possible. Only step 10 fails on a diff; later steps use `|| true`.
- Hosted CI validates file presence, XML well-formedness, and spec headings
  only. YANG compilation and discovery behaviour need the self-hosted
  workflow or a local NSO.
- Stray `.orig` / `.rej` files in `packages/` are patch leftovers; see
  [architecture](architecture.md#stray-patch-artefacts-in-packages).
