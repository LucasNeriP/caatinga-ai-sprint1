"""Bônus - contraexemplo construído à mão para a DFS (ordem N, S, O, L).

Ideia da construção:
- A partir do portão (0, 0) só existem duas saídas: Sul (1, 0) e Leste (0, 1).
  Norte e Oeste estão fora da grade.
- Como a ordem declarada é N, S, O, L, a DFS SEMPRE tenta o Sul antes do Leste.
- O miolo do pomar é bloqueado (#), então quem entra por um lado tem de dar a
  volta inteira por ele: não há como "corrigir" o rumo no meio do caminho.
- Colocamos solo encharcado (~, custo 4) no lado Sul/Oeste, que a DFS escolhe,
  e carreador firme (., custo 1) no lado Norte/Leste, que a DFS nunca olha.
- A DFS devolve o PRIMEIRO caminho que encontra e não compara custos. Como o
  Sul vem antes do Leste, ela desce pelo lado caro e chega ao objetivo sem
  jamais expandir o lado barato.

Em cada talhão do lado caro, o único vizinho novo é o próximo da volta
(o Norte ou é o talhão de onde viemos ou é '#'), então a ordem N, S, O, L não
dá à DFS nenhuma chance de desviar.
"""
from buscas import custo_do_caminho, dfs, ucs

POMAR_CONTRAEXEMPLO = [
    ". . . . . . . .",
    "~ # # # # # # .",
    "~ # # # # # # .",
    "~ # # # # # # .",
    "~ # # # # # # .",
    "~ # # # # # # .",
    "~ # # # # # # .",
    "~ ~ ~ ~ ~ ~ ~ .",
]


def montar_grade(linhas=POMAR_CONTRAEXEMPLO):
    return [linha.split() for linha in linhas]


def desenhar(grade, caminho, marca):
    """Imprime a grade com a rota marcada; ajuda a ver o 'U' que a DFS faz."""
    na_rota = set(caminho)
    for i, linha in enumerate(grade):
        print("  " + " ".join(marca if (i, j) in na_rota else c for j, c in enumerate(linha)))


def main():
    grade = montar_grade()
    r_dfs, r_ucs = dfs(grade), ucs(grade)

    print("Pomar 8x8 construído (. custo 1 | ~ custo 4 | # bloqueado):")
    desenhar(grade, [], "")
    print(f"\nRota da DFS (ordem N, S, O, L) - marcada com D:")
    desenhar(grade, r_dfs.caminho, "D")
    print(f"  {r_dfs.caminho}")
    print(f"  custo = {r_dfs.custo} | passos = {r_dfs.passos} | expandidos = {r_dfs.nos_expandidos}")
    print(f"\nRota ótima (UCS) - marcada com U:")
    desenhar(grade, r_ucs.caminho, "U")
    print(f"  {r_ucs.caminho}")
    print(f"  custo = {r_ucs.custo} | passos = {r_ucs.passos} | expandidos = {r_ucs.nos_expandidos}")

    # Conferência independente: recalcula o custo a partir da rota devolvida.
    assert custo_do_caminho(grade, r_dfs.caminho) == r_dfs.custo
    razao = r_dfs.custo / r_ucs.custo
    print(f"\nCusto DFS / custo ótimo = {r_dfs.custo} / {r_ucs.custo} = {razao:.2f}")
    print("Maior que o dobro do ótimo?", "SIM" if r_dfs.custo > 2 * r_ucs.custo else "NÃO")


if __name__ == "__main__":
    main()
