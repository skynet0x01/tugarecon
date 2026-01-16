# TugaRecon – Architecture

## 1. Introduction

TugaRecon is a modular reconnaissance and subdomain intelligence framework designed for
penetration testers and OSINT practitioners.

Its architecture focuses on clarity, extensibility, and temporal awareness, enabling
both automated reconnaissance and long-term intelligence accumulation.

The system is intentionally designed as an orchestrated pipeline, not a monolithic tool.
Each component has a single responsibility and communicates through well-defined data artifacts.

---

## 2. High-Level Design Goals

- Modularity – Each functional domain is isolated into its own module.
- Extensibility – New engines, intelligence strategies, or reactions can be added with minimal changes.
- Temporal Intelligence – The system remembers previous scans and reasons about change over time.
- Automation – Actionable intelligence can automatically trigger reactions.
- Separation of Concerns – Orchestration, data collection, analysis, and reactions are decoupled.

---

## 3. Architectural Overview

+------------------------------------------------------------------+
|                         TugaRecon CLI                             |
|------------------------------------------------------------------|
| - Argument parsing                                                |
| - Execution flow control                                          |
| - ScanContext lifecycle                                           |
+----------------------------+-------------------------------------+
                             |
                             v
        +--------------------------------------------------+
        |                OSINT Enumeration                  |
        |--------------------------------------------------|
        | Sublist3r | CRT | Certspotter | AlienVault | ... |
        +--------------------------------------------------+
                             |
                             v
        +--------------------------------------------------+
        |        Intelligence & Temporal Analysis           |
        |--------------------------------------------------|
        | - Semantic classification                         |
        | - Snapshot memory                                 |
        | - Temporal state analysis                          |
        | - Scoring & decision engine                        |
        +--------------------------------------------------+
                             |
                             v
        +--------------------------+-----------------------+
        | Automated Reactions      | Optional Enhancers    |
        |--------------------------|-----------------------|
        | - Alerts                 | - IA wordlist growth  |
        | - Logging                | - Bruteforce hints    |
        | - Future integrations    | - Network mapping     |
        +--------------------------+-----------------------+

---

## 4. Core Components

### 4.1 CLI Orchestrator (tugarecon.py)

The CLI orchestrator is the entry point of the framework.

Responsibilities:
- Parse CLI arguments
- Initialize the ScanContext
- Control the execution pipeline
- Invoke high-level workflows

It intentionally avoids implementation details of OSINT, intelligence, or brute-force logic.

---

### 4.2 ScanContext

@dataclass
class ScanContext:
    target: str
    enum: list | None
    bruteforce: bool
    threads: int
    savemap: bool
    args: argparse.Namespace

The ScanContext acts as a shared execution state passed across modules.
It defines what is being scanned, how, and under which conditions.

---

### 4.3 OSINT Enumeration Modules

Location:
modules/OSINT/

Each OSINT engine:
- Operates independently
- Collects subdomains from a specific source
- Writes results to the scan directory

Examples:
- Sublist3r
- CRT / Certspotter
- ThreatCrowd
- AlienVault
- DNSDumpster

---

### 4.4 Intelligence & Temporal Analysis

Location:
modules/Intelligence/
utils/temporal_*

This layer transforms raw enumeration data into actionable intelligence.

Responsibilities:
- Load previous scan snapshots
- Build the current snapshot
- Detect temporal changes
- Classify subdomains into states:
  - NEW
  - ESCALATED
  - LOW
  - DORMANT
- Compute temporal scores
- Drive decision logic

This is the memory and reasoning core of TugaRecon.

---

### 4.5 Snapshot & Temporal Memory

Snapshots are stored per target and date:
results/<target>/<date>/scan_snapshot.json

Each snapshot represents the system’s understanding of a target at a specific moment.

This enables:
- Change detection
- Historical comparison
- Risk escalation or decay

---

### 4.6 Decision Engine

The decision engine determines what should happen for each subdomain.

Inputs:
- Impact score
- Temporal state
- Temporal score

Outputs:
- IGNORE
- Future extensible actions (alerts, scans, notifications)

Non-action is an explicit decision, not an absence of logic.

---

### 4.7 Reaction Engine

Location:
modules/Intelligence/reaction_engine.py

Responsibilities:
- Execute automated reactions
- Persist reaction artifacts
- Remain isolated from decision logic

Reactions are stored in:
results/<target>/<date>/reactions/

---

### 4.8 Brute-Force Engine (Optional)

Location:
modules/Brute_Force/

Features:
- High-performance multithreaded execution
- Optional IA-generated hints
- HTTP and HTTPS verification
- Designed to consume intelligence, not replace it

---

### 4.9 Network Mapping (Optional)

Location:
modules/Map/

Generates visual representations of discovered infrastructure:
- Subdomains
- IP relationships
- ASN groupings (when applicable)

Exports:
- PNG
- SVG
- PDF

---

## 5. Execution Flow

CLI
 └── ScanContext
      └── OSINT Enumeration
           └── Deduplication
                └── Intelligence & Snapshot
                     └── Temporal Analysis
                          └── Decision Engine
                               ├── Reactions
                               ├── Reporting
                               └── Optional Enhancements

---

## 6. Data Flow

- OSINT modules generate raw subdomain data
- Results are normalized and deduplicated
- Snapshots are built and compared temporally
- Scores and decisions are computed
- Reactions are executed when required
- Optional modules extend discovery or visualization

---

## 7. Extensibility Guidelines

- New OSINT engines → modules/OSINT/
- New intelligence logic → modules/Intelligence/
- New reactions → extend reaction_engine
- No changes required in core CLI logic

---

## 8. Architectural Philosophy

TugaRecon is designed as a thinking system, not a simple scanner.

Enumeration discovers.
Intelligence understands.
Memory contextualizes.
Decisions justify action or silence.
Reactions execute with intent.

Growth in complexity must result in more insight, not more noise.
