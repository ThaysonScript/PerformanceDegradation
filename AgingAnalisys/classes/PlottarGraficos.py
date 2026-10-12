import sys
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.linear_model import LinearRegression
import matplotlib.ticker as mticker
from utils.ManipulationPandas import ManipulationPandas
from pymannkendall import original_test
# import utils.plot_configs


class PlottarGraficos(ManipulationPandas):
    def __init__(self):
        super().__init__()

    @staticmethod
    def apply_mk_segment(self, segment):
        try:
            return original_test(segment)
        except Exception as e:
            return e
    
    
    def plot_mann_kendall(self, 
                          file, title, dayfirst, datetime, 
                          includeColYlabel, ylabel, x_lim, y_lim, highlight_intervals=None, 
                          cols_to_divide=[], cols_to_multiply=[],
                          division=1, multiply=1,
                          resample_method='mean', cut_dataset=None
    ):
        print(f"Lendo arquivo: {file}")
        df = pd.read_csv(file, sep=';', dayfirst=dayfirst)
        
        print(df)
        # sys.exit(1)

        
        # Converte vírgulas para pontos apenas nas colunas numéricas
        for col in df.columns:
            if col != datetime:
                df[col] = df[col].astype(str).str.replace(',', '.', regex=False)
                df[col] = pd.to_numeric(df[col], errors='coerce')


        print(df)
        # sys.exit(1)
                                        

        # Converte a coluna de datas para datetime, com segurança
        # df[datetime] = pd.to_datetime(df[datetime], errors='coerce')
        df[datetime] = pd.to_datetime(df[datetime], format="%d-%m-%Y-%H:%M:%S", errors="coerce")

        # df = df.dropna(subset=["date_time"])
        print("Coluna datetime convertida:\n", df[datetime].head())

        print(df)
        # sys.exit(1)


        # Remove linhas com datas inválidas, se houver
        # df = df.dropna(subset=[datetime])

        # Define o índice como datetime
        df = df.set_index(datetime)
        print("Index definido como DatetimeIndex.")




        print(df)
        # sys.exit(1)


        # Aplica o resample
        if resample_method == 'mean':
            df = df.resample('1min').mean()
            print("Resample aplicado com 'mean' (média) a cada 1 minuto.")
            
        elif resample_method == 'max':
            df = df.resample('1min').max()
            print("Resample aplicado com 'max' (máximo) a cada 1 minuto.")
            
        elif resample_method == 'sum':
            df = df.resample('1min').sum()
            print("Resample aplicado com 'sum' (soma) a cada 1 minuto.")
            
        else:
            df = df.resample('1min').mean() # Padrão
            print(f"Método '{resample_method}' desconhecido, usando 'mean'.")
            
        df = df.round(6)
        print("Resample aplicado com média a cada 1 minuto.")


        print(df.tail(100))
        # sys.exit(1)



        # Converte o índice para horas decimais
        df['seconds'] = (df.index - df.index[0]).total_seconds() / 3600
        df = df.set_index('seconds')
        print("Index convertido para horas decimais.")
        
        
        if cut_dataset is not None:
            df = df[df.index <= float(cut_dataset)]





        # sys.exit(1)
        print(df.index)
        print(df.index[0])
        # print((df.index - df.index[0]).total_seconds() / 3600)






        
        # Ajustar 'response_time' conforme necessário
        if file.endswith('nginx_response.csv'):
            df['response_time'] = df['response_time'] * multiply if multiply != 1 else df['response_time'] / division
        else:
            df = ManipulationPandas().multiplicarColunasDataframe(dataframe=df, 
                                                                  colunasParaMultiplicar=cols_to_multiply, 
                                                                  multiplicarPor=multiply)
            df = ManipulationPandas().dividirColunasDataframe(dataframe=df, 
                                                             colunasParaDividir=cols_to_divide, 
                                                             dividirPor=division)
        
        for col in df.columns:
            print(f"\nProcessando coluna: {col}")
            col_mix = col + " " + ylabel if isinstance(ylabel, str) and includeColYlabel else ylabel

            df[col] = df[col].fillna(0)
            print(f"Valores NaN substituídos por 0 em {col}")

            if col == "swap":
                df[col] = (df[col] - 8192) * -1
                print("Transformação aplicada para coluna 'swap'.")

            # Regressão linear
            x = df.index.to_numpy().reshape((-1, 1))
            y = df[col].to_numpy().reshape((-1, 1))
            model = LinearRegression()
            model.fit(x, y)
            Y_pred = model.predict(x)
            
            print(f"Coeficiente da regressão para {col}: {model.coef_[0][0]:.4f}")
            fig, ax = plt.subplots(figsize=(15, 10), dpi=300)
            
            col_name = col.replace('%', '')
                        
            if file.endswith('machine_monitoring-zombies.csv'):
                # 1. Filtra os dados para mostrar apenas quando há zumbis (> 0)
                df_filtered = df[df[col] > 0]
                
                # 2. Plota como um gráfico de "stem" (haste)
                #    'linefmt' é a linha vertical, 'markerfmt' é o ponto no topo, 'basefmt' é a linha do eixo x (desligada)
                ax.stem(df_filtered.index, df_filtered[col], 
                        linefmt='grey',       # Linha vertical cinza
                        markerfmt='ko',      # Marcador 'o' (círculo) preto 'k'
                        basefmt=" ",         # Remove a linha de base em y=0
                        label=col_name,
                        )

                # 3. Força o eixo Y a usar inteiros (0, 1, 2...)
                ax.yaxis.set_major_locator(mticker.MaxNLocator(integer=True))
                # 4. Garante que o gráfico comece no zero
                ax.set_ylim(bottom=0)

            else:
                # Gráfico de linha padrão para todos os outros dados
                ax.plot(df.index, df[col], color='black', label=col_name)
                
                # regressao
                ax.plot(x, Y_pred, color='red', linewidth=5, alpha=0.5, linestyle='-')
            

            ax.set_xlabel("Time (h)")
            ax.set_ylabel(col_mix if isinstance(ylabel, str) else ylabel.get(col, col) if isinstance(ylabel, dict) else col)
            # ax.set_title(title if isinstance(title, str) else title.get(col, col) if isinstance(title, dict) else col)

            # ax.grid(True)
            ax.tick_params(direction="in", which="both", top=True, right=True)
            ax.minorticks_on()

            # Mann-Kendall
            test_result = original_test(df[col])
            print(f"Mann-Kendall para {col}: trend={test_result.trend}, p={test_result.p:.4f}, z={test_result.z:.4f}")
            trend_text = (
                f"trend: {test_result.trend}\n"
                f"p-value: {test_result.p:.4f}\n"
                f"z: {test_result.z:.4f}"
            )

            # ax.text(
            #     0.95, 0.05, trend_text,
            #     transform=ax.transAxes,
            #     fontsize=18,
            #     verticalalignment='bottom',
            #     horizontalalignment='right',
            #     bbox=dict(boxstyle="round", alpha=0.8, color='white')
            # )
            ax.plot([], [], linestyle='none', label=trend_text)

            for spine in ax.spines.values():
                spine.set_linewidth(1.5)
            
            if col == 'swap-free':
                ax.set_ylim([970, 980])
                ax.ticklabel_format(style='plain', axis='y')
                ax.yaxis.set_major_formatter(mticker.StrMethodFormatter('{x:.2f}'))
                ax.get_yaxis().get_offset_text().set_visible(False)
                
            if file.endswith('kvm_libvirtd_service_monitoring.csv') and col == 'vsz':
                ax.ticklabel_format(style='plain', axis='y')
                ax.yaxis.set_major_formatter(mticker.StrMethodFormatter('{x:.2f}'))
                ax.get_yaxis().get_offset_text().set_visible(False)
                
                
            self._adicionar_linhas_verticais(ax, df, col)
            self._salvar_e_fechar_figura(ax, title, col)
            print(f"Gráfico salvo")

            plt.close()
        
        print("Processamento completo.")
        return 1

    def plottar(self,
                nomeArquivo='', ylabel='', 
                datetimeName="date_time", title=None, 
                separador=';', separadorDecimal=",", 
                dayfirst=False, multiply=1, division=1, 
                decimals_quantity=2, includeColYlabel=False, 
                cols_to_divide=[], cols_to_multiply=[], cut_dataset=None,
                apply_mann_kendall=False,
                resample_method='mean'
                ):
        
        
        if apply_mann_kendall is True:
            self.plot_mann_kendall(
                nomeArquivo, title, dayfirst, 
                datetimeName, includeColYlabel, ylabel, 
                None, None, None, 
                cols_to_divide, cols_to_multiply, division, multiply,
                resample_method, cut_dataset
            )
            return
        
        print(f'\n-------------------------------------- Executando plotagens [ {nomeArquivo} ] --------------------------------------')

        # Carregar e preparar os dados
        df = ManipulationPandas().carregarLogDataframe(nomeArquivo, separador, separadorDecimal, 
                                                       dayfirst, datetimeName, parse_date=True)
                
        if cut_dataset != None:
            print(df.columns)
            
            try:
                df = df[df['date_time'] <= cut_dataset]
                
            except:
                df = df[df['seconds'] <= cut_dataset]
                
        
        ManipulationPandas().verificarErrosEGravar(dataframe=df, nomeArquivo=nomeArquivo)
        df = ManipulationPandas().droparColunasNulasVazias(dataframe=df)
        df = ManipulationPandas().converterTempo(dataframe=df, atualName='seconds')
        
        df = ManipulationPandas().definirIndex(dataframe=df, index='seconds', indexWithReplace=True)
        
        if cut_dataset is not None:
            df = df[df.index <= float(cut_dataset)]
        
        # Ajustar 'response_time' conforme necessário
        if nomeArquivo.endswith('nginx_response.csv'):
            df['response_time'] = df['response_time'] * multiply if multiply != 1 else df['response_time'] / division
        else:
            df = ManipulationPandas().multiplicarColunasDataframe(dataframe=df, 
                                                                  colunasParaMultiplicar=cols_to_multiply, 
                                                                  multiplicarPor=multiply)
            df = ManipulationPandas().dividirColunasDataframe(dataframe=df, 
                                                             colunasParaDividir=cols_to_divide, 
                                                             dividirPor=division)
        

        # Gerar gráficos
        for col in df.columns:
            col_mix = f"{col} {ylabel}" if isinstance(ylabel, str) and includeColYlabel else ylabel
            df[col] = df[col].fillna(0)
            
            x = df.index.to_numpy().reshape((-1, 1))
            y = df[col].to_numpy().reshape((-1, 1))

            model = LinearRegression()
            model.fit(x, y)
            Y_pred = model.predict(x)
            
            fig, ax = plt.subplots(figsize=(15, 10), dpi=300)
            
            col_name = col.replace('%', '')
            ax.plot(df.index, df[col], color='black', label=col_name)
            ax.plot(x, Y_pred, color='red', linewidth=3, alpha=0.5, linestyle='-')

            ax.set_xlabel("Time (h)")
            ax.set_ylabel(col_mix if isinstance(ylabel, str) else ylabel.get(col, col) if isinstance(ylabel, dict) else col)
            # ax.set_title(title if isinstance(title, str) else title.get(col, col) if isinstance(title, dict) else col)

            # ax.grid(True)
            ax.tick_params(direction="in", which="both", top=True, right=True)
            ax.minorticks_on()

            if col == 'swap-free':
                ax.set_ylim([970, 980])
                ax.ticklabel_format(style='plain', axis='y')
                ax.yaxis.set_major_formatter(mticker.StrMethodFormatter('{x:.2f}'))
                ax.get_yaxis().get_offset_text().set_visible(False)
                
            if nomeArquivo.endswith('kvm_libvirtd_service_monitoring.csv') and col == 'vsz':
                ax.ticklabel_format(style='plain', axis='y')
                ax.yaxis.set_major_formatter(mticker.StrMethodFormatter('{x:.2f}'))
                ax.get_yaxis().get_offset_text().set_visible(False)
                
                
            self._adicionar_linhas_verticais(ax, df, col)
            self._salvar_e_fechar_figura(ax, title, col)
                        

    def _adicionar_linhas_verticais(self, ax, df, col):
        """Adicionar linhas verticais indicando diferentes fases."""
        interval_1_duration = 12
        interval_2_duration = 72
        max_time = df.index.max()
        current_time = 0

        while current_time <= max_time:
            # Desenhar linha azul (espera)
            if current_time <= max_time:
                ax.axvline(x=current_time, color='royalblue', linestyle='-', linewidth=10, alpha=0.4)
                # ax.annotate(
                #     # "Waiting phase",
                #     xy=(current_time, df[col].max()),
                #     xytext=(3, -15),
                #     textcoords='offset points',
                #     rotation=90,
                #     va='top',
                #     fontsize=8,
                #     color='royalblue',
                #     alpha=1.0
                # )

            # Desenhar linha verde (stress)
            stress_time = current_time + interval_1_duration
            if stress_time <= max_time:
                ax.axvline(x=stress_time, color='royalblue', linestyle='-', linewidth=10, alpha=0.4)
                # ax.annotate(
                #     # "Stress phase",
                #     xy=(stress_time, df[col].max()),
                #     xytext=(3, -15),
                #     textcoords='offset points',
                #     rotation=90,
                #     va='top',
                #     fontsize=8,
                #     color='seagreen',
                #     alpha=1.0
                # )

            current_time += interval_1_duration + interval_2_duration


    def _salvar_e_fechar_figura(self, ax, title, col):
        """Salvar e fechar a figura após a plotagem."""

        ax.legend(loc='best', fontsize='small', ncol=2, frameon=True, framealpha=0.9, edgecolor='black')
        
        # Substituir espaços por underlines no título
        safe_title = title.replace(' ', '_')
        col_ref = col.replace('%', '')

        self.salvarFigura(ax=ax, nomeFigura=f'./imagens_plottadas/{safe_title}_{col_ref}.svg')
        plt.close()