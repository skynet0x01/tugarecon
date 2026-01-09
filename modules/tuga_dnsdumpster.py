#!/usr/bin/python3
# TugaRecon, tribute to Portuguese explorers reminding glorious past of this country
# Bug Bounty Recon, search for subdomains and save in to a file
# Coded By skynet0x01 2020-2026

# This file is part of TugaRecon, developed by skynet0x01 in 2020-2025.
#
# Copyright (C) 2026 skynet0x01
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

# import go here
# ----------------------------------------------------------------------------------------------------------
import time
import requests
import re
from bs4 import BeautifulSoup

from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# Import internal modules
from modules import tuga_useragents  # random user-agent
from utils.tuga_save import write_file


# ----------------------------------------------------------------------------------------------------------
class DNSDUMPSTER:

    def __init__(self, target):
        """
        Constructor: recebe o domínio alvo (target).
        Executa engine_url() que devolve a resposta HTML (ou 1 em caso de erro)
        e chama enumerate() se a resposta for válida.
        """
        self.target = target
        self.module_name = "DNSDumpster"
        self.engine = "dnsdumpster"
        self.response = self.engine_url()  # HTML response or 1 on error

        if self.response != 1:
            self.enumerate(self.response, target)
        else:
            pass

# ----------------------------------------------------------------------------------------------------------
    def engine_url(self):
        """
        Verificar o site dnsdumpster.com: fazer GET para obter csrf token + cookies,
        depois fazer POST com o domínio alvo e devolve o HTML resultante.
        Em caso de erro de conexão devolve 1.
        """
        session = requests.Session()
        # usa um user-agent aleatório do teu módulo interno
        ua = None
        try:
            ua = tuga_useragents.get_random_user_agent()
        except Exception:
            ua = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36"

        headers = {
            "User-Agent": ua,
            "Referer": "https://dnsdumpster.com/",
        }

        try:
            # 1) GET inicial para apanhar o form e o csrf token
            r = session.get("https://dnsdumpster.com/", headers=headers, timeout=20, verify=False)
            r.raise_for_status()
            html_get = r.text

            # procura token csrf no HTML (campo input hidden)
            soup = BeautifulSoup(html_get, "html.parser")
            csrf_input = soup.find("input", {"name": "csrfmiddlewaretoken"})
            if csrf_input and csrf_input.has_attr("value"):
                csrf_token = csrf_input["value"]
            else:
                # por vezes token está apenas nos cookies (django)
                csrf_token = session.cookies.get("csrftoken", "")

            # 2) Faz POST com o token e o domínio alvo
            data = {
                "csrfmiddlewaretoken": csrf_token,
                "targetip": self.target  # field name observado no form do site
            }

            # adicionar Referer e cookie manualmente (o session já tem cookies)
            headers_post = headers.copy()
            headers_post["Content-Type"] = "application/x-www-form-urlencoded"
            headers_post["Origin"] = "https://dnsdumpster.com"
            # envia o POST para a mesma URL
            r2 = session.post("https://dnsdumpster.com/", headers=headers_post, data=data, timeout=40, verify=False)
            r2.raise_for_status()
            return r2.text

        except requests.RequestException:
            return 1

# ----------------------------------------------------------------------------------------------------------
    def enumerate(self, response, target):
        """
        Faz parse do HTML de resposta e extrai subdomínios que contenham target.
        Usa regex para apanhar variações (ex: a.b.target.com, target.com, etc.).
        Chama write_file(subdomain, target) para cada subdomínio encontrado.
        """
        subdomains_found = set()
        self.subdomainscount = 0
        start_time = time.time()

        try:
            soup = BeautifulSoup(response, "html.parser")
            text = soup.get_text(separator="\n")  # texto bruto do HTML

            # Regex: procura palavras que contenham o domínio alvo (escapa o target)
            # aceita letras, números, hífen, underscore e pontos (subdomínios típicos)
            pattern = re.compile(r'([A-Za-z0-9_\-\.]+\.%s)' % re.escape(target), re.IGNORECASE)

            matches = pattern.findall(text)
            for match in matches:
                # normaliza: tira espaços e pontuações indesejadas
                sub = match.strip().strip('.,;:"\'()[]{}<>')
                # evita incluir apenas o domínio sem subdomínio
                # aqui incluímos também o próprio target (caso apareça)
                if sub and sub not in subdomains_found:
                    subdomains_found.add(sub)
                    self.subdomainscount += 1
                    try:
                        write_file(sub, target)
                    except Exception:
                        # se write_file falhar não interrompe a enumeração
                        pass

            # fallback adicional: procura tags <a> que contenham o domínio no href/text
            # (isto ajuda caso o layout tenha listas/links)
            for a in soup.find_all("a", href=True):
                href = a["href"]
                txt = a.get_text(strip=True)
                for candidate in (href, txt):
                    if target.lower() in candidate.lower():
                        # extrai possíveis nomes dentro do candidate com regex simples
                        cand_matches = pattern.findall(candidate)
                        for cm in cand_matches:
                            sub = cm.strip().strip('.,;:"\'()[]{}<>')
                            if sub and sub not in subdomains_found:
                                subdomains_found.add(sub)
                                self.subdomainscount += 1
                                try:
                                    write_file(sub, target)
                                except Exception:
                                    pass

        except Exception:
            # falha silenciosa, segue sem interromper
            pass

        # opcional: podes registar o tempo gasto (não escrito em ficheiro aqui)
        elapsed = time.time() - start_time

        self.elapsed = elapsed
        self.subdomains = sorted(subdomains_found)

# ----------------------------------------------------------------------------------------------------------
