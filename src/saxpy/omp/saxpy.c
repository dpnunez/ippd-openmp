/**
 * Tarefa C - SAXPY com OpenMP
 * y[i] = a * x[i] + y[i]
 * 
 * V1: Sequencial (baseline)
 * V2: #pragma omp simd
 * V3: #pragma omp parallel for simd
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <time.h>
#include <omp.h>

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

// V1: SAXPY sequencial (baseline)
void saxpy_seq(float a, float *x, float *y, size_t n) {
    for (size_t i = 0; i < n; i++) {
        y[i] = a * x[i] + y[i];
    }
}

// V2: SAXPY com SIMD (vetorização explícita)
void saxpy_simd(float a, float *x, float *y, size_t n) {
    #pragma omp simd
    for (size_t i = 0; i < n; i++) {
        y[i] = a * x[i] + y[i];
    }
}

// V3: SAXPY com parallel for simd (paralelismo + vetorização)
void saxpy_parallel_simd(float a, float *x, float *y, size_t n) {
    #pragma omp parallel for simd
    for (size_t i = 0; i < n; i++) {
        y[i] = a * x[i] + y[i];
    }
}

typedef void (*saxpy_fn)(float, float*, float*, size_t);

typedef struct {
    const char *name;
    saxpy_fn fn;
} version_t;

int main(int argc, char *argv[]) {
    size_t n = 1000000;      // Tamanho padrão
    int num_runs = 5;         // Número de execuções
    int num_threads = 4;      // Número de threads
    unsigned int seed = 42;
    int version = -1;         // -1 = todas, 0 = seq, 1 = simd, 2 = parallel_simd
    
    // Parse argumentos
    if (argc >= 2) n = (size_t)atol(argv[1]);
    if (argc >= 3) num_threads = atoi(argv[2]);
    if (argc >= 4) num_runs = atoi(argv[3]);
    if (argc >= 5) seed = (unsigned int)atoi(argv[4]);
    if (argc >= 6) version = atoi(argv[5]);
    
    // Define número de threads
    omp_set_num_threads(num_threads);
    
    // Versões disponíveis
    version_t versions[] = {
        {"seq", saxpy_seq},
        {"simd", saxpy_simd},
        {"parallel_simd", saxpy_parallel_simd}
    };
    int num_versions = sizeof(versions) / sizeof(versions[0]);
    
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
    
    double *times = malloc(num_runs * sizeof(double));
    
    // Determina quais versões executar
    int start_v = (version >= 0 && version < num_versions) ? version : 0;
    int end_v = (version >= 0 && version < num_versions) ? version + 1 : num_versions;
    
    for (int v = start_v; v < end_v; v++) {
        double total_time = 0.0;
        
        for (int run = 0; run < num_runs; run++) {
            // Restaura y
            memcpy(y, y_backup, n * sizeof(float));
            
            double start = get_time();
            versions[v].fn(a, x, y, n);
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
        
        // Threads efetivos (seq e simd usam 1, parallel_simd usa num_threads)
        int effective_threads = (v == 2) ? num_threads : 1;
        
        // Saída CSV: versao,n,threads,tempo_medio,desvio_padrao
        printf("%s,%zu,%d,%.9f,%.9f\n", 
               versions[v].name, n, effective_threads, mean, stddev);
    }
    
    free(times);
    free(x);
    free(y);
    free(y_backup);
    
    return 0;
}
