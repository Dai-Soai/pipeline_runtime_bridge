# Pipeline Runtime Bridge MVP

Pipeline Runtime Bridge is a lightweight runtime execution layer for reusable RADAR_SERVICE utilities.

It provides:

- Runtime Context
- Artifact Registry
- Artifact Routing
- Dispatcher
- Runtime Events
- Runtime JSON Report
- CLI-first workflow

## Features

- Runtime Context initialization
- Artifact registration
- Artifact routing
- Execution dispatcher
- Runtime event exchange
- Runtime report generation
- JSON-based runtime artifacts
- CLI interface

## Installation

```bash
python -m venv .venv

source .venv/bin/activate

pip install -e .

pip install -r requirements-dev.txt
```

## CLI Usage

Initialize runtime

```bash
runtime-bridge init --workspace data/runtime_demo --pipeline-id pipeline-demo
```

Register artifact

```bash
runtime-bridge register ...
```

Route artifact

```bash
runtime-bridge route ...
```

Dispatch request

```bash
runtime-bridge dispatch ...
```

Runtime events

```bash
runtime-bridge events ...
```

Runtime report

```bash
runtime-bridge report --workspace data/runtime_demo --write
```

## Runtime Workspace

```text
runtime_demo/

├── artifact_registry.json
├── runtime_context.json
├── runtime_events.jsonl
├── artifacts/
└── output/
    ├── runtime_report.json
    └── dashboard_<request_id>.json
```

## Runtime Flow

```text
RuntimeStarted

↓

ArtifactRegistered

↓

ArtifactRouted

↓

ExecutionRequested

↓

ExecutionCompleted
```

## Project Structure

```text
src/
    contract.py
    context.py
    dispatcher.py
    events.py
    report.py
    router.py
    cli.py

tests/
```

## Test

```bash
pytest
```

## Status

Version

v0.1.0

Status

MVP Stable
