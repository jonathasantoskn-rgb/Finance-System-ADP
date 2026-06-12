import streamlit as st
import pandas as pd
import json
import os
import re
from google import genai
from google.genai import types

# Configuração da página Web
st.set_page_config(page_title="Sistema Integrante de Fluxo de Caixa", layout="wide")

# --- SEGURANÇA: Chave de API ---
API_KEY = st.secrets.get("GEMINI_API_KEY", "AQ.Ab8RN6LCBRVJ-avkTB0qm-Mh6TLxUSADK00fhiYwU3OIlp6B7A")

CAMPOS_PARAMETRIZADOS = [
    "Data da Transação", "Nome do Pagador", "CPF do Pagador", "ID da Transação",
    "Valor da Transação", "Nome do Destinatário", "Tipo de Transferência",
    "CNPJ do Destinatário", "Instituição do Destinatário", "Chave Pix do Recebedor"
]

# Caminhos do banco de dados (OneDrive)
PASTA_PROJETO = r"C:\Users\jonatha.santos\OneDrive - Kuehne+Nagel\Desktop\Projetos VS code"
CAMINHO_USUARIOS = os.path.join(PASTA_PROJETO, "usuarios.json")
CAMINHO_SAIDAS = os.path.join(PASTA_PROJETO, "saidas.csv")

# Garante a existência do diretório
if not os.path.exists(PASTA_PROJETO):
    try: os.makedirs(PASTA_PROJETO)
    except: pass

# --- FUNÇÕES DE PERSISTÊNCIA (USUÁRIOS) ---
def carregar_usuarios():
    if os.path.exists(CAMINHO_USUARIOS):
        try:
            with open(CAMINHO_USUARIOS, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return obter_admin_padrao()
    else:
        usuarios = obter_admin_padrao()
        salvar_usuarios(usuarios)
        return usuarios

def obter_admin_padrao():
    return {
        "jonatha.santos": {
            "nome": "Jonatha Santos",
            "email": "jonatha.santos.kn@gmail.com",
            "senha": "admin123",
            "perfil": "Administrador",
            "setor": "Logística / TI",
            "status": "Ativo"
        }
    }

def salvar_usuarios(usuarios):
    try:
        with open(CAMINHO_USUARIOS, "w", encoding="utf-8") as f:
            json.dump(usuarios, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        st.error(f"Erro ao salvar alterações de usuários: {e}")
        return False

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


# --- CONTROLE DE SESSÃO ---
if "logado" not in st.session_state:
    st.session_state.logado = False
if "dados_consolidados" not in st.session_state:
    st.session_state.dados_consolidados = []


# --- TELA DE LOGIN ---
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
    # Barra Lateral
    st.sidebar.markdown(f"### 👤 {st.session_state.perfil_logado}")
    st.sidebar.text(f"Usuário: {st.session_state.usuario_logado}")
    st.sidebar.text(f"Setor: {st.session_state.setor_logado}")
    
    if st.sidebar.button("🚪 Sair do Sistema"):
        st.session_state.logado = False
        st.rerun()
        
    st.title("📑 Sistema Integrante de Fluxo de Caixa - IA & Gestão")
    
    # Abas dinâmicas com base no perfil
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
            st.markdown("### Escolha uma nota fiscal ou recibo (JPG/PNG/PDF)")
            arquivos_carregados = st.file_uploader("📂 Selecionar Arquivos", type=["png", "jpg", "jpeg", "pdf"], accept_multiple_files=True, label_visibility="collapsed")
            
            if arquivos_carregados and st.button("🚀 Processar com IA"):
                try:
                    client = genai.Client(api_key=API_KEY)
                    campos_prompt = "\n".join([f"- \"{campo}\"" for campo in CAMPOS_PARAMETRIZADOS])
                    prompt = f"Analise o comprovante enviado e extraia as informações estritamente no formato JSON plano:\n{campos_prompt}"
                    
                    for arq in arquivos_carregados:
                        with st.spinner(f"🧠 Analisando {arq.name}..."):
                            bytes_arquivo = arq.getvalue()
                            nome_minusculo = arq.name.lower()
                            
                            if nome_minusculo.endswith(".png"): mime_type = "image/png"
                            elif nome_minusculo.endswith((".jpg", ".jpeg")): mime_type = "image/jpeg"
                            elif nome_minusculo.endswith(".pdf"): mime_type = "application/pdf"
                            else: mime_type = "application/octet-stream"
                            
                            response = client.models.generate_content(
                                model='gemini-2.5-flash',
                                contents=[types.Part.from_bytes(data=bytes_arquivo, mime_type=mime_type), prompt]
                            )
                            
                            txt = response.text.strip()
                            if "
http://googleusercontent.com/immersive_entry_chip/0
http://googleusercontent.com/immersive_entry_chip/1

### O que essa alteração traz de novo?
* **Segurança de Login:** Se você marcar um usuário como `"Inativo"` no painel, ele será imediatamente bloqueado na tela de autenticação, impedindo o acesso à plataforma.
* **Isolamento de Funcionalidades:** Usuários criados com a role `"Operador"` não visualizarão as abas de *Relatório Total* e nem terão acesso a este painel administrativo de usuários.
* **Persistência Compartilhada:** Todo cadastro criado gera uma modificação direta no arquivo `usuarios.json` dentro da pasta local sincronizada com o OneDrive.
