# 000 Brownfield baseline

## Problem

The repository needs a durable brownfield operating model that makes discovery safety, coverage expectations, and external constraints explicit before larger modernization work begins.

## Brownfield input shape

- Existing device XML fixtures under `device-configs-brownfield/`
- Existing discovery code under `packages/`
- Existing tutorial acceptance flow under `tutorial.mk`

## Expected discovered intent

- The repo documents the current architecture and invariants.
- Brownfield slice work can be proposed and reviewed with consistent structure.
- Fixture inventory is explicit and version-controlled.

## Allowed diff policy

- Documentation-only additions
- Static validation assets that do not alter NSO runtime behavior

## Forbidden diff policy

- Any change that weakens the read-safe discovery model
- Any change that normalizes brownfield config without an explicit slice spec

## Rollout boundary

This baseline covers docs, templates, metadata, and hosted validation only.

## Fallback path

If any new artifact creates confusion, remove the artifact and keep the tutorial workflow as the operational source of truth until the slice is revised.

## Acceptance evidence

- `docs/brownfield/baseline.md`
- `docs/brownfield/spec-kit-adoption.md`
- `brownfield/fixtures/manifest.json`
- `scripts/validate_brownfield_assets.py`
