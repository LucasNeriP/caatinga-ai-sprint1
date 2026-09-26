"""Parte 4.3 - Bayes com os parâmetros do sensor da nossa semente.

P(I)       = prevalência (fração de talhões infestados)
P(+|I)     = sensibilidade
P(+|nao I) = taxa de falso positivo  (= 1 - especificidade)

Bayes:  P(I|+) = P(+|I) P(I) / [ P(+|I) P(I) + P(+|nao I) P(nao I) ]

Quando a praga é rara, o segundo termo do denominador (falsos positivos vindos
da grande massa de talhões sadios) domina, e o VPP fica baixo mesmo com
sensibilidade alta. É isso que os números abaixo mostram.
"""
from gerador_pomar import parametros_sensor

MIN_POR_INSPECAO = 12


def vpp(prevalencia, sensibilidade, taxa_fp):
    """Valor preditivo positivo: P(infestado | sensor positivo)."""
    verdadeiros = sensibilidade * prevalencia
    falsos = taxa_fp * (1 - prevalencia)
    return verdadeiros / (verdadeiros + falsos)


def vpp_dois_positivos(prevalencia, sensibilidade, taxa_fp):
    """P(I | dois positivos seguidos), SUPONDO testes independentes dado o estado.

    Na prática o mesmo sensor no mesmo talhão tende a errar do mesmo jeito
    (mesma folha manchada, mesma luz), então os erros são correlacionados e o
    valor real fica ABAIXO deste. Este número é um teto otimista.
    """
    return vpp(prevalencia, sensibilidade ** 2, taxa_fp ** 2)


def calcular(matricula):
    p = parametros_sensor(matricula)
    prev, sens, fp, semana = (p["prevalencia"], p["sensibilidade"],
                              p["taxa_falso_positivo"], p["talhoes_por_semana"])
    r = {"parametros": p}
    r["vpp"] = vpp(prev, sens, fp)
    r["falsos_em_100"] = 100 * (1 - r["vpp"])
    r["alertas_semana"] = semana * (sens * prev + fp * (1 - prev))
    r["falsos_semana"] = semana * fp * (1 - prev)
    r["horas_falsas_semana"] = r["falsos_semana"] * MIN_POR_INSPECAO / 60
    r["vpp_sens_999"] = vpp(prev, 0.999, fp)
    r["vpp_fp_metade"] = vpp(prev, sens, fp / 2)
    r["vpp_fp_1pct"] = vpp(prev, sens, 0.01)
    r["vpp_dois_positivos"] = vpp_dois_positivos(prev, sens, fp)
    return r


def imprimir(matricula):
    r = calcular(matricula)
    p = r["parametros"]
    prev, sens, fp, semana = (p["prevalencia"], p["sensibilidade"],
                              p["taxa_falso_positivo"], p["talhoes_por_semana"])
    print(f"parametros_sensor({matricula}) = {p}\n")

    print("(a) P(infestado | sensor positivo)")
    print("    = P(+|I) P(I) / [P(+|I) P(I) + P(+|nao I) P(nao I)]")
    print(f"    = {sens} x {prev} / [{sens} x {prev} + {fp} x {1 - prev:.4f}]")
    print(f"    = {sens * prev:.6f} / [{sens * prev:.6f} + {fp * (1 - prev):.6f}]")
    print(f"    = {sens * prev:.6f} / {sens * prev + fp * (1 - prev):.6f}")
    print(f"    = {r['vpp']:.4f}  ({r['vpp']:.1%})\n")

    print(f"(b) A cada 100 alertas do meu sistema, cerca de {r['falsos_em_100']:.0f} serão falsos.\n")

    print(f"(c) Com {semana} talhões inspecionados por semana:")
    print(f"    alertas totais  = {semana} x ({sens} x {prev} + {fp} x {1 - prev:.4f}) "
          f"= {r['alertas_semana']:.1f} por semana")
    print(f"    alertas falsos  = {semana} x {fp} x {1 - prev:.4f} "
          f"= {r['falsos_semana']:.1f} por semana")
    print(f"    tempo perdido   = {r['falsos_semana']:.1f} x {MIN_POR_INSPECAO} min / 60 "
          f"= {r['horas_falsas_semana']:.1f} horas por semana\n")

    print("(d) Sensibilidade 99,9% com a mesma taxa de falso positivo:")
    print(f"    VPP = 0.999 x {prev} / [0.999 x {prev} + {fp} x {1 - prev:.4f}] "
          f"= {r['vpp_sens_999']:.4f}  ({r['vpp_sens_999']:.1%})")
    print(f"    Ganho: {r['vpp']:.1%} -> {r['vpp_sens_999']:.1%} "
          f"(+{100 * (r['vpp_sens_999'] - r['vpp']):.1f} ponto percentual). Quase nada.")
    print(f"    Mexendo na taxa de falso positivo (mantendo sensibilidade {sens}):")
    print(f"      FP {fp} -> {fp / 2}: VPP = {r['vpp_fp_metade']:.1%}")
    print(f"      FP {fp} -> 0.01: VPP = {r['vpp_fp_1pct']:.1%}\n")

    print("(extra, para a auditoria) Dois positivos seguidos no mesmo talhão,")
    print("    SUPONDO independência: P(++|I) = sens², P(++|nao I) = FP²")
    print(f"    VPP = {sens}² x {prev} / [{sens}² x {prev} + {fp}² x {1 - prev:.4f}] "
          f"= {r['vpp_dois_positivos']:.4f}  ({r['vpp_dois_positivos']:.1%})")
    print("    (teto otimista: erros do mesmo sensor no mesmo talhão são correlacionados)")
    return r


if __name__ == "__main__":
    import sys

    imprimir(int(sys.argv[1]) if len(sys.argv) > 1 else 20231045)
