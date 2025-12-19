# Reproducibilidade

Este documento descreve o ambiente e parâmetros utilizados para garantir a reprodutibilidade dos experimentos.

---

## Compilador

| Item | Valor |
|------|-------|
| **Compilador** | Apple Clang 16.0.0 |
| **Comando** | `clang --version` |
| **Runtime OpenMP** | libomp 21.1.7 (via Homebrew) |

Para verificar:
```bash
clang --version
brew info libomp
```

---

## Flags de Compilação

```makefile
CFLAGS = -Wall -Wextra -O3 -march=native
OMP_FLAGS = -Xpreprocessor -fopenmp
LDFLAGS = -lm -lomp
```

| Flag | Propósito |
|------|-----------|
| `-O3` | Nível máximo de otimização |
| `-march=native` | Otimizações específicas para a CPU local |
| `-fopenmp` | Habilita diretivas OpenMP |
| `-lm` | Biblioteca matemática (sin, cos, exp, log, sqrt) |
| `-lomp` | Biblioteca OpenMP (libomp) |

---

## CPU e Sistema

Os experimentos foram executados e validados em múltiplos ambientes:

### Ambiente Principal (macOS)

| Componente | Especificação |
|------------|---------------|
| **Sistema Operacional** | macOS (Darwin 25.1.0) |
| **Arquitetura** | ARM64 (Apple Silicon) |
| **Processador** | Apple M3 Pro |
| **Cores Físicos** | 11 |
| **Cores Lógicos** | 11 |
| **Memória RAM** | 18 GB |

### Ambientes Adicionais Testados

| Ambiente | Sistema Operacional | Observação |
|----------|---------------------|------------|
| **Linux Nativo** | Ubuntu | Testado com GCC + OpenMP |
| **WSL** | Ubuntu via Windows Subsystem for Linux | Compatibilidade verificada |

> **Nota**: Os códigos foram desenvolvidos para serem portáveis entre macOS e Linux. O Makefile detecta automaticamente o sistema e ajusta compilador e flags.


---

## Afinidade de Threads

### macOS / libomp

No macOS com Apple Silicon, a afinidade de threads é gerenciada automaticamente pelo sistema operacional. O runtime OpenMP (libomp) não expõe controle direto de afinidade como em sistemas Linux.

| Variável | Valor Padrão | Descrição |
|----------|--------------|-----------|
| `OMP_PROC_BIND` | `false` | Binding desabilitado por padrão |
| `OMP_PLACES` | N/A | Não aplicável no macOS |

### Configuração Utilizada

Os experimentos foram executados com a configuração padrão do sistema:
- Sem pinning explícito de threads a cores
- Scheduler do macOS distribui threads entre P-cores e E-cores
- Variável `OMP_NUM_THREADS` controla número de threads

Para definir número de threads:
```bash
export OMP_NUM_THREADS=4
./programa
```

---

## Semente do Gerador de Números Aleatórios

| Parâmetro | Valor |
|-----------|-------|
| **Semente (SEED)** | 42 |
| **Gerador** | `srand()` / `rand()` (PRNG padrão C) |

### Uso no Código

```c
#define SEED 42

void init_vectors(float *x, float *y, size_t n, unsigned int seed) {
    srand(seed);
    for (size_t i = 0; i < n; i++) {
        x[i] = (float)rand() / RAND_MAX;
        y[i] = (float)rand() / RAND_MAX;
    }
}
```

### Garantias

- **Mesma semente** → **Mesmos dados de entrada** em todas as execuções
- Vetor `y` é **restaurado** antes de cada iteração para garantir mesmas condições
- Todos os experimentos usam `SEED=42`

---

## Parâmetros dos Experimentos

| Parâmetro | Valores |
|-----------|---------|
| **Tamanhos de N** | 100.000, 500.000, 1.000.000 |
| **Número de Threads** | 1, 2, 4, 8, 16 |
| **Execuções por Ponto** | 5 |
| **Medição de Tempo** | `clock_gettime(CLOCK_MONOTONIC)` |

---

## Como Reproduzir os Resultados

### 1. Requisitos

```bash
# macOS
brew install libomp
pip install matplotlib

# Linux
sudo apt install libomp-dev
pip install matplotlib
```

### 2. Clonar e Executar

```bash
git clone <repositório>
cd openmp-trabalho

# Executar todos os experimentos
./run_all.sh

# Ou executar individualmente
cd src/saxpy && make run && make plot
cd src/parallel_region && make run && make plot
```

