# 001 Fixture regression harness

## Problem

The repository lacks a hosted, repeatable gate that can verify brownfield fixtures, numbered specs, and guardrail assets before changes reach licensed NSO validation.

## Brownfield input shape

- Brownfield fixture XML files for CR-1, CR-2, CR-3, ER-1, ER-2, and ER-3
- Baseline brownfield documentation and numbered specs
- GitHub-native review and workflow assets

## Expected discovered intent

- Fixture inventory is validated automatically.
- Numbered specs are checked for required sections.
- GitHub workflows, PR template, Codespaces config, and Copilot instructions are versioned and present.
- Hosted CI can fail fast before any runtime validation is requested.

## Allowed diff policy

- New metadata, validation scripts, workflow files, and documentation
- New Codespaces and Copilot guidance that do not alter discovery runtime logic

## Forbidden diff policy

- Silent changes to brownfield fixtures
- Relaxing the requirement to document diff policy in a slice spec
- Treating hosted validation as a replacement for licensed runtime validation

## Rollout boundary

This slice stops at static validation and review guardrails.

## Fallback path

If the hosted validation becomes noisy or blocks useful work, keep the manifest and specs but disable the failing workflow until the validation logic is narrowed.

## Acceptance evidence

- `.github/workflows/brownfield-assets.yml`
- `.github/workflows/nso-brownfield-validation.yml`
- `.github/pull_request_template.md`
- `.github/copilot-instructions.md`
- `.devcontainer/devcontainer.json`
- `scripts/validate_brownfield_assets.py`
