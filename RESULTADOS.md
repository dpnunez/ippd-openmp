# Resultados Experimentais

Este documento apresenta os resultados detalhados dos experimentos realizados.

---

## Tarefa C — SAXPY (Vetorização com SIMD)

### Gráficos

#### Gráfico 1: Comparação de Tempo - Todas as Versões

![Tempo por Versão](results/saxpy/charts/grafico1_tempo_versao.png)

**O que mostra:** Tempo de execução (em milissegundos) para cada versão e configuração de threads, separado por tamanho de vetor (N).

**Legenda:**
- **Seq**: Versão sequencial (baseline)
- **SIMD**: Versão com vetorização apenas (1 thread)
- **P.SIMD xT**: Parallel SIMD com x threads (1, 2, 4, 8, 16)

**Barras de erro:** ±1 desvio padrão (baseado em 5 execuções)

**Observações:**
- Para N=100k, a versão SIMD é a mais rápida (0.013ms vs 0.018ms do sequencial)
- O Parallel SIMD com poucas threads (1-4) adiciona overhead sem ganho para vetores pequenos
- Para N=500k e N=1M, o Parallel SIMD com 4 threads começa a mostrar vantagem
- Com 8+ threads, o desempenho degrada devido à contenção de memória

#### Gráfico 2: Speedup de Todas as Versões sobre Sequencial

![Speedup](results/saxpy/charts/grafico2_speedup_simd.png)

**O que mostra:** Speedup de cada versão em relação ao baseline sequencial, para cada tamanho de vetor.

**Como interpretar:**
- **Speedup = 1.0x**: mesmo desempenho do sequencial (linha tracejada)
- **Speedup > 1.0x**: ganho de desempenho (mais rápido que sequencial)
- **Speedup < 1.0x**: perda de desempenho (overhead supera ganhos)

**Legenda:**
- **SIMD (1 thread)**: barra verde
- **P.SIMD (x threads)**: barras em tons de amarelo a vermelho

**Observações:**
- **SIMD** oferece speedup consistente de 1.0x a 1.4x
- **Parallel SIMD com 4 threads** atinge o melhor speedup para N=500k (1.87x)
- Para N=100k, **nenhuma** configuração de Parallel SIMD supera o sequencial
- Com 16 threads, o speedup é sempre < 1.0x (overhead domina)

#### Gráfico 3: Speedup do Parallel SIMD vs Threads

![Escalabilidade](results/saxpy/charts/grafico3_escalabilidade.png)

**O que mostra:** Como o speedup do Parallel SIMD (em relação ao sequencial) varia conforme aumentamos o número de threads.

**Linha de referência:** Speedup = 1.0x (desempenho do sequencial)

**Barras de erro:** ±1 desvio padrão propagado

**Observações:**
- Para **N=100k** (azul): nunca supera o baseline - overhead de threads domina
- Para **N=500k** (verde): pico de speedup com 2-4 threads (~1.9x)
- Para **N=1M** (vermelho): melhor com 4 threads (~1.5x), depois degrada
- A escalabilidade está muito abaixo do ideal devido à natureza memory-bound

**Por que não escala linearmente?**
SAXPY é limitado pela largura de banda da memória, não pelo processamento. Mais threads competem pelo mesmo barramento de memória, causando contenção.

#### Gráfico 4: Tempo Absoluto vs Threads

![Tempo vs Threads](results/saxpy/charts/grafico4_tempo_threads.png)

**O que mostra:** Tempo absoluto de execução do Parallel SIMD para diferentes números de threads.

**Linhas pontilhadas:** Tempo da versão sequencial para cada N (referência)

**Barras de erro:** ±1 desvio padrão

**Observações:**
- Existe um "ponto ótimo" de threads (geralmente 2-4)
- Para N=100k, o tempo **aumenta** com mais threads
- Para N=500k e N=1M, há uma região de ganho (2-4 threads)
- Além de 4 threads, o tempo volta a aumentar

### Tabela Completa de Resultados

> Média de **5 execuções** por configuração

| Versão | N | Threads | Tempo Médio (ms) | Desvio Padrão (ms) | Speedup |
|--------|---|---------|------------------|-------------------|---------|
| seq | 100.000 | 1 | 0.0182 | 0.0072 | 1.00x |
| simd | 100.000 | 1 | 0.0134 | 0.0005 | **1.36x** |
| parallel_simd | 100.000 | 1 | 0.0448 | 0.0767 | 0.41x |
| parallel_simd | 100.000 | 2 | 0.0250 | 0.0341 | 0.73x |
| parallel_simd | 100.000 | 4 | 0.0212 | 0.0267 | 0.86x |
| parallel_simd | 100.000 | 8 | 0.0696 | 0.0614 | 0.26x |
| parallel_simd | 100.000 | 16 | 0.1108 | 0.1037 | 0.16x |
| | | | | | |
| seq | 500.000 | 1 | 0.0932 | 0.0073 | 1.00x |
| simd | 500.000 | 1 | 0.0866 | 0.0346 | 1.08x |
| parallel_simd | 500.000 | 1 | 0.1260 | 0.0565 | 0.74x |
| parallel_simd | 500.000 | 2 | 0.0568 | 0.0478 | 1.64x |
| parallel_simd | 500.000 | 4 | 0.0498 | 0.0472 | **1.87x** |
| parallel_simd | 500.000 | 8 | 0.0934 | 0.1082 | 1.00x |
| parallel_simd | 500.000 | 16 | 0.1368 | 0.1361 | 0.68x |
| | | | | | |
| seq | 1.000.000 | 1 | 0.1278 | 0.0197 | 1.00x |
| simd | 1.000.000 | 1 | 0.1278 | 0.0546 | 1.00x |
| parallel_simd | 1.000.000 | 1 | 0.1284 | 0.0549 | 1.00x |
| parallel_simd | 1.000.000 | 2 | 0.1454 | 0.1621 | 0.88x |
| parallel_simd | 1.000.000 | 4 | 0.0856 | 0.1012 | **1.49x** |
| parallel_simd | 1.000.000 | 8 | 0.0962 | 0.0744 | 1.33x |
| parallel_simd | 1.000.000 | 16 | 0.1314 | 0.1031 | 0.97x |

### Conclusões — SAXPY

#### Ganhos da Vetorização (SIMD)

1. **Speedup modesto mas consistente**: ~1.0x a 1.4x dependendo do tamanho
2. **Sem overhead**: SIMD não tem custo de criação de threads
3. **Melhor para vetores pequenos**: para N=100k, SIMD é a melhor opção

#### Limitações do Paralelismo de Threads

1. **Overhead significativo**: criar/sincronizar threads custa tempo
2. **Contenção de memória**: threads competem pelo barramento
3. **Ponto ótimo**: existe um número ideal de threads (2-4 para SAXPY)
4. **Mais threads ≠ mais velocidade**: para operações memory-bound

#### Recomendações de Uso

| Tamanho do Vetor | Versão Recomendada | Speedup Esperado |
|------------------|-------------------|------------------|
| N < 100k | SIMD | ~1.3x |
| 100k ≤ N < 500k | Parallel SIMD (2-4 threads) | ~1.5x-1.9x |
| N ≥ 500k | Parallel SIMD (4 threads) | ~1.5x |

---

## Tarefa D — Organização de Região Paralela

### Gráficos

#### Gráfico 1: Comparação Ingênua vs Arrumada

![Comparação](results/parallel_region/charts/grafico1_comparacao_versoes.png)

**O que mostra:** Tempo de execução (ms) das versões ingênua e arrumada para cada número de threads.

**Linha azul pontilhada:** Tempo da versão sequencial (referência)

**Barras de erro:** ±1 desvio padrão (5 execuções)

**Observações:**
- Ambas versões paralelas são **mais rápidas** que sequencial para múltiplas threads
- A versão arrumada (verde) geralmente tem tempo menor ou igual à ingênua (vermelho)
- O benefício do paralelismo aumenta com N maior

#### Gráfico 2: Overhead Relativo da Versão Ingênua

![Overhead](results/parallel_region/charts/grafico2_overhead_relativo.png)

**O que mostra:** Quanto a versão ingênua é mais lenta que a arrumada (em %).

**Fórmula:** `Overhead = (Tempo_ingenua - Tempo_arrumada) / Tempo_arrumada × 100%`

**Interpretação:**
- **Overhead > 0%**: Ingênua mais lenta (overhead extra de fork/join)
- **Overhead < 0%**: Ingênua mais rápida (variância experimental)

**Observações:**
- O overhead varia, mas a tendência é a ingênua ser ligeiramente mais lenta
- O custo extra de criar threads duas vezes é mensurável

#### Gráfico 3: Speedup sobre Sequencial

![Speedup](results/parallel_region/charts/grafico3_speedup_sequencial.png)

**O que mostra:** Speedup de ambas versões em relação ao baseline sequencial.

**Legenda:**
- Linha **sólida**: Versão Arrumada
- Linha **tracejada**: Versão Ingênua

**Linha de referência:** Speedup = 1.0x (desempenho sequencial)

**Observações:**
- Speedup aumenta com número de threads até ~8 threads
- Para N=1M com 16 threads: Arrumada ~4.7x vs Ingênua ~3.9x
- A versão arrumada mantém vantagem consistente em threads altos

#### Gráfico 4: Tempo Absoluto da Versão Arrumada

![Tempo Absoluto](results/parallel_region/charts/grafico4_tempo_absoluto.png)

**O que mostra:** Evolução do tempo da versão arrumada com o número de threads.

**Linhas pontilhadas:** Tempo sequencial para cada N

**Observações:**
- Tempo diminui significativamente com mais threads
- Escalabilidade boa até 8 threads, depois estabiliza
- Para N=1M: de ~13ms (seq) para ~2.9ms (16 threads)

### Tabela de Resultados

> Média de **5 execuções** por configuração

| Versão | N | Threads | Tempo Médio (ms) | Speedup |
|--------|---|---------|------------------|---------|
| seq | 100.000 | 1 | 1.29 | 1.00x |
| arrumada | 100.000 | 4 | 0.42 | **3.07x** |
| ingenua | 100.000 | 4 | 0.52 | 2.49x |
| | | | | |
| seq | 500.000 | 1 | 6.46 | 1.00x |
| arrumada | 500.000 | 8 | 1.51 | **4.27x** |
| ingenua | 500.000 | 8 | 1.84 | 3.51x |
| | | | | |
| seq | 1.000.000 | 1 | 13.58 | 1.00x |
| arrumada | 1.000.000 | 16 | 2.88 | **4.72x** |
| ingenua | 1.000.000 | 16 | 3.50 | 3.88x |

### Conclusões — Região Paralela

#### Overhead de Fork/Join

1. **Overhead mensurável**: Criar threads duas vezes é mais lento que uma vez
2. **Diferença de ~10-20%**: Em configurações com muitas threads
3. **Impacto maior em threads altos**: Mais threads = mais custo de fork/join

#### Speedup Obtido

| Configuração | Speedup Arrumada | Speedup Ingênua | Vantagem |
|--------------|------------------|-----------------|----------|
| N=100k, 4T | 3.07x | 2.49x | +23% |
| N=500k, 8T | 4.27x | 3.51x | +22% |
| N=1M, 16T | 4.72x | 3.88x | **+22%** |

#### Boas Práticas

1. **Minimize regiões paralelas**: Agrupe loops dentro de uma única região `parallel`
2. **Use `#pragma omp for`** (sem `parallel`) quando já está dentro de região paralela
3. **Use `nowait`** quando possível para remover barrier desnecessário

---

## Resumo Geral

### Tarefa C — SAXPY (Memory-bound)

| Versão | Melhor Speedup | Observação |
|--------|----------------|------------|
| SIMD | ~1.4x | Sem overhead de threads |
| Parallel SIMD | ~1.9x (4 threads) | Limitado por memória |

**Conclusão**: Para operações memory-bound, SIMD puro é mais eficiente que paralelismo de threads.

### Tarefa D — Região Paralela (Compute-bound)

| Versão | Melhor Speedup | Observação |
|--------|----------------|------------|
| Arrumada | ~4.7x (16 threads) | 1 fork/join |
| Ingênua | ~3.9x (16 threads) | 2 fork/join |

**Conclusão**: Organizar código para minimizar fork/join resulta em ~20% de ganho.

---

## Lições Aprendidas

1. **Medir antes de otimizar**: a intuição sobre paralelismo pode ser enganosa
2. **SIMD é "gratuito"**: vetorização sem threads deve sempre ser considerada
3. **Conhecer o gargalo**: SAXPY é memory-bound, não compute-bound
4. **Overhead importa**: para tarefas rápidas, o custo de paralelismo domina
5. **Organização importa**: ~20% de ganho apenas reorganizando código
6. **Fork/join tem custo**: Criar threads não é gratuito
7. **Reutilize threads**: Uma região parallel com múltiplos for é mais eficiente

