import streamlit as st
import os
import csv
from coletor import buscar_comentarios_recentes
from agente import analisar_comentario

st.set_page_config(page_title="Jarvis Científico", layout="wide")
st.title("🧪 Jarvis: Laboratório de Análise de Discurso")

if 'preconceituoso' not in st.session_state: st.session_state.preconceituoso = 0
if 'nao_preconceituoso' not in st.session_state: st.session_state.nao_preconceituoso = 0

sub = st.text_input("Subreddit:", value="brasil")
qtd = st.slider("Amostragem (Comentários):", 10, 200, 50)

col1, col2, col3 = st.columns(3)
m_proc = col1.metric("Processados", 0)
m_prec = col2.metric("Preconceituosos", 0)
m_neut = col3.metric("Não Preconceituosos", 0)

if st.button("Iniciar Coleta e Análise"):
    comentarios = buscar_comentarios_recentes(sub, limite=qtd)
    
    if not comentarios:
        st.error("Erro na busca (verifique suas chaves de API do Reddit).")
    else:
        progresso_bar = st.progress(0)
        
        for i, c in enumerate(comentarios):
            if len(c['texto']) < 20: continue
            
            # Análise
            res = analisar_comentario(c['texto'])
            
            # Salvamento Seguro
            with open("dataset_final.csv", "a", newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                # Verifica se o arquivo está vazio para escrever o cabeçalho
                if os.stat("dataset_final.csv").st_size == 0:
                    writer.writerow(['texto', 'classificacao', 'justificativa'])
                writer.writerow([c['texto'], res['classificacao'], res['justificativa']])
            
            # Atualizar Métricas
            if res['classificacao'] == "Preconceituoso": st.session_state.preconceituoso += 1
            if res['classificacao'] == "Não Preconceituoso": st.session_state.nao_preconceituoso += 1
            
            # UI
            progresso_bar.progress((i + 1) / len(comentarios))
            m_proc.metric("Processados", i + 1)
            m_prec.metric("Preconceituosos", st.session_state.preconceituoso)
            m_neut.metric("Não Preconceituosos", st.session_state.nao_preconceituoso)

        st.success("🎉 Coleta Finalizada! Dados exportados.")