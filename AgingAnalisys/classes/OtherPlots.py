import glob
import os
from pathlib import Path
import re
import sys

from matplotlib.cm import get_cmap
import pandas as pd
from matplotlib import pyplot as plt, ticker as mticker
from sklearn.linear_model import LinearRegression
from pymannkendall import original_test
import utils.plot_configs
from utils.ManipulationPandas import ManipulationPandas

import matplotlib.cm as cm
import matplotlib.colors as mcolors


def plot_time_series(save_folder, file_path, title, x_label, y_label, max_labels=20):
    # Carregar os dados do arquivo CSV
    df = pd.read_csv(file_path, sep=";")

    # Converter a coluna 'date_time' para o tipo datetime
    df['date_time'] = pd.to_datetime(df['date_time'])

    # Calcular o tempo decorrido em horas
    df['elapsed_hours'] = (df['date_time'] - df['date_time'].min()).dt.total_seconds() / 3600

    # Converter valores de nanosegundos para segundos (exceto 'date_time' e 'elapsed_hours')
    for col in df.columns:
        if col not in ['date_time', 'elapsed_hours']:
            df[col] = df[col] / 1e9  # Convertendo nanosegundos para segundos

    # Para cada coluna (exceto 'date_time' e 'elapsed_hours'), plota um gráfico separado
    for col in df.columns:
        if col not in ['date_time', 'elapsed_hours']:
            plt.figure(figsize=(10, 6))

            # Plotar a série temporal com o eixo X em horas
            plt.plot(df['elapsed_hours'], df[col], label=col)

            # Adicionar título e rótulos dos eixos
            plt.title(f"{title} - {col}")
            plt.xlabel(x_label)
            plt.ylabel(y_label)

            # Adicionar legenda
            plt.legend()

            # Ajustar layout para evitar sobreposição e salvar o gráfico
            plt.tight_layout()
            plt.grid(True)
            plt.savefig(save_folder.joinpath(f"{title} - {col}.png"))

    return 1



def plot(
        filename,
        ylabel,
        datetime="date_time",
        dayfirst=False,
        title=None,
        separator=';',
        decimal_separator=",",
        division=1,
        includeColYlabel=False,
        cols_to_divide=None,
        apply_mann_kendall=True,
        highlight_intervals=None,
        x_lim=None,
        y_lim=None
):
    if cols_to_divide is None:
        cols_to_divide = []

    print(f"\n[DEBUG] Iniciando plotagem do arquivo: {filename}")

    try:
        df = pd.read_csv(filename,
                         sep=separator,
                         decimal=decimal_separator,
                         dayfirst=dayfirst,
                         parse_dates=[datetime])
        print(f"[DEBUG] Leitura do CSV concluída. Colunas disponíveis: {df.columns.tolist()}")
    except Exception as e:
        print(f"[ERROR] Falha ao ler arquivo {filename}: {e}")
        return 0

    # Renomear a coluna datetime para 'seconds' para processamento
    if datetime in df.columns:
        df = df.rename(columns={datetime: 'seconds'})
        print(f"[DEBUG] Coluna '{datetime}' renomeada para 'seconds'")
    else:
        print(f"[ERROR] Coluna '{datetime}' não encontrada no arquivo.")
        return 0

    # Mostrar alguns valores da coluna de datas para verificação
    print(f"[DEBUG] Exemplos de valores na coluna 'seconds' antes da conversão:\n{df['seconds'].head()}")

    try:
        # Converte para diferença em horas desde o primeiro registro
        df['seconds'] = (df['seconds'] - df['seconds'].iloc[0]).dt.total_seconds() / 3600
        print(f"[DEBUG] Conversão da coluna 'seconds' realizada com sucesso. Exemplos:\n{df['seconds'].head()}")
    except Exception as e:
        print(f"[ERROR] Falha na conversão da coluna 'seconds': {e}")
        return 0

    # Definindo index e tentando converter valores numéricos
    try:
        df = df.set_index('seconds')
        print(f"[DEBUG] 'seconds' configurado como índice.")
        df = df.replace(',', '.', regex=True).apply(lambda x: pd.to_numeric(x))
        print(f"[DEBUG] Conversão de valores numéricos realizada. Exemplos das primeiras linhas:\n{df.head()}")
    except Exception as e:
        print(f"[ERROR] Falha na conversão numérica dos dados: {e}")
        return 0

    # Define quais colunas dividir pelo divisor
    if len(cols_to_divide) == 0:
        cols_to_divide = df.columns.tolist()
    print(f"[DEBUG] Colunas que terão divisão aplicada: {cols_to_divide}")

    try:
        df[cols_to_divide] = df[cols_to_divide].div(division)
        print(f"[DEBUG] Divisão aplicada nas colunas selecionadas pelo valor {division}. Exemplos:\n{df[cols_to_divide].head()}")
    except Exception as e:
        print(f"[ERROR] Falha ao dividir colunas: {e}")
        return 0

    # Loop para plotar cada coluna
    for col in df.columns:
        print(f"[DEBUG] Preparando plotagem para a coluna: {col}")

        col_mix = col + " " + ylabel if isinstance(ylabel, str) and includeColYlabel else ylabel

        # Preenchendo NaNs
        df[col] = df[col].fillna(0)
        print(f"[DEBUG] NaNs preenchidos com zero na coluna '{col}'.")

        # Tratamento específico para coluna 'swap'
        if col == "swap":
            df[col] = (df[col] - 8192) * -1
            print(f"[DEBUG] Ajuste específico aplicado na coluna 'swap'.")

        try:
            ax = df.plot(
                y=col,
                legend=False,
                xlabel='Time(h)',
                ylabel=col_mix if isinstance(ylabel, str) else ylabel.get(col, col),
                figsize=(10, 10),
                style='k',
                linewidth=3
            )
            print(f"[DEBUG] Gráfico criado para coluna '{col}'.")
        except Exception as e:
            print(f"[ERROR] Falha ao criar gráfico para coluna '{col}': {e}")
            continue

        ax.set_xlabel('Time(h)', labelpad=15)

        if x_lim is not None:
            ax.set_xlim(right=x_lim)
            print(f"[DEBUG] Limite do eixo x aplicado: {x_lim}")
        if y_lim is not None:
            ax.set_ylim(top=y_lim)
            print(f"[DEBUG] Limite do eixo y aplicado: {y_lim}")

        if highlight_intervals is not None:
            for interval in highlight_intervals:
                start, end, color, alpha = interval
                ax.axvspan(start, end, color=color, alpha=alpha)
            print(f"[DEBUG] Intervalos destacados no gráfico: {highlight_intervals}")

        if apply_mann_kendall:
            try:
                from sklearn.linear_model import LinearRegression
                x = df.index.to_numpy().reshape((-1, 1))
                y = df[col].to_numpy().reshape((-1, 1))
                model = LinearRegression()
                model.fit(x, y)
                Y_pred = model.predict(x)
                ax.plot(x, Y_pred, color='red', linewidth=3)
                print(f"[DEBUG] Regressão linear aplicada para coluna '{col}'.")

                # Supondo que original_test é definido em algum lugar no seu código
                test_result = original_test(df[col])
                
                print(f"[DEBUG] mannkendall test result '{test_result}'.")
                
                trend_text = (
                    f"trend: {test_result.trend}\n"
                    f"p-value: {test_result.p:.4f}\n"
                    f"z: {test_result.z:.4f}"
                )
                ax.text(
                    0.95, 0.05, trend_text,
                    transform=ax.transAxes,
                    fontsize=18,
                    verticalalignment='bottom',
                    horizontalalignment='right',
                    bbox=dict(boxstyle="round", alpha=0.8, color='white')
                )
                print(f"[DEBUG] Teste de Mann-Kendall aplicado e texto inserido no gráfico.")
            except Exception as e:
                print(f"[ERROR] Falha na aplicação do Mann-Kendall ou regressão na coluna '{col}': {e}")

        for spine in ax.spines.values():
            spine.set_linewidth(1.5)

        try:
            fig = ax.get_figure()
            ManipulationPandas.salvarFigura(ax=ax, nomeFigura=f'./imagens_plottadas/{title}_{col}.svg')
            print(f"[DEBUG] Figura salva: ./imagens_plottadas/{title}_{col}.svg")
            plt.close()
        except Exception as e:
            print(f"[ERROR] Falha ao salvar figura para coluna '{col}': {e}")

    print(f"[DEBUG] Plotagem concluída para o arquivo: {filename}\n")
    return 1




def plot_jmeter(folder, file_name, ignore_chunck=False, chunk_size=10000000, throughput_interval=60):
    if not ignore_chunck:
        chunks = pd.read_csv(folder.joinpath(file_name), chunksize=chunk_size, low_memory=False, sep=",")

        # DataFrame acumulativo para todas as chunks
        df_total = pd.DataFrame()
        for i, chunk in enumerate(chunks):
            print(f'Processing chunk {i}')
            # Acumula os dados do chunk no dataframe total
            df_total = pd.concat([df_total, chunk], ignore_index=True)
    else:
        df_total = pd.read_csv(folder.joinpath(file_name), low_memory=False, sep=",")


    print(df_total)

    # Converter 'timeStamp' para segundos (relativos ao início)
    df_total['timeStamp'] = (df_total['timeStamp'] - df_total['timeStamp'].min()) / 1000  # Em segundos

    # Gerar as métricas gerais
    metricas_geral = calcular_metricas(df_total)
    print("General metrics (considering all chunks):")
    for key, value in metricas_geral.items():
        print(f"{key}: {value}")

    # Obter os labels únicos da coluna 'label'
    unique_labels = df_total['label'].unique()

    # Gerar gráficos de série temporal para cada label
    for label in unique_labels:
        df_label = df_total[df_total['label'] == label]

        # Gerar o gráfico de série temporal para o label específico
        plt.figure(figsize=(10, 6))
        plt.plot(df_label['timeStamp'] / 3600, df_label['elapsed'], label=f'Response Time (ms) - {label}', color='blue')

        # Configurações do gráfico
        plt.title(f'Time Series of Response Time - {label}')
        plt.xlabel('Time (hours)')
        plt.ylabel('Response Time (seconds)')
        plt.grid(True)
        plt.legend()

        # Exibir o gráfico
        plt.tight_layout()
        plt.savefig(folder.joinpath('plots_img/jmeter').joinpath(f"Time Series of Response Time - {label}.png"))
        plt.show()

    # Gerar o gráfico de série temporal geral (todos os labels juntos)
    plt.figure(figsize=(10, 6))
    plt.plot(df_total['timeStamp'] / 3600, df_total['elapsed'], label='Overall Response Time (ms)', color='red')

    # Configurações do gráfico geral
    plt.title('Time Series of Overall Response Time')
    plt.xlabel('Time (hours)')
    plt.ylabel('Response Time (seconds)')
    plt.grid(True)
    plt.legend()

    # Exibir o gráfico geral
    plt.tight_layout()
    plt.savefig(folder.joinpath('plots_img/jmeter').joinpath('Time Series of Overall Response Time.png'))
    plt.show()

    # Adiciona a coluna de intervalo de tempo em minutos
    df_total['timeBucket'] = (df_total['timeStamp'] // throughput_interval) * throughput_interval

    # Calcular a vazão em cada intervalo de tempo
    throughput_df = df_total.groupby('timeBucket').size().reset_index(name='Throughput')

    # Gerar o gráfico de série temporal da vazão
    plt.figure(figsize=(10, 6))
    plt.plot(throughput_df['timeBucket'] / 3600, throughput_df['Throughput'], label='Throughput (requests/interval)', color='green')

    # Configurações do gráfico de vazão
    plt.title('Time Series of Throughput')
    plt.xlabel('Time (hours)')
    plt.ylabel(f'Throughput (requests per {throughput_interval} seconds)')
    plt.grid(True)
    plt.legend()

    # Exibir o gráfico de vazão
    plt.tight_layout()
    plt.savefig(folder.joinpath('plots_img/jmeter').joinpath('Time Series of Throughput.png'))
    plt.show()
    return 1

def calcular_metricas(df):
    metricas = {}

    # Amostras (# Samples)
    metricas['# Samples'] = df.shape[0]

    # Média (Mean)
    metricas['Mean'] = df['elapsed'].mean() / 1000  # Converte para segundos

    # Min (Minimum)
    metricas['Min'] = df['elapsed'].min() / 1000  # Converte para segundos

    # Max (Maximum)
    metricas['Max'] = df['elapsed'].max() / 1000  # Converte para segundos

    # Desvio Padrão (Standard Deviation)
    metricas['Standard Deviation'] = df['elapsed'].std() / 1000  # Converte para segundos

    # Contagem de Erros (Number of Errors)
    metricas['Error Count'] = df[df['success'] == False].shape[0]

    # % de Erro (Percentage of Errors)
    metricas['Error Percentage'] = (metricas['Error Count'] / metricas['# Samples']) * 100

    # Vazão (Throughput)
    total_time = (df['timeStamp'].max() - df['timeStamp'].min())  # Em segundos
    metricas['Throughput'] = metricas['# Samples'] / total_time if total_time > 0 else 0

    return metricas


def plot_fragmentation(folder, merge_equals=True, process_per_plot=50, relevant_maximum=200,
                       time_threshold=None, name_filter=None, adjust_x_limits=False, highlight_processes=None,
                       top_n_processes=None, cache_file='processed_data_cache.csv', cut_dataset=None, exclude_names=None):
    folder = Path(folder)
    cache_path = folder.joinpath(cache_file)

    # Verificar se o arquivo de cache existe
    if os.path.exists(cache_path):
        print("Carregando dados do cache...")
        final_dataset = pd.read_csv(cache_path, parse_dates=['datetime'])
    else:
        print("Processando os arquivos e salvando o cache...")
        # Processar todos os arquivos
        final_dataset = process_all_files(folder)  # Uses optimized processing chain

        # Converter 'process_occurrences' para numérico (already done in load_and_split, but good for safety)
        final_dataset['process_occurrences'] = pd.to_numeric(final_dataset['process_occurrences'],
                                                             errors='coerce').fillna(0).astype(int)

        # Salvar o dataset processado no arquivo de cache
        if not final_dataset.empty:
            final_dataset.to_csv(cache_path, index=False)
        else:
            print("Warning: final_dataset is empty, skipping cache save.")
            # If final_dataset is empty, we should probably return or handle this
            # as plotting will fail. For now, let it proceed to see errors if any.

    if final_dataset.empty:
        print("No data to plot after processing/loading from cache.")
        return 0  # Or some other indicator of no action

    print("Final dataset loaded/processed.")

    if merge_equals:
        print("Applying merge_equalcut_datasets logic...")
        # 1. Simplify 'process' column: apply extract_name_pid to get just the name part.
        #    The original loop updated final_dataset.loc[index, 'process'] = name
        final_dataset['process'] = final_dataset['process'].apply(lambda x: extract_name_pid(x)[0])

        # 2. Perform the cumulative sum logic.
        #    The original loop:
        #       if name in lastFounds: final_dataset.loc[index, 'process_occurrences'] += lastFounds[name]
        #       lastFounds[name] = final_dataset.loc[index, 'process_occurrences']
        #    This is equivalent to a groupby().cumsum() if 'process_occurrences' are the base values
        #    that need to be summed up chronologically for each simplified process name.
        #    `sort=False` is crucial to mimic the original row-by-row processing order.
        final_dataset['process_occurrences'] = final_dataset.groupby('process', sort=False)[
            'process_occurrences'].cumsum()
        print("merge_equals logic applied.")

    # 1. Agrupar os dados pelo processo (simplified name if merge_equals was true)
    grouped = final_dataset.groupby('process')

    # 2. Criar um subdataset para cada processo
    subdatasets = {process: group.copy() for process, group in
                   grouped}  # Use .copy() to avoid SettingWithCopyWarning later

    # 3. Filtrar os subdatasets onde o valor da última ocorrência é maior que o limite
    #    Ensure 'process_occurrences' is not empty before accessing iloc[-1]
    subdatasets_filtrados = {
        process: data for process, data in subdatasets.items()
        if not data['process_occurrences'].empty and data['process_occurrences'].iloc[-1] > relevant_maximum
    }

    # Filtro adicional por tempo, se 'time_threshold' for especificado
    if time_threshold is not None:
        subdatasets_filtrados = {
            process: data for process, data in subdatasets_filtrados.items()
            if not data['datetime'].empty and (
                        data['datetime'].max() - data['datetime'].min()).total_seconds() / 3600 <= time_threshold
        }

    # Filtro adicional por nome de processo, se 'name_filter' for especificado
    if name_filter is not None:
        name_filter_set = set(name_filter)  # Use a set for faster lookups if name_filter is large
        subdatasets_filtrados = {
            process: data for process, data in subdatasets_filtrados.items()
            if any(f in process for f in name_filter_set)
        }
        
    if exclude_names is not None:
        exclude_names = set(exclude_names)
        subdatasets_filtrados = {
            process: data for process, data in subdatasets_filtrados.items()
            if extract_name_pid(process)[0] not in exclude_names
        }

    # Separar os processos destacados
    highlighted_subdatasets = {}
    if highlight_processes:
        for process_name in highlight_processes:
            if process_name in subdatasets_filtrados:
                highlighted_subdatasets[process_name] = subdatasets_filtrados.pop(process_name)

    y_formatter = mticker.ScalarFormatter(useMathText=True)
    y_formatter.set_scientific(True)
    y_formatter.set_powerlimits((-1, 1))

    # Plotar gráficos para os processos destacados (em um único gráfico)
    if highlighted_subdatasets:
        fig, ax = plt.subplots(figsize=(15, 10))
        for process, subset in highlighted_subdatasets.items():
            subset['time_in_hours'] = (subset['datetime'] - subset['datetime'].min()).dt.total_seconds() / 3600
            ax.step(subset['time_in_hours'], subset['process_occurrences'], where='post', label=f'{process}', linewidth=3)

        # ax.legend(loc='best', fontsize='small', title='Process')
        ax.legend(loc='best', fontsize='small', ncol=2, frameon=True, framealpha=0.9, edgecolor='black', title='Process')
        ax.set_xlabel('Time (hours)')
        ax.set_ylabel('Process occurrences', labelpad=15)

        if adjust_x_limits:
            max_time = max(
                (subset['datetime'].max() - subset['datetime'].min()).total_seconds() / 3600
                for subset in highlighted_subdatasets.values()
            )
            ax.set_xlim([0, max_time])

        for spine in ax.spines.values():
            spine.set_linewidth(1.5)

        plt.tight_layout()
        plt.savefig(f"imagens_plottadas/time_series_memory_fragmentation_Process_{i * process_per_plot + 1}_{(i + 1) * process_per_plot}.svg", bbox_inches='tight', dpi=300, format="svg")
        plt.close(fig)

    # 4. Ordenar os subdatasets filtrados (remaining after highlight pop) pelo último valor de 'process_occurrences'
    # Ensure 'process_occurrences' is not empty before accessing iloc[-1]
    subdatasets_ordenados = dict(
        sorted(
            (item for item in subdatasets_filtrados.items() if not item[1]['process_occurrences'].empty),
            # Filter out empty occurrences series
            key=lambda item: item[1]['process_occurrences'].iloc[-1],
            reverse=True
        )
    )

    # Se 'top_n_processes' for especificado, limitar aos N processos com mais ocorrências
    if top_n_processes is not None:
        subdatasets_ordenados = dict(list(subdatasets_ordenados.items())[:top_n_processes])

    # 5. Definir o tempo máximo entre todos os subdatasets filtrados, se o ajuste do eixo X estiver ativado
    max_time_overall = 0
    if adjust_x_limits and subdatasets_ordenados:
        # Calculate time_in_hours for all relevant datasets first to find the true max_time
        temp_max_times = []
        for process_name_ord, data_ord in subdatasets_ordenados.items():
            if data_ord['datetime'].min() == data_ord['datetime'].max():
                data_ord.loc[:, 'time_in_hours'] = 0
                temp_max_times.append(0)
            else:
                data_ord.loc[:, 'time_in_hours'] = (data_ord['datetime'] - data_ord[
                    'datetime'].min()).dt.total_seconds() / 3600
                if not data_ord['time_in_hours'].empty:
                    temp_max_times.append(data_ord['time_in_hours'].max())
        if temp_max_times:  # Check if list is not empty
            max_time_overall = max(temp_max_times)

    # 6. Plotar os gráficos apenas com os processos que atendem ao critério e já estão ordenados
    process_list = list(subdatasets_ordenados.keys())
    if not process_list:  # If no processes left to plot
        print("No regular processes to plot after filtering and highlighting.")
        return 1  # Or 0 if highlighted plots were also not made.

    num_plots_to_generate = (len(process_list) - 1) // process_per_plot + 1 if process_per_plot > 0 else 0

    for i in range(num_plots_to_generate):
        fig, ax = plt.subplots(figsize=(15, 10))
        processes_to_plot_on_this_fig = process_list[i * process_per_plot:(i + 1) * process_per_plot]

        color_map = cm.get_cmap('nipy_spectral', len(process_list))
            
        current_max_time_for_plot = 0  # For non-adjust_x_limits case per plot
        
        # for process_name_iter in processes_to_plot_on_this_fig:
        for idx, process_name_iter in enumerate(processes_to_plot_on_this_fig):
            subset = subdatasets_ordenados[process_name_iter]
            # 'time_in_hours' should already be calculated if adjust_x_limits was true.
            # If not, it needs to be calculated here.
            if 'time_in_hours' not in subset.columns:
                if subset['datetime'].min() == subset['datetime'].max():
                    subset.loc[:, 'time_in_hours'] = 0
                else:
                    subset.loc[:, 'time_in_hours'] = (subset['datetime'] - subset[
                        'datetime'].min()).dt.total_seconds() / 3600
                    
                    
            color = color_map(idx % color_map.N)
            # ax.step(subset['time_in_hours'], subset['process_occurrences'], where='post', label=f'{process_name_iter}', linewidth=5)
            ax.step(subset['time_in_hours'], subset['process_occurrences'], where='post', label=f'{process_name_iter}', linewidth=5, color=color)
            if not adjust_x_limits and not subset['time_in_hours'].empty:  # find max time for this plot only
                current_max_time_for_plot = max(current_max_time_for_plot, subset['time_in_hours'].max())

        # ax.legend(loc='best', fontsize='small', title='Process', ncol=2)
        ax.legend(loc='best', fontsize='small', ncol=2, frameon=True, framealpha=0.9, edgecolor='black', title='Process')
        ax.set_xlabel('Time (hours)')
        ax.set_ylabel('Process occurrences', labelpad=15)

        if adjust_x_limits:
            ax.set_xlim([0, max_time_overall if max_time_overall > 0 else 1])
        else:  # Set x_lim based on current plot's data if not adjusting globally
            ax.set_xlim([0, current_max_time_for_plot if current_max_time_for_plot > 0 else 1])

        for spine in ax.spines.values():
            spine.set_linewidth(1.5)

        plt.tight_layout()
        plt.savefig(f"imagens_plottadas/time_series_memory_fragmentation_Process_{i * process_per_plot + 1}_{(i + 1) * process_per_plot}.svg", bbox_inches='tight', dpi=300, format="svg")
        plt.close(fig)

    return 1


def extract_name_pid(process_str):
    """Extrai o nome do processo e o PID da string 'nome_do_processo(pid)'."""
    if pd.isna(process_str):
        return "UNKNOWN", None
    process_str = str(process_str)
    
    match = re.match(r"(.*)\((\d+)\)", process_str)
    if match:
        return match.groups()  # Retorna (nome_do_processo, pid)
    return process_str, None


def load_and_split_dataset(file_path, cut_dataset=None):
    # Load the dataset
    df = pd.read_csv(file_path, sep=';')
    
    print(df.tail(5))
    
    if cut_dataset != None:
            print(df.columns)
            
            try:
                df['datetime'] = pd.to_datetime(df['datetime'], format='%a %b %d %H:%M:%S %Y')
                cut_dataset = pd.to_datetime(cut_dataset)                
                
                df = df[df['datetime'] <= cut_dataset]
                
            except:
                df = df[df['seconds'] <= cut_dataset]
                
    
    print(df.tail(5))
    df['process_occurrences'] = pd.to_numeric(df['process_occurrences'], errors='coerce').fillna(0).astype(int)

    # Create a group identifier that increments each time 'process' is 'EMPTIED'
    df['group'] = (df['process'] == 'EMPTIED').cumsum()

    # Remove 'EMPTIED' rows
    df = df[df['process'] != 'EMPTIED']

    # Split the DataFrame into subdatasets based on the group identifier
    subdatasets = [group_df.reset_index(drop=True) for _, group_df in df.groupby('group')]

    return subdatasets


def process_subdatasets(subdatasets, process_counts):
    # Iterar sobre cada subdataset
    for i, subdataset in enumerate(subdatasets):
        # Converter a coluna 'datetime' para um objeto datetime
        subdataset['datetime'] = pd.to_datetime(subdataset['datetime'], format='%a %b %d %H:%M:%S %Y')

        for index, row in subdataset.iterrows():
            # Extrair nome e pid da coluna 'process'
            process_name, pid = extract_name_pid(row['process'])
            parent_name, ppid = extract_name_pid(row['parent'])

            # Chave que identifica o processo
            process_key = (process_name, parent_name, row['UID'], pid, ppid)

            # Verificar se o processo já foi visto antes
            if process_key in process_counts:
                # Incrementar o valor de 'process_occurrences' com base na última vez que o processo foi encontrado
                subdataset.at[index, 'process_occurrences'] += process_counts[process_key]

            # Atualizar o contador com o valor atual de 'process_occurrences'
            process_counts[process_key] = subdataset.at[index, 'process_occurrences']

        # Substitui o subdataset processado pelo novo
        subdatasets[i] = subdataset

    return subdatasets, process_counts


def process_all_files(directory, cut_dataset=None):
    # Encontrar todos os arquivos que começam com 'fragmentation_'
    
    pattern = os.path.join(directory, '*fragmentation.csv')
    files = glob.glob(pattern)

    all_datasets = []
    process_counts = {}  # Armazenará os processos do último subdataset processado

    for file_path in files:
        print(f"Processando arquivo: {file_path}")
        # Carregar e dividir o dataset em subdatasets
        subdatasets = load_and_split_dataset(file_path, cut_dataset)

        # Processar cada subdataset e atualizar as contagens de processos
        processed_subdatasets, process_counts = process_subdatasets(
            subdatasets,
            process_counts
        )

        # Unir todos os subdatasets processados
        merged_dataset = pd.concat(processed_subdatasets, ignore_index=True)

        # Adicionar ao conjunto de todos os datasets
        all_datasets.append(merged_dataset)

    # Concatenar todos os datasets em um só
    final_dataset = pd.concat(all_datasets, ignore_index=True)
    return final_dataset