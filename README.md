# ML Delivery Platform

A self-service platform that takes machine-learning models through a reproducible and controlled path from source code and versioned data to production deployment.

## Status

The project is in the early foundation stage.

Currently implemented:

- Python 3.12 project managed with `uv`;
- monorepo-style Python workspace;
- initial `platform-contracts` package;
- project architecture and implementation plan;
- Architecture Decision Record for the initial scope.

The training, deployment, monitoring, and rollback workflows described below are the target architecture and are not implemented yet.

## Problem

A Data Scientist can train a model in a notebook or local script, but a local model file is not automatically a safe production artifact.

Production delivery also requires:

- reproducible source code and dependencies;
- versioned and validated data;
- recorded experiments and metrics;
- comparison with the current production model;
- repeatable packaging and serving;
- deployment checks;
- monitoring;
- promotion or rollback decisions;
- an audit trail of what was deployed and why.

The platform standardizes this process.

## Primary user

The primary user is a Data Scientist or ML Engineer who provides:

- training code;
- a versioned `model.yaml` contract;
- immutable dataset references and a dataset manifest;
- a Git commit SHA.

The platform is responsible for creating and validating the official deployable model artifact.

## Target workflow

```text
validate
→ train
→ track
→ compare
→ register
→ stage
→ smoke test
→ canary
→ promote or rollback
→ monitor
```

A newly trained model is a **candidate**.

The currently approved production model is the **champion**.

A candidate becomes the new champion only after it passes the required quality and operational checks.

## Demo workload

The first demo workload is a credit-risk classification model trained on a public dataset.

The model is not the product. It is a workload used to test whether the delivery platform is reproducible, reusable, and safe.

## Non-goals

This project is not:

- a general-purpose replacement for Databricks or SageMaker;
- a notebook hosting platform;
- a system that trusts arbitrary local `.pkl` files;
- an attempt to add every possible MLOps technology;
- a production financial decision system.

## Repository structure

```text
.
├── docs/                         # Architecture, plans, ADRs and progress
├── packages/
│   └── platform_contracts/       # Shared platform contracts
├── TUTOR.md                      # Tutor and learning protocol
├── pyproject.toml                # Root Python workspace configuration
└── uv.lock                       # Locked dependency versions
```

The structure will grow only when new directories contain real code or documentation.

## Local development

Requirements:

- WSL 2 with Ubuntu;
- Python 3.12;
- `uv`;
- Git;
- Docker;
- GNU Make.

Install the current workspace:

```bash
uv sync --all-packages
```

Verify that the initial package can be imported:

```bash
uv run --package platform-contracts python -c \
  "import platform_contracts; print(platform_contracts.hello())"
```

Expected output:

```text
Hello from platform-contracts!
```

## Documentation

- [`docs/truth-paper.md`](docs/truth-paper.md) — product and architecture source of truth;
- [`docs/current-state.md`](docs/current-state.md) — latest verified implementation state;
- [`docs/learning-progress.md`](docs/learning-progress.md) — verified learning progress;
- [`docs/glossary.md`](docs/glossary.md) — project terminology;
- [`docs/adr/`](docs/adr/) — architecture decision records.

## License

This project is licensed under the [MIT License](LICENSE).