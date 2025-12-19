# OpenMP na Prática

**Disciplina:** Introdução à Programação Paralela e Distribuída (IPPD)  
**Instituição:** Universidade Federal de Pelotas (UFPel)

---

## Alunos

| Nome | Matrículas |
|------|-------------------|
| **Daniel Núñez** | 20202019 |
| **Bruno Silveira** | 20200909 |

---

## Descrição do Projeto

Este repositório contém a implementação de atividades práticas com **OpenMP**, focando em:

- Paralelização de laços e escolhas de schedule
- Uso de diretivas SIMD para vetorização
- Organização de regiões paralelas para minimizar overhead
- Análise de desempenho com métricas e gráficos

---

## Tarefas Implementadas

| Tarefa | Descrição | Diretório |
|--------|-----------|-----------|
| **Tarefa C** | Vetorização com SIMD (SAXPY) | [`src/saxpy/`](src/saxpy/) |
| **Tarefa D** | Organização de Região Paralela | [`src/parallel_region/`](src/parallel_region/) |

### Tarefa C — Vetorização com SIMD

Implementação da operação SAXPY (`y = a*x + y`) comparando:
- **V1**: Versão sequencial
- **V2**: `#pragma omp simd` (vetorização)
- **V3**: `#pragma omp parallel for simd` (paralelismo + vetorização)

[Documentação completa](src/saxpy/README.md)

### Tarefa D — Organização de Região Paralela

Comparação de overhead entre duas abordagens:
- **Ingênua**: Dois `#pragma omp parallel for` consecutivos
- **Arrumada**: Uma região `#pragma omp parallel` com dois `#pragma omp for`

[Documentação completa](src/parallel_region/README.md)

---

## Estrutura do Repositório

```
openmp-trabalho/
├── README.md                    # Este arquivo
├── RESULTADOS.md                # Análise detalhada dos resultados
├── REPRODUCIBILIDADE.md         # Informações para reproduzir experimentos
├── run_all.sh                   # Script para executar tudo
├── docs/
│   └── descricao.md             # Enunciado da atividade
│
├── src/
│   ├── saxpy/                   # Tarefa C - SAXPY com SIMD
│   │   ├── seq/                 # Código V1
│   │   ├── omp/                 # Código V2 e V3
│   │   ├── Makefile
│   │   ├── run.sh
│   │   ├── plot.py
│   │   └── README.md            # Documentação da tarefa
│   │
│   └── parallel_region/         # Tarefa D - Região Paralela
│       ├── seq/                 # Código baseline
│       ├── omp/                 # Código ingênua e arrumada
│       ├── Makefile
│       ├── run.sh
│       ├── plot.py
│       └── README.md            # Documentação da tarefa
│
└── results/                     # Resultados gerados
    ├── saxpy/
    │   ├── charts/              # Gráficos PNG
    │   └── table/               # CSV com dados
    │
    └── parallel_region/
        ├── charts/              # Gráficos PNG
        └── table/               # CSV com dados
```

---

## Como Executar

### Requisitos

- **Compilador**: GCC ou Clang com suporte a OpenMP
- **macOS**: `brew install libomp`
- **Python 3** com matplotlib: `pip install matplotlib`

### Executar tudo de uma vez

```bash
# Compila e executa todos os exercícios
./run_all.sh

# Com limpeza prévia
./run_all.sh --clean

# Sem gerar gráficos (mais rápido)
./run_all.sh --no-plot
```

### Executar tarefa individual

```bash
# Tarefa C - SAXPY
cd src/saxpy
make run    # Compila e executa experimentos
make plot   # Gera gráficos

# Tarefa D - Região Paralela
cd src/parallel_region
make run    # Compila e executa experimentos
make plot   # Gera gráficos
```

### Comandos disponíveis em cada tarefa

| Comando | Descrição |
|---------|-----------|
| `make all` | Compila todas as versões |
| `make seq` | Compila versão sequencial |
| `make omp` | Compila versão OpenMP |
| `make run` | Executa matriz de experimentos |
| `make plot` | Gera gráficos a partir dos resultados |
| `make clean` | Remove executáveis e resultados |
| `make help` | Mostra ajuda |

---

## Documentação Adicional

| Documento | Descrição |
|-----------|-----------|
| [`RESULTADOS.md`](RESULTADOS.md) | Análise detalhada dos resultados experimentais |
| [`REPRODUCIBILIDADE.md`](REPRODUCIBILIDADE.md) | Versão do compilador, flags, CPU, afinidade, semente |

---

## Resumo dos Resultados

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

**Para análise completa:** Veja [`RESULTADOS.md`](RESULTADOS.md)

---

## Referências

- [OpenMP Specification](https://www.openmp.org/specifications/)
- [LLVM OpenMP Documentation](https://openmp.llvm.org/)
- Enunciado da atividade: [`docs/descricao.md`](docs/descricao.md)

