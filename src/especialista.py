"""Partes 4.1 e 4.2 - Mini sistema especialista de manejo de talhão.

- Base de regras SE ... ENTÃO ... (R1 a R7) sobre o manejo de um talhão.
- Encadeamento para TRÁS: parte de uma hipótese ("devo pulverizar?") e desce
  pelas regras até chegar aos fatos informados. Só examina o que é relevante
  para a hipótese, ao contrário do encadeamento para frente, que dispara tudo.
- As hipóteses são testadas em ordem de prioridade; a primeira provada é a
  conclusão. A cadeia de regras que a provou é a resposta ao "por quê?".
- Negação por falha (mundo fechado): "NAO x" é verdadeiro quando x não pode
  ser provado com os fatos informados.
"""
from dataclasses import dataclass

PERIODO_CARENCIA_DIAS = 15  # sem inseticida nos últimos dias antes da colheita


@dataclass(frozen=True)
class Regra:
    nome: str
    condicoes: tuple  # cada condição: ("fato", x) | ("nao", x) | (">", var, valor) | ("<", var, valor)
    conclusao: str
    descricao: str


REGRAS_BASE = [
    Regra("R1", (("fato", "armadilha_positiva"), ("fato", "umidade_alta")),
          "condicao_favoravel_praga",
          "mosca capturada na armadilha e umidade alta favorecem a infestação"),
    Regra("R2", (("fato", "condicao_favoravel_praga"), (">", "dias_desde_pulverizacao", 14)),
          "inspecionar_prioridade_alta",
          "condição favorável e a proteção da última pulverização já passou"),
    Regra("R3", (("fato", "sensor_positivo"), ("fato", "vizinho_infestado")),
          "suspeita_confirmada",
          "o sensor apontou e há infestação confirmada em talhão vizinho"),
    Regra("R4", (("fato", "suspeita_confirmada"), (">", "dias_desde_pulverizacao", 14)),
          "pulverizar",
          "suspeita confirmada e talhão desprotegido"),
    Regra("R5", (("fato", "sensor_positivo"), ("nao", "armadilha_positiva")),
          "inspecionar_prioridade_media",
          "só o sensor apontou: pode ser falso positivo (ver Bayes, Parte 4.3)"),
    Regra("R6", (("fato", "armadilha_positiva"),),
          "monitorar",
          "armadilha positiva isolada: acompanhar nas próximas leituras"),
    Regra("R7", (("fato", "suspeita_confirmada"),),
          "inspecionar_prioridade_alta",
          "suspeita confirmada mesmo com pulverização recente: o tratamento pode ter falhado"),
]

# Parte 4.2 - regra que corrige o caso quebrado (ver CASO_QUEBRADO abaixo).
REGRA_CARENCIA = Regra(
    "R8", (("fato", "suspeita_confirmada"), ("<", "dias_ate_colheita", PERIODO_CARENCIA_DIAS)),
    "manejo_sem_quimico",
    f"suspeita confirmada, mas a colheita está a menos de {PERIODO_CARENCIA_DIAS} dias: "
    "inseticida deixaria resíduo acima do permitido (período de carência)")

# Ordem de prioridade das hipóteses. manejo_sem_quimico vem antes de pulverizar
# porque é o caso MAIS ESPECÍFICO (exige tudo o que R4 exige e mais a colheita
# próxima): a regra específica vence a geral, sem apagar a geral.
HIPOTESES = [
    "manejo_sem_quimico",
    "pulverizar",
    "inspecionar_prioridade_alta",
    "inspecionar_prioridade_media",
    "monitorar",
]
SEM_ACAO = "sem_acao"


def texto_condicao(c):
    if c[0] == "fato":
        return c[1]
    if c[0] == "nao":
        return f"NAO {c[1]}"
    return f"{c[1]} {c[0]} {c[2]}"


def texto_regra(r):
    se = " E ".join(texto_condicao(c) for c in r.condicoes)
    return f"{r.nome}: SE {se} ENTAO {r.conclusao}"


class Motor:
    """Motor de encadeamento para trás que registra o traço de execução."""

    def __init__(self, regras, fatos):
        self.regras = regras
        self.fatos = fatos
        self.traco = []

    def _log(self, nivel, texto):
        self.traco.append("  " * nivel + texto)

    def provar(self, meta, nivel=0, pilha=()):
        """Tenta provar `meta`. Devolve a justificativa (árvore) ou None."""
        # Fato informado diretamente pelo agrônomo/sensores: é folha da árvore.
        if meta in self.fatos:
            ok = bool(self.fatos[meta])
            self._log(nivel, f"{meta}? fato informado = {'sim' if ok else 'não'}")
            return {"meta": meta, "como": "fato"} if ok else None
        # Evita laço infinito se uma regra depender (indiretamente) de si mesma.
        if meta in pilha:
            return None
        regras = [r for r in self.regras if r.conclusao == meta]
        if not regras:
            self._log(nivel, f"{meta}? não informado e nenhuma regra conclui -> falso")
            return None
        for r in regras:
            self._log(nivel, f"{meta}? tentando {texto_regra(r)}")
            filhos = []
            for c in r.condicoes:
                j = self._condicao(c, nivel + 1, pilha + (meta,))
                if j is None:
                    self._log(nivel, f"x {r.nome} falhou em '{texto_condicao(c)}'")
                    break
                filhos.append(j)
            else:
                self._log(nivel, f"v {meta} provado por {r.nome}")
                return {"meta": meta, "como": r.nome, "regra": r, "filhos": filhos}
        return None

    def _condicao(self, c, nivel, pilha):
        if c[0] == "fato":
            return self.provar(c[1], nivel, pilha)
        if c[0] == "nao":
            # Negação por falha: prova x em um motor "silencioso" e inverte.
            sub = Motor(self.regras, self.fatos)
            ok = sub.provar(c[1], 0, pilha) is None
            self._log(nivel, f"NAO {c[1]}? {c[1]} {'não' if ok else ''} pode ser provado -> "
                             f"{'verdadeiro' if ok else 'falso'}")
            return {"meta": f"NAO {c[1]}", "como": "negação"} if ok else None
        op, var, valor = c
        atual = self.fatos.get(var)
        ok = atual is not None and (atual > valor if op == ">" else atual < valor)
        self._log(nivel, f"{var} {op} {valor}? valor informado = {atual} -> {'sim' if ok else 'não'}")
        return {"meta": f"{var} = {atual} {op} {valor}", "como": "fato"} if ok else None


def cadeia_porque(j, nivel=0):
    """Transforma a árvore de justificativa em linhas 'porque ...'."""
    if j["como"] == "fato":
        return ["  " * nivel + f"- {j['meta']} (informado)"]
    if j["como"] == "negação":
        return ["  " * nivel + f"- {j['meta']} (não pôde ser provado: negação por falha)"]
    r = j["regra"]
    linhas = ["  " * nivel + f"- {j['meta']} porque {r.nome} ({r.descricao}):"]
    for f in j["filhos"]:
        linhas += cadeia_porque(f, nivel + 1)
    return linhas


def diagnosticar(fatos, regras=REGRAS_BASE):
    """Testa as hipóteses em ordem de prioridade; a primeira provada vence."""
    motor = Motor(regras, fatos)
    for h in HIPOTESES:
        motor._log(0, f"== Hipótese: {h}")
        j = motor.provar(h, 1)
        if j is not None:
            return h, j, motor.traco
    return SEM_ACAO, None, motor.traco


def explicar(nome_caso, fatos, regras=REGRAS_BASE, mostrar_traco=True):
    conclusao, j, traco = diagnosticar(fatos, regras)
    print(f"\n### Caso {nome_caso}")
    print("Fatos: " + ", ".join(f"{k}={v}" for k, v in fatos.items()))
    if mostrar_traco:
        print("Traço do encadeamento para trás:")
        for linha in traco:
            print("  " + linha)
    print(f"CONCLUSÃO: {conclusao}")
    print("Por que concluí isso?")
    if j is None:
        print("  - nenhuma hipótese de manejo pôde ser provada com os fatos informados")
    else:
        for linha in cadeia_porque(j):
            print("  " + linha)
    return conclusao


# Casos de teste do domínio. Todos informam os mesmos fatos para que a
# comparação antes/depois da R8 seja justa.
def caso(sensor, vizinho, armadilha, umidade, dias_pulv, dias_colheita):
    return {
        "sensor_positivo": sensor,
        "vizinho_infestado": vizinho,
        "armadilha_positiva": armadilha,
        "umidade_alta": umidade,
        "dias_desde_pulverizacao": dias_pulv,
        "dias_ate_colheita": dias_colheita,
    }


CASOS = {
    "A - foco confirmado": caso(True, True, True, True, 20, 60),
    "B - clima favorável": caso(False, False, True, True, 18, 60),
    "C - só o sensor": caso(True, False, False, False, 20, 60),
    "D - armadilha isolada": caso(False, False, True, False, 5, 60),
    "E - talhão limpo": caso(False, False, False, False, 30, 60),
    "F - pulverizado há pouco": caso(True, True, False, False, 7, 60),
}

# Parte 4.2 - caso legítimo que a base classifica errado: mesmo quadro do caso A,
# mas a colheita é daqui a 7 dias. A base manda pulverizar, o que deixaria
# resíduo de inseticida na manga (a do Vale do São Francisco é exportada, e o
# lote pode ser recusado). O certo é manejo sem químico: ensacar/catar frutos,
# isolar o talhão e antecipar a colheita.
CASO_QUEBRADO = ("G - foco perto da colheita", caso(True, True, True, True, 20, 7))


def main():
    print("BASE DE REGRAS (4.1)")
    for r in REGRAS_BASE:
        print("  " + texto_regra(r))

    print("\n" + "=" * 70 + "\nPARTE 4.1 - Diagnósticos com a base original")
    for nome, fatos in CASOS.items():
        explicar(nome, fatos, mostrar_traco=(nome.startswith("A")))

    nome, fatos = CASO_QUEBRADO
    print("\n" + "=" * 70 + "\nPARTE 4.2 - Caso que quebra a base")
    print("\n>>> ANTES (R1-R7):")
    antes = explicar(nome, fatos)
    print(f"\nNova regra: {texto_regra(REGRA_CARENCIA)}")
    print("\n>>> DEPOIS (R1-R8):")
    depois = explicar(nome, fatos, REGRAS_BASE + [REGRA_CARENCIA])

    print("\n" + "=" * 70 + "\nA R8 contradiz alguma regra? Conferência em todos os casos:")
    print(f"  {'Caso':<28}{'Antes (R1-R7)':<30}{'Depois (R1-R8)':<30}")
    mudaram = []
    for n, f in list(CASOS.items()) + [CASO_QUEBRADO]:
        a = diagnosticar(f)[0]
        d = diagnosticar(f, REGRAS_BASE + [REGRA_CARENCIA])[0]
        if a != d:
            mudaram.append(n)
        print(f"  {n:<28}{a:<30}{d:<30}{'  <- mudou' if a != d else ''}")
    print(f"\nCasos que mudaram: {mudaram} ({antes} -> {depois}); "
          "os demais mantêm o diagnóstico.")


if __name__ == "__main__":
    main()
