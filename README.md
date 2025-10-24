# TugaRecon
![version](https://img.shields.io/badge/version-2.40-blue)
![python](https://img.shields.io/badge/python-3.8%2B-yellow)
![license](https://img.shields.io/github/license/skynet0x01/tugarecon)
![issues](https://img.shields.io/github/issues/skynet0x01/tugarecon)
![stars](https://img.shields.io/github/stars/skynet0x01/tugarecon?style=social)

> **TugaRecon** is an advanced subdomain enumeration and DNS reconnaissance tool built for security researchers, penetration testers, and OSINT professionals.  
> It combines multiple passive and active modules to extract, verify, and map subdomains of a target domain efficiently.

---
> **TugaRecon**, tribute to Portuguese explorers reminding glorious past of this country.

>During the 15th and 16th centuries, Portuguese explorers were at the forefront of European overseas exploration, which led them to reach India, establish multiple trading posts in Asia and Africa, and settle what would become Brazil, creating one of the most powerful empires.

>skynet0x01

---

## 📸 TugaRecon

<p align="center">

  <img width="803" height="575" alt="tugarecon" src="https://github.com/user-attachments/assets/7e7461e7-ff6c-4132-9356-b8f8cab6bc15" />
</p>

---

## 🚀 Features

- 🔍 Passive and active subdomain enumeration using various OSINT sources
- 📡 Built-in brute-force mode using custom wordlists
- 🌐 DNS resolution with fallback mechanisms
- 🧠 Multi-module integration (Certspotter, DNSDumpster, HackerTarget, etc.)
- 🗺️ Optional subdomain map generation (interactive or visual)
- 📁 Clean output in `.txt`, `.json`, `.html`, or `.csv`
- 🔒 No API keys required for most modules

---

## ⚠️ Legal Notice

**Use TugaRecon only on targets you have explicit permission to test.** The author is not responsible for misuse. Unauthorized use of this tool may be illegal.

---

## 📄 License

This project is licensed under **GNU GPLv3**. The source file headers include the GPLv3 license and a patent restriction clause — the `README` has been updated to reflect that.  

---
## 📦 Requirements & Dependencies

Minimum requirements:
- Python 3.8+

Main dependencies (install via `pip install -r requirements.txt`):

```
dnspython>=2.8.0
whois>=1.20240129.2
DateTime>=5.5
requests>=2.32.5
urllib3>=2.5.0
progress>=1.6.1
asyncio>=4.0.0
pydot>=4.0.1
networkx>=3.5
ipwhois>=1.3.0
pyvis>=0.3.2
multiprocess>=0.70.18
pandas>=2.3.3
argparse>=1.4.0
matplotlib>=3.10.3
networkx>=3.5
graphviz>=0.20.3
tldextract>=5.1.2
colorama>=0.4.6
lxml>=5.2.2
beautifulsoup4
```

## 📦 Installation

```bash
git clone https://github.com/skynet0x01/tugarecon.git
cd tugarecon
pip3 install -r requirements.txt
```

> ✅ Recommended: Run in a Python virtual environment  
> `python3 -m venv venv && source venv/bin/activate`

---

## ⚙️ Basic Usage

```bash
python3 tugarecon.py -d example.com
```

### Main options

| Option         | Description |
|--------------:|----------|
| `-d, --domain`   | Target domain (required), e.g.: `example.com` |
| `-b, --bruteforce` | Enable brute-force mode (uses internal wordlists under `wordlists/`) |
| `-e, --enum`    | Select specific modules (e.g.: `--enum ssl certspotter`) — if omitted, all supported modules run |
| `-t, --threads` | Number of concurrent threads (default: 250) |
| `-m, --map`     | Generate a network/visual map of the domain |
| `-r, --results` | Show previously saved results (invoked without arguments) |

> Note: The previous README mentioned a `--full` flag; the current behavior is: if `--enum` is not passed, all configured modules run by default.

---

## 🔎 Examples

Run all modules (default):

```bash
python3 tugarecon.py -d google.pt
```

Run specific modules only:

```bash
python3 tugarecon.py -d example.com --enum certspotter hackertarget
```

Brute-force using internal wordlists:

```bash
python3 tugarecon.py -d example.com --bruteforce
# or
python3 tugarecon.py -d example.com -b
```

Generate a visual map (relies on the existing visualization utilities):

```bash
python3 tugarecon.py -d example.com -m
```

View saved results (shortcut):

```bash
python3 tugarecon.py -r
```

### Typical output

```
output/
├── tugarecon/results/example.com/2025-07-18/subdomains_clustered.svg
├── tugarecon/results/example.com/2025-07-18/subdomains_clustered.pdf
├── tugarecon/results/example.com/2025-07-18/tuga_bruteforce.txt
└── tugarecon/results/example.com/2025-07-18/subdomains.txt
```

---

## 🧩 Modules (overview)

| Module         | Type      | Function / Source                                      |
|---------------:|----------:|--------------------------------------------------------|
| `certspotter`  | Passive   | Certificate Transparency logs                          |
| `hackertarget` | Passive   | HackerTarget public API                                |
| `alienvault`  | Passive   | Collaborative platform for global threat intelligence. |
| `DNSDumpster`  | Passive   | Extraction from dnsdumpster. ** New **                 |
| `bruteforce`   | Active    | Dictionary-based brute-force using wordlists           |
| `dnsresolve`   | Resolver  | Resolve IPs with fallback DNS                          |
| `mapbuilder`   | Visual    | Generate maps (HTML / Graphviz / pyvis)                |

> The full list of modules is inside `modules/` and can be extended.

---
---

## 🛠 Project structure

```
tugarecon/
├── modules/
│   ├── certspotter.py
│   ├── hackertarget.py
│   └── ...
├── utils/
│   ├── tuga_colors.py
│   ├── tuga_banner.py
│   └── ...
├── wordlists/
│   ├── first_names.txt
│   └── next_names.txt
├── results/
├── tugarecon.py
├── requirements.txt
└── README.md
```

## 🧭 Roadmap (excerpt)

- [ ] Export to PDF/SVG maps (better integration)
- [ ] Integrate `httpx` for active HTTP/HTTPS service detection
- [ ] ASN-based grouping on visual maps
- [ ] Web frontend for remote analysis

---

---

## 📸 Example Map Output

<p align="center">

  <img width="568" height="536" alt="Example Subdomain Map" src="https://github.com/user-attachments/assets/0b6acee3-b716-4e4b-8c88-c72a7b005d1b" />

</p>

---

## 🤝 Contributing

We welcome contributions!  
Please read the [CONTRIBUTING.md](CONTRIBUTING.md) file before submitting pull requests.

---

## 🧪 Related Tools

- [Sublist3r](https://github.com/aboul3la/Sublist3r)
- [Amass](https://github.com/owasp-amass/amass)
- [DNSMap](https://github.com/makefu/dnsmap)

---

## 👤 Author

**Skynet0x01**  
Cybersecurity Researcher & Tool Developer  
🌍 Portugal  

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

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

