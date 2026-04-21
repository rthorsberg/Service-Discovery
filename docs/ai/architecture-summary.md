# Architecture summary for AI agents

- This repository is an NSO service-discovery tutorial for brownfield networks.
- The core loop is: capture device config, discover services, regenerate config, diff, iterate.
- `packages/netinfra-rfs` owns per-device discovery and service regeneration.
- `packages/netinfra` owns customer-facing netinfra discovery.
- `packages/respl3vpn` owns customer-facing L3VPN discovery.
- `tutorial.mk` is the procedural map of the tutorial and its acceptance checkpoints.
- `device-configs-brownfield/` contains the brownfield fixtures that anchor expected behavior.
