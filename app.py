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
st.set_page_config(page_title="Asistente Contable", layout="wide")

# 2. INYECCIÓN DE DISEÑO INTERFAZ CLONADA DE YAPE
st.markdown("""
    <style>
    .stApp { 
        background-color: #69167c !important; 
        font-family: 'Inter', -apple-system, sans-serif; 
    }
    h1, h2, h3, h4, .stMarkdown p, p, span, label { 
        color: #ffffff !important; 
    }
    .stFileUploader { 
        background-color: #7b258e !important; 
        border: 2px dashed #00e6b3 !important; 
        border-radius: 20px !important; 
        padding: 25px !important; 
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2) !important; 
    }
    .yape-voucher-completo {
        max-width: 440px;
        background-color: #69167c;
        margin: 20px auto;
        text-align: center;
        padding-bottom: 20px;
    }
    .yape-banner-valdelomar {
        width: 100%;
        height: 220px;
        background-color: #69167c;
        background-image: 
            radial-gradient(rgba(255, 255, 255, 0.15) 1px, transparent 0),
            radial-gradient(rgba(255, 255, 255, 0.1) 2px, transparent 0);
        background-size: 8px 8px, 16px 16px;
        background-position: 0 0, 4px 4px;
        position: relative;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .yape-logo-top {
        position: absolute;
        left: 25px;
        top: 60px;
        width: 65px;
        height: 65px;
    }
    .yape-logo-circle {
        width: 26px;
        height: 26px;
        background-color: #00e6b3;
        border-radius: 50%;
        display: flex;
        justify-content: center;
        align-items: center;
        font-size: 0.6rem;
        color: #69167c;
        font-weight: 800;
        margin-bottom: 4px;
    }
    .yape-logo-text {
        font-size: 1.6rem;
        color: #ffffff;
        font-weight: 800;
        font-style: italic;
        line-height: 1;
        letter-spacing: -1px;
    }
    .avatar-valdelomar {
        width: 130px;
        height: 130px;
        border-radius: 50%;
        border: 1px solid rgba(255,255,255,0.25);
        background: radial-gradient(circle, rgba(138,43,226,0.3) 0%, rgba(74,18,84,0.8) 100%);
        box-shadow: 0 0 30px rgba(0,0,0,0.4);
    }
    .txt-valdelomar {
        position: absolute;
        right: 25px;
        color: rgba(255,255,255,0.4) !important;
        font-family: 'Times New Roman', serif;
        font-size: 0.85rem;
        text-align: left;
        line-height: 1.1;
        letter-spacing: 1px;
        font-weight: 400;
    }
    .yape-card-blanca {
        background-color: #ffffff !important;
        border-radius: 32px;
        padding: 35px 30px;
        margin: 0 15px;
        text-align: left;
        box-shadow: 0 15px 35px rgba(0,0,0,0.3);
    }
    .yape-header-title {
        color: #69167c !important;
        font-size: 1.6rem !important;
        font-weight: 700;
        margin-bottom: 12px;
    }
    .yape-monto-grande {
        color: #383344 !important;
        font-size: 3.8rem !important;
        font-weight: 700;
        margin-bottom: 15px;
        display: flex;
        align-items: baseline;
        line-height: 1;
    }
    .yape-monto-grande span {
        font-size: 2.2rem !important;
        font-weight: 600;
        margin-right: 6px;
        color: #383344 !important;
    }
    .yape-destinatario {
        color: #2c2536 !important;
        font-size: 1.55rem !important;
        font-weight: 700;
        margin-bottom: 8px;
    }
    .yape-timestamp {
        color: #827e8c !important;
        font-size: 1rem !important;
        margin-bottom: 25px;
        padding-bottom: 20px;
        border-bottom: 1.5px solid #f0edf5;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    .yape-token-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 25px;
        padding-bottom: 20px;
        border-bottom: 1.5px solid #f0edf5;
    }
    .yape-token-title {
        color: #827e8c !important;
        font-size: 0.85rem !important;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .yape-token-blocks {
        display: flex;
        gap: 4px;
    }
    .yape-block-num {
        background-color: #f4f1f7;
        color: #2c2536 !important;
        font-weight: 700;
        font-size: 1.15rem;
        width: 30px;
        height: 34px;
        display: flex;
        justify-content: center;
        align-items: center;
        border-radius: 6px;
        border: 1px solid #e1dae8;
    }
    .yape-info-section-title {
        color: #827e8c !important;
        font-size: 0.85rem !important;
        font-weight: 700;
        text-transform: uppercase;
        margin-bottom: 18px;
        letter-spacing: 0.5px;
    }
    .yape-meta-row {
        display: flex;
        justify-content: space-between;
        margin-bottom: 16px;
        font-size: 1.05rem;
        line-height: 1.2;
    }
    .yape-meta-label {
        color: #827e8c !important;
        font-weight: 500;
    }
    .yape-meta-value {
        color: #2c2536 !important;
        font-weight: 600;
        text-align: right;
    }
    .stButton>button {
        background-color: #00e6b3 !important;
        color: #69167c !important;
        font-weight: 700 !important;
        border-radius: 25px !important;
        border: none !important;
        padding: 12px 25px !important;
        width: 100%;
        font-size: 1.05rem !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    .stButton>button:hover {
        background-color: #ffffff !important;
        color: #69167c !important;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("📊 Extractor de Facturas SUNAT")
st.write("✨ **Motor de Alta Velocidad:** Procesamiento paralelo de comprobantes con visualización nativa idéntica.")

api_key = st.secrets.get("GEMINI_API_KEY", "")

def consulting_gemini_api_direct(prompt, contenido_bytes=None, mime_type=None, api_key_str=""):
    url = f"https://googleapis.com{api_key_str}"
    headers = {"Content-Type": "application/json"}
    partes = [{"text": prompt}]
    if contenido_bytes and mime_type:
        base64_data = base64.b64encode(contenido_bytes).decode("utf-8")
        partes.append({"inlineData": {"mimeType": mime_type, "data": base64_data}})
    payload = {"contents": [{"parts": partes}]}
    response = requests.post(url, headers=headers, json=payload, timeout=30)
    if response.status_code == 200:
        try:
            return response.json()["candidates"]["content"]["parts"]["text"]
        except:
            return "{}"
    return "{}"

def analizar_un_archivo_con_ia(archivo):
    # Inicialización de variables seguras por defecto
    ruc = "No encontrado"
    proveedor = "No encontrado"
    fecha = "No encontrado"
    serie = "F001"
    numero = "00000001"
    total_val = 0.0
    categoria_gasto = "Por clasificar"
    
    try:
        ext = archivo.name.split(".")[-1].lower()
        bytes_archivo = archivo.read()
        
        if ext == "xml":
            archivo.seek(0)
            tree = ET.parse(archivo)
            root = tree.getroot()
            serie_num = root.find(".//{*}ID")
            fecha_emision = root.find(".//{*}IssueDate")
            ruc_emisor = root.find(".//{*}AccountingSupplierParty//{*}CustomerAssignedAccountID")
            nombre_emisor = root.find(".//{*}AccountingSupplierParty//{*}RegistrationName")
            monto_total_xml = root.find(".//{*}LegalMonetaryTotal//{*}PayableAmount")
            
            ruc = ruc_emisor.text if ruc_emisor is not None else "No encontrado"
            proveedor = nombre_emisor.text if nombre_emisor is not None else "No encontrado"
            fecha = fecha_emision.text if fecha_emision is not None else "No encontrado"
            id_comprobante = serie_num.text if serie_num is not None else "F001-00000001"
            serie, numero = id_comprobante.split("-", 1) if "-" in id_comprobante else (id_comprobante[:4], id_comprobante[4:])
            total_val = float(monto_total_xml.text) if monto_total_xml is not None else 0.0
            
            res_txt = consulting_gemini_api_direct("Clasifica este proveedor en una categoría de gasto corta de 2 a 4 palabras. Responde SOLO la categoría.", api_key_str=api_key)
            categoria_gasto = res_txt.strip()
            
        else:
            prompt_lineal = "Analiza este documento contable de Peru de forma exhaustiva y extrae la informacion requerida. Debes responder EXCLUSIVAMENTE un bloque de texto formateado en JSON estructurado. No incluyas marcas markdown de codigo como ```json ni texto adicional fuera de las llaves. Campos exactos a extraer: {\"ruc_emisor\": \"Numero de RUC de 11 digitos del vendedor emisor\", \"razon_social\": \"Nombre o denominacion social de la empresa emisora\", \"fecha_emision\": \"Fecha en formato AAAA-MM-DD\", \"serie\": \"Serie de 4 caracteres (ej. F001)\", \"numero\": \"Numero correlativo\", \"total\": 0.00, \"categoria_gasto\": \"Categoria corta de gasto\"}"
            mime_type = "application/pdf"
            if ext in ["jpg", "jpeg", "png"]:
                mime_type = "image/jpeg"
                
            texto_respuesta = consulting_gemini_api_direct(prompt_lineal, bytes_archivo, mime_type, api_key).strip()
            if "{" in texto_respuesta:
                texto_respuesta = texto_respuesta[texto_respuesta.find("{"):texto_respuesta.rfind("}")+1]
            
            data_ia = json.loads(texto_respuesta)

