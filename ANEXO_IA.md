# Anexo - Uso de assistentes de IA

> **Para a dupla:** este arquivo é um esqueleto. As seções marcadas com
> **PREENCHER** só podem ser escritas por vocês, com fatos reais. A seção
> "Erros detectados durante o desenvolvimento" lista o que realmente aconteceu
> nas sessões do Paulo com o Claude Code; confiram cada item rodando o código
> antes de usá-lo no A.3. Apaguem esta nota e as instruções em itálico antes da
> entrega. Anexo genérico ou fabricado zera as Partes 5 e 6.

## A.1 Ferramentas usadas e em que partes

| Integrante | Ferramenta | Partes do trabalho |
|---|---|---|
| Paulo | Claude Code (modelo Claude Opus 5.5), no terminal do Windows | Estrutura do repositório e BFS/DFS (Etapas 1 e 2); busca local (3.4); contraexemplo da DFS (bônus); sistema especialista (4.1 e 4.2); Bayes (4.3); `main.py`; redação das Partes 3.4, 4 e 5 do relatório; este README; esqueleto deste anexo e o `COMO_EXPLICAR.md` |
| Lucas | **PREENCHER** | **PREENCHER** (UCS, aferição, experimento de escala, A*, relatório das Partes 1 a 3.3) |

*Descrevam também como usaram: o assistente escrevia o código numa pasta
temporária, mostrava a saída e só depois um de vocês copiava, rodava e fazia o
commit.*

## A.2 Dois prompts na íntegra, com a resposta recebida

*Copiem do histórico da sessão (o texto exato, sem editar). Sugestões de trocas
que mostram bem o processo:*

- *o prompt inicial com o PAPEL, as REGRAS INEGOCIÁVEIS e a TABELA DE ETAPAS, e a
  resposta da Etapa 1;*
- *a pergunta "se paramos na etapa 3 (3.3), por que vamos pular para a 6?" e a
  resposta, que explica a diferença entre a numeração das etapas e a do
  enunciado.*

### Prompt 1

```text
PREENCHER - colar o prompt exatamente como foi enviado
```

**Resposta recebida:**

```text
PREENCHER - colar a resposta exatamente como foi recebida
```

### Prompt 2

```text
PREENCHER
```

**Resposta recebida:**

```text
PREENCHER
```

## A.3 Erros, imprecisões ou invenções do assistente

*Escolham pelo menos um item da lista abaixo, rodem de novo para confirmar e
escrevam: o que o assistente afirmou ou fez, e a evidência do experimento que o
desmentiu.*

### Erros detectados durante o desenvolvimento

Registro do que o assistente (Claude Code) errou ou precisou corrigir nas
sessões do Paulo, com a evidência que revelou cada problema:

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
   matrícula 20231045, mas convém comparar com um arquivo original do
   professor, se houver.
6. **Contagem de nós expandidos da UCS** deu 111, e a referência é ~112. A
   diferença é o nó objetivo, que o nosso código não conta como expandido;
   está dentro dos ±20% permitidos, mas é uma divergência real.
7. **Afirmação falsa sobre a fronteira da BFS.** No rascunho do
   `COMO_EXPLICAR.md`, o assistente escreveu que a fronteira da BFS numa grade
   12 x 12 tem "no máximo 12 talhões" (uma diagonal). Rodando
   `python src/buscas.py 20231045`, a fronteira máxima da BFS é **13**, maior
   que 12: a fila guarda a camada atual e o começo da próxima. A resposta foi
   corrigida antes da entrega.

### Item escolhido para o A.3

**PREENCHER** - o que o assistente afirmou ou fez, e a evidência (comando,
número, saída) que mostrou o erro.

## A.4 O que sabíamos depois de rodar o código que não sabíamos lendo a resposta

**PREENCHER** - uma frase, escrita por vocês.

*Exemplos do tipo de frase esperada (não copiem, escrevam a de vocês): um número
que surpreendeu ao rodar, como a fronteira da DFS ser maior que a da BFS, ou a
h3 acertar o custo ótimo numa semente e errar na outra.*
