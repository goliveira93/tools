from typing import Tuple
from datetime import datetime
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from et_lib.ET_Data_Reader import QuantumHistoricalData
from settings import colors

def download_dataframe()->pd.DataFrame:
    tickers=["IFMM BTG Pactual","IMA-B","IBX"]
    start_date=datetime(2010,12,31)
    end_date=datetime.today()
    d=QuantumHistoricalData(start_date,end_date,tickers)
    df=d.getData().dropna()
    df=df.droplevel(1,axis=1)
    return df

def calcula_loadings(df:pd.DataFrame)->dict:
    "Retorna dataframe com loadings e list com a variância explicada por cada componente para cálcul odo scree plot"
    returns = df.pct_change().dropna()
    returns_standardized = StandardScaler().fit_transform(returns)

    pca = PCA(n_components=3)
    pca.fit(returns_standardized)

    # Ver os componentes principais
    components = pca.components_
    #print("Componentes principais:\n", components)

    # Variância explicada por cada componente
    explained_variance = pca.explained_variance_ratio_
    #print("Variância explicada por cada componente:", explained_variance)

    loadings = pca.components_.T * np.sqrt(pca.explained_variance_)

    # Criando um DataFrame para melhor visualização
    loadings_df = pd.DataFrame(loadings, columns=['PC0', 'PC1', 'PC2'], index=returns.columns)

    # Calculando as projeções dos dados originais nos componentes principais
    pca_scores = pca.transform(returns_standardized)

    comparison_df={}

    for base in ["IFMM BTG Pactual","IMA-B","IBX"]:
        pca_i_scores=[pca_scores[:, i] for i in range(0,3)]
        for i in range(0,3):
            if loadings_df.loc[base]["PC"+str(i)]<0:
                pca_i_scores[i]=pca_i_scores[i]*-1
        pca_i_scores_normalized = [(pca_i_scores[i] - pca_i_scores[i].mean()) / pca_i_scores[i].std() for i in range(0,3)]
        base_returns = returns[base]
        pca_i_scores_adjusted = [pca_i_scores_normalized[i] * base_returns.std() + base_returns.mean() for i in range(0,3)]
        comparison_df[base] = pd.DataFrame({
             base: np.cumprod(1+base_returns),
            'PC0': np.cumprod(pca_i_scores_adjusted[0]+1),
            'PC1': np.cumprod(pca_i_scores_adjusted[1]+1),
            'PC2': np.cumprod(pca_i_scores_adjusted[2]+1),
        }, index=base_returns.index)

    resp={"loadings":loadings_df,
          "explained_variance":list(explained_variance),
          "comparison_df":comparison_df}
    return resp

def cria_graficos(resp:dict)->go.Figure:
    explained_variance=resp["explained_variance"]
    fig=make_subplots(rows=3,cols=2)
    fig.add_trace(go.Scatter(x=["PC"+str(i) for i in range(0,len(explained_variance))],y=explained_variance,mode="lines",name="scree"),row=1,col=1)

    for e,base in enumerate(resp["comparison_df"].keys()):
        df=resp["comparison_df"][base]
        show_legend=True if e==0 else True
        col=1 if e % 2 == 0 else 2
        row= int(e/2)+2
        fig.add_trace(go.Scatter(x=df.index,y=df[base].values,mode="lines",name=base, line={"color":colors[0]}),row=row,col=col)
        fig.add_trace(go.Scatter(x=df.index,y=df["PC0"].values,mode="lines",name="PC0",showlegend=show_legend,line={"color":colors[6]}),row=row,col=col)
        fig.add_trace(go.Scatter(x=df.index,y=df["PC1"].values,mode="lines",name="PC1",showlegend=show_legend,line={"color":colors[2]}),row=row,col=col)
        #fig.add_trace(go.Scatter(x=df.index,y=df["PC2"].values,mode="lines",name="PC2",showlegend=show_legend,line={"color":colors[3]}),row=e+2,col=1)

    return fig


if __name__=="__main__":
    df=download_dataframe()
    returns = df.pct_change().dropna()
    print("Correlação")
    print(returns.corr())
    resp=calcula_loadings(df)
    print("Loadings")
    print(resp["loadings"])
    fig=cria_graficos(resp)
    fig.show()


