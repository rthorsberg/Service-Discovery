# Copilot instructions for Service-Discovery

This repository is a **brownfield NSO service-discovery tutorial**.

## Safety rules

- Preserve the capture -> discover -> regenerate -> diff -> iterate loop.
- Do not normalize existing device configuration unless the active spec explicitly allows it.
- Treat brownfield fixtures as the behavioral anchor for changes.
- Prefer bounded slice changes over broad rewrites.
- If a discovery behavior change cannot be validated in hosted CI, require self-hosted NSO validation before merge.

## Files to read first

- `docs/brownfield/baseline.md`
- `docs/brownfield/spec-kit-adoption.md`
- `docs/ai/architecture-summary.md`
- `docs/ai/deviation-catalog.md`
- `specs/`
- `brownfield/fixtures/manifest.json`
