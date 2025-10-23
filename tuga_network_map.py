#!/usr/bin/python3
# TugaRecon, tribute to Portuguese explorers reminding glorious past of this country
# Bug Bounty Recon, search for subdomains and save into a file
# Coded By skynet0x01 2020-2025

# This file is part of TugaRecon, developed by skynet0x01 in 2020-2025.
#
# Copyright (C) 2025 skynet0x01
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
#
# Patent Restriction Notice:
# No patents may be claimed or enforced on this software or any derivative.
# Any patent claims will result in automatic termination of license rights under the GNU GPLv3.

# ----------------------------------------------------------------------------------------------------------
# imports
import os
import sys
import asyncio
import ipaddress
import pydot
import json
import csv
import socket
import ssl
import re
import importlib
import traceback

from datetime import datetime
from ipwhois import IPWhois
from utils.tuga_colors import R, W, Y

# Optional imports for certificate parsing and interactive export
try:
    from cryptography import x509
    from cryptography.hazmat.backends import default_backend
    CRYPTO_AVAILABLE = True
except Exception:
    CRYPTO_AVAILABLE = False

try:
    from pyvis.network import Network
    import networkx as nx
    PYVIS_AVAILABLE = True
except Exception:
    PYVIS_AVAILABLE = False

# ----------------------------------------------------------------------------------------------------------
# Read subdomains from file
def read_subdomains(file_path):
    with open(file_path, 'r') as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('#')]

# ----------------------------------------------------------------------------------------------------------
# Read bruteforce results from file
def read_bruteforce(file_path):
    with open(file_path, 'r') as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('#')]

# ----------------------------------------------------------------------------------------------------------
# Merge sources: subdomains.txt and optional tuga_bruteforce.txt
def merge_sources(sub_file, bruteforce_file=None):
    subs = set(read_subdomains(sub_file)) if os.path.isfile(sub_file) else set()
    brut = set()
    if bruteforce_file and os.path.isfile(bruteforce_file):
        brut = set(read_bruteforce(bruteforce_file))

    all_hosts = subs.union(brut)
    host_sources = {}
    for h in all_hosts:
        if h in subs and h in brut:
            host_sources[h] = 'both'
        elif h in subs:
            host_sources[h] = 'subdomains'
        else:
            host_sources[h] = 'bruteforce'
    return host_sources, list(all_hosts)

# ----------------------------------------------------------------------------------------------------------
# Async DNS resolution for single host
async def resolve_ip(domain):
    loop = asyncio.get_event_loop()
    try:
        return await loop.getaddrinfo(domain, None)
    except Exception:
        return []

# ----------------------------------------------------------------------------------------------------------
# Resolve all hosts concurrently
async def resolve_all_ips(domains):
    ip_map = {}
    tasks = []
    for domain in domains:
        tasks.append(resolve_ip(domain))

    results = await asyncio.gather(*tasks, return_exceptions=True)
    for domain, infos in zip(domains, results):
        try:
            if infos and not isinstance(infos, Exception):
                ip = infos[0][4][0]
                ip_map[domain] = ip
        except Exception:
            continue
    return ip_map

# ----------------------------------------------------------------------------------------------------------
# Lookup ASN and network info (sempre retorna string)
def lookup_network_info(ip):
    try:
        ip_obj = ipaddress.ip_address(ip)
        if ip_obj.is_private:
            return {
                'asn': 'Private Network',
                'asn_description': 'Private Network',
                'country': 'N/A',
                'cidr': 'N/A',
                'org': 'Local / Internal'
            }
    except ValueError:
        return {
            'asn': 'Invalid',
            'asn_description': 'Invalid IP',
            'country': 'N/A',
            'cidr': 'N/A',
            'org': 'N/A'
        }

    try:
        obj = IPWhois(ip)
        res = obj.lookup_rdap()
        # Garantir que nunca devolvemos None
        asn = res.get('asn') or 'Unknown'
        asn_desc = res.get('asn_description') or asn or 'Unknown ASN'
        country = res.get('asn_country_code') or '??'
        cidr = res.get('network', {}).get('cidr') or 'Unknown'
        org = res.get('network', {}).get('name') or 'Unknown Org'
        return {
            'asn': asn,
            'asn_description': asn_desc,
            'country': country,
            'cidr': cidr,
            'org': org
        }
    except Exception:
        return {
            'asn': 'Unknown',
            'asn_description': 'Unknown ASN',
            'country': '??',
            'cidr': 'Unknown',
            'org': 'Unknown Org'
        }

# ----------------------------------------------------------------------------------------------------------
# Classify node type based on keywords
def classify_node(sub):
    sub = sub.lower()
    if any(x in sub for x in ['mail', 'smtp', 'imap', 'mx']):
        return '📧', '#ffd699'  # email
    elif any(x in sub for x in ['web', 'www', 'http', 'site']):
        return '🌐', '#b3d9ff'  # web
    elif any(x in sub for x in ['printer', 'print']):
        return '🖨️', '#ffcccc'  # printer
    elif any(x in sub for x in ['router', 'gateway']):
        return '📡', '#ccffcc'  # router
    elif any(x in sub for x in ['nas', 'file', 'storage']):
        return '💾', '#e0e0e0'  # storage
    elif any(x in sub for x in ['cam', 'camera']):
        return '📷', '#ffe0b3'  # camera
    elif any(x in sub for x in ['dev', 'test', 'lab']):
        return '🧪', '#e6ccff'  # dev
    else:
        return '💻', '#f2f2f2'  # default

# ----------------------------------------------------------------------------------------------------------
# Shorten labels for better graph display
def shorten_label(text, max_len=30):
    if len(text) <= max_len:
        return text
    parts = text.split('.')
    return '\n'.join(['.'.join(parts[i:i+2]) for i in range(0, len(parts), 2)])

# ----------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------
# Fetch SSL certificate synchronously (TLS 1.2+ enforced)
def fetch_cert_sync(host, port=443, timeout=5):
    try:
        ctx = ssl.create_default_context()

        # 🔒 Força protocolos seguros apenas (TLS 1.2 ou superior)
        if hasattr(ssl, "TLSVersion"):
            ctx.minimum_version = ssl.TLSVersion.TLSv1_2
        else:
            # fallback para versões mais antigas do Python
            ctx.options |= ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1

        with socket.create_connection((host, port), timeout=timeout) as sock:
            with ctx.wrap_socket(sock, server_hostname=host) as ss:
                der = ss.getpeercert(binary_form=True)
                return der
    except Exception:
        return None


# ----------------------------------------------------------------------------------------------------------
# Get certificate SANs asynchronously
async def get_cert_sans(host, port=443):
    loop = asyncio.get_event_loop()
    try:
        der = await loop.run_in_executor(None, fetch_cert_sync, host, port)
        if not der:
            return []
        if CRYPTO_AVAILABLE:
            cert = x509.load_der_x509_certificate(der, default_backend())
            sans = []
            try:
                ext = cert.extensions.get_extension_for_class(x509.SubjectAlternativeName)
                for name in ext.value.get_values_for_type(x509.DNSName):
                    sans.append(name)
            except Exception:
                pass
            try:
                cn = cert.subject.get_attributes_for_oid(x509.oid.NameOID.COMMON_NAME)[0].value
                if cn and cn not in sans:
                    sans.append(cn)
            except Exception:
                pass
            return sans
        else:
            return []
    except Exception:
        return []

# ----------------------------------------------------------------------------------------------------------
# Build graph with clusters by ASN, including SAN links
def build_graph_with_clusters(subdomain_ip_map, host_sources=None, cert_map=None):
    graph = pydot.Dot(graph_type='digraph', rankdir='LR')
    asn_clusters = {}
    ip_seen = set()
    network_summary = {}

    for sub, ip in subdomain_ip_map.items():
        net_info = lookup_network_info(ip)

        # **Correção definitiva:** forçar ASN como string
        raw_asn = net_info.get('asn_description') or net_info.get('asn') or 'Unknown ASN'
        asn_id = re.sub(r'[^0-9A-Za-z_]', '_', str(raw_asn)).strip('_')
        if not asn_id:
            asn_id = 'Unknown_ASN'

        try:
            emoji, color = classify_node(sub)
        except Exception:
            emoji, color = '💻', '#f2f2f2'

        source = host_sources.get(sub, 'unknown') if host_sources else 'unknown'
        label = f"{emoji} {shorten_label(sub)}\n[{source}]"

        if asn_id not in asn_clusters:
            cluster_label = f"ASN: {raw_asn}\n({net_info.get('country','??')})"
            cluster = pydot.Cluster(
                asn_id,
                label=cluster_label,
                style='filled',
                fillcolor='#eeeeee'
            )
            graph.add_subgraph(cluster)
            asn_clusters[asn_id] = cluster
            network_summary[asn_id] = {
                'asn_display': raw_asn,
                'country': net_info.get('country', '??'),
                'cidrs': set(),
                'orgs': set(),
                'hosts': []
            }

        cluster = asn_clusters[asn_id]

        if ip not in ip_seen:
            ip_label = f"{ip}\n{net_info.get('country','??')} | {net_info.get('cidr','Unknown')}\n{net_info.get('org','Unknown Org')}"
            node_ip = pydot.Node(ip, label=ip_label, style='filled', fillcolor='lightblue', shape='ellipse')
            cluster.add_node(node_ip)
            ip_seen.add(ip)

        node_sub = pydot.Node(label, style='filled', fillcolor=color, shape='box')
        cluster.add_node(node_sub)
        graph.add_edge(pydot.Edge(node_sub, ip))

        # Link certificate SANs
        if cert_map and sub in cert_map:
            sans = cert_map[sub]
            for san in sans:
                if san != sub:
                    san_label = f"🔖 {shorten_label(san)}\n[cert]"
                    node_san = pydot.Node(san_label, style='rounded')
                    cluster.add_node(node_san)
                    graph.add_edge(pydot.Edge(node_sub, node_san, style='dashed'))

        # Summary
        network_summary[asn_id]['cidrs'].add(net_info.get('cidr', 'Unknown'))
        network_summary[asn_id]['orgs'].add(net_info.get('org', 'Unknown Org'))
        network_summary[asn_id]['hosts'].append({'host': sub, 'ip': ip, 'source': source})

    # footer node outside clusters
    footer_node = pydot.Node(
        'footer',
        label="mapa gerado por: https://github.com/skynet0x01/tugarecon",
        shape='plaintext',
        fontsize='14'
    )
    graph.add_node(footer_node)

    footer_sub = pydot.Cluster(
        'footer_cluster',
        label='',
        style='invis'
    )
    footer_sub.add_node(footer_node)
    footer_sub.set_rank('min')
    graph.add_subgraph(footer_sub)

    return graph, network_summary

# ----------------------------------------------------------------------------------------------------------


# ----------------------------------------------------------------------------------------------------------
# Export graph PDF/SVG
def export_graph(graph, latest_path, output_pdf='subdomains_clustered.pdf', output_svg='subdomains_clustered.svg'):
    os.makedirs(latest_path, exist_ok=True)
    pdf_path = os.path.join(latest_path, output_pdf)
    svg_path = os.path.join(latest_path, output_svg)

    try:
        graph.write_pdf(pdf_path)
        graph.write_svg(svg_path)
        print(f"[+] Graph exported to PDF: {pdf_path}")
        print(f"[+] Graph exported to SVG: {svg_path}")
    except Exception as e:
        print(R + f"[!] Failed to write graph files: {e}" + W)

# ----------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------
# Export network summary as TXT/JSON/CSV (corrigido para JSON-safe)
def export_network_summary(network_summary, latest_path):
    output_file = os.path.join(latest_path, "network_info.txt")
    json_file = os.path.join(latest_path, "network_info.json")
    csv_file = os.path.join(latest_path, "network_info.csv")

    # --- TXT export ---
    with open(output_file, 'w') as f:
        for asn, data in network_summary.items():
            f.write(f"ASN: {data['asn_display']}\n")
            f.write(f"Country: {data['country']}\n")
            f.write(f"Organizations: {', '.join(data['orgs'])}\n")
            f.write(f"CIDRs: {', '.join(data['cidrs'])}\n")
            f.write(f"Hosts ({len(data['hosts'])}):\n")
            for h in data['hosts']:
                f.write(f"  - {h['host']} -> {h['ip']} ({h['source']})\n")
            f.write("\n")

    # --- JSON export (converte sets para listas) ---
    json_safe_summary = {}
    for asn, data in network_summary.items():
        json_safe_summary[asn] = {
            'asn_display': data['asn_display'],
            'country': data['country'],
            'cidrs': list(data['cidrs']),
            'orgs': list(data['orgs']),
            'hosts': data['hosts']
        }

    with open(json_file, 'w') as jf:
        json.dump(json_safe_summary, jf, indent=2)

    # --- CSV export ---
    with open(csv_file, 'w', newline='') as cf:
        writer = csv.writer(cf)
        writer.writerow(['asn', 'country', 'orgs', 'cidrs', 'host', 'ip', 'source'])
        for asn, data in network_summary.items():
            for h in data['hosts']:
                writer.writerow([
                    data['asn_display'],
                    data['country'],
                    ';'.join(data['orgs']),
                    ';'.join(data['cidrs']),
                    h['host'],
                    h['ip'],
                    h['source']
                ])

    print(f"[+] Network information saved: {output_file}")
    print(f"[+] Network JSON saved: {json_file}")
    print(f"[+] Network CSV saved: {csv_file}")


# ----------------------------------------------------------------------------------------------------------
# Export interactive PyVis map (import dinâmico, opcional — não parte se libs ausentes)
def export_pyvis(network_summary, latest_path):
    """
    Gera um mapa interativo (HTML) usando pyvis/networkx, mas não falha caso
    essas dependências não estejam instaladas. Se não existirem, apenas informa e retorna.
    Usa write_html/save_graph/show com fallbacks para evitar erros como
    "'NoneType' object has no attribute 'render'".
    """
    # Tentativa de import dinâmico
    try:
        pyvis_module = importlib.import_module('pyvis.network')
        Network = pyvis_module.Network
    except Exception:
        print(R + "pyvis não instalado - skipping interactive HTML export." + W)
        return

    try:
        nx = importlib.import_module('networkx')
    except Exception:
        print(R + "networkx não instalado - skipping interactive HTML export." + W)
        return

    try:
        G = nx.Graph()
        for asn, data in network_summary.items():
            for h in data['hosts']:
                host = h['host']
                ip = h['ip']
                G.add_node(host, title=f"Host: {host}<br>IP: {ip}")
                G.add_node(ip, title=f"IP: {ip}<br>ASN: {data.get('asn_display','Unknown')}<br>Country: {data.get('country','??')}")
                G.add_edge(host, ip)

        net = Network(height='1000px', width='100%', notebook=False)
        net.from_nx(G)

        outpath = os.path.join(latest_path, 'subdomains_map.html')

        # Tentar APIs mais diretas que não fazem render/abrir browser
        wrote = False
        # 1) tentar write_html (pyvis >= certa versão tem este método)
        try:
            write = getattr(net, 'write_html', None)
            if callable(write):
                write(outpath)
                wrote = True
        except Exception:
            wrote = False

        # 2) fallback para save_graph / save_graph_html (nomes variam)
        if not wrote:
            try:
                save_graph = getattr(net, 'save_graph', None)
                if callable(save_graph):
                    save_graph(outpath)
                    wrote = True
            except Exception:
                wrote = False

        # 3) fallback final: show (pode tentar abrir browser e causar render internamente)
        if not wrote:
            try:
                show = getattr(net, 'show', None)
                if callable(show):
                    show(outpath)
                    wrote = True
            except Exception:
                wrote = False

        if not wrote:
            print(R + "[!] I was unable to write subdomains_map.html with pyvis (methods write_html/save_graph/show failed)." + W)
        else:
            # Inject footer (mesma lógica que tinhas antes)
            try:
                footer_html = '''
<div style="position:fixed;bottom:8px;left:8px;font-size:12px;opacity:0.9;z-index:9999;">
map generated by: <a href="https://github.com/skynet0x01/tugarecon" target="_blank">
https://github.com/skynet0x01/tugarecon</a></div>
'''
                with open(outpath, 'r', encoding='utf-8') as f:
                    html = f.read()
                if '</body>' in html:
                    html = html.replace('</body>', footer_html + '</body>')
                elif '</BODY>' in html:
                    html = html.replace('</BODY>', footer_html + '</BODY>')
                else:
                    html += footer_html
                with open(outpath, 'w', encoding='utf-8') as f:
                    f.write(html)
            except Exception as e:
                print(R + f"[!] Failed to inject footer into HTML: {e}" + W)

            print(f"[+] Interactive map exported: {outpath}")

    except Exception as e:
        print(R + "[!] Failed to export pyvis HTML (full traceback below):" + W)
        traceback.print_exc()
# ----------------------------------------------------------------------------------------------------------
# Main async workflow
async def main_async(file_path, bruteforce_path, latest_path):
    host_sources, hosts = merge_sources(file_path, bruteforce_path)
    print(f"[+] Resolving {len(hosts)} hosts (sources: subdomains/bruteforce)...")

    ip_map = await resolve_all_ips(hosts)
    if not ip_map:
        print("[-] No hosts resolved successfully.")
        return

    # Collect SANs
    cert_tasks = [get_cert_sans(host) for host in hosts]
    cert_results = await asyncio.gather(*cert_tasks, return_exceptions=True)
    cert_map = {}
    for host, res in zip(hosts, cert_results):
        try:
            if isinstance(res, Exception):
                cert_map[host] = []
            else:
                cert_map[host] = res if res else []
        except Exception:
            cert_map[host] = []

    print(f"[+] {len(ip_map)} hosts resolved with IP. Building graph with ASN clusters and cert links...")
    graph, network_summary = build_graph_with_clusters(ip_map, host_sources=host_sources, cert_map=cert_map)

    export_graph(graph, latest_path)
    export_network_summary(network_summary, latest_path)
    export_pyvis(network_summary, latest_path)

    # Export cert map
    cert_file = os.path.join(latest_path, 'cert_sans.json')
    with open(cert_file, 'w') as cf:
        json.dump(cert_map, cf, indent=2)
    print(f"[+] Certificate SAN map saved: {cert_file}")

# ----------------------------------------------------------------------------------------------------------
# Get latest date folder
def get_latest_date_folder(base_path, savetarget):
    try:
        folders = [f for f in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, f))]
    except FileNotFoundError:
        print("")
        print(R + f"Base folder not found: {base_path}")
        print(R + f"Run first, python3 tugarecon.py -d {savetarget}" + W)
        print("")
        sys.exit(1)

    date_folders = []
    for folder in folders:
        try:
            date_obj = datetime.strptime(folder, '%Y-%m-%d')
            date_folders.append((date_obj, folder))
        except ValueError:
            pass

    if not date_folders:
        print("")
        print(R + f"Base folder not found: {base_path}")
        print(R + f"Run first, python3 tugarecon.py -d {savetarget}" + W)
        print("")
        sys.exit(1)

    date_folders.sort()
    latest_folder = date_folders[-1][1]
    return os.path.join(base_path, latest_folder)

# ----------------------------------------------------------------------------------------------------------
# Main map function
def tuga_map(target):
    savetarget = target
    base_path = os.path.join('results', savetarget)
    latest_path = get_latest_date_folder(base_path, savetarget)
    print("")
    print(Y + f"Using the most recent folder: {latest_path}" + W)
    print("")

    subdomains_file = os.path.join(latest_path, 'subdomains.txt')
    bruteforce_file = os.path.join(latest_path, 'tuga_bruteforce.txt')

    # Mensagens de aviso caso um dos ficheiros não exista
    if not os.path.isfile(subdomains_file):
        print(Y + "subdomains.txt not found; only tuga_bruteforce.txt will be used (if it exists)." + W)
    if not os.path.isfile(bruteforce_file):
        print(Y + "tuga_bruteforce.txt not found; only subdomains.txt will be used (if it exists)." + W)
    if not os.path.isfile(subdomains_file) and not os.path.isfile(bruteforce_file):
        print("")
        print(R + f"Run first, python3 tugarecon.py -d {savetarget}")
        print(R + f"No subdomains or bruteforce file found in: {latest_path}" + W)
        print("")
        sys.exit(1)

    asyncio.run(main_async(subdomains_file, bruteforce_file, latest_path))

# ----------------------------------------------------------------------------------------------------------
