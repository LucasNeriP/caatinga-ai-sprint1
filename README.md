# Caatinga.AI - Sprint 1

## 1. Identificação

- **Disciplina:** Inteligência Artificial - Prof. Ronierison Maciel - UniRios
- **Período:** 2026.2
- **Integrante:** Lucas Neri - matrícula 241.14.032
- **Integrante:** Paulo de Lima - matrícula 241.14.009
- **Matrícula usada como semente:** `24114032` (integrante mais velho: Lucas Neri)

## 2. O que este projeto faz

O Caatinga.AI é um agente que atravessa um pomar de manga de 12 x 12 talhões,
do portão `(0, 0)` ao ponto de coleta `(11, 11)`, desviando de bloqueios e
pagando 1 por carreador firme e 4 por solo encharcado. O projeto compara BFS,
DFS, UCS e A* (três heurísticas), escolhe quais 15 talhões inspecionar com busca
local, decide o manejo de um talhão com um sistema especialista e mede, com
Bayes, quantos alertas do sensor de pragas são falsos.

## 3. Como rodar

Requer **Python 3.10 ou superior** (testado com 3.13). Na raiz do repositório:

```powershell
python -m pip install -r requirements.txt
python src/main.py 24114032
```

O segundo comando gera do zero, em `resultados/`, os arquivos `pomar.txt`,
`resultados.csv` e `grafico.png`, e imprime a tabela das buscas. A matrícula
também pode ser digitada com pontos (`241.14.032`).

Comandos opcionais:

```powershell
python src/main.py 24114032 --completo   # inclui busca local (~30 s), especialista, Bayes e contraexemplo
python src/aferir.py                     # confere o código com a caixa de aferição (matrícula 20231045)
python src/experimento_escala.py 24114032 --max-n 1600   # Parte 2.4 (pode levar vários minutos)
```

No Windows, se o comando `python` não for encontrado, use `py` no lugar dele.

## 4. Tabela-resumo dos resultados

Matrícula `24114032`, gerada por `python src/main.py 24114032`:

| Estratégia | Custo da rota (unid. de custo) | Passos (movimentos) | Nós expandidos (nós) | Fronteira máxima (nós) | Ótima em custo? |
|---|---:|---:|---:|---:|---|
| BFS | 55 | 22 | 111 | 11 | Não |
| DFS | 170 | 68 | 105 | 59 | Não |
| UCS | 48 | 24 | 114 | 15 | Sim |
| A* h1 (h = 0) | 48 | 24 | 114 | 15 | Sim |
| A* h2 (Manhattan) | 48 | 24 | 110 | 20 | Sim |
| A* h3 (4 x Manhattan) | 54 | 24 | 42 | 27 | Não |

Outros resultados (detalhes no [RELATORIO.md](RELATORIO.md)):

| Medida | Valor |
|---|---|
| Aferição com 20231045 | UCS 34 (111 nós), BFS 55 / 22 passos, A* h2 90 nós: todos dentro da caixa |
| Escala (Parte 2.4) | primeira falha em n = 3800: DFS passou de 60 s de busca |
| Busca local, 30 execuções (pontos de risco) | subida 1267,8 ± 102,2; têmpera 1307,7 ± 84,5; melhor 1337,3 |
| Bayes: P(infestado \| positivo) | 34,0%; 153,6 alertas falsos/semana = 30,7 h/semana |
| Contraexemplo DFS 8 x 8 | DFS custo 53 contra ótimo 14 (3,79 x) |

## 5. Convenções das buscas

- **Ordem de expansão dos vizinhos: Norte, Sul, Oeste, Leste**, a mesma em todas
  as estratégias. Na DFS os vizinhos são empilhados em ordem inversa para que o
  Norte saia primeiro.
- **O A\* reabre nós**: quando aparece um caminho mais barato para um estado já
  expandido, ele volta para a fila. Entradas antigas da fila de prioridade são
  descartadas ao sair.
- O custo do talhão inicial não é contado.
- BFS testa o objetivo na geração; UCS e A* testam na expansão (necessário para
  a otimalidade).
- Desempate na fila de prioridade: ordem de inserção (FIFO).

## 6. Mapa do repositório

- [`README.md`](README.md): esta página.
- [`RELATORIO.md`](RELATORIO.md): relatório completo, Partes 1 a 6, com todas as tabelas.
- [`ANEXO_IA.md`](ANEXO_IA.md): uso de assistentes de IA (Parte 6).
- [`COMO_EXPLICAR.md`](COMO_EXPLICAR.md): perguntas prováveis e roteiro da arguição.
- [`requirements.txt`](requirements.txt): dependência externa (matplotlib, só para o gráfico).
- [`src/main.py`](src/main.py): comando único; gera `pomar.txt`, `resultados.csv` e `grafico.png`.
- [`src/gerador_pomar.py`](src/gerador_pomar.py): gerador do enunciado, **intacto**.
- [`src/buscas.py`](src/buscas.py): BFS, DFS, UCS e A* com os quatro contadores (Partes 2.2 e 3.1).
- [`src/aferir.py`](src/aferir.py): confere o código com a caixa de aferição do enunciado.
- [`src/experimento_escala.py`](src/experimento_escala.py): aumenta n até uma busca falhar (Parte 2.4).
- [`src/busca_local.py`](src/busca_local.py): subida de encosta e têmpera simulada, K = 15, 30 execuções (Parte 3.4).
- [`src/contraexemplo_dfs.py`](src/contraexemplo_dfs.py): pomar 8 x 8 construído em que a DFS custa mais que o dobro do ótimo (bônus).
- [`src/especialista.py`](src/especialista.py): regras SE-ENTÃO, encadeamento para trás e caso que quebra a base (Partes 4.1 e 4.2).
- [`src/bayes.py`](src/bayes.py): contas da Parte 4.3.
- [`resultados/pomar.txt`](resultados/pomar.txt): a grade, com a matrícula-semente na 1ª linha.
- [`resultados/resultados.csv`](resultados/resultados.csv): custo, passos, nós expandidos, fronteira e tempo por estratégia.
- [`resultados/grafico.png`](resultados/grafico.png): nós expandidos por estratégia.
- [`resultados/escala_3600_corrigida.csv`](resultados/escala_3600_corrigida.csv) e
  [`resultados/escala_3800_corrigida.csv`](resultados/escala_3800_corrigida.csv):
  último tamanho em que as três buscas terminaram e primeira falha. Os demais
  `escala_*.csv` são rodadas intermediárias do mesmo experimento.

## 7. Limitações conhecidas

- **Tempos variam de máquina para máquina.** A coluna `tempo_ms` e o ponto de
  falha da Parte 2.4 (n = 3800) foram medidos em um computador; em outro, a
  falha pode ocorrer em n um pouco diferente. Custo, passos, nós expandidos e
  fronteira não mudam.
- **Fronteira de UCS e A\*** conta o tamanho real da fila de prioridade,
  incluindo entradas obsoletas que ainda não saíram; a da DFS inclui estados
  repetidos na pilha. Por isso a DFS tem fronteira maior que a BFS.
- **Busca local:** o risco de cada talhão é sintético (gerado a partir da
  matrícula), a ordem de visita usa a heurística do vizinho mais próximo (não a
  ordem ótima) e os tempos foram calibrados para o pomar 12 x 12; em grades
  maiores a bateria pode não comportar nenhum conjunto (o programa avisa).
- **Sistema especialista:** os casos de teste estão no código; não há entrada
  interativa de fatos. Os limiares (14 dias desde a pulverização, 15 dias de
  carência) são ilustrativos.
- **Bayes:** o valor de dois positivos seguidos (86,5%) supõe testes
  independentes; na prática é um teto.
- **Experimento de escala:** a medição de memória funciona no Windows e no
  Linux; em outros sistemas (macOS) só o limite de tempo é aplicado.
