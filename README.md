# Caatinga.AI - Sprint 1

## Identificação

- Disciplina: Inteligência Artificial
- Período: 2026.2
- Integrante: Lucas Neri - matrícula 241.14.032
- Integrante: **PREENCHER NOME COMPLETO E MATRÍCULA**
- Matrícula usada como semente: `24114032` (**confirmar se pertence ao integrante mais velho**)

## Sobre o projeto

O Caatinga.AI simula um agente que atravessa um pomar de manga representado por
uma grade de 12 x 12 talhões. O agente parte de `(0, 0)` e busca o ponto de
coleta em `(11, 11)`, evitando bloqueios e considerando os custos dos terrenos.
Esta etapa compara BFS, DFS, UCS e A* por custo, passos, nós expandidos e
tamanho máximo da fronteira.

## Como executar

Requer Python 3.10 ou superior. Na raiz do repositório, execute:

```bash
python -m pip install -r requirements.txt
python src/aferir.py
python src/buscas.py 24114032
```

No Windows, caso o comando `python` não esteja disponível, substitua-o por
`py`.

O comando de aferição compara BFS, UCS e A* com a caixa de referência do
enunciado. O comando de buscas executa BFS, DFS, UCS e as três versões do A*
no pomar da dupla.

## Resultados atuais

Resultados medidos com a matrícula `24114032`:

| Estratégia | Custo da rota | Passos | Nós expandidos | Fronteira máxima | Ótima em custo? |
|---|---:|---:|---:|---:|---|
| BFS | 55 | 22 | 111 | 11 | Não |
| DFS | 170 | 68 | 105 | 59 | Não |
| UCS | 48 | 24 | 114 | 15 | Sim |
| A* h1 | 48 | 24 | 114 | 15 | Sim |
| A* h2 | 48 | 24 | 110 | 20 | Sim |
| A* h3 | 54 | 24 | 42 | 27 | Não |

A BFS encontrou uma rota com menos passos que a UCS, mas não a rota de menor
custo. Isso ocorre porque os passos não têm custo uniforme: entrar em `.` custa
1 unidade e entrar em `~` custa 4 unidades.

### Experimento de escala

O último tamanho em que BFS, DFS e UCS terminaram foi `n=3600`. Em `n=3800`,
a BFS terminou, mas a DFS atingiu o limite de 60 s de busca e foi interrompida.
O pico de memória dessa execução foi 73,6%, abaixo do limite operacional de
88%. A UCS não foi executada porque o experimento para na primeira falha.

## Convenções das buscas

- Ordem de expansão dos vizinhos: Norte, Sul, Oeste e Leste.
- O custo do talhão inicial não é contado.
- A BFS usa fila FIFO e busca a menor profundidade.
- A DFS usa pilha explícita e não depende da pilha de recursão do Python.
- A UCS usa fila de prioridade pelo custo acumulado e aceita melhorias de custo.
- O A* usa `f(n) = g(n) + h(n)` e reabre estados quando encontra um caminho
  mais barato.

## Mapa do repositório

- [`README.md`](README.md): apresentação, execução e resumo dos resultados.
- [`RELATORIO.MD`](RELATORIO.MD): respostas e análises exigidas na atividade.
- [`ANEXO_IA.md`](ANEXO_IA.md): registro obrigatório do uso de assistentes de IA.
- [`requirements.txt`](requirements.txt): dependências externas do projeto.
- [`src/gerador_pomar.py`](src/gerador_pomar.py): gerador fornecido no enunciado,
  mantido intacto.
- [`src/buscas.py`](src/buscas.py): BFS, DFS, UCS, A* e instrumentação das
  buscas.
- [`src/aferir.py`](src/aferir.py): validação contra os números de referência.
- [`src/experimento_escala.py`](src/experimento_escala.py): experimento da Parte
  2.4 com limites controlados de tempo e memória.
- [`resultados/escala_3600_corrigida.csv`](resultados/escala_3600_corrigida.csv):
  último tamanho em que as três buscas terminaram.
- [`resultados/escala_3800_corrigida.csv`](resultados/escala_3800_corrigida.csv):
  primeira falha válida pelo limite de 60 s de busca.

## Limitações conhecidas

- Busca local, sistema especialista, Bayes e o orquestrador `src/main.py` ainda
  não foram implementados.
- `resultados.csv`, `grafico.png` e `pomar.txt` ainda não são gerados
  automaticamente.
- A identificação do segundo integrante e a confirmação da matrícula-semente
  ainda precisam ser preenchidas.
