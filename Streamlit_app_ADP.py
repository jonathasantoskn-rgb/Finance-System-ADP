import streamlit as st
import pandas as pd
import json
import os
import re
from google import genai

# Configuração da página Web
st.set_page_config(page_title="Sistema Integrante de Fluxo de Caixa", layout="wide")

# --- SEGURANÇA: Chave de API ---
# Recomendado salvar nos 'Secrets' do Streamlit Cloud como GEMINI_API_KEY
API_KEY = st.secrets.get("GEMINI_API_KEY", "AQ.Ab8RN6LCBRVJ-avkTB0qm-Mh6TLxUSADK00fhiYwU3OIlp6B7A")

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

# Caminho do banco de dados local (OneDrive)
PASTA_PROJETO = r"C:\Users\jonatha.santos\OneDrive - Kuehne+Nagel\Desktop\Projetos VS code"
CAMINHO_USUARIOS = os.path.join(PASTA_PROJETO, "usuarios.json")
CAMINHO_SAIDAS = os.path.join(PASTA_PROJETO, "saidas.csv")

# Garante que as pastas e arquivos existam
if not os.path.exists(PASTA_PROJETO):
    try: os.makedirs(PASTA_PROJETO)
    except: pass

if not os.path.exists(CAMINHO_USUARIOS):
    admin_padrao = {
        "jonatha.santos": {
            "nome": "Jonatha Santos",
            "email": "jonatha.santos.kn@gmail.com",
            "senha": "admin123",
            "perfil": "Administrador",
            "setor": "Logística / TI",
            "status": "Ativo"
        }
    }
    with open(CAMINHO_USUARIOS, "w", encoding="utf-8") as f:
        json.dump(admin_padrao, f, indent=4, ensure_ascii=False)


# --- FUNÇÕES DE CONTROLE DE SESSÃO E DADOS ---
if "logado" not in st.session_state:
    st.session_state.logado = False
if "dados_consolidados" not in st.session_state:
    st.session_state.dados_consolidados = []

def carregar_usuarios():
    if os.path.exists(CAMINHO_USUARIOS):
        with open(CAMINHO_USUARIOS, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def limpar_e_converter_valor(valor_texto):
    if not valor_texto: return 0.0
    try:
        texto_limpo = re.sub(r"[^\d.,]", "", str(valor_texto)).strip()
        if "," in texto_limpo and "." in texto_limpo:
            texto_limpo = texto_limpo.replace(".", "").replace(",", ".")
        elif "," in texto_limpo:
            texto_limpo = texto_limpo.replace(",", ".")
        return float(texto_limpo)
    except:
        return 0.0


# --- RECURSOS VISUAIS: TELA DE LOGIN ---
def tela_login():
    st.markdown("<h2 style='text-align: center;'>🔐 SISTEMA FINANCEIRO</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: gray;'>Insira suas credenciais para acessar o painel</p>", unsafe_allow_html=True)
    
    with st.form("Formulário de Login"):
        usuario = st.text_input("Usuário (Login)").strip().lower()
        senha = st.text_input("Senha", type="password").strip()
        botao_entrar = st.form_submit_button("🔓 Acessar Sistema")
        
        if botao_entrar:
            usuarios = carregar_usuarios()
            if usuario in usuarios and usuarios[usuario]["senha"] == senha:
                if usuarios[usuario].get("status", "Ativo") == "Inativo":
                    st.error("Acesso Bloqueado! Este usuário está inativo.")
                else:
                    st.session_state.logado = True
                    st.session_state.usuario_logado = usuario
                    st.session_state.perfil_logado = usuarios[usuario]["perfil"]
                    st.session_state.setor_logado = usuarios[usuario].get("setor", "Não Definido")
                    st.rerun()
            else:
                st.error("Usuário ou Senha incorretos!")


# --- CORPO PRINCIPAL DO APP ---
def main_app():
    # Barra Lateral (Sidebar) com Informações do Usuário
    st.sidebar.markdown(f"### 👤 {st.session_state.perfil_logado}")
    st.sidebar.text(f"Usuário: {st.session_state.usuario_logado}")
    st.sidebar.text(f"Setor: {st.session_state.setor_logado}")
    
    if st.sidebar.button("🚪 Sair do Sistema"):
        st.session_state.logado = False
        st.rerun()
        
    st.title("📑 Sistema Integrante de Fluxo de Caixa - IA & Gestão")
    
    # Define as abas disponíveis baseado no perfil do usuário
    abas_disponiveis = ["📥 Entradas (IA)", "📤 Saídas (Manual)"]
    if st.session_state.perfil_logado == "Administrador":
        abas_disponiveis.extend(["📊 Relatório Total", "⚙️ Gestão de Usuários"])
        
    aba_selecionada = st.tabs(abas_disponiveis)
    
    # ==========================================
    # ABA 1: MÓDULO DE ENTRADAS (IA)
    # ==========================================
    with aba_selecionada[0]:
        st.subheader("Módulo de Entradas - Consolidação de Recebimentos")
        
        sub_aba1, sub_aba2, sub_aba3 = st.tabs(["🔄 Processamento em Lote", "✍️ Lançamento Manual", "📊 Dados Extraídos"])
        
        with sub_aba1:
            arquivos_carregados = st.file_uploader("📂 Selecionar Imagens", type=["png", "jpg", "jpeg"], accept_multiple_files=True)
            
            if arquivos_carregados and st.button("🚀 Iniciar Leitura dos Comprovantes"):
                try:
                    client = genai.Client(api_key=API_KEY)
                    campos_prompt = "\n".join([f"- \"{campo}\"" for campo in CAMPOS_PARAMETRIZADOS])
                    
                    for arq in arquivos_carregados:
                        with st.spinner(f"🧠 Analisando {arq.name}..."):
                            bytes_img = arq.getvalue()
                            prompt = f"Analise o comprovante e extraia em JSON plano:\n{campos_prompt}"
                            mime = "image/png" if arq.name.lower().endswith(".png") else "image/jpeg"
                            
                            response = client.models.generate_content(
                                model='gemini-2.5-flash',
                                contents=[genai.types.Part.from_bytes(data=bytes_img, mime_type=mime), prompt]
                            )
                            
                            txt = response.text.strip().replace("```json", "").replace("```", "")
                            dados_json = json.loads(txt)
                            
                            reg = {campo: dados_json.get(campo, "") for campo in CAMPOS_PARAMETRIZADOS}
                            reg["Nome do Arquivo"] = arq.name
                            reg["Usuário Lançamento"] = st.session_state.usuario_logado
                            reg["Setor Lançamento"] = st.session_state.setor_logado
                            
                            st.session_state.dados_consolidados.append(reg)
                    st.success("Lote processado com sucesso!")
                except Exception as e:
                    st.error(f"Erro na API do Gemini: {e}")
                    
        with sub_aba2:
            with st.form("Cadastro Manual Entrada"):
                inputs_manual = {}
                for campo in CAMPOS_PARAMETRIZADOS:
                    inputs_manual[campo] = st.text_input(campo)
                
                if st.form_submit_button("💾 Gravar Entrada Manualmente"):
                    reg = {campo: inputs_manual[campo].strip() for campo in CAMPOS_PARAMETRIZADOS}
                    reg["Nome do Arquivo"] = "✍️ Lançamento Manual"
                    reg["Usuário Lançamento"] = st.session_state.usuario_logado
                    reg["Setor Lançamento"] = st.session_state.setor_logado
                    st.session_state.dados_consolidados.append(reg)
                    st.success("Adicionado com sucesso!")
                    
        with sub_aba3:
            # Dashboard Cards do Streamlit
            col1, col2 = st.columns(2)
            qtd_comprovantes = len(st.session_state.dados_consolidados)
            soma_total = sum([limpar_e_converter_valor(reg.get("Valor da Transação", 0)) for reg in st.session_state.dados_consolidados])
            
            col1.metric("TOTAL COMPROVANTES", qtd_comprovantes)
            col2.metric("VALOR TOTAL PROCESSADO", f"R$ {soma_total:,.2f}")
            
            if st.session_state.perfil_logado == "Administrador" and st.button("🗑️ Limpar Lote Atual"):
                st.session_state.dados_consolidados = []
                st.rerun()
                
            if st.session_state.dados_consolidados:
                df_entradas = pd.DataFrame(st.session_state.dados_consolidados)
                st.dataframe(df_entradas, use_container_width=True)

    # ==========================================
    # ABA 2: MÓDULO DE SAÍDAS
    # ==========================================
    with aba_selecionada[1]:
        st.subheader("Módulo de Saídas - Lançamento de Despesas")
        sub_saida1, sub_saida2 = st.tabs(["📝 Formulário de Cadastro", "📋 Histórico de Saídas"])
        
        with sub_saida1:
            with st.form("Formulário Saídas"):
                nome_saida = st.text_input("Nome Completo")
                email_saida = st.text_input("E-Mail")
                dept_saida = st.text_input("Departamento")
                setor_saida = st.text_input("Congregação / Setor")
                data_saida = st.text_input("Data Saída")
                motivo_saida = st.text_input("Motivo (Descrição)")
                valor_saida = st.text_input("Valor (R$)")
                especie_saida = st.text_input("Valor em Espécie (R$)")
                anexo_saida = st.file_uploader("📎 Anexar Recibo (Imagem/PDF)", type=["png", "jpg", "jpeg", "pdf"])
                
                if st.form_submit_button("💾 Registrar Lançamento de Saída"):
                    nome_anexo = anexo_saida.name if anexo_saida else "Nenhum arquivo"
                    nova_saida = {
                        "Nome Completo": nome_saida, "E-Mail": email_saida, "Departamento": dept_saida,
                        "Congregação_Setor": setor_saida, "Data Saída": data_saida, "Motivo": motivo_saida,
                        "Valor": valor_saida, "Valor em Especie": especie_saida, "Arquivo Comprovante": nome_anexo,
                        "Usuário Lançamento": st.session_state.usuario_logado, "Setor Lançamento": st.session_state.setor_logado
                    }
                    df_nova = pd.DataFrame([nova_saida])
                    df_nova.to_csv(CAMINHO_SAIDAS, mode='a', header=not os.path.exists(CAMINHO_SAIDAS), index=False, sep=";", encoding="utf-8-sig")
                    st.success("Lançamento de Saída registrado!")

        with sub_saida2:
            if os.path.exists(CAMINHO_SAIDAS):
                df_historico_saidas = pd.read_csv(CAMINHO_SAIDAS, sep=";", encoding="utf-8-sig")
                st.dataframe(df_historico_saidas, use_container_width=True)
            else:
                st.info("Nenhum histórico de saídas registrado localmente.")

    # ==========================================
    # ABAS DO ADMINISTRADOR
    # ==========================================
    if st.session_state.perfil_logado == "Administrador":
        with aba_selecionada[2]:
            st.subheader("📊 Relatórios Consolidados Globais")
            st.text("Visão geral construída a partir dos bancos de dados.")
            
        with aba_selecionada[3]:
            st.subheader("⚙️ Gestão de Usuários do Sistema")
            usuarios_cadastrados = carregar_usuarios()
            st.json(usuarios_cadastrados)

# --- EXECUÇÃO DO FLUXO DO APP ---
if __name__ == "__main__":
    if not st.session_state.logado:
        tela_login()
    else:
        main_app()
