import sys
from pprint import pprint
import pymysql
from pymysql import cursors
import os
from datetime import datetime
from database_model import Files, Diligence_gestora_2, Reunioes, Estrela_vespertina_session, Gestoras_ativas

def get_db(db_name:str, autocommit:bool = True)->pymysql.Connection:
    """Opens a connection to a database on the Etrnty server

        Args:
            db_name : database name on server
            autocommit (bool) : Tells if changes will be commited automatically default is True or if connect.commit() must be called

        Raises:
            None

        Returns:
            a pymysql.connect object with the open database connection"""

    host = "172.16.215.2"
    #host="201.6.114.229"
    
    try:
        mydb = pymysql.connect(
                host=host,
                user="root",
                passwd="Loadstep1!",
                charset='utf8mb4',
                database=db_name,
                autocommit=autocommit,
                cursorclass=pymysql.cursors.DictCursor)         # type: ignore
        return mydb
    except:
        raise

def convertToBinaryData(filename):
    # Convert digital data to binary format
    with open(filename, 'rb') as file:
        binaryData = file.read()
    return binaryData

def get_file_from_db(id:int)->dict:
    """
    return dict:{"filename":str, "mimetype": str, "file":binary}
    """
    db=get_db("estrela_vespertina")
    cursor=db.cursor()
    sql="SELECT filename,mimetype, file FROM files WHERE ID="+str(id)+";"
    cursor.execute(sql)
    r=cursor.fetchone()
    db.close
    return r

def get_table()->str:
    x=""
    while x!="1" and x!="2" and x!="3" and x!="4":
        print("1 - reuniões")
        print("2 - diligence_gestora_2")
        print("3 - diligence_fundo_2")
        print("4 - diligence_gestora")
        x=input("Selecione a tabela: ")
    if x=="1":
        return "reunioes"
    elif x=="2":
        return "diligence_gestora_2"
    elif x=="3":
        return "diligence_fundo_2"
    else:
        return "diligence_gestora"

def get_referencias(CNPJ:str, table:str)->int:
    with Estrela_vespertina_session() as session:
        if table=="reunioes":
            dat=session.query(Reunioes).filter(Reunioes.cnpj_gestora==CNPJ).all()
            options= {i.id: i.data.strftime("%d-%m-%y") for i in dat}
        else:
            dat=session.query(Diligence_gestora_2).filter(Diligence_gestora_2.cnpj_gestora==CNPJ).all()
            options= {i.id: i.data_due_diligence.strftime("%d-%m-%y") for i in dat}
    ref=None
    
    while ref not in options.keys():
        pprint(options)
        ref=int(input("Selecione a referencia: "))
    assert type(ref)==int
    return ref

def get_gestoras()->dict:
    with Estrela_vespertina_session() as session:
        dat=session.query(Gestoras_ativas).all()
        options= {i.cnpj: i.nome for i in dat}
    return options

def custom_pretty_print(d):
    for key, value in sorted(d.items(), key=lambda item: item[1]):
        print(f"{key}: {value}")
    
if __name__ =='__main__':
    CNPJ = None
    for i in range(1, len(sys.argv)):
        # Check if the current argument is "cnpj"
        if sys.argv[i] == "--cnpj":
            # Check if there is a value provided after the "cnpj" argument
            if i + 1 < len(sys.argv):
                CNPJ = sys.argv[i + 1]
    db=get_db("estrela_vespertina")
    cursor=db.cursor()
    input("Coloque todos os arquivos no diretorio files_to_upload e pressione enter")
    arr = os.listdir(os.path.join("blob","files_to_upload"))
    gestora_dict=get_gestoras()
   
    for a in arr:
        print("Detalhes do arquivo: "+a)
        if CNPJ is None:
            while CNPJ not in gestora_dict.keys():
                custom_pretty_print(gestora_dict)
                CNPJ=input("ID da gestora: ")

        tabela_referencia=get_table()
        ID_referencia=get_referencias(CNPJ,tabela_referencia)

        titulo=input("Titulo: ")
        mime=input("Mime (application/pdf): ")
        mime = mime if mime!="" else 'application/pdf'
        data=input("Data ("+datetime.now().strftime("%Y-%m-%d")+"): ")
        data = data if data !="" else datetime.now().strftime("%Y-%m-%d")

        s = convertToBinaryData(os.path.join("blob","files_to_upload",a))
        sql = """INSERT INTO files ( CNPJ_gestora, tabela_referencia, ID_referencia, `Data`, Description, mimetype, filename, file) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"""
        v_tuple=(CNPJ, tabela_referencia ,ID_referencia ,data,titulo,mime,a,s)
        r=cursor.execute(sql,v_tuple)

        print("Arquivo inserido com ID: ", cursor.lastrowid)
        print('<a href="/estrela_vespertina/download?ID='+str(cursor.lastrowid)+'">'+titulo+'</a>')
        print()

    print("done")