import psycopg2
import google.generativeai as genai
import json
import os
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
modelo = genai.GenerativeModel('gemini-3.5-flash')

def get_db_connection():
    return psycopg2.connect(dbname="postgres", user="postgres", password="senha123", host="localhost", port="5432")

def processar_fila():
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Busca apenas os que ainda não foram analisados
    cur.execute("SELECT id, texto FROM comentarios WHERE status = 'pendente' LIMIT 15")
    pendentes = cur.fetchall()
    
    prompt_sistema = """Analise o comentário abaixo buscando preconceito. 
    Responda APENAS com JSON: {"classificacao": "...", "justificativa": "..."}"""

    for id_comentario, texto in pendentes:
        try:
            resposta = modelo.generate_content(f"{prompt_sistema}\n\nComentário: {texto}")
            
            # Limpeza do texto para pegar apenas o JSON
            texto_limpo = resposta.text.replace("```json", "").replace("```", "").strip()
            dados_json = json.loads(texto_limpo)
            
            cur.execute("""
                UPDATE comentarios 
                SET classificacao = %s, justificativa = %s, status = 'finalizado' 
                WHERE id = %s
            """, (dados_json['classificacao'], dados_json['justificativa'], id_comentario))
            
            conn.commit()
            print(f"Sucesso: ID {id_comentario}")
            
        except Exception as e:
            print(f"Erro no comentário {id_comentario}: {e}")
            break # Para se atingir limite de cota
            
    cur.close()
    conn.close()

if __name__ == "__main__":
    processar_fila()