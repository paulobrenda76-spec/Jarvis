import os
import json
import time
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
modelo = genai.GenerativeModel('gemini-3.5-flash')

PROMPT_SISTEMA = """
Você é um especialista em linguística forense e moderação de conteúdo.

Analise o comentário procurando preconceitos explícitos ou implícitos.

Considere:
- contexto linguístico;
- ironia;
- sarcasmo;
- humor;
- estereótipos;
- dog whistles;
- generalizações;
- linguagem discriminatória;
- intenção aparente;
- possíveis interpretações alternativas.

Não presuma preconceito quando não houver evidências suficientes.

Retorne SOMENTE um JSON válido:

{
    "classificacao": "Preconceituoso" | "Não Preconceituoso" | "Inconclusivo",
    "confianca": 0.0,
    "tipo_preconceito": [],
    "indicadores": [],
    "justificativa": ""
}

Onde:

- classificacao: resultado final.
- confianca: valor entre 0 e 1.
- tipo_preconceito: lista contendo possíveis categorias, como:
  ["racismo", "sexismo", "homofobia", "xenofobia", "capacitismo", "etarismo", "transfobia", "religioso", "outro"].
- indicadores: liste os elementos encontrados, como:
  ["ironia", "estereótipo", "generalização", "insinuação", "linguagem ofensiva", "dog whistle", "sarcasmo"].
- justificativa: explique de forma objetiva por que chegou à conclusão.
"""

def analisar_comentario(texto):
    # Tentativa com espera progressiva
    for tentativa in range(5):
        try:
            resposta = modelo.generate_content(f"{PROMPT_SISTEMA}\n\nComentário:\n{texto}")
            texto_limpo = resposta.text.strip().replace("```json", "").replace("```", "").strip()
            return json.loads(texto_limpo)
        
        except Exception as e:
            # Se for limite de cota (429), espera mais tempo
            if "429" in str(e):
                print("Limite atingido. Aguardando 60s...")
                time.sleep(60) 
            else:
                time.sleep(5)
            continue
            
    return {"classificacao": "Inconclusivo", "justificativa": "Falha na API: Cota excedida."}