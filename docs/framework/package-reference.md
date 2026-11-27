# Package reference

Reference for the five packages in `packages/` plus the temporary
`patches/leftover-config` package. Paths in YANG are shown without module
prefixes. "v2" and "v3" refer to the patch sets in `patches/` (see
[architecture](architecture.md#patch-evolution-v1--v2--v3)).

| Package | Layer | Min NSO | Requires | Python components |
| --- | --- | --- | --- | --- |
| `netinfra` | CFS (infrastructure) | 6.2 | `resource-manager` | `router`, `backbone_link`, `ibgp_fullmesh` |
| `netinfra-rfs` | RFS (per device) | 6.2 | `multi-service-action` | `base-config`, `backbone-interface`, `ibgp-neighbor`, `nodes-router`, `rfs-vrf`, `rfs-vrf-interface` (+ `rfs-ebgp-neighbor` in v3) |
| `respl3vpn` | CFS (L3VPN) | 6.2 | — (writes into `netinfra-rfs` paths at runtime) | `l3vpn` (+ `vrf-ebgp-customer` in v3) |
| `multi-service-action` | Library (YANG grouping + action) | 6.3 | `maagic-copy` | `main` |
| `maagic-copy` | Library (Python only) | 4.5 | — | none |
| `leftover-config` (in `patches/`) | Temporary discovery service | 6.3 | — | `main` |

`multi-service-action` and `leftover-config` declare `ncs-min-version` 6.3,
so the effective minimum for the full tutorial is **NSO 6.3**.

---

## netinfra (CFS: network infrastructure)

**Represents:** routers as network nodes, the backbone links between them, and
the core iBGP full mesh. These are "internal" infrastructure services rather
than customer services.

### YANG (`src/yang/netinfra.yang`, `src/yang/netinfra-private.yang`)

- `/netinfra` (container)
  - action `find-services` (actionpoint `netinfra-find-services`), input
    `service-type` (`router` | `backbone-link` | `all`, default `all`),
    `dry-run`, `reconcile-type` (`keep-non-service-config` default |
    `discard-non-service-config`); output `success`, `message`, dry-run CLI.
  - `router{name}`: servicepoint `netinfra-router-servicepoint`. `role{name}`
    (`core` | `edge` | `peering`), hidden `netsim`, `custom/{id, ipv4-address,
    ipv6-address}` (optional pinned values), `vars` (oper, persistent:
    `id`, `ipv4-address`, `ipv6-address`).
  - `backbone-link{left-router left-interface right-router right-interface}`:
    nano service, servicepoint `netinfra-backbone-link-servicepoint`, plan
    `netinfra-backbone-link-plan`. `left-router`/`right-router` are leafrefs to
    `/netinfra/router/name`. `status`, `custom/{ipv4-prefix, ipv6-prefix}`,
    `vars` (allocated prefixes, per-side addresses and loopbacks,
    `left-ibgp-type`/`right-ibgp-type`).
  - Plan state `backbone-link-create-rfs` waits (pre-condition monitor) until
    both routers' `vars` have IPv4 and IPv6 addresses.
- `/infra-internal/ibgp-fullmesh` (presence container, in
  `netinfra-private`): servicepoint `netinfra-ibgp-fullmesh-servicepoint`,
  `router{name}` with mandatory `ipv4-address`, `ipv6-address`.

### Python

| File | Class | Behaviour |
| --- | --- | --- |
| `router.py` | `ServiceCallbacks` | Allocates router ID from pool `router-id` (requesting `custom/id` if set) and IPv4 /32 loopback from `ipv4-loopback` (static if `custom/ipv4-address` set). IPv6 loopback is derived as `2001:db8::{id}`; `custom/ipv6-address` and the `ipv6-loopback` pool are not used. Applies `router.xml`. For `role core`, creates `/infra-internal/ibgp-fullmesh/router{name}`. |
| `router.py` | `FindServices` | Registered on `netinfra-find-services`. `find_routers`: for each `/nodes/router` with no existing `/netinfra/router`, copies `base-config` roles, `id`, IPv4/IPv6 into `custom`. `find_backbone_links`: for each RFS `backbone-interface` where `router < remote/device` (alphabetical), creates a `backbone-link` with `custom` prefixes derived from the interface addresses. Commits with reconcile or dry-run. |
| `backbone_link.py` | `CreateRfs` (NanoService) | Enforces `left-router < right-router`. Allocates IPv4 (/31 default) and IPv6 (/126 default) prefixes (static if `custom` set). Sets iBGP types: core-core → `none` (handled by full mesh), core-edge → `rr-client` on core and `direct` on edge. Computes addresses (/31 and /127 use the network address for the left side). Applies `cfs-backbone-link`. |
| `ibgp_fullmesh.py` | `ServiceCallbacks` | Applies `cfs-ibgp-fullmesh` once per member router. |

### Templates

| Template | Writes |
| --- | --- |
| `router.xml` | `/nodes/router{name}/base-config` (roles, id, addresses) and `netsim`. |
| `cfs-backbone-link.xml` | `backbone-interface` on both routers, plus IPv4/IPv6 `ibgp-neighbor` entries when `left-ibgp-type != 'none'`. |
| `cfs-ibgp-fullmesh.xml` | For every ordered pair of member routers, IPv4/IPv6 `ibgp-neighbor` of type `full-mesh`. |

### Build

`src/Makefile` includes `pre-compile.mk`, which can generate a `*-stripped.yang`
module (servicepoints and `BEGIN_STRIP`/`END_STRIP` blocks removed) for reuse
in other models. `STRIP_TARGET` is never set, so in practice only `fxs` is
built; the `BEGIN_STRIP` markers in `netinfra.yang` and `respl3vpn.yang` are
currently inert.

---

## netinfra-rfs (RFS: per-device services)

**Represents:** everything configured on one router, split into service
types under `/nodes/router{name}`. This is where device discovery lives.

### YANG

`src/yang/netinfra-rfs.yang` defines `/nodes/router{name}` with hidden
`netsim`, `uses nirp:infra-grouping`, `uses multi-service-action:multi-service-actions`
(adds `re-deploy` and `check-sync` actions on the router entry), and action
`find-services` (actionpoint `netinfra-nodes-find-services`; `service-type`
enum: `base-config`, `backbone-interface`, `ibgp-neighbor`,
`internet-interface`, `vrf`, `vrf-interface`, `all`).

`src/yang/netinfra-rfs-private.yang`, grouping `infra-grouping`:

| Node | Kind | Key | Servicepoint | Inputs | `vars` (oper) |
| --- | --- | --- | --- | --- | --- |
| `base-config` | presence container | — | `netinfra-rfs-base-config-servicepoint` | `role{name}`, `id`, `ipv4-address`, `ipv6-address` (all mandatory except role) | `ipv4-address`, `ipv6-address`, `router-id`, `isis-net`, `isis-auth-mode`, `asn`, `ibgp-auth-key-junos`, `dns-domain` |
| `backbone-interface` | list | `name` | `netinfra-rfs-backbone-interface-servicepoint` | `disabled` (default false), IPv4/IPv6 address + prefix length, `remote/{device, interface}`; action `self-test` | `interface-name` |
| `ibgp-neighbor` | list | `address` | `netinfra-rfs-ibgp-neighbor-servicepoint` | `name`, `type` (`full-mesh` \| `rr-client` \| `direct`) | `group-name` |
| `internet-interface` | list | `name` | `netinfra-rfs-internet-interface-servicepoint` | `admin-state`, addresses, `remote` | `interface-name` |
| `vrf` | list | `name` | `netinfra-rfs-vrf-servicepoint` | `id` | `asn`, `router-id` |
| `vrf-interface` | list | `name` | `netinfra-rfs-vrf-interface-servicepoint` | `vrf` (leafref `../../vrf/name`), IPv4/IPv6 address + prefix length, `remote`, empty `feature-flags` and `deviations` containers; v2 adds `mtu` | `asn` |
| `ebgp-neighbor` (v3) | list | `address` | `netinfra-rfs-ebgp-neighbor-servicepoint` | `type` (`customer`), `vrf` (leafref) | `group-name`, `description` |

`internet-interface` has a model and a `find-services` enum value but **no
registered Python callback, no template, and no discovery code**. Creating an
instance would fail at commit.

### Python callbacks

| File | Behaviour |
| --- | --- |
| `base_config.py` | Derives IS-IS NET `49.0001.XXXX.XXXX.XXXX.00` from the zero-padded IPv4 loopback, hard-codes `asn = 64999`, sets `router-id` = IPv4 loopback, applies `base-config.xml` to `DEVICE = /nodes/router/name`. |
| `backbone_interface.py` | Sets `vars/interface-name`, applies `rfs-backbone-interface` with `CR = 'true'`. `SelfTest` action calls the Junos `get-isis-adjacency-information` RPC and checks the adjacency is `Up` and the neighbor system name equals `remote/device` (runs as hard-coded user `admin`). |
| `ibgp_neighbor.py` | Picks group name `IPV4-`/`IPV6-` + `IBGP` / `IBGP-FULLMESH` / `IBGP-CLIENTS` from address family and type; applies `rfs-ibgp-neighbor`. |
| `vrf.py` | Hard-codes `asn = 64999` and `router-id = 123.123.123.123` (used in the RD); applies `rfs-vrf`. |
| `vrf_interface.py` | Hard-codes `asn = 64999`; applies `rfs-vrf-interface`. |
| `ebgp_neighbor.py` (v3, copied from `patches/v3/rfs_ebgp_neighbor.py`) | For `type customer`, group `IPV4-VPN-CUSTOMER`, description `Customer router`; applies `rfs-ebgp-neighbor`. |
| `nodes_router.py` | `FindServices` action; see below. |

### Discovery heuristics (`nodes_router.py`)

All discovery reads `/devices/device{router-name}/config/junos:configuration`.

| Service | Detection rule | Fields read |
| --- | --- | --- |
| `base-config` | `system/host-name` starts with `CR` (role `core`) or `ER` (role `edge`); `lo0` unit `0` has exactly one IPv4 and one IPv6 address. | role, `id` = last hextet of the IPv6 loopback, IPv4/IPv6 loopback. |
| `backbone-interface` | Unit 0 description matches `Link to <device> [<interface>]`; exactly one IPv4 and one IPv6 address; interface listed under `protocols/isis/interface`. | `disabled` (from `disable`), addresses, prefix lengths, remote. |
| `ibgp-neighbor` | BGP group name matches `IPV[46]-...` ending in `IBGP` (`direct`), `IBGP-FULLMESH` (`full-mesh`) or `IBGP-CLIENTS` (`rr-client`). | neighbor address, description → `name`. |
| `vrf` | Every routing instance where the RD suffix equals the route-target community suffix. | instance name, `id` = RD suffix. |
| `vrf-interface` | Interface description is exactly `Customer Access Interface`; unit 0 description matches `Customer VRF <vrf> <remote-device> [<remote-interface>]`; exactly one IPv4 address. | VRF, IPv4 address, remote; v2 adds `mtu`. |
| `ebgp-neighbor` (v3) | Routing-instance BGP group named `IPV4-VPN-CUSTOMER`. | neighbor address, VRF. |

After discovery the action commits the transaction with
`reconcile keep-non-service-config` (default) or
`reconcile discard-non-service-config`; with `dry-run` it returns the CLI diff
instead.

### Templates

| Template | Emits (Junos) |
| --- | --- |
| `base-config.xml` | `system` (host-name, time-zone UTC, commit synchronize, console, login retry options, SSH ciphers/limits, removes `netconf rfc-compliant`, syslog source address), `lo0.0` (IPv4/IPv6/ISO), BGP groups (`IPV4/6-CUSTOMER`, `IPV4/6-PEER`, `IPV4/6-IBGP`, `IPV4/6-IBGP-CLIENTS`, `IPV4/6-IBGP-FULLMESH`), IS-IS (levels, SPF options, SR SRGB 16000/10000, node SID index = `id`), `mpls interface all`, `routing-options` (router-id, AS), policy statements `REJECT` and `IPV4-IBGP-EXPORT`, and empty prefix lists. Roughly 850 lines of firewall filters are commented out. |
| `rfs-backbone-interface.xml` | Interface `mtu 2000`, unit 0 description `Link to ...`, IPv4/IPv6 addresses, `disable` handling, IS-IS interface (point-to-point, metric 1337 at levels 1 and 2). The `not($CR)` branches (`mtu = vars/mtu + 14`, `family iso`) are dead because `CR` is always `true`. |
| `rfs-ibgp-neighbor.xml` | Neighbor (address, description) in group `vars/group-name`. |
| `rfs-vrf.xml` | Routing instance `vrf`, RD `router-id:id`, RT `target:asn:id`, `vrf-table-label`, empty BGP groups `IPV4-VPN-CUSTOMER` and `IPV6-VPN-CUSTOMER`. |
| `rfs-vrf-interface.xml` | Interface description `Customer Access Interface`, `flexible-vlan-tagging`, unit 0 description and IPv4 address, interface in the routing instance; v2 adds `mtu`. |
| `rfs-ebgp-neighbor.xml` (v3) | Neighbor in the VRF's `IPV4-VPN-CUSTOMER` group with hard-coded `peer-as 64513` and `as-override`. |

`netinfra-template.xml` at the package root is an unused `ncs-make-package`
skeleton.

---

## respl3vpn (CFS: L3VPN)

**Represents:** a customer L3VPN spanning several edge routers.

### YANG (`src/yang/respl3vpn.yang`)

- `/l3vpn` container with action `find-services` (actionpoint
  `l3vpn-find-services`; `service-type` enum `vpn` | `all`, v3 adds
  `vrf-ebgp-customer`).
- `/l3vpn/vpn{id}` (uint32): servicepoint `respvpn-l3vpn-servicepoint`;
  `name`; `endpoint{router interface}` with mandatory `ipv4-prefix`, optional
  `ipv6-prefix`, `remote/{device, interface}`; empty `feature-flags` and
  `deviations` containers; empty `vars`. v2 adds `vpn/mtu` and
  `endpoint/mtu` (default 1500).
- v3: `/l3vpn/vrf-ebgp-customer{address}` with servicepoint
  `respvpn-vrf-ebgp-customer-servicepoint`, `vpn-id` (leafref to `vpn/id`),
  `router`.

### Python (`python/respl3vpn/l3vpn.py`)

| Class | Behaviour |
| --- | --- |
| `ServiceCallbacks` | VRF name and ID = `10000 + vpn id`. For each endpoint, creates `/nodes/router{router}/vrf{vrf_id}` and `vrf-interface{interface}` directly from Python (no template). The edge router takes the first usable address of the prefix (network address for /31 and /127). v2 adds MTU resolution and writes `vrf-interface/mtu` only when it differs from 1500. |
| `FindServices` | `find_l3vpn`: for each RFS `vrf`, creates `vpn{id - 10000}` and an endpoint per matching `vrf-interface` (IPv4 prefix and remote only). v2 adds the "most common MTU" logic. `find_vrf_ebgp_customer` (present in v1 code but only wired up in v3) creates `vrf-ebgp-customer` from RFS `ebgp-neighbor` entries. |
| `vrf_ebgp_customer.py` (v3) | Creates `/nodes/router{router}/ebgp-neighbor{address}` with `type customer` and `vrf = 10000 + vpn-id`. |

---

## multi-service-action (library)

**Represents:** no network service. It provides one generic action
implementation so a container of services (here `/nodes/router{X}`) can
`re-deploy` or `check-sync` all of its child services in one call.

- YANG grouping `multi-service-actions` (`src/yang/multi-service-action.yang`,
  YANG 1.1): actions `re-deploy` (actionpoint `msa-re-deploy`; input
  `dry-run/outformat`, `ncs-commit-params` such as `no-networking`,
  `service-depth`, `reconcile`) and `check-sync` (actionpoint
  `msa-check-sync`; `outformat`, `service-depth`,
  `suppress-positive-result`, LSA choice). Output is a `service{name}` list
  keyed by service path.
- `python/multi_service_action/action.py` (`InvokeAction`): iterates the
  children of the container. Each presence container is treated as one service
  and each list as a set of services. An optional `services` leaf-list can be
  augmented into the input to restrict which list entries are processed.
  `netinfra-rfs` does not augment it, so every entry is processed. Each
  service's own action runs in its own MAAPI transaction via
  `asyncio.to_thread` (parallel). Results are copied into the output with
  `maagic_copy`. Transactions run as hard-coded user `admin`, context `system`.
- See `packages/multi-service-action/README` for the augment pattern.

---

## maagic-copy (library)

**Represents:** no network service. `maagic_copy(a, b, service_copy=True)`
recursively copies leaves, containers, lists, leaf-lists, presence and empty
leaves from one maagic node to another. It skips NSO service internals
(`private`, `modified`, `directly-modified`, `device-list`,
`used-by-customer-service`, `commit-queue`, `log`, `plan`), handles default
values explicitly via `FLAG_NO_DEFAULTS`, enables delayed `when` evaluation on
the destination, and includes a compatibility shim for the NSO 5.7+ maagic
`_ChildList` API. In this repository it copies action input and output in
`multi-service-action`.

The package has no YANG. Its `src/Makefile` runs `pylint` (strict, using
`src/.pylintrc`) and `mypy` (non-fatal) on `make all`, so the root
`make build` needs `pylint` on `PATH` unless `SKIP_LINT=true` is set.

---

## leftover-config (temporary, `patches/leftover-config`)

**Represents:** "configuration we know about but have not modelled yet". It
exists only to keep a discovery iteration moving.

- YANG `/leftover-config{name}` (leafref to `/devices/device/name`),
  servicepoint `leftover-config-servicepoint`.
- `main.py` applies `cr-2-leftover.xml` only when `name == 'CR-2'`; for other
  devices the service is empty.
- `cr-2-leftover.xml` contains CR-2's `class-of-service` block (DSCP
  classifier, EF/AF forwarding classes, `eth5` unit 0 scheduler map and
  classifier, schedulers at 30%/70%).
- Compiled by the root `make build` (`make_packages`), but only loaded into
  NSO when `make -C patches add-leftover-config-package` symlinks it into
  `ncs-run/packages` (tutorial step 15).
