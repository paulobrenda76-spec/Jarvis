import praw
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    return psycopg2.connect(dbname="postgres", user="postgres", password="senha123", host="localhost", port="5432")

def inicializar_banco():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS comentarios (
            id SERIAL PRIMARY KEY,
            reddit_id TEXT UNIQUE,
            texto TEXT,
            subreddit TEXT,
            autor TEXT,
            classificacao TEXT DEFAULT 'Pendente',
            justificativa TEXT DEFAULT 'Aguardando',
            status TEXT DEFAULT 'pendente'
        )
    """)
    conn.commit()
    cur.close()
    conn.close()

def configurar_reddit():
    return praw.Reddit(
        client_id=os.getenv("REDDIT_CLIENT_ID"),
        client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
        user_agent=os.getenv("REDDIT_USER_AGENT")
    )

def buscar_comentarios_recentes(subreddit_nome, limite=50):
    reddit = configurar_reddit()
    subreddit = reddit.subreddit(subreddit_nome)
    comentarios = []
    for comment in subreddit.comments(limit=limite):
        if comment.body and len(comment.body) > 15:
            comentarios.append({
                "id": comment.id,
                "texto": comment.body,
                "subreddit": subreddit_nome,
                "autor": str(comment.author)
            })
    return comentarios

def salvar_no_banco(lista_comentarios):
    conn = get_db_connection()
    cur = conn.cursor()
    for c in lista_comentarios:
        cur.execute("""
            INSERT INTO comentarios (reddit_id, texto, subreddit, autor) 
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (reddit_id) DO NOTHING
        """, (c['id'], c['texto'], c['subreddit'], c['autor']))
    conn.commit()
    cur.close()
    conn.close()
    print(f"{len(lista_comentarios)} comentários salvos/processados.")

if __name__ == "__main__":
    inicializar_banco()
    dados = buscar_comentarios_recentes("brasil", limite=50)
    salvar_no_banco(dados)