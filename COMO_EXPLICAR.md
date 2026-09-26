# Como explicar - guia para a arguição

## Roteiro de 10 minutos com uma semente nova

A tarefa na lousa é preencher as linhas do **UCS** e do **A\***. Tenham o
repositório clonado, o Python funcionando e o `pip install` já feito **antes**
da aula.

| Minuto | O que fazer | Comando |
|---:|---|---|
| 0 | Abrir o terminal na pasta do repositório | `cd caatinga-ai-sprint1` |
| 0-1 | Confirmar que o código está certo (deve dar 6 x `[OK]`) | `python src/aferir.py` |
| 1-2 | Rodar com a semente sorteada (troque `NNNNNNNN`) | `python src/main.py NNNNNNNN` |
| 2-4 | Copiar para a lousa as linhas `UCS` e `A* h1/h2/h3`: custo, passos, nós expandidos, fronteira máxima | (ler a tabela impressa) |
| 4-5 | Conferir: UCS, A* h1 e A* h2 **têm de ter o mesmo custo**; A* h1 deve ter os mesmos números do UCS; h3 pode dar custo maior | (a linha "Custo ótimo (UCS)" lista quem achou o ótimo) |
| 5-10 | Reserva para as duas perguntas | |

Se o `matplotlib` não estiver instalado e não der tempo de instalar, o comando
abaixo imprime a mesma tabela sem gerar gráfico:

```powershell
python src/buscas.py NNNNNNNN
```

Se a matrícula vier com pontos (`241.14.032`), o `main.py` aceita assim mesmo.
No Windows, se `python` não funcionar, use `py`.

## As 10 perguntas mais prováveis

**1. Por que a fronteira máxima da sua BFS é esse número e não o dobro?**
Porque a BFS marca o talhão como visto **ao gerar**, não ao expandir: cada estado
entra na fila no máximo uma vez. A fila só guarda a "onda": a camada de talhões
a d passos do portão e o começo da camada d + 1. Numa grade 12 x 12 cada camada
é parecida com uma diagonal, com cerca de 12 talhões, menos os bloqueados. No
nosso pomar deu 11 (com a semente 20231045 deu 13, porque a onda estava
passando de uma camada para a outra). O dobro só apareceria se o mesmo talhão
pudesse entrar duas vezes na fila, e a marcação na geração impede isso.

**2. Por que a DFS tem fronteira maior que a BFS (59 contra 11)?**
A nossa DFS marca o estado ao **expandir**. Um talhão pode ser empilhado várias
vezes antes de sair, e essas cópias contam na fronteira. Em n = 3600 a diferença
explode: 5.207.260 contra 3.205. A economia de memória O(b·m) vale para DFS em
árvore, não em grafo com conjunto de explorados.

**3. Qual a diferença entre estado e nó?**
Estado é a coordenada `(linha, coluna)`. Nó é o estado mais o pai e o custo
acumulado. Dois nós podem ter o mesmo estado (chegamos ao mesmo talhão por
caminhos diferentes); é daí que vem o laço infinito se não houver conjunto de
explorados.

**4. Por que a BFS testa o objetivo na geração e o UCS na expansão?**
Na BFS, o primeiro nó gerado com o objetivo já está na camada mais rasa, então
ele tem o menor número de passos. No UCS, quando o objetivo é gerado, ainda pode
existir na fila um caminho mais barato até ele; só quando ele **sai** da fila
(menor custo acumulado) temos a garantia de otimalidade.

**5. Por que a BFS devolveu rota mais cara que o UCS (55 contra 48)?**
A BFS minimiza passos, não custo. Ela só é ótima em custo se todo passo custar
o mesmo, e aqui `.` custa 1 e `~` custa 4. A hipótese violada é a do custo
uniforme por passo.

**6. Seu A\* reabre nós? Como?**
Sim. O dicionário `melhor_custo` guarda o menor g conhecido de cada estado.
Quando aparece um caminho mais barato, o estado entra de novo na fila com o novo
custo; ao sair, uma entrada cujo custo não é o melhor conhecido é descartada.

**7. Por que h2 é admissível e h3 não?**
h2: cada movimento reduz a distância de Manhattan em no máximo 1, e o menor custo
de entrada é 1, então o custo real restante é pelo menos a distância de
Manhattan. h3 = 4 x Manhattan: do portão, h3 = 4 x 22 = 88, mas o custo ótimo
real é 48. Como 88 > 48, h3 superestima.

**8. Se h3 der o custo ótimo com a semente nova, ela é admissível?**
Não. Admissibilidade vale para **todos** os estados; um acerto numa instância
não prova nada, e um único contraexemplo refuta. Com 20231045 a h3 deu 34 (igual
ao ótimo) e com 24114032 deu 54 (ótimo 48).

**9. Por que a têmpera simulada aceita pioras? Por que 30 execuções?**
A subida de encosta para no primeiro topo, porque todo vizinho é pior. Aceitar
piora com probabilidade `exp(delta / T)` deixa o agente descer de um morro e
subir em outro mais alto; T alto no começo explora, T baixo no fim refina. Os
resultados são aleatórios: numa execução isolada a têmpera pode perder (semente
16); a média de 30 mostra o efeito (1307,7 contra 1267,8, e 18 execuções no
melhor valor contra 3).

**10. Por que só 34% dos alertas do sensor são reais, se a sensibilidade é 99%?**
Porque a praga é rara (4%). Em 1000 talhões: 40 infestados geram cerca de 40
alertas verdadeiros; 960 sadios, com 8% de falso positivo, geram cerca de 77
falsos. 40 / 117 = 34%. Para melhorar, baixa-se a taxa de falso positivo (0,01
daria 80,5%), não se aumenta a sensibilidade (99,9% daria só 34,2%).

## Perguntas extras que podem aparecer

- **Quantos estados tem o espaço?** 115: os talhões não bloqueados do nosso
  pomar (144 - 29), todos alcançáveis a partir do portão.
- **Por que a ordem N, S, O, L importa?** Ela decide o caminho da DFS. No
  contraexemplo, o Sul vem antes do Leste, e a DFS desce pelo lado encharcado:
  custo 53 contra 14.
- **O que é negação por falha?** Na R5, `NAO armadilha_positiva` é verdadeiro
  quando o programa não consegue provar que a armadilha capturou algo (hipótese
  do mundo fechado).
- **Por que a R8 não contradiz a R4?** Ela é mais específica: exige tudo o que a
  R4 exige e mais a colheita a menos de 15 dias. É testada antes, e nos outros
  seis casos o diagnóstico não muda.
- **Onde falhou o experimento de escala?** Em n = 3800 a DFS passou de 60 s de
  busca. Custo O(V + E) = O(n²) para a busca em grafo; em n = 3600 a BFS já
  expandia 10.350.249 estados.
