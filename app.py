import streamlit as st
import pandas as pd
import xml.etree.ElementTree as ET
import google.generativeai as genai
import io
import json
import re
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

# Configurar la conexión con Gemini
api_key = st.secrets.get("GEMINI_API_KEY", "")
if api_key:
    genai.configure(api_key=api_key)

# FUNCIÓN INDEPENDIENTE PARA PROCESAR CON LA IA
def analizar_un_archivo_con_ia(archivo):
    try:
        ext = archivo.name.split(".")[-1].lower()
        bytes_archivo = archivo.read()
        
        ruc, proveedor, fecha, serie, numero, total, categoria_gasto = "No encontrado", "No encontrado", "No encontrado", "F001", "00000001", 0.0, "Por clasificar"
        
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
            
            model_text = genai.GenerativeModel('gemini-1.5-flash')
            res_txt = model_text.generate_content(f"Clasifica '{proveedor}' en una categoría de gasto corta de 2 a 4 palabras. Responde SOLO la categoría.")
            categoria_gasto = res_txt.text.strip()
            
            return construir_diccionario_factura(fecha, serie, numero, ruc, proveedor, total, categoria_gasto, archivo.name)

        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = "Analiza este comprobante de pago de Perú y extrae exclusivamente los siguientes campos en un formato JSON limpio y válido, sin bloques de código: {\"ruc_emisor\": \"RUC de 11 dígitos\", \"razon_social\": \"Nombre proveedor\", \"fecha_emision\": \"AAAA-MM-DD\", \"serie\": \"Serie\", \"numero\": \"Número correlativo\", \"total\": 0.00, \"categoria_gasto\": \"Categoría contable corta de 2 a 4 palabras\"}"
        
        if ext in ["jpg", "jpeg", "png"]:
            img = Image.open(io.BytesIO(bytes_archivo))
            img = img.convert("RGB")
            out_img = io.BytesIO()
            img.save(out_img, format="JPEG", quality=40)
            documento_data = {'mime_type': 'image/jpeg', 'data': out_img.getvalue()}
        else:
            documento_data = {'mime_type': 'application/pdf', 'data': bytes_archivo}
            
        response = model.generate_content([prompt, documento_data])
        texto_respuesta = re.sub(r'```json\s*|\s*```', '', response.text.strip())
        data_ia = json.loads(texto_respuesta)
        
        return construir_diccionario_factura(
            data_ia.get("fecha_emision"), data_ia.get("serie"), data_ia.get("numero"),
            data_ia.get("ruc_emisor"), data_ia.get("razon_social"), float(data_ia.get("total", 0.0)),
            data_ia.get("categoria_gasto"), archivo.name
        )
    except Exception:
        return construir_diccionario_factura("No encontrado", "F001", "00000001", "No encontrado", "No encontrado", 0.0, "Por clasificar", archivo.name)

def construir_diccionario_factura(fecha, serie, numero, ruc, proveedor, total, categoria_gasto, nombre_archivo):
    base_imponible = round(total / 1.18, 2)
    igv = round(total - base_imponible, 2)
    
    periodo_ejemplo = "202608"
    if fecha and fecha != "No encontrado" and "-" in fecha:
        anio_f, mes_f, dia_f = fecha.split("-")
        fecha_sire = f"{dia_f}/{mes_f}/{anio_f}"
        periodo_ejemplo = f"{anio_f}{mes_f}"
    else:
        fecha_sire = fecha if fecha else "No encontrado"
        
    return {
        "Periodo": periodo_ejemplo, "Fecha Emisión": fecha_sire, "Tipo Comp.": "01",
        "Serie": serie if serie else "F001", "Número": numero if numero else "00000001",
        "Tipo Doc Identidad": "6", "RUC Emisor": ruc if ruc else "No encontrado",
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
        st.success(f"¡Se consolidaron con éxito {len(datos_facturas)} documentos!")
        st.dataframe(df.drop(columns=["Archivo Original"]), use_container_width=True)
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Base Imponible", f"S/ {df['Base Imponible S/'].sum():,.2f}")
        col2.metric("Total Crédito Fiscal (IGV)", f"S/ {df['IGV S/'].sum():,.2f}")
        col3.metric("Total Facturado", f"S/ {df['Total S/'].sum():,.2f}")
        
        st.subheader("💾 Descarga de Documentos Consolidados")
        lineas_txt = [f"{r['Periodo']}|{r['RUC Emisor']}-{r['Serie']}-{r['Número']}|{r['Fecha Emisión']}||01|{r['Serie']}|{r['Número']}||6|{r['RUC Emisor']}|{r['Razón Social']}|{r['Base Imponible S/']:.2f}|{r['IGV S/']:.2f}||||||{r['Total S/']:.2f}|||1|||" for i, r in df.iterrows()]
        contenido_txt = "\r\n".join(lineas_txt) + "\r\n"
        
        ruc_cliente_ejemplo = "20123456789"
        nombre_txt_oficial = f"LE{ruc_cliente_ejemplo}2026080000080400001111.txt"
        
        b1, b2 = st.columns(2)
        with b1:
            st.download_button("📥 Descargar Archivo Plano SIRE (.txt)", data=contenido_txt, file_name=nombre_txt_oficial, mime="text/plain")
        with b2:
            out = io.BytesIO()
            with pd.ExcelWriter(out, engine='openpyxl') as w: df.drop(columns=["Archivo Original"]).to_excel(w, index=False)
            st.download_button("📥 Descargar Reporte en Excel (.xlsx)", data=out.getvalue(), file_name="reporte_control_sire.xlsx")


