"""
Cria conexão com o banco de dados e a variável de sessão: CVM_datafeed_session
"""
# pylint: disable=invalid-name
from datetime import datetime
from sqlalchemy.orm import declarative_base
from sqlalchemy import create_engine, Integer, String, Date, Float, desc
from sqlalchemy.orm import sessionmaker, mapped_column
import pandas as pd
import env
from et_lib.data_basket import BasketData

__precos_engine__  = create_engine(env.connection_strings["precos"])
__precos_base__ = declarative_base()
__precos_base__.metadata.create_all(__precos_engine__)
precos_session= sessionmaker(bind=__precos_engine__)

__cenarios_macro_engine__  = create_engine(env.connection_strings["cenarios_macro"])
__cenarios_macro_base__ = declarative_base()
__cenarios_macro_base__.metadata.create_all(__cenarios_macro_engine__)
cenarios_macro_session= sessionmaker(bind=__cenarios_macro_engine__)

class Ativo_identificador(__precos_base__):
    """
    Classe que define a tabela fundos_sinonimos
    """
    __tablename__="ativo_identificadores"
    cod_ativo_identificador=mapped_column(Integer,primary_key=True)
    cod_ativo=mapped_column(String)
    cod_identificador=mapped_column(String)
    identificador=mapped_column(String(20))

class Carteiras(__cenarios_macro_base__):
    """
    Definição da tablea cenarios_macro.carteiras
    """
    __tablename__="carteiras"
    ID = mapped_column(Integer,primary_key=True)
    tipo_carteira = mapped_column(String(50))
    nome_perfil = mapped_column(String(100))
    data_rebalanceamento= mapped_column(Date)
    nome_ativo= mapped_column(String(50))
    tag_ativo= mapped_column(String(50))
    ticker_ativo= mapped_column(String(100))
    source_ativo= mapped_column(String(50))
    peso_ativo=mapped_column(Float)
    ticker_proxy_ativo= mapped_column(String(100))
    proxy_source_ativo= mapped_column(String(50))

    def to_dict(self)->dict:
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

def get_carteira(nome:str)->list:
    with cenarios_macro_session() as session:
        basket=[]
        rows=session.query(Carteiras).filter(Carteiras.tipo_carteira=="backtest").filter(Carteiras.nome_perfil==nome).order_by(Carteiras.data_rebalanceamento.desc()).all()
        rows=[r.to_dict() for r in rows]
        ult_data=rows[0]["data_rebalanceamento"]       
        for r in rows:
            if r["data_rebalanceamento"]==ult_data:
                d={
                    "Name"          : r["nome_ativo"],
                    "Ticker"        : r["ticker_ativo"],
                    "Source"        : r["source_ativo"],
                    "Weight"        : r["peso_ativo"]
                }
                if r["ticker_proxy_ativo"] is not None:
                    d["Proxy ticker"]=r["ticker_proxy_ativo"]
                if r["proxy_source_ativo"] is not None:
                    d["Proxy source"] =r["proxy_source_ativo"]
                basket.append(d)
    return basket


def CNPJ_to_name(cnpj:str)->str:
    """
    Converte um CNPJ em um nome de fundo (desde que cadastrado no banco de dados preco)
    """
    with precos_session() as session:
        result = session.query(Ativo_identificador.identificador, Ativo_identificador.cod_ativo).filter(Ativo_identificador.cod_identificador=="CNPJ").filter(Ativo_identificador.identificador==cnpj).first()
        return "" if result is None else result[1]  



if __name__=="__main__":
    print(CNPJ_to_name("51.162.466/0001-241"))