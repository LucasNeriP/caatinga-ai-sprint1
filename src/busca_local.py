"""Parte 3.4 - Busca local: escolher quais K talhões inspecionar.

Modelagem:
- Estado: um conjunto de K talhões livres (sem o portão e sem o ponto de coleta).
- Vizinhança: trocar 1 talhão do conjunto por 1 talhão livre fora dele.
- Objetivo (maximizar, em pontos de risco):
      f(S) = soma do risco dos talhões de S
             - PENALIDADE_POR_MINUTO x max(0, tempo(S) - BATERIA_MIN)
  tempo(S) = deslocamento (portão -> talhões de S -> ponto de coleta, na ordem
  do vizinho mais próximo) + K inspeções de MIN_INSPECAO minutos.

O risco de cada talhão é gerado de forma determinística a partir da matrícula:
alguns focos de praga espalham risco para os vizinhos, e o solo encharcado
(`~`) tem risco maior, porque a umidade favorece as pragas. Os focos criam
vários "morros" na função objetivo, e são eles que prendem a subida de encosta.
"""
import heapq
import math
import random
import statistics
import time

from buscas import vizinhos
from gerador_pomar import BLOQUEADO

K = 15
BATERIA_MIN = 6 * 60          # 6 h de bateria
MIN_POR_UNIDADE = 1.0         # 1 unidade de custo de terreno = 1 min de deslocamento
MIN_INSPECAO = 20             # sensor parado em cada talhão; com K=15 sobram 60 min para andar
PENALIDADE_POR_MINUTO = 100.0 # maior que o risco de qualquer talhão: estourar nunca compensa
N_FOCOS = 4                   # focos de praga no pomar
RAIO_FOCO = 2.0               # alcance (em talhões) do espalhamento de cada foco

# Parâmetros da têmpera simulada.
T_INICIAL = 300.0             # alto o bastante para aceitar, no início, trocas que estouram a bateria
RESFRIAMENTO = 0.9995         # T <- T x RESFRIAMENTO a cada iteração
ITERACOES_TEMPERA = 20000


def gerar_riscos(grade, matricula):
    """Risco de praga (0 a 100 pontos) de cada talhão livre, fixo para a semente.

    Semente própria (matrícula + 999) para não mexer na sequência aleatória
    do gerador do pomar nem na do sensor.
    """
    n = len(grade)
    rng = random.Random((matricula % 1_000_000) + 999)
    focos = [(rng.randrange(n), rng.randrange(n)) for _ in range(N_FOCOS)]
    riscos = {}
    for i in range(n):
        for j in range(n):
            if grade[i][j] == BLOQUEADO:
                continue
            # O foco mais próximo domina; um ruído de fundo evita risco zero.
            espalhamento = max(math.exp(-((i - a) ** 2 + (j - b) ** 2) / (2 * RAIO_FOCO ** 2))
                               for a, b in focos)
            base = 15 * rng.random() + 85 * espalhamento
            fator_umidade = 1.3 if grade[i][j] == "~" else 1.0
            riscos[(i, j)] = round(min(100.0, base * fator_umidade), 1)
    return riscos, focos


def distancias_minimas(grade, origens):
    """Custo mínimo (Dijkstra) de cada origem até todos os talhões alcançáveis.

    Pré-calculado uma vez: a função objetivo é avaliada milhares de vezes e
    não pode rodar uma busca a cada avaliação.
    """
    tabela = {}
    for origem in origens:
        dist = {origem: 0}
        heap = [(0, origem)]
        while heap:
            d, estado = heapq.heappop(heap)
            if d > dist[estado]:
                continue
            for viz, custo in vizinhos(grade, estado):
                if d + custo < dist.get(viz, math.inf):
                    dist[viz] = d + custo
                    heapq.heappush(heap, (d + custo, viz))
        tabela[origem] = dist
    return tabela


class Problema:
    """Guarda o pomar, os riscos e as distâncias; avalia estados."""

    def __init__(self, grade, matricula, k=K):
        n = len(grade)
        self.k = k
        self.inicio, self.fim = (0, 0), (n - 1, n - 1)
        self.riscos, self.focos = gerar_riscos(grade, matricula)
        dist = distancias_minimas(grade, [self.inicio])[self.inicio]
        # Só entram talhões alcançáveis a partir do portão; os extremos da rota
        # ficam de fora porque o agente passa por eles de qualquer jeito.
        self.candidatos = sorted(t for t in self.riscos
                                 if t in dist and t not in (self.inicio, self.fim))
        if len(self.candidatos) < k:
            raise ValueError(f"pomar tem só {len(self.candidatos)} talhões livres; K={k}")
        self.dist = distancias_minimas(grade, [self.inicio] + self.candidatos)
        # Minutos que sobram para desvios depois das K inspeções e da rota
        # direta portão -> coleta. Negativo = nenhum conjunto cabe na bateria
        # (acontece em grades maiores que 12x12, para as quais os tempos não
        # foram calibrados).
        self.folga_min = (BATERIA_MIN - k * MIN_INSPECAO
                          - self.dist[self.inicio][self.fim] * MIN_POR_UNIDADE)

    def deslocamento(self, estado):
        """Custo da rota portão -> talhões -> coleta pelo vizinho mais próximo.

        É uma aproximação (resolver a ordem ótima seria um caixeiro-viajante
        dentro de cada avaliação), mas é determinística e rápida.
        """
        # sorted() fixa a ordem de desempate (menor coordenada vence), para o
        # resultado não depender da ordem interna do conjunto.
        restantes = sorted(estado)
        atual, total = self.inicio, 0
        while restantes:
            d = self.dist[atual]
            proximo = min(restantes, key=d.__getitem__)
            total += d[proximo]
            restantes.remove(proximo)
            atual = proximo
        return total + self.dist[atual][self.fim]

    def tempo_min(self, estado):
        return self.deslocamento(estado) * MIN_POR_UNIDADE + len(estado) * MIN_INSPECAO

    def objetivo(self, estado):
        risco = sum(self.riscos[t] for t in estado)
        excesso = max(0.0, self.tempo_min(estado) - BATERIA_MIN)
        return risco - PENALIDADE_POR_MINUTO * excesso

    def estado_aleatorio(self, rng):
        return frozenset(rng.sample(self.candidatos, self.k))

    def vizinhos(self, estado):
        """Todas as trocas 1-por-1: K x (livres - K) vizinhos."""
        fora = [t for t in self.candidatos if t not in estado]
        for sai in sorted(estado):
            for entra in fora:
                yield (estado - {sai}) | {entra}

    def vizinho_aleatorio(self, estado, rng):
        sai = rng.choice(sorted(estado))
        # Sorteia até cair fora do conjunto: com K=15 em ~100 livres, quase
        # sempre acerta de primeira, e é bem mais rápido que montar a lista.
        entra = rng.choice(self.candidatos)
        while entra in estado:
            entra = rng.choice(self.candidatos)
        return (estado - {sai}) | {entra}


def subida_de_encosta(problema, inicial):
    """Subida de encosta pela maior subida (steepest ascent).

    Avalia TODOS os vizinhos e vai para o melhor; para quando nenhum vizinho
    melhora. Nunca aceita piora, então fica presa no primeiro topo que achar.
    """
    atual, valor = inicial, problema.objetivo(inicial)
    passos = 0
    while True:
        melhor, melhor_valor = None, valor
        for viz in problema.vizinhos(atual):
            v = problema.objetivo(viz)
            if v > melhor_valor:
                melhor, melhor_valor = viz, v
        if melhor is None:
            return {"estado": atual, "valor": valor, "passos": passos}
        atual, valor = melhor, melhor_valor
        passos += 1


def tempera_simulada(problema, inicial, rng):
    """Têmpera simulada com resfriamento geométrico.

    Um vizinho aleatório pior é aceito com probabilidade exp(delta / T).
    No começo (T alto) quase toda piora passa, e o agente consegue descer de
    um morro para subir em outro; no fim (T baixo) vira uma subida de encosta.
    Devolve o MELHOR estado visto, não o último.
    """
    atual, valor = inicial, problema.objetivo(inicial)
    melhor, melhor_valor = atual, valor
    t = T_INICIAL
    pioras_aceitas = 0
    for _ in range(ITERACOES_TEMPERA):
        viz = problema.vizinho_aleatorio(atual, rng)
        v = problema.objetivo(viz)
        delta = v - valor
        if delta > 0 or rng.random() < math.exp(delta / t):
            if delta < 0:
                pioras_aceitas += 1
            atual, valor = viz, v
            if valor > melhor_valor:
                melhor, melhor_valor = atual, valor
        t *= RESFRIAMENTO
    return {"estado": melhor, "valor": melhor_valor, "pioras_aceitas": pioras_aceitas}


def experimento(grade, matricula, execucoes=30):
    """Roda as duas buscas `execucoes` vezes, com as sementes 0..execucoes-1.

    Em cada semente, as duas partem do MESMO estado inicial, para a comparação
    ser justa: a diferença vem só do algoritmo.
    """
    problema = Problema(grade, matricula)
    linhas = []
    for semente in range(execucoes):
        rng = random.Random(semente)
        inicial = problema.estado_aleatorio(rng)
        t0 = time.perf_counter()
        se = subida_de_encosta(problema, inicial)
        t_se = (time.perf_counter() - t0) * 1000
        t0 = time.perf_counter()
        ts = tempera_simulada(problema, inicial, rng)
        t_ts = (time.perf_counter() - t0) * 1000
        linhas.append({
            "semente": semente,
            "inicial": round(problema.objetivo(inicial), 1),
            "subida": round(se["valor"], 1),
            "passos_subida": se["passos"],
            "tempera": round(ts["valor"], 1),
            "pioras_aceitas": ts["pioras_aceitas"],
            "tempo_subida_ms": round(t_se, 1),
            "tempo_tempera_ms": round(t_ts, 1),
            "estado_subida": se["estado"],
            "estado_tempera": ts["estado"],
        })
    return problema, linhas


def resumo(valores):
    return {
        "media": statistics.mean(valores),
        "desvio": statistics.stdev(valores),
        "melhor": max(valores),
    }


def imprimir_relatorio(problema, linhas):
    print(f"Candidatos: {len(problema.candidatos)} talhões livres | K = {problema.k} | "
          f"bateria = {BATERIA_MIN} min | focos de praga = {problema.focos}")
    print(f"Folga para desvios: {problema.folga_min:.0f} min "
          f"(bateria - {problema.k} x {MIN_INSPECAO} min - rota direta)")
    if problema.folga_min < 0:
        print("AVISO: nem a rota direta cabe na bateria; todo conjunto será penalizado.")
    print(f"\n{'Semente':>7}{'Inicial':>10}{'Subida':>10}{'Têmpera':>10}"
          f"{'Pioras aceitas':>16}  Quem venceu")
    for l in linhas:
        if l["tempera"] > l["subida"]:
            venceu = "têmpera"
        elif l["tempera"] < l["subida"]:
            venceu = "subida"
        else:
            venceu = "empate"
        print(f"{l['semente']:>7}{l['inicial']:>10.1f}{l['subida']:>10.1f}{l['tempera']:>10.1f}"
              f"{l['pioras_aceitas']:>16}  {venceu}")

    se = resumo([l["subida"] for l in linhas])
    ts = resumo([l["tempera"] for l in linhas])
    print(f"\n{'Algoritmo':<20}{'Média':>10}{'Desvio':>10}{'Melhor':>10}  (pontos de risco)")
    print(f"{'Subida de encosta':<20}{se['media']:>10.1f}{se['desvio']:>10.1f}{se['melhor']:>10.1f}")
    print(f"{'Têmpera simulada':<20}{ts['media']:>10.1f}{ts['desvio']:>10.1f}{ts['melhor']:>10.1f}")

    vitorias = sum(l["tempera"] > l["subida"] for l in linhas)
    derrotas = sum(l["tempera"] < l["subida"] for l in linhas)
    otimos_subida = len({l["estado_subida"] for l in linhas})
    print(f"\nA têmpera superou a subida em {vitorias}/{len(linhas)} execuções "
          f"(perdeu em {derrotas}).")
    escapou = [l["semente"] for l in linhas if l["tempera"] > l["subida"]]
    print(f"Sementes em que a têmpera saiu do ótimo local onde a subida parou: {escapou}")
    print(f"A subida parou em {otimos_subida} ótimos locais diferentes nas "
          f"{len(linhas)} execuções.")
    media_pioras = statistics.mean(l["pioras_aceitas"] for l in linhas)
    print(f"Pioras aceitas pela têmpera: média de {media_pioras:.0f} por execução.")

    melhor = max(linhas, key=lambda l: l["tempera"])["estado_tempera"]
    print(f"\nMelhor conjunto (têmpera): {sorted(melhor)}")
    print(f"  risco total = {sum(problema.riscos[t] for t in melhor):.1f} pontos | "
          f"tempo = {problema.tempo_min(melhor):.0f} min de {BATERIA_MIN}")


if __name__ == "__main__":
    import sys
    from gerador_pomar import gerar_pomar

    matricula = int(sys.argv[1]) if len(sys.argv) > 1 else 20231045
    imprimir_relatorio(*experimento(gerar_pomar(matricula), matricula))
