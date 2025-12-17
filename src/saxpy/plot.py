#!/usr/bin/env python3
"""
plot.py - Gera gráficos para Tarefa C (SAXPY)
Análise de vetorização com SIMD e OpenMP

Dependências: matplotlib (pip install matplotlib)
"""

import csv
import os
import sys

try:
    import matplotlib.pyplot as plt
    import matplotlib
    matplotlib.use('Agg')  # Backend sem GUI
except ImportError:
    print("Erro: matplotlib não encontrado.")
    print("Instale com: pip install matplotlib")
    sys.exit(1)

# Diretórios
RESULTS_DIR = "../../results/saxpy"
TABLE_DIR = f"{RESULTS_DIR}/table"
CHARTS_DIR = f"{RESULTS_DIR}/charts"
INPUT_FILE = f"{TABLE_DIR}/results.csv"

# Configuração de experimentos
NUM_RUNS = 5  # Número de execuções para média

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

def add_methodology_note(ax, position='bottom'):
    """Adiciona nota sobre metodologia no gráfico."""
    note = f"Cada ponto: média de {NUM_RUNS} execuções. Barras de erro: ±1 desvio padrão."
    if position == 'bottom':
        ax.annotate(note, xy=(0.5, -0.12), xycoords='axes fraction', 
                   ha='center', fontsize=8, style='italic', color='gray')
    else:
        ax.annotate(note, xy=(0.5, 1.02), xycoords='axes fraction', 
                   ha='center', fontsize=8, style='italic', color='gray')

def plot_tempo_por_versao(data):
    """Gráfico 1: Tempo de execução - todas as versões com diferentes threads."""
    fig, axes = plt.subplots(1, 3, figsize=(16, 6))
    
    n_values = get_unique(data, 'n')
    thread_options = [1, 2, 4, 8, 16]
    
    for idx, n in enumerate(n_values):
        ax = axes[idx]
        data_n = filter_data(data, n=n)
        
        # Obtém tempos
        seq_data = filter_data(data_n, versao='seq')[0]
        simd_data = filter_data(data_n, versao='simd')[0]
        
        # Labels e valores
        labels = ['Seq', 'SIMD']
        times = [seq_data['tempo_medio'], simd_data['tempo_medio']]
        errors = [seq_data['desvio_padrao'], simd_data['desvio_padrao']]
        colors = ['#3498db', '#2ecc71']
        
        # Adiciona parallel_simd para cada número de threads
        for t in thread_options:
            p_data = filter_data(data_n, versao='parallel_simd', threads=t)
            if p_data:
                labels.append(f'P.SIMD\n{t}T')
                times.append(p_data[0]['tempo_medio'])
                errors.append(p_data[0]['desvio_padrao'])
                colors.append('#e74c3c')
        
        x = range(len(labels))
        bars = ax.bar(x, [t * 1000 for t in times], color=colors, 
                     edgecolor='black', linewidth=0.5, yerr=[e * 1000 for e in errors], 
                     capsize=3, error_kw={'linewidth': 1})
        
        # Adiciona valores nas barras
        for bar, time in zip(bars, times):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(times)*1000*0.05,
                   f'{time*1000:.3f}', ha='center', va='bottom', fontsize=7, rotation=45)
        
        ax.set_title(f'N = {n:,}', fontweight='bold')
        ax.set_ylabel('Tempo médio (ms)')
        ax.set_xticks(x)
        ax.set_xticklabels(labels, fontsize=8)
        ax.set_ylim(bottom=0)
    
    plt.suptitle('Comparação de Tempo por Versão SAXPY\n(P.SIMD = Parallel SIMD, T = Threads)', 
                 fontsize=12, fontweight='bold')
    
    # Nota de metodologia
    fig.text(0.5, 0.01, f"Cada barra: média de {NUM_RUNS} execuções. Barras de erro: ±1 desvio padrão.", 
             ha='center', fontsize=9, style='italic', color='gray')
    
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.savefig(f'{CHARTS_DIR}/grafico1_tempo_versao.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("  ✓ grafico1_tempo_versao.png")

def plot_speedup_todas_versoes(data):
    """Gráfico 2: Speedup de todas as versões sobre sequencial."""
    fig, ax = plt.subplots(figsize=(12, 6))
    
    n_values = get_unique(data, 'n')
    thread_options = [1, 2, 4, 8, 16]
    
    # Prepara dados para o gráfico agrupado
    labels = []
    for n in n_values:
        labels.append(f'N={n//1000}k')
    
    x = range(len(n_values))
    width = 0.12
    
    # SIMD (1 thread)
    speedups_simd = []
    for n in n_values:
        data_n = filter_data(data, n=n)
        seq_time = filter_data(data_n, versao='seq')[0]['tempo_medio']
        simd_time = filter_data(data_n, versao='simd')[0]['tempo_medio']
        speedups_simd.append(seq_time / simd_time if simd_time > 0 else 0)
    
    bars_simd = ax.bar([i - 2.5*width for i in x], speedups_simd, width, 
                       label='SIMD (1 thread)', color='#2ecc71', edgecolor='black')
    
    # Parallel SIMD para cada número de threads
    colors_parallel = ['#fee08b', '#fdae61', '#f46d43', '#d73027', '#a50026']
    for t_idx, t in enumerate(thread_options):
        speedups = []
        for n in n_values:
            data_n = filter_data(data, n=n)
            seq_time = filter_data(data_n, versao='seq')[0]['tempo_medio']
            p_data = filter_data(data_n, versao='parallel_simd', threads=t)
            if p_data:
                p_time = p_data[0]['tempo_medio']
                speedups.append(seq_time / p_time if p_time > 0 else 0)
            else:
                speedups.append(0)
        
        offset = (t_idx - 1.5) * width
        bars = ax.bar([i + offset for i in x], speedups, width, 
                     label=f'P.SIMD ({t} threads)', color=colors_parallel[t_idx], edgecolor='black')
    
    # Adiciona valores nas barras do SIMD
    for bar, sp in zip(bars_simd, speedups_simd):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.03,
               f'{sp:.2f}x', ha='center', va='bottom', fontsize=7, rotation=90)
    
    ax.axhline(y=1, color='gray', linestyle='--', alpha=0.7, linewidth=2)
    ax.set_xlabel('Tamanho do vetor (N)')
    ax.set_ylabel('Speedup (vs Sequencial)')
    ax.set_title('Speedup sobre Versão Sequencial\n(valores > 1 indicam ganho de desempenho)', 
                fontsize=12, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend(loc='upper left', fontsize=8, ncol=2)
    ax.set_ylim(bottom=0)
    ax.grid(axis='y', alpha=0.3)
    
    # Nota de metodologia
    ax.annotate(f"Speedup = Tempo_seq / Tempo_versão. Baseado em média de {NUM_RUNS} execuções.", 
               xy=(0.5, -0.1), xycoords='axes fraction', ha='center', fontsize=9, 
               style='italic', color='gray')
    
    plt.tight_layout()
    plt.savefig(f'{CHARTS_DIR}/grafico2_speedup_simd.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("  ✓ grafico2_speedup_simd.png")

def plot_escalabilidade_threads(data):
    """Gráfico 3: Speedup do Parallel SIMD vs Sequencial (por threads)."""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    parallel_data = filter_data(data, versao='parallel_simd')
    n_values = get_unique(parallel_data, 'n')
    
    colors = ['#3498db', '#2ecc71', '#e74c3c']
    markers = ['o', 's', '^']
    
    all_threads = get_unique(parallel_data, 'threads')
    
    for idx, n in enumerate(n_values):
        data_n = filter_data(data, n=n)
        seq_time = filter_data(data_n, versao='seq')[0]['tempo_medio']
        
        parallel_n = sorted(filter_data(parallel_data, n=n), key=lambda x: x['threads'])
        
        threads = [d['threads'] for d in parallel_n]
        tempos = [d['tempo_medio'] for d in parallel_n]
        desvios = [d['desvio_padrao'] for d in parallel_n]
        
        # Speedup relativo ao SEQUENCIAL (não à 1 thread do parallel)
        speedups = [seq_time / t if t > 0 else 0 for t in tempos]
        # Propagação de erro simplificada
        speedup_errs = [seq_time / t * (d / t) if t > 0 else 0 for t, d in zip(tempos, desvios)]
        
        ax.errorbar(threads, speedups, yerr=speedup_errs,
                   label=f'N = {n:,}', marker=markers[idx], 
                   color=colors[idx], linewidth=2, markersize=8, capsize=3)
    
    # Linha de referência (speedup = 1)
    ax.axhline(y=1, color='gray', linestyle='--', alpha=0.7, label='Baseline sequencial (1x)')
    
    ax.set_xlabel('Número de Threads')
    ax.set_ylabel('Speedup (vs Sequencial)')
    ax.set_title('Speedup do Parallel SIMD vs Sequencial\n(como o speedup varia com o número de threads)', 
                fontsize=12, fontweight='bold')
    ax.legend()
    ax.set_xticks(all_threads)
    ax.set_ylim(bottom=0)
    ax.grid(True, alpha=0.3)
    
    # Nota de metodologia
    ax.annotate(f"Speedup = Tempo_seq / Tempo_parallel_simd. Média de {NUM_RUNS} execuções. Barras: ±1 desvio padrão.", 
               xy=(0.5, -0.1), xycoords='axes fraction', ha='center', fontsize=9, 
               style='italic', color='gray')
    
    plt.tight_layout()
    plt.savefig(f'{CHARTS_DIR}/grafico3_escalabilidade.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("  ✓ grafico3_escalabilidade.png")

def plot_tempo_threads(data):
    """Gráfico 4: Tempo absoluto vs Threads para parallel simd."""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    parallel_data = filter_data(data, versao='parallel_simd')
    n_values = get_unique(parallel_data, 'n')
    
    colors = ['#3498db', '#2ecc71', '#e74c3c']
    markers = ['o', 's', '^']
    
    for idx, n in enumerate(n_values):
        data_n = sorted(filter_data(parallel_data, n=n), key=lambda x: x['threads'])
        
        threads = [d['threads'] for d in data_n]
        tempos = [d['tempo_medio'] * 1000 for d in data_n]  # ms
        desvios = [d['desvio_padrao'] * 1000 for d in data_n]
        
        ax.errorbar(threads, tempos, yerr=desvios,
                   label=f'N = {n:,}', marker=markers[idx],
                   color=colors[idx], linewidth=2, markersize=8, capsize=3)
        
        # Adiciona linha horizontal com tempo sequencial para referência
        seq_data = filter_data(data, n=n, versao='seq')
        if seq_data:
            seq_time = seq_data[0]['tempo_medio'] * 1000
            ax.axhline(y=seq_time, color=colors[idx], linestyle=':', alpha=0.5)
    
    ax.set_xlabel('Número de Threads')
    ax.set_ylabel('Tempo médio (ms)')
    ax.set_title('Tempo de Execução vs Threads (Parallel SIMD)\n(linhas pontilhadas = tempo sequencial para referência)', 
                fontsize=12, fontweight='bold')
    ax.legend()
    all_threads = get_unique(parallel_data, 'threads')
    ax.set_xticks(all_threads)
    ax.set_ylim(bottom=0)
    ax.grid(True, alpha=0.3)
    
    # Nota de metodologia
    ax.annotate(f"Cada ponto: média de {NUM_RUNS} execuções. Barras de erro: ±1 desvio padrão.", 
               xy=(0.5, -0.1), xycoords='axes fraction', ha='center', fontsize=9, 
               style='italic', color='gray')
    
    plt.tight_layout()
    plt.savefig(f'{CHARTS_DIR}/grafico4_tempo_threads.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("  ✓ grafico4_tempo_threads.png")

def generate_summary_table(data):
    """Gera tabela resumo."""
    print(f"\n=== Tabela Resumo (média de {NUM_RUNS} execuções) ===\n")
    
    print("| Versão | N | Threads | Tempo Médio (ms) | Desvio Padrão (ms) | Speedup |")
    print("|--------|---|---------|------------------|-------------------|---------|")
    
    for n in get_unique(data, 'n'):
        data_n = filter_data(data, n=n)
        seq_time = filter_data(data_n, versao='seq')[0]['tempo_medio']
        
        for row in sorted(data_n, key=lambda x: (x['versao'], x['threads'])):
            speedup = seq_time / row['tempo_medio'] if row['tempo_medio'] > 0 else 0
            print(f"| {row['versao']:13} | {row['n']:,} | {row['threads']:2} | "
                  f"{row['tempo_medio']*1000:12.4f} | {row['desvio_padrao']*1000:13.4f} | "
                  f"{speedup:6.2f}x |")
        print("|--------|---|---------|------------------|-------------------|---------|")

def main():
    print("=== Gerando gráficos para Tarefa C (SAXPY) ===\n")
    print(f"Configuração: {NUM_RUNS} execuções por ponto (média ± desvio padrão)\n")
    
    # Cria diretório de charts se não existir
    os.makedirs(CHARTS_DIR, exist_ok=True)
    
    data = load_data()
    
    print(f"Gráficos salvos em: {CHARTS_DIR}/")
    plot_tempo_por_versao(data)
    plot_speedup_todas_versoes(data)
    plot_escalabilidade_threads(data)
    plot_tempo_threads(data)
    
    generate_summary_table(data)
    
    print("\n=== Gráficos salvos com sucesso! ===")

if __name__ == '__main__':
    main()
