import os
import sys
import matplotlib.pyplot as plt
import pandas as pd

class ManipulationPandas:
    def __init__(self):
        pass
    
    
    def carregarLogDataframe(self, nomeArquivo='', separador=';', separadorDecimal=',', dayfirst=False, datetimeName='date_time', parse_date=False):
        if parse_date == True:
            try:
                return pd.read_csv(nomeArquivo, delimiter=separador, decimal=separadorDecimal, dayfirst=dayfirst, parse_dates=[datetimeName]).rename(columns={datetimeName: 'seconds'})
            
            except ValueError:
                try:
                    return pd.read_csv(nomeArquivo, delimiter=separador, decimal=separadorDecimal, dayfirst=dayfirst, parse_dates=['time']).rename(columns={'time': 'seconds'})        

                except Exception as e:
                    return f'Erro ao ler o arquivo CSV: {e}'
                
                finally:
                    sys.exit(1)
        
        return pd.read_csv(nomeArquivo, delimiter=';')
    
    
    def droparColunasNulasVazias(self, dataframe: pd):
        return dataframe.fillna(0)
        # return dataframe.dropna()
    
    
    def droparSubColunasNulasVazias(self, dataframe: pd, subcoluna=''):
        return dataframe.dropna(subset=[subcoluna]).reset_index(drop=True).copy()
    
    
    def converterColunaDatetime(self, dataframe: pd, column):
        dataframe[f'{column}'] = pd.to_datetime(dataframe[f'{column}'], errors='coerce')
        return dataframe
    
    
    def definirIndex(self, dataframe: pd, index: str, indexWithReplace=False):
        if indexWithReplace == True:
            return dataframe.set_index(index).replace(',', '.', regex=True).apply(lambda x: pd.to_numeric(x, errors='ignore'))
        return dataframe.set_index(index)
    
    
    def converterTempo(self, dataframe, newName='', atualName=None, returnNewColumn=False):
        if returnNewColumn:
            dataframe[f'{newName}'] = (dataframe.index - dataframe.index[0]).total_seconds() / 3600
            return dataframe
        
        elif not returnNewColumn and atualName is not None:
            dataframe = self.converterColunaDatetime(dataframe=dataframe, column=atualName)
            
            # Verifica se há valores inválidos
            if dataframe[f'{atualName}'].isna().any():   
                try:             
                    dataframe_filtrado = dataframe[dataframe[atualName] != False]
                    dataframe_filtrado = dataframe_filtrado.dropna()
                    dataframe = dataframe_filtrado
                
                except:              
                    raise ValueError(f"Coluna '{atualName}' contém valores inválidos após conversão para datetime.")
            
            dataframe[f'{atualName}'] = (dataframe[f'{atualName}'] - dataframe[f'{atualName}'][0]).dt.total_seconds() / 3600
            return dataframe
            
        else:
            print('\n\nErro em converter tempo no modulo de manipular dataframe no pandas\n\n')
            sys.exit(1)
    
    
    def filtrarDados(self, dataframe, column, condicao, ocorrencia):
        return dataframe[f'{dataframe[column]} {condicao} {ocorrencia}']
    
    
    def salvarFigura(self, ax, nomeFigura):
        fig = ax.get_figure()
        fig.savefig(f'{nomeFigura}', bbox_inches='tight', dpi=300, format="svg")
        
        
    def fixarValoresInteirosGrafico(self, ax):
        # transformar decimais em inteiros
        ax.set_yticks(ax.get_yticks())
        ax.set_yticklabels(ax.get_yticks().astype(int))
        
        
    # def plotarGrafico(self, dataframe: pd, yLabel, xLabel, figureSize):
    #     return dataframe.plot.scatter(ylabel=yLabel, xlabel=xLabel, figsize=figureSize)
    # def plotarGrafico(self, dataframe: pd.DataFrame, x_col: str, y_col: str, yLabel: str, xLabel: str, figureSize=(10, 6)):
    #     fig, ax = plt.subplots(figsize=figureSize)
    #     ax.scatter(dataframe[x_col], dataframe[y_col], c='DarkBlue', label='Data points')
    #     ax.set_xlabel(xLabel)
    #     ax.set_ylabel(yLabel)
    #     ax.legend()
    #     return ax
    
    def plotarGrafico(self, dataframe: pd, yLabel, xLabel, figureSize):
        return dataframe.plot(ylabel=yLabel, xlabel=xLabel, figsize=figureSize)
    
    
    def pivotarValoresDataframe(self, dataframe: pd, column, value):
        return dataframe.pivot(columns=column, values=value)
    
    
    def multiplicarColunasDataframe(self, dataframe: pd, colunasParaMultiplicar, multiplicarPor=1):
        # perform data multiplication
        cols_to_multiply = cols_to_multiply if len(colunasParaMultiplicar) != 0 else dataframe.columns
        dataframe[cols_to_multiply] = dataframe[cols_to_multiply].mul(multiplicarPor)
        return dataframe
        
        
    def dividirColunasDataframe(self, dataframe: pd, colunasParaDividir, dividirPor):
        if isinstance(dataframe, pd.Series):
            # Se for uma Series, converte para DataFrame (se necessário)
            dataframe = dataframe.to_frame()
        
        # Se nenhuma coluna for especificada, usa todas as colunas do DataFrame
        if colunasParaDividir is None or len(colunasParaDividir) == 0:
            cols_to_divide = dataframe.columns
        else:
            cols_to_divide = colunasParaDividir
        
        # cols_to_divide = cols_to_divide if len(colunasParaDividir) != 0 else dataframe.columns
        dataframe[cols_to_divide] = dataframe[cols_to_divide].div(dividirPor)
            
        return dataframe        
        
        
    def verificarErrosEGravar(self, dataframe, nomeArquivo):
        erros = []

        # Verificando valores nulos em todo o DataFrame
        nulos = dataframe[dataframe.isna().any(axis=1)]
        if not nulos.empty:
            erros.append(f"\nLinhas com valores NULOS:\n{nulos}\n")
        
        # Verificando valores não numéricos (após tentativa de conversão)
        for coluna in dataframe.select_dtypes(include=['object']).columns:
            try:
                # Tentando converter para numérico e gerar NaN onde houver erro
                dataframe[coluna] = pd.to_numeric(dataframe[coluna], errors='coerce')
                nulos_na_conversao = dataframe[dataframe[coluna].isna()]
                if not nulos_na_conversao.empty:
                    erros.append(f"\nValores não numéricos encontrados na coluna '{coluna}':\n{nulos_na_conversao}\n")
            except Exception as e:
                erros.append(f"Erro ao tentar converter a coluna {coluna} para numérico: {str(e)}")

        # Verificando formato de data inválido
        for coluna in dataframe.select_dtypes(include=['object']).columns:
            try:
                dataframe[coluna] = pd.to_datetime(dataframe[coluna], errors='coerce')
                nulos_na_data = dataframe[dataframe[coluna].isna()]
                if not nulos_na_data.empty:
                    erros.append(f"\nErros de formato de data na coluna '{coluna}':\n{nulos_na_data}\n")
            except Exception as e:
                erros.append(f"Erro ao tentar converter a coluna {coluna} para data: {str(e)}")

        # Verificando valores vazios em colunas específicas
        for coluna in dataframe.columns:
            if dataframe[coluna].isnull().any():
                linhas_com_nulos = dataframe[dataframe[coluna].isnull()]
                if not linhas_com_nulos.empty:
                    erros.append(f"\nLinhas com valores NULOS na coluna '{coluna}':\n{linhas_com_nulos}\n")

        # Salvando os erros em um arquivo txt com o nome do arquivo original
        nome_erro = f"logs_erros/erros_{os.path.basename(nomeArquivo)}.txt"
        with open(nome_erro, 'w') as file:
            if erros:
                file.writelines(erros)
            else:
                file.write("Nenhum erro encontrado.\n")
        
        print(f"Erros salvos em: {nome_erro}")