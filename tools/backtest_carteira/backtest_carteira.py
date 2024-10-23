"""
Dada uma carteira com tickers da quantum e pesos, calcula o backtest da carteira
Quando um ativo não existe para o backtest, seu peso é realocado entre os demais ativos
"""

#from et_lib.ET_Data_Reader import QuantumHistoricalData
from et_lib.ET_Data_Reader import BasketHistoricalData

from datetime import datetime
from datetime import timedelta
from dateutil.relativedelta import relativedelta, FR
import numpy as np
import plotly.express as px
from plotly.graph_objs import Figure
import os
import pandas as pd
from db_functions import get_carteira
import os



def format_fig(fig:Figure)->Figure:
    fig.update_layout(
        plot_bgcolor='white',  # white plot background
        paper_bgcolor='white',  # white paper background
        font=dict(family="Segoe UI", size=12, color="#7f7f7f"),  # setting font
        xaxis_showgrid=False,  # remove gridlines
        yaxis_showgrid=False,
        xaxis_linecolor='white',  # remove x-axis line
        yaxis_linecolor='white',  # remove y-axis line
        xaxis_title="",
        yaxis_title="",
        legend_title="",  # remove legend title
    )
    return fig

def calculate_stats(benchmark:pd.Series, basket:pd.Series)->None:
    print("Vol benchmark: " ,round(benchmark.std()*(252**0.5)*100,1))
    print("Vol basket: "    ,round(basket.std()*(252**0.5)*100,1))
    excess_returns=basket-benchmark
    info_ratio=excess_returns.std()*(252**0.5)
    print("Tracking error: ",round(info_ratio*100,1))
    print("Information error: ",round(excess_returns.mean()*252*100,1))
    days=(basket.index[-1]-basket.index[0]).days
    ret_bm=(1+benchmark).cumprod().iloc[-1]**(365/days)-1
    ret_basket=(1+basket).cumprod().iloc[-1]**(365/days)-1
    print("Retorno anualizado benchmark: ",ret_bm)
    print("Retorno anualizado basket: ",ret_basket)



if __name__=="__main__":
    #basket_name="Mira"
    basket_name="Vega"
    #filename="Mira"
    filename="Vega"
    #benchmark="IFMM BTG PACTUAL"
    #benchmark="CDI"
    benchmark="IBX"
    endDate   = datetime.now()
    #startDate = datetime(endDate.year-10,endDate.month, endDate.day)
    startDate = datetime(2021,12, 31)
    basket=get_carteira(basket_name)
    basket.append({
            "Name"          : benchmark,
            "Ticker"        : benchmark,
            "Source"        : "Quantum",
            "Weight"        : 0
        })
    carteira={b["Ticker"]:b["Weight"] for b in basket}
    CNPJ_dict={i["Ticker"]:i["Name"] for i in basket}
    CNPJ_dict[basket_name]=basket_name
    print("Baixando série de precos da Quantum")
    q = BasketHistoricalData(filename,startDate, endDate, basket)   
    df=q.getData(dropna=False)
    df=df.droplevel(axis=1,level=1)
    df=df.fillna(method="ffill")
    print(df)

    colors=["#2C4257",  
            "#48728A",
            "#708F92",
            "#A3ABA4",
            "#605869",   #cor principal  para texto de corpo
            "#948794",
            "#E7A75F",   #Apenas para detalhes em elementos gráficos
            "#A25B1E"    #Apenas em gráficos
            ]

    fields=["PX_LAST"]

    print("Peso total: ",sum(carteira.values()))

    df.index=pd.Index([i.to_pydatetime().date() for i in df.index] )
    rets=df/df.shift(1)-1

    print("Calculando retornos")
    weights=rets.copy()
    for l in rets.index:
        total_w=0
        cng=0
        for c in rets.columns:
            if np.isnan(rets.loc[l,c]) == False:        #type: ignore
                cng+=rets.loc[l,c]*carteira[c]
                total_w+=carteira[c]
                weights.loc[l,c]=carteira[c]
            else:
                weights.loc[l,c]=0

        #divide retorno dos ativos existentes pelo seu peso, o que significa que os ativos inexistentes tiveram retorno igual ao resto da carteira
        rets.loc[l,basket_name]=cng/total_w if total_w !=0 else np.nan
        #matriz de pesos reponderada para somar 1
        weights.loc[l]=weights.loc[l]/total_w
        #em basket, vamos guardar qual era o peso total dos ativos antes de ajustarmos
        weights.loc[l,basket_name]=total_w


    comp=(rets[[benchmark,basket_name]].dropna()+1).cumprod(axis=0)
    print("Convertendo nomes")
    rets.columns=[CNPJ_dict[i] if CNPJ_dict[i]!="" else i for i in rets.columns]
    weights.columns=[i for i in rets.columns]
    fig = px.line(comp, color='variable', color_discrete_sequence=colors)
    fig=format_fig(fig)
    #fig.update_layout(width=1000)
    fig.write_image(os.path.join("backtest_carteira",filename+".png"))

    weights_plot=weights[[i for i in weights.columns if i!=basket_name and i!=benchmark]]
    fig2=px.area(weights_plot, color_discrete_sequence=colors)
    fig2=format_fig(fig2)
    fig2.write_image(os.path.join("backtest_carteira",filename+"_weights.png"))

    fig3=px.pie(weights_plot.iloc[-1], names=weights_plot.iloc[-1].index, values=weights_plot.iloc[-1].values, color_discrete_sequence=colors)
    fig3=format_fig(fig3)
    fig3.write_image(os.path.join("backtest_carteira",filename+"_pie.png"))

    calculate_stats(rets[benchmark],rets[basket_name])

    with pd.ExcelWriter(os.path.join("backtest_carteira",filename+".xlsx")) as writer:
        rets.to_excel(writer, sheet_name="returns")
        comp.to_excel(writer, sheet_name="prices")
        workbook  = writer.book
        worksheet = writer.sheets['prices']
        worksheet.insert_image('E1', os.path.join("backtest_carteira",filename+".png"))
        worksheet.insert_image('Q1', os.path.join("backtest_carteira",filename+"_weights.png"))

