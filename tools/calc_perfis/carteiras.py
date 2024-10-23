"""
Dados das carteiras
"""
import datetime
from et_lib.ET_Portfolio import Portfolio_item
from database_model import Carteira, cenario_marco_session, get_carteiras

#ETRNTY ÉON MM MASTER FIC MULTIMERCADO
#ETRNTY EVO FIC MULTIMERCADO
#CAPITÂNIA RADAR 90 FI MULTIMERCADO CRÉDITO PRIVADO LP
#XP BANCOS FI RENDA FIXA REFERENCIADO DI CRÉDITO PRIVADO


estrategias = {
    "Mercúrio" : [
        Portfolio_item("Caixa"       ,"Caixa",       "CDI"              ,"Quantum",0.05),
        Portfolio_item("Multimercado","Multimercado","IFMM BTG Pactual" ,"Quantum",0.15),
        Portfolio_item("Inflação"    ,"Inflação",    "IMA-B"            ,"Quantum",0.50),
        Portfolio_item("Ações"       ,"Ações",       "IBX"              ,"Quantum",0.30)
    ],
    "Vênus" : [
        Portfolio_item("Caixa"       ,"Caixa",       "CDI"              ,"Quantum",0.10),
        Portfolio_item("Multimercado","Multimercado","IFMM BTG Pactual" ,"Quantum",0.25),
        Portfolio_item("Inflação"    ,"Inflação",    "IMA-B"            ,"Quantum",0.45),
        Portfolio_item("Ações"       ,"Ações",       "IBX"              ,"Quantum",0.20)
    ],
    "Terra" : [
        Portfolio_item("Caixa"       ,"Caixa",       "CDI"              ,"Quantum",0.20),
        Portfolio_item("Multimercado","Multimercado","IFMM BTG Pactual" ,"Quantum",0.30),
        Portfolio_item("Inflação"    ,"Inflação",    "IMA-B"            ,"Quantum",0.40),
        Portfolio_item("Ações"       ,"Ações",       "IBX"              ,"Quantum",0.10)
    ],
    "Marte" : [
        Portfolio_item("Caixa"       ,"Caixa",       "CDI"              ,"Quantum",0.40),
        Portfolio_item("Multimercado","Multimercado","IFMM BTG Pactual" ,"Quantum",0.25),
        Portfolio_item("Inflação"    ,"Inflação",    "IMA-B"            ,"Quantum",0.30),
        Portfolio_item("Ações"       ,"Ações",       "IBX"              ,"Quantum",0.05)
    ],
    "Júpiter" : [
        Portfolio_item("Caixa"       ,"Caixa",       "CDI"              ,"Quantum",0.60),
        Portfolio_item("Multimercado","Multimercado","IFMM BTG Pactual" ,"Quantum",0.25),
        Portfolio_item("Inflação"    ,"Inflação",    "IMA-B"            ,"Quantum",0.15),
        Portfolio_item("Ações"       ,"Ações",       "IBX"              ,"Quantum",0.00)
    ],
    "Bruges" : [
        Portfolio_item("Caixa"       ,"Caixa",       "CDI"              ,"Quantum",0.15),
        Portfolio_item("Multimercado","Multimercado","IFMM BTG Pactual" ,"Quantum",0.325),
        Portfolio_item("Inflação"    ,"Inflação",    "IMA-B"            ,"Quantum",0.4),
        Portfolio_item("Ações"       ,"Ações",       "IBX"              ,"Quantum",0.125)
    ],
    "Can" : [
        Portfolio_item("Caixa"       ,"Caixa",       "CDI"              ,"Quantum",0.05),
        Portfolio_item("Multimercado","Multimercado","IFMM BTG Pactual" ,"Quantum",0.25),
        Portfolio_item("Inflação"    ,"Inflação",    "IMA-B"            ,"Quantum",0.35),
        Portfolio_item("Ações"       ,"Ações",       "IBX"              ,"Quantum",0.35)
    ],
}

if __name__=="__main__":
    print(get_carteiras("recomendada","Mercúrio"))