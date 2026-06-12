import streamlit as st
import google.generativeai as genai

# Configuração da Chave (Certifique-se de que ela está salva nos Secrets do Streamlit)
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

def tela_login():
    st.markdown("<h1 style='text-align: center;'>SISTEMA FINANCEIRO ADP</h1>", unsafe_allow_html=True)
    st.write("Insira suas credenciais para acessar o painel")
    
    user = st.text_input("Usuário")
    pwd = st.text_input("Senha", type="password")
    
    if st.button("🔓 Acessar Sistema"):
        if user == "jonatha.santos" and pwd == "admin123":
            st.session_state.logado = True
            st.rerun()
        else:
            st.error("Usuário ou Senha incorretos!")

def modulo_entrada():
    st.header("📥 Módulo de Entradas - IA")
    arquivo = st.file_uploader("Escolha uma nota fiscal ou recibo", type=["png", "jpg", "jpeg"])
    if arquivo and st.button("Processar com IA"):
        st.write("Processando...")

def main():
    if "logado" not in st.session_state:
        st.session_state.logado = False
    
    if not st.session_state.logado:
        tela_login()
    else:
        st.sidebar.title("MENU")
        opcao = st.sidebar.radio("Navegação", ["Entradas (IA)", "Sair"])
        if opcao == "Entradas (IA)":
            modulo_entrada()
        elif opcao == "Sair":
            st.session_state.logado = False
            st.rerun()

if __name__ == "__main__":
    main()
