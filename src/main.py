"""Ponto de entrada único: python src/main.py <matricula> [--completo]

Gera do zero, em resultados/:
- pomar.txt       matrícula-semente na 1ª linha, depois a grade 12x12
- resultados.csv  estrategia,heuristica,custo,passos,nos_expandidos,fronteira_max,tempo_ms
- grafico.png     nós expandidos por estratégia, com eixos rotulados

Com --completo, roda também a busca local (~30 s), o sistema especialista,
o Bayes e o contraexemplo da DFS, imprimindo os resultados no terminal.
"""
import argparse
import csv
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # só gera arquivo; não precisa de janela (funciona sem tela)
import matplotlib.pyplot as plt

from buscas import astar, bfs, dfs, imprimir_tabela, ucs
from gerador_pomar import gerar_pomar

# Caminho relativo ao arquivo, e não à pasta onde o comando foi digitado:
# assim `python src/main.py` e `cd src; python main.py` gravam no mesmo lugar.
RAIZ = Path(__file__).resolve().parent.parent
PASTA_RESULTADOS = RAIZ / "resultados"
COLUNAS_CSV = ["estrategia", "heuristica", "custo", "passos",
               "nos_expandidos", "fronteira_max", "tempo_ms"]

COR_BARRA = "#2a78d6"
COR_TEXTO = "#0b0b0b"
COR_TEXTO_SECUNDARIO = "#52514e"
COR_GRADE = "#e4e3df"


def matricula_inteira(texto):
    """Aceita a matrícula com ou sem pontos e hífens (ex.: 241.14.032)."""
    limpo = texto.replace(".", "").replace("-", "").replace(" ", "")
    if not limpo.isdigit():
        raise argparse.ArgumentTypeError(f"matrícula inválida: {texto!r}")
    return int(limpo)


def rodar_buscas(grade):
    return [
        bfs(grade),
        dfs(grade),
        ucs(grade),
        astar(grade, "h1"),
        astar(grade, "h2"),
        astar(grade, "h3"),
    ]


def salvar_pomar(grade, matricula, caminho):
    linhas = [str(matricula)] + [" ".join(linha) for linha in grade]
    caminho.write_text("\n".join(linhas) + "\n", encoding="utf-8")


def salvar_csv(resultados, caminho):
    with caminho.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(COLUNAS_CSV)
        for r in resultados:
            w.writerow([r.estrategia, r.heuristica, r.custo, r.passos,
                        r.nos_expandidos, r.fronteira_max, f"{r.tempo_ms:.3f}"])


def rotulo(r):
    return r.estrategia if r.heuristica == "-" else f"{r.estrategia} {r.heuristica}"


def salvar_grafico(resultados, matricula, caminho):
    nomes = [rotulo(r) for r in resultados]
    # O custo vai embaixo do nome: expandir menos só vale se a rota não piorar.
    ticks = [f"{n}\ncusto {r.custo}" for n, r in zip(nomes, resultados)]
    valores = [r.nos_expandidos for r in resultados]

    fig, ax = plt.subplots(figsize=(9, 5), dpi=150)
    barras = ax.bar(ticks, valores, width=0.6, color=COR_BARRA, zorder=2)
    # Poucas barras e uma imagem estática (sem tooltip): o número acima de
    # cada barra faz o papel da tabela.
    for b, v in zip(barras, valores):
        ax.annotate(str(v), (b.get_x() + b.get_width() / 2, v), xytext=(0, 4),
                    textcoords="offset points", ha="center", va="bottom",
                    fontsize=9, color=COR_TEXTO)

    ax.set_title(f"Nós expandidos por estratégia de busca - pomar da matrícula {matricula}",
                 loc="left", fontsize=11, color=COR_TEXTO)
    ax.set_xlabel("Estratégia de busca (custo da rota em unidades de custo de terreno)",
                  color=COR_TEXTO_SECUNDARIO)
    ax.set_ylabel("Nós expandidos (quantidade de nós)", color=COR_TEXTO_SECUNDARIO)
    ax.set_ylim(0, max(valores) * 1.15)
    ax.grid(axis="y", color=COR_GRADE, linewidth=0.8, zorder=0)
    for lado in ("top", "right"):
        ax.spines[lado].set_visible(False)
    for lado in ("left", "bottom"):
        ax.spines[lado].set_color(COR_GRADE)
    ax.tick_params(colors=COR_TEXTO_SECUNDARIO, labelsize=9)
    fig.tight_layout()
    fig.savefig(caminho)
    plt.close(fig)


def rodar_extras(grade, matricula):
    """Partes 3.4, 4.1-4.3 e bônus, só impressas no terminal."""
    import bayes
    import busca_local
    import contraexemplo_dfs
    import especialista

    secoes = [
        ("PARTE 3.4 - BUSCA LOCAL",
         lambda: busca_local.imprimir_relatorio(*busca_local.experimento(grade, matricula))),
        ("BÔNUS - CONTRAEXEMPLO DA DFS", contraexemplo_dfs.main),
        ("PARTES 4.1 E 4.2 - SISTEMA ESPECIALISTA", especialista.main),
        ("PARTE 4.3 - BAYES", lambda: bayes.imprimir(matricula)),
    ]
    for titulo, rodar in secoes:
        print("\n" + "#" * 70 + f"\n# {titulo}\n" + "#" * 70)
        rodar()


def main():
    parser = argparse.ArgumentParser(description="Caatinga.AI - Sprint 1")
    parser.add_argument("matricula", type=matricula_inteira,
                        help="matrícula-semente (com ou sem pontos)")
    parser.add_argument("--completo", action="store_true",
                        help="roda também busca local, especialista, Bayes e contraexemplo")
    args = parser.parse_args()

    grade = gerar_pomar(args.matricula)
    resultados = rodar_buscas(grade)

    PASTA_RESULTADOS.mkdir(exist_ok=True)
    arquivos = {
        "pomar.txt": lambda p: salvar_pomar(grade, args.matricula, p),
        "resultados.csv": lambda p: salvar_csv(resultados, p),
        "grafico.png": lambda p: salvar_grafico(resultados, args.matricula, p),
    }
    for nome, salvar in arquivos.items():
        salvar(PASTA_RESULTADOS / nome)

    print(f"Matrícula-semente: {args.matricula}\n")
    for linha in grade:
        print("  " + " ".join(linha))
    print()
    imprimir_tabela(resultados)
    otimo = next(r.custo for r in resultados if r.estrategia == "UCS")
    print(f"\nCusto ótimo (UCS): {otimo}. Estratégias que acharam o ótimo: "
          + ", ".join(rotulo(r) for r in resultados if r.custo == otimo))
    print(f"\nArquivos gerados em {PASTA_RESULTADOS}:")
    for nome in arquivos:
        print(f"  - {nome}")

    if args.completo:
        rodar_extras(grade, args.matricula)


if __name__ == "__main__":
    sys.exit(main())
