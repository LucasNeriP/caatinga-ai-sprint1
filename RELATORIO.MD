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

Executamos BFS, DFS e UCS com a matrícula `24114032` e aumentamos a dimensão da
grade na sequência `12, 40, 100, 200, 400, 800, 1600, 2400, 2800, 3000, 3200,
3400, 3600`. Cada estratégia foi executada em um processo isolado, com limite
de 60 s de tempo total e limite operacional de 88% da memória física. O limite
de memória encerra o processo antes de um travamento do sistema e, portanto,
não deve ser confundido com um `MemoryError`.

O último tamanho em que as três estratégias terminaram foi `n=3400`:

| n | Estratégia | Status | Tempo da busca (s) | Tempo total (s) | Nós expandidos | Fronteira máxima | Pico de memória |
|---:|---|---|---:|---:|---:|---:|---:|
| 3400 | BFS | OK | 17,88 | 19,28 | 9.232.948 | 3.078 | 77,4% |
| 3400 | DFS | OK | 48,22 | 50,98 | 7.189.276 | 4.655.357 | 83,4% |
| 3400 | UCS | OK | 39,54 | 40,86 | 9.232.949 | 5.015 | 82,7% |

Em `n=3600`, ocorreu a primeira falha medida:

| n | Estratégia | Status | Tempo da busca (s) | Tempo total (s) | Nós expandidos | Fronteira máxima | Pico de memória |
|---:|---|---|---:|---:|---:|---:|---:|
| 3600 | BFS | OK | 20,49 | 21,98 | 10.350.249 | 3.205 | 77,8% |
| 3600 | DFS | TEMPO | interrompida | 60,17 | - | - | 84,8% |

A UCS não foi executada em `n=3600`, pois o experimento foi programado para
parar assim que uma das três estratégias atingisse um limite. A falha observada
foi de **tempo**, não de memória nem de pilha. Como a DFS foi interrompida, ela
não produziu rota nem contadores finais nesse tamanho.

O tempo de 60 s é o tempo total do processo isolado, incluindo geração da grade
e inicialização. Essa convenção mede o tempo de execução percebido por quem roda
o experimento; por isso o tempo exclusivo da DFS interrompida não está
disponível.

Em uma grade `n x n`, o número de estados possíveis cresce como `Theta(n²)`.
Em `n=3400` há 11.560.000 coordenadas, e a BFS examinou 9.232.948 estados
alcançáveis. Quando `n` cresce, a quantidade de estados que precisa ser
armazenada e examinada também cresce aproximadamente de forma quadrática.

Na formulação clássica da Aula 03, a DFS tem tempo de pior caso `O(b^m)`, em que
`b` é o fator de ramificação e `m` é a profundidade máxima. Neste pomar,
`b <= 4`, mas a profundidade alcançada pela DFS pode ser muito grande. Nossa
implementação em grafo usa conjunto de explorados e pilha explícita, evitando
laços e estouro da pilha de chamadas do Python, mas ainda precisa manter muitos
estados. Em `n=3400`, a fronteira da DFS chegou a 4.655.357 entradas e a busca
levou 48,22 s; no tamanho seguinte, atingiu o limite de 60 s. Os números medidos
mostram o crescimento previsto pela análise teórica e identificam o tempo como
o primeiro recurso limitante neste computador.

## Parte 3 - Busca informada

### 3.1 A* com três heurísticas

Executamos o A* com a matrícula `24114032`. Em todas as versões, a prioridade
da fronteira é `f(n) = g(n) + h(n)`, em que `g(n)` é o custo real acumulado e
`h(n)` estima o custo restante. A implementação reabre um estado quando encontra
um caminho mais barato até ele.

| Heurística | Custo da rota | Nós expandidos | Admissível? |
|---|---:|---:|---|
| h1: `0` | 48 | 114 | Sim |
| h2: Manhattan | 48 | 110 | Sim |
| h3: `4 x Manhattan` | 54 | 42 | Não |

A h1 produziu os mesmos números da UCS, como esperado, pois `f(n) = g(n)`
quando a heurística é zero. A h2 preservou o custo ótimo e expandiu quatro nós a
menos. A h3 expandiu muito menos nós, mas devolveu uma rota mais cara.

### 3.2 Admissibilidade e contraexemplo

A h1 é admissível porque vale zero e os custos restantes nunca são negativos.

Para h2, seja `d` a distância de Manhattan entre o estado atual e `(11, 11)`.
Cada ação ortogonal reduz essa distância em no máximo uma unidade, portanto são
necessários pelo menos `d` movimentos. Como o menor custo de entrada em um
talhão é 1, o custo real restante é pelo menos `d`. Logo,
`h2(n) = d <= h*(n)`, e h2 é admissível.

A h3 não é admissível. Um contraexemplo concreto do nosso pomar é o par de
talhões `(0, 0)` e `(11, 11)`. A distância de Manhattan é 22, então h3 estima
`4 x 22 = 88`. A UCS mediu custo ótimo real 48 entre essas coordenadas. Como
`88 > 48`, a heurística superestima o custo restante.

### 3.3 Custo de h3 e troca entre qualidade e velocidade

A UCS devolveu custo 48 e expandiu 114 nós. O A* com h3 devolveu custo 54 e
expandiu 42 nós. A perda de qualidade foi:

```text
(54 - 48) / 48 x 100 = 12,5%
```

Em troca, h3 evitou `114 - 42 = 72` expansões, uma redução de aproximadamente
63,2%. O resultado ótimo obtido por uma heurística em um caso isolado nunca
provaria sua admissibilidade, pois admissibilidade exige que ela não
superestime em nenhum estado; neste pomar, porém, h3 efetivamente retornou custo
maior e o contraexemplo da seção anterior demonstra formalmente a
superestimação.

Uma condição de negócio verificável para aceitar essa troca seria uma
reconfiguração urgente de rota após a descoberta de um bloqueio: usar h3 apenas
se houver prazo máximo de resposta e se a rota custar no máximo 15% acima da
ótima, ao mesmo tempo em que reduzir pelo menos 50% das expansões. Neste
experimento, h3 respeitou esses dois limites (12,5% de perda e 63,2% de redução).
No pomar 12 x 12, entretanto, todas as buscas terminaram em menos de 1 ms; sem
uma exigência real de tempo, h2 é preferível porque mantém a garantia de
otimalidade.

## Partes seguintes

- Parte 3.4 - Busca local: pendente.
- Parte 4 - Regras e incerteza: pendente.
- Parte 5 - Auditoria do laudo: pendente.
