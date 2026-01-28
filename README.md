# TugaRecon

![version](https://img.shields.io/badge/version-2.53-blue)
![python](https://img.shields.io/badge/python-3.8%2B-yellow)
![license](https://img.shields.io/github/license/skynet0x01/tugarecon)
![issues](https://img.shields.io/github/issues/skynet0x01/tugarecon)
![stars](https://img.shields.io/github/stars/skynet0x01/tugarecon?style=social)

> **TugaRecon** is an advanced reconnaissance and intelligence framework that goes beyond enumeration.  
> It observes, interprets, remembers, and reacts — transforming subdomains into **architectural intelligence**.

---

## 🧭 Philosophy

**TugaRecon** is inspired by Portuguese explorers.

During the 15th and 16th centuries, navigators did more than discover land —  
they **mapped patterns, learned from each voyage, and refined future expeditions**.

TugaRecon follows the same principle:

> **Explore → Map → Learn → Remember → React**

— *skynet0x01*

Reconnaissance is not about collecting data.  
It is about **understanding systems**.

---

## 📸 Preview

<p align="center">
  <img width="803" height="575" alt="tugarecon" src="https://github.com/user-attachments/assets/7e7461e7-ff6c-4132-9356-b8f8cab6bc15" />
</p>

---

## 🚀 Core Capabilities

- 🔍 Passive & active subdomain enumeration (multi-source OSINT)
- 📡 High-performance brute-force with adaptive wordlists
- 🌐 DNS resolution with fallback DNS servers
- 🧠 Semantic analysis & **architectural impact scoring**
- 🎯 Asset prioritization by real security relevance
- 🕒 **Temporal intelligence & asset memory**
- ⚙️ **Automated reactions to risk changes**
- 🧩 Infrastructure & role inference (IAM, DB, CI/CD, SCADA, etc.)
- 🗺️ Optional ASN / infrastructure network mapping
- 📁 Clean outputs: `.txt`, `.json`, `.csv`, `.png`, `.svg`, `.md`, `.pdf`
- 🔒 No API keys required for most modules

---

## 🧠 Semantic & Architectural Intelligence

TugaRecon does not treat subdomains as strings.

It interprets them as **signals of infrastructure design**.

From naming conventions alone, it can infer:

- Identity & access layers (`auth`, `sso`, `iam`)
- Secrets & key management (`vault`, `kms`, `secrets`)
- Databases & data planes (`db`, `rds`, `postgres`)
- Network control (`gateway`, `proxy`, `waf`)
- Orchestration layers (`k8s`, `eks`, `cluster`)
- CI/CD infrastructure (`jenkins`, `gitlab`, `pipeline`)
- Monitoring & operations (`grafana`, `prometheus`)
- ICS / SCADA & industrial systems

This works **even without open ports or HTTP access**.

---

## 🎯 Impact Scoring & Prioritization

Each asset receives a **numeric impact score (0–100)** and a priority level.

### Priority Levels

| Level | Meaning |
|------:|--------|
| **CRITICAL** | Control-plane, secrets, or production exposure |
| **HIGH** | Auth, database, or sensitive infrastructure |
| **MEDIUM** | Internal or supporting systems |
| **LOW** | Non-actionable or static assets |

---

## 🕒 Temporal Intelligence & Asset Memory

TugaRecon is **stateful**.

Every scan is compared against historical snapshots, allowing it to reason about **change over time**.

---

## ⚙️ Automated Reactions

Temporal events can trigger **automatic deep-dive analysis**.

Only **relevant assets** consume resources.

---

## 📦 Installation

```bash
git clone https://github.com/skynet0x01/tugarecon.git
cd tugarecon
pip3 install -r requirements.txt
```

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

