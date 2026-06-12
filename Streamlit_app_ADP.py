import streamlit as st
import google.generativeai as genai
import json
import re

# Configuração da Chave
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

def limpar_json(texto):
    """Remove marcações de markdown do JSON se a IA enviar"""
    texto_limpo = re.sub(r"```json\s*", "", texto)
    texto_limpo = re.sub(r"```\s*", "", texto_limpo)
    return texto_limpo.strip()

def modulo_entrada():
    st.header("📥 Módulo de Entradas - IA")
    arquivo = st.file_uploader("Escolha nota fiscal ou recibo (JPG/PNG/PDF)", type=["png", "jpg", "jpeg", "pdf"])
    
    if arquivo and st.button("Processar com IA"):
        with st.spinner("IA analisando documento..."):
            try:
                model = genai.GenerativeModel('gemini-1.5-flash')
                bytes_data = arquivo.getvalue()
                mime_type = "application/pdf" if arquivo.type == "application/pdf" else "image/jpeg"
                
                # Prompt instruindo a IA a responder estritamente em um formato JSON específico
                prompt = (
                    "Analise o documento e extraia os seguintes dados no formato JSON abaixo. "
                    "Se não encontrar algum campo, deixe o valor como vazio (string vazia '').\n"
                    "Formatos esperados:\n"
                    "{\n"
                    "  'valor_total': '000.00' (apenas números e ponto),\n"
                    "  'data_emissao': 'DD/MM/AAAA',\n"
                    "  'empresa': 'Nome da Empresa',\n"
                    "  'cnpj': '00.000.000/0000-00'\n"
                    "}"
                )
                
                response = model.generate_content([
                    prompt,
                    {"mime_type": mime_type, "data": bytes_data}
                ])
                
                # Tratamento do retorno da IA
                texto_resposta = limpar_json(response.text)
                dados = json.loads(texto_resposta)
                
                st.success("Dados extraídos com sucesso!")
                
                # --- OUTROS PARÂMETROS: EXIBIÇÃO E VALIDAÇÃO ---
                st.subheader("📋 Conferência de Dados")
                
                # Criando campos de texto para o usuário conferir e poder editar se a IA errar
                empresa = st.text_input("Nome da Empresa", value=dados.get("empresa", ""))
                cnpj = st.text_input("CNPJ", value=dados.get("cnpj", ""))
                data_emissao = st.text_input("Data de Emissão", value=dados.get("data_emissao", ""))
                valor_total = st.text_input("Valor Total (R$)", value=dados.get("valor_total", ""))
                
                # Botão final para salvar (aqui conectaremos o banco de dados ou Google Sheets)
                if st.button("Confirmar e Salvar no Sistema"):
                    st.success(f"Lançamento de R$ {valor_total} da empresa {empresa} pronto para ser salvo!")
                    # TODO: Inserir integração com Google Sheets aqui
                    
            except json.JSONDecodeError:
                st.error("Erro ao processar a resposta da IA. Ela não devolveu um JSON válido.")
                st.text("Resposta bruta da IA:")
                st.code(response.text)
            except Exception as e:
                st.error(f"Erro na API: {e}")

def main():
    modulo_entrada()

if __name__ == "__main__":
    main()
