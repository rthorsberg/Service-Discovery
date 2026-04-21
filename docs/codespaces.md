# Codespaces strategy

## What Codespaces is for in this repository

Codespaces is the recommended environment for:

- reading and editing docs, specs, and workflow files
- reviewing discovery code
- maintaining the fixture inventory
- running static brownfield validation
- preparing pull requests with GitHub-native tooling

## What Codespaces is not assumed to provide

Default Codespaces should **not** be treated as the full NSO execution environment.

The following assets are still external constraints:

- NSO runtime
- Juniper Junos NED package
- resource-manager package
- any internal or licensed validation assets

## Hybrid model

Use a two-tier workflow:

1. **Codespaces / hosted CI**
   - edit code and docs
   - update specs
   - run `python3 scripts/validate_brownfield_assets.py`
2. **Self-hosted or private runtime**
   - source `ncsrc`
   - provide licensed packages in `packages/`
   - run tutorial targets for brownfield coverage and diff checks

## Recommended developer loop in Codespaces

```bash
python3 scripts/validate_brownfield_assets.py
```

If that passes and the change affects discovery behavior, hand off to the self-hosted NSO validation workflow before merging.
