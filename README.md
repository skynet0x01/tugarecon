# TugaRecon
![version](https://img.shields.io/badge/version-2.51-blue)
![python](https://img.shields.io/badge/python-3.8%2B-yellow)
![license](https://img.shields.io/github/license/skynet0x01/tugarecon)
![issues](https://img.shields.io/github/issues/skynet0x01/tugarecon)
![stars](https://img.shields.io/github/stars/skynet0x01/tugarecon?style=social)

> **TugaRecon** is an advanced subdomain enumeration, DNS reconnaissance and intelligence framework built for security researchers, penetration testers and OSINT professionals.  
> It combines passive OSINT, active discovery, semantic analysis and **temporal intelligence** to continuously improve asset discovery and prioritization.

---
> **TugaRecon** is a tribute to Portuguese explorers — curiosity, persistence and mapping the unknown.

>During the 15th and 16th centuries, Portuguese explorers were at the forefront of global discovery, creating maps where none existed.  
>TugaRecon follows the same philosophy — explore, map, learn, and evolve.

>skynet0x01

---

## 📸 TugaRecon

<p align="center">
  <img width="803" height="575" alt="tugarecon" src="https://github.com/user-attachments/assets/7e7461e7-ff6c-4132-9356-b8f8cab6bc15" />
</p>

---

## 🚀 Features

- 🔍 Passive & active subdomain enumeration using multiple OSINT sources  
- 📡 Built-in brute-force engine with adaptive wordlists  
- 🌐 DNS resolution with fallback mechanisms  
- 🧠 Multi-module integration (Certspotter, DNSDumpster, HackerTarget, etc.)  
- 🗺️ Optional network & infrastructure map generation  
- 📁 Clean outputs: `.txt`, `.json`, `.csv`, `.svg`, `.pdf`  
- 🔒 No API keys required for most modules  
- 🧠 **Adaptive / Intelligence-Assisted Wordlist Enrichment**  
- 🎯 **Impact Scoring & Asset Prioritization**  
- 🕒 **Temporal Intelligence & Asset Memory (NEW)**  

---

## 🧠 Adaptive / Intelligence-Assisted Wordlist Enrichment

TugaRecon includes an **adaptive intelligence mechanism** designed to improve brute-force efficiency by learning from previously discovered subdomains.

Instead of relying only on static dictionaries, TugaRecon analyzes enumeration results and **automatically enriches its internal wordlists** with relevant tokens and naming patterns.

### How it works

1. Run a standard enumeration:
   ```bash
   python3 tugarecon.py -d example.com
   ```
2. All discovered subdomains are analyzed.
3. Meaningful tokens and structural patterns are extracted.
4. Wordlists are enriched automatically:
   - Existing entries are preserved
   - Duplicates are avoided
5. Subsequent brute-force runs become significantly more effective.

### Recommended workflow

```bash
# Step 1 — Enumeration & learning
python3 tugarecon.py -d example.com

# Step 2 — Brute-force with enriched intelligence
python3 tugarecon.py -d example.com -b
```

### Key characteristics

- Wordlists are only extended, never overwritten  
- Fully automatic and transparent  
- Improves results progressively over time  
- Domain-agnostic and reusable  

---

## 🎯 Impact Scoring & Asset Prioritization

TugaRecon evaluates each discovered subdomain using **semantic indicators** extracted from naming patterns and context.

### Signals considered

- Administrative exposure (`admin`, `panel`, `manage`)
- Authentication services (`auth`, `login`, `sso`)
- Production or critical environments (`prod`, `core`, `primary`)
- Sensitive roles (`api`, `gateway`, `billing`)

### Impact levels

- **CRITICAL** — Administrative or production exposure  
- **HIGH** — Authentication or security-sensitive services  
- **MEDIUM** — Internal or semi-exposed infrastructure  
- **LOW** — Static or non-actionable assets  

### Example output

```bash
[0001] [CRITICAL] impact=100   admin.prod.example.com
[0002] [HIGH    ] impact=75    auth.example.com
[0019] [LOW     ] impact=0     static-img.example.com
```

Impact scoring allows analysts to **prioritize what matters first**, reducing triage time and focusing effort on the most relevant assets.

---

## 🕒 Temporal Intelligence & Asset Memory (NEW)

TugaRecon introduces **temporal awareness**, transforming scans into an evolving intelligence timeline.

Each run creates a **snapshot** of discovered assets and compares it with previous executions.

### Temporal states detected

- **NEW** — Subdomain discovered for the first time  
- **STABLE** — Asset unchanged across scans  
- **ESCALATED** — Impact increased since last snapshot  
- **DORMANT** — Previously seen, now missing for ≥ 2 days  

### What this enables

- Detect newly exposed services instantly  
- Identify assets increasing in criticality  
- Spot disappearing infrastructure (possible decommissioning or defensive action)  
- Build historical awareness without external databases  

### Example intelligence output

```text
TOP TEMPORAL ASSETS
────────────────────────────────
ESCALATED  admin.api.example.com
NEW        auth.prod.example.com
DORMANT    old-panel.dev.example.com
```

Snapshots are stored automatically per target and date, creating **long-term reconnaissance memory**.

---

## ⚠️ Legal Notice

**Use TugaRecon only on targets you own or have explicit permission to test.**  
The author is not responsible for misuse. Unauthorized use may be illegal.

---

## 📦 Requirements & Dependencies

- Python 3.8+

Install dependencies:

```bash
pip3 install -r requirements.txt
```

Main dependencies include:

```
dnspython
requests
urllib3
progress
pydot
networkx
ipwhois
pyvis
multiprocess
pandas
argparse
matplotlib
tldextract
colorama
lxml
beautifulsoup4
```

---

## 📦 Installation

```bash
git clone https://github.com/skynet0x01/tugarecon.git
cd tugarecon
pip3 install -r requirements.txt
```

> ✅ Recommended: use a virtual environment  
> `python3 -m venv venv && source venv/bin/activate`

---

## ⚙️ Basic Usage

```bash
python3 tugarecon.py -d example.com
```

### Main options

| Option | Description |
|------:|------------|
| `-d, --domain` | Target domain (required) |
| `-b, --bruteforce` | Enable brute-force discovery |
| `-e, --enum` | Run specific modules only |
| `-t, --threads` | Concurrent threads (default: 250) |
| `-m, --map` | Generate network / ASN map |
| `-r, --results` | Show saved results |

---

## 🔎 Examples

```bash
python3 tugarecon.py -d example.com
python3 tugarecon.py -d example.com --enum certspotter hackertarget
python3 tugarecon.py -d example.com -b
python3 tugarecon.py -d example.com -m
python3 tugarecon.py -r
```

---

## 🧩 Project Structure

```
tugarecon/
├── modules/
│   └── intelligence/
│       └── snapshot.py
├── utils/
│   ├── temporal_analysis.py
│   └── temporal_view.py
├── wordlists/
├── results/
├── tugarecon.py
└── README.md
```

---

## 🧭 Roadmap

- [ ] HTTP/HTTPS active probing via httpx  
- [ ] Risk trend graphs per subdomain  
- [ ] Web dashboard for intelligence history  
- [ ] Export intelligence reports (PDF)  

---

## 👤 Author

**Skynet0x01**  
Cybersecurity Researcher & Tool Developer  
🌍 Portugal  

---

## 📄 License

This project is licensed under **GNU GPLv3**.

---

> TugaRecon is not just a scanner — it is a reconnaissance system that learns, remembers and evolves.


### 💖 Support & Donations

If you find this project useful, consider supporting its continued development.  
Your contributions help add new features, improve stability, and keep the tool updated.

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

