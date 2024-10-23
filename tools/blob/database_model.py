import json
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Integer, String, SmallInteger, Float, Boolean, Date, Text, LargeBinary
from sqlalchemy.orm import sessionmaker, relationship, mapped_column
from sqlalchemy import ForeignKey

__estrela_vespertina_engine__  = create_engine("mysql+mysqldb://"+"root"+":"+"Loadstep1!"+"@172.16.215.2/"+"estrela_vespertina")
__estrela_vespertina_base__ = declarative_base()

class Reunioes(__estrela_vespertina_base__):
    __tablename__="reunioes"
    id = mapped_column(Integer, primary_key=True)
    cnpj_gestora = mapped_column(String(18), ForeignKey('empresas.cnpj'))
    reuniao_gestora = relationship("Empresa", foreign_keys=[cnpj_gestora])
    data=mapped_column(Date)
    comentarios_publicos=mapped_column(Text)
    comentarios_privados=mapped_column(Text)


class Gestoras_ativas(__estrela_vespertina_base__):
    __tablename__="gestoras_ativas"
    cnpj=mapped_column(String(18),primary_key=True)
    nome=mapped_column(String(255))
    
    def to_dict(self, use_br_for_line_break=True):
        r={}
        for column in self.__table__.columns:
            if getattr(self, column.name) is None:
                r[column.name]=""
            else:
                r[column.name]=getattr(self, column.name)
            if use_br_for_line_break is True:
                if isinstance(r[column.name],str):
                    r[column.name]=r[column.name].replace("\n","<BR>")
        return r


class Empresa(__estrela_vespertina_base__):
    __tablename__="empresas"
    cnpj=mapped_column(String(18),primary_key=True)
    nome=mapped_column(String(255))
    gestora=mapped_column(Boolean)
    auditor=mapped_column(Boolean)
    administrador=mapped_column(Boolean)

class Pessoa(__estrela_vespertina_base__):
    __tablename__="pessoas"
    cpf=mapped_column(String(14),primary_key=True)
    nome=mapped_column(String(255))
    nascimento=mapped_column(Date)
    linkedin=mapped_column(String(255))
    graduacao=mapped_column(String(70))
    certificacoes=mapped_column(String(110))

class Master(__estrela_vespertina_base__):
    __tablename__="masters"
    cnpj=mapped_column(String(18),primary_key=True)
    nome=mapped_column(String(255))
    cnpj_gestora=mapped_column(String(18))
    categoria=mapped_column(String(50))
    proxy=mapped_column(String(50))
    proxy_source=mapped_column(String(20))
    proxy_start_date=mapped_column(Date)
    benchmark=mapped_column(String(30))


class Diligence_gestora_2(__estrela_vespertina_base__):
    __tablename__="diligence_gestora_2"
    #descritivo
    id = mapped_column(Integer, primary_key=True)
    cnpj_gestora = mapped_column(String(18), ForeignKey('empresas.cnpj'))
    cnpj_auditor = mapped_column(String(18), ForeignKey('empresas.cnpj'))
    empresa_gestora = relationship("Empresa", foreign_keys=[cnpj_gestora])
    empresa_auditor = relationship("Empresa", foreign_keys=[cnpj_auditor])
    data_due_diligence=mapped_column(Date)
    ano_fundacao=mapped_column(SmallInteger)
    numero_funcionarios=mapped_column(SmallInteger)
    ativos_sob_gestao=mapped_column(Float)
    rating_agencia=mapped_column(String(50))
    estrategias_de_atuacao=mapped_column(Text)   #lista em JSON
    #partnership
    porcentagem_lucro_bonus_pool=mapped_column(Float)
    regra_remuneracao_variavel=mapped_column(String(280))
    preco_entrada_saida_socios=mapped_column(String(280))
    criterio_entrada_saida_socios=mapped_column(String(280))
    numero_colaboradores_deixaram_equipe_5_anos=mapped_column(SmallInteger)
    comentarios_adicionais_turn_over=mapped_column(Text)
    plano_sucessao=mapped_column(Text)
    score_partnership=mapped_column(SmallInteger)
    resumo_score_partnership=mapped_column(String(280))
    #Controles e risco
    reguladores_gestora=mapped_column(String(280))
    sistemas_risco=mapped_column(String(280))
    checagem_pre_trade=mapped_column(Boolean)
    sistema_processo_checagem_enquadramento=mapped_column(Text)
    sistema_processo_compliance=mapped_column(String(280))
    cpf_responsavel_compliance=mapped_column(String(14), ForeignKey('pessoas.cpf'))
    cpf_compliance = relationship("Pessoa", foreign_keys=[cpf_responsavel_compliance])  
    diretor_risco_zera_posicao=mapped_column(Boolean)
    processos_gestora=mapped_column(Text)
    controle_insider_trading=mapped_column(Text)
    participacao_conselhos=mapped_column(String(280))
    monitoramento_investimentos_pessoais=mapped_column(Text)
    sistemas_redundancia_ti=mapped_column(Text)
    checagem_redundancia=mapped_column(String(280))
    demissao_regras_controle=mapped_column(String(280))
    consideracoes_passivo=mapped_column(Text)
    score_controles=mapped_column(SmallInteger)
    resumo_score_controles=mapped_column(String(280))
    #Alinhamento de interesse
    obrigatoriedade_fundos_casa=mapped_column(String(280))
    lock_up_liquidez_colaboradores=mapped_column(String(280))
    politica_investimentos_pessoais=mapped_column(String(280))
    alinhamento_remuneracao_cotista=mapped_column(Text)
    outras_atividades_executivos=mapped_column(Text)
    score_alinhamento=mapped_column(SmallInteger)
    resumo_score_alinhamento=mapped_column(String(280))
    observacoes=mapped_column(Text)

    def to_dict(self, use_br_for_line_break=True):
        r={}
        for column in self.__table__.columns:
            if getattr(self, column.name) is None:
                r[column.name]=""
            elif column.name=="estrategias_de_atuacao":
                s=getattr(self, column.name)
                s=s.replace("'",'"')
                r[column.name]=json.loads(s)
            else:
                r[column.name]=getattr(self, column.name)
            if use_br_for_line_break is True:
                if isinstance(r[column.name],str):
                    r[column.name]=r[column.name].replace("\n","<BR>")
        return r
    
class Diligence_fundo_2(__estrela_vespertina_base__):
    __tablename__="diligence_fundo_2"
    #descritivo
    id=mapped_column(Integer,primary_key=True)
    cnpj_fundo=mapped_column(String(18), ForeignKey("masters.cnpj"))
    master_fundo = relationship("Master", foreign_keys=[cnpj_fundo])
    data_due_diligence=mapped_column(Date)
    cnpj_gestora=mapped_column(String(18), ForeignKey('empresas.cnpj'))
    cnpj_auditor=mapped_column(String(18), ForeignKey('empresas.cnpj'))
    cnpj_administrador=mapped_column(String(18), ForeignKey('empresas.cnpj'))
    empresa_gestora = relationship("Empresa", foreign_keys=[cnpj_gestora])
    empresa_auditor = relationship("Empresa", foreign_keys=[cnpj_auditor])
    empresa_administrador = relationship("Empresa", foreign_keys=[cnpj_administrador])
    distribuidores=mapped_column(String(280))
    tx_gestao_adm=mapped_column(Float)
    tx_adm_custodia=mapped_column(Float)
    tx_performance=mapped_column(Float)
    benchmark_performance=mapped_column(String(20))
    cotizacao_resgate=mapped_column(String(15))
    pagamento_resgate=mapped_column(String(15))
    key_man_clause=mapped_column(String(280))
    categoria_fundo=mapped_column(String(50))
    estrategia_estilo_atuacao=mapped_column(String(280))
    #Aplicabilidade histórico
    pl_fundo=mapped_column(SmallInteger)
    pl_estrategia=mapped_column(SmallInteger)
    capacidade_estrategia=mapped_column(SmallInteger)
    consideracoes_pl_capacidade=mapped_column(Text)
    estrategia_ja_fechada=mapped_column(Text)
    consideracoes_passivo=mapped_column(Text)
    mudancas_estrategia=mapped_column(Text)
    mudancas_equipe=mapped_column(Text)
    score_aplicabilidade_historico=mapped_column(SmallInteger)
    resumo_score_aplicabilidade=mapped_column(String(280))
    #controles
    historico_marcacao_adm=mapped_column(Text)
    limites_risco=mapped_column(String(280))
    limites_concentracao=mapped_column(String(280))
    limites_liquidez=mapped_column(String(280))
    politicas_zeragem=mapped_column(String(280))
    score_controles=mapped_column(SmallInteger)
    resumo_score_controles=mapped_column(String(280))
    #processo de investimento
    processo_investimentos=mapped_column(Text)
    principais_gestores=mapped_column(Text)
    tamanho_time_investimento=mapped_column(SmallInteger)
    detalhes_time_investimento=mapped_column(Text)
    score_processo=mapped_column(SmallInteger)
    resumo_score_processo=mapped_column(String(280))
    #quant
    score_quant=mapped_column(SmallInteger)
    resumo_score_quant=mapped_column(String(280))
    observacoes=mapped_column(String)

    def to_dict(self, use_br_for_line_break=True):
        r={}
        for column in self.__table__.columns:
            if getattr(self, column.name) is None:
                r[column.name]=""
            else:
                r[column.name]=getattr(self, column.name)
            if use_br_for_line_break is True:
                if isinstance(r[column.name],str):
                    r[column.name]=r[column.name].replace("\n","<BR>")
        return r

class Files(__estrela_vespertina_base__):
    __tablename__="files"
    #descritivo
    id=mapped_column(Integer,primary_key=True)
    cnpj_gestora=mapped_column(String(18), ForeignKey("empresas.cnpj"))
    empresa_file = relationship("Empresa", foreign_keys=[cnpj_gestora])
    tabela_referencia=mapped_column(String(50))
    id_referencia=mapped_column(Integer)
    data=mapped_column(Date)
    description=mapped_column(Text)
    mimetype=mapped_column(String(30))
    filename=mapped_column(String(100))
    file=mapped_column(LargeBinary)

    def to_dict(self, use_br_for_line_break=True):
        r={}
        for column in list(self.__table__.columns)[:-1]:
            if getattr(self, column.name) is None:
                r[column.name]=""
            else:
                r[column.name]=getattr(self, column.name)
            if use_br_for_line_break is True:
                if isinstance(r[column.name],str):
                    r[column.name]=r[column.name].replace("\n","<BR>")
        return r

__estrela_vespertina_base__.metadata.create_all(__estrela_vespertina_engine__)
Estrela_vespertina_session= sessionmaker(bind=__estrela_vespertina_engine__)

