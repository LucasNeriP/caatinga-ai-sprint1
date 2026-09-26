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

| Estratégia | Custo da rota (unid. de custo) | Nº de passos (movimentos) | Nós expandidos (nós) | Fronteira máxima (nós) | Rota ótima em custo? |
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
3400, 3600, 3800`. Cada estratégia foi executada em um processo isolado. O
cronômetro de 60 s começa somente quando a busca inicia, sem incluir a geração
da grade nem a inicialização do processo. Também usamos um limite operacional
de 88% da memória física para evitar o travamento do computador.

O último tamanho em que as três estratégias terminaram foi `n=3600`:

| n | Estratégia | Status | Tempo da busca (s) | Tempo total (s) | Nós expandidos | Fronteira máxima | Pico de memória |
|---:|---|---|---:|---:|---:|---:|---:|
| 3600 | BFS | OK | 19,68 | 21,16 | 10.350.249 | 3.205 | 66,2% |
| 3600 | DFS | OK | 57,43 | 59,45 | 8.063.049 | 5.207.260 | 73,7% |
| 3600 | UCS | OK | 43,71 | 45,21 | 10.350.245 | 5.314 | 72,4% |

Em `n=3800`, ocorreu a primeira falha segundo o critério do enunciado:

| n | Estratégia | Status | Tempo da busca (s) | Tempo total (s) | Nós expandidos | Fronteira máxima | Pico de memória |
|---:|---|---|---:|---:|---:|---:|---:|
| 3800 | BFS | OK | 23,81 | 25,42 | 11.530.933 | 3.428 | 72,2% |
| 3800 | DFS | TEMPO | 60,01 | 61,91 | - | - | 73,6% |

A UCS não foi executada em `n=3800`, pois o experimento para assim que uma das
três estratégias atinge um limite. A primeira falha válida foi, portanto, a DFS
por **tempo de busca acima de 60 s**, não por memória nem por pilha. Como a DFS
foi interrompida, ela não produziu rota nem contadores finais nesse tamanho.

Em uma grade `n x n`, o número de estados possíveis cresce como `Theta(n²)`.
Em `n=3600` há 12.960.000 coordenadas, e a BFS examinou 10.350.249 estados
alcançáveis. Quando `n` cresce, a quantidade de estados que precisa ser
armazenada e examinada também cresce aproximadamente de forma quadrática.

Na formulação clássica da Aula 03, uma DFS em árvore tem tempo de pior caso
`O(b^m)`, em que `b` é o fator de ramificação e `m` é a profundidade máxima.
Nossa implementação é uma busca em grafo com conjunto de explorados; por isso,
o limite mais específico é `O(V + E)`. Como a grade possui `V = n²` coordenadas
e cada uma tem no máximo quatro arestas, o crescimento esperado é `O(n²)`.
A pilha pode conter entradas duplicadas ainda não expandidas, mas cada estado é
expandido no máximo uma vez. Em `n=3600`, a fronteira da DFS chegou a 5.207.260
entradas e a busca levou 57,43 s; em `n=3800`, ela atingiu 60 s antes de
terminar. Os números medidos identificam o tempo como o primeiro recurso
limitante neste computador.

## Parte 3 - Busca informada

### 3.1 A* com três heurísticas

Executamos o A* com a matrícula `24114032`. Em todas as versões, a prioridade
da fronteira é `f(n) = g(n) + h(n)`, em que `g(n)` é o custo real acumulado e
`h(n)` estima o custo restante. A implementação reabre um estado quando encontra
um caminho mais barato até ele.

| Heurística | Custo da rota (unid. de custo) | Nós expandidos (nós) | Admissível? |
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

O caso "ficou igual" também aparece nos nossos experimentos. Com a matrícula de
aferição `20231045`, o A* com h3 devolveu **custo 34, igual ao da UCS**,
expandindo só 24 nós (contra 111 da UCS). Isso **não** prova que h3 é
admissível: admissibilidade é uma propriedade universal (h(n) <= h*(n) para
todo n), e um resultado ótimo numa instância só mostra que, nesse pomar, a
superestimação não chegou a desviar a busca da rota ótima. Um único contraexemplo
basta para refutar a propriedade, e o nosso pomar fornece um: h3(0, 0) = 88 >
h*(0, 0) = 48. A mesma heurística acertou numa semente e errou na outra.

Uma condição de negócio verificável para aceitar essa troca seria uma
reconfiguração urgente de rota após a descoberta de um bloqueio: usar h3 apenas
se houver prazo máximo de resposta e se a rota custar no máximo 15% acima da
ótima, ao mesmo tempo em que reduzir pelo menos 50% das expansões. Neste
experimento, h3 respeitou esses dois limites (12,5% de perda e 63,2% de redução).
No pomar 12 x 12, entretanto, todas as buscas terminaram em menos de 1 ms; sem
uma exigência real de tempo, h2 é preferível porque mantém a garantia de
otimalidade.

### 3.4 Busca local: quais K = 15 talhões inspecionar

**O que foi pedido.** Com 6 h de bateria o agente não visita todos os talhões
livres. Modelar a escolha de K = 15 talhões como busca local, implementar subida
de encosta e têmpera simulada, rodar cada uma 30 vezes e explicar, com os
resultados, por que aceitar piora ajuda.

**Como fizemos** (`src/busca_local.py`). Pense em montar a agenda de um dia de
visitas: não basta escolher os 15 talhões mais arriscados se eles ficam em cantos
opostos do pomar e a bateria acaba no caminho.

| Elemento | Definição |
|---|---|
| Estado | conjunto de 15 talhões livres, sem o portão e sem o ponto de coleta (113 candidatos no nosso pomar) |
| Vizinhança | trocar 1 talhão do conjunto por 1 talhão livre fora dele (15 x 98 = 1.470 vizinhos) |
| Função objetivo (maximizar, em pontos de risco) | `f(S) = soma do risco dos talhões de S - 100 x max(0, tempo(S) - 360 min)` |
| Tempo de um estado | deslocamento portão -> talhões -> coleta (ordem do vizinho mais próximo, 1 unidade de custo = 1 min) + 15 inspeções x 20 min |
| Risco de cada talhão | 0 a 100 pontos, gerado a partir da matrícula: 4 focos de praga espalham risco para os vizinhos e o solo `~` tem risco 30% maior (umidade favorece a praga) |

Com 15 inspeções de 20 min restam 60 min para andar. A rota direta custa 48 min,
então sobra uma **folga de apenas 12 min** para desvios: a bateria é o que torna
o problema difícil. A penalidade de 100 pontos por minuto excedido é maior que o
risco de qualquer talhão, então estourar a bateria nunca compensa.

- **Subida de encosta** (maior subida): avalia os 1.470 vizinhos e vai para o
  melhor; para quando nenhum melhora.
- **Têmpera simulada**: sorteia um vizinho; aceita se melhorar, e se piorar aceita
  com probabilidade `exp(delta / T)`. T começa em 300 e é multiplicada por 0,9995
  a cada uma das 20.000 iterações. Devolve o melhor estado visto.
- Em cada execução (sementes 0 a 29) as duas partem do **mesmo estado inicial
  aleatório**, para que a diferença venha só do algoritmo.

**Resultado** (`python src/busca_local.py 24114032`, 30 execuções):

| Algoritmo | Média | Desvio padrão | Melhor valor | Execuções que atingiram 1337,3 |
|---|---:|---:|---:|---:|
| Subida de encosta | 1267,8 pontos | 102,2 pontos | 1337,3 pontos | 3 de 30 |
| Têmpera simulada | 1307,7 pontos | 84,5 pontos | 1337,3 pontos | 18 de 30 |

Comparação execução a execução: a têmpera **venceu em 22**, empatou em 5
(sementes 5, 8, 11, 13, 22) e perdeu em 3 (sementes 4, 16, 28). A subida parou
em **19 ótimos locais diferentes** nas 30 execuções. A têmpera aceitou em média
**497 pioras** por execução (mínimo 446, máximo 553). O melhor conjunto encontrado
soma 1337,3 pontos de risco e usa exatamente **360 min de 360**.

**Onde "aceitar piora" aparece nos 30 resultados.**

| Semente | Subida (pontos) | Têmpera (pontos) | Pioras aceitas | Leitura |
|---:|---:|---:|---:|---|
| 0 | 942,6 | 1322,4 | 493 | maior ganho (+379,8): a subida parou num morro baixo; a têmpera desceu dele e subiu em outro |
| 20 | 999,7 | 1337,3 | 446 | a subida ficou presa no ótimo local 999,7; a têmpera chegou ao melhor valor conhecido |
| 5 | 999,7 | 999,7 | 458 | as duas presas no mesmo morro: aceitar piora aumenta a chance de escapar, não garante |
| 16 | 1265,5 | 999,7 | 502 | a têmpera perdeu: esfriou dentro do morro 999,7 |

**O que isso significa.** A Aula 04 diz que aceitar piora ajuda porque a subida
de encosta só enxerga os vizinhos imediatos: ao chegar ao topo de um morro, todo
passo é para baixo e ela para, mesmo que exista um morro mais alto do outro lado
do vale. Aqui os morros são os focos de praga: escolher talhões de um foco
distante exige primeiro trocar talhões bons (o valor cai) antes de montar a rota
nova (o valor sobe). A têmpera paga essa "descida" enquanto T é alta e vira uma
subida de encosta quando T esfria. O efeito aparece na média (+39,9 pontos), no
número de execuções que chegam a 1337,3 (18 contra 3) e na semente 0. As
sementes 5 e 16 mostram por que o enunciado pede 30 execuções: uma rodada
isolada da têmpera pode ser pior que a da subida.

Limitação: os tempos foram calibrados para o pomar 12 x 12. Em 500 sementes a
rota direta custou no máximo 49, então todo pomar 12 x 12 é viável; em grades
maiores a folga pode ficar negativa, e o programa avisa.

### Bônus - Contraexemplo construído para a DFS

**O que foi pedido.** Um pomar de no máximo 8 x 8 em que a DFS, com a nossa
ordem de vizinhos, devolva rota com custo maior que o dobro do ótimo.

**Como fizemos** (`src/contraexemplo_dfs.py`). A ordem declarada é N, S, O, L.
No portão (0, 0) Norte e Oeste estão fora da grade, então a DFS **sempre tenta o
Sul antes do Leste**. Construímos a armadilha em torno disso:

1. bloqueamos o miolo (`#`), para que quem entrar por um lado tenha de dar a
   volta inteira por ele;
2. pusemos solo encharcado (`~`, custo 4) no lado para onde a ordem empurra a DFS
   (coluna 0 e linha 7);
3. pusemos carreador firme (`.`, custo 1) no lado que ela nunca visita (linha 0
   e coluna 7).

```text
. . . . . . . .        D . . . . . . .        U U U U U U U U
~ # # # # # # .        D # # # # # # .        ~ # # # # # # U
~ # # # # # # .        D # # # # # # .        ~ # # # # # # U
~ # # # # # # .        D # # # # # # .        ~ # # # # # # U
~ # # # # # # .        D # # # # # # .        ~ # # # # # # U
~ # # # # # # .        D # # # # # # .        ~ # # # # # # U
~ # # # # # # .        D # # # # # # .        ~ # # # # # # U
~ ~ ~ ~ ~ ~ ~ .        D D D D D D D D        ~ ~ ~ ~ ~ ~ ~ U
   pomar                 rota da DFS             rota ótima (UCS)
```

**Resultado:**

| Rota | Talhões | Custo | Passos |
|---|---|---:|---:|
| DFS (N, S, O, L) | (0,0) -> (1,0) -> ... -> (7,0) -> (7,1) -> ... -> (7,7) | 13 x 4 + 1 = **53 unidades de custo** | 14 |
| Ótima (UCS) | (0,0) -> (0,1) -> ... -> (0,7) -> (1,7) -> ... -> (7,7) | 14 x 1 = **14 unidades de custo** | 14 |

53 / 14 = **3,79**, maior que o dobro (28).

**O que isso significa.** As duas rotas têm o mesmo número de passos: a DFS não
errou no tamanho, errou no custo, porque devolve o primeiro caminho que encontra
e nunca compara custos. O contraexemplo depende da ordem declarada: com a ordem
N, L, S, O a mesma grade daria custo 14 para a DFS.

## Parte 4 - Regras e incerteza

Parâmetros do sensor, obtidos com `parametros_sensor(24114032)`:

| Parâmetro | Valor |
|---|---:|
| Prevalência P(I) | 0,04 (4% dos talhões) |
| Sensibilidade P(+\|I) | 0,99 |
| Taxa de falso positivo P(+\|não I) | 0,08 |
| Talhões inspecionados por semana | 2000 talhões/semana |

### 4.1 Mini sistema especialista

**O que foi pedido.** De 5 a 8 regras SE ... ENTÃO ... de manejo de um talhão,
com encadeamento para trás e impressão da cadeia de regras que sustentou a
conclusão.

**Como fizemos** (`src/especialista.py`). O encadeamento para trás funciona como
um médico que suspeita de um diagnóstico e vai atrás das provas: o programa testa
as hipóteses em ordem de gravidade (`manejo_sem_quimico`, `pulverizar`,
`inspecionar_prioridade_alta`, `inspecionar_prioridade_media`, `monitorar`) e,
para cada uma, desce pelas regras até chegar aos fatos informados. A primeira
hipótese provada é a conclusão. `NAO x` usa negação por falha (mundo fechado): é
verdadeiro quando `x` não pode ser provado.

| Regra | SE | ENTÃO |
|---|---|---|
| R1 | armadilha_positiva E umidade_alta | condicao_favoravel_praga |
| R2 | condicao_favoravel_praga E dias_desde_pulverizacao > 14 | inspecionar_prioridade_alta |
| R3 | sensor_positivo E vizinho_infestado | suspeita_confirmada |
| R4 | suspeita_confirmada E dias_desde_pulverizacao > 14 | pulverizar |
| R5 | sensor_positivo E NAO armadilha_positiva | inspecionar_prioridade_media |
| R6 | armadilha_positiva | monitorar |
| R7 | suspeita_confirmada | inspecionar_prioridade_alta |

**Resultado.** Traço do caso A (sensor positivo, vizinho infestado, armadilha
positiva, umidade alta, 20 dias desde a pulverização, colheita em 60 dias):

```text
== Hipótese: manejo_sem_quimico
  manejo_sem_quimico? não informado e nenhuma regra conclui -> falso
== Hipótese: pulverizar
  pulverizar? tentando R4: SE suspeita_confirmada E dias_desde_pulverizacao > 14 ENTAO pulverizar
    suspeita_confirmada? tentando R3: SE sensor_positivo E vizinho_infestado ENTAO suspeita_confirmada
      sensor_positivo? fato informado = sim
      vizinho_infestado? fato informado = sim
    v suspeita_confirmada provado por R3
    dias_desde_pulverizacao > 14? valor informado = 20 -> sim
  v pulverizar provado por R4
CONCLUSÃO: pulverizar
Por que concluí isso?
- pulverizar porque R4 (suspeita confirmada e talhão desprotegido):
  - suspeita_confirmada porque R3 (o sensor apontou e há infestação confirmada em talhão vizinho):
    - sensor_positivo (informado)
    - vizinho_infestado (informado)
  - dias_desde_pulverizacao = 20 > 14 (informado)
```

Diagnósticos dos seis casos de teste:

| Caso | Conclusão | Regra decisiva |
|---|---|---|
| A - foco confirmado | pulverizar | R4 <- R3 |
| B - clima favorável | inspecionar_prioridade_alta | R2 <- R1 |
| C - só o sensor | inspecionar_prioridade_media | R5 |
| D - armadilha isolada | monitorar | R6 |
| E - talhão limpo | sem_acao | nenhuma |
| F - pulverizado há pouco | inspecionar_prioridade_alta | R7 <- R3 |

**O que isso significa.** Cada conclusão vem com a árvore de regras que a
provou, e é essa árvore que responde "por que você concluiu isso?". O caso C já
antecipa o Bayes: só o sensor positivo leva a prioridade média, e não a
pulverizar, porque dois em cada três alertas do sensor são falsos (Parte 4.3).

### 4.2 Caso que quebra a base

**O que foi pedido.** Um caso legítimo que a base classifica errado e uma regra
que o corrige sem contradizer as demais, com o traço antes e depois.

**Como fizemos.** O caso G tem o mesmo quadro do caso A, mas a **colheita é
daqui a 7 dias**. A base manda pulverizar, o que deixaria resíduo de inseticida
na fruta dentro do período de carência; a manga do Vale do São Francisco é
exportada e o lote pode ser recusado. O manejo correto é sem químico (ensacar ou
catar frutos, isolar o talhão, antecipar a colheita). Acrescentamos:

`R8: SE suspeita_confirmada E dias_ate_colheita < 15 ENTAO manejo_sem_quimico`

**Resultado.** Antes (R1 a R7):

```text
== Hipótese: manejo_sem_quimico
  manejo_sem_quimico? não informado e nenhuma regra conclui -> falso
== Hipótese: pulverizar
  pulverizar? tentando R4: SE suspeita_confirmada E dias_desde_pulverizacao > 14 ENTAO pulverizar
    ...
  v pulverizar provado por R4
CONCLUSÃO: pulverizar
```

Depois (R1 a R8):

```text
== Hipótese: manejo_sem_quimico
  manejo_sem_quimico? tentando R8: SE suspeita_confirmada E dias_ate_colheita < 15 ENTAO manejo_sem_quimico
    suspeita_confirmada? tentando R3: SE sensor_positivo E vizinho_infestado ENTAO suspeita_confirmada
      sensor_positivo? fato informado = sim
      vizinho_infestado? fato informado = sim
    v suspeita_confirmada provado por R3
    dias_ate_colheita < 15? valor informado = 7 -> sim
  v manejo_sem_quimico provado por R8
CONCLUSÃO: manejo_sem_quimico
```

Conferência de que a R8 não contradiz as outras regras:

| Caso | Antes (R1 a R7) | Depois (R1 a R8) |
|---|---|---|
| A a F | (iguais aos da tabela da 4.1) | sem alteração |
| G - foco perto da colheita | pulverizar | **manejo_sem_quimico** |

**O que isso significa.** A R8 é mais específica que a R4: exige tudo o que a R4
exige e mais a colheita próxima. Por isso a hipótese dela é testada antes, e a
regra específica vence a geral sem apagar nada. Só o caso G mudou; os outros seis
mantêm o diagnóstico.

### 4.3 Bayes com os nossos números

**O que foi pedido.** (a) P(infestado | positivo); (b) quantos em cada 100
alertas são falsos; (c) alertas falsos por semana e horas perdidas; (d) o efeito
de subir a sensibilidade para 99,9%.

**Como fizemos** (`src/bayes.py`). Uma forma simples de ver: em 1000 talhões,
40 estão infestados e o sensor acerta 0,99 x 40 ≈ 40; os outros 960 estão sadios
e o sensor erra em 0,08 x 960 ≈ 77. De 117 alertas, só 40 são reais.

**Resultado.**

(a) Substituindo na fórmula:

```text
P(I|+) = P(+|I) P(I) / [P(+|I) P(I) + P(+|não I) P(não I)]
       = 0,99 x 0,04 / [0,99 x 0,04 + 0,08 x 0,96]
       = 0,0396 / [0,0396 + 0,0768]
       = 0,0396 / 0,1164
       = 0,3402  (34,0%)
```

(b) A cada 100 alertas do meu sistema, cerca de **66** serão falsos.

(c) Com 2000 talhões inspecionados por semana:

| Medida | Conta | Valor |
|---|---|---:|
| Alertas totais | 2000 x (0,99 x 0,04 + 0,08 x 0,96) | 232,8 alertas/semana |
| Alertas falsos | 2000 x 0,08 x 0,96 | **153,6 alertas falsos/semana** |
| Tempo perdido | 153,6 x 12 min / 60 | **30,7 horas/semana** |

(d) Sensibilidade de 99,9% com a mesma taxa de falso positivo:

```text
VPP = 0,999 x 0,04 / [0,999 x 0,04 + 0,08 x 0,96] = 0,03996 / 0,11676 = 0,3422  (34,2%)
```

| Mudança | VPP |
|---|---:|
| Situação atual | 34,0% |
| Sensibilidade 0,99 -> 0,999 | 34,2% (+0,2 ponto percentual) |
| Falso positivo 0,08 -> 0,04 | 50,8% |
| Falso positivo 0,08 -> 0,01 | 80,5% |

Para a auditoria (Parte 5), dois positivos seguidos no mesmo talhão, **supondo
independência** entre os testes:
`VPP = 0,99² x 0,04 / [0,99² x 0,04 + 0,08² x 0,96] = 0,0392 / 0,0453 = 86,5%`.

**O que isso significa.** O problema não melhorou: 30,7 horas por semana
continuam indo para alarmes falsos. Com sensibilidade de 99% quase nenhum
infestado escapa; o que polui os alertas são os falsos positivos vindos dos 96%
de talhões sadios. O parâmetro a mexer é a **taxa de falso positivo**
(especificidade do sensor) ou, sem trocar o sensor, a **prevalência entre os
talhões testados**: usar o sensor só onde a armadilha já capturou mosca, que é o
que a R5 faz ao rebaixar "só o sensor" para prioridade média.

### 4.4 A regra que salva o modelo

**Decisão que deve ficar em regra explícita:** *aplicar inseticida em um
talhão*, e em particular o bloqueio da R8 (sem inseticida a menos de 15 dias da
colheita).

**Justificativa (auditabilidade e responsabilidade).** Aplicar agrotóxico no
Brasil exige receituário agronômico assinado por um profissional habilitado, que
responde pela prescrição. Se um lote exportado for recusado por resíduo, a
cooperativa precisa mostrar **por que** aquele talhão foi pulverizado naquele
dia. Com a regra explícita, o registro é a própria cadeia impressa pelo programa
(R4 <- R3 <- sensor_positivo, vizinho_infestado; dias_ate_colheita = 7 < 15
acionaria R8), que o agrônomo lê, confere e assina. Um modelo aprendido pode até
acertar mais, mas não produz uma justificativa que alguém possa assinar, e mudar
seu comportamento exige retreinar, enquanto o limiar de 15 dias muda numa linha
revisável. A responsabilidade legal é de uma pessoa, então a decisão precisa ser
legível por essa pessoa.

## Parte 5 - Auditoria do laudo da AgroVision

**O que foi pedido.** Classificar cada afirmação como correta, parcialmente
correta ou incorreta, com a teoria das Aulas 01 a 05 e um número medido por nós.

| # | Afirmação | Veredito | Teoria | Nosso número |
|---:|---|---|---|---|
| 1 | "A* com Manhattan x 4 é comprovadamente ótimo; a rota é sempre a mais barata." | **Incorreta** | O A* só garante otimalidade com heurística admissível (h(n) <= h*(n)). Como o menor custo de entrada é 1, Manhattan x 4 pode superestimar o custo real restante. | No nosso pomar, A* h3 devolveu **custo 54** contra o ótimo **48** (+12,5%); em (0, 0), h3 = 88 > h* = 48. |
| 2 | "Substituir BFS por A* reduziu o custo em 38%; a heurística melhora a qualidade da solução." | **Parcialmente correta** | A redução de custo pode acontecer, mas vem de ordenar a fronteira pelo custo acumulado g(n), não da heurística. Uma heurística admissível só reduz expansões; nunca produz custo menor que o ótimo, e a inadmissível pode piorar. | BFS 55 -> UCS (sem heurística, h = 0) **48**: toda a redução (-12,7%) já vem sem heurística. A* h2 também dá 48 (a heurística só cortou expansões, de 114 para 110). A* h3 piora para 54. |
| 3 | "Sensibilidade de 99%, portanto 99% dos talhões apontados estão infestados." | **Incorreta** | Confunde P(+\|I) com P(I\|+). Pelo teorema de Bayes, a prevalência baixa domina o resultado. | Com a mesma sensibilidade de 0,99, nosso VPP é **34,0%**: 66 de cada 100 alertas são falsos. |
| 4 | "Aplicando o teste duas vezes e exigindo dois positivos, a confiança passa de 99%." | **Incorreta** | Dois testes ajudam, mas a prevalência continua pesando; além disso, repetir o mesmo sensor no mesmo talhão produz erros correlacionados, e a independência é otimista. | Mesmo supondo independência, dois positivos dão **86,5%**, abaixo de 99%. |
| 5 | "Usamos DFS porque consome muito menos memória; como o pomar é estático e totalmente observável, a DFS é suficiente." | **Incorreta** | A economia de memória O(b·m) vale para DFS em árvore; em grafo com conjunto de explorados, a pilha acumula duplicatas. Ambiente estático e observável não torna a DFS ótima: ela devolve o primeiro caminho, não o mais barato. | Fronteira máxima em n = 12: DFS **59** contra BFS 11 e UCS 15. Em n = 3600: DFS **5.207.260** entradas contra BFS 3.205. Custo: DFS **170** contra ótimo 48 (3,5x); no contraexemplo, 53 contra 14. |

**Recomendação à diretoria.** Recomendamos **não contratar a AgroVision na forma
atual**. Quatro das cinco afirmações são incorretas e a quinta atribui à
heurística um ganho que vem do custo acumulado; os erros estão justamente nos
pontos que custam dinheiro: rotas até 12,5% mais caras que o necessário (e 3,5x
com DFS) e um detector em que 66 de cada 100 alertas são falsos, o que para nós
significaria 30,7 horas semanais de agrônomo perdidas. Mudaríamos para
"contratar com ressalvas" se a empresa (1) trocar a heurística por uma admissível
e mostrar custo igual ao da UCS em pomares de teste nossos e (2) informar a taxa
de falso positivo do sensor e demonstrar VPP de pelo menos 80%, o que exige
falso positivo em torno de 1%.

## Parte 6 - Uso de IA

O registro do uso de assistentes de IA está em [`ANEXO_IA.md`](ANEXO_IA.md).
