#!/bin/bash
#
# run_all.sh - Compila e executa todos os exercícios do trabalho de OpenMP
#
# Uso: ./run_all.sh [opções]
#   --clean     Limpa antes de compilar
#   --no-plot   Não gera gráficos (mais rápido)
#

set -e  # Para no primeiro erro

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Parse argumentos
CLEAN=false
PLOT=true

for arg in "$@"; do
    case $arg in
        --clean)
            CLEAN=true
            ;;
        --no-plot)
            PLOT=false
            ;;
        --help|-h)
            echo "Uso: ./run_all.sh [opções]"
            echo ""
            echo "Opções:"
            echo "  --clean     Limpa antes de compilar"
            echo "  --no-plot   Não gera gráficos (mais rápido)"
            echo "  --help, -h  Mostra esta ajuda"
            exit 0
            ;;
    esac
done

# Diretório raiz
ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Lista de tarefas
TASKS=("saxpy" "parallel_region")
TASK_NAMES=("Tarefa C - SAXPY (Vetorização SIMD)" "Tarefa D - Organização de Região Paralela")

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║          OpenMP - Compilação e Execução Completa          ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Início
START_TIME=$(date +%s)

# Executa cada tarefa
for i in "${!TASKS[@]}"; do
    TASK=${TASKS[$i]}
    NAME=${TASK_NAMES[$i]}
    TASK_DIR="$ROOT_DIR/src/$TASK"
    
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${YELLOW}  $NAME${NC}"
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    
    cd "$TASK_DIR"
    
    # Limpa se solicitado
    if [ "$CLEAN" = true ]; then
        echo -e "${BLUE}[1/4] Limpando...${NC}"
        make clean > /dev/null 2>&1 || true
    fi
    
    # Compila
    echo -e "${BLUE}[2/4] Compilando...${NC}"
    if make all; then
        echo -e "${GREEN}      ✓ Compilação concluída${NC}"
    else
        echo -e "${RED}      ✗ Erro na compilação${NC}"
        exit 1
    fi
    
    # Executa experimentos
    echo -e "${BLUE}[3/4] Executando experimentos...${NC}"
    if make run; then
        echo -e "${GREEN}      ✓ Experimentos concluídos${NC}"
    else
        echo -e "${RED}      ✗ Erro nos experimentos${NC}"
        exit 1
    fi
    
    # Gera gráficos
    if [ "$PLOT" = true ]; then
        echo -e "${BLUE}[4/4] Gerando gráficos...${NC}"
        if make plot; then
            echo -e "${GREEN}      ✓ Gráficos gerados${NC}"
        else
            echo -e "${RED}      ✗ Erro ao gerar gráficos${NC}"
            exit 1
        fi
    else
        echo -e "${BLUE}[4/4] Gráficos ignorados (--no-plot)${NC}"
    fi
    
    echo ""
done

# Volta para raiz
cd "$ROOT_DIR"

# Tempo total
END_TIME=$(date +%s)
ELAPSED=$((END_TIME - START_TIME))

echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                    Execução Concluída!                     ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "Tempo total: ${YELLOW}${ELAPSED}s${NC}"
echo ""
echo "Resultados disponíveis em:"
echo "  - results/saxpy/charts/           (gráficos Tarefa C)"
echo "  - results/saxpy/table/            (dados Tarefa C)"
echo "  - results/parallel_region/charts/ (gráficos Tarefa D)"
echo "  - results/parallel_region/table/  (dados Tarefa D)"
echo ""

