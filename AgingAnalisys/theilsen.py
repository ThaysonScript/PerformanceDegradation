import pandas as pd
import numpy as np
from scipy.stats import theilslopes
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import MinMaxScaler
import json
import os
import gc

# --- 1. CONFIGURAÇÃO ---
DRIVE_PATH = "./"
LOGS_FOLDER = os.path.join(DRIVE_PATH, "logs_monitoramento")

LIMIT_HOURS = 348
LIMIT_DAYS = LIMIT_HOURS / 24.0

# Configuração visual para os gráficos
plt.rcParams.update({'font.size': 10, 'figure.facecolor': 'white', 'savefig.dpi': 300})
plt.rcParams['svg.fonttype'] = 'none'

# --- 2. FUNÇÕES DE SUPORTE (JSON & CATEGORIZAÇÃO) ---

def convert_nan_to_none(obj):
    if isinstance(obj, dict):
        return {k: convert_nan_to_none(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_nan_to_none(i) for i in obj]
    elif isinstance(obj, float) and np.isnan(obj):
        return None
    return obj

def convert_none_to_nan(obj):
    if isinstance(obj, dict):
        return {k: convert_none_to_nan(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_none_to_nan(i) for i in obj]
    elif obj is None:
        return np.nan
    return obj

def extract_categorical_info(folder_name):
    folder_name_lower = folder_name.lower()
    system = "Debian 12" if "debian" in folder_name_lower else \
             "Ubuntu 22.04" if "ubuntu22" in folder_name_lower else \
             "Ubuntu 24.04" if "ubuntu24" in folder_name_lower else "Unknown OS"
    
    system = "Debian 12 bookworm"
    
    if "docker" in folder_name_lower:
        software, version = "Docker", "27.2" if "novo" in folder_name_lower else "23"
    elif "podman" in folder_name_lower:
        software, version = "Podman", "5.1.3"
    else:
        software, version = "Unknown Software", "N/A"
    return system, software, version

# --- 3. MOTOR DE PROCESSAMENTO E CÁLCULO ---

def calculate_slope(df, time_col_numeric, metric_col):
    """Calcula o slope Theil-Sen (unidade/dia) com alinhamento rigoroso."""
    if metric_col not in df.columns or time_col_numeric not in df.columns:
        return np.nan
    
    y = pd.to_numeric(df[metric_col], errors='coerce')
    x = pd.to_numeric(df[time_col_numeric], errors='coerce')

    temp_df = pd.DataFrame({'y': y, 'x': x}).dropna()

    if len(temp_df['y']) < 2: return np.nan

    try:
        slope, *_ = theilslopes(temp_df['y'], temp_df['x'], alpha=0.95)
        return slope
    except:
        return np.nan

def load_and_resample(file_path, metrics):
    """
    Lógica Revisada: Chunks + Filtro 348h + Resample 1min.
    """
    chunks = []
    t0 = None
    try:
        # Detecta separador automaticamente para maior flexibilidade
        reader = pd.read_csv(file_path, sep=None, engine='python', chunksize=100000)
        for chunk in reader:
            chunk['date_time'] = pd.to_datetime(chunk['date_time'], dayfirst=True, errors='coerce')
            chunk = chunk.dropna(subset=['date_time'])
            
            if t0 is None: t0 = chunk['date_time'].min()
            chunk['t_days'] = (chunk['date_time'] - t0).dt.total_seconds() / 86400
            
            filtered = chunk[chunk['t_days'] <= LIMIT_DAYS].copy()
            for m in metrics:
                if m in filtered.columns:
                    if filtered[m].dtype == 'object':
                        filtered[m] = filtered[m].str.replace(',', '.', regex=False)
                    filtered[m] = pd.to_numeric(filtered[m], errors='coerce')
            
            chunks.append(filtered)
            if chunk['t_days'].max() > LIMIT_DAYS: break
            
        if not chunks: return pd.DataFrame()
        
        df_full = pd.concat(chunks, ignore_index=True).set_index('date_time')
        # Resample de 1 minuto (Média)
        df_res = df_full[metrics].resample('1min').mean().reset_index()
        # Recalcula t_days após resample para garantir consistência no slope
        df_res['t_days'] = (df_res['date_time'] - t0).dt.total_seconds() / 86400
        return df_res
    except Exception as e:
        print(f"Erro ao processar {file_path.name}: {e}")
        return pd.DataFrame()

# --- 4. FUNÇÕES DE ORGANIZAÇÃO (ESTRUTURA ORIGINAL) ---

def process_csv_file(file_path, metrics_to_calculate, folder_log_list):
    """
    Processa um arquivo CSV específico usando a lógica de resample.
    """
    if not file_path.exists():
        folder_log_list.append(f"  Arquivo {file_path.name} não encontrado. Pulando.")
        return {metric: np.nan for metric in metrics_to_calculate}

    df_agg = load_and_resample(file_path, metrics_to_calculate)
    
    if df_agg.empty:
        folder_log_list.append(f"  Dados insuficientes em {file_path.name}. Pulando.")
        return {metric: np.nan for metric in metrics_to_calculate}

    slopes = {}
    for col in metrics_to_calculate:
        # Lógica especial para swap (Inversão)
        if col == 'swap-free':
            df_agg['swap_util'] = (pd.to_numeric(df_agg['swap-free'], errors='coerce') - 8192) * -1
            slopes[col] = calculate_slope(df_agg, 't_days', 'swap_util')
        else:
            slopes[col] = calculate_slope(df_agg, 't_days', col)
            
    return slopes

def process_folder(subfolder_path):
    folder_name = subfolder_path.name
    cache_file_path = subfolder_path / "_slope_cache.json"

    if cache_file_path.exists():
        try:
            with open(cache_file_path, 'r') as f:
                return convert_none_to_nan(json.load(f))
        except: pass

    system, software, version = extract_categorical_info(folder_name)
    res = {
        'scenario_folder': folder_name,
        'scenario_label': folder_name,
        'system': system
    }

    # Helper para processar os arquivos com a lógica revisada (load_and_resample)
    def get_slopes(file_name, metrics):
        f_p = subfolder_path / file_name
        if not f_p.exists(): return {m: np.nan for m in metrics}
        df_agg = load_and_resample(f_p, metrics)
        if df_agg.empty: return {m: np.nan for m in metrics}
        
        slopes = {}
        for m in metrics:
            if m == 'swap-free':
                # Inversão do swap: (8192 - livre)
                df_agg['swap_util'] = (pd.to_numeric(df_agg['swap-free'], errors='coerce') - 8192) * -1
                slopes[m] = calculate_slope(df_agg, 't_days', 'swap_util')
            else:
                slopes[m] = calculate_slope(df_agg, 't_days', m)
        return slopes

    # Processamento Memória
    m_slopes = get_slopes("machine_monitoring-mem.csv", ['used', 'cached', 'buffer', 'swap-free'])
    res.update({
        'mem_used_slope': m_slopes.get('used'),
        'mem_cached_slope': m_slopes.get('cached'),
        'mem_buffer_slope': m_slopes.get('buffer'),
        'mem_swap_slope': m_slopes.get('swap-free')
    })

    # Processamento CPU
    c_slopes = get_slopes("machine_monitoring-cpu.csv", ['usr', 'sys'])
    res.update({'cpu_usr_slope': c_slopes.get('usr'), 'cpu_sys_slope': c_slopes.get('sys')})

    try:
        with open(cache_file_path, 'w') as f:
            json.dump(convert_nan_to_none(res), f, indent=4)
    except: pass
    return res

# --- 5. EXECUÇÃO PRINCIPAL (ORQUESTRAÇÃO) ---

def main():
    root_folder_path = Path(LOGS_FOLDER)
    all_results_data = []

    print(f"Analisando pastas em: {root_folder_path.resolve()}")
    if not root_folder_path.exists(): return print("Erro: Pasta não encontrada.")

    subfolder_paths = [p for p in root_folder_path.iterdir() if p.is_dir()]
    for p in subfolder_paths:
        all_results_data.append(process_folder(p))

    if not all_results_data: return print("Nenhum dado processado.")

    results_df = pd.DataFrame(all_results_data)
    
    # Definição das colunas de Slope
    mem_cols = ['mem_used_slope', 'mem_cached_slope', 'mem_buffer_slope', 'mem_swap_slope']
    cpu_cols = ['cpu_usr_slope', 'cpu_sys_slope']
    slope_cols = mem_cols + cpu_cols
    
    # Normalização Min-Max
    scaler = MinMaxScaler()
    norm_cols = []
    for col in slope_cols:
        results_df[col] = results_df[col].fillna(0)
        if results_df[col].nunique() > 1:
            results_df[f'{col}_norm'] = scaler.fit_transform(results_df[[col]])
            norm_cols.append(f'{col}_norm')
        else:
            results_df[f'{col}_norm'] = 0.0

    # Índices de Envelhecimento
    results_df['aging_index_euclidean'] = np.sqrt(results_df[norm_cols].pow(2).sum(axis=1))
    results_df['aging_index_sum'] = results_df[norm_cols].sum(axis=1)
    results_df = results_df.sort_values(by='aging_index_euclidean', ascending=False)

#     # --- SALVAMENTO DE DADOS ---
#     results_df.to_csv(os.path.join(DRIVE_PATH, "aging_analysis_results.csv"), index=False, sep=';')
#     results_df[['scenario_label'] + mem_cols].to_csv(os.path.join(DRIVE_PATH, "memory_analysis_results.csv"), index=False, sep=';')
#     results_df[['scenario_label'] + cpu_cols].to_csv(os.path.join(DRIVE_PATH, "cpu_analysis_results.csv"), index=False, sep=';')

#     # --- GERAÇÃO DE GRÁFICOS (ESTILO ORIGINAL) ---
#     plot_df = results_df.set_index('scenario_label')

#     # A. TABELA DE RESULTADOS (Imagem)
#     plt.figure(figsize=(18, 6))
#     plt.axis('off')
#     cols_tbl = slope_cols + ['aging_index_sum', 'aging_index_euclidean']
#     tbl_data = results_df[['scenario_label'] + cols_tbl].round(6)
#     the_table = plt.table(cellText=tbl_data.values, colLabels=tbl_data.columns, loc='center', cellLoc='center')
#     the_table.auto_set_font_size(False); the_table.set_fontsize(8); the_table.scale(1, 2)
#     plt.title("Tabela Final: Slopes Reais e Índices", pad=20, fontweight='bold')
#     plt.savefig(os.path.join(DRIVE_PATH, "tabela_final_resultados.svg"), bbox_inches='tight'); plt.show()

#     # B. SLOPES BRUTOS: MEMÓRIA
#     plt.figure(figsize=(12, 6))
#     plot_df[mem_cols].plot(kind='bar', ax=plt.gca(), width=0.8)
#     plt.title('Slopes Brutos: Memória (used, cached, buffer, swap)')
#     plt.ylabel('Unidade/Dia'); plt.xticks(rotation=45, ha='right')
#     plt.savefig(os.path.join(DRIVE_PATH, "theil_sen_slopes_mem_raw.svg"), bbox_inches='tight'); plt.show()

#     # C. SLOPES BRUTOS: CPU
#     plt.figure(figsize=(12, 6))
#     plot_df[cpu_cols].plot(kind='bar', ax=plt.gca(), width=0.8, color=['#ff7f0e', '#d62728'])
#     plt.title('Slopes Brutos: CPU (usr, sys)')
#     plt.ylabel('%/Dia'); plt.xticks(rotation=45, ha='right')
#     plt.savefig(os.path.join(DRIVE_PATH, "theil_sen_slopes_cpu_raw.svg"), bbox_inches='tight'); plt.show()

#     # D. SLOPES NORMALIZADOS
#     plt.figure(figsize=(14, 7))
#     plot_df[norm_cols].plot(kind='bar', ax=plt.gca(), width=0.8)
#     plt.title('Slopes Theil-Sen Normalizados (Min-Max)')
#     plt.ylabel('Valor [0-1]'); plt.xticks(rotation=45, ha='right')
#     plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
#     plt.savefig(os.path.join(DRIVE_PATH, "theil_sen_slopes_normalized.svg"), bbox_inches='tight'); plt.show()

#     # E. ÍNDICE EUCLIDIANO
#     plt.figure(figsize=(10, 6))
#     plot_df['aging_index_euclidean'].plot(kind='bar', color='teal', ax=plt.gca())
#     plt.title('Índice de Envelhecimento Euclidiano')
#     plt.xticks(rotation=45, ha='right')
#     plt.savefig(os.path.join(DRIVE_PATH, "aging_index_euclidean.svg"), bbox_inches='tight'); plt.show()

#     # F. ÍNDICE DE SOMA
#     plt.figure(figsize=(10, 6))
#     plot_df['aging_index_sum'].plot(kind='bar', color='purple', ax=plt.gca())
#     plt.title('Índice de Envelhecimento (Soma)')
#     plt.xticks(rotation=45, ha='right')
#     plt.savefig(os.path.join(DRIVE_PATH, "aging_index_sum_normalized.svg"), bbox_inches='tight'); plt.show()

#     print(f"\n✅ Concluído! Gráficos e CSVs salvos em: {DRIVE_PATH}")


# main()


# ==========================================================
    # SALVAMENTO CSV
    # ==========================================================

    results_df.to_csv(os.path.join(DRIVE_PATH, "aging_analysis_results.csv"),
                      index=False, sep=';')

    results_df[['scenario_label'] + mem_cols].to_csv(
        os.path.join(DRIVE_PATH, "memory_analysis_results.csv"),
        index=False, sep=';')

    results_df[['scenario_label'] + cpu_cols].to_csv(
        os.path.join(DRIVE_PATH, "cpu_analysis_results.csv"),
        index=False, sep=';')

    # ==========================================================
    # TABELA FORMATO DO ARTIGO
    # ==========================================================

    from matplotlib import rcParams
    rcParams['font.family'] = 'serif'

    table_df = pd.DataFrame({
        "Virtualizer": results_df['scenario_label'],
        "Usr": results_df['cpu_usr_slope'],
        "Sys": results_df['cpu_sys_slope'],
        "Used": results_df['mem_used_slope'],
        "Cached": results_df['mem_cached_slope'],
        "Buffer": results_df['mem_buffer_slope'],
        "Usr N": results_df['cpu_usr_slope_norm'],
        "Sys N": results_df['cpu_sys_slope_norm'],
        "Used N": results_df['mem_used_slope_norm'],
        "Cached N": results_df['mem_cached_slope_norm'],
        "Buffer N": results_df['mem_buffer_slope_norm'],
        "Aging Index": results_df['aging_index_euclidean']
    }).round(2)

    fig, ax = plt.subplots(figsize=(22, 7))
    ax.axis('off')

    tbl = ax.table(
        cellText=table_df.values,
        colLabels=table_df.columns,
        cellLoc='center',
        loc='center'
    )

    tbl.auto_set_font_size(False)
    tbl.set_fontsize(10)
    tbl.scale(1.2, 2.0)

    plt.title(
        "TABLE V\nSummary of Aging Metrics by Scenario - Theil-Sen",
        fontsize=14,
        fontweight='bold',
        pad=20
    )

    plt.savefig(os.path.join(DRIVE_PATH, "tabela_final_resultados.svg"),
                format="svg",
    bbox_inches="tight")

    plt.savefig(os.path.join(DRIVE_PATH, "tabela_final_resultados.png"),
    bbox_inches="tight")
    plt.close()

    # ==========================================================
    # GRÁFICOS ORIGINAIS (MANTIDOS)
    # ==========================================================

    plot_df = results_df.set_index('scenario_label')

    # MEMÓRIA BRUTO
    plt.figure(figsize=(12, 6))
    plot_df[mem_cols].plot(kind='bar', ax=plt.gca(), width=0.8)
    plt.title('Slopes Brutos: Memória')
    plt.ylabel('Unidade/Dia')
    plt.xticks(rotation=45, ha='right')
    plt.savefig(os.path.join(DRIVE_PATH, "theil_sen_slopes_mem_raw.svg"),
                format="svg",
    bbox_inches="tight")
    plt.close()

    # CPU BRUTO
    plt.figure(figsize=(12, 6))
    plot_df[cpu_cols].plot(kind='bar', ax=plt.gca(), width=0.8)
    plt.title('Slopes Brutos: CPU')
    plt.ylabel('%/Dia')
    plt.xticks(rotation=45, ha='right')
    plt.savefig(os.path.join(DRIVE_PATH, "theil_sen_slopes_cpu_raw.svg"),
                format="svg",
    bbox_inches="tight")
    plt.close()

    # ==========================================================
    # GRÁFICO NORMALIZADO – PADRÃO CONSISTENTE COM SEU FRAMEWORK
    # ==========================================================

    metric_keys = [
        'cpu_sys_slope_norm',
        'cpu_usr_slope_norm',
        'mem_used_slope_norm',
        'mem_cached_slope_norm',
        'mem_buffer_slope_norm'
    ]

    metric_labels = [
        'CPU sys',
        'CPU usr',
        'Mem used',
        'Mem cached',
        'Mem buffer'
    ]

    plot_df = results_df.set_index('scenario_label')
    data = plot_df[metric_keys].values
    scenarios = plot_df.index.tolist()

    n_metrics = len(metric_keys)
    n_groups = len(scenarios)

    x = np.arange(n_groups)
    width = 0.14

    fig, ax = plt.subplots(figsize=(6, 4), dpi=300)

    bars = []
    for i in range(n_metrics):
        bars.append(
            ax.bar(
                x + (i - (n_metrics-1)/2) * width,
                data[:, i],
                width,
                label=metric_labels[i],
                edgecolor='black',
                linewidth=0.6
            )
        )

    # =====================================================
    # VALORES NAS BARRAS (VERTICAL)
    # =====================================================

    threshold_small = 0.12

    for bar_group in bars:
        for bar in bar_group:
            height = bar.get_height()
            x_text = bar.get_x() + bar.get_width() / 2

            if height >= threshold_small:
                ax.text(
                    x_text,
                    height / 2,
                    f"{height:.2f}",
                    ha='center',
                    va='center',
                    rotation=90,
                    fontsize=7
                )
            else:
                ax.text(
                    x_text,
                    height + 0.02,
                    f"{height:.2f}",
                    ha='center',
                    va='bottom',
                    fontsize=7
                )

    # =====================================================
    # EIXOS
    # =====================================================

    ax.set_ylabel("Normalized Slope [0–1]", fontsize=11)
    ax.set_xticks(x)
    ax.set_xticklabels(scenarios, rotation=25, ha='right', fontsize=10)

    ax.set_ylim(0, 1.05)

    ax.tick_params(direction="in", which="both", top=True, right=True)
    ax.minorticks_on()

    # Spines mais visíveis (igual seu padrão)
    for spine in ax.spines.values():
        spine.set_linewidth(1.2)

    # =====================================================
    # LEGENDA (Padrão do seu framework)
    # =====================================================

    ax.legend(
        loc='best',
        fontsize=9,
        ncol=2,
        frameon=True,
        framealpha=0.9,
        edgecolor='black',
        title="Metrics",
        title_fontsize=10
    )

    # =====================================================
    # SALVAR
    # =====================================================

    # plt.savefig(
    #     os.path.join(DRIVE_PATH, "theil_sen_slopes_normalized.svg"),
    #     format="svg"
    # )
    plt.savefig(
        os.path.join(DRIVE_PATH, "theil_sen_slopes_normalized.pdf"),
        format="pdf",
        bbox_inches="tight"
    )

    plt.close()

    # ==========================================================
    # ÍNDICES
    # ==========================================================

    plt.figure(figsize=(10, 6))
    plot_df['aging_index_euclidean'].plot(kind='bar', color='teal')
    plt.title('Aging Index (Euclidean)')
    plt.xticks(rotation=45, ha='right')
    plt.savefig(os.path.join(DRIVE_PATH, "aging_index_euclidean.svg"),
                format="svg",
    bbox_inches="tight")
    plt.close()

    plt.figure(figsize=(10, 6))
    plot_df['aging_index_sum'].plot(kind='bar', color='purple')
    plt.title('Aging Index (Sum)')
    plt.xticks(rotation=45, ha='right')
    plt.savefig(os.path.join(DRIVE_PATH, "aging_index_sum_normalized.svg"),
                format="svg",
    bbox_inches="tight")
    plt.close()

    print(f"\n✅ Concluído! Arquivos gerados em: {os.path.abspath(DRIVE_PATH)}")




main()