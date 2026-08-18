import streamlit as st
import pandas as pd
import xml.etree.ElementTree as ET
import io
import json
import re
import requests
import base64
from PIL import Image
from concurrent.futures import ThreadPoolExecutor

# 1. Configuración de la página en la nube
st.set_page_config(page_title="Asistente Contable", layout="wide")

# 2. INYECCIÓN DE DISEÑO AVANZADO CORPORATIVO
st.markdown("""
    <style>
    .stApp { background-color: #1e293b !important; font-family: sans-serif; }
    h1 { color: #ffffff !important; font-weight: 800 !important; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }
    .stMarkdown p, p, span, label { color: #cbd5e1 !important; }
    .stFileUploader { background-color: #334155 !important; border: 2px dashed #2563eb !important; border-radius: 15px !important; padding: 25px !important; box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3) !important; }
    [data-testid="stMetric"] { background-color: #334155 !important; border-left: 5px solid #2563eb !important; border-radius: 8px !important; padding: 15px !important; }
    [data-testid="stMetricValue"] { color: #60a5fa !important; font-weight: 700 !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("📊 Extractor de Facturas SUNAT")
st.write("✨ **Motor de Alta Velocidad (Paralelo):** Procesamiento instantáneo de XML, PDF e imágenes con compresión automática e IA Google Gemini.")

# Obtener API Key de los Secrets de Streamlit
api_key = st.secrets.get("GEMINI_API_KEY", "")

# FUNCIÓN PARA LLAMAR A GEMINI MEDIANTE HTTP DIRECTO (BYPASSEA EL BUG DEL SDK 404)
def consultar_gemini_api_directo(prompt, contenido_bytes, mime_type, api_key_str):
    url = f"https://googleapis.com{api_key_str}"
    
    # Convertir el archivo a Base64 requerido por la API de Google
    base64_data = base64.b64encode(contenido_bytes).decode("utf-8")
    
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt},
                    {
                        "inlineData": {
                            "mimeType": mime_type,
                            "data": base64_data
                        }
                    }
                ]
            }
        ]
    }
    
    response = requests.post(url, headers=headers, json=payload, timeout=30)
    if response.status_code == 200:
        resultado_json = response.json()
        try:
            texto = resultado_json["candidates"][0]["content"]["parts"][0]["text"]
            return texto
        except KeyError:
            raise Exception("Estructura de respuesta inesperada de la API de Google.")
    else:
        raise Exception(f"Error HTTP {response.status_code}: {response.text}")

# FUNCIÓN PARA LLAMAR A GEMINI SOLO TEXTO (XML CLASIFICACIÓN)
def consultar_gemini_texto_directo(prompt, api_key_str):
    url = f"https://googleapis.com{api_key_str}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    response = requests.post(url, headers=headers, json=payload, timeout=20)
    if response.status_code == 200:
        try:
            return response.json()["candidates"][0]["content"]["parts"][0]["text"]
        except KeyError:
            return "General"
    return "General"

# FUNCIÓN PARA NORMALIZAR FECHAS DE MANERA SEGURA
def normalizar_fecha(texto_fecha):
    if not texto_fecha or texto_fecha == "No encontrado":
        return "No encontrado"
    
    texto_str = str(texto_fecha).strip()
    numeros = re.findall(r'\d+', texto_str)
    
    if len(numeros) >= 3:
        if len(numeros[0]) == 4:  # Formato AAAA-MM-DD
            return f"{numeros[0]}-{numeros[1].zfill(2)}-{numeros[2].zfill(2)}"
        elif len(numeros[2]) == 4:  # Formato DD-MM-AAAA
            return f"{numeros[2]}-{numeros[1].zfill(2)}-{numeros[0].zfill(2)}"
            
    return texto_str

# FUNCIÓN INDEPENDIENTE PARA PROCESAR CON LA IA
def analizar_un_archivo_con_ia(archivo):
    if not api_key:
        return construir_diccionario_factura("No encontrado", "Error", "Error", "No encontrado", "Falta configurar GEMINI_API_KEY", 0.0, "Sin Configurar", archivo.name)
        
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
            total = float(monto_total_xml.text) if monto_total_xml is not None else 0.0
            
            res_txt = consultar_gemini_texto_directo(f"Clasifica '{proveedor}' en una categoría de gasto contable de 2 a 4 palabras. Responde SOLO la categoría.", api_key)
            categoria_gasto = res_txt.strip()
            
            return construir_diccionario_factura(fecha, serie, numero, ruc, proveedor, total, categoria_gasto, archivo.name)

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
          "categoria_gasto": "Categoría corta como 'Servicios Básicos', 'Alimentos', 'Sistemas'"
        }
        """
        
        if ext in ["jpg", "jpeg", "png"]:
            img = Image.open(io.BytesIO(bytes_archivo))
            img = img.convert("RGB")
            out_img = io.BytesIO()
            img.save(out_img, format="JPEG", quality=60)
            contenido_envio = out_img.getvalue()
            mime_type = "image/jpeg"
        else:
            contenido_envio = bytes_archivo
            mime_type = "application/pdf"
            
        texto_respuesta = consultar_gemini_api_directo(prompt, contenido_envio, mime_type, api_key)
        texto_respuesta = texto_respuesta.strip()
        
        if "{" in texto_respuesta:
            texto_respuesta = texto_respuesta[texto_respuesta.find("{"):texto_respuesta.rfind("}")+1]
        
        data_ia = json.loads(texto_respuesta)
        fecha_normalizada = normalizar_fecha(data_ia.get("fecha_emision"))
        
        return construir_diccionario_factura(
            fecha_normalizada, data_ia.get("serie"), data_ia.get("numero"),
            data_ia.get("ruc_emisor"), data_ia.get("razon_social"), float(data_ia.get("total", 0.0)),
            data_ia.get("categoria_gasto"), archivo.name
        )
    except Exception as e:
        return construir_diccionario_factura("No encontrado", "Error", "Error", "No encontrado", f"Fallo: {str(e)}", 0.0, "Por clasificar", archivo.name)

def construir_diccionario_factura(fecha, serie, numero, ruc, proveedor, total, categoria_gasto, nombre_archivo):
    base_imponible = round(total / 1.18, 2)
    igv = round(total - base_imponible, 2)
    
    periodo_ejemplo = "202608"
    if fecha and fecha != "No encontrado" and "-" in str(fecha):
        try:
            partes = str(fecha).split("-")
            if len(partes) == 3:
                anio_f, mes_f, dia_f = partes
                fecha_sire = f"{dia_f}/{mes_f}/{anio_f}"
                periodo_ejemplo = f"{anio_f}{mes_f}"
            else:
                fecha_sire = fecha
        except Exception:
            fecha_sire = fecha
    else:
        fecha_sire = fecha if fecha else "No encontrado"
        
    return {
        "Periodo": periodo_ejemplo, "Fecha Emisión": fecha_sire, "Tipo Comp.": "01",
        "Serie": str(serie) if serie else "F001", "Número": str(numero) if numero else "00000001",
        "Tipo Doc Identidad": "6", "RUC Emisor": str(ruc) if ruc else "No encontrado",
        "Razón Social": proveedor if proveedor else "No encontrado",
        "Base Imponible S/": base_imponible, "IGV S/": igv, "Total S/": total,
        "Categoría IA (Gasto)": categoria_gasto if categoria_gasto else "Por clasificar",
        "Archivo Original": nombre_archivo
    }

archivos_subidos = st.file_uploader("Sube tus comprobantes masivos (XML, PDF, JPG, PNG)", type=["xml", "pdf", "jpg", "png"], accept_multiple_files=True)

if archivos_subidos:
    datos_facturas = []
    st.info("🚀 **Motor de procesamiento asíncrono activado:** Consultando múltiples archivos en paralelo con los servidores de Google...")
    
    with ThreadPoolExecutor() as executor:
        resultados = executor.map(analizar_un_archivo_con_ia, archivos_subidos)
        datos_facturas = list(resultados)

    if datos_facturas:
        df = pd.DataFrame(datos_facturas)


