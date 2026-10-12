import matplotlib.pyplot as plt
import utils.plot_configs

class GenerateGraphics:
    def __init__(self, dataframe):
        self.df = dataframe

    def gerar_grafico(self, tipo='plot', x_col=None, y_col=None, **kwargs):
        """
        Gera diferentes tipos de gráficos baseados no tipo especificado.

        Args:
            tipo (str): Tipo do gráfico ('plot', 'scatter', etc.).
            x_col (str): Nome da coluna para o eixo X.
            y_col (str): Nome da coluna para o eixo Y.
            **kwargs: Argumentos adicionais específicos do tipo de gráfico.
        """
        if x_col not in self.df.columns or y_col not in self.df.columns:
            raise ValueError(f"As colunas {x_col} e {y_col} devem estar no DataFrame.")
        
        if tipo == 'plot':
            self._plot_simples(x_col, y_col, **kwargs)
        elif tipo == 'scatter':
            self._scatter_com_regressao(x_col, y_col, **kwargs)
        else:
            raise ValueError(f"Tipo de gráfico '{tipo}' não suportado.")
        
    def adicionar_intervalos(dataframe, interval1=12, interval2=72, current_time=0):
        # máximo de tempo (x) dos dados
        max_time = dataframe.index.max()

        # linha vertical no início de cada intervalo
        while current_time <= max_time:
            # linha azul no início do ciclo de 12 horas
            dataframe.axvline(x=current_time, color='blue', linestyle='--', label='start waiting phase' if current_time == 0 else None)
            
            # linha verde no início do ciclo de 3 dias
            dataframe.axvline(x=current_time + interval1, color='green', linestyle='--', label='start stress phase' if current_time == 0 else None)

            # atualizando tempo atual para o próximo ciclo de 3 dias
            current_time += interval1 + interval2  # Move para o próximo início de 12h + 3 dias

        # Remover duplicatas de legenda
        handles, labels = dataframe.get_legend_handles_labels()
        by_label = dict(zip(labels, handles))
        dataframe.legend(by_label.values(), by_label.keys())

        

    def _plot_simples(self, x_col, y_col, xlabel='X', ylabel='Y', title='Plot Simples', figsize=(10, 6)):
        """
        Gera um gráfico de linha simples.
        """
        plt.figure(figsize=figsize)
        plt.plot(self.df[x_col], self.df[y_col], label=y_col, color='blue')
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.title(title)
        plt.legend()
        plt.grid()
        plt.show()

    def _scatter_simples(self, x_col, y_col, xlabel='X', ylabel='Y', title='Scatter Simples', figsize=(10, 6)):
        """
        Gera um gráfico de dispersão simples.
        """
        plt.figure(figsize=figsize)
        plt.scatter(self.df[x_col], self.df[y_col], color='blue', label='Pontos')
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.title(title)
        plt.legend()
        plt.grid()
        plt.show()
