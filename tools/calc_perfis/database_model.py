from datetime import datetime
from sqlalchemy import create_engine, Integer, String, SmallInteger, Float, Boolean, Date, Text, LargeBinary, JSON
from sqlalchemy.orm import sessionmaker, relationship, mapped_column, declarative_base

from et_lib.ET_Portfolio import Portfolio_item
import env as env

__cenario_macro_engine__  = create_engine(env.connection_strings["cenarios_macro"])
__cenario_macro_base__ = declarative_base()

class Carteira(__cenario_macro_base__):
    __tablename__="carteiras"
    id                      = mapped_column(Integer, primary_key=True)
    tipo_carteira           = mapped_column(String(50))
    nome_perfil             = mapped_column(String(100))
    data_rebalanceamento    = mapped_column(Date)
    nome_ativo              = mapped_column(String(50))
    tag_ativo               = mapped_column(String(50))
    ticker_ativo            = mapped_column(String(50))
    source_ativo            = mapped_column(String(50))
    peso_ativo              = mapped_column(Float)
    ticker_proxy_ativo      = mapped_column(String(50))
    proxy_source_ativo      = mapped_column(String(50))

    def to_dict(self)->dict:
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
    
class Grupo_perfil(__cenario_macro_base__):
    __tablename__="grupo_perfis"
    id                      = mapped_column(Integer, primary_key=True)
    nome_grupo              = mapped_column(String(50))
    idx                     = mapped_column(SmallInteger)
    nome_perfil             = mapped_column(String(100))
    pesos                   = mapped_column(JSON)

    def to_dict(self)->dict:
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

cenario_marco_session = sessionmaker(bind=__cenario_macro_engine__)

def get_carteiras(tipo: str, nome: str)->dict:
    ret={}
    with cenario_marco_session() as session:
        rows=session.query(Carteira).filter(Carteira.tipo_carteira==tipo).filter(Carteira.nome_perfil==nome).all()
        rows=[r.to_dict() for r in rows]
        for r in rows:
            data=datetime(r["data_rebalanceamento"].year, r["data_rebalanceamento"].month, r["data_rebalanceamento"].day)
            if data not in ret.keys():
                ret[data]=[]
            ret[data].append(
                Portfolio_item(r["nome_ativo"],r["tag_ativo"],r["ticker_ativo"],r["source_ativo"],r["peso_ativo"])
            )
    return ret

def get_estrategia(grupo:str,nome_perfil:str)->dict:
    with cenario_marco_session() as session:
        row=session.query(Grupo_perfil).filter(Grupo_perfil.nome_grupo==grupo).filter(Grupo_perfil.nome_perfil==nome_perfil).first()
        if row is None:
            return {}
        else:
            return row.to_dict()["pesos"]


if __name__=="__main__":
    x=get_estrategia("Local","Vênus")
    print(x)
    print(type(x))