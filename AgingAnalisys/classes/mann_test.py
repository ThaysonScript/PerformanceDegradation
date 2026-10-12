from sklearn.linear_model import LinearRegression
from matplotlib import pyplot as plt
import pandas as pd
from pymannkendall import original_test
from pathlib import Path
import plot_configs


def common_ylabels():
    return {
        'cpu': 'Cpu Utilization (\\%)',
        'mem': 'Memory Usage (\\%)',
        'vmrss': 'Physical Memory (MB)',
        'vsz': 'Virtual Memory (MB)',
        'threads': 'Thread Count',
        'swap': 'Swap Usage (MB)'
    }
    

def common_cpu_labels():
    return {
        '%usr': 'User Cpu Usage (\\%)',
        '%nice': 'Nice Cpu Usage (\\%)',
        '%sys': 'System Cpu Usage (\\%)',
        '%iowait': 'I/O Wait Cpu Usage (\\%)',
        '%soft': 'Soft Cpu Usage (\\%)'
    }
    

def plot(title=None, file='',
         cols_to_divide=None, datetime='date_time', division=1, ylabel='cpu', includeColYlabel=False,
         x_lim=None, y_lim=None, highlight_intervals=None, dayfirst=False):
    
    print(f"Lendo arquivo: {file}")
    df = pd.read_csv(file, sep=';', dayfirst=dayfirst)
    
    # Converte vírgulas para pontos apenas nas colunas numéricas
    for col in df.columns:
        if col != datetime:
            df[col] = df[col].astype(str).str.replace(',', '.', regex=False)
            df[col] = pd.to_numeric(df[col], errors='coerce')


    # Converte a coluna de datas para datetime, com segurança
    df[datetime] = pd.to_datetime(df[datetime], errors='coerce')
    print("Coluna datetime convertida:", df[datetime].head())

    # Remove linhas com datas inválidas, se houver
    df = df.dropna(subset=[datetime])

    # Define o índice como datetime
    df = df.set_index(datetime)
    print("Index definido como DatetimeIndex.")

    # Aplica o resample
    df = df.resample('1T').mean()
    # df = df.resample('30S').mean()
    print("Resample aplicado com média a cada 5 minutos.")

    # Converte o índice para horas decimais
    df['seconds'] = (df.index - df.index[0]).total_seconds() / 3600
    df = df.set_index('seconds')
    print("Index convertido para horas decimais.")
    
    for col in df.columns:
        print(f"\nProcessando coluna: {col}")
        col_mix = col + " " + ylabel if isinstance(ylabel, str) and includeColYlabel else ylabel

        df[col] = df[col].fillna(0)
        print(f"Valores NaN substituídos por 0 em {col}")

        if col == "swap":
            df[col] = (df[col] - 8192) * -1
            print("Transformação aplicada para coluna 'swap'.")

        print(f"Gerando gráfico para {col}...")
        ax = df.plot(
            y=col,
            legend=0,
            xlabel='Time(h)',
            ylabel=col_mix if isinstance(ylabel, str) else ylabel[col] if isinstance(ylabel, dict) and col in ylabel else col,
            figsize=(15, 10),
            style='k',
            linewidth=3
        )

        ax.set_xlabel('Time(h)', labelpad=15)

        if x_lim is not None:
            ax.set_xlim(right=x_lim)
            print(f"x_lim aplicado: {x_lim}")
        if y_lim is not None:
            ax.set_ylim(top=y_lim)
            print(f"y_lim aplicado: {y_lim}")

        if highlight_intervals is not None:
            for interval in highlight_intervals:
                start, end, color, alpha = interval
                ax.axvspan(start, end, color=color, alpha=alpha)
            print(f"Intervalos destacados: {highlight_intervals}")

        # Regressão linear
        x = df.index.to_numpy().reshape((-1, 1))
        y = df[col].to_numpy().reshape((-1, 1))
        model = LinearRegression()
        model.fit(x, y)
        Y_pred = model.predict(x)
        print(f"Coeficiente da regressão para {col}: {model.coef_[0][0]:.4f}")
        ax.plot(x, Y_pred, color='red', linewidth=3)

        # Mann-Kendall
        test_result = original_test(df[col])
        print(f"Mann-Kendall para {col}: trend={test_result.trend}, p={test_result.p:.4f}, z={test_result.z:.4f}")
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

        for spine in ax.spines.values():
            spine.set_linewidth(1.5)

        fig = ax.get_figure()
        folder = Path('/home/thayson/repositorios/AgingAnalisys/imagens_plottadas')
        folder.mkdir(parents=True, exist_ok=True)
        filename = folder / f"{title}-{col}.svg"
        fig.savefig(filename, bbox_inches='tight', dpi=300, format="svg")
        print(f"Gráfico salvo em: {filename}")

        plt.close()
    
    print("Processamento completo.")
    return 1


files = '/home/thayson/repositorios/AgingAnalisys/logs_monitoramento/xen'

sum_cpu = f'{files}/cpu_monitoring_sumAllCores.csv'
frag = f'{files}/fragmentation.csv'
cpu_mean = f'{files}/machine_monitoring-cpu.csv'
disk = f'{files}/machine_monitoring-disk.csv'
mem = f'{files}/machine_monitoring-mem.csv'
zombie = f'{files}/machine_monitoring-zombies.csv'
nginx = f'{files}/nginx_response.csv'
oxenstored = f'{files}/xen_monitoring-oxenstored.csv'
xenballon = f'{files}/xen_monitoring-xen-ballon.csv'
xenbus = f'{files}/xen_monitoring-xenbus.csv'
xenconsoled = f'{files}/xen_monitoring-xenconsoled.csv'
xenDom0 = f'{files}/xenDomain0MetricsMonitoring.csv'
xenVm = f'{files}/xenVmMetricsMonitoring.csv'

# plot(
#     file=sum_cpu, 
#     title="CPU Utilization Across All Cores Over Time", 
#     cols_to_divide=[
#         '%usr', '%nice', '%sys', '%iowait', '%soft',
#     ],
#     ylabel={
#         **common_cpu_labels()
#     },
#     # apply_mann_kendall=True,
#     dayfirst=True
# )


# plot(
#     title="Fragmentation",
#     file=frag,
#     ylabel='Average Cpu Utilization (\\%)', 
#     dayfirst=True, 
#     datetime='datetime'
#     # includeColYlabel=True
# )


plot(
    title="Average CPU Utilization Across All Cores Over Time",
    file=cpu_mean,
    ylabel='Average Cpu Utilization (\\%)', 
    dayfirst=True, 
    # includeColYlabel=True
)

plot(
    title="Disk Usage Over Time", 
    file=disk,
    ylabel='Disk Usage (GB)', 
    dayfirst=True, division=(1024**2)
)

plot(
    title="Number of Zombie Processes Over Time", 
    file=zombie,
    ylabel='Number of Zombie Processes', 
    dayfirst=True
)

plot(
    title="Memory Usage Over Time", 
    file=mem,
    ylabel='Memory Usage (MB)', 
    dayfirst=True, 
    division=1024, 
    # includeColYlabel=True
)


plot(
    title="Process_xen_monitoring_oxenstored", 
    file=oxenstored,
    cols_to_divide=["vmrss","vsz","swap"],
    ylabel={
        **common_ylabels()
    },
    division=1024, dayfirst=True
)

plot(
    title="Process_xen_monitoring_xen_balloon", 
    file=xenballon,
    cols_to_divide=["vmrss","vsz","swap"],
    ylabel={
        **common_ylabels()
    },
    division=1024, dayfirst=True
)

plot(
    title="Process_xen_monitoring_xenbus", 
    file=xenbus,
    cols_to_divide=["vmrss","vsz","swap"],
    ylabel={
        **common_ylabels()
    },
    division=1024, dayfirst=True
)

plot(
    title="Process_xen_monitoring_xenconsoled", 
    file=xenconsoled,
    cols_to_divide=["vmrss","vsz","swap"],
    ylabel={
        **common_ylabels()
    },
    division=1024, dayfirst=True
)

plot(
    title="Nginx Server Response Time Over Time", 
    file=nginx,
    ylabel='Response Time (seconds)', 
    multiply=1, dayfirst=True
)