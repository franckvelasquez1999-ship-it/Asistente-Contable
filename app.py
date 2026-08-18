import streamlit as st
import pandas as pd
import xml.etree.ElementTree as ET
import io
import json
import re
import requests
import base64
import random
from PIL import Image
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

# 1. Configuración de la página
st.set_page_config(page_title="Extractor SIRE - Estilo Yape", layout="wide")

# 2. INYECCIÓN DE DISEÑO INTERFAZ YAPE PREMIUM
st.markdown("""
    <style>
    /* Fondo morado Yape oficial de la aplicación */
    .stApp { 
        background-color: #742284 !important; 
        font-family: 'Inter', sans-serif; 
    }
    
    /* Configuración de textos fijos */
    h1, h2, h3, h4, .stMarkdown p, p, span, label { 
        color: #ffffff !important; 
    }
    
    /* Zona de carga de archivos (Drag & Drop) */
    .stFileUploader { 
        background-color: #8c339c !important; 
        border: 2px dashed #00e6b3 !important; 
        border-radius: 20px !important; 
        padding: 25px !important; 
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2) !important; 
    }

    /* CONTENEDOR DE LA CONSTANCIA ESTILO VOUCHER YAPE */
    .yape-container {
        max-width: 420px;
        background: #742284;
        border-radius: 30px;
        padding: 0px;
        margin: 20px auto;
        box-shadow: 0 15px 40px rgba(0,0,0,0.4);
        text-align: center;
        overflow: hidden;
    }
    
    /* Cabecera decorativa del voucher */
    .yape-header-art {
        background-color: #631971;
        padding: 20px;
        font-size: 1.1rem;
        font-weight: bold;
        letter-spacing: 1px;
        border-bottom: 2px solid rgba(255,255,255,0.1);
    }
    
    /* Tarjeta Blanca Central del Voucher */
    .yape-card {
        background-color: #ffffff !important;
        border-radius: 24px;
        padding: 25px;
        margin: 15px;
        text-align: left;
    }
    
    .yape-title {
        color: #742284 !important;
        font-size: 1.6rem !important;
        font-weight: 800;
        margin-bottom: 5px;
    }
    
    .yape-monto {
        color: #2b2b2b !important;
        font-size: 2.8rem !important;
        font-weight: 800;
        margin: 10px 0;
    }
    
    .yape-monto span {
        font-size: 1.8rem !important;
        color: #2b2b2b !important;
        font-weight: 700;
    }
    
    .yape-usuario {
        color: #333333 !important;
        font-size: 1.3rem !important;
        font-weight: 700;
        margin-bottom: 5px;
    }
    
    .yape-fecha {
        color: #727272 !important;
        font-size: 0.95rem !important;
        margin-bottom: 20px;
        border-bottom: 1px solid #e2e8f0;
        padding-bottom: 15px;
    }
    
    /* Sección del Código de Seguridad de 3 dígitos */
    .yape-seguridad-box {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 20px;
        border-bottom: 1px solid #e2e8f0;
        padding-bottom: 15px;
    }
    
    .yape-seguridad-label {
        color: #7c7c7c !important;
        font-size: 0.85rem !important;
        font-weight: 700;
        text-transform: uppercase;
    }
    
    .yape-token-container {
        display: flex;
        gap: 6px;
    }
    
    .yape-digit {
        background-color: #f1f5f9;
        color: #1e293b !important;
        font-weight: 800;
        font-size: 1.1rem;
        padding: 4px 10px;
        border-radius: 6px;
        border: 1px solid #cbd5e1;
    }
    
    /* Filas de Información de la Transacción */
    .yape-row {
        display: flex;
        justify-content: space-between;
        margin-bottom: 12px;
        font-size: 0.95rem;
    }
    
    .yape-label {
        color: #7c7c7c !important;
        font-weight: 500;
    }
    
    .yape-value {
        color: #1a1a1a !important;
        font-weight: 700;
        text-align: right;
    }
    
    /* Estilos globales para botones de descarga inferiores */
    .stButton>button {
        background-color: #00e6b3 !important;
        color: #742284 !important;
        font-weight: bold !important;
        border-radius: 25px !important;
        border: none !important;
        padding: 10px 25px !important;
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #ffffff !important;
        color: #742284 !important;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("📊 Extractor de Facturas SUNAT")
st.write("✨ **Motor de Alta Velocidad (Paralelo):** Procesamiento de documentos con el diseño de tu billetera digital.")

api_key = st.secrets.get("GEMINI_API_KEY", "")

def consultar_gemini_api_directo(prompt, contenido_bytes, mime_type, api_key_str):
    url = f"https://googleapis.com{api_key_str}"
    base64_data = base64.b64encode(contenido_bytes).decode("utf-8")
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"parts": [{"text": prompt}, {"inlineData": {"mimeType": mime_type, "data": base64_data}}]}]
    }
    response = requests.post(url, headers=headers, json=payload, timeout=30)
    if response.status_code == 200:
        try:
            return response.json()["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError):
            raise Exception("Estructura de respuesta inesperada de la API de Google.")
    else:
        raise Exception(f"Error HTTP {response.status_code}")

def analizar_un_archivo_con_ia(archivo):
    try:
        ext = archivo.name.split(".")[-1].lower()
        bytes_archivo = archivo.read()
        
        prompt = """
        Analiza este documento contable de Perú de forma exhaustiva y extrae la información requerida.
        Debes responder EXCLUSIVAMENTE un bloque de texto formateado en JSON estructurado. No incluyas marcas markdown de código como ```json ni texto adicional fuera de las llaves.
        
        Campos exactos a extraer:
        {
          "ruc_emisor": "Número de RUC de 11 dígitos del vendedor emisor",
          "razon_social": "Nombre o denominación social de la empresa emisora",
          "fecha_emision": "Fecha en formato AAAA-MM-DD",
          "serie": "Serie de 4 caracteres (ej. F001)",
          "numero": "Número correlativo",
          "total": 0.00,
          "categoria_gasto": "Categoría corta"
        }
        """
        
        if ext in ["jpg", "jpeg", "png"]:
            mime_type = "image/jpeg"
        else:
            mime_type = "application/pdf"
            
        texto_respuesta = consultar_gemini_api_directo(prompt, bytes_archivo, mime_type, api_key)
        texto_respuesta = texto_respuesta.strip()
        
        if "{" in texto_respuesta:
            texto_respuesta = texto_respuesta[texto_respuesta.find("{"):texto_respuesta.rfind("}")+1]
        
        data_ia = json.loads(texto_respuesta)
        
        total_val = float(data_ia.get("total", 0.0))
        base_imponible = round(total_val / 1.18, 2)
        igv = round(total_val - base_imponible, 2)
        
        return {
            "Periodo": "202608",
            "Fecha Emisión": data_ia.get("fecha_emision", "18/08/2026"),
            "Serie": data_ia.get("serie", "F001"),
            "Número": data_ia.get("numero", "00000001"),
            "RUC Emisor": data_ia.get("ruc_emisor", "No encontrado"),
            "Razón Social": data_ia.get("razon_social", "No encontrado"),
            "Base Imponible S/": base_imponible,
            "IGV S/": igv,
            "Total S/": total_val,
            "Categoría IA (Gasto)": data_ia.get("categoria_gasto", "Por clasificar")
        }
    except Exception as e:
        return {"Periodo": "202608", "Fecha Emisión": "18/08/2026", "Serie": "F001", "Número": "00000001", "RUC Emisor": "Error", "Razón Social": f"Fallo: {str(e)}", "Base Imponible S/": 0.0, "IGV S/": 0.0, "Total S/": 0.0, "Categoría IA (Gasto)": "Error"}

archivos_subidos = st.file_uploader("Sube tus comprobantes masivos (XML, PDF, JPG, PNG)", type=["pdf", "jpg", "png"], accept_multiple_files=True)

if archivos_subidos:
    with ThreadPoolExecutor(max_workers=5) as executor:
        resultados = executor.map(analizar_un_archivo_con_ia, archivos_subidos)
        datos_facturas = list(resultados)

    if datos_facturas:
        df = pd.DataFrame(datos_facturas)
        
        # OBTENEMOS LOS DATOS DEL PRIMER COMPROBANTE PARA MOSTRAR EN EL VOUCHER
        primera_factura = datos_facturas[0]
        monto_total = primera_factura["Total S/"]
        razon_social_corto = primera_factura["Razón Social"][:22]
        ruc_emisor = primera_factura["RUC Emisor"]
        nro_comprobante = f"{primera_factura['Serie']}-{primera_factura['Número']}"
        
        # Generar código de seguridad aleatorio como el de Yape
        token_1, token_2, token_3 = str(random.randint(0,9)), str(random.randint(0,9)), str(random.randint(0,9))
        nro_operacion = str(random.randint(10000000, 99999999))
        fecha_actual_str = datetime.now().strftime("%d %b. %Y | %I:%M %p.")

        # RENDEREADO HTML EXACTO DE LA CONSTANCIA DE YAPE
        st.markdown(f"""
        <div class="yape-container">
            <div class="yape-header-art">📦 EXTRACTOR INTELIGENTE</div>
            <div class="yape-card">
                <div class="yape-title">¡Yapeaste!</div>
                <div class="yape-monto"><span>S/</span> {monto_total:,.2f}</div>
                <div class="yape-usuario">{razon_social_corto}</div>
                <div class="yape-fecha">📅 {fecha_actual_str}</div>
                
                <div class="yape-seguridad-box">
                    <div class="yape-seguridad-label">Código de seguridad</div>
                    <div class="yape-token-container">
                        <span class="yape-digit">{token_1}</span>
                        <span class="yape-digit">{token_2}</span>
                        <span class="yape-digit">{token_3}</span>
                    </div>
                </div>
