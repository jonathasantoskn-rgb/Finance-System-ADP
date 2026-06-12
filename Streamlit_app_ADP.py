import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json

# --- CONFIGURAÇÃO DA CONEXÃO COM GOOGLE SHEETS ---
def conectar_sheets():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    
    # Carrega as credenciais seguras do painel "Secrets" do Streamlit
    creds_dict = json.loads(st.secrets["gcp_service_account"])
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    
    # ID da sua planilha (Extraído do link que você forneceu)
    sheet = client.open_by_key("1gZbKfzeXmb9oP--5rOyFF2VFNwZrDx3Vv_EwX1DP2Gc").sheet1
    return sheet

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Sistema Financeiro ADP", layout="wide")
st.title("💰 Sistema Financeiro ADP")

# --- FORMULÁRIO DE LANÇAMENTO ---
with st.form("form_saida"):
    st.subheader("Registrar Nova Saída")
    col1, col2 = st.columns(2)
    
    with col1:
        nome = st.text_input("Nome Completo")
        email = st.text_input("E-mail")
        depto = st.selectbox("Departamento", ["TI", "Financeiro", "RH", "Operações"])
    
    with col2:
        setor = st.text_input("Congregação / Setor")
        data = st.date_input("Data da Saída")
        valor = st.number_input("Valor (R$)", min_value=0.0, format="%.2f")
    
    motivo = st.text_area("Motivo")
    submit = st.form_submit_button("Salvar no Google Sheets")

# --- LÓGICA DE ENVIO ---
if submit:
    if nome and valor > 0:
        try:
            sheet = conectar_sheets()
            # Dados a serem salvos (deve coincidir com as colunas da sua planilha)
            dados = [nome, email, depto, setor, str(data), motivo, valor]
            sheet.append_row(dados)
            st.success("Dados enviados com sucesso para a planilha!")
        except Exception as e:
            st.error(f"Erro ao salvar: {e}")
    else:
        st.warning("Por favor, preencha o Nome e o Valor.")

# --- VISUALIZAÇÃO DOS DADOS ---
if st.checkbox("Exibir dados da planilha"):
    try:
        sheet = conectar_sheets()
        # Converte a planilha em um DataFrame do Pandas
        dados = sheet.get_all_records()
        if dados:
            df = pd.DataFrame(dados)
            st.dataframe(df)
        else:
            st.info("A planilha está vazia.")
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
