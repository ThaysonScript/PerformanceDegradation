from utils.ManipulationPandas import ManipulationPandas

class PlottarFragmentado:
    def __init__(self):
        pass
    
    
    def analisar(self, minimum_process_occurrences=1, arquivo=''):
        objeto = ManipulationPandas()
        
        df = objeto.carregarLogDataframe(nomeArquivo=arquivo)
        
        df = objeto.converterColunaDatetime(df, 'datetime')
        
        df = objeto.definirIndex(df, 'datetime')
        
        df = objeto.converterTempo(df, 'time_passed', returnNewColumn=True)
        
        # Resetando o índice para usar as colunas corretamente
        df = df.reset_index()
        
        # Resetting the index 'datetime' to use 'time_passed' as index
        # df = objeto.definirIndex(df, 'time_passed')
        
        
        df_filtered = df[df['process_occurrences'] >= minimum_process_occurrences]
        
        
        
        # Verificar se 'time_passed' existe após filtragem
        if 'time_passed' not in df_filtered.columns:
            raise KeyError("Coluna 'time_passed' não encontrada após filtragem.")
    
    

        df_pivot = objeto.pivotarValoresDataframe(dataframe=df_filtered, column='process', value='process_occurrences')
        
        # ax = objeto.plotarGrafico(dataframe=df_pivot, yLabel='Process occurrences (qtt)', xLabel='Time(H)', figureSize=(10, 6))
        # ax = objeto.plotarGrafico(
        #     dataframe=df_filtered,
        #     x_col='time_passed',
        #     y_col='process_occurrences',
        #     yLabel='Process occurrences (qtt)',
        #     xLabel='Time(H)',
        #     figureSize=(10, 6)
        # )
        ax = objeto.plotarGrafico(dataframe=df_pivot, yLabel='Process occurrences (qtt)', xLabel='Time(H)', figureSize=(10, 6))

        
        objeto.fixarValoresInteirosGrafico(ax=ax)
        
        # Save the figure
        # objeto.salvarFigura(ax=ax, nomeFigura=f'imagens_plottadas/fragmentation.png')
        objeto.salvarFigura(ax=ax, nomeFigura=f'imagens_plottadas/fragmentation.png')

