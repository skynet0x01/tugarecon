#!/usr/bin/python3
# TugaRecon, tribute to Portuguese explorers reminding glorious past of this country
# Bug Bounty Recon, search for subdomains and save in to a file
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
# import go here :)
import os
import sys
import asyncio
import pydot

from datetime import datetime
from ipwhois import IPWhois
from utils.tuga_colors import R, W, Y


# ----------------------------------------------------------------------------------------------------------
def read_subdomains(file_path):
    with open(file_path, 'r') as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('#')]


# ----------------------------------------------------------------------------------------------------------
async def resolve_ip(domain):
    loop = asyncio.get_event_loop()
    try:
        return await loop.getaddrinfo(domain, None)
    except Exception:
        return []


# ----------------------------------------------------------------------------------------------------------
async def resolve_all_ips(domains):
    ip_map = {}
    for domain in domains:
        try:
            infos = await resolve_ip(domain)
            if infos:
                ip = infos[0][4][0]
                ip_map[domain] = ip
        except Exception:
            continue
    return ip_map


# ----------------------------------------------------------------------------------------------------------
def lookup_asn(ip):
    try:
        obj = IPWhois(ip)
        res = obj.lookup_rdap()
        return res.get('asn_description', 'Unknown ASN')
    except Exception:
        return 'Unknown ASN'


# ----------------------------------------------------------------------------------------------------------
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
def shorten_label(text, max_len=30):
    if len(text) <= max_len:
        return text
    parts = text.split('.')
    return '\n'.join(['.'.join(parts[i:i+2]) for i in range(0, len(parts), 2)])


# ----------------------------------------------------------------------------------------------------------
def build_graph_with_clusters(subdomain_ip_map):
    graph = pydot.Dot(graph_type='digraph', rankdir='LR')
    asn_clusters = {}
    ip_seen = set()

    for sub, ip in subdomain_ip_map.items():
        asn = lookup_asn(ip)
        emoji, color = classify_node(sub)
        label = f"{emoji} {shorten_label(sub)}"

        if asn not in asn_clusters:
            cluster = pydot.Cluster(asn.replace(" ", "_"), label=f"ASN: {asn}", style='filled', fillcolor='#eeeeee')
            graph.add_subgraph(cluster)
            asn_clusters[asn] = cluster

        cluster = asn_clusters[asn]

        # Adiciona IP uma vez por cluster
        if ip not in ip_seen:
            node_ip = pydot.Node(ip, style='filled', fillcolor='lightblue', shape='ellipse')
            cluster.add_node(node_ip)
            ip_seen.add(ip)

        node_sub = pydot.Node(label, style='filled', fillcolor=color, shape='box')
        cluster.add_node(node_sub)

        graph.add_edge(pydot.Edge(ip, label))

    return graph


# ----------------------------------------------------------------------------------------------------------
def export_graph(graph, latest_path, output_pdf='subdomains_clustered.pdf', output_svg='subdomains_clustered.svg'):
    # Garante que o diretório de destino existe
    os.makedirs(latest_path, exist_ok=True)

    # Caminhos completos para os ficheiros de saída
    pdf_path = os.path.join(latest_path, output_pdf)
    svg_path = os.path.join(latest_path, output_svg)

    # Exporta os ficheiros
    graph.write_pdf(pdf_path)
    graph.write_svg(svg_path)

    # Mensagens de confirmação
    print(f"[+] Graph exported to PDF: {pdf_path}")
    print(f"[+] Graph exported to SVG: {svg_path}")


# ----------------------------------------------------------------------------------------------------------
def main(file_path, latest_path):
    subdomains = read_subdomains(file_path)
    print(f"[+] Resolving {len(subdomains)} subdomains...")
    ip_map = asyncio.run(resolve_all_ips(subdomains))

    if not ip_map:
        print("[-] No subdomains resolved successfully.")
        return

    print(f"[+] {len(ip_map)} subdomains resolved with IP. Building graph with ASN clusters...")
    graph = build_graph_with_clusters(ip_map)
    export_graph(graph, latest_path)


# ----------------------------------------------------------------------------------------------------------
def get_latest_date_folder(base_path, savetarget):
    # Listar pastas que parecem datas (formato YYYY-MM-DD)
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
            # Tenta converter o nome para data
            date_obj = datetime.strptime(folder, '%Y-%m-%d')
            date_folders.append((date_obj, folder))
        except ValueError:
            pass  # ignora pastas que não são datas
    
    if not date_folders:
        print("")
        print(R + f"Base folder not found: {base_path}")
        print(R + f"Run first, python3 tugarecon.py -d {savetarget}" + W)
        print("")
        sys.exit(1)
    
    # Ordena e pega a pasta mais recente
    date_folders.sort()
    latest_folder = date_folders[-1][1]
    return os.path.join(base_path, latest_folder)


# ----------------------------------------------------------------------------------------------------------
def tuga_map(target):
    savetarget = target
    base_path = os.path.join('results', savetarget)
    latest_path = get_latest_date_folder(base_path, savetarget)
    print("")
    print(Y + f"Using the most recent folder: {latest_path}" + W)
    print("")

    subdomains_file = os.path.join(latest_path, 'subdomains.txt')
    if not os.path.isfile(subdomains_file):
        print("")
        print(R + f"Run first, python3 tugarecon.py -d {savetarget}")
        print(R + f"Subdomains file not found: {subdomains_file}" + W)
        print("")
        sys.exit(1)

    main(subdomains_file, latest_path)
