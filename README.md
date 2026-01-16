# TugaRecon

![version](https://img.shields.io/badge/version-2.52-blue)
![python](https://img.shields.io/badge/python-3.8%2B-yellow)
![license](https://img.shields.io/github/license/skynet0x01/tugarecon)
![issues](https://img.shields.io/github/issues/skynet0x01/tugarecon)
![stars](https://img.shields.io/github/stars/skynet0x01/tugarecon?style=social)

> **TugaRecon** is an advanced subdomain reconnaissance and intelligence framework built for security researchers, penetration testers, and OSINT professionals.  
> It combines OSINT enumeration, semantic analysis, **temporal intelligence**, and **automated reactions** to continuously improve asset discovery and prioritization.

---

## 🧭 Philosophy

**TugaRecon** is inspired by Portuguese explorers.

During the 15th and 16th centuries, navigators mapped the unknown, learned from each voyage, and refined future expeditions.  
TugaRecon follows the same principle:

> **Explore → Map → Learn → Remember → React**

— *skynet0x01*

---

## 📸 Preview

<p align="center">
  <img width="803" height="575" alt="tugarecon" src="https://github.com/user-attachments/assets/7e7461e7-ff6c-4132-9356-b8f8cab6bc15" />
</p>

---

## 🚀 Core Features

- 🔍 Passive & active subdomain enumeration (multiple OSINT sources)
- 📡 Built-in brute-force engine with adaptive wordlists
- 🌐 DNS resolution with fallback DNS servers
- 🧠 Semantic analysis & impact scoring
- 🎯 Asset prioritization by security relevance
- 🕒 **Temporal Intelligence & asset memory**
- ⚙️ **Automated reactions to temporal events**
- 🗺️ Optional ASN / infrastructure network mapping
- 📁 Clean outputs: `.txt`, `.json`, `.csv`, `.png`, `.svg`, `.pdf`
- 🔒 No API keys required for most modules

---

## 🧠 Adaptive Intelligence & Wordlist Enrichment

TugaRecon learns from every scan.

Instead of relying solely on static wordlists, it analyzes discovered subdomains and automatically extracts **meaningful tokens and naming patterns**, enriching its internal dictionaries.

### Workflow

```bash
# Initial scan (learning phase)
python3 tugarecon.py -d example.com

# Brute-force using enriched intelligence
python3 tugarecon.py -d example.com -b
```

### Key Properties

- Wordlists are **extended**, never overwritten
- Duplicate-safe and transparent
- Improves brute-force efficiency over time
- Domain-agnostic and reusable

---

## 🎯 Impact Scoring & Asset Prioritization

Each subdomain is evaluated using semantic indicators extracted from its name and context.

### Signals Considered

- Administrative exposure (`admin`, `panel`, `manage`)
- Authentication services (`auth`, `login`, `sso`)
- Critical environments (`prod`, `core`, `primary`)
- Sensitive roles (`api`, `gateway`, `billing`)

### Impact Levels

| Level | Meaning |
|------:|--------|
| **CRITICAL** | Admin or production exposure |
| **HIGH** | Auth or security-sensitive service |
| **MEDIUM** | Internal or semi-exposed |
| **LOW** | Non-actionable |

### Example

```text
[CRITICAL] impact=100   admin.prod.example.com
[HIGH    ] impact=75    auth.example.com
[LOW     ] impact=0     static.example.com
```

This allows analysts to **focus immediately on what matters**.

---

## 🕒 Temporal Intelligence & Asset Memory

TugaRecon is **stateful**.

Each run creates a snapshot and compares it with previous scans, classifying assets by **temporal state**.

### Temporal States

- **NEW** — First time seen
- **STABLE** — Unchanged across scans
- **ESCALATED** — Impact increased
- **FLAPPING** — Appears / disappears intermittently
- **DORMANT** — Previously seen, now missing (≥ 2 days)

### Example Output

```text
[🧠] Temporal Risk View – Top Targets
ESCALATED  admin.api.example.com
NEW        auth.prod.example.com
DORMANT    old-panel.dev.example.com
```

Snapshots are stored per target and date, creating **long-term reconnaissance memory**.

---

## ⚙️ Automated Reactions (Reaction Engine)

Temporal intelligence can trigger **automatic reactions**.

When a subdomain becomes relevant (e.g. `ESCALATED`), TugaRecon can automatically execute deeper analysis modules.

### Supported Reactions

- HTTP probing (httpx)
- TLS inspection
- Security headers analysis

### Example Logic

```text
ESCALATED → HTTPX + TLS + HEADERS
NEW + high impact → HEADERS
FLAPPING → WATCH
```

### Output Structure

```text
results/<target>/<date>/reactions/
└── sub.example.com/
    ├── metadata.json
    ├── tls.json
    ├── httpx.txt
    └── headers.json
```

Only **relevant subdomains** generate reactions.

---

## 📦 Installation

```bash
git clone https://github.com/skynet0x01/tugarecon.git
cd tugarecon
pip3 install -r requirements.txt
```

Recommended:

```bash
python3 -m venv venv
source venv/bin/activate
```

---

## ⚙️ Basic Usage

```bash
python3 tugarecon.py -d example.com
```

### Main Options

| Option | Description |
|------:|------------|
| `-d, --domain` | Target domain (required) |
| `-b, --bruteforce` | Enable brute-force |
| `-e, --enum` | Run specific OSINT modules |
| `-t, --threads` | Concurrent threads (default: 250) |
| `-m, --map` | Generate ASN / network map |

---

## 📁 Project Structure (Simplified)

```text
modules/
├── OSINT/               # Enumeration engines
├── Intelligence/        # Temporal memory & reactions
│   ├── snapshot.py
│   ├── decision_engine.py
│   ├── reaction_engine.py
│   └── reactions/
├── Brute_Force/         # High-performance brute-force
├── Map/                 # Network / ASN visualization
utils/
├── temporal_analysis.py
├── temporal_score.py
├── temporal_view.py
```

---

## ⚠️ Legal Notice

Use **only** on targets you own or have explicit authorization to test.  
The author assumes no responsibility for misuse.

---

## 👤 Author

**skynet0x01**  
Cybersecurity Researcher & Tool Developer  
🇵🇹 Portugal

---

## 📄 License

GNU GPLv3

Patent Restriction Notice:
No patents may be claimed or enforced on this software or any derivative.
Any patent claims result in automatic termination of license rights.

---

> **TugaRecon is not just a scanner.  
> It is a reconnaissance system that learns, remembers, and reacts.**

**🔗 Donate with your favorite cryptocurrency:**

- **Bitcoin (BTC):** `18Zg2qiypXRj7QnGWCpcXrKywmcfKkcUSs`
- **Ethereum (ETH):** `0x177c81746009cd7ab02adf85d28fbf27aca7a240`
- **Litecoin (LTC):** `Le1jfoWqVoEJtm4BYbQRJbggiauMQNqjWy`
- **Dogecoin (DOGE):** `DSnRY69q1k6xhFkKULSTcSCQdJpVuGeB7k`
- **Harmony (ONE):** `one1cv90mednznu629p3jr7gqgmqd6qcm368stalwp`
- **Solana (SOL):** `5yRzoxDp17B5XEHSzmgTHWY4NYTWnk7s4qT48t941wyP`

Every contribution, no matter how small, makes a big difference. Thank you!


   ![tugarecon](https://user-images.githubusercontent.com/39160972/75924110-45d8e300-5e5e-11ea-8832-55c08ecc2902.jpg)

---

### Final note
This README has been updated to match the current behavior of `tugarecon.py` (flags/usage) and to resolve the license inconsistency. If you prefer the MIT license instead of GPLv3, tell me and I can update the source file headers or switch the README to reflect MIT licensing.

