# Makefile para Tarefa C - SAXPY com OpenMP
# Vetorização com SIMD

# Detecta sistema operacional
UNAME_S := $(shell uname -s)

# Configuração base
CFLAGS = -Wall -Wextra -O3
LDFLAGS = -lm

# Configuração específica por sistema
ifeq ($(UNAME_S),Darwin)
    # macOS - usa Clang com libomp (instalar: brew install libomp)
    CC = clang
    CFLAGS += -march=native
    OMP_FLAGS = -Xpreprocessor -fopenmp
    LDFLAGS += -lomp
    # Se libomp foi instalado via Homebrew
    HOMEBREW_PREFIX := $(shell brew --prefix 2>/dev/null || echo /usr/local)
    CFLAGS += -I$(HOMEBREW_PREFIX)/opt/libomp/include
    LDFLAGS += -L$(HOMEBREW_PREFIX)/opt/libomp/lib
else
    # Linux - usa GCC
    CC = gcc
    CFLAGS += -march=native
    OMP_FLAGS = -fopenmp
endif

# Diretórios
SRC_SEQ = seq
SRC_OMP = omp
BIN = bin
RESULTS = ../../results/saxpy
CHARTS = $(RESULTS)/charts
TABLE = $(RESULTS)/table

# Executáveis
SEQ_TARGET = $(BIN)/saxpy_seq
OMP_TARGET = $(BIN)/saxpy_omp

.PHONY: all seq omp run plot clean help check-omp

all: seq omp

# Cria diretórios se não existirem
$(BIN):
	mkdir -p $(BIN)

$(RESULTS):
	mkdir -p $(CHARTS) $(TABLE)

# Compila versão sequencial
seq: $(BIN) $(SEQ_TARGET)

$(SEQ_TARGET): $(SRC_SEQ)/saxpy.c
	$(CC) $(CFLAGS) -o $@ $< $(LDFLAGS)

# Verifica se libomp está instalado (macOS)
check-omp:
ifeq ($(UNAME_S),Darwin)
	@if ! brew list libomp >/dev/null 2>&1; then \
		echo "Erro: libomp não instalado. Execute: brew install libomp"; \
		exit 1; \
	fi
endif

# Compila versão OpenMP
omp: $(BIN) check-omp $(OMP_TARGET)

$(OMP_TARGET): $(SRC_OMP)/saxpy.c
	$(CC) $(CFLAGS) $(OMP_FLAGS) -o $@ $< $(LDFLAGS)

# Executa experimentos
run: all $(RESULTS)
	./run.sh

# Gera gráficos
plot:
	python3 plot.py

# Limpeza
clean:
	rm -rf $(BIN) $(RESULTS)

# Ajuda
help:
	@echo "=== Tarefa C - SAXPY com SIMD ==="
	@echo ""
	@echo "Sistema detectado: $(UNAME_S)"
	@echo "Compilador: $(CC)"
	@echo ""
	@echo "Estrutura:"
	@echo "  seq/  - Código sequencial (V1)"
	@echo "  omp/  - Código OpenMP (V2, V3)"
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
