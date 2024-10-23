import pandas as pd
from blp import blp

bquery = blp.BlpQuery().start()

start_date_list=["20201115","20211115","20221115"]
end_date_list=["20211115","20221115","20231115"]


for start_date,end_date in zip(start_date_list,end_date_list):
    df=bquery.bds("BZRFIMAB Index", "INDX_MWEIGHT_HIST",overrides=[("END_DATE_OVERRIDE", start_date)])
    df["Ticker ANBE"]=df["Index Member"]+"@ANBE Govt"
    df["Ticker TUNE"]=df["Index Member"]+"@TUNE Govt"
    df["Ticker"]=df["Index Member"]+" Govt"
    names=bquery.bdp(list(df["Ticker"])+["BZRFIMAB Index"],["SECURITY_NAME"])
    
    temp=bquery.bdh(list(df["Ticker ANBE"])+["BZRFIMAB Index"],["PX_LAST"],start_date=start_date, end_date=end_date)
    temp["security"]=temp["security"].apply(lambda x: names.loc[names["security"]==x.replace("@ANBE",""),"SECURITY_NAME"].values[0])
    prices=temp.pivot(index="date",columns="security").droplevel(level=0,axis=1)

    temp=bquery.bdh(list(df["Ticker TUNE"]),["PX_BID","PX_ASK","DUR_ADJ_OAS_BID"],start_date=start_date, end_date=end_date)
    temp["security"]=temp["security"].apply(lambda x: names.loc[names["security"]==x.replace("@TUNE",""),"SECURITY_NAME"].values[0])
    temp["spread"]=(temp["PX_BID"]-temp["PX_ASK"])*temp["DUR_ADJ_OAS_BID"]
    spread=temp[["date","security","spread"]].pivot(index="date",columns="security").droplevel(level=0,axis=1)



    drops=prices.isna().sum().loc[prices.isna().sum()>100]
    prices=prices.loc[:,prices.columns.isin(drops.index)==False]
    rets=(prices/prices.shift(5)-1).dropna()
    spreads=spread.dropna().mean()/100
    corr=rets.corr()["Anbima Brazil IPCA Inflation L"]
    result=pd.concat([corr,spreads],axis=1).dropna()
    result.columns=["correlação","bid/offer"]
    print(result.sort_values(by="correlação"))
    result.sort_values(by="correlação").to_clipboard()
    input("press enter")

