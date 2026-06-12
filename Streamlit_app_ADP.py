import streamlit as st
import google.generativeai as genai

# Carrega a chave de forma segura
api_key = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=api_key)

def modulo_entrada():
    st.header("📥 Módulo de Entradas - IA")
    
    arquivo = st.file_uploader("Escolha uma nota fiscal ou recibo", type=["png", "jpg", "jpeg"])
    
    if arquivo and st.button("Processar com IA"):
        with st.spinner("IA analisando documento..."):
            try:
                model = genai.GenerativeModel('gemini-1.5-flash')
                bytes_data = arquivo.getvalue()
                
                prompt = "Extraia Valor, Data, Empresa e CNPJ deste documento. Retorne apenas JSON."
                
                response = model.generate_content([
                    prompt,
                    {"mime_type": "image/jpeg", "data": bytes_data}
                ])
                
                st.success("Dados extraídos com sucesso!")
                st.json(response.text)
            except Exception as e:
                st.error(f"Erro ao processar: {e}")
