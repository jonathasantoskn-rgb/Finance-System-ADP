def modulo_entrada():
    st.header("📥 Módulo de Entradas - IA")
    arquivo = st.file_uploader("Escolha uma nota fiscal ou recibo", type=["png", "jpg", "jpeg"])
    
    if arquivo and st.button("Processar com IA"):
        with st.spinner("IA analisando documento..."):
            try:
                # 1. Preparar o modelo
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                # 2. Ler os bytes da imagem
                bytes_data = arquivo.getvalue()
                
                # 3. Enviar para a IA
                prompt = "Extraia o valor total, a data da nota e o nome da empresa. Retorne em formato JSON."
                response = model.generate_content([
                    prompt,
                    {"mime_type": "image/jpeg", "data": bytes_data}
                ])
                
                # 4. Exibir o resultado
                st.success("Dados extraídos com sucesso!")
                st.json(response.text) # Aqui você verá o JSON que a IA criou
                
            except Exception as e:
                st.error(f"Erro ao processar: {e}")
