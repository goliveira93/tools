from datetime import date
 
from gb.shortcuts_requests import Factory
 
if __name__ == "__main__":
    inicial = date(2023, 11, 30)
 
    final = date(2023, 11, 30)
 
    aa = Factory.get_posicao_carteira(
        IdsCarteira="3583751;3583751",
        dataInicial=inicial,
        dataFinal=final,
        desconsideraGrossup="true",
    )
 
    print(aa)
    print("MAIN")
   
 