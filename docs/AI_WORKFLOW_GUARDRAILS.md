# AI Workflow Guardrails

Review this document before implementation, debugging, refactoring, migrations, or production fixes in this repository.

## Core Rule

Move fast, but move surgically. Prefer the smallest safe change that solves the measured problem. Avoid broad rewrites, speculative refactors, or unrelated cleanup.

## Repo-Specific Focus

- Protect realtime overlay performance.
- Keep websocket and event fan-out bounded.
- Minimize startup and module load costs.
- Prefer async processing patterns for slow or bursty work.
- Degrade gracefully during spikes or missing external data.
- Avoid unnecessary rendering, capture, or data loading.
- Keep UI iteration low-blast-radius.

## Required Before Changing Code

- Identify the specific problem and files likely involved.
- Name the expected impact and rollback path.
- Check whether the change affects realtime overlays, capture, websocket traffic, user data, data integrity, or production operations.
- Avoid touching unrelated files.

## Architecture Defaults

- Prefer queue-based async processing over synchronous fan-out.
- Prefer append-only events or buffers over hot shared state.
- Prefer bounded event fan-out and explicit backpressure.
- Prefer indexed or projected reads over repeated raw scans.
- Prefer idempotent and retry-safe jobs.

## Change Review Checklist

Before finalizing a change, answer what changed, why it is safe, what could break, how to roll back, and what validation proves the change.
