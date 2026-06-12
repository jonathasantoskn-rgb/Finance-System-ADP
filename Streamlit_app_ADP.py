import streamlit as st
import pandas as pd

# --- CONFIGURAÇÃO INICIAL ---
st.set_page_config(page_title="Sistema Financeiro ADP", layout="wide")

# Inicializa o estado de login
if "logado" not in st.session_state:
    st.session_state.logado = False
    st.session_state.usuario = None
    st.session_state.perfil = None

# --- FUNÇÕES DE MÓDULOS ---

def tela_login():
    st.markdown("<h1 style='text-align: center;'>SISTEMA FINANCEIRO ADP</h1>", unsafe_allow_html=True)
    st.write("Insira suas credenciais para acessar o painel")
    
    user = st.text_input("Usuário")
    pwd = st.text_input("Senha", type="password")
    
    if st.button("🔓 Acessar Sistema"):
        # Aqui você futuramente carregará os dados do JSON/Sheets
        if user == "jonatha.santos" and pwd == "admin123":
            st.session_state.logado = True
            st.session_state.usuario = user
            st.session_state.perfil = "Administrador"
            st.rerun()
        else:
            st.error("Usuário ou Senha incorretos!")

def modulo_entrada():
    st.header("📥 Módulo de Entradas - IA")
    tab1, tab2 = st.tabs(["Processamento em Lote", "Lançamento Manual"])
    with tab1:
        st.write("Aqui virá a lógica de leitura com Gemini")
    with tab2:
        st.write("Formulário manual")

def modulo_saida():
    st.header("📤 Módulo de Saídas")
    # Aqui virá o formulário que criamos anteriormente
    st.write("Formulário de lançamento de despesas")

# --- NAVEGAÇÃO PRINCIPAL ---
def main():
    if not st.session_state.logado:
        tela_login()
    else:
        st.sidebar.title(f"👤 {st.session_state.perfil}")
        st.sidebar.write(f"Usuário: {st.session_state.usuario}")
        
        menu = st.sidebar.radio("MENU NAVEGAÇÃO", 
                                ["Entradas (IA)", "Saídas (Manual)", "Relatórios", "Gestão de Usuários"])
        
        if menu == "Entradas (IA)":
            modulo_entrada()
        elif menu == "Saídas (Manual)":
            modulo_saida()
        elif menu == "Relatórios":
            st.header("📊 Relatório Total")
        elif menu == "Gestão de Usuários":
            st.header("⚙️ Gestão de Usuários")
            
        if st.sidebar.button("Sair"):
            st.session_state.logado = False
            st.rerun()

if __name__ == "__main__":
    main()
