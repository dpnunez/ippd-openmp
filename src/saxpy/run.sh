#!/bin/bash
#
# run.sh - Executa matriz de experimentos para Tarefa C (SAXPY)
# Gera arquivo CSV com resultados

# Diretórios de saída
RESULTS_DIR="../../results/saxpy"
TABLE_DIR="$RESULTS_DIR/table"
OUTPUT="$TABLE_DIR/results.csv"

NUM_RUNS=5
SEED=42

# Tamanhos de N conforme especificação
N_VALUES=(100000 500000 1000000)

# Número de threads conforme especificação
THREAD_VALUES=(1 2 4 8 16)

# Cria diretórios se não existirem
mkdir -p "$TABLE_DIR"

# Verifica se executáveis existem
if [ ! -f "bin/saxpy_seq" ] || [ ! -f "bin/saxpy_omp" ]; then
    echo "Compilando executáveis..."
    make all
fi

# Cabeçalho CSV
echo "versao,n,threads,tempo_medio,desvio_padrao" > $OUTPUT

echo "=== Executando experimentos SAXPY ==="
echo "Resultados serão salvos em: $OUTPUT"
echo ""

# Executa versão sequencial (baseline)
echo "--- Versão Sequencial ---"
for n in "${N_VALUES[@]}"; do
    echo "  N=$n"
    ./bin/saxpy_seq $n $NUM_RUNS $SEED >> $OUTPUT
done

# Executa versão SIMD (apenas vetorização, sem paralelismo de threads)
echo ""
echo "--- Versão SIMD ---"
for n in "${N_VALUES[@]}"; do
    echo "  N=$n"
    ./bin/saxpy_omp $n 1 $NUM_RUNS $SEED 1 >> $OUTPUT
done

# Executa versão Parallel SIMD (paralelismo + vetorização)
echo ""
echo "--- Versão Parallel SIMD ---"
for n in "${N_VALUES[@]}"; do
    for threads in "${THREAD_VALUES[@]}"; do
        echo "  N=$n, Threads=$threads"
        ./bin/saxpy_omp $n $threads $NUM_RUNS $SEED 2 >> $OUTPUT
    done
done

echo ""
echo "=== Experimentos concluídos ==="
echo "Resultados salvos em: $OUTPUT"
echo ""
echo "Para gerar gráficos, execute: make plot"
