import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score

class MachineLearningAnalysis:
    def __init__(self, dataframe, target_col, test_size=0.2, random_state=42, model_type='linear_regression'):
        """
        Inicializa a classe com os dados e as configurações para a análise de ML.

        Args:
            dataframe (pd.DataFrame): Dados de entrada para a análise.
            target_col (str): Nome da coluna que será prevista.
            test_size (float): Proporção dos dados para o conjunto de teste. Padrão é 0.2 (20%).
            random_state (int): Semente para aleatoriedade nos splits de dados.
        """
        self.df = dataframe
        self.target_col = target_col
        self.test_size = test_size
        self.random_state = random_state
        
        if model_type is 'linear_regression':
            self.model = LinearRegression()
        
        self.X = self.df.drop(columns=[self.target_col])
        self.y = self.df[self.target_col]

    def treinar_modelo(self):
        """
        Divide os dados em treino e teste e treina o modelo.
        """
        X_train, X_test, y_train, y_test = train_test_split(self.X, self.y, test_size=self.test_size, random_state=self.random_state)
        self.model.fit(X_train, y_train)
        self.y_pred = self.model.predict(X_test)
        self.X_test = X_test
        self.y_test = y_test

    def avaliar_modelo(self):
        """
        Avalia o modelo e retorna métricas de desempenho.
        """
        mse = mean_squared_error(self.y_test, self.y_pred)
        r2 = r2_score(self.y_test, self.y_pred)
        
        return {
            'Mean Squared Error': mse,
            'R-squared': r2
        }

    def resultados(self):
        """
        Retorna os resultados da análise: valores reais vs previstos.
        """
        return pd.DataFrame({
            'Real': self.y_test,
            'Previsto': self.y_pred
        })

    def resumo(self):
        """
        Exibe o resumo do modelo com as métricas e resultados.
        """
        self.treinar_modelo()
        metrics = self.avaliar_modelo()
        results = self.resultados()

        print("Resumo do Modelo:")
        print(f"Mean Squared Error: {metrics['Mean Squared Error']}")
        print(f"R-squared: {metrics['R-squared']}")
        print("\nPrimeiras 10 Previsões vs Reais:")
        print(results.head(10))

