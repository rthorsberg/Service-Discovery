# Deviation catalog

## Current known deviation families

### Marker typo on CR-2

- Symptom: discovery misses a backbone interface because the description marker is misspelled.
- Current handling: correct the safe description typo during the tutorial.
- Risk: marker-based discovery is brittle.

### Temporary leftover coverage on CR-2

- Symptom: some configuration is not yet modeled by first-class services.
- Current handling: load `patches/leftover-config` to cover the temporary gap.
- Risk: leftover coverage should not become permanent architecture.

### MTU deviation on ER-1

- Symptom: generated configuration omits a meaningful non-default MTU.
- Current handling: evolve the service model and discovery code to support the variation.
- Risk: silently normalizing meaningful runtime differences would be unsafe.

### MTU default side effect on ER-1, ER-2 and ER-3 (after v2)

- Symptom: v2 `vrf-interface/mtu` defaults to 1500 and is always emitted, so `eth4` gains `mtu 1500`.
- Current handling: accepted as a cleanup-phase diff on ER-1 (step 22). On ER-2 and ER-3 (steps 23 and 24) the find-services commit likely pushes it to the device, and the diff hides it because the original is saved after find-services.
- Risk: discovery is not strictly read-safe; default-valued leaves can normalise the network.

### Out-of-band change on ER-3

- Symptom: a customer eBGP neighbor (`2.1.3.2` in VRF `10456`) appears that no service type models (step 29).
- Current handling: patch set v3 adds the RFS `ebgp-neighbor` and CFS `l3vpn/vrf-ebgp-customer` service types plus discovery (steps 31 to 34).
- Risk: v3 discovery does not read `peer-as`; the template hard-codes `64513`, so other peer AS values would be normalised.
