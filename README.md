# TugaRecon
![version](https://img.shields.io/badge/version-1.30-blue)
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

## 🚀 Features

- 🔍 Passive and active subdomain enumeration using various OSINT sources
- 📡 Built-in brute-force mode using custom wordlists
- 🌐 DNS resolution with fallback mechanisms
- 🧠 Multi-module integration (Certspotter, DNSDumpster, HackerTarget, etc.)
- 🗺️ Optional subdomain map generation (interactive or visual)
- 📁 Clean output in `.txt`, `.json`, `.html`, or `.csv`
- 🔒 No API keys required for most modules

---

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

### Common Options

| Option       | Description                                 |
|--------------|---------------------------------------------|
| `-d DOMAIN`  | Target domain (required)                    |
| `--bruteforce` | Enable subdomain brute-forcing              |
| `--full`     | Run all available modules                   |
| `--map`      | Save interactive map of discovered hosts    |
| `--help`     | Show full list of options                   |

---

## 🔎 Example

```bash
python3 tugarecon.py -d google.pt --map
```

📁 Output:

```
output/
├── tugarecon/results/google.com/2025-07-18/subdomains_clustered.svg
├── tugarecon/results/google.com/2025-07-18/subdomains_clustered.pdf
├── tugarecon/results/google.com/2025-07-18/tuga_bruteforce.txt
└── tugarecon/results/google.com/2025-07-18/subdomains.txt
```

---

## 🧩 Modules Overview

| Module         | Type      | Source/Functionality                     |
|----------------|-----------|------------------------------------------|
| `certspotter`  | Passive   | Queries certificate transparency logs     |
| `hackertarget` | Passive   | Uses HackerTarget public API             |
| `dnsdumpster`  | Passive   | Extracts data from dnsdumpster.com       |
| `bruteforce`   | Active    | Dictionary-based subdomain brute-force   |
| `dnsresolve`   | Resolver  | Resolves IPs with optional fallback DNS  |
| `mapbuilder`   | Visual    | Generates HTML/Graphviz subdomain maps   |

---

## 📁 Project Structure

```
tugarecon/
├── modules/
│   ├── certspotter.py
│   ├── hackertarget.py
│   └── ...
├── wordlists/
│   ├── first_names.txt
│   └── next_names.txt
├── results/
├── tugarecon.py
├── requirements.txt
└── README.md
```

---

## 🧠 Roadmap

- [ ] Add support for export to PDF/SVG maps
- [ ] Integrate `httpx` to detect live HTTP/HTTPS services
- [ ] ASN-based grouping in visual maps
- [ ] Web-based frontend interface for remote analysis

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
