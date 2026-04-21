# Spec Kit brownfield adoption

## Why Spec Kit fits this repository

This repository already follows the essential brownfield loop:

1. capture brownfield device config
2. run discovery
3. regenerate device config from discovered service intent
4. diff original versus regenerated output
5. iterate until the service model is trustworthy

Spec Kit should be used here as a **control system around that loop**, not as a greenfield generator.

## Artifact map

- Baseline rules: `docs/brownfield/baseline.md`
- Fixture inventory: `brownfield/fixtures/manifest.json`
- Numbered specs: `specs/`
- Slice template: `specs/templates/brownfield-slice-spec.md`
- Static validation: `scripts/validate_brownfield_assets.py`
- GitHub guardrails: `.github/`
- Codespaces setup: `.devcontainer/`
- AI context assets: `docs/ai/`

## Repo-level brownfield workflow

### 1. Start with the baseline

Confirm that the requested change respects the invariants in `docs/brownfield/baseline.md`.

### 2. Write or update a numbered slice spec

Every change should have a bounded slice spec that states:

- brownfield input shape
- expected discovered intent
- allowed and forbidden diffs
- rollout boundary
- fallback path
- acceptance evidence

### 3. Update fixture coverage metadata

If the slice depends on a fixture, add or update its entry in `brownfield/fixtures/manifest.json`.

### 4. Implement the change

Keep the implementation bounded to one service family, one deviation family, or one acceptance harness improvement.

### 5. Validate in two tiers

- **Hosted/static tier**: validate docs, specs, and fixture inventory in GitHub-hosted CI.
- **Licensed/runtime tier**: run NSO tutorial coverage checks in a self-hosted or private environment.

## Suggested initial slice backlog

1. **Fixture regression harness**
   - codify fixture inventory
   - codify spec requirements
   - add hosted static validation
2. **Discovery markers hardening**
   - reduce fragile marker dependence where safe
3. **Leftover-config exit slices**
   - replace temporary leftovers with first-class service support
4. **Drift and out-of-band handling**
   - specify and validate expected operator workflows

## Optional Spec Kit bootstrap

When you are ready to install the Spec Kit CLI locally, initialize it in place rather than creating a parallel project:

```bash
specify init --here --ai copilot
```

After bootstrapping, keep using the numbered `specs/` slices in this repository as the source of truth for brownfield changes.
