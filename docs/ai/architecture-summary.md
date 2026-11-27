# Architecture summary for AI agents

- This repository is an NSO service-discovery tutorial for brownfield networks.
- The core loop is: capture device config, discover services, regenerate config, diff, iterate.
- `packages/netinfra-rfs` owns per-device discovery (`/nodes/router{X}/find-services`, reading Junos device config) and service regeneration.
- `packages/netinfra` owns CFS infrastructure discovery (routers, backbone links, iBGP full mesh), reading discovered RFS intent rather than device config.
- `packages/respl3vpn` owns CFS L3VPN discovery, reading discovered RFS `vrf`/`vrf-interface` (and `ebgp-neighbor` in v3).
- `packages/multi-service-action` provides `/nodes/router{X}/re-deploy` and `check-sync` across all services on a device; `packages/maagic-copy` is its copy helper.
- `patches/v2` (MTU) and `patches/v3` (eBGP customer) evolve the packages in place and must be applied in order; `patches/leftover-config` is the temporary coverage service.
- find-services commits with reconcile flags and without no-networking, so it can push config; always dry-run first.
- `tutorial.mk` is the procedural map of the tutorial and its acceptance checkpoints.
- `device-configs-brownfield/` contains the brownfield fixtures that anchor expected behavior.
- Full reference: `docs/framework/`.
