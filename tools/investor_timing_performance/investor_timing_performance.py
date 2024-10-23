from et_lib.ET_Data_Reader import QuantumHistoricalData
from datetime import datetime
import pandas as pd
import numpy_financial as npf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

funds =[["RETORNO ABSOLUTO QUALIFICADO FI AÇÕES","Taler"],
        ["UBS CONSENSO MULTIMANAGER LONG BIASED FI AÇÕES", "Consenso"],
        ["VIC RV FIC AÇÕES","JBFO"],
        #["HONOR MASTER FI AÇÕES", "PRAGMA"],
        ["TURIM TFO AÇÕES FIC AÇÕES","TURIM"]#,
        #["18.060.935/0001-29","G5"]
]

funds_old = [
    "ALASKA POLAND INVESTIMENTO NO EXTERIOR FI AÇÕES BDR NÍVEL I",
    "ATMOS MASTER FI AÇÕES",
    "DYNAMO COUGAR FIC AÇÕES",
    "GERAÇÃO L. PAR FI AÇÕES",
    "ISHARES IBOVESPA FUNDO DE ÍNDICE - BOVA11",
    "IT NOW PIBB IBX-50 FUNDO DE ÍNDICE - PIBB11",
    "OPPORTUNITY LÓGICA MASTER FI AÇÕES",
    "SQUADRA MASTER LONG BIASED FI AÇÕES",
    "TEMPO CAPITAL PRINCIPAL FI AÇÕES"
]

def calc_stats(df: pd.DataFrame)->dict:
    """
    Calcula o conjunto de dados para um período e retorna um dicionário
    """
    df["Net_NAV_Cng"]=df["NAV"]-df["NAV"].shift(1)-df["flow"]
    df["Net_NAV_Cng"].iloc[0]=0
    df["return"].iloc[0]=1
    df["index_price"]=df["return"].cumprod(axis=0)
    df["Expected NAV"].iloc[0]=df["NAV"].iloc[0]
    df["flow"].iloc[0]=0

    nav_start = df["NAV"].iloc[0]
    #nav_end =   df["NAV"].iloc[-1]
    flows=df["flow"].sum()
    cost_basis = nav_start+flows
    net_return = df["Net_NAV_Cng"].sum()

    irr=df["flow"]
    irr[0]=nav_start
    irr[-1]=-df["Expected NAV"].iloc[-1]

    dalbar_ret = net_return/cost_basis
    market_ret = df["index_price"].iloc[-1]/df["index_price"].iloc[0]-1
    investor_irr=(1+npf.irr(irr.values))**(len(irr)-1)-1

    daily_rate=(df["index_price"][-1]/df["index_price"][0])**(1/(df.shape[0]-1))-1
    df["FV"]=[0 for _ in df.index]
    for i in range(0,df.shape[0]):
        df.iloc[i,7]=df.iloc[i,0]*(1+daily_rate)**(df.shape[0]-1-i)

    df.to_clipboard()

    return {"Dalbar":dalbar_ret, "Market":market_ret, "IRR":investor_irr, "FV (R$mm)":-round(df["FV"].sum()/100000,0)/10, "Avg NAV (R$mm)":round(df["NAV"].mean()/100000)/10}

def save_agg_data():
    fields=["PX_LAST","NAV"]
    startDate=datetime.strptime("2011-12-01", "%Y-%m-%d")
    endDate=datetime.strptime("2023-06-30", "%Y-%m-%d")
    q = QuantumHistoricalData(startDate, endDate, [i[0] for i in funds], fields)
    df=q.getData()

    for f in funds:
        df[(f[0],"Expected NAV")]=df[(f[0],"PX_LAST")]/df[(f[0],"PX_LAST")].shift(1)*df[(f[0],"NAV")].shift(1)
        df[(f[0],"flow")]=df[(f[0],"NAV")]-df[(f[0],"Expected NAV")]
        df[(f[0],"Expected NAV")].iloc[0]=df[(f[0],"NAV")].iloc[0]
        df[(f[0],"flow")].iloc[0]=0

    df.to_pickle(os.path.join("investor_timing_performance","agg_data.pickle"))
    return df

def load_demo_data():
    """
    Carrega dados do example.csv para simulação
    """
    df=pd.read_csv(os.path.join("investor_timing_performance","example.csv"))
    df=df.set_index("Unnamed: 0")
    df.columns=pd.MultiIndex.from_tuples([("a","PX_LAST"),("a","NAV")])
    df.index.name=""
    df=df.dropna()

    df[("a","Expected NAV")]=df[("a","")]/df[("a","PX_LAST")].shift(1)*df[("a","NAV")].shift(1)
    df[("a","flow")]=df[("a","NAV")]-df[("a","Expected NAV")]
    df[("a","Expected NAV")].iloc[0]=df[("a","NAV")].iloc[0]
    df[("a","flow")].iloc[0]=0
    return df

def calc_stats_table(agg_df:pd.DataFrame)->pd.DataFrame:
    """
    Calcula as estatísticas para todos os anos e retorna uma tabela
    """
    agg_df["return"]=agg_df["Expected NAV"]/agg_df["NAV"].shift(1)
    agg_df["return"].iloc[0]=1
    agg_df["index_price"]=agg_df["return"].cumprod(axis=0)
    agg_df["def_NAV"]=agg_df["NAV"]*agg_df["index_price"].iloc[0]/agg_df["index_price"]

    results=[]
    start_date=agg_df.loc[agg_df.index<=str(2012)+"-12-31"].index.max()
    for y in range(2011,2022):
        start_date=agg_df.loc[agg_df.index<=str(y)+"-12-31"].index.max()
        sub_df=agg_df[start_date:str(y+1)+"-12-31"]
        results.append({"Year":y+1}|calc_stats(sub_df.copy()))

    start_date=agg_df.loc[agg_df.index<=str(2011)+"-12-31"].index.max()
    agg_df=agg_df[str(2011)+"-12-31":str(2022)+"-12-31"]
    results.append({"Year":"total"}|calc_stats(agg_df.copy()))
    res=pd.DataFrame(data=results)
    res = res.set_index("Year")  #type: ignore
    return res 



def load_agg_data():
    df=pd.read_pickle(os.path.join("investor_timing_performance","agg_data.pickle"))
    return df

df=save_agg_data()
df=load_agg_data()

agg_df=pd.DataFrame(data={"flow":df.xs("flow",axis=1,level=1).sum(axis=1),"Expected NAV":df.xs("Expected NAV",axis=1,level=1).sum(axis=1), "NAV":df.xs("NAV",axis=1,level=1).sum(axis=1)})

#FUND BY FUND DATA
results={}
results2={}
for f in funds:
    sub_df=df[f[0]].copy()
    r=calc_stats_table(sub_df[["flow","Expected NAV","NAV"]])
    results[f[0]]=r["FV (R$mm)"]/r["Avg NAV (R$mm)"]
    results2[f[0]]=r["IRR"]-r["Market"]
    print(f)
    print(r)

industry_df=pd.DataFrame(data=results)
industry_df.to_clipboard()

print(industry_df)
industry_df=pd.DataFrame(data=results2)
industry_df.to_clipboard()
print(industry_df)

res=calc_stats_table(agg_df)

res.to_clipboard()

plot_chart=False
if plot_chart is True:
    assert(isinstance(agg_df.index,pd.DatetimeIndex))

    x={"flow"   :agg_df.groupby(by=[agg_df.index.year,agg_df.index.month])["flow"].sum().values,
    "price"  :agg_df.groupby(by=[agg_df.index.year,agg_df.index.month])["index_price"].mean().values,
    "NAV"    :agg_df.groupby(by=[agg_df.index.year,agg_df.index.month])["NAV"].mean().values,
    "def_NAV":agg_df.groupby(by=[agg_df.index.year,agg_df.index.month])["def_NAV"].mean().values,
    }

    idx=agg_df.groupby(by=[agg_df.index.year,agg_df.index.month])["flow"].sum().index.to_list()
    idx=[datetime(a[0],a[1],15) for a in idx]

    fig = make_subplots(rows=1,cols=2, specs=[[{"secondary_y": True},{"secondary_y": True}]])

    fig.add_trace(
        go.Bar(y=x["NAV"], x=idx, name="NAV", opacity=0.5),
        secondary_y=True, row=1, col=1
    )

    fig.add_trace(
        go.Scatter(y=x["price"], x=idx, name="índice", mode="lines"),
        secondary_y=False, row=1, col=1
    )

    fig.add_trace(
        go.Bar(y=x["def_NAV"], x=idx, name="NAV deflated", opacity=0.5),
        secondary_y=True, row=1, col=2
    )

    fig.add_trace(
        go.Scatter(y=x["price"], x=idx, name="índice", mode="lines"),
        secondary_y=False, row=1, col=2
    )

    # Set y-axes titles
    fig.update_yaxes(title_text="índice", secondary_y=False)
    fig.update_yaxes(title_text="PL deflacionado", secondary_y=True)
    fig.write_image(os.path.join("investor_timing_performance","NAV x Index.png"))
    fig.show()
