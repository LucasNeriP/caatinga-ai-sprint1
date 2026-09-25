# Relatório - Caatinga.AI Sprint 1

## Identificação

- Disciplina: Inteligência Artificial
- Período: 2026.2
- Integrante: Lucas Neri - matrícula 241.14.032
- Integrante: **PREENCHER NOME COMPLETO E MATRÍCULA**
- Matrícula usada como semente: `24114032` (**confirmar se pertence ao integrante mais velho**)
- Ordem de expansão dos vizinhos: Norte, Sul, Oeste e Leste

## Parte 1 - O agente antes do código

### 1.1 Ficha PEAS

| Elemento | Definição no Caatinga.AI |
|---|---|
| **P - Medida de desempenho** | Chegar ao ponto de coleta e minimizar o custo total da rota, medido em unidades de custo de terreno. Como medidas auxiliares, registrar número de passos e tempo de execução em milissegundos. |
| **E - Ambiente** | Pomar de manga em uma grade 12 x 12, com carreadores firmes (`.`), solos encharcados (`~`), bloqueios (`#`), portão em `(0, 0)` e ponto de coleta em `(11, 11)`. |
| **A - Atuadores** | Movimentação de um talhão para Norte, Sul, Oeste ou Leste e emissão de indicação de talhão suspeito para inspeção humana. |
| **S - Sensores** | Localização do agente, informação sobre bloqueios e tipo de terreno, além do sensor óptico que indica suspeita de pragas. |

### 1.2 Classificação do ambiente

| Dimensão | Classificação adotada | Evidência e justificativa |
|---|---|---|
| Observabilidade | Parcialmente observável, sob interpretação conservadora | O cenário informa que há um sensor óptico para apontar talhões suspeitos, mas não afirma que o agente conhece previamente todo o pomar nem o estado real de infestação. Esta é uma dimensão discutível: se o mapa completo e o estado de cada talhão forem fornecidos antes da busca, o ambiente de navegação pode ser tratado como totalmente observável. |
| Determinismo | Determinístico | As ações ortogonais levam a uma célula vizinha válida e os custos de entrada são fixos em 1 ou 4. O enunciado não descreve falha de movimento ou resultado aleatório da ação de navegação. |
| Episódico ou sequencial | Sequencial | Cada movimento altera a posição e o custo acumulado, influenciando todas as escolhas seguintes até o objetivo. |
| Estático ou dinâmico | Estático durante o planejamento, por hipótese | A grade é gerada antes da busca e o enunciado não relata mudanças durante a execução. Esta é a segunda dimensão discutível: seria necessário saber se alagamentos, bloqueios ou condições de pragas podem mudar enquanto o agente se desloca. |
| Discreto ou contínuo | Discreto | Há 144 posições de grade, quatro ações possíveis e custos discretos para entrar nos talhões. |
| Agente único ou multiagente | Agente único | Apenas o Caatinga.AI toma decisões de navegação; a inspeção humana acontece como consequência dos alertas e não como agente competidor. |

As duas classificações dependentes de informação não fornecida são
**observabilidade** e **estaticidade**. Para decidir definitivamente, seria
necessário saber se o agente recebe o mapa completo antes de agir e se o pomar
pode mudar enquanto a rota está em execução.

### 1.3 Tipo de agente

Adotamos um **agente baseado em utilidade**. Alcançar `(11, 11)` define o
objetivo, mas não basta distinguir as rotas possíveis: elas podem ter o mesmo
número de passos e custos diferentes. A função de utilidade dá preferência à
rota de menor custo acumulado, permitindo comparar alternativas que chegam ao
mesmo objetivo. Essa escolha é mais específica que afirmar apenas que o agente
é "mais completo".

### 1.4 Métrica perversa

Uma métrica aparentemente razoável seria **maximizar o número de talhões
inspecionados por hora de bateria**. Se otimizada isoladamente, ela incentivaria
o agente a permanecer em talhões firmes e próximos ao portão, como `(1, 1)`,
porque são rápidos e baratos de visitar. Ele evitaria regiões distantes ou
encharcadas, como a vizinhança de `(10, 11)`, mesmo que apresentassem maior risco
de infestação.

A correção é medir **infestações confirmadas por hora de bateria**, exigir uma
cobertura mínima por região do pomar e penalizar áreas de alto risco deixadas
sem inspeção. Assim, aumentar a quantidade de visitas só melhora a métrica se
as visitas também forem relevantes para a cooperativa.

## Parte 2 - Formulação e busca cega

### 2.1 Formulação do problema

1. **Estado inicial:** posição `(0, 0)`, correspondente ao portão.
2. **Ações:** mover Norte, Sul, Oeste ou Leste quando a coordenada resultante
   estiver dentro da grade e não for `#`.
3. **Modelo de transição:** uma ação válida altera deterministicamente a posição
   atual para o talhão vizinho escolhido.
4. **Teste de objetivo:** verificar se a posição atual é `(11, 11)`.
5. **Custo do caminho:** soma dos custos dos talhões em que o agente entra; `.`
   custa 1, `~` custa 4 e o talhão inicial não é contado.

Com a matrícula `24114032`, a grade possui 144 coordenadas. Destas, 29 são
bloqueadas e 115 são livres. Todas as 115 posições livres são alcançáveis a
partir de `(0, 0)`, portanto o espaço de estados alcançáveis deste pomar possui
**115 estados**.

### 2.2 Resultados de BFS, DFS e UCS

Resultados produzidos por `python src/buscas.py 24114032`:

| Estratégia | Custo da rota | Nº de passos | Nós expandidos | Fronteira máxima | Rota ótima em custo? |
|---|---:|---:|---:|---:|---|
| BFS | 55 | 22 | 111 | 11 | Não |
| DFS | 170 | 68 | 105 | 59 | Não |
| UCS | 48 | 24 | 114 | 15 | Sim |

Os quatro contadores são obtidos pelo próprio programa. O custo soma os
terrenos da rota, os passos correspondem ao número de movimentos, os nós
expandidos contam estados cujos sucessores foram examinados e a fronteira
máxima registra o maior tamanho atingido pela estrutura de busca.

### 2.3 Por que a BFS pode ser mais cara que a UCS

A BFS devolveu uma rota de 22 passos e custo 55. A UCS utilizou 24 passos, mas
reduziu o custo para 48. Isso não é um erro: a BFS minimiza a profundidade da
solução, isto é, a quantidade de ações, e não a soma de custos diferentes.

A hipótese necessária para a BFS ser ótima em custo é que todas as ações tenham
o mesmo custo. Essa hipótese foi violada porque entrar em um carreador firme
custa 1 unidade, enquanto entrar em solo encharcado custa 4 unidades. A UCS
considera essa diferença ao ordenar a fronteira pelo custo acumulado.

### 2.4 Experimento de escala

**Pendente de medição.** O experimento deverá executar BFS, DFS e UCS com
`n = 12, 40, 100, ...` até que uma estratégia ultrapasse 60 segundos, esgote a
memória ou encontre outro limite mensurável. Não registramos um ponto de falha
sem executar o experimento.

Como a DFS atual usa pilha explícita, ela não deve falhar pelo limite de
recursão do Python. Ainda assim, tempo e memória precisam ser medidos antes de
relacionar o resultado às fórmulas teóricas da Aula 03.

## Partes seguintes

- Parte 3 - Busca informada: pendente.
- Parte 4 - Regras e incerteza: pendente.
- Parte 5 - Auditoria do laudo: pendente.
