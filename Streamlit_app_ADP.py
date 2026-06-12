import streamlit as st
import google.generativeai as genai
import pandas as pd

# Configuração da API Key (Certifique-se de que a chave está nos 'Secrets' do Streamlit)
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

def tela_login():
    st.markdown("<h1 style='text-align: center;'>🔐 SISTEMA FINANCEIRO ADP</h1>", unsafe_allow_html=True)
    user = st.text_input("Usuário")
    pwd = st.text_input("Senha", type="password")
    
    if st.button("Acessar Sistema"):
        if user == "jonatha.santos" and pwd == "admin123":
            st.session_state.logado = True
            st.rerun()
        else:
            st.error("Usuário ou Senha incorretos!")

def modulo_entrada():
    st.header("📥 Módulo de Entradas - IA")
    aba1, aba2 = st.tabs(["Processamento com IA", "Lançamento Manual"])
    
    with aba1:
        # Aceita imagens e PDF
        arquivo = st.file_uploader("Escolha nota fiscal ou recibo (JPG/PNG/PDF)", type=["png", "jpg", "jpeg", "pdf"])
        
        if arquivo and st.button("Processar com IA"):
            with st.spinner("IA analisando documento..."):
                try:
                    # Modelo mais estável e capaz
                    model = genai.GenerativeModel('gemini-1.5-pro')
                    bytes_data = arquivo.getvalue()
                    
                    # Define o tipo MIME correto
                    mime_type = "application/pdf" if arquivo.type == "application/pdf" else "image/jpeg"
                    
                    prompt = "Extraia o Valor Total, Data da emissão, Nome da empresa e CNPJ deste documento. Retorne apenas JSON puro."
                    
                    response = model.generate_content([
                        prompt,
                        {"mime_type": mime_type, "data": bytes_data}
                    ])
                    
                    st.success("Dados extraídos com sucesso!")
                    st.json(response.text)
                except Exception as e:
                    st.error(f"Erro ao processar: {e}")
                    
    with aba2:
        st.write("Formulário de Lançamento Manual em construção.")

def main():
    if "logado" not in st.session_state:
        st.session_state.logado = False
    
    if not st.session_state.logado:
        tela_login()
    else:
        st.sidebar.title("MENU ADP")
        opcao = st.sidebar.radio("Navegação", ["Entradas (IA)", "Sair"])
        
        if opcao == "Entradas (IA)":
            modulo_entrada()
        elif opcao == "Sair":
            st.session_state.logado = False
            st.rerun()

if __name__ == "__main__":
    main()
