/**
 * Tarefa D - Organização de Região Paralela com OpenMP
 * 
 * Compara duas abordagens de paralelização:
 * 
 * V1 (seq): Sequencial - baseline
 * V2 (ingenua): Dois #pragma omp parallel for consecutivos
 * V3 (arrumada): Uma região #pragma omp parallel com dois #pragma omp for
 * 
 * Kernel com carga computacional significativa:
 * - Loop 1: y[i] = sin(x[i]) * cos(x[i]) + sqrt(x[i])
 * - Loop 2: z[i] = log(y[i] + 1) * exp(-y[i] * 0.01)
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

// Inicializa vetor com valores determinísticos
void init_vector(double *x, size_t n, unsigned int seed) {
    srand(seed);
    for (size_t i = 0; i < n; i++) {
        x[i] = 0.1 + 9.9 * (double)rand() / RAND_MAX;
    }
}

// Força uso dos resultados
volatile double dummy_sum = 0;
double use_results(double *y, double *z, size_t n) {
    double sum = 0;
    for (size_t i = 0; i < n; i += n/100 + 1) {
        sum += y[i] + z[i];
    }
    return sum;
}

// V1: Sequencial (baseline)
void process_sequential(double *x, double *y, double *z, size_t n) {
    for (size_t i = 0; i < n; i++) {
        y[i] = sin(x[i]) * cos(x[i]) + sqrt(x[i]);
    }
    for (size_t i = 0; i < n; i++) {
        z[i] = log(y[i] + 1.0) * exp(-y[i] * 0.01);
    }
}

// V2: Ingênua - dois parallel for consecutivos
// Cria e destrói a equipe de threads DUAS vezes
void process_ingenua(double *x, double *y, double *z, size_t n) {
    // Primeira região paralela - cria threads
    #pragma omp parallel for
    for (size_t i = 0; i < n; i++) {
        y[i] = sin(x[i]) * cos(x[i]) + sqrt(x[i]);
    }
    // Threads são destruídas aqui (barrier implícito + fim da região)
    
    // Segunda região paralela - cria threads NOVAMENTE
    #pragma omp parallel for
    for (size_t i = 0; i < n; i++) {
        z[i] = log(y[i] + 1.0) * exp(-y[i] * 0.01);
    }
    // Threads são destruídas aqui novamente
}

// V3: Arrumada - uma região parallel com dois for
// Cria a equipe de threads apenas UMA vez
void process_arrumada(double *x, double *y, double *z, size_t n) {
    // Uma única região paralela - cria threads uma vez
    #pragma omp parallel
    {
        // Primeiro for - distribui trabalho entre threads existentes
        #pragma omp for
        for (size_t i = 0; i < n; i++) {
            y[i] = sin(x[i]) * cos(x[i]) + sqrt(x[i]);
        }
        // Barrier implícito aqui (sincroniza antes do próximo for)
        
        // Segundo for - reutiliza as mesmas threads
        #pragma omp for
        for (size_t i = 0; i < n; i++) {
            z[i] = log(y[i] + 1.0) * exp(-y[i] * 0.01);
        }
    }
    // Threads são destruídas apenas aqui
}

typedef void (*process_fn)(double*, double*, double*, size_t);

typedef struct {
    const char *name;
    process_fn fn;
} version_t;

int main(int argc, char *argv[]) {
    size_t n = 1000000;
    int num_runs = 5;
    int num_threads = 4;
    unsigned int seed = 42;
    int version = -1;  // -1 = todas, 0 = seq, 1 = ingenua, 2 = arrumada
    
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
        {"seq", process_sequential},
        {"ingenua", process_ingenua},
        {"arrumada", process_arrumada}
    };
    int num_versions = sizeof(versions) / sizeof(versions[0]);
    
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
    
    double *times = malloc(num_runs * sizeof(double));
    
    // Determina quais versões executar
    int start_v = (version >= 0 && version < num_versions) ? version : 0;
    int end_v = (version >= 0 && version < num_versions) ? version + 1 : num_versions;
    
    for (int v = start_v; v < end_v; v++) {
        double total_time = 0.0;
        
        for (int run = 0; run < num_runs; run++) {
            // Limpa y e z
            memset(y, 0, n * sizeof(double));
            memset(z, 0, n * sizeof(double));
            
            double start = get_time();
            versions[v].fn(x, y, z, n);
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
        
        // Threads efetivos (seq usa 1, ingenua e arrumada usam num_threads)
        int effective_threads = (v == 0) ? 1 : num_threads;
        
        // Saída CSV: versao,n,threads,tempo_medio,desvio_padrao
        printf("%s,%zu,%d,%.9f,%.9f\n",
               versions[v].name, n, effective_threads, mean, stddev);
    }
    
    free(times);
    free(x);
    free(y);
    free(z);
    
    return 0;
}
