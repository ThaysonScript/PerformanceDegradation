import pandas as pd
from pymannkendall import original_test
from pathlib import Path
from sklearn.preprocessing import MinMaxScaler

def extract_categorical_info(folder_name='debian'):
    print(f"[INFO] Extraindo informações categóricas da pasta: {folder_name}")
    system = None
    software = None
    version = None

    if "debian" in folder_name:
        system = "Debian 12"
    elif "ubuntu22" in folder_name:
        system = "Ubuntu 22.04"
    elif "ubuntu24" in folder_name:
        system = "Ubuntu 24.04"

    if "docker" in folder_name:
        software = "Docker"
        version = "27.2" if "novo" in folder_name else "23"
    elif "podman" in folder_name:
        software = "Podman"
        version = "5.1.3"

    print(f"[INFO] Sistema: {system}, Software: {software}, Versão: {version}")
    return system, software, version


def perform_mann_kendall_analysis(data, columns, intervals):
    print(f"[INFO] Iniciando análise Mann-Kendall com colunas: {columns}")
    results = []
    for label, (start, end) in intervals.items():
        print(f"[DEBUG] Intervalo '{label}': de {start} até {end} horas")
        subset = data[(data.index >= start) & (data.index <= end)]
        print(f"[DEBUG] Subconjunto de dados tem {len(subset)} linhas")
        if subset.empty:
            print(f"[WARNING] Intervalo '{label}' está vazio, pulando...")
            continue
        for col in columns:
            if col not in subset.columns:
                print(f"[WARNING] Coluna '{col}' não está no subconjunto, pulando...")
                continue
            print(f"[DEBUG] Analisando coluna '{col}' no intervalo '{label}'")
            mk_result = original_test(subset[col])
            results.append({
                "Interval": label,
                "Resource": col,
                "Trend": mk_result.trend,
                "p-value": mk_result.p,
                "z": mk_result.z
            })
    return results


def normalize_columns(df, columns):
    print(f"[INFO] Normalizando colunas: {columns}")
    for column in columns:
        if column in df.columns:
            min_val = df[column].min()
            max_val = df[column].max()
            print(f"[DEBUG] Coluna '{column}': min={min_val}, max={max_val}")
            df[column] = (df[column] - min_val) / (max_val - min_val) if max_val > min_val else 0
    return df


def analyze_file_return(file_path):
    """Retorna a lista de resultados da análise para um arquivo .csv."""
    output_data = []
    try:
        file_name = file_path.name
        print(f"[Worker] Analisando: {file_name}")

        system, software, version = extract_categorical_info(file_path.parent.name)

        intervals = {
            "Full": (0, float('inf')),
            "0 to 0.5 days": (0, 12),
            "0.5 days to 3.5 days": (12, 84),
            "3.5 to 4 days": (84, 96),
            "4 days to 7 days": (96, 168),
            "7 to 7.5 days": (168, 180),
            "7.5 days to 10.5 days": (180, 252),
            "10.5 to 11 days": (252, 264),
            "11 days to 14 days": (264, 336),
        }

        df = pd.read_csv(file_path, sep=';', parse_dates=['date_time'])
        df = df.replace(',', '.', regex=True)
        df['elapsed_hours'] = (df['date_time'] - df['date_time'].min()).dt.total_seconds() / 3600
        df = df.set_index('elapsed_hours')
        df = df.drop(columns=['date_time'], errors='ignore')
        df = df.apply(pd.to_numeric, errors='coerce')

        if "swap" in df.columns:
            df["swap"] = (df["swap"] - 8192) * -1

        target_columns = [col for col in df.columns if col != 'elapsed_hours']
        mk_results = perform_mann_kendall_analysis(df, target_columns, intervals)

        for res in mk_results:
            res.update({
                "System": system,
                "Resource": file_name.replace(".csv", "") + " - " + res["Resource"],
                "Software": software,
                "Software Version": version,
            })
            output_data.append(res)

        print(f"[Worker] Finalizado: {file_name}")
    except Exception as e:
        print(f"[Worker] Erro em {file_path.name}: {e}")
    return output_data



from concurrent.futures import ProcessPoolExecutor, as_completed

def main(base_directory, output_csv_path):
    base_path = Path(base_directory)
    file_paths = list(base_path.glob("*.csv"))
    output_data = []

    print(f"🟢 Iniciando análise paralela com {len(file_paths)} arquivos...")

    with ProcessPoolExecutor() as executor:
        futures = {executor.submit(analyze_file_return, file_path): file_path for file_path in file_paths}
        for future in as_completed(futures):
            file_path = futures[future]
            try:
                results = future.result()
                output_data.extend(results)
            except Exception as e:
                print(f"[Main] Erro ao processar {file_path.name}: {e}")

    print(f"💾 Salvando resultados em: {output_csv_path}")
    results_df = pd.DataFrame(output_data)
    results_df.to_csv(output_csv_path, index=False)
    print("✅ Análise finalizada.")



# Executar
base_directory = "/home/thayson/repositorios/AgingAnalisys/logs_monitoramento/xen"  # Substitua se necessário
output_csv_path = "/home/thayson/repositorios/AgingAnalisys/imagens_plottadas/mann_kendall_results.csv"
main(base_directory, output_csv_path)

print(f"[FINAL] Resultados Mann-Kendall salvos em: {output_csv_path}")
