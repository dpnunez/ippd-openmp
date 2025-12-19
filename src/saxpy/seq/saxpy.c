/**
 * Tarefa C - SAXPY Sequencial
 * y[i] = a * x[i] + y[i]
 * 
 * Versão V1: Implementação sequencial básica
 */

#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <string.h>
#include <math.h>

// Função para medir tempo em segundos
double get_time() {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return ts.tv_sec + ts.tv_nsec * 1e-9;
}

// Inicializa vetores com valores determinísticos
void init_vectors(float *x, float *y, size_t n, unsigned int seed) {
    srand(seed);
    for (size_t i = 0; i < n; i++) {
        x[i] = (float)rand() / RAND_MAX;
        y[i] = (float)rand() / RAND_MAX;
    }
}

// SAXPY sequencial: y = a*x + y
void saxpy_seq(float a, float *x, float *y, size_t n) {
    for (size_t i = 0; i < n; i++) {
        y[i] = a * x[i] + y[i];
    }
}

int main(int argc, char *argv[]) {
    size_t n = 1000000;  // Tamanho padrão
    int num_runs = 5;     // Número de execuções para média
    unsigned int seed = 42;
    
    // Parse argumentos
    if (argc >= 2) n = (size_t)atol(argv[1]);
    if (argc >= 3) num_runs = atoi(argv[2]);
    if (argc >= 4) seed = (unsigned int)atoi(argv[3]);
    
    // Aloca vetores
    float *x = malloc(n * sizeof(float));
    float *y = malloc(n * sizeof(float));
    float *y_backup = malloc(n * sizeof(float));
    
    if (!x || !y || !y_backup) {
        fprintf(stderr, "Erro ao alocar memória\n");
        return 1;
    }
    
    float a = 2.5f;
    
    // Inicializa vetores
    init_vectors(x, y, n, seed);
    memcpy(y_backup, y, n * sizeof(float));
    
    double times[num_runs];
    double total_time = 0.0;
    
    // Executa múltiplas vezes para média
    for (int run = 0; run < num_runs; run++) {
        // Restaura y para cada execução
        memcpy(y, y_backup, n * sizeof(float));
        
        double start = get_time();
        saxpy_seq(a, x, y, n);
        double end = get_time();
        
        times[run] = end - start;
        total_time += times[run];
    }
    
    // Calcula média e desvio padrão
    double mean = total_time / num_runs;
    double variance = 0.0;
    for (int i = 0; i < num_runs; i++) {
        variance += (times[i] - mean) * (times[i] - mean);
    }
    double stddev = (num_runs > 1) ? sqrt(variance / (num_runs - 1)) : 0.0;
    
    // Saída em formato CSV: versao,n,threads,tempo_medio,desvio_padrao
    printf("seq,%zu,1,%.9f,%.9f\n", n, mean, stddev);
    
    free(x);
    free(y);
    free(y_backup);
    
    return 0;
}
