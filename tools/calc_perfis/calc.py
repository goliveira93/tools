"""
Esse programa calcular graficos de waterfall com a quebra de performance para cada um dos 5 perfis
parameters:
    None
Returns:
    None
Throws:
    Assertion error se algum perfil não tiver pesos somando 100
"""

# pylint: disable=invalid-name

from typing import Tuple
from datetime import datetime
import os
import pandas as pd
import plotly.graph_objects as go
from math import isclose
from plotly.subplots import make_subplots
from et_lib.ET_Portfolio import Portfolio, Portfolio_item
from et_lib.ET_Data_Reader import QuantumHistoricalData
from carteiras import estrategias
from settings import colors
from pie_chart import tabela_recomendada
from database_model import get_carteiras

#end_date=datetime.datetime.today()

chart_horizontal_layout = dict(
    width=1500,
    height=500,
    margin={"l":100,"r":20},
    font={"family":"Segoe UI"},
    legend={"yanchor":"bottom",
            "xanchor":"left",
            "x":0,
            "y":-0.2,
            "orientation":"h"},
    #shapes=recs,
    yaxis={
        "tickformat":".2f"
        },
    xaxis={
        "domain": [0, 0.97]  # Set the domain of the x-axis to use 90% of the available space
    },
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)'
)

combined_chart_layout=dict(
    width=650*3,
    height=650,
    font={"family":"Segoe UI","size":15},
    legend={"orientation":"h"},
    showlegend=False,
    xaxis1= {"tickformat":",","showgrid":False, "zeroline":False},
    yaxis1= {"tickformat":".1%","showgrid":False, "zeroline":False},
    xaxis2= {"tickformat":",","showgrid":False, "zeroline":False},
    yaxis2= {"tickformat":".1%","showgrid":False, "zeroline":False},
    xaxis3= {"tickformat":",","showgrid":False, "zeroline":False},
    yaxis3= {"tickformat":".1%","showgrid":False, "zeroline":False},
    margin=dict(l=20, r=20, t=25, b=25),
    hovermode = "x",
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)'
)

def get_strategy_waterfall(perfil:str, start_date:datetime, MTD_date: datetime, YTD_date:datetime, end_date:datetime)->go.Figure:
    """"
    retorna uma figura com tres gráficos de quebra de estratégia
    """
    fig = make_subplots(rows=1, cols=3, subplot_titles=('Performance mês', 'Performance YTD', 'Performance LTD'))
    #for annotation in fig.layout.annotations:   #type: ignore
    #    annotation.font.size = 16  # Change the number to your desired font size
    w={i.ticker:i.weight for i in estrategias[perfil]}
    p=Portfolio(False,estrategias[perfil])

    labels=["CDI",
            "Multimercado",
            "Inflação",
            "Ações",
            "Outros",
            "Estratégia"]
    measure = ["relative", "relative", "relative", "relative", "relative", "total"]

    strategy_prices=p.portfolio_prices(start_date,end_date)
    assert isinstance(p.returns,pd.DataFrame)
    assert isinstance(p.prices,pd.DataFrame)
    daily_returns=p.returns.droplevel(level=1,axis=1)
    daily_excess_returns=daily_returns.subtract(daily_returns["CDI"],axis=0)
    daily_excess_contribution=daily_excess_returns.multiply(w)  #type: ignore
    YTD=YTD_date if start_date<YTD_date else start_date


    for chart_no,dat in enumerate([MTD_date,YTD,start_date]):
        subset=daily_excess_contribution.loc[(daily_excess_contribution.index<=end_date) & (daily_excess_contribution.index>dat)]
        total_strat_ret=strategy_prices.loc[end_date]/strategy_prices.loc[dat]-1
        total_CDI_ret=p.prices.loc[end_date][("CDI","PX_LAST")]/p.prices.loc[dat][("CDI","PX_LAST")]-1   #type_ignore
        x=(subset+1).product()-1

        data=[total_CDI_ret,
              x["IFMM BTG Pactual"],
              x["IMA-B"],
              x["IBX"],
              total_strat_ret-total_CDI_ret-x.sum(),    #interação dos fatores
              total_strat_ret]

        fig.add_trace(go.Waterfall(
            orientation = "v",
            measure = measure,
            x = labels,
            textposition = "outside",
            increasing = {"marker":{"color":colors[0]}},
            decreasing = {"marker":{"color":colors[3]}},
            totals =     {"marker":{"color":colors[6]}},
            connector =  {"visible":False},
            text = [f"{i:.1%}" for i in data],
            y = data
        ), row=1,col=chart_no+1)
    fig.update_layout(combined_chart_layout)#, title={"text":"Performance "+tit, "x":0.5, "y":0.99, "xanchor":"center","yanchor":"top"})
    for annotation in fig.layout.annotations:   #type: ignore
        annotation.font.size = 20  # Change the number to your desired font size
    return fig

def get_perfil_waterfall(perfil:str, ipca_prices:pd.Series, benchmark_prices:pd.Series, start_date:datetime, MTD_date: datetime, YTD_date:datetime, end_date:datetime)->Tuple[go.Figure,go.Figure]:
    """"
    retorna um grafico triplo com as quebras de performance entre estratégia, tática e seleção em 3 janelas (mtd, ytd, ltd)
    """

    fig = make_subplots(rows=1, cols=3, subplot_titles=('Performance mês', 'Performance YTD', 'Performance LTD'))
    #for annotation in fig.layout.annotations:   #type: ignore
    #    annotation.font.size = 16  # Change the number to your desired font size
    w=sum([i.weight for i in estrategias[perfil]])
    p=Portfolio(False,estrategias[perfil])
    strategy_prices=p.portfolio_prices(start_date,end_date)

    prices={}
    for tipo in ["tática","recomendada"]:
        carteiras=get_carteiras(tipo, perfil)
        datas=sorted(carteiras.keys())
        w=sum([i.weight for i in carteiras[datas[0]]])
        assert isclose(w,1)
        t=Portfolio(True,carteiras[datas[0]])
        for r in datas[1:]:
            w=sum([i.weight for i in carteiras[r]])
            try:
                assert isclose(w,1)
            except:
                print(carteiras[r])
                print(w)
                raise AssertionError
            if r<end_date:
                t.add_rebalance(r,carteiras[r])
        prices[tipo]=t.portfolio_prices(start_date,end_date)

    analysis=pd.concat([benchmark_prices,strategy_prices,prices["tática"],prices["recomendada"]],axis=1)
    analysis.columns=["CDI","Estratégia","Tática","Seleção"]
    analysis=analysis.dropna(how="any")
    labels=["CDI",
            "Estratégia",
            "Tática",
            "Seleção",
            "Outros",
            "Total"]
    measure = ["relatve", "relative", "relative", "relative", "relative", "total"]

    for chart_no, (tit,dat) in enumerate([("Mês",MTD_date), ("YTD",YTD_date), ("LTD",start_date)]):
        subset=analysis.loc[end_date]/analysis.loc[dat]
        data=[subset["CDI"]-1,
                    subset["Estratégia"]/subset["CDI"]-1,
                    subset["Tática"]/subset["Estratégia"]-1,
                    subset["Seleção"]/subset["Tática"]-1]
        data.append(subset["Seleção"]-1-sum(data))
        data.append(subset["Seleção"]-1)
        #base = [sum(data[:i]) for i in range(len(data))]

        fig.add_trace(go.Waterfall(
            orientation = "v",
            measure = measure,
            x = labels,
            textposition = "outside",
            increasing = {"marker":{"color":colors[0]}},
            decreasing = {"marker":{"color":colors[3]}},
            totals =     {"marker":{"color":colors[6]}},
            connector =  {"visible":False},
            text = [f"{i:.1%}" for i in data],
            y = data,
            #base=max(base)*1.1
        # connector = {"line":{"color":"rgb(63, 63, 63)"}},
        ), row=1,col=chart_no+1)
        fig.update_layout(combined_chart_layout)#, title={"text":"Performance "+tit, "x":0.5, "y":0.99, "xanchor":"center","yanchor":"top"})
        for annotation in fig.layout.annotations:   #type: ignore
            annotation.font.size = 20  # Change the number to your desired font size
    
    time_series_fig=go.Figure()
    analysis=pd.concat([ipca_prices,analysis],axis=1)
    analysis=analysis.rename(columns={0:"IPC-A"})
    for c,column in zip([3,4,1,6,7],analysis.columns):
        time_series_fig.add_trace(go.Scatter(x=analysis.index, y=analysis[column],mode='lines', name=column, line={"color":colors[c]} ))
    time_series_fig.update_layout(chart_horizontal_layout)
    time_series_fig.update_yaxes(title="retorno acumulado")
    return fig, time_series_fig

def make_bar_charts(start_date:datetime, MTD_date:datetime,YTD_date:datetime, end_date:datetime)->go.Figure:
    """
    Faz 3 gráficos de barra com performance do CDI, IFMM, IMA-B e IBX
    """
    fig = make_subplots(rows=1, cols=3, subplot_titles=('Performance mês', 'Performance YTD', 'Performance LTD'))
    bench_dict={
        "IPCA":"IPC-A",
        "CDI":"CDI",
        "IFMM BTG Pactual":"Multimercado",
        "IMA-B":"Inflação",
        "IBX":"Ações"
    }
    q=QuantumHistoricalData(start_date,end_date,list(bench_dict.keys()))
    df=q.getData().droplevel(1,axis=1)
    cols=[bench_dict[i] for i in df.columns]
    df.columns=cols
    for chart_no,dat in enumerate([MTD_date,YTD_date,start_date]):
        returns=df.loc[end_date] / df.loc[dat]-1
        fig.add_trace(go.Bar(
            x=returns.index,
            text = [f"{i:.1%}" for i in returns],
            y = returns.values,
            marker_color=colors
        ), row=1,col=chart_no+1)
        fig.update_layout(combined_chart_layout)#, title={"text":"Performance "+tit, "x":0.5, "y":0.99, "xanchor":"center","yanchor":"top"})
        for annotation in fig.layout.annotations:   #type: ignore
            annotation.font.size = 20  # Change the number to your desired font size
    fig.write_image(os.path.join(".","calc_perfis","figures","benchmarks.png"))
    return fig
        



def make_charts(perfis:list, start_date:datetime,YTD_date:datetime, MTD_date:datetime, end_date:datetime):
    benchmark=Portfolio(False,[Portfolio_item("Caixa" ,"Caixa","CDI","Quantum",1)])
    benchmark_prices=benchmark.portfolio_prices(start_date,end_date)
    ipca=Portfolio(False,[Portfolio_item("Caixa" ,"Caixa","IPCA","Quantum",1)])
    ipca_prices=ipca.portfolio_prices(start_date,end_date)
    for perf in perfis:
        print("Getting charts: "+perf)
        (fig,time_series_fig)=get_perfil_waterfall(perf, ipca_prices, benchmark_prices,start_date,MTD_date,YTD_date,end_date)

        fig.write_image(os.path.join(".","calc_perfis","figures",perf+".png"))
        time_series_fig.write_image(os.path.join(".","calc_perfis","figures","time_series_"+perf+".png"))
        carteiras=get_carteiras("recomendada",perf)
        idx=max(carteiras.keys())
        carteira=carteiras[idx]
        fig=tabela_recomendada(perf,carteira)
        fig.write_image(os.path.join(".","calc_perfis","figures",perf+"_recomendada.png"))

        f=get_strategy_waterfall(perf,start_date,MTD_date,YTD_date,end_date)
        f.write_image(os.path.join(".","calc_perfis","figures","estrategia_"+perf+".png"))



if __name__ =="__main__":
    start_date= datetime.strptime("12-30-2022","%m-%d-%Y")
    YTD_date= datetime.strptime("12-29-2023","%m-%d-%Y")
    MTD_date= datetime.strptime("12-29-2023","%m-%d-%Y")
    end_date= datetime.strptime("01-31-2024","%m-%d-%Y")
    make_bar_charts(start_date,MTD_date,YTD_date,end_date)
    make_charts(["Mercúrio","Vênus","Terra","Marte","Júpiter"], start_date, YTD_date, MTD_date, end_date)
    start_date= datetime.strptime("03-14-2023","%m-%d-%Y")
    make_charts(["Bruges"], start_date, YTD_date, MTD_date, end_date)