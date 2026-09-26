# Anexo - Uso de assistentes de IA

## A.1 Ferramentas usadas e em que partes

| Integrante | Ferramenta | Partes do trabalho |
|---|---|---|
| Paulo | Claude Code (modelo Claude Opus 5.5), no terminal do Windows | Estrutura do repositório e BFS/DFS (Etapas 1 e 2); busca local (3.4); contraexemplo da DFS (bônus); sistema especialista (4.1 e 4.2); Bayes (4.3); `main.py`; redação das Partes 3.4, 4 e 5 do relatório; README; este anexo e o `COMO_EXPLICAR.md` |
| Lucas | **PREENCHER** | **PREENCHER** |

Como usamos: Pedimos instruções, explicações e códigos aos agentes para nos instruir e auxiliar.

Fluxo com o Claude Code: o assistente escrevia e testava cada arquivo numa pasta
temporária, mostrava a saída, e só depois o Paulo copiava o arquivo para o
repositório, rodava de novo e fazia o commit.

## A.2 Dois prompts na íntegra, com a resposta recebida

### Prompt 1

````text
# PAPEL
Você é um engenheiro de software e professor de Inteligência Artificial. Sua tarefa é
construir, do zero, o projeto "Caatinga.AI – Sprint 1" descrito no enunciado anexado,
e explicar cada parte em linguagem simples, como se estivesse ensinando a um colega
que ainda está aprendendo.

# DADOS DA DUPLA (preencha antes de rodar)
- Integrante A: <nome completo> – matrícula <xxxx> – usuário GitHub <@xxxx>
- Integrante B: <nome completo> – matrícula <xxxx> – usuário GitHub <@xxxx>
- Matrícula-semente (integrante mais velho): <xxxxxxxx>
- Sistema operacional: Windows | Versão do Python: <3.x>
- Ordem de expansão dos vizinhos: Norte, Sul, Oeste, Leste (usar em TODAS as estratégias)

# REGRAS INEGOCIÁVEIS
1. Copie `gerador_pomar.py` EXATAMENTE como está no enunciado. Não altere nenhum caractere.
   Salve-o em `src/gerador_pomar.py` e apenas importe-o.
2. Nunca invente números. Todo valor em tabela, relatório ou README deve vir da
   execução real do código. Se não conseguir executar, deixe `<A PREENCHER APÓS EXECUÇÃO>`.
3. Antes de rodar com a semente da dupla, VALIDE com a matrícula 20231045. O resultado
   precisa bater com a caixa de aferição:
   - UCS: custo 34
   - BFS: custo 55 e 22 passos
   - UCS: ~112 nós expandidos (±20%)
   - A* com Manhattan: ~93 nós expandidos (±20%)
   Se não bater, depure antes de seguir e registre o que estava errado.
4. Use apenas a biblioteca padrão do Python, mais matplotlib para o gráfico.
5. O código deve funcionar com QUALQUER semente e qualquer n, não só com a da dupla.
   Haverá arguição com uma semente nova.
6. Comentários no código em português, curtos, explicando o PORQUÊ de cada decisão
   e não só o quê.

# FLUXO DE TRABALHO COM COMMITS (MUITO IMPORTANTE)
O projeto exige no mínimo 8 commits, feitos pelos DOIS integrantes, cada um com a
própria conta do GitHub, com mensagens descritivas e distribuídos ao longo do tempo.
Por isso:

- Trabalhe em UMA etapa por vez, seguindo a tabela abaixo.
- Cada etapa termina com algo que RODA. Nada de commit pela metade.
- Ao final de cada etapa, PARE e responda neste formato:

  ✅ ETAPA X CONCLUÍDA
  **Arquivos criados/alterados:** <lista>
  **Como testar:** <comando para rodar no terminal do Windows>
  **Saída esperada:** <o que deve aparecer>
  **Explicação simples:** <3 a 6 frases do que foi feito e por quê>
  **Commit — quem faz: Integrante <A/B>**
      git add <arquivos>
      git commit -m "<mensagem descritiva>"
      git push
  ⏸️ Aguardando confirmação. Responda "commit feito" para eu seguir para a Etapa X+1.

- NÃO avance para a próxima etapa sem a confirmação "commit feito".
- Se eu informar um erro na execução, corrija DENTRO da mesma etapa antes de seguir.
- Na primeira etapa, lembre cada integrante de configurar a identidade no próprio
  computador:
      git config user.name "<nome>"
      git config user.email "<email do GitHub>"

# TABELA DE ETAPAS
| Etapa | Entrega | Quem commita | Mensagem de commit sugerida |
|------:|---------|:------------:|-----------------------------|
| 1 | Estrutura de pastas, .gitignore, requirements.txt, gerador_pomar.py intacto | A | cria estrutura do repositório e adiciona gerador_pomar intacto |
| 2 | BFS e DFS iterativa com os 4 contadores | B | implementa BFS e DFS com contadores de nós e fronteira |
| 3 | UCS + validação com 20231045 | A | implementa UCS com fila de prioridade e valida com semente de aferição |
| 4 | Escalonamento de n e DFS recursiva (Parte 2.4) | B | adiciona experimento de escalonamento de n até falha |
| 5 | A* com h1, h2, h3 + validação | A | implementa A* com heurísticas nula, Manhattan e 4x Manhattan |
| 6 | Função que acha o talhão onde h3 superestima | B | adiciona detecção de superestimação da heurística h3 |
| 7 | Subida de encosta e têmpera simulada, 30 execuções cada | A | implementa busca local com subida de encosta e têmpera simulada |
| 8 | Contraexemplo DFS 8×8 (bônus) | B | adiciona contraexemplo construído para DFS |
| 9 | Sistema especialista + encadeamento para trás + caso que quebra a base | A | implementa sistema especialista com encadeamento para trás |
| 10 | bayes.py com os itens (a) a (d) e dois testes seguidos | B | implementa cálculos bayesianos do sensor |
| 11 | main.py gerando resultados.csv, grafico.png e pomar.txt | A | cria main.py que gera resultados, gráfico e pomar |
| 12a | RELATORIO.md: Partes 1, 2 e 3 | B | escreve relatório das Partes 1 a 3 |
| 12b | RELATORIO.md: Partes 4 e 5 + README.md | A | escreve relatório das Partes 4 e 5 e README |
| 12c | ANEXO_IA.md (esqueleto) + COMO_EXPLICAR.md | B | adiciona anexo de uso de IA e guia de arguição |

Dica para a dupla: não façam tudo no mesmo dia. Dois ou três commits por dia, ao longo
de alguns dias, deixam o histórico mais convincente.

# ESTRUTURA DO REPOSITÓRIO (obrigatória)
caatinga-ai-sprint1/
├── README.md
├── RELATORIO.md
├── ANEXO_IA.md
├── COMO_EXPLICAR.md
├── requirements.txt
├── .gitignore            (venv/, __pycache__/, *.pyc)
├── src/
│   ├── main.py           (python src/main.py <matricula> gera tudo)
│   ├── gerador_pomar.py  (INTACTO)
│   ├── buscas.py         (BFS, DFS, UCS, A*)
│   ├── busca_local.py    (subida de encosta e têmpera simulada)
│   ├── especialista.py   (regras + encadeamento para trás)
│   └── bayes.py          (cálculos da Parte 4.3)
└── resultados/
    ├── resultados.csv    (estrategia,heuristica,custo,passos,nos_expandidos,fronteira_max,tempo_ms)
    ├── grafico.png       (nós expandidos × estratégia, eixos rotulados e com unidade)
    └── pomar.txt         (1ª linha = matrícula-semente; depois a grade)

# DETALHES TÉCNICOS POR ETAPA

**Etapas 2 e 3 – Busca cega**
- Custo = soma do custo dos talhões ENTRADOS (o inicial não conta). "#" é intransponível.
- Diferencie ESTADO (coordenada) de NÓ (estado + pai + custo). Use conjunto de visitados.
- A fronteira máxima é o MAIOR tamanho atingido durante a execução, não o final.
- BFS: teste de objetivo na GERAÇÃO.
- UCS e A*: teste de objetivo na EXPANSÃO, que é necessário para a otimalidade.
  Se aparecer um caminho mais barato para um estado já na fronteira, atualize-o.
- DFS iterativa (pilha explícita) para a tabela principal.
- Desempate na fila de prioridade: contador de inserção. Documente essa escolha.

**Etapa 4 – Escalonamento**
- Rode com n = 12, 40, 100, 200, 500… e registre em qual n e em qual algoritmo houve
  falha (memória, pilha ou tempo > 60 s).
- Inclua uma DFS RECURSIVA para mostrar o estouro de pilha real.
- Compare o valor medido com O(b^d), O(b^m) e com o número de estados n².

**Etapas 5 e 6 – A***
- Declare se o A* reabre nós (recomendado: sim).
- Use UCS reverso a partir do objetivo para achar o custo real restante e encontre
  automaticamente um talhão onde h3(n) > custo real. Imprima as coordenadas e os
  dois números.
- Calcule a perda percentual de h3 em relação ao UCS e a diferença de nós expandidos.

**Etapa 7 – Busca local**
- Estado: conjunto de K = 15 talhões livres.
- Vizinhança: trocar 1 talhão do conjunto por 1 talhão livre fora dele.
- Função objetivo explícita e documentada. Exemplo: risco de praga dos talhões
  escolhidos menos a penalidade por tempo de deslocamento (bateria de 6 h). Gere o
  risco de forma determinística a partir da semente.
- 30 execuções de cada algoritmo, com sementes 0 a 29: média, desvio padrão e melhor valor.
- Conte quantas pioras a têmpera aceitou e mostre em quais execuções ela superou o
  ótimo local em que a subida de encosta ficou presa.

**Etapa 8 – Bônus DFS**
Construa À MÃO um pomar de até 8×8 em que a DFS (ordem N, S, O, L) devolva uma rota
com custo maior que o dobro do ótimo. Explique por que a ordem dos vizinhos "puxa"
a DFS para o caminho caro. Mostre a grade, as duas rotas e os dois custos.

**Etapa 9 – Sistema especialista**
- De 5 a 8 regras SE…ENTÃO sobre manejo de talhão, com encadeamento para trás.
  O programa imprime a cadeia de regras ("por que concluí isso?").
- Mostre um caso real do domínio que a base classifica errado, adicione uma regra
  que corrige sem contradizer as outras e imprima o traço ANTES e DEPOIS.

**Etapa 10 – Bayes** (usando parametros_sensor(semente))
(a) P(infestado | positivo), com a substituição na fórmula;
(b) quantos em cada 100 alertas são falsos;
(c) alertas falsos por semana e horas perdidas (12 min por inspeção);
(d) o novo VPP com sensibilidade de 99,9%, e qual parâmetro realmente importa e por quê;
(extra) o VPP de dois positivos seguidos, supondo independência, para a auditoria.

**Etapa 11 – main.py**
`python src/main.py <matricula>` gera resultados.csv, grafico.png e pomar.txt do zero
e imprime um resumo. Teste com 20231045 e com a semente da dupla.

# DOCUMENTAÇÃO (Etapas 12a, 12b, 12c) – EXPLIQUE COMO UM PROFESSOR PACIENTE

## RELATORIO.md
Organize por Partes 1 a 6. Em cada item, use sempre este formato:
- **O que foi pedido** (1 frase)
- **Como fizemos** (passo a passo simples, com analogia do dia a dia quando ajudar)
- **Resultado** (tabela com números reais e unidades)
- **O que isso significa** (2 a 4 frases)

Conteúdo específico:
- **Parte 1:** ficha PEAS com métrica mensurável e com unidade. Classifique o
  ambiente nas 6 dimensões, citando a frase do enunciado que sustenta cada uma, e
  aponte as 2 discutíveis (sugestão: determinístico e estático) dizendo qual
  informação resolveria a dúvida. Escolha o tipo de agente com justificativa
  concreta. Descreva uma métrica perversa com comportamento concreto e lugar no
  pomar, e depois a correção.
- **Parte 2:** os 5 componentes do problema e o número de estados (talhões não
  bloqueados, contados no pomar real). Tabela BFS/DFS/UCS. Explicação da 2.3 (a BFS
  supõe custo uniforme por passo). Resultado da 2.4 ligado à fórmula.
- **Parte 3:** tabela h1/h2/h3, prova de admissibilidade de h2 (custo mínimo de
  entrada = 1), par de coordenadas da h3, resposta formal da 3.3 (um custo igual NÃO
  prova admissibilidade) e uma condição de negócio verificável. Busca local com a
  explicação de por que aceitar piora ajuda. Bônus DFS.
- **Parte 4:** regras, traços de execução e contas de Bayes com a fórmula substituída.
- **Parte 5:** as 5 afirmações do laudo, cada uma com veredito, teoria e o NÚMERO
  medido pela dupla. Recomendação final em no máximo 8 linhas.

## README.md (nesta ordem exata)
1. Identificação (disciplina, período, nomes, matrículas, semente)
2. O que o projeto faz (3 a 5 linhas)
3. Como rodar (versão do Python, pip install -r requirements.txt, comando copiável,
   com comandos para Windows)
4. Tabela-resumo: custo, passos, nós expandidos e fronteira máxima por estratégia
5. Ordem dos vizinhos e se o A* reabre nós
6. Mapa do repositório, com uma linha por arquivo e links para RELATORIO.md e ANEXO_IA.md
7. Limitações conhecidas (seja honesto)

## ANEXO_IA.md – NÃO FABRIQUE NADA
Crie apenas o esqueleto com as seções A.1 a A.4 e instruções para a dupla preencher
com fatos reais. Numa seção "Erros detectados durante o desenvolvimento", registre
honestamente qualquer erro seu que a validação com 20231045 tenha revelado ao longo
das etapas, para a dupla verificar e usar no item A.3.

## COMO_EXPLICAR.md
- As 10 perguntas mais prováveis do professor, com respostas curtas.
- Um roteiro de 10 minutos para rodar o código com uma semente nova e preencher UCS
  e A* na lousa.

# COMECE AGORA
Comece pela Etapa 1 e pare ao final dela, aguardando "commit feito".
````

**Resposta recebida:**

````text
✅ ETAPA 1 CONCLUÍDA

Antes de tudo: os dados da dupla no seu prompt ainda estão como `<nome completo>`, `<xxxx>`. Não inventei nada. Esses dados só entram no README (Etapa 12b), então por enquanto não atrapalham.

**Arquivos criados**
- `src/gerador_pomar.py`: cópia do código do enunciado, sem nenhuma mudança na lógica.
- `.gitignore`: ignora `venv/`, `.venv/`, `__pycache__/` e `*.pyc`.
- `requirements.txt`: só `matplotlib>=3.7`, que é a única dependência externa.
- `resultados/.gitkeep`: o Git não guarda pasta vazia, então esse arquivo mantém `resultados/` no repositório até o `main.py` gerar os arquivos de verdade.

**Como testar (PowerShell, na pasta `C:\dev\caatinga-ai-sprint1`)**
```powershell
pip install -r requirements.txt
python src/gerador_pomar.py 20231045
```

**Saída esperada:** uma grade 12×12 começando com `. . ~ . . ~ . ~ . . . .` e terminando com `. ~ ~ . . . ~ . . # . .`, e depois:
`{'prevalencia': 0.0337, 'sensibilidade': 0.99, 'taxa_falso_positivo': 0.03, 'talhoes_por_semana': 1200}`

**Explicação simples:** o gerador funciona como um "contrato" com o professor. Com a mesma matrícula, ele sempre gera o mesmo pomar, porque o `random.Random(semente)` é determinístico. Por isso ele fica intacto e os outros módulos só vão importá-lo. Para conferir se a cópia está fiel, rodei um Dijkstra rápido e descartável, fora do repositório, com a semente 20231045. Deu **custo ótimo 34**, igual à caixa de aferição.

**Três pontos para conferir**
1. **Espaços no gerador:** o texto extraído do PDF perde o alinhamento dos espaços, então reconstruí a indentação pela imagem do enunciado (4 espaços, e os `j += 1` alinhados). O resultado bate, mas se o professor distribuiu um `.py` original, comparem os dois arquivos com `git diff --no-index`. A regra diz "sem alterar uma vírgula", e o que vale é o arquivo do professor.
2. **matplotlib não está instalado nesta máquina.** Rodem o `pip install -r requirements.txt` acima antes da Etapa 11.
3. **Identidade do Git:** nesta máquina o Git está configurado como `Paulo <paulotjr20080@gmail.com>`, e o `origin` aponta para `LucasNeriP/caatinga-ai-sprint1`. Cada integrante deve configurar a própria identidade no próprio computador:
   ```powershell
   git config user.name "<nome completo>"
   git config user.email "<email da conta GitHub>"
   ```

**Commit: quem faz é o Integrante A**
```powershell
git add .gitignore requirements.txt src/gerador_pomar.py resultados/.gitkeep
git commit -m "cria estrutura do repositório e adiciona gerador_pomar intacto"
git push
```

⏸️ Aguardando confirmação. Responda **"commit feito"** para eu seguir para a Etapa 2 (BFS e DFS com os 4 contadores).
````

### Prompt 2

````text
se paramos na etapa 3 (3.3), por que vamos pular para a 6?
````

**Resposta recebida:**

````text
Não estamos pulando nada. Há dois sistemas de numeração misturados: o **3.3 é item do enunciado** (Parte 3, pergunta 3.3), e a **"Etapa 6" é o número na nossa lista de commits**. Vocês pararam no item 3.3 do enunciado, e o próximo item é o **3.4 (busca local)**. É justamente isso que chamei de Etapa 6.

Por que o número da etapa andou mais rápido que o do enunciado:

| Etapa (nossa lista) | Item do enunciado | Situação |
|---:|---|---|
| 1 | estrutura do repositório | ✅ Integrante A |
| 2 | 2.2: BFS e DFS | ✅ Integrante A |
| 3 | 2.2: UCS e aferição | ✅ Integrante B |
| 4 | 2.4: escalonamento de n | ✅ Integrante B |
| 5 | 3.1: A* com h1, h2 e h3 | ✅ Integrante B |
| ~~6 original~~ | 3.2: par de talhões em que h3 superestima | ✅ já está no relatório do B: (0,0)→(11,11), 88 > 48 |
| **6 (nova)** | **3.4: busca local** | ⏭️ próximo |

O Integrante B fez de uma vez o que seriam as Etapas 3, 4 e 5 do plano original, e ainda escreveu o relatório das Partes 1, 2, 3.1, 3.2 e 3.3. A antiga Etapa 6 era só um programa para achar automaticamente onde h3 superestima. Como o relatório já mostra esse par com os dois números, que é o que o 3.2 exige, ela ficou desnecessária. Por isso renumerei o que falta a partir de 6.

Então a sequência continua do ponto onde vocês pararam: **3.4 (busca local)**, depois o bônus da DFS, e em seguida as Partes 4 e 5.

Se preferirem, posso usar o número do item do enunciado no nome de cada etapa daqui para frente, por exemplo "Etapa 3.4 – Busca local". Assim não há confusão. Posso começar a 3.4?
````

## A.3 Erros, imprecisões ou invenções do assistente

### Item escolhido: afirmação falsa sobre a fronteira da BFS

**O que o assistente afirmou.** No rascunho do `COMO_EXPLICAR.md`, respondendo à
pergunta "por que a fronteira máxima da BFS é esse número e não o dobro?", o
assistente escreveu que, numa grade 12 x 12, a fila da BFS guarda uma diagonal
"com no máximo 12 talhões".

**A evidência que desmentiu.** Rodamos a BFS com a matrícula de aferição:

```text
> python src/buscas.py 20231045
Estratégia    Custo  Passos  Expandidos  Fronteira máx.  Tempo (ms)
BFS              55      22         114              13        0.28
```

A fronteira máxima é **13**, maior que 12. O limite "no máximo 12" é falso: a
fila guarda a camada de talhões a d passos do portão **e o começo da camada
d + 1**, e na transição entre camadas passa do tamanho de uma diagonal. A
resposta foi corrigida no `COMO_EXPLICAR.md` antes da entrega.

### Outros erros registrados durante o desenvolvimento

1. **Busca local calibrada errado (primeira versão).** A primeira versão usava
   10 min por inspeção. A bateria nunca limitava a escolha (o melhor conjunto
   gastava 239 de 360 min), o problema virava "pegar os 15 maiores riscos" e as
   duas buscas davam 1418,1 em todas as 30 execuções: subida com desvio 0, e a
   têmpera empatava ou perdia (0 vitórias, 11 derrotas). Não havia ótimo local
   para demonstrar a Aula 04. Corrigido para 20 min por inspeção.
2. **Penalidade que deixava estourar a bateria.** Com 5 pontos de penalidade por
   minuto excedido, o melhor conjunto usava **363 min de 360**: compensava
   "comprar" minutos extras. O robô pararia no meio do pomar. Corrigido para
   100 pontos por minuto; o melhor conjunto passou a usar 360 de 360.
3. **Têmpera simulada mal ajustada.** Com 3.000 iterações e T inicial 30, a
   têmpera não era melhor que a subida: em 10 execuções com a nossa semente,
   5 vitórias e 5 derrotas. Com 20.000 iterações passou a 9 vitórias e
   1 derrota. Depois do ajuste da penalidade (item 2), T inicial 30, 100 e 300
   foram comparados em 3 sementes com 30 execuções cada; T = 300 teve a maior
   média e menos derrotas nas três, e foi o valor adotado.
4. **Regra que nunca disparava no sistema especialista.** A primeira R7 era
   `SE sensor_positivo ENTAO monitorar`. Rodando todos os casos, ela nunca
   decidia nada, porque R5 ou R6 concluíam antes. Foi trocada por
   `SE suspeita_confirmada ENTAO inspecionar_prioridade_alta`, que decide o
   caso F.
5. **Gerador reconstruído a partir do PDF.** O texto extraído do PDF perdeu os
   espaços de alinhamento de `gerador_pomar.py`; o assistente reconstruiu a
   indentação pela imagem. A cópia foi validada pelo custo ótimo 34 na
   matrícula 20231045.
6. **Contagem de nós expandidos da UCS** deu 111, e a referência é ~112. A
   diferença é o nó objetivo, que o nosso código não conta como expandido;
   está dentro dos ±20% permitidos, mas é uma divergência real.

## A.4 O que sabíamos depois de rodar o código que não sabíamos lendo a resposta

**PREENCHER**
