# Brownfield specs

Use numbered specs for bounded brownfield slices.

## Layout

- `000-*` baseline and invariants
- `001-*`, `002-*`, ... incremental slices
- `templates/` reusable templates for new slices

## Rules

- Keep each slice small enough to validate against a known fixture set.
- Link each slice to the relevant fixture entries in `brownfield/fixtures/manifest.json`.
- Treat the diff policy as part of the contract.
- If runtime behavior changes, require the self-hosted NSO validation workflow before merge.
