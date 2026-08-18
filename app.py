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
    .stApp { 
        background-color: #742284 !important; 
        font-family: 'Inter', sans-serif; 
    }
    h1, h2, h3, h4, .stMarkdown p, p, span, label { 
        color: #ffffff !important; 
    }
    .stFileUploader { 
        background-color: #8c339c !important; 
        border: 2px dashed #00e6b3 !important; 
        border-radius: 20px !important; 
        padding: 25px !important; 
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2) !important; 
    }
    .yape-voucher-completo {
        max-width: 450px;
        background-color: #742284;
        border-radius: 0px;
        margin: 20px auto;
        font-family: 'Inter', sans-serif;
        text-align: center;
        box-shadow: 0 20px 50px rgba(0,0,0,0.5);
    }
    .yape-banner-valdelomar {
        width: 100%;
        height: 180px;
        background: #742284 linear-gradient(135deg, rgba(255,255,255,0.05) 25%, transparent 25%, transparent 50%, rgba(255,255,255,0.05) 50%, rgba(255,255,255,0.05) 75%, transparent 75%, transparent);
        background-size: 40px 40px;
        position: relative;
        border-bottom: 2px solid rgba(255,255,255,0.1);
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .yape-logo-top {
        position: absolute;
        left: 25px;
        top: 45px;
        width: 65px;
        height: 65px;
        background-color: #00e6b3;
        border-radius: 50%;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        box-shadow: 0 4px 10px rgba(0,0,0,0.2);
    }
    .yape-logo-top .s-moneda {
        font-size: 0.65rem;
        color: #742284;
        font-weight: 800;
        margin-bottom: -5px;
    }
    .yape-logo-top .brand-txt {
        font-size: 1.2rem;
        color: #ffffff;
        font-weight: 900;
        font-style: italic;
        font-family: sans-serif;
    }
    .avatar-valdelomar {
        width: 110px;
        height: 110px;
        border-radius: 50%;
        border: 3px double rgba(255,255,255,0.4);
        background: radial-gradient(circle, #8c339c, #4a1254);
        box-shadow: inset 0 0 20px rgba(0,0,0,0.6);
    }
    .txt-valdelomar {
        position: absolute;
        right: 20px;
        color: rgba(255,255,255,0.4) !important;
        font-family: 'Georgia', serif;
        font-size: 0.85rem;
        text-align: right;
        line-height: 1.1;
        letter-spacing: 1px;
    }
    .yape-card-blanca {
        background-color: #ffffff !important;
        border-radius: 28px;
        padding: 30px 25px;
        margin: 0 20px 30px 20px;
        text-align: left;
        box-shadow: 0 10px 25px rgba(0,0,0,0.2);
    }
    .yape-header-title {
        color: #742284 !important;
        font-size: 1.65rem !important;
        font-weight: 800;
        margin-bottom: 5px;
    }
    .yape-monto-grande {
        color: #3b3b3b !important;
        font-size: 3.4rem !important;
        font-weight: 800;
        margin: 15px 0;
        display: flex;
        align-items: baseline;
    }
    .yape-monto-grande span {
        font-size: 2.1rem !important;
        font-weight: 700;
        margin-right: 8px;
    }
    .yape-destinatario {
        color: #1e293b !important;
        font-size: 1.5rem !important;
        font-weight: 700;
        margin-bottom: 4px;
    }
    .yape-timestamp {
        color: #64748b !important;
        font-size: 0.95rem !important;
        margin-bottom: 25px;
        padding-bottom: 15px;
        border-bottom: 1px solid #e2e8f0;
    }
    .yape-token-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 25px;
        padding-bottom: 15px;
        border-bottom: 1px solid #e2e8f0;
    }
    .yape-token-title {
        color: #64748b !important;
        font-size: 0.85rem !important;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .yape-token-blocks {
        display: flex;
        gap: 5px;
    }
    .yape-block-num {
        background-color: #f8fafc;
        color: #0f172a !important;
        font-weight: 800;
        font-size: 1.2rem;
        width: 32px;
        height: 36px;
        display: flex;
        justify-content: center;
        align-items: center;
        border-radius: 8px;
        border: 1px solid #cbd5e1;
    }
    .yape-info-section-title {
        color: #64748b !important;
        font-size: 0.8rem !important;
        font-weight: 700;
        text-transform: uppercase;
        margin-bottom: 15px;
        letter-spacing: 0.5px;
    }
    .yape-meta-row {
        display: flex;
        justify-content: space-between;
        margin-bottom: 14px;
        font-size: 0.98rem;
    }
    .yape-meta-label {
        color: #64748b !important;
        font-weight: 500;
    }
    .yape-meta-value {
        color: #0f172a !important;
        font-weight: 700;
    }
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
st.write("✨ **Motor de Alta Velocidad:** Procesamiento de comprobantes con el diseño e identidad de Yape.")

api_key = st.secrets.get("GEMINI_API_KEY", "")

def consultar_gemini_api_directo(prompt, contenido_bytes=None, mime_type=None, api_key_str=""):
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
        except (KeyError, IndexError):
            raise Exception("Respuesta con estructura inesperada.")
    else:
        raise Exception(f"Error HTTP {response.status_code}")

def analizar_un_archivo_con_ia(archivo):
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
            
            res_txt = consultar_gemini_api_directo("Clasifica este proveedor en una categoría de gasto corta de 2 a 4 palabras. Responde SOLO la categoría.", api_key_str=api_key)
            categoria_gasto = res_txt.strip()
        else:
            prompt_lineal = "Analiza este documento contable de Peru de forma exhaustiva y extrae la informacion requerida. Debes responder EXCLUSIVAMENTE un bloque de texto formateado en JSON estructurado. No incluyas marcas markdown de codigo como ```json ni texto adicional fuera de las llaves. Campos exactos a extraer: {\"ruc_emisor\": \"Numero de RUC de 11 digitos del vendedor emisor\", \"razon_social\": \"Nombre o denominacion social de la empresa emisora\", \"fecha_emision\": \"Fecha en formato AAAA-MM-DD\", \"serie\": \"Serie de 4 caracteres (ej. F001)\", \"numero\": \"Numero correlativo\", \"total\": 0.00, \"categoria_gasto\": \"Categoria corta de gasto\"}"
            mime_type = "image/jpeg" if ext in ["jpg", "jpeg", "png"] else "application/pdf"
            texto_respuesta = consultar_gemini_api_directo(prompt_lineal, bytes_archivo, mime_type, api_key)
            texto_respuesta = texto_respuesta.strip()
            
            if "{" in texto_respuesta:
                texto_respuesta = texto_respuesta[texto_respuesta.find("{"):texto_respuesta.rfind("}")+1]
            
            data_ia = json.loads(texto_respuesta)
            ruc = data_ia.get("ruc_emisor", "No encontrado")
            proveedor = data_ia.get("razon_social", "No encontrado")
            fecha = data_ia.get("fecha_emision", "No encontrado")
            serie = data_ia.get("serie", "F001")
            numero = data_ia.get("numero", "00000001")
