import streamlit as st
import google.generativeai as genai

# Configuração da API
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
    arquivo = st.file_uploader("Escolha nota fiscal ou recibo (JPG/PNG/PDF)", type=["png", "jpg", "jpeg", "pdf"])
    
    if arquivo and st.button("Processar com IA"):
        with st.spinner("IA analisando documento..."):
            try:
                # Inicialização direta do modelo mais compatível
                model = genai.GenerativeModel('gemini-1.5-flash')
                bytes_data = arquivo.getvalue()
                mime_type = "application/pdf" if arquivo.type == "application/pdf" else "image/jpeg"
                
                prompt = "Extraia o Valor Total, Data, Empresa e CNPJ. Retorne apenas JSON puro."
                
                response = model.generate_content([
                    prompt,
                    {"mime_type": mime_type, "data": bytes_data}
                ])
                st.success("Dados extraídos!")
                st.json(response.text)
            except Exception as e:
                st.error(f"Erro ao processar: {e}")

def main():
    if "logado" not in st.session_state: st.session_state.logado = False
    if not st.session_state.logado: tela_login()
    else:
        if st.sidebar.button("Sair"):
            st.session_state.logado = False
            st.rerun()
        modulo_entrada()

if __name__ == "__main__":
    main()
