# ADR-0001: Define v1 scope, primary user and non-goals

- **Status:** Accepted
- **Date:** 2026-10-17
- **Owners:** Yevhen Kovalov
- **Related:** `docs/truth-paper.md` sections 1–8, 12–19 and 20–22

## Context

ML systems often fail to reach production reliably because every model author manually rebuilds the same delivery work: packaging, experiment tracking, validation, comparison, serving, deployment, monitoring and rollback.

For a portfolio project it is easy to drift into one of two weaker outcomes:

1. a notebook and API for one specific model;
2. an unrealistically broad clone of Databricks, Kubeflow or SageMaker.

The project needs a narrow but end-to-end product boundary that demonstrates production ML engineering without pretending to be a managed enterprise platform.

## Decision

Build **ML Delivery Platform**, a local-first self-service platform that standardizes the path from versioned training inputs to a monitored production deployment.

### Primary user

The primary user is a Data Scientist / ML Engineer who understands the model and data, but should not need to hand-build Docker images, Kubernetes manifests, monitoring and rollout logic for every model.

The user provides:

- version-controlled training code;
- a versioned `model.yaml`;
- immutable dataset and manifest references;
- a Git commit SHA;
- domain-specific metric and schema choices.

The platform provides:

- layered contract and data validation;
- controlled and reproducible training;
- experiment tracking and artifact storage;
- candidate-versus-champion quality gates;
- model registration;
- reusable model serving;
- staging, smoke tests and canary rollout;
- promotion or rollback;
- operational and ML monitoring;
- status, evidence and audit trail.

The official deployable model artifact is produced by the controlled platform pipeline. A model file created in an arbitrary local environment is not accepted as the trusted production candidate.

### Secondary users

- **ML Platform Engineer:** operates and evolves the platform.
- **Approver / service owner:** reviews evidence and approves sensitive promotion steps.

### Product interface

The primary interfaces are:

- Git repository and pull request;
- `model.yaml`;
- Control API;
- later, the Rust `mlctl` CLI;
- logs, status and generated evidence.

A polished web dashboard is not required for v1.

### Demo workload

Use UCI Default of Credit Card Clients as the first educational workload. Logistic Regression is the initial baseline; a stronger candidate may use LightGBM or another approved adapter later.

The credit model is not the product and must not be presented as suitable for real lending decisions. A second model will later prove platform reuse.

### v1 success boundary

The first full version must demonstrate these scenarios:

1. a valid candidate reaches staging and can become champion;
2. a weak candidate fails a quality gate and is not deployed;
3. a degraded canary triggers detection and rollback;
4. a second model uses the same platform path without core-code duplication.

## Non-goals

The first version will not attempt to provide:

- a public multi-tenant SaaS;
- a production lending or credit-decision system;
- arbitrary notebook execution;
- trust of arbitrary external pickle files;
- automatic acceptance of untrusted training code;
- feature store;
- Kafka-based streaming architecture;
- Kubeflow;
- service mesh;
- multi-cloud portability;
- GPU scheduling platform;
- online feature serving;
- a large web UI;
- complete enterprise RBAC/governance;
- fully automatic production promotion without defined approval boundaries.

These technologies may be reconsidered only when a measured requirement cannot be met by the current design.

## Responsibility boundary

| Responsibility | Model author | Platform |
|---|---:|---:|
| Training logic and domain assumptions | Yes | Validates contract and execution |
| Dataset meaning and legal suitability | Yes | Tracks immutable snapshot and schema |
| Reproducible execution environment | Declares requirements | Builds and runs it |
| Experiment metadata | Supplies meaningful parameters | Captures and stores it |
| Quality thresholds | Proposes/domain-owns | Enforces consistently |
| Artifact creation | Supplies code | Produces trusted artifact |
| Serving template | No custom infrastructure by default | Owns reusable implementation |
| Rollout and rollback mechanics | No | Owns |
| Operational telemetry | No | Owns standard metrics/logs |
| Final approval where required | Participates | Enforces workflow and audit |

## Consequences

### Positive

- The repository tells one coherent MLOps/ML Platform story.
- Architectural decisions can be evaluated against a specific user journey.
- The simple demo model leaves time for engineering depth.
- Local-first development keeps cost and feedback time low.
- A second model provides a clear reuse test.

### Negative and trade-offs

- The system will initially support fewer frameworks and workflows than a generic enterprise platform.
- Trusted-code execution is acceptable for the educational v1, so this is not a hostile multi-tenant boundary.
- Some production controls will be demonstrated rather than operated at enterprise scale.
- A CLI/config-first interface is less visually impressive than a dashboard but better represents the chosen product.

## Reconsideration triggers

Revisit this ADR if:

- onboarding the second model requires copying or modifying core pipeline code;
- the trusted-code assumption becomes invalid;
- a real external user requires multi-tenancy or stronger isolation;
- the current interface prevents the defined user from completing the golden path;
- measured operational needs justify an explicitly excluded technology.

Any scope change must update this ADR and the relevant truth-paper sections in the same pull request.
