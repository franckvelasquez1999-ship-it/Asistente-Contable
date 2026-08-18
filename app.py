import base64

def procesar_comprobante_con_ia_vision(archivo_bytes, es_imagen=False):
    if not api_key:
        return None
    try:
        client = Groq(api_key=api_key)
        
        prompt_instrucciones = """
        Eres un extractor de facturas de Perú de alta precisión con visión artificial. Analiza visualmente el documento proporcionado y extrae EXCLUSIVAMENTE los siguientes campos en un formato JSON limpio, sin textos adicionales, sin saludos y sin bloques de código ```json ```:
        {
            "ruc_emisor": "Solo el número de RUC de 11 dígitos del proveedor",
            "razon_social": "Nombre de la empresa proveedora",
            "fecha_emision": "Fecha en formato AAAA-MM-DD",
            "serie": "Serie del comprobante (ejemplo: F001)",
            "numero": "Número correlativo",
            "total": 0.00,
            "categoria_gasto": "Una categoría contable corta de 2 a 4 palabras (ejemplo: Útiles de Oficina, Combustibles, Servicios Básicos)"
        }
        """
        
        # Codificamos el archivo en Base64 para que la IA con visión pueda "ver" la foto
        base64_image = base64.b64encode(archivo_bytes).decode('utf-8')
        
        # Llamamos al modelo Llama de Visión de Groq
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt_instrucciones},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}",
                            },
                        },
                    ],
                }
            ],
            model="llama-3.2-11b-vision-preview",
            temperature=0.1
        )
        
        resultado = chat_completion.choices.message.content.strip()
        resultado_limpio = re.sub(r'```json\s*|\s*```', '', resultado)
        return json.loads(resultado_limpio)
    except Exception:
        return None
