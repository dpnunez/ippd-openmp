# Tarefa D — Organização de Região Paralela

## Objetivo

Comparar o **overhead de criação de threads** entre duas abordagens de paralelização com OpenMP:

- **Versão Ingênua**: Dois `#pragma omp parallel for` consecutivos
- **Versão Arrumada**: Uma única região `#pragma omp parallel` contendo dois `#pragma omp for`

## O Problema

Quando temos múltiplos loops que podem ser paralelizados, existem duas formas de estruturar o código:

### Abordagem Ingênua (dois `parallel for`)

```c
// Cria equipe de threads
#pragma omp parallel for
for (int i = 0; i < n; i++) {
    y[i] = sin(x[i]) * cos(x[i]) + sqrt(x[i]);
}
// Destrói equipe de threads (barrier + fork/join)

// Cria equipe de threads NOVAMENTE
#pragma omp parallel for
for (int i = 0; i < n; i++) {
    z[i] = log(y[i] + 1) * exp(-y[i] * 0.01);
}
// Destrói equipe de threads novamente
```

**Problema**: A equipe de threads é criada e destruída **duas vezes**, gerando overhead de fork/join desnecessário.

### Abordagem Arrumada (um `parallel` com dois `for`)

```c
// Cria equipe de threads UMA VEZ
#pragma omp parallel
{
    #pragma omp for
    for (int i = 0; i < n; i++) {
        y[i] = sin(x[i]) * cos(x[i]) + sqrt(x[i]);
    }
    // Barrier implícito (threads sincronizam, mas não são destruídas)
    
    #pragma omp for
    for (int i = 0; i < n; i++) {
        z[i] = log(y[i] + 1) * exp(-y[i] * 0.01);
    }
}
// Destrói equipe de threads apenas aqui
```

**Vantagem**: A equipe de threads é criada apenas **uma vez**, e reutilizada para ambos os loops.

## Kernel Utilizado

Dois processamentos com carga computacional significativa (funções matemáticas):

```
Loop 1: y[i] = sin(x[i]) * cos(x[i]) + sqrt(x[i])
Loop 2: z[i] = log(y[i] + 1) * exp(-y[i] * 0.01)
```

Este kernel é **compute-bound** (limitado por processamento), permitindo observar benefícios reais do paralelismo.

## Versões Implementadas

| Versão | Descrição | Criações de Threads |
|--------|-----------|---------------------|
| **seq** | Sequencial (baseline) | 0 |
| **ingenua** | Dois `#pragma omp parallel for` | 2 |
| **arrumada** | Um `#pragma omp parallel` com dois `for` | 1 |

---

## Metodologia

### Parâmetros de Teste

| Parâmetro | Valores |
|-----------|---------|
| N (tamanho dos vetores) | 100.000, 500.000, 1.000.000 |
| Threads | 1, 2, 4, 8, 16 |
| Execuções por ponto | **5** |
| Semente aleatória | 42 |

### Métricas Coletadas

- **Tempo médio**: média de 5 execuções
- **Desvio padrão**: variabilidade entre execuções
- **Speedup**: `Tempo_seq / Tempo_versão`
- **Overhead relativo**: `(Tempo_ingenua - Tempo_arrumada) / Tempo_arrumada × 100%`

---

## Estrutura de Arquivos

```
src/parallel_region/
├── seq/
│   └── parallel_region.c    # Versão baseline
├── omp/
│   └── parallel_region.c    # Versões ingênua e arrumada
├── Makefile
├── run.sh
├── plot.py
└── README.md

results/parallel_region/
├── charts/                   # Gráficos PNG
└── table/
    └── results.csv           # Dados brutos
```

## Como Executar

```bash
cd src/parallel_region

# Compilar
make all

# Executar experimentos
make run

# Gerar gráficos
make plot

# Limpar
make clean
```

---

## Resultados

Os resultados detalhados desta tarefa estão disponíveis em:

- **Análise completa**: [`../../RESULTADOS.md`](../../RESULTADOS.md#tarefa-d--organização-de-região-paralela)
- **Reprodutibilidade**: [`../../REPRODUCIBILIDADE.md`](../../REPRODUCIBILIDADE.md)

### Resumo

| Versão | Melhor Speedup | Observação |
|--------|----------------|------------|
| Arrumada | ~4.7x (16 threads) | 1 fork/join |
| Ingênua | ~3.9x (16 threads) | 2 fork/join |

**Conclusão**: Organizar código para minimizar fork/join resulta em ~20% de ganho.

### Gráficos Gerados

Os gráficos são salvos em `../../results/parallel_region/charts/`:
- `grafico1_comparacao_versoes.png` - Comparação ingênua vs arrumada
- `grafico2_overhead_relativo.png` - Overhead da versão ingênua
- `grafico3_speedup_sequencial.png` - Speedup sobre sequencial
- `grafico4_tempo_absoluto.png` - Tempo absoluto vs threads

### Boas Práticas

1. **Minimize regiões paralelas**: Agrupe loops dentro de uma única região `parallel`
2. **Use `#pragma omp for`** (sem `parallel`) quando já está dentro de região paralela
3. **Use `nowait`** quando possível para remover barrier desnecessário:

```c
#pragma omp parallel
{
    #pragma omp for nowait  // Sem barrier no final
    for (...) { ... }
    
    #pragma omp for
    for (...) { ... }
}
```
