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
    
    .yape-monto-simbolo {
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
st.write("✨ **Motor de Alta Velocidad:** Procesamiento de comprobantes con el diseño e identidad de Yape.")

api_key = st.secrets.get("GEMINI_API_KEY", "")

# FUNCIÓN HTTP DIRECTA COMPATIBLE CON GEMINI
def consultar_gemini_api_directo(prompt, contenido_bytes=None, mime_type=None, api_key_str=""):
    url = f"https://googleapis.com{api_key_str}"
    headers = {"Content-Type": "application/json"}
    
    partes = [{"text": prompt}]
    if contenido_bytes and mime_type:
        base64_data = base64.b64encode(contenido_bytes).decode("utf-8")
        partes.append({
            "inlineData": {
                "mimeType": mime_type,
                "data": base64_data
            }
        })
        
    payload = {"contents": [{"parts": partes}]}
    response = requests.post(url, headers=headers, json=payload, timeout=30)
    
    if response.status_code == 200:
        try:
            return response.json()["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError):
            raise Exception("Respuesta con estructura inesperada de Google.")
    else:
        raise Exception(f"Error del servidor Google (HTTP {response.status_code})")

# FUNCIÓN PARA PROCESAR LOS ARCHIVOS
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
            
            res_txt = consultar_gemini_api_directo(f"Clasifica '{proveedor}' en una categoría de gasto corta de 2 a 4 palabras. Responde SOLO la categoría.", api_key_str=api_key)
            categoria_gasto = res_txt.strip()
        else:
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
              "categoria_gasto": "Categoría corta de gasto"
            }
            """
            mime_type = "image/jpeg" if ext in ["jpg", "jpeg", "png"] else "application/pdf"
            texto_respuesta = consultar_gemini_api_directo(prompt, bytes_archivo, mime_type, api_key)
            texto_respuesta = texto_respuesta.strip()
            
            if "{" in texto_respuesta:
                texto_respuesta = texto_respuesta[texto_respuesta.find("{"):texto_respuesta.rfind("}")+1]
            
            data_ia = json.loads(texto_respuesta)
            ruc = data_ia.get("ruc_emisor", "No encontrado")
            proveedor = data_ia.get("razon_social", "No encontrado")
            fecha = data_ia.get("fecha_emision", "No encontrado")
            serie = data_ia.get("serie", "F001")
            numero = data_ia.get("numero", "00000001")
            total_val = float(data_ia.get("total", 0.0))
            categoria_gasto = data_ia.get("categoria_gasto", "Por clasificar")

        base_imponible = round(total_val / 1.18, 2)
        igv = round(total_val - base_imponible, 2)
        
        # Formatear la fecha para SUNAT (DD/MM/AAAA)
        fecha_sire = fecha
        periodo_sire = "202608"
        if fecha and "-" in str(fecha):
            partes = str(fecha).split("-")
            if len(partes) == 3:
                fecha_sire = f"{partes[2]}/{partes[1]}/{partes[0]}"
                periodo_sire = f"{partes[0]}{partes[1]}"

        return {
            "Periodo": periodo_sire,
            "Fecha Emisión": fecha_sire,
            "Tipo Comp.": "01",
            "Serie": str(serie),
            "Número": str(numero),
            "Tipo Doc Identidad": "6",
            "RUC Emisor": str(ruc),
            "Razón Social": str(proveedor),
            "Base Imponible S/": base_imponible,
            "IGV S/": igv,
            "Total S/": total_val,
            "Categoría IA (Gasto)": str(categoria_gasto)
        }
    except Exception as e:

