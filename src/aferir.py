"""Confere as buscas com a caixa de aferição do enunciado.

Use a matrícula fictícia 20231045 antes de rodar a semente da dupla. Custo e
passos precisam coincidir exatamente; nós expandidos admitem a variação de
20% indicada no enunciado por causa do desempate da fila de prioridade.
"""

from buscas import bfs, ucs
from gerador_pomar import gerar_pomar


MATRICULA_AFERICAO = 20231045


def conferir(nome, obtido, esperado, tolerancia=0.0):
    limite = tolerancia * abs(esperado)
    ok = abs(obtido - esperado) <= limite
    faixa = f" (±{tolerancia:.0%})" if tolerancia else ""
    situacao = "OK" if ok else "FALHOU"
    print(
        f"[{situacao}] {nome}: obtido {obtido}, "
        f"esperado {esperado}{faixa}"
    )
    return ok


def main():
    grade = gerar_pomar(MATRICULA_AFERICAO)
    r_bfs = bfs(grade)
    r_ucs = ucs(grade)
    verificacoes = [
        conferir("Custo ótimo (UCS)", r_ucs.custo, 34),
        conferir("Custo da rota da BFS", r_bfs.custo, 55),
        conferir("Passos da rota da BFS", r_bfs.passos, 22),
        conferir(
            "Nós expandidos pelo UCS",
            r_ucs.nos_expandidos,
            112,
            0.20,
        ),
    ]
    return all(verificacoes)


if __name__ == "__main__":
    raise SystemExit(0 if main() else 1)
