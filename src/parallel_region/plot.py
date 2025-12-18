#!/usr/bin/env python3
"""
plot.py - Gera gráficos para Tarefa D (Organização de Região Paralela)
Compara overhead de criação de threads entre versão ingênua e arrumada

Dependências: matplotlib (pip install matplotlib)
"""

import csv
import os
import sys

try:
    import matplotlib.pyplot as plt
    import matplotlib
    matplotlib.use('Agg')
except ImportError:
    print("Erro: matplotlib não encontrado.")
    print("Instale com: pip install matplotlib")
    sys.exit(1)

# Diretórios
RESULTS_DIR = "../../results/parallel_region"
TABLE_DIR = f"{RESULTS_DIR}/table"
CHARTS_DIR = f"{RESULTS_DIR}/charts"
INPUT_FILE = f"{TABLE_DIR}/results.csv"

# Configuração de experimentos
NUM_RUNS = 5

# Configuração de estilo
plt.rcParams['figure.figsize'] = (10, 6)
plt.rcParams['font.size'] = 11

def load_data(filename=INPUT_FILE):
    """Carrega dados do CSV de resultados."""
    if not os.path.exists(filename):
        print(f"Erro: Arquivo {filename} não encontrado.")
        print("Execute 'make run' primeiro para gerar os resultados.")
        sys.exit(1)
    
    data = []
    with open(filename, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            data.append({
                'versao': row['versao'],
                'n': int(row['n']),
                'threads': int(row['threads']),
                'tempo_medio': float(row['tempo_medio']),
                'desvio_padrao': float(row['desvio_padrao'])
            })
    return data

def filter_data(data, **kwargs):
    """Filtra dados por critérios."""
    result = data
    for key, value in kwargs.items():
        result = [d for d in result if d.get(key) == value]
    return result

def get_unique(data, key):
    """Retorna valores únicos de uma chave."""
    return sorted(set(d[key] for d in data))

def plot_comparacao_versoes(data):
    """Gráfico 1: Comparação Ingênua vs Arrumada para cada N."""
    fig, axes = plt.subplots(1, 3, figsize=(16, 5))
    
    n_values = get_unique(data, 'n')
    thread_options = get_unique(filter_data(data, versao='ingenua'), 'threads')
    
    for idx, n in enumerate(n_values):
        ax = axes[idx]
        data_n = filter_data(data, n=n)
        
        # Tempo sequencial para referência
        seq_data = filter_data(data_n, versao='seq')
        seq_time = seq_data[0]['tempo_medio'] if seq_data else 0
        
        x = range(len(thread_options))
        width = 0.35
        
        # Ingênua
        ingenua_times = []
        ingenua_errs = []
        for t in thread_options:
            d = filter_data(data_n, versao='ingenua', threads=t)
            if d:
                ingenua_times.append(d[0]['tempo_medio'] * 1000)
                ingenua_errs.append(d[0]['desvio_padrao'] * 1000)
            else:
                ingenua_times.append(0)
                ingenua_errs.append(0)
        
        # Arrumada
        arrumada_times = []
        arrumada_errs = []
        for t in thread_options:
            d = filter_data(data_n, versao='arrumada', threads=t)
            if d:
                arrumada_times.append(d[0]['tempo_medio'] * 1000)
                arrumada_errs.append(d[0]['desvio_padrao'] * 1000)
            else:
                arrumada_times.append(0)
                arrumada_errs.append(0)
        
        bars1 = ax.bar([i - width/2 for i in x], ingenua_times, width,
                      yerr=ingenua_errs, capsize=3,
                      label='Ingênua (2x parallel for)', color='#e74c3c', edgecolor='black')
        bars2 = ax.bar([i + width/2 for i in x], arrumada_times, width,
                      yerr=arrumada_errs, capsize=3,
                      label='Arrumada (1x parallel)', color='#2ecc71', edgecolor='black')
        
        # Linha de referência sequencial
        ax.axhline(y=seq_time * 1000, color='blue', linestyle='--', 
                  alpha=0.7, label=f'Sequencial ({seq_time*1000:.3f}ms)')
        
        ax.set_title(f'N = {n:,}', fontweight='bold')
        ax.set_ylabel('Tempo médio (ms)')
        ax.set_xlabel('Número de Threads')
        ax.set_xticks(x)
        ax.set_xticklabels(thread_options)
        ax.legend(fontsize=8)
        ax.set_ylim(bottom=0)
    
    plt.suptitle('Comparação: Ingênua vs Arrumada\n(menor = melhor)', 
                fontsize=12, fontweight='bold')
    fig.text(0.5, 0.01, f"Cada barra: média de {NUM_RUNS} execuções. Barras de erro: ±1 desvio padrão.",
            ha='center', fontsize=9, style='italic', color='gray')
    
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.savefig(f'{CHARTS_DIR}/grafico1_comparacao_versoes.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("  ✓ grafico1_comparacao_versoes.png")

def plot_overhead_relativo(data):
    """Gráfico 2: Overhead da versão Ingênua em relação à Arrumada."""
    fig, ax = plt.subplots(figsize=(12, 6))
    
    n_values = get_unique(data, 'n')
    thread_options = get_unique(filter_data(data, versao='ingenua'), 'threads')
    
    colors = ['#3498db', '#2ecc71', '#e74c3c']
    markers = ['o', 's', '^']
    
    for idx, n in enumerate(n_values):
        data_n = filter_data(data, n=n)
        
        overheads = []
        for t in thread_options:
            ingenua = filter_data(data_n, versao='ingenua', threads=t)
            arrumada = filter_data(data_n, versao='arrumada', threads=t)
            
            if ingenua and arrumada:
                # Overhead percentual: (ingenua - arrumada) / arrumada * 100
                overhead = ((ingenua[0]['tempo_medio'] - arrumada[0]['tempo_medio']) 
                           / arrumada[0]['tempo_medio'] * 100)
                overheads.append(overhead)
            else:
                overheads.append(0)
        
        ax.plot(thread_options, overheads, marker=markers[idx], 
               color=colors[idx], linewidth=2, markersize=8,
               label=f'N = {n:,}')
    
    ax.axhline(y=0, color='gray', linestyle='--', alpha=0.7)
    ax.set_xlabel('Número de Threads')
    ax.set_ylabel('Overhead da Ingênua (%)')
    ax.set_title('Overhead da Versão Ingênua em Relação à Arrumada\n(valores > 0 indicam que Ingênua é mais lenta)',
                fontsize=12, fontweight='bold')
    ax.legend()
    ax.set_xticks(thread_options)
    ax.grid(True, alpha=0.3)
    
    ax.annotate(f"Overhead = (Tempo_ingenua - Tempo_arrumada) / Tempo_arrumada × 100%. Média de {NUM_RUNS} execuções.",
               xy=(0.5, -0.12), xycoords='axes fraction', ha='center', fontsize=9,
               style='italic', color='gray')
    
    plt.tight_layout()
    plt.savefig(f'{CHARTS_DIR}/grafico2_overhead_relativo.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("  ✓ grafico2_overhead_relativo.png")

def plot_speedup_vs_sequencial(data):
    """Gráfico 3: Speedup de ambas versões sobre sequencial."""
    fig, ax = plt.subplots(figsize=(12, 6))
    
    n_values = get_unique(data, 'n')
    thread_options = get_unique(filter_data(data, versao='ingenua'), 'threads')
    
    # Cores diferentes para cada N, linha sólida para arrumada, tracejada para ingênua
    colors = ['#3498db', '#2ecc71', '#e74c3c']
    
    for idx, n in enumerate(n_values):
        data_n = filter_data(data, n=n)
        seq_time = filter_data(data_n, versao='seq')[0]['tempo_medio']
        
        speedups_ingenua = []
        speedups_arrumada = []
        errs_ingenua = []
        errs_arrumada = []
        
        for t in thread_options:
            ing = filter_data(data_n, versao='ingenua', threads=t)
            arr = filter_data(data_n, versao='arrumada', threads=t)
            
            if ing:
                sp = seq_time / ing[0]['tempo_medio']
                speedups_ingenua.append(sp)
                errs_ingenua.append(sp * ing[0]['desvio_padrao'] / ing[0]['tempo_medio'])
            if arr:
                sp = seq_time / arr[0]['tempo_medio']
                speedups_arrumada.append(sp)
                errs_arrumada.append(sp * arr[0]['desvio_padrao'] / arr[0]['tempo_medio'])
        
        ax.errorbar(thread_options, speedups_arrumada, yerr=errs_arrumada,
                   marker='o', color=colors[idx], linewidth=2, markersize=8,
                   capsize=3, label=f'Arrumada N={n//1000}k')
        ax.errorbar(thread_options, speedups_ingenua, yerr=errs_ingenua,
                   marker='s', color=colors[idx], linewidth=2, markersize=8,
                   capsize=3, linestyle='--', alpha=0.7, label=f'Ingênua N={n//1000}k')
    
    ax.axhline(y=1, color='gray', linestyle=':', alpha=0.7, linewidth=2, label='Baseline (1x)')
    ax.set_xlabel('Número de Threads')
    ax.set_ylabel('Speedup (vs Sequencial)')
    ax.set_title('Speedup sobre Versão Sequencial\n(linha sólida = Arrumada, tracejada = Ingênua)',
                fontsize=12, fontweight='bold')
    ax.legend(fontsize=8, ncol=2)
    ax.set_xticks(thread_options)
    ax.set_ylim(bottom=0)
    ax.grid(True, alpha=0.3)
    
    ax.annotate(f"Speedup = Tempo_seq / Tempo_versão. Média de {NUM_RUNS} execuções. Barras: ±1 desvio padrão.",
               xy=(0.5, -0.12), xycoords='axes fraction', ha='center', fontsize=9,
               style='italic', color='gray')
    
    plt.tight_layout()
    plt.savefig(f'{CHARTS_DIR}/grafico3_speedup_sequencial.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("  ✓ grafico3_speedup_sequencial.png")

def plot_tempo_absoluto(data):
    """Gráfico 4: Tempo absoluto para todas as versões."""
    fig, ax = plt.subplots(figsize=(12, 6))
    
    n_values = get_unique(data, 'n')
    thread_options = get_unique(filter_data(data, versao='ingenua'), 'threads')
    
    colors = ['#3498db', '#2ecc71', '#e74c3c']
    
    for idx, n in enumerate(n_values):
        data_n = filter_data(data, n=n)
        
        # Arrumada
        arrumada_times = []
        arrumada_errs = []
        for t in thread_options:
            d = filter_data(data_n, versao='arrumada', threads=t)
            if d:
                arrumada_times.append(d[0]['tempo_medio'] * 1000)
                arrumada_errs.append(d[0]['desvio_padrao'] * 1000)
        
        ax.errorbar(thread_options, arrumada_times, yerr=arrumada_errs,
                   marker='o', color=colors[idx], linewidth=2, markersize=8,
                   capsize=3, label=f'Arrumada N={n//1000}k')
        
        # Linha horizontal com tempo sequencial
        seq_time = filter_data(data_n, versao='seq')[0]['tempo_medio'] * 1000
        ax.axhline(y=seq_time, color=colors[idx], linestyle=':', alpha=0.5)
    
    ax.set_xlabel('Número de Threads')
    ax.set_ylabel('Tempo médio (ms)')
    ax.set_title('Tempo de Execução da Versão Arrumada\n(linhas pontilhadas = tempo sequencial)',
                fontsize=12, fontweight='bold')
    ax.legend()
    ax.set_xticks(thread_options)
    ax.set_ylim(bottom=0)
    ax.grid(True, alpha=0.3)
    
    ax.annotate(f"Cada ponto: média de {NUM_RUNS} execuções. Barras de erro: ±1 desvio padrão.",
               xy=(0.5, -0.12), xycoords='axes fraction', ha='center', fontsize=9,
               style='italic', color='gray')
    
    plt.tight_layout()
    plt.savefig(f'{CHARTS_DIR}/grafico4_tempo_absoluto.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("  ✓ grafico4_tempo_absoluto.png")

def generate_summary_table(data):
    """Gera tabela resumo."""
    print(f"\n=== Tabela Resumo (média de {NUM_RUNS} execuções) ===\n")
    
    print("| Versão | N | Threads | Tempo Médio (ms) | Desvio Padrão (ms) | Speedup |")
    print("|--------|---|---------|------------------|-------------------|---------|")
    
    for n in get_unique(data, 'n'):
        data_n = filter_data(data, n=n)
        seq_data = filter_data(data_n, versao='seq')
        seq_time = seq_data[0]['tempo_medio'] if seq_data else 1
        
        for row in sorted(data_n, key=lambda x: (x['versao'], x['threads'])):
            speedup = seq_time / row['tempo_medio'] if row['tempo_medio'] > 0 else 0
            print(f"| {row['versao']:8} | {row['n']:,} | {row['threads']:2} | "
                  f"{row['tempo_medio']*1000:12.4f} | {row['desvio_padrao']*1000:13.4f} | "
                  f"{speedup:6.2f}x |")
        print("|--------|---|---------|------------------|-------------------|---------|")

def main():
    print("=== Gerando gráficos para Tarefa D (Região Paralela) ===\n")
    print(f"Configuração: {NUM_RUNS} execuções por ponto (média ± desvio padrão)\n")
    
    os.makedirs(CHARTS_DIR, exist_ok=True)
    
    data = load_data()
    
    print(f"Gráficos salvos em: {CHARTS_DIR}/")
    plot_comparacao_versoes(data)
    plot_overhead_relativo(data)
    plot_speedup_vs_sequencial(data)
    plot_tempo_absoluto(data)
    
    generate_summary_table(data)
    
    print("\n=== Gráficos salvos com sucesso! ===")

if __name__ == '__main__':
    main()

