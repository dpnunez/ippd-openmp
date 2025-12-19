/**
 * Tarefa D - Organização de Região Paralela (Sequencial)
 * 
 * Versão baseline: dois loops sequenciais consecutivos
 * 
 * Kernel com carga computacional significativa:
 * - Loop 1: y[i] = sin(x[i]) * cos(x[i]) + sqrt(x[i])
 * - Loop 2: z[i] = log(y[i] + 1) * exp(-y[i] * 0.01)
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

// Inicializa vetor com valores determinísticos
void init_vector(double *x, size_t n, unsigned int seed) {
    srand(seed);
    for (size_t i = 0; i < n; i++) {
        // Valores entre 0.1 e 10.0 para evitar problemas com log/sqrt
        x[i] = 0.1 + 9.9 * (double)rand() / RAND_MAX;
    }
}

// Versão sequencial: dois loops consecutivos com carga computacional
// Usa volatile para evitar que o compilador elimine código
volatile double dummy_sum = 0;

void process_sequential(double *x, double *y, double *z, size_t n) {
    // Loop 1: operações trigonométricas e raiz
    for (size_t i = 0; i < n; i++) {
        y[i] = sin(x[i]) * cos(x[i]) + sqrt(x[i]);
    }
    
    // Loop 2: operações logarítmicas e exponenciais
    for (size_t i = 0; i < n; i++) {
        z[i] = log(y[i] + 1.0) * exp(-y[i] * 0.01);
    }
}

// Força uso dos resultados para evitar otimização
double use_results(double *y, double *z, size_t n) {
    double sum = 0;
    for (size_t i = 0; i < n; i += n/100 + 1) {
        sum += y[i] + z[i];
    }
    return sum;
}

int main(int argc, char *argv[]) {
    size_t n = 1000000;
    int num_runs = 5;
    unsigned int seed = 42;
    
    // Parse argumentos
    if (argc >= 2) n = (size_t)atol(argv[1]);
    if (argc >= 3) num_runs = atoi(argv[2]);
    if (argc >= 4) seed = (unsigned int)atoi(argv[3]);
    
    // Aloca vetores
    double *x = malloc(n * sizeof(double));
    double *y = malloc(n * sizeof(double));
    double *z = malloc(n * sizeof(double));
    
    if (!x || !y || !z) {
        fprintf(stderr, "Erro ao alocar memória\n");
        return 1;
    }
    
    // Inicializa vetor x
    init_vector(x, n, seed);
    
    double times[num_runs];
    double total_time = 0.0;
    
    // Executa múltiplas vezes para média
    for (int run = 0; run < num_runs; run++) {
        // Limpa y e z
        memset(y, 0, n * sizeof(double));
        memset(z, 0, n * sizeof(double));
        
        double start = get_time();
        process_sequential(x, y, z, n);
        double end = get_time();
        
        // Força uso dos resultados
        dummy_sum += use_results(y, z, n);
        
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
    
    // Saída CSV: versao,n,threads,tempo_medio,desvio_padrao
    printf("seq,%zu,1,%.9f,%.9f\n", n, mean, stddev);
    
    free(x);
    free(y);
    free(z);
    
    return 0;
}
