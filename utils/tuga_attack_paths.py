# ----------------------------------------------------------------------------------------------------------
# TugaRecon – Attacks path
# Module utils/tuga_attack_paths.py
#
# Este módulo é responsável por:
#   1) Guardar os attack paths em JSON estruturado
#   2) Gerar um resumo textual legível para humanos
#
# Não faz análise, não calcula risco, não valida nada.
# Apenas persiste os dados para posterior utilização.
# ----------------------------------------------------------------------------------------------------------

import json      # Usado para serializar estruturas Python para formato JSON
import os        # Usado para manipulação segura de caminhos e diretórios

def save_attack_paths(attack_paths, base_dir):
    """
    Guarda os caminhos de ataque inferidos em formato JSON puro.

    Parâmetros:
        attack_paths (dict ou list):
            Estrutura contendo os caminhos de ataque já calculados
            por outro módulo (ex: análise semântica / impacto).

        base_dir (str):
            Diretório base onde os resultados do target estão guardados.

    Retorna:
        path (str):
            Caminho completo para o ficheiro JSON criado.
    """

    # Define diretório onde os dados da superfície de ataque serão guardados.
    # Estrutura final esperada:
    # base_dir/
    #   └── attack_surface/
    out_dir = os.path.join(base_dir, "attack_surface")

    # Cria o diretório caso não exista.
    # exist_ok=True evita erro se já estiver criado.
    os.makedirs(out_dir, exist_ok=True)

    # Define o caminho final do ficheiro JSON.
    path = os.path.join(out_dir, "attack_paths.json")

    # Abre o ficheiro em modo escrita.
    # "w" sobrescreve se já existir.
    with open(path, "w") as f:

        # Converte a estrutura Python (dict/list) para JSON formatado.
        # indent=2 melhora legibilidade para humanos.
        json.dump(attack_paths, f, indent=2)

    # Retorna o caminho do ficheiro criado
    # Permite que outros módulos saibam onde foi salvo.
    return path

# ----------------------------------------------------------------------------------------------------------
# Função de geração de resumo legível
# ----------------------------------------------------------------------------------------------------------

def generate_attack_path_summary(attack_paths, base_dir):
    """
    Gera um ficheiro de resumo legível para humanos baseado nos caminhos de ataque.

    Esta função não calcula caminhos nem valida nada.
    Apenas transforma dados estruturados (JSON/dict) em texto interpretável.

    Parâmetros:
        attack_paths (list):
            Lista de dicionários contendo:
                - path (lista de etapas)
                - total_cost
                - final_impact
                - confidence (pode ser string "LOW"/"MEDIUM"/"HIGH"/"CRITICAL" ou número 0-1)
        base_dir (str):
            Diretório base onde os resultados do target estão guardados.

    Retorna:
        path (str):
            Caminho completo do ficheiro de resumo criado.
    """

    import os

    # Define o diretório onde será guardada a informação
    out_dir = os.path.join(base_dir, "attack_surface")
    os.makedirs(out_dir, exist_ok=True)  # Garante que o diretório existe

    # Caminho final do ficheiro de resumo
    path = os.path.join(out_dir, "attack_path_summary.txt")

    # Caso não existam caminhos plausíveis
    if not attack_paths:
        with open(path, "w") as f:
            f.write("No plausible attack paths identified.\n")
        return path

    # Mapeamento de strings de confiança para percentagens
    confidence_map = {
        "LOW": 25,
        "MEDIUM": 50,
        "HIGH": 75,
        "CRITICAL": 100
    }

    with open(path, "w") as f:

        # Cabeçalho do relatório
        f.write("=== TugaRecon – Plausible Attack Paths Report ===\n\n")

        # Itera sobre cada caminho
        for i, ap in enumerate(attack_paths, 1):

            # Valores seguros com fallback
            steps = ap.get("path", [])
            total_cost = ap.get("total_cost", "N/A")
            impact = ap.get("final_impact", "UNKNOWN")
            raw_confidence = ap.get("confidence", "LOW")  # Pode ser string ou número

            # Processa confidence
            if isinstance(raw_confidence, str):
                # Converte string para percentagem via mapeamento
                confidence_percent = confidence_map.get(raw_confidence.upper(), 0)
            elif isinstance(raw_confidence, (int, float)):
                # Se for número, assume 0-1 e converte para percentagem
                confidence_percent = round(raw_confidence * 100)
            else:
                confidence_percent = 0  # fallback seguro

            # Define ponto de entrada e alvo final
            entry = steps[0] if steps else "N/A"
            pivot = steps[-1] if len(steps) > 1 else entry

            # Bloco principal
            f.write(f"[PATH {i}]\n")
            f.write(f"Entry Point      : {entry}\n")
            f.write(f"Final Target     : {pivot}\n")
            f.write(f"Risk Level       : {impact}\n")
            f.write(f"Estimated Cost   : {total_cost}\n")
            f.write(f"Confidence       : {confidence_percent}%\n\n")

            # Narrativa adaptativa baseada no impacto
            f.write("Narrative:\n")
            if impact in ("CRITICAL", "HIGH"):
                f.write(
                    f"Exposure of '{entry}' may allow lateral movement "
                    f"towards '{pivot}', potentially leading to significant impact.\n"
                )
            elif impact == "MEDIUM":
                f.write(
                    f"Compromise of '{entry}' could facilitate partial access "
                    f"to '{pivot}', with moderate operational impact.\n"
                )
            else:
                f.write(
                    f"The path starting at '{entry}' appears to have limited "
                    f"impact based on current evidence.\n"
                )

            # Separador visual
            f.write("\n" + "-" * 60 + "\n\n")

    # Retorna o caminho do ficheiro criado
    return path

