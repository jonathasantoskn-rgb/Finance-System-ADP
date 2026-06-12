import streamlit as st
import google.generativeai as genai
import pandas as pd

# Configuração da Chave de API de forma segura
# (Lembre-se de adicionar a chave no painel "Secrets" do Streamlit Cloud)
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# --- FUNÇÕES DE MÓDULOS ---

def tela_login():
    st.markdown("<h1 style='text-align: center;'>🔐 SISTEMA FINANCEIRO ADP</h1>", unsafe_allow_html=True)
    user = st.text_input("Usuário")
    pwd = st.text_input("Senha", type="password")
    
    if st.button("Acessar Sistema"):
        # Exemplo de credencial (em breve podemos usar um banco de dados)
        if user == "jonatha.santos" and pwd == "admin123":
            st.session_state.logado = True
            st.rerun()
        else:
            st.error("Usuário ou Senha incorretos!")

def modulo_entrada():
    st.header("📥 Módulo de Entradas - IA")
    aba1, aba2 = st.tabs(["Processamento com IA", "Lançamento Manual"])
    
    with aba1:
        arquivo = st.file_uploader("Escolha uma nota fiscal ou recibo", type=["png", "jpg", "jpeg"])
        if arquivo and st.button("Processar com IA"):
            with st.spinner("IA analisando documento..."):
                try:
                   model = genai.GenerativeModel('gemini-1.5-flash-latest')
                    bytes_data = arquivo.getvalue()
                    
                    prompt = "Extraia Valor Total, Data da emissão, Nome da empresa e CNPJ deste documento. Retorne apenas JSON puro."
                    
                    response = model.generate_content([
                        prompt,
                        {"mime_type": "image/jpeg", "data": bytes_data}
                    ])
                    
                    st.success("Dados extraídos!")
                    st.json(response.text)
                except Exception as e:
                    st.error(f"Erro ao processar: {e}")
                    
    with aba2:
        st.write("Formulário de Lançamento Manual (Em breve)")

# --- ESTRUTURA PRINCIPAL ---

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
