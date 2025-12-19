# Makefile para Tarefa D - Organização de Região Paralela
# Compara overhead de criação de threads

# Detecta sistema operacional
UNAME_S := $(shell uname -s)

# Configuração base
CFLAGS = -Wall -Wextra -O3
LDFLAGS = -lm

# Configuração específica por sistema
ifeq ($(UNAME_S),Darwin)
    CC = clang
    CFLAGS += -march=native
    OMP_FLAGS = -Xpreprocessor -fopenmp
    LDFLAGS += -lomp
    HOMEBREW_PREFIX := $(shell brew --prefix 2>/dev/null || echo /usr/local)
    CFLAGS += -I$(HOMEBREW_PREFIX)/opt/libomp/include
    LDFLAGS += -L$(HOMEBREW_PREFIX)/opt/libomp/lib
else
    CC = gcc
    CFLAGS += -march=native
    OMP_FLAGS = -fopenmp
endif

# Diretórios
SRC_SEQ = seq
SRC_OMP = omp
BIN = bin
RESULTS = ../../results/parallel_region
CHARTS = $(RESULTS)/charts
TABLE = $(RESULTS)/table

# Executáveis
SEQ_TARGET = $(BIN)/parallel_region_seq
OMP_TARGET = $(BIN)/parallel_region_omp

.PHONY: all seq omp run plot clean help check-omp

all: seq omp

$(BIN):
	mkdir -p $(BIN)

$(RESULTS):
	mkdir -p $(CHARTS) $(TABLE)

seq: $(BIN) $(SEQ_TARGET)

$(SEQ_TARGET): $(SRC_SEQ)/parallel_region.c
	$(CC) $(CFLAGS) -o $@ $< $(LDFLAGS)

check-omp:
ifeq ($(UNAME_S),Darwin)
	@if ! brew list libomp >/dev/null 2>&1; then \
		echo "Erro: libomp não instalado. Execute: brew install libomp"; \
		exit 1; \
	fi
endif

omp: $(BIN) check-omp $(OMP_TARGET)

$(OMP_TARGET): $(SRC_OMP)/parallel_region.c
	$(CC) $(CFLAGS) $(OMP_FLAGS) -o $@ $< $(LDFLAGS)

run: all $(RESULTS)
	./run.sh

plot:
	python3 plot.py

clean:
	rm -rf $(BIN) $(RESULTS)

help:
	@echo "=== Tarefa D - Organização de Região Paralela ==="
	@echo ""
	@echo "Sistema detectado: $(UNAME_S)"
	@echo "Compilador: $(CC)"
	@echo ""
	@echo "Estrutura:"
	@echo "  seq/  - Código sequencial (baseline)"
	@echo "  omp/  - Código OpenMP (ingênua e arrumada)"
	@echo ""
	@echo "Alvos disponíveis:"
	@echo "  all   - Compila todas as versões"
	@echo "  seq   - Compila versão sequencial"
	@echo "  omp   - Compila versão OpenMP"
	@echo "  run   - Executa experimentos"
	@echo "  plot  - Gera gráficos"
	@echo "  clean - Remove executáveis e resultados"
ifeq ($(UNAME_S),Darwin)
	@echo ""
	@echo "Nota (macOS): Requer libomp (brew install libomp)"
endif

