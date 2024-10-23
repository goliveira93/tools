"""
Esse programa calcular graficos de waterfall com a quebra de performance para cada um dos 5 perfis
parameters:
    None
Returns:
    None
Throws:
    Assertion error se algum perfil não tiver pesos somando 100
"""
import datetime
import os
from math import isclose
import pandas as pd
import plotly.graph_objects as go
from et_lib.ET_Portfolio import Portfolio, Portfolio_item
from carteiras import estrategias
from calc import get_strategy_waterfall
from settings import colors
from database_model import get_carteiras
from plotly.subplots import make_subplots
from calc import combined_chart_layout


start_date= datetime.datetime.strptime("03-14-2023","%m-%d-%Y")
#start_date= datetime.datetime.strptime("12-30-2022","%m-%d-%Y")
YTD_date= datetime.datetime.strptime("12-29-2023","%m-%d-%Y")
#YTD_date= datetime.datetime.strptime("12-30-2022","%m-%d-%Y")
MTD_date= datetime.datetime.strptime("12-29-2023","%m-%d-%Y")
end_date= datetime.datetime.strptime("01-31-2024","%m-%d-%Y")
#end_date=datetime.datetime.today()

benchmark=Portfolio(False,[Portfolio_item("Caixa" ,"Caixa","CDI","Quantum",1)])
benchmark_prices=benchmark.portfolio_prices(start_date,end_date)
ipca=Portfolio(False,[Portfolio_item("Caixa" ,"Caixa","IPCA","Quantum",1)])
ipca_prices=ipca.portfolio_prices(start_date,end_date)

chart_layout=dict(
    width=650,
    height=650,
    font={"family":"Segoe UI","size":15},
    legend={"orientation":"h"},
    xaxis= {"tickformat":",","showgrid":False, "zeroline":False},
    yaxis= {"tickformat":".1%","showgrid":False, "zeroline":False},
    margin=dict(l=20, r=20, t=25, b=25),
    hovermode = "x",
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)'
)



for perfil in ["Bruges"]:#","Can"]:
    fig = make_subplots(rows=1, cols=3, subplot_titles=('Performance mês', 'Performance YTD', 'Performance LTD'))
    w=sum([i.weight for i in estrategias[perfil]])
    assert isclose(w,1) is True
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



        f=get_strategy_waterfall(perfil,start_date=start_date)
        f.write_image(os.path.join(".","calc_perfis","figures","estrategia_"+perfil+".png"))
        fig.update_layout(chart_layout, title={"text":"Performance "+tit, "x":0.5, "y":0.99, "xanchor":"center","yanchor":"top"})
        print("Writing: "+perfil+"_"+tit+".png")
        fig.write_image(os.path.join(".","calc_perfis","figures",perfil+"_"+tit+".png"))
        