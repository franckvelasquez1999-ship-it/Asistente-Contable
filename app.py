import streamlit as st
import pandas as pd
import xml.etree.ElementTree as ET
import google.generativeai as genai
import io
import json
import re
from pypdf import PdfReader

# 1. Configuración de la página en la nube
st.set_page_config(page_title="Asistente Contable", layout="wide")

# 2. INYECCIÓN DE DISEÑO AVANZADO (GRIS OSCURO Y AZUL CORPORATIVO)
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
st.write("✨ **IDP Multimodal:** Procesamiento inteligente de documentos XML, PDF e imágenes impulsado por Google Gemini.")

# Configurar la conexión con Gemini
api_key = st.secrets.get("GEMINI_API_KEY", "")
if api_key:
    genai.configure(api_key=api_key)

# FUNCIÓN PARA PROCESAR CUALQUIER DOCUMENTO DE FORMA VISUAL CON GEMINI
def procesar_con_gemini_vision(archivo_bytes, mime_type):
    if not api_key:
        return None
    try:
        # Usamos el modelo ultra rápido y con excelente visión de Google
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = """
        Analiza este comprobante de pago de Perú (puede ser factura o boleta) y extrae los datos requeridos. 
        Debes responder ÚNICAMENTE con un objeto JSON limpio y válido con esta estructura exacta, sin textos adicionales, sin saludos y sin las marcas de código ```json:
        {
            "ruc_emisor": "Número de RUC de 11 dígitos del proveedor",
            "razon_social": "Nombre o Razón Social de la empresa proveedora",
            "fecha_emision": "Fecha en formato AAAA-MM-DD",
            "serie": "Serie (ejemplo: F001 o E001)",
            "numero": "Número correlativo",
            "total": 0.00,
            "categoria_gasto": "Categoría contable corta de 2 a 4 palabras (ejemplo: Útiles de Oficina, Combustibles, Servicios Básicos)"
        }
        Si un dato no es visible o está borroso, ponlo como null.
        """
        
        # Estructuramos el archivo binario para mandarlo directo a los ojos de Gemini
        documento_data = {
            'mime_type': mime_type,
            'data': archivo_bytes
        }
        
        response = model.generate_content([prompt, documento_data])
        texto_respuesta = response.text.strip()
        
        # Limpiar posibles bloques que ponga la IA
        texto_respuesta = re.sub(r'```json\s*|\s*```', '', texto_respuesta)
        return json.loads(texto_respuesta)
    except Exception:
        return None

# Caja de subida multimedios
archivos_subidos = st.file_uploader("Sube tus comprobantes oficiales (XML, PDF, JPG, PNG)", type=["xml", "pdf", "jpg", "png"], accept_multiple_files=True)

if archivos_subidos:
    datos_facturas = []
    barra_progreso = st.progress(0, text="Analizando documentos con los ojos de Google Gemini...")

    ruc_cliente_ejemplo = "20123456789" 
    periodo_ejemplo = "202608"

    for i, archivo in enumerate(archivos_subidos):
        try:
            ext = archivo.name.split(".")[-1].lower()
            bytes_archivo = archivo.read()
            
            # Inicializar variables
            ruc, proveedor, fecha, serie, numero, total, categoria_gasto = "No encontrado", "No encontrado", "No encontrado", "F001", "00000001", 0.0, "Por clasificar"
            
            # CASO 1: XML TRADICIONAL (Lectura rápida por código nativo)
            if ext == "xml":
                try:
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
                    
                    # Clasificación por texto con Gemini
                    model_text = genai.GenerativeModel('gemini-1.5-flash')
                    res_txt = model_text.generate_content(f"Clasifica '{proveedor}' en una categoría de gasto corta de 2 a 4 palabras. Responde SOLO la categoría.")
                    categoria_gasto = res_txt.text.strip()
                except Exception:
                    ext = "pdf" # Forzar a lectura visual si el XML está corrupto

            # CASO 2: PDF DIGITAL O ESCANEADO (¡Usamos los ojos de Gemini!)
            if ext == "pdf":
                data_ia = procesar_con_gemini_vision(bytes_archivo, "application/pdf")
                if data_ia:
                    ruc = data_ia.get("ruc_emisor", "No encontrado")
                    proveedor = data_ia.get("razon_social", "No encontrado")
                    fecha = data_ia.get("fecha_emision", "No encontrado")
                    serie = data_ia.get("serie", "F001")
                    numero = data_ia.get("numero", "00000001")
                    total = float(data_ia.get("total", 0.0))
                    categoria_gasto = data_ia.get("categoria_gasto", "Por clasificar")

            # CASO 3: FOTOS DIRECTAS (JPG / PNG)
            elif ext in ["jpg", "jpeg", "png"]:
                mime = f"image/{'jpeg' if ext in ['jpg', 'jpeg'] else 'png'}"
                data_ia = procesar_con_gemini_vision(bytes_archivo, mime)
                if data_ia:
                    ruc = data_ia.get("ruc_emisor", "No encontrado")
                    proveedor = data_ia.get("razon_social", "No encontrado")
                    fecha = data_ia.get("fecha_emision", "No encontrado")
                    serie = data_ia.get("serie", "E001")
                    numero = data_ia.get("numero", "000001")
                    total = float(data_ia.get("total", 0.0))
                    categoria_gasto = data_ia.get("categoria_gasto", "Por clasificar")

            # Cálculos automáticos tributarios peruanos
            base_imponible = round(total / 1.18, 2)
            igv = round(total - base_imponible, 2)
            
            if fecha and fecha != "No encontrado" and "-" in fecha:
                anio_f, mes_f, dia_f = fecha.split("-")
                fecha_sire = f"{dia_f}/{mes_f}/{anio_f}"
                periodo_ejemplo = f"{anio_f}{mes_f}"
            else:
                fecha_sire = fecha

            datos_facturas.append({
                "Periodo": periodo_ejemplo,
                "Fecha Emisión": fecha_sire,
                "Tipo Comp.": "01",
                "Serie": serie,
                "Número": numero,
                "Tipo Doc Identidad": "6",
                "RUC Emisor": ruc,
                "Razón Social": proveedor,
                "Base Imponible S/": base_imponible,
                "IGV S/": igv,
                "Total S/": total,
                "Categoría IA (Gasto)": categoria_gasto
            })
            barra_progreso.progress((i + 1) / len(archivos_subidos), text=f"Procesando: {archivo.name}")
        except Exception as e:
            st.error(f"Error en archivo {archivo.name}: {e}")

    barra_progreso.empty()

    if datos_facturas:
        df = pd.DataFrame(datos_facturas)
        st.success(f"¡Se consolidaron con éxito {len(datos_facturas)} documentos!")
        st.dataframe(df, use_container_width=True)
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Base Imponible", f"S/ {df['Base Imponible S/'].sum():,.2f}")
        col2.metric("Total Crédito Fiscal (IGV)", f"S/ {df['IGV S/'].sum():,.2f}")
        col3.metric("Total Facturado", f"S/ {df['Total S/'].sum():,.2f}")
        
        st.subheader("💾 Descarga de Documentos Consolidados")
        lineas_txt = [f"{r['Periodo']}|{r['RUC Emisor']}-{r['Serie']}-{r['Número']}|{r['Fecha Emisión']}||01|{r['Serie']}|{r['Número']}||6|{r['RUC Emisor']}|{r['Razón Social']}|{r['Base Imponible S/']:.2f}|{r['IGV S/']:.2f}||||||{r['Total S/']:.2f}|||1|||" for i, r in df.iterrows()]
        contenido_txt = "\r\n".join(lineas_txt) + "\r\n"
        nombre_txt_oficial = f"LE{ruc_cliente_ejemplo}{periodo_ejemplo}00080400001111.txt"
        
        b1, b2 = st.columns(2)
        with b1:
            st.download_button("📥 Descargar Archivo Plano SIRE (.txt)", data=contenido_txt, file_name=nombre_txt_oficial, mime="text/plain")
        with b2:
            out = io.BytesIO()
            with pd.ExcelWriter(out, engine='openpyxl') as w: df.to_excel(w, index=False)
            st.download_button("📥 Descargar Reporte en Excel (.xlsx)", data=out.getvalue(), file_name="reporte_control_sire.xlsx")
