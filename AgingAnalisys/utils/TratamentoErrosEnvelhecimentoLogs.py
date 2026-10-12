import re
from matplotlib import pyplot as plt
import pandas as pd
import utils.plot_configs


file_vbox = 'VBox.log'

class TratamentoErrosEnvelhecimentoLogs:
    def __init__(self, pasta_logs, barras: bool, ponto: bool):
        self.pasta_logs = pasta_logs
        self.barras = barras
        self.ponto = ponto

        if barras:
            self.grafico_barras()

        if ponto:
            self.grafico_ponto()

    def grafico_ponto(self):
        # Lista para armazenar as linhas extraídas
        data = []

        # Abrir o arquivo e ler linha por linha
        with open(f'{self.pasta_logs}/{file_vbox}', "r") as file:
            for line in file:
                # Extração de timestamp e tipo de erro
                match = re.match(r"(\d+:\d+:\d+\.\d+)\s+(VMSetError|ERROR \[COM\]):\s+(.*)", line)

                if match:
                    timestamp = match.group(1)
                    error_type = match.group(2)
                    message = match.group(3)

                    # Adiciona os dados extraídos na lista
                    data.append([timestamp, error_type, message])

        # Criar o DataFrame
        df = pd.DataFrame(data, columns=["Timestamp", "ErrorType", "Message"])

        # Converter o timestamp para horas acumuladas
        def convert_to_hours(timestamp):
            match = re.match(r"(\d+):(\d+):(\d+\.\d+)", timestamp)
            if match:
                hours = int(match.group(1))
                minutes = int(match.group(2))
                seconds = float(match.group(3))
                return hours + minutes / 60 + seconds / 3600
            return 0

        df["Hours"] = df["Timestamp"].apply(convert_to_hours)

        # Agrupar os erros por tipo e tempo
        error_counts = df.groupby(["Hours", "ErrorType"]).size().reset_index(name="ErrorCount")

        # Filtrar os erros, considerando um limite mínimo de ocorrências
        minimum = 1
        filtered_df = error_counts[error_counts["ErrorCount"] >= minimum]

        # Verificar se a coluna 'ErrorCount' é numérica
        filtered_df['ErrorCount'] = pd.to_numeric(filtered_df['ErrorCount'], errors='coerce')

        # Calcular a soma acumulada dos erros para cada tipo de erro
        filtered_df['CumulativeErrorCount'] = filtered_df.groupby('ErrorType')['ErrorCount'].cumsum()

        # Criar o gráfico com as ocorrências acumuladas como pontos
        df_pivot = filtered_df.pivot(columns='ErrorType', values='CumulativeErrorCount')

        # Verificar se df_pivot contém dados numéricos
        if df_pivot.empty or df_pivot.isnull().all().all():
            print("Não há dados numéricos para plotar.")
            
        else:
            fig, ax = plt.subplots(figsize=(15, 10), dpi=300)

            # Plot manualmente no eixo criado
            df_pivot.plot(ax=ax, marker='o')
            
            ax.legend(loc='best', fontsize='small', ncol=2, frameon=True, framealpha=0.9, edgecolor='black')
            # plt.title("Cumulative Number of Errors by Type Over Time")
            ax.set_xlabel('Time (Hours)')
            ax.set_ylabel('Cumulative Number of Error Occurrences', labelpad=15)
                
            for spine in ax.spines.values():
                spine.set_linewidth(1.5)
                
            plt.xticks(rotation=45)

            # Salvar o gráfico como um arquivo PNG
            plt.savefig("imagens_plottadas/erros_relacionados_envelhecimento_ponto.svg", bbox_inches='tight', dpi=300, format="svg")


    def grafico_barras(self):
        # Lista para armazenar as linhas extraídas
        data = []

        # Abrir o arquivo e ler linha por linha
        with open(f'{self.pasta_logs}/{file_vbox}', "r") as file:
            for line in file:
                # Extração de timestamp e tipo de erro
                match = re.match(r"(\d+:\d+:\d+\.\d+)\s+(VMSetError|ERROR \[COM\]):\s+(.*)", line)

                if match:
                    timestamp = match.group(1)
                    error_type = match.group(2)
                    message = match.group(3)

                    # Adiciona os dados extraídos na lista
                    data.append([timestamp, error_type, message])

        # Criar o DataFrame
        df = pd.DataFrame(data, columns=["Timestamp", "ErrorType", "Message"])

        # Contar as ocorrências de cada tipo de erro
        error_counts = df['ErrorType'].value_counts()

        fig, ax = plt.subplots(figsize=(15, 10), dpi=300)
        
        error_counts.plot(kind='bar', color='skyblue')
        
        ax.legend(loc='best', fontsize='small', ncol=2, frameon=True, framealpha=0.9, edgecolor='black')
        ax.set_xlabel('Error Type')
        ax.set_ylabel('Number of Error Occurrences', labelpad=15)
                
        
        for spine in ax.spines.values():
            spine.set_linewidth(1.5)
            
        plt.xticks(rotation=0)
        
        plt.tight_layout()

        # # Salvar o gráfico como um arquivo PNG
        plt.savefig("imagens_plottadas/erros_relacionados_envelhecimento_barras.svg", bbox_inches='tight', dpi=300, format="svg")