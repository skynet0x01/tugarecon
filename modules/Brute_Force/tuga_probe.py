# --------------------------------------------------------------------------------------------------
# TugaRecon – Service Probe Module
#
# Este módulo é responsável por:
#   - Testar conectividade HTTP/HTTPS de hosts descobertos
#   - Identificar serviços web ativos
#   - Extrair metadados básicos (status, title, server header)
#   - Classificar hosts como vivos ou mortos
#
# Ele NÃO:
#   - Faz scanning profundo
#   - Analisa vulnerabilidades
#   - Calcula impacto
#   - Decide prioridades
#
# Ele é uma camada de aquisição de dados.
# A inteligência vem depois.
# --------------------------------------------------------------------------------------------------

import asyncio
import httpx
import os
import json
import time
import logging

from modules.Intelligence.probe_connector import convert_services_to_semantic
from utils.tuga_colors import G, Y, R, W

# Desativa logs verbosos do httpx para manter output limpo
logging.getLogger("httpx").disabled = True


class TugaServiceProbe:
    """
    Motor assíncrono de probing HTTP.

    Entrada:
        - Ficheiro com lista de hosts
    Saída:
        - services.json
        - web_hosts.txt
        - dead_hosts.txt
        - semantic_results.json (via conector)

    Este módulo é a ponte entre:
        Recon bruto ➜ Dados estruturados de serviço
    """

    # --------------------------------------------------------------------------------------------------
    def __init__(self, input_file, output_dir, concurrency=50, timeout=6, retries=2, verbose=False):
        """
        Parâmetros:

        input_file   → ficheiro com hosts (subdomínios)
        output_dir   → diretório onde guardar resultados
        concurrency  → número máximo de conexões simultâneas
        timeout      → timeout por pedido HTTP
        retries      → número de tentativas por host
        verbose      → controla output detalhado

        Estruturas internas:
            web_hosts   → hosts com resposta válida
            dead_hosts  → hosts sem resposta
            services    → metadados HTTP por host
        """

        self.input_file = input_file
        self.output_dir = output_dir
        self.concurrency = concurrency
        self.timeout = timeout
        self.retries = retries
        self.verbose = verbose

        self.web_hosts = []
        self.dead_hosts = []
        self.services = []

        os.makedirs(self.output_dir, exist_ok=True)

    # --------------------------------------------------------------------------------------------------
    def load_hosts(self):
        """
        Lê o ficheiro de entrada e extrai os hosts.

        Espera formato simples:
            sub.example.com
            api.example.com

        Retorna:
            Lista de hosts.
        """
        hosts = []
        with open(self.input_file) as f:
            for line in f:
                h = line.strip().split("\t")[0]
                if h:
                    hosts.append(h)
        return hosts

    # --------------------------------------------------------------------------------------------------
    async def probe_host(self, client, host):
        """
        Tenta contactar o host usando:

            1. HTTPS
            2. HTTP (fallback)

        Para cada tentativa:
            - Segue redirecionamentos
            - Extrai status code
            - Extrai título HTML
            - Extrai header 'server'

        Retorna:
            dict com dados do serviço
            ou None se falhar após retries
        """

        for attempt in range(1, self.retries + 2):
            for scheme in ["https", "http"]:
                url = f"{scheme}://{host}"
                try:
                    r = await client.get(url, follow_redirects=True)

                    service = {
                        "host": host,
                        "url": str(r.url),
                        "status": r.status_code,
                        "title": self.extract_title(r.text),
                        "server": r.headers.get("server", ""),
                        "scheme": scheme,
                        "redirected": str(r.url) != url
                    }

                    return service

                except httpx.RequestError:
                    continue

            # Pequena pausa entre tentativas
            await asyncio.sleep(0.05)

        return None

    # --------------------------------------------------------------------------------------------------
    def extract_title(self, html):
        """
        Extrai o conteúdo da tag <title>.

        Implementação simples:
            - Procura substring
            - Não usa parser HTML

        Isto é intencional:
            Rápido > perfeito

        Retorna string vazia se não encontrar.
        """
        if not html:
            return ""

        html_lower = html.lower()
        start = html_lower.find("<title>")
        end = html_lower.find("</title>")

        if start != -1 and end != -1:
            return html[start+7:end].strip()

        return ""

    # --------------------------------------------------------------------------------------------------
    async def run_async(self, hosts):
        """
        Motor principal assíncrono.

        Usa:
            - httpx.AsyncClient
            - Semaphore para limitar concorrência
            - asyncio.as_completed para progresso incremental

        Fluxo:
            - Dispara tarefas
            - Processa resultados conforme terminam
            - Atualiza listas internas
        """

        limits = httpx.Limits(max_connections=self.concurrency)
        timeout = httpx.Timeout(self.timeout)

        async with httpx.AsyncClient(
            limits=limits,
            timeout=timeout,
            verify=False  # ignora problemas de SSL
        ) as client:

            sem = asyncio.Semaphore(self.concurrency)

            async def bound_probe(host):
                async with sem:
                    try:
                        result = await self.probe_host(client, host)
                        return host, result
                    except Exception:
                        return host, None

            tasks = [bound_probe(h) for h in hosts]

            total = len(hosts)
            completed = 0

            for coro in asyncio.as_completed(tasks):
                host, result = await coro
                completed += 1

                if result:
                    self.services.append(result)
                    self.web_hosts.append(host)
                else:
                    self.dead_hosts.append(host)

                # Feedback visual de progresso
                if completed % 10 == 0 or completed == total:
                    print(Y + f"[*] Probing hosts... {completed}/{total}" + W, end="\r")

    # --------------------------------------------------------------------------------------------------
    def save_results(self):
        """
        Guarda resultados no disco:

            services.json   → dados estruturados
            web_hosts.txt   → hosts ativos
            dead_hosts.txt  → hosts inativos
        """

        services_path = os.path.join(self.output_dir, "services.json")
        webhosts_path = os.path.join(self.output_dir, "web_hosts.txt")
        deadhosts_path = os.path.join(self.output_dir, "dead_hosts.txt")

        with open(services_path, "w") as f:
            json.dump(self.services, f, indent=2)

        with open(webhosts_path, "w") as f:
            for h in sorted(set(self.web_hosts)):
                f.write(h + "\n")

        with open(deadhosts_path, "w") as f:
            for h in sorted(set(self.dead_hosts)):
                f.write(h + "\n")

        print(G + f"[+] Saved {len(self.services)} services" + W)

    # --------------------------------------------------------------------------------------------------
    def run(self):
        """
        Método orquestrador.

        Ordem:
            1. Carrega hosts
            2. Executa probing assíncrono
            3. Guarda resultados
            4. Converte para camada semântica (Intelligence layer)

        Este método é a única interface pública do módulo.
        """

        print(Y + "[*] Loading hosts..." + W)
        hosts = self.load_hosts()

        print(Y + f"[*] Probing {len(hosts)} hosts..." + W)

        start = time.time()

        try:
            asyncio.run(self.run_async(hosts))
        except Exception as e:
            print(R + f"[!] Probe crashed: {e}" + W)

        self.save_results()

        # ─────────────────────────────────────────────────────────────
        # Conector semântico
        #
        # Converte services.json em semantic_results.json
        # Isto separa:
        #   Camada de rede (probe)
        #   Camada de inteligência (impacto / análise)
        # ─────────────────────────────────────────────────────────────

        semantic_path = os.path.join(
            os.path.dirname(self.output_dir),
            "semantic_results.json"
        )

        services_path = os.path.join(self.output_dir, "services.json")

        try:
            convert_services_to_semantic(services_path, semantic_path)
            print(G + "[+] Semantic entries generated" + W)
        except Exception as e:
            print(R + f"[!] Failed to generate semantic entries: {e}" + W)

        print(G + f"\n[+] Probe completed in {time.time() - start:.2f}s" + W)
        print(G + f"[+] Alive hosts: {len(self.web_hosts)} | Dead hosts: {len(self.dead_hosts)}" + W)
        print(G + f"[+] Results saved in: {self.output_dir}" + W)
