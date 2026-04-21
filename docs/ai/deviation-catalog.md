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

### Out-of-band change on ER-3

- Symptom: service-owned state diverges from live device state.
- Current handling: later tutorial steps show how to detect and reason about it.
- Risk: brownfield ownership without auditability creates operational surprises.
