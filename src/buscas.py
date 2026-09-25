"""Buscas sobre o pomar: BFS, DFS, UCS e A*.

Convenções usadas em TODAS as estratégias:
- Estado = coordenada (linha, coluna). Nó = estado + pai + custo acumulado.
- Ordem de expansão dos vizinhos: Norte, Sul, Oeste, Leste.
- Custo do caminho = soma do custo dos talhões ENTRADOS (o inicial não conta).
- Contadores: custo, passos, nós expandidos e fronteira máxima (o MAIOR
  tamanho que a fronteira atingiu durante a execução, não o final).
"""
import time
from collections import deque
from dataclasses import dataclass, field
from heapq import heappop, heappush
from itertools import count

from gerador_pomar import BLOQUEADO, CUSTO

# (delta_linha, delta_coluna) na ordem declarada: N, S, O, L.
# Linha 0 fica no topo da grade, por isso Norte é linha - 1.
DIRECOES = [(-1, 0), (1, 0), (0, -1), (0, 1)]

# h1 não estima custo; h2 usa Manhattan; h3 multiplica Manhattan por 4.
MULTIPLICADORES_HEURISTICA = {"h1": 0, "h2": 1, "h3": 4}


@dataclass
class Resultado:
    estrategia: str
    heuristica: str = "-"
    caminho: list = field(default_factory=list)  # lista de estados, do início ao objetivo
    custo: int | None = None
    passos: int | None = None
    nos_expandidos: int = 0
    fronteira_max: int = 0
    tempo_ms: float = 0.0

    @property
    def encontrou(self):
        return bool(self.caminho)


def vizinhos(grade, estado):
    """Gera (vizinho, custo_de_entrar) na ordem N, S, O, L, pulando '#' e bordas."""
    n = len(grade)
    i, j = estado
    for di, dj in DIRECOES:
        a, b = i + di, j + dj
        if 0 <= a < n and 0 <= b < n and grade[a][b] != BLOQUEADO:
            yield (a, b), CUSTO[grade[a][b]]


def custo_do_caminho(grade, caminho):
    # O talhão inicial não é contado, por isso começamos do índice 1.
    return sum(CUSTO[grade[i][j]] for i, j in caminho[1:])


def reconstruir(pais, objetivo):
    # Guardamos só o pai de cada estado (e não o caminho inteiro em cada nó)
    # para a memória crescer com o número de estados, não com o comprimento da rota.
    caminho = [objetivo]
    while pais[caminho[-1]] is not None:
        caminho.append(pais[caminho[-1]])
    caminho.reverse()
    return caminho


def _finalizar(res, grade, pais, objetivo, t0):
    res.tempo_ms = (time.perf_counter() - t0) * 1000
    if objetivo is not None:
        res.caminho = reconstruir(pais, objetivo)
        res.custo = custo_do_caminho(grade, res.caminho)
        res.passos = len(res.caminho) - 1
    return res


def bfs(grade, inicio=(0, 0), objetivo=None):
    """Busca em largura em grafo, com teste de objetivo na GERAÇÃO.

    Testar na geração é seguro na BFS porque ela já garante o menor número de
    passos: o primeiro nó gerado com o objetivo está na camada mais rasa.
    Isso poupa expandir a camada inteira do objetivo.
    """
    n = len(grade)
    objetivo = objetivo or (n - 1, n - 1)
    t0 = time.perf_counter()
    res = Resultado("BFS")

    pais = {inicio: None}  # também serve de conjunto de "alcançados"
    if inicio == objetivo:
        return _finalizar(res, grade, pais, objetivo, t0)

    fronteira = deque([inicio])  # FIFO: o mais antigo sai primeiro
    res.fronteira_max = 1
    while fronteira:
        estado = fronteira.popleft()
        res.nos_expandidos += 1
        for viz, _ in vizinhos(grade, estado):
            # Marcamos ao GERAR: assim o mesmo estado nunca entra duas vezes
            # na fila, o que mantém a fronteira pequena e evita laços.
            if viz in pais:
                continue
            pais[viz] = estado
            if viz == objetivo:
                return _finalizar(res, grade, pais, objetivo, t0)
            fronteira.append(viz)
        res.fronteira_max = max(res.fronteira_max, len(fronteira))
    return _finalizar(res, grade, pais, None, t0)


def dfs(grade, inicio=(0, 0), objetivo=None):
    """Busca em profundidade ITERATIVA (pilha explícita), em grafo.

    - Pilha explícita em vez de recursão: o Python limita a recursão a ~1000
      chamadas, e uma rota em grade grande passa disso fácil (ver Parte 2.4).
    - Os vizinhos são empilhados em ordem INVERSA (L, O, S, N) para que o
      Norte fique no topo e seja o primeiro a ser expandido, respeitando a
      ordem declarada N, S, O, L.
    - O estado é marcado como explorado ao ser EXPANDIDO (não ao ser gerado).
      É isso que dá o comportamento "profundo" de verdade: se um estado for
      reencontrado por um caminho mais fundo, a versão mais recente (topo da
      pilha) é a que vale. Por isso a pilha pode ter duplicatas, e elas
      contam no tamanho da fronteira.
    - Teste de objetivo na expansão, junto com a marcação.
    """
    n = len(grade)
    objetivo = objetivo or (n - 1, n - 1)
    t0 = time.perf_counter()
    res = Resultado("DFS")

    pais = {}
    explorados = set()  # estados já expandidos: é o que impede o laço infinito
    pilha = [(inicio, None)]  # (estado, pai): o pai viaja junto porque só é fixado ao expandir
    res.fronteira_max = 1
    while pilha:
        estado, pai = pilha.pop()  # LIFO: o mais novo sai primeiro
        if estado in explorados:
            continue  # duplicata antiga de um estado já expandido
        explorados.add(estado)
        pais[estado] = pai
        if estado == objetivo:
            return _finalizar(res, grade, pais, objetivo, t0)
        res.nos_expandidos += 1
        for viz, _ in reversed(list(vizinhos(grade, estado))):
            if viz not in explorados:
                pilha.append((viz, estado))
        res.fronteira_max = max(res.fronteira_max, len(pilha))
    return _finalizar(res, grade, pais, None, t0)


def ucs(grade, inicio=(0, 0), objetivo=None):
    """Busca de custo uniforme em grafo, com reabertura de estados.

    A fronteira guarda ``(custo, ordem_de_insercao, estado)``. O segundo campo
    torna o desempate reproduzível e preserva a ordem N, S, O, L entre nós de
    mesmo custo. Um estado volta à fronteira quando aparece um caminho mais
    barato; entradas antigas ficam obsoletas e são ignoradas ao sair da fila.

    O objetivo é aceito ao ser removido da fila de prioridade. Com custos de
    entrada positivos, esse é o momento em que a UCS garante que o menor custo
    até ele foi encontrado.
    """
    n = len(grade)
    objetivo = objetivo or (n - 1, n - 1)
    t0 = time.perf_counter()
    res = Resultado("UCS")

    desempate = count()
    fronteira = [(0, next(desempate), inicio)]
    melhor_custo = {inicio: 0}
    custo_expandido = {}
    pais = {inicio: None}
    res.fronteira_max = 1

    while fronteira:
        custo, _, estado = heappop(fronteira)

        # Uma melhoria posterior pode deixar entradas antigas na heap.
        if custo != melhor_custo.get(estado):
            continue
        anterior = custo_expandido.get(estado)
        if anterior is not None and custo >= anterior:
            continue

        if estado == objetivo:
            return _finalizar(res, grade, pais, objetivo, t0)

        custo_expandido[estado] = custo
        res.nos_expandidos += 1
        for viz, custo_entrada in vizinhos(grade, estado):
            novo_custo = custo + custo_entrada
            if novo_custo >= melhor_custo.get(viz, float("inf")):
                continue
            melhor_custo[viz] = novo_custo
            pais[viz] = estado
            heappush(fronteira, (novo_custo, next(desempate), viz))
        res.fronteira_max = max(res.fronteira_max, len(fronteira))

    return _finalizar(res, grade, pais, None, t0)


def distancia_manhattan(estado, objetivo):
    """Distância ortogonal entre duas coordenadas da grade."""
    return abs(estado[0] - objetivo[0]) + abs(estado[1] - objetivo[1])


def astar(grade, heuristica="h2", inicio=(0, 0), objetivo=None):
    """Busca A* em grafo, com reabertura e três heurísticas do enunciado.

    A prioridade é ``f(n) = g(n) + h(n)``. ``g`` é o custo real já percorrido
    e ``h`` é Manhattan multiplicada por 0 (h1), 1 (h2) ou 4 (h3).

    Quando surge um caminho mais barato para um estado, ele entra novamente na
    fila. Entradas antigas são descartadas ao sair da heap. O contador de
    inserção resolve empates em ordem FIFO e mantém o resultado reproduzível.
    """
    if heuristica not in MULTIPLICADORES_HEURISTICA:
        opcoes = ", ".join(MULTIPLICADORES_HEURISTICA)
        raise ValueError(f"heurística inválida: {heuristica!r}; use {opcoes}")

    n = len(grade)
    objetivo = objetivo or (n - 1, n - 1)
    multiplicador = MULTIPLICADORES_HEURISTICA[heuristica]
    t0 = time.perf_counter()
    res = Resultado("A*", heuristica)

    def estimativa(estado):
        return multiplicador * distancia_manhattan(estado, objetivo)

    desempate = count()
    fronteira = [(estimativa(inicio), next(desempate), 0, inicio)]
    melhor_custo = {inicio: 0}
    custo_expandido = {}
    pais = {inicio: None}
    res.fronteira_max = 1

    while fronteira:
        _, _, custo, estado = heappop(fronteira)

        # Ignora uma entrada que ficou obsoleta após uma melhoria de custo.
        if custo != melhor_custo.get(estado):
            continue
        anterior = custo_expandido.get(estado)
        if anterior is not None and custo >= anterior:
            continue

        if estado == objetivo:
            return _finalizar(res, grade, pais, objetivo, t0)

        custo_expandido[estado] = custo
        res.nos_expandidos += 1
        for viz, custo_entrada in vizinhos(grade, estado):
            novo_custo = custo + custo_entrada
            if novo_custo >= melhor_custo.get(viz, float("inf")):
                continue
            melhor_custo[viz] = novo_custo
            pais[viz] = estado
            prioridade = novo_custo + estimativa(viz)
            heappush(
                fronteira,
                (prioridade, next(desempate), novo_custo, viz),
            )
        res.fronteira_max = max(res.fronteira_max, len(fronteira))

    return _finalizar(res, grade, pais, None, t0)


def imprimir_tabela(resultados):
    print(f"{'Estratégia':<12}{'Custo':>7}{'Passos':>8}{'Expandidos':>12}"
          f"{'Fronteira máx.':>16}{'Tempo (ms)':>12}")
    for r in resultados:
        nome = r.estrategia if r.heuristica == "-" else f"{r.estrategia} {r.heuristica}"
        print(f"{nome:<12}{str(r.custo):>7}{str(r.passos):>8}{r.nos_expandidos:>12}"
              f"{r.fronteira_max:>16}{r.tempo_ms:>12.2f}")


if __name__ == "__main__":
    import sys
    from gerador_pomar import gerar_pomar

    matricula = int(sys.argv[1]) if len(sys.argv) > 1 else 20231045
    grade = gerar_pomar(matricula)
    imprimir_tabela(
        [
            bfs(grade),
            dfs(grade),
            ucs(grade),
            astar(grade, "h1"),
            astar(grade, "h2"),
            astar(grade, "h3"),
        ]
    )
