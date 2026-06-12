import streamlit as st
import pandas as pd
import json
import os
import re
from google import genai

# Configuração da página Web
st.set_page_config(page_title="Sistema Financeiro - IA & Gestão",
                   page_icon="📑", layout="wide")

API_KEY = "AQ.Ab8RN6LCBRVJ-avkTB0qm-Mh6TLxUSADK00fhiYwU3OIlp6B7A"

CAMPOS_PARAMETRIZADOS = [
    "Data da Transação", "Nome do Pagador", "CPF do Pagador", "ID da Transação",
    "Valor da Transação", "Nome do Destinatário", "Tipo de Transferência",
    "CNPJ do Destinatário", "Instituição do Destinatário", "Chave Pix do Recebedor"
]

COLUNAS_SAIDAS = [
    "Nome Completo", "E-Mail", "Departamento", "Congregação_Setor",
    "Data Saída", "Motivo", "Valor", "Valor em Especie", "Arquivo Comprovante",
    "Usuário Lançamento", "Setor Lançamento"
]

# Definição de caminhos (Para teste local, mantive sua pasta. Na nuvem, usaremos caminhos relativos)
PASTA_PROJETO = r"C:\Users\jonatha.santos\OneDrive - Kuehne+Nagel\Desktop\Projetos VS code"
CAMINHO_USUARIOS = os.path.join(PASTA_PROJETO, "usuarios.json")
CAMINHO_SAIDAS = os.path.join(PASTA_PROJETO, "saidas.csv")

# Inicialização do Estado da Sessão (Guarda se o usuário está logado entre os cliques)
if "logado" not in st.session_state:
    st.session_state.logado = False
    st.session_state.usuario = None
    st.session_state.perfil = None
    st.session_state.setor = None
if "dados_consolidados" not in st.session_state:
    st.session_state.dados_consolidados = []


def limpar_e_converter_valor(valor_texto):
    if not valor_texto:
        return 0.0
    try:
        texto_limpo = re.sub(r"[^\d.,]", "", str(valor_texto)).strip()
        if "," in texto_limpo and "." in texto_limpo:
            texto_limpo = texto_limpo.replace(".", "").replace(",", ".")
        elif "," in texto_limpo:
            texto_limpo = texto_limpo.replace(",", ".")
        return float(texto_limpo)
    except:
        return 0.0


# ==========================================
# RECORTE DA TELA DE LOGIN
# ==========================================
if not st.session_state.logado:
    st.markdown("<h1 style='text-align: center;'>📑 Sistema Integrante de Fluxo de Caixa</h1>",
                unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #64748b;'>Insira suas credenciais para acessar o painel web</p>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        with st.form("form_login"):
            usuario_input = st.text_input("Usuário (Login)").strip().lower()
            senha_input = st.text_input("Senha", type="password").strip()
            botao_entrar = st.form_submit_button(
                "🔓 Acessar Sistema", use_container_width=True)

            if botao_entrar:
                if os.path.exists(CAMINHO_USUARIOS):
                    with open(CAMINHO_USUARIOS, "r", encoding="utf-8") as f:
                        usuarios = json.load(f)
                    if usuario_input in usuarios and usuarios[usuario_input]["senha"] == senha_input:
                        if usuarios[usuario_input].get("status", "Ativo") == "Inativo":
                            st.error(
                                "Usuário Inativo. Contate o administrador.")
                        else:
                            st.session_state.logado = True
                            st.session_state.usuario = usuario_input
                            st.session_state.perfil = usuarios[usuario_input]["perfil"]
                            st.session_state.setor = usuarios[usuario_input].get(
                                "setor", "Logística")
                            st.rerun()
                    else:
                        st.error("Usuário ou Senha incorretos.")
                else:
                    st.error("Arquivo de usuários não encontrado.")
    st.stop()

# ==========================================
# AMBIENTE PRINCIPAL (PÓS-LOGIN)
# ==========================================

# Barra Lateral (Menu)
st.sidebar.title("Navegação")
st.sidebar.markdown(
    f"👤 **{st.session_state.perfil}**\n({st.session_state.usuario})")
st.sidebar.write(f"🏢 Setor: {st.session_state.setor}")

paginas = ["📥 Entradas (IA)", "📤 Saídas (Manual)", "📊 Relatório Total"]
if st.session_state.perfil == "Administrador":
    paginas.append("⚙️ Gestão de Usuários")

opcao_menu = st.sidebar.radio("Selecione o Módulo:", paginas)

if st.sidebar.button("🚪 Sair do Sistema"):
    st.session_state.logado = False
    st.rerun()

# --- MÓDULO 1: ENTRADAS (IA) ---
if opcao_menu == "📥 Entradas (IA)":
    st.title("Módulo de Entradas - Consolidação via IA")

    aba_lote, aba_manual, aba_dash = st.tabs(
        ["🔄 Processamento em Lote", "✍️ Lançamento Manual", "📊 Dashboard"])

    with aba_lote:
        arquivos_carregados = st.file_uploader("Selecione os Comprovantes", type=[
                                               "png", "jpg", "jpeg"], accept_multiple_files=True)
        if arquivos_carregados and st.button("🚀 Iniciar Leitura com Gemini"):
            try:
                client = genai.Client(api_key=API_KEY)
                campos_prompt = "\n".join(
                    [f"- \"{campo}\"" for campo in CAMPOS_PARAMETRIZADOS])

                progresso = st.progress(0)
                for idx, arq in enumerate(arquivos_carregados):
                    st.write(f"Lendo: {arq.name}...")
                    bytes_img = arq.read()
                    prompt = f"Analise o comprovante e extraia em JSON plano:\n{campos_prompt}"

                    mime = "image/png" if arq.name.endswith(
                        ".png") else "image/jpeg"
                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=[genai.types.Part.from_bytes(
                            data=bytes_img, mime_type=mime), prompt]
                    )

                    txt = response.text.strip().replace("```json", "").replace("```", "")
                    dados_json = json.loads(txt)

                    reg = {campo: dados_json.get(campo, "")
                           for campo in CAMPOS_PARAMETRIZADOS}
                    reg["Nome do Arquivo"] = arq.name
                    reg["Usuário Lançamento"] = st.session_state.usuario
                    reg["Setor Lançamento"] = st.session_state.setor
                    st.session_state.dados_consolidados.append(reg)

                    progresso.progress((idx + 1) / len(arquivos_carregados))
                st.success("Todos os arquivos foram processados!")
            except Exception as e:
                st.error(f"Erro na API do Gemini: {e}")

    with aba_manual:
        with st.form("form_manual_entrada"):
            inputs = {}
            for campo in CAMPOS_PARAMETRIZADOS:
                inputs[campo] = st.text_input(campo)
            if st.form_submit_button("💾 Gravar Entrada Manualmente"):
                inputs["Nome do Arquivo"] = "✍️ Lançamento Manual"
                inputs["Usuário Lançamento"] = st.session_state.usuario
                inputs["Setor Lançamento"] = st.session_state.setor
                st.session_state.dados_consolidados.append(inputs)
                st.success("Adicionado com sucesso!")

    with aba_dash:
        df_entradas = pd.DataFrame(st.session_state.dados_consolidados)

        if not df_entradas.empty:
            soma_total = sum([limpar_e_converter_valor(val)
                             for val in df_entradas.get("Valor da Transação", [0])])

            c1, c2 = st.columns(2)
            c1.metric("TOTAL COMPROVANTES", len(df_entradas))
            c2.metric("VALOR TOTAL PROCESSADO", f"R$ {soma_total:,.2f}")

            st.dataframe(df_entradas, use_container_width=True)
            if st.button("🗑️ Limpar Lote Atual"):
                st.session_state.dados_consolidados = []
                st.rerun()
        else:
            st.info("Nenhum dado extraído neste lote.")

# --- MÓDULO 2: SAÍDAS ---
elif opcao_menu == "📤 Saídas (Manual)":
    st.title("Módulo de Saídas - Registro de Despesas")

    aba_cad, aba_hist = st.tabs(
        ["📝 Formulário de Cadastro", "📋 Histórico de Saídas"])

    with aba_cad:
        with st.form("form_saida"):
            nome = st.text_input("Nome Completo")
            email = st.text_input("E-Mail")
            dept = st.text_input("Departamento")
            cong = st.text_input("Congregação / Setor")
            data_s = st.text_input("Data Saída")
            motivo = st.text_input("Motivo (Descrição)")
            valor = st.text_input("Valor (R$)")
            especie = st.text_input("Valor em Espécie (R$)")

            if st.form_submit_button("💾 Registrar Lançamento de Saída"):
                nova_saida = {
                    "Nome Completo": nome, "E-Mail": email, "Departamento": dept, "Congregação_Setor": cong,
                    "Data Saída": data_s, "Motivo": motivo, "Valor": valor, "Valor em Especie": especie,
                    "Arquivo Comprovante": "", "Usuário Lançamento": st.session_state.usuario, "Setor Lançamento": st.session_state.setor
                }
                df_nova = pd.DataFrame([nova_saida])
                if os.path.exists(CAMINHO_SAIDAS):
                    df_antigo = pd.read_csv(
                        CAMINHO_SAIDAS, sep=";", encoding="utf-8-sig")
                    df_final = pd.concat(
                        [df_antigo, df_nova], ignore_index=True)
                else:
                    df_final = df_nova
                df_final.to_csv(CAMINHO_SAIDAS, index=False,
                                sep=";", encoding="utf-8-sig")
                st.success("Saída gravada com sucesso!")

    with aba_hist:
        if os.path.exists(CAMINHO_SAIDAS):
            df_s = pd.read_csv(CAMINHO_SAIDAS, sep=";", encoding="utf-8-sig")
            st.dataframe(df_s, use_container_width=True)
        else:
            st.info("Nenhuma saída registrada ainda.")

# --- MÓDULO 3: RELATÓRIO TOTAL ---
elif opcao_menu == "📊 Relatório Total":
    st.title("Relatório Consolidado Total de Fluxo")

    df_ent = pd.DataFrame(st.session_state.dados_consolidados)
    df_sai = pd.read_csv(CAMINHO_SAIDAS, sep=";",
                         encoding="utf-8-sig") if os.path.exists(CAMINHO_SAIDAS) else pd.DataFrame()

    st.subheader("Entradas")
    st.dataframe(df_ent, use_container_width=True)

    st.subheader("Saídas")
    st.dataframe(df_sai, use_container_width=True)

    v_ent = sum([limpar_e_converter_valor(v)
                for v in df_ent["Valor da Transação"]]) if not df_ent.empty else 0.0
    v_sai = sum([limpar_e_converter_valor(v)
                for v in df_sai["Valor"]]) if not df_sai.empty else 0.0
    saldo = v_ent - v_sai

    st.metric("SALDO FINAL CONSOLIDADO",
              f"R$ {saldo:,.2f}", delta=f"{saldo:,.2f}")

# --- MÓDULO 4: GESTÃO DE USUÁRIOS ---
elif opcao_menu == "⚙️ Gestão de Usuários":
    st.title("Painel Administrativo de Usuários")
    if os.path.exists(CAMINHO_USUARIOS):
        with open(CAMINHO_USUARIOS, "r", encoding="utf-8") as f:
            u_data = json.load(f)
        st.json(u_data)
