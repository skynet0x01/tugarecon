# TugaRecon – Architecture & Internal Flow

This document describes the internal architecture of **TugaRecon**, explaining how modules interact, how intelligence evolves over time, and how automated reactions are triggered.

Nothing here is magic. It is deliberate engineering.

──────────────────────────────
1. OVERVIEW

──────────────────────────────

TugaRecon is not a linear scanner.  
It is a cyclic system with memory.

Conceptual flow:

INPUT
  ↓
ENUMERATION
  ↓
SEMANTIC INTELLIGENCE
  ↓
TEMPORAL INTELLIGENCE (MEMORY)
  ↓
DECISION ENGINE
  ↓
REACTION ENGINE
  ↓
PERSISTENCE
  ↓
NEXT EXECUTION (smarter)

Each run improves the next one.

──────────────────────────────
2. ENUMERATION LAYER

──────────────────────────────

Responsible for discovering subdomains.

Typical sources:
- OSINT (crt.sh, passive DNS, search engines)
- Adaptive brute-force
- Automatically enriched wordlists

Output:
- Raw list of valid subdomains
- No decisions, no judgment

Typical output:
results/<target>/<date>/subdomains_raw.txt

──────────────────────────────
3. SEMANTIC INTELLIGENCE

──────────────────────────────

This is where real intelligence begins.

Each subdomain is semantically analyzed:
- Relevant tokens (admin, api, auth, prod, internal, etc.)
- Functional context inferred from naming
- Estimated impact (0–100)

Internal example:
admin.api.prod.example.com
→ tokens: [admin, api, prod]
→ impact: 100
→ category: CRITICAL

Structured output:
semantic_results.json

Simplified structure:
{
  "subdomain": "admin.api.example.com",
  "tokens": ["admin", "api"],
  "impact": 100,
  "category": "CRITICAL"
}

──────────────────────────────
4. TEMPORAL INTELLIGENCE (MEMORY)

──────────────────────────────

This is the core of the system.

Each scan creates a snapshot:
results/<target>/<date>/snapshot.json

The current snapshot is compared with the previous one.

Possible temporal states:
- NEW       → never seen before
- STABLE    → unchanged
- ESCALATED → impact increased
- FLAPPING  → appears/disappears
- DORMANT   → missing for ≥ N days

Example:
auth.example.com
previous impact: 30
current impact: 75
→ state: ESCALATED

Nothing is deleted. Everything is remembered.

──────────────────────────────
5. TEMPORAL SCORING

──────────────────────────────

Temporal score combines:
- Semantic impact
- Temporal state
- Change frequency
- Historical persistence

Formula (simplified):
temporal_score = impact × state_weight × stability_factor

Result:
An objective temporal risk ranking.

──────────────────────────────
6. DECISION ENGINE

──────────────────────────────

Transforms states into actions.

Example logic:

if state == "ESCALATED":
    action = "HTTPX"

elif state == "NEW" and impact >= 20:
    action = "HTTP"

elif state == "FLAPPING":
    action = "WATCH"

else:
    action = "IGNORE"

The Decision Engine executes nothing.
It only decides.

Output:
{
  "subdomain": "...",
  "state": "...",
  "impact": 75,
  "score": 180,
  "action": "HTTPX"
}

──────────────────────────────
7. REACTION ENGINE

──────────────────────────────

Executes actions ONLY for relevant subdomains.

Input:
- subdomain
- action
- metadata

Example mapping:

REACTION_MAP = {
    "HTTPX": [run_httpx, run_tls, run_headers],
    "HTTP":  [run_httpx]
}

Each subdomain gets its own isolated directory.

Structure:
results/<target>/<date>/reactions/<subdomain>/
├── metadata.json
├── tls.json
├── httpx.txt
├── headers.json
└── error.log (if needed)

Failures are isolated.
One reaction never breaks the pipeline.

──────────────────────────────
8. PERSISTENCE & HISTORY

──────────────────────────────

Everything is stored by design.

- Snapshots are never overwritten
- Reactions are versioned by date
- Wordlists are incrementally enriched

The system improves over time, even without code changes.

──────────────────────────────
9. WHY THIS IS NOT “JUST ANOTHER RECON TOOL”

──────────────────────────────

Traditional recon:
- Stateless
- Disposable results
- No learning

TugaRecon:
- Stateful
- Historical memory
- Time-based decisions
- Automated reactions
- Real risk prioritization

It is the difference between:
“listing subdomains”
and
“understanding an attack surface over time”.

──────────────────────────────
10. CORE PRINCIPLE

──────────────────────────────

Exploring is easy.
Remembering is rare.
Reacting correctly is engineering.

TugaRecon does all three.
