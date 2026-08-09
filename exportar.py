import pandas as pd
import psycopg2

def exportar_para_excel():
    # Conecta no banco
    conn = psycopg2.connect(
        dbname="postgres", 
        user="postgres", 
        password="senha123", 
        host="localhost", 
        port="5432"
    )
    
    # Busca os dados usando pandas
    query = "SELECT * FROM comentarios"
    df = pd.read_sql_query(query, conn)
    
    # Salva como Excel
    df.to_excel("comentarios_analisados.xlsx", index=False)
    
    conn.close()
    print("Sucesso! O arquivo 'comentarios_analisados.xlsx' foi criado na sua pasta.")

if __name__ == "__main__":
    exportar_para_excel()