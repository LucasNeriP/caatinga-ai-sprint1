"""Mede o limite de escala de BFS, DFS e UCS.

Cada busca roda em um processo separado. Isso permite interromper uma execução
que ultrapasse o limite de tempo ou de memória sem deixar o experimento inteiro
travado.

Exemplos:
    python src/experimento_escala.py 24114032
    python src/experimento_escala.py 241.14.032 --max-n 1600
    python src/experimento_escala.py 24114032 --tamanhos 12 40 100
    python src/experimento_escala.py 24114032 --tamanhos 3200 --limite-memoria-percentual 92
    python src/experimento_escala.py 24114032 --saida resultados/escala.csv
"""

import argparse
import csv
import ctypes
import multiprocessing as mp
import sys
import time
import traceback
from pathlib import Path
from queue import Empty

from buscas import bfs, dfs, ucs
from gerador_pomar import gerar_pomar


ESTRATEGIAS = {
    "BFS": bfs,
    "DFS": dfs,
    "UCS": ucs,
}

MEBIBYTE = 1024 * 1024


def matricula_inteira(texto):
    """Aceita a matrícula com ou sem pontos e hífens."""
    normalizada = texto.replace(".", "").replace("-", "").replace(" ", "")
    if not normalizada.isdigit():
        raise argparse.ArgumentTypeError(
            "a matrícula deve conter apenas algarismos, pontos ou hífens"
        )
    return int(normalizada)


def sequencia_de_tamanhos(max_n):
    """Produz 12, 40, 100 e depois dobra até alcançar ``max_n``."""
    if max_n < 2:
        raise ValueError("--max-n deve ser pelo menos 2")

    tamanhos = [n for n in (12, 40, 100) if n <= max_n]
    if not tamanhos:
        return [max_n]

    atual = tamanhos[-1]
    while atual < max_n:
        atual = min(atual * 2, max_n)
        if atual != tamanhos[-1]:
            tamanhos.append(atual)
    return tamanhos


def situacao_memoria_sistema():
    """Retorna (percentual usado, MiB disponíveis, MiB totais).

    Usa somente a biblioteca padrão. O monitoramento está disponível no Windows
    e no Linux; em outros sistemas, retorna três valores ``None``.
    """
    if sys.platform == "win32":
        class MemoryStatusEx(ctypes.Structure):
            _fields_ = [
                ("dwLength", ctypes.c_ulong),
                ("dwMemoryLoad", ctypes.c_ulong),
                ("ullTotalPhys", ctypes.c_ulonglong),
                ("ullAvailPhys", ctypes.c_ulonglong),
                ("ullTotalPageFile", ctypes.c_ulonglong),
                ("ullAvailPageFile", ctypes.c_ulonglong),
                ("ullTotalVirtual", ctypes.c_ulonglong),
                ("ullAvailVirtual", ctypes.c_ulonglong),
                ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
            ]

        memoria = MemoryStatusEx()
        memoria.dwLength = ctypes.sizeof(MemoryStatusEx)
        if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(memoria)):
            return None, None, None
        total = memoria.ullTotalPhys / MEBIBYTE
        disponivel = memoria.ullAvailPhys / MEBIBYTE
        usado = 100.0 * (total - disponivel) / total
        return usado, disponivel, total

    if sys.platform.startswith("linux"):
        try:
            valores = {}
            with Path("/proc/meminfo").open(encoding="ascii") as arquivo:
                for linha in arquivo:
                    nome, valor = linha.split(":", 1)
                    valores[nome] = int(valor.strip().split()[0])
            total = valores["MemTotal"] / 1024
            disponivel = valores["MemAvailable"] / 1024
            usado = 100.0 * (total - disponivel) / total
            return usado, disponivel, total
        except (OSError, KeyError, ValueError):
            return None, None, None

    return None, None, None


def _executar_busca(matricula, n, nome_estrategia, fila):
    """Função executada no processo filho."""
    try:
        inicio_geracao = time.perf_counter()
        grade = gerar_pomar(matricula, n)
        tempo_geracao = time.perf_counter() - inicio_geracao

        inicio_busca = time.perf_counter()
        resultado = ESTRATEGIAS[nome_estrategia](grade)
        tempo_busca = time.perf_counter() - inicio_busca

        fila.put(
            {
                "status": "OK" if resultado.encontrou else "SEM_ROTA",
                "custo": resultado.custo,
                "passos": resultado.passos,
                "nos_expandidos": resultado.nos_expandidos,
                "fronteira_max": resultado.fronteira_max,
                "tempo_geracao_s": tempo_geracao,
                "tempo_busca_s": tempo_busca,
                "detalhe": "",
            }
        )
    except MemoryError:
        fila.put(
            {
                "status": "MEMORIA",
                "detalhe": "MemoryError durante a geração ou a busca",
            }
        )
    except RecursionError:
        fila.put(
            {
                "status": "PILHA",
                "detalhe": "RecursionError durante a execução",
            }
        )
    except BaseException as erro:
        fila.put(
            {
                "status": "ERRO",
                "detalhe": f"{type(erro).__name__}: {erro}\n"
                f"{traceback.format_exc(limit=3)}",
            }
        )


def executar_com_limite(
    matricula,
    n,
    estrategia,
    limite_segundos,
    limite_memoria_percentual,
):
    """Executa isoladamente e encerra ao atingir tempo ou memória."""
    contexto = mp.get_context("spawn")
    fila = contexto.Queue()
    processo = contexto.Process(
        target=_executar_busca,
        args=(matricula, n, estrategia, fila),
    )

    inicio_total = time.perf_counter()
    processo.start()
    prazo = inicio_total + limite_segundos
    motivo_parada = None
    pico_memoria = None
    minimo_disponivel = None

    while processo.is_alive():
        memoria_usada, memoria_disponivel, _ = situacao_memoria_sistema()
        if memoria_usada is not None:
            pico_memoria = max(pico_memoria or 0.0, memoria_usada)
            minimo_disponivel = min(
                minimo_disponivel if minimo_disponivel is not None else float("inf"),
                memoria_disponivel,
            )
            if memoria_usada >= limite_memoria_percentual:
                motivo_parada = "MEMORIA"
                break

        restante = prazo - time.perf_counter()
        if restante <= 0:
            motivo_parada = "TEMPO"
            break
        processo.join(min(0.1, restante))

    if motivo_parada is not None and processo.is_alive():
        processo.terminate()
        processo.join(5)
        if processo.is_alive():
            processo.kill()
            processo.join()

    tempo_total = time.perf_counter() - inicio_total
    if motivo_parada == "TEMPO":
        resultado = {
            "status": "TEMPO",
            "detalhe": f"execução interrompida após {limite_segundos:g} s",
        }
    elif motivo_parada == "MEMORIA":
        resultado = {
            "status": "MEMORIA",
            "detalhe": (
                "execução interrompida porque a memória do sistema atingiu "
                f"{pico_memoria:.1f}% (limite configurado: "
                f"{limite_memoria_percentual:g}%; disponível: "
                f"{minimo_disponivel:.0f} MiB)"
            ),
        }
    else:
        try:
            resultado = fila.get(timeout=2)
        except Empty:
            resultado = {
                "status": "ERRO",
                "detalhe": f"processo terminou com código {processo.exitcode}",
            }

    fila.close()
    fila.join_thread()
    resultado.update(
        {
            "n": n,
            "estrategia": estrategia,
            "tempo_total_s": tempo_total,
            "memoria_sistema_pico_percentual": pico_memoria,
            "memoria_disponivel_min_mib": minimo_disponivel,
            "limite_memoria_percentual": limite_memoria_percentual,
        }
    )
    return resultado


def imprimir_cabecalho():
    print(
        f"{'n':>6}  {'Estratégia':<10} {'Status':<10} {'Custo':>8} "
        f"{'Passos':>8} {'Expandidos':>12} {'Fronteira':>10} "
        f"{'Busca (s)':>10} {'Total (s)':>10} {'Mem.%':>7}"
    )


def imprimir_resultado(resultado):
    def valor(nome):
        dado = resultado.get(nome)
        return "-" if dado is None else str(dado)

    tempo_busca = resultado.get("tempo_busca_s")
    busca_texto = "-" if tempo_busca is None else f"{tempo_busca:.3f}"
    memoria_pico = resultado.get("memoria_sistema_pico_percentual")
    memoria_texto = "-" if memoria_pico is None else f"{memoria_pico:.1f}"
    print(
        f"{resultado['n']:>6}  {resultado['estrategia']:<10} "
        f"{resultado['status']:<10} {valor('custo'):>8} "
        f"{valor('passos'):>8} {valor('nos_expandidos'):>12} "
        f"{valor('fronteira_max'):>10} {busca_texto:>10} "
        f"{resultado['tempo_total_s']:>10.3f} {memoria_texto:>7}"
    )
    if resultado.get("detalhe"):
        print(f"        detalhe: {resultado['detalhe']}")


def salvar_csv(caminho, resultados):
    caminho.parent.mkdir(parents=True, exist_ok=True)
    campos = [
        "n",
        "estrategia",
        "status",
        "custo",
        "passos",
        "nos_expandidos",
        "fronteira_max",
        "tempo_geracao_s",
        "tempo_busca_s",
        "tempo_total_s",
        "memoria_sistema_pico_percentual",
        "memoria_disponivel_min_mib",
        "limite_memoria_percentual",
        "detalhe",
    ]
    with caminho.open("w", newline="", encoding="utf-8") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=campos)
        escritor.writeheader()
        for resultado in resultados:
            escritor.writerow({campo: resultado.get(campo, "") for campo in campos})


def criar_argumentos():
    parser = argparse.ArgumentParser(
        description=(
            "Executa BFS, DFS e UCS em grades crescentes até ocorrer uma falha "
            "ou chegar ao maior tamanho configurado."
        )
    )
    parser.add_argument(
        "matricula",
        type=matricula_inteira,
        help="matrícula-semente, com ou sem pontuação",
    )
    parser.add_argument(
        "--limite-segundos",
        type=float,
        default=60.0,
        help="limite por estratégia (padrão: 60)",
    )
    parser.add_argument(
        "--max-n",
        type=int,
        default=800,
        help="maior dimensão testada na sequência automática (padrão: 800)",
    )
    parser.add_argument(
        "--limite-memoria-percentual",
        type=float,
        default=92.0,
        help="interrompe quando a memória do sistema atingir o percentual (padrão: 92)",
    )
    parser.add_argument(
        "--tamanhos",
        type=int,
        nargs="+",
        help="lista explícita de dimensões; substitui --max-n",
    )
    parser.add_argument(
        "--saida",
        type=Path,
        help="caminho opcional para salvar os resultados em CSV",
    )
    return parser


def main():
    argumentos = criar_argumentos().parse_args()
    if argumentos.limite_segundos <= 0:
        raise SystemExit("--limite-segundos deve ser maior que zero")
    if not 1 <= argumentos.limite_memoria_percentual <= 100:
        raise SystemExit(
            "--limite-memoria-percentual deve estar entre 1 e 100"
        )

    memoria_atual, memoria_disponivel, memoria_total = situacao_memoria_sistema()
    if memoria_atual is None:
        print(
            "AVISO: monitoramento de memória indisponível neste sistema; "
            "somente o limite de tempo será aplicado.\n"
        )
    else:
        print(
            f"Memória antes do experimento: {memoria_atual:.1f}% em uso; "
            f"{memoria_disponivel:.0f} de {memoria_total:.0f} MiB disponíveis.\n"
        )

    if argumentos.tamanhos:
        if any(n < 2 for n in argumentos.tamanhos):
            raise SystemExit("todos os tamanhos devem ser pelo menos 2")
        tamanhos = argumentos.tamanhos
    else:
        tamanhos = sequencia_de_tamanhos(argumentos.max_n)

    resultados = []
    houve_falha = False
    imprimir_cabecalho()
    for n in tamanhos:
        for estrategia in ESTRATEGIAS:
            resultado = executar_com_limite(
                argumentos.matricula,
                n,
                estrategia,
                argumentos.limite_segundos,
                argumentos.limite_memoria_percentual,
            )
            resultados.append(resultado)
            imprimir_resultado(resultado)
            if resultado["status"] != "OK":
                houve_falha = True
                break
        if houve_falha:
            break

    if argumentos.saida:
        salvar_csv(argumentos.saida, resultados)
        print(f"\nResultados salvos em: {argumentos.saida}")

    if houve_falha:
        ultimo = resultados[-1]
        print(
            f"\nPrimeira falha: {ultimo['estrategia']} em n={ultimo['n']} "
            f"({ultimo['status']})."
        )
    else:
        print(
            f"\nNenhuma estratégia falhou até n={tamanhos[-1]}. "
            "Aumente --max-n para continuar o experimento."
        )


if __name__ == "__main__":
    mp.freeze_support()
    main()
