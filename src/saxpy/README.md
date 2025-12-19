# Tarefa C — Vetorização com SIMD

## Objetivo

Implementar e avaliar versões paralelas da operação **SAXPY** usando OpenMP, com foco em:

- Vetorização explícita com `#pragma omp simd`
- Combinação de paralelismo de threads com vetorização (`#pragma omp parallel for simd`)
- Análise de ganhos e limitações da vetorização

## O que é SAXPY?

SAXPY (*Single-precision A·X Plus Y*) é uma operação fundamental de álgebra linear definida como:

```
y[i] = a * x[i] + y[i]
```

Onde:
- `a` é um escalar (constante = 2.5)
- `x` e `y` são vetores de ponto flutuante (`float`)
- A operação é aplicada elemento a elemento

Esta operação é um exemplo clássico de computação **memory-bound** (limitada por memória), pois a intensidade aritmética é baixa: apenas 2 operações de ponto flutuante (multiplicação + soma) para cada 3 acessos à memória (2 leituras + 1 escrita).

## Versões Implementadas

### V1: Sequencial (`seq`)
Implementação básica com um loop sequencial simples.

```c
void saxpy_seq(float a, float *x, float *y, size_t n) {
    for (size_t i = 0; i < n; i++) {
        y[i] = a * x[i] + y[i];
    }
}
```

### V2: SIMD (`simd`)
Vetorização explícita usando a diretiva `#pragma omp simd`, que instrui o compilador a gerar código vetorizado (usando instruções SIMD como SSE, AVX, NEON).

```c
void saxpy_simd(float a, float *x, float *y, size_t n) {
    #pragma omp simd
    for (size_t i = 0; i < n; i++) {
        y[i] = a * x[i] + y[i];
    }
}
```

**Características:**
- Executa em uma única thread
- Processa múltiplos elementos por instrução (ex: 4 floats com SSE, 8 com AVX)
- Não tem overhead de criação de threads

### V3: Parallel SIMD (`parallel_simd`)
Combina paralelismo de threads com vetorização usando `#pragma omp parallel for simd`.

```c
void saxpy_parallel_simd(float a, float *x, float *y, size_t n) {
    #pragma omp parallel for simd
    for (size_t i = 0; i < n; i++) {
        y[i] = a * x[i] + y[i];
    }
}
```

**Características:**
- Divide o trabalho entre múltiplas threads
- Cada thread aplica vetorização SIMD em sua porção
- Potencial para maior speedup, mas com overhead de paralelismo

---

## Metodologia

### Parâmetros de Teste

Conforme especificado na atividade:

| Parâmetro | Valores |
|-----------|---------|
| N (tamanho do vetor) | 100.000, 500.000, 1.000.000 |
| Threads (para parallel_simd) | 1, 2, 4, 8, 16 |
| Execuções por ponto | **5** |
| Semente aleatória | 42 (reprodutibilidade) |

### Métricas Coletadas

Para cada combinação de parâmetros:

- **Tempo médio**: média aritmética de 5 execuções
- **Desvio padrão**: medida de variabilidade entre as execuções
- **Speedup**: razão entre o tempo sequencial e o tempo da versão testada
  - `Speedup = Tempo_sequencial / Tempo_versão`
  - Speedup > 1 indica ganho de desempenho
  - Speedup < 1 indica perda de desempenho (overhead maior que ganho)

### Controle de Variáveis

- Os vetores são inicializados com a mesma semente (42) para garantir reprodutibilidade
- O vetor `y` é restaurado antes de cada execução para garantir mesmas condições iniciais
- O tempo é medido usando `clock_gettime(CLOCK_MONOTONIC)` para alta precisão

---

## Estrutura de Arquivos

```
src/saxpy/
├── seq/
│   └── saxpy.c          # Versão V1
├── omp/
│   └── saxpy.c          # Versões V2 e V3
├── Makefile
├── run.sh               # Script de experimentos
├── plot.py              # Geração de gráficos
└── README.md            # Este arquivo

results/saxpy/
├── charts/              # Gráficos PNG
└── table/
    └── results.csv      # Dados brutos
```

## Como Executar

```bash
cd src/saxpy

# Compilar
make all

# Executar experimentos (gera CSV)
make run

# Gerar gráficos
make plot

# Limpar
make clean
```

**Requisitos:**
- GCC ou Clang com suporte a OpenMP
- macOS: `brew install libomp`
- Python 3 com matplotlib: `pip install matplotlib`

---

## Resultados

Os resultados detalhados desta tarefa estão disponíveis em:

- **Análise completa**: [`../../RESULTADOS.md`](../../RESULTADOS.md#tarefa-c--saxpy-vetorização-com-simd)
- **Reprodutibilidade**: [`../../REPRODUCIBILIDADE.md`](../../REPRODUCIBILIDADE.md)

### Resumo

| Versão | Melhor Speedup | Observação |
|--------|----------------|------------|
| SIMD | ~1.4x | Sem overhead de threads |
| Parallel SIMD | ~1.9x (4 threads) | Limitado por memória |

### Gráficos Gerados

Os gráficos são salvos em `../../results/saxpy/charts/`:
- `grafico1_tempo_versao.png` - Comparação de tempo entre versões
- `grafico2_speedup_simd.png` - Speedup sobre sequencial
- `grafico3_escalabilidade.png` - Speedup vs threads
- `grafico4_tempo_threads.png` - Tempo absoluto vs threads
